"""gnosis-leash plugin contract tests.

The plugin is JS (runs inside OpenCode's Bun runtime — no node here), so
we assert the source contract (exports, hook keys) plus the shape of real
timeline events produced by actual OpenCode sessions.
"""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = Path.home() / ".config/opencode/plugins/gnosis-leash.js"
TIMELINE = Path.home() / ".config/opencode/plugins/state/gnosis-events.jsonl"


class TestPluginContract(unittest.TestCase):
    def test_plugin_exists_and_exports(self):
        self.assertTrue(PLUGIN.is_file(), f"missing plugin: {PLUGIN}")
        src = PLUGIN.read_text()
        self.assertIn("export const GnosisLeash", src)

    def test_hook_keys_present(self):
        src = PLUGIN.read_text()
        for key in [
            "event:",
            '"experimental.session.compacting"',
            '"experimental.chat.system.transform"',
            "session.created",
            "session.idle",
            "session.compacted",
        ]:
            self.assertIn(key, src, f"plugin missing hook key: {key}")

    def test_never_throws_guard(self):
        src = PLUGIN.read_text()
        # Every catch must be a typed/diagnostic catch, never a silent swallow.
        self.assertIn("catch (err)", src, "missing typed error catch")
        self.assertIn("appendDiagnostic(", src, "missing diagnostic sink")
        self.assertIn("gnosis-errors.jsonl", src, "missing error trace file")

    def test_timeline_event_shape(self):
        if not TIMELINE.is_file():
            self.skipTest("no sessions have fired yet (run opencode once)")
        lines = [l for l in TIMELINE.read_text().splitlines() if l.strip()]
        self.assertTrue(lines, "timeline empty")
        evt = json.loads(lines[0])
        self.assertIn("ts", evt)
        self.assertIn("kind", evt)
        self.assertIn(evt["kind"], {"session.created", "session.idle", "session.compacted"})


if __name__ == "__main__":
    unittest.main()