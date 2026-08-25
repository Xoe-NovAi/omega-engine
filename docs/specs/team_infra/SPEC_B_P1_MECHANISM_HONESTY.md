# SPEC-B · P1 MECHANISM HONESTY — Council 2 Build Arm, Node 2 (domain: specb)
⬡ OMEGA ⬡ MAAT/node2 ⬡ trc_c2_specb ⬡ DRAFT
**SESSION_ID**: `20260825-094633-first-light-c2` | **Date**: 2026-08-25 | **Status**: DRAFT-COUNCIL2-PREP
**Authority**: SOVEREIGN_DECREE.md (20260825-094633-first-light) Art. V, VIII, X (P1 list), XII; SYNTHESIS_ARM_REPORT §6 gates
**Bright line**: this spec DRAFTS remediation only. ZERO edits to existing production files are authorized by this document. All changes herein require separate single-writer execution with their own review.
**Provenance rule**: every file:line anchor below was re-verified by node2 in this session (2026-08-25). Mismatches vs upstream claims are flagged inline and logged in `node2_notes.md`.

---

## §0 SCOPE SUMMARY

Five P1 work items from Decree Art. X ("P1 mechanism honesty"), one spec, sequenced per Art. V:

| # | Work item | Decree hook | Gates | Est. hours |
|---|-----------|-------------|-------|-----------|
| WI-1 | Plugin path fixes (`opencode.json` `.plugin[]`) | Art. VIII.1 | G1 | 1.5 |
| WI-2 | Agent-level `instructions[]` → `prompt:{file:}` migration | Art. VIII.4 | G10 | 3.0 |
| WI-3 | Provider-order / M7 alignment + credentialed-fabric honesty | Art. VIII.5 | G3, G4 | 2.0 |
| WI-4 | doc-gate `--strict` code change | Art. III | G22 | 4.0 |
| WI-5 | Discovery fix → staged identity-repair application (Art. V sequence) | Art. V | G20 → G21 | 6.0 |

**Total**: ~16.5h including shared validator deliverable (§ VALIDATOR-FIRST CLAUSE).

---

## WI-1 · PLUGIN PATH FIXES (G1)

### (a) Problem statement
Root `opencode.json` `.plugin[]` registers two plugins at dead singular-dir paths:
`file:///…/omega-engine/.opencode/plugin/error-capture.ts` and `…/.opencode/plugin/awareness.ts`.
The directory `.opencode/plugin/` **does not exist**; the live dir is `.opencode/plugins/`
(contains awareness.ts, error-capture.ts, silent-stall-sensor.ts, test-event.js.DISABLED).
Researcher GAP-1 twin-canary verdict: OpenCode v1.18.23 auto-loads from BOTH dirs (+ user-level
`~/.config/opencode/plugin/`). Therefore the tools are LIVE via plural-dir discovery and the
defect is **HIGH lying-config** (the registration list is what lies), NOT CRITICAL dead-tools.
T-8 residue: if auto-discovery ever regresses to neither-dir loading, severity automatically
reverts to CRITICAL — the fix must land before any such regression.

### (b) Evidence links
- Decree: SOVEREIGN_DECREE.md Art. VIII.1, Art. X P1, §3 T-8 residue.
- Research: `data/council/20260825-094633-first-light/phase4_research/RESEARCHER_EMPIRICAL_GAPS_1_4.md` §GAP-1 (probe transcript, fixtures preserved at `/tmp/opencode/gap1/`).
- Node reports: `phase1_nodes/P1_report.md` F-01 (original finding + nuance) · `phase1_nodes/P6_report.md` F-01/E4 (silent-failure mode) · `phase1_nodes/P10_report.md` X-5 (independent confirmation).
- **node2-verified anchors (this session)**:
  - `opencode.json` `.plugin[]` entries 3–4 = the two dead `file://…/.opencode/plugin/*.ts` paths ✓
  - `ls -d .opencode/plugin` → "No such file or directory" ✓
  - `ls .opencode/plugins/` → awareness.ts error-capture.ts silent-stall-sensor.ts test-event.js.DISABLED ✓

### (c) Proposed change (diff-level)
```diff
--- a/opencode.json
+++ b/opencode.json
@@ .plugin[]
-    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts",
-    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/awareness.ts"
+    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/error-capture.ts",
+    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/awareness.ts"
```
Equivalent mechanical form (N1 F-01 AC): `sed -i 's#\.opencode/plugin/#.opencode/plugins/#g' opencode.json`.
Alternative accepted fix: DROP both entries entirely — plural-dir auto-discovery already loads
them (researcher GAP-1). Decision default: **correct the paths** (registration list should tell
the truth about mechanism even where discovery is redundant). Do NOT register
`silent-stall-sensor.ts` as part of this item (separate hygiene decision; it already works).
Note for executor: nested `.opencode/opencode.json` overrides root on conflicting keys
(GAP-3 verdict); confirm no plugin key exists in the nested file before editing root.

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6 / decree §4)
```bash
# ── G1. Plugin registrations resolve (Art. VIII; N1 F-01 / N6 F-01) ──
jq -r '.plugin[]' opencode.json | grep '^file://' | sed 's#file://##' | while read f; do test -f "$f" || echo "MISSING $f"; done   # expect: no output
```
Supplementary liveness check (P6 F-01 AC): `opencode agent list 2>&1 | grep -c 'Plugin initialized'` → ≥ 4 post-fix.

### (e) Risk assessment
LOW. Path correction only; discovery behavior unchanged (both dirs load either way). Only risk:
typo introduces a NEW dead path — mitigated by G1 running pre-commit via validator (§VFC).

### (f) Effort estimate
0.5h edit + 1.0h validator function & test share = **1.5h**.

---

## WI-2 · AGENT-LEVEL `instructions[]` → `prompt:{file:}` MIGRATION (G10)

### (a) Problem statement
12 of ~13 agent defs in root `opencode.json` carry an agent-level `instructions[]` key that is
NOT in the OpenCode v1.18.23 `AgentConfig` schema. Researcher GAP-4 (canary-proven +
binary strings-audit) established: **NO legacy injection path exists** — the unknown-key handler
(`uH`) sweeps `instructions[]` into `options`, which merge into LLM provider request params
(`d=Rs(Rs(Rs(r, e.model.options), e.agent.options), a)`). Consequence: every dispatch of these
agents ships an unrequested array upstream — a **data-exposure class defect** (config-litter
crossing the provider boundary; provider-dependent ignore/warn/reject behavior). Decree Art.
VIII.4 sets migration urgency **HIGH**. Note calibration delta: researcher memo rated MED
("correctness hygiene"); decree fusion re-scaled by impact — decree governs.

### (b) Evidence links
- Decree: SOVEREIGN_DECREE.md Art. VIII.4, Art. X P1.
- Research: `phase4_research/RESEARCHER_EMPIRICAL_GAPS_1_4.md` §GAP-4 (AgentConfig schema verbatim, canary transcript, binary extraction; fixtures `/tmp/opencode/gap4/`).
- Node reports: `phase1_nodes/P6_report.md` F-02/F-03 (schema absence, masking hazard, grok_cli double-registration) · `phase1_nodes/P3_report.md` F-03 (dead plan.md/grok_cli.md paths).
- **node2-verified anchors**: `jq '.agent | to_entries[] | select(.value.instructions) | .key' opencode.json` → exactly 12: makali, jem, doom_guy, roc_racoon, researcher, kali, maat, lilith, verity, node, john_carmack, grok_cli ✓. Root `instructions[]` at opencode.json line 27 ✓ (includes `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` — remediated under G5/WI-3 scope note below). Dead targets confirmed: `.opencode/agents/plan.md` MISSING; `.opencode/agents/grok_cli.md` MISSING (moved to `.opencode/agents/archive/grok_cli.md`) ✓.

### (c) Proposed change — migration table (all 12 defs)
Schema-valid target shape per vendor docs: `"prompt": { "file": "<path>" }`.

| # | Agent | Current `instructions[]` | Target `prompt:{file:}` | Note |
|---|-------|--------------------------|--------------------------|------|
| 1 | makali | `.opencode/agents/plan.md` (**DEAD**) | `{".opencode/agents/makali.md"}` | plan.md never existed; makali survives today only via markdown loader on makali.md. Point at the real file. |
| 2 | jem | `.opencode/agents/jem.md` | same path | direct migrate |
| 3 | doom_guy | `.opencode/agents/doom_guy.md` ; `CREDITS.md` | `{".opencode/agents/doom_guy.md"}` | drop CREDITS.md entry — CREDITS.md is ALREADY injected fleet-wide by root `instructions[]` (line 27 block); per-agent duplication is redundant payload |
| 4 | roc_racoon | `.opencode/agents/roc_racoon.md` | same path | direct migrate |
| 5 | researcher | `.opencode/agents/researcher.md` | same path | direct migrate |
| 6 | kali | `.opencode/agents/kali.md` | same path | direct migrate |
| 7 | maat | `.opencode/agents/maat.md` | same path | direct migrate |
| 8 | lilith | `.opencode/agents/lilith.md` | same path | direct migrate |
| 9 | verity | `.opencode/agents/verity.md` | same path | direct migrate |
| 10 | node | `.opencode/agents/node.md` | same path | direct migrate |
| 11 | john_carmack | `.opencode/agents/john_carmack.md` ; `CREDITS.md` | `{".opencode/agents/john_carmack.md"}` | drop CREDITS.md (same rationale as #3) |
| 12 | grok_cli | `.opencode/agents/grok_cli.md` (**DEAD** — archived) | DELETE the JSON def OR restore file | P6 F-03: grok_cli currently registers with EMPTY prompt body AND archive/grok_cli also registers (double registration). Default: delete JSON def; keep archived md as the single registration. Requires owner sign-off (agent-fleet decision, M10 adjacent). |

Diff pattern (per def):
```diff
-      "instructions": [".opencode/agents/jem.md"],
+      "prompt": { "file": ".opencode/agents/jem.md" },
```
Executor notes: (i) after migration, verify no behavioral regression via `opencode agent list`
(permission arrays unchanged); (ii) this item does NOT touch scribe.md frontmatter passthrough
(P6 F-04 — separate ticket); (iii) root-level `instructions[]` (line 27) is LIVE and stays —
only its `docs/archive/` entry is removed under G5.

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6)
```bash
# ── G10. Dead agent instruction/config paths resolved (Art. VIII; N3 F-03 / N6 F-02) ──
for f in $(jq -r '.agent[].instructions[]?' opencode.json); do test -e "$f" || echo "DEAD: $f"; done   # expect: no output
jq '.agent | to_entries[] | select(.value.instructions) | .key' opencode.json                          # expect: empty after prompt:{file:} migration
```

### (e) Risk assessment
MEDIUM. Masking hazard (P6 F-02): today the markdown loader injects the same bodies anyway, so
migration should be behavior-neutral — but makali (#1) and grok_cli (#12) involve DEAD paths
where intent diverges from reality; those two need explicit decisions, not blind migration.
Risk of dropping CREDITS.md entries: none identified (global injection covers it) — verify with
one diff of a spawned agent's "Instructions from:" sections pre/post.

### (f) Effort estimate
2.0h (10 mechanical migrations + table verification) + 1.0h validator/test share = **3.0h**
(excludes grok_cli/makali owner-decision wait; defaults specified above keep it unblocked).

---

## WI-3 · PROVIDER-ORDER / M7 ALIGNMENT + CREDENTIALED-FABRIC HONESTY (G3, G4)

### (a) Problem statement
Provider order is stated FOUR ways: M7 text (`SOVEREIGN_MANDATES.md:55`: chain ending Copilot),
Ark D-355 (Antigravity→Google→OCZ→OpenRouter), providers.yaml fallback_chain
(openrouter=5 BEFORE opencode-zen=6 — contradicting Ark), and ORACLE_STACK.md (sixth variant).
An agent obeying constitution text routes differently than the engine does. Additionally,
credentialed reality ≠ configured fabric: google/anthropic/xai/antigravity enabled with
`env:` keys that are UNSET (P1 F-04 probe) — sovereignty claims must be stated against the
REAL fabric until keys exist.

### (b) Evidence links
- Decree: SOVEREIGN_DECREE.md Art. VIII.5, Art. X P1; Ark D-355 (SOVEREIGN_ARK_BLUEPRINT.md §7/§8).
- Node reports: `phase1_nodes/P1_report.md` F-03/F-04/F-05 · `phase2_arms/BUILD_SIDE_REPORT.md` B-C4.
- **node2-verified anchors**: providers.yaml fallback_chain live priorities: native-gguf 0, lmster 1, ollama 2(disabled), antigravity 3, google 4, openrouter 5, opencode-zen 6, cline 7, anthropic 8, xai 9, mock 10(disabled); duplicate priority 4 (google-compat) noted ✓. `SOVEREIGN_MANDATES.md:55` carries the stale literal chain ✓. Root `instructions[]` includes `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` (the G5 archived-roadmap injection) ✓.

### (c) Proposed change
1. **providers.yaml**: swap so OCZ precedes OpenRouter per D-355:
```diff
--- a/config/providers.yaml  (inference.fallback_chain)
-    - provider: openrouter   … priority: 5
-    - provider: opencode-zen … priority: 6
+    - provider: opencode-zen … priority: 5
+    - provider: openrouter   … priority: 6
```
Also record (follow-up ticket, not this PR): duplicate priority 4 google/google-compat.
2. **SOVEREIGN_MANDATES.md M7 Pattern line (:55)** amend to canonical chain, pairwise-bound with the config change (Art. II.2):
```diff
-- **Pattern**: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → Copilot(6).
+- **Pattern**: local: native-gguf(0) → lmster(1) → Ollama(2); cloud: antigravity(3) → Google(4) → OpenCode Zen(5) → OpenRouter(6). Canonical order = Ark D-355; providers.yaml is executable truth.
```
3. **Credentialed-fabric honesty statement** (lands in M7 Enforcement note + OMEGA_ENGINE state doc at execution time): sovereignty/failover claims stated against REAL fabric = native-gguf + lmster + opencode-zen + openrouter until GOOGLE_API_KEY/ANTIGRAVITY_API_KEY/etc. exist; uncredentialed providers stay listed but marked unkeyed (or `enabled: false` per Architect choice — WAKE Q-owned, not this spec's call).
4. **G5 companion (in-scope because same file, one commit)**: remove `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` from root `instructions[]` (Decree Art. VIII.6).

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6)
```bash
# ── G3. Provider chain matches Ark D-355 (Art. VIII; N1 F-03) ──
python3 -c "
import yaml; c=yaml.safe_load(open('config/providers.yaml'))
p={e['provider']:e['priority'] for e in c['inference']['fallback_chain']}
assert p['opencode-zen'] < p['openrouter'], p"

# ── G4. Enabled providers have resolvable keys (Art. VIII; N1 F-04) ──
python3 -c "
import yaml, os
c=yaml.safe_load(open('config/providers.yaml'))
bad=[n for n,p in c['inference']['providers'].items() if p.get('enabled') and str(p.get('api_key','')).startswith('env:') and str(p['api_key']).split(':',1)[1] not in os.environ]
print('DEAD:',bad); assert not bad"

# ── G5. No archived docs injected as instructions (Art. VIII; N1 F-05) ──
test "$(jq -r '.instructions[]' opencode.json | grep -c '^docs/archive/')" = 0
```
**Execution caveat (record honestly)**: G4 asserts zero dead enabled providers. Until keys are
provisioned or providers disabled (Architect action outside this spec), G4 will FAIL. Per
decree Art. VIII.5 the honest interim state is the credentialed-fabric STATEMENT; G4 becomes
the hard gate the moment keys land or `enabled:false` flips. Do not fake-pass G4.

### (e) Risk assessment
MEDIUM. Routing-order swap changes live failover behavior (OCZ before OpenRouter) — desired per
D-355 but must be smoke-tested against real endpoints. M7 text edit is pairwise-bound: landing
text without config (or vice versa) fails review (Art. II.2). G5 removal is LOW risk (archived
roadmap contradicts live Ark; removal reduces per-session contradiction).

### (f) Effort estimate
1.5h (swap + text patch + statement + smoke) + 0.5h validator share = **2.0h**.

---

## WI-4 · DOC-GATE `--strict` CODE CHANGE (G22)

### (a) Problem statement
`scripts/validate_llm_docs.py` has NO strict mode (verity confirmed; node2 re-verified: zero
occurrences of "strict" in the file; argparse surface = `--frontmatter-schema`, `--token-budget`,
`--answer-first-check`, `--code-block-check`, `--dependency-graph-check`, positional paths — no
`--strict`). The gate exits 0 through warnings, making `doc-llm-validate` a gate that cannot
fail (~60 warnings tolerated per N7 F7-01; temple-grade T2 inherits the rubber stamp). A gate
that cannot fail is itself a claim-outliving-mechanism (C-A class).

### (b) Evidence links
- Decree: SOVEREIGN_DECREE.md Art. III ("code change required"), Art. X P1, §4 G22.
- Node reports: `phase1_nodes/P7_report.md` F7-01 (via SYNTHESIS §1 C-A row + X-4 corroboration in P10) — N7 measured 7-of-1,533-doc coverage and always-green exit.
- **node2-verified anchors**: `grep -c 'strict' scripts/validate_llm_docs.py` → 0 ✓; `sed -n '201,209p'` shows full argparse surface without --strict ✓.

### (c) Proposed change (code-level sketch — implementation lands in execution phase)
```python
# scripts/validate_llm_docs.py — main() additions
parser.add_argument("--strict", action="store_true",
                    help="Exit non-zero on ANY warning (not just errors)")
# ...after result aggregation:
if args.strict and total_warnings > 0:
    print(f"STRICT FAIL: {total_warnings} warning(s)", file=sys.stderr)
    sys.exit(1)
```
Semantics: default behavior unchanged (warn-only, backward compatible); `--strict` converts
warnings to failures. Makefile gains a strict invocation target (e.g. `doc-llm-validate-strict`)
but does NOT flip CI default in this item — scope expansion (7 docs → corpus) is N7 F7-01's
separate path; this item only makes failure POSSIBLE (G22 wording: "strict mode must
discriminate"). Pairwise binding: the Makefile/text reference to strict mode lands in the SAME
PR as the code (no promised-but-absent mechanism).

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6)
```bash
# ── G22. doc-llm-validate can FAIL (Art. III; N7 F7-01) ──
python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ >/dev/null 2>&1; echo "strict-exit=$?"   # strict mode must discriminate (exit ≠ always 0)
```
Discrimination proof requires BOTH polarities in tests: known-clean fixture → exit 0;
known-warning fixture → exit 1 under `--strict`, exit 0 without flag.

### (e) Risk assessment
LOW-MEDIUM. Backward-compatible by default; risk is scope creep (being asked to fix all warnings
now) — explicitly out of scope. If current `docs/sprints/current/` content fails strict, that is
a TRUE POSITIVE to be triaged, not a reason to soften the gate.

### (f) Effort estimate
3.0h (argparse + aggregation + fixtures + tests) + 1.0h validator/test share = **4.0h**.

---

## WI-5 · DISCOVERY FIX → STAGED IDENTITY-REPAIR APPLICATION (G20 BEFORE G21)

### (a) Problem statement
The Delivered-Home expert fleet is unreachable cold through 2 of 3 retrieval paths (P10):
1. **Defect 5A (CODE)**: `task_registry_query()` status-filter bug — when `status` omitted
   (default None), guard `None != "all"` is True → filter `t["status"] == None` matches nothing.
   Any default query returns 0 rows regardless of tags/entity/type. No workaround: Literal type
   at :100 excludes `'all'`. This blocks Art. V mass identity repair.
2. **Defect 5B (CONFIG/tooling)**: `.gitignore:109` pattern `data/coordination/*` makes ripgrep
   (and the grep MCP tool wrapping it) blind to coordination SSOTs regardless of git tracking.
3. With discovery broken, applying corrected registrations would write records into an index
   nobody can search — hence **Art. V SEQUENCE IS LOAD-BEARING**: fix discovery FIRST (G20),
   THEN apply payloads (single writer), THEN verify retrieval ≥10 (G21 runs ONLY after G20 passes).
4. Root-cause prevention: future dispatch packets must specify exact registration field values
   (packet-template precision rule — Ruling D; 15/20 corrupted fields traced to unspecified packets).

### (b) Evidence links
- Decree: SOVEREIGN_DECREE.md Art. V (full sequence), Art. X P1, §4 G20/G21, §5 Tracker Directives 1.
- Research: `phase4_research/JEM_DEEP_DIVE_GAPS_5_7.md` GAP-5 Defect 5A/5B (live repro + verification appendix).
- Node reports: `phase1_nodes/P10_report.md` X-2 + Part 3 (15/20 identity matrix, repair script §3.3) · `phase2_arms/BUILD_SIDE_REPORT.md` BG-4.
- Staged payloads: `data/council/20260825-094633-first-light/phase6_integration/registration_payloads.json` — node2 verified present; top-level keys `canonical` (subagent_type=node<N>, entity=node<N>, 4-tag set), `tasks[]` (10 corrected records), `gated_on: "GAP-5 discovery fix (task_registry.py:134 + .gitignore:109)"` ✓.
- **node2-verified anchors (mismatch check vs JEM)**:
  - `task_registry.py:134-135` contains EXACTLY the quoted two-line bug ✓ (JEM cited :134-135 — MATCH, no drift).
  - `task_registry.py:100` Literal excludes 'all' ✓ (MATCH).
  - `.gitignore:109` = `data/coordination/*` ✓ (MATCH; sed window 105-112 confirms exact line number).

### (c) Proposed change
**Step 1 — discovery fix (precondition, ~1.5h):**
```diff
--- a/mcp_servers/omega_hub/hub_tools/task_registry.py
@@ line 134
-    if status != "all":
+    if status is not None:
         tasks = [t for t in tasks if t["status"] == status]
```
(JEM minimal fix; optional extension adding 'all' to the Literal deferred — not needed for G20.)
Plus unit tests: query-with-no-status returns tagged rows; each Literal status filters correctly.
**Step 2 — ripgrep blindness (~0.5h):** append to `.gitignore` coordination section:
```diff
+!data/coordination/*.json
```
(option 1 of JEM's two; standing-rule option 2 recorded in dispatch-packet template as belt-and-braces).
**Step 3 — staged identity repair (single writer ONLY, ~2h):** apply
`registration_payloads.json` tasks[] corrections (subagent_type/entity per canonical block,
preserve existing 4-tag sets) to `data/coordination/TASK_REGISTRY.json` via the MCP writer —
AFTER Step 1's own atomicity fix lands if available (G6 territory, owned by SPEC-A; this spec
does not duplicate it but flags the lost-update window: apply during quiescence, verify counts
before/after).
**Step 4 — packet-template precision rule (~1h):** future dispatch packets MUST embed exact
field values (`subagent_type`, `entity`, full tag list) — add template block to dispatch
protocol at execution time (text patch paired with this spec's validator check).
**Step 5 — retrieval verification:** ≥10 successful retrievals via the repaired tool before
Delivered-Home is declared complete (by-tag, by-entity, by-subagent_type, by-task_id paths).

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6; ORDER ENFORCED)
```bash
# ── G20. Expert-fleet discovery restored BEFORE identity repair (Art. V; N10 X-2) ──
omega_task_registry_query_tagcount() { :; }   # tool-side; bash proxy:
jq '[.tasks[] | select(.tags // [] | index("express:first-light"))] | length' data/coordination/TASK_REGISTRY.json
# GATE: task_registry_query(tags=["express:first-light"]).count MUST equal the jq number (≥10 post-repair)

# ── G21. Registration identities correct (Art. V; N10 §3.3 — RUN AFTER G20) ──
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
print("wrong subagent_type:",bad_st); print("wrong entity:",bad_en)
assert not bad_st and not bad_en
EOF
```
**HARD RULE**: G21 executes ONLY after G20 passes (tool count == jq count). Running G21 first
repeats the exact Art. V violation (repairing records into an unsearchable index). Additional
Step-5 evidence: log ≥10 distinct successful `task_registry_query` retrievals (tag/entity/
subagent_type/task_id axes) into the execution report before Delivered-Home completion claim.
Defect-5B check: `rg --files data/coordination | grep -c TASK_REGISTRY` → ≥1 post-fix.

### (e) Risk assessment
MEDIUM-HIGH operational (lowest code complexity, highest sequencing sensitivity). Risks:
(i) concurrent registry writers during payload application (lost-update window — mitigate with
quiescence check + before/after count parity); (ii) `.gitignore` negation interacting with
existing `*.md` negation at :2 — verify `git check-ignore` post-fix for both json and md files;
(iii) single-writer discipline — exactly ONE actor applies payloads (MaKaLi Stage-6 analog);
(iv) if Council-2 session spawns NEW express-c2-* records, G21 regex scoped to `express-c1-node`
pattern only — do not over-match.

### (f) Effort estimate
1.5h (5A fix+tests) + 0.5h (gitignore) + 2.0h (staged apply + verification) + 1.0h (template rule) + 1.0h (validator/test share) = **6.0h**.

---

## § VALIDATOR-FIRST CLAUSE (Decree Art. XII — MANDATORY FOR THIS SPEC)

This spec is **validator-first**: the CI check ships IN THE SAME deliverable as each work item —
never as a follow-up. Per Art. XII guard clause and G30, the literal string "validator-first"
appears here and in every `docs/specs/team_infra/*.md`.

**New validator module**: `scripts/validate_config_honesty.py` (name checked against `scripts/` inventory 2026-08-25 — NO collision; existing validators are validate_docs/llm_docs/tracking_state/soul/etc.). Functions:

| Function | Enforces | Paired work item |
|----------|----------|------------------|
| `check_plugin_paths(root="opencode.json")` | G1 — every `file://` plugin path exists | WI-1 |
| `check_agent_prompt_schema(root="opencode.json")` | G10 — no agent def uses `instructions[]`; every `prompt.file` exists | WI-2 |
| `check_provider_chain_canonical(cfg="config/providers.yaml")` | G3 — ocz < openrouter; G4 — enabled⇒keyed (skippable via `--allow-unkeyed` until Architect keys land, prints WARN honestly) | WI-3 |
| `check_no_archived_instructions(root="opencode.json")` | G5 — no `docs/archive/` in instructions[] | WI-3 |
| `check_doc_gate_strict_discriminates()` | G22 — runs validate_llm_docs.py --strict against clean+dirty fixtures, asserts exit polarity | WI-4 |
| `check_registry_discovery_parity(tag)` | G20 precondition — tool count == jq count; refuses identity-repair claims when false | WI-5 |

**Tests**: `tests/test_validate_config_honesty.py` — per-function positive/negative fixtures
(tmp-path opencode.json variants; providers.yaml variants; TASK_REGISTRY fixture with seeded
tags). Contract tests assert return types (M21). Every function has a negative test that FAILS
against the CURRENT (pre-fix) repo state — proving the validator can catch the defect it claims
to catch (anti-theater clause).

**Pairwise binding (Art. II.2, adopted as review rule)**: a PR adding any gate above without its
mandate-text/config patch FAILS REVIEW; a text patch promising a gate without the gate FAILS
REVIEW. Split-PR evasion (landing gate in one PR, text in "a later one") is the same violation.

**Anti-big-bang sizing**: five independently landable sub-deliverables (WI-1..WI-5), each ≤6h,
each shippable with its validator slice; no combined mega-PR. Land order respects Art. V:
WI-5 Step 1 may land anytime; WI-5 Steps 3-5 strictly after G20 green.

**Naming-collision check (Art. XII)**: performed 2026-08-25 — `scripts/validate_config_honesty.py`,
`tests/test_validate_config_honesty.py`, and this spec filename are unique in-tree
(docs/specs/team_infra/ holds SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md, SPEC-D-p2-hygiene.md,
SPEC-E-agents-md-reconstruction.md — no B collision).

**G30 self-check**:
```bash
for f in docs/specs/team_infra/*.md; do grep -q 'validator-first' "$f" || echo "MISSING GUARD: $f"; done   # expect: no output
```

---

## § EXECUTION ORDER & DEPENDENCIES

```
WI-1 (G1) ─┐
WI-2 (G10) ─┼── independent, any order; each lands with its validator slice
WI-3 (G3,G4,G5) ─┤
WI-4 (G22) ─┘
WI-5: Step1+2 (discovery) → G20 GREEN → Step3 (payloads, single writer) → Step5 (≥10 retrievals) → G21 GREEN
```
Post-remediation acceptance for this spec = G1, G3, G4*, G5, G10, G20, G21, G22 green
(*G4 gated on key provisioning per WI-3(d) caveat) + G30 across team_infra specs.

## § VERIFIED-ANCHOR LEDGER (provenance summary)

| Anchor | Upstream claim | node2 verification | Verdict |
|---|---|---|---|
| `.plugin[]` dead paths | maat 15:22Z / P1 F-01 / P6 F-01 / P10 X-5 | jq + ls reproduced | MATCH |
| 12 agents w/ `instructions[]` | maat 15:22Z list | jq list identical (names + count) | MATCH |
| root `instructions[]` @ line 27 incl. archive doc | mission brief / P1 F-05 | sed 25-35 confirms | MATCH |
| task_registry.py:134-135 bug | JEM :134-135 | sed 125-145 exact match | MATCH (mission said "~134 region" — precise locant confirmed) |
| Literal excludes 'all' @ :100 | JEM :100 | sed 95-105 confirms | MATCH |
| .gitignore:109 `data/coordination/*` | JEM :109 | sed 105-112 confirms | MATCH |
| validate_llm_docs.py no --strict | verity / decree Art. III | grep -c 'strict' = 0; argparse read | MATCH |
| providers.yaml OCZ-after-OpenRouter | P1 F-03 | yaml dump: openrouter 5 < ocz 6 | MATCH |
| M7 stale chain @ SOVEREIGN_MANDATES.md:55 | P1 F-03 | grep hit line 55 | MATCH |
| registration_payloads.json staged | decree §5.1 | file read; canonical+tasks+gated_on present | MATCH |
| plan.md / grok_cli.md dead | P3 F-03 / P6 F-03 | ls confirms missing; grok_cli.md in archive/ | MATCH |
| GAP-4 urgency | researcher MED vs decree HIGH | calibration delta recorded in WI-2(a); decree governs | FLAGGED (documented, not a factual mismatch) |

*⬡ OMEGA ⬡ MAAT/node2 ⬡ trc_c2_specb ⬡ DRAFT-COUNCIL2-PREP ⬡ validator-first ⬡ 2026-08-25*
