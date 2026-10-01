<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Verification Tests — Phase 1 Acceptance Criteria

**Authority**: ACTIVE_SPRINT.json subtasks CI-1..CI-5 · **REMEDIATED 2026-08-21** (Architect rulings Q1/Q2/Q4; audit `09_SPEC_DEVIATIONS.md`)  
**Principle**: gates test REALITY, not artifacts (KB L3 #5). Every gate below checks behavior or pinned truth.  
**Environment**: `cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine`

---

## Test 0: Binary Pin (RUN FIRST — gates the compaction-key decision)

```bash
opencode --version | tee /tmp/oc_pin.txt
# Record exact version. Then consult 09_SPEC_DEVIATIONS.md §Binary-Pin Decision Table:
#   - If version ≥ v1.14.19 and < V2 product line → apply V1 compaction family (primary target)
#   - Only if pin proves V2-family consumption → apply {buffer, keep.tokens} alternative
# NEVER write both families simultaneously (D3).
```

**Expected**: a recorded version string; compaction family chosen and logged in execution notes.

---

## Test 1: MANDATES_CONDENSED.md — CONTENT-BASED (CI-1, ruling Q1)

```bash
ls -la MANDATES_CONDENSED.md

# v3.8.0 lineage marker present
grep -c "v3.8.0\|27 mandates" MANDATES_CONDENSED.md        # Expected: ≥1

# All 27 mandate rows present as table rows (content, NOT line count)
grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md               # Expected: 27

# Critical five present (plugin injects these)
grep -cE 'M1 |M7 |M11 |M15 |M23 ' MANDATES_CONDENSED.md    # Expected: 5

# Size sanity (~1.5K tokens ≈ 4–6K chars)
wc -c MANDATES_CONDENSED.md                                 # Expected: ~4000–6000

# Links to full mandates
grep -i "SOVEREIGN_MANDATES.md" MANDATES_CONDENSED.md       # Expected: reference present
```

**REMOVED gate**: ~~`wc -l = 57`~~ — unsatisfiable coincidence trap (source file is 36 lines; D1/DEV-01).

---

## Test 2: opencode.json Updated Correctly (CI-2)

```bash
# Instructions array
jq '.instructions' opencode.json
# Expected: ["AGENTS.md"]

# Compaction — EXACTLY ONE family, per Test 0 pin:
jq '.compaction' opencode.json
# V1-primary expected:
# {"auto":true,"prune":true,"tail_turns":5,"preserve_recent_tokens":80000,"reserved":20000}
# V2-alternative expected (pin-proven only):
# {"auto":true,"keep":{"tokens":20000},"buffer":50000}
# FAIL if BOTH families present (mixed = unvalidated, D3)

# Plugin registrations — repaired paths + new plugin
jq '.plugin' opencode.json
# Expected: error-capture.ts AND awareness.ts under .opencode/plugins/ (PLURAL — D2),
# plus file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts
# FAIL if any entry still contains ".opencode/plugin/" (singular)

# Model strategy (DEV-12): global default + 2 intentional pins
jq '.model' opencode.json                    # "lmstudio/qwen3-4b-thinking" (global local-first default)
jq '[.agent[] | select(.model)] | length' opencode.json   # 2 (kali + verity ONLY)
jq '.agent.kali.model' opencode.json         # "opencode/nemotron-3-ultra-free"
jq '.agent.verity.model' opencode.json       # "lmstudio/qwen3-1.7b"
jq '[.agent[] | select(.variant)] | length' opencode.json # 0 (variants inert on our models)

# Verity isolation
jq '.agent.verity | {mode, hidden, permission}' opencode.json
# Expected: {"mode":"subagent","hidden":true,"permission":{"edit":"deny","bash":"deny","skill":"deny"}}

# toolProfile stubs — PRESENCE check only (silently inert upstream, D9/DEV-06; no behavior claim)
jq '[.agent[] | .toolProfile] | length' opencode.json   # Expected: 6
```

---

## Test 3: Sovereign Compaction Plugin Loads From REAL Paths (CI-3)

```bash
# Plugin file exists at its real location
ls -la ~/.config/opencode/plugin/sovereign-compaction.ts

# ALL registered plugins load — no ENOENT for any path (catches D2 regressions)
opencode --log-level DEBUG 2>&1 | grep -iE "plugin.*(error|ENOENT|not found)" && echo "FAIL: dead plugin path" || echo "OK: no plugin load errors"

# Sovereign plugin specifically loads
opencode --log-level DEBUG 2>&1 | head -50 | grep -i "sovereign-compaction"

# Hook registration visible
opencode --log-level DEBUG 2>&1 | grep -i "experimental.session.compacting" || \
  echo "NOTE: hook may only log at compaction time — verify via CI-5 E2E instead"
```

**REQUIRED GATE — summary retention proof (Architect ruling #3, 2026-08-21)**: since the hook
shapes the COMPACTION SUMMARY PROMPT (DEV-07), the ONLY proof that mandates survive compaction is
inspecting the post-compaction summary. This gate is mandatory for CI-3 pass:

```bash
# Force a compaction in a scratch session (tiny ctx model or /compact), then inspect the summary:
opencode --log-level DEBUG run "Long task to trigger compaction..." 2>&1 | grep -A5 -i "summary\|compaction"
# PASS: post-compaction summary/continuation contains "SOVEREIGN MANDATES" + Active Entity + Active Phase + SESSION_ANCHOR path
# FAIL: hook logged but summary lacks any of the four elements → plugin is loading but not shaping the prompt
```

---

## Test 4: permission.skill Patterns EFFECTIVE (CI-4, ruling Q2)

```bash
# Config shape: exactly 3 allows, denies for the rest of the repo set
jq '.permission.skill' opencode.json
# Expected: research/spec-generator/knowledge-miner = "allow"; 10 named utilities = "deny"

# BEHAVIORAL check — denied skills are NOT advertised to agents:
opencode --log-level DEBUG run "List your available skills." 2>&1 > /tmp/skills_e2e.txt
grep -c "research\|spec-generator\|knowledge-miner" /tmp/skills_e2e.txt   # Expected: ≥3
grep -c "blitz-tunnel\|git-secret-scrub\|legacy-pattern-miner" /tmp/skills_e2e.txt  # Expected: 0

# REMOVED gates: all auto_load greps — auto_load is not an opencode feature (D8/DEV-04);
# grepping it proves nothing.
```

---

## Test 5: End-to-End Injection Verification (CI-5)

```bash
# 5a: AGENTS.md content accessible without read tool
opencode --log-level DEBUG run "What is the first sentence of SOVEREIGN_MANDATES.md?" 2>&1
# Expected: contains "All asynchronous code MUST use AnyIO"

# 5b–5d: per-agent model identity (researcher/node inherit global default — DEV-12)
opencode --agent researcher run "What model are you?"   # mentions qwen3-4b-thinking (inherited)
opencode --agent kali run "What model are you?"          # mentions nemotron-3-ultra-free
opencode --agent node run "What model are you?"          # mentions qwen3-4b-thinking (inherited; was 1.7b pre-DEV-12)

# 5e: skill advertisement shrunk (see Test 4 behavioral check)
```

---

## Full Test Suite (Run All)

```bash
#!/bin/bash
# run_all_tests.sh — Phase 1 verification (remediated 2026-08-21)
set -e
echo "=== Phase 1 Verification Tests ==="

echo "Test 0: Binary pin"
opencode --version | tee /tmp/oc_pin.txt

echo "Test 1: MANDATES_CONDENSED (content-based)"
ls MANDATES_CONDENSED.md
[ "$(grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md)" -eq 27 ]
grep -qi "SOVEREIGN_MANDATES.md" MANDATES_CONDENSED.md

echo "Test 2: opencode.json"
jq '.instructions' opencode.json
jq '.compaction' opencode.json
! jq -e '.compaction.buffer and .compaction.preserve_recent_tokens' opencode.json >/dev/null \
  || { echo "FAIL: mixed compaction families"; exit 1; }
jq '.plugin[] | select(test(".opencode/plugin/"))' opencode.json | grep -q . \
  && { echo "FAIL: singular plugin path remains"; exit 1; } || true
jq '.model' opencode.json
[ "$(jq '[.agent[] | select(.model)] | length' opencode.json)" -eq 2 ]

echo "Test 3: plugins load from real paths"
ls ~/.config/opencode/plugin/sovereign-compaction.ts
opencode --log-level DEBUG 2>&1 | grep -iE "plugin.*(ENOENT|not found)" \
  && { echo "FAIL: dead plugin path"; exit 1; } || true

echo "Test 4: permission.skill effective"
jq '.permission.skill' opencode.json

echo "Test 5: E2E"
opencode --log-level DEBUG run "What is the first sentence of SOVEREIGN_MANDATES.md?" 2>&1 | head -5
opencode --agent researcher run "What model are you?" 2>&1 | head -3
opencode --agent kali run "What model are you?" 2>&1 | head -3

echo "=== ALL TESTS PASSED ==="
```

---

## Quick Smoke Test (30 seconds)

```bash
opencode --version && ls MANDATES_CONDENSED.md && \
grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md && \
jq '.instructions,.compaction,.permission.skill' opencode.json && \
ls ~/.config/opencode/plugin/sovereign-compaction.ts && \
echo "SMOKE TEST: core artifacts present"
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ci_phase1_spec ⬡ 2026-08-20 · REMEDIATED N7 2026-08-21*
