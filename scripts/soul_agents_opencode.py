#!/usr/bin/env python3
"""OpenCode adapter: install rendered WAD souls as OpenCode agents.

THE BOUNDARY (docs/PORTABILITY.md, Well fc3c8c43, D-LIL-006)
-------------------------------------------------------------
OpenCode is a disposable third-party interface. Omega Engine (WADs, MemPalace,
Hivemind) is the platform-agnostic core. This file is the ADAPTER and the only
place allowed to know OpenCode's registration format. Core rendering lives in
`soul_render.py`, which knows nothing about OpenCode — so when the custom Omega
CLI arrives, this file is deleted and replaced, and nothing in the WAD moves.

REGISTRATION CHOSEN: `opencode.json` agents block with
`system: "{file:<path>}"` indirection (V2 native).

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

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from omega.governance.config_resolver import WADS_DIR  # noqa: E402

DEFAULT_WAD = "arcana_novai"
WAD_ENTITIES = WADS_DIR / DEFAULT_WAD / "entities"

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


def resolve_entities_dir(wad: Optional[str] = None, wads_dir: Optional[Path] = None) -> Path:
    base = Path(wads_dir) if wads_dir is not None else WADS_DIR
    return base / (wad or DEFAULT_WAD) / "entities"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(entity_id: str, wad: Optional[str] = None, wads_dir: Optional[Path] = None) -> str:
    """Render via soul_render so there is exactly one renderer."""
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "soul_render.py"), entity_id]
    if wad:
        cmd.extend(["--wad", wad])
    if wads_dir is not None:
        cmd.extend(["--wads-dir", str(wads_dir)])
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout


def description_for(
    entity_id: str, wad: Optional[str] = None, wads_dir: Optional[Path] = None
) -> str:
    """Build the required `description` from the soul — the source of truth."""
    import yaml

    entities_dir = resolve_entities_dir(wad=wad, wads_dir=wads_dir)
    soul = yaml.safe_load((entities_dir / entity_id / "soul.yaml").read_text(encoding="utf-8")) or {}
    desc_path = entities_dir / entity_id / f"{entity_id}.yaml"
    domains: list[str] = []
    if desc_path.exists():
        d = yaml.safe_load(desc_path.read_text(encoding="utf-8")) or {}
        domains = (d.get("entity", {}) or {}).get("domains", []) or []

    ident = soul.get("identity") or soul.get("entity") or {}
    name = ident.get("keeper") or ident.get("name") or ident.get("id") or entity_id
    epithet = ident.get("epithet") or ident.get("archetype") or ""
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


def install(
    *, dry_run: bool = False, wad: Optional[str] = None, wads_dir: Optional[Path] = None
) -> int:
    entities_dir = resolve_entities_dir(wad=wad, wads_dir=wads_dir)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    HASH_RECORD.parent.mkdir(parents=True, exist_ok=True)

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    # Self-migration: V1 "agent" → V2 "agents".
    if "agent" in config and "agents" not in config:
        config["agents"] = config.pop("agent")
    # Clean up V1 top-level keys that have V2 equivalents or are inert.
    config.pop("permission", None)   # V1 → V2 defaults (* * allow)
    config.pop("tools", None)        # V1 → V2 defaults (* * allow)
    config.pop("subagent_depth", None)  # V1 → experimental.subagent_depth
    if isinstance(config.get("compaction"), dict):
        config["compaction"].pop("prune", None)
        config["compaction"].pop("tail_turns", None)
    agents = config.setdefault("agents", {})
    hashes: dict[str, str] = {}

    for eid in TARGETS:
        soul_path = entities_dir / eid / "soul.yaml"
        if not soul_path.exists():
            print(f"  SKIP  {eid}: no soul.yaml")
            continue

        prompt = render(eid, wad=wad, wads_dir=wads_dir)
        out = PROMPT_DIR / f"{eid}.md"
        hashes[eid] = sha256(soul_path)

        task = {"*": "deny"}
        for t in DELEGATE_TO:
            task[t] = "allow"

        # V2 native: permissions array with action "subagent".
        permissions = [{"action": "subagent", "resource": r, "effect": e} for r, e in task.items()]
        entry = {
            "mode": MODE,
            "description": description_for(eid, wad=wad, wads_dir=wads_dir),
            "system": "{file:" + str(out) + "}",
            "permissions": permissions,
        }

        if dry_run:
            print(f"  WOULD install {eid} -> {out}")
            print(f"    description: {entry['description'][:100]}")
            continue

        out.write_text(prompt, encoding="utf-8")
        agents[eid] = entry
        print(f"  installed {eid} -> {out} ({len(prompt)} bytes, soul {hashes[eid][:12]})")

    # Prune dead delegation targets from the build allowlist.
    # V2: read subagent permissions from the permissions array.
    build_perms = (agents.get("build", {}) or {}).get("permissions", []) or []
    # Self-migrate V1 permission.task → V2 permissions array.
    if not build_perms and isinstance((agents.get("build", {}) or {}).get("permission", {}), dict):
        v1_task = (agents.get("build", {}) or {}).get("permission", {}).get("task", {})
        if isinstance(v1_task, dict):
            build_perms = [{"action": "subagent", "resource": r, "effect": e} for r, e in v1_task.items()]
            # Remove V1 key.
            if "permission" in (agents.get("build", {}) or {}):
                del agents["build"]["permission"]
    # Extract subagent task dict from permissions array.
    build_task = {}
    for p in build_perms:
        if p.get("action") == "subagent":
            build_task[p.get("resource", "*")] = p.get("effect", "deny")
    if "*" not in build_task:
        build_task["*"] = "deny"
    if build_task:
        live_souls = {p.parent.name for p in entities_dir.glob("*/soul.yaml")}
        dead = [k for k, v in build_task.items()
                if v == "allow" and k not in live_souls
                and k not in ("explore", "general", "lilith")]
        for k in dead:
            build_task.pop(k)
            print(f"  pruned dead delegation target: {k}")

    # The new souls must be delegable by build, or they exist but are unreachable.
    if build_task:
        for eid in TARGETS:
            if (entities_dir / eid / "soul.yaml").exists():
                build_task[eid] = "allow"
        # Re-sort broad-first, specific-last (last match wins).
        ordered = {"*": build_task.pop("*", "deny")}
        ordered.update({k: build_task[k] for k in sorted(build_task)})
        # Rebuild permissions array: remove old subagent entries, append new ones.
        build_perms = [p for p in build_perms if p.get("action") != "subagent"]
        for resource, effect in ordered.items():
            build_perms.append({"action": "subagent", "resource": resource, "effect": effect})
        if "build" not in agents:
            agents["build"] = {}
        agents["build"]["permissions"] = build_perms
        print(f"  build.permissions (subagent) -> {json.dumps(ordered)}")

    # Set default model, default agent, and experimental flags (V2 native).
    config["model"] = "opencode/big-pickle"
    config["default_agent"] = "lilith"
    config.setdefault("experimental", {})
    config["experimental"]["subagent_depth"] = 2
    config["experimental"]["todo"] = True

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


def verify(*, wad: Optional[str] = None, wads_dir: Optional[Path] = None) -> int:
    """Drift gate. Non-zero exit means a soul changed without a re-render."""
    entities_dir = resolve_entities_dir(wad=wad, wads_dir=wads_dir)
    if not HASH_RECORD.exists():
        print("FAIL  no hash record — run `make agent-souls` first")
        return 1
    recorded = json.loads(HASH_RECORD.read_text(encoding="utf-8"))
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    # V2: read from "agents" key.
    agents = config.get("agents", {}) or {}

    failures: list[str] = []

    for eid, rec_hash in sorted(recorded.items()):
        soul_path = entities_dir / eid / "soul.yaml"
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
            failures.append(f"{eid}: registered hash but absent from opencode.json agents block")
            continue
        m = (entry.get("system") or "").strip()
        if not m.startswith("{file:"):
            failures.append(f"{eid}: prompt is not a {{file:}} reference ({m[:40]!r})")
            continue
        target = Path(m[len("{file:"):].rstrip("}"))
        if not target.exists():
            failures.append(f"{eid}: prompt file missing: {target}")
            continue
        expected = render(eid, wad=wad, wads_dir=wads_dir)
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
    parser = argparse.ArgumentParser(
        description="OpenCode adapter: install rendered WAD souls as OpenCode V2 agents."
    )
    parser.add_argument("action", choices=["install", "verify"])
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--wad", default=None, help=f"WAD name (default: {DEFAULT_WAD})")
    parser.add_argument("--wads-dir", default=None, type=Path, help="Override WADS_DIR")
    args = parser.parse_args(argv)

    if args.action == "verify":
        return verify(wad=args.wad, wads_dir=args.wads_dir)
    return install(dry_run=args.dry_run, wad=args.wad, wads_dir=args.wads_dir)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
