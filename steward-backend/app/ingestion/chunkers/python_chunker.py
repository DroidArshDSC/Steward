import ast
from typing import List

from app.ingestion.chunkers.base import CodeChunk, CodeChunker


class PythonChunker(CodeChunker):

    def chunk(self, code: str) -> List[CodeChunk]:
        tree = ast.parse(code)
        self._attach_parents(tree)

        lines = code.splitlines()
        chunks: List[CodeChunk] = []

        for node in ast.walk(tree):

            if isinstance(node, ast.ClassDef):
                chunks.append(
                    self._build_chunk(
                        lines, node, node.name, "class"
                    )
                )

            elif isinstance(node, ast.FunctionDef):
                symbol_type = "method" if self._is_method(node) else "function"
                chunks.append(
                    self._build_chunk(
                        lines, node, node.name, symbol_type
                    )
                )

        return chunks

    def _build_chunk(self, lines, node, name, symbol_type) -> CodeChunk:
        start = node.lineno - 1
        end = (node.end_lineno or node.lineno) - 1
        text = "\n".join(lines[start:end + 1])

        return CodeChunk(
            text=text,
            symbol_name=name,
            symbol_type=symbol_type,
            start_line=start + 1,
            end_line=end + 1,
            language="python"
        )

    def _is_method(self, node: ast.FunctionDef) -> bool:
        return isinstance(getattr(node, "parent", None), ast.ClassDef)

    def _attach_parents(self, tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
