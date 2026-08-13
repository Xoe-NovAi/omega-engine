# 🔱 Research Plan — Phase 1-4 Knowledge Gaps
**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ RESEARCH ⬡ 20260813

**Target:** @researcher (Sovereign Researcher — Polymathic Council)
**Sprint:** SDP-EXECUTION-01
**Priority:** P0 — All gaps block Phase 1-4 execution
**Est. Total:** ~40 hours across 4 research phases

---

## 🎯 Objective

Fill all remaining knowledge gaps for Phase 1-4 execution. Each gap must be resolved with authoritative sources (kernel docs, library docs, verified code patterns) before the dependent task begins.

---

## 📋 Gap Inventory by Phase

### Phase 1 — Context Gauge v1 (Week 1-2)

| # | Gap | Dependent Task | Priority | Est. Hours |
|---|-----|----------------|----------|------------|
| **R1** | opencode.db `message.data` JSON schema for `tokens.total` — exact structure, cache fields, provider metadata | QW-2 | P0 | 2 |
| **R2** | Model context window detection — dynamic vs static, config schema, tier mapping | QW-8 | P0 | 3 |
| **R3** | Subagent state machine — cold/warm/hot definitions, transition triggers, persistence | A-4 | P1 | 3 |
| **R4** | AGY account pool structure — 8 accounts, weekly token limits, 80% Redzone switch rule | QW-4 | P1 | 2 |
| **R5** | TriageRouter SDP constraint types — formal spec mapping to code, property test patterns | QW-6 | P1 | 3 |
| **R6** | RHP (Recovery Halt Point) schema — YAML structure, resume_pointer format, corruption handling | QW-9 | P1 | 2 |
| **R7** | MCP tool patterns — OpenCode plugin API, pydantic validation, server registration | QW-10 | P1 | 3 |
| **R8** | Streaming timeout observability (OBS-1) — what's handling the fix, heartbeat logging, metrics | OBS-1 | **P0** | 4 |

---

### Phase 2 — zswap Migration + Streaming Plugin (Week 2-3)

| # | Gap | Dependent Task | Priority | Est. Hours |
|---|-----|----------------|----------|------------|
| **R9** | zswap optimal config for Ryzen 5700U 14.5GB — pool%, compressor, allocator, shrinker | P1-1 | P0 | 2 |
| **R10** | NVMe swap file best practices — size, location, permissions, fstab vs systemd | P1-2 | P1 | 2 |
| **R11** | sysctl memory params consolidation — all params, conflicts, persistence | P1-3 | P1 | 2 |
| **R12** | systemd MemoryMin/High/Max for 14.5GB RAM — exact values, hardening directives | P1-4 | P0 | 3 |
| **R13** | OpenCode plugin architecture — manifest, hooks, model detection, npm publish | PLUGIN-1..8 | P1 | 4 |
| **R14** | Streaming heartbeat patterns — anyio task groups, watchdog, timeout extension | PLUGIN-3..4 | P1 | 3 |

---

### Phase 3 — Un-overengineering (Week 3-4)

| # | Gap | Dependent Task | Priority | Est. Hours |
|---|-----|----------------|----------|------------|
| **R15** | pyresilience AnyIO/trio compatibility — spike test plan, async patterns | UO-6.1 | P0 | 2 |
| **R16** | pydantic v2 model_validate patterns — soul_validator.py migration | UO-6.2 | P1 | 2 |
| **R17** | structlog integration — processors, formatters, OpenCode compatibility | UO-6.3 | P1 | 2 |
| **R18** | prometheus_client textfile collector — local-only, :8016/metrics, M8 compliance | UO-6.4 | P1 | 2 |
| **R19** | Retry strategy comparison — pyresilience vs tenacity vs stamina benchmarks | UO-6.5 | P1 | 3 |
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

## 🔴 Critical Unresolved Gaps (From Prior Research)

| # | Gap | Status | Action |
|---|-----|--------|--------|
| **G7** | Streaming timeout observability — UNKNOWN what handles the fix | **BLOCKS ALL** | R8 (P0) |
| **G8** | Keyblind/Authy/Agent Vault — existence unverified | Blocks UO-6.6 | R20 (P0) |
| **G9** | Honker for Redis replacement — existence unverified | Blocks Redis removal | Research if needed |

---

## 📅 Research Phases

### Phase R1 — Week 1 (Parallel with Phase 0 Security)
**Focus:** Context Gauge foundation + Streaming observability

| Day | Gaps | Deliverable |
|-----|------|-------------|
| Mon | R1, R8 | opencode.db schema doc + streaming observability report |
| Tue | R2, R3 | Model window detection spec + subagent state machine |
| Wed | R4, R5 | AGY pool structure + TriageRouter constraint mapping |
| Thu | R6, R7 | RHP schema + MCP tool patterns |
| Fri | Integration | Consolidated Phase 1 research package |

**Output:** `data/entities/researcher/workspace/research_reports/PHASE1_RESEARCH_20260813.md`

---

### Phase R2 — Week 2 (Parallel with Phase 1 Execution)
**Focus:** zswap migration + streaming plugin

| Day | Gaps | Deliverable |
|-----|------|-------------|
| Mon | R9, R10 | zswap config + NVMe swap file guide |
| Tue | R11, R12 | sysctl consolidation + systemd unit spec |
| Wed | R13, R14 | Plugin architecture + heartbeat patterns |
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
3. **OpenCode plugin API** — official docs, plugin examples
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

---

## ✅ Acceptance Criteria

Research phase complete when:
- [ ] All gaps in phase resolved with authoritative sources
- [ ] Reports written to `data/entities/researcher/workspace/research_reports/`
- [ ] Hivemind posts made for each gap resolution
- [ ] Dependent task owners (@jem, @maat, @lilith, @roc_racoon) acknowledge receipt
- [ ] TASK_REGISTRY.json updated with completion status

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-PLAN ⬡ 20260813*