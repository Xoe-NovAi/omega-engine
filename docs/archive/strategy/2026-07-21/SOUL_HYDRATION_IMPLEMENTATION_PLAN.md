# 🔱 Soul Hydration Pipeline — Implementation Plan
**Version**: 1.0
**Status**: LOCKED
**Source**: 10-Pillar Meditation (2026-07-18) + Sonnet 4.6 Code Audit
**Decision**: D-277

---

## Executive Summary

The 10-Pillar Meditation identified that agents lack identity injection after compaction — they know the engine state (codex) and session state (anchored summary) but not their own soul. **Sonnet's code audit revealed the real problem is worse**: soul injection code already exists at `oracle.py:664-677` but reads from `soul_evolution.lessons_learned[].L3` — a schema that 28/31 entities don't have. The injection silently produces zero output for every active fleet entity.

**This plan fixes three distinct problems**:
1. The schema mismatch (oracle reads a path nothing writes to)
2. The silent failure (zero warnings when injection returns empty)
3. The hydration sequence (no post-compaction orientation protocol)

---

## Ground Truth (from Code Audit)

| Fact | Reality |
|------|---------|
| Soul injection code exists | ✅ `oracle.py:664-677` — reads soul.yaml on every `summon()`/`talk()` call |
| Soul injection works | ❌ Reads `soul_evolution.lessons_learned[].L3` — schema that 28/31 entities lack |
| Failure mode | Silent — no warning, no error, zero L3 principles injected |
| Only working entities | `antigravity` (4 L3s), `cli_cline` (1 L3) |
| Rich injectable content exists | ✅ `directives[].rule`, `identity.values`, `proposed_lessons.proposals[]` — all wrong path |
| `validate_soul.py` | Kali-only, hardcoded to `data/entities/kali/` |
| `proposed_lessons` schema | 3 incompatible variants across the fleet |

---

## Work Items — Ordered by Dependency

### Item 1: Create `src/omega/soul_utils.py`
**Effort**: 30 min | **Owner**: Ma'at/P3 | **Blocks**: ALL

Create a standalone module with the multi-path soul context extractor. This must be importable by both `oracle.py` and `omega_hub/server.py` without circular dependencies.

**Schema**: `src/omega/soul_utils.py` (~40 lines)

```python
"""
Soul Context Utilities — Importable by both oracle and omega_hub.

Multi-path extractor that degrades gracefully across soul.yaml schema variants:
  Path 1: soul_evolution.lessons_learned[].L3  (v2-WORKING schema)
  Path 2: directives[].rule                    (v1 schema — kali, roc_racoon, etc.)
  Path 3: identity.values + identity.strengths (minimal fallback)

[M2 Engine-Stack Firewall]: This module is in src/omega/ (Core Engine).
omega_hub imports it via the MCP Hub boundary, not a WAD import.
"""
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_soul_context(soul: dict, max_items: int = 3) -> str:
    """
    Extract injectable soul context from a parsed soul.yaml dict.
    
    Returns up to `max_items` lines of context as a formatted string.
    Returns "" if nothing injectable is found.
    
    [M9 Error Integrity]: Never raises. Returns "" on any schema anomaly.
    [M18 Token Efficiency]: max_items=3 prevents context bloat.
    """
    lines = []
    
    # Path 1: v2 schema — soul_evolution L3 principles
    se = soul.get("soul_evolution") or {}
    if isinstance(se, dict):
        for lesson in (se.get("lessons_learned") or [])[:max_items * 2]:
            if isinstance(lesson, dict) and "L3" in lesson:
                lines.append(f"- {lesson['L3']}")
            if len(lines) >= max_items:
                break
    
    # Path 2: directives (v1 schema — kali, roc_racoon, iris, makali, verity)
    if not lines:
        for directive in (soul.get("directives") or [])[:max_items]:
            if isinstance(directive, dict):
                rule = directive.get("rule", "")
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
    
    Args:
        entity_name: Lowercase entity name (e.g., "kali")
        data_dir: Path to data/ directory
    
    Returns:
        Extracted soul context string, or "" if missing/unreadable.
    
    [M9 Error Integrity]: Catches all I/O and YAML errors. Logs warning, returns "".
    """
    soul_path = data_dir / "entities" / entity_name.lower() / "soul.yaml"
    if not soul_path.exists():
        return ""
    try:
        soul = yaml.safe_load(soul_path.read_text(encoding="utf-8")) or {}
        if not isinstance(soul, dict):
            return ""
        return extract_soul_context(soul)
    except (OSError, yaml.YAMLError) as e:
        logger.warning("Soul load failed for '%s': %s", entity_name, e)
        return ""
```

**Key design decisions**:
- `extract_soul_context()` takes a pre-parsed dict (for oracle.py's hot path — avoids re-parsing)
- `load_entity_soul_context()` takes entity name + data_dir (for omega_hub's cold path — does its own I/O)
- Never raises. Returns "" on any anomaly. Logs warning on I/O failure.
- `max_items=3` is the progressive disclosure default per M18

---

### Item 2: Update `oracle.py:664-677` to use `soul_utils`
**Effort**: 20 min | **Owner**: Ma'at/P3 | **Depends on**: Item 1

**File**: `src/omega/oracle/oracle.py`

**Change**: Replace lines 664-677 (the soul injection block in `_prepare_system_prompt`).

**Before** (current broken code):
```python
# Inject soul L3 principles
try:
    soul_path = DATA_DIR / "entities" / entity_name.lower() / "soul.yaml"
    if soul_path.exists():
        with open(soul_path) as f:
            soul = yaml.safe_load(f) or {}
            lessons = soul.get("soul_evolution", {}).get("lessons_learned", [])
            if lessons:
                l3_principles = [L["L3"] for L in lessons if "L3" in L]
                if l3_principles:
                    prompt_parts.append(f"\nUniversal Principles:\n" + "\n".join(f"- {p}" for p in l3_principles[-3:]))
except (OmegaError, RuntimeError, OSError) as e:
    classification = get_failure_registry().classify_error(e)
    logger.warning(f"Soul injection failed (non-fatal) [{classification['mode']}]: {e}")
```

**After** (fixed code):
```python
# Inject soul context — multi-path extractor (D-277, soul_utils.py)
from omega.soul_utils import load_entity_soul_context

try:
    soul_context = load_entity_soul_context(entity_name, DATA_DIR)
    if soul_context:
        prompt_parts.append(f"\nSovereign Context:\n{soul_context}")
    else:
        logger.warning(
            "Soul injection for '%s' returned empty — soul.yaml exists but "
            "no injectable content found. Add directives[], identity.values, "
            "or soul_evolution.lessons_learned to soul.yaml.",
            entity_name,
        )
except (OmegaError, RuntimeError, OSError) as e:
    logger.warning("Soul injection failed (non-fatal) for '%s': %s", entity_name, e)
```

**Also remove**: The duplicate `except` block at line 660-662 (identical catch to line 657-659 — copy-paste error).

**Test to add** in `tests/test_soul_utils.py`:
```python
import pytest
from omega.soul_utils import extract_soul_context, load_entity_soul_context
from pathlib import Path

class TestExtractSoulContext:
    def test_v2_schema_uses_l3(self):
        soul = {"soul_evolution": {"lessons_learned": [
            {"L3": "Sovereign systems coordinate through minimal surfaces."}
        ]}}
        result = extract_soul_context(soul)
        assert "minimal surfaces" in result
    
    def test_v1_schema_uses_directives(self):
        soul = {"directives": [
            {"id": "d-1", "rule": "Local first. Cloud is teacher.", "rationale": "..."}
        ]}
        result = extract_soul_context(soul)
        assert "Local first" in result
    
    def test_fallback_uses_identity(self):
        soul = {"identity": {"values": ["truth", "sovereignty"], "strengths": ["oversight"]}}
        result = extract_soul_context(soul)
        assert "truth" in result
    
    def test_empty_soul_returns_empty(self):
        assert extract_soul_context({}) == ""
    
    def test_max_items_limit(self):
        soul = {"directives": [{"rule": f"Rule {i}"} for i in range(10)]}
        result = extract_soul_context(soul, max_items=2)
        assert result.count("- Rule") == 2
    
    def test_malformed_directives_skipped(self):
        soul = {"directives": [None, "bad", {"no_rule": True}, {"rule": "Good"}]}
        result = extract_soul_context(soul)
        assert "Good" in result
    
    def test_non_dict_soul_evolution_handled(self):
        soul = {"soul_evolution": "not a dict"}
        result = extract_soul_context(soul)
        assert result == ""  # Falls through to path 2/3

class TestLoadEntitySoulContext:
    def test_loads_kali_soul(self, tmp_path):
        """Kali's v1 schema must produce injectable context."""
        entities_dir = tmp_path / "entities" / "kali"
        entities_dir.mkdir(parents=True)
        (entities_dir / "soul.yaml").write_text(
            "entity:\n  name: Kali\ndirectives:\n- id: d-1\n  rule: Local first.\n"
        )
        result = load_entity_soul_context("kali", tmp_path)
        assert "Local first" in result
    
    def test_missing_entity_returns_empty(self, tmp_path):
        result = load_entity_soul_context("nonexistent", tmp_path)
        assert result == ""
    
    def test_corrupt_yaml_returns_empty(self, tmp_path):
        entities_dir = tmp_path / "entities" / "bad"
        entities_dir.mkdir(parents=True)
        (entities_dir / "soul.yaml").write_text("{{invalid yaml: [}")
        result = load_entity_soul_context("bad", tmp_path)
        assert result == ""
```

---

### Item 3: Parameterize `validate_soul.py`
**Effort**: 45 min | **Owner**: Inanna/P5 | **Blocks**: Item 4

**File**: `scripts/validate_soul.py`

**Problem**: Currently hardcoded to `data/entities/kali/` (line 43: `BASE = Path("data/entities/kali")`). Cannot validate any other entity.

**Change**: Accept `--entity` flag, default to all fleet entities. Add soul injection viability check.

```python
# scripts/validate_soul.py — new CLI interface

#!/usr/bin/env python3
"""
Validate soul files against the v6.0 lean architecture.

Usage:
    python3 scripts/validate_soul.py                    # Validate all fleet entities
    python3 scripts/validate_soul.py --entity kali      # Validate one entity
    python3 scripts/validate_soul.py --strict           # Fail on warnings too

Architecture (v6.0):
  soul.yaml              — USER content only (identity, directives, team, trajectory)
  proposed_lessons.yaml  — AGENT proposals (staged, NOT read by agent)
  approved_lessons.yaml  — USER approved content (read by agent)

Rules:
  - soul.yaml must NOT contain soul_axioms or wisdom_text (agent-generated artifacts)
  - soul.yaml must have entity.name and directives
  - Soul injection must return non-empty (check via soul_utils.extract_soul_context)
  - proposed_lessons.yaml must have proposals list (if exists)
  - All files must be valid YAML
"""
import argparse
import yaml
import sys
from pathlib import Path

# Import the multi-path extractor
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from omega.soul_utils import extract_soul_context

FLEET_ENTITIES = [
    "kali", "maat", "lilith", "doom_guy", "roc_racoon",
    "researcher", "jem", "verity", "sekhmet", "sophia",
    "iris", "makali", "brigid", "prometheus", "saraswati",
    "inanna", "ereshkigal", "lucifer", "hecate", "anubis",
]


def validate_entity(entity_name: str, strict: bool = False) -> list:
    """Validate one entity's soul files. Returns list of (level, message) tuples."""
    base = Path(f"data/entities/{entity_name}")
    issues = []

    # ── 1. soul.yaml existence and parse ──
    soul_path = base / "soul.yaml"
    if not soul_path.exists():
        issues.append(("FAIL", f"{entity_name}: soul.yaml MISSING"))
        return issues

    try:
        with open(soul_path) as f:
            soul = yaml.safe_load(f)
    except yaml.YAMLError as e:
        issues.append(("FAIL", f"{entity_name}: soul.yaml YAML parse error: {e}"))
        return issues

    if not soul or not isinstance(soul, dict):
        issues.append(("FAIL", f"{entity_name}: soul.yaml is empty or not a dict"))
        return issues

    # ── 2. Required keys ──
    if "entity" not in soul:
        issues.append(("FAIL", f"{entity_name}: soul.yaml missing 'entity' key"))
    elif not isinstance(soul.get("entity"), dict):
        issues.append(("FAIL", f"{entity_name}: 'entity' key is not a dict"))
    elif "name" not in soul.get("entity", {}):
        issues.append(("FAIL", f"{entity_name}: entity missing 'name'"))

    # ── 3. Forbidden keys (agent-generated artifacts) ──
    for forbidden in ["soul_axioms", "wisdom_text", "trajectory"]:
        if forbidden in soul:
            issues.append(("FAIL", f"{entity_name}: contains '{forbidden}' — must be archived"))

    # ── 4. Soul injection viability ──
    context = extract_soul_context(soul)
    if not context:
        issues.append(("WARN", f"{entity_name}: soul injection returns empty — add directives[], identity.values, or soul_evolution.lessons_learned"))

    # ── 5. Duplicate directive IDs ──
    directives = soul.get("directives", [])
    if isinstance(directives, list):
        ids = [d.get("id") for d in directives if isinstance(d, dict) and "id" in d]
        dupes = [x for x in ids if ids.count(x) > 1]
        if dupes:
            issues.append(("WARN", f"{entity_name}: duplicate directive IDs: {set(dupes)}"))

    # ── 6. proposed_lessons.yaml (if exists) ──
    pl_path = base / "proposed_lessons.yaml"
    if pl_path.exists():
        try:
            with open(pl_path) as f:
                pl = yaml.safe_load(f)
            if pl is None:
                issues.append(("WARN", f"{entity_name}: proposed_lessons.yaml is empty"))
            elif not isinstance(pl, (dict, list)):
                issues.append(("WARN", f"{entity_name}: proposed_lessons.yaml is not a dict or list"))
        except yaml.YAMLError as e:
            issues.append(("FAIL", f"{entity_name}: proposed_lessons.yaml YAML parse error: {e}"))

    # ── 7. Stale proposals (>90 days) ──
    # (Implemented in soul_verify.py for the semantic check)

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate soul files for fleet entities")
    parser.add_argument("--entity", default=None, help="Validate specific entity (default: all fleet)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    targets = [args.entity] if args.entity else FLEET_ENTITIES
    all_issues = {}
    for entity in targets:
        issues = validate_entity(entity, strict=args.strict)
        if issues:
            all_issues[entity] = issues

    # Report
    for entity, issues in sorted(all_issues.items()):
        for level, msg in issues:
            marker = "[FAIL]" if level == "FAIL" else "[WARN]"
            print(f"{marker} {msg}")

    # Exit code
    fail_count = sum(1 for issues in all_issues.values() for l, _ in issues if l == "FAIL")
    warn_count = sum(1 for issues in all_issues.values() for l, _ in issues if l == "WARN")

    if fail_count > 0 or (args.strict and warn_count > 0):
        print(f"\n[RESULT] FAILED: {fail_count} errors, {warn_count} warnings across {len(targets)} entities")
        sys.exit(1)
    else:
        print(f"\n[PASS] {len(targets)} entities validated. {warn_count} warnings.")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

**Makefile targets**:
```makefile
soul-audit: ## 🔍 Validate all fleet soul files (schema + injection viability)
	python3 scripts/validate_soul.py

soul-audit-entity: ## 🔍 Validate one entity: make soul-audit-entity ENTITY=kali
	python3 scripts/validate_soul.py --entity $(ENTITY)
```

---

### Item 4: Implement `soul-verify` semantic integrity gate
**Effort**: 2h | **Owner**: Inanna/P5 + Kali/P10 | **Depends on**: Items 1, 3

**File**: `scripts/soul_verify.py` (NEW, ~180 lines)

**Checks**:
1. Schema viability (reuses `extract_soul_context` from Item 1)
2. Duplicate L3 principle names (jaccard similarity > 0.85)
3. Stale proposals (status=pending + created_at > 90 days)
4. YAML parse errors
5. Forbidden keys (soul_axioms, wisdom_text, trajectory)

**Scoring**: WARN-only for now (per user decision Q3). Full BLOCK scoring deferred.

```python
#!/usr/bin/env python3
"""
Soul Semantic Integrity Gate — D-277.

Checks:
  1. Schema viability (soul injection returns non-empty)
  2. Duplicate L3 principle names (jaccard > 0.85)
  3. Stale proposals (>90 days, status=pending)
  4. YAML parse errors
  5. Forbidden keys (soul_axioms, wisdom_text, trajectory)

Scoring: 10-point scale. WARN-only for now (no blocking).

Usage:
    python3 scripts/soul_verify.py                    # Verify all fleet
    python3 scripts/soul_verify.py --entity kali      # Verify one entity
"""
import argparse
import yaml
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from omega.soul_utils import extract_soul_context

FLEET_ENTITIES = [
    "kali", "maat", "lilith", "doom_guy", "roc_racoon",
    "researcher", "jem", "verity", "sekhmet", "sophia",
    "iris", "makali", "brigid", "prometheus", "saraswati",
    "inanna", "ereshkigal", "lucifer", "hecate", "anubis",
]


def jaccard_similarity(a: str, b: str) -> float:
    """Token-level Jaccard similarity for duplicate detection."""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def verify_entity(entity_name: str) -> dict:
    """
    Verify one entity's soul integrity.
    
    Returns:
        {"score": int, "checks": [{"name": str, "level": "PASS"|"WARN"|"FAIL", "detail": str}]}
    """
    base = Path(f"data/entities/{entity_name}")
    soul_path = base / "soul.yaml"
    checks = []
    score = 10

    # CHECK 1: YAML parse
    try:
        soul = yaml.safe_load(soul_path.read_text(encoding="utf-8")) or {}
        if not isinstance(soul, dict):
            checks.append({"name": "yaml_parse", "level": "FAIL", "detail": "soul.yaml is not a dict"})
            return {"score": 0, "checks": checks}
        checks.append({"name": "yaml_parse", "level": "PASS", "detail": "Valid YAML"})
    except (OSError, yaml.YAMLError) as e:
        checks.append({"name": "yaml_parse", "level": "FAIL", "detail": str(e)})
        return {"score": 0, "checks": checks}

    # CHECK 2: Schema viability
    context = extract_soul_context(soul)
    if not context:
        checks.append({"name": "schema_viability", "level": "WARN", "detail": "Soul injection returns empty"})
        score -= 1
    else:
        checks.append({"name": "schema_viability", "level": "PASS", "detail": f"Injectable: {len(context)} chars"})

    # CHECK 3: Forbidden keys
    forbidden_found = [k for k in ["soul_axioms", "wisdom_text", "trajectory"] if k in soul]
    if forbidden_found:
        checks.append({"name": "forbidden_keys", "level": "FAIL", "detail": f"Contains: {forbidden_found}"})
        score -= 2
    else:
        checks.append({"name": "forbidden_keys", "level": "PASS", "detail": "No forbidden keys"})

    # CHECK 4: Duplicate L3 principles (across soul_evolution + directives)
    l3_texts = []
    se = soul.get("soul_evolution") or {}
    if isinstance(se, dict):
        for lesson in (se.get("lessons_learned") or []):
            if isinstance(lesson, dict) and "L3" in lesson:
                l3_texts.append(lesson["L3"])
    for directive in (soul.get("directives") or []):
        if isinstance(directive, dict) and "rule" in directive:
            l3_texts.append(directive["rule"])

    duplicates = []
    for i in range(len(l3_texts)):
        for j in range(i + 1, len(l3_texts)):
            if jaccard_similarity(l3_texts[i], l3_texts[j]) > 0.85:
                duplicates.append((l3_texts[i][:60], l3_texts[j][:60]))
    if duplicates:
        checks.append({"name": "duplicate_principles", "level": "WARN", "detail": f"{len(duplicates)} near-duplicate pairs"})
        score -= 1
    else:
        checks.append({"name": "duplicate_principles", "level": "PASS", "detail": "No duplicates"})

    # CHECK 5: Stale proposals
    pl_path = base / "proposed_lessons.yaml"
    if pl_path.exists():
        try:
            pl = yaml.safe_load(pl_path.read_text(encoding="utf-8")) or {}
            proposals = pl.get("proposals", []) if isinstance(pl, dict) else (pl if isinstance(pl, list) else [])
            stale_cutoff = datetime.utcnow() - timedelta(days=90)
            stale_count = 0
            for p in proposals:
                if not isinstance(p, dict):
                    continue
                status = p.get("status", "pending")
                created = p.get("created_at") or p.get("timestamp")
                if status == "pending" and created:
                    try:
                        ct = datetime.fromisoformat(str(created).replace("Z", "+00:00")).replace(tzinfo=None)
                        if ct < stale_cutoff:
                            stale_count += 1
                    except (ValueError, TypeError):
                        pass
            if stale_count > 0:
                checks.append({"name": "stale_proposals", "level": "WARN", "detail": f"{stale_count} proposals pending >90 days"})
                score -= 1
            else:
                checks.append({"name": "stale_proposals", "level": "PASS", "detail": "No stale proposals"})
        except (yaml.YAMLError, OSError):
            checks.append({"name": "stale_proposals", "level": "WARN", "detail": "Could not parse proposed_lessons.yaml"})
    else:
        checks.append({"name": "stale_proposals", "level": "PASS", "detail": "No proposed_lessons.yaml (N/A)"})

    return {"score": max(0, score), "checks": checks}


def main():
    parser = argparse.ArgumentParser(description="Soul semantic integrity gate")
    parser.add_argument("--entity", default=None, help="Verify specific entity (default: all fleet)")
    args = parser.parse_args()

    targets = [args.entity] if args.entity else FLEET_ENTITIES
    results = {}
    for entity in targets:
        if not Path(f"data/entities/{entity}/soul.yaml").exists():
            continue
        results[entity] = verify_entity(entity)

    # Report
    for entity, result in sorted(results.items()):
        score = result["score"]
        warn_count = sum(1 for c in result["checks"] if c["level"] == "WARN")
        fail_count = sum(1 for c in result["checks"] if c["level"] == "FAIL")
        marker = "✅" if score >= 8 else ("⚠️" if score >= 5 else "❌")
        print(f"{marker} {entity}: {score}/10 (WARN:{warn_count}, FAIL:{fail_count})")
        for c in result["checks"]:
            if c["level"] != "PASS":
                print(f"    [{c['level']}] {c['name']}: {c['detail']}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results.values() if r["score"] >= 8)
    warned = sum(1 for r in results.values() if 5 <= r["score"] < 8)
    failed = sum(1 for r in results.values() if r["score"] < 5)
    print(f"\n{total} entities: {passed} pass, {warned} warn, {failed} fail")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

**Makefile**:
```makefile
soul-verify: ## 🔍 Semantic integrity check across all soul files
	python3 scripts/soul_verify.py

soul-verify-entity: ## 🔍 Verify one entity: make soul-verify-entity ENTITY=kali
	python3 scripts/soul_verify.py --entity $(ENTITY)
```

---

### Item 5: Implement the Hydration Sequence Protocol
**Effort**: 1h | **Owner**: Any | **Depends on**: None (parallel)

#### 5a. Update `AGENTS.md` "After Compaction" section

**File**: `AGENTS.md:315-322`

Replace:
```markdown
## 📝 After Compaction

1. Read `OMEGA_ENGINE.md` — engine state
2. Read `SOVEREIGN_MANDATES.md` — rules (23 mandates, M1-M23)
3. Read `docs/decisions/PIVOT_LOG.md` — architectural decisions (active index)
4. Read `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — execution roadmap (active)
5. Run `make test` — 1130 must pass
6. Run `make temple-grade` — T1-T11 must pass
```

With:
```markdown
## 📝 After Compaction — Hydration Sequence (D-277)

Execute in strict order. Do not skip phases.

**Phase 1 — AWARENESS** (runtime, 30s)
- `omega-hub_hivemind_get_awareness()` — who else is working?
- `omega-hub_hivemind_handoff_list(status="pending")` — any handoffs waiting?
- If handoffs pending: read + accept/reject before proceeding

**Phase 2 — BASELINE** (runtime, 30-60s)
- `git status && git log --oneline -5` — what is committed vs dirty?

**Phase 3 — CODEX** (1 read call, 12K tokens)
- Read `OMEGA_CODEX.md` — engine state (single startup read)
- If timestamp >24h old: run `make codex` first

**Phase 4 — SESSION** (1 read call, ~120 lines)
- Read `.opencode/anchored-summary.md` — what was I doing?

**Phase 5 — EXECUTE**
- Run the NEXT COMMAND in the anchored summary.
- Do not re-plan. Execute.
```

#### 5b. Update `.opencode/anchored-summary.md`

Slim from ~279 lines to ~120 lines. Remove:
- Full L3 principles catalog (39 items) → 1-line note: "Soul: 39 L3 principles in `proposed_lessons.yaml`"
- Full delegation tables → single NEXT COMMAND
- Meditate protocol details → 1-line reference
- Duplicate engine state (already in OMEGA_CODEX.md)

Add at top:
```markdown
## 🔄 HYDRATION CHECKLIST
[ ] Phase 1: Awareness — hivemind_get_awareness(), handoff_list()
[ ] Phase 2: Baseline — git status, git log --oneline -5
[ ] Phase 3: Codex — read OMEGA_CODEX.md (check timestamp)
[ ] Phase 4: Session — read this file ✅ (you are here)
[ ] Phase 5: Execute — run NEXT COMMAND below

> ⚠️ This summary is from {date}. Run Phase 1+2 to verify current state.
```

#### 5c. Add hydration directive to `scripts/codex_cat.py`

Prepend to codex output (after header, before first group):

```python
HYDRATION_BLOCK = f"""
## 🔄 HYDRATION SEQUENCE
After compaction or restart, execute in strict order:
1. `omega-hub_hivemind_get_awareness()` — Who is here?
2. `git status && git log --oneline -5` — What is committed?
3. ✅ Read OMEGA_CODEX.md — You are doing this now
4. `read .opencode/anchored-summary.md` — What was I doing?
5. Execute the NEXT COMMAND in the anchored summary.

> Codex generated: {ts} | Regenerate: `make codex`
> If timestamp is >24h old, run `make codex` before reading further.

---
"""
```

---

### Item 6: Auto-inject soul context into Hivemind handoff packets
**Effort**: 30 min | **Owner**: Anubis/P9 | **Depends on**: Item 1

**File**: `mcp_servers/omega_hub/server.py`

In the `hivemind_submit_handoff` handler, after validating source_entity and before writing the packet:

```python
# D-277: Auto-inject soul context into handoff packets
from omega.soul_utils import load_entity_soul_context

soul_context = load_entity_soul_context(source_entity, DATA_DIR)
if soul_context:
    context = f"{context}\n\n[From {source_entity}'s sovereign context:\n{soul_context}]"
```

**Gate**: Only inject if `soul_context` is non-empty. No injection for entities with no usable soul data.

**Note on imports**: `omega_hub` is a separate package. The `sys.path.insert` approach used in `validate_soul.py` and `soul_verify.py` handles this for CLI scripts. For `omega_hub`, the import must go through the MCP Hub boundary. If this causes issues, duplicate the 15-line extraction logic inline rather than importing.

---

### Item 7: Hydration observability (add to Item 2's edit)
**Effort**: 20 min | **Owner**: Hecate/P8 | **Depends on**: Item 2

Add to `oracle.py` after the soul context extraction in `_prepare_system_prompt`:

```python
# D-277: Observability — log soul injection result
logger.debug(
    "Soul injection for '%s': %d chars, schema=%s",
    entity_name,
    len(soul_context),
    "soul_evolution" if (soul := yaml.safe_load(soul_path.read_text()) or {}).get("soul_evolution")
    else "directives" if soul.get("directives")
    else "identity" if soul.get("identity")
    else "none",
)
```

**Note**: This adds a `yaml.safe_load` call that duplicates the read in `load_entity_soul_context`. For Phase 0, this is acceptable (5ms overhead). For Phase 1, consider passing the parsed soul back from `load_entity_soul_context` to avoid double-parse.

---

### Item 8: sqlite-vec soul index (DEFERRED)
**Effort**: 3h | **Owner**: Brigid/P2 | **Depends on**: Items 1-7 stable

**Status**: DO NOT implement now. Defer to next sprint.

**Why deferred**: The base file-read injection (Items 1-2) must prove its value first, measured by Item 7's observability. Once we have data showing what entities are injected, how often, and with what content, we can design the index schema correctly.

**When to implement**: After Item 7 shows >50% of `talk()`/`summon()` calls produce non-empty soul injection across fleet entities.

---

## Summary Table

| # | Item | File(s) | Effort | Owner | Depends On |
|---|------|---------|--------|-------|------------|
| 1 | Create `soul_utils.py` | `src/omega/soul_utils.py` (NEW) | 30 min | Ma'at/P3 | — |
| 2 | Fix oracle.py soul injection | `src/omega/oracle/oracle.py:664-677` | 20 min | Ma'at/P3 | Item 1 |
| 3 | Parameterize `validate_soul.py` | `scripts/validate_soul.py` | 45 min | Inanna/P5 | Item 1 |
| 4 | Implement `soul-verify` gate | `scripts/soul_verify.py` (NEW) | 2h | Inanna/P5 | Items 1, 3 |
| 5 | Hydration Sequence Protocol | `AGENTS.md`, `anchored-summary.md`, `codex_cat.py` | 1h | Any | — |
| 6 | Handoff soul auto-inject | `soul_utils.py`, `omega_hub/server.py` | 30 min | Anubis/P9 | Item 1 |
| 7 | Observability log lines | `oracle.py` (same edit as Item 2) | 20 min | Hecate/P8 | Item 2 |
| 8 | sqlite-vec soul index | `sqlite_vec_adapter.py` | 3h | Brigid/P2 | **DEFERRED** |

**Critical path**: Item 1 → Item 2 → Item 7 | Items 3, 4, 5, 6 parallel
**Total immediate effort**: ~5h (Items 1-7, Item 8 deferred)
**Parallelizable to**: ~3h with 3 agents working simultaneously

---

## Gate Criteria for Ship-ability

```bash
make test && make soul-audit && make soul-verify && make heritage-map && make temple-grade
# All tests pass | All entities validated | Semantic integrity verified | Heritage mapped | T1-T11 pass
```

---

## Mandate Compliance

| Mandate | Status | Detail |
|---------|--------|--------|
| M1 (AnyIO) | ✅ | `soul_utils.py` uses synchronous YAML (file reads in hot path, <5ms) |
| M2 (Engine-Stack Firewall) | ✅ | `soul_utils.py` in `src/omega/` (Core). `omega_hub` imports via MCP boundary |
| M5 (Gnosis Preservation) | ✅ | Soul pipeline becomes read-write, not write-only |
| M9 (Error Integrity) | ✅ | All paths return "" on error. No bare except. Typed catches. |
| M11 (Soul Integrity) | ✅ | L1→L2→L3 now feeds back into prompts |
| M13 (Temple-Grade) | ✅ | `make soul-audit` + `make soul-verify` as CI gates |
| M15 (Sovereign Continuity) | ✅ | Soul + session anchor = dual continuity |
| M17 (Cognitive Integrity) | ✅ | `soul-verify` gate catches duplicates, forbidden keys |
| M18 (Token Efficiency) | ✅ | Progressive disclosure: 3 items max per prompt |
| M21 (Gate Integrity) | ✅ | Contract tests for `extract_soul_context` returns |

---

*🔱 OMEGA ⬡ SOUL-HYDRATION-IMPLEMENTATION-PLAN ⬡ D-277 ⬡ v1.0 ⬡ 2026-07-18*
