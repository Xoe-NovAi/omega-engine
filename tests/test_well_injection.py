#!/usr/bin/env python3
"""End-to-end regression tests for Well injection (P0 hardening, 2026-10-01).

Why this file exists
--------------------
Every existing Well test redirected storage to a `tempfile.TemporaryDirectory()`
in `setUp`, and no test ever executed `gnosis-leash.js`. So on 2026-09-30 a
record with `tags` stored as a JSON array made `readWellForInjection` throw,
the outer catch returned `[]`, and The Well silently injected nothing into every
session on this host — while all 114 tests stayed green.

These tests close that gap in two directions:

  1. They drive the REAL plugin, in node, against a fixture corpus, and assert
     the invariants that were violated (one bad record must not empty the batch;
     `scanned>0 && records===0` must be distinguishable from "no data").
  2. They drive the REAL plugin against the REAL corpus on disk, asserting that
     injection is non-empty — the machine-checkable form of ROADMAP P1.3's
     done-when ("next-session system prompt demonstrably contains Well rules"),
     which had been satisfied only by a human eyeballing it.
"""

from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
PLUGIN = Path.home() / ".config/opencode/plugins/gnosis-leash.js"
WELL_JSONL = REPO / "gnosis" / "well" / "well.jsonl"
WELL_SCRIPT = REPO / "scripts" / "well_storage.py"

NODE = shutil.which("node") or shutil.which("bun")

# Harness imports the real plugin by absolute path and calls the real hook with a
# real-shaped output object, so nothing here reimplements the code under test.
HARNESS = r"""
import process from "node:process";
const mod = await import(process.env.PLUGIN_PATH);
const plugin = await mod.GnosisLeash({
  project: "test", client: {}, $: () => {}, directory: process.cwd(),
});
const hook = plugin["experimental.chat.system.transform"];
const output = { system: ["BASE_SYSTEM_PROMPT"] };
await hook({ sessionID: "test-session", model: {} }, output);
process.stdout.write(JSON.stringify({
  system_length: output.system.length,
  system0: output.system[0],
}));
"""


def run_hook(corpus_dir: Path):
    """Invoke the plugin's system.transform hook against `corpus_dir`."""
    harness = Path(tempfile.mkdtemp()) / "harness.mjs"
    harness.write_text(HARNESS, encoding="utf-8")
    env = {
        **os.environ,
        "PLUGIN_PATH": str(PLUGIN),
        "WELL_DIR_OVERRIDE": str(corpus_dir),
    }
    proc = subprocess.run(
        [NODE, str(harness)], capture_output=True, text=True, timeout=60, env=env
    )
    if proc.returncode != 0:
        raise AssertionError(f"plugin harness failed: {proc.stderr.strip()[:500]}")
    return json.loads(proc.stdout)


def make_record(**over):
    rec = {
        "record_id": "00000000-0000-4000-8000-000000000001",
        "ts": "2026-09-01T00:00:00Z",
        "kind": "correction",
        "source_pack": "test-pack",
        "domain": "harness",
        "trigger": "a trigger",
        "rule": "a rule",
        "rationale": "a rationale",
        "tags": "one,two",
        "status": "active",
        "superseded_by": "",
    }
    rec.update(over)
    return json.dumps(rec, separators=(",", ":"))


class TestWellInjectionResilience(unittest.TestCase):
    """A malformed record must degrade to OMITTED, never to EVERYTHING omitted."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def write(self, lines):
        (self.dir / "well.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_array_tags_do_not_empty_the_batch(self):
        """The 2026-09-30 defect: one array-tagged record killed all injection."""
        self.write([
            make_record(record_id="00000000-0000-4000-8000-00000000000a",
                        ts="2026-09-02T00:00:00Z", rule="GOOD STRING TAGS"),
            make_record(record_id="00000000-0000-4000-8000-00000000000b",
                        ts="2026-09-03T00:00:00Z", rule="ARRAY TAGS RECORD",
                        tags=["x", "y"]),
        ])
        out = run_hook(self.dir)
        self.assertIn("⬡ THE WELL", out["system0"],
                      "Well block missing entirely — the silent-empty regression")
        self.assertIn("ARRAY TAGS RECORD", out["system0"],
                      "array-tagged record was dropped instead of coerced")
        self.assertIn("GOOD STRING TAGS", out["system0"])

    def test_unparseable_line_does_not_empty_the_batch(self):
        self.write([
            make_record(rule="SURVIVOR RECORD"),
            "{ this is not json at all",
        ])
        out = run_hook(self.dir)
        self.assertIn("⬡ THE WELL", out["system0"])
        self.assertIn("SURVIVOR RECORD", out["system0"])

    def test_empty_corpus_yields_no_block(self):
        """An genuinely empty Well must stay silent — not invent a block."""
        self.write([])
        out = run_hook(self.dir)
        self.assertNotIn("⬡ THE WELL", out["system0"])
        # The leash rules block must still be present regardless.
        self.assertIn("GNOSIS LEASH", out["system0"])

    def test_injection_appends_in_place_and_keeps_one_system_message(self):
        """output.system must stay length 1.

        Upstream collapses the system array only when `length > 2`; a push()
        leaves it at 2, so two {role:"system"} messages are emitted and
        OpenAI-compatible providers reject the request (#34243, unmerged).
        """
        self.write([make_record(rule="SINGLE MESSAGE CHECK")])
        out = run_hook(self.dir)
        self.assertEqual(out["system_length"], 1,
                         "system array grew — risks a second system message")
        self.assertTrue(out["system0"].startswith("BASE_SYSTEM_PROMPT"),
                        "original system content must be preserved, not replaced")

    def test_non_injected_domain_is_filtered(self):
        self.write([
            make_record(domain="harness", rule="HARNESS DOMAIN RECORD"),
            make_record(domain="consciousness", rule="CONSCIOUSNESS DOMAIN RECORD"),
        ])
        out = run_hook(self.dir)
        self.assertIn("HARNESS DOMAIN RECORD", out["system0"])
        self.assertNotIn("CONSCIOUSNESS DOMAIN RECORD", out["system0"],
                         "domain filter must hold")


@unittest.skipIf(NODE is None, "node/bun not on PATH — cannot execute the plugin")
class TestWellInjectionAgainstRealCorpus(unittest.TestCase):
    """The gate that was missing: the live corpus must actually inject."""

    def test_real_corpus_injects_records(self):
        if not WELL_JSONL.is_file():
            self.skipTest(f"no corpus at {WELL_JSONL}")
        out = run_hook(WELL_JSONL.parent)
        self.assertIn("⬡ THE WELL", out["system0"],
                      "The Well injected nothing from the real corpus")
        # A non-empty block means the rendered rule text is present.
        self.assertIn("(kind:", out["system0"],
                      "Well block present but carries no record lines")

    def test_real_corpus_passes_the_verify_gate(self):
        proc = subprocess.run(
            ["python3", str(WELL_SCRIPT), "verify"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(proc.returncode, 0,
                         f"well-verify failed on the real corpus:\n{proc.stdout}")


if __name__ == "__main__":
    unittest.main()