import pytest
import anyio
from pathlib import Path
import tempfile
import json
from src.omega.oracle.dual_write import write_dual, DualWriteEntry

class TestDualWrite:
    @pytest.mark.asyncio
    async def test_dual_write_atomic(self, tmp_path):
        entry = DualWriteEntry(
            canonical_path=tmp_path / "CANONICAL.md",
            active_path=tmp_path / "ACTIVE.md",
            full_content="FULL CONTENT",
            summary="SUMMARY",
            trace_id="test-123"
        )
        await write_dual(entry)
        
        assert (tmp_path / "CANONICAL.md").read_text() == "FULL CONTENT"
        assert (tmp_path / "ACTIVE.md").read_text() == "SUMMARY"
        
        # Verify journal has complete marker
        journal = (tmp_path / ".dual_write_journal.jsonl").read_text()
        assert "complete" in journal

    @pytest.mark.asyncio
    async def test_crash_recovery(self, tmp_path):
        # Simulate crash by writing journal without complete marker
        journal = tmp_path / ".dual_write_journal.jsonl"
        journal.write_text(json.dumps({
            "canonical": str(tmp_path / "CANONICAL.md"),
            "active": str(tmp_path / "ACTIVE.md"),
            "full": "RECOVERED",
            "summary": "RECOVERED_SUMMARY",
            "ts": "2026-01-01T00:00:00",
            "trace": "recovery-test",
            "status": "pending"
        }) + "\n")
        
        # Import and run recovery
        from src.omega.oracle.dual_write import recover_pending_writes
        await recover_pending_writes(tmp_path)
        
        assert (tmp_path / "CANONICAL.md").read_text() == "RECOVERED"
        assert (tmp_path / "ACTIVE.md").read_text() == "RECOVERED_SUMMARY"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
