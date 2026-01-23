import ast
from typing import List, Optional

from app.ingestion.chunkers.base import CodeChunk, CodeChunker


HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options"}


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
                api_info = self._extract_api_info(node)

                if api_info:
                    chunks.append(
                        self._build_api_chunk(
                            lines,
                            node,
                            node.name,
                            api_info
                        )
                    )
                else:
                    symbol_type = "method" if self._is_method(node) else "function"
                    chunks.append(
                        self._build_chunk(
                            lines, node, node.name, symbol_type
                        )
                    )

        return chunks

    # -------------------------
    # Chunk builders
    # -------------------------

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

    def _build_api_chunk(self, lines, node, name, api_info) -> CodeChunk:
        start = node.lineno - 1
        end = (node.end_lineno or node.lineno) - 1
        text = "\n".join(lines[start:end + 1])

        # encode API info into symbol_name deterministically
        api_signature = f"{name} [{','.join(api_info['methods'])} {api_info['route']}]"

        return CodeChunk(
            text=text,
            symbol_name=api_signature,
            symbol_type="api",
            start_line=start + 1,
            end_line=end + 1,
            language="python"
        )

    # -------------------------
    # API detection
    # -------------------------

    def _extract_api_info(self, node: ast.FunctionDef) -> Optional[dict]:
        methods = []
        route = None

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            func = decorator.func

            # matches router.get / app.post etc.
            if isinstance(func, ast.Attribute) and func.attr in HTTP_METHODS:
                methods.append(func.attr.upper())

                # extract route path if static
                if decorator.args:
                    arg = decorator.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        route = arg.value

        if methods:
            return {
                "methods": methods,
                "route": route or "unknown"
            }

        return None

    # -------------------------
    # Utilities
    # -------------------------

    def _is_method(self, node: ast.FunctionDef) -> bool:
        return isinstance(getattr(node, "parent", None), ast.ClassDef)

    def _attach_parents(self, tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
