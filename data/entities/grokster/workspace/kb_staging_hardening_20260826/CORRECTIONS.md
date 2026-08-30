<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# CORRECTIONS — Things in grokster KB v2.0.0 / Strategies Found WRONG, Stale, or Overstated
**Miner**: roc_racoon · **Pass**: Local Hardening (deep verification) · **Date**: 2026-08-26
**Method**: source-code reads + live-config checks + git forensics + log/JSONL evidence. No kb/ writes.

---

## C-1. G1 implication "plugins silently dead" is WRONG for the local trio — they ARE loading
**KB claim**: GOTCHAS.md G1 — "`plugin[]` entries pointing at `.opencode/plugin/` (singular) are silently dead… Live config STILL has both dead registrations as of 2026-08-26."
**Verdict**: The *registration observation* is TRUE; the *implied consequence* is FALSE.
**Refutation evidence**:
- `opencode.json:7-8` registers `file://…/.opencode/plugin/error-capture.ts` and `awareness.ts`; `.opencode/plugin/` does not exist (`ls`: No such file or directory).
- YET `data/coordination/errors/silent-stalls-2026-08-26.jsonl` exists, written **today 03:12:16Z**, and daily `silent-stalls-*.jsonl` + `provider-health-*.json` files exist for 2026-08-22→26. Only `silent-stall-sensor.ts` writes those filenames → the plugin executes on the pinned binary.
- Conclusion: OpenCode auto-discovers the project `.opencode/plugins/` (plural) directory regardless of the dead explicit entries. The trap is narrower than stated: dead file:// entries are redundant-but-harmless when the plural dir is populated; the danger is believing the explicit registration is the load mechanism (it isn't) and editing files under a path you *think* is registered.
**Required KB action**: upgrade G1 (see PATCHES P-1). Also cite D-598 (PIVOT_LOG:416) which already authorized the CI-2 plugin-path prototype targeting exactly this key.

## C-2. G19's parent-notification defense is DEAD CODE — proven by today's production stall
**KB claim**: GOTCHAS.md G19 defense — stall sensor detects empty task returns and notifies parent to resume child via task_id.
**Refutation evidence** (source read, `silent-stall-sensor.ts`):
- Lines 261-279: notification fires only inside `if (out.trim().length === 0)`; then `const child = out.match(/ses_[A-Za-z0-9]+/)?.[0]`. An empty output contains no `ses_` ID → `child` is always undefined on this exact path → `notifyParentToResume` can never execute from SILENT_STALL_TASK.
- Live proof: `silent-stalls-2026-08-26.jsonl` records `SILENT_STALL_TASK … durationMs:0` with NO subsequent `RECOVERY_ISSUED` event in the same file. Parent was not notified.
- Bonus: `durationMs=0` means the empty return was dispatch-level instant, not a provider stream death — a *third* failure shape the sensor does not distinguish.
**Required KB action**: correct G19 defense text (PATCHES P-2); propose sensor fix upstream of KB (extract child session from `session.created` tracking map, not from the empty output string).

## C-3. AGENT_COMMUNICATION.md §3 STRP claim is overstated → contradicts our own G9
**KB claim**: "Every `task()` call MUST include a `task_id`… On failure, resuming with the SAME task_id restores full active context."
**Refutation evidence**: R_SUBAGENT_RECOVERY_PROTOCOL_20260807.md + GOTCHAS G9: same-task_id resume restores context for FAILED/stalled tasks only; CANCELLED tasks get a fresh session (Phase 3 Kali incident). "Every call MUST include task_id" also overstates the tool contract (task_id is optional; subagent sessions are addressable by session ID per PGTL paging-universality entry, lines 111-118).
**Required KB action**: rewrite §3 bullet 2 with the stalled/cancelled split + forensic-recovery path (PATCHES P-6).

## C-4. CLI_IDE_ECOSYSTEM.md contains three factually stale claims
1. "OpenCode … Uses `opencode.json` (`mcpServers`)" — WRONG key name. Live key is `"mcp"` (`opencode.json:34`). `mcpServers` is the Claude Code/Cursor schema.
2. "Supports 11 custom agents" — STALE. `.opencode/agents/` now holds 14 agent files (build.md deprecated → 13 live incl. node parameterized by slot); opencode.json `agent{}` block defines 12 named agents.
3. "Omega Hub MCP server (`:8016/sse` or `:8016/mcp`)" — live config uses `http://127.0.0.1:8016/mcp` (Streamable HTTP, C-4b dual transport); SSE transport is the legacy path (firecrawl entry still uses `/sse`, `opencode.json:47`).
**Disposition proposal**: do NOT merge-and-delete. Mark frontmatter `status: DEPRECATED` + `superseded_by: platforms/opencode/ + other_platforms/` per docs/kb/AGENT_KB_PROTOCOL.md supersession convention; keep as link-target stub (full content already duplicated in the two newer modules). See PATCHES P-7.

## C-5. GROK_FLEET_ARCHITECTURE.md pricing claims are UNVERIFIABLE against any local authoritative source
Claims checked: "$5.00 per 1k calls" server-side tools; "≥200K tokens triggers 2x penalty"; "Prompt caching $0.20-$0.30/1M"; "Grok Build open-sourced July 15, 2026".
**Finding**: no local corpus document (PGTL, PIVOT_LOG, docs/kb/grok*, R_* grok research) corroborates any xAI price point or the open-source date. PGTL's only authoritative Grok-adjacent ruling is architectural (OC Zen keyed by IP, line 188-194), not pricing. D-582 (free-tier-only cost model, PIVOT_LOG:222) further reduces operational relevance of paid-xAI optimization.
**Required KB action**: annotate each claim `unverified-local · single-source · last_verified: never` and add pointer that fleet policy is free-tier-only until V-1/W-1 land (PATCHES P-8).

## C-6. EXPERT_SESSIONS.md page format deviates from the ratified pattern it cites
**Claimed basis**: "Invocation follows the house pattern … NODE_EXPERT_SESSIONS_PLAN.md §3".
**Deviation**: §3 template requires a charter-header line — `[Charter header: You are N_X <keeper>, <department>. Charter: this file §4.]` — grokster's template substitutes `[Domain: <domain>. Context: this KB index.]`. Defensible (grokster has no §4 charter), but MR-discipline says declare the deviation, not silently differ. Additionally:
- None of the three registered session IDs exist in `data/coordination/TASK_REGISTRY.json` (grep: zero hits) — the "flagged to Kali" note is accurate but should be elevated: unregistered sessions are invisible to `generate_session_registry.py` renders (scripts/generate_session_registry.py reads TASK_REGISTRY.json exclusively, lines 5-14).
- Session `ses_fe8cf0b39ffeL3L8eaMEj3CW9H` (opencode-platform, marked CONSULTABLE) threw a SILENT_STALL_TASK at 2026-08-26T03:12Z — context preserved in DB, but status row deserves a post-stall integrity note.
See PATCHES P-5.

## C-7. DP blueprint premise check: 06_PHASE_1_PLAN.md is HISTORICAL — do not cite its numbers as constraints
Mission item asked to verify DP premises vs `docs/specs/context_injection/phase1_spec/06_PHASE_1_PLAN.md`. Findings:
- That exact path does not exist; the plan lives at `docs/specs/context_injection/06_PHASE_1_PLAN.md` (MINING_LOG #10 correctly used the top-level path but stamped it 🟡 HISTORICAL, superseded by `phase1_spec/09_SPEC_DEVIATIONS.md`).
- Its numbers are pre-Carmack-rewrite: Tier 0 ≈45K tokens pinned, `preserve_recent_tokens: 80000`, `reserved: 20000`, AGENTS.md ~80K chars (~20K tokens). Current ratified direction (N7 charter, NODE_EXPERT_SESSIONS_PLAN.md:83): MANDATES_CONDENSED.md 57-line Tier 0, compaction buffer 50K/20K, **18K base token target** for Tier 0 viability.
- New hard constraint since the plan: D-602 ground truth — auto-compact threshold is CONFIGURABLE, house value raised to 75%→85%, evaluated at tool-completion boundaries (PIVOT_LOG:422-433; ARCHITECTURE.md:48 already reflects this — CONFIG_REFERENCE §4 does not).
**Action**: DP blueprint must cite 09_SPEC_DEVIATIONS + N7 charter numbers, never 06_PHASE_1_PLAN values (PATCHES P-9).

## C-8. Freshness scheme vs AGENT_KB_PROTOCOL staleness tiers — reconcile, don't fork
grokster rot_class (fast/medium/slow) and the Omega-KB Protocol's 3-tier staleness (Critical/Moderate/Cosmetic, AGENT_KB_PROTOCOL.md:214-222) are isomorphic but diverge in two respects the KB should adopt:
1. Protocol distinguishes `reviewed` (accuracy verified) from `modified` (any edit) — grokster docs carry only `last_verified`, which conflates them. An append-only mining pass *modifies* without *reviewing* prior content.
2. Protocol mandates explicit supersession chains (`supersedes`/`superseded_by`) — grokster's merge-stub strategy (KB-D-007) keeps stubs but carries no machine-readable supersession field.
Full reconciliation proposal in PATCHES P-10.

## C-9. Minor: MINING_LOG contradiction #3 phrasing risk
MINING_LOG says global plugin dir singular is "by design — sovereign-compaction.ts target path is CORRECT as-singular". True per 06_PHASE_1_PLAN.md:90/158 (`~/.config/opencode/plugin/`), but C-1 shows project-level loading works from the PLURAL dir via auto-discovery — so the singular/plural rule is: global = singular-by-design, project = plural-auto-discovered, explicit file:// entries = must match reality. State all three legs or readers will over-generalize again.

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ HARDENING-CORRECTIONS ⬡ 2026-08-26*
