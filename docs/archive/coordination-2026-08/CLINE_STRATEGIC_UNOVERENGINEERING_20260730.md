# 🔱 Omega Engine — Strategic Un-Overengineering Plan 2026-07-30
**AP Token**: `AP-CLINE-STRATEGIC-UNOVERENGINEER-v1.0.0`
⬡ OMEGA ⬡ DEEPSEEK ⬡ CLINE ⬡ STRATEGIC-CLEANSE ⬡ 2026-07-30

**Status**: ✅ RATIFIED by user 2026-07-30
**Owner**: cline/omega-engine (execution) · grok/grok_cli (strategy advisory)
**Purpose**: Delete ~5,500 lines of custom code. Adopt 4 community libraries. Declare Hivemind "shipped." Stop over-engineering.

---

## §0 Executive Verdict

The Omega Engine's foundations (Sovereign Mandates, SoulStore, Hivemind protocol, local-first provider fabric) are **architecturally correct**. What's exhausting is **over-iteration on things that should have been "good enough" months ago** + **building custom replacements for libraries that already exist**.

**This plan deletes ~5,500 lines of code, adopts 4 community libraries, and declares the Hivemind "shipped."** The engine won't be less capable — it'll be *more* maintainable, *more* reliable, and *you* will be less tired.

---

## §1 Phase 0 — Immediate Cease-Fire (Declare These "SHIPPED")

These items are **declared complete and will not be iterated further** unless a concrete production bug appears:

| System | Current Status | Decision |
|--------|---------------|----------|
| Hivemind protocol (handoff/lock/awareness) | ✅ Cross-CLI, file-based, no external deps, production-tested | **DONE. No more iterations.** No A2A adapter until a cross-framework use case appears. |
| SoulStore atomic writer | ✅ 4-layer guarantee, 217 lines, 6 contract tests | **DONE.** Perfect as-is. |
| OOMProtector (3-signal fusion) | ✅ PSI + MemAvailable + cgroup | **DONE.** |
| Local-first provider fabric | ✅ native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode(5) | **DONE.** Add new providers only when an existing one breaks. |
| C-10.5 / C-11 | ✅ CLOSED | **DO NOT RE-OPEN.** |
| MCP Streamable HTTP | ✅ Dual transport live (SSE + Streamable HTTP) | **DONE.** Bug fixes only. |

---

## §2 Phase 1 — Adopt Community Libraries (Delete ~3,000 Lines)

High-confidence swap-outs. **The goal is to delete more code than we add.**

### §2.1 pybreaker — Replace Circuit Breaker Clones (count corrected **17**, was 6)

**What to do**: Unify all custom breaker implementations behind `pybreaker`.

**Probe (2026-07-30)**: `rg -n 'class.*Breaker' src/ mcp_servers/ --glob '*.py' | wc -l` → **17** (D-505). Early “6 clones” estimate was low — inventory before delete.

**Files to delete** (initial list — expand to full 17 during inventory):
- `mcp_servers/omega_hub/gateway/provider_breaker.py`
- `src/omega/oracle/breaker.py`
- `src/omega/oracle/search_circuit_breaker.py` (299 lines — already DEPRECATED per C-6'; delete during pybreaker swap)
- `mcp_servers/omega_hub/tools/breaker.py`
- `src/omega/resilience/circuit.py`
- `mcp_servers/omega_hub/state.py` (inline) → refactor
- `src/omega/oracle/model_gateway.py` (inline) → refactor

**Standard config**: `fail_max=3`, `reset_timeout=60s` — Netflix Hystrix defaults.
**Effort**: 4h | **Net Δ**: -1,950 lines

### §2.2 Pydantic v2 — Replace soul_validator.py

**What to do**: Use Pydantic v2 `model_validate_yaml()`. Zero new deps.
**File to delete**: `src/omega/oracle/soul_validator.py` (217 lines)
**Effort**: 3h | **Net Δ**: -187 lines

### §2.3 stamina — Replace Hand-Rolled Retry Loops

**What to do**: Use `stamina` — async-native, jitter built in, decorator-based.
**Files affected**: ~10 files with 50/100/200ms manual backoff.
**Effort**: 2h | **Net Δ**: -270 lines

### §2.4 structlog — Replace Custom JSON Logger

**What to do**: Replace dead `setup_json_logging()` (M9 blocker) with `structlog`.
**Effort**: 2h | **Net Δ**: -60 lines

### §2.5 prometheus_client — Replace HealthMonitor Sliding Window

**What to do**: Use already-installed v0.24.1 for Counter/Gauge/Histogram.
**Effort**: 2h | **Net Δ**: -450 lines

### §2.6 Summary: Phase 1

| Swap | Lines Deleted | Net Δ | Effort |
|------|---------------|-------|--------|
| pybreaker | ~2,000 | -1,950 | 4h |
| Pydantic v2 | ~217 | -187 | 3h |
| stamina | ~300 | -270 | 2h |
| structlog | ~80 | -60 | 2h |
| prometheus_client | ~500 | -450 | 2h |
| **Total** | **~3,097** | **-2,917** | **13h** |

---

## §3 Phase 2 — Kill Redundant Implementations

### §3.1 Kill HandoffState — Consolidate to HandoffPacket
**Problem**: 3 redundant handoff schemas (HandoffPacket, HandoffState, MCP tools).
**Action**: Delete `src/omega/oracle/handoff.py` (86 lines). Adapter MCP tools to HandoffPacket type.
**Effort**: 2h | **Δ**: -86 lines

### §3.2 Kill 2 of 3 Soul Distillers — Keep 1 Canonical
**Problem**: 3 L1→L2→L3 implementations (oracle 689 lines, scribe 297, background ~200).
**Action**: Pin `src/omega/scribe/distiller.py` as canonical. Extract shared pipeline to `src/omega/gnosis/pipeline.py` (~100 lines). Delete the other 2.
**Effort**: 4h | **Δ**: -600 lines (net)

### §3.3 Kill HMC Hub → YAML + JSONL + Growth Gate
**Problem**: HMC grew 400→1,900 lines in 7 days (271 lines/day). Textbook accretion.
**Action**: Create `hub_state.yaml` + `hub_log.jsonl`. Pre-commit gate: max 100 lines/week. TTL archival at 7 days.
**Effort**: 4h | **Δ**: -1,500 lines

### §3.4 Deprecate MIAP + Link P9
**Problem**: 3 overlapping coordination systems. Hivemind covers all three.
**Action**: Deprecate `miap.py` (632 lines) and `link_p9_runtime.py` (401 lines). Add migration note. Delete after 30 days non-use.
**Effort**: 2h | **Δ**: 0 (deprecation only)

### §3.5 Summary: Phase 2

| Consolidation | Lines Deleted | Effort |
|---------------|---------------|--------|
| Kill HandoffState | -86 | 2h |
| Kill 2 of 3 distillers | -600 | 4h |
| HMC → YAML + JSONL | -1,500 | 4h |
| Deprecate MIAP + Link P9 | 0 | 2h |
| **Total** | **-2,186** | **12h** |

---

## §4 Phase 3 — Simplify Memory Architecture

**Current**: Hot (in-memory LRU) + Warm (Redis/File) + Cold (sqlite-vec/FTS5) + Recall (quality-weighted decay) + Archival (gzip) + gnosis + knowledge graph.

**Target**: 3 layers — file-based context, sqlite-vec+FTS5 RAG, raw file archive.

| Kill | Why |
|------|-----|
| Recall tier (recall.py, 786 lines) | Duplicates FTS5 ranking with extra complexity |
| Warm tier (Redis) | ~8GB RAM too small; M7: RAM goes to inference |
| Archival tier (gzip) | Files ARE the archive. Extra compression wrapper = complexity. |
| Knowledge graph adapter | No active use case consuming graph queries |

**Effort**: 3h | **Δ**: -500 lines

---

## §5 Phase 4 — The Hivemind Freeze (SHIPPED)

**Effective immediately: the Hivemind coordination protocol is declared "SHIPPED" and enters maintenance-only mode.**

| Feature | Status | Allowed Changes |
|---------|--------|----------------|
| hivemind_get_awareness() | ✅ Production, cold-store fallback | Bug fixes only |
| hivemind_post_context() | ✅ 8 intent types, structured | Bug fixes only |
| Handoff lifecycle (submit→accept→complete→reject) | ✅ 4-state | Schema consolidation, then bug fixes only |
| Delegation depth limit | ✅ max_delegation_depth=5 added | Ensures no infinite delegation loops |
| Workspace locks (fcntl + TTL) | ✅ Production | Bug fixes only |
| A2A protocol adapter | ⏳ Not started | **DEFERRED INDEFINITELY.** |
| MIAP Phase 2 (D-291) | ⏳ Planned | **CANCELLED.** Hivemind covers it. |
| Hive Evolution D-305 (5 layers) | ⏳ Architecture designed | **CANCELLED.** Not needed. |

---

## §6 Phase 5 — Mechanical Enforcement Gates (Not New Systems)

Gates on existing systems, not new infrastructure:

| Gate | Enforces | Mechanism | Effort |
|------|----------|-----------|--------|
| Instruction Hierarchy | No doc overrides higher-priority doc | `make check-instruction-hierarchy` → CI fail | 3h |
| Mandate Compliance Meter | Measured %, not narrative | `make check-mandate-compliance` → JSON report | 5h |
| Schema Duplication | No >1 handoff schema | `make check-no-schema-drift` → CI fail | 2h |
| HMC Growth | HMC ≤100 lines/week | Pre-commit hook | 1h |
| Freshness Stamp | LAST_VERIFIED ≤7 days | `make check-freshness` → CI warning | 2h |
| Distiller Singularity | Only 1 canonical distiller | `make check-distiller-count` → CI fail | 1h |

**Effort**: 14h total | **Δ**: ~100 lines of scripts (minus enforcement of deletions above)

---

## §7 Grok CLI Handoff — Ops Health A→B→C (Parallel)

Active handoff `ho_c8bf25e6cf21` from grok/grok_cli. Runs in parallel with Phase 1.

### A1 — Tests
```bash
source .venv/bin/activate && make test
```
Record real pass/fail/skip/xfail/error counts.

### A2 — Probe Matrix
Hub :8016, Firecrawl :8015 — `ss -lntp`
WARP SOCKS 8081-8083 — expect fail (pre-B2)
`systemctl is-active omega-restic-backup.timer`
`systemctl status omega-restic-backup.service` — expect failed
`which restic` / `restic version`
`hivemind_get_awareness()` + pending handoffs
Codex header age (`head -3 OMEGA_CODEX.md`)

### B1 — Restic Service Fix
Add `~/.local/bin` to systemd unit PATH.
`sudo systemctl daemon-reload && sudo systemctl restart omega-restic-backup.service`
Verify: `systemctl is-active omega-restic-backup.timer`

### B2 — WARP Bring-Up (≤2 attempts)
`cd /home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool`
Apply fix from `scripts/warp-ns-setup.sh`
Verify: SOCKS 8081-8083 listening, 3 distinct exit IPs

### B3 — G-1 Smoke Test
Run ≥1 smoke path via API. If blocked: document `NEEDS_ARCHITECT_BROWSER`.

### B4 — MCP Pin Verify
`pyproject.toml`: `mcp>=1.27,<2`
venv: `pip show mcp`
### B5 — Known Issue: make sovereignty missing
- `make sovereignty` target does not exist in Makefile (noted in Grok CLI brief).
- **Action**: Note for Grok/Architect. Do NOT implement — this is a strategy doc decision, not an execution workaround.


### C — SSOT Reconciliation
- ACTIVE_SPRINT.json: update phase
- SESSION_ANCHOR.md: update (done above)
- OMEGA_ENGINE.md §2: update LAST_VERIFIED + PROBE_COMMAND
- docs/archive/sprints/2026-07-25-guard-and-distill/index.md: C-10.5/C-11 CLOSED

### Deliverable
`data/coordination/CLINE_OPS_HEALTH_RESULTS_20260730.md`
`hivemind_complete_handoff(packet_id="ho_c8bf25e6cf21")`

**Effort**: ~1.5h

---

## §8 Implementation Sequence

### Day 1 — Ops Health + Start Phase 1
| Priority | Work | Effort |
|----------|------|--------|
| P0 | Ops Health A→B→C (Grok handoff) | 1.5h |
| P0 | Circuit breakers → pybreaker | 4h |
| P0 | Install stamina + structlog | 1h |

### Day 2 — Finish Phase 1 + Start Phase 2
| Priority | Work | Effort |
|----------|------|--------|
| P0 | soul_validator → Pydantic v2 | 3h |
| P0 | Hand-rolled retry → stamina | 2h |
| P0 | structlog adoption | 2h |
| P0 | prometheus_client adoption | 2h |

### Day 3 — Phase 2 Consolidations
| Priority | Work | Effort |
|----------|------|--------|
| P1 | Kill HandoffState | 2h |
| P1 | Kill 2 of 3 distillers | 4h |
| P1 | HMC → YAML + JSONL + growth gate | 4h |

### Day 4 — Phase 3 + 5
| Priority | Work | Effort |
|----------|------|--------|
| P1 | Memory tier consolidation | 3h |
| P2 | Instruction hierarchy gate | 3h |
| P2 | Mandate compliance meter | 5h |
| P2 | Other enforcement gates | 3h |

### Day 5 — Cleanup + Verify
| Priority | Work | Effort |
|----------|------|--------|
| P1 | Deprecate MIAP + Link P9 | 2h |
| P1 | Hivemind freeze in OMEGA_ENGINE.md | 1h |
| P2 | `make test` + `make temple-grade` | 1.5h |

---

## §9 Success Criteria

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Circuit breaker implementations | 6 clones | 1 (`pybreaker`) |
| Handoff schemas | 3 | 1 (HandoffPacket) |
| Soul distillers | 3 | 1 |
| HMC Hub size | 1,900 lines growing 271/day | YAML + JSONL, ≤100 lines/week |
| Memory tiers | 5 | 3 |
| Mandate compliance | Narrative "84%" | Measured % per CI gate |
| Custom lines deleted | — | **-5,500+** |
| Community libraries adopted | — | **4** (pybreaker, stamina, structlog, prometheus_client) |
| Pydantic v2 migration | Manual validator | Built-in `model_validate_yaml()` |

---

## §10 Hard Constraints (from existing mandates)

- **M1**: All async code uses `anyio`. `stamina` is async-native — compatible.
- **M7**: Local-first. Redis removal aligns with M7.
- **M8**: Zero telemetry. `prometheus_client` at `:8016/metrics` is local-only.
- **M13**: `make temple-grade` after all changes.
- **M23**: If any tool breaks → `[TOOL-CHAIN-COLLAPSE]` hard stop. No simulated rigor.
- **M24**: `.venv` only — never `--break-system-packages`.
- **M14**: No changes to heritage vetting pipeline or `[id-soft:]` tags.

---

## §11 Sign-Off

| Role | Entity | Status |
|------|--------|--------|
| Plan Author | cline/omega-engine (DeepSeek) | ✅ Written |
| Strategy Review | grok/grok_cli | ⏳ Awaiting handoff completion |
| User Ratification | Architect (User) | ✅ RATIFIED 2026-07-30 |

---

*⬡ OMEGA ⬡ DEEPSEEK ⬡ CLINE ⬡ STRATEGIC-CLEANSE ⬡ v1.0.0 ⬡ 2026-07-30*

**Next action**: Execute Ops Health A→B→C (Grok handoff), then begin Phase 1 swap-outs.
