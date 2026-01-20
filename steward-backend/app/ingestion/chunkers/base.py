from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class CodeChunk:
    text: str
    symbol_name: str
    symbol_type: str
    start_line: int
    end_line: int
    language: str


class CodeChunker(ABC):

    @abstractmethod
    def chunk(self, code: str) -> List[CodeChunk]:
        pass