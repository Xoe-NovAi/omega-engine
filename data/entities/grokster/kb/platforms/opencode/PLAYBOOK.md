<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# OpenCode CLI — Canonical Operating Playbook (Omega Engine House Practices)

**KB Entry**: grokster/platforms/opencode/PLAYBOOK
**last_verified**: 2026-08-26 · **rot_class**: medium (practices stable; version-pinned details fast)
**Scope**: Omega Engine repo, opencode binary observed at **1.18.23** (self-updated Aug-25 unattended — autoupdate ACTIVE; freeze pending F0 of config remediation plan. Legacy Architect ruling pinned 1.18.19 — premise broken by autoupdate, see GOTCHAS G31).
**F0 freeze protocol (pre-execution)**: `OPENCODE_DISABLE_AUTOUPDATE=true` + global `"autoupdate": false` BEFORE any config surgery; record binary hash + plugin commit (7db338b). `tui.json` may not exist on all installs (absent here) — skip gracefully.
**Sources**: `docs/specs/context_injection/phase1_spec/` (esp. 09_SPEC_DEVIATIONS.md), `docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md`, `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`, `docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md`, `docs/research/R_SUBAGENT_RECOVERY_PROTOCOL_20260807.md`

---

## §1 Sessions & Context Discipline

- **Compaction trigger doctrine (D-602 ground truth)**: threshold is **configurable**, set to **85%** of window by the Architect. Auto-compact NEVER fires below it without manual `/compact`. Overshoot past 85% happens only when a tool call that STARTED before the mark completes and pushes over — evaluation occurs at **tool-completion boundaries**. Never plan around a fixed percentage in general docs; upstream formula is `total_tokens > context_limit − max(output, 20000) − reserved`.
- **Never consume `opencode db` output through a pipe.** Silently truncates (~1.3MB ceiling, exit 0, empty stderr; reproduced 5/5). Always stage: `opencode db "..." > /tmp/stage.json && parse /tmp/stage.json`. Byte-count verify for forensic reads. Upstream-bug-worthy.
- **No session ID is exposed to wrapped processes.** Only `OPENCODE_PID` + `OPENCODE=1` env vars exist. PID+timestamp correlation is APPROXIMATE — never cite as Tier-0 ground truth (M22). Feature request pending: `OPENCODE_SESSION_ID`.
- Defense-in-depth context preservation ordering: checkpoint sidecar @80% (primary) → sovereign-compaction plugin hook (secondary) → SESSION_ANCHOR.md (tertiary).

## §2 Subagent Dispatch (task tool)

- **MANDATORY inline context** (SUBAGENT_DISPATCH_PROTOCOL §0): subagents cannot reliably read files by path during first tool calls. Three identical dispatches proved it: path-reference → empty result ×2; inline-embedded content → 544-line Temple-Grade report. Embed actual content under `## Inline Context`; paths are supplementary only. Exceptions: >500-line files (summarize inline), binaries, files-to-modify.
- **task_id continuation — the split truth**:
  - **Stalled/errored tasks**: resume with SAME `task_id` → full active-context restoration (STRP-v1.0.0). Verify after every resume with *"Tell me what you have in active context... NO FILE READS."*
  - **Cancelled tasks**: task_id reuse does NOT work — creates a new session, no continuation. Recover via forensics instead (sessions-explorer timeline/summary/grep-session → extract context → relaunch).
  - Every launch MUST carry a persistent task_id, format `{Tier0-ID}-{domain}-{action}-{date}-{seq}`; log to Hivemind `task_ids[]` + session_gnosis.md.
- **subagent_depth**: config key since 1.18.2, default 1 (prevents nested subagents). Live repo sets `"subagent_depth": 2`.
- Dispatch-suffix hygiene: synthetic trailing lines ("call the task tool with subagent X") inside task() prompts are wrapper artifacts — never missions.

## §3 Permissions Model Operation

- Precedence (high→low): session approvals (persisted) → agent-level `permission` → global config `permission` → built-in defaults (`*.env`=ask, `external_directory`=ask, doom_loop=ask).
- **Last matching rule wins** — put broad `"*"` first, specifics after.
- `deny` throws DeniedError back to the model (visible failure); denied skills are hidden from advertisement entirely.
- Doom-loop detection: same tool call repeated 3× identical input → `ask`.
- ⚠️ Live config currently has `"/*": "allow"` under external_directory — wide-open, flagged as risk (see GOTCHAS).

## §4 MCP Configuration

Live remote servers (opencode.json `mcp`): omega-hub (:8016/mcp), searxng (:8018/mcp), exa (keyed header `${EXA_API_KEY}`), parallel-search; firecrawl SSE disabled. Pattern: `"type": "remote", "url": ...`. Block whole servers via permission: `"mymcp_*": "deny"`.

## §5 Skills Operation

- Discovery scans `.opencode/skills/*/SKILL.md`, `~/.config/opencode/skills/`, `.claude/skills/`, `.agents/skills/`.
- Only `name`+`description` advertise upfront (~50 tok each); full body loads on `skill({name})` call. Already lazy — do NOT claim savings from "opt-in" beyond shrinking the ad list.
- Opt-in lever = `permission.skill` glob patterns in opencode.json (NOT frontmatter — `auto_load:` does not exist, zod parses name/description only).
- Never prune target: skill-type tool outputs survive compaction pruning.

## §6 Plugins Operation

- Real plugin dir: `.opencode/plugins/` (**plural**). Registration via `plugin` array: npm names, `file:///abs/path.ts`, or dir names. npm plugins auto-installed by Bun into `~/.cache/opencode/node_modules`. Load order: global → project → global plugin dir → project plugin dir.
- Runtime = Bun. No Node-only APIs in plugins.
- House plugins (all in `.opencode/plugins/`): awareness.ts (event buffer → injects `<system-awareness>` into parent session via `client.session.prompt` with `synthetic:true, noReply:true`), error-capture.ts (subagent failure JSONL logs + parent injection + Hivemind notify), silent-stall-sensor.ts (detects protocol-clean degradations: SILENT_STALL_EMPTY, SILENT_STALL_TASK, TRUNCATED_ARGS, SLOW_DRIBBLE; **detection works; automated recovery is DEAD CODE** — parent-notification regex extraction returns empty, RECOVERY_ISSUED never fires; manual recovery required; see GOTCHAS G19).
- ⚠️ Registrations for awareness/error-capture still point at singular `.opencode/plugin/` in live opencode.json → registrations DEAD but plugins STILL LOAD via directory auto-discovery (G1 upgraded: dual-mechanism load model).

## §7 Model Routing Practice (DEV-12)

- Global top-level model should be `lmstudio/qwen3-4b-thinking` (local-first default all agents inherit). Per-agent pins ONLY where binding is intentional: kali (cloud floor `opencode/nemotron-3-ultra-free`) + verity (cheap critic `lmstudio/qwen3-1.7b`).
- CLI `-m` always wins; precedence chain: CLI flag > agent pin > session > global.
- Variant rule: never set `agent.<n>.variant` without confirming a non-empty variants map on the pinned binary (`opencode models --verbose`). Use invocation-time `--variant high` / TUI variant_cycle instead.
- TUI `/models` snap-back (#13456): agent pins make interactive model choice non-durable — another reason to prefer global-default + inheritance.

## §8 Verification Discipline

- Import-smoke gates MUST invoke `--help`, not just import (typer/click lazy construction defers all errors to invocation).
- Gates test REALITY not artifacts: behavioral checks (`opencode run "List your available skills"`) over grep-the-config checks.
- Binary pin FIRST before any compaction-key decision: record `opencode --version`, consult decision table, apply exactly ONE compaction family, never both.

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB v2.1.3 ⬡ 2026-08-26*
