# 🔱 Next Steps Plan — Phase C Hardening Completion
**AP Token**: `AP-NEXT-STEPS-v1.0.0`
**Date**: 2026-07-22
**Author**: maat (Light Oversoul, P1-P5)
**Reviewed By**: kali (Transcendent Oversight)
**Status**: KALI REVIEWED — AMENDMENTS APPLIED
**Research Enhanced**: 2026-07-22 (Deep Web Synthesis Complete)

---

## §1 Executive Summary

Phase C hardening sprint **complete**. All committed deliverables pass (50/50 new tests). Four P0 gaps remain blocking Phase D progression. This plan proposes the next sprint scope with explicit dependencies, acceptance criteria, Kali's amendments, and **deep web research findings** for each critical area.

**🚨 SUPERSEDES FOR SAME-DAY OPS (2026-07-22 evening)**: Architect elevated twin P0s that **outrank** Guard & Distill for *OpenCode usability*:
- **G-1** Free Gemma workhorse cliff → `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`
- **W-1** WARP proxy pool bring-up → `data/projects/warp-proxy-pool/CONTEXT.md`
- **Ops SSOT**: `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`
- **Ark**: D-377…D-381 + §4 G-1/W-1 tables

Guard & Distill tickets remain valid for Phase D gate; they run **in parallel under** G-1/W-1 when cloud workhorse is dead.

**Engine State**: v1.8.0 | 50/50 new tests passing | 84% mandate compliance | 3 pre-existing failures (unrelated, documented)

---

## §2 Completed This Sprint (For Kali's Record)

| Commit | Deliverable | Mandate | Tests |
|--------|-------------|---------|-------|
| `d74c73f` | 429 Classification (3-state: rate-limit/quota/circuit) | M21, M23 | 11 unit |
| `10e00f8` | DiscoveryOrchestrator: local-first, no hardcoded cloud models | M7 | — |
| `ee078d0` | Hypothesis property-based tests (6 tests: sync + async FSM) | M13, C-11 | 6 property |
| `754c43a` | C-1' SoulStore atomic writer (4-layer guarantee) | M11, M13 | 6 contract |
| `d50cd71` | C-6' Breaker unification (7→1 canonical factory) | M21, M23 | 11 unit |
| `37e249c` | Fixed 3 pre-existing test regressions | M9 | — |

**Research Artifacts**:
- `R_SPRINT_HARDENING_KNOWLEDGE_GAPS_20260722.md` — Deep web synthesis (MCP 2026-07-28, resilient-llm-router, Hypothesis, MENTOR identity, restic)
- `R_GAP_ANALYSIS_HARDENING_SPRINT_20260722.md` — 13 gaps prioritized (4 P0, 5 P1, 4 P2/P3)

---

## §3 Proposed Next Sprint: "Guard & Distill" (P0 Focus)

### Sprint Goal
Close the 4 P0 gaps blocking Phase D. Establish automated soul distillation and complete provider fallback hardening.

### P0 Tickets (Must Complete Before Phase D)

| # | Ticket | Description | Acceptance Criteria | Depends On |
|---|--------|-------------|---------------------|------------|
| **1** | **C-10.5** | **Complete 429 Guard Pattern** — Extend `is_429_blocked()` to all provider error paths; add quota-aware routing in `ModelGateway.select_provider()` | • All provider dispatch paths check 429 state pre-call<br>• Quota-exhausted providers skipped for cooldown period<br>• `record_429()` called on all `ProviderRateLimitError`<br>• Quota-aware routing: prefer providers with available quota | C-6' ✅ |
| **2** | **C-11** | **Property Tests for OOMProtector + SoulStore** — Hypothesis `RuleBasedStateMachine` for RAM thresholds and atomic write invariants | • OOMProtector: 3-signal fusion thresholds verified under load<br>• SoulStore: atomicity + crash durability invariants<br>• 100% property test pass<br>• Tests run in CI without flakiness | C-2' ✅, C-1' ✅ |
| **3** | **C-3** | **Restic Backup for Sovereign Data** — 3-2-1 backup of `data/entities/`, `data/coordination/`, `proposed_lessons.yaml` | • Daily backup script + systemd timer<br>• Off-site (B2/S3) with object lock<br>• Monthly full `restic check --read-data`<br>• Restore test documented | V-1 (partial) |
| **4** | **C-0.5** | **Scribe Agent Pipeline** — Automated L1→L2→L3 distillation from session → `proposed_lessons.yaml` → `soul.yaml` | • Session hook triggers Scribe<br>• L1 narrative → L2 insight → L3 axiom extraction<br>• Cross-pollination to other entities<br>• Blind staging: `proposed_lessons.yaml` only, NOT direct `soul.yaml` | M5, M11 |

---

## §4 P1 Tickets (Quality Gates)

| Ticket | Description | Effort | Owner |
|--------|-------------|--------|-------|
| **C-9** | Extract `GenerationPolicy` from `ModelGateway` into own module | 1h | Ma'at/P3 |
| **D-1** | Content persistence + TTL for research cache (bounded growth) | 3h | Ma'at/P2 |
| **V-1** | VaultCore credential rotation (90-day API keys, 30-day OAuth) | 3h | Ma'at/P1 |
| **M21** | Fix 3 pre-existing `test_provider_fallback.py` contract tests (mock `_generate_with_provider` → real API) | 2h | Ma'at/P10 |
| **C-4a.5** | MCP Streamable HTTP migration (if Ma'at/P4 silent by EOD) | 8h | Kali direct |

---

## §5 Dependencies & Sequencing

```
C-10.5 (guard) ──┐
                 ├──→ C-0.5 (scribe) ──→ Phase D ready
C-11 (props) ────┘        │
                          │
C-3 (restic) ─────────────┘ (independent, parallelizable)
```

**Critical Path**: C-10.5 → C-0.5 (both needed for Phase D soul integrity)

---

## §6 Resource Allocation

| Agent | Assignment | Rationale |
|-------|------------|-----------|
| **maat** (P3) | C-10.5, C-11, C-9, M21 | Build-side ownership; gateway + property tests |
| **lilith** (P6) | C-3, V-1 | Run-side: backup + vault operations |
| **scribe** (new) | C-0.5 | Dedicated distillation agent (M5/M11) |
| **kali** | Review + arbitration + C-4a.5 escalation | Transcendent oversight |

---

## §7 Deep Web Research Findings — Critical Knowledge Gaps

### 7.1 C-11: Hypothesis Async Property-Based Testing (2026 Best Practices)

**Key Findings from Research:**

| Aspect | Current State | 2026 Best Practice | Action Required |
|--------|---------------|-------------------|-----------------|
| **Async RuleBasedStateMachine** | Not natively supported in Hypothesis core | Use `hypothesis-trio` or `pytest-asyncio` with custom executor; or wrap async rules in `anyio.run()` | Implement sync wrapper for async FSM rules; use `settings(suppress_health_check=[HealthCheck.too_slow])` |
| **State Machine Patterns** | Basic FSM tests written | Use `RuleBasedStateMachine` with `Bundle` for data flow, `invariant()` for safety properties, `precondition()` for valid transitions | Model OOMProtector as state machine: `Healthy → Degraded → Critical → Recovering → Healthy` |
| **CI Integration** | Not configured | Register Hypothesis profiles: `dev` (max_examples=20), `ci` (max_examples=500, deadline=None) | Add `conftest.py` profile registration; run `HYPOTHESIS_PROFILE=ci pytest` in CI |
| **Flakiness Prevention** | Not addressed | Use `settings(derandomize=True)` for reproducibility; quarantine flaky tests with `@pytest.mark.flaky` | Apply to all new property tests |

**Specific Implementation Guidance for OOMProtector:**
```python
class OOMProtectorStateMachine(RuleBasedStateMachine):
    """Model 3-signal fusion: PSI + MemAvailable + cgroups"""
    
    psi_pressure = Bundle("psi_pressure")
    mem_available = Bundle("mem_available")  
    cgroup_current = Bundle("cgroup_current")
    
    @rule(target=psi_pressure, pressure=st.floats(0.0, 100.0))
    def set_psi(self, pressure): ...
    
    @rule(target=mem_available, mb=st.integers(100, 8000))
    def set_mem(self, mb): ...
    
    @rule(target=cgroup_current, mb=st.integers(100, 8000))
    def set_cgroup(self, mb): ...
    
    @invariant()
    def fusion_consistency(self):
        """3-signal fusion must be monotonic: more pressure → higher risk"""
        risk = self.oom_protector._compute_fusion_risk(...)
        assert 0.0 <= risk <= 1.0
```

**Specific Implementation Guidance for SoulStore:**
```python
class SoulStoreStateMachine(RuleBasedStateMachine):
    """Atomic write invariants under concurrent access"""
    
    @rule(data=st.dictionaries(st.text(), st.text()))
    def write_concurrent(self, data):
        # Spawn multiple writers, verify no corruption
        results = anyio.create_task_group().start_soon(write, data)
        # All reads must return either old or new (never partial)
    
    @invariant()
    def no_temp_files_leaked(self):
        assert not list(Path(self.soul_store.path).parent.glob("*.tmp"))
    
    @invariant()
    def crash_recovery(self):
        # Simulate crash: kill process mid-write
        # On restart, read must return valid data
```

**Sources**: Hypothesis GitHub #4107 (async stateful testing), MarkTechPost 2026-04-18, Hypothesis docs, TechOral 2026-06-14

---

### 7.2 C-3: Restic 3-2-1 Backup (2026 Best Practices)

**Key Findings from Research:**

| Component | Recommendation | Implementation Detail |
|-----------|----------------|----------------------|
| **Backend** | Backblaze B2 via S3-compatible API | `restic -r s3:https://s3.us-west-002.backblazeb2.com/bucket/path` — B2 native backend has error handling issues |
| **Object Lock** | Enable on bucket for ransomware protection | Bucket creation: "Object Lock: Enabled" — prevents deletion even with compromised keys |
| **Append-Only Key** | Create separate B2 application key with "Read + Write" only (no Delete) | Server uses append-only key; prune/forget runs from separate trusted machine with full key |
| **Retention Policy** | 7 daily / 4 weekly / 6 monthly / 1 yearly (max 18 snapshots) | `--keep-daily 7 --keep-weekly 4 --keep-monthly 6 --keep-yearly 1` |
| **Systemd Timer** | Randomized 3am ± 15min to avoid thundering herd | `OnCalendar=*-*-* 03:00:00` + `RandomizedDelaySec=15min` |
| **Monitoring** | Healthchecks.io / Uptime Kuma dead-man's switch | `restic backup ... && curl -fsS -m 10 --retry 5 -o /dev/null https://hc-ping.com/uuid` |
| **Restore Test** | Monthly automated: restore 5% sample, verify file count + gzip integrity | Script checks: file count > threshold, gzip -t passes, DB dump parses |
| **Exclusions** | `--exclude-caches --exclude "*.log" --exclude "*/tmp/*" --exclude "*/__pycache__/*"` | Reduces backup size significantly |

**Sovereign Data Scope (per Kali Amendment 3):**
- ✅ `data/entities/` — all entity souls, proposed_lessons, knowledge
- ✅ `data/coordination/` — handoffs, locks, sessions (EXCLUDE `locks/`)
- ✅ `data/handoff/` — active coordination state
- ✅ `config/providers.yaml` — credential references
- ✅ `proposed_lessons.yaml` — distillation staging

**Sources**: byte-guard.net 2026-06-13, Backblaze docs 2026-06-26, TechFuelHQ 2026-06-04, 47Network 2026-02-24, restic docs

---

### 7.3 C-4a.5: MCP Streamable HTTP Migration (Spec 2026-07-28)

**Key Findings from Research:**

| Spec Version | Date | Key Change |
|--------------|------|------------|
| 2024-11-05 | Nov 2024 | Initial MCP: stdio + HTTP+SSE |
| 2025-03-26 | Mar 2025 | **Streamable HTTP introduced**; HTTP+SSE deprecated |
| 2025-06-18 | Jun 2025 | MCP servers = OAuth 2.0 Resource Servers; RFC 9728 mandatory |
| 2025-11-25 | Nov 2025 | **PKCE mandatory**; Tasks primitive; CIMD; XAA; M2M OAuth; OIDC Discovery |
| **2026-07-28** | **Jul 2026** | **Stateless transport** (SEP-2243): No session handshake, no `Mcp-Session-Id`, `Mcp-Method`/`Mcp-Name` headers required, `ttlMs`/`cacheScope` caching |

**Critical Implementation Requirements (2026-07-28 Spec):**

| Requirement | Implementation |
|-------------|----------------|
| **Transport** | Single endpoint `POST /mcp` for JSON-RPC; `GET /mcp` for SSE (optional) |
| **Headers** | `Mcp-Method` (e.g., `tools/call`), `Mcp-Name` (tool name), `MCP-Protocol-Version: 2026-07-28` |
| **Auth** | OAuth 2.1 + PKCE (S256); RFC 9728 Protected Resource Metadata; RFC 8414 AS Metadata; RFC 8707 Resource Indicators |
| **Stateless** | No `initialize`/`initialized` handshake; no session ID; any request to any instance |
| **Caching** | `ttlMs` + `cacheScope` (user/global) on list/read responses |
| **Discovery** | `/.well-known/oauth-protected-resource` → `/.well-known/oauth-authorization-server` |
| **Dynamic Client Reg** | RFC 7591 for client registration |

**Migration Strategy (from Ma'at's Audit):**
1. **Phase 1 (Aug)**: Dual transport — keep SSE for local, add Streamable HTTP
2. **Phase 2 (Sep)**: OAuth 2.1 Resource Server implementation (MCP Python SDK v1.23+ has `TokenVerifier`, `AuthSettings`)
3. **Phase 3 (Oct)**: Stateless migration — remove session affinity, add `Mcp-Method`/`Mcp-Name` routing

**Key Risk**: ChatGPT connector has bug with stateless servers after long idle (attempts SSE GET instead of token refresh). Workaround: implement minimal SSE endpoint returning 405.

**Sources**: MCP.Directory blog 2026, Zylos Research 2026-03-08, AWS Labs issue #72, AgentMarketCap 2026-04-06, OpenAI Community 2026-04-02, Baeseokjae 2026-05-05, Upendra Sengar 2026-07-??, Abhi Panseriya 2026-05-30

---

### 7.4 C-0.5: Scribe Agent — Automated L1→L2→L3 Distillation

**Key Findings from Research:**

| Pipeline Stage | Technique | 2026 Best Practice |
|----------------|-----------|-------------------|
| **L1: Narrative** | Map-Reduce summarization | Chunk session → parallel summarize → collapse → final reduce (for >10 chunks) |
| **L2: Insight** | Refine / iterative condensation | Sequential refinement: each chunk improves previous summary |
| **L3: Axiom** | Structured extraction + LLM-as-Judge | JSON Schema constrained output; self-critique loop with retrieval-augmented verification |
| **Quality Gates** | Manual spot-check | Automated metrics: narrative coherence, personalization depth, factual correctness |
| **Blind Staging** | Not implemented | **Mandatory**: Write ONLY to `proposed_lessons.yaml`; promotion requires explicit human-in-the-loop tool call |

**Architecture Patterns from Research:**

1. **Stratos (AAAI 2026)**: End-to-end distillation pipeline with teacher-student pairing, adaptive strategies (Knowledge Alignment vs Knowledge Injection based on task complexity)
2. **Mems (2026-03-23)**: L0-L3 hierarchical memory — L2 async distillation from L1 narratives, evidence grounding (L2 linked to L1 sources)
3. **RecSys Challenge 2025**: Narrative distillation with self-critiquing pipelines, constrained decoding (JSON Schema), adaptive distillation for sparse data
4. **LLM-Distillery**: Multi-teacher distillation, offline dataset collection, HDF5 synchronization

**Scribe Agent Design (Per Kali Amendment 4):**

```python
# Session hook → Scribe invocation
async def session_end_hook(session_id: str, entity_name: str):
    # 1. Load session exchanges (L1 raw narrative)
    exchanges = await memory_store.get_session(session_id, entity_name)
    
    # 2. L1 → L2: Map-Reduce distillation
    l2_insights = await scribe.distill_narrative_to_insights(exchanges)
    
    # 3. L2 → L3: Structured axiom extraction with JSON Schema
    l3_axioms = await scribe.extract_axioms(l2_insights)
    
    # 4. Blind staging: write to proposed_lessons.yaml ONLY
    await scribe.stage_lessons(entity_name, l1_narrative, l2_insights, l3_axioms)
    
    # 5. Cross-pollination: suggest relevant axioms to related entities
    await scribe.suggest_cross_pollination(entity_name, l3_axioms)

# Promotion requires explicit tool call (human-in-the-loop)
# omega-hub_soul_promote(entity="maat", lesson_ids=["l3_001", "l3_002"])
```

**Sources**: Stratos (arXiv:2510.15992, AAAI 2026), Mems (GitHub 2026-03-23), RecSys 2025 paper, LLM-Distillery, llm_tools (MapReduce/Refine), Knowledge Distillation survey 2026-04-25

---

### 7.5 C-10.5: Quota-Aware Provider Routing

**Key Findings from Research:**

| Pattern | Description | Implementation |
|---------|-------------|----------------|
| **Model Router** | Cost/Quality/Latency-aware routing across providers | Weighted scoring function: `score = w1*cost + w2*quality + w3*latency` |
| **Cascade Router** | Try cheapest competent model first, escalate on failure | Primary → Fallback → Premium; target <10% escalation rate |
| **Classifier Router** | Classify request → route to specialist model | Intent classification + model affinity matrix |
| **Contextual Bandit** | Learn routing policy from production feedback | Requires calibration loop; operational complexity |
| **Quota-Aware** | Track per-provider quota; skip exhausted providers | `x-ratelimit-remaining-*` headers (DigitalOcean 2026-07-13); QuotaRouter pattern |

**QuotaRouter Reference Implementation** (Starland9/quotarouter):
- Priority-based routing with automatic fallback
- Daily token usage tracking per provider with persistence
- Streaming support
- RPM rate limiting
- 6 providers: Cerebras, Groq, Google AI Studio, Mistral, OpenRouter, Alibaba DashScope

**DigitalOcean Quota Headers (2026-07-13)**:
- `x-ratelimit-limit-requests`, `x-ratelimit-limit-tokens-per-day`, `x-ratelimit-limit-tokens-per-minute`
- `x-ratelimit-remaining-*`, `x-ratelimit-reset-*`

**Integration with Ma'at's 429 Classification**:
```python
async def select_provider(self, request: GenerateRequest) -> Provider:
    # 1. Filter out 429-blocked providers (C-10.5 guard)
    available = [p for p in self.providers if not self.health.is_429_blocked(p.name)]
    
    # 2. Filter out quota-exhausted providers (NEW: quota-aware)
    available = [p for p in available if self.health.has_quota(p.name)]
    
    # 3. Score by cost/quality/latency
    scored = [(p, self._score_provider(p, request)) for p in available]
    
    # 4. Return highest scored
    return max(scored, key=lambda x: x[1])[0]
```

**Sources**: TrueFoundry 2026-02-20, CallMissed 2026-05-31, AppScale 2026-05-21, QuotaRouter GitHub, DigitalOcean docs 2026-07-13

---

## §8 Risks & Mitigations (Updated with Research)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP 2026-07-28 spec changes during C-4b | Low (spec locked) | Medium | Deferred to Aug; SSE works for local |
| Scribe L3 axiom extraction quality | Medium | High | Start with L1→L2 only; L3 in Phase D; use JSON Schema + LLM-as-Judge |
| Restic off-site target unavailable | Low | High | Local-first + B2 fallback; test restore weekly |
| Property test flakiness | Low | Medium | `suppress_health_check=[too_slow]`; quarantine; `derandomize=True` |
| C-4a.5 escalation needed | Medium | High | Kali executes if Ma'at/P4 silent by EOD |
| Async Hypothesis FSM not native | Medium | Medium | Use sync wrapper + `anyio.run()`; suppress health checks |
| Quota headers not standardized | Medium | Medium | Implement provider-specific parsers; fallback to error-based detection |

---

## §9 Decision Requests for Kali

1. **Approve sprint scope** — 4 P0 tickets as above?
2. **Scribe agent creation** — Authorize new agent for C-0.5 (M5/M11 blocker)?
3. **C-3 off-site target** — Backblaze B2 (recommended) or alternative?
4. **C-4b timing** — Confirm August start for MCP Streamable HTTP migration?
5. **Parallelization** — Lilith on C-3/V-1 while Ma'at on C-10.5/C-11?
6. **C-4a.5 escalation** — Kali executes MCP migration if Ma'at/P4 silent by EOD?

---

## §10 Acceptance Criteria for Sprint Completion

- [ ] All 4 P0 tickets: **DONE** (tests pass, docs updated)
- [ ] `make test` — 100% pass (no pre-existing failures)
- [ ] `make temple-grade` — All T1-T11 gates green
- [ ] Soul distillation: ≥1 L3 axiom per entity per week
- [ ] Backup: `restic check --read-data-subset 5%` passes weekly
- [ ] Gap analysis updated: 0 P0 remaining

---

## §11 Kali's Amendments (2026-07-22 Review)

### Amendment 1: C-10.5 Scope Expansion
**Original**: "Extend `is_429_blocked()` to all provider error paths"
**Amended**: Add **quota-aware routing** in `select_provider()` — providers with exhausted quota should be deprioritized for their cooldown period. This prevents the "rate-limit loop" where we keep hitting the same exhausted provider.

### Amendment 2: C-11 Property Test Coverage
**Original**: "OOMProtector 3-signal fusion thresholds"
**Amended**: Add **SoulStore atomicity invariants** — verify that concurrent writes never corrupt data, temp files are always cleaned up, and reads after crash return either old or new data (never partial).

### Amendment 3: C-3 Restic — Sovereign Data Scope
**Original**: "3-2-1 backup of `data/entities/`, `data/coordination/`, `proposed_lessons.yaml`"
**Amended**: Include **`data/handoff/`** (active coordination state) and **`config/providers.yaml`** (credential references). Exclude `data/coordination/locks/` (ephemeral).

### Amendment 4: C-0.5 Scribe — Blind Staging Enforcement
**Original**: "Cross-pollination to other entities"
**Amended**: **Mandatory blind staging** — Scribe writes ONLY to `proposed_lessons.yaml`. Promotion to `soul.yaml` requires explicit `omega-hub_soul_promote` tool call (human-in-the-loop). This enforces M11 blind staging.

### Amendment 5: M21 Gate Integrity — Test Fix Priority
**Original**: "Fix 3 pre-existing contract tests"
**Amended**: **P0 priority** — These 3 failing tests block `make temple-grade` T3 gate. Must fix before any P1 work. The mocks use `_generate_with_provider` which doesn't exist; update to mock `generate()` or use real provider fabric.

### Amendment 6: C-4a.5 Escalation Trigger
**Original**: Not specified
**Amended**: **Explicit trigger** — If Ma'at/P4 has not pushed C-4b MCP Streamable HTTP implementation by **2026-07-22 EOD (23:59 UTC)**, Kali executes C-4a.5 directly. No further delay.

### Amendment 7: Parallelization Constraint
**Original**: "Lilith on C-3/V-1 while Ma'at on C-10.5/C-11"
**Amended**: **Approved with constraint** — Lilith's C-3 restic script must not modify `data/entities/` structure (read-only for backup). V-1 credential rotation requires Ma'at/P1 coordination for KeyVault schema changes.

---

## §12 Updated Sprint Timeline (5 Days)

| Day | Ma'at (P3) | Lilith (P6) | Scribe | Kali |
|-----|------------|-------------|--------|------|
| **Day 1** | C-10.5 quota-aware routing | C-3 restic script (local) | Agent spec + session hook | Review C-4a.5 escalation |
| **Day 2** | C-11 property tests (OOM + SoulStore) | C-3 restic off-site (B2) | L1→L2 distillation | Arbitrate conflicts |
| **Day 3** | C-9 GenerationPolicy extract | V-1 credential rotation | L3 axiom extraction | Verify temple-grade |
| **Day 4** | M21 fix 3 fallback tests | V-1 integration test | Cross-pollination logic | Final review |
| **Day 5** | Integration + CI | Restore test | Pipeline hardening | **SPRINT COMPLETE** |

---

## §13 Research References (For Implementation)

| Area | Key References |
|------|----------------|
| **Hypothesis Async FSM** | GitHub #4107, MarkTechPost 2026-04-18, TechOral 2026-06-14, oneuptime 2026-01-30 |
| **Restic + B2** | byte-guard.net 2026-06-13, Backblaze 2026-06-26, TechFuelHQ 2026-06-04, 47Network 2026-02-24 |
| **MCP Streamable HTTP** | MCP.Directory 2026, Zylos 2026-03-08, AWS Labs #72, AgentMarketCap 2026-04-06, OpenAI Community 2026-04-02, Baeseokjae 2026-05-05, Upendra Sengar 2026 |
| **LLM Distillation** | Stratos (arXiv:2510.15992, AAAI 2026), Mems (2026-03-23), RecSys 2025, LLM-Distillery, llm_tools, KD Survey 2026-04-25 |
| **Quota-Aware Routing** | TrueFoundry 2026-02-20, CallMissed 2026-05-31, AppScale 2026-05-21, QuotaRouter, DigitalOcean 2026-07-13 |

---

*⬡ OMEGA ⬡ MAAT ⬡ AP-NEXT-STEPS ⬡ 2026-07-22 ⬡*

**Kali Verdict: APPROVED WITH AMENDMENTS (§11) — RESEARCH ENHANCED**