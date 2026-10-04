#!/usr/bin/env python3
"""OpenCode adapter: install rendered WAD souls as OpenCode agents.

THE BOUNDARY (docs/PORTABILITY.md, Well fc3c8c43, D-LIL-006)
-------------------------------------------------------------
OpenCode is a disposable third-party interface. Omega Engine (WADs, MemPalace,
Hivemind) is the platform-agnostic core. This file is the ADAPTER and the only
place allowed to know OpenCode's registration format. Core rendering lives in
`soul_render.py`, which knows nothing about OpenCode — so when the custom Omega
CLI arrives, this file is deleted and replaced, and nothing in the WAD moves.

REGISTRATION CHOSEN: `opencode.json` agent block with
`prompt: "{file:<path>}"` indirection.

Why NOT a markdown agent file (~/.config/opencode/agent/<id>.md):
  1. `prompt:` in frontmatter is SILENTLY IGNORED — the body always wins
     (config/agent.ts does {...md.data, prompt: md.content.trim()}). OpenCode
     issues #26434, #7369, #47616.
  2. `{file:}` is NOT substituted in markdown bodies — only in opencode.json.
     Issue #47616.
  3. With frontmatter prompt + empty body, the agent gets an EMPTY prompt and
     SILENTLY falls back to the default build prompt. No warning. An agent
     that self-identifies as "opencode" instead of its persona.

The `{file:}` form has none of those failure modes: it is a stable pointer,
the prompt file is the real source at runtime, and the config never needs
regenerating when a soul changes. Precedent: researcher_humboldt (live).

DRIFT GATE
----------
Install records each soul's sha256. `agent-souls-verify` fails if a soul
changed without a re-render, or if a rendered prompt went missing or
hand-edited. A hand-edited prompt file is drift: it is overwritten on the next
render, and it silently diverges from the soul in the meantime.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WAD_ENTITIES = REPO_ROOT / "wads" / "arcana_novai" / "entities"

CONFIG_PATH = Path(os.path.expanduser("~/.config/opencode/opencode.json"))
PROMPT_DIR = Path(os.path.expanduser("~/.config/opencode/prompts"))
HASH_RECORD = REPO_ROOT / ".opencode" / "soul-agent-hashes.json"

# Entities this adapter installs. lilith and researcher_humboldt are NOT here:
#   lilith              -> already live as a markdown agent (works; don't touch)
#   researcher_humboldt -> already live via opencode.json + hand-curated prompt
# Adding them here would duplicate a working registration.
TARGETS = ["avgn", "kali", "maat", "sophia"]

MODE = "all"

# Task delegation. Broad-first, specific-last: last matching rule wins
# (docs/OPENCODE_FOUNDATION.md, permission doctrine).
DELEGATE_TO = ["explore", "general"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(entity_id: str) -> str:
    """Render via soul_render so there is exactly one renderer."""
    res = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "soul_render.py"), entity_id],
        capture_output=True, text=True, check=True,
    )
    return res.stdout


def description_for(entity_id: str) -> str:
    """Build the required `description` from the soul — the source of truth."""
    import yaml
    soul = yaml.safe_load((WAD_ENTITIES / entity_id / "soul.yaml").read_text(encoding="utf-8"))
    desc_path = WAD_ENTITIES / entity_id / f"{entity_id}.yaml"
    domains: list[str] = []
    if desc_path.exists():
        d = yaml.safe_load(desc_path.read_text(encoding="utf-8")) or {}
        domains = (d.get("entity", {}) or {}).get("domains", []) or []

    ident = soul.get("identity", {}) or {}
    name = ident.get("keeper", entity_id)
    epithet = ident.get("epithet", "")
    seat = (ident.get("seat") or "").strip()

    lead = f"{name}-N1"
    if epithet:
        lead += f" — {epithet}"
        if not lead.endswith((".", "!", "?")):
            lead += "."
    use = ("Use for " + ", ".join(d.replace('_', ' ') for d in domains[:5]) + "."
           if domains else "")
    if seat and not seat.lower().startswith("none"):
        use += f" Seat: {seat}."
    return (lead + " " + use).strip()


def install(*, dry_run: bool = False) -> int:
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    HASH_RECORD.parent.mkdir(parents=True, exist_ok=True)

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    agents = config.setdefault("agent", {})
    hashes: dict[str, str] = {}

    for eid in TARGETS:
        soul_path = WAD_ENTITIES / eid / "soul.yaml"
        if not soul_path.exists():
            print(f"  SKIP  {eid}: no soul.yaml")
            continue

        prompt = render(eid)
        out = PROMPT_DIR / f"{eid}.md"
        hashes[eid] = sha256(soul_path)

        task = {"*": "deny"}
        for t in DELEGATE_TO:
            task[t] = "allow"

        entry = {
            "mode": MODE,
            "description": description_for(eid),
            "prompt": "{file:" + str(out) + "}",
            "permission": {"task": task},
        }

        if dry_run:
            print(f"  WOULD install {eid} -> {out}")
            print(f"    description: {entry['description'][:100]}")
            continue

        out.write_text(prompt, encoding="utf-8")
        agents[eid] = entry
        print(f"  installed {eid} -> {out} ({len(prompt)} bytes, soul {hashes[eid][:12]})")

    # Prune dead delegation targets from the build allowlist.
    build_task = ((agents.get("build", {}) or {}).get("permission", {}) or {}).get("task")
    if isinstance(build_task, dict):
        live_souls = {p.parent.name for p in WAD_ENTITIES.glob("*/soul.yaml")}
        dead = [k for k, v in build_task.items()
                if v == "allow" and k not in live_souls
                and k not in ("explore", "general", "lilith")]
        for k in dead:
            build_task.pop(k)
            print(f"  pruned dead delegation target: {k}")

    # The new souls must be delegable by build, or they exist but are unreachable.
    if isinstance(build_task, dict):
        for eid in TARGETS:
            if (WAD_ENTITIES / eid / "soul.yaml").exists():
                build_task[eid] = "allow"
        # Re-sort broad-first, specific-last (last match wins).
        ordered = {"*": build_task.pop("*", "deny")}
        ordered.update({k: build_task[k] for k in sorted(build_task)})
        agents["build"]["permission"]["task"] = ordered
        print(f"  build.permission.task -> {json.dumps(ordered)}")

    if dry_run:
        return 0

    backup = CONFIG_PATH.with_suffix(".json.bak-souls")
    backup.write_text(CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    HASH_RECORD.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"  config   -> {CONFIG_PATH} (backup: {backup.name})")
    print(f"  hashes   -> {HASH_RECORD}")
    print("\n  RESTART OPENCODE — a running session keeps its startup config.")
    return 0


def verify() -> int:
    """Drift gate. Non-zero exit means a soul changed without a re-render."""
    if not HASH_RECORD.exists():
        print("FAIL  no hash record — run `make agent-souls` first")
        return 1
    recorded = json.loads(HASH_RECORD.read_text(encoding="utf-8"))
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    agents = config.get("agent", {}) or {}

    failures: list[str] = []

    for eid, rec_hash in sorted(recorded.items()):
        soul_path = WAD_ENTITIES / eid / "soul.yaml"
        if not soul_path.exists():
            failures.append(f"{eid}: soul.yaml deleted but agent still registered")
            continue
        live = sha256(soul_path)
        if live != rec_hash:
            failures.append(
                f"{eid}: soul.yaml changed since render — re-run `make agent-souls` "
                f"(soul {live[:12]} vs recorded {rec_hash[:12]})"
            )
        entry = agents.get(eid)
        if not entry:
            failures.append(f"{eid}: registered hash but absent from opencode.json agent block")
            continue
        m = (entry.get("prompt") or "").strip()
        if not m.startswith("{file:"):
            failures.append(f"{eid}: prompt is not a {{file:}} reference ({m[:40]!r})")
            continue
        target = Path(m[len("{file:"):].rstrip("}"))
        if not target.exists():
            failures.append(f"{eid}: prompt file missing: {target}")
            continue
        expected = render(eid)
        actual = target.read_text(encoding="utf-8")
        if actual != expected:
            failures.append(
                f"{eid}: prompt file is HAND-EDITED or stale — re-run `make agent-souls`"
            )
        if not entry.get("description"):
            failures.append(f"{eid}: description is required for agent discovery")
        if entry.get("mode") not in ("primary", "subagent", "all"):
            failures.append(f"{eid}: invalid mode {entry.get('mode')!r}")

    # No hardcoded model names in the agent block — operator order 2026-10-03.
    for eid, entry in sorted(agents.items()):
        if isinstance(entry, dict) and entry.get("model"):
            failures.append(f"{eid}: agent block pins a model — operator order forbids it")

    print(f"checked {len(recorded)} registered souls")
    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print("PASS: every registered soul renders clean, no drift, no model pins.")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("install", "verify"):
        print("usage: soul_agents_opencode.py install [--dry-run] | verify", file=sys.stderr)
        return 2
    if argv[0] == "verify":
        return verify()
    return install(dry_run="--dry-run" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
