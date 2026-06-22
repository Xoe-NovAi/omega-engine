# AP Token: AP-ORACLE-RESTORE-v2.3.0
"""Omega Library & Research System — Offline-first knowledge infrastructure.

AP: AP-OMEGA-LIBRARY-v1.0.0
ICS: [NODE: KNOWLEDGE | ARCHETYPE: SOPHIA | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: LIBRARY-SYSTEM]

Submodules:
  inbox.py       — Intake inbox (queues items for processing)
  extractor.py   — Content extraction (web, PDF, RSS, HTML)
  curator.py     — Curation pipeline (quality gates, classification)
  library.py     — Offline library (storage, search, retrieval)
  indexer.py     — Vector + FTS indexing
  research.py    — Multi-depth research engine
  security.py    — SSRF, path traversal, and download size guards (Phase 1 H2-N)
  coordinator.py — Resource-aware background worker coordinator (Phase 2 H2-N)
  rate_limiter.py— Per-domain token bucket rate limiter (Phase 3 H2-N)
  hivemind_bridge.py — Curation event publishing to Hivemind (Phase 4 H2-N)

Data directories (at ~/omega/data/):
  inbox/       — Pending/processing/failed intake items
  library/     — Curated documents, sources, search indices
  research/    — Research outputs
"""

from .inbox import InboxManager, InboxItem, InboxStatus
from .extractor import ContentExtractor, ExtractedContent
from .curator import CurationPipeline, CuratedDocument
from .library import Library
from .indexer import Indexer
from .research import ResearchEngine, ResearchResult
from .security import SSRFGuard, validate_path_scope, validate_download_size
