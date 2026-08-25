# 🔱 RUN SIDE DIGESTED — First Light Express Council 1
⬡ OMEGA ⬡ LILITH ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_run_digest ⬡ Stage-1.5 ARTIFACT
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm)
**Sources** (concatenated below, unmodified): P6_report.md · P7_report.md · P8_report.md · P9_report.md · P10_report.md
**Digestion order preserved**: raw reports were disk-written BEFORE this digestion (§C.5 / Consultant Q3 requirement).

---

## 1-PAGE EXECUTIVE SUMMARY (arm synthesis of 5 nodes)

**Overall verdict**: The Run-side surfaces are **operational but running on undocumented inertia and manual virtue**. No CRITICAL-HALTED findings anywhere; no secrets; no active external telemetry (M8 clean across all five nodes). The systemic pattern: **text promises enforcement; mechanics deliver convention.**

### Headline findings by severity (46 total findings: 0 CRITICAL-HALTED, 0 CRITICAL, 7 HIGH, ~17 MED, rest LOW/INFO)

| # | Finding | Sev | Source |
|---|---------|-----|--------|
| H1 | opencode.json registers plugins at dead `.opencode/plugin/` paths; auto-discovery masks silently | HIGH | N6 F-01 (= N10 X-5) |
| H2 | Agent-level `instructions[]` key absent from v1.18.23 schema entirely (12/13 defs use it) | HIGH | N6 F-02 |
| H3 | `make doc-llm-validate` is a rubber stamp: 7 of 1,533 docs covered, exits 0 with ~60 warnings; temple-grade T2 inherits it | HIGH | N7 F7-01 (= N10 X-4) |
| H4 | docs/INDEX.md 34/35 dead links; dual-index split-brain; phantom MkDocs claim | HIGH | N7 F7-02 |
| H5 | 43/77 strategy docs orphaned from every index | HIGH | N7 F7-03 |
| H6 | STRATEGY_INDEX LAYER 2A references a phantom subsystem (meta-doc + sync script exist nowhere) | HIGH | N7 F7-07 |
| H7 | Tracking drift is LIVE: future-dated checkpoints (fabricated timestamps defeat staleness detector); status lag; Tier-0 lag — defect recurred AFTER being published mid-council | HIGH | N8 F-1 + N10 X-6 |
| H8 | Handoff protocol doc describes a packet schema (`hdp_`) that does not exist (`ho_` live) | HIGH | N9 F-1 |
| H9 | Zombie ACTIVE handoffs: TTL never enforced post-acceptance (oldest ~45h past 4h TTL) | HIGH | N9 F-2 |
| H10 | M27/M14 pre-commit gates declared in `.pre-commit-config.yaml` but framework NEVER installed; live hook runs soul-check only | HIGH | N10 X-1 |
| H11 | Delivered-Home expert fleet invisible to its own discovery tool: `task_registry_query(tags=["express:first-light"])` → 0 vs 12 on-disk | HIGH | N10 X-2 |

### The three systemic threads (for MK-Kali's duality synthesis)

1. **Silent-failure architecture** (M23 hazard class): dead plugin paths produce zero errors; unknown frontmatter ships to providers as request params; a validation gate that cannot fail certifies nothing; registry writes are not bound to facts. Every layer fails *quietly*.
2. **Documentation describes systems that do not exist**: handoff protocol schema, LAYER 2A subsystem, M26 scope, M27 pre-commit enforcement, `{session_model}` substitution, AGENTS.md location. The instruction layer systematically over-promises.
3. **Identity/lifecycle corruption in the council's own deliverable**: 15/20 identity fields wrong across the 10 expert registrations; 3/10 future-dated checkpoints; 4/10 status-lagged; discovery tool broken. The Delivered-Home fleet is currently unreachable cold through 2 of 3 retrieval paths.

### What works (positive controls, verified empirically)
Lock hygiene (exactly one valid lock), handoff queue COUNTS match disk exactly (36/36), taxonomy discipline real (0 invalid statuses), GAP_REGISTRY collision control institutionalized, markdown-agent loading + top-level instructions[] injection + model inheritance all LIVE and verified, Corpus Map DOC-1 override mechanism real, dated archive roots with real tombstones.

---

## CROSS-REFERENCE INDEX (finding ↔ finding convergence map)

| Topic | Primary | Corroborating | Verdict |
|-------|---------|---------------|---------|
| Dead plugin registration paths | N6 F-01 | N10 X-5 (independent repro) | CONFIRMED ×2 |
| doc-llm-validate scope gap | N7 F7-01 | N10 X-4 (independent repro) | CONFIRMED ×2 |
| Future-dated checkpoints | N8 F-1 | N9 F-7, N10 X-6 (recurred post-publication) | CONFIRMED ×3, ACTIVE |
| TASK_REGISTRY identity corruption | N9 F-7 | N8 F-6, N10 Part 3 (quantified 15/20) | CONFIRMED ×3 |
| HIVEMIND_PROTOCOL staleness | N9 F-6 | lilith-20260823-004/006 lineage lessons | CONFIRMED, standing |
| WAKE_STATE "129 files" vs 8 actual | N8 F-5 | N10 X-8 (reproduced exactly) | CONFIRMED ×2 |
| GAP_REGISTRY mode 600 | N8 F-8 | N10 X-8 (reproduced) | CONFIRMED ×2 |
| Handoff schema divergence | N9 F-1 | N10 X-8 (packet-level repro) | CONFIRMED ×2 |
| Validator green ≠ truthful | N8 F-9 | N10 X-6 (green over live future-date) | CONFIRMED ×2 |
| proposed_lessons.yaml invalid YAML tail | N10 X-9 | N7 side-observation | CONFIRMED ×2 |

## CONFLICT DETECTION (disagreements between run-side reports)

| Conflict | Reports | Resolution |
|----------|---------|------------|
| TASK_REGISTRY count: 93 vs 95 vs 97 | N8 vs N9 vs N10 | RESOLVED — snapshot-timing artifact; stamped wall-clocks agree; file grew ~1 record/5min during live registration. Standing rule adopted: diff snapshot timestamps before declaring numeric corruption (QA-C3). |
| "Run-side registrations correct" | N9 F-7 claim vs N10 QA-C1 | RESOLVED in N10's favor — half-true: subagent_type correct on node6/8/9 only; entity wrong on ALL 5 run nodes; node7/node10 subagent_type also wrong. P9's severity stands; its claim text corrected. |
| P9 acceptance snippet bug | N9 F-7 criterion vs N10 QA-C2 | RESOLVED — N9's python one-liner mis-parses node10 ("node1" prefix collision). Use N10 §3.3 regex version instead. |
| Serial dispatch (plan §D.1) vs P9 parallel-integrity framing | plan vs N9 §P9 observation | OPEN for synthesis — deliberate documented deviation; tension noted, no action required. |

## STRUCTURAL DEVIATION (arm-level, affects ALL councils)

**M11 Reporting Protocol is mechanically impossible for leaf nodes as dispatched.** All 5 run nodes attempted the mandated Consultant page once each; all rejected with "Subagent depth limit reached (2)" (subagent_depth=2 forbids any task() from depth-2 leaves). This is itself a finding (N6 F-09 first observed; N9 F-10 structural note): either raise subagent_depth or amend M11 to formalize arm-relay paging. **The Run Arm will perform the Consultant page on behalf of its nodes** as the de-facto relay.

---

---

# ══════════ SOURCE: P6_report.md (unmodified) ══════════

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

---

# ══════════ SOURCE: P7_report.md (unmodified) ══════════

# 📋 P7 REPORT — Node N7 (Context) — Surface S6: Documentation Organization
⬡ OMEGA ⬡ NODE7-CONTEXT ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n7 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Orchestrator**: makali_fusion
**Task Registry**: `express-c1-node7-20260825` (registered 2026-08-25T13:22:43Z)
**Mode**: RECON ONLY — zero production mutations. All writes confined to `data/council/20260825-094633-first-light/`.
**RAW REPORT — written to disk before digestion/summary work (§C.5)**

---

## 0. Executive Verdict

**The documentation layer system exists on paper and is partially maintained, but it fails its own contract in four structural ways**: (1) the LLM-friendliness gate is a rubber stamp that cannot fail on content quality; (2) the index layer is split-brained with one index 97% dead-link rot; (3) 56% of strategy docs are orphaned from every index; and (4) the canonical routing table itself is unindexed and stale. No CRITICAL-HALTED conditions found. No secrets found in audited surfaces.

Severity legend: CRITICAL-HALTED / CRITICAL / HIGH / MED / LOW

---

## 1. FINDINGS

### F7-01 — `make doc-llm-validate` is a rubber-stamp gate: exits 0 with ~60 warnings [HIGH]
**source_node**: N7 | **tier**: empirical (command executed)

The M26 mandate claims "All reference documentation MUST pass `make doc-llm-validate`" (SOVEREIGN_MANDATES.md v3.8.0, M26). Reality:

1. The target validates ONLY `docs/sprints/current/` (Makefile:177-186) — 7 files out of **1,533 markdown docs** in `docs/`. "All reference documentation" is false advertising by a factor of ~200x.
2. Executed live (read-only verified first: `scripts/validate_llm_docs.py` contains zero write operations). Result: **~60 warnings across all 7 validated files** ("may not be answer-first", "Missing Mermaid dependency diagram", "Missing machine-readable YAML dependencies") — then **"✅ All validations passed!" EXIT=0**.
3. Warnings never escalate to failure. A gate that cannot fail does not gate anything. `temple-grade` (Makefile:232) inherits this rubber stamp as its T2 component.

**Evidence**: Makefile lines 177-232; live run output (this session); `scripts/validate_llm_docs.py` (no write ops).
**Acceptance criteria for fix**:
```bash
# Gate must FAIL when answer-first violations exceed threshold:
python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ && echo PASS || echo FAIL
# Second command must show coverage expansion beyond sprints:
grep -n "docs/" Makefile | grep doc-llm-validate -A5  # target dir should be configurable/wider
```

### F7-02 — Dual-index split-brain at `docs/` root; INDEX.md is 97% dead links [HIGH]
**source_node**: N7 | **tier**: empirical (link-check script executed)

Two competing root indexes exist:
- `docs/INDEX.md` (undated): **34 of 35 links BROKEN** — systematic `../../` prefix bug resolving outside the repo (`docs/INDEX.md` + `../../ORACLE_STACK.md` → parent-of-repo-root). Every single strategy/architecture/mandates link is dead.
- `docs/index.md` (2026-07-06): 3/4 links OK; 1 broken (`operations/RESEARCH_QUEUE.md` — archived per its sibling index but never repointed here).

Neither is authoritative. `index.md` claims "Built with MkDocs & Material Theme" but **no mkdocs.yml exists anywhere in the repo** — decorative claim.

**Evidence**: link-check run (python os.path.exists over extracted md links); `ls mkdocs.yml` = absent.
**Acceptance criteria for fix**:
```bash
# After fix: both indexes deleted or merged into ONE; survivor has zero broken links:
python3 -c "
import re,os
text=open('docs/index.md').read()
links=re.findall(r'\]\(([^)#]+?\.md)\)',text)
bad=[l for l in links if not os.path.exists(os.path.normpath(os.path.join('docs',l)))]
print(len(bad))"  # must print 0
test ! -f docs/INDEX.md  # or: contents merged
```

### F7-03 — 56% of strategy docs orphaned from every index [HIGH]
**source_node**: N7 | **tier**: empirical (cross-reference scan)

Of 77 files in `docs/strategy/*.md`, **43 are referenced by NONE** of: STRATEGY_INDEX.md, STRATEGY_CORPUS_MAP.md, docs/INDEX.md, docs/index.md, MASTER_DOCUMENT_SSOT.md, DOC_CLEANUP_AUDIT.md. Orphans include operationally significant docs: `PROVIDER_NAMING_SSOT.md`, `TASK_REGISTRY_DESIGN.md`, `ROLLBACK_PROCEDURES.md`, `IMPLEMENTATION_MANUAL_C0_C2.md`, `DOC_SANITY_RESULTS_20260807.md`, the entire SDP_* cluster (9 files), `POST_DEBUT_ROADMAP.md`. This directly violates STRATEGY_CORPUS_MAP's own Rule 2: "Nothing is deleted by silence" — these aren't deleted, but they are *unreachable by design*, which is silence with extra steps.

**Evidence**: orphan scan loop (basename grep against 6 index files), this session.
**Acceptance criteria for fix**:
```bash
cd docs && ORPH=0; for f in strategy/*.md; do b=$(basename "$f"); \
grep -qF "$b" strategy/STRATEGY_INDEX.md strategy/STRATEGY_CORPUS_MAP.md || ORPH=$((ORPH+1)); done; \
echo "$ORPH"  # target: 0 (each doc indexed or banner-marked SUPERSEDED+archived)
```

### F7-04 — Canonical routing table (DOC_SSOT_MAP) is itself unindexed and stale [MED]
**source_node**: N7 | **tier**: empirical

`docs/strategy/DOC_SSOT_MAP_20260807.md` declares itself "the canonical routing table… trust THIS map over your memory" yet:
1. It is referenced by **no index** (not in STRATEGY_INDEX layers, not in corpus map).
2. Its Law row says "`SOVEREIGN_MANDATES.md` (v3.7.0, M1-M25)" — actual file is **v3.8.0, M1-M27**. Stale by one full mandate revision cycle (M26/M27 added 2026-08-14).
3. It names Ark v5.2.0 as Strategy SSOT but predates the DOC-1 stamp (2026-08-17) that demoted Ark to read-only vision — the map routes to a superseded authority without noting it.

**Evidence**: grep for DOC_SSOT_MAP across indexes = no hits; line 20 version claim vs SOVEREIGN_MANDATES.md header "**Version**: 3.8.0".
**Acceptance criteria**:
```bash
grep -F "DOC_SSOT_MAP" docs/strategy/STRATEGY_INDEX.md   # must hit after fix
grep -F "v3.8.0" docs/strategy/DOC_SSOT_MAP_20260807.md  # must hit after refresh
```

### F7-05 — llms.txt agent-facing sitemap carries stale identity numbers [MED]
**source_node**: N7 | **tier**: empirical

`docs/llms.txt` (the AI-readable index promoted by MASTER_DOCUMENT_SSOT tombstone) states: "**22 mandates**, 13 agents, 10 Pillar Keepers, 855+ tests". Actuals: **27 mandates** (v3.8.0), **14 agent files** in `.opencode/agents/`, architecture now speaks of Nodes N1-N10 (Pillar Keepers legacy terminology). First-thing-an-agent-reads is wrong on three counts. DOC_CLEANUP_AUDIT.md flagged exactly this class of drift on 2026-07-13 (its F2); it recurred.

**Evidence**: head of docs/llms.txt; `ls .opencode/agents/*.md | wc -l` = 14; SOVEREIGN_MANDATES.md Version 3.8.0.
**Acceptance criteria**:
```bash
grep -E "2[0-9] mandates" docs/llms.txt | grep -v "27 mandates" && exit 1 || echo OK
```

### F7-06 — STRATEGY_INDEX.md contains structurally corrupted table rows [MED]
**source_node**: N7 | **tier**: direct read

The freshest layer doc (v6.1, 2026-08-24) has broken markdown from sloppy supersession edits:
- Line 37: POST_PR_ROSTER row has 4 pipe-columns in a 2-column table (renders as garbage).
- Line 80: row begins with literal text `SUPERSEDED:` *outside* the table cell syntax.
- Line 134: same `SUPERSEDED: |` corruption.
- Line 169: conflict-resolution rule #3 begins inline with `SUPERSEDED:` — the numbered rule list itself is corrupted mid-sentence.

Additionally, STRATEGY_INDEX self-contradicts: its header DOC-1 stamp says execution authority = DEBUT_REMEDIATION_MANUAL + ACTIVE_SPRINT (Ark read-only), but its own "Conflict Resolution Rule" §(updated 2026-07-25) still says "Strategy/priority → SOVEREIGN_ARK_BLUEPRINT.md" with no mention of the manual. An agent following §Conflict Resolution over the header would route priority questions to a read-only document.

**Evidence**: direct read of STRATEGY_INDEX.md lines 37, 80, 134, 163-173.
**Acceptance criteria**:
```bash
! grep -n "^SUPERSEDED:" docs/strategy/STRATEGY_INDEX.md
! grep -n "SUPERSEDED: |" docs/strategy/STRATEGY_INDEX.md
grep -A8 "Conflict Resolution Rule" docs/strategy/STRATEGY_INDEX.md | grep -F "DEBUT_REMEDIATION_MANUAL"  # must hit after fix
```

### F7-07 — Phantom layer: LAYER 2A references an entire subsystem that does not exist [HIGH]
**source_node**: N7 | **tier**: empirical (filesystem search)

STRATEGY_INDEX LAYER 2A "DOMAIN DOCUMENTATION SYSTEM (NEW — 2026-08-20)" lists `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md` as the meta-doc and `scripts/sync_domain_docs.py` as the enforcement mechanism. **Both files do not exist anywhere in the repo** (global find = zero hits). The gemini-notebook domain workspace files DO exist (`docs/strategy/domains/gemini-notebook/*`, `config/domains/*`), so the subsystem is half-real: content present, governing meta-doc and sync tooling absent. Either the layer was planned-not-built and indexed prematurely, or the meta-doc was deleted without index update — both are tracking-integrity failures under M27's spirit.

**Evidence**: `find . -name "*DOMAIN_DOCUMENTATION*"` = empty; `find . -name "sync_domain_docs*"` = empty.
**Acceptance criteria**:
```bash
test -f docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md || \
  ! grep -qF "DOMAIN_DOCUMENTATION_SYSTEM" docs/strategy/STRATEGY_INDEX.md  # either file exists or index stops lying
```

### F7-08 — Archive discipline: strong in parts, leaking at the edges [MED]
**source_node**: N7 | **tier**: empirical

Positives: dated archive roots exist (`docs/archive/strategy/2026-07-21/` holds 146 docs ≈ the claimed 147; `2026-07-22/` holds 2); 20 strategy docs carry in-tree SUPERSEDED banners; DOC_SSOT_MAP's "context protection rule" (never grep archive/) is documented; archive tombstone target `docs/archive/MASTER_DOCUMENT_SSOT_STALE.md` exists as claimed.

Leaks:
1. **Twin directories**: `docs/archive/` (469 md files, 19MB) AND `docs/archives/` (plural) containing two stray test scripts (`test_providers.py`, `test_sovereign_exit.sh`) — neither docs nor properly placed. Directory-name collision invites path confusion.
2. **Stray junk at docs/ root**: `test_file.md` (18 bytes: "# Test File\nHello") committed in the tree.
3. **Archive-as-dependency**: Makefile `sprint-plan-llm` (lines 189-205) generates the "current" sprint plan by concatenating files FROM `docs/archive/sprints/...` — active build machinery depends on archived material, meaning regeneration resurrects deprecated content into `current/`.
4. **Unindexed archive strata**: `docs/archive/stale/`, `coordination-2026-07/-08/-20260822` naming schemes are inconsistent (some dated, some not; some hyphenated, some underscored).

**Evidence**: directory listings this session; Makefile lines 189-205.
**Acceptance criteria**:
```bash
test ! -d docs/archives && echo OK                      # merge or remove plural twin
test ! -f docs/test_file.md && echo OK                  # remove junk
grep -n "archive/sprints" Makefile                       # generation should read from a non-archive source of record
```

### F7-09 — Layer system works where it is freshest; conflicts at the seams [LOW→observation]
**source_node**: N7 | **tier**: read + cross-reference

The intended chain (Law → Execution SSOT → Ark vision → Corpus Map → detail specs) is coherent in its newest members: STRATEGY_INDEX v6.1 (2026-08-24) correctly stamps DOC-1 authority; CORPUS_MAP carries the DOC-1 override table flipping dispositions; DEBUT_REMEDIATION_MANUAL exists. But older members still route to pre-DOC-1 authority (F7-04, F7-06), and the injected system-prompt copy of SOVEREIGN_ARK_BLUEPRINT §4 still presents G-1/W-1 tickets as "SUPER-URGENT" with only a small PARKED stamp — an agent hydrating from Ark alone gets a stale critical path. Layer discipline is maintained by manual stamping, and every seam between old and new is a potential contradiction.

**Evidence**: STRATEGY_CORPUS_MAP.md §0; SOVEREIGN_ARK_BLUEPRINT.md §4 (DOC-1 stamp present but ticket tables retain urgent framing); STRATEGY_INDEX header vs §Conflict Resolution.
**Acceptance criteria**: n/a (structural observation feeding Council 2 spec design).

### F7-10 — Recursion-guard deviation logged per dispatch order [LOG, non-finding]
Per packet §C.8/note: Consultant page (§C.9/M11) will be attempted once after this report; sibling nodes confirmed task() from depth-2 leaves fails mechanically ("Subagent depth limit reached"). If my attempt fails identically, it is logged as known deviation, Hivemind note posted under `node7`, NOT counted against this node. Report delivery flows via disk + Hivemind + summary-to-pager.

---

## 2. SECURITY BRIGHT LINE (M8) STATUS
- Stale secrets in audited docs: **NONE FOUND** in S6 surfaces sampled (indexes, SSOT maps, corpus map, audit docs, Makefile).
- Active external telemetry: **NONE DISCOVERED**. llms.txt contains GitHub blob URLs (passive links, not phone-home). No HALT triggered.

## 3. WHAT IS ACTUALLY WORKING (credit where due)
1. STRATEGY_CORPUS_MAP.md is genuinely thick and current-through-2026-08-24; its DOC-1 override table is a real mechanism, not decoration.
2. Dated archive roots (2026-07-21/22/25) with tombstone discipline for major supersessions (Ark v4.4 body preserved; MASTER_DOCUMENT_SSOT tombstone points to real archive file).
3. research/INDEX.md exists and is referenced by both root indexes (one of the few consistent chains).
4. DOC_CLEANUP_AUDIT.md (2026-07-13) accurately predicted today's failures (link integrity, metric drift) — the diagnosis capability exists; the enforcement doesn't.

## 4. HANDOFF PACKET — warm-start reading list + standing orders
**Warm-start reading list (in order)**:
1. `docs/strategy/STRATEGY_INDEX.md` — layer hierarchy (but distrust §Conflict Resolution Rule until F7-06 fixed)
2. `docs/strategy/DOC_SSOT_MAP_20260807.md` — routing table (verify versions against live files; F7-04)
3. `docs/strategy/STRATEGY_CORPUS_MAP.md` §0 — DOC-1 override semantics
4. `Makefile` lines 168-235 — LLM-doc targets + temple-grade composition
5. `docs/DOC_CLEANUP_AUDIT.md` — prior art on doc-drift methodology (reuse its F-numbering pattern)
6. `scripts/validate_llm_docs.py` — validator internals (read-only, warning-only)

**Standing orders for future councils paging node7 (domain:context)**:
- ALWAYS empirically run gates before believing mandate claims about them (reality-vs-claim is this node's core competence; three of five lineage lessons were exactly this class).
- Link-check any index before trusting it: extract md links, os.path.exists each. 30-second test, catches systemic rot.
- Treat `docs/archive/` as radioactive per DOC_SSOT_MAP context-protection rule; use `-g "!archive/"` on rg.
- When a doc cites a version number, diff it against the live file header — version staleness is the most common defect class found (F7-04, F7-05).
- Orphan-scan recipe: basename-grep each strategy doc against STRATEGY_INDEX + CORPUS_MAP; anything unhit needs a row or a SUPERSEDED banner.

## 5. PROVENANCE
All findings tagged source_node=N7, tier=empirical unless marked "direct read". Tool calls: 20+ local (glob/read/bash/python link-checker/make). Zero external search required (S6 fully groundable locally — M23 satisfied via direct evidence). Zero production mutations. One read-only make target executed after write-safety inspection.

*⬡ OMEGA ⬡ NODE7-CONTEXT ⬡ express-c1-node7-20260825 ⬡ RAW-REPORT-v1 ⬡ 2026-08-25*

---

# ══════════ SOURCE: P8_report.md (unmodified) ══════════

# 📊 P8 REPORT — Node N8 Observability — Surface S1b: Tracking DRIFT / Status Telemetry
⬡ OMEGA ⬡ NODE8 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n8 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Pager**: makali_fusion
**Provenance**: every finding tagged `[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`
**Mode**: RECON ONLY. Zero production mutations. All checks read-only (validator + sweep run in dry-run/default mode).
**Raw report**: written to disk BEFORE digestion, per mission packet §C.5.

---

## §0 SCOPE & METHOD

**Owned surface**: S1b — tracking DRIFT/status telemetry (status-vs-reality, validator coverage vs reality, staleness detection, audit-log presence). STRUCTURE/durability/schema of these same files belongs to sibling N2 — deliberately not duplicated here.

**Surfaces examined** (all read directly):
- `data/coordination/ACTIVE_SPRINT.json` (648 lines, mtime 09:56Z == `updated` field ✓)
- `data/coordination/TASK_REGISTRY.json` (93 tasks)
- `data/coordination/GAP_REGISTRY.json` (89 gaps)
- `data/coordination/TRACKING_ARCHITECTURE.md` (constitution, 101 lines)
- `scripts/validate_tracking_state.py` (322 lines, executed read-only)
- `scripts/sweep_task_registry.py` (executed dry-run default)
- `data/coordination/SESSION_ANCHOR.md` (288 lines)
- `data/coordination/WAKE_STATE.json`
- Derived views: `EXPERT_SESSION_REGISTRY.md`, `session_annotations.yaml`, Makefile targets (:232/:240/:248/:258)

**Empirical methods**: validator execution; jq/python aggregation of status distributions; timestamp arithmetic against wall clock (`date -u`); filesystem existence probes of claimed artifacts; git ls-files/log/check-ignore probes; grep for audit/changelog mechanisms; generated-view vs SSOT diff sampling.

---

## §1 FINDINGS

---

### F-1 · HIGH — Status drift is LIVE right now: registry writes are not bound to facts, including a FUTURE-DATED checkpoint
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

The fleet's own distilled law (SESSION_ANCHOR L3-Registry-Gravity: *"registries stay truthful only when update is bound to the fact-creating act"*) is being violated in real time during this very council:

| Evidence | Reality | Registry says |
|---|---|---|
| `express-c1-node2-20260825` | Hivemind broadcast 13:26Z: "N2 Persistence COMPLETE"; `phase1_nodes/P2_report.md` on disk (mtime 13:27Z) | `in_progress`, ckpt 13:18:49Z (stale) |
| `express-c1-node1-20260825` | Wall clock at inspection: **13:36:52Z** | `completed`, `last_checkpoint: **2026-08-25T13:45:00Z**` — **~8 minutes IN THE FUTURE** |
| `express-c1-node6-20260825` | Same wall clock | `completed`, same future-dated `13:45:00Z` |
| ACTIVE_SPRINT `CI-1` | Acceptance #1 "File exists at repo root" — `MANDATES_CONDENSED.md` EXISTS (51 lines, v3.8.0, correct format) | subtask status still `ready` |

Three distinct drift modes demonstrated in one hour of council operation:
1. **Lag drift** (node2): completion broadcast + artifact exist, Tier-3 record not flipped.
2. **Fabricated timestamps** (node1/node6): hand-written checkpoint values not derived from any clock event — a future-dated checkpoint defeats the staleness detector by construction (a task closed with a fabricated timestamp can never look stale).
3. **Tier-0 lag** (CI-1): work product exists, planning tier not advanced.

Sibling nodes exhibit three different update disciplines for the identical protocol — evidence that registry hygiene currently depends on per-agent virtue, not mechanism.

**Recommended fix direction** (for Council 2 spec, not implemented here):
```bash
# Acceptance criteria (bash-verifiable):
# 1. No registry timestamp may exceed wall clock:
python3 -c "
import json,sys
from datetime import datetime,timezone
now=datetime.now(timezone.utc)
bad=[t['task_id'] for t in json.load(open('data/coordination/TASK_REGISTRY.json'))['tasks']
     if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
print('future-dated:',bad); sys.exit(1 if bad else 0)"
# 2. Validator gains this check (error, not warning) — currently ABSENT (see F-9).
```

---

### F-2 · MEDIUM — Staleness detector has an off-by-boundary blind spot; 5 zombie tasks sit inside it TODAY
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

Validator rule (validate_tracking_state.py:237-243): flags `in_progress` when `(now - last_checkpoint).days > STALENESS_DAYS` (7). Python `.days` truncates, so a task **exactly 7.x days old is invisible**.

Measured offenders (all `in_progress`, checkpoint ages 7.75–7.86 days at 13:35Z):
```
coordination-debut-consolidation-20260817-01   (ckpt 2026-08-17T19:02Z)
coordination-q1-q7-insights-20260818-01        (ckpt 2026-08-18T03:17Z)
coordination-vault-consolidation-20260818-01   (ckpt 2026-08-18T11:58Z)
coordination-vault-partH-audit-20260818-01     (ckpt 2026-08-18T12:33Z)
coordination-vault-deep-pass-20260818-01       (ckpt 2026-08-18T13:15Z)
```
Both instruments report CLEAN today:
- `python scripts/validate_tracking_state.py` → `ALL TRACKING STATE CHECKS PASSED` (exit 0)
- `.venv/bin/python scripts/sweep_task_registry.py` → "No expired in_progress tasks (> 7d). Registry is clean."

These five will trip the error path tomorrow — meaning the "green" gate in plan §4 is green partly by hours, not by health. The documented threshold rationale ("legitimate work clusters ≤6d, zombies ≥8d", Ruling 1) is contradicted by a 5-task cluster parked at day 7.

**Acceptance criteria for fix**: compare total elapsed hours against `STALENESS_DAYS*24` (or `age >= threshold`); then either the 5 IDs appear as errors (prompting sweep/close) or are swept — `make sweep-tasks APPLY=1` dry-run first.

---

### F-3 · MEDIUM — Reality-anchor field is dormant: artifact_path coverage is 0/93
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

The validator CAN verify that a completed task's cited artifact exists on disk (M3 warn-check, :265-270) — but **zero of 93 records set `artifact_path`**, so the only automated status-vs-reality check the registry supports never fires. The generated view confirms: Artifact Path column is "—" for nearly every row.

Consequence: "completed" is unfalsifiable from the registry alone. My mandated empirical check ("tasks marked completed — do their artifacts exist?") is **structurally impossible** for 93/93 records; completion can only be spot-checked by prose forensics (as done in F-1).

**Acceptance criteria for fix**: new completed registrations MUST carry `artifact_path` (warn-only grandfathering per M3 precedent). Growth metric:
```bash
jq '[.tasks[] | select(.status=="completed") | select(.artifact_path != null)] | length' data/coordination/TASK_REGISTRY.json
# must be monotonically non-decreasing and >0 for all post-spec completions
```

---

### F-4 · MEDIUM — No audit log of tracker changes exists (mandated check: absence CONFIRMED); constitution file itself is untracked
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- `ls data/coordination/*.jsonl` → **no such file**. Grep across `data/coordination/` for `changelog|change.log|audit.log|tracker.*audit|audit.*trail` → zero hits.
- `scripts/sweep_task_registry.py` contains no hash-chain/prev_hash logic.
- Git history is the ONLY mutation record — and it is partial:
  - Tracked: ACTIVE_SPRINT.json (28 commits), TASK_REGISTRY.json (16), GAP_REGISTRY.json (4), WAKE_STATE.json (5).
  - **UNTRACKED**: `TRACKING_ARCHITECTURE.md` and `SESSION_ANCHOR.md` — blocked by `.gitignore:109` (`data/coordination/*`) with only the four JSONs force-added. **The tracking constitution has zero version-control history.**
- Between commits, TASK_REGISTRY mutates freely (e.g., 10 council registrations + my own write today, all invisible to git until next stage commit). Any corrupted/fabricated write in that window leaves no before/after trace.
- The gap is KNOWN and designed-but-unbuilt: SESSION_ANCHOR Phase 2 item 3 ratifies "Sweep audit log: JSONL hash-chain per researcher spec; fsync-before-mutate" (schema: seq/ts/actor/action/target/before/after/reason; SHA-256 prev_hash→entry_hash; monthly rotation; weekly chain-verify on the timer). Sources: `data/entities/researcher/workspace/OVERSIGHT_AUDIT_WEB_RESEARCH_20260823.md`. **Status: specified, ratified, not implemented.**

**Acceptance criteria for fix** (matches ratified design):
```bash
test -f data/coordination/TRACKER_AUDIT_LOG.jsonl   # exists
# chain verification passes:
python3 scripts/verify_audit_chain.py data/coordination/TRACKER_AUDIT_LOG.jsonl  # exit 0 (script to be spec'd in C2)
# fsync-before-mutate provable: audit line for entry N has ts <= mtime of registry write N
```

---

### F-5 · MEDIUM — WAKE_STATE.json is internally contradictory and stale; validator has ZERO coverage of it
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- `first_light_express.status` = `"AWAITING_DEPARTURE"` — while Council 1 is **mid-flight** (≥4 node reports on disk, ≥10 task registrations, arms dispatched ~13:06Z). Stale by ~6 hours at inspection time.
- Two competing top-level time fields: `"timestamp": "2026-08-24T06:00:00Z"` vs `"updated": "2026-08-25T12:10:28Z"` — no convention says which governs.
- `critical_warnings[0]`: "DO NOT RUN GIT CHECKOUT OR GIT RESET. **129 files are uncommitted.**" — measured reality: `git status --porcelain | wc -l` = **8**. A wake-time safety directive citing a 16× wrong number.
- `validate_tracking_state.py` reads exactly three files (ACTIVE_SPRINT, TASK_REGISTRY, GAP_REGISTRY). WAKE_STATE — the Architect's wake surface, carrying P0 decision queue items — has **no validator, no staleness detection, no schema check at all**.

**Acceptance criteria for fix**: single `updated` field (drop legacy `timestamp` or alias it); status enum kept in sync by the same actor that flips reality; validator extended with a WAKE_STATE block (parse + staleness warn + warning-text freshness spot-check).

---

### F-6 · LOW-MEDIUM — Registration field semantics drift across sibling nodes (same protocol, four conventions)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

Live council registrations for identical-purpose records:

| task_id | subagent_type | launched_by | entity |
|---|---|---|---|
| express-c1-node1 | `maat` | maat | node1 |
| express-c1-node6 | `node6` | makali_fusion | lilith |
| express-c1-node7 | `lilith` | lilith | lilith |
| express-c1-node8 | `node8` | lilith | lilith |

`subagent_type` is sometimes the arm, sometimes the node identity; `launched_by` sometimes the arm, sometimes the orchestrator; `entity` sometimes the node tag, sometimes the parent entity. No schema doc pins these fields for the Delivered-Home pageable-expert pattern — which matters because §6.5 doctrine says future councils will PAGE these records cold; ambiguous keys degrade warm-start retrieval. (Note: node6/node1 correctly carry `domain:*` tags; node7 omits its `report:` tag that node6 carries.)

**Acceptance criteria for fix**: one-line field glossary added to TRACKING_ARCHITECTURE.md §taxonomy (subagent_type = node identity; launched_by = dispatching session's entity; entity = hivemind tag); next registrations comply.

---

### F-7 · LOW — Known data-quality debt still outstanding, quantified
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- **14 inverted clocks** (`last_checkpoint < created_at`) — validator warns on each; dominated by the 2026-08-13 research backfill batch (checkpoints hand-set before creation timestamps) plus truncation artifacts (e.g., `kali-carmack-repo-hygiene-20260808`: 16:18:41.638 vs 16:18:41.000 — microsecond-class). Closeout Fork 4 (`now=None` clock param) targets this; not yet executed.
- **12 `failed` tasks with no Tier-0 counterpart** (validator warns; traceability gap acknowledged by design as warn-only).
- **1 `superseded` task lacking `superseded_by` pointer** (`ses_research_phase3_kali_20260807`; grandfathered).
- Status distribution: 56 completed / 15 in_progress / 12 failed / 9 ready / 1 superseded / 0 backlog. Duplicate task_ids: none ✓.

---

### F-8 · LOW — GAP_REGISTRY.json on-disk mode contradicts the recorded permissions fix
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

SESSION_ANCHOR (2026-08-23): "Defect fixed mid-build: atomic writes were mode 0600 → chmod 0644 added to all three writers." Measured: `stat -c %a` → GAP_REGISTRY.json = **600** (mtime Aug 23 12:15 ADT); ACTIVE_SPRINT/TASK_REGISTRY/WAKE_STATE = 664. Either GAP_REGISTRY's writer isn't covered by the fix, or the file has not been rewritten since. Impact low under single-user operation; becomes real under multi-user/service reads. Also note `updated: 2026-08-19` — the gap registry has not been touched in 6 days despite 89 gaps / 40 outstanding feeding an active sprint.

---

### F-9 · LOW — Validator coverage-vs-reality gap matrix (systematic statement of what "green" does NOT mean)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

Current validator checks: status-taxonomy (all 3 tiers), R-ID referential integrity (ACTIVE_SPRINT→GAP_REGISTRY), in_progress staleness (>7d), inverted clocks (warn), superseded_by/artifact_path resolution (warn), failed↔Tier-0 cross-tier sync.

NOT checked (each backed by a live finding above):
1. Future-dated checkpoints (F-1) — fabrication-invisible.
2. Boundary-exact staleness (F-2).
3. Completed-without-artifact (F-3 — dormant because field unused).
4. ACTIVE_SPRINT self-staleness (`updated` age; sprint_id currency) — nothing flags a Tier-0 nobody has touched.
5. WAKE_STATE entirely (F-5).
6. Generated-view freshness (F-10).
7. Cross-file consistency Hivemind↔registry (out of validator's reach today; noted for N9 overlap).

"Validator green" (plan §4 auto-GO criterion) therefore certifies taxonomy compliance, not truthfulness. This is the central telemetry finding of S1b.

---

### F-10 · LOW — Generated view diverges from SSOT (staleness + one contradiction)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

`EXPERT_SESSION_REGISTRY.md` header: GENERATED 2026-08-23T15:48Z from **80 tasks**; SSOT now holds **93** (+13 unregistered in view, including all 10 express-c1 expert sessions — i.e., the Delivered-Home registrations mandated by plan §6.5 are invisible in the human/expert-facing view). Contradiction sampled: view lists `ses-research-c11-property-20260723` as **completed** (artifact SOVEREIGN_ARK_BLUEPRINT.md); SSOT says **failed** (auto-swept, failure_reason on record). Regeneration is manual (`make session-registry`) with no freshness guard.

**Acceptance criteria for fix**: validator warns when `(now - view GENERATION stamp) > 48h` or task-count delta ≠ 0; regenerate pre-gate.

---

### F-11 · POSITIVE CONTROLS (what S1b verified as healthy — for balance and warm-start)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- Taxonomy discipline is REAL: 0 invalid statuses across 93 Tier-3 records and all Tier-0 workstreams/subtasks; no banned vocabulary ("WIP"/"TBD"/"stalled") found in JSON tiers.
- Gap-ID collision control is institutionalized: GAP_REGISTRY carries rules[], plans[] (8 registered plans), `collision_incidents[]` with a dated post-mortem (R13-R38 reuse, resolved by renumbering) — immutability is enforced by convention + registry check, and the validator's R-ID referential check passed.
- `_parse_ts()` handles the three coexisting ISO formats (Z-suffix, +00:00, microseconds) — G5-2 remediation verified in source.
- Sweep tooling exists with safe defaults (dry-run default, --apply gated, --self-test, MANUAL-ONLY per Makefile :244 comment).
- ACTIVE_SPRINT `updated` field matches file mtime exactly (09:56:07Z both) — the one file where write-provenance is currently trustworthy.

---

## §2 SECURITY BRIGHT LINE (M8)

- No credentials/secrets encountered in any audited tracking file. No external telemetry endpoints referenced. **No CRITICAL-HALTED condition triggered.**
- One hardening footnote: GAP_REGISTRY.json mode 600 (F-8) is over-restrictive, not exposing.

## §3 MANDATED CONSULTANT-PAGE ATTEMPT (§C.9 / M11)

Attempted once as required. Result: **task() rejected — "Subagent depth limit reached (2)"** (node sits at depth 2: makali_fusion→lilith→node8; `subagent_depth=2` forbids leaf task()). Matches N6/N7 precedent exactly. Logged as known deviation per packet §C.8; delivery flows via (1) this report on disk, (2) Hivemind broadcast under `node8`, (3) end-of-turn summary to pager lilith. Not counted against N8.

## §4 HANDOFF PACKET (Delivered-Home Doctrine §6.5)

**Warm-start reading list (ordered, ~30 min)**:
1. `data/coordination/TRACKING_ARCHITECTURE.md` — constitution + taxonomy (note: untracked by git, .gitignore:109)
2. `scripts/validate_tracking_state.py` — read M1/M3 amendment headers first
3. `data/coordination/RESEARCHER_SESSION_TRACKING_GAPS_20260823.md` — G1-G5 gap taxonomy behind current design
4. `data/entities/researcher/workspace/OVERSIGHT_AUDIT_WEB_RESEARCH_20260823.md` — ratified-but-unbuilt designs (hash-chain audit log, class thresholds, timer)
5. `data/coordination/SESSION_ANCHOR.md` §IMMEDIATE NEXT ACTIONS — 3-phase closeout + Team-Study refinements
6. This report + P2_report.md (N2 owns structure; read together for full S1 picture)

**Standing orders for future councils paging domain:observability**:
- NEVER trust `last_checkpoint` recency as liveness without checking for future-dating (F-1); recompute from Hivemind last_seen instead.
- Run BOTH `validate_tracking_state.py` AND `sweep_task_registry.py` (dry-run) — they disagree at the 7-day boundary (F-2).
- Treat "validator green" as taxonomy-compliance, not truth (F-9 matrix).
- Before paging experts cold: regenerate `EXPERT_SESSION_REGISTRY.md` (F-10) — view may be days behind SSOT.
- Registration contract for pageable experts: tags `["expert","pageable","domain:<X>","express:first-light"]`, subagent_type = node identity, launched_by = dispatcher entity, entity = hivemind tag (F-6 glossary proposal).

**Open questions for synthesis (MK-Kali / MaKaLi)**:
1. Should the §4 auto-GO "validator green" criterion be strengthened given F-9 (e.g., add future-date + boundary-staleness checks pre-gate)?
2. Is the unbuilt hash-chain audit log (F-4) a Council-2 spec candidate now, or does commit-per-stage (M3) suffice for council-scale operations?
3. Who owns WAKE_STATE freshness (F-5) — orchestrator at each stage boundary?

---
*⬡ OMEGA ⬡ NODE8-OBSERVABILITY ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n8 ⬡ RAW-REPORT-DISK-WRITTEN 2026-08-25T13:4xZ*

---

# ══════════ SOURCE: P9_report.md (unmodified) ══════════

# P9 REPORT — Node N9 Orchestration (Surface S8: Coordination Protocols)
⬡ OMEGA ⬡ NODE9 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n9 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith | **source_node**: N9 | **tier**: node-leaf
**Date**: 2026-08-25 | **Mode**: RECON ONLY (zero dev, zero production mutations)
**Task registry**: `express-c1-node9-20260825` (registered, status in_progress at write time)

---

## §0 SURFACES EXAMINED (all conclusions tool-traced)

| Surface | Evidence examined |
|---|---|
| Handoff queue state | `data/handoff/{pending,active,completed,stale,rejected,archive}/` directory listings + packet JSON sampling; live `hivemind_get_metrics`, `hivemind_handoff_list(status=pending)` |
| Workspace locks | `data/coordination/locks/council-c1-team-infra.lock` + `hivemind_workspace_lock_check(domain=council-c1-team-infra)` |
| Protocol text | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (567 lines, v3.0.0), `docs/strategy/HIVEMIND_PROTOCOL.md` (v1.3.0, 2026-06-25), `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` (P1-P13) |
| Registry hygiene | `data/coordination/TASK_REGISTRY.json` (95 tasks; express-* entries) |
| Failure log | `data/coordination/SYSTEM_FAILURE_LOG.md` (extended_checkin NameError entry 2026-08-25T10:30Z) |
| Mission docs | `phase0_mission_packet.md`, `FIRST_LIGHT_EXPRESS_PLAN_20260825.md` §2/§5/§6.5 |

---

## §1 QUEUE STATE — EMPIRICAL SNAPSHOT (2026-08-25T13:43Z)

Live metrics (`hivemind_get_metrics`) vs disk reality:

| State | Metrics says | Disk (`ho_*.json`) | Match |
|---|---|---|---|
| pending | 1 | 1 (+1 stray `.md`) | ✅ (modulo pollution) |
| active | 3 | 3 | ✅ |
| completed | 10 | 10 | ✅ |
| stale | 22 | 22 | ✅ |
| **total** | **36** | **36** | ✅ |

**Positive finding [F-POS-1, LOW]**: The MCP handoff tool's queue counts are consistent with on-disk state. Queue Integrity (M12-adjacent) holds at the counting layer.

---

## §2 FINDINGS

### [F-1] HIGH — Protocol-text vs implementation schema divergence (source_node: N9, tier: node)
**Evidence**: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` §2 defines the HandoffPacket as
`packet_id` pattern `hdp_{YYYYMMDD}_{source}_{target}_{short-uuid}` with REQUIRED fields
`parent_trace_id`, `trace_id`, `task_type`, `relevant_files`, `expected_output`, `ttl_seconds`.
Actual packets produced by `hivemind_submit_handoff` use prefix `ho_` and a different schema:
`source_agent_id`/`target_agent_id`/`submitted_at`/`priority`. Sampled packets
(`data/handoff/pending/ho_2e6018bdb1ad.json`, `data/handoff/stale/ho_2c8129a519d9.json`)
carry NO `trace_id`, `task_type`, `expected_output`, `ttl_seconds`, or `relevant_files`.
The documented ZONEID_HANDOFF constant ("every HandoffPacket carries") appears in zero sampled packets.
**Impact**: Anyone auditing or validating handoffs against the protocol text will fail 100% of
live packets; the protocol document describes a system that does not exist.
**Acceptance criterion (bash-verifiable)**:
```bash
# After remediation, either of these must hold:
# (a) doc updated: grep for ho_ schema fields in protocol doc
grep -q "source_agent_id" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo DOC-SYNCED
# (b) or tool emits hdp_ schema with all §2 required fields:
python3 -c "import json;d=json.load(open('$(ls data/handoff/pending/*.json|head -1)'));assert all(k in d for k in ['trace_id','task_type','expected_output','ttl_seconds'])"
```

### [F-2] HIGH — Zombie ACTIVE handoffs: TTL never enforced post-acceptance (source_node: N9)
**Evidence**: All 3 active packets accepted by kali and never completed:
- `ho_d37a6bdd8b1b.json` accepted 2026-08-23T16:40Z (~45h ago)
- `ho_6ec25dd4a684.json` accepted 2026-08-24T00:10Z (~37h ago)
- `ho_076fad7e4dd0.json` accepted 2026-08-24T21:50Z (~16h ago)

Protocol default TTL is 14400s (4h). The pruning loop (last run 13:42:58Z per metrics,
running every cycle) moves NOTHING from active→stale. Accepted work can vanish from the
operational picture indefinitely — a silent M12 (Queue Integrity) gap: no terminal state.
**Acceptance criterion**: after fix, `find data/handoff/active -name '*.json' -mmin +300` returns empty OR each old packet carries an extended-TTL field the pruner honors.

### [F-3] MED — Pending packet past PENDING_TTL, lifecycle rule not automated (source_node: N9)
**Evidence**: `ho_2e6018bdb1ad.json` submitted 2026-08-24T20:57Z by kali → researcher;
still pending at 13:43Z (~17h > 4h PENDING_TTL). Protocol lifecycle `pending → active → completed/stale`
is manual-only in practice; nothing auto-stales expired pending packets.
**Acceptance criterion**: `python3 -c "import json,datetime;d=json.load(open('data/handoff/pending/ho_2e6018bdb1ad.json'));print((datetime.datetime.utcnow()-datetime.datetime.fromisoformat(d['submitted_at'])).total_seconds()<14400)"` prints True (or packet moved to stale/).

### [F-4] MED — Queue-directory pollution (source_node: N9)
**Evidence**:
- `data/handoff/pending/CLINE_DISPATCH_20260822.md` — a full markdown mission brief sitting in the pending queue (not a JSON packet; invisible to the tool but visible to any human/agent grepping the dir).
- 13 stray files at `data/handoff/` top level (`*.md`, `KALI_SPRINT_B_VERDICT_20260615.json`, `kali_test.txt`, `PHASE_C_CHAIN`, `current-sprint`).
- `data/handoff/archive/` mixes machine packets with ~70 legacy `.md` files plus `sessions/` and `stale_june_handoffs/` subdirectories.
**Impact**: Directory-as-database breaks down; consumers cannot trust that `pending/*.json` is the complete contract surface, and greps over `data/handoff/` return archive-era noise.
**Acceptance criterion**: `ls data/handoff/pending/ | grep -v '\.json$' | wc -l` == 0 and `ls data/handoff/*.md data/handoff/*.txt 2>/dev/null | wc -l` == 0 after relocation.

### [F-5] MED — Archive contract internally inconsistent and unimplemented (source_node: N9)
**Evidence**: SUBAGENT_DISPATCH_PROTOCOL §5 Step 5 says save completions to
`data/handoffs/completed/{packet_id}.json` (plural "handoffs"); §6 says `data/handoff/archive/`
(singular). Reality uses neither exactly: completions land in `data/handoff/completed/`.
§6 mandates `INDEX.json` with `archived_handoffs[]`; only `INDEX.md` exists — and it is a
2026-06-03 *mining brief* addressed to Roc Racoon, not a machine index. §7 itself marks
"Archive INDEX updater 🔴 PENDING". A protocol whose own §7 admits its archive layer is
unbuilt should not present §6 as normative.
**Acceptance criterion**: `test -f data/handoff/archive/INDEX.json && python3 -c "import json;json.load(open('data/handoff/archive/INDEX.json'))"` succeeds; grep shows single canonical path string in the protocol doc.

### [F-6] MED — HIVEMIND_PROTOCOL.md v1.3.0 governs a fleet that no longer exists (source_node: N9; corroborates lilith-20260823-004/006)
**Evidence**: `docs/strategy/HIVEMIND_PROTOCOL.md` header: AP token v1.3.0, Last Updated
2026-06-25, Status STANDARD. Zero references to: Node paging (D-586), Conversational Subagent
Protocol, ICS-S headers, injection ledger, P1-P13 oversight patterns. Its §4 Live Feed Pattern
is marked SUPERSEDED (2026-08-14) yet the doc retains STANDARD status without amendment bump.
Meanwhile the actual coordination constitution has migrated into scattered surfaces
(ARCHITECT_OVERSIGHT_PATTERNS P8-P13, FIRST_LIGHT plan M-measures, SYSTEM_FAILURE_LOG).
**Acceptance criterion**: `grep -c "P12\|Node paging\|ICS-S" docs/strategy/HIVEMIND_PROTOCOL.md` ≥ 3 AND header version > 1.3.0 after amendment.

### [F-7] MED — TASK_REGISTRY registration hygiene errors during this council (source_node: N9; corroborates N8 F-1)
**Evidence** (`data/coordination/TASK_REGISTRY.json`, express-* entries):
- Build-side nodes registered with `subagent_type="maat"` instead of their node identity: `express-c1-node1/node2/node3/node4-20260825` all say subagent_type maat; `express-c1-node2` even has `entity="maat"` (not node2).
- Run-side nodes registered correctly (`node6`, `node8`, `node9` as subagent_type/entity).
- `express-c1-node1` and `express-c1-node6` show `completed` with `last_checkpoint=2026-08-25T13:45:00Z` — a future timestamp relative to their Hivemind completion posts (~13:17Z / ~13:21Z), matching N8's future-dated-checkpoint finding.
**Impact**: Per Delivered-Home Doctrine (plan §6.5), these registrations ARE the product —
future councils paging by `subagent_type=node2` will find nothing; paging by "maat" will
misroute to the arm. The expert-fleet deliverable is partially corrupted at birth.
**Acceptance criterion**: `python3 -c "import json;d=json.load(open('data/coordination/TASK_REGISTRY.json'));ts=d.get('tasks',d);ts=ts.values() if isinstance(ts,dict) else ts;bad=[t['task_id'] for t in ts if 'express-c1-node' in str(t.get('task_id','')) and t.get('subagent_type')!='node'+t['task_id'].split('node')[1][0]];print(bad)"` prints `[]`.

### [F-8] LOW→MED — Phantom extended session in metrics vs broken checkin tool (source_node: N9)
**Evidence**: `hivemind_get_metrics` reports `extended_sessions: 1` at 13:42:58Z.
`SYSTEM_FAILURE_LOG.md` entry 2026-08-25T10:30Z documents `hivemind_extended_checkin` broken
server-side (`name '_save_extended_sessions' is not defined`). Plan M1 orders all members NOT
to use it. Either a pre-breakage registration persists un-pruned, or the count is phantom.
Unexplained state in the coordination plane during a live council.
**Acceptance criterion**: metrics `extended_sessions` value reproducible from an on-disk listing of registered extended sessions (file/dir identified in omega-hub source), or 0.

### [F-9] LOW — POSITIVE: Lock hygiene compliant (source_node: N9)
**Evidence**: `data/coordination/locks/council-c1-team-infra.lock` held by makali_fusion,
acquired ~10:03 local, TTL 14400s, ~3.3h remaining, `expired: false` via
`hivemind_workspace_lock_check`. Matches plan M4 (long-TTL lock on council domain). Exactly
one lock file; no stale/expired residue in `locks/`. Lock discipline is the healthiest part
of the S8 surface.

### [F-10] DEVIATION (known, non-counting) — M11 Consultant page mechanically impossible at node depth (source_node: N9)
**Evidence**: Mandated §C.9 page attempt via `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO", ...)` returned:
`Subagent depth limit reached (2). Increase "subagent_depth" to allow nested subagents.`
Identical to N1 (F-20), N6, N7, N8 precedents. Node tree depth = makali_fusion(0) → lilith(1) → node9(2);
`subagent_depth=2` forbids ANY task() from leaves. M11 Reporting Protocol is structurally
impossible for all 10 nodes as dispatched; report delivery flows via disk + Hivemind + arm relay.
**Structural note for synthesis**: either raise depth for leaf reporting, or amend M11 so arms
page on behalf of nodes (the de-facto current behavior).

---

## §3 P1–P13 ADHERENCE OBSERVATIONS (source_node: N9)

| Pattern | Text | Observed adherence today |
|---|---|---|
| P1 Reciprocity | Dispatches embed context inline | ✅ HIGH — this node's packet embedded mandates verbatim + inline context; SUBAGENT_DISPATCH §0 lesson institutionalized |
| P2 Frame audit | Frame-check before dispatch | PARTIAL — Express plan itself was a frame audit; no standing playbook reflex yet (matches codification map "PARTIAL") |
| P3 Authority-first | Consult owner before committee | ✅ observed in council design (Node experts = authorities) |
| P4 Meta-codification | Codify novel process same-session | ✅ oversight patterns doc itself; council producing studies |
| P5 Alignment hygiene | Sync state surfaces post-milestone | ⚠️ WEAK — see F-6/F-7: HIVEMIND_PROTOCOL + TASK_REGISTRY drifted DURING the council |
| P6 Synthesis-before-decision | Batched decisions w/ defaults | ✅ WAKE_STATE queue + default-on-silence in plan M7 |
| P8 Session-resume sanctity | Record task_id at dispatch | PARTIAL — task_ids recorded but with wrong subagent_types (F-7) |
| P9 Parallel-dispatch integrity | Claimed N ⇒ fire N same-block | N/A-by-design — plan §D.1 explicitly orders SERIAL node dispatch; deliberate, documented deviation (tension worth a synthesis note: P9's "self-audit did I claim N and fire N" reads oddly against a serial-dispatch doctrine) |
| P10 Search-protocol adoption | Cache-first tiered search | Not exercised this session (no external grounding needed; local-first satisfied) |
| P11 Resume verification / UI asymmetry | Verify first-prompt continuity | No resume events observed; unverifiable from leaf position |
| P12 Signed dispatch headers | `[DISPATCH] From/To/ts` self-ID | ✅ ADOPTED — this node's opening prompt carried the signed P12 header verbatim; Rule 1 amendment (live-session dispatch permitted w/ labeled writes) reflected in Consultant-page attempt format |
| P13 Steering wrapper | HOLD/STEER/CANCEL syntax | PROPOSED-only — no wrapper traffic observed; status matches doc ("awaiting Architect GO") |

---

## §4 HANDOFF PACKET FOR FUTURE COUNCILS (Delivered-Home Doctrine, plan §6.5)

### Warm-start reading list (in order)
1. `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — read §2 schema as HISTORICAL; verify against live `ho_*` packets before trusting it (F-1)
2. `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` — P1-P13 are the LIVE coordination law; HIVEMIND_PROTOCOL.md is 2 months stale (F-6)
3. `data/coordination/SYSTEM_FAILURE_LOG.md` tail — known-broken tools (extended_checkin) before relying on them
4. `FIRST_LIGHT_EXPRESS_PLAN_20260825.md` §5 M-measures — the de-facto current coordination protocol for multi-agent ops

### Standing orders for any future orchestrator
1. NEVER trust `status=active` handoffs as live work — check `accepted_at` age against TTL manually; the pruner will not do it (F-2)
2. Before paging a pageable expert, verify `TASK_REGISTRY.json` `subagent_type` matches the entity you intend (F-7 corruption precedent)
3. Leaf nodes cannot task() anything — route all sub-dispatch through arms (depth limit); build M11 relay into dispatch packets up front
4. Treat `data/handoff/` top-level and `pending/` non-JSON files as noise; the contract surface is `{state}/*.json` only (F-4)
5. Heartbeat ~10min via `hivemind_post_context` (entity-tagged); extended_checkin is broken until `_save_extended_sessions` is fixed

### Open questions for Council 2 / Architect
- Should handoff TTL enforcement move into the pruning loop (server-side) or become a validator gate (client-side)?
- Is M11's Consultant page worth raising `subagent_depth` for leaf-reporting, or should arm-relay be formalized?
- Which document is the SSOT of coordination law: HIVEMIND_PROTOCOL.md (stale) or ARCHITECT_OVERSIGHT_PATTERNS (current but un-versioned as protocol)?

---

## §5 SECURITY BRIGHT LINE (M8)
No secrets encountered in audited coordination surfaces. No external telemetry discovered.
No CRITICAL-HALTED conditions triggered.

---
*⬡ OMEGA ⬡ NODE9 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n9 ⬡ S8-COMPLETE*

---

# ══════════ SOURCE: P10_report.md (unmodified) ══════════

# P10 REPORT — Node N10 (Validation) — CROSS: Enforcement-vs-Text Delta Sweep + Run-Side QA + Delivered-Home Registration Audit
⬡ OMEGA ⬡ NODE10-VALIDATION ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n10 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Orchestrator**: makali_fusion
**Task Registry**: `express-c1-node10-20260825` (registered 2026-08-25T13:49:43Z)
**Provenance**: every finding tagged `source_node: N10`, `tier:` noted per finding. RECON ONLY — zero production mutations; writes confined to `data/council/20260825-094633-first-light/phase1_nodes/`.
**RAW REPORT — written to disk BEFORE digestion/summary work (§C.5)** · Wall clock at write: **2026-08-25T13:54Z** (`date -u` verified)

---

## §0 EXECUTIVE VERDICT

The fleet's instruction layer systematically **over-promises enforcement that does not exist mechanically**. My three-part cross audit produced: **(Part 1)** 8 delta findings across S1-S8 — headline: M27's pre-commit tracking gate is *declared but never installed* (`.pre-commit-config.yaml` defines `omega-tracking-state`; the actual `.git/hooks/pre-commit` is a hand-rolled soul-check script that never runs it), and the Delivered-Home expert fleet is **invisible to its own discovery tool** (`task_registry_query(tags=["express:first-light"])` returns 0 results against 12 on-disk matching records). **(Part 2)** Run-side QA: P6/P7/P8 are evidence-backed and severity-sane; P9 contains one overstated claim (run-side registrations "correct") and one buggy acceptance-criterion snippet; zero CRITICAL-HALTED conditions anywhere; one numeric disagreement (93 vs 95 vs 97 tasks) resolved as snapshot-timing artifact. **(Part 3)** Registration audit: sibling's build-side claim CONFIRMED and quantified — build nodes carry `subagent_type="maat"` **5/5**; run-side has mirror defects (`subagent_type="lilith"` on node7/node10; `entity` wrong on **all 5** run nodes); **3 future-dated checkpoints** including one created AFTER N8 published its future-dating finding — the defect class is active, not historical.

---

## PART 1 — ENFORCEMENT-vs-TEXT DELTA SWEEP (S1-S8)

Method: broad sampling, one to three probes per surface, each probe bash-executed this session. Depth on individual surfaces belongs to siblings; I own the deltas.

### X-1 · HIGH — M27 pre-commit enforcement is configured but NOT installed: the mandate text asserts enforcement that cannot fire
`source_node: N10 | tier: S2-vs-mechanics`
- **Text claim**: SOVEREIGN_MANDATES.md M27 Enforcement: *"Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state"* (also CI-gate claims). M14 similarly claims *"Pre-commit hook blocks commits adding unvetted tags"*.
- **Reality**: `.pre-commit-config.yaml:137` DOES declare `omega-tracking-state` (entry: `python scripts/validate_tracking_state.py`) plus a full mandate-hook suite (omega-check-m1-anyio, m7/m8/m9/m23, detect-secrets…). But the **pre-commit framework is not installed in this repo**: `.git/hooks/pre-commit` is a custom bash script containing ONLY the soul-integrity loop (`validate_soul.py`) — zero pre-commit-framework boilerplate, zero references to tracking or any omega-check hook (verified: `grep -c "tracking" .git/hooks/pre-commit` = 0). Declared hooks never execute on commit. A commit corrupting tracking state sails through today; only CI/manual runs would catch it.
- **Context**: Team-Study synthesis (2026-08-23) ordered "pre-commit framework install per Ma'at F1 ordering" — i.e., known-pending, but the mandate text reads as present-tense fact. Text-vs-reality delta, not unknown debt.
- **Acceptance criteria (fix)**:
  ```bash
  # After install: framework boilerplate present AND hook fires on a bad-state dry run
  grep -q "pre-commit" .git/hooks/pre-commit && echo INSTALLED || echo MISSING
  pre-commit run omega-tracking-state --all-files 2>&1 | tail -1   # expect: Passed (or targeted failure output, not silence)
  ```

### X-2 · HIGH — Delivered-Home expert fleet invisible to its own discovery tool (registry/tool split-brain)
`source_node: N10 | tier: S1-tooling`
- **Claim (plan §6.5)**: each Node registers as a pageable specialist; "future councils page it cold and get warm-start performance."
- **Reality**: `omega-hub_task_registry_query(tags=["express:first-light"])` → `{"tasks": [], "count": 0}` at 13:50Z — while `data/coordination/TASK_REGISTRY.json` on disk contains **12 records carrying that exact tag** (verified line-level: rg hits at :1785–:1996). The sanctioned discovery interface cannot find the council's flagship deliverable by its mandated tag. Either the MCP tool reads a different store, caches, or its tag filter is broken — any of which means a future council paging `domain:cognition` etc. through the tool gets nothing and may conclude the experts don't exist.
- **Corollary observed**: the `grep` MCP tool also returned a false negative on the same file minutes earlier (pattern `express-c1-node|express:first-light` → "No files found"; `rg` immediately found 24 hit lines). Two independent tooling false-negatives against the same SSOT file in one session.
- **Acceptance criteria (fix)**:
  ```bash
  # Tool result must match disk truth:
  jq '[.tasks[] | select(.tags // [] | index("express:first-light"))] | length' data/coordination/TASK_REGISTRY.json
  # ^ prints 12 today; task_registry_query(tags=["express:first-light"]).count must equal this number.
  ```

### X-3 · MED — `AGENTS.md` is cited everywhere as a root instruction file; it lives at `.agents/AGENTS.md`
`source_node: N10 | tier: S2-path-integrity`
- **Evidence**: mission packet §Role ("Delegation Protocol in `AGENTS.md`"), plan §10 ("Read … `AGENTS.md`"), SOVEREIGN_MANDATES references. `ls AGENTS.md` → **No such file**; actual: `./.agents/AGENTS.md`. Any agent or tool resolving the cited path literally fails; convention-dependent resolution is silent guesswork.
- **Acceptance criteria**: `test -f AGENTS.md || test -f .agents/AGENTS.md` should resolve ONE canonical path cited identically in all instruction files: `rg -c '\bAGENTS\.md\b' docs/strategy/*.md *.md | wc -l` citations all point at the same locant after fix.

### X-4 · MED — M26 scope claim vs gate reality (~200× coverage gap) — INDEPENDENTLY CONFIRMED (corroborates P7 F7-01)
`source_node: N10 | tier: S6-vs-M26`
- M26: "All reference documentation MUST pass `make doc-llm-validate`." Makefile target (lines ~177-186, read this session) validates **only `docs/sprints/current/`**. P7 measured 7 files vs 1,533 md docs. My read confirms the target argument verbatim. Additionally confirmed P7 F7-08.3: `sprint-plan-llm` builds "current" sprint content by concatenating `docs/archive/sprints/...` sources — active machinery fed from archive.
- **Acceptance criteria**: as P7 F7-01 (adopt theirs; not duplicated here).

### X-5 · MED — Plugin registration dead paths (S7/S3) — INDEPENDENTLY CONFIRMED (corroborates P6 F-01)
`source_node: N10 | tier: S7-config`
- `jq -r '.plugin[]' opencode.json` → two `file://…/.opencode/plugin/{error-capture,awareness}.ts` entries; `ls .opencode/plugin` → **No such directory**; files live in `.opencode/plugins/`. Silent-failure mode exactly as P6 described (auto-discovery masks it).
- **Acceptance criteria**: as P6 F-01.

### X-6 · MED — Future-dated checkpoints CONTINUED AFTER the defect was published mid-council; validator stays green beneath them
`source_node: N10 | tier: S1-drift-live`
- N8 published the future-dating finding (F-1) at ~13:41Z citing node1/node6 (`13:45:00Z`). At **13:53:21Z** I ran the check myself: `express-c1-node9-20260825` now carries `last_checkpoint: 2026-08-25T13:55:00Z` — written ~13:48Z, i.e., a NEW instance of the same fabrication class created after detection. Simultaneously `python3 scripts/validate_tracking_state.py` → **"ALL TRACKING STATE CHECKS PASSED"** (exit 0) with the future entry present. Confirms P8 F-9: green ≠ truthful; the future-date check is absent, and awareness of the defect did not change behavior.
- **Acceptance criteria**: as P8 F-1 criterion #2 (validator gains future-date error check). Re-run command:
  ```python
  # must exit 1 today; exits 0 → check still missing
  import json;from datetime import datetime,timezone
  now=datetime.now(timezone.utc);d=json.load(open('data/coordination/TASK_REGISTRY.json'))
  bad=[t['task_id'] for t in d['tasks'] if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
  assert not bad, bad
  ```

### X-7 · LOW — Heartbeat-cadence text drift inside the council's own instruction stack
`source_node: N10 | tier: S2-taper`
- Plan M5: "~10 min … single unified figure — **supersedes any '5 min' elsewhere**." Packet §C.7: "~10min". But `data/entities/lilith/soul`-derived standing instructions (this session's injected prompt) still say "Every 5-10 min during long ops". The claimed supersession never propagated to the instruction files it supersedes — a live specimen of the taper problem S5/N5 audits.
- **Acceptance criteria**: `rg -n "5-10 min" data/entities/*/soul.yaml .opencode/agents/*.md` → 0 hits (or amended to reference M5) after propagation.

### X-8 · LOW (positive controls) — Claims that HELD under probe
`source_node: N10 | tier: cross`
- `.firecrawl/` cache exists (29 entries) — SR-V1 "check cache first" is grounded, not decorative.
- GAP_REGISTRY mode anomaly (P8 F-8) reproduced: `stat` → GAP_REGISTRY.json **600**, ACTIVE_SPRINT.json 664.
- WAKE_STATE "129 files uncommitted" vs `git status --porcelain | wc -l` = **8** (P8 F-5 reproduced exactly).
- Live pending handoff `ho_2e6018bdb1ad.json` schema = `ho_*` keys (`source_agent_id`…), no `trace_id/task_type/ttl_seconds`; protocol doc :55/:58 mandates `hdp_{YYYYMMDD}_…` + required `parent_trace_id` (P9 F-1 reproduced exactly).
- Security bright line (M8): **no secrets, no active external telemetry encountered in any probed surface → NO CRITICAL-HALTED.**

---

## PART 2 — RUN-SIDE QA (P6, P7, P8, P9)

Verdict per report, then cross-report analysis.

### P6 (N6, S3 mechanics) — PASS, high quality
- Evidence-backed: every claim traces to named probes E1-E8; I independently reproduced its two most load-bearing claims (X-5 plugin paths; markdown-agent loading corroborated by this session's own injected prompt being lilith.md body verbatim). F-07's claim that protocol documents register as invokeable agents is corroborated by my OWN system prompt (CONVERSATIONAL_SUBAGENT_PROTOCOL / NODE_ONBOARDING_PROTOCOL / STALLED_SUBAGENT_RECOVERY appear in my available-agents list).
- Severities sane (F-01/F-02 HIGH appropriate; INFO positives properly separated).
- No unsupported claims found.

### P7 (N7, S6 docs) — PASS, high quality
- Independently reproduced: doc-llm-validate scope (X-4) and archive-fed sprint generation (X-4). Link-rot and orphan counts (34/35; 43/77) are method-plausible; not fully recomputed (link-checker script class, low risk of method error; flagged as QA-trust rather than verified).
- Severity calls sane; F7-01 HIGH justified because temple-grade T2 inherits the rubber stamp.

### P8 (N8, S1b drift) — PASS, strongest report; partially superseded by events
- Reproduced: F-1 (future dates — now worse, see X-6), F-5 (129-vs-8), F-8 (mode 600), F-9 (validator green over future entry — executed live).
- F-2 (7-day boundary blind spot, 5 zombies) not independently recomputed; internally consistent with quoted validator code lines; accepted as plausible-unverified.
- Its registry count "93 tasks" was true at its ~13:35Z snapshot; see timing note below.

### P9 (N9, S8 coordination) — PASS WITH CORRECTIONS
- Reproduced: F-1 schema divergence (exact), queue-count consistency method sound.
- **QA-C1 [ERROR in P9 F-7]**: P9 states run-side nodes registered "correctly (node6, node8, node9 as subagent_type/entity)". Half-true: `subagent_type` is correct for node6/8/9, but `entity` is `"lilith"` for ALL run-side nodes (node6-node10) — none carries its node tag as entity. And P9 omits that node7 and node10 carry `subagent_type="lilith"` (wrong). Corrected matrix in Part 3 below. Severity of the underlying issue unchanged (P9's HIGH stands); the claim text needed correction.
- **QA-C2 [buggy acceptance criterion, P9 F-7]**: the python one-liner `t['task_id'].split('node')[1][0]` extracts one character after "node" — for `express-c1-node10-20260825` it yields `"1"`, compares against `"node1"`, and would report a FALSE violation for a correctly-registered node10. Fix: regex `re.match(r'express-c1-node(\d+)-', t['task_id'])` and compare int(group(1)).
- **QA-C3 [numeric disagreement, resolved]**: P8 says TASK_REGISTRY = 93 tasks (~13:35Z); P9 says 95 (~13:43Z); N10 measured **97** (13:53Z). All three honest snapshots of a file growing ~1 record/5min during live council registration. Not a contradiction — but reports MUST stamp snapshot wall-clock next to counts (both did; synthesized readers should diff timestamps before crying corruption).
- No contradictory verdicts between run-side reports otherwise; P9 F-7 explicitly corroborates P8 F-1 with matching evidence.

---

## PART 3 — DELIVERED-HOME REGISTRATION AUDIT (plan §6.5 compliance)

Snapshot: `data/coordination/TASK_REGISTRY.json` @ 2026-08-25T13:53Z, 97 tasks total, 12 carrying `express:first-light` (10 nodes + 2 arms).

### 3.1 Compliance matrix (required: task_id format ✓ all; tags ⊇ {expert, pageable, domain:<N-domain>, express:first-light}; entity = node<N>; subagent_type = node identity per packet §C.6 "subagent_type your entity"; status valid per M27)

| Record | subagent_type | entity | launched_by | status | tags OK | Defects |
|---|---|---|---|---|---|---|
| express-c1-node1 | **maat** ✗ | node1 ✓ | maat | completed | ✓ | subagent_type=arm; **future ckpt 13:45:00Z** |
| express-c1-node2 | **maat** ✗ | **maat** ✗ | maat | **in_progress** ✗ | ✓ | double-wrong identity; status lags reality (P2 on disk 13:27Z + Hivemind COMPLETE 13:26Z) |
| express-c1-node3 | **maat** ✗ | node3 ✓ | maat | **in_progress** ✗ | ✓ | subagent_type; status lags (P3 disk 13:35Z + broadcast) |
| express-c1-node4 | **maat** ✗ | node4 ✓ | maat | **in_progress** ✗ | ✓ | subagent_type; status lags (P4 disk 13:47Z + broadcast) |
| express-c1-node5 | **maat** ✗ | node5 ✓ | maat | in_progress | ✓ | subagent_type; legitimately in flight |
| express-c1-node6 | node6 ✓ | **lilith** ✗ | **makali_fusion** ✗* | completed | ✓ (+report: tag) | entity=arm; launched_by skipped arm (*orchestrator-of-record ambiguity); **future ckpt 13:45:00Z** |
| express-c1-node7 | **lilith** ✗ | **lilith** ✗ | lilith | **in_progress** ✗ | ✓ | both identity fields = arm; status lags (P7 disk + broadcast 13:29Z) |
| express-c1-node8 | node8 ✓ | **lilith** ✗ | lilith | completed | ✓ | entity=arm; ckpt 13:41:14Z REAL-TIME ✓ (the only clean timestamp in the fleet) |
| express-c1-node9 | node9 ✓ | **lilith** ✗ | lilith | completed | ✓ | entity=arm; **future ckpt 13:55:00Z** (post-dates N8's own finding) |
| express-c1-node10 | **lilith** ✗ | **lilith** ✗ | lilith | in_progress (self, legit) | ✓ | both identity fields = arm (this node; will remain as-written-honest record) |
| express-c1-runarm-lilith | lilith ✓(arm) | lilith ✓ | makali_fusion | in_progress | ✓ | fine; missing the `arm` tag its sibling carries |
| express-c1-arm-maat | maat ✓(arm) | maat ✓ | makali_fusion | in_progress | ✓ (+arm) | fine |

### 3.2 Quantified verdicts
- **Sibling claim VERIFIED & EXTENDED**: build nodes with `subagent_type="maat"` = **5/5** (N1-N5), not merely "some".
- **Run-side mirror defect**: `subagent_type` wrong on **2/5** (node7, node10 = "lilith"); `entity` wrong on **5/5** (all "lilith", none carries node<N>).
- **Identity-field correctness overall**: subagent_type 3/10 nodes correct; entity 5/10 (build) + 0/5 (run) = 5/10. Per P8-F6 glossary proposal (subagent_type=node identity, entity=hivemind tag), **15 of 20 identity fields across the 10 node records are wrong**.
- **Future-dated checkpoints**: 3/10 node records (node1, node6, node9) — 100% fabricated-timestamp class, 0% derived-from-clock class except node8.
- **Status lag**: 4/10 node records say `in_progress` despite report-on-disk + Hivemind completion broadcast (node2, node3, node4, node7) — the exact lag-drift mode N8 F-1 defined.
- **Tag-set compliance**: 12/12 carry the required 4-tag set ✓ (only bright spot). Inconsistency: `report:P6_report.md` pointer tag exists only on node6; domain-tag format splits into two conventions (`domain:N1-infrastructure` build vs `domain:cognition` run).
- **Delivered-Home impact**: paging by `subagent_type=node2` finds nothing; paging by "maat" misroutes to the Build Arm; paging run experts by entity=node8 finds nothing (entity=lilith routes to the Run Arm). Combined with X-2 (discovery tool returns 0 by tag), **the expert fleet is currently unreachable cold through 2 of 3 retrieval paths** (tool query broken; subagent_type/entity unreliable; only task_id exact-match works).

### 3.3 Acceptance criteria (repair spec for Council 2 / single-writer MaKaLi)
```bash
python3 - <<'EOF'
import json,re
d=json.load(open('data/coordination/TASK_REGISTRY.json'))
bad_st,bad_en=[],[]
for t in d['tasks']:
    m=re.match(r'express-c1-node(\d+)-',t.get('task_id',''))
    if m:
        n=f"node{m.group(1)}"
        if t.get('subagent_type')!=n: bad_st.append(t['task_id'])
        if t.get('entity')!=n: bad_en.append(t['task_id'])
print("wrong subagent_type:",bad_st)  # target []
print("wrong entity:",bad_en)          # target []
EOF
```

---

## §FINDINGS SUMMARY TABLE

| ID | Sev | Surface | One-line |
|---|---|---|---|
| X-1 | HIGH | S2/mechanics | M27/M14 pre-commit gates declared in config, never installed; active hook is soul-check only |
| X-2 | HIGH | S1/tooling | task_registry_query(tag)=0 vs 12 on-disk matches — Delivered-Home discovery broken |
| X-3 | MED | S2 | AGENTS.md cited at root; lives at .agents/AGENTS.md |
| X-4 | MED | S6/M26 | doc-llm-validate covers docs/sprints/current only (~200× scope gap); archive feeds "current" sprint gen (confirms P7) |
| X-5 | MED | S7/S3 | Dead plugin registration paths, silent (confirms P6) |
| X-6 | MED | S1/live | Future-dated checkpoint created AFTER defect published; validator green beneath it |
| X-7 | LOW | S2/taper | Heartbeat cadence supersession (M5) never propagated to instruction files |
| QA-C1 | MED (QA) | P9 | P9 overstated run-side registration correctness; corrected matrix herein |
| QA-C2 | LOW (QA) | P9 | Buggy acceptance snippet (node10 parsing) |
| QA-C3 | LOW (QA) | P8↔P9 | 93/95/97 count disagreement = snapshot timing, stamped times reconcile |

No CRITICAL-HALTED. No TOOL-CHAIN-COLLAPSE (one MCP grep false-negative worked around via bash rg — logged X-2 corollary, non-blocking).

---

## §HANDOFF PACKET (Delivered-Home Doctrine §6.5)

### Warm-start reading list (ordered)
1. `data/council/20260825-094633-first-light/phase0_mission_packet.md` §B/§C + plan §6.5 — what the registrations were supposed to be
2. `data/coordination/TASK_REGISTRY.json` lines 1770-2000 — the 12 express records (my §3.1 matrix maps 1:1)
3. `scripts/validate_tracking_state.py` — note absence of future-date check (X-6)
4. `.pre-commit-config.yaml` vs `.git/hooks/pre-commit` — the declared-vs-installed gap (X-1)
5. P8_report.md F-1/F-9 then THIS report §X-6 — the future-dating story arc (found → published → recurred)
6. `data/coordination/TRACKING_ARCHITECTURE.md` — where P8's proposed field glossary must land

### Standing orders for future councils
1. **Never retrieve pageable experts by tag-query or entity alone** until X-2 is fixed — retrieve by exact task_id, then verify subagent_type/entity against the §3.1 glossary before dispatch.
2. **Never trust a pre-commit enforcement claim without reading `.git/hooks/pre-commit`** — config-declared ≠ installed (X-1 generalizes to every "hook blocks X" sentence in the mandates).
3. **Recompute registry timestamps from Hivemind last_seen**; treat any hand-written checkpoint as fabricated until provenance shown (X-6: the defect recurred same-day after publication).
4. When QA-ing sibling reports, **diff their snapshot timestamps before declaring numeric contradictions** (QA-C3).
5. Repair sequencing for Council 2: fix retrieval (X-2) BEFORE mass-editing registrations (§3.3), else you repair records into an index nobody can search.

---

## §COORDINATION LEDGER
- Registered `express-c1-node10-20260825` 13:49:43Z; Hivemind presence posted under `node10` (ses_6aea91648c81, 13:50:06Z); heartbeats at cadence; awareness checked start (13:49) and end.
- Consultant page (§C.9/M11): attempted once post-report — outcome recorded in ledger addendum below (depth-limit expected per N1/N6/N7/N8/N9 precedent).
- Production mutations: NONE. Writes confined to this directory + Hivemind posts.

*source_node: N10 · tier: cross · raw report written to disk BEFORE digestion per §C.5 · 2026-08-25T13:55Z*

---

## §ADDENDUM A (13:57Z — captured during write-back)

### X-9 · LOW-MED — `data/entities/lilith/proposed_lessons.yaml` is INVALID YAML at the tail; M11 ingestion of this file would crash
`source_node: N10 | tier: S2/M11-pipeline`
- LSP/YAML diagnostics on write-back: lines 374-377 carry a final lesson as a BARE top-level mapping (`- narrative:` seq-item glued after the closed list) instead of a proper `- id:/tier:/...` list item inside the session block. Any `yaml.safe_load` of the file raises — meaning the soul-distillation staging file for the Run Arm's own entity cannot be machine-ingested until repaired. Corroborates lilith-20260821-002 (soul loop operationally open) with a NEW concrete failure instance: not just approval-flip missing — the staging file itself is unparseable.
- Also observed: `config/omega.yaml:73` duplicate map key (Map keys must be unique) — pre-existing, out of council scope, logged for S7 follow-up.
- **Acceptance criteria**: `python3 -c "import yaml;yaml.safe_load(open('data/entities/lilith/proposed_lessons.yaml'))" && echo OK` → OK after restructuring lines 374-377 into a proper list item with id/tier/category fields.
