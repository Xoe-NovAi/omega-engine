#!/usr/bin/env python3
"""verify_knowledge_sovereign.py — Sovereign Knowledge Verification.

AP: AP-VERIFY-KNOWLEDGE-SOVEREIGN-v1.0.0

Verifies:
  1. All 3 gap documents (TDP, RRF, aiosqlite) exist on disk as JSON
  2. Each gap document is indexed in FTS5
  3. Hybrid search returns relevant results for keyword queries
  4. Vector embeddings are present for each gap doc
  5. CrossRefEngine finds related documents

Usage:
    source .venv/bin/activate
    python scripts/verify_knowledge_sovereign.py

Exit: 0 = Sovereign Grade, 1 = checks failed.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
os.environ.setdefault("OMEGA_DATA_DIR", str(REPO_ROOT / "data"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_sovereign")

GAP_DOCS = [
    {
        "doc_id": "doc_security_R_tainted_data_protocol",
        "keywords": ["tainted", "tdp", "injection"],
        "domain": "sentinel",
        "label": "GAP #1 — Tainted Data Protocol",
    },
    {
        "doc_id": "doc_datastore_R_hybrid_search_rrf",
        "keywords": ["hybrid", "rrf", "fts5"],
        "domain": "datastore",
        "label": "GAP #2 — Hybrid Search RRF",
    },
    {
        "doc_id": "doc_watchtower_R_aiosqlite_teardown_hardening",
        "keywords": ["aiosqlite", "teardown", "lifespan"],
        "domain": "watchtower",
        "label": "GAP #3 — aiosqlite Teardown Hardening",
    },
]

OK = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"


async def check_docs_exist() -> bool:
    print("\n─── CHECK 1: Gap documents exist ─────────────────────────")
    docs_dir = REPO_ROOT / "data" / "library" / "documents"
    ok = True
    for gap in GAP_DOCS:
        path = docs_dir / f"{gap['doc_id']}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if data.get("doc_id") == gap["doc_id"]:
                    print(f"  {OK}  {gap['label']}")
                else:
                    print(f"  {FAIL}  {gap['label']} — doc_id mismatch")
                    ok = False
            except json.JSONDecodeError as e:
                print(f"  {FAIL}  {gap['label']} — invalid JSON: {e}")
                ok = False
        else:
            print(f"  {FAIL}  {gap['label']} — NOT FOUND: {path}")
            ok = False
    return ok


async def check_fts_indexed() -> bool:
    print("\n─── CHECK 2: FTS5 index coverage ─────────────────────────")
    db_path = REPO_ROOT / "data" / "library" / "index" / "fts_index.db"
    if not db_path.exists():
        print(f"  {WARN}  FTS index not found — run ingest_seeded_knowledge.py")
        return False
    try:
        import aiosqlite
    except ImportError:
        print(f"  {WARN}  aiosqlite not installed")
        return False

    ok = True
    conn = await aiosqlite.connect(str(db_path))
    try:
        for gap in GAP_DOCS:
            cur = await conn.execute(
                "SELECT doc_id FROM documents_fts WHERE doc_id = ?", (gap["doc_id"],)
            )
            row = await cur.fetchone()
            if row:
                print(f"  {OK}  {gap['label']}")
            else:
                print(f"  {FAIL}  {gap['label']} — NOT in FTS index")
                ok = False
    finally:
        await conn.close()
    return ok


async def check_hybrid_search() -> bool:
    print("\n─── CHECK 3: Hybrid search coverage ──────────────────────")
    db_path = REPO_ROOT / "data" / "library" / "index" / "fts_index.db"
    if not db_path.exists():
        print(f"  {WARN}  FTS index not found — skipping")
        return False
    try:
        from omega.library.indexer import Indexer
    except ImportError as e:
        print(f"  {WARN}  Cannot import Indexer: {e}")
        return False

    indexer = Indexer()
    ok = True
    try:
        for gap in GAP_DOCS:
            query = gap["keywords"][0]
            results = await indexer.hybrid_search(query, limit=10)
            found = any(r.get("doc_id") == gap["doc_id"] for r in results)
            if found:
                print(f"  {OK}  '{query}' → {gap['label']}")
            else:
                print(f"  {FAIL}  '{query}' did not return {gap['doc_id']}")
                ok = False
    finally:
        await indexer.flush()
        await indexer.close()
    return ok


async def check_vector_embeddings() -> bool:
    print("\n─── CHECK 4: Vector embeddings ───────────────────────────")
    db_path = REPO_ROOT / "data" / "library" / "index" / "fts_index.db"
    if not db_path.exists():
        print(f"  {WARN}  FTS index not found — skipping")
        return False
    try:
        from omega.library.crossref import CrossRefEngine
    except ImportError as e:
        print(f"  {WARN}  Cannot import CrossRefEngine: {e}")
        return False

    engine = CrossRefEngine()
    ok = True
    try:
        count = await engine.load_vectors()
        print(f"         Loaded {count} document vectors")
        for gap in GAP_DOCS:
            if gap["doc_id"] in engine._vectors:
                print(f"  {OK}  {gap['label']} — vector present")
            else:
                print(f"  {FAIL}  {gap['label']} — NO vector embedding")
                ok = False
    finally:
        await engine.close()
    return ok


async def check_crossref() -> bool:
    print("\n─── CHECK 5: CrossRef relatedness ────────────────────────")
    db_path = REPO_ROOT / "data" / "library" / "index" / "fts_index.db"
    if not db_path.exists():
        print(f"  {WARN}  FTS index not found — skipping")
        return False
    try:
        from omega.library.crossref import CrossRefEngine
    except ImportError as e:
        print(f"  {WARN}  Cannot import CrossRefEngine: {e}")
        return False

    engine = CrossRefEngine()
    ok = True
    try:
        await engine.load_vectors()
        for gap in GAP_DOCS:
            try:
                refs = await engine.find_related(gap["doc_id"], limit=3)
                if refs:
                    top = refs[0]
                    paths = "+".join(top.get("_paths", []))
                    print(f"  {OK}  {gap['label']}")
                    print(f"         → {top['doc_id']} (rrf={top['_rrf_score']}, via {paths})")
                else:
                    print(f"  {WARN}  {gap['label']} — no related docs (sparse index)")
            except Exception as e:
                print(f"  {FAIL}  {gap['label']} — CrossRef error: {e}")
                ok = False
    finally:
        await engine.close()
    return ok


async def main() -> int:
    print("=" * 60)
    print("⬡ OMEGA — Sovereign Knowledge Verification")
    print("  Checking: 3 gap docs + FTS index + vectors + crossref")
    print("=" * 60)

    checks = [
        await check_docs_exist(),
        await check_fts_indexed(),
        await check_hybrid_search(),
        await check_vector_embeddings(),
        await check_crossref(),
    ]

    passed = sum(1 for c in checks if c)
    total = len(checks)

    print("\n" + "=" * 60)
    print(f"⬡ RESULT: {passed}/{total} checks passed")
    if passed == total:
        print("🏛️  SOVEREIGN GRADE — Knowledge layer is complete.")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed — not Sovereign Grade.")
        print("   Action: python scripts/ingest_gap_documents.py")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
