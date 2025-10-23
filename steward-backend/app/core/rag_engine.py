# app/core/rag_engine.py
import os
import time
import json
import logging
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# optional reranker
from sentence_transformers import CrossEncoder

# optional redis cache
import redis
import pickle

load_dotenv()

# --- Configuration (env-driven) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openai")  # descriptive only
FAST_LLM_MODEL = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo")
HIGH_LLM_MODEL = os.getenv("HIGH_LLM_MODEL", "gpt-4o")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
RETRIEVE_K = int(os.getenv("RETRIEVE_K", "4"))
CACHE_TTL_SECONDS = int(os.getenv("RAG_CACHE_TTL", "300"))  # 5 minutes default
MODEL_TIERING = os.getenv("MODEL_TIERING", "true").lower() == "true"
MODEL_TIERING_SCORE_THRESHOLD = float(os.getenv("MODEL_TIERING_SCORE_THRESHOLD", "0.18"))
LOG_LEVEL = os.getenv("RAG_LOG_LEVEL", "INFO")
REDIS_URL = os.getenv("REDIS_URL", None)

# --- Logging ---
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("steward.rag_engine")


# --- Simple in-memory TTL cache (thread-safe) ---
class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            ts, value = entry
            if time.time() - ts > self.ttl:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.time(), value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# --- Redis-backed cache wrapper (optional) ---
class RedisCache:
    def __init__(self, url: str, ttl_seconds: int = 300):
        self.url = url
        self.ttl = ttl_seconds
        try:
            self.client = redis.StrictRedis.from_url(url)
            self.client.ping()
            logger.info("Redis cache connected at %s", url)
        except Exception as e:
            logger.warning("Redis unavailable: %s", e)
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.debug("Redis get failed: %s", e)
        return None

    def set(self, key: str, value: dict) -> None:
        if not self.client:
            return
        try:
            self.client.setex(key, self.ttl, pickle.dumps(value))
        except Exception as e:
            logger.debug("Redis set failed: %s", e)

class TelemetryLogger:
    """Writes structured RAG trace logs per query."""
    def __init__(self, base_dir: str = "data/trace_logs"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def log(self, record: Dict[str, Any]) -> None:
        """Append a trace record to a daily JSONL file."""
        try:
            # Normalize data for JSON serialization
            safe_record = {}
            for k, v in record.items():
                if isinstance(v, (float, int, str, bool)) or v is None:
                    safe_record[k] = v
                elif hasattr(v, "item"):  # e.g., numpy.float32
                    safe_record[k] = v.item()
                else:
                    safe_record[k] = str(v)

            safe_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            log_path = os.path.join(self.base_dir, f"{date_str}.jsonl")

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(safe_record, ensure_ascii=False) + "\n")

            logger.debug("Telemetry trace logged to %s", log_path)
        except Exception as e:
            logger.debug("Telemetry logging failed: %s", e)


# --- Singleton engine that persists retriever/llm instances ---
class RAGEngine:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RAGEngine, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is missing. RAG engine will return errors on queries.")

        self.telemetry = TelemetryLogger()


        # --- Initialize embeddings & vector store ---
        self.embeddings = None
        self.vectordb = None
        self.retriever = None
        self.reranker = None

        try:
            self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
            self.vectordb = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )
            self.retriever = self.vectordb.as_retriever(search_kwargs={"k": RETRIEVE_K})
            logger.info("Chroma vectorstore loaded from %s", CHROMA_PERSIST_DIR)
        except Exception as e:
            logger.exception("Failed to initialize Chroma or embeddings: %s", e)

        # --- Initialize reranker ---
        try:
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Cross-encoder reranker loaded successfully.")
        except Exception as e:
            logger.warning("Reranker not initialized (will skip reranking): %s", e)
            self.reranker = None

        # --- Initialize LLMs ---
        try:
            self.llm_fast = ChatOpenAI(
                model=FAST_LLM_MODEL,
                temperature=TEMPERATURE,
                api_key=OPENAI_API_KEY
            )
            self.llm_high = ChatOpenAI(
                model=HIGH_LLM_MODEL,
                temperature=TEMPERATURE,
                api_key=OPENAI_API_KEY
            )
            logger.info("LLMs initialized (fast=%s, high=%s)", FAST_LLM_MODEL, HIGH_LLM_MODEL)
        except Exception as e:
            logger.exception("Failed to initialize LLMs: %s", e)
            self.llm_fast = None
            self.llm_high = None

        # --- Cache Layer ---
        if REDIS_URL:
            self.cache = RedisCache(REDIS_URL, CACHE_TTL_SECONDS)
        else:
            self.cache = TTLCache(ttl_seconds=CACHE_TTL_SECONDS)

        # --- Metrics ---
        self.metrics = {"queries": 0, "cache_hits": 0, "avg_latency_s": 0.0}
        self._metrics_lock = Lock()

    # ------------------------------
    # Adaptive retrieval + reranking
    # ------------------------------
    def _retrieve_and_rerank(self, question: str, k: int, r_min: int = 3, r_max: int = 8) -> List[Dict]:
        """Retrieve top-k docs, rerank them, and adaptively choose how many to return."""
        if not self.vectordb:
            raise RuntimeError("Vector DB not initialized.")

        # Step 1: Retrieve candidates
        try:
            docs_with_scores = self.vectordb.similarity_search_with_score(question, k=k)
        except Exception as e:
            logger.exception("Chroma similarity_search_with_score failed: %s", e)
            docs = self.retriever.get_relevant_documents(question) if self.retriever else []
            return [{"page_content": d.page_content, "metadata": getattr(d, "metadata", {}), "score": 0.0} for d in docs]

        results = [
            {"page_content": doc.page_content, "metadata": getattr(doc, "metadata", {}), "score": float(score)}
            for doc, score in docs_with_scores
        ]

        if not results:
            return []

        # Step 2: Calculate similarity spread
        scores = [r["score"] for r in results]
        spread = max(scores) - min(scores) if len(scores) > 1 else 0.0

        # Step 3: Adaptive top-r
        if spread < 0.05:
            r = r_max
        elif spread < 0.15:
            r = int((r_max + r_min) / 2)
        else:
            r = r_min
        r = min(r, len(results))

        logger.debug("Adaptive retrieval: k=%d, spread=%.4f → r=%d", k, spread, r)

        # Step 4: Optional reranking
        if not self.reranker:
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:r]

        try:
            pairs = [(question, item["page_content"]) for item in results]
            rerank_scores = self.reranker.predict(pairs)
            for i, s in enumerate(rerank_scores):
                results[i]["rerank_score"] = float(s)
            results.sort(key=lambda x: x.get("rerank_score", x["score"]), reverse=True)
        except Exception as e:
            logger.warning("Reranking failed, fallback to raw scores: %s", e)
            results.sort(key=lambda x: x["score"], reverse=True)

        return results[:r]

    # ------------------------------
    # Main query handler
    # ------------------------------
    def answer_query(self, question: str, use_cache: bool = True, k: int = RETRIEVE_K) -> Dict[str, Any]:
        start_total = time.time()
        self._increment_metric("queries")

        if not OPENAI_API_KEY:
            return {"answer": "❌ Missing OpenAI API key.", "sources": []}

        cache_key = self._cache_key(question, k, FAST_LLM_MODEL if not MODEL_TIERING else "tiered")
        if use_cache:
            try:
                cached = self.cache.get(cache_key)
                if cached:
                    self._increment_metric("cache_hits")
                    return cached
            except Exception:
                pass

        try:
            # Step 1: Retrieve adaptively
            t0 = time.time()
            reranked = self._retrieve_and_rerank(question, k=k)
            retrieval_time = time.time() - t0

            if not reranked:
                return {"answer": "No relevant information found.", "sources": []}

            # Step 2: Compute average retrieval confidence
            scores = [r["score"] for r in reranked] or [0.0]
            avg_score = sum(scores) / len(scores)

            # Step 3: Compute reranker confidence
            rerank_conf = 0.0
            if self.reranker:
                try:
                    pairs = [(question, r["page_content"]) for r in reranked]
                    rerank_scores = self.reranker.predict(pairs)
                    mean_conf = sum(rerank_scores) / len(rerank_scores)
                    spread_conf = max(rerank_scores) - min(rerank_scores)
                    rerank_conf = mean_conf - spread_conf
                    logger.debug("Reranker confidence: mean=%.4f, spread=%.4f, eff=%.4f",
                                 mean_conf, spread_conf, rerank_conf)
                except Exception as e:
                    logger.debug("Reranker confidence computation failed: %s", e)

            # Step 4: Choose model based on multi-signal confidence
            use_high = False
            if (MODEL_TIERING and (
                avg_score < MODEL_TIERING_SCORE_THRESHOLD or rerank_conf < 0.15
            )):
                use_high = True

            chosen_llm = self.llm_high if use_high else self.llm_fast
            model_used = "HIGH" if use_high else "FAST"
            logger.debug("Confidence routing → using %s model (retr=%.3f, rerank=%.3f)",
                         model_used, avg_score, rerank_conf)

            # Step 5: Build RetrievalQA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=chosen_llm,
                retriever=self.retriever,
                return_source_documents=True
            )

            # Step 6: Execute query
            t1 = time.time()
            response = qa_chain({"query": question})
            llm_time = time.time() - t1

            answer = response.get("result") or response.get("answer") or ""
            src_docs = response.get("source_documents", [])
            final_sources = []
            for d in src_docs:
                md = getattr(d, "metadata", {}) or {}
                s = md.get("source") or md.get("file_name") or md.get("path")
                if s:
                    final_sources.append(s)

            payload = {
                "answer": answer.strip(),
                "sources": list(dict.fromkeys(final_sources)),
                "model_used": model_used,
                "retrieval_conf": round(avg_score, 4),
                "rerank_conf": round(rerank_conf, 4),
            }

            if use_cache:
                try:
                    self.cache.set(cache_key, payload)
                except Exception:
                    pass

            total_time = time.time() - start_total
            self._update_avg_latency(total_time)
            logger.info("Query handled in %.3fs (retr=%.3fs, llm=%.3fs) model=%s sources=%d",
                        total_time, retrieval_time, llm_time, model_used, len(payload["sources"]))
            
                    # --- Telemetry trace ---
            try:
                self.telemetry.log({
                    "question": question,
                    "model_used": payload.get("model_used", "N/A"),
                    "retrieval_conf": payload.get("retrieval_conf", 0.0),
                    "rerank_conf": payload.get("rerank_conf", 0.0),
                    "latency_s": round(time.time() - start_total, 3),
                    "cache_hit": False if not use_cache else self.cache.get(cache_key) is not None
                })
            except Exception as e:
                logger.debug("Failed to write telemetry trace: %s", e)
            
            

            return payload

        except Exception as e:
            logger.exception("answer_query failed: %s", e)
            return {"answer": "❌ Error processing query.", "sources": []}

        
    # ------------------------------
    # Utility + metrics
    # ------------------------------
    @staticmethod
    def _cache_key(question: str, k: int, model_name: str) -> str:
        payload = {"q": question, "k": k, "m": model_name}
        return json.dumps(payload, sort_keys=True)

    def _increment_metric(self, key: str) -> None:
        with self._metrics_lock:
            self.metrics[key] = self.metrics.get(key, 0) + 1

    def _update_avg_latency(self, latency_s: float) -> None:
        with self._metrics_lock:
            q = self.metrics.get("queries", 1)
            current_avg = self.metrics.get("avg_latency_s", 0.0)
            self.metrics["avg_latency_s"] = ((current_avg * (q - 1)) + latency_s) / q

    def get_metrics(self) -> Dict[str, Any]:
        with self._metrics_lock:
            return dict(self.metrics)



# --- Module-level convenience function kept for backwards compatibility ---
_engine = RAGEngine()


def answer_query(question: str) -> Dict[str, Any]:
    """
    Backwards-compatible wrapper.
    Returns a dict {answer: str, sources: [str]}.
    """
    return _engine.answer_query(question)
