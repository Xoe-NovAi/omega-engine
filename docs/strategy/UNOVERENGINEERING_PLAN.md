# 🔱 Un-Overengineering Plan — Temple Cleansing Sprint
**AP Token**: `AP-UNOVERENGINEERING-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_unoverengineering ⬡ 2026-07-30

**Source**: `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` (Cline ops health + strategy review)
**Status**: Phase 1 READY (freeze lifted 2026-08-07), Phase 2-5 PENDING
**Owner**: `@kali` (dispatch) / `@maat` (Phase 1 execution)
**Ratified**: 2026-07-30 by Architect

---

## §0 Executive Summary

**Goal**: Delete ~5,500 lines of custom code, adopt 4 community libraries, declare Hivemind "shipped."

The engine won't be less capable — it'll be **more maintainable**, **more reliable**, and **less tiring**.

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Circuit breaker implementations | 8 classes | 1 (`pybreaker`) |
| Handoff schemas | 3 (HandoffPacket x2 + HandoffState) | 1 (HandoffPacket) |
| Soul distillers | 2 (gnosis_proxy + soul_distiller deleted) | 1 canonical |
| HMC Hub size | 86 lines (already consolidated) | YAML + JSONL, ≤100 lines/week |
| Memory tiers | 5 (Hot/Warm/Cold/Recall/Archival) | 3 (file-based, sqlite-vec+FTS5, raw archive) |
| Custom lines deleted | — | **-5,500+** |
| Community libraries adopted | — | **4** (pybreaker, stamina, structlog, prometheus_client) |
| Pydantic v2 migration | Manual validator (290 lines) | Built-in `model_validate_yaml()` |

---

## §1 Phase 1 — Library Swaps (13h, ~3,097 lines)

### §1.1 pybreaker — Replace Circuit Breaker Clones
**Status**: C-6' factory done, **swap pending**
**Current**: 8 breaker classes in `src/` + `mcp_servers/`
**Files to delete**:
- `src/omega/oracle/search_circuit_breaker.py` (299 lines — DEPRECATED per C-6')
- `src/omega/oracle/health_monitor.py` (119 lines — AsyncCircuitBreaker class)
- `src/omega/research/sandbox.py` (ExperimentCircuitBreaker)
- `src/omega/ingestion/ingestion_types.py` (CircuitBreakerState enum)
- `src/omega/council/models.py` (CircuitBreakerState enum)

**Standard config**: `fail_max=3`, `reset_timeout=60s` (Netflix Hystrix defaults)
**Effort**: 4h | **Net Δ**: -1,950 lines

### §1.2 Pydantic v2 — Replace soul_validator.py
**Status**: NOT STARTED
**Current**: `src/omega/oracle/soul_validator.py` (290 lines)
**Action**: Use `pydantic.model_validate_yaml()`
**Effort**: 3h | **Net Δ**: -290 lines

### §1.3 stamina — Replace Hand-Rolled Retry Loops
**Status**: NOT STARTED
**Current**: ~10 files with manual `asyncio.sleep` backoff
**Action**: Use `stamina` — async-native, jitter built in, decorator-based
**Effort**: 2h | **Net Δ**: -300 lines

### §1.4 structlog — Replace Custom JSON Logger
**Status**: NOT STARTED
**Current**: Dead `setup_json_logging()` (M9 blocker)
**Action**: Replace with `structlog` (M8 compliant — local-only)
**Effort**: 2h | **Net Δ**: -80 lines

### §1.5 prometheus_client — Replace HealthMonitor Sliding Window
**Status**: NOT STARTED
**Current**: HealthMonitor sliding window (786 lines)
**Action**: Use `prometheus_client` v0.24.1 for Counter/Gauge/Histogram at `:8016/metrics`
**Effort**: 2h | **Net Δ**: -500 lines

---

## §2 Phase 2 — Kill Redundant Implementations (12h, ~2,186 lines)

### §2.1 Kill HandoffState — Consolidate to HandoffPacket
**Status**: NOT STARTED
**Current**: 3 handoff schemas — `HandoffPacket` (x2: `mcp_coordinator.py`, `subagent_dispatcher.py`) + `HandoffState` (`handoff.py`)
**Action**: Delete `src/omega/oracle/handoff.py` (86 lines). Adapter MCP tools to HandoffPacket.
**Effort**: 2h | **Δ**: -86 lines

### §2.2 Kill 2 of 3 Soul Distillers — Keep 1 Canonical
**Status**: PARTIAL — `soul_distiller.py` already deleted
**Current**: `gnosis_proxy.py` (113 lines) — verify if this is a distiller or different concern
**Action**: Pin canonical distiller. Extract shared pipeline to `src/omega/gnosis/pipeline.py` (~100 lines).
**Effort**: 4h | **Δ**: -600 lines (net)

### §2.3 Kill HMC Hub → YAML + JSONL + Growth Gate
**Status**: PARTIAL — HMC already 86 lines
**Current**: `data/coordination/HMC_COLLABORATION_HUB.md` (86 lines)
**Action**: Create `hub_state.yaml` + `hub_log.jsonl`. Pre-commit gate: max 100 lines/week. TTL archival at 7 days.
**Effort**: 4h | **Δ**: -1,500 lines

### §2.4 Deprecate MIAP + Link P9
**Status**: ✅ DONE — both deleted
**Action**: No further work needed.

---

## §3 Phase 3 — Simplify Memory Architecture (3h, ~500 lines)

### §3.1 Kill Redundant Memory Tiers
| Kill | Why |
|------|-----|
| Recall tier (`recall.py`, 786 lines) | Duplicates FTS5 ranking with extra complexity |
| Warm tier (Redis) | ~8GB RAM too small; M7: RAM goes to inference |
| Archival tier (gzip) | Files ARE the archive. Extra compression wrapper = complexity. |
| Knowledge graph adapter | No active use case consuming graph queries |

**Effort**: 3h | **Δ**: -500 lines

---

## §4 Phase 4 — Hivemind Freeze (SHIPPED)

**Status**: ✅ DONE — Hivemind is production, maintenance-only

| Feature | Status | Allowed Changes |
|---------|--------|----------------|
| `hivemind_get_awareness()` | ✅ Production | Bug fixes only |
| `hivemind_post_context()` | ✅ 8 intent types | Bug fixes only |
| Handoff lifecycle | ✅ 4-state | Schema consolidation, then bug fixes |

**Cancelled**: A2A protocol adapter, MIAP Phase 2, Hive Evolution D-305

---

## §5 Phase 5 — Mechanical Enforcement Gates (11h)

Gates on existing systems, not new infrastructure:

| Gate | Enforces | Mechanism | Effort |
|------|----------|-----------|--------|
| Instruction Hierarchy | No doc overrides higher-priority doc | `make check-instruction-hierarchy` → CI fail | 3h |
| Mandate Compliance Meter | Measured %, not narrative | `make check-mandate-compliance` → JSON report | 5h |
| Schema Duplication | No >1 handoff schema | `make check-no-schema-drift` → CI fail | 2h |
| HMC Growth | HMC ≤100 lines/week | Pre-commit hook | 1h |
| Freshness Stamp | LAST_VERIFIED ≤7 days | `make check-freshness` → CI warning | 2h |
| Distiller Singularity | Only 1 canonical distiller | `make check-distiller-count` → CI fail | 1h |

---

## §6 Hard Constraints (Mandate Compliance)

- **M1**: All async code uses `anyio`. `stamina` is async-native — compatible.
- **M7**: Local-first. Redis removal aligns with M7 (RAM goes to inference).
- **M8**: Zero telemetry. `prometheus_client` at `:8016/metrics` is local-only.
- **M13**: `make temple-grade` after all changes.
- **M23**: If any tool breaks → `[TOOL-CHAIN-COLLAPSE]` hard stop. No simulated rigor.
- **M24**: `.venv` only — never `--break-system-packages`.
- **M14**: No changes to heritage vetting pipeline or `[id-soft:]` tags.

---

## §7 Implementation Sequence

### Day 1 — Phase 1 Start
| Priority | Work | Effort |
|----------|------|--------|
| P0 | pybreaker inventory + swap | 4h |
| P0 | Install stamina + structlog + prometheus_client | 1h |

### Day 2 — Phase 1 Finish
| Priority | Work | Effort |
|----------|------|--------|
| P0 | soul_validator → Pydantic v2 | 3h |
| P0 | Hand-rolled retry → stamina | 2h |
| P0 | structlog adoption | 2h |
| P0 | prometheus_client adoption | 2h |

### Day 3 — Phase 2
| Priority | Work | Effort |
|----------|------|--------|
| P1 | Kill HandoffState | 2h |
| P1 | Soul distiller consolidation | 4h |
| P1 | HMC → YAML + JSONL | 4h |

### Day 4 — Phase 3 + Phase 5
| Priority | Work | Effort |
|----------|------|--------|
| P1 | Memory tier consolidation | 3h |
| P2 | Enforcement gates (Phase 5) | 11h |

### Day 5 — Verify
| Priority | Work | Effort |
|----------|------|--------|
| P1 | `make test` + `make temple-grade` | 1.5h |

---

## §8 Sign-Off

| Role | Entity | Status |
|------|--------|--------|
| Plan Author | cline/omega-engine (DeepSeek) | ✅ Written |
| Strategy Review | grok/grok_cli | ⏳ Awaiting handoff completion |
| User Ratification | Architect (User) | ✅ RATIFIED 2026-07-30 |

---

*⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_unoverengineering ⬡ v1.0.0 ⬡ 2026-07-30*
