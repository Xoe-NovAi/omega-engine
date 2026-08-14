#!/usr/bin/env python3
"""Omega Realm CLI — Vision Operating System (VOS) v1.0.

Manages the 7 sovereign realms of the Omega Engine vision:
Engine Core, Stacks, Fleet, Memory, Heritage, Omegaverse, Community.

Each realm has a state.yaml, interface_contract, and evolution_log.
This CLI provides commands to inspect, handoff, and coordinate across realms.

AP Token: AP-VOS-REALM-CLI-20260814
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# --- Constants ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]
REALMS_DIR = PROJECT_ROOT / "data" / "realms"
COORDINATION_DIR = PROJECT_ROOT / "data" / "coordination"

VALID_REALMS = {
    "engine_core": "Engine Core",
    "stacks": "Stack Ecosystem",
    "fleet": "Agent Fleet",
    "memory": "Memory & Soul",
    "heritage": "Heritage & id Software DNA",
    "omegaverse": "Omegaverse (VR/P2P)",
    "community": "Community & Launch",
}

REALM_OWNERS = {
    "engine_core": "maat_n3",
    "stacks": "maat_n4",
    "fleet": "kali",
    "memory": "lilith_n7",
    "heritage": "doom_guy",
    "omegaverse": "lilith_n6",
    "community": "kali",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_yaml() -> None:
    if yaml is None:
        print("ERROR: PyYAML is required. Run: .venv/bin/pip install pyyaml", file=sys.stderr)
        sys.exit(1)


def _realm_path(realm: str) -> Path:
    return REALMS_DIR / realm


def _load_state(realm: str) -> Dict[str, Any]:
    _require_yaml()
    path = _realm_path(realm) / "state.yaml"
    if not path.exists():
        print(f"ERROR: Realm '{realm}' state not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def _save_state(realm: str, state: Dict[str, Any]) -> None:
    _require_yaml()
    path = _realm_path(realm) / "state.yaml"
    with open(path, "w") as f:
        yaml.safe_dump(state, f, sort_keys=False, default_flow_style=False)


def _validate_realm(realm: str) -> str:
    realm = realm.lower()
    if realm not in VALID_REALMS:
        print(f"ERROR: Unknown realm '{realm}'. Valid realms: {', '.join(sorted(VALID_REALMS))}", file=sys.stderr)
        sys.exit(1)
    return realm


# --- Commands ---

def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a realm (create state.yaml if missing)."""
    realm = _validate_realm(args.realm)
    _require_yaml()
    path = _realm_path(realm)
    state_path = path / "state.yaml"
    if state_path.exists():
        print(f"Realm '{realm}' already initialized at {state_path}")
        return
    path.mkdir(parents=True, exist_ok=True)
    (path / "workspace").mkdir(exist_ok=True)
    (path / "archive").mkdir(exist_ok=True)
    state = {
        "realm": {
            "name": realm,
            "display_name": VALID_REALMS[realm],
            "owner": REALM_OWNERS[realm],
            "version": "1.0.0",
            "status": "active",
            "last_updated": _now(),
            "updated_by": args.by or "unknown",
            "session_id": args.session or "unknown",
        },
        "mandates": {"primary": [], "secondary": []},
        "components": [],
        "interface_contract": {"provides": [], "requires": [], "consumes": [], "produces": []},
        "health": {"overall": "unknown", "last_check": _now(), "checks": []},
        "active_work": [],
        "blockers": [],
        "deferred": [],
        "evolution_log": [],
    }
    _save_state(realm, state)
    print(f"✅ Realm '{realm}' initialized: {state_path}")


def cmd_state(args: argparse.Namespace) -> None:
    """Read realm state."""
    realm = _validate_realm(args.realm)
    state = _load_state(realm)
    if args.json:
        print(json.dumps(state, indent=2, default=str))
    else:
        _require_yaml()
        print(yaml.safe_dump(state, sort_keys=False, default_flow_style=False))


def cmd_list(args: argparse.Namespace) -> None:
    """List all realms and their status."""
    _require_yaml()
    print(f"{'REALM':<14} {'DISPLAY':<28} {'OWNER':<12} {'STATUS':<12} {'BLOCKERS'}")
    print("-" * 80)
    for realm, display in VALID_REALMS.items():
        state_path = _realm_path(realm) / "state.yaml"
        if not state_path.exists():
            print(f"{realm:<14} {display:<28} {REALM_OWNERS[realm]:<12} {'NOT_INIT':<12} -")
            continue
        state = _load_state(realm)
        owner = state.get("realm", {}).get("owner", REALM_OWNERS[realm])
        status = state.get("health", {}).get("overall", "unknown")
        blockers = state.get("blockers", [])
        blocker_str = "; ".join(blockers[:2]) if blockers else "-"
        print(f"{realm:<14} {display:<28} {owner:<12} {status:<12} {blocker_str}")


def cmd_handoff(args: argparse.Namespace) -> None:
    """Propose cross-realm work via Hivemind-style handoff record."""
    from_realm = _validate_realm(args.from_realm)
    to_realm = _validate_realm(args.to_realm)
    task = args.task
    task_id = args.task_id or f"{from_realm[:3].upper()}-{to_realm[:3].upper()}-{int(datetime.now().timestamp())}"

    # Create handoff record in coordination dir
    handoff = {
        "packet_id": task_id,
        "from_realm": from_realm,
        "to_realm": to_realm,
        "task": task,
        "context": args.context or "",
        "priority": args.priority or 0,
        "status": "pending",
        "created_at": _now(),
        "source_entity": args.by or "unknown",
    }
    handoff_dir = COORDINATION_DIR / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    path = handoff_dir / f"{task_id}.json"
    with open(path, "w") as f:
        json.dump(handoff, f, indent=2)
    print(f"✅ Handoff {task_id} proposed: {from_realm} → {to_realm}")
    print(f"   Task: {task}")
    print(f"   Record: {path}")


def cmd_decision(args: argparse.Namespace) -> None:
    """Log a decision to the DECISION_LEDGER.md."""
    realm = _validate_realm(args.realm)
    ledger_path = COORDINATION_DIR / "DECISION_LEDGER.md"
    if not ledger_path.exists():
        print(f"ERROR: DECISION_LEDGER.md not found at {ledger_path}", file=sys.stderr)
        sys.exit(1)

    # Find next D-VOS number
    next_id = 13  # 12 decisions already logged
    with open(ledger_path) as f:
        content = f.read()
    import re
    ids = re.findall(r"D-VOS-(\d+)", content)
    if ids:
        next_id = max(int(i) for i in ids) + 1

    entry = f"""
### D-VOS-{next_id:03d}: {args.title}
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Realm**: {realm.upper()}
**Decision**: {args.decision}
**Rationale**: {args.rationale or 'N/A'}
**Alternatives Considered**: {args.alternatives or 'N/A'}
**Impact**: {args.impact or 'N/A'}
**Reversible?**: {args.reversible or 'Yes'}
**Supersedes**: {args.supersedes or 'None'}
**Author**: {args.by or 'unknown'}
**Session**: {args.session or 'unknown'}
"""
    with open(ledger_path, "a") as f:
        f.write(entry)
    print(f"✅ Decision D-VOS-{next_id:03d} logged to DECISION_LEDGER.md")


def cmd_dashboard(args: argparse.Namespace) -> None:
    """Show vision dashboard (single pane of glass)."""
    _require_yaml()
    print("=" * 80)
    print("🌌 OMEGA ENGINE — VISION DASHBOARD")
    print("=" * 80)

    # Vision anchor
    anchor_path = COORDINATION_DIR / "VISION_ANCHOR.md"
    if anchor_path.exists():
        print("\n📌 VISION ANCHOR:")
        with open(anchor_path) as f:
            for line in f:
                if line.startswith(">") or line.startswith("# 🎯"):
                    print(f"   {line.strip()}")

    # Realm states
    print("\n📊 REALM HEALTH:")
    print(f"{'REALM':<14} {'OWNER':<12} {'STATUS':<12} {'ACTIVE TASKS':<14} {'BLOCKERS'}")
    print("-" * 80)
    for realm, display in VALID_REALMS.items():
        state_path = _realm_path(realm) / "state.yaml"
        if not state_path.exists():
            continue
        state = _load_state(realm)
        owner = state.get("realm", {}).get("owner", "?")
        status = state.get("health", {}).get("overall", "?")
        active = len(state.get("active_work", []))
        blockers = state.get("blockers", [])
        blocker_str = "; ".join(blockers[:1]) if blockers else "-"
        print(f"{realm:<14} {owner:<12} {status:<12} {active:<14} {blocker_str}")

    # Recent decisions
    ledger_path = COORDINATION_DIR / "DECISION_LEDGER.md"
    if ledger_path.exists():
        print("\n📜 RECENT DECISIONS:")
        with open(ledger_path) as f:
            content = f.read()
        import re
        decisions = re.findall(r"### (D-VOS-\d+): (.+)", content)
        for did, title in decisions[-5:]:
            print(f"   {did}: {title}")

    print("\n" + "=" * 80)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omega realm",
        description="Omega Realm CLI — Vision Operating System (VOS) v1.0",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = sub.add_parser("init", help="Initialize a realm")
    p_init.add_argument("realm", help="Realm name (engine_core, stacks, fleet, memory, heritage, omegaverse, community)")
    p_init.add_argument("--by", default="unknown", help="Entity performing the action")
    p_init.add_argument("--session", default="unknown", help="Session ID")
    p_init.set_defaults(func=cmd_init)

    # state
    p_state = sub.add_parser("state", help="Read realm state")
    p_state.add_argument("realm", help="Realm name")
    p_state.add_argument("--json", action="store_true", help="Output as JSON")
    p_state.set_defaults(func=cmd_state)

    # list
    p_list = sub.add_parser("list", help="List all realms")
    p_list.set_defaults(func=cmd_list)

    # handoff
    p_handoff = sub.add_parser("handoff", help="Propose cross-realm work")
    p_handoff.add_argument("from_realm", help="Source realm")
    p_handoff.add_argument("to_realm", help="Target realm")
    p_handoff.add_argument("--task", required=True, help="Task description")
    p_handoff.add_argument("--task_id", help="Task ID (auto-generated if omitted)")
    p_handoff.add_argument("--context", default="", help="Background context")
    p_handoff.add_argument("--priority", type=int, default=0, help="0=normal, 1=high, 2=critical")
    p_handoff.add_argument("--by", default="unknown", help="Entity proposing")
    p_handoff.set_defaults(func=cmd_handoff)

    # decision
    p_decision = sub.add_parser("decision", help="Log a decision to DECISION_LEDGER.md")
    p_decision.add_argument("realm", help="Realm name")
    p_decision.add_argument("--title", required=True, help="Decision title")
    p_decision.add_argument("--decision", required=True, help="Decision text")
    p_decision.add_argument("--rationale", default="", help="Rationale")
    p_decision.add_argument("--alternatives", default="", help="Alternatives considered")
    p_decision.add_argument("--impact", default="", help="Impact")
    p_decision.add_argument("--reversible", default="Yes", help="Reversible?")
    p_decision.add_argument("--supersedes", default="None", help="Supersedes")
    p_decision.add_argument("--by", default="unknown", help="Author")
    p_decision.add_argument("--session", default="unknown", help="Session ID")
    p_decision.set_defaults(func=cmd_decision)

    # dashboard
    p_dash = sub.add_parser("dashboard", help="Show vision dashboard")
    p_dash.set_defaults(func=cmd_dashboard)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
