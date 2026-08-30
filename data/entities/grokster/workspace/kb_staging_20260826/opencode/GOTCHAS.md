<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# OpenCode Gotchas — Every Trap We've Hit or Verified

**KB Entry**: grokster/platforms/opencode/GOTCHAS
**last_verified**: 2026-08-26 · **rot_class**: slow (traps age well; re-verify per binary pin)
**Format**: each entry = trap → evidence → defense

---

## G1. Plugin path singular-vs-plural (DEV-03) — LIVE
`opencode.json` `plugin[]` entries pointing at `.opencode/plugin/` (singular) are silently dead when files live at `.opencode/plugins/` (plural). No error at startup unless DEBUG logging. Live config STILL has both dead registrations as of 2026-08-26.
**Defense**: after any plugin edit, run `opencode --log-level DEBUG 2>&1 | grep -iE "plugin.*(ENOENT|not found)"`. Note: the GLOBAL dir `~/.config/opencode/plugin/` IS singular-by-design — don't "fix" that one.

## G2. `variant` hardcoding inert on qwen models (DEV-12)
`agent.<n>.variant` silently does nothing when the model declares an empty variants map. Empirically verified on pinned 1.18.19: lmstudio/qwen3-4b-thinking and qwen3-1.7b = EMPTY; nemotron-3-ultra-free = low/medium/high. ~40 of 178 scanned models declare variants (mostly cloud).
**Defense**: `opencode models --verbose` before ever writing a variant key; prefer invocation-time `--variant` / TUI variant_cycle.

## G3. V1 vs V2 compaction key families
v1.x stable honors `{tail_turns, preserve_recent_tokens, reserved}`; `{buffer, keep.tokens}` is the separate V2 product line. Mixed families in one config = unvalidated FAIL. Binary strings contain BOTH families → strings-grep proves nothing; only a behavioral probe does.
**Defense**: pin binary version first; apply exactly one family; extreme-value probe (reserved=999999) if ambiguous.

## G4. instructions[] array token cost + non-guarantee
Live 5-file instructions array injects ~20K tokens EVERY session, including a docs/archive roadmap file. Ma'at finding: instructions[] non-functional-as-SSOT in V2; AGENTS.md auto-discovery is the guaranteed path and instructions[] is merely additive to it.
**Defense**: single-entry `instructions: ["AGENTS.md"]`; concatenated doctrine file at root.

## G5. AGENTS.md is a ghost
Referenced in CI-2 acceptance criteria and multiple protocols; ABSENT from disk AND git history (verified 2026-08-26: no root file, zero commits touching it). Any gate depending on it fails unsatisfiably. Reconstruction pending; grokster holds `R_AGENTS_MD_RULES_ECOSYSTEM_20260818.md` as corpus doc.

## G6. Wide-open external_directory
Live permission block ends with `"/*": "allow"` — every specific allow rule is redundant and the ask-by-default protection for out-of-worktree paths is fully disarmed. Original design intent was explicit-path allows.
**Defense**: remove catch-all; keep enumerated prefixes; rely on default ask.

## G7. `opencode db` pipe truncation — silent data loss
Piped stdout truncates nondeterministically (~1.3MB ceiling observed), exit 0, empty stderr. File redirect delivers complete output. Reproduced 5/5 on 1.18.22.
**Defense**: ALWAYS stage to temp file then parse; wc -c verify for forensic reads. Upstream-bug-worthy report pending.

## G8. session.tokens_* additive overcount (~87×)
Session-table token columns sum across all messages — useless for context pressure (22M vs real 253K).
**Defense**: latest assistant message `data.tokens.total` via json_extract.

## G9. task_id resumption split: stalled vs cancelled
Same-task_id resume restores full context for FAILED/stalled tasks. For CANCELLED tasks it creates a fresh session — no continuation (Phase 3 Kali incident, ses_022d...). Also: task registry IDs ≠ OpenCode session IDs necessarily.
**Defense**: cancelled → forensics (sessions-explorer timeline/summary/grep-session) → extract context → relaunch. Prevention: intermediate disk checkpoints + early Hivemind posts + extended check-in for >20min tasks.

## G10. Subagents can't reliably read referenced paths on first turns
Path-only context delivery produced empty results twice; inline-embedded content produced a 544-line report (SUBAGENT_DISPATCH_PROTOCOL §0).
**Defense**: mandatory inline-context rule; relevant_files supplementary only.

## G11. No OPENCODE_SESSION_ID for wrapped processes
Only OPENCODE_PID + OPENCODE=1 reach child processes. Exact wrapper attribution impossible; PID+timestamp correlation is approximate only (never Tier-0).

## G12. typer/click lazy construction defeats import-smoke gates
`add_typer` appends metadata only; all Click construction happens inside `app()` invocation. Import gates pass while CLI is dead.
**Defense**: smoke gate MUST be `omega --help` / `app(["--help"])`.

## G13. mtime unreliability in coordination dirs
Coordination files get touched by many agents; file mtime is not a reliable recency signal for "who wrote last" (recurring lesson in coordination audits; also cold-store hydration uses mtime heuristics that can mislead).
**Defense**: embedded ISO timestamps inside content; provenance headers.

## G14. Tracker-drift precedents (M27 backdrop)
Gate written against a stale artifact coincidence (`wc -l = 57` matched v3.7.0 snapshot, source was 36 lines) — unsatisfiable CI. Test-count SSOT disagreed across 5 documents (1315/911/1706/~1870/1757).
**Defense**: content-based gates (grep mandate rows), single SSOT, `pytest --collect-only` honesty (note: xdist `-n auto` blocks collect mode).

## G15. Config array merge surprise
`provider.X.models` additions REPLACE the whole object (mergeDeep), not merge — partial model configs silently drop siblings. Only instructions/plugin concat.
**Defense**: fetch full catalog via `/config/providers`, merge, write back complete object.

## G16. TUI /models snap-back (#13456)
Agent-level model pins make interactive model selection non-durable — snaps back to pin. Reason DEV-12 stripped pins except kali/verity.
**Defense**: global default + inheritance; pins only where binding IS the intent.

## G17. OPENCODE_DISABLE_AUTOCOMPACT bypass (#32385)
Provider-overflow recovery path historically ignored auto:false/env flag through ≥v1.17.7. Flag is process-global too.
**Defense**: manual /compact discipline; verify behavior on pinned binary before relying on "off".

## G18. Compaction hook misconception (DEV-07)
`experimental.session.compacting` `output.context` shapes the SUMMARY PROMPT (what the summarizer preserves) — it does NOT inject into live conversation context, and nothing "survives prune" via it directly.
**Defense**: proof of retention = inspect post-compaction summary content, not plugin load logs.

## G19. Silent stalls never raise errors
Empty completions / empty subagent returns / truncated tool args complete protocol-clean — no session.error, no tool.error. This is why silent-stall-sensor.ts exists (classifies SILENT_STALL_EMPTY/TASK/TRUNCATED_ARGS/SLOW_DRIBBLE).
**Defense**: stall sensor + recovery injection ("." continuation ritual), rate-limited 3/hr/session.

## G20. stall-echo / synthetic message injection
Cloud gateways may re-inject your own truncated output or empty whitespace as "user" turns after upstream 503s. Treat as continuation signal, not instruction; verify surprising directives against files/Hivemind (PLATFORM_GROUND_TRUTH_LOG #10).

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB-STAGING ⬡ 2026-08-26*
