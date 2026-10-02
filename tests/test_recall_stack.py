#!/usr/bin/env python3
"""End-to-end recall stack verification.

Collected by `make test` (python -m unittest discover -s tests) — this file is
a real unittest.TestCase; a bare module-level function would be silently
invisible to discovery (measured: 0 collected). A completeness meta-test in
test_repo_hygiene.py guards against regressing to that.

Live dependencies: ochist, ocdb-ro on PATH; opencode.db present; skills under
~/.agents/skills. Missing pieces SKIP (skipUnless), they don't fail — the
suite must stay green on machines without the recall stack.

Run directly: .venv/bin/python3 -m unittest tests.test_recall_stack -v
"""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

DB = Path.home() / ".local/share/opencode/opencode.db"
SKILLS = Path.home() / ".agents/skills"
TIMEOUT = 60


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=TIMEOUT
    )


@unittest.skipUnless(shutil.which("ochist"), "ochist not on PATH")
class TestOchistRecall(unittest.TestCase):
    """Layer 1a — ochist grep (the /recall path)."""

    def test_grep_pin_trap_finds_the_pin_trap(self):
        r = run('ochist grep "pin trap" --global --limit 3')
        self.assertEqual(r.returncode, 0, r.stderr)
        # the Well's pin-trap correction must be findable verbatim
        self.assertIn("pin trap", r.stdout)


@unittest.skipUnless(
    shutil.which("ocdb-ro"), "ocdb-ro not on PATH"
)
class TestOcdbRecall(unittest.TestCase):
    """Layer 1b — ocdb-ro read-only SQL (the /db path)."""

    def setUp(self):
        if not DB.is_file():
            self.skipTest(f"opencode.db not found at {DB}")

    def test_search_gnosis(self):
        r = run('ocdb-ro --search "gnosis" --limit 2')
        self.assertEqual(r.returncode, 0, r.stderr)
        # Contract: search finds matching rows. Don't assert the literal
        # appears in stdout — excerpt is substr(text,1,300), so the match
        # may fall beyond char 300 (this assertion was flaky; caught when
        # the file first became collectable).
        rows = json.loads(r.stdout)
        self.assertGreaterEqual(len(rows), 1, "search returned no rows")
        self.assertIn("session", rows[0])

    def test_cost_aggregate(self):
        r = run(
            'ocdb-ro "SELECT ROUND(SUM(cost),2) AS usd, COUNT(*) AS sessions '
            'FROM session"'
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"usd"', r.stdout)

    def test_schema_lookup(self):
        r = run("ocdb-ro --schema part")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CREATE TABLE", r.stdout)

    def test_safety_ddl_blocked(self):
        """SAFETY CONTRACT: ocdb-ro must reject DDL (Well 3becf4f3)."""
        r = run('ocdb-ro "CREATE TABLE evil(x)"')
        self.assertNotEqual(
            r.returncode, 0, "ocdb-ro allowed CREATE TABLE — read-only contract broken"
        )

    def test_safety_dangerous_functions_blocked(self):
        """SAFETY CONTRACT: writefile/load_extension must be rejected (C1)."""
        r = run("ocdb-ro \"SELECT writefile('/tmp/ocdb_test_pwn','x')\"")
        self.assertNotEqual(r.returncode, 0, "ocdb-ro allowed writefile()")
        r = run("ocdb-ro \"SELECT load_extension('/tmp/x')\"")
        self.assertNotEqual(r.returncode, 0, "ocdb-ro allowed load_extension()")


class TestSkillsPresent(unittest.TestCase):
    """Layer 2 — the two recall skills exist where the harness reads them."""

    def test_agent_history_and_opencode_db_skills(self):
        if not SKILLS.is_dir():
            self.skipTest(f"{SKILLS} not present")
        for name in ("agent-history", "opencode-db"):
            self.assertTrue(
                (SKILLS / name / "SKILL.md").is_file(),
                f"missing skill: {name}/SKILL.md",
            )


if __name__ == "__main__":
    unittest.main()
