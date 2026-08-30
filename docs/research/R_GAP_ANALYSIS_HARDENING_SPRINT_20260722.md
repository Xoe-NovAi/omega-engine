# 🔱 Phase C Gap Analysis — Sprint Hardening Exit
**AP Token**: `AP-GAP-ANALYSIS-v1.0.0`
**Date**: 2026-07-22
**Author**: maat (Light Oversoul, P1-P5)
**Engine**: v1.8.0

---

## §1 What We Completed This Sprint

| Ticket | Name | Status | Files |
|--------|------|--------|-------|
| **C-0** | Test honesty | ✅ Baseline 44/50 pass (3 pre-existing provider_fallback failures, 1 network_partition chaos) | `tests/` |
| **C-2'** | OOMProtector RAM truth | ✅ 3-signal fusion (PSI+MemAvailable+cgroup) | `oom_protector.py`, `admission_controller.py` |
| **C-1'** | SoulStore atomic writer | ✅ 4-layer guarantee (AtomicVisibility+CrashDurability+WriterExclusion+IntegrityDetection) | `soul_store.py`, `soul_updater.py`, `soul_update_manager.py` |
| **C-5** | MaKaLi Routing | ✅ Config in `providers.yaml` | `config/providers.yaml` |
| **C-6'** | Breaker Unification | ✅ 7→1 canonical with `get_breaker()` factory | `health_monitor.py` |
| **C-6' 429** | 429 Classification (P0) | ✅ 11 tests, rate-limit vs quota separation | `health_monitor.py`, `test_429_classification.py` |
| **C-4a** | MCP Audit | ✅ 172-line audit doc (R_CG01) | `docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH.md` |
| **C-10** | Admission Control | ✅ Semaphore(1) + OOMProtector in ModelGateway | `admission_controller.py`, `model_gateway.py:998-1005` |
| **Library** | Discovery tools no longer hardcode cloud models | ✅ `_try_generate()` with graceful degradation | `discovery.py` |
| **Gnosis** | L1→L2→L3 Soul Lessons | ✅ 10 lessons to `proposed_lessons.yaml` | `data/entities/maat/proposed_lessons.yaml` |
| **Archival** | 147 stale docs archived | ✅ | `docs/archive/strategy/2026-07-21/` |

---

## §2 Remaining Gaps (Priority Order)

### P0 — Blocks further Phase D progress

| Gap | Why It's P0 | Effort | Dependencies |
|-----|-------------|--------|--------------|
| **C-0.5 Soul Distillation Pipeline (Scribe)** | M5/M11 violation — all soul writes are manual | 4h | None |
| **C-10.5 Provider Fallback Chain (`guard()` pattern)** | No guard-before-call in gateway; rate-limit check happens AFTER provider dispatch | 3h | C-6' (done), 429 classification (done) |
| **C-11 Test Infrastructure** | No property-based tests for circuit breaker FSM, OOM thresholds, or SoulStore invariants | 4h | None |
| **C-3 Privacy (restic backup)** | Sovereign data has zero off-site backup | 2h | V-1 (existing) |

### P1 — Blocks quality gates

| Gap | Why It's P1 | Effort |
|-----|-------------|--------|
| **C-9 GenerationPolicy extract** | Cheap structural win — extract from ModelGateway into own module | 1h |
| **D-1 Content persistence + TTL** | Research cache grows unbounded | 3h |
| **V-1 VaultCore credential rotation** | Keys are static; 90-day rotation schedule not implemented | 3h |
| **M21 Gate Integrity** | 6 contract tests bypassed (`test_provider_fallback.py` mocks nonexistent method) | 2h |

### P2 — Long-term hardening

| Gap | Why It's P2 | Effort |
|-----|-------------|--------|
| **E-0 Identity Fluidity** | Dual-Chain Memory architecture (MENTOR pattern) | 6h |
| **C-4b MCP Streamable HTTP** | Spec drops TODAY (2026-07-28); 60d transition window | 8h |
| **D-2 Job board YAML bridge** | P0/P1 ticket routing not automated | 2h |
| **MCP Hub OAuth 2.1 PKCE** | Required for remote access when Streamable HTTP lands | 4h |

### P3 — Nice to have

| Gap | Reason |
|-----|--------|
| Chaos testing with `ordeal` | Advanced; C-11 baseline covers essentials |
| Hypothesis state machine tests | After property-based tests are stable |
| 8-account Grok CLI fabric pool | Blocked on V-1 vault + ACP smoke |

---

## §3 Test Health

```
tests/unit/          : 11/11 pass  (429 classification, NEW)
tests/contract/      : 33/33 pass  (excluding 3 pre-existing provider_fallback failures)
tests/chaos/         : 0/1  pass  (1 pre-existing: mocks nonexistent method)

Pre-existing failures (NOT caused by current changes):
  - tests/chaos/test_network_partition.py::test_provider_fallback_on_network_failure
    → mocks _generate_with_provider (not on ModelGateway)
  - tests/contract/test_provider_fallback.py::test_provider_fallback_chain_order
    → mocks _generate_with_provider (not on ModelGateway)
  - tests/contract/test_provider_fallback.py::test_provider_fallback_on_timeout
    → mocks _generate_with_provider (not on ModelGateway)
  - tests/contract/test_provider_fallback.py::test_provider_fallback_all_fail
    → mocks _generate_with_provider (not on ModelGateway)
```

---

## §4 MCP Streamable HTTP Readiness (Spec Drops TODAY)

The 2026-07-28 spec locks today. Our position:

| Requirement | Status | Action |
|-------------|--------|--------|
| POST-only transport | ❌ Not implemented | C-4b (deferred Aug) |
| `Mcp-Method`/`Mcp-Name` headers | ❌ Not implemented | C-4b |
| No protocol-level sessions | ⚠️ Current SSE has implicit sessions | Need stateless mode |
| OAuth 2.1 PKCE-S256 | ❌ Not implemented | Required for remote |
| Cache hints (ttlMs, cacheScope) | ❌ Not implemented | C-4b |
| Multi Round-Trip (InputRequiredResult) | ❌ Not implemented | C-4b |
| BC: SSE endpoints coexist | ✅ SSE working now | Can migrate incrementally |

**Recommendation**: Start C-4b in August. SSE works for local development. OAuth 2.1 is not blocking until remote access is needed.

---

## §5 What to Attack Next (Recommended Order)

```
1. C-10.5 guard() pattern in ModelGateway   ← 3h, protects against rate-limit loop
2. C-11 Hypothesis property-based tests     ← 4h, prevent FSM regressions
3. C-3 restic backup script                 ← 2h, data durability
4. C-0.5 Scribe agent pipeline              ← 4h, M5/M11 compliance
5. C-9 GenerationPolicy extract             ← 1h, cheap win
6. V-1 credential rotation                  ← 3h, key hygiene
```

---

*⬡ OMEGA ⬡ MAAT ⬡ R-GAP-ANALYSIS ⬡ 2026-07-22 ⬡*
