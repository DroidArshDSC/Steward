from typing import Dict, Optional
import hashlib


def build_metadata(
    repo,
    file_path,
    symbol,
    symbol_type,
    language,
    doc_type,
    chunk_id: str | None = None,
):
    meta = {
        "repo": repo,
        "file_path": file_path,
        "symbol": symbol,
        "symbol_type": symbol_type,
        "language": language,
        "doc_type": doc_type,
    }
    if chunk_id:
        meta["chunk_id"] = chunk_id
    return meta


def _hash_metadata(meta: Dict) -> str:
    """
    Generates a stable hash so identical chunks can be detected later.
    """
    payload = "|".join(
        f"{k}:{meta[k]}"
        for k in sorted(meta.keys())
        if meta[k] is not None
    )

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
