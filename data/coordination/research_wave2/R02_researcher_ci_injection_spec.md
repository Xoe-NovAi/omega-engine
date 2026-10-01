---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0.0"
document_type: "research_deliverable"
task_id: "R02"
session_purpose: "Full audit of Context Injection Phase 1 spec + Carmack review; extraction of everything implementer needs to build CI Ph1 correctly"
author: "CI-Injection Specialist (researcher sub-facet)"
date: "2026-08-26"
ground_truth_date: "2026-08-26T18:00:00Z"
binary_pin: "opencode 1.18.23 (Architect decision 2026-08-26: KEEP 1.18.23, revalidate — no downgrade from 1.18.19)"
sources:
  - "docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md"
  - "docs/specs/context_injection/CONTEXT_INJECTION_PHASE1_IMPLEMENTATION_SPEC.md"
  - "docs/specs/context_injection/phase1_spec/ (all 9 files)"
  - "opencode.json (live, 2026-08-26)"
  - "MANDATES_CONDENSED.md (exists, 2026-08-22)"
  - "~/.config/opencode/plugin/sovereign-compaction.ts (exists, 2026-08-21)"
---

> ## ⚡ ARCHITECT DECISION (2026-08-26) — OVERRIDES ALL "BLOCKING" STATUSES BELOW
> **OpenCode binary: KEEP 1.18.23. Do NOT downgrade to 1.18.19.** Re-run the behavioral compaction
> probe on 1.18.23 to verify V1 vs V2 key-family consumption, then proceed with config edits. The
> version mismatch is RESOLVED by this decision — wave 2 implementer should treat 1.18.23 as the
> ground-truth binary and validate compaction key family against it.
> **Source**: WAKE_STATE.json pre_compaction_lockin_20260826.architect_decisions.opencode_binary

# R02 — Context Injection Phase 1: Complete Implementation Audit

## §1: What CI Ph1 Is (Summary)

Context Injection Phase 1 is a **config-only, zero-code-change** optimization of the OpenCode
agent runtime. It reduces the base token prompt from ~31K measured to ~18K theoretical (42%
reduction), enabling local models (Qwen3-4B, 8K-16K context) to function as Tier 0 execution
engines instead of requiring cloud fallback. The work consists of 5 deliverables:
(1) MANDATES_CONDENSED.md for Tier 0 injection, (2) opencode.json restructuring (instructions,
compaction, model routing, plugin paths, skill permissions), (3) sovereign-compaction TypeScript
plugin for pre-compaction context injection, (4) permission.skill deny patterns for skills
opt-in, (5) verification tests. All changes are reversible. The spec has been through
Carmack review (2026-08-20, ACCEPTED WITH MODIFICATIONS) and N7 remediation audit
(2026-08-21, 13 hazards found, 11 deviations logged). The remediated spec in `phase1_spec/`
supersedes the original `06_PHASE_1_PLAN.md`.

## §2: Acceptance Criteria (Binary, Testable)

### CI-1: MANDATES_CONDENSED.md Creation

| # | Criterion | Verification Command | Expected | Status |
|---|-----------|---------------------|----------|--------|
| 1 | File exists at repo root | `ls MANDATES_CONDENSED.md` | File present | **PASS** (verified 2026-08-26) |
| 2 | v3.8.0 lineage marker | `grep -c "v3.8.0\|27 mandates" MANDATES_CONDENSED.md` | ≥1 | **PASS** |
| 3 | ~1.5K tokens (4-6K chars) | `wc -c MANDATES_CONDENSED.md` | ~4000-6000 | **PASS** (51 lines) |
| 4 | All 27 mandate rows | `grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md` | 27 | **PASS** |
| 5 | Markdown table header | `head -6 MANDATES_CONDENSED.md` | Table format | **PASS** |
| 6 | Links to SOVEREIGN_MANDATES.md | `grep -i "SOVEREIGN_MANDATES.md" MANDATES_CONDENSED.md` | Reference present | **PASS** |

**REMOVED gate**: ~~`wc -l = 57`~~ — unsatisfiable coincidence trap (DEV-01/D1).

**CI-1 VERDICT: ✅ COMPLETE — no action needed.**

---

### CI-2: opencode.json Updates

| # | Criterion | Verification Command | Expected | Status |
|---|-----------|---------------------|----------|--------|
| 0 | Binary pin recorded | `opencode --version` | 1.18.23 (NOTE: spec pins 1.18.19) | **⚠️ MISMATCH** |
| 1 | instructions = ["AGENTS.md"] | `jq '.instructions' opencode.json` | `["AGENTS.md"]` | **NOT DONE** (still 5-file array) |
| 2 | Compaction = ONE key family | `jq '.compaction' opencode.json` | V1: {tail_turns:5, preserve_recent_tokens:80000, reserved:20000} | **NOT DONE** (still old values) |
| 3 | Plugin paths all plural | `jq '.plugin[] \| select(test(".opencode/plugin/"))' opencode.json` | Empty (no singular paths) | **FAIL** (2 dead singular paths exist) |
| 4 | sovereign-compaction registered | `jq '.plugin[] \| select(contains("sovereign-compaction"))' opencode.json` | Path string | **NOT DONE** |
| 5 | Global local-first model | `jq '.model' opencode.json` | `"lmstudio/qwen3-4b-thinking"` | **NOT DONE** (currently "opencode/nemotron-3-ultra-free") |
| 6 | Pins ONLY on kali + verity | `jq '[.agent[] \| select(.model)] \| length'` | 2 | **NOT DONE** (no per-agent models at all currently) |
| 7 | No variant keys | `jq '[.agent[] \| select(.variant)] \| length'` | 0 | **PASS** (no variants in current config) |
| 8 | verity isolation | `jq '.agent.verity \| {mode,hidden,permission}'` | subagent/true/3 denies | **PARTIAL** (mode=subagent exists; hidden+permission NOT DONE) |
| 9 | toolProfile stubs on 6 agents | `jq '[.agent[] \| .toolProfile] \| length'` | 6 | **NOT DONE** |
| 10 | permission.skill block | `jq '.permission.skill' opencode.json` | 3 allows + denies | **NOT DONE** |

**CI-2 VERDICT: ❌ NOT STARTED — this is the primary remaining work.**

---

### CI-3: Sovereign Compaction Plugin

| # | Criterion | Verification Command | Expected | Status |
|---|-----------|---------------------|----------|--------|
| 1 | Plugin file exists | `ls ~/.config/opencode/plugin/sovereign-compaction.ts` | File present | **PASS** (verified) |
| 2 | Plugin loads without error | `opencode --log-level DEBUG 2>&1 \| grep sovereign-compaction` | Loading message | **UNTESTED** (requires opencode restart) |
| 3 | Hook registered | Debug grep for `experimental.session.compacting` | Hook present | **UNTESTED** |
| 4 | Injects mandates | Post-compaction summary grep | M1,M7,M11,M15,M23 present | **UNTESTED** |

**CI-3 VERDICT: ✅ DEPLOYED — file exists with correct implementation. Testing requires opencode restart.**

---

### CI-4: Skills Opt-In

| # | Criterion | Verification Command | Expected | Status |
|---|-----------|---------------------|----------|--------|
| 1 | permission.skill block | `jq '.permission.skill' opencode.json` | Object with 3 allows + denies | **NOT DONE** |
| 2 | Core 3 allowed | `jq '.permission.skill \| with_entries(select(.value=="allow")) \| keys'` | research/spec-generator/knowledge-miner | **NOT DONE** |
| 3 | Denies present | `jq '.permission.skill \| with_entries(select(.value=="deny")) \| length'` | ≥10 | **NOT DONE** |

**CI-4 VERDICT: ❌ NOT STARTED — requires CI-2 (opencode.json edit).**

---

### CI-5: Verification Tests

| # | Criterion | Command | Expected | Status |
|---|-----------|---------|----------|--------|
| 1 | AGENTS.md injection | `opencode run "What is first sentence of SOVEREIGN_MANDATES.md?"` | Correct quote | **NOT TESTED** |
| 2 | Researcher local model | `opencode --agent researcher run "What model are you?"` | qwen3-4b-thinking | **NOT TESTED** |
| 3 | Kali cloud model | `opencode --agent kali run "What model are you?"` | nemotron-3-ultra-free | **NOT TESTED** |
| 4 | Skills shrunk | Debug grep for skill count | ~3 visible | **NOT TESTED** |
| 5 | Plugin injects context | Post-compaction summary check | Mandates present | **NOT TESTED** |

**CI-5 VERDICT: ❌ BLOCKED on CI-2 + CI-4 completion.**

---

## §3: Config-Only Boundary (In-Scope / Out-of-Scope)

### In-Scope (Phase 1 — Config Changes Only)

| Change | Target File | Type | Reversible |
|--------|-------------|------|------------|
| Create MANDATES_CONDENSED.md | `MANDATES_CONDENSED.md` (repo root) | New file | `rm` |
| Update instructions array | `opencode.json` → `instructions` | JSON edit | `git checkout` |
| Update compaction config | `opencode.json` → `compaction` | JSON edit | `git checkout` |
| Fix plugin paths (singular→plural) | `opencode.json` → `plugin[]` | JSON edit | `git checkout` |
| Register sovereign-compaction plugin | `opencode.json` → `plugin[]` | JSON edit | `git checkout` |
| Add global model default | `opencode.json` → `model` | JSON edit | `git checkout` |
| Add per-agent model pins (kali, verity) | `opencode.json` → `agent.{kali,verity}.model` | JSON edit | `git checkout` |
| Add per-agent temperatures | `opencode.json` → `agent.*.temperature` | JSON edit | `git checkout` |
| Add verity isolation (hidden, permission) | `opencode.json` → `agent.verity` | JSON edit | `git checkout` |
| Add toolProfile stubs | `opencode.json` → `agent.*.toolProfile` | JSON edit | `git checkout` |
| Add permission.skill block | `opencode.json` → `permission.skill` | JSON edit | `jq del` |
| Deploy sovereign-compaction plugin | `~/.config/opencode/plugin/sovereign-compaction.ts` | New file | `rm` |
| Set env vars (OMEGA_ENTITY, OMEGA_PHASE, DISABLE_AUTOCOMPACT) | `~/.bashrc` / `~/.zshrc` | Shell profile | `sed -i` removal |

### Explicitly OUT of Scope (Phase 1)

| Item | Why Out | Phase |
|------|---------|-------|
| Any Python code changes | Config-only mandate | Phase 2 |
| MCP server domain split | Requires code refactoring | Phase 2 (Q2.1) |
| SequentialModelLoader | Requires new Python module | Phase 2 |
| HeadroomMiddleware integration | Requires oracle code changes | Phase 2 |
| Hydration Engine | Requires sidecar process | Phase 2 |
| Token Budget Enforcer | Requires ModelGateway changes | Phase 2 |
| Local Token Counter (ctypes) | Requires llama.cpp bindings | Phase 2 |
| Tool profile BEHAVIORAL enforcement | toolProfile is inert upstream (D9) | Phase 2 |
| zswap/NVMe subsystem | Requires sysadmin/sudo | Phase 2 |
| Schema compression | REJECTED as solution theater (Q2.2) | NEVER |
| Validator service (NeMo Guardrails) | REJECTED as over-engineering (Q7.2) | NEVER |
| Dynamic per-model compaction | Requires upstream OpenCode change | Phase 2+ |
| Per-agent compaction overrides | OpenCode doesn't support it | Upstream |

---

## §4: Carmack Decisions (Accepted / Rejected / Modified)

### Accepted (Implemented in Remediated Spec)

| ID | Question | Verdict | Rationale | Spec Section |
|----|----------|---------|-----------|--------------|
| Q1.1 | 31K vs 4K-8K context conflict | **MODIFY** → MANDATES_CONDENSED.md | Base prompt exceeds local model context by 4-8x. Condense to 1.5K tokens for Tier 0. | §1 (CI-1) |
| Q1.2 | Sequential loading (--no-mmap --mlock) | **ACCEPT** | Correct for constrained hardware. One model at a time, peak 7.5GB, headroom 8.5GB. | Phase 2 |
| Q1.3 | KV Cache q8_0 standard | **ACCEPT** | 50% memory savings, <2% quality loss. Standard llama.cpp best practice. | Phase 2 |
| Q3.2 | Hydration Engine sidecar | **ACCEPT** | Separate process survives OpenCode crashes. Independent checkpoint at 80%. | Phase 2 |
| Q3.3 | Compaction loses sovereign context | **REJECT** plugin-only → **BOTH layers** | Plugin hook = defense-in-depth (secondary). Checkpoint at 80% = primary. Both needed. | Plugin (Ph1) + Hydration (Ph2) |
| Q4.1 | Per-agent budgets in ModelGateway | **ACCEPT** | Minimal sovereign point. In-process, no extra hop. Fixed tier budgets. | Phase 2 |
| Q4.2 | Token counting via llama.cpp ctypes | **MODIFY** → ±10% with headroom | tiktoken inaccurate for non-OpenAI. Use llama_tokenize() via ctypes. | Phase 2 |
| Q5.2 | Subagent model inheritance | **ACCEPT** | Use @agent invocation with primary-mode agents. Don't fight framework. | Phase 1 config |
| Q6.1 | Headroom middleware compression | **ACCEPT with verification** | Real-world 60-85% on tool outputs. Worth the 5ms latency. | Phase 2 |
| Q6.2 | Compression latency budget | **ACCEPT** | Break-even ~2ms for local models. Net win 260ms per request. | Phase 2 |

### Modified (Amended by N7/Architect After Carmack)

| ID | Carmack Said | N7/Architect Changed | Why | Impact |
|----|-------------|---------------------|-----|--------|
| Q5.1 | Per-agent model pins: researcher=qwen3-4b-thinking, maat=qwen3-4b-thinking, lilith=qwen3-4b-thinking, node=qwen3-1.7b | **Global default** `"model": "lmstudio/qwen3-4b-thinking"` + inheritance; pins ONLY kali (nemotron) + verity (qwen3-1.7b) | TUI `/models` snap-back (#13456); Architect dislikes hardcoded variants; precedence chain (CLI > agent > session > global) makes pins redundant | agent config structure significantly different from original Carmack spec |
| Q3.1 compaction | `buffer: 50000`, `keep.tokens: 20000` (V2 keys) | **V1 keys primary**: `tail_turns:5, preserve_recent_tokens:80000, reserved:20000`. V2 only if binary-pin proves consumption. | v1.x honors V1 family only; V2 keys may trip strict validation (additionalProperties:false) | Compaction config is completely different from original Carmack spec |
| Q2.1 toolProfile | Tool profiles with behavioral enforcement | **Presence-only stubs** (inert upstream, D9) | AgentConfig has no toolProfile key; silently accepted, does nothing | No token savings claimed from toolProfile |

### Rejected (Solution Theater per M19/M23)

| ID | Item | Verdict | Reason |
|----|------|---------|--------|
| Q2.2 | Schema compression engineering | **REJECT** | Fix architecture (split servers), don't compress symptom |
| Q7.2 | Validator service (NeMo Guardrails) | **REJECT** | Condensed mandates + CI gates sufficient; adds dependency + latency |
| — | Hydration 5-layer recovery | **CUT to 3-layer** | L4/L5 over-engineering |
| — | Dynamic token budget allocation | **CUT to fixed tiers** | Fixed tiers proven; dynamic = complexity |
| — | 3-level session summarizer | **CUT to 1-level** | Single summary sufficient |
| — | Gateway observability (LiteLLM) | **CUT** | In-process OTel → local Prometheus is sovereign |
| — | Custom compaction plugin replacing OpenCode | **DELETE** | Over-engineering; use hook + dynamic buffer |
| — | "Accept cloud fallback for Tier 0" | **DELETE** | Violates M7 Local-First |
| — | Per-model compaction config in OpenCode | **DEFER** | Upstream dependency |

### Critical N7 Findings (13 Hazards, 11 Deviations)

| DEV | Finding | Impact on Implementer |
|-----|---------|----------------------|
| DEV-01 | CI-1 line-count gate (57 lines) was unsatisfiable; replaced with content-based (27 mandate rows) | Use `grep -cE '^\| M[0-9]+'` not `wc -l` |
| DEV-02 | Compaction V2 keys (`buffer`, `keep.tokens`) are a different product line from V1 | **MUST pin binary first**, apply ONE family, never both |
| DEV-03 | Plugin paths in opencode.json use singular `.opencode/plugin/` but files live at `.opencode/plugins/` | Current live config has DEAD plugin paths — fix is part of CI-2 |
| DEV-04 | `auto_load:` in SKILL.md is NOT an opencode feature | CI-4 uses `permission.skill` patterns instead |
| DEV-05 | "23K→150 tokens" claim was false (skills already on-demand) | Real saving = advertisement-list shrink (~1.1K→~150) |
| DEV-06 | toolProfile is silently inert upstream | No behavior claim; presence-only check |
| DEV-07 | Plugin hook shapes compaction SUMMARY PROMPT, not live context | Verify by inspecting post-compaction summary |
| DEV-08 | OPENCODE_DISABLE_AUTOCOMPACT is process-global, no per-agent | #32385 bypass documented (provider overflow ignores flag) |
| DEV-09 | "Qwen3-4B 8K-16K" was inaccurate; base=32K native, 128K YaRN | Live cap 8192 is a config choice; ctx-raise deferred |
| DEV-10 | Rollback + impl-order updated for CI-4 re-scope | Use `jq del(.permission.skill)` not `sed` on SKILL.md |
| DEV-11 | Index updated with 09 registered | Navigation completeness |
| DEV-12 | Model strategy re-mechanized: global default + inheritance | Significant structural change from Carmack's per-agent pins |

---

## §5: Implementation Steps (Ordered, File:Line Cited)

### Prerequisite: Binary Pin Verification

**CRITICAL**: The spec pins opencode 1.18.19. The live binary is **1.18.23**. This is a
**blocking discrepancy** that must be resolved before any compaction config changes.

**Step 0: Resolve Binary Pin**
```bash
opencode --version  # Currently returns 1.18.23
```
**Decision required**: Either (a) downgrade to 1.18.19, or (b) re-run the behavioral
compaction probe on 1.18.23 to verify V1 vs V2 key family consumption. The spec's
Binary-Pin Decision Table (09_SPEC_DEVIATIONS.md §Binary-Pin) applies:
- If 1.18.23 is v1.x stable → V1 family (tail_turns/preserve_recent_tokens/reserved)
- If 1.18.23 proves V2 consumption → V2 family (buffer/keep.tokens)
- NEVER both simultaneously

**Owner**: Architect (billing/infrastructure) or whoever controls the binary.

---

### Step 1: CI-2 — Update opencode.json (PRIMARY REMAINING WORK)

**Target file**: `opencode.json` (repo root: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json`)

**Current state** (verified 2026-08-26):
- Line 27-33: `instructions` = 5-file array (needs → `["AGENTS.md"]`)
- Line 64-70: `compaction` = old V1 values (needs → tail_turns:5, preserve:80000, reserved:20000)
- Line 4-9: `plugin[]` = 4 entries with 2 DEAD singular paths (needs → repair to plural + add sovereign-compaction)
- Line 171-262: `agent` = 12 agents, no model routing, no toolProfile (needs → add global model, pins on kali+verity, toolProfile stubs)
- Line 263: `model` = "opencode/nemotron-3-ultra-free" (needs → "lmstudio/qwen3-4b-thinking")
- No `permission.skill` block exists (needs → add 3 allows + denies)

**Complete target state** (from `phase1_spec/02_OPENCODE_JSON_DIFF.md` lines 91-153):

```json
{
  "model": "lmstudio/qwen3-4b-thinking",
  "instructions": ["AGENTS.md"],
  "plugin": [
    "opencode-antigravity-auth@latest",
    "opencode-sessions-explorer",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/error-capture.ts",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/awareness.ts",
    "file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
  ],
  "permission": {
    "skill": {
      "research": "allow",
      "spec-generator": "allow",
      "knowledge-miner": "allow",
      "legacy-pattern-miner": "deny",
      "blitz-tunnel": "deny",
      "blitz-validate": "deny",
      "git-secret-scrub": "deny",
      "hf-cli": "deny",
      "omega-doc-architect": "deny",
      "pr-readiness-checker": "deny",
      "provider-validator": "deny",
      "sovereign-refinement-protocol": "deny",
      "sovereign-search": "deny"
    }
  },
  "agent": {
    "kali": {
      "mode": "all",
      "model": "opencode/nemotron-3-ultra-free",
      "temperature": 0.3,
      "steps": 50,
      "toolProfile": "deploy"
    },
    "researcher": {
      "mode": "all",
      "temperature": 0.1,
      "steps": 100,
      "toolProfile": "research"
    },
    "maat": {
      "mode": "all",
      "temperature": 0.2,
      "toolProfile": "dev"
    },
    "lilith": {
      "mode": "all",
      "temperature": 0.3,
      "toolProfile": "run"
    },
    "node": {
      "mode": "all",
      "temperature": 0.1,
      "steps": 20,
      "toolProfile": "debug"
    },
    "verity": {
      "mode": "subagent",
      "model": "lmstudio/qwen3-1.7b",
      "temperature": 0.0,
      "prompt": "{file:.opencode/agents/verity.md}",
      "permission": { "edit": "deny", "bash": "deny", "skill": "deny" },
      "hidden": true,
      "toolProfile": "audit"
    }
  }
}
```

**⚠️ CRITICAL NOTES FOR IMPLEMENTER**:
1. **Preserve all 12 existing agents** — the target state above only shows the 6 CI-scope agents. The other 6 (makali, jem, doom_guy, roc_racoon, john_carmack, grok_cli) must remain UNTOUCHED. Only ADD model/toolProfile/temperature to the 6 in scope; do NOT delete or modify the other 6.
2. **Preserve ALL existing keys** in each agent block (instructions, description, mode, etc.). Only ADD the new keys.
3. **Plugin paths**: current config at line 7-8 has `.opencode/plugin/` (singular) — must become `.opencode/plugins/` (plural). The actual directory is `.opencode/plugins/` (verified).
4. **top-level `"model"`**: currently `"opencode/nemotron-3-ultra-free"` at line 263. Change to `"lmstudio/qwen3-4b-thinking"`. This becomes the global default that unpinned agents inherit.
5. **`small_model`**: currently at line 264, keep as-is or update — spec doesn't address it.
6. **`default_agent`**: currently `"kali"` at line 265, keep as-is.
7. **JSONC caveat**: the diff in `02_OPENCODE_JSON_DIFF.md` line 186 shows a `// V2 family` comment. **Do NOT paste comments into opencode.json** — it's JSON, not JSONC.

**Implementation approach**: Use `jq` for atomic edits:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
cp opencode.json opencode.json.backup  # ALWAYS backup first

# Step 1: Fix global model
jq '.model = "lmstudio/qwen3-4b-thinking"' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# Step 2: Fix instructions
jq '.instructions = ["AGENTS.md"]' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# Step 3: Fix compaction (V1 family — PRIMARY TARGET)
jq '.compaction = {"auto":true,"prune":true,"tail_turns":5,"preserve_recent_tokens":80000,"reserved":20000}' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# Step 4: Fix plugin paths (singular→plural) + add sovereign-compaction
jq '.plugin = [
  "opencode-antigravity-auth@latest",
  "opencode-sessions-explorer",
  "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/error-capture.ts",
  "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/awareness.ts",
  "file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
]' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# Step 5: Add permission.skill block
jq '.permission.skill = {
  "research":"allow","spec-generator":"allow","knowledge-miner":"allow",
  "legacy-pattern-miner":"deny","blitz-tunnel":"deny","blitz-validate":"deny",
  "git-secret-scrub":"deny","hf-cli":"deny","omega-doc-architect":"deny",
  "pr-readiness-checker":"deny","provider-validator":"deny",
  "sovereign-refinement-protocol":"deny","sovereign-search":"deny"
}' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# Step 6: Update 6 agent blocks (ADD keys, preserve existing)
# kali — add model, temperature, toolProfile
jq '.agent.kali.model = "opencode/nemotron-3-ultra-free" | .agent.kali.temperature = 0.3 | .agent.kali.toolProfile = "deploy"' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# researcher — add temperature, toolProfile (inherits global model)
jq '.agent.researcher.temperature = 0.1 | .agent.researcher.toolProfile = "research"' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# maat — add temperature, toolProfile
jq '.agent.maat.temperature = 0.2 | .agent.maat.toolProfile = "dev"' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# lilith — add temperature, toolProfile
jq '.agent.lilith.temperature = 0.3 | .agent.lilith.toolProfile = "run"' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# node — add temperature, steps, toolProfile
jq '.agent.node.temperature = 0.1 | .agent.node.steps = 20 | .agent.node.toolProfile = "debug"' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# verity — add model, temperature, permission, hidden, toolProfile
jq '.agent.verity.model = "lmstudio/qwen3-1.7b" | .agent.verity.temperature = 0.0 | .agent.verity.hidden = true | .agent.verity.permission = {"edit":"deny","bash":"deny","skill":"deny"} | .agent.verity.toolProfile = "audit"' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json

# Step 7: Verify
jq '.instructions,.compaction,.model,.permission.skill' opencode.json
```

**Time estimate**: 15-20 minutes
**Depends on**: Step 0 (binary pin resolution)

---

### Step 2: CI-4 — Permission.skill (INCLUDED in Step 1)

CI-4 is part of the opencode.json edit in Step 1. The `permission.skill` block is applied
as part of the same file. No separate step needed.

**Depends on**: Step 1
**Time estimate**: Included in Step 1

---

### Step 3: Environment Variables

**Target files**: `~/.bashrc`, `~/.zshrc`

```bash
# Add to shell profile
echo 'export OMEGA_ENTITY="kali"' >> ~/.bashrc
echo 'export OMEGA_PHASE="PUBLIC-DEBUT-01"' >> ~/.bashrc
echo 'export OPENCODE_DISABLE_AUTOCOMPACT=1' >> ~/.bashrc
```

**⚠️ KNOWN BYPASS (DEV-08)**: `OPENCODE_DISABLE_AUTOCOMPACT` is process-global. The #32385
bypass means provider-overflow auto-recovery may ignore this flag through ≥v1.17.7.
Manual `/compact` discipline is required under this flag.

**Depends on**: None
**Time estimate**: 2 minutes

---

### Step 4: CI-5 — Verification Tests

Run the full test suite from `phase1_spec/05_VERIFICATION_TESTS.md`:

```bash
# Test 0: Binary pin
opencode --version | tee /tmp/oc_pin.txt

# Test 1: MANDATES_CONDENSED (already passes)
grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md  # → 27

# Test 2: opencode.json shape
jq '.instructions' opencode.json               # → ["AGENTS.md"]
jq '.compaction' opencode.json                  # → V1 family
jq '.model' opencode.json                       # → "lmstudio/qwen3-4b-thinking"
jq '.permission.skill' opencode.json            # → 3 allows + denies

# Test 3: Plugin loads (requires restart)
opencode --log-level DEBUG 2>&1 | grep -i "sovereign-compaction"

# Test 4: Skills effective
jq '.permission.skill | with_entries(select(.value=="allow")) | keys' opencode.json

# Test 5: E2E agent identity
opencode --agent researcher run "What model are you?"  # → qwen3-4b-thinking
opencode --agent kali run "What model are you?"         # → nemotron-3-ultra-free
```

**Depends on**: Steps 1-3 complete
**Time estimate**: 10-30 minutes

---

### Step 5: Commit

```bash
git add MANDATES_CONDENSED.md opencode.json
git commit -m "ci: Phase 1 context injection — config-only optimization"
```

**Depends on**: Step 4 pass
**Time estimate**: 2 minutes

---

### Implementation Timeline

```
Step 0 (Binary pin)  → 5 min (verify version, choose compaction family)
Step 1 (opencode.json) → 20 min (jq edits, verify each change)
Step 3 (env vars)    → 2 min
Step 4 (verification) → 15 min
Step 5 (commit)      → 2 min
────────────────────────────
TOTAL                → ~45 minutes (if binary pin is already resolved)
```

---

## §6: Regression Risk + Required Tests

### High-Risk Changes

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Binary version mismatch** (1.18.23 vs pin 1.18.19) | 🔴 BLOCKING | MUST resolve before compaction edit. Run behavioral probe on 1.18.23 to verify V1 key consumption. |
| **Dead plugin paths** (singular → plural) | 🔴 HIGH | Current live config has 2 DEAD plugin entries. Fix is part of CI-2. Verify with `ls .opencode/plugins/` |
| **Global model override** (nemotron → qwen3-4b-thinking) | 🟡 MEDIUM | Changes default model for ALL agents including makali, jem, doom_guy, roc_racoon, john_carmack, grok_cli. These 6 are NOT in CI scope. Verify they still function with local model. |
| **Compaction thrashing** on local models | 🟡 MEDIUM | `OPENCODE_DISABLE_AUTOCOMPACT=1` is process-global; also disarms auto-compaction for 1M-context cloud workhorse. Manual `/compact` discipline required. |
| **Plugin hook shape** (DEV-07) | 🟡 MEDIUM | Plugin shapes compaction SUMMARY PROMPT, not live context. Verify post-compaction summary retains mandates. |
| **Agent key loss** during jq edits | 🟡 MEDIUM | jq `|=` operations must preserve existing keys. ALWAYS backup first. Test with `jq '.agent.kali' opencode.json` after each edit. |
| **Permission.skill breaks agent invocation** | 🟢 LOW | permission.skill deny only affects skill tool availability, not agent spawning or basic functionality. |

### Required Regression Tests

| Test | Command | Pass Criteria | Blocks |
|------|---------|---------------|--------|
| `make test` | `source .venv/bin/activate && make test` | 0 failures (baseline) | All CI subtasks |
| `omega talk` | `source .venv/bin/activate && omega talk "hello"` | EXIT 0, response present | CI-5 E2E |
| Local inference | `omega talk "hello"` (with native-gguf or lmster) | No cloud fallback | M7 compliance |
| Plugin load | `opencode --log-level DEBUG 2>&1 \| grep -i error` | No ENOENT for any plugin path | CI-3 |
| Agent spawn | `opencode --agent researcher run "hello"` | Agent starts, model = qwen3-4b-thinking | CI-5 |
| Kali spawn | `opencode --agent kali run "hello"` | Agent starts, model = nemotron-3-ultra-free | CI-5 |
| Verity isolation | `opencode --agent verity run "hello"` | Agent starts, cannot edit/bash/skill | CI-2 |

### Post-Deployment Monitoring

After CI Ph1 commits, monitor for:
1. **Compaction behavior**: Does auto-compaction actually stop when `OPENCODE_DISABLE_AUTOCOMPACT=1` is set? (DEV-08 warning: #32385 bypass)
2. **Plugin errors**: Check OpenCode logs for sovereign-compaction load failures
3. **Model fallback**: Do unpinned agents (makali, jem, etc.) attempt cloud when local is unavailable?
4. **Skill visibility**: Run `opencode --log-level DEBUG run "hello"` and verify only 3 skills advertised

---

## §7: Build-Packet (Implementer's Checklist)

This is the complete, self-contained guide for the wave-2 implementer. Open this file and follow sequentially.

### Pre-Flight Checklist

- [ ] Read this document (R02) completely
- [ ] Read `docs/specs/context_injection/phase1_spec/index.md` (spec overview)
- [ ] Read `docs/specs/context_injection/phase1_spec/09_SPEC_DEVIATIONS.md` (11 deviations — you MUST understand these)
- [ ] Read `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` (Carmack's verdict)
- [ ] Verify `MANDATES_CONDENSED.md` exists at repo root → **CI-1 already done**
- [ ] Verify `~/.config/opencode/plugin/sovereign-compaction.ts` exists → **CI-3 already done**
- [ ] Run `opencode --version` → record version (currently 1.18.23, spec pins 1.18.19)

### Blocking Issue: Binary Pin

| Current | Spec Pin | Action Required |
|---------|----------|----------------|
| 1.18.23 | 1.18.19 | **Decision needed**: downgrade to 1.18.19 OR re-run behavioral probe on 1.18.23 |

**Behavioral probe** (if keeping 1.18.23):
```bash
# Create temp config with extreme V1 value
jq '.compaction.reserved = 999999' /tmp/test_oc.json > /tmp/test_oc2.json
# Run opencode with temp config, trigger compaction in scratch session
# Observe: does reserved=999999 take effect? → V1 family confirmed
# If not: try V2: jq '.compaction = {"auto":true,"buffer":999999,"keep":{"tokens":999999}}'
# Observe: does buffer/keep take effect? → V2 family confirmed
```

### Execution Steps

| Step | What | Command | Time | Gate |
|------|------|---------|------|------|
| **0** | Binary pin | `opencode --version` + behavioral probe if needed | 5 min | Version recorded |
| **1** | Backup opencode.json | `cp opencode.json opencode.json.backup` | 1 min | Backup exists |
| **2** | Fix global model | `jq '.model = "lmstudio/qwen3-4b-thinking"' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | `jq '.model' opencode.json` = lmstudio/qwen3-4b-thinking |
| **3** | Fix instructions | `jq '.instructions = ["AGENTS.md"]' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | `jq '.instructions' opencode.json` = ["AGENTS.md"] |
| **4** | Fix compaction (V1) | `jq '.compaction = {"auto":true,"prune":true,"tail_turns":5,"preserve_recent_tokens":80000,"reserved":20000}' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | `jq '.compaction' opencode.json` has no buffer/keep.tokens |
| **5** | Fix plugin paths + add sovereign | `jq '.plugin = ["opencode-antigravity-auth@latest","opencode-sessions-explorer","file:///.../plugins/error-capture.ts","file:///.../plugins/awareness.ts","file:///.../.config/opencode/plugin/sovereign-compaction.ts"]' opencode.json > .tmp && mv .tmp opencode.json` | 2 min | `jq '.plugin[] \| select(test(".opencode/plugin/"))'` = empty |
| **6** | Add permission.skill | `jq '.permission.skill = {"research":"allow",...}' opencode.json > .tmp && mv .tmp opencode.json` | 2 min | `jq '.permission.skill \| with_entries(select(.value=="allow")) \| keys'` = 3 |
| **7** | Update kali agent | `jq '.agent.kali.model = "opencode/nemotron-3-ultra-free" \| .agent.kali.temperature = 0.3 \| .agent.kali.toolProfile = "deploy"' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | `jq '.agent.kali.model'` = nemotron |
| **8** | Update researcher agent | `jq '.agent.researcher.temperature = 0.1 \| .agent.researcher.toolProfile = "research"' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | `jq '.agent.researcher.toolProfile'` = research |
| **9** | Update maat agent | `jq '.agent.maat.temperature = 0.2 \| .agent.maat.toolProfile = "dev"' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | toolProfile = dev |
| **10** | Update lilith agent | `jq '.agent.lilith.temperature = 0.3 \| .agent.lilith.toolProfile = "run"' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | toolProfile = run |
| **11** | Update node agent | `jq '.agent.node.temperature = 0.1 \| .agent.node.steps = 20 \| .agent.node.toolProfile = "debug"' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | toolProfile = debug |
| **12** | Update verity agent | `jq '.agent.verity.model = "lmstudio/qwen3-1.7b" \| .agent.verity.temperature = 0.0 \| .agent.verity.hidden = true \| .agent.verity.permission = {"edit":"deny","bash":"deny","skill":"deny"} \| .agent.verity.toolProfile = "audit"' opencode.json > .tmp && mv .tmp opencode.json` | 1 min | mode=subagent, hidden=true |
| **13** | Set env vars | `echo 'export OPENCODE_DISABLE_AUTOCOMPACT=1' >> ~/.bashrc` | 1 min | `echo $OPENCODE_DISABLE_AUTOCOMPACT` = 1 |
| **14** | Full gate check | `opencode --version && grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md && jq '.instructions,.compaction,.model,.permission.skill' opencode.json` | 2 min | All values correct |
| **15** | E2E agent test | `opencode --agent researcher run "What model are you?"` + `opencode --agent kali run "What model are you?"` | 5 min | researcher=qwen3, kali=nemotron |
| **16** | Plugin load test | `opencode --log-level DEBUG 2>&1 \| grep sovereign-compaction` | 2 min | Loads without ENOENT |
| **17** | Commit | `git add MANDATES_CONDENSED.md opencode.json && git commit -m "ci: Phase 1 context injection"` | 2 min | Clean commit |

### Rollback (If Any Step Fails)

```bash
# Complete rollback (< 2 minutes)
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
git checkout opencode.json
rm -f MANDATES_CONDENSED.md
rm -f ~/.config/opencode/plugin/sovereign-compaction.ts
jq 'del(.permission.skill)' opencode.json > .tmp && mv .tmp opencode.json
sed -i '/OMEGA_ENTITY\|OMEGA_PHASE\|OPENCODE_DISABLE_AUTOCOMPACT/d' ~/.bashrc ~/.zshrc 2>/dev/null
```

---

## §8: Open Questions

| # | Question | Impact | Owner | Status |
|---|----------|--------|-------|--------|
| OQ-1 | **Binary pin: 1.18.19 vs 1.18.23** — spec pins 1.18.19 but live binary is 1.18.23. Must we downgrade or re-validate? | BLOCKING for compaction config | Architect | OPEN |
| OQ-2 | **Global model default affects 6 non-CI agents** — changing `model` to `lmstudio/qwen3-4b-thinking` means makali, jem, doom_guy, roc_racoon, john_carmack, grok_cli also inherit local model. Is this intended? | These agents are NOT in CI scope | Kali | OPEN |
| OQ-3 | **`small_model` key** — currently `"opencode/nemotron-3-ultra-free"`. Spec doesn't address it. Should it change? | Affects small model routing | Architect | OPEN |
| OQ-4 | **`default_agent` key** — currently `"kali"`. Spec doesn't address it. | Minor — just default TUI agent | Kali | OPEN |
| OQ-5 | **Live agent count mismatch** — opencode.json has 12 agents (makali, jem, doom_guy, roc_racoon, researcher, kali, maat, lilith, verity, node, john_carmack, grok_cli). Spec's target state only models 6. The other 6 must be preserved exactly. | Risk of accidental deletion during jq edits | Implementer | OPEN |
| OQ-6 | **`subagent_depth: 2`** — present in current config, not in spec target. Keep or remove? | Minor | Kali | OPEN |
| OQ-7 | **`opencode-antigravity-auth`** — current config uses directory path `opencode-antigravity-auth`, spec uses `opencode-antigravity-auth@latest`. Which is correct? | Plugin loading | Kali | OPEN |
| OQ-8 | **`permission` block overlap** — current config has `permission.external_directory` with extensive path rules. Adding `permission.skill` must not clobber this. Verify jq merges correctly. | Config corruption risk | Implementer | OPEN |
| OQ-9 | **Qwen3-4B context window reality** — DEV-09 corrected "8K-16K" to "base=32K native, 128K YaRN, live cap 8192". The 18K base prompt theory assumes 8K-16K usable context. If live cap is 8192, 18K base STILL overflows. Is the context cap being raised? | Token budget may be invalid | Architect | OPEN |
| OQ-10 | **`opencode-antigravity-auth` path** — current entry is a directory path (line 5: `opencode-antigravity-auth`), not a file:// URL. Spec target uses `opencode-antigravity-auth@latest`. These are different resolution mechanisms. | Plugin may not load if path changed | Kali | OPEN |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_r02_ci_injection ⬡ 2026-08-26*
*Ground truth: opencode 1.18.23, MANDATES_CONDENSED.md exists (51 lines), sovereign-compaction.ts deployed, opencode.json NOT YET UPDATED*
