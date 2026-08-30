# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Core document reader implementation."""
# AP: AP-OMEGA-DOC-READER-CORE-v1.0.0
# ⬡ OMEGA ⬡ DOC_READER_CORE ⬡ 2026-07-13

import os
from pathlib import Path
from typing import Tuple, Dict

from .readers import get_reader, SUPPORTED_FORMATS
from .types import DocumentMetadata


class DocumentReader:
    """Universal document reader with metadata extraction."""

    def __init__(self):
        self._cache: Dict[str, Tuple[str, DocumentMetadata]] = {}
        # Import here to avoid circular import
        from .readers import _READERS

        self._readers = _READERS

    def read(self, path: str, use_cache: bool = True) -> str:
        """Read document and return plain text.

        Args:
            path: Path to document file
            use_cache: Whether to use cached result

        Returns:
            Plain text content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format not supported
        """
        text, _ = self.read_with_metadata(path, use_cache)
        return text

    def read_with_metadata(self, path: str, use_cache: bool = True) -> Tuple[str, DocumentMetadata]:
        """Read document and return text with metadata.

        Args:
            path: Path to document file
            use_cache: Whether to use cached result

        Returns:
            Tuple of (text, metadata)
        """
        path = str(Path(path).resolve())

        if use_cache and path in self._cache:
            return self._cache[path]

        if not os.path.exists(path):
            raise FileNotFoundError(f"Document not found: {path}")

        ext = Path(path).suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {ext}. Supported: {SUPPORTED_FORMATS}")

        reader = get_reader(ext)
        text, metadata = reader.read(path)

        # Calculate basic stats
        metadata.word_count = len(text.split())
        metadata.char_count = len(text)
        metadata.size_bytes = os.path.getsize(path)
        metadata.path = path
        metadata.format = ext

        if use_cache:
            self._cache[path] = (text, metadata)

        return text, metadata

    def clear_cache(self):
        """Clear the read cache."""
        self._cache.clear()


# Module-level convenience functions
_default_reader = DocumentReader()


def read_document(path: str, use_cache: bool = True) -> str:
    """Read document and return plain text.

    Args:
        path: Path to document file
        use_cache: Whether to use cached result

    Returns:
        Plain text content
    """
    return _default_reader.read(path, use_cache)


def read_document_with_metadata(path: str, use_cache: bool = True) -> Tuple[str, DocumentMetadata]:
    """Read document and return text with metadata.

    Args:
        path: Path to document file
        use_cache: Whether to use cached result

    Returns:
        Tuple of (text, metadata)
    """
    return _default_reader.read_with_metadata(path, use_cache)
