"""Gnosis Lock regressions over real state (read-only).

Verifies the evolution log + identity files are coherent, current, and
valid JSON. Uses the live gnosis/ directory (no mocks — the temple's
actual records must be truthful).
"""

import json
import subprocess
import unittest
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GNOSIS = REPO / "gnosis"


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


class TestEvolutionLog(unittest.TestCase):
    def test_stats_command_runs(self):
        r = subprocess.run(
            ["python3", str(REPO / "scripts/compaction/evolution_log.py"), "stats"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(0, r.returncode, f"stats failed: {r.stderr[-500:]}")

    def test_index_has_events_and_last_is_session_end(self):
        idx = json.loads((GNOSIS / "evolution/evolution_index.json").read_text())
        # Schema: by_session/by_type/by_tag/last_event/total_events/last_updated
        self.assertGreaterEqual(idx["total_events"], 7, "evolution index below expected floor")
        session_ends = idx.get("by_type", {}).get("SESSION_END", [])
        self.assertGreaterEqual(len(session_ends), 4, "fewer SESSION_END events than expected")
        # last_event is an event id — confirm it resolves to a SESSION_END record.
        events = [
            json.loads(l)
            for l in (GNOSIS / "evolution/evolution_log.jsonl").read_text().splitlines()
            if l.strip()
        ]
        by_id = {e["event_id"]: e for e in events}
        self.assertIn(idx["last_event"], by_id, "last_event id not in log")
        self.assertEqual("SESSION_END", by_id[idx["last_event"]]["event_type"])

    def test_identity_current(self):
        ident = json.loads((GNOSIS / "identity/identity.json").read_text())
        self.assertGreaterEqual(ident["session_count"], 17, "identity behind session 17")
        self.assertTrue(ident["current_session"], "current_session missing")
        # last_updated must parse
        parse_iso(ident["last_updated"])

    def test_timeline_command_runs(self):
        r = subprocess.run(
            ["python3", str(REPO / "scripts/compaction/evolution_log.py"), "timeline", "--limit", "20"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(0, r.returncode, f"timeline failed: {r.stderr[-500:]}")
        # Timeline prints ascending; a larger window must contain a SESSION_END.
        self.assertIn("SESSION_END", r.stdout)


if __name__ == "__main__":
    unittest.main()