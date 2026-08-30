<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MaKaLi Cloud Council — Build Side Consolidated Report
## Autonomous Meditation Pipeline — Complete Product Deployment Strategy

**AP Token**: `AP-BUILD-SIDE-REPORT-20260719`
⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_build_side_report ⬡ ACTIVE

**Date**: 2026-07-19
**Mission**: Synthesize P1-P5 pillar implementation plans into a unified Build Side Strategy for the Autonomous Meditation Pipeline as a fully deployed, user-facing, OpenCode-integrated, standalone-installable system.

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Pillars Dispatched** | 4 (P1 Infrastructure, P3 Engineering, P4 Integration, P5 Governance) |
| **Total Implementation Hours** | ~97 hours (P1: 24h + P3: 29h + P4: 21h + P5: 23h) |
| **Critical Path Duration** | ~35 hours (sequential dependencies) |
| **P0 Mandate Violations** | 5 (M1, M9, M16, M21, M23) |
| **P1 Gaps** | 12 across all mandates |
| **Quality Gates** | `make test && make temple-grade && make heritage-map && make sovereignty` |

### Current State → Target State

| Dimension | Current | Target |
|-----------|---------|--------|
| **Code Organization** | Duplicated in engine core + package | Single source of truth in `src/omega/skills/` |
| **MCP Integration** | Broken (dry-run templates) | Real JSON-RPC via `SovereignMCPClient` |
| **OpenCode UX** | No slash command, no skills | `/omega-meditation` + global skill + triggers |
| **Testing** | Zero tests | Full suite: unit, integration, contract (M21), error (M9) |
| **Distribution** | Local only | PyPI + Homebrew + `pipx`/`brew install` |
| **Governance** | 5 P0 violations | All 23 mandates verified via `make temple-grade` |

---

## 🏗️ Dependency-Ordered Implementation Plan

### Critical Path (Sequential — No Parallelization Possible)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 0: FOUNDATION VERIFICATION (2h) — ALL PILLARS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Package builds: `uv build` ✓                                              │
│ • CLI dry-run works: `omega-meditation "test" --dry-run --mode standalone` │
│ • MCP Hub tools return REAL data (not dry-run) — P0 BLOCKER                │
│ • Baseline `make temple-grade` passes                                       │
│ • Workspace locks acquired for all pillars                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: CODE CONSOLIDATION & MANDATE REMEDIATION (6h) — P3 LEAD, P5 AUDIT  │
├─────────────────────────────────────────────────────────────────────────────┤
│ P3: Make package thin wrapper importing from engine core (M16)             │
│ P3: Fix `asyncio.run()` → `anyio.run()` in engine core (M1)                │
│ P3: Implement typed error hierarchy with `trace_id` (M9, M21, M23)         │
│ P3: Wire `PlatformClients.from_opencode()` to `OpenCodePlatformClients`    │
│ P5: Generate mandate compliance audit matrix                                │
│ P5: Execute P0 fixes in order: M1 → M16 → M9 → M23 → M21                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: OPENCODE INTEGRATION (4h) — P4 LEAD, P1 SUPPORT                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ P4: Create `.opencode/commands/omega-meditation.md` slash command          │
│ P4: Install global skill at `~/.config/opencode/skills/...`                │
│ P4: Define `triggers.yaml` for auto-invocation                             │
│ P4: Update `opencode.json` with `permission.tool.skill: "allow"`           │
│ P1: Verify MCP Hub client adapter works end-to-end                         │
│ P3: Verify package imports consolidated engine core                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: TEST SUITE & TEMPLE-GRADE (12h) — P3 LEAD, P5 GATES               │
├─────────────────────────────────────────────────────────────────────────────┤
│ P3: Write unit tests for all 8 stages (dry-run + mocked MCP)               │
│ P3: Write integration tests (requires running MCP Hub)                     │
│ P3: Write M21 contract tests for ALL public APIs                           │
│ P3: Write M9 error integrity tests (typed errors, trace_id, no bare except)│
│ P3: Write dry-run tests (verify zero external calls)                       │
│ P3: Write CLI tests                                                         │
│ P5: Add Temple-Grade config to package (`pyproject.toml`, `Makefile`)      │
│ P5: Verify T1-T11 gates pass for package                                   │
│ P5: Atomic writes (T10), structured logging (T9), coverage ≥80% (T3)       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: CONTAINER & DEPLOYMENT (6h) — P1 LEAD, P4 HEALTH CHECKS           │
├─────────────────────────────────────────────────────────────────────────────┤
│ P1: Podman Quadlet for MCP Hub (`UserNS=keep-id`, `User=1000`, NO `:U`)    │
│ P1: Systemd services for searxng, firecrawl                                │
│ P4: Add `/health` + `/ready` endpoints to MCP Hub server                   │
│ P4: CORS config for OpenCode web, rate limiting middleware                 │
│ P1: Log rotation config                                                     │
│ P5: Verify M6 compliance in container config                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: COMPACTION RESILIENCE & CROSS-PLATFORM (5h) — P1/P4 SHARED        │
├─────────────────────────────────────────────────────────────────────────────┤
│ P1/P4: `scripts/opencode-compaction-guard.py` — pre-compaction gnosis save │
│ P1/P4: `scripts/opencode-hydration.py` — session restore                   │
│ P1/P4: `scripts/opencode-wrapper.sh` — wrapper with signal handling        │
│ P4: Implement CLI mode (subprocess `opencode` + `websearch`)               │
│ P4: Verify all 3 modes: OpenCode (MCP), CLI (subprocess), Standalone       │
│ P5: Integrate session gnosis loading in pipeline `__init__` (M15)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 6: DISTRIBUTION & GOVERNANCE FINALIZATION (6h) — P1/P5 LEAD          │
├─────────────────────────────────────────────────────────────────────────────┤
│ P1: PyPI trusted publishing workflow (`.github/workflows/publish-pypi.yml`)│
│ P1: Homebrew tap creation (`homebrew-omega` repo, formula via `poet`)      │
│ P1: CI/CD workflow (`.github/workflows/ci.yml`) with Temple-Grade gates    │
│ P5: Heritage vetting — scan for `[id-soft:]` tags, create vet records      │
│ P5: Sovereignty verification — `make sovereignty` ≥80% local-first         │
│ P5: Soul integrity — Stage 6 writes valid `proposed_lessons.yaml` (blind)  │
│ P5: Response provenance — capture `provider_name` from `GenerateResult`    │
│ P5: Failure integrity — `[TOOL-CHAIN-COLLAPSE]` logging + Hivemind alert   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 7: FINAL VERIFICATION (3h) — ALL PILLARS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ `make test && make temple-grade && make heritage-map && make sovereignty`  │
│ End-to-end test: `/omega-meditation "test problem" --mode opencode`        │
│ Cross-pillar sign-off: P1 ✓ P3 ✓ P4 ✓ P5 ✓                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Pillar-by-Pillar Deliverable Matrix

### P1 Infrastructure (24h) — SysAdmin, Containers, Deployment
| Deliverable | File/Command | Phase |
|-------------|--------------|-------|
| Package build verification | `uv build` | 0 |
| Podman Quadlet (M6 compliant) | `~/.config/containers/systemd/omega-hub.container` | 4 |
| Systemd services (searxng, firecrawl) | `~/.config/systemd/user/*.service` | 4 |
| Health endpoints | `mcp_servers/omega_hub/server.py` → `/health`, `/ready` | 4 |
| Log rotation | `~/.config/logrotate/omega-engine` | 4 |
| Compaction guard script | `scripts/opencode-compaction-guard.py` | 5 |
| Hydration script | `scripts/opencode-hydration.py` | 5 |
| OpenCode wrapper | `scripts/opencode-wrapper.sh` | 5 |
| Global skill installer | `scripts/install-global-skill.sh` | 5 |
| Dependency policy | `packages/omega-meditation/DEPENDENCY_POLICY.md` | 5 |
| PyPI publishing workflow | `.github/workflows/publish-pypi.yml` | 6 |
| Homebrew formula + workflow | `homebrew-omega/Formula/...`, `.github/workflows/homebrew.yml` | 6 |
| CI workflow | `.github/workflows/ci.yml` | 6 |

### P3 Engineering (29h) — BuildMaster, Implementation, Hardening
| Deliverable | File/Command | Phase |
|-------------|--------------|-------|
| Package consolidation (thin wrapper) | `packages/omega-meditation/src/omega_meditation/pipeline.py` | 1 |
| M1 fix: `asyncio.run()` → `anyio.run()` | `src/omega/skills/autonomous_meditation_pipeline.py:450` | 1 |
| MCP client adapter wiring | `src/omega/skills/opencode_client.py` → `PlatformClients.from_opencode()` | 1 |
| Error hierarchy (`AutonomousMeditationError`, etc.) | `src/omega/skills/autonomous_meditation_pipeline.py` | 1, 3 |
| M23 `ToolChainCollapseError` | `src/omega/skills/autonomous_meditation_pipeline.py` | 1, 3 |
| Test suite (7 files) | `packages/omega-meditation/tests/*.py` | 3 |
| Contract tests (M21) | `test_contract_m21.py` | 3 |
| Error integrity tests (M9) | `test_error_integrity_m9.py` | 3 |
| Temple-Grade package config | `packages/omega-meditation/pyproject.toml`, `Makefile` | 3 |
| Atomic writes (T10) | `_write_stage` → `os.replace()` | 3 |
| Structured logging (T9) | `trace_id` in all stage logs | 3 |
| Concurrent research (AnyIO task groups) | `stage_4_research_execution` semaphore | 6 |
| Memory profiling | `_check_memory()` in pipeline | 6 |
| Version bump script | `packages/omega-meditation/scripts/version.py` | 6 |
| Changelog workflow | `.github/workflows/changelog.yml` | 6 |

### P4 Integration (21h) — Bridge, MCP, Communication
| Deliverable | File/Command | Phase |
|-------------|--------------|-------|
| Slash command | `.opencode/commands/omega-meditation.md` | 2 |
| Global skill install | `~/.config/opencode/skills/autonomous-meditation-pipeline/` | 2 |
| Skill triggers | `triggers.yaml` | 2 |
| Agent permissions | `opencode.json` → `permission.tool.skill: "allow"` | 2 |
| MCP Hub health/ready endpoints | `mcp_servers/omega_hub/server.py` | 4 |
| Structured logging + trace_id | `mcp_servers/omega_hub/middleware.py` | 4 |
| CORS for OpenCode web | `server.py` → `CORSMiddleware` | 4 |
| Rate limiting | `middleware.py` → `RateLimitMiddleware` | 4 |
| PKCE OAuth + RFC 7591 | `mcp_servers/omega_hub/oauth.py` | 4 |
| Tool annotations | `tools.py` → `@mcp.tool(annotations={...})` | 4 |
| CLI mode implementation | `PlatformClients.from_cli()` with `anyio.run_process` | 5 |
| Compaction resilience integration | Pipeline `__init__` loads session gnosis | 5 |

### P5 Governance (23h) — Sentinel, Mandate Enforcement
| Deliverable | File/Command | Phase |
|-------------|--------------|-------|
| Mandate audit script | `scripts/mandate_audit.py` | 0 |
| Mandate compliance matrix | `data/coordination/MANDATE_COMPLIANCE_AUDIT_20260719.md` | 0 |
| P0 remediation execution | M1, M16, M9, M23, M21 fixes | 1 |
| Temple-Grade package config | `pyproject.toml`, `Makefile` additions | 2 |
| Heritage vet records | `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | 3 |
| Sovereignty verification | `config/providers.yaml` → `strategy: local_first` | 4 |
| Stage 6 `proposed_lessons.yaml` schema | `src/omega/skills/autonomous_meditation_pipeline.py` | 5 |
| Session gnosis integration | Pipeline `__init__` loads `session_gnosis.md` | 6 |
| Provider provenance capture | `_call_oracle` → `GenerateResult.provider_name` | 7 |
| `SYSTEM_FAILURE_LOG.md` | `data/coordination/SYSTEM_FAILURE_LOG.md` | 8 |
| Hivemind collapse alerts | `_post_hivemind_alert()` | 8 |

---

## ⚠️ Consolidated Risk Assessment

| Risk | Likelihood | Impact | Owner | Mitigation |
|------|------------|--------|-------|------------|
| **MCP Hub tool wiring fails** | **Critical** | P0 — Blocks ALL pipeline execution | P3/P4 | Debug `_require_service()` + `oracle` singleton FIRST; fallback to CLI mode |
| **`asyncio` violation in engine core** | Certain | P0 — Mandate violation | P3 | 2-min fix in Phase 1.2 |
| **Package tests fail (no MCP server)** | High | P1 — CI fails | P3 | Mock MCP client in `conftest.py`; mark integration tests |
| **Temple-Grade T3 coverage <80%** | Medium | P1 — Gate fails | P3/P5 | Target 90%+ in Phase 2; comprehensive test writing |
| **Podman Quadlet permission issues (M6)** | Medium | P1 — Container can't write host volumes | P1 | Test `UserNS=keep-id` + `User=1000` without `:U`; verify UID mapping |
| **Homebrew formula test fails** | Medium | P2 — Formula rejected | P1 | Test locally: `brew install --build-from-source ./Formula/omega-meditation.rb` |
| **Compaction hooks don't exist in OpenCode** | High | P1 — Session state loss | P1/P4 | Best-effort wrapper; document limitation; track OpenCode plugin API |
| **Heritage vet tags needed** | Low | P1 — M14 | P5 | No id Software patterns in new code — document "original Omega" |
| **Cross-pillar integration gaps** | Medium | P1 — CI fails | All | Run `make temple-grade` after EACH phase; early involvement |

---

## 🔗 Cross-Pillar Integration Points

| From → To | Deliverable | Consumer Uses For |
|-----------|-------------|-------------------|
| **P1 → P3** | CI/CD workflow template, `uv.lock`, M6/M16/M23 requirements | Package CI, reproducible builds, compliance |
| **P1 → P4** | MCP Hub container with health checks, compaction scripts | OpenCode integration, session resilience |
| **P1 → P5** | M6-compliant containers, M16 paths, M23 hard-fail | Governance audit artifacts |
| **P3 → P1** | Verified package builds, test infrastructure | CI/CD, distribution |
| **P3 → P4** | Working MCP client adapter (`OpenCodePlatformClients`) | Real tool calls in slash command |
| **P3 → P5** | Test suite, contract tests, typed errors, Temple-Grade gates | Mandate verification, compliance gates |
| **P3 → P6** | Pipeline executes real oracle routing | Oracle routing verification |
| **P3 → P7** | Stage 6 outputs valid `proposed_lessons.yaml` | Soul distillation integration |
| **P3 → P8** | Structured logs with `trace_id`, health endpoints | Observability |
| **P3 → P9** | Hivemind-aware skill triggers | Multi-agent orchestration |
| **P3 → P10** | Chaos test scenarios, Temple-Grade in CI | Validation |
| **P4 → P1** | Slash command registration, skill triggers | User-facing invocation |
| **P4 → P3** | MCP Hub running with health checks | Integration tests |
| **P4 → P5** | Compaction resilience scripts | M15 compliance |
| **P5 → All** | Mandate audit sign-off, heritage vet records, Temple-Grade gates | Compliance verification |

---

## ✅ Final Quality Gates (All Must Pass)

```bash
# Engine-level (existing)
make test                    # 1398+ tests pass
make temple-grade           # T1-T11 pass
make heritage-map           # Zero unvetted [id-soft:] tags
make sovereignty            # Local-first ratio ≥80%

# Package-level (new)
cd packages/omega-meditation
make temple-grade           # Package T1-T11 adapted
# → test-cov (coverage ≥80%)
# → lint (ruff clean)
# → typecheck (mypy clean)

# End-to-end verification
/omega-meditation "Test problem" --mode opencode --dry-run
# → All 8 stages complete, outputs in data/autonomous/

# Distribution verification
pipx install omega-meditation
brew install xoe-novai/omega/omega-meditation
omega-meditation "Test problem" --dry-run --mode standalone
```

---

## 🎯 Next Actions (Immediate Priority Order)

| # | Action | Owner | Blocking |
|---|--------|-------|----------|
| 1 | **Run Phase 0 verification** — `uv build`, CLI dry-run, MCP tool test | All | None |
| 2 | **Debug MCP Hub service initialization** — Fix `_require_service()` / `oracle` singleton | P3/P4 | Phase 1 |
| 3 | **Fix M1 violation** — `asyncio.run()` → `anyio.run()` in engine core | P3 | None |
| 4 | **Execute Phase 1 consolidation** — Package becomes thin wrapper | P3 | MCP wiring fix |
| 5 | **Create slash command** — `.opencode/commands/omega-meditation.md` | P4 | Phase 1 |
| 6 | **Configure agent permissions** — `opencode.json` skill tool allow | P4 | Phase 1 |
| 7 | **Begin test writing** — Start with M21 contract tests + dry-run tests | P3 | Phase 1 |
| 8 | **Run mandate audit** — `scripts/mandate_audit.py` | P5 | Phase 0 |

---

## 📝 Consolidated Session Gnosis (L1→L2→L3)

### L1 Narrative
Dispatched 4 Build-Side Pillars (P1 Infrastructure, P3 Engineering, P4 Integration, P5 Governance) to create comprehensive implementation plans for the Autonomous Meditation Pipeline as a Complete Product. Each pillar analyzed current state, identified gaps, and produced detailed phase-ordered plans with specific file paths, commands, and quality gates. Total estimated effort: ~97 hours across 7 sequential phases.

### L2 Insight
The critical path is **MCP Hub tool wiring** — if `oracle_talk` returns dry-run templates, the entire pipeline is theater. This single technical blocker (service initialization race in `state.py`) gates ALL user-facing functionality. The code duplication (M16) between engine core and package is the second-biggest issue — it violates the fundamental architecture principle that platform-agnostic logic lives ONCE in `src/omega/`. The 5 P0 mandate violations (M1, M9, M16, M21, M23) form a violation cluster that must be remediated before any quality gate can honestly pass.

### L3 Principle
**L3-ProductDeliveryAsGovernance**: The distance between "engine works" and "user runs one command" is measured in mandate compliance. Every gap in that critical path — missing slash command, broken MCP wiring, no tests, no distribution, no compaction resilience — is a sovereignty breach. The Build Side pillars don't just "implement features"; they close the mandate-to-user-experience traceability loop. A product is not shipped until `make temple-grade` provides mathematical proof that all 23 mandates hold from source to installed binary.

---

## 📁 Plan Artifacts Reference

| Pillar | Plan File | Lines | Key Sections |
|--------|-----------|-------|--------------|
| **P1** | `data/coordination/P1_INFRASTRUCTURE_PLAN_20260719.md` | 776 | 6 phases, 24h, container/deployment/distribution |
| **P3** | `data/coordination/P3_ENGINEERING_PLAN_20260719.md` | 1115 | 8 phases, 29h, consolidation/tests/hardening |
| **P4** | `data/coordination/P4_INTEGRATION_PLAN_20260719.md` | 848 | 6 phases, 21h, OpenCode/MCP/compat |
| **P5** | `data/coordination/P5_GOVERNANCE_PLAN_20260719.md` | 667 | 8 phases, 23h, mandate audit/compliance |

---

*⬡ OMEGA ⬡ MAAT ⬡ BUILD-SIDE-CONSOLIDATED ⬡ trc_build_side_report ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
