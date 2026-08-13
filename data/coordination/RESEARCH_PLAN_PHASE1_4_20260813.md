# 🔱 Research Plan — Phase 1-4 Knowledge Gaps (ENHANCED v2)
**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ RESEARCH ⬡ 20260813

**Target:** @researcher (Sovereign Researcher — Polymathic Council)
**Sprint:** SDP-EXECUTION-01
**Priority:** P0 — All gaps block Phase 1-4 execution
**Est. Total:** ~28 hours (reduced from 40 — 6 gaps already resolved)

---

## 🎯 Objective

Fill all **genuinely open** knowledge gaps for Phase 1-4 execution. This v2 plan eliminates redundancy by marking already-resolved gaps (with pointers to existing docs) so @researcher does not re-research resolved items.

---

## ✅ ALREADY RESOLVED — Do NOT Re-Research (Pointer Only)

These gaps are fully resolved by existing research. @researcher should **verify the pointer exists** and move on — no new research.

| # | Gap | Resolved By | Status |
|---|-----|-------------|--------|
| **R1** | opencode.db `message.data` JSON schema for `tokens.total` | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` (verified against live 16GB DB) | ✅ RESOLVED |
| **R8** | Streaming timeout **mystery** — what handles the fix | `data/entities/researcher/workspace/research_reports/STREAMING_TIMEOUT_MYSTERY_RESEARCH_20260810.md` — **SOLVED: OpenCode v1.18.14 (Aug 5) native retry, NOT the plugin** | ✅ SOLVED |
| **R9** | zswap optimal config (pool%, compressor, allocator) | `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` + `data/entities/researcher/workspace/zram_tuning_guide.md` — **zswap 25%, lzo_rle, zsmalloc, shrinker** | ✅ RESOLVED |
| **R10** | NVMe swap file best practices | `MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` — **16GB, lower priority than zswap** | ✅ RESOLVED |
| **R11** | sysctl memory params consolidation | `MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` + `KNOWLEDGE_GAPS_RESEARCH_20260811.md` — **swappiness=100, 99-omega-memory.conf** | ✅ RESOLVED |
| **R12** | systemd MemoryMin/High/Max + hardening | `MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` + `data/entities/john_carmack/workspace/zram_review_20260811.md` — **MemoryMin=2G, High=5G, Max=6G + full hardening** | ✅ RESOLVED |
| **R14** | Streaming heartbeat patterns (anyio task groups, watchdog) | `docs/research/R_C11_STREAMING_PATTERNS_20260723.md` + `docs/research/R_CARMACK_CG-002_STREAMING_TIMEOUT_20260719.md` — **move_on_after vs fail_after, heartbeat loop** | ✅ RESOLVED |

---

## 📋 GENUINELY OPEN Gaps by Phase

### Phase 1 — Context Gauge v1 (Week 1-2)

| # | Gap | Dependent Task | Priority | Est. Hours |
|---|-----|----------------|----------|------------|
| **R2** | Model context window **detection mechanism** — dynamic (from config/API) vs static, tier mapping, fallback. NOTE: windows themselves are known (D-522); the *detection code path* is the gap | QW-8 | P0 | 2 |
| **R3** | Subagent state machine — cold/warm/hot definitions, transition triggers, persistence | A-4 | P1 | 3 |
| **R4** | AGY account pool structure — 8 accounts, weekly token limits, 80% Redzone switch rule | QW-4 | P1 | 2 |
| **R5** | TriageRouter SDP constraint types — formal spec mapping to code, property test patterns | QW-6 | P1 | 3 |
| **R6** | RHP (Recovery Halt Point) schema — YAML structure, resume_pointer format, corruption handling | QW-9 | P1 | 2 |
| **R7** | MCP tool patterns **in THIS codebase** — `src/omega/mcp/tools/` registration, pydantic validation, server wiring | QW-10 | P1 | 3 |
| **R8b** | **OBS-1 re-scoped**: Since mystery is SOLVED (v1.18.14 native retry), the remaining gap is *implementing* streaming observability — heartbeat logging to MetricsDB, timeout event capture, plugin detector. **Owner: @jem** (was TBD) | OBS-1 | **P0** | 3 |

---

### Phase 2 — zswap Migration + Streaming Plugin (Week 2-3)

| # | Gap | Dependent Task | Priority | Est. Hours |
|---|-----|----------------|----------|------------|
| **R13** | OpenCode **plugin architecture** — manifest, hooks, model detection, npm publish (config analysis exists; plugin build API is the gap) | PLUGIN-1..8 | P1 | 4 |
| **R14b** | **Nemotron plugin fallback chain** — Nemotron 3 Ultra → Super → Laguna S 2.1, state preservation on failover | PLUGIN-5 | P1 | 2 |

---

### Phase 3 — Un-overengineering (Week 3-4)

| # | Gap | Dependent Task | Priority | Est. Hours |
|---|-----|----------------|----------|------------|
| **R15** | pyresilience AnyIO/trio compatibility — spike test plan, async patterns (library is NEW 2026-03, only 68 stars) | UO-6.1 | P0 | 2 |
| **R16** | pydantic v2 model_validate patterns — soul_validator.py migration | UO-6.2 | P1 | 2 |
| **R17** | structlog integration — processors, formatters, OpenCode compatibility | UO-6.3 | P1 | 2 |
| **R18** | prometheus_client textfile collector — local-only, :8016/metrics, M8 compliance | UO-6.4 | P1 | 2 |
| **R19** | Retry strategy comparison — pyresilience vs tenacity vs stamina benchmarks (live spike) | UO-6.5 | P1 | 3 |
| **R20** | Keyblind/Authy/Agent Vault verification — existence, stars, MCP integration, maturity | UO-6.6 | P0 | 4 |

---

### Phase 4 — Phase D Gate Closure (Week 4-6)

| # | Gap | Dependent Task | Priority | Est. Hours |
|---|-----|----------------|----------|------------|
| **R21** | OpenCode workhorse paths — billing Tier 1, Antigravity OAuth, OCZ+WARP, paid alt | G-1 | P0 | 3 |
| **R22** | WARP proxy pool fix — warp-ns-setup.sh source, iptables, bridge config | W-1 | P0 | 3 |
| **R23** | Restic passphrase management — OMEGA_VAULT_PASSPHRASE, .env.backup, timer | C-3 | P0 | 2 |
| **R24** | AppArmor container profiles — confinement, profile generation, aa-status | V-10 | P1 | 3 |
| **R25** | IA2 envelope freshness — timestamp, signature verification, replay protection | V-9 | P1 | 3 |

---

## 🆕 NEW Gaps Added in v2

| # | Gap | Why Added | Dependent Task | Priority | Est. Hours |
|---|-----|-----------|----------------|----------|------------|
| **R26** | Honker (Redis replacement) verification — existence, SQLite NOTIFY/LISTEN viability, wafris.org precedent | G9 was "research if needed" — now explicit; blocks Redis removal decision | UO-7 / Redis removal | P2 | 2 |
| **R27** | `tokens.total` **query verification against live DB** — confirm `json_extract(data,'$.tokens.total')` returns correct value on real sessions (R1 gave schema; this validates the actual gauge query) | QW-2 needs a working query, not just schema | QW-2 | P0 | 1 |
| **R28** | **MCP Streamable HTTP + tool registration** — how Omega Hub exposes MCP tools to OpenCode (client SEP-2575), tool schema format | QW-10 needs to know how tools reach OpenCode | QW-10 | P1 | 2 |
| **R29** | **OpenCode plugin detection** — how to scan loaded plugins (config + plugins dir), plugin manifest schema | OBS-4 (plugin detector) | OBS-4 | P1 | 2 |
| **R27b** | **NULL `tokens.total` handling** — VERIFIED: live DB returns NULL for some assistant messages. Gauge must handle NULL (fallback to input+cache.read, or skip+sum rest). QW-2 acceptance must include NULL handling | QW-2 | **P0** | 1 |
| **R30** | **Circuit breaker library decision audit** — 4-way spike: pyresilience vs tenacity (installed) vs stamina vs pybreaker. Maturity scoring (stars, last release, open issues) + AnyIO compat + happy-path latency. D-528 picked pyresilience (68 stars) — under-weighted maturity risk | UO-6.1 | **P0** | 3 |
| **R31** | **Streaming plugin scope reduction** — confirm OpenCode v1.18.14 native retry coverage; scope PLUGIN-1..8 from 26h → ~8h (observability + fallback + detection only, NO retry re-impl) | PLUGIN-1..8 | P1 | 1 |
| **R32** | **In-session gauge data source** — DB-poll (lags async writes) vs in-memory hook (real-time). For 80% pressure halt, real-time matters. Specify for R2/QW-2 | QW-2, R2 | P1 | 2 |

---

## 🔴 Critical Unresolved Gaps (From Prior Research)

| # | Gap | Status | Action |
|---|-----|--------|--------|
| **G7** | Streaming timeout observability — **MYSTERY SOLVED** (v1.18.14 native retry) | Re-scoped | R8b: implement observability, not investigate |
| **G8** | Keyblind/Authy/Agent Vault — existence unverified | Blocks UO-6.6 | R20 (P0) |
| **G9** | Honker for Redis replacement — existence unverified | Blocks Redis removal | R26 (NEW, P2) |

---

## 📅 Research Phases (Updated Schedule)

### Phase R1 — Week 1 (Parallel with Phase 0 Security)
**Focus:** Context Gauge foundation + Streaming observability
**NOTE:** R1, R8, R14 already resolved — skip. R8b is the new scope.

| Day | Gaps | Deliverable |
|-----|------|-------------|
| Mon | R27 (verify tokens.total query), R27b (NULL handling), R8b | Gauge query validation + NULL strategy + streaming observability impl plan |
| Tue | R2, R3 | Model window detection spec + subagent state machine |
| Wed | R4, R5 | AGY pool structure + TriageRouter constraint mapping |
| Thu | R6, R7, R28 | RHP schema + MCP tool patterns + Streamable HTTP |
| Fri | Integration | Consolidated Phase 1 research package |

**Output:** `data/entities/researcher/workspace/research_reports/PHASE1_RESEARCH_20260813.md`

---

### Phase R2 — Week 2 (Parallel with Phase 1 Execution)
**Focus:** Streaming plugin + Redis decision
**NOTE:** R9-R12, R14 already resolved — skip.

| Day | Gaps | Deliverable |
|-----|------|-------------|
| Mon | R13 | OpenCode plugin architecture + npm publish |
| Tue | R14b | Nemotron plugin fallback chain |
| Wed | R26 | Honker / Redis replacement verification |
| Thu | Integration | Consolidated Phase 2 research package |
| Fri | Buffer | Overflow / verification |

**Output:** `data/entities/researcher/workspace/research_reports/PHASE2_RESEARCH_20260813.md`

---

### Phase R3 — Week 3 (Parallel with Phase 2 Execution)
**Focus:** Un-overengineering library verification

| Day | Gaps | Deliverable |
|-----|------|-------------|
| Mon | R15, R16 | pyresilience spike results + pydantic v2 patterns |
| Tue | R17, R18 | structlog + prometheus_client integration guide |
| Wed | R19, R20 | Retry strategy decision + Vault replacement verification |
| Thu | Integration | Consolidated Phase 3 research package |
| Fri | Buffer | Overflow / verification |

**Output:** `data/entities/researcher/workspace/research_reports/PHASE3_RESEARCH_20260813.md`

---

### Phase R4 — Week 4 (Parallel with Phase 3 Execution)
**Focus:** Phase D gate closure

| Day | Gaps | Deliverable |
|-----|------|-------------|
| Mon | R21, R22 | Workhorse paths + WARP fix |
| Tue | R23, R24 | Restic passphrase + AppArmor profiles |
| Wed | R25 | IA2 envelope freshness |
| Thu | Integration | Consolidated Phase 4 research package |
| Fri | Buffer | Overflow / verification |

**Output:** `data/entities/researcher/workspace/research_reports/PHASE4_RESEARCH_20260813.md`

---

## 📚 Source Requirements

### Authoritative Sources (Priority Order)
1. **Kernel.org docs** — zswap, cgroup v2, sysctl
2. **Library official docs** — pyresilience, structlog, prometheus_client, pydantic v2
3. **OpenCode plugin API** — official docs, plugin examples, changelog
4. **Verified code patterns** — grep existing codebase for patterns
5. **Community sources** — Chris Down blog, Fedora wiki, GitHub issues (verified)

### Forbidden Sources
- Unverified blog posts
- Stack Overflow answers without verification
- AI-generated content without source citation
- Outdated docs (pre-2024 for kernel, pre-2025 for libraries)

---

## 📝 Deliverable Format

Each research report must include:

```markdown
# Gap R<N>: <Title>

## Summary
<2-3 sentence summary of what was found>

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|

## Findings
<Detailed findings with code snippets, config examples, command outputs>

## Recommendation
<Specific actionable recommendation for the dependent task>

## Confidence
<HIGH/MEDIUM/LOW with justification>

## Remaining Unknowns
<What still needs investigation>
```

---

## 🔗 Coordination

### Handoff Protocol
1. **Before starting:** Post to Hivemind with `intent: "question"` and gap IDs
2. **During research:** Heartbeat every 2 hours via Hivemind
3. **On completion:** Post report to Hivemind with `intent: "decision"` and link to report
4. **Blockers:** Immediately post with `intent: "blocker"`

### Task Registry Entries
Each research phase gets a task_id in TASK_REGISTRY.json:
- `research-phase1-gaps-20260813`
- `research-phase2-gaps-20260813`
- `research-phase3-gaps-20260813`
- `research-phase4-gaps-20260813`

---

## ⚠️ Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| pyresilience fails AnyIO test | Medium | High | Fallback to tenacity (already installed) |
| Keyblind/Authy don't exist | Medium | High | Keep VaultCore, slim to adapter only |
| Streaming observability gap unsolvable | Low | Critical | Implement OBS-1 as best-effort, document |
| Model window detection unreliable | Low | Medium | Use config fallback + manual override |
| Honker doesn't exist | Medium | Medium | Keep Redis; defer removal (M12 advisory) |

---

## ✅ Acceptance Criteria

Research phase complete when:
- [ ] All **genuinely open** gaps in phase resolved with authoritative sources
- [ ] Already-resolved gaps verified (pointer exists, no re-research)
- [ ] Reports written to `data/entities/researcher/workspace/research_reports/`
- [ ] Hivemind posts made for each gap resolution
- [ ] Dependent task owners (@jem, @maat, @lilith, @roc_racoon) acknowledge receipt
- [ ] TASK_REGISTRY.json updated with completion status

---

## 📊 v2 Change Log

| Change | Detail |
|--------|--------|
| **Marked 7 gaps RESOLVED** | R1, R8, R9, R10, R11, R12, R14 — pointer-only, no re-research |
| **Re-scoped R8 → R8b** | Mystery SOLVED (v1.18.14 native retry); now about implementing observability |
| **Added 4 NEW gaps (v2)** | R26 (Honker), R27 (tokens.total query validation), R28 (MCP Streamable HTTP), R29 (plugin detection) |
| **Added 5 NEW gaps (v3 Hy3)** | R27b (NULL tokens.total), R30 (CB library 4-way audit), R31 (plugin scope reduction), R32 (in-session gauge source), OBS-1 owner assigned (@jem) |
| **Split R14 → R14b** | Heartbeat patterns resolved; fallback chain is the new gap |
| **Reduced total** | 40h → 28h (removed resolved-gap hours) |

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-PLAN ⬡ v2.0.0 ⬡ 20260813*
