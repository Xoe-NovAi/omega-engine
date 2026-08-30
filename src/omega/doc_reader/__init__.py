# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Engine Universal Document Reader.

A sovereign, local-first document reader supporting multiple formats:
.docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml, .yml

AP: AP-OMEGA-DOC-READER-v1.0.0
⬡ OMEGA ⬡ DOC_READER ⬡ 2026-07-13
"""

from .core import (
    DocumentReader,
    read_document,
    read_document_with_metadata,
)
from .types import DocumentMetadata
from .readers import SUPPORTED_FORMATS, get_reader, register_reader

__version__ = "1.0.0"
__all__ = [
    "DocumentReader",
    "read_document",
    "read_document_with_metadata",
    "DocumentMetadata",
    "SUPPORTED_FORMATS",
    "get_reader",
    "register_reader",
]

# Supported formats
SUPPORTED_FORMATS = SUPPORTED_FORMATS
