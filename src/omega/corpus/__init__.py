# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Sovereign Ark Corpus — dedicated embedding library for the local archive.

[D-1024-DIM-NATIVE-20260926] The corpus vector collection is canonical
1024-dim (Qwen3-Embedding-0.6B native). The engine's session corpus is a
SEPARATE documented system at 384 (minilm) and is deliberately NOT
rewritten by this module — one-space-per-collection (Node 1 rule).

Motivation: the early vision and the technical record live on partitions
(omega_vault, omega_library, omega-cut-final) that no engine index covers.
This module gives them a lexical + semantic index so an agent can find
"the 3-Stage Offline Build System" or "the Creative Reclamation principle"
without knowing which partition a file was left on.

Mandates:
- M1  AnyIO only — this module NEVER imports asyncio.
- M2  Engine-Stack Firewall — core infrastructure, no stack/WAD content.
- M7  Local-first — embedding runs on local GGUF. No cloud path exists.
- M23 Failure integrity — no soft-failures; missing embedder is fatal, not
       silently downgraded to hashing.
"""

from .store import CorpusStore
from .chunker import Chunk, chunk_document, extract_text
from .sources import CORPUS_SOURCES, CorpusSource, resolve_sources
from .indexer import CorpusIndexer, IndexReport
from .search import CorpusSearch, SearchHit

__all__ = [
    "CorpusStore",
    "Chunk",
    "chunk_document",
    "extract_text",
    "CORPUS_SOURCES",
    "CorpusSource",
    "resolve_sources",
    "CorpusIndexer",
    "IndexReport",
    "CorpusSearch",
    "SearchHit",
]
