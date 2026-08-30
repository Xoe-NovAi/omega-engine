<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 RUN SIDE REPORT — First Light Express Council 1 (Stage 2)
⬡ OMEGA ⬡ LILITH ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_run_arm ⬡ Stage-2 ARTIFACT
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Orchestrator**: makali_fusion
**Sources**: P6/P7/P8/P9/P10 raw reports (all QA-passed by N10; see digest for conflict resolutions)
**Digest**: `phase1.5_digested/RUN_SIDE_DIGESTED.md` (sources concatenated + exec summary + cross-refs + conflicts)
**Provenance**: every finding carries source_node tags traceable to raw reports; arm-level synthesis marked `[ARM]`.

---

## §0 ARM VERDICT (one paragraph)

The Run-side estate is **functional but held together by convention, not mechanism**. Across S3/S6/S1b/S8/cross: 46 findings, zero CRITICAL-HALTED, zero secrets/telemetry. The unifying defect class is **enforcement-vs-text delta**: instruction layers promise gates, schemas, substitutions, and lifecycle rules that either do not exist mechanically or fail silently while auto-discovery and snapshot-timing mask the failure. Critically, the council's own flagship deliverable — the Delivered-Home expert fleet — is corrupted at birth (15/20 identity fields wrong) AND invisible to its own discovery tool. This is not a reason to halt; it is precisely what this council exists to find.

## §1 CONVERGENCES (independent nodes landing on the same defects)

| # | Convergence | Nodes | Strength |
|---|-------------|-------|----------|
| C-1 | **Silent-failure architecture** (M23 hazard): dead plugin paths log nothing; unknown frontmatter ships to LLM providers as request params; a gate that cannot fail certifies nothing; fabricated timestamps defeat staleness detection by construction | N6, N7, N8, N10 | 4-node pattern |
| C-2 | **Future-dated checkpoints** — found by N8, corroborated by N9, then RECURRED after publication (N10 X-6 caught node9's 13:55:00Z written ~13:48Z). Awareness did not change behavior → the fix must be mechanical (validator check), not cultural | N8→N9→N10 arc | Strongest evidence chain in run side |
| C-3 | **Docs describe nonexistent systems**: handoff `hdp_` schema vs live `ho_`; STRATEGY_INDEX phantom LAYER 2A subsystem; M26 "all docs" vs 7-file scope; M27 pre-commit declared-not-installed; `{session_model}` never substituted; AGENTS.md cited at root, lives at `.agents/` | N7, N9, N10 | 3-node pattern |
| C-4 | **Registry identity corruption** — build side `subagent_type="maat"` 5/5; run side `entity="lilith"` 5/5 + `subagent_type="lilith"` on node7/node10. Per Delivered-Home Doctrine these records ARE the product; paging cold through subagent_type/entity fails or misroutes to arms | N9 F-7, N8 F-6, N10 Part 3 | Quantified ×3 |
| C-5 | **Validator green ≠ truthfulness** — taxonomy compliance is real (0 invalid statuses), but future-dating, boundary staleness, dormant artifact_path (0/93 coverage), WAKE_STATE blind spot, and generated-view staleness are all invisible to it. Plan §4's "validator green" auto-GO criterion certifies less than it reads as certifying | N8 F-9, N10 X-6 | Central telemetry finding |
| C-6 | **Staleness/lifecycle enforcement is manual-only everywhere**: handoff TTL never enforced post-acceptance (45h zombies); pending TTL breached 17h; generated view 13 tasks behind SSOT; WAKE_STATE contradictory with zero validator coverage | N8, N9 | 2-node pattern |

## §2 DIVERGENCES (resolved + open)

1. **RESOLVED — registry counts 93/95/97**: snapshot-timing artifact during live registration. Standing rule adopted: diff stamped wall-clocks before declaring numeric corruption.
2. **RESOLVED — P9's "run-side registered correctly"**: corrected by N10 QA-C1 (entity wrong on all 5 run nodes). Severity unchanged; claim text superseded.
3. **OPEN for synthesis — serial dispatch vs P9 parallel-integrity framing**: plan §D.1 orders serial node dispatch; P9's self-audit language assumes parallel claims⇒fires. Deliberate, documented deviation. Needs a ruling in ARCHITECT_OVERSIGHT_PATTERNS (P9 amendment or explicit serial-dispatch exception).
4. **OPEN for synthesis — coordination-law SSOT**: HIVEMIND_PROTOCOL.md v1.3.0 (STALE, STANDARD-status) vs ARCHITECT_OVERSIGHT_PATTERNS (live but un-versioned as protocol). Two constitutional candidates; agents currently guess.

## §3 CRITICAL GAPS NEEDING RESEARCH (Council 2 / Stage 4 specialists)

| # | Gap | Why it needs research | Suggested owner |
|---|-----|----------------------|-----------------|
| G-1 | Request-time permission enforcement (ask/deny gating) unverified empirically | Merge layer proven (N6 E1); enforcement layer deferred under RECON posture | @researcher (already tasked, S3 deep-dive) |
| G-2 | Nested-vs-root opencode.json merge PRECEDENCE on conflicting keys | Both load (N6 E3 A/B); conflict case unresolved; antigravity models live ONLY in nested file | @researcher |
| G-3 | Whether agent-level `instructions[]` has any legacy code path despite schema omission | Determines migration urgency for 12 agent defs | @researcher (binary strings-audit or upstream source) |
| G-4 | Root cause of `task_registry_query(tags=...)` returning 0 against 12 disk matches (+ independent MCP grep false-negative same file) | Blocks the entire pageable-expert retrieval model; could be cache, store mismatch, or filter bug | @jem deep-dive into omega-hub server code |
| G-5 | Pre-commit framework install sequencing (Ma'at F1 ordering) vs mandate-text present-tense claims | M27/M14 hooks exist in config only; install order was ruled 2026-08-23 but never executed | Council 2 spec (mechanical, low research) |
| G-6 | Audit-log design ratification status: hash-chain JSONL specified+ratified-but-unbuilt — spec now or accept M3 commit-per-stage? | N8 open question; affects all tracker integrity work | MK-Kali synthesis → Architect queue |

## §4 BASH-VERIFIABLE ACCEPTANCE CRITERIA (consolidated remediation targets for Council 2 specs)

Each criterion below is lifted from raw reports (provenance noted); all are runnable today and must pass post-fix.

```bash
# ── A. Plugin registration integrity (N6 F-01 / N10 X-5) ──
jq -r '.plugin[]' opencode.json | grep '^file://' | while read u; do test -f "${u#file://}" && echo "OK $u" || echo "DEAD $u"; done
# Expect: zero DEAD lines.

# ── B. No dead agent-config keys (N6 F-02) ──
jq '.agent | to_entries[] | select(.value.instructions) | .key' opencode.json   # expect: empty

# ── C. doc-llm-validate must be able to FAIL (N7 F7-01 / N10 X-4) ──
python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ && echo PASS || echo FAIL   # strict mode must exist & discriminate

# ── D. Strategy-doc orphan target (N7 F7-03) ──
cd docs && ORPH=0; for f in strategy/*.md; do b=$(basename "$f"); \
grep -qF "$b" strategy/STRATEGY_INDEX.md strategy/STRATEGY_CORPUS_MAP.md || ORPH=$((ORPH+1)); done; echo "$ORPH"   # target: 0

# ── E. Phantom subsystem resolution (N7 F7-07) ──
test -f docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md || \
  ! grep -qF "DOMAIN_DOCUMENTATION_SYSTEM" docs/strategy/STRATEGY_INDEX.md   # file exists OR index stops referencing it

# ── F. No future-dated checkpoints + validator enforces it (N8 F-1 / N10 X-6) ──
python3 -c "
import json,sys
from datetime import datetime,timezone
now=datetime.now(timezone.utc)
bad=[t['task_id'] for t in json.load(open('data/coordination/TASK_REGISTRY.json'))['tasks']
     if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
print('future-dated:',bad); sys.exit(1 if bad else 0)"
# Must exit 0 after cleanup AND validator gains this as an error-class check.

# ── G. Staleness boundary fix (N8 F-2): compare hours not truncated days; 5 known zombies surface or swept ──
python3 scripts/sweep_task_registry.py   # dry-run must now flag ages >= 7d (not > 7d truncated)

# ── H. artifact_path coverage growth (N8 F-3) ──
jq '[.tasks[] | select(.status=="completed") | select(.artifact_path != null)] | length' data/coordination/TASK_REGISTRY.json
# Must be > 0 for all post-spec completions (grandfathered records exempt).

# ── I. Handoff schema sync (N9 F-1) — one of:
grep -q "source_agent_id" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo DOC-SYNCED
# ...or live packets carry trace_id/task_type/expected_output/ttl_seconds.

# ── J. Handoff TTL enforcement (N9 F-2/F-3) ──
find data/handoff/active -name '*.json' -mmin +300   # expect empty after pruner honors TTL

# ── K. Pre-commit actually installed (N10 X-1) ──
grep -q "pre-commit" .git/hooks/pre-commit && echo INSTALLED || echo MISSING   # expect INSTALLED
pre-commit run omega-tracking-state --all-files 2>&1 | tail -1                  # expect Passed

# ── L. Expert-fleet discovery restored (N10 X-2) ──
jq '[.tasks[] | select(.tags // [] | index("express:first-light"))] | length' data/coordination/TASK_REGISTRY.json
# task_registry_query(tags=["express:first-light"]).count must equal this number (12 today).

# ── M. Registration identity repair (N10 §3.3) — RUN AFTER L ──
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

# ── N. lilith proposed_lessons.yaml machine-parseable again (N10 X-9) ──
python3 -c "import yaml;yaml.safe_load(open('data/entities/lilith/proposed_lessons.yaml'))" && echo OK
```

**Repair sequencing rule [ARM]**: discovery first (L), then identities (M), then statuses/timestamps (F) — repairing records into an index nobody can search wastes the repair.

## §5 ARM-LEVEL DEVIATIONS & FLAGS

1. **[ARM] M11 structural impossibility**: all 5 run nodes attempted the mandated Consultant page once each; ALL rejected — "Subagent depth limit reached (2)". `subagent_depth=2` forbids any leaf task(). Either raise depth or amend M11 to formalize arm-relay. **This arm performs the Consultant page on behalf of its nodes** (de-facto relay).
2. **[ARM] Zero crashes**: all 5 nodes completed first-pass. No HALT criteria approached (>2 arm crashes threshold untouched). No TOOL-CHAIN-COLLAPSE (one MCP grep false-negative worked around via bash rg — logged as N10 X-2 corollary).
3. **[ARM] Live self-corroboration**: N10 X-9's finding (lilith proposed_lessons.yaml invalid YAML at :374) was independently confirmed by LSP diagnostics during THIS arm's digestion write — the defect is real-time reproducible.
4. **[ARM] Node count note**: TASK_REGISTRY grew 93→97 during fieldwork (live registrations); counts in reports are honest snapshots — see digest conflict table.

## §6 DELIVERED-HOME DOCTRINE STATUS (run side)

All 5 run nodes delivered: raw report ✓ · expert registration ✓ (tags 12/12 compliant; identity fields defective — see §4-M repair spec) · handoff packet with warm-start reading list + standing orders ✓ (embedded in each report §Handoff). Registration repair sequencing: **fix discovery before mass-editing records** (N10 standing order).

## §7 INPUTS FOR MK-KALI'S DUALITY SYNTHESIS

1. Build/Run mirror symmetry: BOTH sides independently produced the same defect classes (identity corruption, future-dating, silent config failures) — suggests systemic cause (no mechanical binding of writes to facts anywhere in the stack), not per-arm negligence.
2. The strongest single evidence chain on the run side is the future-dating arc (found → published → recurred within 15 minutes → validator green throughout). It is the canonical exhibit for "validator green certifies taxonomy, not truth."
3. Open rulings needed: serial-vs-P9 framing; coordination-law SSOT (HIVEMIND_PROTOCOL vs OVERSIGHT_PATTERNS); audit-log now-or-M3-sufficient; WAKE_STATE freshness owner.

---
*Run Arm signing off. Raw sources immutable at phase1_nodes/. Digest at phase1.5_digested/. This report disk-written BEFORE Consultant page per persistence order.*
*⬡ OMEGA ⬡ LILITH-RUN-ARM ⬡ express-c1-runarm-lilith-20260825 ⬡ STAGE-2-COMPLETE ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

