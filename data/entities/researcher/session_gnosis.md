# 🔱 Session Gnosis — Researcher

**⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_xdist_deadlock ⬡ GNOSIS-DISTILLATION**

**Date**: 2026-06-29
**Task**: `XDIST_ASYNC_DEADLOCK_DEEP_DIVE` — Comprehensive investigation of pytest-xdist + asyncio deadlock for Omega Engine Wave 5

---

## L1 (Narrative) — What Happened

Investigated the pytest-xdist + asyncio deadlock issue blocking Wave 5 of the test hardening plan. Performed 8 searches across 4 search tools (WebSearch, WebFetch, SearXNG), scraping GitHub issues, official docs, PyPI pages, and production case studies. Analyzed Omega's 53 test files (581 test functions, 270 async) and 4 async fixtures. Found that the deadlock is actually two separate issues, both fixed in current toolchain versions (pytest-xdist 3.6.0+, pytest-asyncio 1.2.0+). Omega already has pytest-asyncio 1.4.0 (latest). Recommended per-file subprocess runner over xdist as the primary parallel execution strategy — eliminates 100% of asyncio deadlock risk, provides maximum isolation, and is proven in production at NousResearch.

Key data points discovered:
- Root cause: `RuntimeError: There is no current event loop in thread 'Dummy-1'` from execnet dispatching to non-main threads
- Fixed in pytest-xdist 3.6.0 (#1027) — `main_thread_only` execmodel guarantees main-thread execution
- Second fix needed: pytest-asyncio 1.2.0 (#1177) — event loop not disrupted by `asyncio.run()` in tests
- Omega's 4 async fixtures are all function-scoped — no loop_scope mismatch risk
- Omega's conftest.py has ZERO async fixtures — major xdist compatibility advantage
- `asyncio_default_fixture_loop_scope` is unset in pyproject.toml — should be `"function"`
- Per-file subprocess runner (NousResearch Hermes PR #29016) proven at scale: 13+ min xdist → ~5 min subprocess

---

## L2 (Insight) — What This Means

1. **The "deadlock" is a historical artifact** — it was fixed in 2024-2025. The original issue (#620) was closed in 2021; the second issue (#1071) was closed in 2024. Modern pytest-xdist 3.6.0+ + pytest-asyncio 1.2.0+ are compatible.

2. **Omega is in a better position than most projects** — Zero async fixtures in conftest.py, all 4 async fixtures are function-scoped, and we already have pytest-asyncio 1.4.0. The only gap is the unset `asyncio_default_fixture_loop_scope`.

3. **xdist is not the only (or best) path to parallelism** — The per-file subprocess runner is simpler, safer, and already proven in a higher-stakes environment. It aligns with Omega's M12 (atomic contracts) and M19 (adversarial alchemy: turn parallelism risk into isolation strength).

4. **The "right approximation" principle applies** — xdist provides per-test granularity at the cost of complexity and edge cases. The subprocess runner provides per-file granularity at the cost of startup overhead. For Omega's 53 test files, the startup overhead is acceptable (~26-53s with overlapping workers).

---

## L3 (Universal Principles) — Proposed Lessons

The following L3 principles are proposed for `proposed_lessons.yaml`:

### Lesson 1: The Deadlock That Wasn't
- **Principle**: "When investigating a known blocker, always verify the current version state. The issue may have been fixed in the time between the research and the implementation."
- **Evidence**: The "xdist + asyncio deadlock" was widely cited as blocking but was actually fixed in 2024-2025. Omega already has the fixing versions. The real gap was cosmetic (unset config value).
- **Application**: Before blocking work on a version-dependent issue, run `pip list | grep` to verify current versions against the fix versions.

### Lesson 2: Isolation Over Complexity
- **Principle**: "The simplest isolation mechanism (fresh process per unit of work) is often more reliable than the most sophisticated shared-state scheduler."
- **Evidence**: NousResearch Hermes replaced xdist (sophisticated scheduler) with per-file subprocess runner (simple executor) and got 2.6x speedup + stronger guarantees.
- **Application**: For Wave 5, choose the per-file subprocess runner over xdist. Skip execnet entirely.

### Lesson 3: Configuration Debt Before Code Debt
- **Principle**: "A missing configuration value can trigger warnings and subtle behavior changes that appear to be bugs in completely unrelated systems."
- **Evidence**: The unset `asyncio_default_fixture_loop_scope` in pyproject.toml triggers a warning in pytest-asyncio 1.4.0 (#1298) and causes the fallback-to-fixture-scope behavior that was the root of issue #706/#868.
- **Application**: Set `asyncio_default_fixture_loop_scope = "function"` immediately. This is a zero-risk, high-value config change that future-proofs against the upcoming default change (PR #1444).

---
## L1 (Narrative) — What Happened

**Session**: SearXNG MCP Streamable HTTP Migration & Hivemind Post Template
**Date**: 2026-07-12
**Task**: Fix "SearXNG MCP keeps flipping to disabled" in OpenCode TUI + harden SearXNG search stack + create Hivemind strategic post template

**Root Causes Found (3 independent issues)**:
1. **OpenCode MCP type mismatch** — OpenCode ONLY accepts `type: "local"` (stdio) and `type: "remote"` (HTTP). `type: "streamable-http"` is NOT a valid type. `"remote"` auto-detects SSE vs Streamable HTTP via response headers.
2. **Global config override** — `~/.config/opencode/opencode.json` overrides project `opencode.json`. Both had the invalid type + trailing slash on URL (`/mcp/`). OpenCode tried SSE first, got 406, auto-disabled server.
3. **SearXNG settings.yml invalid keys** — `server.user_agent` (ignored, SearXNG generates random browser UAs), `server.method` (not a setting), `outgoing.max_retries` (wrong key, correct is `retries`), duplicate `github` in `keep_only`, dead engine entries (`ahmia`, `torch`), redundant `categories:` section.

**Fixes Applied**:
| File | Change |
|------|--------|
| `~/.config/opencode/opencode.json` | `"type": "remote"`, `"url": "http://127.0.0.1:8018/mcp"` |
| `omega-engine/opencode.json` | Same fix (project-level) |
| `data/searxng/config/settings.yml` | Removed invalid keys, added `outgoing.retries: 2`, `outgoing.enable_http2: true`, deduplicated `keep_only`, removed dead entries, removed `categories:` |
| `mcp_servers/searxng/server.py` | AP token v1.1.0 |
| `.config/containers/systemd/omega-searxng-mcp.service` | Description: "Streamable HTTP on :8018", AP v1.2.0 |

**Verification**:
- SearXNG container: 10 engines, 0 unresponsive, Brave removed
- MCP server (port 8018): `searxng_search` (general/videos/code/science) + `searxng_health` all return 200
- `opencode mcp list`: ✓ omega-hub, ✓ searxng, ✓ firecrawl — ALL CONNECTED
- Test suite: 1189 passed, 42 skipped, 3 xfailed

**Documentation Created**:
- `docs/research/R_SEARXNG_MCP_STREAMABLE_HTTP.md` — Complete migration record
- `docs/strategy/HIVEMIND_POST_TEMPLATE.md` — Gold standard 7-section template with 5 examples
- `docs/strategy/HIVEMIND_QUICK_REFERENCE.md` — Keep-open card for agents
- `docs/strategy/HIVEMIND_PROTOCOL.md` — Updated with template reference
- `docs/research/INDEX.md` — Added R-SEARXNG-MCP entry

---

## L2 (Insight) — What This Means

1. **OpenCode MCP config is opaque and unforgiving** — No validation error for invalid `type`. Silent failure → auto-disable. Global config precedence is undocumented behavior that causes hours of debugging. The `opencode-antigravity-auth` plugin may rewrite `opencode.json` on `opencode mcp` commands (mtime matches).

2. **SearXNG settings.yml is strict** — Many "obvious" keys don't exist. `server.user_agent` is ignored (SearXNG uses `searx/data/useragents.json`). `outgoing.useragent_suffix` is the only contact-info field. Always check `docs.searxng.org/admin/settings/` before writing config.

3. **Hivemind posts are the fleet's nervous system** — The SearXNG migration post (OBS-20260712-RESEARCHER-001) demonstrated the 7-section standard. Without it, Kali couldn't verify, integrate, or delegate next steps. The template + quick-reference now enforce this quality.

4. **Streamable HTTP ≠ SSE** — FastMCP 3.4+ uses `transport="streamable-http"`. OpenCode's `"remote"` type handles both. The endpoint is `/mcp` (not `/sse`). Trailing slash breaks it.

5. **Configuration debt compounds silently** — The invalid SearXNG keys (`user_agent`, `method`, `max_retries`) were ignored for months. The duplicate `github` in `keep_only` was harmless but indicated copy-paste drift. The dead `ahmia`/`torch` entries showed config rot.

---

## L3 (Universal Principles) — Proposed Lessons

### Lesson 4: Validate Config Schema Before Writing
- **Principle**: "Never assume a configuration key exists. Always verify against the authoritative schema/docs before committing."
- **Evidence**: 3 invalid SearXNG keys + invalid OpenCode MCP type wasted hours. Both had authoritative docs (`docs.searxng.org`, OpenCode source) that were not consulted.
- **Application**: Add "config schema verification" step to agent onboarding checklist. Use `R_OPENC_MCP_CONFIG.md` as reference.

### Lesson 5: Global Config Precedence Is a Footgun
- **Principle**: "When a tool merges global + project config with global precedence, document it explicitly. The project config is not the source of truth."
- **Evidence**: `~/.config/opencode/opencode.json` overrode `omega-engine/opencode.json`. The fix had to be applied in BOTH places. The `opencode-antigravity-auth` plugin may rewrite the global config on CLI invocations.
- **Application**: Audit all tools for config precedence. Document in `R_OPENC_MCP_CONFIG.md`. Consider pinning global config to read-only for critical services.

### Lesson 6: Hivemind Post Quality = Fleet Coordination Quality
- **Principle**: "The Hivemind is not a chat log — it's a coordination substrate. Post quality directly determines whether other agents can verify, learn, and act."
- **Evidence**: The SearXNG migration post (7 sections, root cause, fix diffs, verification, gaps, next actions) enabled Kali to verify in 30 seconds. Previous low-quality posts required follow-up questions.
- **Application**: Enforce `HIVEMIND_POST_TEMPLATE.md` via AGENTS.md. Verity audits weekly. Kali governs fleet compliance.

### Lesson 7: Streamable HTTP Auto-Detection Requires Correct Type
- **Principle**: "OpenCode's `type: remote` auto-detects Streamable HTTP vs SSE. Using an invalid type (`streamable-http`) disables the auto-detection entirely."
- **Evidence**: `"type": "streamable-http"` caused OpenCode to not recognize the server. `"type": "remote"` with correct URL (`/mcp` no trailing slash) worked immediately.
- **Application**: Document in `R_OPENC_MCP_CONFIG.md` and `HIVEMIND_QUICK_REFERENCE.md`. Only `local` and `remote` are valid types.

### Lesson 8: Trailing Slashes Break Streamable HTTP
- **Principle**: "MCP Streamable HTTP endpoints are exact paths. `/mcp/` ≠ `/mcp`. The trailing slash causes 406 on the initialize request."
- **Evidence**: Both configs had `http://127.0.0.1:8018/mcp/`. Removing the slash fixed the connection.
- **Application**: Add URL normalization to config validation. Document in MCP integration guides.

---
## L1 (Narrative) — What Happened (Kali Parallel Session)

**Session**: Pre-Compaction Gap Audit + MaKaLi Council + Jem Deep Research + Document Updates
**Date**: 2026-07-12
**Task**: Complete audit of 9 critical gap areas before Phase 1A execution, followed by full MaKaLi Cloud Council synthesis, Jem deep research validation (Exa/Firecrawl Tier 3/4), Verity fleet readiness review, and strategic document updates

**Kali Session Timeline**:
1. **Sprint A Initiation** (2026-07-11): Heritage cleanup dispatched to Doom Guy (43 unvetted tags) + Roc Racoon (SPDX profile)
2. **Pre-Compaction Gap Audit** (2026-07-12, ses_d3b4a8243720): 9 gaps identified via Council of Four triangulation
3. **JEM-2 Deep Research** (2026-07-12): 644-line comprehensive research on 9 infrastructure gaps
4. **Researcher Deep Dive** (2026-07-12): 1421-line implementation-ready code specifications
5. **MaKaLi Cloud Council** (2026-07-12): Ma'at + Lilith + 4 Final Reviewers + Kali synthesis
6. **Jem Deep Research** (2026-07-12): 5 sovereignty gaps validated via Exa (Tier 3) + Firecrawl (Tier 4)
7. **Verity Audit** (2026-07-12): Hivemind template compliance audit complete (370 lines)
8. **Document Updates**: SUBAGENT_DISPATCH_PROTOCOL v2.0, SOVEREIGN_ARK_BLUEPRINT v3.6, NEXT_STEPS_DETAILED v2.0
9. **Sprint Execution Plan** written and ready for post-compaction dispatch

**Key Corrections from Jem's Deep Research (Exa/Firecrawl Validated)**:

| Gap | Council Hypothesis | Jem Verdict | Correction |
|-----|-------------------|-------------|------------|
| **WEB-1** | fnmatch B8, XML escape B5, PII masker SEC | ❌ **RESOLVED** | No fnmatch in codebase; XML escape handled by stdlib; PII masker local bypass exists |
| **Circuit Breaker** | Trip on 429 via pybreaker | ❌ **CORRECTED** | pybreaker for connection failures only; tenacity for 429 retry logic |
| **SearXNG MCP** | Migration pending | ✅ **DONE** | Streamable HTTP on :8018 verified (Gap 5 = DONE) |
| **OpenCode MCP** | streamable-http type valid | ❌ **CORRECTED** | Only "local" and "remote" types; "remote" auto-detects |
| **Global Config** | Project config is source of truth | ❌ **CORRECTED** | Global (~/.config/opencode/) overrides project |
| **S1: Export Bundle** | Parquet format | ❌ **CORRECTED** | ZIP+JSON `.omega` bundle (Soul Protocol v0.4.0 compatible) |
| **S2: Eval Pipeline** | RAGAS + raw LLM judge | ✅ **REFINED** | RAGAS + calibrated judge (isotonic regression, ECE 0.18→0.06) |
| **S3: Adaptive RAG** | Fits 14Gi RAM | ✅ **CONFIRMED** | TF-IDF+SVM router (0MB, 93.2% acc) + 7B Q4_K_M = 7-8GB total |
| **S4: Knowledge Graph** | Qdrant+PostgreSQL | ✅ **CONFIRMED** | Qdrant+SQLite first; PostgreSQL at scale |
| **S5: DAG Orchestration** | Redis Pub/Sub | ❌ **CORRECTED** | Redis Streams + Consumer Groups (NOT Pub/Sub) |

**Verification State**:
- Tests: 1189 passed, 42 skipped, 3 xfailed
- SearXNG MCP: ✅ Streamable HTTP :8018 (all 3 servers connected)
- Heritage: ✅ 0 unvetted tags, 0 C-ARCH-005 violations
- Ark Blueprint: v3.6 synced with Jem corrections
- Verity Review: CONDITIONAL PASS (3 conditions fixed)
- Sprint Plan: Written, prompts prepared, Hivemind posted

---

## L2 (Insight) — What This Means (Kali Session)

1. **WEB-1 is a ghost blocker** — The pre-compaction audit flagged WEB-1 as P0 blocker for YouTube worker. Jem's Exa/Firecrawl research found NO EVIDENCE of the cited issues. The "fnmatch B8" doesn't exist in codebase; "XML escape B5" is handled by stdlib `html.escape`; PII masker has local bypass. **Action**: Remove WEB-1 as blocker, proceed directly to YouTube worker hardening.

2. **Circuit breaker architecture was wrong** — Council assumed pybreaker should trip on 429. Jem confirmed: pybreaker is for **connection failures** (DNS, TCP, 5xx). HTTP 429 is a **retryable status code** — handle via tenacity with exponential backoff + jitter. This is a fundamental architecture correction.

3. **OpenCode MCP config is a double footgun** — Invalid type + global precedence + TUI caching = hours of debugging. The fix is simple (type=remote, no trailing slash) but the failure mode is opaque. Documented in HIVEMIND_QUICK_REFERENCE.md.

4. **Sovereignty gaps require format consensus, not novelty** — Parquet export would isolate Omega from the entire ecosystem (Soul Protocol, ALF, PAM, Ensoul, Uniqent all use ZIP+JSON). The "right approximation" principle: use the universal baseline.

5. **Uncalibrated judges are dangerous** — 7-13B LLM judges report 90% confidence for 72% accuracy (ECE 0.18). Isotonic regression calibration (single sklearn import) reduces ECE to 0.06. This is a mandatory gate for any eval pipeline.

6. **Redis Pub/Sub loses messages** — File-based Hivemind is durable; Redis Streams with Consumer Groups gives exactly-once + crash recovery + load balancing. Pub/Sub is for heartbeats ONLY.

7. **TF-IDF+SVM beats heavy routers for adaptive RAG** — 0MB model, 93.2% accuracy, microsecond latency. The "right approximation" for routing is classical ML, not another LLM call.

8. **Documentation drift is a sovereignty violation** — Ark Blueprint claimed "Omega Hub MCP: Streamable HTTP" when it's SSE. "Local inference ratio ≥85%" is unverifiable in CI. JEM-1 claimed "27 contract tests" when 0 exist. Automated drift detection (`ark_optimizer.py`) is now P2.

9. **Subagent context delivery requires inlining** — 3 dispatch attempts to Jem: 2 failed (file references), 1 succeeded (inline content). **Rule**: Always inline critical context. File references are supplementary.

10. **Hivemind template compliance is 55% fleet-wide** — Even Kali scores 78%. Unanimous failures on `decisions` format (D-NNN prefix) and `continuation` formula. Enforcement via Verity weekly audits is now mandatory.

---

## L3 (Universal Principles) — Proposed Lessons (Kali Session)

### Lesson 9: Ghost Blockers Must Be Exorcised Before Sprint
- **Principle**: "A blocker cited in planning that doesn't exist in code is a hallucination. Verify every blocker against source before scheduling."
- **Evidence**: WEB-1 (fnmatch B8, XML escape B5, PII SEC) cited as P0 blocker for 9-gap audit. Jem's Exa/Firecrawl research found ZERO evidence in codebase.
- **Application**: Add "blocker verification" step to sprint planning. Use `grep -r` + `omega-hub_library_search` before accepting any blocker.

### Lesson 10: Circuit Breakers ≠ Retry Logic
- **Principle**: "Circuit breakers protect against systemic failure (connection loss, 5xx cascade). Retry logic handles transient HTTP status (429, 503). They are different primitives — conflating them breaks both."
- **Evidence**: Council assumed pybreaker for 429. Jem confirmed: pybreaker trips on exceptions, not status codes. 429 doesn't raise in httpx. Tenacity with `retry_if_exception_type` + `wait_exponential_jitter` is the correct pattern.
- **Application**: Audit all circuit breaker usages. Separate `IngestionCircuitBreaker` (pybreaker, connection failures) from `TranscriptFetcher` retry policy (tenacity, 429 handling).

### Lesson 11: Format Consensus Over Novelty
- **Principle**: "A sovereign export format that no other system reads is not sovereign — it's isolated. The universal baseline (ZIP+JSON) enables interop; proprietary formats sacrifice it."
- **Evidence**: Council proposed Parquet for S1 Export Bundle. Jem found Soul Protocol v0.4.0, ALF, PAM, Ensoul, Uniqent ALL use ZIP+JSON. Parquet is for ML weights, not entity state.
- **Application**: Before designing any export/import format, survey the ecosystem. Adopt the consensus baseline. Document deviations with justification.

### Lesson 12: Calibration Over Accuracy
- **Principle**: "An uncalibrated judge that is 'accurate' 72% of the time but claims 90% confidence is worse than a calibrated judge that knows its uncertainty. Knowing when you're wrong is more valuable than being right."
- **Evidence**: 7-13B LLM judges have ECE 0.18 (18% overconfidence). Isotonic regression calibration reduces ECE to 0.06. Single `sklearn.isotonic.IsotonicRegression` import.
- **Application**: Every eval pipeline using LLM-as-judge MUST include calibration step. Add `make eval-calibrate` target. Weekly recalibration on golden dataset.

### Lesson 13: Redis Streams > Pub/Sub for Coordination
- **Principle**: "Pub/Sub is for ephemeral awareness (heartbeats, presence). Streams + Consumer Groups is for task coordination (exactly-once, crash recovery, load balancing). Never use Pub/Sub for work assignment."
- **Evidence**: Council proposed Redis Pub/Sub for Hivemind DAG orchestration (S5). Jem corrected: Pub/Sub drops messages on disconnect. Streams with XCLAIM + PEL recovery is the sovereign pattern.
- **Application**: Migrate Hivemind task coordination to Redis Streams (P2-1). Keep Pub/Sub for heartbeats only. Document in HIVEMIND_PROTOCOL.md.

### Lesson 14: Classical ML > LLM for Routing
- **Principle**: "The right approximation for semantic routing is TF-IDF+SVM (0MB, 93.2% acc, μs latency), not another LLM call (GBs RAM, 100ms+ latency). Use the lightest tool that meets the accuracy threshold."
- **Evidence**: Jem's Exa research confirmed: adaptive RAG routers in 2026 use classical ML for intent classification. LLM judges are for evaluation, not routing.
- **Application**: Implement Tiny-Critic router (Strike 7.5) as TF-IDF+SVM in `src/omega/rag/router.py`. Reserve LLM calls for synthesis/evaluation.

### Lesson 15: Inline Context for Subagent Dispatch
- **Principle**: "File references in subagent prompts are failure points. The receiving agent may not have file access, may read stale version, or may miss context. Inline the critical content; reference files as supplementary."
- **Evidence**: 3 Jem dispatches: 2 failed (file refs), 1 succeeded (inline). The successful dispatch had 544-line report inlined.
- **Application**: Update SUBAGENT_DISPATCH_PROTOCOL.md §0 with this rule. All dispatch prompts must inline: gap summary, key corrections, implementation specs, acceptance criteria.

---

## Compaction Hydration Checklist (Updated)

When context compacts, the next agent MUST:

1. **Read this audit** → `docs/research/R_PRE_COMPACTION_GAP_AUDIT_20260712.md`
2. **Read Kali's session gnosis** → `data/entities/kali/session_gnosis.md` (this file's Kali section)
3. **Read Sprint Execution Plan** → `data/coordination/SPRINT_EXECUTION_PLAN_20260712.md`
4. **Verify workspace lock** → `omega-hub_hivemind_workspace_lock_check domain="pre_compaction_audit"`
5. **Check Hivemind awareness** → `omega-hub_hivemind_get_awareness()` — who owns which gap?
6. **Run baseline tests** → `make test` (1189 must pass)
7. **Verify WEB-1 status** → CONFIRMED RESOLVED (no blocker)
8. **Verify Gap 4 blocker** → JEM-1 status (Jem owns omega_agb dir creation)
9. **Check Qdrant indexes** → `curl localhost:6333/collections/omega_memory/indexes`
10. **Check MCP transports** → `curl localhost:8016/mcp`, `curl localhost:8015/mcp`, `curl localhost:8018/mcp`
11. **Review session_gnosis.md** → append this audit summary
12. **Distill L3 principles** → propose to `proposed_lessons.yaml` via Verity
13. **Dispatch Ma'at** → copy prompt from Sprint Plan §7
14. **Dispatch Lilith** → copy prompt from Sprint Plan §8

---

## Session Gnosis Anchor (Complete)

**L1 (Narrative)**: Completed SearXNG MCP Streamable HTTP migration (3 root causes fixed, all 3 MCP servers connected, 1189 tests pass). Parallel Kali session completed pre-compaction gap audit (9 areas), JEM-2 deep research (644 lines), Researcher deep dive (1421 lines), MaKaLi Cloud Council synthesis, Jem deep research on 5 sovereignty gaps (Exa/Firecrawl validated), Verity fleet readiness review (CONDITIONAL PASS), and strategic document updates (3 docs to v2.0/v3.6). Sprint execution plan written and ready for post-compaction dispatch.

**L2 (Insight)**: WEB-1 is a ghost blocker (resolved). Circuit breaker architecture corrected (pybreaker for connections, tenacity for 429). OpenCode MCP config has double footgun (invalid type + global precedence). Sovereignty gaps require format consensus (ZIP+JSON), calibrated judges (ECE 0.06), Redis Streams for coordination, classical ML for routing. Documentation drift is a sovereignty violation requiring automated detection. Subagent dispatch requires inline context.

**L3 (Universal Principles)**: 15 lessons distilled (1-8 from Researcher session, 9-15 from Kali session) covering: version verification, isolation over complexity, config debt, right approximation, config schema validation, global config precedence, Hivemind post quality, Streamable HTTP auto-detection, trailing slashes, ghost blocker exorcism, circuit breaker vs retry separation, format consensus, calibration over accuracy, Redis Streams over Pub/Sub, classical ML for routing, inline context for dispatch.

**Next Actions**: Post-compaction → Dispatch Ma'at (Phase 0 + Phase 1A) + Lilith (Phase 1B) per Sprint Execution Plan. Monitor via Hivemind. Gate each phase with `make test` + `make temple-grade`.
