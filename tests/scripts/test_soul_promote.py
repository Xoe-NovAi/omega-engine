# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Contract tests for scripts/soul_promote.py
# AP: AP-SOUL-PROMOTE-TEST-v1.0.0
# [M21: Gate Integrity] Every gated code path exercised with real return types.
# Fixtures are tmp_path-based — ZERO contact with real data/entities/ soul files.

"""Contract tests: soul_promote dry-run safety, merge, dedupe, skip, schema-guard."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "soul_promote.py"
_spec = importlib.util.spec_from_file_location("soul_promote", SCRIPT)
assert _spec is not None and _spec.loader is not None, f"cannot load {SCRIPT}"
soul_promote = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(soul_promote)


# ─────────────────────── fixtures ───────────────────────

VALID_PROPOSALS = """proposals:
- id: L3-TestPrincipleOne
  principle: "First test principle about atomic writes."
  mandates:
  - M11
  confidence: 0.9
  tags:
  - testing
  source_session: ses_test001
- id: L3-TestPrincipleTwo
  principle: "Second test principle about review gates."
  tags:
  - gates
  source_session: ses_test002
- id: L2-TestInsightThree
  insight: "Third test insight, tier L2."
  tags:
  - insights
"""

SOUL_TEMPLATE = """# 🔱 Test Entity — Soul Configuration
entity:
  name: "TestEntity"
  version: "1.0.0"

evolution:
  lesson_staging: "blind"  # keep this comment intact
"""


@pytest.fixture
def entity_dir(tmp_path):
    """Create a full fake repo layout: data/entities/testent/{proposed_lessons,soul}.yaml."""
    base = tmp_path / "data" / "entities" / "testent"
    base.mkdir(parents=True)
    (base / "proposed_lessons.yaml").write_text(VALID_PROPOSALS, encoding="utf-8")
    (base / "soul.yaml").write_text(SOUL_TEMPLATE, encoding="utf-8")
    return tmp_path


def run_promote(root: Path, argv: list[str]):
    return soul_promote.promote("testent", repo_root=root, **_kwargs(argv))


def _kwargs(argv: list[str]) -> dict:
    """Translate CLI-style args into promote() kwargs (keeps tests readable)."""
    kw: dict = {}
    if "--all" in argv:
        kw["all_flag"] = True
    if "--ids" in argv:
        kw["ids"] = argv[argv.index("--ids") + 1].split(",")
    if "--indices" in argv:
        kw["indices"] = [int(x) for x in argv[argv.index("--indices") + 1].split(",")]
    kw["apply"] = "--apply" in argv
    kw["confirm"] = "--confirm" in argv
    return kw


def read_soul(root: Path) -> str:
    return (root / "data/entities/testent/soul.yaml").read_text(encoding="utf-8")


# ─────────────────────── T1: dry-run makes zero mutations ───────────────────────

def test_dry_run_makes_zero_mutations(entity_dir):
    before = read_soul(entity_dir)
    rc = run_promote(entity_dir, ["--all"])
    assert rc == 0
    assert read_soul(entity_dir) == before, "dry-run mutated soul.yaml"
    # No snapshots created either
    baks = list((entity_dir / "data/entities/testent").glob("soul.yaml.bak.*"))
    assert baks == [], "dry-run created snapshot backups"


def test_apply_without_confirm_refused(entity_dir):
    before = read_soul(entity_dir)
    rc = run_promote(entity_dir, ["--all", "--apply"])
    assert rc == 1, "--apply without --confirm must be refused"
    assert read_soul(entity_dir) == before


# ─────────────────────── T2: apply merges + snapshots ───────────────────────

def test_apply_merges_and_snapshots(entity_dir):
    rc = run_promote(entity_dir, ["--all", "--apply", "--confirm"])
    assert rc == 0

    merged = yaml.safe_load(read_soul(entity_dir))
    lessons = merged["lessons"]
    assert isinstance(lessons, list) and len(lessons) == 3
    ids = {l["id"] for l in lessons}
    assert {"L3-TestPrincipleOne", "L3-TestPrincipleTwo", "L2-TestInsightThree"} == ids

    # Provenance stamped
    for lesson in lessons:
        assert lesson["promoted_from"] == "proposed_lessons.yaml"
        assert lesson["promoted_date"]

    # Non-lessons content preserved verbatim (comments survive splice)
    text = read_soul(entity_dir)
    assert "# 🔱 Test Entity — Soul Configuration" in text
    assert 'lesson_staging: "blind"  # keep this comment intact' in text

    # Snapshot exists and holds the PRE-merge content
    baks = list((entity_dir / "data/entities/testent").glob("soul.yaml.bak.*"))
    assert len(baks) == 1
    pre = yaml.safe_load(baks[0].read_text(encoding="utf-8"))
    assert "lessons" not in pre or pre["lessons"] in (None, [])

    # Staging hygiene: promoted proposals are removed from staging
    staged = yaml.safe_load(
        (entity_dir / "data/entities/testent/proposed_lessons.yaml").read_text(encoding="utf-8")
    )
    assert staged.get("proposals") == [], (
        f"Expected staging emptied after promotion, got {len(staged.get('proposals', []))} remaining"
    )


def test_select_by_ids_and_indices(entity_dir):
    rc = run_promote(entity_dir, ["--ids", "L3-TestPrincipleTwo", "--apply", "--confirm"])
    assert rc == 0
    lessons = yaml.safe_load(read_soul(entity_dir))["lessons"]
    assert len(lessons) == 1 and lessons[0]["id"] == "L3-TestPrincipleTwo"


def test_index_selection_one_based(entity_dir):
    rc = run_promote(entity_dir, ["--indices", "1,3", "--apply", "--confirm"])
    assert rc == 0
    lessons = yaml.safe_load(read_soul(entity_dir))["lessons"]
    assert {l["id"] for l in lessons} == {"L3-TestPrincipleOne", "L2-TestInsightThree"}


# ─────────────────────── T3: dedupe works ───────────────────────

def test_dedupe_on_id(entity_dir):
    run_promote(entity_dir, ["--all", "--apply", "--confirm"])
    count_before = len(yaml.safe_load(read_soul(entity_dir))["lessons"])

    # Re-stage same id with different content — must be skipped by id.
    ppath = entity_dir / "data/entities/testent/proposed_lessons.yaml"
    ppath.write_text(
        VALID_PROPOSALS.replace("ses_test001", "ses_test999"), encoding="utf-8"
    )
    rc = run_promote(entity_dir, ["--all", "--apply", "--confirm"])
    assert rc == 0
    lessons = yaml.safe_load(read_soul(entity_dir))["lessons"]
    assert len(lessons) == count_before, "duplicate id was re-promoted"


def test_dedupe_on_content_hash(entity_dir):
    run_promote(entity_dir, ["--ids", "L3-TestPrincipleOne", "--apply", "--confirm"])

    # New id, identical principle content → content-hash dedupe must catch it.
    dup = (
        "proposals:\n"
        "- id: L3-DifferentIdSameContent\n"
        '  principle: "First test principle about atomic writes."\n'
    )
    (entity_dir / "data/entities/testent/proposed_lessons.yaml").write_text(dup, encoding="utf-8")
    rc = run_promote(entity_dir, ["--all", "--apply", "--confirm"])
    assert rc == 0
    lessons = yaml.safe_load(read_soul(entity_dir))["lessons"]
    assert len(lessons) == 1, "identical content promoted under new id"
    assert lessons[0]["id"] == "L3-TestPrincipleOne"


# ─────────────────────── T4: corrupt proposal skipped gracefully ───────────────────────

CORRUPT_PROPOSALS = """proposals:
- id: L3-GoodOne
  principle: "A perfectly valid principle."
- not_even_a_mapping_string
- 42
- principle: "missing an id entirely"
- id: L3-EmptyBody
  principle: ""
  tags: []
- id: L3-Survivor
  principle: "The survivor after the corruption storm."
"""


def test_corrupt_proposals_skipped_not_crash(entity_dir):
    (entity_dir / "data/entities/testent/proposed_lessons.yaml").write_text(
        CORRUPT_PROPOSALS, encoding="utf-8"
    )
    rc = run_promote(entity_dir, ["--all", "--apply", "--confirm"])
    assert rc == 0, "malformed proposals must never crash the merge"

    lessons = yaml.safe_load(read_soul(entity_dir))["lessons"]
    assert {l["id"] for l in lessons} == {"L3-GoodOne", "L3-Survivor"}

    # soul.yaml still fully parseable
    assert isinstance(yaml.safe_load(read_soul(entity_dir)), dict)


def test_out_of_range_selection_reported(entity_dir):
    proposals = soul_promote.load_proposals(
        entity_dir / "data/entities/testent/proposed_lessons.yaml"
    )
    selected, skips = soul_promote.select_proposals(proposals, False, [], [99])
    assert selected == []
    assert any("out of range" in s for s in skips)


# ─────────────────────── T5: schema-guard abort restores backup ───────────────────────

def test_schema_guard_pre_write_abort_leaves_soul_untouched(entity_dir, monkeypatch):
    # Force dump_lesson_block to emit garbage → guard fails BEFORE any write.
    monkeypatch.setattr(soul_promote, "dump_lesson_block", lambda entries: "\t::not::yaml::\n")
    before = read_soul(entity_dir)

    with pytest.raises(Exception):  # PromotionError from pre-write guard
        run_promote(entity_dir, ["--all", "--apply", "--confirm"])

    assert read_soul(entity_dir) == before, "failed guard still mutated soul.yaml"
    baks = list((entity_dir / "data/entities/testent").glob("soul.yaml.bak.*"))
    assert baks == [], "snapshot taken despite pre-write guard failure"


def test_post_write_verification_failure_restores_snapshot(entity_dir, monkeypatch):
    # Let the write happen, then break post-write verification → restore path.
    real_verify = soul_promote.verify_result

    calls = {"n": 0}

    def flaky_verify(old_text, new_text, expected_entries):
        calls["n"] += 1
        if calls["n"] == 1:
            return real_verify(old_text, new_text, expected_entries)  # pre-write passes
        raise soul_promote.PromotionError("simulated post-write corruption")

    monkeypatch.setattr(soul_promote, "verify_result", flaky_verify)

    with pytest.raises(soul_promote.PromotionError):
        run_promote(entity_dir, ["--all", "--apply", "--confirm"])

    restored = yaml.safe_load(read_soul(entity_dir))
    assert "lessons" not in restored or not restored["lessons"], "restore failed — soul was mutated"
    baks = list((entity_dir / "data/entities/testent").glob("soul.yaml.bak.*"))
    assert len(baks) == 1, "restoration snapshot missing"


# ─────────────────────── T6: snapshot pruning keeps last N ───────────────────────

def test_snapshot_pruning_keeps_last_five(entity_dir):
    soul_path = entity_dir / "data/entities/testent/soul.yaml"
    for i in range(7):
        bak = soul_path.with_name(f"soul.yaml.bak.2026010{i}T000000Z")
        bak.write_text(f"# backup {i}", encoding="utf-8")

    pruned = soul_promote.prune_snapshots(soul_path, keep=5)
    assert pruned == 2
    remaining = sorted(p.name for p in soul_path.parent.glob("soul.yaml.bak.*"))
    assert len(remaining) == 5
    assert remaining[0].endswith("20260102T000000Z"), "oldest should be pruned first"


# ─────────────────────── T7: CLI smoke via subprocess ───────────────────────

def test_cli_subprocess_dry_run_smoke(entity_dir):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "testent", "--all"],
        cwd=entity_dir,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Entity resolution is repo-root-relative; inside tmp layout the default root
    # won't contain testent, so expect a clean error exit — NOT a traceback crash.
    assert result.returncode in (0, 1)
    assert "Traceback" not in result.stderr


def test_cli_requires_selection(entity_dir):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "testent"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0, "must refuse to run without --all/--ids/--indices"
