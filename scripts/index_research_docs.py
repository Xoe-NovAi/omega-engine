#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Bulk-index research documents into Library FTS5 search index.

Usage:
  OMEGA_DATA_DIR=/path/to/repo/data PYTHONPATH=src python3 scripts/index_research_docs.py

Indexes all docs/research/*.md files (top-level only, skips archive/ subdirectory)
into the Library FTS5 full-text search index at data/library/index/fts_index.db.

Existing documents are skipped (upsert is idempotent by doc_id).
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import List, Optional

import anyio

# ── Ensure src/ is on the path ──
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

# ── Set OMEGA_DATA_DIR if not set ──
if "OMEGA_DATA_DIR" not in os.environ:
    os.environ["OMEGA_DATA_DIR"] = str(REPO_ROOT / "data")

from omega.library.indexer import Indexer
from omega.library.curator import CuratedDocument
from omega.memory.vector_adapters import MemoryVectorAdapter

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ── Configuration ──
RESEARCH_DIR = REPO_ROOT / "docs" / "research"
SKIP_FILES = {"_TEMPLATE.md", "INDEX.md"}  # skip template and index files
SKIP_DIRS = {"archive"}  # skip subdirectories


def derive_domain(file_path: Path, content: str) -> str:
    """Derive domain from file path and content."""
    name = file_path.stem.lower()
    # Check filename keywords
    if any(k in name for k in ("warp", "proxy", "netns", "fast-router", "fastrouter")):
        return "networking"
    if any(k in name for k in ("security", "taint", "pii", "hardening", "sentinel")):
        return "security"
    if any(k in name for k in ("memory", "qdrant", "vector", "embedding", "mnemosyne",
                                 "holographic", "lattice")):
        return "memory"
    if any(k in name for k in ("provider", "model", "gateway", "gemma", "copilot",
                                 "openrouter", "validated")):
        return "providers"
    if any(k in name for k in ("podman", "container", "deploy", "installer")):
        return "infrastructure"
    if any(k in name for k in ("heritage", "id-soft", "doom", "carmack", "extraction")):
        return "heritage"
    if any(k in name for k in ("agent", "fleet", "subagent", "lattice")):
        return "agents"
    if any(k in name for k in ("mcp", "hivemind", "a2a")):
        return "integration"
    if any(k in name for k in ("soul", "distil", "gnosis", "knowledge")):
        return "soul"
    if any(k in name for k in ("search", "firecrawl", "exa", "crawl")):
        return "search"
    if any(k in name for k in ("opencode", "cline", "cli")):
        return "toolchain"
    if any(k in name for k in ("rag", "retrieval", "tri-store", "database")):
        return "storage"
    return "research"


def derive_tags(file_path: Path, content: str) -> List[str]:
    """Extract tags from filename and content."""
    tags = []
    name = file_path.stem.lower()

    tag_keywords = [
        "warp", "proxy", "ftsearch", "hybrid", "rsearch", "security", "heritage",
        "podman", "provider", "memory", "qdrant", "mcp", "agent", "a2a",
        "firecrawl", "search", "embedding", "soul", "gnosis", "id-software",
        "doom", "carmack", "opencode", "fastrouter", "lattice", "subagent",
        "tri-store", "rag", "database", "installer", "copilot", "gemma",
    ]

    for kw in tag_keywords:
        if kw in name:
            tags.append(kw)
    return tags[:5]


def extract_headings(content: str) -> List[str]:
    """Extract markdown headings from content."""
    headings = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            # Strip leading # and whitespace
            heading = line.lstrip("#").strip()
            if heading:
                headings.append(heading)
    return headings


async def main():
    # Use MemoryVectorAdapter as sovereign fallback — avoids Qdrant dependency
    vector_adapter = MemoryVectorAdapter()
    indexer = Indexer(vector_adapter=vector_adapter)

    # ── Dedup FTS5 if needed (FTS5 doesn't support INSERT OR REPLACE) ──
    conn = await indexer._get_fts()
    cur = await conn.execute("SELECT count(*) FROM documents_fts")
    row = await cur.fetchone()
    total_before = row[0]
    cur = await conn.execute("SELECT count(DISTINCT doc_id) FROM documents_fts")
    row = await cur.fetchone()
    distinct_before = row[0]
    if total_before > distinct_before:
        logger.info(f"FTS5 has duplicates ({total_before} rows, {distinct_before} distinct). Rebuilding...")
        # Collect all stored JSON files to re-index from
        documents_dir_check = Path(os.environ.get("OMEGA_DATA_DIR", str(REPO_ROOT / "data"))) / "library" / "documents"
        await conn.execute("DELETE FROM documents_fts")
        await conn.commit()
        reindexed = 0
        for p in sorted(documents_dir_check.glob("*.json")):
            try:
                with open(p) as jf:
                    data = json.load(jf)
                if "doc_id" not in data:
                    continue
                await conn.execute(
                    "INSERT INTO documents_fts (doc_id, title, body, summary, domain, tags) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        data["doc_id"],
                        data.get("title", ""),
                        data.get("body", "")[:100000],
                        data.get("summary", ""),
                        data.get("domain", "general"),
                        " ".join(data.get("tags", [])),
                    ),
                )
                reindexed += 1
            except Exception:
                pass
        await conn.commit()
        logger.info(f"FTS5 rebuilt: {reindexed} documents re-indexed")

    # Also write JSON files so Library.get() can retrieve full documents
    documents_dir = Path(os.environ.get("OMEGA_DATA_DIR", str(REPO_ROOT / "data"))) / "library" / "documents"
    sources_dir = Path(os.environ.get("OMEGA_DATA_DIR", str(REPO_ROOT / "data"))) / "library" / "sources"
    documents_dir.mkdir(parents=True, exist_ok=True)
    sources_dir.mkdir(parents=True, exist_ok=True)

    # Collect all .md files in docs/research/ (top-level only)
    files = sorted(RESEARCH_DIR.glob("*.md"))
    logger.info(f"Found {len(files)} research documents in {RESEARCH_DIR}")

    # Pre-load set of already-indexed doc_ids for skip check
    fts_conn = await indexer._get_fts()
    cur = await fts_conn.execute("SELECT doc_id FROM documents_fts")
    indexed_ids = {row[0] for row in await cur.fetchall()}

    indexed = 0
    skipped = 0
    errors = 0

    for f in files:
        # Skip template and index files
        if f.name in SKIP_FILES:
            logger.info(f"  SKIP (template): {f.name}")
            skipped += 1
            continue

        doc_id = f"research_{f.stem}"

        try:
            content = f.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"  ERROR reading {f.name}: {e}")
            errors += 1
            continue

        # Skip if already indexed (FTS5 doesn't dedup on INSERT OR REPLACE)
        if doc_id in indexed_ids:
            skipped += 1
            continue

        # Extract title from first heading
        title = f.stem.replace("_", " ").replace("-", " ").title()
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                break

        # Extract summary (first non-heading, non-empty, non-frontmatter line)
        summary = ""
        past_frontmatter = False
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped == "---":
                past_frontmatter = not past_frontmatter
                continue
            if past_frontmatter:
                continue
            if stripped and not stripped.startswith("#"):
                summary = stripped[:200]
                break

        if not summary:
            summary = f"Research document: {title}"

        # Extract headings for metadata
        headings = extract_headings(content)

        # Extract links (markdown links)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        link_urls = [url for _, url in links[:30]]

        domain = derive_domain(f, content)
        tags = derive_tags(f, content)

        doc = CuratedDocument(
            doc_id=doc_id,
            source=str(f),
            source_type="markdown",
            title=title,
            body=content,
            summary=summary,
            domain=domain,
            quality_score=0.9,
            author="Sovereign Master Researcher",
            tags=tags,
            headings=headings,
            links=link_urls,
            word_count=len(content.split()),
        )

        try:
            await indexer.index_document(doc)

            # Write JSON storage file for Library.get() retrieval
            json_path = documents_dir / f"{doc_id}.json"
            async with await anyio.open_file(str(json_path), "w") as f:
                await f.write(json.dumps(doc.to_dict(), indent=2, default=str))

            # Write domain link for browse-by-domain
            domain_dir = sources_dir / domain
            domain_dir.mkdir(parents=True, exist_ok=True)
            link_path = domain_dir / f"{doc_id}.json"
            if not link_path.exists():
                async with await anyio.open_file(str(link_path), "w") as f:
                    await f.write(json.dumps({"doc_id": doc_id, "title": title, "domain": domain}, indent=2))

            indexed += 1
            logger.info(f"  OK [{indexed}] {doc_id}: {title[:70]} [{domain}]")
        except Exception as e:
            logger.error(f"  ERROR indexing {doc_id}: {e}")
            errors += 1

    # Final flush
    await indexer.flush()

    # Print summary
    stats = await indexer.stats()
    logger.info("")
    logger.info("=" * 60)
    logger.info("BULK INGESTION COMPLETE")
    logger.info(f"  Indexed:  {indexed}")
    logger.info(f"  Skipped:  {skipped}")
    logger.info(f"  Errors:   {errors}")
    logger.info(f"  FTS5 total docs: {stats.get('fts_documents', 'N/A')}")
    logger.info("=" * 60)

    await indexer.close()


if __name__ == "__main__":
    anyio.run(main)
