"""Repo hygiene tests: README links, Makefile gates, pin-trap guard, async gate.

Run:  python3 -m unittest discover -s tests -v   (from repo root)
All assertions are read-only over the repo — no network, no model calls.
"""

import os
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Linked docs from README + CONTRIBUTING + DEVELOPER_GUIDE
EXPECTED_DOCS = [
    "README.md",
    "CONTRIBUTING.md",
    "docs/GETTING_STARTED.md",
    "docs/ARCHITECTURE.md",
    "docs/DEVELOPER_GUIDE.md",
    "docs/PLUGIN_DEVELOPMENT.md",
    "docs/CODE_QUALITY.md",
    "docs/WANDERGROUND_SPEC.md",
    "docs/SYSTEM_GUIDE.md",
    "docs/HARDWARE.md",
    "docs/AGENT_RUNBOOK.md",
    "docs/GNOSIS_USAGE.md",
    "docs/ROADMAP.md",
    "docs/models/README.md",
    "LICENSE",
]


class TestRepoToc(unittest.TestCase):
    def test_expected_docs_exist(self):
        missing = [d for d in EXPECTED_DOCS if not (REPO / d).is_file()]
        self.assertEqual([], missing, f"missing linked docs: {missing}")

    def test_make_targets_exist(self):
        makefile = (REPO / "Makefile").read_text()
        for tgt in ["docs:", "lint-async:", "test:", "gnosis-lock:", "bench:"]:
            self.assertIn(tgt, makefile, f"target {tgt!r} missing from Makefile")


class TestAsyncGate(unittest.TestCase):
    def test_bare_asyncio_trio_rejected_in_scripts(self):
        """CODE_QUALITY: absolute anyio — bare asyncio/trio must not appear."""
        bad = re.compile(r"^\s*(import|from)\s+(asyncio|trio)\b", re.M)
        hits = []
        for p in (REPO / "scripts").rglob("*.py"):
            for m in bad.finditer(p.read_text()):
                hits.append(f"{p.relative_to(REPO)}:{m.group(0)!r}")
        self.assertEqual([], hits, f"bare asyncio/trio imports: {hits}")

    def test_anyio_advertised_in_code_quality(self):
        doc = (REPO / "docs" / "CODE_QUALITY.md").read_text().lower()
        self.assertIn("anyio", doc)


class TestPinTrap(unittest.TestCase):
    """HARDWARE.md invariant: AllowedCPUs=0-11 + OLLAMA_NUM_THREADS=8."""

    def test_correct_mask_documented_in_hardware_ssot(self):
        hw = (REPO / "docs" / "HARDWARE.md").read_text()
        self.assertIn("AllowedCPUs=0-11", hw)
        self.assertIn("OLLAMA_NUM_THREADS=8", hw)

    def test_threads_in_env_example(self):
        env = (REPO / ".env.ollama.example").read_text()
        self.assertIn("OLLAMA_NUM_THREADS=8", env)

    def test_physical_pcore_only_mask_never_the_recommended_config(self):
        hw = (REPO / "docs" / "HARDWARE.md").read_text()
        env = (REPO / ".env.ollama.example").read_text()
        # The trap mask MAY appear in docs AS the documented anti-pattern (it
        # must be called out), but it must never appear as a live/recommended
        # setting in the env example.
        self.assertNotIn("AllowedCPUs=0,2,4,6,8,10", env)
        self.assertNotIn("OLLAMA_NUM_THREADS=6", env)
        # And the doc must explicitly warn about it (case-insensitive).
        self.assertIn("pin TRAP", hw)
        self.assertRegex(hw, r"(?i)do not narrow")

    def test_lint_script_itself_passes_gates(self):
        from scripts.lint_checks import scan

        self.assertEqual([], scan(), "scripts/lint_checks.py must pass its own gates")


class TestNoTorch(unittest.TestCase):
    def test_torch_ban_in_code_quality(self):
        doc = (REPO / "docs" / "CODE_QUALITY.md").read_text().lower()
        self.assertIn("no torch", doc)


if __name__ == "__main__":
    unittest.main()