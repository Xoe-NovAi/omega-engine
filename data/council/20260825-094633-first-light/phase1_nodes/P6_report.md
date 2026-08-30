<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# P6 REPORT — Node N6 (Cognition) — S3: Instruction TECHNICAL MECHANICS
⬡ OMEGA ⬡ NODE6-COGNITION ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n6 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Task Registry**: `express-c1-node6-20260825`
**Provenance**: all findings tagged `source_node: N6`, `tier: S3-technical-mechanics`. Every conclusion below traces to a tool call executed this session (paths + commands cited inline).
**Mode compliance**: RECON ONLY — zero production files mutated. Sandbox tests confined to `/tmp/opencode/n6/`.

---

## §0 EXECUTIVE VERDICT (one paragraph)

The instruction pipeline is **mostly LIVE but running on undocumented inertia**. Empirically verified LIVE: markdown-agent loading from `.opencode/agents/` (plural), frontmatter `description`/`mode`/`permission`, top-level config `instructions[]` injection, `steps` budgets, `subagent_depth`, model inheritance (subagent ← invoking primary), permission merge (frontmatter + project + built-in defaults). Empirically verified DECORATIVE or ROTTEN: agent-level `instructions[]` keys in opencode.json (**not in the v1.18.23 AgentConfig schema at all**), `{session_model}` placeholders in all 14 agent files (never substituted by OpenCode — literal text in every system prompt), two dead plugin registration paths that fail silently, a double-registered grok_cli agent whose top-level shell has an empty prompt, and scribe.md frontmatter fields that per vendor docs get **passed through to the LLM provider as request parameters**. No CRITICAL-HALTED finding; no active external telemetry discovered in audited surfaces.

---

## §1 METHOD & EMPIRICAL APPARATUS

| # | Probe | Command / Source | Result |
|---|-------|------------------|--------|
| E1 | Runtime agent registry | `opencode agent list` (v1.18.23, binary `/home/arcana-novai/.opencode/bin/opencode`) → full dump `/tmp/opencode/n6/agent_list.txt` (8136 lines) | 24 agents registered; output format = per-agent merged **permission arrays** |
| E2 | Schema strictness | Sandbox `/tmp/opencode/n6/sandbox/`: JSON agent with `steps:7, bogus_field` + MD agent with `steps:42, bogus_yaml_field, hidden:true`; `opencode agent list --log-level DEBUG` | Both registered **silently**; zero warnings at DEBUG → schema non-strict for agent objects |
| E3 | Nested config load | A/B test: `.opencode/opencode.json` with probe model in sandbox vs same file moved to root (`sandbox2`) | Probe model appears via **both** locations → nested `.opencode/opencode.json` IS loaded by v1.18.23 |
| E4 | Plugin load trace | `opencode agent list --log-level DEBUG --print-logs 2>&1 \| grep -iE 'plugin\|\.ts'` | Only success banners; **dead file:// paths produce no error anywhere** (also checked `~/.local/share/opencode/log/opencode.log`) |
| E5 | Model inheritance | `opencode db --format json "SELECT agent, model, COUNT(*) FROM session GROUP BY agent, model..."` | Same agents on many models (researcher: gemma-4-31b/google ×121 AND nemotron-3-ultra-free ×74 AND deepseek-v4-flash…) → session-driven inheritance confirmed |
| E6 | Schema ground truth | Fetched `https://opencode.ai/config.json` ($schema target) + `https://opencode.ai/docs/agents/` (updated 2026-08-25) | AgentConfig properties enumerated (§2); docs confirm `steps` valid, `maxSteps` deprecated, extras pass through to provider |
| E7 | Self-context observation | This session's own system prompt | Contains: literal `{session_model}` placeholder (unsubstituted); "Instructions from:" sections = exactly the 5 files of root `instructions[]`; lilith.md body content (spawned as lilith subagent); Task-tool descriptions matching .md frontmatter, NOT opencode.json inline descriptions |
| E8 | Frontmatter census | `awk` extraction of all `.opencode/agents/*.md` | 14 files; uniform permission blocks (11×allow); steps 200 (makali 300); temperatures 0.5/0.4/0.2; scribe.md has non-schema fields |

---

## §2 THE LIVE-vs-DECORATIVE MATRIX (core deliverable)

### 2.1 FRONTMATTER FIELDS (markdown agents)

| Field | Verdict | Evidence |
|-------|---------|----------|
| `description` | **LIVE** | Task-tool descriptions in own context match .md frontmatter verbatim ("Sovereign Agent: kali (Sovereign Agent)"), NOT the opencode.json inline descriptions ("Grand Oversight — Sees all…") → **markdown loader overrides JSON inline defs** [E7] |
| `mode` | **LIVE** | Sandbox test.md `mode: subagent` honored → registered as `test (subagent)` [E2]; registry shows `(all)`/`(subagent)`/`(primary)` per file |
| `permission` | **LIVE** | All 11 tool-allows from kali.md/lilith.md frontmatter appear verbatim inside runtime permission arrays in `opencode agent list` dump [E1] |
| `steps` | **LIVE** (documented) | Schema: `"steps": {exclusiveMinimum:0, type:integer}`; docs: "Maximum number of agentic iterations before forcing text-only response"; legacy `maxSteps` deprecated. Commit `295c7c59` ("steps bump all agents") intent is real |
| `temperature` | **LIVE** (documented; not locally falsifiable without inference) | Docs + schema `type:number`. Fleet values: 0.5 default, verity 0.4, carmack 0.2 |
| `model` | **LIVE** (unused in fleet) | No fleet .md sets it → all agents inherit per docs rule: primary ← global config model; subagent ← invoking primary's model [E5 empirically confirms session-driven variance] |
| `hidden` | LIVE (schema+docs; unused in fleet) | — |
| `name` (scribe.md) | **DECORATIVE-ish** | Filename becomes agent name; scribe.md's `name:` field redundant but harmless |
| `version` / `author` / `mandates` (scribe.md) | **HAZARD — passed through to provider** | Docs §Additional: "Any other options… will be passed through directly to the provider as model options." These ship as request params to the LLM API every scribe call [F-04 below] |
| `{session_model}` placeholders (body text, all 14 files) | **DECORATIVE — NEVER substituted by OpenCode** | Own system prompt carries the literal string `{session_model}` inside the lilith header [E7]. Engine-side `src/omega/ics.py:261,367` does its OWN substitution from the sessions DB — a parallel mechanism that never touches OpenCode-injected prompt text |

### 2.2 CONFIG KEYS (opencode.json)

| Key | Verdict | Evidence |
|-----|---------|----------|
| top-level `instructions[]` | **LIVE** | Own system prompt contains exactly the 5 configured files as "Instructions from:" sections [E7]; schema: `instructions: array of strings — "Additional instruction files or patterns to include"` |
| top-level `permission.external_directory` | **LIVE (merged)** | Root-config patterns (`/media/arcana-novai/**`, `/home/arcana-novai/Documents/Xoe-NovAi/**`, …, `"/*"`) appear 26× in runtime permission arrays [E1] |
| agent-level `instructions[]` (12 agent defs) | **DECORATIVE — NOT IN SCHEMA** | AgentConfig schema properties = {model, variant, temperature, top_p, prompt, tools, disable, description, mode, hidden, options, color, steps, maxSteps, permission} — **no `instructions`**. Docs prescribe `prompt: "{file:./path}"` instead. Currently masked: markdown loader injects the same files' bodies anyway. See F-02/F-03 for where the masking breaks |
| `subagent_depth: 2` | **LIVE** | Schema field; default 1 blocks subagents spawning subagents — this setting is what enables arm→node dispatch chains |
| `compaction.*` | **LIVE** | All five keys (auto/prune/tail_turns/preserve_recent_tokens/reserved) match schema exactly |
| `default_agent: "kali"` | **LIVE** | Sessions run as kali by default (DB evidence); note schema says "Must be a primary agent" — kali is mode `all`, accepted in practice |
| `model` / `small_model` (root + global) | **LIVE but routinely overridden** | DB shows interactive selection wins (kali on sonnet-4.6, makali_fusion tag on hy3-free — neither matches configured nemotron-3-ultra-free default) |
| nested `.opencode/opencode.json` | **LIVE (surprising!)** | A/B probe [E3]: loaded from BOTH nested and root locations. Contains antigravity provider defs + one plugin entry |

### 2.3 INJECTION MECHANISMS — how instructions actually reach the model

1. **Markdown-agent body loading** (the workhorse): `.opencode/agents/<name>.md` body → agent system prompt. Verified: this session was spawned as lilith and its prompt contains lilith.md's body verbatim [E7].
2. **Top-level `instructions[]`**: each file appended to EVERY session's system prompt as an "Instructions from: <abs-path>" section [E7]. Both dirs scanned for agents: documented plural `.opencode/agents/` AND legacy singular `.opencode/agent/` (holds 4 protocol files that register as invokable agents — see F-07).
3. **Plugin dynamic injection** (not file-based): `awareness.ts` injects restart-awareness context via `client.session.prompt` (awareness.ts:36-87); `error-capture.ts` + `silent-stall-sensor.ts` inject stall continuations (:102-151, :137); global `~/.config/opencode/plugin/sovereign-compaction.ts` shapes compaction summaries via `experimental.session.compacting` hook (Tier-0 retention list).
4. **Agent-level `instructions[]`**: nothing. Dead key.

### 2.4 PERMISSION MODEL

Runtime merge order observed in `opencode agent list` arrays (last-match-wins per docs):
built-in defaults (`*.env` read=**ask**, `doom_loop`=ask, `external_directory *`=ask) → root-config external_directory allows → skill-dir auto-allows (OpenCode auto-adds an external_directory allow per discovered skill dir — 27 distinct paths in dump) → agent frontmatter allows.

**Enforcement status**: merge layer fully verified [E1]; request-time ask/deny gating is documented vendor behavior — headless spot-check skipped (would burn inference against RECON posture; handed to @researcher Stage-4 as standing order, §6).

---

## §3 FINDINGS

### F-01 [HIGH] Dead plugin registration paths — silent failure mode
- **Evidence**: `opencode.json:7-8` registers `file://…/.opencode/plugin/error-capture.ts` + `awareness.ts`; directory `.opencode/plugin/` (singular) **does not exist** (`ls: cannot access`). Files actually live in `.opencode/plugins/` (plural). Probes E4: zero errors logged at DEBUG/print-logs/logfile; plugins still initialize because plural-dir auto-discovery loads them anyway.
- **Why it matters**: M23 Failure Integrity — the registration list lies, and the failure is invisible. Today's behavior is correct **by accident** (auto-discovery). Any refactor that "cleans up" plugins/, or a future OpenCode version that changes discovery semantics, silently drops awareness/error-capture/stall-sensor with no signal.
- **Acceptance criteria (bash-verifiable fix)**:
  ```bash
  # 1. Registration entries point at existing files:
  jq -r '.plugin[]' opencode.json | grep '^file://' | while read u; do test -f "${u#file://}" && echo "OK $u" || echo "DEAD $u"; done
  # Expect: zero DEAD lines.
  # 2. Plugins still load after fix:
  opencode agent list 2>&1 | grep -c 'Plugin initialized'   # expect >= 4
  ```

### F-02 [HIGH] Agent-level `instructions[]` key is not part of the v1.18.23 schema
- **Evidence**: AgentConfig schema (fetched from `$schema` URL, E6) has NO `instructions` property; docs prescribe `prompt: "{file:./path}"`. Yet 12 of 13 agent defs in `opencode.json:229-320` use `"instructions": [...]`.
- **Masking hazard**: harmless today ONLY because every referenced .md also exists in `.opencode/agents/` and the markdown loader picks it up. The two places masking breaks are F-03 (grok_cli) and the missing `plan.md` for makali (`opencode.json:233-235` references `.opencode/agents/plan.md` — absent; makali survives only because `makali.md` exists).
- **Acceptance criteria**:
  ```bash
  # No agent def uses the dead key:
  jq '.agent | to_entries[] | select(.value.instructions) | .key' opencode.json   # expect: empty (after migration to prompt/{file:})
  # Every referenced instruction file exists:
  jq -r '.agent[].instructions[]?' opencode.json | while read f; do test -f "$f" && echo OK || echo "MISSING $f"; done
  ```

### F-03 [MED] grok_cli double-registration; top-level shell has EMPTY prompt
- **Evidence**: `.opencode/agents/grok_cli.md` was moved to `.opencode/agents/archive/grok_cli.md`. Consequences observed in registry [E1]: (a) `grok_cli (all)` still registered from opencode.json JSON def — with its instructions file gone and the `instructions` key decorative, its prompt body is empty; (b) `archive/grok_cli (all)` ALSO registered — the archive subdir is scanned recursively, so the "archived" agent is fully live (frontmatter permissions + body). Task tool offers both.
- **Also**: `build.md` self-describes as DEPRECATED ("Build agent removed") yet remains `mode: all` with full tool allows and appears as invokable.
- **Acceptance criteria**:
  ```bash
  opencode agent list 2>&1 | grep -cE '^(grok_cli|archive/grok_cli) \('   # expect 1 after cleanup, currently 2
  ```

### F-04 [MED] scribe.md ships non-schema frontmatter to the LLM provider
- **Evidence**: scribe.md frontmatter carries `version`, `author`, `mandates: [M5, M11, M18, M22]`. Vendor docs (§Additional): unknown agent options "passed through directly to the provider as model options". Sandbox E2 proved unknown keys parse silently.
- **Risk**: param pollution on strict OpenAI-compatible endpoints (potential 4xx); silent garbage params on lenient ones. Also sets precedent that frontmatter is free-form when it is not.
- **Acceptance criteria**: `awk '/^---$/{c++} c==1' .opencode/agents/scribe.md | grep -cE '^(version|author|mandates):'` → expect 0 after moving these to body comment.

### F-05 [MED] `{session_model}` placeholder substitution does not exist at the OpenCode layer
- **Evidence**: literal `{session_model}` present in ALL 14 agent files (rg counts 1-3 each) and appears UNsubstituted in this session's own system prompt header [E7]. Engine-side `src/omega/ics.py:261,367` (`_read_opencode_session_model`) substitutes only in ENGINE-rendered artifacts; `scripts/correct_ics_provenance.py` exists to patch headers post-hoc — evidence the split-brain already caused provenance drift (FP-04 stamp found in MASTER_SYNTHESIS archive doc).
- **Status**: M22 already instructs agents to use the OpenCode-injected "You are powered by…" line instead — a workaround, not a fix. Options for Council 2: strip placeholders from agent files, or implement a plugin that substitutes at chat.params time.
- **Acceptance criteria**: `grep -rl '{session_model}' .opencode/agents/*.md | wc -l` → 0 (if stripped) OR a plugin exists whose code performs substitution (then: `rg -l 'session_model' .opencode/plugins/` non-empty).

### F-06 [MED] Permission posture is permissive-by-construction; `"/*": "allow"` neuters external-directory protection
- **Evidence**: `opencode.json:10-26` — every scoped path allow + final `"/*": "allow"` catch-all; every agent frontmatter allows all 11 tools. The only remaining friction defaults are built-ins: `read *.env = ask` and `doom_loop = ask` (observed in all 24 runtime permission arrays [E1]).
- **Assessment**: this is a deliberate fleet choice (autonomous overnight operation), not a bug — but it means the permission model provides **no meaningful guardrail** for RECON-style mandates like ours; discipline is enforced by prompt text only (S2/N5's surface), not mechanics. Record as risk-acceptance decision for Council 2 to make explicit.
- **Acceptance criteria (if hardening desired)**: replace `"/*": "allow"` with explicit prefixes; verify `jq -r '.permission.external_directory | keys[]' opencode.json | grep -c '^\*/\*$'` → 0.

### F-07 [LOW] Dual agent directories; protocol documents register as agents
- **Evidence**: `.opencode/agent/` (singular, undocumented location) holds CONVERSATIONAL_SUBAGENT_PROTOCOL.md, NODE_ONBOARDING_PROTOCOL.md, STALLED_SUBAGENT_RECOVERY.md, autonomous_meditation.md — all four appear as selectable/invokeable agents in the Task-tool namespace (visible in this session's available-agents list) alongside the documented `.opencode/agents/` (plural). Both dirs scanned by v1.18.23.
- **Impact**: namespace pollution; an orchestrator model can "task()" a protocol document as if it were an executor (their descriptions even say "should only be called manually"). Recursion-guard noise.
- **Acceptance criteria**: `opencode agent list 2>&1 | grep -cE '^CONVERSATIONAL_SUBAGENT_PROTOCOL|^NODE_ONBOARDING'` → 0 after relocating protocol docs out of agent scan paths.

### F-08 [LOW] Config-layer opacity: three config files, undocumented nested location
- **Evidence**: root `opencode.json`, nested `.opencode/opencode.json` (antigravity providers + plugin entry — proven LOADED by E3 A/B test), global `~/.config/opencode/opencode.json` (15 providers, `plugin: []`, `lsp: true`). Merge precedence between nested vs root untested (both applied in probe; conflict case unresolved).
- **Impact**: N1/S7 relevance — config-instruction consistency audits must check all three layers or miss live settings (e.g., antigravity models live ONLY in the nested file).

### F-09 [INFO] Verified-LIVE inventory (positive findings, for Council 2 baseline)
- `steps` budgets real (schema-typed; deprecation of `maxSteps` noted — fleet already migrated).
- `subagent_depth: 2` enables the arm→node topology; default 1 would forbid node-dispatched subtasks.
- Markdown-loader > JSON-inline precedence for duplicate agent definitions (description evidence, E7).
- Model inheritance: subagent ← invoking primary (docs + E5 DB distribution). No fleet agent pins a model → the "Arms inherit session model" hazard note in plan §8 is mechanically accurate.
- Plugin reality: 4 active (sovereign-compaction[global singular dir], awareness, error-capture, silent-stall-sensor[project plural dir]) vs 2 npm entries registered; both singular `plugin/` and plural `plugins/` auto-discover.
- Built-in secret friction exists: `read *.env = ask` default in every agent — the one mechanical teeth in an otherwise allow-all posture.

### F-10 [INFO] Security bright-line sweep (M8) — NEGATIVE (clean)
- No stale secrets in audited surfaces: EXA key referenced via `${EXA_API_KEY}` env interpolation (opencode.json:54), local LM Studio keys are `sk-local*` dummies. Global `antigravity-accounts.json` exists but was NOT opened (out of S3 scope; flagged for N1/S7 follow-up). No active external telemetry found in plugins (all local file/DB writes); remote MCP endpoints (exa, parallel-search) are user-configured tools, not covert telemetry.

---

## §4 REVIEW QUESTIONS → ANSWERS (plan §2 S3 mapping)

| Question | Answer |
|----------|--------|
| Does frontmatter behave as documented? | Yes for description/mode/permission/steps/temperature/model (each verified or schema+doc grounded, §2.1). NO for anything outside the schema — those pass through to the provider (F-04) or do nothing. |
| Which fields are LIVE vs decorative? | Matrix in §2.1/§2.2. Headline decorations: agent-level `instructions[]`, `{session_model}`, scribe metadata fields. |
| How do instructions-from-files get injected? | Four mechanisms, §2.3: md-body loading (workhorse), top-level instructions[] ("Instructions from:" sections), plugin session.prompt injections (dynamic), and NOTHING for agent-level instructions[]. |
| Model inheritance verified? | Yes — subagents inherit invoking primary's model; primaries take global/session selection; empirically confirmed via per-agent model variance in sessions DB (E5). |
| Permission model enforced? | Merge layer: proven (E1). Request-time enforcement: documented, spot-check deferred to researcher specialist (RECON constraint). Posture: allow-all by design; only *.env-read=ask + doom_loop=ask have mechanical teeth (F-06). |

---

## §5 HANDOFF PACKET (Delivered-Home Doctrine §6.5)

### Warm-start reading list (ordered)
1. `opencode.json` (root) — agent defs, plugin registrations, permission block, instructions[]
2. `https://opencode.ai/config.json` — AgentConfig schema; diff any agent key against it before trusting it
3. `https://opencode.ai/docs/agents/` — options semantics; §Max-steps, §Model (inheritance rules), §Permissions
4. `/tmp/opencode/n6/agent_list.txt` — full runtime permission-array dump (regenerate: `opencode agent list`)
5. `.opencode/plugins/*.ts` + `~/.config/opencode/plugin/sovereign-compaction.ts` — the four live plugins
6. `src/omega/ics.py:261,367` — engine-side session-model substitution (parallel to, not part of, OpenCode injection)

### Standing orders for future councils / pagees
- **Never trust an agent-config key just because the fleet uses it.** Diff against the $schema first; this fleet carries two generations of dead keys (agent-level `instructions[]`, deprecated `maxSteps` ancestors).
- **Registration lists lie silently.** Verify plugin/agent wiring with `opencode agent list` banners, not config text (M23: silent failure is the enemy).
- **To test frontmatter mechanics without touching prod**: replicate the `/tmp/opencode/n6/sandbox/` pattern (temp dir + minimal opencode.json + .opencode/agents/test.md → `opencode agent list [--log-level DEBUG --print-logs]`).
- **Open items deliberately left for @researcher (Stage 4, S3 deep-dive)**:
  1. Request-time permission enforcement spot-check (headless `opencode run` with a deny-rule agent; needs one cheap inference — out of RECON budget here).
  2. Nested-vs-root config merge PRECEDENCE on conflicting keys.
  3. Whether agent-level `instructions[]` has any legacy code path in the binary despite schema omission (strings-audit of the bun binary, or GitHub source of anomalyco/opencode v1.18.23).
  4. Whether AGENTS.md rules auto-discovery contributed sections to this session's prompt (could not introspect own full prompt reliably).
- **Do NOT use `hivemind_extended_checkin`** (broken, per mission packet) — heartbeat cadence instead.

---

## §6 REGISTRATION & COORDINATION LEDGER
- TASK_REGISTRY: `express-c1-node6-20260825` registered 2026-08-25T13:07:02Z, tags `["expert","pageable","domain:cognition","express:first-light"]`
- Hivemind presence posted (ses_ad2bbd37284f) at fieldwork start; heartbeats sent ~10 min cadence; entity tag `node6` throughout
- Awareness checked at start (council: kali/makali_fusion/maat/lilith/node1 visible) — re-check at end performed
- Recursion guard honored: zero task() launches except the mandated Consultant report page (§C.9)
- Production mutations: NONE (writes confined to `data/council/20260825-094633-first-light/phase1_nodes/` + `/tmp/opencode/n6/`)

*source_node: N6 · tier: S3-technical-mechanics · raw report written to disk BEFORE digestion per §C.5*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

