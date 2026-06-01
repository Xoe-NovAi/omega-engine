import anyio

class TestLibraryCatalogInit:
    def test_init_creates_db(self):
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog()
        # Just verify it initializes without error

class TestLibraryCatalogStats:
    def test_stats_returns_dict(self):
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog()

        async def _run():
            await c.ensure_db()
            stats = await c.stats()
            assert "total_documents" in stats
            assert "avg_quality" in stats
            assert "by_domain" in stats

        anyio.run(_run)

class TestLibraryCatalogSearch:
    def test_search_returns_list(self):
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog()

        async def _run():
            await c.ensure_db()
            results = await c.search(query="test")
            assert isinstance(results, list)

        anyio.run(_run)
