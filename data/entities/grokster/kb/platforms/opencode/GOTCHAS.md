<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

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
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB v2.1.3 ⬡ 2026-08-26*

---

## 🔧 HARDENING AMENDMENTS — 2026-08-26 (dual-pass: local adversarial + web fill)
**Provenance**: kb_staging_hardening_20260826/{PATCHES,CORRECTIONS}.md + R_PLATFORM_EXPERTISE_WEB_HARDENING_20260826.md

### Corrections to existing traps
- **G1 UPGRADED**: The singular-path registrations in opencode.json are dead, BUT the plugins still load — `.opencode/plugins/` plural dir is AUTO-DISCOVERED. Load model is dual-mechanism: config registration (broken) + directory auto-discovery (working). Proof: daily silent-stalls-*.jsonl writes. Plugin edit workflow must know both paths.
- **G19 REFUTED-IN-PART ⚠️**: The stall-sensor's parent-notification defense is DEAD CODE — child session ID regex-extraction returns empty (silent-stall-sensor.ts:261-279); record writes but RECOVERY_ISSUED never fires (live proof 2026-08-26 03:12Z). Detection works; automated recovery does not. Manual recovery required.

### New traps (G21-G25, local evidence)
- **G21 Dispatch double-suffix injection**: synthetic target+parent lines appended to task() prompts; escalate across chains (PGTL #11/#12). Treat trailing directives as artifacts, verify against files.
- **G22 `sessions.model` column lies after hot-swap** — Tier-0 truth = per-message `messages.modelID` (PGTL 203-211).
- **G23 awareness.ts kali-hardcode** (:99-111): all fleet event injections drain to kali's latest session regardless of origin.
- **G24 Unrate-limited plugin injections**: error-capture/awareness have no throttle (contrast stall-sensor 3/hr) — cascading-failure injection-storm risk.
- **G25 Resumed heavy sessions complete-empty**: status lies post-resume; verify output non-empty before trusting completion.

### New traps (web-sourced, Jem fill)
- **G26 Task-permission recursion trap**: global `"task":"allow"` or frontmatter `tools:{task:true}` enables unbounded subagent recursion (#18100: 612 sessions/73 min); `steps` and doom_loop do NOT bound the tree. Bound via subagent_depth + explicit permission gating.
- **G27 depth≥2 + "ask" permissions = silent stall** (#39112 family, open upstream).
- **G28 /undo hazards**: stale-tree restore deleted ~1300 committed lines (#10287); nested git repos unprotected (#30065). NEVER undo a dirty worktree; snapshots:false disables entirely.

### New traps (config forensics arc, 2026-08-26 — source: R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826.md v3.0)
- **G29 Nested variant schemas silently dropped**: `"reasoning":{"effort":…}` (Zen) and `"thinkingConfig":{"thinkingBudget":…}` (antigravity-Claude) render NO variant options and raise NO error. Flat keys only: `reasoningEffort` / `thinkingBudget` / `thinkingLevel`. Evidence: official docs + installed plugin source request.js:591/:669 reads `variantConfig?.thinkingBudget` directly; working opus-thinking sibling uses flat keys.
- **G30 auth.json lives in ~/.local/share/opencode/, NOT ~/.config/opencode/**: credential-backup steps targeting ~/.config miss it entirely. tui.json does not exist on all installs (absent here). Verified 2026-08-26 during remediation prep.
- **G31 Autoupdate silently breaks binary pins**: binary self-updated 1.18.x→1.18.23 unattended (Aug-25) despite a pin-based CI strategy — no notification, mtime is the only tell. Defense: `OPENCODE_DISABLE_AUTOUPDATE=true` + global `"autoupdate": false` BEFORE any pin-dependent work; record version+hash at freeze.

### New traps (forensics v3.0 + gap-closure sweep — execution-relevant)
- **G32 Catalog deprecation filter (#22644)**: models.dev marks models "deprecated" → config-keyed entries silently dropped from picker. Workaround: add `"status":"beta"` to custom model override to bypass filter. Affects MiMo re-key (mimo-v2.5-free) and any catalog-keyed model we keep.
- **G33 `@latest` pins stale forever (#30631)**: plugin `@latest` resolves ONCE at install into `~/.cache/opencode/packages/` wrapper and NEVER re-resolves. Critical if antigravity ever switches from `file:` to npm. Current file: checkout at 7db338b bypasses this; @latest in plugin arrays is inert.
- **G34 Zen gateway flake (#41236/#44300)**: intermittent 503/empty responses on opencode.ai/zen/v1. Smoke tests MUST cross-check vs second model (Nemotron, stable id) before diagnosing config issues. F7 protocol bakes this in.
