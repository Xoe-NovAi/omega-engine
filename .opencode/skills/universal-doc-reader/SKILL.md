<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Universal Document Reader Skill
**AP Token**: `AP-UNIVERSAL-DOC-READER-v1.0.0`
⬡ OMEGA ⬡ SKILL ⬡ UNIVERSAL-DOC-READER ⬡ 2026-07-13

## Purpose
Enable agents to read **any document format** seamlessly: `.docx`, `.pdf`, `.odt`, `.rtf`, `.html`, `.md`, `.txt`, `.json`, `.yaml`, `.yml`.

## Installation
```bash
# Dependencies already installed in .venv:
# python-docx, PyMuPDF, odfpy, striprtf, beautifulsoup4
```

## Usage

### From Agent (bash tool)
```bash
# Read any document
.venv/bin/python scripts/universal_doc_reader.py /path/to/document.docx
.venv/bin/python scripts/universal_doc_reader.py /path/to/report.pdf
.venv/bin/python scripts/universal_doc_reader.py /path/to/notes.odt
.venv/bin/python scripts/universal_doc_reader.py /path/to/page.html
```

### From Python
```python
import subprocess
result = subprocess.run([
    '.venv/bin/python', 'scripts/universal_doc_reader.py', '/path/to/file.docx'
], capture_output=True, text=True)
print(result.stdout)
```

## Supported Formats

| Extension | Library | Notes |
|-----------|---------|-------|
| `.docx` | python-docx | Full paragraph extraction |
| `.pdf` | PyMuPDF (fitz) | Full text extraction |
| `.odt` | odfpy | OpenDocument Text |
| `.rtf` | striprtf | Rich Text Format |
| `.html`/`.htm` | beautifulsoup4 | HTML parsing |
| `.md`/`.txt`/`.json`/`.yaml`/`.yml` | native | Plain text |

## Error Handling
Returns `[FORMAT ERROR: <message>]` on failure — never crashes.

## Agent Integration
Add to agent prompt:
> "Use `.venv/bin/python scripts/universal_doc_reader.py <path>` to read ANY document format."

---

*🔱 OMEGA ⬡ UNIVERSAL-DOC-READER ⬡ SEAMLESS ⬡ 2026-07-13*