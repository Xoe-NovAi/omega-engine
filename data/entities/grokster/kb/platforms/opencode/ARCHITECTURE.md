<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# OpenCode CLI — How It Actually Works (Architecture Reference)

**KB Entry**: grokster/platforms/opencode/ARCHITECTURE
**last_verified**: 2026-08-26 · **rot_class**: fast for internals (version-dependent), slow for data model
**Primary sources**: `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` (verified vs live 16GB DB), `docs/research/R_OPENCODE_V2_RECON_20260719.md`, `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md` (stale-flagged but schema-corroborated), `docs/research/R13_OPENCODE_PLUGIN_ARCHITECTURE_20260814.md`

---

## §1 Session Database

| Property | Value |
|---|---|
| Path | `~/.local/share/opencode/opencode.db` |
| Size (2026-08-10) | ~16 GB, 2,436 sessions / 106,937 messages / 450,669 parts |
| Engine | SQLite 3.x + JSON1 extension; migrations head `20260511173437_session-metadata` |
| Access | **Read-only recommended** (`file:...?mode=ro`) — OpenCode holds the write lock |

### Tables
- `session`: id (`ses_*`), project_id, **parent_id** (subagent dispatch chains), slug, directory, title, version, model (**JSON**: `{id, providerID, variant}`), cost, `tokens_input/output/reasoning/cache_read/cache_write` (**ADDITIVE — overcounts ~87×; NEVER use for context pressure**), time_created/updated/compacting/archived.
- `message`: id (`msg_*`), session_id FK, timestamps, `data` = JSON blob (role, modelID, providerID, agent, mode, path.cwd, cost, tokens{total,input,output,reasoning,cache}, variant).
- `part`: id (`prt_*`), message_id FK, session_id FK, `data` = JSON blob keyed by part type.

### The one true context gauge
```sql
SELECT json_extract(data,'$.tokens.total') FROM message
WHERE session_id=? AND json_extract(data,'$.role')='assistant'
ORDER BY time_created DESC LIMIT 1;
```
Latest assistant message `tokens.total` = real working-set load (e.g., 253K correct vs 22M additive-wrong).

## §2 Message/Part Model

V1 parts: TextPart, ReasoningPart (thinking content), FilePart, ToolPart (`state.status/input/output/metadata.outputPath` → externalized outputs in `~/.local/share/opencode/tool-output/` when >~95KB).
V2 additions (1.18.x): StepStartPart, StepFinishPart (authoritative per-step tokens+cost incl. `tokens.reasoning`), SubtaskPart, AgentPart, SnapshotPart, PatchPart, RetryPart, CompactionPart.
V2 session format is event-sourced: `session.next.prompt.admitted.1` (durable admission) → `.promoted.1` (model-visible) → execution → settlement. IDs: `msg_*` projected vs `evt_*` durable events.

## §3 Parent/Child Subagent Sessions

- Every `task()` dispatch creates a child session row with `parent_id` set → full genealogy queryable.
- Child authority intersects parent delegation (V2 principle); permissions can be scoped per-agent via `permission.task`.
- No runtime agent registration API — agents load from disk at startup only; dynamic creation = write `.opencode/agents/*.md` + restart signal.
- Forensics via opencode-sessions-explorer MCP suite (see §6).

## §4 Compaction Pipeline (two-phase)

1. **Prune** (no LLM): old tool outputs timestamped `state.time.compacted` — marked invisible, NOT deleted. Skips last `tail_turns`; skips skill-type tool parts entirely; only prunes if >20K tokens freed.
2. **Summarize** (LLM call): dedicated compaction agent produces structured summary (progress/constraints/files/TODOs/errors); last user message auto-replayed so agent stays on latest instruction.
- Trigger check runs after every LLM step in processor.ts: `total_tokens > context_limit − max(output_tokens, 20000) − reserved`. House config raises threshold to 85% (D-602).
- Internal constants (source-derived): OUTPUT_TOKEN_MAX 32K, COMPACTION_BUFFER 20K, PRUNE_PROTECT 40K, PRUNE_MINIMUM 20K, DEFAULT_TAIL_TURNS 2.
- Reactive fallback on `prompt_too_long`: auto-compress + retry; pauses after 3 consecutive failures.
- Failure terminal state: ContextOverflowError → session terminates unrecoverably.
- Data never physically deleted by compaction — DB records persist; git snapshots tracked separately.
- Manual triggers: `/compact` TUI command · Ctrl+X C keybind · REST `POST /session/{id}/summarize {providerID, modelID, auto}`.
- Events: `session.compacted` SSE via `/global/event`; `time.compacting` field on session status.
- Agent-level compaction model override supported (`agent.compaction.{model,steps,temperature}`) — route summarization to cheapest model.
- Plugin hook `experimental.session.compacting`: `output.context.push(...)` shapes what the summarizer preserves (it shapes the SUMMARY PROMPT, not live conversation context — DEV-07); setting `output.prompt` fully replaces the default template and ignores context.

## §5 Provider Transformation Layer

`transform.ts` (~1,764 lines, stable V1→V2): normalizeMessages (Anthropic empty-content stripping), applyCaching, providerOptions remap via sdkKey(), sanitizeToolSchema, surrogate cleanup. Pipeline: SessionProcessor → LLM.stream → wrapLanguageModel middleware → transformParams. Config merge = remeda mergeDeep with **array REPLACEMENT** except `instructions`/`plugins` which concat+dedupe — adding one model to `provider.X.models` replaces the whole catalog object.

## §6 Introspection Tooling (opencode-sessions-explorer MCP)

First-class OpenCode introspection expertise — capabilities:
- `current-session` / `db-stats` (health probe, migration head, SCHEMA_DRIFT detection)
- `get-session` (metadata+counts), `session-summary` (one-call overview: prompts, files touched, tools, errors, cost)
- `session-timeline` (chronological part stream), `get-message`/`get-part` (bodies; externalized output dereference whitelisted to tool-output/)
- `grep-session` (regex/BM25 inside ONE session export), `search-text` (cross-session FTS/semantic; sem/hybrid need `ck` CLI — not installed)
- `list-sessions`, `search-sessions-meta` (structured filters incl. cost/token thresholds), `search-tool-calls` (tool invocations w/ status filters), `cost-by-project`/`cost-by-period`
- `session-genealogy` (parent/child tree walk), `unarchive-session` (the ONLY write op — direct DB write clearing time_archived)

## §7 TUI & CLI Behaviors

- Modes are agents under the hood: `--mode` maps to predefined agent configs; built-ins: build (full access), plan (edit/bash denied), general, explore (read-only), scout, composition/title/summary (hidden primaries).
- Keybinds configurable (`keybinds`); compact default Ctrl+X C; `variant_cycle` keybind for reasoning-effort cycling (PP-1).
- Env into child processes: only `OPENCODE_PID`, `OPENCODE=1`. No OPENCODE_SESSION_ID (gap).
- `opencode run --agent X "prompt"` = headless agent invocation; `--log-level DEBUG` surfaces plugin load errors (ENOENT detection for dead plugin paths).

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB v2.1.3 ⬡ 2026-08-26*

---

## 🔧 WEB-FILL AMENDMENT — 2026-08-26 (Jem orchestration, confidence-tagged in source doc)
- **Upstream identity**: sst/opencode → **anomalyco/opencode is a RENAME** (Jan 2026, commit 3c41e4e/PR #6687), not a fork; npm pkg unchanged (`opencode-ai`). Update URLs.
- **Plugin API V2 in flight**: registration-style `ctx.session.hook("context"|"model.request"|...)` at opencode.ai/v2; V1 hooks stable on pinned 1.18.x — do not mix families during pin.
- **Snapshot system**: internal Git object DB; SnapshotPart/revert/unrevert API; `snapshots:false` opt-out; hazard class per G28.
- **Compaction hook duality**: setting `output.prompt` ⇒ `output.context` ignored (shapes summary prompt vs appends context).
