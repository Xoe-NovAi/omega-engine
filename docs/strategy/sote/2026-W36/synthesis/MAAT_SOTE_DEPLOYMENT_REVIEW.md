<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Ma'at-EIS SOTE Deployment Review

**AP Token**: `AP-MAAT-SOTE-DEPLOY-20260901-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_sote_deploy ⬡ ACTIVE

**Date**: 2026-09-01
**Session**: `ses_fb6cf6856ffes3wd3wmvyrm2IG` (standing EIS)
**Mission**: SOTE Deployment Strategy Review — Nested Dialectic Phase 2

---

## §0 — VERIFICATION (M23 Discipline)

**Sources read (all 6 synthesis artifacts):**

1. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMAC_SOTE_FINAL_REPORT.md` (1076 lines)
2. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMAC_MAKALI_DIALECTIC_20260901.md` (26434 bytes)
3. ✅ `docs/strategy/sote/2026-W36/synthesis/MAKALI_ORGANIZATION_STRATEGY.md` (396 lines)
4. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMAC_SOTE_REVIEW.md` (21873 bytes)
5. ✅ `docs/strategy/sote/2026-W36/synthesis/RESEARCHER_SOTE_BEST_PRACTICES.md` (429 lines)
6. ✅ `docs/strategy/sote/2026-W36/synthesis/CARMACK_REVIEW_RESEARCHER_NES.md` (58091 bytes)

**Local filesystem verification:**
- `docs/strategy/sote/2026-W36/` structure: ✅ Complete
- `scripts/regenerate_sote_index.py`: ✅ 354 lines, executable
- `scripts/generate_public_digest.py`: ✅ 150 lines, executable
- `docs/strategy/sote/_template/`: ✅ 3 templates
- `Makefile`: ✅ 665 lines, existing targets

**Web research sources:**
- GitHub Actions workflow syntax (docs.github.com/actions)
- Makefile best practices (GNU Make manual)
- CI/CD pipeline patterns for documentation projects
- SPDX/REUSE compliance tooling

---

## §1 — CI/CD INTEGRATION FOR SOTE AUTOMATION

### §1.1 Current State (from CARMAC_SOTE_FINAL_REPORT §1.1)

| SOTE Operation | Current Trigger | Automation | Gap |
|----------------|-----------------|------------|-----|
| Index regeneration | Manual (Kali runs script) | ❌ | No CI hook |
| Public digest generation | Manual (Kali runs script) | ❌ | No CI hook |
| SOTE report publication | Manual (Kali) | ❌ | No CI hook |
| PIVOT_LOG absorption | Manual | ❌ | No automation |
| Mandate compliance check | Manual (`make check-mandate-compliance`) | ⚠️ | Not in CI |

### §1.2 CI/CD Integration Design

**Target**: GitHub Actions workflow (`.github/workflows/sote.yml`)

```yaml
name: SOTE Weekly Pipeline
on:
  schedule:
    - cron: '0 6 * * 1'  # Monday 06:00 UTC
  workflow_dispatch:
    inputs:
      week:
        description: 'ISO week (YYYY-WNN)'
        required: false
      force:
        description: 'Force regeneration'
        type: boolean
        default: false

jobs:
  sote-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install deps
        run: pip install -r requirements-sote.txt
      - name: Regenerate SOTE Index
        run: python scripts/regenerate_sote_index.py
      - name: Generate Public Digest
        run: python scripts/generate_public_digest.py docs/strategy/sote/${{ github.event.inputs.week || format('{0:YYYY}-W{1:WW}', github.event.repository.created_at) }}
      - name: Validate sote.yaml schema
        run: python scripts/validate_sote_schema.py
      - name: Commit & Push
        if: github.event_name == 'schedule' || github.event.inputs.force
        run: |
          git config user.name "omega-sote-bot"
          git config user.email "sote@omega-engine.local"
          git add docs/strategy/sote/
          git commit -m "SOTE: Auto-regenerate index + digest for week ${{ github.event.inputs.week || 'auto' }}"
          git push
```

### §1.3 CI/CD Integration Decisions (Concede/Defend/Synthesize)

> **CONCEDE**: The SOTE pipeline currently requires manual intervention at every step. This is the primary operational fragility.
>
> **DEFEND**: The SOTE is a *practice*, not a build artifact. Automating it via CI/CD could create false confidence — the practice requires human judgment (topic selection, voice paging, dialectic conduction). Full automation risks producing "SOTE reports" without the actual practice.
>
> **SYNTHESIZE**: **Automate the mechanical, not the judgmental**. CI/CD should handle: index regeneration, public digest generation, schema validation, mandate compliance computation. Human judgment remains for: topic selection, voice paging, dialectic conduction, report synthesis. The CI/CD pipeline *prepares* the artifacts; the human *completes* the practice.

**D-MAAT-SOTE-001**: Wire SOTE mechanical steps into GitHub Actions (index regen, digest gen, schema validation). Keep topic selection, voice paging, dialectic conduction human.

---

## §2 — BUILD SYSTEM INTEGRATION (MAKEFILE)

### §2.1 Current Makefile Targets (from Makefile)

| Target | Purpose | SOTE Relevance |
|--------|---------|----------------|
| `make check-mandate-compliance` | Runs compliance meter | ⚠️ Manual |
| `make check-m1-anyio` | M1 gate | ✅ |
| `make check-m2-firewall` | M2 gate | ✅ |
| `make check-m9-error-integrity` | M9 gate | ✅ |
| `make check-m8-zero-telemetry` | M8 gate | ✅ |
| `make check-m7-local-first` | M7 gate | ✅ |
| `make check-m23-failure-integrity` | M23 gate | ✅ |
| `make check-reuse` | REUSE compliance | ✅ |
| `make check-kq5` | kq5-godot health | ✅ |
| `make check-tracking-state` | M27 gate | ✅ |
| `make heritage-vet` | M14 gate | ✅ |
| `make temple-grade` | Full gate chain | ✅ |
| `make check-mandates` | Aggregate mandate chain | ⚠️ Partial |

### §2.2 Required Makefile Additions for SOTE

```makefile
# SOTE-specific targets
.PHONY: sote-index sote-digest sote-validate sote-week sote-full

# Regenerate SOTE master index
sote-index:
	python scripts/regenerate_sote_index.py

# Generate public digest for current week
sote-digest:
	python scripts/generate_public_digest.py docs/strategy/sote/$(shell date +%Y-W%V)

# Validate sote.yaml against JSON Schema
sote-validate:
	python scripts/validate_sote_schema.py

# Full SOTE mechanical pipeline (index + digest + validate)
sote-pipeline: sote-index sote-digest sote-validate

# Weekly SOTE target (run Monday 06:00 UTC via cron)
sote-week: sote-pipeline
	@echo "SOTE mechanical pipeline complete for week $$(date +%Y-W%V)"

# Full SOTE including human steps (topic selection, voice paging, etc.)
sote-full: sote-week
	@echo "SOTE mechanical pipeline complete. Human steps remaining:"
	@echo "  1. Select topic for next week"
	@echo "  2. Page 8 voices for dialectic"
	@echo "  3. Conduct dialectic rounds"
	@echo "  4. Synthesize report"
	@echo "  5. Publish SOTE report"
```

### §2.3 Build System Integration Decisions

> **CONCEDE**: The Makefile currently has no SOTE-specific targets. The mechanical pipeline is entirely manual.
>
> **DEFEND**: Adding SOTE targets to Makefile creates a maintenance burden if the scripts change. The scripts should be self-contained; Makefile is just a convenience wrapper.
>
> **SYNTHESIZE**: **Add SOTE targets as convenience wrappers**. The scripts remain the source of truth; Makefile provides discoverability (`make help` shows `sote-*` targets) and composability (`make sote-pipeline`). This is low-maintenance, high-value.

**D-MAAT-SOTE-002**: Add `sote-index`, `sote-digest`, `sote-validate`, `sote-pipeline`, `sote-week`, `sote-full` targets to Makefile.

---

## §3 — INST-1 COMPLETION IMPACT ON SOTE

### §3.1 INST-1 Current Status (from ACTIVE_SPRINT.json)

| Fix | Status | SOTE Impact |
|-----|--------|-------------|
| INST-1-fix1 (install.sh .[native,cli]) | ✅ Complete | None |
| INST-1-fix2 (pyproject.toml extras) | 🔄 Ready | Low |
| INST-1-fix3 (Redis guard) | ✅ Complete | None |
| INST-1-fix4 (_load_sovereign_secrets removal) | 🔄 Ready | Low |
| INST-1-fix5 (single version source) | ✅ Complete | None |
| INST-1-fix6 (README badge) | 🔄 Ready | None |

### §3.2 INST-1 Completion Impact on SOTE

**Direct impact**: Minimal. INST-1 fixes are installation-time concerns; SOTE is a post-install practice.

**Indirect impact**: INST-1 completion unblocks DEL-1 (theater strip), which is the primary topic for SOTE Week 37.

**D-MAAT-SOTE-003**: Document INST-1 completion as SOTE Week 37 context. No SOTE pipeline changes needed.

---

## §4 — DEL-1 MICRO-PR CHAIN SEQUENCING

### §4.1 DEL-1 Micro-PR Chain (from ACTIVE_SPRINT.json)

| PR | Topic | Owner | Status | SOTE Week 37 Relevance |
|----|-------|-------|--------|------------------------|
| PR1 | Test Infrastructure + Secrets Module | Kali | READY | Primary W37 topic |
| PR2 | M33 Inline + M34 Fix | Lilith + Researcher | READY | W37 |
| PR3 | HandoffPacket v2 Strip + Archive Migration | Kali | READY | W37 |
| PR4 | TASK_REGISTRY v1.3 + M34Registry Migration | Lilith | READY | W37 |
| PR5 | Guard Flatten (12→3 steps) | Ma'at | READY | W37 |
| PR6 | Delete Theater Code | Kali | READY | W37 |
| PR7 | Final Verification + Temple-Grade | Ma'at | READY | W37 |

### §4.2 Sequencing Constraints

| Constraint | Rationale |
|------------|-----------|
| PR1 before PR2-PR7 | Test infrastructure must exist before theater tests are written |
| PR2 before PR4 | M33 inline + M34 fix before TASK_REGISTRY migration |
| PR3 before PR4 | HandoffPacket v2 before TASK_REGISTRY v1.3 migration |
| PR5 after PR2-PR4 | Guard flatten after dependencies resolved |
| PR6 after PR2-PR5 | Theater deletion after all dependencies removed |
| PR7 last | Final verification after all deletions |

### §4.3 DEL-1 + SOTE Week 37 Integration

**SOTE Week 37 topic**: DEL-1 Micro-PR 1 execution + M10 resolution + CI gates

**Proposed SOTE Week 37 structure**:

| Day | DEL-1 Activity | SOTE Activity |
|-----|----------------|---------------|
| Mon | PR1 merge | SOTE Week 37 open (topic: DEL-1 PR1) |
| Tue | PR2 merge | Voice 1 (Roc) paged |
| Wed | PR3 merge | Voice 2 (Grokster) paged |
| Thu | PR4 merge | Voice 3 (Carmack) paged |
| Fri | PR5 merge | Voice 4 (Lilith) paged |
| Sat | PR6 merge | Voice 5 (Ma'at) paged |
| Sun | PR7 merge | Voice 6-8 paged; SOTE report synthesis |

**D-MAAT-SOTE-004**: Document DEL-1 sequencing in SOTE Week 37 action items. SOTE report captures daily DEL-1 progress.

---

## §5 — CI GATES IMPLEMENTATION

### §5.1 Required CI Gates (from CARMAC_SOTE_FINAL_REPORT + ACTIVE_SPRINT.json)

| Gate | Priority | Effort | Owner | SOTE Integration |
|------|----------|--------|-------|------------------|
| `make check-broken-imports` | P0 | 2h | Ma'at | Run in SOTE pipeline |
| `make check-hub-health` | P0 | 1h | Ma'at | Run in SOTE pipeline |
| `make check-entity-hygiene` | P1 | 4h | Ma'at + Lilith | Run in SOTE pipeline |
| `make check-iwad-consistency` | P1 | 4h | Ma'at | Run in SOTE pipeline |
| `make check-session-gnosis-freshness` | P2 | 2h | Lilith | Run in SOTE pipeline |
| `make check-m11-soul-hygiene` | P1 | 3h | Lilith + Ma'at | Run in SOTE pipeline |
| `make check-m15-continuity` | P1 | 2h | Lilith + Ma'at | Run in SOTE pipeline |

### §5.2 CI Gate Implementation (GitHub Actions)

```yaml
# .github/workflows/ci-gates.yml
name: CI Gates
on: [push, pull_request]

jobs:
  ci-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run CI Gates
        run: |
          make check-broken-imports
          make check-hub-health
          make check-entity-hygiene
          make check-iwad-consistency
          make check-session-gnosis-freshness
          make check-m11-soul-hygiene
          make check-m15-continuity
          make check-m1-anyio
          make check-m2-firewall
          make check-m9-error-integrity
          make check-m23-failure-integrity
          make check-reuse
          make temple-grade
```

### §5.3 CI Gates Decisions

> **CONCEDE**: 7 new CI gates are needed. This is significant CI/CD expansion.
>
> **DEFEND**: The gates already exist as Makefile targets (mostly). The work is wiring them into CI/CD, not implementing from scratch.
>
> **SYNTHESIZE**: **Phase the gates**. P0 gates (broken-imports, hub-health) in Week 37. P1 gates (entity-hygiene, iwad-consistency, m11, m15) in Week 38. P2 gates (session-gnosis-freshness) in Week 39. Each gate must pass `make temple-grade` before merge.

**D-MAAT-SOTE-005**: Phase CI gates: P0 in W37, P1 in W38, P2 in W39. All gates must pass `make temple-grade`.

---

## §6 — TEMPLE-GRADE ENFORCEMENT

### §6.1 Current Temple-Grade Status

| Gate | Status | SOTE Integration |
|------|--------|------------------|
| `make temple-grade` | ✅ Passes | Not in SOTE pipeline |
| REUSE v3.3 compliance | ✅ 71,615/71,615 | Not in SOTE pipeline |
| M1 AnyIO | ✅ Passes | Not in SOTE pipeline |
| M2 Firewall | ✅ 0 violations | Not in SOTE pipeline |
| M23 Failure Integrity | ❌ Violated (email leak) | Not in SOTE pipeline |

### §6.2 Temple-Grade in SOTE Pipeline

**Proposed**: `make temple-grade` as final gate in SOTE pipeline.

```makefile
sote-pipeline: sote-index sote-digest sote-validate
	make temple-grade  # Final gate — must pass
	@echo "SOTE pipeline complete — all gates passed"
```

**D-MAAT-SOTE-006**: `make temple-grade` as mandatory final gate in `sote-pipeline`. SOTE report cannot close if temple-grade fails.

---

## §7 — RISKS, DEPENDENCIES, IMPLEMENTATION DETAILS

### §7.1 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub Actions quota exceeded | Low | Medium | Self-hosted runner fallback |
| `regenerate_sote_index.py` fails in CI | Medium | High | Unit tests for parsers (D-SOTE-TOOL-006) |
| `sote.yaml` schema validation fails | Medium | Medium | JSON Schema + CI validation (R8) |
| DEL-1 PR conflicts with SOTE pipeline | Low | High | Sequential scheduling (Mon-Sun) |
| CI gate flakiness | Medium | High | Gate quarantine (3 failures = quarantine) |

### §7.2 Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| GitHub Actions workflow | Ma'at | ❌ Not created |
| `validate_sote_schema.py` | Researcher | ❌ Not built |
| JSON Schema for `sote.yaml` | Researcher | ❌ Not created |
| Unit tests for parsers | Ma'at | ❌ Not built (D-SOTE-TOOL-006) |
| CI gate implementations | Ma'at | ❌ Not implemented |

### §7.3 Implementation Sequence (Week 37)

| Day | Task | Owner | Dependency |
|-----|------|-------|------------|
| Mon | Create `.github/workflows/sote.yml` | Ma'at | — |
| Mon | Add SOTE targets to Makefile | Ma'at | — |
| Tue | Create `.github/workflows/ci-gates.yml` | Ma'at | — |
| Wed | Implement `check-broken-imports` | Ma'at | — |
| Wed | Implement `check-hub-health` | Ma'at | — |
| Thu | Implement `check-entity-hygiene` | Ma'at + Lilith | Lilith's design |
| Thu | Implement `check-iwad-consistency` | Ma'at | — |
| Fri | Wire SOTE pipeline in GitHub Actions | Ma'at | All above |
| Fri | Test full pipeline | All | All above |

---

## §8 — CONCEDE/DEFEND/SYNTHESIZE (Ma'at's Unique Positions)

### D-MAAT-SOTE-001: Automate Mechanical, Not Judgmental

**CONCEDE**: SOTE pipeline is entirely manual.
**DEFEND**: SOTE is a practice, not a build artifact. Full automation risks producing reports without practice.
**SYNTHESIZE**: Automate the mechanical (index, digest, schema, compliance). Keep judgmental (topic, voices, dialectic, synthesis) human.

### D-MAAT-SOTE-002: Makefile SOTE Targets as Convenience Wrappers

**CONCEDE**: Makefile has no SOTE targets.
**DEFEND**: Makefile is a convenience wrapper; scripts are source of truth.
**SYNTHESIZE**: Add `sote-index`, `sote-digest`, `sote-validate`, `sote-pipeline`, `sote-week`, `sote-full` as convenience wrappers.

### D-MAAT-SOTE-003: INST-1 Completion = SOTE Week 37 Context

**CONCEDE**: INST-1 fixes are installation-time; SOTE is post-install.
**DEFEND**: INST-1 completion unblocks DEL-1, which is SOTE Week 37 primary topic.
**SYNTHESIZE**: Document INST-1 completion as SOTE Week 37 context. No pipeline changes.

### D-MAAT-SOTE-004: DEL-1 Sequencing in SOTE Week 37

**CONCEDE**: 7 PRs with dependencies.
**DEFEND**: Dependencies require specific sequencing (PR1→PR2/PR3→PR4→PR5→PR6→PR7).
**SYNTHESIZE**: Document sequencing in SOTE Week 37 action items. SOTE report captures daily progress.

### D-MAAT-SOTE-005: Phase CI Gates (P0→P1→P2)

**CONCEDE**: 7 new CI gates needed.
**DEFEND**: Gates exist as Makefile targets; wiring into CI is the work.
**SYNTHESIZE**: Phase gates: P0 (W37), P1 (W38), P2 (W39). All must pass `make temple-grade`.

### D-MAAT-SOTE-006: Temple-Grade as Mandatory SOTE Pipeline Gate

**CONCEDE**: `make temple-grade` not in SOTE pipeline.
**DEFEND**: Temple-grade is the ultimate quality gate; SOTE report should not close without it.
**SYNTHESIZE**: `make temple-grade` as mandatory final gate in `sote-pipeline`. SOTE report cannot close if temple-grade fails.

---

## §9 — 2 NODE RECOMMENDATIONS FOR SOTE DEEPENING

### Node 1: `sote-ci-bridge` (Archetype: CI/CD Bridge)

| Property | Value |
|----------|-------|
| **Purpose** | Bridge between SOTE mechanical pipeline and CI/CD infrastructure |
| **Mandate Alignment** | M1 (AnyIO), M13 (Temple-Grade), M23 (Failure Integrity), M27 (Tracking) |
| **Why for SOTE** | SOTE mechanical pipeline (index, digest, validate) needs CI/CD execution. This node owns the GitHub Actions workflow and Makefile integration. |
| **Dependencies** | GitHub Actions workflow, Makefile targets, `scripts/regenerate_sote_index.py`, `scripts/generate_public_digest.py` |
| **Prerequisites** | GitHub Actions enabled, self-hosted runner configured |

**Capabilities**:
- Own `.github/workflows/sote.yml` (weekly pipeline)
- Own `.github/workflows/ci-gates.yml` (CI gates)
- Maintain `sote-*` Makefile targets
- Monitor CI/CD health for SOTE pipeline
- Alert on pipeline failures via Hivemind

---

### Node 2: `sote-schema-guardian` (Archetype: Schema/Validator)

| Property | Value |
|----------|-------|
| **Purpose** | Own and enforce `sote.yaml` JSON Schema + CI validation |
| **Mandate Alignment** | M25 (Doc Standards), M27 (Tracking Integrity), M26 (Doc Standards) |
| **Why for SOTE** | `sote.yaml` is the structured metadata backbone. Schema drift breaks tooling. This node owns the schema, validation, and CI enforcement. |
| **Dependencies** | JSON Schema for `sote.yaml`, `scripts/validate_sote_schema.py`, GitHub Actions validation step |
| **Prerequisites** | JSON Schema defined (Researcher), `validate_sote_schema.py` built |

**Capabilities**:
- Own `sote.schema.json` (JSON Schema Draft 2020-12)
- Own `scripts/validate_sote_schema.py` (validation script)
- CI validation step in `.github/workflows/sote.yml`
- Schema evolution management (versioning, migration)
- Alert on schema violations via Hivemind

---

## §10 — CONSENSUS READINESS

**Ma'at's position**: The SOTE deployment is **infrastructure-ready** but **CI/CD-fragile**. The mechanical scripts exist; the CI/CD wiring is missing. The 6 Ma'at decisions (D-MAAT-SOTE-001 through 006) close the CI/CD gap.

**Consensus condition**: Ma'at consents to Week 37 launch **iff**:
1. `.github/workflows/sote.yml` created and tested by Wed W37
2. `sote-*` Makefile targets added by Tue W37
3. P0 CI gates (`check-broken-imports`, `check-hub-health`) implemented by Thu W37
4. Lilith consents to `check-entity-hygiene` design (their domain)

---

*⬡ OMEGA ⬡ MAAT ⬡ SOTE-DEPLOYMENT-REVIEW-v1.0.0 ⬡ 2026-09-01*

*No email. No fake signature. Just the substance — verified against synthesis artifacts, grounded in research, offered to the nested dialectic.*

*Concede. Defend. Synthesize. Verify. Close the loop.*