#print("RAG ENGINE FILE LOADED FROM:", __file__)

import os
import time
import json
import logging
import hashlib
from threading import Lock
from typing import Any, Dict, Tuple
from datetime import datetime

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from sentence_transformers import CrossEncoder

import redis
import pickle

load_dotenv()

# ============================================================
# Configuration
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")

FAST_LLM_MODEL = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

RETRIEVE_K = int(os.getenv("RETRIEVE_K", "4"))
CACHE_TTL_SECONDS = int(os.getenv("RAG_CACHE_TTL", "300"))

REDIS_URL = os.getenv("REDIS_URL")
LOG_LEVEL = os.getenv("RAG_LOG_LEVEL", "INFO")

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("steward.rag_engine")

# ============================================================
# Prompt Templates
# ============================================================

QUERY_PROMPT = """
You are an AI assistant answering questions about a codebase.

STRICT RULES:
- Use ONLY the provided context.
- If the answer is not explicitly present, respond with:
  "This information is not present in the uploaded codebase."
- Do NOT infer or use general knowledge.

Context:
{context}

Question:
{question}""".strip()

SUGGEST_PROMPT = """
You are an AI onboarding assistant helping a developer extend a codebase.

IMPORTANT:
- The requested functionality is NOT present in the current codebase.
- You are proposing how to implement it.
- Do NOT claim the code already supports this feature.

RULES:
1. Clearly state that the functionality is missing.
2. Propose how to implement it using the existing codebase structure.
3. Specify which files should be created or modified.
4. Provide drop-in code blocks where appropriate.
5. Do NOT assume the changes are applied.

Context:
{context}

Feature request:
{question}""".strip()

DOCS_PROMPT = """
You are generating {doc_type} documentation for a software project.

RULES (MANDATORY):
- Base ALL technical statements strictly on the provided code context
- Use business context ONLY for framing and motivation
- If something is unclear or missing, say so explicitly
- Do NOT invent APIs, flows, or dependencies
- Write for the specified audience
- For doc_type "onboarding", focus on:
  * First 30 minutes
  * Entry points
  * Key files to read
  * What not to change
  * Known gaps or risks

Audience:
{audience}

Business Context (optional):
{business_context}

Code Context:
{context}

Output:
Well-structured markdown documentation.""".strip()

# ============================================================
# Cache
# ============================================================

class TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._lock = Lock()

    def get(self, key: str):
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            ts, value = entry
            if time.time() - ts > self.ttl:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any):
        with self._lock:
            self._store[key] = (time.time(), value)

class RedisCache:
    def __init__(self, url: str, ttl_seconds: int):
        self.ttl = ttl_seconds
        try:
            self.client = redis.StrictRedis.from_url(url)
            self.client.ping()
        except Exception:
            self.client = None

    def get(self, key: str):
        if not self.client:
            return None
        data = self.client.get(key)
        return pickle.loads(data) if data else None

    def set(self, key: str, value: Any):
        if self.client:
            self.client.setex(key, self.ttl, pickle.dumps(value))

# ============================================================
# RAG Engine
# ============================================================

class RAGEngine:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

        self.llm = ChatOpenAI(
            model=FAST_LLM_MODEL,
            temperature=TEMPERATURE,
            api_key=OPENAI_API_KEY,
        )

        try:
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception:
            self.reranker = None

        self.cache = RedisCache(REDIS_URL, CACHE_TTL_SECONDS) if REDIS_URL else TTLCache(CACHE_TTL_SECONDS)

    # ------------------
    # Vector DB helpers
    # ------------------
    def _get_vectordb(self, session_id: str) -> Chroma:
        path = os.path.join(CHROMA_PERSIST_DIR, session_id)
        if not os.path.isdir(path):
            raise RuntimeError(f"No ingestion found for session_id={session_id}")
        return Chroma(persist_directory=path, embedding_function=self.embeddings)

    def _retrieve_docs(self, question: str, session_id: str, k: int = RETRIEVE_K):
        vectordb = self._get_vectordb(session_id)
        docs = vectordb.similarity_search_with_score(question, k=k)

        return [
            {
                "text": d.page_content,
                "meta": d.metadata,
                "score": float(score),
            }
            for d, score in docs
        ]

    def _build_context(self, docs):
        return "\n\n".join(
            f"[{d['meta'].get('file_path', 'unknown')}]\n{d['text']}"
            for d in docs
        )

    # ============================================================
    # QUERY (read-only)
    # ============================================================
    def query(self, question: str, session_id: str):
        docs = self._retrieve_docs(question, session_id)

        if not docs:
            return {
                "answer": "This information is not present in the uploaded codebase.",
                "sources": [],
            }

        avg_score = sum(d["score"] for d in docs) / len(docs)
        if avg_score < 0.05:
            return {
                "answer": "This information is not present in the uploaded codebase.",
                "sources": [],
            }

        context = self._build_context(docs)

        answer = self.llm.predict(
            QUERY_PROMPT.format(
                context=context,
                question=question,
            )
        ).strip()

        return {
            "answer": answer,
            "sources": list({
                d["meta"].get("file_path")
                for d in docs
                if d["meta"].get("file_path")
            }),
        }

    # ============================================================
    # SUGGEST (propositional)
    # ============================================================
    def suggest(self, question: str, session_id: str):
        docs = self._retrieve_docs(question, session_id)
        context = self._build_context(docs)

        proposal = self.llm.predict(
            SUGGEST_PROMPT.format(
                context=context,
                question=question,
            )
        ).strip()

        return {
            "status": "proposed",
            "summary": "Proposed implementation for the requested functionality.",
            "proposal": proposal,
            "warning": "This code is a proposal and has NOT been applied to the codebase.",
        }
    # ============================================================
    # GENERATE DOCS
    # ============================================================
    def generate_docs(self,session_id: str,doc_type: str,audience: str,business_context: str | None,k: int = 12,):
        # Normalize empty business context
        if business_context is not None and not business_context.strip():
            business_context = None
        
        prompt_business_context = (business_context if business_context is not None else "No business context provided by the user.")

        cache_key = self._docs_cache_key(
            session_id=session_id,
            doc_type=doc_type,
            audience=audience,
            business_context=prompt_business_context,
        )

        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Broaden retrieval for onboarding docs
        query_hint = doc_type.replace("_", " ")
        if doc_type == "onboarding":
            query_hint = "entrypoint overview main app config routing"
        vectordb = self._get_vectordb(session_id)

        docs = vectordb.similarity_search_with_score(
            query_hint,
            k=k,
        )

        if not docs:
            result = {
                "doc_type": doc_type,
                "audience": audience,
                "content": "Not enough information in the codebase to generate documentation.",
                "sources": [],
                "warning": "Documentation generation failed due to insufficient context.",
            }
            self.cache.set(cache_key, result)
            return result

        normalized = [
            {"text": d.page_content, "meta": d.metadata, "score": float(s)}
            for d, s in docs
        ]

        context = "\n\n".join(
            f"[{d['meta'].get('file_path', 'unknown')}]\n{d['text']}"
            for d in normalized
        )

        # DEFINE content BEFORE using it
        content = self.llm.predict(
            DOCS_PROMPT.format(
                doc_type=doc_type,
                audience=audience,
                business_context=business_context or "None provided",
                context=context,
            )
        ).strip()

        sources = list({
            d["meta"].get("file_path")
            for d in normalized
            if d["meta"].get("file_path")
        })

        result = {
            "doc_type": doc_type,
            "audience": audience,
            "content": content,
            "sources": sources,
            "warning": "Generated documentation is inferred from code and may be incomplete.",
        }

        self.cache.set(cache_key, result)
        return result


    # ============================================================
    # HASH BUSINESS CONTEXT 
    # ============================================================
    def _hash_business_context(self, business_context: str | None) -> str:
        if not business_context:
            return "none"
        return hashlib.sha256(business_context.strip().encode("utf-8")).hexdigest()

    # ============================================================
    # CACHE KEY
    # ============================================================
    def _docs_cache_key(self,session_id: str,doc_type: str,audience: str,business_context: str | None,) -> str:
        return json.dumps(
            {
            "session_id": session_id,
            "doc_type": doc_type,
            "audience": audience,
            "business_ctx": self._hash_business_context(business_context),
            },
            sort_keys=True,
        )


# ============================================================
# Public API wrappers (NO shadowing)
# ============================================================

_engine = RAGEngine()


def run_query(question: str, session_id: str):
    return _engine.query(question=question, session_id=session_id)

def run_suggest(question: str, session_id: str):
    return _engine.suggest(question=question, session_id=session_id)

def run_generate_docs(session_id: str,doc_type: str,audience: str,business_context: str | None = None,):
    return _engine.generate_docs(session_id=session_id,doc_type=doc_type,audience=audience,business_context=business_context,)
