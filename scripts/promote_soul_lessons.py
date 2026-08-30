#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""promote_soul_lessons — W1-3 staged-proposal promotion (ruling S5 / MF2).

Moves an entity's staged proposals (proposed_lessons.yaml) into the approved
soul surface (approved_lessons.yaml — the Vetted-Wisdom surface injected into
identity prompts by entity_workspace.py), attaching structured evidence refs
(session_id / artifact / quote) populated from the artifacts each proposal
cites.

HARD CONSTRAINTS:
  - Uses the EXISTING SoulStore atomic writer ONLY (C-1'). No second
    production soul-write path (structural-debt gate #1).
  - Schema patch (src/omega/soul/lessons.py) landed BEFORE this promotion
    (Gemini trap-catch #2).
  - Every evidence artifact path is probe-bound: verified to exist on disk
    at promotion time (ledger O-Q4). Missing artifact => promotion aborts.

Usage:
    .venv/bin/python scripts/promote_soul_lessons.py --entity kali [--dry-run]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from omega.soul_store import get_soul_store  # noqa: E402
from omega.soul.lessons import EvidenceRef, Lesson, validate_lessons  # noqa: E402

# ── Evidence map ───────────────────────────────────────────────────────
# Keyed by proposal id (if present) else positional index in the staging
# file. Every artifact path below was disk-verified before inclusion.
# SANITATION LAW respected: no real-name markers in any evidence string.

_KALI_SES_TEAMSTUDY = "ses_fdef2be4effe4pAaLXCTUx62GO"

AO_ARTIFACT = "data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md"

EVIDENCE_BY_KEY: dict[str | int, list[dict]] = {
    # Triplet 1 — GitHub secret-scrub codification
    0: [{"artifact": "scripts/git-secret-scan.sh"},
        {"artifact": ".opencode/skills/git-secret-scrub/SKILL.md"},
        {"artifact": "docs/strategy/GITHUB_FORENSICS_SCRIPTING_GUIDE.md",
         "quote": "Validate against known-positive samples (MANDATORY)"}],
    1: [{"artifact": "docs/strategy/GITHUB_FORENSICS_SCRIPTING_GUIDE.md",
         "quote": "the script was validated against known-positive samples"}],
    2: [{"artifact": "docs/strategy/GITHUB_FORENSICS_SCRIPTING_GUIDE.md"}],
    # Triplet 2 — Vault overhaul synthesis
    3: [{"artifact": "docs/specs/VAULT_SYSTEM_OVERHAUL_MASTER_INDEX_20260818.md"},
        {"artifact": "docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md"}],
    4: [{"artifact": "docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md"},
        {"artifact": "docs/specs/VAULT_SYSTEM_OVERHAUL_MASTER_INDEX_20260818.md"}],
    5: [{"artifact": "docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md"}],
    # Triplet 3 — MaKaLi Cloud Council
    6: [{"artifact": "data/coordination/MAKALI_COUNCIL_AUDIT_20260818.md",
         "quote": "The MaKaLi Cloud Council verdict is **directionally correct** "
                  "but has **one critical blind spot**"}],
    7: [{"artifact": "data/coordination/MAKALI_COUNCIL_AUDIT_20260818.md",
         "quote": "Adversarial review must probe the FULL call graph"}],
    8: [{"artifact": "data/coordination/MAKALI_COUNCIL_AUDIT_20260818.md"}],
    # Triplet 4 — Phase 0 tracker lock-in
    9: [{"artifact": "docs/decisions/PIVOT_LOG.md",
         "quote": "D-581: zswap + NVMe Swap Confirmed — D-526 REAFFIRMED (2026-08-20)"},
        {"artifact": "data/coordination/GAP_REGISTRY.json"}],
    10: [{"artifact": "docs/decisions/PIVOT_LOG.md"}],
    11: [{"artifact": "data/coordination/ACTIVE_SPRINT.json"}],
    # Context Packer v3 meditation (KALI-INTEGRATION-004)
    12: [{"artifact": "data/coordination/meditations/records/"
                     "MEDITATION_KALI_20260823_CONTEXT_PACKER_ENHANCEMENT.md",
          "quote": "The packer is the sovereignty boundary",
          "session_id": _KALI_SES_TEAMSTUDY}],
    # Architect Oversight patterns AO-P1..P7
    "AO-P1-RECIPROCITY": [
        {"artifact": AO_ARTIFACT,
         "quote": "Communication that transfers no context is extraction; "
                  "collaboration requires symmetrical awareness.",
         "session_id": _KALI_SES_TEAMSTUDY}],
    "AO-P2-FRAME-AUDIT": [{"artifact": AO_ARTIFACT,
                           "session_id": _KALI_SES_TEAMSTUDY}],
    "AO-P3-AUTHORITY-FIRST": [{"artifact": AO_ARTIFACT,
                               "session_id": _KALI_SES_TEAMSTUDY}],
    "AO-P4-META-CODIFICATION": [{"artifact": AO_ARTIFACT,
                                 "session_id": _KALI_SES_TEAMSTUDY}],
    "AO-P5-ALIGNMENT-HYGIENE": [{"artifact": AO_ARTIFACT,
                                 "session_id": _KALI_SES_TEAMSTUDY}],
    "AO-P6-SYNTHESIS-BEFORE-DECISION": [{"artifact": AO_ARTIFACT,
                                         "session_id": _KALI_SES_TEAMSTUDY}],
    "AO-P7-FREE-IS-THE-SPEC": [
        {"artifact": AO_ARTIFACT, "session_id": _KALI_SES_TEAMSTUDY},
        {"artifact": "data/coordination/teamstudy_20260823/FINAL_SYNTHESIS.md"}],
}


def _key_for(item: dict, index: int) -> str | int:
    key = item.get("id")
    return key if isinstance(key, str) and key else index


def promote(entity: str, dry_run: bool) -> int:
    entity_dir = REPO_ROOT / "data" / "entities" / entity
    staged_path = entity_dir / "proposed_lessons.yaml"
    approved_path = entity_dir / "approved_lessons.yaml"

    staged_doc = yaml.safe_load(staged_path.read_text(encoding="utf-8")) or {}
    raw_items = staged_doc.get("proposals") or []
    if not raw_items:
        print(f"[promote] {entity}: nothing staged — aborting (idempotent no-op)")
        return 0

    # Pre-flight: bind every evidence artifact to disk BEFORE any write (O-Q4).
    missing: list[str] = []
    for i, item in enumerate(raw_items):
        refs = EVIDENCE_BY_KEY.get(_key_for(item, i))
        if not refs:
            missing.append(f"<no-evidence-map:{_key_for(item, i)}>")
            continue
        for ref in refs:
            art = ref.get("artifact")
            if art and not (REPO_ROOT / art).exists():
                missing.append(art)
    if missing:
        print(f"[promote] ABORT — unresolvable evidence probe-paths: {sorted(set(missing))}")
        return 2

    # Build approved lessons with evidence attached.
    promoted: list[dict] = []
    now = datetime.now(timezone.utc).isoformat()
    for i, item in enumerate(raw_items):
        refs = [EvidenceRef.model_validate(r) for r in EVIDENCE_BY_KEY[_key_for(item, i)]]
        lesson = Lesson.model_validate({**item, "status": "approved", "evidence": refs})
        entry = lesson.model_dump(exclude_none=True)
        # Identity-injection compat: entity_workspace renders `lesson` key.
        entry["lesson"] = lesson.principle or lesson.insight or lesson.narrative or ""
        entry["promoted_at"] = now
        entry["promoted_by"] = "maat/w1-3"
        promoted.append(entry)

    # Validate the full approved payload through the warn-only validator.
    lessons, warnings = validate_lessons({"approved": promoted}, source=str(approved_path))
    assert len(lessons) == len(promoted)
    for w in warnings:
        print(f"[promote][WARN] {w}")

    # Coverage report (honest numbers).
    with_evidence = sum(1 for e in promoted if e.get("evidence"))
    with_quote = sum(
        1 for e in promoted
        if any(r.get("quote") for r in (e.get("evidence") or []))
    )
    print(f"[promote] {entity}: {len(promoted)} proposal(s) ready — "
          f"evidence coverage {with_evidence}/{len(promoted)} "
          f"({100 * with_evidence // max(len(promoted), 1)}%), "
          f"quote coverage {with_quote}/{len(promoted)}")

    if dry_run:
        print("[promote] dry-run — no writes performed")
        return 0

    # Write BOTH surfaces through the existing SoulStore atomic writer only.
    store = get_soul_store()

    async def _write() -> None:
        await store.write_atomic(approved_path,
                                 yaml.dump(promoted, default_flow_style=False,
                                           sort_keys=False, allow_unicode=True))
        staged_doc["proposals"] = []
        staged_doc.setdefault("metadata", {})["last_promotion"] = now
        await store.write_atomic(staged_path,
                                 yaml.dump(staged_doc, default_flow_style=False,
                                           sort_keys=False, allow_unicode=True))

    asyncio.run(_write())

    # FP-08 read-back verification (post-write proof, never trust the write).
    check = yaml.safe_load(approved_path.read_text(encoding="utf-8"))
    if not isinstance(check, list) or len(check) != len(promoted):
        print("[promote] FAIL — read-back mismatch on approved surface")
        return 3
    leftover = yaml.safe_load(staged_path.read_text(encoding="utf-8")) or {}
    if leftover.get("proposals"):
        print("[promote] FAIL — staging file not emptied")
        return 3

    print(f"[promote] OK — {len(promoted)} lesson(s) promoted to {approved_path.name}; "
          f"staging emptied. Atomic writer: SoulStore (single production path).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="promote_soul_lessons")
    parser.add_argument("--entity", default="kali")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return promote(args.entity, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
