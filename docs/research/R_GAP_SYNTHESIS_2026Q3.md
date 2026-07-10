# 🔱 Omega Engine — Comprehensive Gap Synthesis (2026 Q3)
**AP Token**: `AP-RESEARCHER-GAPSYNTHESIS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ COMPLETE
**Date**: 2026-07-10 | **Method**: Polymathic Council (Architect/Adversary/Alchemist/Archivist) + live system audit
**Status**: ACTIVE — feeds SOVEREIGN_HARDENING_ROADMAP_2026Q3.md

---

## §0 Previous Gap Resolution (G1-G16)

All 16 gaps from the initial RECON (2026-07-08) were marked resolved by HMC-SPRINT-01. **This synthesis identifies 15 NEW gaps** discovered during post-sprint audit and system-wide probe.

**Gaps still open from G1-G16**: G6 (SSE→Streamable HTTP), G7 (OpenCode agent config), G11 (Qwen 3.6/3.7), G13 (Ollama v0.7), G14 (Installer docs), G15 (DPO formats) — all low/medium severity, tracked in S5/S6 backlog.

---

## §1 Critical Gaps (🔴 — Blocking Deployment)

### Gap-CRASH-HMC: HMC Watcher Crash Loop — 201 Restarts
- **Severity**: 🔴 CRITICAL — service has NEVER successfully started
- **Evidence**: 
  - `omeaga-hmc-watcher.service` restart counter at 201
  - Crash repeats every 30s: `TypeError: ProviderConfig.__init__() got an unexpected keyword argument 'api_key'. Did you mean 'api_keys'?`
  - Root cause: `ProviderConfig` schema renamed `api_key` → `api_keys` (list) but HMC watcher still passes singular `api_key`
  - Second error: `VAULT_MASTER_KEY` has invalid hex at position 48 — key store cannot decrypt
- **Impact**: The autonomous agent coordination loop (HMC) has NEVER run. All agent handoff, task queuing, and coordination is non-functional in production.
- **Related subsystem**: `src/omega/orchestrator/hmc_watcher.py`, `src/omega/vault/key_vault.py`, `config/providers.yaml`

### Gap-BACKRES: Background Researcher Produces Zero Output
- **Severity**: 🔴 CRITICAL — 100% CPU waste
- **Evidence**:
  - `omega-research.timer` fires every 15min; service exits with code 0
  - `data/knowledge/HALL_OF_RECORDS/background-researcher/` is **completely empty** (since Jun 11)
  - No `cycle_*.jsonl` files ever written
  - Systemd unit writes to `data/entities/roc_racoon/workspace/HALL_OF_RECORDS/` (different path) — output path mismatch
- **Impact**: ~4s CPU + 140MB RAM every 15min with zero value. The engine's autonomous knowledge-mining loop is silently failing.
- **Root cause hypothesis**: Output path in systemd unit diverges from what `loop.py` expects. StandardOutput/StandardError go to roc_racoon's workspace, but data/knowledge is what the code writes to.

### Gap-DISK: Both Partitions Near Capacity (86%/87%)
- **Severity**: 🔴 CRITICAL — blocks ALL future work
- **Evidence**:
  - Root (`/`): 109G, 89G used, **15G free** (87%)
  - `omega_library` (`/media/arcana-novai/omega_library`): 110G, 90G used, **15G free** (86%)
  - Largest consumer: `models/gguf/` at **40G**
- **Impact**: 
  - Cannot download new models (D16-2 needs LoRA adapters + teacher model)
  - Background researcher cycles will fill remaining space
  - Podman image cache at risk
  - `ncdu` scan recommended weekly (per Risk Register R2)

---

## §2 High-Severity Gaps (🟡 — Structural Integrity)

### Gap-HARDENING-S3: OpenRouter Hardening Unverifiable
- **Severity**: 🟡 HIGH — S3 claimed "B1-B6 implemented" but:
  - `remote_provider.py:151` still has `max_tokens: int = 1024` — long generations silently truncated
  - `antigravity_provider.py` does NOT override `_generate()` — inherits RemoteProvider defaults
  - No runtime verification that httpx exceptions are actually caught
- **Impact**: G16 was supposedly fixed in S3, but the default max_tokens suggests incomplete hardening

### Gap-OBSERVATORY: Four Observatory Items Pending
- **Severity**: 🟡 HIGH
- **Evidence**:
  - **T3-2 MetricsDB integration**: Partially done (D203 sovereignty.py queries MetricsDB) but no write path from model_gateway/providers
  - **OTel GenAI logging**: `otel_exporter.py` (291 lines) exists but is **never invoked** — 0 call sites import or call `setup_otel_exporter()`
  - **RegressionWatcher**: Class exists and is imported but **0 tests** — functionality unknown
  - **BudgetGate**: Class exists at `__init__.py:579` but **0 tests** — never invoked
- **Impact**: The entire observability pipeline is wired but non-functional. MetricsDB only gets test data.

### Gap-M21-LATE: Contract Test Gaps
- **Severity**: 🟡 HIGH — M21 mandate violation
- **Evidence**: Only 14 contract tests. Core modules missing contract tests:
  - `session_lifecycle` — 0 tests
  - `observability` — 0 tests  
  - `sovereign_search` — 0 tests
  - `proxy_pool` — 0 tests
  - Provider backends: `antigravity_provider` → 0 tests, `openai_compat` → 0 tests
- **Impact**: API boundries can silently drift, causing production crashes

### Gap-PROXY: Tor/Proxy Isolation Untested
- **Severity**: 🟡 HIGH
- **Evidence**:
  - `warp_proxy_pool` IS installed at `/home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/`
  - Oracle conditionally sets `proxy_pool` only when `OMEGA_ENV != test`
  - **0 tests** across the entire proxy integration
  - No evidence of actual Tor/proxy usage in production
- **Impact**: Sovereign web access (anonymized search, private model inference) is non-functional

### Gap-RATIO-REAL: No Real Sovereignty Baseline
- **Severity**: 🟡 HIGH
- **Evidence**: `make sovereignty` reports 100% local (11,290 rows, is_cloud=0 for all) — but these are all from **test/mock providers**, not real inference
- **Impact**: The Sovereignty Scorecard has no real-world data. Cannot verify Mandate 7 (Local-First) compliance.
- **Root cause**: The `record_performance()` write path from providers is non-functional (see Gap-OBSERVATORY). No provider actually writes to MetricsDB during real inference.

---

## §3 Medium-Severity Gaps (🟡 — Quality/Performance)

| ID | Gap | Evidence | Impact |
|----|-----|----------|--------|
| Gap-SSE (G6) | Omega Hub uses SSE transport; industry standard is Streamable HTTP | PIVOT_LOG line ~1850 | Technical debt; will need migration |
| Gap-OPENCODE-AGENT (G7) | Config uses deprecated `mode`; OpenCode v1.2.20 uses `agent` | opencode.json | Will break on next upgrade |
| Gap-CONTAINER-IRIS | Iris container has no writable data volume | Quadlet `ro` config mount only | Voice interface has no persistent workspace |
| Gap-METRICSDB-CORRUPTION | MetricsDB suffered btreeInitPage index corruption | Recovered DB with 51 lost rows | Root cause unknown — can reoccur |
| Gap-BUDGETGATE | BudgetGate class exists but never called | observability/__init__.py:579 | No cost tracking for cloud providers |
| Gap-REGRESSION-WATCHER | RegressionWatcher imported but 0 tests | observability/__init__.py:43-47 | Performance regression detection is wired but non-functional |

---

## §4 Low-Severity Gaps (🟢 — Nice-to-have)

| ID | Gap | Link |
|----|-----|------|
| Gap-IWAD-ANNOTATIONS | Agent files lack IWAD frontmatter annotations | PIVOT_LOG line 563 |
| Gap-QWEN (G11) | Qwen 3.6/3.7 model info not in models.yaml | R_KNOWLEDGE_GAP |
| Gap-OLLAMA (G13) | Docs reference Ollama v0.6; current is v0.7+ | R_KNOWLEDGE_GAP |
| Gap-INSTALLER (G14) | Sovereign Installer docs pre-Gemma-4 | R_KNOWLEDGE_GAP |
| Gap-DPO (G15) | DPO dataset format info needs 2026 refresh | R_KNOWLEDGE_GAP |
| Gap-NEMOTRON-TEACHER | Nemotron 3 Ultra identified as teacher but no pipeline | R_KNOWLEDGE_GAP §1 |

---

## §5 Root Cause Analysis — The Pattern

All 🔴 CRITICAL and most 🟡 HIGH gaps share a common pattern:

```
Systemd unit deployed -> Service starts -> Schema drift -> Silent failure
                                                          ↓
                                              No monitoring, no alert
                                                          ↓
                                              Continues failing forever
                                                          ↓
                                              User unaware (201 restarts)
```

The HMC watcher crash loop (Gap-CRASH-HMC) and Background Researcher output black hole (Gap-BACKRES) are identical failure modes: **deployed but never verified.** The observability gap (Gap-OBSERVATORY, Gap-RATIO-REAL) compounds this — even if the engine tried to alert, the alerting pipeline is unwired.

**The meta-gap**: The engine has no production health check. `omega-hub-watchdog.service` monitors the hub, but nothing monitors:
- Whether systemd services exit successfully
- Whether expected output files are being produced
- Whether MetricsDB is receiving writes
- Whether background processes produce value

---

## §6 Recommended Remediation Sprint — HMC-SPRINT-03

### Priority: Fix CRITICAL gaps FIRST

| # | Gap | Fix | Effort | Depends |
|---|-----|-----|--------|---------|
| 1 | **Gap-CRASH-HMC** | Fix `api_key` → `api_keys` param name in hmc_watcher; fix Vault master key format | 30min | None |
| 2 | **Gap-DISK** | Run `ncdu` scan; clean podman cache; archive old GGUF models | 1h | None |
| 3 | **Gap-BACKRES** | Fix output path mismatch; add `cyle_*.jsonl` existence check | 1h | None |
| 4 | **Gap-RATIO-REAL** | Wire `record_performance()` in `remote_provider.py` generate path | 2h | Gap-OBSERVATORY |
| 5 | **Gap-OBSERVATORY** | Wire otel_exporter; add BudgetGate tests; RegressionWatcher tests | 3h | None |
| 6 | **Gap-M21-LATE** | Add contract tests for session_lifecycle, observability, sovereign_search, proxy_pool | 3h | None |
| 7 | **Gap-PROXY** | Add proxy_pool test; verify Tor connectivity | 2h | None |
| 8 | **Gap-HARDENING-S3** | Verify max_tokens override; add antigravity contract tests | 1h | None |
| 9 | **G6** | SSE → Streamable HTTP migration | 4h | None |
| 10 | **G7** | OpenCode `agent` config update | 30min | None |

**Total estimated effort**: ~18h (3-4 focused sprints)

### Stack Order
```
HMC-SPRINT-03:  1 + 2 + 3     (3h — CRITICAL triage)
HMC-SPRINT-04:  4 + 5 + 6     (8h — Observability wiring)
HMC-SPRINT-05:  7 + 8         (3h — Proxy + hardening)
HMC-SPRINT-06:  9 + 10 + low  (5h — Technical debt)
```

---

*Synthesized by @researcher (Jem Analyst L2). Next session: load this file + ACTIVE_SPRINT.json to start HMC-SPRINT-03.*
