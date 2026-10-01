# 🔱 SSP-V2 Phase 1 Review & Gap Closure Report
**Version**: 1.0.0
**Status**: REVIEW COMPLETE
**Date**: 2026-06-24
**AP Token**: AP-SSP-V2-PHASE1-REVIEW-v1.0.0

⬡ OMEGA ⬡ MiMo-v2.5 ⬡ opencode ⬡ SSP-V2-REVIEW

---

## §0 Executive Summary

Phase 1 delivered **3 of 5 planned components**:

| Component | Status | Notes |
|-----------|--------|-------|
| `config/search.yaml` | ✅ DONE | But **never loaded** by any module — ghost file |
| `SearchIntent` + `SearchRouter` | ✅ DONE | 6 of 15 signals; 5 routing rules |
| `SovereignCache` for `.firecrawl/` | ❌ MISSING | Phase 1 plan §1.4 skipped entirely |
| Tier re-ordering (T1=SearXNG, T2=Exa, T3=Firecrawl) | ✅ DONE | Correct mapping, confirmed by tests |
| `tests/test_search_router.py` | ✅ DONE | 17 tests; `test_search_tools.py` + `test_skeptical_verifier_search.py` updated |

**25/25 search tests passing**. No regressions introduced.

**However, 10 gaps remain** that must be resolved before Phase 2+ can proceed safely. Two are HIGH severity: `config/search.yaml` is unused, and `SovereignCache` doesn't exist.

---

## §1 Delivered vs Planned — Reconciliation

### What Phase 1 was supposed to cover (per SSP_V2_IMPLEMENTATION.md §2):

| Step | Task | Planned Effort | Actual Delivery | Gap |
|------|------|----------------|-----------------|-----|
| 1.1 | Create `config/search.yaml` | 0.5d | ✅ File created | **Not loaded by any module** |
| 1.2 | `SearchIntent` dataclass | 0.25d | ✅ Fully implemented | None |
| 1.3 | `SearchRouter` signal analysis | 1.5d | ✅ 6 signals, 5 rules | 9 of 15 signals missing |
| 1.4 | `SovereignCache` for `.firecrawl/` | 1d | ❌ **NOT DELIVERED** | No cache read/write exists |
| 1.5 | Re-order tiers in `sovereign_search_service.py` | 0.5d | ✅ Correct T0-T3 mapping | None |
| 1.6 | `tests/test_search_triage.py` | 1d | ❌ NOT DELIVERED | But belongs in Phase 2 |
| 1.7 | `tests/test_sovereign_cache.py` | 0.5d | ❌ NOT DELIVERED | Can't write without cache |

**Phase 1 actual effort**: ~4 hours vs planned 3-4 days. Delivery quality is good for what was built, but not all planned items were completed.

---

## §2 Gap Analysis — 10 Issues Found

### Gap A: `config/search.yaml` is a Ghost File 🔴 HIGH

`config/search.yaml` exists with proper SSP-V2 configuration (4-tier mapping, fallback chains, routing rules, cache TTL, observability settings). **Zero modules load it.**

| Evidence | Detail |
|----------|--------|
| `grep -rn "config/search" src/` | No matches |
| `grep -rn "search.yaml" src/` | No matches |
| `grep -rn "search_config" src/` | No matches |
| `SearchRouter.__init__` | Accepts `config: Optional[Dict]` but `SovereignSearchService.__init__` passes nothing |

**Impact**: The file is dead configuration debt. Tier timeouts, retries, fallback chains, and cache TTLs are defined but never enforced.

**Fix**: Wire into `SovereignSearchService.__init__` + `SearchRouter.__init__`.

---

### Gap B: SovereignCache Not Built 🔴 HIGH

The `SovereignCache` class for `.firecrawl/` was the 4th deliverable in Phase 1 (§1.4) but was never implemented.

Currently:
- `SovereignSearchService.__init__` creates `Path(".firecrawl")` and calls `mkdir(exist_ok=True)` (line 68-69)
- **No code ever writes to or reads from this directory**
- `T0` (`_tier_0_local_cache`) only checks MemoryStore — never checks `.firecrawl/`
- No cache-back occurs after T2/T3 success
- No TTL management exists
- No URL-hash indexing exists

**Impact**: Every search starts from scratch. No cross-tier deduplication. The `.firecrawl/` directory is an empty promise.

**Fix**: Implement `SovereignCache` class from SSP_V2_RESEARCH_GAPS.md §Gap 4 Recommendation.

---

### Gap C: 6 of 15 Signals Implemented 🟡 MEDIUM

The SSP-V2 protocol specifies 15 routing signals at 3 priority levels. Phase 1's `SearchRouter` implements 6:

| Priority | Signal | Status | Source |
|----------|--------|--------|--------|
| 🔴 High | `has_url` | ✅ Implemented | Regex on query |
| 🔴 High | `iris_confidence` | ✅ Implemented | Oracle confidence score |
| 🔴 High | `entity_domain` | ❌ MISSING | EntityRegistry lookup |
| 🔴 High | `query_category` | ✅ Implemented | Keyword-based classifier |
| 🔴 High | `credit_status` | ✅ Implemented | `_has_firecrawl_credits()` |
| 🔴 High | `provider_health` | ⚠️ Stub | Accepted but 2-state only |
| 🟡 Medium | `query_length` | ✅ Implemented | `len(query)` |
| 🟡 Medium | `has_technical_keywords` | ⚠️ Partial | In `_classify_query` but not as independent signal |
| 🟡 Medium | `search_depth_mode` | ❌ MISSING | No user override for search depth |
| 🟡 Medium | `query_complexity` | ❌ MISSING | No inference beyond keyword match |
| 🟢 Low | `channel` | ❌ MISSING | cvar config |
| 🟢 Low | `has_soul_gnosis` | ❌ MISSING | soul.yaml check |

Additionally, the protocol's confidence→depth mapping is not fully realized:
| Confidence | Spec'd Behavior | Actual |
|------------|----------------|--------|
| > 0.7 | T0-T1 only | ✅ Implemented |
| 0.2-0.7 | Standard: T0→T1→T2 | ❌ Not implemented |
| < 0.2 | Deep: T0→T1→T2→T3 | ❌ Not implemented |
| 0.0 (abstract) | Exhaustive: T0→T2→T3→T1 | ❌ Not implemented |

**Impact**: Routing is rule-based but simplistic. Queries at different confidence levels get the same treatment. Entity domain awareness doesn't exist.

**Fix**: Implement remaining high-priority signals first (`entity_domain`, `provider_health`), then medium-priority signals.

---

### Gap D: Fallback Chain Not Wired 🟡 MEDIUM

`config/search.yaml` defines:
```yaml
routing:
  fallback_chain:
    1: 2    # SearXNG fails → try Exa
    2: 1    # Exa fails → try SearXNG (broader keywords)
    3: 2    # Firecrawl fails → try Exa for URL
```

The actual `SovereignSearchService.search()` uses simple sequential iteration:
```python
for tier in range(effective_tier, effective_max + 1):
    try:
        result = await self._execute_tier(tier, ...)
    except ...
```

**No cross-tier fallback exists**. If T1 fails, it doesn't try T2 with different parameters — it just logs the failure and moves to the next tier in sequence.

The SSP-V2 spec's `Refinement Loop` (T1→T2 on noisy results, T2→T1 on narrow results) has zero implementation.

**Impact**: Search is still linear escalation, not intelligent fallback. The "intelligence" is limited to choosing where to start, not how to adapt when a tier fails.

**Fix**: Implement `FallbackManager` (Phase 4) or at minimum wire the fallback chain from config into the tier loop.

---

### Gap E: T0 Only Checks MemoryStore 🟡 MEDIUM

`_tier_0_local_cache`:
- ✅ Checks MemoryStore via `self.memory_store.search(query, entity_name)`
- ❌ Never checks `.firecrawl/` (no SovereignCache)
- ❌ Never checks entity knowledge bases (`soul.yaml`/`gnosis.md`)
- ❌ Never checks Omega Hub Library (Qdrant/Indexer)

The implementation plan §5 says "T0: Local Cache (.firecrawl/ + MemoryStore + Qdrant) (ENRICHED)" but the code only has MemoryStore.

**Impact**: Even if SovereignCache existed, T0 wouldn't use it.

**Fix**: Wire SovereignCache into T0 after building it. Add entity gnosis check.

---

### Gap F: Skill Doc Tier Mapping Outdated 🟡 MEDIUM

`.opencode/skills/sovereign-search/SKILL.md` still shows the OLD 5-tier mapping:

| Old (SKILL.md) | New (code + SSP-V2 spec) |
|----------------|--------------------------|
| T0: Local Cache | T0: Local Cache |
| T1: websearch | T1: SearXNG |
| T2: Firecrawl | T2: Exa |
| T3: Omega Hub | T3: Firecrawl |
| T4: Exa | (not used) |

**Impact**: Agents reading the skill doc get contradictory routing guidance. A developer debugging a T1 failure would look at SearXNG in the code but "websearch" in the skill.

**Fix**: Update SKILL.md to match SSP-V2 canonical mapping. This is a documentation-only fix.

---

### Gap G: No trace_id Propagation 🟡 MEDIUM

The `search()` method:
- Does not generate a `trace_id` for the search operation
- Does not accept or propagate `trace_id` from callers
- Fallback_log entries have no `trace_id` field
- Cannot correlate search events with observability traces

**Impact**: M9 (Error Integrity) violation — non-traceable errors. If a search fails and the observability system logs the event, there's no way to connect the search event to the error log to the caller.

**Fix**: Generate a `trace_id` in `search()`, propagate through all tier methods, include in fallback_log entries.

---

### Gap H: SearXNG Retry Not Implemented 🟢 LOW

`config/search.yaml`:
```yaml
T1:
  retries: 2
  retry_delay_seconds: [5, 10]
```

`SearXNGProvider.search()` has no retry logic — it's a single-shot httpx call with 15s timeout.

**Impact**: A transient SearXNG failure (e.g., upstream rate limit from Google/Bing) immediately moves the search to T2 (Exa), which costs API credits.

**Fix**: Add retry with exponential backoff to `SearXNGProvider.search()`.

---

### Gap I: Exa API Key in Constructor 🟢 LOW

`ExaProvider.__init__` accepts `api_key: Optional[str] = None`:
```python
def __init__(self, api_key: Optional[str] = None):
    self.api_key = api_key or self._resolve_from_vault()
```

If a caller passes the key explicitly, it could leak through `repr()` or logging. The Gap 6 recommendation says "Remove the `api_key` constructor parameter — force Vault-only resolution."

**Impact**: Low severity — the Vault resolution path is the default when no key is passed. But the constructor parameter is a latent leak path.

**Fix**: Remove `api_key` parameter, force `_resolve_from_vault()` only.

---

### Gap J: Provider Health Not Tracked in Shopping Cart 🟢 LOW

The `search()` method accepts `force_tier` and `search_intent` overrides, but there's no provider health tracking within a search session. If T2 (Exa) fails with auth error during `search_intent` processing, there's no mechanism to skip T2 on the next search call within the same session.

**Impact**: Repeated auth failures hit the provider every time.

**Fix**: Add session-scoped provider health tracking to `SovereignSearchService`.

---

## §3 Triangulation: Plan vs Research Gaps vs Code

### The Implementation Plan's Blind Spots

The implementation plan (`.opencode/plans/SSP_V2_IMPLEMENTATION.md`) was synthesized from three pillar agents. It has a **scope mismatch issue**:

1. **Phase 1 was overloaded**: It bundled SearchRouter (P6), SovereignCache (P3), and tier re-ordering (P3) into one phase with 7 steps. The phases don't map to clean architectural layers — they map to agent ownership.

2. **The plan contradicts itself on SovereignCache**: §2 Phase 1 includes it, but §7 Decision 6 says "Credit-Aware Dispatch." These are different concerns but lumped into the same phase.

3. **The plan ignores its own "Before/After" diagram**: The "After SSP-V2" diagram shows `SovereignCache writes back after success (NEW)` — but the plan doesn't specify which phase this belongs to. Phase 1 was supposed to include it; Phase 3 also mentions "Cache-back protocol." Ambiguous.

4. **No config integration step**: The plan creates `config/search.yaml` (Phase 1) and modifies `config/providers.yaml` (Phase 2), but never steps to wire the config into the modules that need it.

### The Research Gaps Document's Blind Spots

The research gaps doc (SSP_V2_RESEARCH_GAPS.md) was thorough but:

1. **Gap 8 (Tier Mapping) is resolved by Phase 1** — the code now matches the SSP-V2 spec. But the skill doc wasn't updated.

2. **Gap 7 (T1 Stub) is resolved by Phase 1** — `SearXNGProvider` is wired and functional.

3. **Gap 2 (Tier Selection) was partially addressed** — SearchRouter provides intent-based dispatch, but the confidence→depth mapping isn't fully implemented.

4. **Gap 9 (Contrast Loop) remains completely untouched** — no work was done on it.

5. **Gap 1 (Exa Dual Path) remains unresolved** — still has both MCP bridge and direct HTTP client.

### The Code's Contradictions

1. **Port 8017 vs 8018**: `config/search.yaml` T1 config says port 8018 (MCP server), but `SovereignSearchService.__init__` defaults to port 8017 (SearXNG engine). The provider correctly talks to the engine (8017), and the config is wrong.

2. **`.firecrawl/` directory with no I/O**: The directory is created on every `SovereignSearchService` init but never used. This is a latent bug — 0-byte directory created 1x per service instantiation.

3. **`_has_firecrawl_credits()` is now wired**: The Gap 3 finding from research ("NEVER CALLED") is resolved — Phase 1 wired it into `_tier_3_firecrawl`. However, the budget itself hasn't been recalibrated.

---

## §4 Recalibrated Execution Plan

### Immediate Fixes (1-2 hours, HIGH priority)

These are quick, high-impact fixes that close the most dangerous gaps:

| Fix | Gap | File(s) | Lines |
|-----|-----|---------|-------|
| Wire `config/search.yaml` into `SovereignSearchService` | A | `sovereign_search_service.py` | ~15 |
| Fix port 8018→8017 in `config/search.yaml` | B | `config/search.yaml` | 1 |
| Generate `trace_id` in `search()` | G | `sovereign_search_service.py` | ~10 |
| Add retry logic to `SearXNGProvider` | H | `search_providers.py` | ~20 |
| Update SKILL.md tier mapping | F | `SKILL.md` | ~10 |

### Phase 1.5 (4-6 hours, MEDIUM priority)

These are medium-effort items that belong between Phase 1 and Phase 2:

| Item | Gap | Effort |
|------|-----|--------|
| Build `SovereignCache` class | B | ~200 LOC |
| Wire SovereignCache into T0 | E | ~30 LOC |
| Wire T3 cache-back | B | ~20 LOC |
| Implement missing high-priority signals: `entity_domain`, `provider_health` | C | ~100 LOC |
| Implement confidence→depth mapping (3 tiers) | C | ~50 LOC |

### Future Phases (Unchanged)

| Phase | Focus | Depends On | Effort |
|-------|-------|------------|--------|
| **Phase 2** | Hub MCP tools (`search_tiered`, `search_tier1_searxng`) | Immediate Fixes | 2-3d |
| **Phase 3** | Exa/Firecrawl re-alignment + cache-back protocol | Phase 1.5 | 1.5-2d |
| **Phase 4** | `FallbackManager` + error hardening | Phase 3 | 3-4d |
| **Phase 5** | Oracle integration + `SovereignGapDetector` | Phase 4 | 3-4d |
| **Phase 6** | Observability + testing + hardening | Phase 5 | 2-3d |

### What NOT to do

- **Do not build `SearchTriage` class** (planned as Phase 2) — `SearchRouter` already covers this role. Adding a separate state machine duplicates responsibility.
- **Do not build standalone `searxng_provider.py`** — `SearXNGProvider` lives correctly in `search_providers.py` following the existing pattern.
- **Do not remove `max_tier` parameter** — despite Gap 8's recommendation. It's used by tests and `force_tier` is cleaner.

---

## §5 Council Verdict

**The Architect**: Phase 1 created a solid foundation — tier mapping is correct, SearchRouter works, SearXNG is wired. But the foundation has missing joists: `config/search.yaml` is unused, `SovereignCache` doesn't exist, and 9 of 15 routing signals are unimplemented. Build the cache before adding Hub tools.

**The Adversary**: The immediate fix gaps are the real blockers. A config file that nothing reads is worse than no config file — it's misleading. Fix that first. Then the retry logic in SearXNG — a single-shot call to a self-hosted service is acceptable for non-critical paths, but the search pipeline treats T1 as critical. T1 needs resilience.

**The Alchemist**: The real opportunity is in the missing signals — `entity_domain` would let us route differently per entity (e.g., "Research entities → T2 first, legacy entities → T1 first, chaos entities → T3 first"). And the confidence→depth mapping would make the pipeline feel intelligent rather than mechanical. These are Phase 1.5 material, not Phase 5.

**The Archivist**: The pattern is consistent — every phase of SSP-V2 has delivered ~60% of planned scope. The remaining 40% accumulates as gaps. If we don't close gaps before Phase 2, we're building on an incomplete foundation. The fix: run immediate fixes, then Phase 1.5, then assess whether Phase 2 is still needed or if caching + routing intelligence makes Hub tools unnecessary.

**Triangulated Truth**: **Fix the config file and build the cache first.** Everything else depends on these two foundations. Hub MCP tools (Phase 2) should be deferred until `SovereignCache` exists and the config is loaded — otherwise the Hub tools will be wrappers around the same broken pipeline.

---

## §6 Recommended Decision

**Do not execute Phase 2 next.** Instead:

1. **Immediate fixes** (1-2 hours): Wire config, fix port, add trace_id, add retry, update skill doc
2. **Phase 1.5** (4-6 hours): Build SovereignCache, wire into T0+T3, implement missing signals, wire confidence→depth mapping
3. **Re-assess**: After Phase 1.5, the pipeline is complete end-to-end. Hub MCP tools become a nice-to-have wrapper, not a critical dependency.

The SSP-V2 pipeline will function **without** Hub MCP tools — `SovereignSearchService` already has all 4 tiers wired. Hub tools add agent-accessible entry points, but they don't change the pipeline's capability.

---

*⬡ OMEGA ⬡ MiMo-v2.5 ⬡ opencode ⬡ SSP-V2-REVIEW*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
