<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

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
House pattern: agents defined inline in opencode.json with `instructions: [".opencode/agents/<name>.md"]` pointing at the prompt body files; 12 agents live (makali, jem, doom_guy, roc_racoon, researcher, kali, maat, lilith, verity, node, john_carmack, grok_cli).
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

Custom provider via npm adapter: `{"npm":"@ai-sdk/openai-compatible","options":{"baseURL":"http://localhost:1234/v1","apiKey":"..."}}` + `models: {id: {name, limit:{context,output}, variants:{high:{reasoningEffort:"high"}}}}`. **Variants are FLAT keys only** (see §9 amendment below — nested schemas silently dropped).
House providers: lmstudio (6 local models, caps 4K–16K context), opencode (Zen free tier, post-remediation 2026-08-26: mimo-v2.5-free 200K/32K [re-keyed from orphan mimo-v2.5 per catalog restructure], nemotron-3-ultra-free **1M ctx/128K out** [live-catalog VERIFIED 2026-08-26 via models.dev/api.json]; ~~deepseek-v4-flash-free~~ **DEAD upstream #43829 — entry DELETED in F5 remediation**; ~~openrouter/llama-3.3-70b-free~~ **override deleted in F2** — stock openrouter catalog serves instead).
**Zen base URL**: `https://opencode.ai/zen/v1` (not the standard OpenAI-compatible path) — required for custom Zen model overrides to route correctly.
**google-standard provider rationale**: retained because it hijacks the builtin `google` provider's model catalog (which ships stale/limited models) and replaces it with a curated set pointing at the correct Google AI Studio endpoints — the only way to get working Gemini models without the builtin catalog's stale entries.
Credentials live at `~/.local/share/opencode/auth.json` (NOT ~/.config/opencode/) — backup target for any config surgery.
Variant maps are model-specific: nemotron/deepseek declare low–high(/max); LM Studio models declare EMPTY variant maps → agent.variant inert there (DEV-12 empirical table).

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB v2.1.3 ⬡ 2026-08-26*

---

## 🔧 WEB-FILL AMENDMENT — 2026-08-26
- **`subagent_depth`**: default 1; parentID-chain depth walk; agent-visible error at limit; permission.task interplay per G26/G27.
- **Keybinds live in `tui.json`, NOT opencode.json** — separate file; variant_cycle + tui.* keys there.
- **`snapshots`:** boolean, internal git-object snapshot/revert system (see ARCHITECTURE amendment + G28).
- **`OPENCODE_SESSION_ID`: absent from official env table → unofficial/internal; do not depend on it** (needs local probe to confirm behavior).
- **Version intel**: latest v1.18.23 (Aug 25 2026); v1.18.20 surfaces resumable task_id on subagent failure (validates house playbook); v1.18.16+ ignores unknown config keys (pin forward-compat).

---

## 🔧 VARIANTS SCHEMA — AUTHORITATIVE (2026-08-26, official docs + INSTALLED PLUGIN SOURCE request.js:591/:669)
**Flat keys only. Nested schemas are silently dropped.**
- Zen/OpenAI-style models: `"variants": { "high": { "reasoningEffort": "high" } }` — flat, per opencode.ai/docs/models (which uses the `opencode` provider as its literal example); **live caps: mimo-v2.5-free = 200K/32K · nemotron-3-ultra-free = 1M/128K (models.dev verified 2026-08-26)**
- Antigravity Claude: `"variants": { "max": { "thinkingBudget": 32768 } }` — FLAT budget key; source reads `variantConfig?.thinkingBudget` directly (request.js:669); working sibling proof = antigravity-claude-opus-4-6-thinking in .opencode/opencode.json
- Gemini: bare flat `"thinkingLevel"` (e.g. `{ "low": { "thinkingLevel": "low" } }`)
- ⚠️ G29: nested `"reasoning": {"effort": ...}` or `"thinkingConfig": {"thinkingBudget": ...}` render NO variant options and no error — the silent-drop trap that killed our Zen thinking levels
- Built-in default variants exist per-provider for known providers; custom model overrides REPLACE catalog entries including any inherited defaults
- Config files MERGE with precedence remote < global < project; `.opencode/opencode.json` is valid project config
- Full forensics: docs/research/R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826.md
