import pytest
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _clean_benchmarks():
    p = DATA_DIR / "benchmarks"
    if p.exists():
        for f in p.iterdir():
            f.unlink()


class TestBenchmarkRunner:
    def test_imports(self):
        from omega.benchmarks.runner import BenchmarkRunner, BenchmarkResult
        assert BenchmarkRunner is not None
        assert BenchmarkResult is not None

    @pytest.mark.anyio
    async def test_list_runs_empty(self):
        _clean_benchmarks()
        from omega.benchmarks.runner import BenchmarkRunner
        r = BenchmarkRunner()

        results = await r.list_runs()
        assert isinstance(results, list)
        assert len(results) == 0

    @pytest.mark.anyio
    async def test_run_returns_result(self):
        from omega.benchmarks.runner import BenchmarkRunner
        r = BenchmarkRunner()

        result = await r.run("test-model", "test-role", samples=3)
        assert result.model == "test-model"
        assert result.role == "test-role"
        assert result.samples == 3
        assert result.ttft_ms > 0
        assert result.tokens_per_sec > 0
        assert result.peak_ram_mb > 0
        assert "accuracy" in result.scores