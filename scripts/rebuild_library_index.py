#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Offline Library FTS5 Index Rebuilder
# AP: AP-REBUILD-LIBRARY-INDEX-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ sovereign ⬡ REBUILD ⬡ CRITICAL
#
# [id-soft: doom-1993] FTS5 Index Rebuild
# Ported from WAD directory rebuild: scan all lumps, rebuild lookup table.
#
# Usage:
#   python scripts/rebuild_library_index.py
#
# Scans all stored documents in the offline library and re-indexes
# them into the SQLite FTS5 full-text search index. Idempotent —
# safe to run multiple times.

import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path for direct script invocation
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
sys.path.insert(0, str(_project_root))

import anyio  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rebuild_index")


async def main() -> int:
    """Rebuild the library FTS5 index from all stored documents."""
    print("=" * 60)
    print("⬡ Omega Engine — Offline Library FTS5 Index Rebuilder")
    print("=" * 60)

    # Lazy import to avoid circulars when running as script
    from omega.library.library import Library  # noqa: E402

    lib = Library()
    doc_count = len(lib._documents)

    if doc_count == 0:
        print("⬡ No documents found in library. Nothing to index.")
        return 0

    print(f"⬡ Found {doc_count} documents. Rebuilding FTS5 index...")

    indexed = 0
    failed = 0
    for doc_id, doc in list(lib._documents.items()):
        try:
            await lib._indexer.index_document(doc)
            indexed += 1
            if indexed % 5 == 0:
                print(f"  ⬡ Progress: {indexed}/{doc_count} indexed...")
        except Exception as exc:
            logger.error("Failed to index %s: %s", doc_id, exc)
            failed += 1

    await lib._indexer.flush()
    stats = await lib._indexer.stats()

    print()
    print("─" * 60)
    print(f"⬡ Rebuild complete.")
    print(f"  ✅ Indexed: {indexed}")
    print(f"  ❌ Failed:  {failed}")
    print(f"  📊 FTS docs: {stats.get('fts_documents', '?')}")
    print(f"  📊 Vectors:  {stats.get('vector_embeddings', '?')}")
    print("=" * 60)

    await lib.close()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(anyio.run(main))
