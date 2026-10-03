<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# opencode.json — Full Config Key Reference (with House Values + DEV Rulings)

**KB Entry**: grokster/platforms/opencode/CONFIG_REFERENCE
**last_verified**: 2026-08-26 · **rot_class**: medium
**Sources**: live `opencode.json` (read 2026-08-26), `docs/research/R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md`, `docs/specs/context_injection/phase1_spec/02_OPENCODE_JSON_DIFF.md` + `09_SPEC_DEVIATIONS.md`

---

## §1 Config Precedence & Merging

Low→high: remote `.well-known/opencode` → `~/.config/opencode/opencode.json` → `OPENCODE_CONFIG` env → `./opencode.json` → `./.opencode/opencode.json` → `OPENCODE_CONFIG_CONTENT` env → managed config (`/etc/opencode/`) → MDM.
Variable substitution: `{env:VAR}`, `{file:path}`. JSONC supported. Merge = deep-merge with **array replacement**, EXCEPT `instructions` and `plugin` arrays which **concat+dedupe** across sources.

## §2 Top-Level Keys

| Key | House value / note |
|---|---|
| `$schema` | `https://opencode.ai/config.json` |
| `model` | Live: `opencode/nemotron-3-ultra-free` ⚠️; DEV-12 target: `lmstudio/qwen3-4b-thinking` (local-first global default) |
| `small_model` | Live: nemotron-3-ultra-free |
| `default_agent` | `kali` |
| `subagent_depth` | `2` (live). Upstream key since 1.18.2, default 1 |
| `instructions` | Live: 5-file array (~20K tok cost!) incl. a docs/archive file; DEV target: `["AGENTS.md"]` single entry — AGENTS.md is the guaranteed auto-discovery path, instructions[] is ADDITIVE to it |
| `compaction` | see §4 |
| `plugin` | see §5 |
| `permission` | see §6 |
| `mcp` | see §7 |
| `provider` | see §8 |
| `agent` | see §3 |
| Others (schema-documented) | username, autoupdate, logLevel, snapshot, share, shell, disabled_providers, enabled_providers, watcher.ignore, experimental, command, formatter, lsp, keybinds, tui, server, attachment. `tools` = DEPRECATED → use `permission` |

## §3 Agent Config (inline in opencode.json AND/OR .opencode/agents/*.md frontmatter)

Frontmatter/inline schema: `description` (required), `mode` (primary/subagent/all), `model`, `variant`, `temperature`, `top_p`, `prompt` (+`{file:path}` support), `steps` (max iterations), `disable`, `hidden` (hide from @ autocomplete), `color`, `permission` overrides. Unknown fields pass through to provider as model options (not enforced).
House pattern (⚠️ CORRECTED 2026-09-23 in the live KB): prompt bodies live in `.opencode/agents/<name>.md` (frontmatter + body), loaded by OpenCode's native directory scan; an inline def may bind one with `"prompt": "{file:.opencode/agents/<name>.md}"`. **`"instructions": [...]` must not be used in an agent block** — it is not a schema field, is forwarded to the provider as a model option, and collides with OpenAI's real `instructions` option (type `string`), which broke every `@ai-sdk/openai` OpenCode-Zen model with `invalid openai provider options`. Evidence: `data/coordination/CLINE_ZEN_PROVIDER_FIX_20260923.md` §2/§12. 12 agents live (makali, jem, doom_guy, roc_racoon, researcher, kali, maat, lilith, verity, slot, john_carmack, grok_cli).
Verity isolation pattern (target): `mode: subagent` + `hidden: true` + `permission: {edit: deny, bash: deny, skill: deny}` + cheap model pin.
⚠️ `toolProfile` = silently-inert stub (upstream has no such key, no additionalProperties:false → neither fails validation nor does anything). Phase-2 intent documentation ONLY; claim no savings.

## §4 Compaction Keys — THE V1/V2 FAMILY TRAP

**V1 family (what v1.x stable honors — house primary)**:
```json
{"auto":true,"prune":true,"tail_turns":5,"preserve_recent_tokens":80000,"reserved":20000}
```
Live config still at old values: tail_turns 3 / preserve 40000 / reserved 10000.
**V2 family `{auto, keep:{tokens}, buffer}` belongs to the separate V2 product line** — inert or validation-failing on v1.x (schema sets additionalProperties:false). NEVER write both families simultaneously (D3). Gate any family choice on binary pin (`opencode --version`; preserve_recent_tokens named since v1.14.19).
Invalid/decoy keys that silently do nothing: `context_threshold`, `min_messages` (they come from community plugins/Claude Code, not OpenCode).
Env: `OPENCODE_DISABLE_AUTOCOMPACT=1` is **process-global** (no per-agent variant); KNOWN BYPASS #32385 — provider-overflow recovery ignored auto:false through ≥v1.17.7; treat "fully off" as unreliable until verified on pinned binary.
Agent-level compaction model override: `"agent": {"compaction": {"model": "...", "steps": 1, "temperature": 0.3}}`.

## §5 Plugin Registration

```json
"plugin": ["npm-pkg@latest", "file:///abs/path.ts", "dir-name"]
```
⚠️ **THE SINGULAR/PLURAL TRAP (DEV-03)**: correct project dir is `.opencode/plugins/` (plural). Live opencode.json registers error-capture.ts + awareness.ts under `.opencode/plugin/` (singular) which DOES NOT EXIST → both registrations silently dead. Detection: `opencode --log-level DEBUG 2>&1 | grep -iE "plugin.*(ENOENT|not found)"`. Global plugin dir: `~/.config/opencode/plugin/` (singular IS correct for the GLOBAL path per spec — e.g., sovereign-compaction.ts target lives there).

## §6 Permission Keys

Full set: read(path), edit(path), glob, grep, list, bash(command), task(agent name), skill(skill name), lsp, webfetch(URL), websearch, todowrite, question, external_directory(path), doom_loop. Actions: allow/ask/deny. Last-matching-rule-wins; MCP servers blockable via `"servername_*": "deny"`.
House external_directory: broad allows for Xoe-NovAi/**, media partitions, archives, ~/.lmstudio, ~/.ollama, ~/.config/opencode, /tmp/omega, ~/.local/share/opencode — plus ⚠️ `"/*": "allow"` catch-all that nullifies the entire ask-by-default protection (flagged for remediation).

## §7 MCP Config

```json
"mcp": {"name": {"type":"remote","url":"http://...","enabled":true,"headers":{"x-api-key":"${ENV}"}}}
```
Local stdio variant: `{type:"local", "command":[...], "environment":{...}}`.

## §8 Provider Config

Custom provider via npm adapter: `{"npm":"@ai-sdk/openai-compatible","options":{"baseURL":"http://localhost:1234/v1","apiKey":"..."}}` + `models: {id: {name, limit:{context,output}, variants:{low/medium/high:{reasoning:{effort}}}}}`.
House providers: lmstudio (6 local models, caps 4K–16K context), opencode (Zen free tier: mimo-v2.5 200K, nemotron-3-ultra-free **1M ctx/128K out**, deepseek-v4-flash-free 163K), openrouter (llama-3.3-70b-free).
Variant maps are model-specific: nemotron/deepseek declare low–high(/max); LM Studio models declare EMPTY variant maps → agent.variant inert there (DEV-12 empirical table).

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB-STAGING ⬡ 2026-08-26*
