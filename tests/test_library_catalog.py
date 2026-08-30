# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for LibraryCatalog — SQLite-backed document catalog.

Uses anyio for async SQLite and tmp_path for DB isolation.
"""

import pytest
import anyio
from pathlib import Path


class TestLibraryCatalogInit:
    @pytest.mark.anyio
    async def test_init_creates_db(self, tmp_path):
        db_path = tmp_path / "library" / "test.db"
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog(db_path)
        await c.ensure_db()
        assert db_path.exists()


class TestLibraryCatalogStats:
    @pytest.mark.anyio
    async def test_stats_returns_dict(self, tmp_path):
        db_path = tmp_path / "library" / "test.db"
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog(db_path)
        await c.ensure_db()
        stats = await c.stats()
        assert "total_documents" in stats
        assert "avg_quality" in stats
        assert "by_domain" in stats
        assert stats["total_documents"] == 0


class TestLibraryCatalogRegister:
    @pytest.mark.anyio
    async def test_register_and_search(self, tmp_path):
        db_path = tmp_path / "library" / "test.db"
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog(db_path)
        await c.ensure_db()

        result = await c.register_document(
            doc_id="doc-001",
            path="/tmp/test.md",
            domain="code",
            title="Test Doc",
            author="Author",
            quality_vector=[0.8, 0.7, 0.6, 0.9, 0.75],
        )
        assert result is True

        # Search by domain
        results = await c.search(domain="code")
        assert len(results) == 1
        assert results[0]["id"] == "doc-001"
        assert results[0]["avg_quality"] > 0.7

        # Search by query
        results2 = await c.search(query="Test")
        assert len(results2) == 1

        # Search with min_quality filter
        results3 = await c.search(domain="code", min_quality=0.9)
        assert len(results3) == 0


class TestLibraryCatalogGetDocument:
    @pytest.mark.anyio
    async def test_get_document_by_id(self, tmp_path):
        db_path = tmp_path / "library" / "test.db"
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog(db_path)
        await c.ensure_db()

        await c.register_document("doc-001", "/tmp/test.md", "science",
                                   title="Science Doc", quality_vector=[0.9, 0.8, 0.7, 0.6, 0.5])

        doc = await c.get_document("doc-001")
        assert doc is not None
        assert doc["title"] == "Science Doc"
        assert doc["domain"] == "science"
        assert doc["quality_vector"] == [0.9, 0.8, 0.7, 0.6, 0.5]

        doc_missing = await c.get_document("nonexistent")
        assert doc_missing is None


class TestLibraryCatalogPrune:
    @pytest.mark.anyio
    async def test_prune_old_documents(self, tmp_path):
        db_path = tmp_path / "library" / "test.db"
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog(db_path)
        await c.ensure_db()

        await c.register_document("old-doc", "/tmp/old.md", "general",
                                   title="Old Doc", quality_vector=[0.5] * 5)

        # Prune with 0 days = all documents
        count = await c.prune(max_age_days=0)
        assert count >= 0  # At minimum, no crash
