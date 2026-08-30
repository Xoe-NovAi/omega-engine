# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Document format readers for UniversalDocReader."""
# AP: AP-OMEGA-DOC-READER-READERS-v1.0.0
# ⬡ OMEGA ⬡ DOC_READER_READERS ⬡ 2026-07-13

import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Tuple

from .types import DocumentMetadata


class BaseReader(ABC):
    """Base class for document readers."""

    @abstractmethod
    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        """Read document and return text with metadata."""
        pass


class DocxReader(BaseReader):
    """Microsoft Word .docx reader using python-docx."""

    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        try:
            import docx

            doc = docx.Document(path)

            paragraphs = [p.text for p in doc.paragraphs]
            text = "\n".join(paragraphs)

            core_props = doc.core_properties
            metadata = DocumentMetadata(
                path=path,
                format=".docx",
                size_bytes=os.path.getsize(path),
                author=core_props.author or None,
                created=core_props.created.isoformat() if core_props.created else None,
                modified=core_props.modified.isoformat() if core_props.modified else None,
                title=core_props.title or None,
                extra={
                    "paragraphs": len(paragraphs),
                    "category": core_props.category or None,
                    "comments": core_props.comments or None,
                    "keywords": core_props.keywords or None,
                },
            )
            return text, metadata

        except ImportError:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")
        except Exception as e:
            raise RuntimeError(f"Failed to read DOCX: {e}")


class PdfReader(BaseReader):
    """PDF reader using PyMuPDF (fitz)."""

    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(path)

            pages_text = [page.get_text() for page in doc]
            text = "\n".join(pages_text)

            pdf_meta = doc.metadata
            metadata = DocumentMetadata(
                path=path,
                format=".pdf",
                size_bytes=os.path.getsize(path),
                page_count=doc.page_count,
                author=pdf_meta.get("author") or None,
                created=pdf_meta.get("creationDate") or None,
                modified=pdf_meta.get("modDate") or None,
                title=pdf_meta.get("title") or None,
                extra={
                    "producer": pdf_meta.get("producer"),
                    "creator": pdf_meta.get("creator"),
                    "subject": pdf_meta.get("subject"),
                    "keywords": pdf_meta.get("keywords"),
                },
            )
            return text, metadata

        except ImportError:
            raise ImportError("PyMuPDF not installed. Install with: pip install PyMuPDF")
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF: {e}")


class OdtReader(BaseReader):
    """OpenDocument Text .odt reader using odfpy."""

    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        try:
            from odf.opendocument import load
            from odf import text, teletype, meta

            doc = load(path)

            paragraphs = [teletype.extractText(p) for p in doc.getElementsByType(text.P)]
            text = "\n".join(paragraphs)

            meta_elem = doc.meta

            def safe_get(attr):
                try:
                    return meta_elem.getAttribute(attr) if meta_elem else None
                except (ValueError, KeyError):
                    return None

            metadata = DocumentMetadata(
                path=path,
                format=".odt",
                size_bytes=os.path.getsize(path),
                author=safe_get("meta:author"),
                created=safe_get("meta:creation-date"),
                modified=safe_get("meta:editing-duration"),
                title=safe_get("dc:title"),
                extra={
                    "paragraphs": len(paragraphs),
                },
            )
            return text, metadata

        except ImportError:
            raise ImportError("odfpy not installed. Install with: pip install odfpy")
        except Exception as e:
            raise RuntimeError(f"Failed to read ODT: {e}")


class RtfReader(BaseReader):
    """Rich Text Format .rtf reader using striprtf."""

    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        try:
            from striprtf.striprtf import rtf_to_text

            with open(path, "r") as f:
                content = f.read()
            text = rtf_to_text(content)

            metadata = DocumentMetadata(
                path=path, format=".rtf", size_bytes=os.path.getsize(path), extra={}
            )
            return text, metadata

        except ImportError:
            raise ImportError("striprtf not installed. Install with: pip install striprtf")
        except Exception as e:
            raise RuntimeError(f"Failed to read RTF: {e}")


class HtmlReader(BaseReader):
    """HTML reader using BeautifulSoup."""

    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        try:
            from bs4 import BeautifulSoup

            with open(path, "r") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            text = soup.get_text()

            title_tag = soup.find("title")
            metadata = DocumentMetadata(
                path=path,
                format=".html",
                size_bytes=os.path.getsize(path),
                title=title_tag.get_text() if title_tag else None,
                extra={
                    "has_forms": bool(soup.find("form")),
                    "has_tables": bool(soup.find("table")),
                    "links": len(soup.find_all("a")),
                    "images": len(soup.find_all("img")),
                },
            )
            return text, metadata

        except ImportError:
            raise ImportError(
                "beautifulsoup4 not installed. Install with: pip install beautifulsoup4"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to read HTML: {e}")


class TextReader(BaseReader):
    """Plain text reader for .md, .txt, .json, .yaml, .yml"""

    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        try:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(path, "r", encoding="latin-1") as f:
                    text = f.read()

            ext = Path(path).suffix.lower()
            metadata = DocumentMetadata(
                path=path, format=ext, size_bytes=os.path.getsize(path), extra={}
            )
            return text, metadata

        except Exception as e:
            raise RuntimeError(f"Failed to read text file: {e}")


# Reader registry
_READERS = {
    ".docx": DocxReader(),
    ".pdf": PdfReader(),
    ".odt": OdtReader(),
    ".rtf": RtfReader(),
    ".html": HtmlReader(),
    ".htm": HtmlReader(),
    ".md": TextReader(),
    ".txt": TextReader(),
    ".json": TextReader(),
    ".yaml": TextReader(),
    ".yml": TextReader(),
}

SUPPORTED_FORMATS = tuple(sorted(_READERS.keys()))


def get_reader(extension: str) -> BaseReader:
    """Get reader for extension."""
    ext = extension.lower()
    if ext not in _READERS:
        raise ValueError(f"No reader for format: {ext}")
    return _READERS[ext]


def register_reader(extension: str, reader: BaseReader):
    """Register custom reader."""
    _READERS[extension.lower()] = reader
