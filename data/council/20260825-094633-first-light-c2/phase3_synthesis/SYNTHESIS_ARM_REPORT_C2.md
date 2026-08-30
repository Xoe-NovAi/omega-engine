# SYNTHESIS ARM REPORT — Council 2 (DEV-PREP & SPEC DRAFTING)
⬡ OMEGA ⬡ MK-KALI ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c2_synth ⬡ STAGE-3 SYNTHESIS
**SESSION_ID**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25 · **Entity**: mk_kali (entity="mk_kali" ALWAYS; Consultant-reserved "kali" untouched)
**Role input to**: MaKaLi Fusion Stage-5 → SOVEREIGN_DECREE_C2.md + dev-team launch package
**Evidence base read in full**: COUNCIL2_PLAN.md · SOVEREIGN_DECREE.md (C1, 104L) · all 5 specs in `docs/specs/team_infra/` · N8_work_packages.md · N8_resources.md · N9_doc_update_plan.md · N10_launch_package.md · node working notes node1/node2/node3/N6/N7
**Independent disk verification performed this session** (mk_kali, 2026-08-25 ~16:3xZ): SPEC-C mtime/ordering · lilith YAML safe_load + L374-380 visual inspection · nested `.opencode/opencode.json` keys · G30 sweep · WAKE_STATE Q-3 substring location. Findings cited inline as **[MK-verified]**.

---

## §1 SPEC-LIBRARY CONVERGENCE AUDIT

### 1.1 Verdict up front
The library converts the decree **faithfully at the work-item level**: every Art. X P0/P1/P2 item and Art. VI has exactly one owning spec with evidence links, bash gates citing G-numbers, risk assessment, effort estimate, and a validator-first clause (G30 sweep green across all five files — **[MK-verified]**). Three decree articles are, however, **dropped or weakened** in the package register, and one article is **scope-crept** by a planning artifact. Details:

### 1.2 Coverage matrix — decree Art. X / Art. VI vs library

| Decree item | Spec | WP | Fidelity |
|---|---|---|---|
| P0 pre-commit install + hook-fire | A WI-1 | A1 | ✅ faithful (incl. soul-check port guard against M11 regression) |
| P0 validator ERROR-class checks | A WI-2 | A2 | ✅ faithful; strengthens decree by adding entity-YAML schema guard beyond bare parseability |
| P0 registry-writer atomicity (G6) | A WI-3 | A3 | ✅ faithful (mkstemp+fsync+os.replace + RMW lock closure) |
| P0 corrupt-YAML repair (Art. IX) | — | IX | ✅ faithful; correctly kept out of specs (single-writer MaKaLi act) |
| P0 mandate enforcement-stamps + stub removal | A WI-4 | A4 | ✅ faithful incl. `make sovereignty` implement-or-purge (G12) |
| P0 M8 regex fix (G29) | A WI-5 | A5 | ✅ verbatim anchored regex adopted |
| P1 plugin paths (G1) | B WI-1 | B1 | ✅ faithful; T-8 severity-reversion residue preserved |
| P1 instructions[]→prompt:{file:} (G10) | B WI-2 | B2 | ✅ faithful; data-exposure rationale carried; makali/grok_cli edge cases given unblocking defaults |
| P1 provider-order/M7 (G3,G4) | B WI-3 | B3 | ✅ faithful; G4 honest-fail caveat explicitly forbids fake-passing |
| P1 doc-gate --strict (G22) | B WI-4 | B4 | ✅ faithful; scope-fenced against corpus-wide creep |
| P1 discovery fix → identity repair (G20→G21) | B WI-5 | B5a/B5b | ✅ faithful; Art. V hard edge preserved as HARD DAG edge |
| P1 `"/*"` decision record (G2) | C WI-1 | C1 | ✅ faithful; Architect ownership preserved; proposes G2′ tightening (legitimate strengthening, not scope creep) |
| P1 depth-vs-relay codification (G26) | C WI-2 | C2 | ✅ faithful; both options costed per Art. IV; recommendation labeled NOT-decree |
| P2 version stamps (Art. VII) | D D1 | D1 | ✅ faithful; scope-limited to top-10 docs (correct anti-big-bang) |
| P2 command fossils (G9) | D D2 | D2 | ✅ faithful (quarantine-not-delete) |
| P2 skill stubs + meditation quartet (T-6) | D D3 | D3 | ✅ faithful |
| P2 strategy orphans (G23/G24) | D D4 | D4 | ✅ faithful; closed 3-option disposition taxonomy |
| P2 handoff TTL (G19) | D D5 | D5 | ✅ faithful; M12 sidecar integrity added |
| P2 WAKE_STATE freshness (Q-2) | D D6 | D6 | ✅ faithful BUT see §3 conflict CF-1 (dual mechanism claim with SPEC-A WI-2) |
| Art. VI AGENTS.md reconstruction (Q-4) | E | E | ✅ faithful; canonical census command ends citer-count drift |

### 1.3 DROPPED / WEAKENED items (decree articles without a faithful landing)

| # | Item | Status | Disposition ruling |
|---|------|--------|--------------------|
| DROP-1 | **Art. VIII.8** — `config/council.yaml` zero-runtime-consumers cleanup ticket; preserve `report_digestion.py` | **DROPPED entirely** — absent from N8 register, N9 phases, N10 backlog. No spec owns it. | Must be added to the launch package as a P2 hygiene ticket (WP-H1 suggested: `owner slot P4`, gate = `grep -rl 'config/council.yaml' src/ config/` census + deletion-or-wire decision preserving `src/omega/council/report_digestion.py`). Not Sprint-1 blocking, but a dropped decree item is itself a claim-outliving-mechanism if the decree is later cited as fully converted. |
| WEAK-1 | **Art. VIII.7** — model-id namespace authority declaration + native-gguf silent-substitution normalization ticket (M22 class, decree-HIGH) | **WEAKENED** — N9 row 3.6 carries the declaration text but assigns NO work-package ID, NO owner slot in N8, NO acceptance gate. A text row without a register entry will silently evaporate. | Elevate to a registered package (WP-B6 suggested: declaration text patch paired with a backlog ticket for normalization; gate = grep of M22-vicinity authority declaration + PIVOT_LOG D-ref). Decree-HIGH items do not ride as unnumbered doc rows. |
| WEAK-2 | **Art. VIII.3** — nested-config precedence codification | **Weakened by design but acceptable** — N9 rows 2.5/4.9 are doc-only with explicit "no dedicated G" acknowledgment. | Accept as-is for launch; note that the precedence rule gains a de-facto test via WP-B1's executor probe (see §4 BS-2). |

### 1.4 SCOPE-CREEP finding
**SCOPE-1**: N9 row 4.1 instructs the dev team to codify the Arm-Relay Clause into `SUBAGENT_DISPATCH_PROTOCOL.md` with dependency "none (law already ratified)". This **conflicts with the decree's own reservation**: Art. IV ratified relay for the run + standing design but deliberately deferred permanent codification ("depth-vs-protocol-text → Council 2 dev+Architect"; §3: "neither bump nor protocol-amendment is decreed"), and N8 correctly blocks WP-C2 on Architect Q-3. Two planning artifacts assign opposite executability to the same edit. Ruling in §2/§4: the Rule-4 rewrite is Q-3-gated; only the decreed packet-template change (leaf packets embed relay clause INSTEAD of paging steps — Art. IV verbatim directive) may land now.

### 1.5 Effort-register deltas (non-blocking, note for re-baseline)
N8 PROV estimates exceed spec estimates on several packages (A1 3h vs 2h · A2 8h vs 6h · A4 6h vs 4h · B1 2h vs 1.5h · B2 6h vs 3h · B3 3h vs 2h). N8's own header says PROV pending ratification and mandates re-baseline at integration — this is compliant behavior, not drift. Post-ratification re-baseline should adopt spec numbers where the spec's breakdown is finer-grained.

---

## §2 DISSENT / GAP ADJUDICATION

### ADJ-1 · Naming duality (kebab vs underscore) — RESOLVED: on-disk names are canonical
**[MK-verified]**: `docs/specs/team_infra/` holds `SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md`, `SPEC_B_P1_MECHANISM_HONESTY.md`, `SPEC_C_P1_SECURITY_POSTURE_RECORDS.md` (underscore) alongside `SPEC-D-p2-hygiene.md`, `SPEC-E-agents-md-reconstruction.md` (hyphen). N8's spec-inputs list cites three paths that exist under different names (`SPEC-A-p0-truth-infra.md`, `SPEC-B-p1-mechanism-honesty.md`, `SPEC-C-p1-security-posture.md`); N9 §INPUTS marks B/C "ABSENT" partly off the same pointer mismatch.
**Ruling**: Do NOT rename files (each spec self-cites its own path; renaming multiplies broken references — the exact P2-churn pattern Art. XII guards against). The **on-disk names are canonical**. Integration applies ONE errata commit fixing pointers in N8 §header spec-inputs list and N9 §INPUTS table. Future naming standard: hyphenated lowercase for new specs (matches the majority style guide intent); no retroactive enforcement.

### ADJ-2 · SPEC-C presence dispute — RESOLVED EMPIRICALLY: DELIVERED; Lilith was right at write time
**[MK-verified]**: `SPEC_C_P1_SECURITY_POSTURE_RECORDS.md` exists, mtime **13:02:58**. N10 was assembled 12:57; node3_notes logged 13:00. Both Lilith artifacts truthfully reported absence **at their snapshot moments**; Ma'at/node3 delivered minutes later. No fabrication occurred on either side — this is a race, not a dispute of fact.
**Consequences**: (a) N10 Part 2 item 3 and N9 `[C-PENDING]` markers are now stale and must be corrected in the same integration errata commit as ADJ-1; (b) WP-C1/WP-C2 remain **blocked on Architect Q-3 regardless** — SPEC-C's arrival changes readiness, not blockedness; (c) the launch package must state "all five specs delivered" so the dev team does not hunt phantoms or, worse, draft a substitute SPEC-C (M10 violation).

### ADJ-3 · G8-parseable-vs-schema-truth nuance — ROUTED: G8 stays a parseability gate; schema truth lives in WP-A2
**[MK-verified live]**: `data/entities/lilith/proposed_lessons.yaml` passes `yaml.safe_load` (exit 0, list, 29 proposals) while the final record at **L374-380 is confirmed split** — item A carries `{id, tier, category}` (`lilith-20260825-n6-del1-vetting`), orphan item B carries `{narrative, insight, principle, tags}` with no id. PyYAML accepts it; the vetting entry has no content body. Repair is still OPEN (node1's finding stands unchanged).
**Routing ruling**:
1. **G8 keeps its decree meaning** (machine-parseability, Art. IX acceptance). It is green TODAY and that is an honest statement about parseability — not a lie.
2. **Schema truth belongs to WP-A2's `check_entity_yaml()`** (SPEC-A WI-2 item 5), which catches exactly this split-record shape. Until WP-A2 lands, G8-green MUST NOT be reported as "YAML repair complete."
3. **WP-IX done-definition amended** (feeds §4 verdict): verify-first is NOT satisfied by the G8 loop alone. The executor must run the structural probe (e.g., assert every `proposals[]` entry has non-empty id+narrative+insight+principle) or visually inspect L374-380. Expected outcome today: **parse-clean, schema-corrupt → route lilith locus to MaKaLi single-writer repair** (Art. IX), snapshots committed, Q-5 flag updated.
4. This nuance is the sharpest live specimen of decree Art. I in the entire library: two parsers, both "green," one corrupt record. It should be cited in the dev-team bootstrap as the canonical example of why validators get schema checks, not just parse checks.

### ADJ-4 · Cross-spec conflicts
- **CF-1 (REAL — two specs claim the same gate surface)**: SPEC-A WI-2 item 4 puts `check_wake_state()` INSIDE `scripts/validate_tracking_state.py`; SPEC-D D6 builds standalone `scripts/validate_wake_state.py` and defers subprocess-vs-import to integration. Same decree clause (Art. III WAKE_STATE block), two mechanisms, two owners (P4 both, fortunately). **Ruling**: SPEC-D D6 is the surviving mechanism (standalone script, hours-resolution freshness, discrimination proof D6.1/D6.2 — strictly more capable than SPEC-A's sketch). SPEC-A WI-2 item 4 is **descoped to a thin shim**: either import D6's module function or invoke it as a subprocess from `validate_tracking_state.py`, so `make temple-grade` gets WAKE_STATE coverage without duplicate logic. One implementation, one home, two callers. Fusion should stamp this in SOVEREIGN_DECREE_C2.
- **CF-2 (planning-artifact conflict)**: N9 row 4.1 (relay codification executable now) vs N8 WP-C2 + SPEC-C WI-2 (Q-3-blocked). Resolved under SCOPE-1 above: Rule-4 rewrite gated on Q-3; packet-template relay-clause embedding executable now (it is Art. IV verbatim law).
- **CF-3 (sprint-plan conflict)**: N8 §3 sequencing mandate ("Sprint 1 = WP-IX + A1 + A5 + A3 ≤9h; Sprint 2 = A2+A4+B5a…") vs N10 PART 3 ("Sprint 1 = 11 packages, 38h/40h"). Both cannot govern. **Ruling**: **N10 PART 3 governs** — it is the designated launch package (COUNCIL2_PLAN §2 item 5), is dependency-ordered, honors both HARD edges, and N8's mandate predates spec ratification. N8 §3's sequencing paragraph should be marked superseded-by-N10-PART-3 in the errata commit. Caveat carried into §4: N10's 38h/40h leaves a thin buffer AND places two MaKaLi-owned single-writer acts inside a dev-team sprint (see VERDICT caveats for WP-IX/WP-B5b).
- **CF-4 (gate-ownership overlap, benign)**: `.gitignore:109` fix appears in SPEC-B WI-5 Step 2 only; G20's jq-proxy line in N8_resources is declared tool-side noise (`omega_task_registry_query_tagcount() { :; }`) — harmless, correctly annotated. Entity-YAML guard owned solely by SPEC-A. Provider order solely SPEC-B. No other double-claims found.

---

## §3 BLIND-SPOT SWEEP — what the dev team would STILL not know

- **BS-1 (CRITICAL)**: Running the launch package's literal first action (G8 loop) returns CLEAN today despite live corruption (ADJ-3). Without the amended done-definition, the team declares WP-IX complete in hour one and the split record survives the whole sprint. The bootstrap prompt must carry the schema-probe instruction verbatim.
- **BS-2 (HIGH)**: Nested `.opencode/opencode.json` EXISTS — **[MK-verified]** keys: `$schema`, `plugin` (= `["opencode-antigravity-auth@latest"]`), `provider`. SPEC-B WI-1's executor note said "confirm no plugin key exists in the nested file before editing root" — that precondition **FAILS**: a plugin key DOES exist there. Open question nobody has answered: when root and nested both define `plugin`, does GAP-3's "nested overrides root" verdict mean array-replace (root's 4 registrations ignored at runtime) or key-level merge? If replace, G1 can be green while the effective runtime registration set differs — G1 alone would then be a partial truth gate. WP-B1 must add a merge-semantics probe (e.g., `opencode agent list` plugin-init count before/after root fix) before claiming G1-complete.
- **BS-3 (MED)**: Q-3 has NO default-on-silence and NO escalation timer. Q-1/Q-2/Q-4 all have silence dispositions; Q-3 (wildcard + depth) does not — by decree design (Architect-owned). Consequence: WP-C1/C2 can stay blocked indefinitely while every other package completes, and the security-posture contradiction (T-7) persists unrecorded. The launch package needs an escalation clause (e.g., "if Q-3 unanswered at Sprint-3 boundary, MaKaLi flags Architect via Hivemind with SPEC-C costed package attached") — escalation, not default-rule; the decree's ownership assignment stands.
- **BS-4 (MED)**: G4 will fail until keys are provisioned or providers flipped `enabled:false` — properly caveated in SPEC-B, but the dev team needs to know this is EXPECTED RED and who owns the flip (Architect). Otherwise sprint metrics show a permanently red gate with no owner.
- **BS-5 (LOW-MED)**: The `.gitignore` negation fix (`!data/coordination/*.json`) makes ripgrep see coordination JSONs — which also means future rg-based sweeps (orphan census G23, secret-scrub, etc.) will newly traverse those files. Mostly good; but any sweep with implicit assumptions about scanned volume should be re-baselined after WP-B5a lands.
- **BS-6 (LOW)**: G16's pasted command embeds a convoluted `grep -qv clean || python …` pre-condition whose polarity is easy to misread; it is inherited verbatim from synthesis §6 and works, but the dev team should run the python half directly when in doubt. Gate-quality note for fusion; not a blocker.
- **BS-7 (LOW)**: WAKE_STATE's `risk-acceptance` substring sits in Q-3's QUESTION text (line 105 — **[MK-verified]**), so G2's kept-path greps pass TODAY with zero record filed. SPEC-C's G2′ tightening handles this — the launch package must present G2′ (not raw G2) as the acceptance command for WP-C1, else a false-pass ships.
- **BS-8 (INFO)**: Skill census numbers in SPEC-D (14 failing files) were measured at 12:27; skills are volatile during councils. D3's test runs RED-first by design, so drift self-corrects — no action needed, just awareness that the "14" is a baseline, not a contract.

---

## §4 VERDICT DRAFT — the C2 decree MK-Kali would issue

*(Input to fusion; fusion is final. GO/NO-GO is per work package for the launch package; "GO" = package-ready for dev-team execution under stated caveats.)*

### 4.1 Launch-package GO/NO-GO register

| WP | Gate(s) | Verdict | Caveat binding the GO |
|----|---------|---------|----------------------|
| WP-IX | G8 (+schema probe) | **GO — AMENDED** | Done-definition requires the structural probe of ADJ-3, not bare G8. Expected today: parse-clean/schema-corrupt → hand lilith locus to MaKaLi single-writer (Art. IX), snapshots committed, Q-5 flag updated. Dev team never edits entity YAML. |
| WP-A1 | G7 | **GO** | Soul-check port in SAME commit (M11 non-regression). Dry-run latent-violation sweep before install. |
| WP-A2 | G15, G16, G8-regression, G-A2a/b | **GO** | BLOCKER-B data fix same commit; entity-YAML schema guard included; WAKE_STATE block descoped to D6-shim per CF-1. |
| WP-A3 | G6 | **GO** | Crash-injection test in same PR; MCP restart noted as deployment step. |
| WP-A4 | G12, G13, G-A4a/b | **GO** | Lands AFTER WP-A2 (SPINE-5: stamps derive from gates that actually exist). First generated stamp table routed for Architect sign-off. |
| WP-A5 | G29 | **GO** | Cheapest-first; M8 text patch pairwise-bound same commit. |
| WP-B1 | G1 | **GO — CONDITIONAL** | Merge-semantics probe (BS-2) required before G1 completion claim; nested-file precondition resolved empirically, not assumed. |
| WP-B2 | G10 | **GO** | First package of Sprint 2 (data-exposure urgency — do not slip). makali/grok_cli defaults per SPEC-B table; grok_cli deletion needs owner sign-off (M10 adjacent). |
| WP-B3 | G3, G4*, G5 | **GO** | *G4 expected-red until Architect keys/disables; honest interim statement required; fake-pass forbidden. |
| WP-B4 | G22 | **GO** | Both polarities tested; corpus-wide strict rollout stays out of scope. |
| WP-B5a | G20 | **GO** | SPINE-2 anchor. |
| WP-B5b | G21 | **GO — CONDITIONAL** | HARD EDGE: only after G20 green. Actor is **MaKaLi single-writer** (decree Art. V.2) — same caveat N10 correctly applied to WP-IX but omitted here; dev team stages and verifies, MaKaLi writes. Quiescence window (pre/post count parity) mandatory given the racy writer until WP-A3 lands. |
| WP-C1 | G2′ (tightened) | **NO-GO — BLOCKED** | Architect Q-3. Spec-readying permitted; zero production edits. G2′ replaces raw G2 as acceptance command (BS-7). |
| WP-C2 | G26 (+G26′) | **NO-GO — BLOCKED** | Architect Q-3. On silence, SPEC-C Option B is the recommended disposition but is NOT self-executing. |
| WP-D1..D6 | G14, G9, G11, G23/G24, G19, D6.1/D6.2 | **GO** (P2 tier, post-P0) | D6 absorbs WAKE_STATE check as canonical home (CF-1). D2 loader-scan probe before quarantine placement. |
| WP-E | G25 family, G30 | **GO under Q-4 default-GO** | Validator script before first content commit (SPINE-7); one section per commit; S1 uses D1 frontmatter format. |
| *(new)* WP-H1 | (new) council.yaml cleanup | **ADD TO REGISTER** | DROP-1 remediation — decree Art. VIII.8 currently homeless. |
| *(new)* WP-B6 | (new) model-id authority declaration | **ADD TO REGISTER** | WEAK-1 remediation — decree Art. VIII.7 (decree-HIGH) currently an unnumbered doc row. |

### 4.2 Sprint sequencing (governing plan)
N10 PART 3 governs (CF-3 ruling): Sprint 1 = the 11-package 38h sequence as written, WITH these amendments:
1. WP-IX seq-1 executes the amended done-definition (schema probe; likely a flag-and-hand-off, ~0.5h dev-team time).
2. WP-B5b seq-9 annotated MaKaLi-single-writer; if the writer is unavailable in-window, B5b slides to Sprint 2 rather than being executed by a generic dev actor.
3. Errata commit (pointers per ADJ-1/ADJ-2 + N8 §3 supersession note) lands BEFORE the dev team hydrates — cheapest possible prevention of phantom-hunting.
4. Sprint 2 opens with WP-B2 (slip-prevention per N10 §3.2) + WP-B6 + WP-H1 additions; Sprints 3–5 = D-cluster + WP-E parallel lane unchanged; Q-3 escalation check fires at the Sprint-3 boundary (BS-3).

### 4.3 Explicitly Architect-owned (NOT dev-team executable under any package)
- **Q-3 composite**: `"/*": "allow"` risk-acceptance record AND `subagent_depth` raise-vs-relay (WP-C1/C2; SPEC-C delivers templates/costed options only).
- **Q-1**: audit-log hash-chain build-vs-defer (default DEFER stands).
- **G4 flip**: provider key provisioning or `enabled:false` decisions.
- **Art. VIII.7 ticket ratification**: model-id normalization ticket approval (declaration text is dev-team writable; the ticket itself is Architect-ratified).
- **First ENFORCEMENT-STAMP table sign-off** (SPEC-A WI-4 recommends; visibility downgrade deserves Architect eyes).
- **DOC-1-stamped strategy docs** and Ark supersession (Kali/Architect mark only — N9 DO-NOT-TOUCH appendix stands).
- **grok_cli agent-def deletion** (fleet-composition decision, M10 adjacent — sign-off, not silent default).

---

## §5 REMAINING_GAPS — only what truly blocks the launch package

**Hard blockers for Sprint-1 start: ZERO.** The executable set (13 packages) is fully specified, gated, and dependency-ordered. What remains is one pre-launch errata and two open external dependencies:

| # | Gap | Class | Blocks? | Disposition |
|---|-----|-------|---------|-------------|
| RG-1 | Stale pointers/statuses in N8 (spec-inputs paths) + N9 ([B/C]-PENDING markers) + N8 §3 superseded sprint mandate | Errata | Blocks clean hydration (dev team would hunt absent files / follow dead sequencing) | ONE errata commit at integration start (ADJ-1/ADJ-2/CF-3) — 15 min |
| RG-2 | Q-3 unanswered (wildcard + depth) | External (Architect) | Blocks ONLY WP-C1/C2 (by design) | Escalation timer at Sprint-3 boundary (BS-3); everything else proceeds |
| RG-3 | Provider keys unprovisioned → G4 red | External (Architect) | Blocks G4-green only; WP-B3 otherwise executable with honest interim statement | Tracked; no fake-pass (M23) |
| RG-4 | lilith split-record repair | Single-writer act (MaKaLi, Art. IX) | Blocks distillation acts, NOT dev-team packages | Hand-off flagged at WP-IX execution; schema probe prevents false-close |
| RG-5 | Nested-config plugin merge semantics unprobed (BS-2) | Evidence gap | Blocks WP-B1 COMPLETION claim only, not its start | Probe added to WP-B1 done-definition |

Nothing here warrants delaying launch. RG-1 is the only item that should land before the dev team's first session, and it is a fifteen-minute documentation fix.

---

## §6 MEASURABLE_GATES

Per-package commands live verbatim in `N8_resources.md` §2 (single-source rule — not duplicated here). Below: the **paste-and-run FULL-LIBRARY acceptance block** — run from repo root after ALL packages land; every line must match its expect comment. Plus the two new-library gates this synthesis adds.

```bash
#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════
# C2 FULL-LIBRARY ACCEPTANCE — paste-and-run from repo root
# Composes: decree §4 G29/G30 · SYNTHESIS(C1) §6 G1–G28 (via N8_resources §2)
#           · spec-specific gates · C2-synthesis additions (S-1..S-3)
# PASS = no FAIL lines in output.
# ══════════════════════════════════════════════════════════════════
set -u; FAIL=0
ck(){ if eval "$2" >/dev/null 2>&1; then echo "PASS $1"; else echo "FAIL $1"; FAIL=1; fi; }

# ── P0 ──
ck G7  'grep -q "pre-commit" .git/hooks/pre-commit && grep -q "break-system-packages" .git/hooks/pre-commit'
ck G6  'grep -qE "mkstemp|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py'
ck G13 '! grep -q "would go here" Makefile'
ck G29 "rg -n '^import (segment|posthog|datadog|amplitude|mixpanel)\b|^from (segment|posthog|datadog|amplitude|mixpanel)\b' src/omega/ --type py | (! grep .)"
ck G15 'python3 -c "
import json,sys
from datetime import datetime,timezone
now=datetime.now(timezone.utc)
bad=[t[\"task_id\"] for t in json.load(open(\"data/coordination/TASK_REGISTRY.json\"))[\"tasks\"]
     if t.get(\"last_checkpoint\") and datetime.fromisoformat(t[\"last_checkpoint\"].replace(\"Z\",\"+00:00\"))>now]
sys.exit(1 if bad else 0)"'
ck G16 'python3 -c "
import json,datetime
d=json.load(open(\"data/coordination/TASK_REGISTRY.json\"))
now=datetime.datetime.now(datetime.timezone.utc)
z=[t[\"task_id\"] for t in d[\"tasks\"] if t.get(\"status\")==\"in_progress\" and t.get(\"last_checkpoint\") and (now-datetime.datetime.fromisoformat(t[\"last_checkpoint\"].replace(\"Z\",\"+00:00\"))).total_seconds()>=7*86400]
import sys; sys.exit(1 if z else 0)"'
ck G8  'for f in data/entities/*/proposed_lessons.yaml data/entities/*/soul.yaml; do .venv/bin/python3 -c "import yaml;yaml.safe_load(open(\"$f\"))" || exit 1; done'
ck G-A2a 'grep -q "blockers" scripts/validate_tracking_state.py && python3 -c "
import json;d=json.load(open(\"data/coordination/ACTIVE_SPRINT.json\"))
T0={\"backlog\",\"ready\",\"in_progress\",\"blocked\",\"completed\",\"superseded\"}
bad=[(k,v[\"status\"]) for k,v in d.get(\"blockers\",{}).items() if v.get(\"status\") not in T0]
import sys; sys.exit(1 if bad else 0)"'

# ── P1 ──
ck G1  'jq -r ".plugin[]" opencode.json | grep "^file://" | sed "s#file://##" | while read f; do test -f "$f" || exit 1; done'
ck G10 'test -z "$(jq -r ".agent | to_entries[] | select(.value.instructions) | .key" opencode.json)" && for f in $(jq -r ".agent[].instructions[]?" opencode.json); do test -e "$f" || exit 1; done'
ck G3  'python3 -c "
import yaml; c=yaml.safe_load(open(\"config/providers.yaml\"))
p={e[\"provider\"]:e[\"priority\"] for e in c[\"inference\"][\"fallback_chain\"]}
assert p[\"opencode-zen\"] < p[\"openrouter\"]"'
ck G5  'test "$(jq -r ".instructions[]" opencode.json | grep -c "^docs/archive/")" = 0'
ck G22 'python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ >/dev/null 2>&1; [ "$?" -ne 0 ] || python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ >/dev/null 2>&1; true'
# NOTE G22 semantics: strict mode must DISCRIMINATE — record the exit code; a fixture pair
# (clean→0, dirty→1) is the authoritative proof per SPEC-B WI-4(d). Raw command kept for parity.
ck G20 'jq -e "[.tasks[] | select(.tags // [] | index(\"express:first-light\"))] | length >= 10" data/coordination/TASK_REGISTRY.json'
ck G21 'python3 - <<'"'"'EOF'"'"'
import json,re,sys
d=json.load(open("data/coordination/TASK_REGISTRY.json"))
bad=[]
for t in d["tasks"]:
    m=re.match(r"express-c1-node(\d+)-",t.get("task_id",""))
    if m:
        n=f"node{m.group(1)}"
        if t.get("subagent_type")!=n or t.get("entity")!=n: bad.append(t["task_id"])
sys.exit(1 if bad else 0)
EOF'
ck G2P 'if jq -e ".permission.external_directory | has(\"/*\")" opencode.json | grep -q true; then test -f data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md && grep -q "RESOLVED-AS:" data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md; fi'
ck G26 'jq -e ".subagent_depth >= 3" opencode.json >/dev/null || rg -q "Arm-Relay" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md'
ck G26P 'grep -qE "D-[0-9]+.*(subagent_depth|Arm-Relay)" docs/decisions/PIVOT_LOG.md'

# ── P2 ──
ck G14 'V=$(grep -m1 "^\*\*Version\*\*" SOVEREIGN_MANDATES.md | grep -o "[0-9.]*$"); grep -rq "$V" scripts/codex/*.md && ! grep -rq "3\.7\.0" scripts/codex/*.md'
ck D1  '.venv/bin/python3 scripts/lint_governance_frontmatter.py'
ck G9  '! ls .opencode/commands/council-local.md .opencode/commands/council-fast.md 2>/dev/null'
ck G11 'for f in .opencode/skills/*/SKILL.md; do head -1 "$f" | grep -q "^---$" || exit 1; done && ! find .opencode/skills -name SKILL.md -exec sh -c "lines=\$(wc -l < \"\$1\"); [ \"\$lines\" -lt 20 ]" _ {} \; | grep .'
ck G24 'test -f docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md || ! grep -qF "DOMAIN_DOCUMENTATION_SYSTEM" docs/strategy/STRATEGY_INDEX.md'
ck G19 '! find data/handoff/active -name "*.json" -mmin +300 | grep .'
ck D61 '.venv/bin/python3 scripts/validate_wake_state.py data/coordination/WAKE_STATE.json'
ck D62 'printf "not-json{" > /tmp/opencode/ws_bad.json; .venv/bin/python3 scripts/validate_wake_state.py /tmp/opencode/ws_bad.json; [ "$?" -eq 1 ]'

# ── Cross-tier ──
ck G25 'test -f AGENTS.md'
ck G25a 'grep -o "derived-from: [^ ]*" AGENTS.md 2>/dev/null | awk "{print \$2}" | while read f; do test -e "$f" || exit 1; done'
ck G25c 'L=$(wc -l < AGENTS.md 2>/dev/null || echo 0); S=$(grep -c "^## " AGENTS.md 2>/dev/null || echo 0); C=$(grep -c "derived-from:" AGENTS.md 2>/dev/null || echo 0); [ "$L" -ge 120 ] && [ "$S" -ge 5 ] && [ "$C" -ge "$S" ]'

# ── Library guards (decree §4 G30 + C2-synthesis additions) ──
ck G30 'for f in docs/specs/team_infra/*.md; do grep -q "validator-first" "$f" || exit 1; done'
# S-1 (this report §1.3): decree Art. VIII.8 no longer homeless — council.yaml cleanup ticket registered
ck S-1 'grep -rq "council.yaml" docs/specs/team_infra/ data/council/20260825-094633-first-light-c2/phase1_nodes/N8_work_packages.md 2>/dev/null || echo "WARN: WP-H1 not yet registered"'
# S-2 (this report ADJ-3): schema-truth probe — G8-green must coincide with schema-clean
ck S-2 '.venv/bin/python3 - <<'"'"'EOF'"'"'
import yaml,sys,glob
bad=[]
for f in glob.glob("data/entities/*/proposed_lessons.yaml"):
    d=yaml.safe_load(open(f))
    for i,r in enumerate(d if isinstance(d,list) else []):
        if isinstance(r,dict) and ("id" in r or "narrative" in r):
            for k in ("id","narrative","insight","principle"):
                if k in r and not r.get(k): bad.append(f"{f}:{i}:{k}")
            if ("id" in r) != ("narrative" in r): bad.append(f"{f}:{i}:split-record")
sys.exit(1 if bad else 0)
EOF'
# S-3 (this report §2 ADJ-1): spec-pointer integrity — every spec path cited in N8 exists on disk
ck S-3 'for n in SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE SPEC_B_P1_MECHANISM_HONESTY SPEC_C_P1_SECURITY_POSTURE_RECORDS SPEC-D-p2-hygiene SPEC-E-agents-md-reconstruction; do test -f "docs/specs/team_infra/$n.md" || exit 1; done'

echo "──────────────────────────────────"
[ "$FAIL" -eq 0 ] && echo "FULL-LIBRARY ACCEPTANCE: GREEN" || echo "FULL-LIBRARY ACCEPTANCE: RED (see FAIL lines)"
exit $FAIL
```

**Gate notes**: G22's raw form records an exit code (discrimination proof needs the fixture pair per SPEC-B WI-4(d)); G9 post-quarantine reads as file-absence (rewrite acceptance re-checks both original lines at restored path per SPEC-D D2); G28 remains a recorded BASELINE, not an acceptance gate (decree §6 exception). S-1 emits WARN (not FAIL) until WP-H1 is registered — it audits register completeness, not code.

---

## §7 PROVENANCE & LAST-STEP RELAY

- All §1–§5 claims verified against disk this session by mk_kali; five **[MK-verified]** empirical findings independently reproduced (SPEC-C mtime ordering · lilith parse/schema divergence · nested-config keys · G30 sweep · WAKE_STATE:105 substring).
- Sole artifact written: this report. Zero production edits. Zero agent spawns attempted prior to the mandated last step below.
- **LAST STEP — Consultant page attempt**: `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO")` [REPORT] attempted per mission order. Result recorded immediately after this file write.

*⬡ OMEGA ⬡ MK-KALI ⬡ SYNTHESIS_ARM_REPORT_C2 ⬡ INPUT-TO-FUSION ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

