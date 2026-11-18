#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Render a WAD soul.yaml (or entity YAML) into a target-neutral agent system prompt.

PORTABILITY DOCTRINE (D-LIL-006 / M2 Engine-Stack Firewall)
-----------------------------------------------------------
This renderer knows NOTHING about OpenCode. Its only job is to turn
`<WADS_DIR>/<wad>/entities/<id>/soul.yaml` (or flat `<id>.yaml`) into plain
markdown prompt prose usable by any interface — the Omega CLI, OpenCode, or a
future runtime.

Source of truth is the WAD soul. Never hand-edit a rendered prompt — it is
overwritten. Edit soul.yaml, re-render.

Usage:
    python3 scripts/soul_render.py <entity_id> [--wad arcana_novai]
    python3 scripts/soul_render.py --all [--wad arcana_novai]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from omega.governance.config_resolver import WADS_DIR, get_active_iwad  # noqa: E402


def resolve_wad_entities_dir(
    wad: Optional[str] = None, wads_dir: Optional[Path] = None
) -> tuple[str, Path]:
    """Resolve the active WAD name and its entities directory."""
    base = Path(wads_dir) if wads_dir is not None else WADS_DIR
    if wad is None:
        if (base / "arcana_novai" / "entities").is_dir():
            wad = "arcana_novai"
        else:
            wad = get_active_iwad()
    return wad, base / wad / "entities"


def _load(
    entity_id: str, wad: Optional[str] = None, wads_dir: Optional[Path] = None
) -> tuple[str, dict, dict, str]:
    """Return (wad_name, soul_dict, entity_descriptor_dict, source_relpath)."""
    wad_name, entities_dir = resolve_wad_entities_dir(wad=wad, wads_dir=wads_dir)
    soul_path = entities_dir / entity_id / "soul.yaml"
    desc_dir_path = entities_dir / entity_id / f"{entity_id}.yaml"
    flat_path = entities_dir / f"{entity_id}.yaml"

    soul: dict = {}
    desc: dict = {}
    source_rel = f"config/wads/{wad_name}/entities/{entity_id}/soul.yaml"

    if soul_path.exists():
        soul = yaml.safe_load(soul_path.read_text(encoding="utf-8")) or {}
        if desc_dir_path.exists():
            loaded = yaml.safe_load(desc_dir_path.read_text(encoding="utf-8")) or {}
            desc = loaded.get("entity", {}) or {}
    elif flat_path.exists():
        loaded = yaml.safe_load(flat_path.read_text(encoding="utf-8")) or {}
        desc = loaded.get("entity", {}) or {}
        source_rel = f"config/wads/{wad_name}/entities/{entity_id}.yaml"
    else:
        raise SystemExit(f"no soul or entity definition at {soul_path} or {flat_path}")

    return wad_name, soul, desc, source_rel


def _render_identity_schema(
    entity_id: str, wad_name: str, soul: dict, desc: dict, source_rel: str
) -> str:
    """Render ANAi-style `identity:` + `axioms:` + `directives:` + `voice:` soul."""
    ident = soul.get("identity", {}) or {}
    sov = soul.get("sovereignty", {}) or {}
    if not isinstance(sov, dict):
        sov = {}
    voice = soul.get("voice", {}) or {}

    out: list[str] = []
    add = out.append

    title = ident.get("keeper", entity_id)
    epithet = ident.get("epithet", "")
    add(f"# {title} System Prompt")
    if epithet:
        add(f"## {epithet}")
    add("")

    # Persona boundary, hoisted above the fold when present (load-bearing for AVGN).
    boundary = ident.get("persona_boundary") or ""
    if boundary:
        add("## Persona Boundary — READ FIRST, LOAD-BEARING")
        add(boundary.strip())
        add("")

    # Identity
    add("## Identity")
    ident_line = f"**{title}**" + (f" — {epithet}" if epithet else "")
    add(
        f"You are {ident_line} — a persistent sovereign entity of the `{wad_name}` WAD."
    )
    add("")
    facts = [
        ("Entity ID", title),
        ("Seat", ident.get("seat")),
        ("Wing", sov.get("wing")),
        ("KG prefix", sov.get("kg_prefix")),
        ("Diary agent", sov.get("diary_agent")),
        ("Card assignments", sov.get("card_assignments")),
    ]
    for label, value in facts:
        if value:
            add(f"**{label}**: {value}")
    if any(v for _, v in facts):
        add("")

    if desc.get("domains"):
        add("**Domains**: " + ", ".join(str(d) for d in desc["domains"]))
        add("")

    # Axioms
    axioms = soul.get("axioms", []) or []
    if axioms:
        add("## Axioms")
        add("")
        for ax in axioms:
            text = ax.get("text") if isinstance(ax, dict) else str(ax)
            ax_id = ax.get("id") if isinstance(ax, dict) else None
            links = ax.get("links") if isinstance(ax, dict) else None
            entry = f"- **{ax_id}** — {text}" if ax_id else f"- {text}"
            if links:
                entry += f" *(see {', '.join(str(x) for x in links)})*"
            add(entry)
        add("")

    # Directives
    directives = soul.get("directives", []) or []
    if directives:
        add("## Directives")
        add("")
        for d in directives:
            if isinstance(d, dict):
                rule = d.get("rule") or d.get("directive") or ""
                d_id = d.get("id")
                add(f"- **{d_id}** — {rule}" if d_id else f"- {rule}")
            else:
                add(f"- {d}")
        add("")

    # Principles
    principles = soul.get("principles", []) or []
    if principles:
        add("## Principles")
        add("")
        for p in principles:
            add(f"- {p}")
        add("")

    # Voice
    if isinstance(voice, dict) and voice:
        add("## Voice")
        weights = voice.get("base_weights", {}) or {}
        if weights:
            rendered = ", ".join(f"{k} {v}" for k, v in weights.items())
            add(f"Baseline weights: {rendered}.")
        if voice.get("default_preset"):
            add(f"Default preset: `{voice['default_preset']}`.")
        dna = voice.get("dna_ref")
        if dna:
            add(
                f"Voice DNA lineage: `{dna}` — refine via versioned delta, never "
                "silent rewrite."
            )
        add("")

    # Held
    held = soul.get("held", []) or []
    if held:
        add("## Held")
        add("")
        add("*Non-negotiables and known gaps. These are settled — do not re-derive.*")
        add("")
        for h in held:
            add(f"- {h}")
        add("")

    add("---")
    add("")
    add(
        f"*Rendered from `{source_rel}`. "
        "Do not edit this file — edit the soul and re-render. "
        "Hand edits are drift and will be overwritten.*"
    )
    return "\n".join(out)


def _render_entity_schema(
    entity_id: str, wad_name: str, soul: dict, desc: dict, source_rel: str
) -> str:
    """Render `entity:`-rooted soul (Researcher-Humboldt or OED flat entity YAML)."""
    ent = soul.get("entity", {}) if isinstance(soul.get("entity"), dict) else {}
    if not ent:
        ent = desc or {}

    out: list[str] = []
    add = out.append

    title = ent.get("name") or ent.get("id") or entity_id
    epithet = ent.get("epithet") or ent.get("archetype") or ent.get("role") or ""
    add(f"# {title} System Prompt")
    if epithet:
        add(f"## {epithet}")
    add("")

    add("## Identity")
    ident_line = f"**{title}**" + (f" — {epithet}" if epithet else "")
    add(f"You are {ident_line} — a sovereign entity of the `{wad_name}` WAD.")
    add("")

    for label, value in (
        ("Entity ID", ent.get("id") or entity_id),
        ("Archetype", ent.get("archetype")),
        ("Entity Class", ent.get("entity_class")),
        ("Role", ent.get("role") or desc.get("role")),
    ):
        if value:
            add(f"**{label}**: {value}")
    add("")

    if desc.get("personality") or ent.get("personality"):
        personality = (desc.get("personality") or ent.get("personality") or "").strip()
        add("## Persona & Core Voice")
        add(personality)
        add("")

    domains = desc.get("domains") or ent.get("domains") or []
    if domains:
        add("**Domains**: " + ", ".join(str(d) for d in domains))
        add("")

    domain_affinities = ent.get("domain_affinities") or []
    if domain_affinities:
        add("## Domain Affinities")
        add("")
        for item in domain_affinities:
            if isinstance(item, dict):
                for k, v in item.items():
                    add(f"- **{k}**: {v}")
            else:
                add(f"- {item}")
        add("")

    methodology = ent.get("methodology") or []
    if methodology:
        add("## Methodology")
        add("")
        for m in methodology:
            add(f"- {m}")
        add("")

    voice_dna = ent.get("voice_dna") or {}
    if isinstance(voice_dna, dict) and voice_dna:
        add("## Voice DNA")
        add("")
        for field in ("tone", "register", "cadence"):
            if voice_dna.get(field):
                add(f"**{field.title()}**: {voice_dna[field]}")
        if voice_dna.get("metaphors"):
            add("**Metaphors**: " + ", ".join(str(m) for m in voice_dna["metaphors"]))
        if voice_dna.get("quirks"):
            for q in voice_dna["quirks"]:
                add(f"- {q}")
        add("")

    sovereignty = ent.get("sovereignty") or []
    if isinstance(sovereignty, list) and sovereignty:
        add("## Sovereignty")
        add("")
        for s in sovereignty:
            add(f"- {s}")
        add("")

    add("---")
    add("")
    add(
        f"*Rendered from `{source_rel}`. "
        "Do not edit this file — edit the soul and re-render. "
        "Hand edits are drift and will be overwritten.*"
    )
    return "\n".join(out)


def render(
    entity_id: str, wad: Optional[str] = None, wads_dir: Optional[Path] = None
) -> str:
    """Render an entity's soul (or flat entity YAML) to target-neutral markdown."""
    wad_name, soul, desc, source_rel = _load(entity_id, wad=wad, wads_dir=wads_dir)
    if "identity" in soul and isinstance(soul["identity"], dict):
        return _render_identity_schema(entity_id, wad_name, soul, desc, source_rel)
    return _render_entity_schema(entity_id, wad_name, soul, desc, source_rel)


def discover(wad: Optional[str] = None, wads_dir: Optional[Path] = None) -> list[str]:
    """Discover renderable entity IDs in the target WAD."""
    _, entities_dir = resolve_wad_entities_dir(wad=wad, wads_dir=wads_dir)
    if not entities_dir.is_dir():
        return []
    found = {p.parent.name for p in entities_dir.glob("*/soul.yaml")}
    for p in entities_dir.glob("*.yaml"):
        if p.stem != "dispatch":
            found.add(p.stem)
    return sorted(found)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Render a WAD soul.yaml into a target-neutral agent system prompt."
    )
    parser.add_argument("entity_id", nargs="?", help="Entity ID to render")
    parser.add_argument(
        "--wad", default=None, help="WAD name under WADS_DIR (default: arcana_novai or active IWAD)"
    )
    parser.add_argument(
        "--wads-dir", default=None, type=Path, help="Override WADS_DIR root (for testing)"
    )
    parser.add_argument("--all", action="store_true", help="List all discoverable entities")
    args = parser.parse_args(argv)

    if args.all:
        for eid in discover(wad=args.wad, wads_dir=args.wads_dir):
            print(f"discovered: {eid}")
        return 0

    if not args.entity_id:
        parser.print_help(sys.stderr)
        return 2

    print(render(args.entity_id, wad=args.wad, wads_dir=args.wads_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
