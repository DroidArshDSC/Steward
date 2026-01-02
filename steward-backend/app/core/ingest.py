import os
import time
import glob
from typing import Dict, List

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_BASE_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")

# MVP scope — honest and controllable
SUPPORTED_CODE_EXT = {".py"}
SUPPORTED_DOC_EXT = {".md"}

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}


def _is_excluded(path: str) -> bool:
    parts = path.split(os.sep)
    return any(p in EXCLUDE_DIRS for p in parts)


def _detect_language(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py":
        return "python"
    if ext == ".md":
        return "markdown"
    return "unknown"


def ingest_codebase(root_path: str, session_id: str) -> Dict:
    """
    Deterministically ingest a codebase for a single session.
    Assumes root_path is a directory created by zip/file normalization.
    """
    if not os.path.isdir(root_path):
        raise ValueError(f"Invalid ingestion path: {root_path}")

    if not session_id:
        raise ValueError("session_id is required")

    start_time = time.time()

    persist_dir = os.path.join(CHROMA_BASE_DIR, session_id)

    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )

    patterns = [
        "**/*.py",
        "**/*.md",
    ]

    files: List[str] = []
    for pattern in patterns:
        files.extend(
            glob.glob(os.path.join(root_path, pattern), recursive=True)
        )

    files_seen = set()
    chunks_created = 0

    for path in files:
        if not os.path.isfile(path):
            continue
        if _is_excluded(path):
            continue

        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_CODE_EXT | SUPPORTED_DOC_EXT:
            continue

        try:
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()

            rel_path = os.path.relpath(path, root_path)
            language = _detect_language(path)
            source_type = "code" if ext in SUPPORTED_CODE_EXT else "doc"

            for d in docs:
                d.metadata = {
                    "session_id": session_id,
                    "file_path": rel_path,
                    "language": language,
                    "source_type": source_type,
                }

            chunks = splitter.split_documents(docs)
            vectordb.add_documents(chunks)

            files_seen.add(rel_path)
            chunks_created += len(chunks)

        except Exception as e:
            # Fail soft: ingestion must not die on one bad file
            print(f"⚠️ Skipped {path}: {e}")

    vectordb.persist()

    return {
        "session_id": session_id,
        "files_ingested": len(files_seen),
        "chunks_created": chunks_created,
        "persist_dir": persist_dir,
        "duration_s": round(time.time() - start_time, 2),
    }
