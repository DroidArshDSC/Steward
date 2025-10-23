import os
import glob
import time
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")

def ingest_sources():
    """Lightweight ingestion: picks up markdowns + code, prints files only."""
    start_time = time.time()
    paths = (
        glob.glob("../*.md") +
        glob.glob("docs/**/*.md", recursive=True) +
        glob.glob("app/**/*.py", recursive=True)
    )

    if not paths:
        print("⚠️  No files found for ingestion.")
        return

    print("📂 Files picked for ingestion:\n")

    # Track critical docs
    critical_docs = {"README.md": False, "PRODUCT_BRIEF.md": False}
    added = 0

    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)

    for path in paths:
        try:
            if not os.path.isfile(path):
                continue
            if any(path.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".pdf"]):
                continue

            print(f"   • {path}")
            filename = os.path.basename(path)
            if filename in critical_docs:
                critical_docs[filename] = True

            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            chunks = splitter.split_documents(docs)
            vectordb.add_documents(chunks)
            added += 1

        except Exception as e:
            print(f"   └─ ❌ Failed to process {path}: {e}")
            continue

    vectordb.persist()
    duration = time.time() - start_time

    print(f"\n✅ Ingestion complete. {added} files added in {duration:.2f}s.")
    print(f"📍 Stored at: {CHROMA_PERSIST_DIR}\n")

    # Highlight if important docs are missing
    for doc, found in critical_docs.items():
        if not found:
            print(f"⚠️  Missing critical doc: {doc}")
        else:
            print(f"✔️  Included: {doc}")


if __name__ == "__main__":
    ingest_sources()
