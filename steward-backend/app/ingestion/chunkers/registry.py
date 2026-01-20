from app.ingestion.chunkers.python_chunker import PythonChunker

CODE_CHUNKER_REGISTRY = {
    ".py": PythonChunker()
}