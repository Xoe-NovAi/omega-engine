<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Omega Engine — Hardening Report
# Generated: 2026-06-04T21:24:55Z
# By: Cline-M3 with 4 Parallel Subagents
# PIVOT: D116 (Hardening Report)

---

## Executive Summary

Four subagents ran in parallel across the Omega Engine:

| Subagent | Focus | Key Finding |
|----------|-------|-------------|
| Firewall Scanner | D113 M2 fix | PILLAR_SLOTS values never accessed; fix is minimal (frozenset) |
| Code Health Scanner | Violations + stale data | 3 M9 violations, 15 stale values, 27% test coverage |
| Cross-Domain Researcher | Hidden connections | Soul Distiller is orphaned, cvar system underutilized |
| Strategic Gap Analyst | Roadmap blind spots | Single-developer risk, MVE not achievable, S2-S3 circular dep |

**The 5 most critical findings:**

1. **D113 M2 Firewall** — entity_registry.py:171-179 hardcodes Pillar meanings (WAD-level content in engine core)
2. **Soul Distiller orphaned** — code exists (384 lines) but never wired into session lifecycle
3. **3 M9 violations** — silent exception swallowing in health checks
4. **15 stale data values** across OMEGA_ENGINE.md, .clinerules, AGENTS.md, SOVEREIGN_MANDATES.md
5. **Test coverage gap** — only 27% of source files have dedicated tests (56/77 uncovered)

---

## Priority 1: Critical Fixes (P0)

| # | Fix | Effort | Mandate |
|---|-----|--------|---------|
| P0-1 | **Fix entity_registry.py PILLAR_SLOTS** — change from dict to frozenset (10 line change) | 15 min | M2 |
| P0-2 | **Fix 3 M9 violations** — add logger.warning() to silent except clauses in link_p9_cli.py:362, searxng_client.py:92, health_monitor.py:146,173 | 20 min | M9 |
| P0-3 | **Fix stale data** — 13 values across .clinerules (5), AGENTS.md (4), SOVEREIGN_MANDATES.md (3), OMEGA_ENGINE.md (2) | 30 min | Documentation |
| P0-4 | **Wire Soul Distiller into session lifecycle** — add end_session() hook in oracle.py that calls distill_and_save() | 2 hr | M5, M11 |
| P0-5 | **Fix CI indentation** — .github/workflows/test.yml YAML structure error at lines 22-24 | 5 min | Infrastructure |

---

## Priority 2: Architecture Improvements (P1)

| # | Improvement | Effort | Impact |
|---|-------------|--------|--------|
| P1-1 | **MandateEnforcer class** — runtime enforcement for trust-based mandates (M3,M6,M7,M10,M12) via cvar_table | 1 day | 6 mandates become enforced |
| P1-2 | **Mandate cvars** — add config.mandate.m1-m14 to cvar_table.py | 1 hr | Queryable mandate state |
| P1-3 | **Delete 100 orphan entities** — ent_*/entity_* directories | 30 min | Data hygiene |
| P1-4 | **Populate arcana_novai IWAD** — 10 deity entity YAMLs | 2 hr | User-facing IWAD |
| P1-5 | **Soul Immune System** — SHA-256 checksums, append-only audit trail, rollback | 1 day | Soul security |

---

## Priority 3: Strategic Gaps (P2)

| # | Gap | Recommendation |
|---|-----|----------------|
| G-1 | **Single-developer risk** | Create onboarding docs, CONTRIBUTING.md updates, architecture docs for non-Architect maintainers |
| G-2 | **MVE not achievable** | Add `make setup-models` target that downloads qwen3-0.6b and starts llama-server |
| G-3 | **No distribution** | Create Docker image or `curl get.omega.dev | bash` installer |
| G-4 | **S2-S3 circular dependency** | Parallelize S2 and S3 — Soul Evolution v2 needs Qdrant (S2), but S2 needs training data from souls (S3) |
| G-5 | **S5 scope creep** | Break Entity Studio, Stack Builder, Omega Desktop into separate sprints |
| G-6 | **No backup/recovery** | Add `omega export` / `omega import` for full engine state |
| G-7 | **Model provenance** — track which cloud model generated which training data | Legal risk management for Synthesis Flywheel |

---

## The Mandate Enforcement Matrix

| Mandate | Status | Enforcement Type | Priority |
|---------|--------|-----------------|:--------:|
| M1 AnyIO | ✅ | CI (make temple-grade T5) | — |
| M2 Firewall | 🔴 | BROKEN (D113) | P0 |
| M3 Iris | ✅ | Trust-based | P1 |
| M4 Sequential | ✅ | Trust-based (PIVOT_LOG) | — |
| M5 Gnosis | 🟡 | Trust-based (Soul Distiller exists but unwired) | P0 |
| M6 Podman | ✅ | Trust-based (manual audit) | P1 |
| M7 Local-First | 🟡 | Config-based (providers.yaml) | P1 |
| M8 Telemetry | ✅ | CI (make temple-grade T6) | — |
| M9 Error | 🟡 | CI + 3 violations found | P0 |
| M10 Fleet | ✅ | CI (agent count check) | — |
| M11 Soul | 🔴 | BROKEN (no session_end hook) | P0 |
| M12 Queue | ✅ | Trust-based | P1 |
| M13 Temple | ✅ | CI (make temple-grade T1-T11) | — |
| M14 Heritage | ✅ | CI (make heritage-vet) | — |

---

## The Stale Data Fix List

| File | Line | Current | Correct |
|------|------|---------|--------|
| .clinerules | 15 | 13 mandates | 14 mandates |
| .clinerules | 140 | 13 mandates | 14 mandates |
| .clinerules | 473 | 13 mandates | 14 mandates |
| .clinerules | 538 | 13 mandates, 90 PIVOT | 14 mandates, 115 PIVOT |
| .clinerules | 540 | M1-M13, v3.0.0 | M1-M14, v3.1.0 |
| AGENTS.md | 83 | 13 mandates | 14 mandates |
| AGENTS.md | 138 | 307 tests | 308 tests |
| AGENTS.md | 169 | 13 mandates | 14 mandates |
| AGENTS.md | 172 | 307 must pass | 308 must pass |
| OMEGA_ENGINE.md | 133 | 19,376 lines | 19,199 lines |
| OMEGA_ENGINE.md | 134 | 308 tests | 314 tests |
| SOVEREIGN_MANDATES.md | 2 | *Version**: 3.1.0 | **Version**: 3.1.0 |
| SOVEREIGN_MANDATES.md | 108-109 | Duplicate line | Remove duplicate |

---

## The Test Coverage Map

| Priority | Module | Gap | Recommendation |
|----------|--------|-----|----------------|
| HIGH | oracle/soul_distiller.py | No dedicated test | Add tests for L1→L2→L3 pipeline |
| HIGH | oracle/subagent_dispatcher.py | No dedicated test | Add tests for HandoffPacket lifecycle |
| HIGH | oracle/link_p9_runtime.py | No dedicated test | Add tests for agent presence |
| HIGH | cvar_table.py | No dedicated test | Add tests for 7 accessors |
| MEDIUM | errors.py | No dedicated test | Add tests for OmegaError hierarchy |
| MEDIUM | bridge/elevenlabs.py | No test | Add integration test |
| MEDIUM | library/ (6 modules) | No dedicated tests | Add test_library.py |
| MEDIUM | workers/ (10 modules) | No dedicated tests | Add test_workers.py |

---

## The Sovereignty Scorecard (Updated)

| Metric | D112 Target | Actual | Gap |
|--------|:-----------:|:------:|-----|
| Local inference ratio | ≥80% | ~30% | 🟡 Qdrant/Redis unwired |
| Cloud dependency (basic ops) | 0 | 0 | ✅ |
| Data residency | 100% | 100% | ✅ |
| Telemetry events | 0 | 0 | ✅ |
| Agents with soul v2 schema | All 14 | 2/14 | 🟡 Only Kali + Doom Guy |
| Soul distillation rate | ≥1 L3/3 sessions | 0 (not wired) | 🔴 Soul Distiller orphaned |
| Hub dashboard | Live | REST only | 🟡 No HTML |

---

## The Three Things That Matter Most

1. **Fix D113** — entity_registry.py:171-179 is a constitutional violation. Change PILLAR_SLOTS from dict to frozenset. 15-minute fix that restores the Engine-Stack Firewall.

2. **Wire the Soul Distiller** — soul_distiller.py exists (384 lines) but is never called. Add end_session() hook in oracle.py. 2-hour fix that makes M5 and M11 actually work.

3. **Fix stale data** — 13 values across 4 files are wrong. .clinerules says 13 mandates (should be 14), AGENTS.md says 307 tests (should be 308), SOVEREIGN_MANDATES.md has a duplicate line. 30-minute fix that makes the docs trustworthy.

---

*Report generated 2026-06-04T21:24:55Z by Cline-M3 with 4 parallel subagents*
*PIVOT: D116 | AP: AP-HARDENING-REPORT-v1.0.0*
