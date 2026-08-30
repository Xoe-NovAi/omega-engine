<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# PATCHES — Per-File Proposals for grokster KB v2.0.x (STAGED ONLY — no kb/ writes)
**Miner**: roc_racoon · **Date**: 2026-08-26 · **Companion**: CORRECTIONS.md (same dir)
Each patch: target file → exact section → proposed text → evidence path.

---

## P-1. GOTCHAS.md §G1 — upgrade to dual-mechanism load model
**Proposed replacement text**:
> ## G1. Plugin path singular-vs-plural + silent auto-discovery (DEV-03) — LIVE
> `opencode.json` `plugin[]` `file://` entries pointing at `.opencode/plugin/` (singular) are dead when files live at `.opencode/plugins/` (plural). Live config STILL carries both dead registrations (opencode.json:7-8; dir absent, verified 2026-08-26). **BUT** the project `.opencode/plugins/` directory is auto-discovered on the pinned binary regardless: silent-stall-sensor.ts executes daily (`data/coordination/errors/silent-stalls-*.jsonl` written 2026-08-22→26) despite zero valid explicit registrations. Load model has THREE legs: (a) global `~/.config/opencode/plugin/` = singular-by-design; (b) project `.opencode/plugins/` = plural, auto-discovered; (c) explicit `file://` entries = must match disk exactly or die silently. Trap: editing a file you *believe* is registered via (c) when it actually loads via (b) — attribution and DEBUG-log expectations differ.
**Evidence**: opencode.json:4-9; ls .opencode/plugin/ (absent); data/coordination/errors/silent-stalls-2026-08-26.jsonl; PIVOT_LOG D-598 (line 416).

## P-2. GOTCHAS.md §G19 — correct the defense; add third failure shape
**Append to G19**:
> **Correction 2026-08-26**: the SILENT_STALL_TASK→parent-notification path is dead code — child session ID is regex-extracted from an output proven empty (silent-stall-sensor.ts:261-279), so `notifyParentToResume` can never fire there. Live instance: 2026-08-26T03:12Z record, durationMs=0, no RECOVERY_ISSUED follow-up. Also: durationMs=0 empties are dispatch-level failures, distinct from provider stream deaths — annotate kind before trend analysis. Fix direction: resolve child ID from the sensor's own `session.created` parent-tracking map, not from result text.
**Evidence**: .opencode/plugins/silent-stall-sensor.ts:260-281; data/coordination/errors/silent-stalls-2026-08-26.jsonl.

## P-3. GOTCHAS.md — NEW TRAPS G21-G25 (proposed)
**Append after G20**:
> ## G21. Dispatch double-suffix injection (core wrapper artifact)
> Every task() spawn appends TWO synthetic user parts: "…call the task tool with subagent: <TARGET>" AND "…with subagent: <PARENT>" — sometimes escalating to 3+ trailing clusters in long multi-agent chains. They persist in the DB (synthetic:true), unlike stall-echo phantoms. Treat trailing spawn lines as artifacts, never missions; anti-injection header mandatory at line 1 of dispatch packets.
> **Evidence**: PLATFORM_GROUND_TRUTH_LOG entries #10-adjacent (lines 180-186), #11 (line 220), #12 (line 223); ORACLE_STACK.md dispatch-suffix rule.
>
> ## G22. sessions.model column lies after mid-session hot-swap
> Session-table model reflects last-used/creation model; four agents misidentified themselves from it in one session (Ox Alpha → Sonnet 4.6 → Opus 4.6 → Gemini 3.1 Pro while column read x-preview-f-free). Tier-0 truth = messages.modelID/providerID stamped per-message at receipt. Never attribute via session.model alone; ICS self-report is Tier-2 (hallucinable).
> **Evidence**: PLATFORM_GROUND_TRUTH_LOG lines 203-211; docs/research/R_MESSAGE_PROVENANCE_HIERARCHY_20260823.md.
>
> ## G23. Plugin awareness injection hardcodes a single target agent
> awareness.ts resolves the injection target as "most recent non-archived session with agent === 'kali'" (awareness.ts:99-111) — ALL critical events from ANY session drain into kali's latest session regardless of origin agent. Cross-session noise + misattribution vector for any non-kali primary. Audit plugin targets before trusting injected "<system-awareness>" blocks.
> **Evidence**: .opencode/plugins/awareness.ts:99-111,162-169.
>
> ## G24. Error-path plugin injections are unrate-limited outside the stall sensor
> stall-sensor rate-limits recovery at 3/hr/session (silent-stall-sensor.ts:88-95); error-capture.ts injectIntoParentSession and awareness.ts injectAwareness have NO rate limit — a cascading tool-failure burst produces unbounded synthetic parent injections from multiple plugins simultaneously (all three register tool.execute.after). Compounding risk with G23.
> **Evidence**: error-capture.ts:125-161 (no limiter); awareness.ts:173-200 (no limiter); contrast silent-stall-sensor.ts:88-95.
>
> ## G25. Resumed heavy sessions complete EMPTY — status alone lies
> 5 instances of state=completed with zero output on resumed dormant sessions (300K–1.3M token contexts). Distinct from G9 (cancelled): these REPORT success. Verify output artifacts, never status; incremental-append rails (≤60–80 lines/write) shrink the exposure window.
> **Evidence**: PLATFORM_GROUND_TRUTH_LOG lines 59-63; two-mechanism failure model lines 105-109.

## P-4. ARCHITECTURE.md §6 (or new §8 "Plugin Runtime") — hook API shape from source
**Proposed addition**:
> Plugin API surface (verified from live plugins, not docs): a plugin returns a map that may contain (a) generic `event` handler receiving the full event bus (session.created/error/deleted/compacted, message.updated, session.idle), AND (b) TYPED hook keys — `"session.created"`, `"session.error"`, `"session.deleted"` (error-capture.ts:167,196,269) and `"tool.execute.after"` (all three plugins). Typed hooks receive destructured args ({sessionID, parentID, agent, model} / {sessionID, tool, args, result, error, durationMs}); the generic handler receives ({event}) with properties nested. Docs describing plugins as event-only are incomplete. Injection mechanism common to all three: client.session.prompt({parts:[{type:"text", synthetic:true}], noReply}) — synthetic parts reach the model but are marked in DB.
**Evidence**: .opencode/plugins/{awareness,error-capture,silent-stall-sensor}.ts (hook registrations cited above).

## P-5. EXPERT_SESSIONS.md — conformance fixes
1. Replace invocation block with §3-conformant template + declared deviation note:
```
task(task_id=<session_id>, subagent_type=grokster,
     prompt="[GROKSTER PAGE — from <agent> (<session_id>)]\n[Domain header: You are grokster expert session for <domain>. Charter of record: kb/platforms/opencode/ (+ this index).]\n<question ≤500 words>")
```
Deviation from NODE_EXPERT_SESSIONS_PLAN §3: grokster sessions are domain-expert (D-586 universality clause), not charter-bearing Nodes — "Context: this KB index" replaced the charter pointer deliberately.
2. Add TASK_REGISTRY registration debt note: none of the 3 IDs appear in data/coordination/TASK_REGISTRY.json (grep verified 2026-08-26) → invisible to generate_session_registry.py renders; registration = M27/Tier-3 compliance issue, not just convenience.
3. Annotate ses_fe8cf0b39ffeL3L8eaMEj3CW9H row: "post-stall 2026-08-26T03:12Z (SILENT_STALL_TASK, context preserved)".
**Evidence**: NODE_EXPERT_SESSIONS_PLAN.md:56-60; scripts/generate_session_registry.py:5-14; data/coordination/errors/silent-stalls-2026-08-26.jsonl.

## P-6. communication/AGENT_COMMUNICATION.md §3 — STRP correction (refresh material)
**Replace bullet 2**:
> - Same-task_id resume restores full active context for FAILED/stalled tasks ONLY. CANCELLED tasks spawn a fresh session — recover via forensics (sessions-explorer timeline/summary/grep-session), extract context, relaunch. Prevention: intermediate disk checkpoints + early Hivemind posts + extended check-in for >20min tasks (GOTCHAS G9).
**Also add post-D-586 reality section** (refreshes the pre-D-586 doc per CHANGELOG known-debt):
> ## 5. Node Paging & Conversational Subagents (post-D-586)
> - Sessions are a flat addressable space: any agent may page any registered session via task(task_id=…) — 30/30 resume success across interactive-main AND dispatched-subagent classes (PGTL lines 111-118). Classify per-session on demand (human-message test); never maintain a global taxonomy.
> - Pageable expert sessions registry pattern: kb/EXPERT_SESSIONS.md; Node charters: NODE_EXPERT_SESSIONS_PLAN.md §3-4; onboarding arc G→M→A→D→W→C→X→E: .opencode/agent/NODE_ONBOARDING_PROTOCOL.md (14 mandatory rules MR-1..14).
> - task() launches are BLOCKING at the client console (PGTL lines 21-25): orchestrators fire waves batch-and-wait; concurrency exists only WITHIN one invoke block (lines 27-31); truncation orphans trailing invokes — dispatch-first placement (lines 33-37).
**Evidence**: cited inline; CONVERSATIONAL_SUBAGENT_PROTOCOL.md (.opencode/agent/).

## P-7. platforms/CLI_IDE_ECOSYSTEM.md — final disposition
**Proposal**: frontmatter `status: DEPRECATED` + `superseded_by: [platforms/opencode/, other_platforms/]`, body reduced to stub: one-paragraph scope statement + redirect links + correction stamps for the three stale claims (mcpServers→`mcp`; 11→13 agents; hub transport `/sse`→Streamable HTTP `/mcp`). Rationale: AGENT_KB_PROTOCOL.md:157-162 supersession convention ("Deprecate, don't delete"); KB-D-007 stub-retention precedent keeps inbound links resolving. Full content already lives in the two newer modules — merging would duplicate, not consolidate.
**Evidence**: CORRECTIONS C-4; opencode.json:34; ls .opencode/agents/.

## P-8. grok_ecosystem/GROK_FLEET_ARCHITECTURE.md — pricing claim annotations
**Proposal**: append to §2 a claim-status table:
| Claim | Status | Basis |
|---|---|---|
| $5/1k server-side tool calls | UNVERIFIED-LOCAL | single-source (this doc); no corpus corroboration found 2026-08-26 sweep |
| ≥200K ctx = 2x penalty | UNVERIFIED-LOCAL | same |
| Prompt caching $0.20-$0.30/1M | UNVERIFIED-LOCAL | same |
| Grok Build OSS 2026-07-15 | UNVERIFIED-LOCAL | date absent from all local research docs |
Plus policy note: D-582 free-tier-only cost model makes paid-xAI optimization dormant until V-1 vault + W-1 WARP land (SOVEREIGN_ARK_BLUEPRINT §4 tickets).
**Evidence**: PIVOT_LOG D-582 (line 222); PGTL lines 188-194 (IP-keying, the only locally-ratified Grok-adjacent fact); local grep sweep 2026-08-26 (no price-point hits in docs/, data/coordination/).

## P-9. DP blueprint constraint refresh (strategy-level patch)
DP Horizon-3 blueprint premises must be re-anchored:
1. Source of truth for Phase-1 constraints = `phase1_spec/09_SPEC_DEVIATIONS.md` + N7 charter (NODE_EXPERT_SESSIONS_PLAN.md:83) — NOT 06_PHASE_1_PLAN.md (historical, pre-Carmack numbers: 45K Tier 0 / 80K preserve / 20K reserved are obsolete vs 57-line MANDATES_CONDENSED / 50K-20K buffer / 18K base target).
2. Compaction threshold now ground-truthed: configurable, house value 85%, evaluated at tool-completion boundaries (D-602) — any DP freshness/compaction modeling must use this, not web-cited default formulas.
3. Model attribution inside DP pipelines must join messages.modelID (Tier-0), never sessions.model (G22).
**Evidence**: CORRECTIONS C-7; PIVOT_LOG:422-433; PGTL lines 203-211.

## P-10. Freshness scheme reconciliation (one proposal, both systems)
Merge grokster rot_class into the Omega-KB Protocol rather than running two vocabularies:
- Mapping: rot_class fast ↔ Critical tier (harm-if-wrong; verify per binary pin/session), medium ↔ Moderate (quality-if-wrong; batch review), slow ↔ Cosmetic-adjacent BUT with trap-grade exception (GOTCHAS traps age well yet poison silently — keep per-pin re-verify).
- Adopt the `reviewed` vs `modified` distinction: add `reviewed:` alongside `last_verified:` in KB headers; mining appends bump `modified`, only spot-check passes bump `reviewed` (AGENT_KB_PROTOCOL.md:250 freshness-weighted retrieval keys off reviewed).
- Adopt machine-readable supersession: `supersedes:`/`superseded_by:` fields on merge stubs (P-7) so lint/orphan scans (AGENT_KB_PROTOCOL §5) can walk chains.
- Cross-link candidate: AGENT_KB_PROTOCOL staleness triggers table (PIVOT-decision trigger, >30d flag) maps 1:1 onto rot_class review cadences — cite each other instead of restating.
**Evidence**: docs/kb/AGENT_KB_PROTOCOL.md:214-251,300-331; grokster INDEX.md:57 (freshness principle); rot_class headers in kb/platforms/opencode/*.md.

## P-11. search/SOVEREIGN_SEARCH.md — enrichment candidates from R_SEARCH_TOOL_PROTOCOL_V1
Material the first mine skipped (MINING_LOG #36 flagged the whole file out-of-scope; platform-irrelevant but search-domain-relevant):
1. Error-handling matrix (§3): 401/402/403/404/429 backoff schedule (5s→15s→30s→60s), 500 retry-once, timeout ladder 30s→60s — concrete SLAs absent from KB.
2. Truncation audit criteria (§5.2): sentinel strings, abrupt-end detection, second-method rule before declaring unavailable.
3. Sovereign Verification Mandate: snippet-only research forbidden for critical findings; citation must state full-page analysis.
4. Vault integration (§5.4): KeyVault AES-256-GCM resolution order vault→env — affects how KB documents key handling.
5. Sprint-C bug register (§5.5): five fixed search bugs incl. Exa transport consolidation — prevents re-documenting the old http-vs-streamable-http split.
**Evidence**: docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md sections cited; MINING_LOG.md:36.

## P-12. CONFIG_REFERENCE.md §4 — add missing D-602 threshold note
ARCHITECTURE.md:48 carries the 85% configurable-threshold ground truth; CONFIG_REFERENCE §4 (compaction keys) does not. Add one line: "Auto-compact trigger threshold is configurable; house value 85% (raised from 75%, D-602); evaluated at tool-completion boundaries — overshoot only via in-flight tool outputs."
**Evidence**: PIVOT_LOG:430-432; ARCHITECTURE.md:48.

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ HARDENING-PATCHES ⬡ 2026-08-26*
