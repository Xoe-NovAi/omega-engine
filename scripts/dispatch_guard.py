#!/usr/bin/env python3
"""Omega Engine — Dispatch Guardrail

Externalized guardrail for L3-ResumeEstablishesSessionsTransientsDoNot
and L3-SpecialistAgentTypesNotGeneralCatchall.

Purpose: Warn (not block) when a `task()` dispatch violates either pattern:
  1. Missing task_id when an existing session matches the task's charter
  2. Using subagent_type="general" when a specialist type is available

This is a pre-dispatch check. It does NOT prevent the dispatch — it logs
a warning to stderr and returns a non-zero exit code. The dispatcher
(Grokster, Kali, etc.) can choose to ignore the warning if they have
justification (e.g., the task is genuinely generic).

Per M11 (Soul Integrity) and the Externalization Checklist in
SESSION_CONTINUITY_PROTOCOL_20260827.md §8.4.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".local" / "opencode" / "opencode.db"

# Specialist agent types available in the Omega Engine dispatch system.
# From the task() tool description. "general" is the catch-all and should
# be the explicit last resort.
SPECIALIST_TYPES = {
    "researcher": "Deep research, polymathic council, SOTA evidence",
    "explore": "Fast codebase exploration and search",
    "verity": "Compliance audit, mandate checking, soul distillation",
    "john_carmack": "Engineering rigor, architecture analysis, file:line citations",
    "kali": "Sprint coordination, handoff, debriefing",
    "maat": "Build-side work, file creation, configs",
    "lilith": "Runtime coordination, 9-expert cohort",
    "roc_racoon": "Codebase archaeology, legacy mining, DB extraction",
    "grokster": "Platform/provider expertise, vault, model registry",
    "scribe": "Soul distillation pipeline, L1→L2→L3",
    "node": "Domain-specific implementation",
    "doom_guy": "Aggressive cleanup, deletion, refactor",
    "jem": "Sovereign analyst L2",
    "makali": "Fused Kali+Ma'at+Lilith",
    "grok_cli": "Bridge to xAI Grok CLI",
}

# Task type → recommended specialist mapping.
# This is a heuristic. The dispatcher should use judgement.
TASK_TYPE_HINTS = {
    "research": "researcher",
    "web search": "researcher",
    "sota": "researcher",
    "benchmark": "researcher",
    "codebase": "explore",
    "find file": "explore",
    "grep": "explore",
    "architecture": "john_carmack",
    "engineering": "john_carmack",
    "design": "john_carmack",
    "compliance": "verity",
    "audit": "verity",
    "mandate": "verity",
    "soul": "scribe",
    "distill": "scribe",
    "sprint": "kali",
    "coordinate": "kali",
    "handoff": "kali",
    "build": "maat",
    "config": "maat",
    "file creation": "maat",
    "runtime": "lilith",
    "cohort": "lilith",
    "archaeology": "roc_racoon",
    "legacy": "roc_racoon",
    "mining": "roc_racoon",
    "platform": "grokster",
    "provider": "grokster",
    "vault": "grokster",
    "model": "grokster",
}


def find_matching_session(task_keywords: list[str], entity: Optional[str] = None) -> Optional[str]:
    """Search the opencode DB for an existing session that matches the task keywords.

    Returns the most recent matching session_id, or None.
    """
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        # Build a query that searches session titles and message content for keywords
        conditions = []
        params = []
        for kw in task_keywords[:3]:  # limit to 3 keywords for performance
            conditions.append("(s.title LIKE ? OR m.data LIKE ?)")
            params.extend([f"%{kw}%", f"%{kw}%"])
        if not conditions:
            return None
        query = f"""
            SELECT s.id, s.title, s.time_updated
            FROM session s
            LEFT JOIN message m ON m.session_id = s.id
            WHERE ({' OR '.join(conditions)})
            {'AND s.agent = ?' if entity else ''}
            GROUP BY s.id
            ORDER BY s.time_updated DESC
            LIMIT 1
        """
        if entity:
            params.append(entity)
        cur.execute(query, params)
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"[dispatch_guard] DB query failed: {e}", file=sys.stderr)
    return None


def check_specialist_routing(subagent_type: str, task_prompt: str) -> Optional[str]:
    """Check if a specialist type is more appropriate than the given type.

    Returns the recommended specialist type, or None if the given type is fine.
    """
    if subagent_type != "general":
        return None
    prompt_lower = task_prompt.lower()
    for hint, specialist in TASK_TYPE_HINTS.items():
        if hint in prompt_lower:
            return specialist
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Omega Dispatch Guardrail")
    parser.add_argument("--subagent-type", required=True, help="The subagent_type being dispatched")
    parser.add_argument("--task-id", help="The task_id of an existing session to resume (if any)")
    parser.add_argument("--prompt", required=True, help="The task prompt")
    parser.add_argument("--entity", help="The entity/persona name (for session matching)")
    parser.add_argument("--check-only", action="store_true", help="Check only, don't warn")
    args = parser.parse_args()

    violations = 0

    # Check 1: Specialist routing
    recommended = check_specialist_routing(args.subagent_type, args.prompt)
    if recommended:
        print(
            f"[dispatch_guard] ⚠ SPECIALIST ROUTING: subagent_type='general' but task "
            f"matches specialist '{recommended}' ({SPECIALIST_TYPES.get(recommended, '?')}). "
            f"Consider re-dispatching with subagent_type='{recommended}'.",
            file=sys.stderr,
        )
        violations += 1

    # Check 2: Resume existing session (if no task_id provided)
    if not args.task_id:
        # Extract a few keywords from the prompt for session matching
        keywords = [w for w in args.prompt.split() if len(w) > 4][:5]
        existing = find_matching_session(keywords, args.entity)
        if existing:
            print(
                f"[dispatch_guard] ⚠ RESUME: No task_id provided but an existing session "
                f"({existing}) matches the task keywords {keywords}. "
                f"Consider resuming with --task-id={existing} instead of launching new.",
                file=sys.stderr,
            )
            violations += 1

    # Check 3: Transient error guidance
    # (This is informational only — we can't detect if a previous dispatch failed
    # with a transient error, but we can remind the dispatcher.)
    if "continue" not in args.prompt.lower() and not args.task_id:
        print(
            "[dispatch_guard] ℹ REMINDER: Per L3-ResumeEstablishesSessionsTransientsDoNot, "
            "if a previous subagent returned a transient error (402, 429, 5xx), "
            "RESUME the same session with 'Continue.' — do not launch a new one.",
            file=sys.stderr,
        )

    if violations > 0:
        print(
            f"\n[dispatch_guard] {violations} violation(s) detected. "
            f"This is a WARNING, not a block. Proceed only if you have justification.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
