# 🔱 R_BUILD_VS_BUY_COMMUNITY_LIBS — Canonical Decision Matrix
**AP Token**: `AP-BUILD-VS-BUY-v1.0.0`
⬡ OMEGA ⬡ DEEPSEEK ⬡ CLINE ⬡ BUILD-VS-BUY ⬡ 2026-07-30

**Status**: COMPLETE
**Source**: PROCESS_IMPROVEMENT_PLAN §10 + fresh web research 2026-07-30
**Supersedes**: Scattered decisions in PROCESS_IMPROVEMENT_PLAN §10, R_CIRCUIT_BREAKER_PATTERNS.md, individual gap docs

---

## §1 Executive Summary

| Verdict | Count | Systems |
|---------|-------|---------|
| ✅ **ADOPT** (replace custom) | 4 | pybreaker, stamina, structlog, prometheus_client |
| ✅ **MIGRATE** (upgrade existing) | 2 | Pydantic v2, SOPS + age wrapper |
| ✅ **KEEP CUSTOM** (correct decision) | 6 | Hivemind, SoulStore, OOMProtector, Mandates, capability registry, sqlite-vec adapter |
| 🟡 **CONSIDER** (defer) | 1 | sentence-transformers (Phase D-3) |
| ⏳ **DEFER INDEFINITELY** | 1 | eventsourcing lib |

---

## §2 Adopt — Community Libraries

### §2.1 pybreaker
| Field | Value |
|-------|-------|
| Library | pybreaker (danielfm/pybreaker) |
| Stars | 500+ |
| Why | 3-state FSM, thread-safe, decorator support, exception filtering. 6 custom clones are redundant. |
| Custom deleted | 6 files, ~2,000 lines |
| Effort | 4h |
| Verdict | ✅ **ADOPT** — Netflix Hystrix defaults: `fail_max=3`, `reset_timeout=60s` |

### §2.2 stamina
| Field | Value |
|-------|-------|
| Library | stamina (hynek/stamina) |
| Stars | 1,500+ |
| Why | Async-native, decorator-based, jitter built-in. Replaces scattered 50/100/200ms hand-rolled retry. |
| Custom deleted | ~300 lines across ~10 files |
| Effort | 2h |
| Verdict | ✅ **ADOPT** — pairs with pybreaker: stamina for retry, pybreaker for fail-fast |

### §2.3 structlog
| Field | Value |
|-------|-------|
| Library | structlog (hynek/structlog) |
| Stars | 13,000+ |
| Why | 2026 production standard for JSON logging. Binds trace_id via contextvars. Replaces dead `setup_json_logging()` (M9 blocker). |
| Custom deleted | ~80 lines dead code |
| Effort | 2h |
| Verdict | ✅ **ADOPT** — closes M9 compliance gap |

### §2.4 prometheus_client
| Field | Value |
|-------|-------|
| Library | prometheus_client (Official Python) |
| Stars | 4,500+ |
| Why | Counter/Gauge/Histogram types. Already installed v0.24.1 — unused! Replaces HealthMonitor sliding window. |
| Custom deleted | ~500 lines |
| Effort | 2h |
| Verdict | ✅ **ADOPT** — already installed, free win, unlocks Grafana |

---

## §3 Migrate — Upgrade Existing

### §3.1 Pydantic v2
| Field | Value |
|-------|-------|
| What | Migrate manual validation → Pydantic v2 `model_validate_yaml()` |
| Why | Zero new deps. Built-in `.yaml()` I/O. Replaces 217-line soul_validator.py. |
| Effort | 3h |
| Verdict | ✅ **MIGRATE** — closes tech debt |

### §3.2 SOPS + age
| Field | Value |
|-------|-------|
| What | VaultCore already uses age (correct). Add SOPS wrapper. Install `age` CLI binary. |
| Why | SOPS+age is 2026 GitOps standard. Pattern already correct; just add binary. |
| Effort | 1h |
| Verdict | ✅ **MIGRATE** — pattern correct, add binary |

---

## §4 Keep Custom — Correct Decisions

| System | Lines | Why It Stays Custom |
|--------|-------|---------------------|
| Hivemind (MCP coordination) | ~600 | Cross-CLI, file-based, sovereign. A2A is complementary, not replacement. |
| SoulStore atomic writer | 217 | 4-layer guarantee. File-based sovereignty = differentiator. |
| OOMProtector (3-signal fusion) | ~300 | No community lib for CCX-aware local LLM OOM. Genuinely novel. |
| 25 Sovereign Mandates | n/a | No community constitutional-law framework for multi-agent governance. Novel. |
| Capability registry / soul.yaml | domain-specific | No off-the-shelf system models agent identity like soul.yaml. |
| sqlite-vec + MemoryStore | confirmed | Per §10.4: correct for single-user local-first. Stripping Qdrant. |

---

## §5 Defer / Do Not Adopt

| System | Why Not | Re-evaluate If |
|--------|---------|----------------|
| eventsourcing (9.5.5) | JSONL handles audit trails. Full event-sourcing is over-engineering. | Mnemosyne Phase 2 needs replay/projection |
| msgspec (3.2× faster) | Pydantic v2 already installed, ecosystem standard. Our schemas are not hot paths. | MCP RPC SerDes shows bottleneck at 10,000+ ops/min |
| sentence-transformers | Current ONNX loader works. Lower priority. | Phase D-3 |
| A2A protocol | No cross-framework agents. Hivemind handles coordination. | When LangGraph/CrewAI agents join fleet |
| OpenBao / Keycloak | VaultCore MVP sufficient. Adds server process dependency. | When remote MCP clients need auth |

---

## §6 Source References

- `docs/strategy/PROCESS_IMPROVEMENT_PLAN_20260725.md` §10 (base build-vs-buy decisions)
- `docs/research/R_CIRCUIT_BREAKER_PATTERNS.md` (breaker clone locations, pybreaker recommendation)
- `docs/research/R_DEEP_WEB_RESEARCH_OMEGA_GAPS_20260729.md` (7-domain deep research, 50+ sources)
- `docs/changelog.md` (build-vs-buy summary)
- `docs/research/R_COORDINATION_ENTROPY_PREVENTION_20260730.md` (HMC accretion analysis)
- `docs/research/R_AGENT_FLEET_TOPOLOGY.md` (HMAS architecture)
- `docs/research/R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md` (SG-01 through SG-10)

---

*⬡ OMEGA ⬡ DEEPSEEK ⬡ CLINE ⬡ BUILD-VS-BUY ⬡ v1.0.0 ⬡ 2026-07-30*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: CLINE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
