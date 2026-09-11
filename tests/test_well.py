#!/usr/bin/env python3
"""Tests for The Well storage invariants (P1.1)."""

from pathlib import Path
import json
import subprocess
import uuid
import unittest
import sys

REPO = Path(__file__).resolve().parents[1]
WELL_DIR = REPO / "gnosis" / "well"
WELL_JSONL = WELL_DIR / "well.jsonl"
WELL_MD = WELL_DIR / "WISDOM.md"
WELL_SCRIPT = REPO / "scripts" / "well_storage.py"


def run_well(*args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(WELL_SCRIPT), *args],
        capture_output=True, text=True, timeout=30, **kwargs
    )


class TestWellStorage(unittest.TestCase):
    def setUp(self):
        """Clean slate for each test."""
        if WELL_JSONL.exists():
            WELL_JSONL.unlink()
        if WELL_MD.exists():
            WELL_MD.unlink()

    def tearDown(self):
        if WELL_JSONL.exists():
            WELL_JSONL.unlink()
        if WELL_MD.exists():
            WELL_MD.unlink()

    def test_well_add_basic(self):
        """Add a record and verify it appears in the JSONL."""
        r = run_well("add", "correction", "harness",
                       "test trigger", "test rule", "test rationale",
                       "--tags", "test,unit", "--pack", "test-pack")
        self.assertEqual(r.returncode, 0, f"add failed: {r.stderr}")
        self.assertTrue(WELL_JSONL.exists())

        # Verify JSONL is valid + record content
        lines = WELL_JSONL.read_text().strip().splitlines()
        self.assertEqual(len(lines), 1)
        rec = json.loads(lines[0])
        self.assertEqual(rec["kind"], "correction")
        self.assertEqual(rec["domain"], "harness")
        self.assertEqual(rec["trigger"], "test trigger")
        self.assertEqual(rec["rule"], "test rule")
        self.assertEqual(rec["rationale"], "test rationale")
        self.assertEqual(rec["tags"], "test,unit")
        self.assertEqual(rec["source_pack"], "test-pack")
        self.assertEqual(rec["status"], "active")
        self.assertEqual(rec["superseded_by"], "")
        # UUID format
        import re
        self.assertRegex(rec["record_id"], r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
        # ISO timestamp
        self.assertTrue(rec["ts"].endswith("Z") and "T" in rec["ts"])

    def test_well_no_secrets(self):
        """Secrets in any field are rejected."""
        # API key pattern
        r = run_well("add", "tip", "other", "trigger",
                     "rule with api_key=sk-shortfakekey", "rationale")
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue("secret" in r.stderr.lower() or "validation" in r.stderr.lower())

        # Password pattern
        r = run_well("add", "tip", "other", "trigger", "rule",
                     "rationale with password=secret123")
        self.assertNotEqual(r.returncode, 0)

        # Token pattern
        r = run_well("add", "tip", "other", "trigger", "rule",
                     "rationale", "--tags", "token=ghp_shortfake")
        self.assertNotEqual(r.returncode, 0)

    def test_well_supersession_resolves(self):
        """Supersession chain resolves correctly."""
        # Add original
        r1 = run_well("add", "correction", "harness", "t1", "rule v1", "rationale", "--pack", "p1")
        self.assertEqual(r1.returncode, 0)
        # Output: "Added <uuid> (kind)" — UUID is second token
        id1 = r1.stdout.strip().split()[1]

        # Add replacement
        r2 = run_well("add", "correction", "harness", "t2", "rule v2", "rationale", "--pack", "p2")
        self.assertEqual(r2.returncode, 0)
        id2 = r2.stdout.strip().split()[1]

        # Supersede
        r3 = run_well("supersede", id1, id2)
        self.assertEqual(r3.returncode, 0, f"supersede failed: {r3.stderr}")

        # Verify both records exist, id1 is superseded, id2 active
        lines = WELL_JSONL.read_text().strip().splitlines()
        self.assertEqual(len(lines), 2)
        recs = {json.loads(l)["record_id"]: json.loads(l) for l in lines}
        self.assertEqual(recs[id1]["status"], "superseded")
        self.assertEqual(recs[id1]["superseded_by"], id2)
        self.assertEqual(recs[id2]["status"], "active")

        # get_active() should only return id2
        r_list = run_well("list", "--status", "active")
        self.assertEqual(r_list.returncode, 0)
        self.assertIn(id2[:8], r_list.stdout)
        self.assertNotIn(id1[:8], r_list.stdout)

        # Superseding non-existent fails gracefully
        r4 = run_well("supersede", str(uuid.uuid4()), id2)
        self.assertNotEqual(r4.returncode, 0)

    def test_well_index_matches_jsonl(self):
        """WISDOM.md render matches the active records in JSONL."""
        # Add records of different kinds
        run_well("add", "correction", "harness", "t1", "fix lint", "why", "--pack", "p1")
        run_well("add", "tip", "local_ai", "t2", "use lru_cache", "why", "--pack", "p2")
        run_well("add", "preference", "harness", "t3", "prefer stdlib", "why", "--pack", "p3")
        run_well("add", "anti_pattern", "harness", "t4", "no bare except", "why", "--pack", "p4")

        # Supersede one
        lines = WELL_JSONL.read_text().strip().splitlines()
        recs = [json.loads(l) for l in lines]
        id_to_supersede = next(r["record_id"] for r in recs if r["rule"] == "fix lint")
        new_id = next(r["record_id"] for r in recs if r["rule"] == "use lru_cache")
        run_well("supersede", id_to_supersede, new_id)

        # Render and verify
        run_well("render-md")
        md = WELL_MD.read_text()

        # WISDOM.md should contain the 3 active records
        self.assertIn("use lru_cache", md)
        self.assertIn("prefer stdlib", md)
        self.assertIn("no bare except", md)
        # Superseded one should NOT appear
        self.assertNotIn("fix lint", md)

# Count lines for each kind section (only kinds with active records appear)
        self.assertNotIn("fix lint", md)  # superseded
        self.assertIn("## Tip (1)", md)
        self.assertIn("## Preference (1)", md)
        self.assertIn("## Anti_pattern (1)", md)
        # Correction section should not exist (0 active)
        self.assertNotIn("## Correction", md)

    def test_well_jsonl_valid_utf8_and_newlines(self):
        """JSONL is valid UTF-8, one JSON object per line, no trailing garbage."""
        run_well("add", "insight", "consciousness", "t",
                 "rule with unicode: café 🧠", "rationale", "--pack", "p1")
        run_well("add", "dream", "games", "t",
                 "dream: flying spaceships", "rationale", "--pack", "p2")

        content = WELL_JSONL.read_bytes()
        # Valid UTF-8
        content.decode("utf-8")
        # Each line is valid JSON
        for i, line in enumerate(content.strip().split(b"\n"), 1):
            json.loads(line)  # raises if invalid
        # No empty lines
        self.assertTrue(all(line.strip() for line in content.strip().split(b"\n")))

    def test_well_stats_counts_match(self):
        """stats() counts match actual records."""
        run_well("add", "correction", "harness", "t1", "r1", "why", "--pack", "p1")
        run_well("add", "correction", "harness", "t2", "r2", "why", "--pack", "p2")
        run_well("add", "tip", "local_ai", "t3", "r3", "why", "--pack", "p3")

        r = run_well("stats")
        self.assertEqual(r.returncode, 0)
        stats = json.loads(r.stdout)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["active"], 3)
        self.assertEqual(stats["superseded"], 0)
        self.assertEqual(stats["by_kind"]["correction"], 2)
        self.assertEqual(stats["by_kind"]["tip"], 1)
        self.assertEqual(stats["by_domain"]["harness"], 2)
        self.assertEqual(stats["by_domain"]["local_ai"], 1)

    def test_make_targets_work(self):
        """The Makefile targets execute without error."""
        # well-stats
        r = subprocess.run(["make", "well-stats"], cwd=REPO, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, f"make well-stats failed: {r.stderr}")
        stats = json.loads(r.stdout)
        self.assertIn("total", stats)

        # well-list
        r = subprocess.run(["make", "well-list"], cwd=REPO, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, f"make well-list failed: {r.stderr}")

        # well-export (renders WISDOM.md)
        r = subprocess.run(["make", "well-export"], cwd=REPO, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, f"make well-export failed: {r.stderr}")
        self.assertTrue(WELL_MD.exists())