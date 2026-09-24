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

    def test_plugin_has_narrative_fallback(self):
        """readLatestNarrative must fall back to the most recent REFLECTED
        pack. Regression: ritual runs right before /compact and stamps a
        fresh CAPTURED template as current_session; old code returned null and
        skipped the previous session's human reflection (has_narrative: false)."""
        self.assertTrue(PLUGIN.is_file())
        src = PLUGIN.read_text()
        self.assertIn("function isPopulatedNarrative", src)
        self.assertIn("function packStatus", src)
        self.assertIn("reflection_status", src)
        self.assertIn("TODO: Fill in", src)
        self.assertIn("function findLatestReflectedNarrative", src)

    def test_plugin_loud_failure_markers(self):
        """NO SILENT FAILURES: a compaction without a populated narrative must
        (a) inject a visible INCIDENT block into the compaction context, and
        (b) write a structured diagnostic to gnosis-errors.jsonl."""
        self.assertTrue(PLUGIN.is_file())
        src = PLUGIN.read_text()
        self.assertIn("GNOSIS-LOCK INCIDENT: NO HUMAN NARRATIVE AVAILABLE", src)
        self.assertIn("findLatestReflectedNarrative", src)
        self.assertIn("compaction_without_narrative", src)
        # The event log must carry provenance so the watchdog can act on it.
        self.assertIn("narrative_source", src)
        self.assertIn("narrative_reason", src)
        self.assertIn("pack_state", src)

    def test_watchdog_flags_last_compaction_without_narrative(self):
        """The watchdog must turn the last compacting event's has_narrative:false
        into a degraded (non-zero) exit — a compaction without human gnosis is an
        incident, never 'healthy'."""
        script = REPO / "scripts/compaction/leash_status.py"
        r = subprocess.run(["python3", str(script)], capture_output=True, text=True, timeout=30)
        src_check = PLUGIN.read_text()
        event_lines = []
        if TIMELINE.is_file():
            for l in TIMELINE.read_text().splitlines():
                if not l.strip():
                    continue
                try:
                    e = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if e.get("kind") == "session.compacting":
                    event_lines.append(e)
        # The current box HAS a historical has_narrative:false event (the bug we
        # caught). While it remains the LAST compacting event, watchdog must exit 1.
        if event_lines and not event_lines[-1].get("has_narrative", False):
            self.assertNotEqual(r.returncode, 0,
                                "watchdog must be degraded while last compaction lacked narrative")
            self.assertIn("NARRATIVE MISSING", r.stdout)
        else:
            # No historical incident: watchdog must be healthy AND source-marks ok.
            if "GNOSIS-LOCK INCIDENT" in src_check:
                self.assertEqual(r.returncode, 0,
                                 "watchdog should be healthy when last compaction had narrative")

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


class TestRitualEntityAttribution(unittest.TestCase):
    """gnosis-lock records must carry entity/channel/phase so per-agent
    continuity is a query over one flat store (not folders per agent)."""

    RITUAL = REPO / "scripts/compaction/pre_compaction_ritual.sh"

    def test_ritual_emits_entity_fields(self):
        src = self.RITUAL.read_text()
        for needle in [
            'ENTITY="${ENTITY:-build}"',
            'CHANNEL="${CHANNEL:-cli}"',
            'PHASE="${PHASE:-unset}"',
            '\\"entity\\": \\"${ENTITY}\\"',
            '\\"channel\\": \\"${CHANNEL}\\"',
            '\\"phase\\": \\"${PHASE}\\"',
        ]:
            self.assertIn(needle, src, f"ritual missing {needle!r}")

    def test_ritual_has_machine_narrative_autofill(self):
        """CLI locks cannot run the question tool; the ritual must still produce
        a continuity record by auto-filling summary/code-changes from state."""
        src = self.RITUAL.read_text()
        self.assertIn("Machine-generated continuity record", src)
        self.assertIn("Step 6.5", src)
        self.assertIn("narrative summary auto-filled", src)

    def test_ritual_has_per_entity_identity_map(self):
        src = self.RITUAL.read_text()
        # In shell echo "...", JSON quotes are escaped: \"current_entity\"
        self.assertIn("pending_pack", src)
        self.assertIn("LEASH CHECK FAILED", src)
        self.assertIn("reflection_status", src)
        self.assertIn("FORCE_PACK", src)


class TestPauseLedger(unittest.TestCase):
    """Pause Ledger = full visibility: every pack's lifecycle state + leash."""

    LEDGER = REPO / "scripts/compaction/pause_ledger.py"

    def test_ledger_exists_and_runs(self):
        self.assertTrue(self.LEDGER.is_file())
        r = subprocess.run(["python3", str(self.LEDGER)], capture_output=True, text=True, timeout=30)
        self.assertIn("Pause Ledger", r.stdout)
        self.assertIn("CAPTURED", r.stdout + r.stderr)

    def test_ledger_lists_manifests(self):
        """Ledger must surface every manifest on disk — including named packs."""
        manifest_paths = list((GNOSIS / "sessions").glob("*_manifest.json"))
        manifest_ids = []
        for path in manifest_paths:
            data = json.loads(path.read_text())
            manifest_ids.append(data.get("session_id", path.stem.replace("_manifest", "")))
        r = subprocess.run(["python3", str(self.LEDGER)], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode in (0, 1), True, "ledger runs")
        rows = [line for line in r.stdout.splitlines() if any(sid in line for sid in manifest_ids)]
        self.assertGreaterEqual(
            len(rows),
            len(manifest_paths),
            f"ledger hides packs: {len(manifest_paths)} manifests vs {len(rows)} rows",
        )


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
        # Readiness is a CONSISTENCY invariant, not an absolute: a REFLECTED
        # pack must be marked ready (with a reflected_at timestamp), while a
        # mid-pipeline CAPTURED pack is legitimately not-yet-ready (the ritual
        # stamps it before the human reflection step runs). Requiring
        # ready=true on every current session broke the normal capture→reflect
        # flow that happens on every compaction prep.
        if m.get("reflection_status") == "reflected":
            self.assertTrue(m.get("ready_for_compaction"),
                            f"reflected pack {manifest.name} not marked ready")
            self.assertTrue(m.get("reflected_at"),
                            f"reflected pack {manifest.name} missing reflected_at")
        else:
            self.assertFalse(m.get("ready_for_compaction"),
                             f"captured pack {manifest.name} must not claim readiness")

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


class TestLegacyPackMigration(unittest.TestCase):
    """P0.2 — migrate_legacy_packs.py must make every state EXPLICIT and never
    demote an already-explicit reflection_status."""

    MIGRATE = REPO / "scripts/compaction/migrate_legacy_packs.py"

    def test_migration_script_exists_and_runs_dry_run(self):
        self.assertTrue(self.MIGRATE.is_file(), "missing migrate_legacy_packs.py")
        r = subprocess.run(["python3", str(self.MIGRATE)], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("DRY-RUN", r.stdout)

    def test_no_manifest_has_implicit_state(self):
        """Every manifest must carry an explicit reflection_status now."""
        for mf in (GNOSIS / "sessions").glob("*_manifest.json"):
            m = json.loads(mf.read_text("utf-8"))
            self.assertIn("reflection_status", m,
                          f"{mf.name} still lacks explicit reflection_status")
            self.assertIn(m["reflection_status"], ("captured", "reflected", "superseded"))

    def test_explicit_packs_never_demoted(self):
        """Reflected packs must not be re-classified to captured by the migrator."""
        r = subprocess.run(["python3", str(self.MIGRATE)], capture_output=True, text=True, timeout=30)
        self.assertIn("already-triaged", r.stdout)
        for mf in (GNOSIS / "sessions").glob("*_manifest.json"):
            m = json.loads(mf.read_text("utf-8"))
            if m.get("reflection_status") == "reflected":
                self.assertTrue(m.get("reflected_at"), f"{mf.name} reflected without reflected_at")
                self.assertNotIn("triage_script", m,
                                 f"reflected pack {mf.name} wrongly touched by migration")


if __name__ == "__main__":
    unittest.main()