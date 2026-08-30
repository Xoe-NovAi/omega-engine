#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""ingest_gap_documents.py — Seed the 3 S2-C semantic gap docs into FTS5 + vector store.

AP: AP-INGEST-GAP-DOCS-v1.0.0

Reads the 3 JSON library documents created in S2-C and ingests them into:
  - FTS5 index (via Indexer.index_document)
  - In-memory vector store (via MemoryVectorAdapter, embedded at index time)

Usage:
    source .venv/bin/activate
    python scripts/ingest_gap_documents.py
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
os.environ.setdefault("OMEGA_DATA_DIR", str(REPO_ROOT / "data"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_gap_docs")

GAP_DOC_FILES = [
    "doc_security_R_tainted_data_protocol.json",
    "doc_datastore_R_hybrid_search_rrf.json",
    "doc_watchtower_R_aiosqlite_teardown_hardening.json",
]


async def main() -> int:
    from omega.library.indexer import Indexer
    from omega.library.curator import CuratedDocument

    docs_dir = REPO_ROOT / "data" / "library" / "documents"
    indexer = Indexer()
    ingested = 0

    print("⬡ Ingesting S2-C gap documents into FTS5 + vector store...")

    for filename in GAP_DOC_FILES:
        path = docs_dir / filename
        if not path.exists():
            logger.error(f"Gap document not found: {path}")
            print(f"  ❌ {filename} — NOT FOUND")
            continue

        try:
            data = json.loads(path.read_text())

            doc = CuratedDocument(
                doc_id=data["doc_id"],
                source=data.get("source", str(path)),
                source_type=data.get("source_type", "sovereign_source"),
                title=data["title"],
                body=data["body"],
                summary=data["summary"],
                domain=data.get("domain", "general"),
                quality_score=data.get("quality_score", 0.9),
                tags=data.get("tags", []),
                author=data.get("author", "Antigravity-IDE"),
                published_date=data.get("curated_at", datetime.utcnow().isoformat()),
                word_count=data.get("word_count", len(data["body"].split())),
                curated_at=data.get("curated_at", datetime.utcnow().isoformat()),
            )

            await indexer.index_document(doc)
            ingested += 1
            print(f"  ✅ {data['doc_id']} [{data.get('domain', 'general')}]")

        except Exception as e:
            logger.error(f"Failed to ingest {filename}: {e}", exc_info=True)
            print(f"  ❌ {filename} — ERROR: {e}")

    await indexer.flush()
    await indexer.close()

    stats_msg = f"\nIngestion complete: {ingested}/{len(GAP_DOC_FILES)} documents indexed."
    print(stats_msg)
    logger.info(stats_msg)
    return 0 if ingested == len(GAP_DOC_FILES) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
