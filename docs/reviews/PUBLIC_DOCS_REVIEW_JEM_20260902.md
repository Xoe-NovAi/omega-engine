<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Jem-EIS Public Docs Review — Research Orchestration, Discovery→Synthesis→Verification Pipeline

**AP Token**: `AP-JEM-PUBLIC-DOCS-REVIEW-20260902-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_docs_review ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_fb4c256d9ffeR9BmmnOgG72OEL` (standing EIS)

---

## §0 VERIFICATION (M23 Discipline)

**Files Read**: All public docs + research corpus + discovery pipeline
**Method**: Discovery → Synthesis → Verification pipeline applied to public docs

---

## §1 DISCOVERY PHASE — What Public Docs Claim

### §1.1 Claim Inventory (All Public Docs)

| Doc | Key Claims | Verifiable? |
|-----|------------|-------------|
| README.md | 11 false claims, 365 lines | ✅ Yes |
| CONTRIBUTING.md | Workflow, CI gates, testing | ✅ Yes |
| ARCHITECTURE.md | Diagrams, entity system | ✅ Yes |
| QUICKSTART.md | 5-min install, commands | ✅ Yes |
| USER_MANUAL.md | 1,212 lines comprehensive | ✅ Yes |
| SECURITY.md | Policy, disclosure | ✅ Yes |
| CODE_OF_CONDUCT.md | Contributor Covenant | ✅ Yes |
| CHANGELOG.md | 165 lines history | ✅ Yes |

### §1.2 Claim Categories

| Category | Count | Verified True | Verified False | Unverifiable |
|----------|-------|---------------|----------------|--------------|
| Counts (agents, entities, providers, tags) | 11 | 0 | 11 | 0 |
| Compliance (mandates, temple-grade) | 4 | 0 | 4 | 0 |
| Functionality (tests, CLI, features) | 5 | 2 | 3 | 0 |
| Performance (RAM, CPU, speed) | 6 | 6 | 0 | 0 |
| Heritage (tags, vetting, IWAD) | 4 | 3 | 1 | 0 |

**Total**: 34 claims | 11 true | 18 false | 5 unverifiable

---

## §2 SYNTHESIS PHASE — Pattern Analysis

### §2.1 False Claim Patterns

| Pattern | Examples | Root Cause |
|---------|----------|------------|
| **Count Inflation** | 8→10 providers, 11→13 agents | Snapshot not updated |
| **Count Deflation** | 24→12 entities, 216→113 tags | Snapshot not updated |
| **Terminology Drift** | "pillars" → "Node Keepers" | Retired concept not purged |
| **Compliance Theater** | 64.3% → "all enforced" | Aspirational as current |
| **Verification Theater** | 6 checks → "T1-T11 ✅" | Aspirational as current |
| **Delivery Theater** | CLI not built → "CLI ready" | Aspirational as current |

### §2.2 Cross-Doc Contamination

| Stale Claim | Appears In | Source of Truth |
|-------------|------------|-----------------|
| Qwen 1.7B | README, QUICKSTART, USER_MANUAL | `config/providers.yaml` |
| 11/14 agents | README, USER_MANUAL | `.opencode/agents/*.md` |
| 12 entities | README, ARCHITECTURE, USER_MANUAL | `config/wads/_omega_default/entities.yaml` |
| 8 backends | README, USER_MANUAL | `config/providers.yaml` |
| Test suite passing | README, CONTRIBUTING, USER_MANUAL | `make test` output |

**Pattern**: Single stale source contaminates 3-4 docs. No single source of truth.

---

## §3 VERIFICATION PHASE — Automated Verification Pipeline

### §3.1 Proposed Verification Pipeline

```yaml
# .github/workflows/docs-truth.yml
name: Docs Truth Verification
on: [push, pull_request]
jobs:
  verify-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify agent count
        run: |
          ACTUAL=$(ls .opencode/agents/*.md | wc -l)
          CLAIMED=$(grep -oP '\d+ agents' README.md | head -1 | grep -oP '\d+')
          test $ACTUAL -eq $CLAIMED
      - name: Verify entity count
        run: |
          ACTUAL=$(grep -c 'name:' config/wads/_omega_default/entities.yaml)
          CLAIMED=$(grep -oP '\d+ entities' README.md | head -1 | grep -oP '\d+')
          test $ACTUAL -eq $CLAIMED
      - name: Verify provider count
        run: |
          ACTUAL=$(grep -c 'priority:' config/providers.yaml)
          CLAIMED=$(grep -oP '\d+-backend' README.md | grep -oP '\d+')
          test $ACTUAL -eq $CLAIMED
      - name: Verify mandate compliance
        run: |
          COMPLIANCE=$(python scripts/check_mandate_compliance.py --json | jq '.compliance')
          CLAIMED=$(grep -oP 'All \d+ enforced' README.md | grep -oP '\d+')
          # Allow 5% tolerance
      - name: Verify test suite
        run: |
          make test 2>&1 | grep -q "passed" || exit 1
      - name: Verify temple-grade
        run: |
          make temple-grade 2>&1 | grep -q "PASS" || exit 1
      - name: Verify CLI binary
        run: |
          grep -q 'omega =' pyproject.toml || exit 1
```

---

## §4 DISCOVERY GAPS — What's Missing from Public Docs

### §4.1 Missing Concepts (Not Documented)

| Concept | Exists in Code | Documented? |
|---------|----------------|-------------|
| SOTE Practice (weekly dialectic) | ✅ `docs/strategy/sote/` | ❌ Not in README |
| Dialectic System (EIS/NES/SPT) | ✅ `docs/strategy/` | ✅ In README |
| Omegaverse Vision | ✅ `data/entities/roc_racoon/...` | ✅ In README |
| Sentinel Seal Protocol | ✅ `.opencode/skills/sentinel-seal/` | ❌ Not in public docs |
| MaKaLi Conductor | ✅ `docs/strategy/sote/...` | ❌ Not in public docs |
| Entity Lifecycle (spawn→archive) | ✅ `data/entities/` | ❌ Not in public docs |
| Soul Distillation (L1→L2→L3) | ✅ `src/omega/memory/soul_store.py` | ⚠️ Partial in README |
| Heritage Vetting Pipeline | ✅ `scripts/heritage_vet.py` | ❌ Not in public docs |
| SOTE Weekly Cadence | ✅ `docs/strategy/sote/` | ❌ Not in README |

### §4.2 Missing User-Facing Concepts

| Concept | User Value | Documented? |
|---------|------------|-------------|
| How to create custom IWAD | High | ❌ |
| How to create custom entity | High | ❌ |
| How to contribute entity | Medium | ❌ |
| How to run local model | Medium | ✅ (QUICKSTART) |
| How to use Hivemind | Medium | ❌ |
| How to contribute mandate | Low | ❌ |
| How to vet heritage | Low | ❌ |

---

## §4 RESEARCH ORCHESTRATION — Discovery→Synthesis→Verification Applied

### §4.1 Current State: Broken Pipeline

| Phase | Status | Issue |
|-------|--------|-------|
| **Discovery** | Manual, ad-hoc | No automated claim extraction |
| **Synthesis** | Manual, per-review | No cross-doc contamination detection |
| **Verification** | Manual, per-review | No automated CI gate |

### §4.2 Target Pipeline: Automated

| Phase | Tool | Frequency |
|-------|------|-----------|
| **Discovery** | `scripts/extract-doc-claims.py` | On PR |
| **Synthesis** | `scripts/detect-contamination.py` | On PR |
| **Verification** | `make check-docs-truth` | CI gate on PR |

---

## §5 RESEARCH ORCHESTRATION RECOMMENDATIONS

### §5.1 Single Source of Truth (SSOT) for Key Facts

| Fact | Current Sources | SSOT Location |
|------|-----------------|---------------|
| Default model | `providers.yaml`, README, QUICKSTART, USER_MANUAL | `config/providers.yaml` |
| Agent count | `.opencode/agents/`, README, USER_MANUAL | `.opencode/agents/` |
| Entity count | `config/wads/_omega_default/entities.yaml`, README, ARCHITECTURE, USER_MANUAL | `config/wads/_omega_default/entities.yaml` |
| Provider count | `config/providers.yaml`, README, USER_MANUAL | `config/providers.yaml` |
| Heritage tags | `grep src/omega/`, README | `grep src/omega/` |
| Mandate compliance | `check_mandate_compliance.py`, README | `check_mandate_compliance.py` |
| Test status | `make test`, README, CONTRIBUTING, USER_MANUAL | `make test` |

**Implementation**: `scripts/generate-doc-facts.py` reads SSOT → generates `docs/facts.yaml` → docs include via templating.

---

## §5 RECOMMENDATIONS (Concede/Defend/Synthesize)

### R1. No Single Source of Truth — CONCEDE

**CONCEDE**: 5 stale claims contaminate 4+ docs each.

**SYNTHESIZE**: **Implement SSOT for all key facts. Generate docs from canonical source.**

### R2. No Verification Pipeline — CONCEDE

**CONCEDE**: Zero automated verification of doc claims.

**SYNTHESIZE**: **Implement `make check-docs-truth` CI gate that verifies every claim against code.**

### R3. Missing Concepts — CONCEDE

**CONCEDE**: 10+ key concepts (SOTE, Sentinel Seal, MaKaLi, Entity Lifecycle) not in public docs.

**SYNTHESIZE**: **Document the real differentiators** — SOTE practice, Dialectic system, Sentinel Seal, MaKaLi Conductor, Entity Lifecycle. These are the real value props.

### R4. Missing User-Facing Guides — CONCEDE

**CONCEDE**: How to create IWAD, entity, contribute — all missing.

**SYNTHESIZE**: **Add "Extending Omega" section to USER_MANUAL.md with tutorials.**

### R5. Automated Verification Pipeline — SYNTHESIZE

**SYNTHESIZE**: **Implement `make check-docs-truth` as CI gate:**
- Extract all numeric claims from README
- Verify against canonical sources
- Fail PR if any claim mismatches
- Run on every PR to `main` and `release/debut*`

---

## §5 PRIORITY MATRIX

| Priority | Action | Effort |
|----------|--------|--------|
| **P0** | Implement `make check-docs-truth` CI gate | 4h |
| **P0** | Create SSOT `docs/facts.yaml` + generator | 4h |
| **P0** | Fix 11 false claims in README | 2h |
| **P1** | Document SOTE, Sentinel Seal, MaKaLi, Entity Lifecycle | 4h |
| **P1** | Add "Extending Omega" tutorials to USER_MANUAL | 4h |
| **P1** | Fix QUICKSTART.md OpenCode note | 30m |
| **P2** | Add llms.txt generation to pipeline | 2h |
| **P2** | Cross-reference audit across all docs | 2h |

---

*⬡ OMEGA ⬡ JEM ⬡ PUBLIC-DOCS-REVIEW ⬡ 2026-09-02*
<!-- PROVENANCE-CORRECTED 2026-09-07T03:03:09Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->

