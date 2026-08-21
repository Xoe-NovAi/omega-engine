# Acceptance Criteria — Mapped to ACTIVE_SPRINT.json CI-1..CI-5

**Authority**: `data/coordination/ACTIVE_SPRINT.json` → workstream `CONTEXT-INJECTION` → subtasks CI-1..CI-5  
**Status**: All subtasks `status: "ready"` — awaiting execution  
**Completion**: All criteria must pass for Phase 1 `status: "completed"`  

> **⚠️ REMEDIATED 2026-08-21** per Architect rulings Q1/Q2/Q4/Q5 (audit trail: `09_SPEC_DEVIATIONS.md`;
> hazard refs: `data/entities/lilith/workspace/N7_DOMAIN_INDEX.md`). Changes: CI-1 content-based gate
> (D1), CI-2 compaction pin-gate + repaired plugin paths (D2/D3) + toolProfile presence-only (D9),
> CI-4 re-scoped to `permission.skill` (D8), global env-var caveat documented (D10).

---

## Subtask CI-1: MANDATES_CONDENSED.md Creation

**Spec Reference**: `docs/specs/context_injection/06_PHASE_1_PLAN.md` + Carmack Q1.1  
**Owner**: Kali  
**Status**: ready

### Acceptance Criteria (remediated — CONTENT-BASED, ruling Q1)

| # | Criterion | Verification Command | Expected Result |
|---|-----------|---------------------|-----------------|
| 1 | File exists at repo root | `ls -la MANDATES_CONDENSED.md` | File present |
| 2 | v3.8.0 lineage marker | `grep -c "v3.8.0\|27 mandates" MANDATES_CONDENSED.md` | `≥1` |
| 3 | ~1.5K tokens | `wc -c MANDATES_CONDENSED.md` | `~4000–6000 chars` |
| 4 | All 27 mandates as one-liner table rows | `grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md` | `27` |
| 5 | Table format with columns: #, Mandate, One-Liner, Status | `head -6 MANDATES_CONDENSED.md` | Markdown table header |
| 6 | Links to full SOVEREIGN_MANDATES.md | `grep -i "SOVEREIGN_MANDATES.md" MANDATES_CONDENSED.md` | Reference present |

**REMOVED**: ~~criterion "57 lines"~~ (`wc -l`) — unsatisfiable as written; source artifact is 36
lines and 57 matched the stale v3.7.0 codex snapshot by coincidence (D1/DEV-01).

### Carmack Modifications Applied
- ✅ Condensed from full AGENTS.md (~80K chars) to ~36 lines (~1.5K tokens)
- ✅ Tier 0 injection target (context truth D11: base=32K native/128K YaRN; Thinking-2507=256K native)
- ✅ Critical mandates (M1, M7, M11, M15, M23) highlighted for plugin injection
- ✅ Full mandates available in Tier 1/2 via AGENTS.md

---

## Subtask CI-2: opencode.json Updates

**Spec Reference**: `docs/specs/context_injection/06_PHASE_1_PLAN.md` + Carmack Q1.1, Q2.1, Q3.1, Q5.1  
**Owner**: Kali  
**Status**: ready  

### Acceptance Criteria (remediated — pin-gated compaction, repaired paths)

| # | Criterion | Verification Command | Expected Result |
|---|-----------|---------------------|-----------------|
| 0 | Binary pinned BEFORE compaction edit | `opencode --version` (Test 0) | Version recorded; ONE family chosen per 09 table |
| 1 | instructions array = ["AGENTS.md"] only | `jq '.instructions' opencode.json` | `["AGENTS.md"]` |
| 2 | Compaction = exactly ONE key family | `jq '.compaction' opencode.json` | V1: `{tail_turns:5, preserve_recent_tokens:80000, reserved:20000}` — OR (pin-proven only) V2: `{buffer:50000, keep.tokens:20000}`. **FAIL if both present** |
| 3 | Plugin paths all resolve (D2 repair) | `jq '.plugin[] \| select(test(".opencode/plugin/"))' opencode.json` | Empty output — no singular `.opencode/plugin/` entries remain |
| 4 | sovereign-compaction registered | `jq '.plugin[] \| select(contains("sovereign-compaction"))' opencode.json` | Path string |
| 5 | Global local-first default present (DEV-12) | `jq '.model' opencode.json` | `"lmstudio/qwen3-4b-thinking"` |
| 6 | Intentional pins ONLY on kali + verity (DEV-12) | `jq '[.agent[] \| select(.model)] \| length'` + `jq '.agent.kali.model, .agent.verity.model'` | `2`; nemotron-3-ultra-free / qwen3-1.7b |
| 7 | No `variant` keys anywhere (inert on our models — DEV-12) | `jq '[.agent[] \| select(.variant)] \| length'` | `0` |
| 8 | agent.verity isolation object | `jq '.agent.verity \| {mode,hidden,permission}'` | subagent / true / 3 denies |
| 9 | toolProfile stubs PRESENT on 6 agents (presence-only) | `jq '[.agent[] \| .toolProfile] \| length'` | `6` — values deploy/research/dev/run/debug/audit. **No behavior claim** (silently inert upstream, D9) |

### Carmack Modifications Applied
- ✅ Local-first defaults for maat/lilith/researcher/node — Q5.1 INTENT preserved via DEV-12 mechanism (global model + inheritance; was per-agent pins)
- ✅ `kali.model` cloud pin + `verity.model` local pin — the only intentional bindings
- ✅ `toolProfile` stubs on all agents — Q2.1 (intent documentation ONLY; inert upstream)
- ✅ Compaction retune for 1M context — Q3.1, now via pin-gated family selection
- ✅ 6/6 agents local-capable (only kali cloud) — Q5.1

---

## Subtask CI-3: Sovereign Compaction Plugin

**Spec Reference**: `docs/specs/context_injection/06_PHASE_1_PLAN.md` + Carmack Q3.3  
**Owner**: Kali  
**Status**: ready  

### Acceptance Criteria (from ACTIVE_SPRINT.json)

| # | Criterion | Verification Command | Expected Result |
|---|-----------|---------------------|-----------------|
| 1 | Plugin file exists | `ls -la ~/.config/opencode/plugin/sovereign-compaction.ts` | File present |
| 2 | Plugin loads without error | `opencode --log-level DEBUG 2>&1 \| grep -i "sovereign-compaction"` | "Loading plugin..." message |
| 3 | Hook registered | `opencode --log-level DEBUG 2>&1 \| grep "experimental.session.compacting"` | Hook registered |
| 4 | Injects mandates pre-compaction | `opencode --log-level DEBUG run "test" 2>&1 \| grep -A3 "SOVEREIGN MANDATES"` | M1,M7,M11,M15,M23 present |
| 5 | Injects active entity | `opencode --log-level DEBUG run "test" 2>&1 \| grep "Active Entity:"` | Entity name (e.g., "kali") |
| 6 | Injects active phase | `opencode --log-level DEBUG run "test" 2>&1 \| grep "Active Phase:"` | Phase name (e.g., "PUBLIC-DEBUT-01") |
| 7 | Injects session anchor path | `opencode --log-level DEBUG run "test" 2>&1 \| grep "Session Anchor:"` | "data/coordination/SESSION_ANCHOR.md" |
| 8 | Uses unshift() for top-of-context priority | Code review: `output.context.unshift(mandates)` | Present in plugin |
| 9 | **REQUIRED: post-compaction summary retains mandates** (ruling #3, DEV-07) | Force compaction in scratch session; grep summary for the four elements | "SOVEREIGN MANDATES" + Active Entity + Active Phase + SESSION_ANCHOR all present in summary |

### Carmack Modifications Applied
- ✅ Defense-in-depth (not primary) — Q3.3: "Plugin hook = defense-in-depth... Checkpoint is primary; hook is secondary"
- ✅ Injects Tier 0 mandates (5 critical) not full 27
- ✅ Reads OMEGA_ENTITY, OMEGA_PHASE from environment
- ✅ References SESSION_ANCHOR.md for hydration

---

## Subtask CI-4: Skills Opt-In

**Spec Reference**: `docs/specs/context_injection/06_PHASE_1_PLAN.md` + Lazy Skills pattern  
**Owner**: Kali  
**Status**: ready  

### Acceptance Criteria (remediated — CI-4 re-scoped to permission.skill, ruling Q2)

| # | Criterion | Verification Command | Expected Result |
|---|-----------|---------------------|-----------------|
| 1 | Global `permission.skill` block present | `jq '.permission.skill' opencode.json` | Object with 3 `"allow"` + named `"deny"` entries |
| 2 | Core 3 allowed: research, spec-generator, knowledge-miner | `jq '.permission.skill \| with_entries(select(.value=="allow")) \| keys'` | Those 3 keys |
| 3 | Repo utility skills denied (10 named) | `jq '.permission.skill \| with_entries(select(.value=="deny")) \| length'` | `≥10` |
| 4 | BEHAVIORAL: denied skills not advertised | E2E: agent lists available skills; grep for denied names | `0` hits for denied; core 3 present |
| 5 | No SKILL.md files modified by this subtask | `git status .opencode/skills/` | Clean |

**REMOVED**: all `auto_load:` criteria — auto_load is NOT an opencode feature (zod parses only
name/description; web Q-B5). Original sed-loop plan was a no-op (D8/DEV-04). Token-impact claim
"23K→150" also corrected: skills were already on-demand; real saving = advertisement-list shrink
(~1.1K → ~150 tok) + prevented accidental heavy loads (DEV-05).

### Carmack Modifications Applied
- ✅ Lazy Skills pattern preserved via upstream-native mechanism (advertise-on-demand was already true)
- ✅ Only core research/spec/miner skills visible by default
- ✅ Per-agent overrides available via agent-level `permission.skill` (explicit > ambient)

---

## Subtask CI-5: Verification Tests

**Spec Reference**: `docs/specs/context_injection/06_PHASE_1_PLAN.md` §5  
**Owner**: Kali  
**Status**: ready  

### Acceptance Criteria (from ACTIVE_SPRINT.json)

| # | Criterion | Verification Command | Expected Result |
|---|-----------|---------------------|-----------------|
| 1 | AGENTS.md injection works | `opencode --log-level DEBUG run "What is first sentence of SOVEREIGN_MANDATES.md?"` | Returns "All asynchronous code MUST use AnyIO" |
| 2 | Researcher uses local model | `opencode --agent researcher run "What model are you?"` | Mentions "qwen3-4b-thinking" |
| 3 | Kali uses cloud model | `opencode --agent kali run "What model are you?"` | Mentions "nemotron-3-ultra-free" |
| 4 | Node uses local model | `opencode --agent node run "What model are you?"` | Mentions "qwen3-1.7b" |
| 5 | Only 3 skills visible in debug | `opencode --log-level DEBUG run "hello" 2>&1 \| grep -c "skill"` | `~3` |
| 6 | Compaction plugin injects context | `opencode --log-level DEBUG run "test" 2>&1 \| grep "SOVEREIGN MANDATES"` | Present |

### Test Execution Order
1. Run CI-1 verification (file checks)
2. Run CI-2 verification (jq queries)
3. Run CI-3 verification (plugin load + hook)
4. Run CI-4 verification (skill counts)
5. Run CI-5 verification (E2E agent queries)

---

## Phase 1 Completion Gate

**All 5 subtasks must pass** for `CONTEXT-INJECTION` workstream status → `completed`

```bash
# Final gate check (remediated — content-based, pin-gated, behavior-tested)
echo "=== PHASE 1 GATE ===" && \
opencode --version && \
grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md && \
jq '.instructions' opencode.json && \
jq '.compaction' opencode.json && \
ls ~/.config/opencode/plugin/sovereign-compaction.ts && \
jq '.permission.skill' opencode.json && \
opencode --agent researcher run "What model are you?" 2>&1 | head -1 && \
opencode --agent kali run "What model are you?" 2>&1 | head -1 && \
echo "=== GATE PASSED ==="
```

**Expected Output** (V1-family variant shown):
```
=== PHASE 1 GATE ===
1.18.19          # <- whatever Test 0 pinned; recorded in execution notes
27
["AGENTS.md"]
{"auto":true,"prune":true,"tail_turns":5,"preserve_recent_tokens":80000,"reserved":20000}
/home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts
{...3 allows + denies...}
qwen3-4b-thinking
nemotron-3-ultra-free
=== GATE PASSED ===
```

**Gate additions vs original**: binary pin first; mandate-row count replaces line count; compaction
family shown whole (mixed families = FAIL); permission.skill block required; plugin path checks in
CI-2/CI-3 catch the D2 dead-path regression.

---

## Traceability Matrix

| Spec Section | ACTIVE_SPRINT.json Subtask | Verification File | Carmack Q |
|--------------|---------------------------|-------------------|-----------|
| 01_MANDATES_CONDENSED.md | CI-1 | 05_VERIFICATION_TESTS.md Test 1 | Q1.1, Q3.1 |
| 02_OPENCODE_JSON_DIFF.md | CI-2 | 05_VERIFICATION_TESTS.md Test 2 | Q1.1, Q2.1, Q3.1, Q5.1 |
| 03_SOVEREIGN_COMPACTION_PLUGIN.md | CI-3 | 05_VERIFICATION_TESTS.md Test 3 | Q3.3 |
| 04_SKILLS_OPT_IN.md | CI-4 | 05_VERIFICATION_TESTS.md Test 4 | Lazy Skills |
| 05_VERIFICATION_TESTS.md | CI-5 | 05_VERIFICATION_TESTS.md Test 5 | All |

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ci_phase1_spec ⬡ 2026-08-20*