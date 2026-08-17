"""
Soul Context Utilities — Importable by both oracle and omega_hub.

Multi-path extractor that degrades gracefully across soul.yaml schema variants,
and integrates approved lessons from proposed_lessons.yaml to close the distillation loop.

[M2 Engine-Stack Firewall]: This module is in src/omega/ (Core Engine).
"""

import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_soul_context(soul: dict, max_items: int = 3) -> str:
    """
    Extract injectable soul context from a parsed soul.yaml dict.
    Returns up to `max_items` lines of context as a formatted string.
    """
    lines = []

    # Path 1: v2 schema — soul_evolution L3 principles
    se = soul.get("soul_evolution") or {}
    if isinstance(se, dict):
        for lesson in (se.get("lessons_learned") or [])[: max_items * 2]:
            if isinstance(lesson, dict) and "L3" in lesson:
                lines.append(f"- {lesson['L3']}")
            if len(lines) >= max_items:
                break

    # Path 2: directives (v1 schema — kali, roc_racoon, iris, makali, verity)
    if not lines:
        for directive in (soul.get("directives") or [])[:max_items]:
            if isinstance(directive, dict):
                # DUAL-KEY LOOKUP: handles standard "rule" and roc_racoon's "directive"
                rule = directive.get("rule") or directive.get("directive", "")
                if rule:
                    lines.append(f"- {rule[:150]}")

    # Path 3: identity values + strengths (minimal fallback)
    if not lines:
        identity = soul.get("identity") or {}
        if isinstance(identity, dict):
            values = identity.get("values") or []
            strengths = identity.get("strengths") or []
            if values:
                lines.append(f"- Values: {', '.join(str(v) for v in values[:5])}")
            if strengths:
                lines.append(f"- Strengths: {', '.join(str(s) for s in strengths[:5])}")

    return "\n".join(lines[:max_items])


def load_entity_soul_context(entity_name: str, data_dir: Path) -> str:
    """
    Load and extract soul context for an entity from disk.
    Reads both soul.yaml and proposed_lessons.yaml (approved).
    """
    entity_dir = data_dir / "entities" / entity_name.lower()
    context_lines = []

    # 1. Check proposed_lessons.yaml for recently approved distillations
    pl_path = entity_dir / "proposed_lessons.yaml"
    if pl_path.exists():
        try:
            pl_data = yaml.safe_load(pl_path.read_text(encoding="utf-8")) or {}
            proposals = (
                pl_data.get("proposals", [])
                if isinstance(pl_data, dict)
                else (pl_data if isinstance(pl_data, list) else [])
            )
            for p in proposals:
                if isinstance(p, dict) and p.get("status") == "approved" and p.get("L3"):
                    context_lines.append(f"- {p['L3']}")
        except (OSError, yaml.YAMLError) as e:
            logger.warning("Failed to read proposed_lessons.yaml for '%s': %s", entity_name, e)

    # 2. Extract from primary soul.yaml
    soul_path = entity_dir / "soul.yaml"
    if soul_path.exists():
        try:
            soul = yaml.safe_load(soul_path.read_text(encoding="utf-8")) or {}
            if isinstance(soul, dict):
                base_context = extract_soul_context(soul, max_items=3)
                if base_context:
                    # Add base context lines that aren't already in our list
                    for line in base_context.split("\n"):
                        if line and line not in context_lines:
                            context_lines.append(line)
        except (OSError, yaml.YAMLError) as e:
            logger.warning("Soul load failed for '%s': %s", entity_name, e)

    # M18 Token Efficiency: Cap at 3 items total
    return "\n".join(context_lines[:3])
