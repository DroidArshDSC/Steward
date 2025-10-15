import os
import ast
import time
from dotenv import load_dotenv
from pathlib import Path
from tqdm import tqdm
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

load_dotenv()
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")


# === Markdown Ingestion ===
def load_markdown_docs():
    """
    Loads Markdown documentation from the top-level /docs folder.
    Works regardless of where the script is executed.
    """
    # Three levels up: core → app → steward-backend → project root
    project_root = Path(__file__).resolve().parents[3]
    docs_path = project_root / "docs"

    if not docs_path.exists():
        print(f"⚠️ No docs folder found at {docs_path} — skipping Markdown ingestion.")
        return []

    print(f"📚 Loading Markdown docs from: {docs_path}")
    loader = DirectoryLoader(str(docs_path), glob="**/*.md")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)


# === Code Ingestion ===
def extract_code_docs(directory="."):
    """
    Scans the given directory for Python source files, extracts docstrings
    or representative code snippets, and returns them as LangChain Documents.
    Automatically skips irrelevant or external directories.
    """

    EXCLUDE_DIRS = {
        ".venv", "venv", "__pycache__", "node_modules",
        "site-packages", "dist", "build", ".git"
    }

    code_docs = []

    for root, dirs, files in os.walk(directory):
        # Prevent recursion into excluded folders
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        code = file.read()

                    # Skip overly large files
                    if len(code) > 20000:
                        print(f"⚠️ Skipping {path} (too large: {len(code)} chars)")
                        continue

                    try:
                        tree = ast.parse(code)
                    except SyntaxError:
                        print(f"⚠️ Syntax error while parsing {path}, skipping.")
                        continue

                    found = False
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(node):
                            content = f"{node.name}: {ast.get_docstring(node)}"
                            code_docs.append(Document(page_content=content, metadata={"source": path}))
                            found = True

                    # If no docstrings found, fallback to a small code snippet
                    if not found:
                        snippet = "\n".join(code.splitlines()[:15])
                        code_docs.append(Document(page_content=snippet, metadata={"source": path}))

                except (UnicodeDecodeError, OSError) as e:
                    print(f"⚠️ Skipped {path} (read error: {e})")
                    continue

    print(f"🧠 Extracted {len(code_docs)} code entries from {directory}")
    return code_docs



# === Build VectorDB ===
def build_vector_db():
    md_docs = load_markdown_docs()
    code_docs = extract_code_docs()

    if not code_docs and not md_docs:
        print("⚠️ No code or docs found. Please add Python files or Markdown documents.")
        return

    all_docs = md_docs + code_docs
    print(f"📄 Loaded {len(md_docs)} Markdown docs and 🧠 {len(code_docs)} code entries.")

    embeddings = OpenAIEmbeddings()
    vectordb = None

    batch_size = 500
    for i in tqdm(range(0, len(all_docs), batch_size), desc="Embedding batches"):
        batch = all_docs[i:i + batch_size]
        try:
            vectordb = Chroma.from_documents(
                batch,
                embeddings,
                persist_directory=CHROMA_PERSIST_DIR
            )
            #vectordb.persist()
            time.sleep(0.5)  # gentle rate limit
        except Exception as e:
            print(f"⚠️ Skipped batch {i // batch_size} due to error: {e}")
            continue

    print("✅ Steward knowledge base built successfully!")


if __name__ == "__main__":
    build_vector_db()
