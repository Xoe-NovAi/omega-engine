# SPEC-C · P1 SECURITY POSTURE RECORDS — Council 2 Build Arm, Node 3 (domain: specc)
⬡ OMEGA ⬡ MAAT/node3 ⬡ trc_c2_specc ⬡ DRAFT
**SESSION_ID**: `20260825-094633-first-light-c2` | **Date**: 2026-08-25 | **Status**: DRAFT-COUNCIL2-PREP
**Authority**: SOVEREIGN_DECREE.md (`data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md`) Art. IV, VIII.2, X (P1 list), XII; §3 Preserved Dissent (depth OPEN); §5 tracker directive Q-3; SYNTHESIS_ARM_REPORT §2 T-7, §5 GAP-11, §6 gates G2/G26.
**Bright line**: this spec DRAFTS records and decision packages only. ZERO edits to existing production files are authorized by this document. The `"/*"` ruling and the depth-vs-relay decision are **Architect-owned (WAKE_STATE Q-3)** — this spec delivers the record template, process, and costed options; it delivers NO ruling.
**Provenance rule**: every file:line anchor below was re-verified by node3 in this session (2026-08-25) via jq/grep/sed. Mismatches vs upstream claims are flagged inline and logged in `node3_notes.md`.

---

## §0 SCOPE SUMMARY

Two P1 work items from Decree Art. X ("P1 mechanism honesty"), one spec:

| # | Work item | Decree hook | Gates | Est. hours (post-decision execution) |
|---|-----------|-------------|-------|------|
| WI-1 | `"/*": "allow"` decision record + WAKE_STATE annotation + resolution | Art. VIII.2 / T-7 / Q-3 | G2 (verbatim), G2′ (tightened, proposed) | 1.5 |
| WI-2 | Depth-vs-relay codification — both options fully costed as Architect decision package | Art. IV / GAP-11 / N5 F-9 / N1 F-20 | G26 (verbatim), PIVOT_LOG D-series check | 2.0–3.0 |
| — | Shared validator deliverable (§ VALIDATOR-FIRST CLAUSE) | Art. XII / G30 | G30 + two new checks | incl. below |

**Total**: ~4.5h post-decision execution + ~1h validator hook = **~5.5h** (matches N8 WP-C1 1.5h PROV + WP-C2 2h PROV within tolerance; delta is the shared validator deliverable).

Both work items are ⛔ BLOCKED on Architect Q-3 per N8_work_packages.md; this spec unblocks them the moment the Architect rules.

---

## WI-1 · `"/*": "allow"` DECISION RECORD + ANNOTATION (G2)

### (a) Problem statement
Root `opencode.json` `.permission.external_directory` enumerates 12 specific allow-rules (lines 12–23) and then grants `"/*": "allow"` (line 24) — a universal filesystem grant that mechanically nullifies the enumeration. Verified this session:
```bash
jq '.permission.external_directory["/*"]' opencode.json   # → "allow"
jq '.permission.external_directory | has("/*")' opencode.json   # → true
```
Decree Art. VIII.2 confirms permission enforcement itself is REAL (deny strips toolset; ask gates at request-time) — so the wildcard is a live, effective policy of "allow all external directories". T-7 adjudication (SYNTHESIS §2): N1 read it as a HIGH defect nullifying instruction-layer sandbox preaching (M8/T11/tainted-data quarantine); N6 read it as a deliberate autonomous-operation posture. Both are right — **the undocumented risk-acceptance is the defect**. An undocumented security posture is indistinguishable from a misconfiguration. Per WAKE_STATE Q-3 and decree §5 tracker directive 2, recording the decision explicitly is Architect-owned; this spec ships the RECORD TEMPLATE and process.

### (b) Evidence links
- Decree Art. VIII.2 (`SOVEREIGN_DECREE.md:49`): T-7 ruling stands — record explicitly, then remove wildcard or annotate enumeration informational (G2).
- Decree Art. X P1 (`SOVEREIGN_DECREE.md:63`): "`\"/*\"` decision recorded" listed as P1 mechanism-honesty item.
- SYNTHESIS T-7 (`SYNTHESIS_ARM_REPORT.md:84–86`); GAP row C-B3 (`:42`).
- Node evidence: `P1_report.md` F-02 (`opencode.json:10-26` claimed; actual verified block = lines 11–24 — minor line-number drift from upstream, substance confirmed).
- Counter-position: RUN_SIDE_REPORT / N6 F-06 deliberate-posture reading (preserved dissent).
- Verified anchor (this session): `opencode.json:11` opens `.permission.external_directory`; `opencode.json:24` = `"/*": "allow"`; current value exactly `"allow"`.

### (c) Proposed change/deliverable

**Deliverable 1 — Decision record file** (dev team creates; path fixed by this spec):
`data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md`

Verbatim-ready template:

```markdown
# DECISION RECORD — opencode.json `.permission.external_directory["/*"]`
⬡ OMEGA ⬡ ARCHITECT (Q-3) ⬡ recorded-by: <executor> ⬡ trc_c2_wildcard_record
**Date recorded**: <YYYY-MM-DD> | **Status**: [RESOLVED-AS: REMOVE-WILDCARD | KEEP-ANNOTATE]
**Supersedes**: none | **Related**: PIVOT_LOG D-<NNN>, WAKE_STATE Q-3, SPEC_C WI-1

## What `"/*": "allow"` grants
A universal allow rule on `.permission.external_directory`, granting every agent session
read/write access to EVERY path on the host filesystem outside the project root. Because it
is the LAST key in the map (opencode.json:24) and permission maps merge by specificity,
the 12 enumerated project-scoped allows (opencode.json:12-23) are subsumed: the effective
policy is "allow all", making the enumeration decorative.

## Mechanical evidence of nullification
- `jq '.permission.external_directory | has("/*")' opencode.json` → true (verified 2026-08-25, node3)
- `jq '.permission.external_directory["/*"]' opencode.json` → "allow"
- Enforcement layer itself is REAL per Council 1 Stage-4 probe (decree Art. VIII.2):
  deny strips toolset; ask gates at request-time. Therefore this rule is LIVE policy,
  not dead config.

## Explicit risk-acceptance statement
<RISK-ACCEPTANCE TEXT — Architect fills. Must state, at minimum:>
The wildcard posture is [ACCEPTED / REJECTED] for the autonomous-fleet operating mode
because <rationale>. Accepted residual risks: (1) any prompt-injected or compromised
agent can read/write arbitrary host paths, including ~/.ssh, credentials, and other
projects; (2) instruction-layer sandbox mandates (M8 zero-telemetry hygiene, T11 agent
security, tainted-data protocol) are advisory-only at the filesystem boundary;
(3) dispatch-suffix injection forensics (GAP-12, PLATFORM_GROUND_TRUTH_LOG entry #11)
show wrapper artifacts exist — a wildcard grant widens what an injected directive can do.
Compensating controls currently in place: <enumerate or state NONE>.

## Owner & expiry
- **Owner**: Architect (per WAKE_STATE Q-3).
- **Review date**: <recorded-date + 90 days> — mandatory re-review; if not re-reviewed,
  the default-on-silence disposition is REMOVE-WILDCARD (fail-safe to least privilege).

## Resolution paths (choose ONE via Status field above)
### Path A — REMOVE-WILDCARD
Delete the `"/*": "allow"` key from opencode.json `.permission.external_directory`.
The 12 enumerated allows remain the effective policy. Instruction-layer sandbox preaching
becomes truthful again.
### Path B — KEEP-ANNOTATE
Retain the wildcard. Add adjacent comment/documentation declaring the enumeration
INFORMATIONAL ONLY (documents intended minimum access, does not restrict). All fleet
docs referencing sandbox discipline must carry a pointer to this record.

## Acceptance
G2 (SYNTHESIS §6, verbatim):
  jq '.permission.external_directory | has("/*")' opencode.json   # false AFTER decision recorded; if kept: rg -c 'risk-acceptance' data/coordination/WAKE_STATE.json ≥ 1
```

**Deliverable 2 — WAKE_STATE.json annotation snippet** (extends existing Q-3 entry at ~line 103; dev team applies):

```json
{
  "id": "Q-3",
  "gap": "GAP-11+T-7",
  "question": "subagent_depth raise-vs-codify-relay AND '\"/*\": \"allow\"' risk-acceptance record",
  "default": "Relay codified as standing law (Art. IV); wildcard annotated informational pending Architect record",
  "wildcard_risk-acceptance": {
    "status": "RECORDED",
    "decision_record": "data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md",
    "resolved_as": "<REMOVE-WILDCARD|KEEP-ANNOTATE>",
    "pivot_log_ref": "D-<NNN>",
    "review_by": "<+90d>"
  }
}
```
Note: the literal string `risk-acceptance` must appear in the ADDED FIELD (not only inside the pre-existing question text) so G2's kept-path grep certifies the record, not the question.

**Deliverable 3 — one-line PIVOT_LOG D-series stub** pointing at the record file (keeps Art. VII version-stamp discipline; single-writer applies).

### (d) Acceptance gates (bash, citing gate numbers)
```bash
# ── G2 (verbatim, SYNTHESIS_ARM_REPORT.md §6 lines 194-195) ──
jq '.permission.external_directory | has("/*")' opencode.json   # false AFTER decision recorded; if kept: rg -c 'risk-acceptance' data/coordination/WAKE_STATE.json ≥ 1

# ── G2′ (PROPOSED tightening — node3 addition, closes a false-pass) ──
# Current G2 kept-path can pass on the pre-existing "risk-acceptance" substring inside
# Q-3's QUESTION text (WAKE_STATE.json ~line 105). Require the record REFERENCE instead:
test -f data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md \
  && jq -e '.first_light_express.decision_queue[]? | select(.id=="Q-3") | .wildcard_risk-acceptance.decision_record' data/coordination/WAKE_STATE.json >/dev/null \
  && echo G2-PRIME-PASS || echo G2-PRIME-FAIL

# Record must carry an explicit resolution status (either path acceptable once ruled):
grep -q 'RESOLVED-AS:' data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md
```

### (e) Risk assessment
- **Risk of doing nothing**: HIGH — config contradicts instruction-layer security preaching every session (C-A class); auditors re-litigate T-7 every council; an injected directive meets an allow-all filesystem.
- **Risk of the record itself**: LOW — documentation-only until the Architect picks a path. Path A (remove) risk: some workflow may legitimately rely on out-of-tree access (mitigation: the 12 enumerated paths cover all council-observed mounts; run G2 + a smoke session after removal). Path B (annotate) risk: annotation becomes another claim-outliving-mechanism if not lint-gated — mitigated by the validator clause below.
- **Reversibility**: trivial either way (one JSON key + one doc).

### (f) Effort estimate
1.5h total: 0.25h fill template + apply WAKE_STATE snippet (single writer), 0.25h PIVOT_LOG stub, 0.5h chosen-path execution + smoke, 0.5h gates + Hivemind announcement. (Matches N8 WP-C1 1.5h PROV.)

---

## WI-2 · DEPTH-VS-RELAY CODIFICATION — COSTED OPTIONS PACKAGE (Art. IV / GAP-11)

### (a) Problem statement
`opencode.json:3` sets `"subagent_depth": 2`. A dispatched leaf executes AT depth 2 and therefore cannot call `task()` at all — while dispatch protocol §1 Rule 4 (`docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md:43`) authorizes single-level nesting, and the council's own M11 protocol mandated leaf paging. This was proven mechanically TEN times in Council 1 (identical rejection string from every leaf — Exhibit E, SYNTHESIS §4). Art. IV ratified Arm-Relay for that run and as standing design, but deliberately deferred the permanent codification: depth-vs-protocol-text → Council 2 dev + Architect, BOTH options costed (GAP-11; preserved dissent §3 keeps the depth question OPEN). Leaving it undecided invites the next council to re-hit the wall.

### (b) Evidence links
- Decree Art. IV (`SOVEREIGN_DECREE.md:33–34`): relay ratified; NO mid-run change; both options costed; future leaf packets embed relay clause INSTEAD of paging steps.
- Decree §3 (`SOVEREIGN_DECREE.md:75`): depth deliberately OPEN; neither bump nor amendment decreed.
- SYNTHESIS T-3 (`SYNTHESIS_ARM_REPORT.md:68–70`) + GAP-11 row (`:181`): expected artifact = "Decision entry, PIVOT_LOG D-series".
- N1 F-20 (`P1_report.md:257–273`): options A/B first costed; live rejection transcript 2026-08-25T13:16Z.
- N5 F-9 (`P5_report.md:214–225`): Rule 4 text grants what config revokes; §4 deviation log records the 7th consecutive rejection.
- Arms: BUILD_SIDE_REPORT B-C5 (`:22`), RUN_SIDE_REPORT `:121` — both arms performed relay de-facto.
- Verified anchors (this session): `opencode.json:3` = `"subagent_depth": 2`; `SUBAGENT_DISPATCH_PROTOCOL.md:43` = Rule 4 "Single-Level Nesting… Limit delegation to a single level of nesting unless explicitly authorized."

### (c) Proposed change/deliverable — BOTH OPTIONS FULLY COSTED

| Dimension | **Option A — raise `subagent_depth` to 3** | **Option B — codify Arm-Relay in protocol text** |
|---|---|---|
| Mechanism class | Config/mechanism change | Doc/process change |
| Exact surface | One key: `opencode.json:3` `"subagent_depth": 2 → 3` | (1) `SUBAGENT_DISPATCH_PROTOCOL.md` §1 Rule 4 (:43) rewritten: leaves are TERMINAL (no task() at depth 2); delegation beyond one level flows arm→orchestrator→leaf (relay). (2) New §"M11 Arm-Relay Clause": leaves write report+payload to disk; arms relay pages once per stage; orchestrator pages direct. (3) Leaf packet template amended: relay clause embedded INSTEAD of paging steps (Art. IV verbatim). (4) Cross-ref note in `ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` P-row index. |
| Blast radius | Every existing leaf gains spawn capability immediately, retroactively legitimizing any packet text still carrying paging steps. Depth-3 chains become possible: orchestrator→arm→node→expert. | Zero runtime blast radius. Text aligns with observed, working practice (both arms relayed successfully in C1). |
| Failure modes | Runaway-recursion chains (agent spawns agent spawns agent); token burn (M18); the ONLY hard cap remaining is OpenCode's depth counter itself — `observability_check_recursion(entity_name, current_depth)` exists in the MCP toolchain but is an ADVISORY/manual check, not an enforcing gate. **GAP-12 interaction: NEGATIVE** — dispatch-suffix injection (two occurrences council-wide, PLATFORM_GROUND_TRUTH_LOG entry #11) means synthetic trailing lines instructing agents to spawn entities become EXECUTABLE at leaf tier; depth bump converts a nuisance artifact into a deeper exploit surface. | Stale-text recurrence (the exact C-A defect class) if enforcement is absent — mitigated below. **GAP-12 interaction: POSITIVE** — a depth-2 leaf physically cannot act on injected spawn instructions; Hop Rule becomes structural containment. |
| Enforcement (anti claim-outliving-mechanism) | Self-enforcing (config IS the mechanism); but requires amending Rule 4 text anyway or the contradiction merely inverts. | Requires a lint hook so the text cannot silently rot: pre-commit/lint script scans NEW leaf packets under `data/council/**/phase0*packet*.md` and `data/handoff/pending/` for paging steps (`task(subagent_type=` at leaf tier) vs the embedded relay clause marker `<!-- RELAY-CLAUSE:v1 -->`. Packet without the marker fails lint. Plus G26 else-branch greps the protocol for 'Arm-Relay'. |
| Effort | 0.5h change + 1.5h probe/tests (spawn-chain fixture, recursion-guard interplay check, GAP-12 threat note) = **~2.0h** | 1.5h text (Rule 4 rewrite + relay clause + template) + 1.0h lint hook + 0.5h backfill note = **~3.0h** |
| Risk | MED-HIGH (injection amplification + advisory-only recursion guard) | LOW (doc-only; worst case is drift, which the hook detects) |
| Reversibility | Trivial (one JSON key) | Trivial (git revert docs) |
| Precedent alignment | Contradicts Art. IV's ratified relay design; contradicts N1 F-20's own recommendation of option B | Matches Art. IV ratification, both arms' de-facto practice, and preserves the Hop Rule structurally |

**RECOMMENDATION (clearly labeled — NOT a decree; Architect owns Q-3)**: On Architect silence, adopt **Option B**. Rationale: Art. IV already ratified relay as standing design; Option B contains the GAP-12 injection surface instead of widening it; Option A's only hard safety net (depth counter) sits above an advisory-only recursion guard. If the Architect chooses A, ship it WITH the recursion-guard promotion ticket (observability_check_recursion → enforcing gate) and the GAP-12 packet-citation rule in the same commit (pairwise binding, Art. II.2).

### (d) Acceptance gates (bash, citing gate numbers)
```bash
# ── G26 (verbatim, SYNTHESIS_ARM_REPORT.md §6 lines 306-307) ──
jq '.subagent_depth' opencode.json   # ≥3 IF depth-bump chosen; ELSE: rg -q 'Arm-Relay' docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md (relay codified, no bump)

# ── G26′ (PROPOSED — decision-recorded gate; GAP-11 expected artifact was "PIVOT_LOG D-series") ──
grep -qE 'D-[0-9]+.*(subagent_depth|Arm-Relay)' docs/decisions/PIVOT_LOG.md && echo G26-PRIME-PASS || echo G26-PRIME-FAIL
# Either outcome MUST leave a D-series entry naming the choice — silence is not a state.

# ── Relay-clause presence in NEW leaf packets (Option B enforcement; feeds validator clause) ──
for p in $(find data/handoff/pending -name '*.json' -newer docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md 2>/dev/null); do
  grep -q 'RELAY-CLAUSE\|Arm-Relay' "$p" || echo "PACKET MISSING RELAY CLAUSE: $p"; done   # expect: no output
```

### (e) Risk assessment
- Risk of deferral (status quo): each new council re-discovers the wall (10 live rejections in C1); packets keep carrying impossible paging steps; GAP-11 stays open.
- Option A residual risks enumerated in table (recursion + injection amplification).
- Option B residual risk: protocol doc drift — historically near-certain without a hook (protocol self-version conflict F-5, stale Pending-Sprint-2 items F-6); mitigated by the packet lint + G26 else-branch.
- Both options preserve M23 failure integrity: leaves keep reporting tool-chain failures to their arm rather than swallowing them.

### (f) Effort estimate
Option A ≈ 2.0h · Option B ≈ 3.0h · decision-package review (Architect) ≈ 0.5h. (Matches N8 WP-C2 2h PROV for the post-decision execution window.)

---

## § VALIDATOR-FIRST CLAUSE

This cluster is records-not-code, but per Art. XII ("validator-first — spec ships its CI check in the same deliverable") and G30, its CI checks ship WITH this spec — never as follow-up. Deliverable: `scripts/check_council_guards.sh` + `make check-council-guards` target, landing in the same commit as the first applied work item:

```bash
#!/usr/bin/env bash
# check_council_guards.sh — SPEC-C validator-first deliverable (Council 2, node3)
set -u; FAIL=0

# Guard 1 — wildcard must not exist without a recorded decision reference (extends G2/G2′)
if jq -e '.permission.external_directory | has("/*")' opencode.json | grep -q true; then
  test -f data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md || { echo "FAIL: \"/*\" present, no decision record"; FAIL=1; }
  grep -q 'RESOLVED-AS:' data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md 2>/dev/null || { echo "FAIL: decision record unresolved"; FAIL=1; }
fi

# Guard 2 — leaf packets must embed the relay clause, not paging steps (WI-2 Option B enforcement)
for p in data/handoff/pending/*.json; do
  [ -e "$p" ] || continue
  grep -q 'RELAY-CLAUSE\|Arm-Relay' "$p" || { echo "FAIL: leaf packet lacks relay clause: $p"; FAIL=1; }
done

exit $FAIL
```
Pairwise binding (Art. II.2): the first PR that touches `opencode.json` permissions or the dispatch protocol MUST include this script + make target; a change without its guard fails review. G30 re-check (decree §4, verbatim):
```bash
for f in docs/specs/team_infra/*.md; do grep -q 'validator-first' "$f" || echo "MISSING GUARD: $f"; done   # expect: no output
```

## § ANTI-BIG-BANG SIZING

Both work items are independently committable in ≤ one sprint each: WI-1 = 1.5h single commit (record + snippet + stub + gates); WI-2 = one commit per option component (text, hook, backfill), largest ≤1.5h. No package exceeds N8's sprint budget; the tree is greener (G2/G26 closer to green) after each commit regardless of which option the Architect picks.

## § NAMING-COLLISION CHECK

Verified 2026-08-25: `ls docs/specs/team_infra/` shows SPEC_A/SPEC_B/SPEC-D/SPEC-E only — no collision with `SPEC_C_P1_SECURITY_POSTURE_RECORDS.md`. **Flagged drift**: `N8_work_packages.md` spec-inputs list references `SPEC-C-p1-security-posture.md` (hyphenated, different name). Integration must reconcile the pointer to this file's actual name (NOT performed here — bright line). Sibling specs themselves mix underscore/hyphen conventions; recommend integration standardizes during launch-package assembly.

## § REFERENCES

| Source | Role |
|---|---|
| `data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md` | Art. IV, VIII.2, X, XII; §3 dissent; §4 G29/G30; §5 Q-3 |
| `data/council/20260825-094633-first-light/phase3_synthesis/SYNTHESIS_ARM_REPORT.md` | T-7, T-3, GAP-11, gates G2/G26 |
| `data/council/20260825-094633-first-light/phase1_nodes/P1_report.md` | F-02, F-20 |
| `data/council/20260825-094633-first-light/phase1_nodes/P5_report.md` | F-9, deviation log |
| `data/council/20260825-094633-first-light/phase2_arms/{BUILD,RUN}_SIDE_REPORT.md` | B-C4/B-C5; relay precedent |
| `data/council/20260825-094633-first-light-c2/phase1_nodes/N8_work_packages.md` | WP-C1/WP-C2 consumers of this spec |
| `opencode.json:3,11,24` · `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md:43` · `data/coordination/WAKE_STATE.json` (Q-3) · `docs/decisions/PIVOT_LOG.md` | verified anchors |
| Working notes | `data/council/20260825-094633-first-light-c2/phase1_nodes/node3_notes.md` |

---
*⬡ OMEGA ⬡ MAAT/node3 ⬡ trc_c2_specc ⬡ DRAFT-COUNCIL2-PREP ⬡ validator-first ⬡ 2026-08-25*
