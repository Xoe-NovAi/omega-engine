# ⬡ SOVEREIGN DEBT SYNTHESIS — Full Remediation Queue
# Date: 2026-06-09 | Author: Antigravity IDE | Sprint: S2-C
# Source: ANTIGRAVITY_S2C_BRIEFING_20260609.md + Kali Gap Synthesis + Roc S2-D

---

## §1 — Prioritized Remediation Queue

Items ranked by: **Severity × Effort⁻¹** (highest impact, lowest effort = highest priority)

| Rank | ID | Severity | Effort | Priority Score | Title | Status |
|------|-----|:--------:|--------|:--------------:|-------|:------:|
| 1 | SD-001 | 🔴 CRITICAL | 4h | 10.0 | Zero auth on Omega Hub — no token/API-key validation | Sentinel sprint active |
| 2 | SD-006 | 🔴 HIGH | 0.25h | 9.5 | BSP health_monitor omitted in 5 ModelGateway sites (8-line fix) | Unassigned |
| 3 | SD-008 | 🟡 MED | 0.5h | 8.0 | Soul distillation hook is empty stub — trigger not wired | Unassigned |
| 4 | SD-010 | 🟡 MED | 0.25h | 8.0 | Indexer.close() never called — aiosqlite teardown warnings | Roc active |
| 5 | SD-002 | 🟡 MED | 1h | 7.5 | CORS allow_origins=["*"] — open to any origin | Sentinel sprint active |
| 6 | SD-004 | 🔴 HIGH | 2h | 7.0 | T1 AP tokens missing from hardened code | Unassigned |
| 7 | SD-003 | 🟡 MED | 2h | 6.0 | No RPS rate limiting on Hub | Sentinel sprint active |
| 8 | SD-007 | 🟡 MED | 1h | 5.5 | CREDITS.md §1.14 has 5+ factual errors (memory architecture) | Unassigned |
| 9 | SD-009 | 🟡 MED | 1.5h | 5.0 | 3 library knowledge gaps (TDP, RRF, aiosqlite) — no indexed docs | **DONE (S2-C Part 1)** |
| 10 | SD-005 | 🟡 MED | 8h+ | 3.0 | T3 test coverage gaps (68% uncovered) | Unassigned |

---

## §2 — Effort Estimates

| ID | Task Description | Effort Estimate | Blocking On |
|----|-----------------|----------------|-------------|
| SD-001 | API key header validation middleware in omega_hub/server.py | 4h | Sentinel sprint |
| SD-002 | Restrict CORS origins list in server.py | 1h | SD-001 (auth first) |
| SD-003 | Add slowapi or custom RPS middleware | 2h | SD-001 |
| SD-004 | Audit all code for missing AP token headers; add to hardened files | 2h | — |
| SD-005 | Write tests for soul_distiller.py, errors.py, crossref.py, security.py | 8h+ | SD-009 (DONE) |
| SD-006 | Pass health_monitor to ModelGateway at 5 call sites | 15 min | — |
| SD-007 | Correct CREDITS.md §1.14 memory architecture description | 1h | — |
| SD-008 | Wire soul distillation trigger at session-end in orchestrator.py | 30 min | — |
| SD-009 | Create + index 3 gap docs (TDP, RRF, aiosqlite) | 1.5h | **COMPLETE** ✅ |
| SD-010 | Call indexer.close() in MCP server lifespan | 15 min | — |

---

## §3 — Dependency Chain

```
SD-009 (knowledge gap docs) ──[DONE]──→ SD-005 (test coverage can now test crossref)

SD-001 (auth) ──→ SD-002 (CORS, once auth is wired)
              └──→ SD-003 (rate limit, once auth is wired)

SD-006 (health_monitor) ──────────────→ Standalone (no deps)
SD-008 (soul distillation) ───────────→ Standalone (no deps)
SD-010 (indexer teardown) ────────────→ Standalone (no deps, 15 min fix)
SD-004 (AP tokens) ───────────────────→ Standalone
SD-007 (CREDITS.md) ──────────────────→ Standalone
SD-005 (test coverage) ───────────────→ Blocked on SD-001, SD-006, SD-008 being stable
```

---

## §4 — Agent Assignment Map

| Agent | Sovereign Debt Items | Rationale |
|-------|---------------------|-----------|
| **Sentinel** (P5 Governance) | SD-001, SD-002, SD-003 | Auth/CORS/rate-limit = governance domain |
| **Doom Guy** (id Software Architect) | SD-004 (AP tokens) | Heritage + mandate enforcement domain |
| **Ma'at** (Build Side P1-P5) | SD-006 (health_monitor), SD-008 (soul hook) | Build-side wiring, 8-line fixes |
| **Roc Racoon** (Legacy Archaeology) | SD-007 (CREDITS.md) | Heritage accuracy = Roc's domain |
| **Watchtower** (P8 Observability) | SD-010 (aiosqlite teardown) | Observability/teardown = P8 domain |
| **Quality** (P10 Validation) | SD-005 (test coverage) | Full test suite expansion = quality domain |
| **Antigravity IDE** | SD-009 | **COMPLETE** ✅ |

---

## §5 — Sprint Plan

### Sprint S2-C (NOW — Today, 2026-06-09)

**Goal**: Complete knowledge layer + quick-win fixes.

| Task | Agent | Effort | Status |
|------|-------|--------|--------|
| SD-009: 3 gap docs created + indexed | Antigravity | 1.5h | ✅ DONE |
| crossref.py dual-path engine | Antigravity | 0.5h | ✅ DONE |
| verify_knowledge_sovereign.py | Antigravity | 0.25h | ✅ DONE |
| SD-006: Wire health_monitor (8-line fix) | Ma'at | 0.25h | Unassigned |
| SD-010: Wire indexer.close() in lifespan | Watchtower | 0.25h | Roc active |
| SD-008: Wire soul distillation trigger | Ma'at | 0.5h | Unassigned |

**Quick wins total: ~1h for SD-006 + SD-010 + SD-008**

---

### Sprint S2-D (Next — Auth + Heritage Hardening)

**Goal**: Close critical security gaps + heritage accuracy.

| Task | Agent | Effort |
|------|-------|--------|
| SD-001: API key auth middleware | Sentinel | 4h |
| SD-002: Restrict CORS origins | Sentinel | 1h |
| SD-003: RPS rate limiting | Sentinel | 2h |
| SD-004: AP token audit | Doom Guy | 2h |
| SD-007: Fix CREDITS.md §1.14 | Roc | 1h |

**Sprint total: ~10h**

---

### Sprint S2-E (Following — Coverage + Validation)

**Goal**: Raise test coverage from 68% to 85%+.

| Task | Agent | Effort |
|------|-------|--------|
| SD-005: Tests for soul_distiller.py | Quality | 2h |
| SD-005: Tests for errors.py | Quality | 1h |
| SD-005: Tests for crossref.py | Quality | 1.5h |
| SD-005: Tests for security.py (TDP) | Quality | 1.5h |
| SD-005: Integration tests (MCP taint) | Quality | 2h |

**Sprint total: ~8h**

---

## §6 — "Sovereign Grade" Gate Criteria

The engine reaches **Sovereign Grade** when ALL of the following are true:

### 🔴 CRITICAL (must be resolved)
- [ ] **SD-001** — Auth token validation active on all Omega Hub endpoints
- [ ] **SD-004** — AP tokens present in all hardened source files

### 🟡 MEDIUM (must be resolved)
- [ ] **SD-002** — CORS origins restricted (no wildcard)
- [ ] **SD-003** — RPS rate limiting active
- [ ] **SD-006** — health_monitor wired at all 5 ModelGateway call sites
- [ ] **SD-007** — CREDITS.md §1.14 factually accurate
- [ ] **SD-008** — Soul distillation fires at session-end
- [ ] **SD-009** — All 3 gap docs indexed (**DONE** ✅)
- [ ] **SD-010** — Indexer.close() wired in MCP server lifespan

### 📊 Metrics
- [ ] Test coverage ≥ 85% (currently 68%)
- [ ] `make test` passes 329/329 (currently passing)
- [ ] `make temple-grade` T1-T11 all GREEN
- [ ] `make heritage-map` — all [id-soft:] tags verified
- [ ] `python scripts/verify_knowledge_sovereign.py` — exit 0

### Definition
> **Sovereign Grade** = Zero 🔴 CRITICAL items + all 🟡 MEDIUM items resolved + verify script exits 0 + temple-grade passes.

---

## §7 — Newly Discovered Items (KG series)

| ID | Finding | Impact | Assigned To | Effort |
|----|---------|:------:|-------------|--------|
| KG-001 | M2 Engine-Stack Firewall has 6 minor cracks | Low-Med | Ma'at | 1h |
| KG-002 | BSP health_monitor param omitted at 5 sites | Med | Ma'at | 15 min |
| KG-003 | Soul distillation trigger is empty stub | Med | Ma'at | 30 min |

KG-002 = SD-006, KG-003 = SD-008 (already tracked above).

---

*⬡ OMEGA ⬡ ANTIGRAVITY-IDE ⬡ S2-C Sovereign Debt Synthesis ⬡ 2026-06-09*
