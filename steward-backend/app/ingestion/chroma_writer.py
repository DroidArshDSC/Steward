import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings


def persist_chunks(
    session_id: str,
    chunks: list,
    persist_dir: str = "data/chroma",
):
    if not chunks:
        raise RuntimeError("No chunks to persist")

    texts = [c["text"] for c in chunks]

    metadatas = [
        {k: v for k, v in c["metadata"].items() if v is not None}
        for c in chunks
    ]

    path = os.path.join(persist_dir, session_id)
    os.makedirs(path, exist_ok=True)

    vectordb = Chroma(
        persist_directory=path,
        embedding_function=OpenAIEmbeddings(),
    )

    vectordb.add_texts(texts=texts, metadatas=metadatas)
    vectordb.persist()
