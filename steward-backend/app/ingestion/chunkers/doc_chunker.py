from typing import List, Dict


def chunk_docs(text: str) -> List[Dict]:
    """
    Minimal markdown/doc chunker.
    Splits by double newline.
    Later replace with heading-aware logic.
    """
    chunks = []
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]

    for i, part in enumerate(parts):
        chunks.append({
            "text": part,
            "symbol": f"section_{i+1}",
        })

    return chunks
