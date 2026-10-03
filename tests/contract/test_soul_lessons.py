# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract Tests — Soul Lessons Schema + Promotion (W1-3).

Covers:
  1. EvidenceRef / Lesson schema validation (backward compat, warn-only).
  2. Round-trip write→load→compare through the EXISTING SoulStore atomic
     writer (single production soul-write path — structural-debt gate #1).
  3. M21 Gate Integrity: the REAL promoted kali approved surface must carry
     evidence fields whose artifact probe-paths RESOLVE on disk (O-Q4
     probe-path binding).

SANITATION LAW: no fixture contains real-name contamination.
"""

import sys
from pathlib import Path

import pytest
import anyio
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from omega.soul_store import SoulStore  # noqa: E402
from omega.soul.lessons import (  # noqa: E402
    EvidenceRef,
    Lesson,
    validate_lessons,
)


# ── Schema unit tests ─────────────────────────────────────────────────


class TestEvidenceRef:
    def test_valid_ref_with_artifact(self):
        ref = EvidenceRef(artifact="docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md")
        assert ref.artifact.endswith(".md")

    def test_empty_ref_rejected(self):
        with pytest.raises(Exception):  # pydantic ValidationError
            EvidenceRef()

    def test_extra_keys_forbidden(self):
        with pytest.raises(Exception):
            EvidenceRef(bogus="x", artifact="a.md")


class TestLessonSchema:
    def test_legacy_triplet_without_evidence_is_valid(self):
        """Backward compat: historical bare triplets must stay valid."""
        lesson = Lesson.model_validate({
            "level": "L3",
            "narrative": "did a thing",
            "insight": "it meant another thing",
            "principle": "timeless truth",
        })
        assert lesson.level == "L3"
        assert lesson.evidence is None

    def test_lesson_with_evidence_round_trips(self):
        lesson = Lesson.model_validate({
            "id": "AO-P1-RECIPROCITY",
            "level": "L3",
            "principle": "symmetrical awareness",
            "evidence": [{"artifact": "data/coordination/x.md",
                          "quote": "verbatim line"}],
        })
        dumped = lesson.model_dump(exclude_none=True)
        reloaded = Lesson.model_validate(dumped)
        assert reloaded.evidence[0].quote == "verbatim line"

    def test_bad_level_rejected(self):
        with pytest.raises(Exception):
            Lesson.model_validate({"level": "L9"})

    def test_malformed_evidence_entry_rejected(self):
        with pytest.raises(Exception):
            Lesson.model_validate({"level": "L3", "evidence": [{"quote": ""}]})


class TestValidateLessons:
    def test_warn_only_on_missing_evidence(self):
        data = {"proposals": [{"level": "L3", "principle": "p1"},
                              {"level": "L2", "insight": "i1"}]}
        lessons, warnings = validate_lessons(data, source="test")
        assert len(lessons) == 2
        assert len(warnings) == 2
        assert "warn-only" in warnings[0]

    def test_list_shape_accepted(self):
        lessons, _ = validate_lessons([{"level": "L1", "narrative": "n"}])
        assert len(lessons) == 1


# ── Round-trip through SoulStore (existing atomic writer) ────────────


class TestSoulStoreRoundTrip:
    @pytest.mark.anyio
    async def test_write_load_compare(self, tmp_path):
        target = tmp_path / "approved_lessons.yaml"
        payload = [
            {"id": "T-1", "level": "L3", "lesson": "truth one",
             "evidence": [{"artifact": "a.md", "session_id": "ses_x"}]},
            {"id": "T-2", "level": "L2", "lesson": "truth two",
             "evidence": [{"artifact": "b.md", "quote": "q"}]},
        ]
        content = yaml.dump(payload, default_flow_style=False, sort_keys=False,
                            allow_unicode=True)

        store = SoulStore(max_backups=2)
        await store.write_atomic(target, content)

        # Read-back compare (FP-08 discipline)
        loaded = yaml.safe_load(target.read_text(encoding="utf-8"))
        assert loaded == payload

        # Atomic-writer guarantees visible: no leftover tempfiles
        leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
        assert leftovers == []

    @pytest.mark.anyio
    async def test_unreadable_main_recovers_from_bak(self, tmp_path):
        """IntegrityDetection guarantees recovery when the main file is
        UNREADABLE (the .bak path). YAML-validity is the loader's concern,
        not the store's."""
        import os
        import shutil

        target = tmp_path / "approved_lessons.yaml"
        good = yaml.dump([{"id": "G-1", "level": "L3", "lesson": "safe"}])
        store = SoulStore()
        await store.write_atomic(target, good)
        shutil.copy2(str(target), str(target.with_suffix(target.suffix + ".1.bak")))
        target.chmod(0o000)  # simulate unreadable/corrupt storage
        try:
            recovered = await store.read_with_recovery(target)
        finally:
            target.chmod(0o644)
        assert recovered is not None and "safe" in recovered


# ── M21 Contract: REAL promoted kali surface ─────────────────────────


class TestPromotedKaliSurface:
    APPROVED = REPO_ROOT / "data" / "entities" / "kali" / "approved_lessons.yaml"
    STAGED = REPO_ROOT / "data" / "entities" / "kali" / "proposed_lessons.yaml"

    def _load_promoted(self) -> list:
        data = (
            yaml.safe_load(self.APPROVED.read_text(encoding="utf-8"))
            if self.APPROVED.exists() else None
        )
        if not data:
            pytest.skip("promotion not yet executed")
        return data

    def test_approved_surface_exists_with_20_lessons(self):
        assert len(self._load_promoted()) == 20

    def test_every_promoted_lesson_carries_resolvable_evidence(self):
        """M21 gate integrity: evidence fields present AND probe-paths resolve."""
        data = self._load_promoted()
        unanchored = []
        for entry in data:
            refs = entry.get("evidence")
            if not refs:
                unanchored.append(f"{entry.get('id', '?')}:no-evidence")
                continue
            for ref in refs:
                art = ref.get("artifact")
                if art and not (REPO_ROOT / art).exists():
                    unanchored.append(f"{entry.get('id', '?')}:{art}")
        assert unanchored == [], f"unresolvable evidence: {unanchored}"

    def test_staging_emptied_after_promotion(self, tmp_path):
        """M11 hygiene: promoted proposals are removed from staging.

        Deterministic mechanism check (not a live-data snapshot): build a
        temp entity with staged proposals, run the promotion, and assert the
        staging file is emptied. The mechanism is scripts/soul_promote.py.
        """
        from scripts import soul_promote

        base = tmp_path / "data" / "entities" / "proment"
        base.mkdir(parents=True)
        (base / "proposed_lessons.yaml").write_text(
            "proposals:\n"
            "- id: t-001\n"
            "  date: '2026-09-16'\n"
            "  narrative: n\n"
            "  insight: i\n"
            "  principle: p\n",
            encoding="utf-8",
        )
        (base / "soul.yaml").write_text(
            "# 🔱 Test Entity — Soul Configuration\n"
            "entity:\n"
            "  name: \"Proment\"\n"
            "  version: \"1.0.0\"\n"
            "\n"
            "evolution:\n"
            "  lesson_staging: \"blind\"\n",
            encoding="utf-8",
        )

        rc = soul_promote.promote(
            "proment", all_flag=True, apply=True, confirm=True, repo_root=tmp_path
        )
        assert rc == 0

        staged = yaml.safe_load(
            (base / "proposed_lessons.yaml").read_text(encoding="utf-8")
        )
        assert staged.get("proposals") == []

    def test_schema_validator_accepts_promoted_surface(self):
        data = self._load_promoted()
        lessons, warnings = validate_lessons({"approved": data}, source="kali-approved")
        assert len(lessons) == len(data)
        assert warnings == []  # all promoted lessons carry evidence
