# 🔱 Doc Reader — Universal Document Reader
**AP Token**: `AP-DOC-READER-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Doc Reader package — sovereign, local-first document reader supporting multiple formats with metadata extraction.
**Tags**: doc-reader, document, reader, metadata, local-first, formats
**Cross-references**: src/omega/doc_reader/core.py, src/omega/doc_reader/readers.py, src/omega/doc_reader/types.py

---

## Overview

The `doc_reader` package provides a **universal document reader** for the Omega Engine. It supports multiple document formats with metadata extraction, designed for sovereign, local-first operation.

**Supported Formats**: `.docx`, `.pdf`, `.odt`, `.rtf`, `.html`, `.htm`, `.md`, `.txt`, `.json`, `.yaml`, `.yml`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Doc Reader Package                        │
├─────────────────────────────────────────────────────────────┤
│  core.py             │  DocumentReader — main class         │
│  readers.py          │  Format-specific readers (registry)  │
│  types.py            │  DocumentMetadata dataclass          │
│  __init__.py         │  Public exports + convenience funcs  │
└─────────────────────────────────────────────────────────────┘
```

**Reader Registry Pattern**: Each format has a dedicated reader class implementing `BaseReader.read(path) -> (text, metadata)`.

---

## Core Classes

### DocumentReader

Main interface with caching support.

#### Constructor

```python
DocumentReader()
```

#### Methods

##### `read(path: str, use_cache: bool = True) -> str`
Read document and return plain text.

```python
reader = DocumentReader()
text = reader.read("document.pdf")
print(text[:500])
```

##### `read_with_metadata(path: str, use_cache: bool = True) -> Tuple[str, DocumentMetadata]`
Read document and return text with full metadata.

```python
text, metadata = reader.read_with_metadata("report.docx")
print(f"Author: {metadata.author}")
print(f"Created: {metadata.created}")
print(f"Pages: {metadata.page_count}")
print(f"Words: {metadata.word_count}")
```

##### `clear_cache() -> None`
Clear the read cache.

---

### DocumentMetadata

Extracted document metadata.

```python
@dataclass
class DocumentMetadata:
    path: str
    format: str                    # File extension
    size_bytes: int
    word_count: int = 0
    char_count: int = 0
    page_count: Optional[int] = None
    author: Optional[str] = None
    created: Optional[str] = None  # ISO 8601
    modified: Optional[str] = None # ISO 8601
    title: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
```

**Format-specific extra fields**:

| Format | Extra Fields |
|--------|--------------|
| `.docx` | `paragraphs`, `category`, `comments`, `keywords` |
| `.pdf` | `producer`, `creator`, `subject`, `keywords` |
| `.odt` | `paragraphs` |
| `.html` | `has_forms`, `has_tables`, `links`, `images` |
| Others | `{}` |

---

## Format Readers (readers.py)

Each reader handles one format with its own dependencies.

| Reader | Format | Dependency | Install |
|--------|--------|------------|---------|
| `DocxReader` | `.docx` | `python-docx` | `pip install python-docx` |
| `PdfReader` | `.pdf` | `PyMuPDF` (fitz) | `pip install PyMuPDF` |
| `OdtReader` | `.odt` | `odfpy` | `pip install odfpy` |
| `RtfReader` | `.rtf` | `striprtf` | `pip install striprtf` |
| `HtmlReader` | `.html`, `.htm` | `beautifulsoup4` | `pip install beautifulsoup4` |
| `TextReader` | `.md`, `.txt`, `.json`, `.yaml`, `.yml` | stdlib | Built-in |

### BaseReader (Abstract)

```python
class BaseReader(ABC):
    @abstractmethod
    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        """Read document and return text with metadata."""
```

### Registering Custom Readers

```python
from omega.doc_reader import register_reader, BaseReader

class CustomReader(BaseReader):
    def read(self, path: str) -> Tuple[str, DocumentMetadata]:
        # Your implementation
        ...

register_reader(".custom", CustomReader())
```

---

## Convenience Functions

Module-level functions using a shared default reader instance:

```python
from omega.doc_reader import read_document, read_document_with_metadata

# Simple text extraction
text = read_document("report.pdf")

# With metadata
text, metadata = read_document_with_metadata("report.docx")
```

---

## Usage Examples

### Basic Reading

```python
from omega.doc_reader import DocumentReader

reader = DocumentReader()

# Read any supported format
text = reader.read("paper.pdf")
text = reader.read("notes.md")
text = reader.read("data.json")
```

### Metadata Extraction

```python
text, meta = reader.read_with_metadata("contract.docx")

print(f"File: {meta.path}")
print(f"Format: {meta.format}")
print(f"Size: {meta.size_bytes} bytes")
print(f"Words: {meta.word_count}")
print(f"Author: {meta.author}")
print(f"Created: {meta.created}")
print(f"Title: {meta.title}")

# Format-specific extras
if meta.format == ".pdf":
    print(f"Producer: {meta.extra.get('producer')}")
    print(f"Subject: {meta.extra.get('subject')}")
elif meta.format == ".html":
    print(f"Links: {meta.extra.get('links')}")
    print(f"Images: {meta.extra.get('images')}")
```

### Batch Processing

```python
from pathlib import Path

reader = DocumentReader()
docs_dir = Path("documents/")

for doc_path in docs_dir.glob("**/*"):
    if doc_path.suffix.lower() in reader._readers:
        try:
            text, meta = reader.read_with_metadata(str(doc_path))
            # Index for search, store in memory, etc.
            print(f"Indexed: {meta.path} ({meta.word_count} words)")
        except Exception as e:
            print(f"Failed to read {doc_path}: {e}")
```

### Cache Management

```python
reader = DocumentReader()

# First read - caches result
text1 = reader.read("large_doc.pdf")

# Second read - uses cache (fast)
text2 = reader.read("large_doc.pdf")

# Force re-read
text3 = reader.read("large_doc.pdf", use_cache=False)

# Clear cache when done
reader.clear_cache()
```

---

## Error Handling

| Exception | Cause |
|-----------|-------|
| `FileNotFoundError` | Document not found |
| `ValueError` | Unsupported format |
| `ImportError` | Required dependency not installed |
| `RuntimeError` | Reading failed (corrupt file, etc.) |

```python
try:
    text = reader.read("document.xyz")
except ValueError as e:
    print(f"Unsupported: {e}")  # "Unsupported format: .xyz. Supported: ..."
except ImportError as e:
    print(f"Missing dependency: {e}")  # "PyMuPDF not installed. Install with: pip install PyMuPDF"
except RuntimeError as e:
    print(f"Read failed: {e}")
```

---

## Dependencies

**Required** (for full format support):
```bash
pip install python-docx PyMuPDF odfpy striprtf beautifulsoup4
```

**Minimal** (text formats only):
```bash
# No extra dependencies — .md, .txt, .json, .yaml, .yml work out of the box
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | Sync operations; async callers use `anyio.to_thread` |
| **M7 Local-First** | All processing local; no cloud dependencies |
| **M8 Zero Telemetry** | No external analytics |
| **M13 Temple-Grade** | Graceful degradation; clear error messages |
| **M23 Failure Integrity** | Typed exceptions; no silent failures |

---

## Testing

```bash
pytest tests/test_doc_reader.py -v
```

Key test scenarios:
- Each format reader
- Metadata extraction accuracy
- Cache behavior
- Error handling for missing deps
- Custom reader registration

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ DOC_READER-v1.0.0 ⬡ 2026-10-02 ⬡*