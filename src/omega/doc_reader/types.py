"""Type definitions for document reader."""
# AP: AP-OMEGA-DOC-READER-TYPES-v1.0.0
# ⬡ OMEGA ⬡ DOC_READER_TYPES ⬡ 2026-07-13

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class DocumentMetadata:
    """Extracted document metadata."""

    path: str
    format: str
    size_bytes: int
    word_count: int = 0
    char_count: int = 0
    page_count: Optional[int] = None
    author: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    title: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "format": self.format,
            "size_bytes": self.size_bytes,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "page_count": self.page_count,
            "author": self.author,
            "created": self.created,
            "modified": self.modified,
            "title": self.title,
            "extra": self.extra,
        }
