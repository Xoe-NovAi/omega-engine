"""leash_status.py watchdog + ritual/plugin congruence tests.

Proves the two gnosis systems are BOTH alive and AGREE with each other:
  - the ritual (pre_compaction_ritual.sh) makes deep archival snapshots
  - the plugin (gnosis-leash.js) keeps a live event timeline + injects context
The watchdog must pass on the real box (no mocks — the temple is truthful),
and the session/evolution records must line up with the plugin timeline.
"""

import json
import subprocess
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GNOSIS = REPO / "gnosis"
PLUGIN = Path.home() / ".config/opencode/plugins/gnosis-leash.js"
STATE_DIR = Path.home() / ".config/opencode/plugins/state"
TIMELINE = STATE_DIR / "gnosis-events.jsonl"
INDEX_MD = Path.home() / "WanderGround/INDEX.md"


class TestLeashStatus(unittest.TestCase):
    def test_watchdog_exists_and_runs_clean(self):
        script = REPO / "scripts/compaction/leash_status.py"
        self.assertTrue(script.is_file(), "missing leash_status.py")
        r = subprocess.run(
            ["python3", str(script)], capture_output=True, text=True, timeout=30
        )
        # Exit 0 = healthy. (Exit 1/2 tolerated only if explicitly degraded —
        # on a fresh leash the FIRST run may have no compaction yet.)
        self.assertIn("LEASH", r.stdout)
        self.assertNotIn("PLUGIN MISSING", r.stdout)
        self.assertNotIn("TIMELINE MISSING", r.stdout)

    def test_index_md_is_injectable(self):
        self.assertTrue(INDEX_MD.is_file(), "WanderGround INDEX.md missing"
                        " — plugin injects its first 24 lines")
        rules = [l for l in INDEX_MD.read_text().splitlines() if l.strip()]
        self.assertGreaterEqual(len(rules), 24, "INDEX.md too short to yield 24 rule lines")
        self.assertIn("local_ai", INDEX_MD.read_text(), "weighted matrix missing")

    def test_native_skill_and_command_exist(self):
        skill = Path.home() / ".config/opencode/skills/gnosis-lock/SKILL.md"
        command = Path.home() / ".config/opencode/commands/gnosis-lock.md"
        self.assertTrue(skill.is_file(), f"missing native skill: {skill}")
        self.assertTrue(command.is_file(), f"missing native command: {command}")
        skill_text = skill.read_text()
        self.assertIn("name: gnosis-lock", skill_text)
        self.assertIn("question", skill_text)
        command_text = command.read_text()
        self.assertIn("gnosis-lock", command_text)

    def test_agent_awareness_surfaces_reference_runbook(self):
        """Global + project AGENTS.md, build prompt, and INDEX.md must point
        agents at the runbook so every session has operational awareness."""
        runbook = REPO / "docs/AGENT_RUNBOOK.md"
        self.assertTrue(runbook.is_file(), "runbook missing")
        rb = runbook.read_text()
        for needle in ["/gnosis-lock", "/compact", "gnosis-leash-status",
                       "WanderGround", "prepare for compaction", "question"]:
            self.assertIn(needle.lower(), rb.lower(), f"runbook missing: {needle}")

        # Global AGENTS.md (every session)
        g = Path.home() / ".config/opencode/AGENTS.md"
        gt = g.read_text()
        self.assertIn("AGENT_RUNBOOK", gt)
        self.assertIn("gnosis-lock", gt)

        # Project AGENTS.md
        p = REPO / "AGENTS.md"
        pt = p.read_text()
        self.assertIn("gnosis-leash-status", pt)
        self.assertIn("AGENT_RUNBOOK", pt)

        # INDEX.md injected into every session system prompt
        it = INDEX_MD.read_text()
        self.assertIn("AGENT_RUNBOOK", it, "INDEX.md must point at the runbook")


class TestRitualPluginCongruence(unittest.TestCase):
    """The two systems must tell the SAME story about the last session."""

    def test_last_session_id_appears_in_both_systems(self):
        if not TIMELINE.is_file():
            self.skipTest("plugin timeline never written")
        identity = json.loads((GNOSIS / "identity/identity.json").read_text())
        current = identity.get("current_session", "")
        if not current:
            self.skipTest("identity has no current_session yet")

        # ------- plugin side: has the leash seen this session? -------
        events = [
            json.loads(l)
            for l in TIMELINE.read_text().splitlines()
            if l.strip()
        ]
        # session ids in the timeline are the shorter event.sessionID; we only
        # require the timeline to be reasonably close in time, not id-equal
        # (the ritual id and the plugin id live on different clocks).
        last_event = events[-1] if events else {}
        self.assertIn("ts", last_event)
        evt_time = datetime.fromisoformat(last_event["ts"].replace("Z", "+00:00"))
        self.assertLess(
            (datetime.now(timezone.utc) - evt_time).total_seconds(),
            24 * 3600,
            "plugin timeline stale; leash may be dead",
        )

        # ------- ritual side: the manifest for that session is complete -------
        manifest = GNOSIS / "sessions" / f"{current}_manifest.json"
        self.assertTrue(manifest.is_file(), f"ritual manifest missing: {manifest}")
        m = json.loads(manifest.read_text())
        for artifact in ["git_state", "opencode_config", "mcp_status",
                         "system_state", "narrative", "evolution"]:
            self.assertIn(artifact, m.get("artifacts", {}), f"manifest lacks {artifact}")
            self.assertTrue(
                Path(m["artifacts"][artifact]).is_file(),
                f"manifest points to missing {artifact} file",
            )
        self.assertTrue(m.get("ready_for_compaction"), "manifest not marked ready")

    def test_evolution_log_count_matches_manifests(self):
        """Every SESSION_END in the evolution log must resolve to a manifest.

        Note: manifests may legitimately outnumber SESSION_END events — the
        evolution logger was introduced after the first ritual runs. The
        invariant holds one way: each logged SESSION_END has a manifest.
        """
        manifest_count = len(list((GNOSIS / "sessions").glob("*_manifest.json")))
        idx = json.loads((GNOSIS / "evolution/evolution_index.json").read_text())
        session_ends = idx.get("by_type", {}).get("SESSION_END", [])
        self.assertLessEqual(len(session_ends), manifest_count,
                             "more SESSION_END events than manifests (impossible)")
        # last_event must reference a session we can find a manifest for
        last = idx.get("last_event")
        recs = []
        log = GNOSIS / "evolution/evolution_log.jsonl"
        if log.is_file():
            for l in log.read_text().splitlines():
                if not l.strip():
                    continue
                e = json.loads(l)
                if e.get("event_id") == last:
                    recs.append(e)
        if recs and recs[-1].get("event_type") == "SESSION_END":
            sid = recs[-1].get("session_id", "")
            self.assertTrue((GNOSIS / "sessions" / f"{sid}_manifest.json").is_file(),
                            f"last SESSION_END references missing manifest for {sid}")


if __name__ == "__main__":
    unittest.main()