import os
import zipfile
import tempfile
from collections import defaultdict
from typing import Dict, List

from app.ingestion.chunkers.registry import CODE_CHUNKER_REGISTRY
from app.ingestion.chunkers.doc_chunker import chunk_docs
from app.ingestion.metadata import build_metadata


SUPPORTED_DOC_EXT = {".md", ".rst"}


def ingest_repository(job_id: str, request) -> Dict:
    """
    Orchestrates repo ingestion.
    - Extracts repo
    - Walks files
    - Routes to chunkers
    - Emits structured chunks + summary
    """

    repo_path = _prepare_repo(request)

    chunks: List[Dict] = []
    skipped = defaultdict(int)

    for root, _, files in os.walk(repo_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1]

            # ---- CODE FILES ----
            if ext in CODE_CHUNKER_REGISTRY:
                chunker = CODE_CHUNKER_REGISTRY[ext]
                chunks.extend(
                    _process_code(file_path, request, chunker)
                )

            # ---- DOC FILES ----
            elif ext in SUPPORTED_DOC_EXT:
                chunks.extend(
                    _process_docs(file_path, request)
                )

            # ---- UNSUPPORTED ----
            else:
                skipped[ext or "no_ext"] += 1

    return {
        "job_id": job_id,
        "repo": request.repo_name,
        "chunks_created": len(chunks),
        "files_skipped": dict(skipped),
        "chunks": chunks
    }


# -------------------------
# Helpers
# -------------------------

def _prepare_repo(request) -> str:
    if request.source_type == "zip":
        return _extract_zip(request.source)

    raise NotImplementedError("GitHub ingestion not implemented yet")


def _extract_zip(zip_path: str) -> str:
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(temp_dir)
    return temp_dir


def _process_code(file_path: str, request, chunker) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    raw_chunks = chunker.chunk(code)

    return [
        {
            "text": chunk.text,
            "metadata": build_metadata(
                repo=request.repo_name,
                file_path=file_path,
                symbol=chunk.symbol_name,
                symbol_type=chunk.symbol_type,
                language=chunk.language,
                doc_type="code"
            )
        }
        for chunk in raw_chunks
    ]


def _process_docs(file_path: str, request) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        doc = f.read()

    raw_chunks = chunk_docs(doc)

    return [
        {
            "text": chunk["text"],
            "metadata": build_metadata(
                repo=request.repo_name,
                file_path=file_path,
                symbol=chunk["symbol"],
                symbol_type="section",
                language="markdown",
                doc_type="doc"
            )
        }
        for chunk in raw_chunks
    ]
