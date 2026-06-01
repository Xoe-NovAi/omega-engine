"""Integration test: Queue → Library → Benchmark workflow."""
import json
import anyio
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _clean_queue():
    qd = DATA_DIR / "requests"
    for d in ["queued", "claimed", "completed", "review", "dead"]:
        p = qd / d
        if p.exists():
            for f in p.iterdir():
                if f.suffix == ".json" and f.name != "INDEX.json":
                    f.unlink()

def _clean_benchmarks():
    p = DATA_DIR / "benchmarks"
    if p.exists():
        for f in p.iterdir():
            f.unlink()

class TestNewSystemsIntegration:
    """End-to-end: enqueue process → library status → benchmark."""

    def test_queue_to_library_pipeline(self):
        """Enqueue a request, complete it, then check stats."""

        async def _run():
            from omega.request_queue import RequestQueue
            _clean_queue()
            q = RequestQueue()

            req = await q.create_queued_request("curate P7 knowledge", priority="P0")
            assert req["id"].startswith("req_"), "Create failed"

            completed = await q.complete_request(req["id"], {"result": "curated"})
            assert completed, "Complete failed"

            stats = await q.stats()
            assert stats["completed"] > 0

        anyio.run(_run)

    def test_benchmark_after_queue(self):
        """Run a benchmark and verify it's persisted and listable."""
        _clean_benchmarks()

        async def _run():
            from omega.benchmarks.runner import BenchmarkRunner
            r = BenchmarkRunner()
            result = await r.run("qwen3-1.7b", "p7_context", samples=5)
            assert result.avg_quality_score > 0

            results = await r.list_runs()
            matching = [x for x in results if x.role == "p7_context"]
            assert len(matching) >= 1

        anyio.run(_run)

    def test_hardware_profile_available(self):
        """Verify hardware detection works (needed by benchmark)."""
        from omega.hardware import detect_hardware
        profile = detect_hardware()
        assert profile.cpu_count >= 1
        assert profile.total_ram_gb > 0
