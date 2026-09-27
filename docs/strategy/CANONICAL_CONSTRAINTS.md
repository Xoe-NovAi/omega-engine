# 🔱 CANONICAL CONSTRAINTS — Hard Constraints (Mandates, Hardware, Budget, Law)
**AP Token**: `AP-CANONICAL-CONSTRAINTS-20260829-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem-2.0 ⬡ opencode ⬡ trc_canonical_constraints ⬡ ACTIVE

**Date**: 2026-08-29
**Status**: CANONICAL — Consolidated from `SOVEREIGN_MANDATES.md` (27 laws, v3.8.0) + `MANDATES_CONDENSED.md` + `ACTIVE_SPRINT.json` + `CLINE_FULL_REVIEW_ROLLUP_20260828.md` + `CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` + `VISION_ANCHOR_PERPETUAL.md` + `MODEL_WINDOW_ECONOMICS_20260823.md` + `DEBUT_REMEDIATION_MANUAL_20260817.md`

---

## ⚖️ TIER 0: SOVEREIGN MANDATES (27 Laws, v3.8.0) — NON-NEGOTIABLE

*Source: `SOVEREIGN_MANDATES.md` + `MANDATES_CONDENSED.md` (Tier-0 injection pre-compaction)*

| Mandate | Title | One-Line Enforcement | Gate |
|---------|-------|---------------------|------|
| **M1** | AnyIO | Never `import asyncio` in `src/omega/` | `make check-m1-anyio` |
| **M2** | Engine-Stack Firewall | `src/omega/` = Core; `config/wads/` = Stacks | `FirewallChecker.scan()` = 0 |
| **M3** | (Reserved) | — | — |
| **M4** | No Cowboy Sed | No mass `sed` across repo; surgical edits only | PR review |
| **M5** | Gnosis Preservation | Every session distills L1→L2→L3 to `proposed_lessons.yaml` | `session_end.py` hook |
| **M6** | (Reserved) | — | — |
| **M7** | Local-First | Local inference primary; cloud fallback only | Provider chain order (0,1,2 local) |
| **M8** | Zero Telemetry | No external analytics; local observability in `data/` | `make check-m8-zero-telemetry` |
| **M9** | Error Integrity | No bare `except:` in core | `make check-m9-error-integrity` |
| **M10** | Fleet Cap | Max 14 agents (`.opencode/agents/`) | `ls .opencode/agents/` ≤ 14 |
| **M11** | Soul Integrity | Every session ends with L1→L3 distillation | Scribe pipeline |
| **M12** | (Reserved) | — | — |
| **M13** | Temple-Grade | `make temple-grade` exits 0 before any release | CI gate |
| **M14** | Heritage | Every `[id-soft:]` tag has vet record ≥7/10 with scope | `make heritage-vet` |
| **M15** | Sovereign Continuity | Maintain `session_gnosis.md` for context loss | Hivemind continuation |
| **M16** | (Reserved) | — | — |
| **M17** | (Reserved) | — | — |
| **M18** | (Reserved) | — | — |
| **M19** | (Reserved) | — | — |
| **M20** | (Reserved) | — | — |
| **M21** | Gate Integrity | Contract test file exists for every gate | `make check-m21-gate-integrity` |
| **M22** | Response Provenance | `GenerateResult.provider_name` = ACTUAL provider | Fabric wiring |
| **M23** | Failure Integrity | Broken tools → `[TOOL-CHAIN-COLLAPSE]`; no synthesis | Hard-stop on tool failure |
| **M24** | Venv Sovereignty | All Python in `.venv/`; no `--break-system-packages` | `pip install -e .` |
| **M25** | Streaming Resilience | Chunk/total timeouts + fallback on timeout | Provider config |
| **M26** | Doc Standards | Reference docs pass `make doc-llm-validate` | CI gate |
| **M27** | Tracking Integrity | State follows 5-Tier Tracking Architecture | `TRACKING_ARCHITECTURE.md` |

### Tier-0 Injection (Pre-Compaction Survival)
These 5 mandates are injected pre-compaction so the law survives context loss:
- **M1 AnyIO** — never `import asyncio` in `src/omega/`
- **M7 Local-First** — local inference primary, cloud fallback only
- **M11 Soul Integrity** — every session ends with L1→L3 distillation
- **M15 Sovereign Continuity** — maintain `session_gnosis.md` for context loss
- **M23 Failure Integrity** — broken tools → STOP, report; no soft-failures

---

## 🖥️ HARDWARE CONSTRAINTS (Physical Reality)

| Constraint | Value | Source | Implication |
|------------|-------|--------|-------------|
| **CPU** | Ryzen 7 5700U (8C/16T, Zen 2) | `config/hardware_profile.yaml` | No AVX-512; Vulkan target for llama.cpp |
| **RAM** | 16GB DDR4 (shared with iGPU) | `config/hardware_profile.yaml` | cgroup MemoryMax=6G for engine; 10GB for OS/models |
| **NVMe** | 512GB (OS + active models + swap) | `config/hardware_profile.yaml` | `omega_library` partition for active GGUF |
| **HDD** | 8TB (model cache, datasets) | `config/hardware_profile.yaml` | `~/OmegaLibrary/hf_cache/hub` — sequential only (~150MB/s) |
| **iGPU** | Radeon Vega 7 (7 CUs) | `config/hardware_profile.yaml` | `GGML_VULKAN=ON` for llama.cpp; 8-15 tok/s on 7B Q4 |
| **zswap** | 16GB NVMe swap, 25% pool, lzo_rle, zsmalloc | D-526/D-527/D-584 | zRAM DISABLED; swappiness=100; cgroup MemoryMax=6G |
| **Podman** | Rootless quadlets (native-gguf, Qdrant) | `POST_DEBUT_ROADMAP.md` | Qdrant: v1.18.1, telemetry disabled, 6G MemoryLimit, 80% CPUQuota, gRPC pool=20 |

### Model Storage Architecture (M7 + HF Integration)

| Tier | Location | Purpose | Access Pattern |
|------|----------|---------|----------------|
| **HF Cache** | `~/OmegaLibrary/hf_cache/hub` (HDD) | Model weight blobs, large datasets | Sequential only |
| **HF Metadata** | `~/.cache/huggingface` (NVMe) | Tokens, config, small metadata | Random |
| **Active Models** | `omega_library` (NVMe) | GGUF/safetensors for inference | Random (copy from HDD before use) |
| **Datasets** | `~/OmegaLibrary/hf_cache/datasets` (HDD) | Parquet files | Sequential |

**Rule**: Never download directly to HDD for active use — always `hf download` to cache, then copy to `omega_library` for inference.

---

## 💰 BUDGET CONSTRAINTS (Model Fleet Economics)

### Current Fleet (Carmack Option E — Awaiting Architect Sign-Off)

| Account | Model | Role | Cost/1K req | Monthly @ 100K req/day |
|---------|-------|------|-------------|------------------------|
| 1-3 | M3:free (`minimax/minimax-m3:free`) | Long-write workhorse | $0.00 | $0 |
| 4-7 | DeepSeek V4 Flash 0731 (`deepseek/deepseek-v4-flash-0731`) | Bulk coding | $0.069 | ~$207 |
| 8 | GPT 5.6 Sol (`openai/gpt-5.6-sol`) | Newer family probe | ~$1.80 (est) | ~$5,400 |

**Total**: ~$5,600/mo at 100K req/day (dominated by GPT 5.6 Sol probe)

### Cost Laws (D-601 Model Window Economics)

| Law | Constraint |
|-----|------------|
| **LAW 3** | Cheap Prime, Expensive Cognate — Tool calls on cheap models; reasoning on expensive |
| **LAW 5** | Family Diversity Weights — Different family > same family/newer version > same weights |
| **Nemotron True Cost** | $0.00 (zero cost-bearing messages ever) — 611 sessions / 35,111 messages |

### Rate Limits (Hard Constraints)

| Provider | Limit | Scope | Notes |
|----------|-------|-------|-------|
| **OpenAI API** | Tier 1: 500 RPM / 500K TPM | Per ORG (shared across keys) | 8 accounts on 1 ORG = no multiplication |
| **OpenRouter** | Per-key generous | Per API key | 8 keys = 8× rate |
| **ChatGPT Plus** | 5h Codex windows | Per subscription | 8 accounts = 8× $20/mo = $160/mo |
| **ChatGPT Pro** | Generous | Per subscription | 8 accounts = 8× $200/mo = $1,600/mo |
| **DeepSeek V4 Flash** | 2,500 concurrent/account | Per account | 8 accounts = 20,000 concurrent |
| **M3:free** | 50 RPD/account | Per account | 3 accounts = 150 RPD headroom |

---

## 🏗️ ARCHITECTURAL CONSTRAINTS (Structural Debt Gates)

### God-Module Freeze (Gate §9 — from Grok CLI + Carmack)

| Module | Lines | Constraint |
|--------|-------|------------|
| `observability/__init__.py` | 1660 | Split by concern |
| `oracle/model_gateway.py` | 1582 | **ATOMIC SPLIT REQUIRED (D-551)** — ProviderSelector + ModelGateway |
| `oracle/oracle.py` | 1459 | Split: IntentDetection + EntityRouting + ProviderSelection |
| `oracle/providers.py` | 1303 | Split: ProviderRegistry + CapabilityMatrix |
| `workers/youtube_worker.py` | 1253 | Extract to stack (config/wads/) |
| `cli/oracle_cli.py` | 1234 | **P1-1 logger landmine** — logger at L106, used at L80/85 |
| `memory_store.py` | 1224 | Split: HybridSearch + Collections + SoulOps |
| `benchmarks/comprehensive_runner.py` | 1213 | Move to stack |
| `memory/sqlite_vec_adapter.py` | 1031 | Keep (IVectorStoreAdapter impl) |
| `oracle/sovereign_search_service.py` | 1026 | Split: SearchService + TriangulationVerifier |
| `entity_registry.py` | 1017 | Split: Registry + LockManager |

**Rule**: No new code pushed into god-modules >1000 lines without a split (D-551: atomic split in DEL-1 Week 2 with contract tests).

### Circuit Breaker Unification (C-6′)

- **Canonical**: `HealthMonitor` factory only
- **Deprecated**: 5/7 legacy clones deprecated; 2 unmigrated (P-5 ticket open)
- **Rejected**: `pybreaker` port — use HealthMonitor
- **Rule**: No new breaker classes added

### Test Honesty (C-0)

- **96 failures triaged**: Class A (~20 real bugs), Class B (~50 test/code drift), Class C (~26 integration)
- **Full suite never green on CI**: `test.yml` not on `release/debut`; `verify-mining` target missing
- **Compliance meter broken (P0-1)**: `check_mandate_compliance.py` calls `python` (not `python3`); meter excluded from all green gates

### M1 AnyIO Loophole (P2-4)

- `tty_agent.py:32` has `import asyncio` — exempted by Makefile comment
- `governance/` directory exempted — **no D-number in PIVOT_LOG**

---

## 📦 RELEASE CONSTRAINTS (Debut Mechanics)

| Constraint | Rule | Source |
|------------|------|--------|
| **Publication Mechanic** | `release/debut` branch from `PUBLIC_ALLOWLIST.txt` | D-553 |
| **Vault in Debut** | Excluded via allowlist; zero code changes | D-565/D-566 |
| **CP-3 Claim** | Only true after INST-1 passes on machine without warp-proxy-pool | D-539 |
| **Test Baseline** | Full pytest 0 failures before DEL-1 Week 1 | D-550 |
| **Temple-Grade** | `make temple-grade` exits 0 before release | M13 |
| **Heritage** | All `[id-soft:]` tags vetted ≥7/10 | M14 |
| **Doc Standards** | Reference docs pass `make doc-llm-validate` | M26 |
| **No `git add -A`** | Path-stage every commit; secrets re-commit risk | DEBUT_REMEDIATION_MANUAL |
| **No filter-repo + 2000-doc PR same week** | Scrub first, then delete | DEBUT_REMEDIATION_MANUAL |

---

## 🔬 RESEARCH CONSTRAINTS (Methodology)

| Constraint | Rule | Source |
|------------|------|--------|
| **FTS5-First (C-MEM-004)** | Never linear Python scans for doc search; query FTS5 first, hydrate by doc IDs | Researcher mandate |
| **Gnosis Hygiene (C-MEM-005)** | Auto-distillation runs pruning + deduplication; discard L2="Unknown" stubs | Researcher mandate |
| **Soul Bloat Prevention (C-MEM-006)** | Check new L3 against existing lessons before append to `soul.yaml` | Researcher mandate |
| **Hybrid Scoring Negation (C-MEM-013)** | Negate FTS5 rank: `-rank + vec_score * 10` (SQLite negative ranking) | Researcher mandate |
| **Active Tool Call (Researcher)** | MUST perform ≥1 active tool call per research query; no parametric synthesis | Researcher mandate |
| **Sovereign Search Protocol** | Local cache → local FTS → web search → web fetch → [TOOL-CHAIN-COLLAPSE] | AGENTS.md §Search |
| **M23 on Search** | If ALL search tools fail → `[TOOL-CHAIN-COLLAPSE]`; no synthesis | M23 |

---

## 🤝 COORDINATION CONSTRAINTS (Hivemind)

| Constraint | Rule | Source |
|------------|------|--------|
| **Hop Rule (M10/M15)** | Single-level subagent nesting; direct execution first; no self-recursion | AGENTS.md |
| **Workspace Locks** | `data/coordination/locks/{domain}.lock` — TTL-based auto-release (default 1h, max 24h) | Hivemind |
| **Handoff Protocol** | `submit` → `accept` → `complete` (hardening-p9 contract layer) | A2A_PROTOCOL.md |
| **Extended Sessions** | `hivemind_extended_checkin` up to 24h TTL for long-running agents | Hivemind |
| **Provenance (M22)** | `GenerateResult.provider_name` = ACTUAL provider | M22 |

---

## 🚫 EXPLICITLY FORBIDDEN

| Forbidden | Reason | Mandate |
|-----------|--------|---------|
| `import asyncio` in `src/omega/` | Use AnyIO | M1 |
| Stack logic in `src/omega/` | Engine-Stack Firewall | M2 |
| External telemetry/analytics | Zero Telemetry | M8 |
| Bare `except:` in core | Error Integrity | M9 |
| >14 agents in `.opencode/agents/` | Fleet Cap | M10 |
| Session without L1→L3 distillation | Soul Integrity | M11 |
| Release without `make temple-grade` = 0 | Temple-Grade | M13 |
| `[id-soft:]` tag without vet record ≥7/10 | Heritage | M14 |
| `GenerateResult.provider_name` ≠ actual provider | Response Provenance | M22 |
| Soft-failure on broken tool (synthesis) | Failure Integrity | M23 |
| `--break-system-packages` | Venv Sovereignty | M24 |
| Reference doc failing `doc-llm-validate` | Doc Standards | M26 |
| State not following 5-Tier Tracking | Tracking Integrity | M27 |
| `git add -A` | Secrets re-commit risk | DEBUT_REMEDIATION |
| Mass `sed` across repo | No Cowboy Sed | M4 |
| Linear Python scans for doc search | FTS5-First | C-MEM-004 |
| Parametric synthesis without tool call | Researcher mandate | Researcher |

---

## 📋 CONSTRAINT CHECKLIST (Pre-Commit / Pre-Release)

```
[ ] M1: rg 'import asyncio|from asyncio' src/omega/ --type py --glob '!*test*' --glob '!*governance*' --glob '!*tty_agent*' → 0
[ ] M2: FirewallChecker.scan() → 0 errors, 0 warnings
[ ] M7: Provider chain order = local (0,1,2) → cloud (3-9)
[ ] M8: make check-m8-zero-telemetry → "No telemetry SDKs in core"
[ ] M9: make check-m9-error-integrity → "No bare except in core"
[ ] M10: ls .opencode/agents/ → ≤ 14
[ ] M11: Session ends with L1→L3 in proposed_lessons.yaml
[ ] M13: make temple-grade → exit 0
[ ] M14: make heritage-vet → "All heritage tags have vet records"
[ ] M22: GenerateResult.provider_name = actual provider
[ ] M23: No synthesis when mandatory tool fails
[ ] M24: All Python in .venv/; no --break-system-packages
[ ] M26: make doc-llm-validate → "All validations passed"
[ ] M27: State follows 5-Tier Tracking Architecture
[ ] D-536: rg 'TriageRouter|SemanticRouter|RoutingTable' src/omega/ → Empty
[ ] D-551: oracle.py + model_gateway.py split with contract tests
[ ] D-526/527: zswap enabled, zRAM disabled, never both
[ ] D-601: Model window economics laws followed in multi-model chains
[ ] C-MEM-004: FTS5-first search pattern used
[ ] C-MEM-013: FTS5 rank negated in hybrid scoring
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ CANONICAL-CONSTRAINTS ⬡ 2026-08-29*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: jem-2.0 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

