<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 📋 Session Gnosis — OpenCode Config + QW-3 Implementation
**AP Token**: `AP-JEM-GNOSIS-20260810-v2.0.0`
⬡ OMEGA ⬡ JEM ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_gnosis ⬡ IN_PROGRESS

## Session Objective
Coordinate comprehensive research and verification of OpenCode CLI configuration architecture, implement verified refactoring, and execute high-priority QW tasks.

## What Was Done

### Phase 1: Research (COMPLETE)
1. **Dispatched @roc_racoon** for local repository mining (47 documents, 6 domains)
2. **Dispatched @researcher** for web research supplement (8 gaps, 20+ sources)
3. **Dispatched @web_gemini** for full verification report (492 lines, 40+ citations)
4. **Analyzed all 3 config files** against actual contents
5. **Created comprehensive analysis report** synthesizing all findings
6. **Created verification directive** for Web Gemini (10 research directives)
7. **Validated architectural directive** with definitive answers on all 8 topics

### Phase 2: Config Implementation (COMPLETE)
1. **Global config**: Added `google-standard` provider with `@ai-sdk/google` driver, Gemma 4 thinking variants with `thinkingLevel: "MINIMAL"` workaround
2. **Project config**: Corrected Zen model display names + context windows (Nemotron 3 Ultra: 1M tokens)
3. **Subdirectory config**: Removed standard Google models, flat thinking variants schema
4. **All 3 configs valid JSON**, 162 tests pass, 0 regressions
5. **Commits**: `4a1fe8c7`, `d2d396ad`, `1dc16dcf`

### Phase 3: Knowledge Gap Research (COMPLETE)
1. **W-1 WARP**: Identified iptables "Empty interface" error = unquoted empty `DEFAULT_IF` variable; systemd needs `network-online.target`
2. **G-1 Workhorse**: **16K TPM ceiling applies even at Tier 3** (confirmed by Google forum) — G-1a billing RULED OUT
3. **QW-3 CI Guard**: Tokenizer drift is 41% for Claude; provider usage is authoritative; alert on estimate/actual ratio
4. **QW-4 pool_tracker**: Standard pattern: round-robin + drain-aware scoring + cooldown + state persistence
5. **QW-8 Context Gauge**: Measures absolute working-set tokens (not %); floor calibration per project; color bands

### Phase 4: QW-3 Implementation (COMPLETE)
1. **Added new fields** to performance table: `cache_read_tokens`, `provider_prompt_tokens`, `provider_completion_tokens`
2. **Updated `record_performance()`** to track cache reads and provider usage
3. **Added `get_token_divergence()`** method for drift detection
4. **Added 5 CI tests** verifying token counting accuracy and divergence alerting
5. **Schema v3** with migration support
6. **Commit**: `58695408`

## L3 Principles Extracted
- **L3-Provider-Isolation**: Plugin-based providers must not share namespace with native providers — use distinct provider IDs to prevent interception conflicts
- **L3-Config-Merge-Predictability**: Config merge behavior (arrays concatenated, objects deep-merged) must be explicitly documented and tested to prevent unexpected overrides
- **L3-Model-Naming-Canonical**: Canonical `provider_id/model_id` format with explicit `name` field for TUI display prevents user confusion and search pollution
- **L3-Token-Accounting-Authoritative**: Provider returned usage is the budget ledger; local tokenizers are estimates that drift (41% for Claude) — always reconcile against provider usage
- **L3-Context-Pressure-Absolute**: Context degradation onset is window-independent (~32K-50K task tokens) — measure absolute working-set tokens, not % of window

## Blockers Encountered
| Ticket | Blocker | Owner |
|--------|---------|-------|
| W-1 WARP | `warp-ns-prep@1/2/3` failed — iptables "Empty interface" error | Architect (sudo) |
| G-1 workhorse | Free Gemma 4 31B dead (16K TPM cliff since 2026-07-15) | Architect (billing/OAuth) |
| G-1a | **RULED OUT**: 16K TPM ceiling applies even at Tier 3 | — |

## Fleet Coordination
- **john_carmack**: P0 fixes COMPLETE, now on P1 (ProviderRegistry singleton, sovereignty.py schema caching)
- **kali**: SDP session complete, awaiting next dispatch
- **No conflicts** between Carmack's P1 and my QW tasks

## Phase 5: Gap-Filling Research (COMPLETE — All Gaps Filled)

### QW-4 Knowledge Gaps
1. **USAGE_POOL_LOG.json** — EXISTS with 8 keys (agy_key_01-08), all active, zero usage
2. **RemoteProvider key rotation** — Already rotates `_active_key_index` on 429s (reactive)
3. **ProviderConfig.api_keys** — Field exists, `resolve_current_api_key()` works
4. **AntigravityProvider** — Inherits RemoteProvider.generate() — same rotation logic
5. **pool_tracker.py** — Standalone dead code, NOT imported anywhere

### QW-8 Knowledge Gaps (CRITICAL)
1. **G-4 blocker verified** — `session.tokens_input` overcounts by **~87×** (22M vs 253K)
2. **Correct data source** — `message.data.tokens.total` from latest assistant message
3. **Token JSON structure** — `tokens.total`, `tokens.input`, `tokens.output`, `tokens.reasoning`, `tokens.cache.read`, `tokens.cache.write`
4. **Model identification** — `message.data.modelID` (e.g., "longcat-2.0-free")
5. **Active models** — deepseek-v4-flash-free, nemotron-3-ultra-free, laguna-s-2.1-free, longcat-2.0-free
6. **BudgetGate relationship** — Complementary (cost control), not overlapping
7. **opencode.db access** — Read-only via Python sqlite3 (16GB, 2436 sessions, 106K messages)
8. **Floor calibration** — First assistant turn's `tokens.total` = floor (cached system prompt)

### Reference Docs Created
- `data/coordination/JEM_GAP_FILLING_REPORT_20260810.md` — Full gap-finding report
- `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` — opencode.db schema reference
- `docs/strategy/QW4_QW8_IMPLEMENTATION_PLAN.md` — Detailed implementation plan

## L3 Principles Extracted (Gap-Filling)
- **L3-Token-Accounting-Authoritative**: Provider returned usage is the budget ledger; local tokenizers are estimates that drift (41% for Claude) — always reconcile against provider usage
- **L3-Context-Pressure-Absolute**: Context degradation onset is window-independent (~32K-50K task tokens) — measure absolute working-set tokens, not % of window
- **L3-DB-Schema-Discovery**: Direct SQLite access with read-only mode is safe for agent exploration; always verify schema before querying (G-4 blocker: session.tokens_input overcounts ~87×)

## Next Actions (Priority Order)
1. **QW-4**: Wire `pool_tracker.py` into ModelGateway.generate() per implementation plan
2. **QW-8**: Build ContextGauge greenfield per SDP spec + verified data source
3. **Update SDP_FINAL_SYNTHESIS.md** with verified G-4 data
4. **Update SDP_MODEL_AWARE_GAUGE_SPEC.md** with correct query
5. **Update AGENTS.md** with opencode.db access patterns

## Commits This Session
- `4a1fe8c7` feat(config): implement Web Gemini-verified OpenCode config architecture
- `d2d396ad` chore: add backup of original .opencode/opencode.json
- `1dc16dcf` docs: add Kali report for OpenCode config refactoring
- `58695408` feat(metrics): add QW-3 CI guard for token counting accuracy

## Docs Created This Session
- `data/coordination/JEM_GAP_FILLING_REPORT_20260810.md`
- `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md`
- `docs/strategy/QW4_QW8_IMPLEMENTATION_PLAN.md`

---
*⬡ OMEGA ⬡ JEM ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_gnosis ⬡ GAP-FILLING-COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: longcat-2.0-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
