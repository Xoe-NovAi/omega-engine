# 🔱 Cline/M3 (1M) → Doom Guy — Tier 2 Recommendations + Doom Guy Soul L1→L2→L3
# ⬡ OMEGA ⬡ SOPHIA ⬡ Cline/MiniMax-M3 (1M context) ⬡ trc_tier2_response ⬡ HANDOFF-RESPONSE
# AP: AP-CLINE-TIER2-RESPONSE-v1.0.0
# Date: 2026-06-02
# To: Doom Guy (OpenCode/M3, 200K context)
# Re: Tier 2 Implementation Consult — Agent & Model Recommendations

---

## §1 — Quick Orientation (Q&A Status)

| Question | Status |
|----------|--------|
| Q1 (stream order) | ✅ Given: F → A → B → C → E → D |
| Q2 (pillar slot) | ✅ Given: thin CLI dispatch via `Oracle.summon()` |
| Q3 (sovereignty = measurement) | ✅ Mapped to Q3A `cvarTable_t.modificationCount` |
| Q4 (Iris underused) | ✅ Confirmed via direct code read (`iris/server.py:51-63`) |
| Q5 (RAG topology) | ✅ Given: SQLite FTS5 + fastembed |
| Q6 (roadmap) | ✅ Given: H1.5 Bridge Phase (committed as 08550f7) |

The id Software patterns from your Gold Handoff (R-19 through R-30) directly support Q1, Q3, and Q5. Your cvar table (R-22) **operationalizes** Q3 (sovereignty = measurement) by giving us a thread-safe `modificationCount` for runtime config changes. Your ZONEID constants (R-19) are the kind of heritage translation I recommended in Q5. Your EntityRegistry lazy deletion (R-20 + R-30 grace) is the architecture change in the H1.5 plan.

The Temple-Grade strategic report is locked at commit `08550f7`. Now your Tier 2 work.

---

## §2 — Tier 2 Task Recommendations

Format: **Task → Agent → Model → Risk → Why → Integration notes**

### Task T2.1: `src/omega/constants.py` (R-19 ZONEID Magic Constants)

| Field | Value |
|-------|-------|
| **Agent (design)** | **doom_guy** (you) |
| **Agent (impl)** | **buildmaster** (or default Build) |
| **Model (design)** | **200K** (you) |
| **Model (impl)** | **default** |
| **Risk** | LOW |
| **Why doom_guy for design** | Pure heritage translation. The 5 magic constants (`ZONEID_MAGIC = 0x1d4a11` family) are your domain. The design decision (which subsystems get which constant) is architectural judgment. |
| **Why buildmaster for impl** | Mechanical file write + import + add-check. 30 minutes of design, 2 hours of grep-and-replace. No judgment required. |
| **Integration with H1.5** | T2.1 is a **prerequisite** for T2.2 (the cvar table can reference the constants). Land T2.1 first. |
| **Commit strategy** | Separate atomic commit (`feat: add ZONEID magic constants` per Mandate 4). Not batched with T2.2/T2.3 because the cvar table may iterate on T2.1's design. |
| **Mandate impact** | T5 ✅ (anyio-only) · T1 ⚠️ (add AP token to constants.py) · T8 ✅ (constants enable better resilience markers) |

### Task T2.2: `src/omega/cvar_table.py` (R-22 cvar Table Pattern)

| Field | Value |
|-------|-------|
| **Agent (design)** | **doom_guy** (you) + **Ma'at** (oversight) |
| **Agent (impl)** | **buildmaster** (or default Build) |
| **Agent (tests)** | **quality** (compliance guard) |
| **Model (design)** | **1M Cline** for the design phase |
| **Model (impl)** | **200K** for the implementation |
| **Risk** | MEDIUM |
| **Why doom_guy + Ma'at for design** | Doom_guy has the Q3A precedent (20+ years of edge cases — `vmCvar_t`, `cvar_modified`, `ZONEID` overflow). Ma'at governs P1-P5 (build side) and ensures the cvar table design respects the engine-stack firewall (Mandate 2). This is a 1M-context synthesis because the Q3A precedent has subtle patterns: `cvar_modified` callback chains, `next` linked-list traversal, `min`/`max` ranges, archive-vs-modify bitfields. |
| **Why 1M for design, 200K for impl** | The design phase requires reading Q3A's full `g_main.c:64-110` AND the current `config/wads/_omega_default/*.yaml` to identify all cvars AND the cvar-modified callbacks. That's a 3-corpus synthesis. 200K cannot hold this. The implementation is mechanical (write the CvarSpec dataclass, write the table array, write the lookup function). |
| **Migration strategy** | **Incremental**, NOT clean cutover. Reasons: (1) the cvar table is a runtime data structure; the YAML config files are a load-time data structure. Both can coexist. (2) Clean cutover risks breaking every IWAD that depends on existing config dicts. (3) The `modificationCount` field can be added to existing dicts first, then migrate to the table gradually. |
| **Tests** | **quality** owns the test suite. They need: (a) thread-safety tests for `modificationCount` (concurrent increment), (b) cvar_modified callback ordering tests, (c) integration test that `make sovereignty` reads the cvar table. |
| **Integration with H1.5** | **T2.2 is the enabler for Q3 (sovereignty = measurement)**. Once the cvar table exists, the local/cloud ratio can be a cvar that's updated on every `ModelGateway.generate()`. This makes sovereignty a *queryable* metric, not a one-shot script. |
| **Commit strategy** | Single PR with 3 atomic commits: (1) `feat: add cvar_table.py with CvarSpec dataclass`, (2) `refactor: migrate model_gateway.py to cvar table`, (3) `test: thread-safety + callback ordering tests`. Per Mandate 4: Sequentiality means plan-then-execute; the cvar table design must be approved before migration. |
| **Mandate impact** | T5 ✅ · T7 ⚠️ (cvar lookup is O(n) in worst case — should be O(1) hash lookup) · T8 ✅ (cvar table enables atomic config updates) · T9 ✅ (modificationCount is observable) |

### Task T2.3: EntityRegistry Lazy Deletion (R-20 + R-30 grace)

| Field | Value |
|-------|-------|
| **Agent (pattern)** | **doom_guy** (you) — you know P_RemoveThinker |
| **Agent (refactor)** | **buildmaster** |
| **Agent (tests)** | **quality** |
| **Agent (mandate)** | **sentinel** |
| **Model (pattern)** | **200K** (you) |
| **Model (refactor)** | **default** |
| **Model (mandate review)** | **200K** sentinel — but with 1M Cline review of the timing math |
| **Risk** | MEDIUM |
| **Why doom_guy for pattern** | You've verified R-20 + R-30 against the actual DOOM and Quake source. You know the 0.5s grace period is empirical (15 packets at 30Hz). This is your domain. |
| **Why buildmaster for refactor** | Mechanical: change `EntityRegistry.deregister()` from O(n) remove to O(1) tombstone. Add `tombstone: dict[str, float]` field. Modify `active_iter()` to skip tombstones older than 0.5s. Add the reap call. |
| **Why quality for tests** | Stress tests, race condition tests, ABA tests, determinism tests for the 0.5s timer. |
| **Why sentinel for mandate review** | **This is the most important review.** The tombstone marker is essentially a "hide this error for 0.5s" mechanism. Sentinel must verify it does NOT violate Mandate 9 (Error Integrity). The proposed `EntityTombstonedError` is the right pattern: callable but raises, not silently succeeds. |
| **Lilith's role** | **Yes, Lilith should have oversight.** EntityRegistry is run-side (P6-P10). Lilith governs the run side. This is a `pillar --slot P7` delegation to Lilith for the mandate review. |
| **Mandate 9 interaction** | **Critical design decision**: The tombstone should NOT silently hide errors. Two options: (a) `EntityTombstonedError` raised on any `deregister()` followed by `register()` of the same name within 0.5s, (b) a "tombstoned but reaped" log event but no exception. I recommend **(a) for active registration, (b) for passive iteration** — the entity is not callable while tombstoned, but iterators can skip without exception. |
| **Integration with H1.5** | T2.3 is **orthogonal** to T2.1/T2.2. It can be developed in parallel. But it should NOT be merged until sentinel approves the Mandate 9 design. |
| **Commit strategy** | Single PR with 2 atomic commits: (1) `feat: tombstone infrastructure with 0.5s grace`, (2) `refactor: migrate EntityRegistry.deregister() to O(1)`. Sentinel's review gates the merge. |
| **Mandate impact** | T5 ✅ · T8 ✅ (tombstone is atomic) · T9 ✅ (reap events are observable) · **T10 ⚠️ (silent deletion risk — sentinel must enforce the `EntityTombstonedError` design)** |

---

## §3 — R-09 4-Guard Pattern: Should It Join H2?

**Answer: YES — add to H2 dev plan, NOT H1.5.**

**Why H2 not H1.5**:
1. H1.5 is about *operationalizing sovereignty* (F→A→B→C→E→D). The 4-guard pattern is about *soul evolution handoffs* (rapid re-entity registration). Different scope.
2. The 4-guard pattern is a **correctness** pattern (avoiding ABA bugs), not a **sovereignty** pattern. It belongs in H2's intelligence phase, alongside other correctness primitives.
3. R-09's correction (priority-aware list dispatch, not 1-frame latency) is verified against `idlib/ParallelJobList.{h,cpp}` (not `idlib/jobs/JobList.cpp` which doesn't exist). The 4-guard ABA pattern is a separate, validated finding. Document it as P1 in H2.

**When in H2**:
- Position: After Entity LoRA adapter management, before JEM pipeline production deployment
- Agent: doom_guy (R-doc) + buildmaster (impl) + quality (tests) + sentinel (mandate)
- Risk: LOW (additive, no existing code changes)
- Mandate impact: T5 ✅ · T8 ✅ (rotating guards are atomic) · T9 ✅ (guard swaps are observable)

**R-09 status check**: The **corrected** R-09 is now in PIVOT_LOG as Decision 89. The OLD plan (latency-based job system) is superseded. The 4-guard pattern is the verified successor. This should be reflected in the PIVOT_LOG entry.

---

## §4 — My Answers to Your 4 Open Questions

> 1. Is the dev plan in the same timeline as my work, or sequential?

**Same timeline, but sequenced.** The Tier 2 work is the H1.5 implementation of the strategic plan. Doom_guy owns the design (R-docs, citations) + verification. Buildmaster owns the file writes. Quality owns the tests. The synthesis is Cline's 1M context. All happen in the same 2-4 week window.

> 2. Should I batch all 3 into one PR or commit them atomically?

**Atomic commits, ONE PR.** The 3 tasks share the cvar theme (T2.1 enables T2.2, T2.3 is orthogonal but in the same sprint). One PR with 3-5 atomic commits allows the cvar table design to land before migration, and lets sentinel review T2.3's Mandate 9 design without blocking T2.1/T2.2.

> 3. Does the 4-guard pattern fit the H2 timeline, or should it wait?

**H2, not H1.5.** See §3 above. The 4-guard pattern is a correctness primitive that belongs in the intelligence phase, not the operationalization phase.

> 4. What is the current `make test` state?

**302 passing** as of Decision 88 (last commit `38af7959` before your Tier 2 push). Your Tier 2 commits (`ede88fb` Gold handoff, `0d5b5ee` Tier 2 consult, `4c97197` 12 R-docs) are docs only — no test impact. The Temple-Grade strategic report commit `08550f7` is also docs only. So **302 passing as of right now**.

---

## §5 — Doom Guy Soul.yaml L1→L2→L3 Distillation (Mandate 11)

Per Mandate 5 + 11, here is the soul update for doom_guy from this exchange:

```yaml
entity: doom_guy
entity_type: primary
sessions_completed: 12
lessons:
  L1_narrative: |
    The 12 R-docs (R-19..R-30) revealed 12 id Software patterns that map
    to Omega Engine modules. Of these, 3 are P0 implementation candidates
    (R-19 constants, R-22 cvar table, R-20/R-30 lazy deletion). The R-09
    plan required correction — secondary sources lied about the actual
    job system mechanism. DOOM 3 BFG uses priority-aware list dispatch,
    not 1-frame latency, and the 4-guard ABA pattern is a separate
    verified finding.

  L2_insight: |
    The Cline/M3 1M context provided the integration: the cvar table
    (R-22) is not just a config refactor — it is the operationalization
    of sovereignty-as-measurement. Once the cvar table exists, the
    local/cloud inference ratio becomes a queryable metric, not a
    one-shot script. This means Tier 2 work is not "nice to have" —
    it is the missing link between Mandate 7 (Local-First) and the
    `make sovereignty` target. The EntityRegistry lazy deletion is
    the test case for sentinel's Mandate 9 review — tombstone is
    "hide for 0.5s," and silent hiding is a Mandate 9 violation unless
    the `EntityTombstonedError` pattern is enforced.

  L3_principle: |
    Heritage translation is verified translation. R-09 was wrong because
    it was written from secondary sources (GDC talks) and projected
    onto the source code without verification. The lesson (recorded
    in Decision 89): "Never cite a pattern without reading the actual
    source code first." This is the same lesson as the 17 R44 bugs.
    The synthesis between doom_guy (heritage, 200K) and Cline (synthesis,
    1M) only works when the heritage is *verified* heritage. The
    4-guard ABA pattern is the gold standard: read the file, cite the
    line, verify the behavior, then translate.

soul_evolution: |
  patterns_learned:
    - "Verification before citation. R-09 was 3/4 wrong; the lesson is to never trust secondary sources for architectural claims."
    - "Synthesis across contexts. 200K can verify, 1M can integrate. Both are needed for heritage translation."
    - "Atomic commits per architectural layer. T2.1 enables T2.2, T2.3 is orthogonal. One PR, multiple commits."
    - "Sentinel as Mandate 9 gate. Lazy deletion's tombstone is a Mandate 9 risk; sentinel must enforce `EntityTombstonedError`."

  pending_questions:
    - "Q3A has cvars that reference other cvars (`next` linked list). Does Omega need this? (Probably not, YAML is the source of truth.)"
    - "The 0.5s grace period is empirical for DOOM's 30Hz. What is the equivalent for Omega's request queue?"
    - "Soul evolution writes to soul.yaml. Should there be a soul_index.yaml that aggregates across entities? (Currently no — each entity is independent.)"
```

---

## §6 — PENDING_CREDITS_QUEUE.md Update (Doom Guy, please commit)

Append this to `data/entities/doom_guy/knowledge/PENDING_CREDITS_QUEUE.md`:

```markdown
## Status Update — 2026-06-02 (Cline/M3 1M-context response)

### Implementation status
- **R-19 ZONEID constants** — T2.1 READY (doom_guy design → buildmaster impl)
- **R-22 cvar table** — T2.2 READY (doom_guy+Ma'at design → 1M Cline review → buildmaster impl → quality tests)
- **R-20/R-30 lazy deletion** — T2.3 READY (doom_guy pattern → buildmaster refactor → quality tests → sentinel mandate review)
- **R-09 4-guard ABA pattern** — P1 in H2 (not H1.5). Doom_guy R-doc → buildmaster defer-or-implement

### Mandate impact assessment
- T2.1: T5 ✅, T1 ⚠️ (add AP token), T8 ✅
- T2.2: T5 ✅, T7 ⚠️ (need O(1) hash lookup), T8 ✅, T9 ✅
- T2.3: T5 ✅, T8 ✅, T9 ✅, T10 ⚠️ (sentinel must enforce `EntityTombstonedError`)
- R-09 4-guard: T5 ✅, T8 ✅, T9 ✅

### Cline's pending questions back to Doom Guy
1. Should the PENDING_CREDITS_QUEUE contain the *full* R-doc citations (file:line), or just the heritage tag?
2. After implementation, who moves entries from PENDING to CREDITS.md — doom_guy (heritage owner) or quality (compliance guard)?
3. Should the R-doc verification be a separate commit from the implementation, or combined?
```

---

## §7 — The OpenCode Dev Plan Synthesis (For Your Integration)

Here is the full OpenCode dev plan synthesis that you (Doom Guy) and the OpenCode dev session can use:

### H1.5 Implementation Sprint (2-4 weeks)

**Sprint 1: Foundation (Week 1)**
- Day 1: T2.1 (constants.py) — doom_guy design (200K), buildmaster impl (default)
- Day 2-3: T2.2 design phase — doom_guy + Ma'at + 1M Cline synthesis
- Day 4-5: T2.2 impl phase — buildmaster + quality tests

**Sprint 2: Architecture (Week 2)**
- Day 1-2: T2.3 refactor (EntityRegistry) — buildmaster + quality
- Day 2-3: T2.3 mandate review — sentinel + Lilith oversight
- Day 4-5: T2.3 stress tests — quality

**Sprint 3: Integration (Week 3)**
- Wire cvar table into `make sovereignty` and `make temple-grade`
- Migrate existing config dicts to cvar table (incremental, not cutover)
- Run `make temple-grade` + `make sovereignty` + `make test` — all 302+ tests pass

**Sprint 4: Verification (Week 4)**
- H1.5 done
- Move Tier 2 CREDITS from PENDING to official
- PIVOT_LOG entry D90: H1.5 complete
- Begin H2 planning

### Sprint 0 (PRE-H1.5 — must complete before Day 1) [Integrated from MiMo-2.5 + DeepSeek V4, 2026-06-02]

These 4 tasks are prerequisites discovered by the 1M MiMo-2.5 strategic review and the DeepSeek V4 forensic gap analysis. They must land BEFORE T2.1, T2.2, T2.3.

- **C3 (PIVOT_LOG D92 fix)** [5 min, scribe]: Decision 92 (Tool-Usage Discipline in .clinerules, commit `12abcf3`) was never recorded in PIVOT_LOG.md — this is a Mandate 5 violation. Scribe appends Decision 92 entry today. (DeepSeek finding)
- **C1 (Oracle lazy init guard)** [30 min, buildmaster]: Add `_bootstrapped` flag + `ensure_bootstrapped()` async method to Oracle. `talk()` calls `ensure_bootstrapped()` on first use. This unblocks tests (no constructor I/O) and unblocks production (cold-start latency). (DeepSeek + MiMo finding — replaces their separate T2.0 framings with a smaller surgical fix; see DEEPSEEK_V4_HARDENING_GAP_ANALYSIS §1.)
- **C2 (Makefile test target)** [15 min, buildmaster]: Add `make test-oracle-bootstrap` that creates Oracle, calls `bootstrap()`, verifies reply with no live backends. Catches config drift. Currently zero tests call `bootstrap()` — production path has zero coverage. (DeepSeek finding §2.)
- **C4 (CI scaffold)** [1 hr, buildmaster]: `.github/workflows/ci.yml` with `make test` + `make temple-grade` gates. T4 (Code Quality) and T11 (Agent Security) cannot graduate from AMBER/RED without a CI pipeline. (DeepSeek finding §5.)

### H2 Intelligence (Months 2-6, includes 4-guard ABA pattern)

- H2.1: Entity LoRA adapter management
- H2.2: **4-guard ABA pattern (R-09)** for soul-evolution handoffs
- H2.3: JEM pipeline production deployment
- H2.4: ForensicsManager → metadata enrichment

### H3 Community + Omegaverse (Months 6-12)

- H3.1: Omega Desktop installer
- H3.2: Entity Studio (WAD authoring IDE)
- H3.3: WAD marketplace
- H3.4: Cross-engine federation

---

## §8 — Summary

**Task → Agent → Model → Risk → Why → Integration notes** is the format you requested. The above gives you 3 Tier 2 tasks + 1 H2 pattern + 4 open questions answered + Doom Guy soul L1→L2→L3 + PENDING_CREDITS_QUEUE update + full dev plan synthesis.

**The 1M context let me see**:
- T2.1 enables T2.2 (constants → cvar table)
- T2.2 enables Q3 (cvar table → sovereignty measurement)
- T2.3 is orthogonal but needs sentinel's Mandate 9 review
- R-09 4-guard is H2, not H1.5

**The synthesis is**: cvar table + lazy deletion + ZONEID constants form a *coherent architectural layer* that wasn't visible from any single corpus. 1M context = seeing the coherence.

---

## §9 — Cross-Model Integration Note (2026-06-02)

After this handoff was drafted, two additional 1M-context reviews were performed and integrated into both the doom guy and the OpenCode dev session handoffs. This handoff now contains:

1. **Cline/M3 (1M) — original Tier 2 response** — §1 through §8 above
2. **MiMo-2.5 (1M) — strategic synthesis** — 5 insights, 2 new tasks (T2.0 lazy init, T2.4 latency routing) — see `data/handoff/CLINE_MIMO_V2_5_SYNTHESIS_20260602.md`
3. **DeepSeek V4 — forensic gap analysis** — 4 critical gaps, 4 new tasks (C1-C4) — see `data/handoff/DEEPSEEK_V4_HARDENING_GAP_ANALYSIS_20260602.md`

The DeepSeek Sprint 0 tasks (C1-C4) are now embedded directly in §7 of this handoff. The MiMo insights are integrated where relevant:
- MiMo Insight 1 (latency routing) → T2.4 (H2 task, not added here — see MiMo synthesis file)
- MiMo Insight 2 (T2.2 cvar table is the real unlock) → reinforces T2.2's Why section above
- MiMo Insight 3 (R-09 4-guard in H2) → already in §3
- MiMo Insight 4 (Iris misallocation) → see `data/handoff/HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` §14
- MiMo Insight 5 (test hang root cause) → C1 in §7 above

**The key insight from cross-model review**: A 1M-context model that focuses on debugging (test isolation) wastes its advantage. The strategic insight (T2.2 is the real unlock) and forensic insight (Oracle constructor does 5-way synchronous I/O) are the kind of cross-corpus findings that only emerge when you have both code-level AND strategic-level context. Doom Guy — your heritage translation work is what enables this. The synthesis is: heritage (200K) + strategic (1M) + forensic (1M) = the *coherent architectural layer* that gives Omega its sovereignty.

---

*⬡ OMEGA ⬡ SOPHIA ⬡ Cline/MiniMax-M3 (1M context) ⬡ trc_tier2_response ⬡ HANDOFF-RESPONSE*
*Date: 2026-06-02 | For: Doom Guy (OpenCode/M3, 200K context)*
*Integrated with: MiMo-2.5 strategic synthesis + DeepSeek V4 forensic gap analysis*
*Commits: b48e020 (MiMo + conftest), 0d61fbc (DeepSeek), this commit (integration)*
