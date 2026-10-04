#!/usr/bin/env python3
"""Render a WAD soul.yaml into a target-neutral agent system prompt.

PORTABILITY DOCTRINE (docs/PORTABILITY.md)
------------------------------------------
This renderer knows NOTHING about OpenCode. Its only job is to turn
`wads/arcana_novai/entities/<id>/soul.yaml` into prompt prose. The output is
plain markdown usable by any interface — the Omega CLI, OpenCode, or a future
runtime.

The OpenCode-specific wiring (opencode.json agent blocks, the ~/.config
prompt directory) lives in a SEPARATE, thin install step. That separation is
the whole point: OpenCode is a disposable third-party interface, and this
renderer must survive its replacement.

Source of truth is the soul. Never hand-edit a rendered prompt — it is
overwritten. Edit soul.yaml, re-render.

Usage:
    python3 scripts/soul_render.py <entity_id>              # stdout
    python3 scripts/soul_render.py --all                   # all entities
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WAD_ENTITIES = REPO_ROOT / "wads" / "arcana_novai" / "entities"

# Domains are rendered into a "when to invoke me" line in the description.
# Keep this mapping free of model names — see the model-pin doctrine in
# docs/OPENCODE_FOUNDATION.md (hardcode policy and behavior, not capacity).


def _load(entity_id: str) -> tuple[dict, dict]:
    """Return (soul, entity_descriptor_or_empty)."""
    soul_path = WAD_ENTITIES / entity_id / "soul.yaml"
    if not soul_path.exists():
        raise SystemExit(f"no soul at {soul_path}")
    soul = yaml.safe_load(soul_path.read_text(encoding="utf-8")) or {}

    # The <id>.yaml sibling (avgn/avgn.yaml) is the loader-visible envelope.
    # It is optional here: the soul alone must be renderable.
    desc_path = WAD_ENTITIES / entity_id / f"{entity_id}.yaml"
    desc: dict = {}
    if desc_path.exists():
        loaded = yaml.safe_load(desc_path.read_text(encoding="utf-8")) or {}
        desc = loaded.get("entity", {}) or {}
    return soul, desc


def _identity_line(soul: dict, entity_id: str) -> str:
    ident = soul.get("identity", {}) or {}
    epithet = ident.get("epithet", "")
    return f"**{ident.get('keeper', entity_id)}**" + (f" — {epithet}" if epithet else "")


def render(entity_id: str) -> str:
    soul, desc = _load(entity_id)
    ident = soul.get("identity", {}) or {}
    sov = soul.get("sovereignty", {}) or {}
    voice = soul.get("voice", {}) or {}

    out: list[str] = []
    add = out.append

    title = ident.get("keeper", entity_id)
    add(f"# {title} System Prompt")
    if ident.get("epithet"):
        add(f"## {ident['epithet']}")
    add("")

    # --- Persona boundary, hoisted above the fold when present -------------
    # This is load-bearing for AVGN. It must appear before any style guidance
    # that could be misread as instruction to impersonate.
    boundary = ident.get("persona_boundary") or ""
    if boundary:
        add("## Persona Boundary — READ FIRST, LOAD-BEARING")
        add(boundary.strip())
        add("")

    # --- Identity ----------------------------------------------------------
    add("## Identity")
    add(f"You are {_identity_line(soul, entity_id)} — a persistent sovereign entity "
        f"of the Arcana-NovAi WAD.")
    add("")
    facts = [
        ("Entity ID", ident.get("keeper", entity_id)),
        ("Seat", ident.get("seat")),
        ("Wing", sov.get("wing")),
        ("KG prefix", sov.get("kg_prefix")),
        ("Diary agent", sov.get("diary_agent")),
        ("Card assignments", sov.get("card_assignments")),
    ]
    for label, value in facts:
        if value:
            add(f"**{label}**: {value}")
    add("")

    if desc.get("domains"):
        add("**Domains**: " + ", ".join(desc["domains"]))
        add("")

    # --- Axioms ------------------------------------------------------------
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
                entry += f" *(see {', '.join(links)})*"
            add(entry)
        add("")

    # --- Directives --------------------------------------------------------
    directives = soul.get("directives", []) or []
    if directives:
        add("## Directives")
        add("")
        for d in directives:
            rule = d.get("rule") if isinstance(d, dict) else str(d)
            d_id = d.get("id") if isinstance(d, dict) else None
            add(f"- **{d_id}** — {rule}" if d_id else f"- {rule}")
        add("")

    # --- Principles --------------------------------------------------------
    principles = soul.get("principles", []) or []
    if principles:
        add("## Principles")
        add("")
        for p in principles:
            add(f"- {p}")
        add("")

    # --- Voice -------------------------------------------------------------
    if voice:
        add("## Voice")
        weights = voice.get("base_weights", {}) or {}
        if weights:
            rendered = ", ".join(f"{k} {v}" for k, v in weights.items())
            add(f"Baseline weights: {rendered}.")
        if voice.get("default_preset"):
            add(f"Default preset: `{voice['default_preset']}`.")
        dna = voice.get("dna_ref")
        if dna:
            add(f"Voice DNA lineage: `{dna}` — refine via versioned delta, never "
                f"silent rewrite.")
        add("")

    # --- Held (explicit non-negotiables / known gaps) ----------------------
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
    add(f"*Rendered from `wads/arcana_novai/entities/{entity_id}/soul.yaml`. "
        f"Do not edit this file — edit the soul and re-render "
        f"(`make agent-souls`). Hand edits are drift and will be overwritten.*")

    return "\n".join(out)


def discover() -> list[str]:
    if not WAD_ENTITIES.is_dir():
        return []
    return sorted(
        p.parent.name
        for p in WAD_ENTITIES.glob("*/soul.yaml")
    )


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: soul_render.py <entity_id> | --all", file=sys.stderr)
        return 2
    if argv[0] == "--all":
        for eid in discover():
            print(f"discovered: {eid}")
        return 0
    print(render(argv[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
