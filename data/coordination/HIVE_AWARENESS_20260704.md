# 🔱 HIVEMIND AWARENESS — 2026-07-04 (Phase 5 Complete)
⬡ OMEGA ⬡ COORDINATION ⬡ 2026-07-04 ⬡ SOVEREIGN-STATE
**AP**: `AP-HIVEMIND-COORDINATION-v1.0.0`

---

## 📡 Active Agent State

| Agent | Session | Duration | Files | Lines | Status | Last Contact |
|-------|---------|----------|-------|-------|--------|-------------|
| **Researcher** | WARP Proxy Pool | ~3.5 hrs | 5 new, 5 cleaned | ~900 | 🟢 ACTIVE (post-WARP) | 2026-07-05 |
| **Jem** | Doc Arch + Wave 2 Hardening + T2 Ports + T3 Fix + T3-1 Lifecycle + T3-2 MetricsDB | ~8.5 hrs | 19 new, 25 archived | ~2,473 | 🔄 T3-2 IN PROGRESS | 02:00 UTC |
| **John Carmack** | Selective Hydration + Polish Sprint | ~2 hrs | 1 new (+6 tests) | ~150 | ✅ COMPLETE | 02:15 UTC |

**Fleet-wide**: 3 parallel sessions, ~8.5 agent-hours, zero file conflicts, all gates green.
**Post-session**: Carmack ACK filed. Researcher active as of 2026-07-05. Jem Phase 5 done — T2-11, T2-12, T3 timeout fix all delivered.

---

## 🗺️ Territory Map (File Ownership)

### 🔴 Researcher — DO NOT TOUCH
| File | Purpose |
|------|---------|
| `scripts/spawn_warp_node.sh` | WARP node lifecycle automation (v1.2.0) |
| `deploy/infra/warp_pool/warp-node@.service` | systemd template unit (v1.1.0) |
| `deploy/infra/warp_pool/warp-pool.target` | systemd target (v1.0.0) |
| `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` | Canonical spec (v1.1.0, 487 lines) |
| `docs/research/warp_proxy_pool/validate_warp_pool.sh` | 8-scenario validation script |
| `docs/research/OPENCODE_ZEN_BYPASS.md` | Setup guide (updated) |

### 🔴 Jem — DO NOT TOUCH
| File | Purpose |
|------|---------|
| `src/omega/proxy_pool.py` | Sovereign WARP Proxy Pool Python wrapper (v1.0.0) |
| `src/omega/oracle/soul_edit_history.py` | **NEW** Append-only YAML audit trail (T2-11) |
| `src/omega/oracle/compaction_harvester.py` | **NEW** Compaction monitoring + metrics (T2-12) |
| `src/omega/oracle/session_lifecycle.py` | **NEW** Session lifecycle state machine (T3-1) |
| `src/omega/oracle/provider_selector.py` | PII-aware backend scoring |
| `src/omega/oracle/degradation.py` | Graceful degradation manager |
| `src/omega/oracle/rate_limiter.py` | Token bucket rate limiter |
| `src/omega/oracle/timeout_manager.py` | 4-layer cancellation |
| `src/omega/oracle/somatic_state.py` | KV cache serialization |
| `docs/llms.txt` | AI agent navigation sitemap (57 lines) |
| `docs/llms-full.txt` | Concatenated key docs (147 lines) |
| `docs/USER_MANUAL.md` | User manual (1,198 lines, refreshed) |
| `docs/QUICKSTART.md` | 5-minute install guide (88 lines) |
| `docs/contributing/setup.md` | Developer environment guide (124 lines) |
| `docs/how-to/*.md` | 3 guides (review-soul-lessons, use-hivemind, handoff-tasks) |
| `docs/explanation/*.md` | 4 guides (makali-triad, hivemind-protocol, provider-chain, why-22-mandates) |
| `docs/reference/api/*.md` | 5 API ref docs (oracle, entity_registry, model_gateway, memory_store, context_builder) |
| `docs/tutorials/first-wad.md` | First WAD tutorial |
| `scripts/validate_somatic_links.py` | AST-based Somatic-Doc CI check |
| `scripts/generate_llms_full.py` | llms-full.txt generator |
| `scripts/validate_doc_examples.py` | Executable examples CI check |
| `tests/test_soul_edit_history.py` | **NEW** 17 tests for SoulEditHistory |
| `tests/test_compaction_harvester.py` | **NEW** 31 tests for CompactionHarvester |
| `tests/test_session_lifecycle.py` | **NEW** 24 tests for SessionLifecycleManager |
| `tests/test_metrics_db.py` | Existing 30 tests for MetricsDB (wired this session) |

### 🔴 John Carmack — DO NOT TOUCH
| File | Purpose |
|------|---------|
| `src/omega/oracle/selective_hydration.py` | L3Principle + SelectiveHydration (Qdrant-backed) |
| `src/omega/oracle/context_builder.py` | Gnosis block injection (modified) |
| `tests/test_selective_hydration.py` | 27 tests |
| `tests/test_headroom.py` | 3 tests (rewritten) |

### 🟡 Shared (Coordination Required Before Edit)
| File | Risk | Owners | Notes |
|------|------|--------|-------|
| `src/omega/oracle/model_gateway.py` | Medium | Jem + Researcher | Jem wired ProviderSelector + RateLimiter; Researcher wired proxy pool |
| `src/omega/oracle/oracle.py` | Medium | Jem + Carmack | Jem wired TimeoutManager + Degradation + SoulEditHistory + CompactionHarvester; Carmack wired SelectiveHydration |
| `config/providers.yaml` | Low | Jem + Researcher | Jem added env: prefix; Researcher may add proxy settings |
| `Makefile` | Low | Jem | Fixed `test-cov` target — added `OMEGA_ENV=test` for T3 timeout |

---

## 🔧 Integration Points (Pending & Complete)

### Pending — Ready for Next Session
| Integration | Owner | Effort | Blocked By | Priority |
|-------------|-------|--------|------------|----------|
| **WARP Proxy Pool → ModelGateway** | Jem (impl) + Researcher (design) | 2 hr | User deployment of systemd units + `validate_warp_pool.sh` pass | 🟡 P1 |
| **SomaticState → Oracle public API** | Jem | 1 hr | None — `save_state()`/`load_state()` added this session | 🟡 P1 |
| **T3n-1**: Session lifecycle automation (Active→Archive→Compress→Delete) | Jem | 3 hr | None | 🟢 **DONE** — 24 tests, recall-from-external, Oracle wired |
| **T3-2**: Observability DB (Metrics DB wiring) | Jem | 2 hr | Schema already exists (D184) | ✅ **COMPLETE** — 12 integration tests, _obs_engine→observability fix, all 791 tests pass |
| **T3-3**: Mandate CI gates (16/22 mandates) | Jem | 3 hr | None | 🟢 P2 |

### Complete — Wired This Session (Phases 1-5)
| Integration | Owner | Status |
|-------------|-------|--------|
| ProviderSelector → ModelGateway.generate() | Jem | ✅ `get_ordered_providers()` replaces raw iteration |
| RateLimiter → ModelGateway.generate() | Jem | ✅ Token bucket checked per-provider |
| TimeoutManager → Oracle.talk() + Oracle._summon() | Jem | ✅ 4-layer: Tool→Group→Turn→Workflow |
| GracefulDegradation → Oracle.talk() | Jem | ✅ Optimal→Stressed→Critical→Disabled |
| SomaticState → NativeGGUFProvider | Jem | ✅ SAVE_STATE/LOAD_STATE worker commands |
| SomaticState → Oracle public API | Jem | ✅ `save_state()`/`load_state()` exposed |
| SelectiveHydration → ContextBuilder | Carmack | ✅ Auto-injects L3 gnosis into every query |
| DocRef Somatic-Doc Binding → `make temple-grade` T12 | Jem | ✅ AST-based link validation |
| `llms-full.txt` generator → CI | Jem | ✅ `scripts/generate_llms_full.py` |
| Soul Edit History → Oracle.close_session() | Jem | ✅ Immutable audit trail for soul.yaml |
| Soul Edit History → soul_updater.py | Jem | ✅ Background researcher L3 writes tracked |
| Compaction Harvester → Oracle.close_session() | Jem | ✅ Session size monitoring + metrics |
| Compaction Harvester → Oracle.__init__() | Jem | ✅ Singleton wired to Oracle lifecycle |
| T3 timeout fix: `test-cov` → `OMEGA_ENV=test` | Jem | ✅ Coverage no longer runs real model loading |
| SessionLifecycleManager → Oracle.bootstrap() | Jem | ✅ Active→Archived→External→Deleted lifecycle sweep |
| recall_from_external() → D189 gap resolved | Jem | ✅ Write-only archival → bidirectional lifecycle |
| MetricsDB → ObservabilityEngine | Jem | ✅ Lazy init, record_performance, record_metrics_error, record_breaker_transition |
| MetricsDB → HealthMonitor | Jem | ✅ Breaker transitions recorded on state change |
| MetricsDB → Oracle | Jem | ✅ Performance recording after inference in _summon + _route_by_domain |

---

## 🧬 Combined Soul Distillation (23 L3 Principles)

### From Jem (Phase 1-2 — Documentation Architecture)
1. **Functional Identity** — role defined by entropy reduced
2. **Mathematical Sovereignty** — control via probability distribution
3. **Integration Seam** — failure at module boundaries
4. **Dual-Source Convergence** — external + internal convergence validates path
5. **Expected Truncation** — detect, log, compensate at every boundary
6. **Asynchronous Sovereign Handoff** — file-based coordination survives outages
7. **Interface-Then-Document** — specify API before writing docs
8. **SSOT Singularity** — a triplicated SSOT is no SSOT at all
9. **High-Density Markdown** — AI-readable docs must be dense and clear
10. **Somatic-Doc Binding** — bind code to docs via AST-based CI
11. **The Staging Gate** — agents write to proposed_lessons.yaml; user approves
12. **Executable Examples** — validate code examples in CI

### From Jem (Phase 3 — Sovereign Hardening)
13. **Cascade-of-Complexity** — build layers in order: base → health → PII penalty
14. **Pre-Existing Bug Theorem** — every uncovered code path is a latent failure
15. **CI-Gate Rigor** — CI must validate exact formats, not fuzzy substrings

### From Researcher (WARP Proxy Pool)
16. **Socat Bridge Pattern** — host↔namespace loopback without veth pairs
17. **Defensive Programming** — dependency checks, input validation, lifecycle management
18. **Resource Containment** — systemd MemoryHigh/MemoryMax/CPUQuota for 12GiB systems

### Implicit from Carmack (Selective Hydration)
19. **Entity Namespace Isolation** — L3 principles stored under `l3_gnosis_{entity_name}` collections
20. **Silent Fallback** — M9 compliance via silent error handling in hydration

### From Jem (Phase 4 — WARP Integration)
21. **Sovereign-Sieve Loop** — IP rotation + PII masking + rate limiting = complete cloud sovereignty

### From Jem (Phase 5 — T2 Ports + T3 Fix)
22. **Append-Only Audit** — immutable audit trails prevent soul drift through deterministic replay
23. **Coverage Isolation** — coverage instrumentation must not activate real backends; test isolation applies to coverage runs

### From Jem (T3-1 — Session Lifecycle)
24. **Lifecycle Bidirectionality** — a lifecycle system that only progresses forward without the ability to reverse is a one-way valve that violates data sovereignty

---

## ❓ Open Questions (For Next Session)

| # | Question | Asked By | Answered By | Status |
|---|----------|----------|-------------|--------|
| 1 | What import path / interface does `EphemeralWarpPool` use? Does it exist yet as a Python class? | Jem | Carmack | ✅ **RESOLVED**: No Python class exists. Write `src/omega/proxy_pool.py` during ModelGateway integration. See §Integration Spec below. |
| 2 | Should `SelectiveHydration.store()` be called by agents directly or through user-approval gate? | Carmack | Jem + Carmack | ✅ **RESOLVED**: agents → `proposed_lessons.yaml`, user → `store()`. Carmack confirmed his `store()` enforces no gate — gate lives in protocol. |
| 3 | What taxonomy should the `domain` field use in `L3Principle`? | Carmack | Council | ✅ **RESOLVED** — Carmack: Use Diátaxis (tutorial/how_to/reference/explanation) as primary. Add "cross-cutting" fallback for principles spanning multiple domains. Pillar slots (P1-P10) are for entity routing, not gnosis classification. |
| 4 | Should `MIN_CONFIDENCE = 0.5` be tunable per entity? | Carmack | Council | ✅ **RESOLVED** — Carmack: Global 0.5 locked. Per-entity tuning deferred to D16-2 (Parametric Gnosis). No changes needed. |
| 5 | **AP Token format inconsistency** | Carmack | All | ✅ **RESOLVED** — Carmack migrated 48+7 files; 0 old-format remain |
| 6 | **T3 `test-cov` timeout** | Jem | Self | ✅ **RESOLVED** — Missing `OMEGA_ENV=test` caused real model loading during coverage |

---

## 📊 Test Suite & CI State

| Metric | Value | Status |
|--------|-------|--------|
| Tests collected | **791** | ✅ (+12 from T3-2 MetricsDB integration tests) |
| New tests (SoulEditHistory) | 17 | ✅ Added by Jem |
| New tests (CompactionHarvester) | 31 | ✅ Added by Jem |
| New tests (SomaticState/Oracle API) | 4 | ✅ Added by Jem |
| Temple-Grade | 10/11 green, 1 amber | ✅ T7 latency exempted |
| T3 timeout fix | `test-cov` → `OMEGA_ENV=test` | ✅ Applied in Makefile |
| AP Token compliance | 136/136 files | ✅ (2 new files added this session) |
| AST syntax clean | 136/136 files | ✅ (2 new files verified) |

---

## 🧠 Key Technical Decisions (Immutable Record)

| Decision | Rationale | Source |
|----------|-----------|--------|
| Providers scored by: BasePriority*10 − PII_Penalty(100) − Error_Penalty | Aligns M7 (local-first) with M22 (provenance) via incentive engineering, not policy | Jem D169 |
| `socks5h://` over `socks5://` for WARP proxy | Forces DNS through WARP exit node, preventing local DNS leaks | Researcher Phase 4 |
| `socat` bridge over veth pairs for namespace isolation | Simpler, no rootless networking issues, proven pattern | Researcher Phase 2 |
| Agents write `proposed_lessons.yaml`; only user calls `store()` | Prevents sycophancy loops (Staging Gate) | Carmack + Jem |
| SomaticState via ctypes `llama_copy_state_data` in worker process | C-FFI process isolation prevents C-level segfaults from crashing engine | Carmack S3 |
| Diátaxis for external docs; R-doc system for internal research | Quadrant clarity preserves BOTH agent-readability and developer heritage | Jem Phase 1 |
| Three SSOT → one: OMEGA_ENGINE.md is sole state SSOT | Eliminates drift between overlapping authority claims | Jem Phase 1 |
| SoulEditHistory append-only with tmp+rename | Prevents data corruption from partial writes (Quake 0.5s Realloc Grace) | Jem Phase 5 |
| CompactionHarvester in-memory with rolling window | Avoids spurious disk I/O for metric recording; window prevents unbounded growth | Jem Phase 5 |
| `test-cov` must use `OMEGA_ENV=test` | Coverage adds ~2x overhead; real backend loading makes it unusable (>120s timeout) | Jem Phase 5 |

---

## ⏰ Heartbeat

```
Agent: opencode/jem
Channel: opencode
Entity: jem
Status: 🟢 ALL 5 PHASES COMPLETE — T2-11, T2-12, T3 Fix Delivered
Timestamp: 2026-07-04 ~21:00 UTC
```

```
Agent: opencode/jem
Channel: opencode
Entity: jem
Status: 🟢 HANDOFF TO CARMACK POSTED — T3 Sprint Plan + WARP Status + Heritage Distillation
Timestamp: 2026-07-05 ~00:00 UTC
```

```
Agent: opencode/jem
Channel: opencode
Entity: jem
Status: 🟢 T3-1 SESSION LIFECYCLE COMPLETE — 24 tests, recall-from-external, Oracle wired
Timestamp: 2026-07-05 ~01:00 UTC
```

```
Agent: opencode/jem
Channel: opencode
Entity: jem
Status: 🔄 T3-2 METRICS DB WIRING IN PROGRESS — ObservabilityEngine + HealthMonitor + Oracle wired, tests pending
Timestamp: 2026-07-05 ~02:00 UTC
```

---

## 📁 Compact Recovery Reference

After compaction, any agent can resume by reading these files in order:

```
1. data/coordination/HIVE_AWARENESS_20260704.md         ← THIS FILE (current state)
2. data/coordination/MASTER_COORDINATION_20260704.md     ← Session summary (Researcher)
3. data/coordination/CARMACK_WIRING_COMPLETE.md          ← Selective Hydration details
4. data/entities/jem/proposed_lessons.yaml               ← 23 L3 principles
5. data/entities/jem/workspace/session_gnosis.md         ← Jem's full session log
6. data/coordination/JEM_LIVE_FEED.md                    ← Phase 5 events
```

---

*🔱 OMEGA ⬡ COORDINATION ⬡ HIVEMIND-AWARENESS ⬡ 2026-07-04 ⬡ 3 AGENTS ⬡ 23 L3 PRINCIPLES*
