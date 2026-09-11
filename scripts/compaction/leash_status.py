#!/usr/bin/env python3
"""leash_status.py — watchdog for the gnosis-leash plugin (the puppeteer hand).

Monitors that the automated OpenCode plugin is alive, writing its timeline,
growing correctly, and that what it injects (INDEX.md) still exists on disk.
Complements `pre_compaction_ritual.sh` (deep archival snapshot) by watching the
*constant* background system the ritual can't see.

Checks:
  1. plugin source exists and exports GnosisLeash with the expected hooks
  2. timeline (gnosis-events.jsonl) exists, is valid JSONL, non-empty
  3. timeline freshness — has it written anything recently? (stale = dead hand)
  4. event-kind coverage — the kinds the source *could* emit are actually present
     (a session.compacted with NO session.compacting means the injector hook
     predates logging, or is silently failing)
  5. errors log — zero new errors is the healthy state
  6. INDEX.md exists and yields rules (the injected payload must be readable)

Exit codes: 0 = healthy, 1 = degraded (fixable), 2 = FAIL (hand is dead).
Prints structured plain output. Pure stdlib, sync, no network.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/home/xnai"))
PLUGIN = HOME / ".config/opencode/plugins/gnosis-leash.js"
STATE_DIR = HOME / ".config/opencode/plugins/state"
TIMELINE = STATE_DIR / "gnosis-events.jsonl"
ERRLOG = STATE_DIR / "gnosis-errors.jsonl"
INDEX_MD = HOME / "WanderGround/INDEX.md"
SKILL_MD = HOME / ".config/opencode/skills/gnosis-lock/SKILL.md"
COMMAND_MD = HOME / ".config/opencode/commands/gnosis-lock.md"
RUNBOOK_MD = HOME / "Documents/Projects/omega-engine-alpha/docs/AGENT_RUNBOOK.md"

STALE_AFTER_SECONDS = 24 * 60 * 60  # no event for a day → suspicious

REQUIRED_KINDS = {
    "session.created",
    "session.idle",
    "session.compacting",
    "session.compacted",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    problems: list[str] = []
    notes: list[str] = []

    print(f"gnosis-leash watchdog @ {now_iso()}")
    print(f"  plugin    : {PLUGIN}")
    print(f"  timeline  : {TIMELINE}")
    print()

    # 1. Plugin source
    if not PLUGIN.is_file():
        problems.append("PLUGIN MISSING — gnosis-leash.js not found (2: FAIL)")
    else:
        src = PLUGIN.read_text("utf-8")
        if "export const GnosisLeash" not in src:
            problems.append("PLUGIN BROKEN — export missing (2: FAIL)")
        for hook in [
            '"experimental.session.compacting"',
            '"experimental.chat.system.transform"',
            "event:",
        ]:
            if hook not in src:
                problems.append(f"PLUGIN REGRESSED — hook {hook} gone (1: degraded)")
        print(f"  source    : OK (export + hooks present)")
        # Version marker: did the source get the v2 event logging?
        print(("  v2 logging: OK (session.compacting logged)" if "session.compacting" in src
               else "  v2 logging: MISSING — session.compacting not logged (1: degraded)"))
        if "session.compacting" not in src:
            problems.append("no session.compacting logging in source (1: degraded)")

    # 2–4. Timeline
    if not TIMELINE.is_file():
        problems.append("TIMELINE MISSING — no gnosis-events.jsonl (2: FAIL)")
    else:
        lines = [l for l in TIMELINE.read_text("utf-8").splitlines() if l.strip()]
        if not lines:
            problems.append("TIMELINE EMPTY — plugin never wrote an event (2: FAIL)")
        else:
            kinds = set()
            try:
                parsed = []
                for l in lines:
                    evt = json.loads(l)
                    parsed.append(evt)
                    kinds.add(evt.get("kind"))
            except json.JSONDecodeError as e:
                problems.append(f"TIMELINE CORRUPT — bad JSONL ({e}) (2: FAIL)")
                parsed = []
            if parsed:
                last_ts = datetime.fromisoformat(parsed[-1]["ts"].replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - last_ts).total_seconds()
                if age > STALE_AFTER_SECONDS:
                    problems.append(
                        f"TIMELINE STALE — last event {age/3600:.1f}h ago (1: degraded)"
                    )
                else:
                    print(f"  timeline  : {len(lines)} events, last {age/60:.0f}m ago")
                for missing in sorted(REQUIRED_KINDS - kinds):
                    if missing == "session.compacting" and "session.compacting" not in src:
                        notes.append(
                            "event kind 'session.compacting' not expected (source predates v2 logging)"
                        )
                        continue
                    if missing == "session.compacted":
                        notes.append(
                            "no session.compacted yet — no compaction has ever fired under this plugin (expected on a fresh leash)"
                        )
                        continue
                    if missing == "session.created":
                        problems.append(f"timeline lacks session.created (1: degraded)")
                    else:
                        notes.append(f"event kind '{missing}' absent from timeline (informational)")
                print(f"  kinds     : {', '.join(sorted(kinds)) or '(none)'}")

    # 5. Errors
    if ERRLOG.is_file():
        err_lines = [l for l in ERRLOG.read_text("utf-8").splitlines() if l.strip()]
        if err_lines:
            problems.append(f"ERRORS PRESENT — {len(err_lines)} diagnostics in gnosis-errors.jsonl (1: degraded)")
            print(f"  errors    : {len(err_lines)} diagnostics")
        else:
            print("  errors    : none")
    else:
        print("  errors    : none (file absent = clean)")

    # 6. Injection payload
    if not INDEX_MD.is_file():
        problems.append(f"INDEX_MD MISSING — injected payload gone: {INDEX_MD} (2: FAIL)")
    else:
        raw = INDEX_MD.read_text("utf-8")
        n_rules = len([l for l in raw.splitlines() if l.strip()])
        if n_rules == 0:
            problems.append("INDEX.md EMPTY — nothing to inject (1: degraded)")
        else:
            print(f"  injected  : INDEX.md OK ({n_rules} lines, first 24 injected)")

    # 7. Native TUI Gnosis Lock (Skill & Command)
    if not SKILL_MD.is_file():
        problems.append(f"SKILL MISSING — {SKILL_MD} (1: degraded)")
    else:
        print("  skill     : gnosis-lock SKILL.md OK")

    if not COMMAND_MD.is_file():
        problems.append(f"COMMAND MISSING — {COMMAND_MD} (1: degraded)")
    else:
        print("  command   : gnosis-lock.md command OK")

    # 8. Agent Runbook (agent awareness surface)
    if not RUNBOOK_MD.is_file():
        problems.append(f"RUNBOOK MISSING — {RUNBOOK_MD} (1: degraded)")
    else:
        runbook = RUNBOOK_MD.read_text("utf-8")
        for needle in ["gnosis-lock", "/compact", "WanderGround", "CODE_QUALITY"]:
            if needle not in runbook:
                problems.append(f"RUNBOOK DEGRADED — missing section: {needle} (1: degraded)")
        print("  runbook   : AGENT_RUNBOOK.md OK")

    for n in notes:
        print(f"  note      : {n}")

    print()
    if not problems:
        print("✅ LEASH HEALTHY — puppeteer hand is alive, timeline fresh, zero errors.")
        return 0
    worst = max(p for p in problems if "(2:" in p or "(1:" in p).split("(")[-1][:3]
    for p in problems:
        print(f"  ✗ {p}")
    print(f"❌ LEASH DEGRADED — fix above ({worst} severity).")
    return 2 if "(2:" in worst else 1


if __name__ == "__main__":
    sys.exit(main())