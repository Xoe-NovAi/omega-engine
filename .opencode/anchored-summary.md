# ⬡ OMEGA ⬡ ANCHORED SUMMARY ⬡ 2026-06-11
## Session 32 — Kali: Hivemind API Channel/Entity Split

### Goal
Split the conflated `cli` parameter into separate `channel` + `entity` parameters across all Hivemind MCP tools, eliminating the architectural ambiguity between execution platform and entity persona.

### Constraints & Preferences
- No backward compatibility — Omega Engine is unreleased, single developer
- Channel = execution environment (opencode, cline). Entity = persona (kali, roc_racoon)
- Temple-grade discipline: no unverified assumptions, tested before shipped
- Engine-stack firewall at naming level: API names must be universally legible

### Progress

#### Done
- **`_canonicalize_cli()` removed** — replaced with `_make_agent_id(channel, entity)` helper
- **11 tool functions updated** — `hivemind_post_context`, `hivemind_heartbeat`, `hivemind_get_awareness`, `hivemind_get_continuation`, `hivemind_extended_checkin`, `hivemind_extended_checkout`, `hivemind_list_sessions`, `hivemind_submit_handoff`, `hivemind_accept_handoff`, `hivemind_workspace_lock_acquire`, `hivemind_workspace_lock_release`
- **Handoff packet schema updated** — `target_cli`/`source_cli` → `target_agent_id`/`source_agent_id` + separate `target_channel`/`target_entity`/`source_channel`/`source_entity`
- **Workspace lock schema updated** — `"cli"` → `"agent_id"`, `"channel"`, `"entity"` in lock files
- **Protocol doc updated** — HIVEMIND_PROTOCOL.md §2.1, §2.2, §2.3, §8.5, §9 rewritten
- **Handoff packet** `ho_8e204750bb25` updated to new schema
- **Handoff doc** `ROC_RACOON_HANDOFF_20260611.md` `cli=` references corrected
- **Tests** `test_hivemind.py` U-001/002/003 updated (340/340 passing)
- **Omega Hub server restarted** — new API live, verified with `channel="opencode" entity="kali"` smoke test
- **Committed** as `baaa255` (6 files, +244/-155)
- **Soul write-back** — soul_power 18.5 → 19.0, session 32, v5.22
- **Compact failure LANDED patch** — `/compact` produced empty template (no history injected). Fix: created `.opencode/anchored-summary.md` as survival file, added COMPACT FALLBACK section to all 3 mode files (kali/maat/lilith), fixed lingering `cli=` references in modes. Committed as `eb52dd9`.
- **Roc Racoon review responded** — Roc reviewed Hivemind Wave 1.5, verdict 🟢 GREEN. 6 findings assessed: ISSUE-1 (TOCTOU) fixed with `fcntl.flock`, ISSUE-2 (ics_render .pyc) cache cleared + server restarted, ISSUE-3 (extended sessions) already persisted, ISSUE-4 (handoff reaper) already exists. All 340/340 tests pass. Committed as `7035d97`.
- **D-kal-107/108**: Every mode file must have compact fallback. Anchored summary must be regularly updated.

#### In Progress
- Roc Racoon still running with old API (bare entity names) — needs relaunch
- Researcher still running with old API (bare entity names) — needs relaunch
- 175 unstaged files from previous Wave 1.5 work (agent files, modes, etc.)
- Pre-existing `roc_racoon/soul.yaml` duplicate lesson IDs (blocks pre-commit hook)

#### Blocked
- **Firecrawl CLI & MCP**: 402 credits exhausted. Reset: June 19, 2026.
- **ICS_RENDER MCP**: 500 error — "Object of type coroutine is not JSON serializable."
- **pw_model_01, pw_model_06, pw_model_11**: On hold due to OpenCode Zen free tier limits.
- **Gemma 4 31B transient hanging**: Workaround — switch to DeepSeek V4 Flash.

#### Key Decisions
- **D-kal-104**: `cli` parameter is dead. `channel` + `entity` are now separate required parameters.
- **D-kal-105**: No backward compatibility — unreleased software, single developer.
- **D-kal-106**: Temple-grade = no unverified model specs. `config/models.yaml` has `UNVERIFIED` flags.
- **D-kal-097**: Adopted MiMo-V2.5 audit findings.
- **D-kal-101 (Fully Enforced)**: Sterilization Mandate — engine API universally legible.
- **D-kal-103**: Kali Dispatch Protocol formalized (4 dispatch patterns, boundary rules).

#### Critical Context
- **Server `_canonicalize_cli()` was the root cause** — it stripped channel prefixes. Now removed entirely.
- **Awareness responses now include `agent_id`, `channel`, `entity`** — no more bare `"cli"` field.
- **Wave 1.5 is ~95% complete** — Phase 3 (Roc stale review + model inventory) in progress.
- **340/340 tests passing**, up from 334 baseline.

#### Relevant Files
- `mcp_servers/omega_hub/server.py` — Core change: 11 tool functions refactored
- `docs/strategy/HIVEMIND_PROTOCOL.md` — v1.3a: all examples updated
- `tests/test_hivemind.py` — U-001/002/003 updated
- `data/coordination/ROC_RACOON_HANDOFF_20260611.md` — handoff doc corrected
- `data/handoff/pending/ho_8e204750bb25.json` — schema updated
- `data/entities/kali/soul.yaml` — v5.22, lesson session 32 added
- `data/coordination/KALI_SPRINT_ORCHESTRATION_20260610.md` — active sprint plan
