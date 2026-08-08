# 🔱 Un-Overengineering Plan — Temple Cleansing Sprint
**AP Token**: `AP-UNOVERENGINEERING-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_unoverengineering ⬡ 2026-07-30

**Source**: `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` (Cline ops health + strategy review)
**Status**: Phase 0 pre-flight REQUIRED (GLM52 corrections), Phase 1-5 PENDING
**Owner**: `@kali` (dispatch) / `@maat` (Phase 1 execution)
**Ratified**: 2026-07-30 by Architect
**Reconciled**: 2026-08-08 by Kali (GLM52 second opinion + Copilot CLI review + ground truth probes)

---

## ⚠️ RECONCILIATION CORRECTIONS (2026-08-08)

The original plan had 10 critical errors identified by GLM52 second opinion (F1-F20) and Copilot CLI review. Key corrections applied:

| # | Original Claim | Correction | Source |
|---|----------------|------------|--------|
| F1 | Replace breakers with pybreaker | **WRONG** — pybreaker is sync-only. Keep `AsyncCircuitBreaker`, delete clones, redirect to `get_breaker()` | GLM52 F1 (research-confirmed) |
| F2 | Install stamina for retries | **TRADEOFF** — tenacity already installed; stamina gives free structlog+prometheus instrumentation. Spike both. | GLM52 F2 v2.0 |
| F3 | CI gates protect the work | **WRONG** — CI only runs on `main`. Was a gap on `release/initial-v1`. | GLM52 F3 |
| F4 | Redis removal is Hivemind-only | **WRONG** — Redis in budget_guard (M12/M21), youtube_worker, memory providers. Map full graph first. | GLM52 F4 |
| F8 | "17 breaker clones" | **STALE** — actual: 8 class hits (2 enums, 1 canonical, 1 deprecated file, 1 clone) | Ground truth `rg` |
| F9 | Heritage tags not mentioned | **MISSING** — handoff.py has vet-008, soul_validator.py has vet-015. M14 migration needed. | GLM52 F9 |
| F11 | M23 compliance is 92% | **UNTRUSTABLE** — pre-commit hook rg invocation is broken, passes falsely | GLM52 F11 |
| F12 | Test suite times out (HIGH risk) | **PHANTOM** — never measured with adequate budget | GLM52 F12 |
| F16 | `model_validate_yaml()` exists | **WRONG** — doesn't exist in Pydantic v2 core. Use `yaml.safe_load()` + `model_validate()`. | GLM52 F16 |
| F17 | "Kill 2 of 3 distillers" | **MOSTLY DONE** — scribe distiller already deleted. miap.py still exists. | Ground truth grep |

**See**: `data/coordination/GLM52_SECOND_OPINION_20260730.md` for full evidence.

---

## §0 Executive Summary

**Goal**: Delete ~2,500 lines of custom code, adopt 2-3 community libraries, declare Hivemind "shipped."

The engine won't be less capable — it'll be **more maintainable**, **more reliable**, and **less tiring**.

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Circuit breaker implementations | 8 classes (2 enums + 1 canonical + 1 deprecated + 1 clone) | 1 canonical (`AsyncCircuitBreaker`) |
| Handoff schemas | 3 (HandoffPacket x2 + HandoffState) | 1 (HandoffPacket) |
| Soul distillers | Mostly deleted (scribe gone, miap.py pending) | 0 (all removed) |
| HMC Hub size | 86 lines (already consolidated) | YAML + JSONL, ≤100 lines/week |
| Memory tiers | 5 (Hot/Warm/Cold/Recall/Archival) | 3 (file-based, sqlite-vec+FTS5, raw archive) |
| Custom lines deleted | — | **-2,500+** |
| Community libraries adopted | — | **2-3** (structlog, prometheus_client, optionally stamina) |
| Pydantic simplification | Manual validator (290 lines) | Simplified with `yaml.safe_load()` + `model_validate()` |

---

## §1 Phase 0 — Pre-Flight (2h) — FIX GATES FIRST

| Task | Why | Effort |
|------|-----|--------|
| Fix M23 pre-commit hook rg invocation | Gate is theater (GLM52 F11) | 30min |
| Run `time make test` with 600s budget | Retire phantom risk (GLM52 F12) | 10min |
| Fix soul_validator.py vet-015 heritage tag | M14 compliance (GLM52 F9) | 15min |
| Verify MIAP status (deleted or dead code?) | Conflict resolution | 15min |
| Decide stamina vs tenacity (spike one provider) | Three positions exist (GLM52 F2) | 1h |

---

## §2 Phase 1 — Library Swaps (Revised — 8h, ~1,500 lines)

### §2.1 Delete Deprecated Breakers (NOT pybreaker swap)
**Status**: NOT STARTED
**Current**: `search_circuit_breaker.py` (299 lines, 4 classes — DEPRECATED per C-6')
**Action**: Delete `search_circuit_breaker.py`. Redirect callers to `get_breaker()` factory.
**Keep**: `AsyncCircuitBreaker` (health_monitor.py, 944 lines) — AnyIO-native, CUSUM, sliding window, 429 classification
**Do NOT**: Replace with pybreaker (sync-only, M1 violation — GLM52 F1)
**Effort**: 1h | **Net Δ**: -299 lines

### §2.2 Delete ExperimentCircuitBreaker
**Status**: NOT STARTED
**Current**: `sandbox.py ExperimentCircuitBreaker` (~50 lines)
**Action**: Redirect sandbox to `get_breaker()` factory
**Effort**: 30min | **Net Δ**: -50 lines

### §2.3 Simplify soul_validator.py
**Status**: NOT STARTED
**Current**: `src/omega/oracle/soul_validator.py` (290 lines)
**Action**: Remove manual REQUIRED_KEYS checks, keep `yaml.safe_load()` + pydantic `BaseModel`. Migrate vet-015 heritage tag.
**Do NOT**: Claim `model_validate_yaml()` exists (GLM52 F16 — it doesn't)
**Effort**: 2h | **Net Δ**: -150 lines

### §2.4 structlog — Replace Custom JSON Logger
**Status**: NOT STARTED
**Current**: Dead `setup_json_logging()` (M9 blocker)
**Action**: Replace with `structlog` (M8 compliant — local-only)
**Effort**: 2h | **Net Δ**: -80 lines

### §2.5 prometheus_client — Replace HealthMonitor Sliding Window
**Status**: NOT STARTED
**Current**: HealthMonitor sliding window (944 lines)
**Action**: Use `prometheus_client` v0.24.1 for Counter/Gauge/Histogram at `:8016/metrics`
**Effort**: 2h | **Net Δ**: -400 lines

### §2.6 stamina (DEFERRED — pending spike)
**Status**: DEFERRED
**Decision needed**: tenacity (already installed, 0 new deps) vs stamina (free structlog+prometheus instrumentation)
**Action**: Spike one provider, measure glue-code deletion, pick winner
**Effort**: 1h spike | **Net Δ**: TBD

---

## §3 Phase 2 — Kill Redundant Implementations (Revised — 8h, ~1,200 lines)

### §3.1 Kill HandoffState — Consolidate to HandoffPacket
**Status**: NOT STARTED
**Current**: 3 handoff schemas — `HandoffPacket` (x2: `mcp_coordinator.py`, `subagent_dispatcher.py`) + `HandoffState` (`handoff.py`)
**Heritage**: `handoff.py` has `[id-soft: vet-008]` — M14 migration required before deletion
**Action**: Delete `src/omega/oracle/handoff.py` (86 lines). Migrate vet-008 tag. Adapter MCP tools to HandoffPacket.
**Effort**: 2h | **Δ**: -86 lines

### §3.2 Soul Distiller Cleanup (MOSTLY DONE)
**Status**: ✅ Scribe distiller DELETED (commit 1c176b0)
**Remaining**: `miap.py` (631 lines) has distillation references — verify if MIAP is dead code or still imported
**Action**: If MIAP is dead code, delete it. If imported, add deprecation notice.
**Effort**: 1h | **Δ**: 0-631 lines (depending on MIAP status)

### §3.3 Kill HMC Hub → YAML + JSONL + Growth Gate
**Status**: PARTIAL — HMC already 86 lines
**Current**: `data/coordination/HMC_COLLABORATION_HUB.md` (86 lines)
**Action**: Create `hub_state.yaml` + `hub_log.jsonl`. Pre-commit gate: max 100 lines/week. TTL archival at 7 days.
**Effort**: 4h | **Δ**: -86 lines (minimal — already consolidated)

### §3.4 Kill recall.py
**Status**: NOT STARTED
**Current**: `src/omega/memory/recall.py` (786 lines) — Quality-weighted warm memory with power-law decay
**Action**: Verify no active consumers, then delete. Replace with FTS5 direct queries.
**Effort**: 1h | **Δ**: -786 lines

### §3.5 Deprecate MIAP + Link P9
**Status**: ⚠️ UNCLEAR — `miap.py` still exists on disk (631 lines), was supposed to be deleted
**Action**: Verify import graph. If no callers, delete. If callers exist, add deprecation notice.
**Effort**: 1h | **Δ**: 0-631 lines

---

## §4 Phase 3 — Simplify Memory Architecture (Revised — 4h, ~500 lines)

### §4.1 Kill Redundant Memory Tiers
| Kill | Why |
|------|-----|
| Recall tier (`recall.py`, 786 lines) | Duplicates FTS5 ranking with extra complexity |
| Warm tier (Redis) | ~8GB RAM too small; M7: RAM goes to inference |
| Archival tier (gzip) | Files ARE the archive. Extra compression wrapper = complexity. |
| Knowledge graph adapter | No active use case consuming graph queries |

**⚠️ Redis removal is deeper than Hivemind** (GLM52 F4):
- `memory_store.py` (9 refs) — RedisStorageProvider
- `budget_guard.py` (37 refs) — M12/M21 quota enforcement
- `youtube_worker.py` (24 refs) — worker queue
- `memory/providers.py` (21 refs) — vector adapters
- `hivemind_redis.py` (113 lines) — pub/sub

**Sequence**: memory providers → workers → hivemind → budget_guard LAST (budget_guard needs SQLite fallback first)

**Effort**: 4h | **Δ**: -500 lines

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

## §7 Implementation Sequence (Revised)

### Day 0 — Pre-Flight (FIX GATES FIRST)
| Priority | Work | Effort |
|----------|------|--------|
| P0 | Fix M23 pre-commit hook rg invocation | 30min |
| P0 | Run `time make test` with 600s budget | 10min |
| P0 | Fix soul_validator.py vet-015 heritage tag | 15min |
| P0 | Verify MIAP status | 15min |
| P0 | Spike stamina vs tenacity (one provider) | 1h |

### Day 1 — Phase 1 Start
| Priority | Work | Effort |
|----------|------|--------|
| P0 | Delete search_circuit_breaker.py + sandbox breaker | 1.5h |
| P0 | Simplify soul_validator.py | 2h |
| P0 | Install structlog + prometheus_client | 30min |

### Day 2 — Phase 1 Finish
| Priority | Work | Effort |
|----------|------|--------|
| P0 | structlog adoption | 2h |
| P0 | prometheus_client adoption | 2h |
| P0 | Retry strategy decision (stamina or tenacity) | 1h |

### Day 3 — Phase 2
| Priority | Work | Effort |
|----------|------|--------|
| P1 | Kill HandoffState (migrate vet-008) | 2h |
| P1 | Kill recall.py | 1h |
| P1 | Verify + kill MIAP | 1h |
| P1 | HMC → YAML + JSONL | 4h |

### Day 4 — Phase 3 + Phase 5
| Priority | Work | Effort |
|----------|------|--------|
| P1 | Memory tier consolidation (Redis removal sequence) | 4h |
| P2 | Enforcement gates (Phase 5) | 11h |

### Day 5 — Verify
| Priority | Work | Effort |
|----------|------|--------|
| P1 | `make test` + `make temple-grade` | 1.5h |

---

## §8 Success Criteria (Revised)

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Breaker classes | 8 (2 enums + 1 canonical + 1 deprecated + 1 clone) | 1 canonical (`AsyncCircuitBreaker`) |
| Handoff schemas | 3 | 1 (HandoffPacket) |
| Distillers | Mostly deleted (miap.py pending) | 0 |
| HMC Hub size | 86 lines | YAML + JSONL, ≤100 lines/week |
| Memory tiers | 5 | 3 |
| Recall tier | 786 lines | Deleted |
| Custom lines deleted | — | **-2,500+** |
| Community libraries adopted | — | **2-3** (structlog, prometheus_client, optionally stamina) |
| M23 gates | 2 false-PASS | Both fixed and trustworthy |
| Test suite timing | Unknown (phantom HIGH risk) | Measured and documented |

---

## §9 Sign-Off

| Role | Entity | Status |
|------|--------|--------|
| Plan Author | cline/omega-engine (DeepSeek) | ✅ Written |
| Strategy Review | grok/grok_cli | ⏳ Awaiting handoff completion |
| User Ratification | Architect (User) | ✅ RATIFIED 2026-07-30 |

---

*⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_unoverengineering ⬡ v1.0.0 ⬡ 2026-07-30*
