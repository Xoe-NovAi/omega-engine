import json
import time
import anyio
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TEST_QUEUE_DIR = DATA_DIR / "requests"

def _clean():
    for d in ["queued", "claimed", "completed", "review", "dead"]:
        p = TEST_QUEUE_DIR / d
        if p.exists():
            for f in p.iterdir():
                if f.suffix == ".json" and f.name != "INDEX.json":
                    f.unlink()

class TestRequestQueue:
    def test_create_queued(self):
        from omega.request_queue import RequestQueue

        async def _run():
            _clean()
            q = RequestQueue()
            req = await q.create_queued_request("test query", priority="P0")
            assert req["id"].startswith("req_")
            assert req["status"] == "queued"

        anyio.run(_run)

    def test_create_review(self):
        from omega.request_queue import RequestQueue

        async def _run():
            _clean()
            q = RequestQueue()
            req = await q.create_review_request("/tmp/test.md")
            assert req["id"].startswith("review_")
            assert req["status"] == "pending_review"

        anyio.run(_run)

    def test_complete_queued_request(self):
        from omega.request_queue import RequestQueue

        async def _run():
            _clean()
            q = RequestQueue()
            req = await q.create_queued_request("test")
            completed = await q.complete_request(req["id"], {"result": "ok"})
            assert completed is True
            stats = await q.stats()
            assert stats["queued"] == 0
            assert stats["completed"] >= 1

        anyio.run(_run)

    def test_stats(self):
        from omega.request_queue import RequestQueue

        async def _run():
            _clean()
            q = RequestQueue()
            stats = await q.stats()
            assert "queued" in stats
            assert "completed" in stats
            assert "pending_review" in stats

        anyio.run(_run)

    def test_prune_stale(self):
        from omega.request_queue import RequestQueue

        async def _run():
            _clean()
            q = RequestQueue()
            await q.create_queued_request("old request")
            await anyio.sleep(0.1)
            pruned = await q.prune_stale(days=0)
            assert pruned >= 1

        anyio.run(_run)
