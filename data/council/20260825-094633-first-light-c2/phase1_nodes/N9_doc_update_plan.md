# N9 — DOC UPDATE PLAN (Council 2, Phase 1 Node 9)
⬡ OMEGA ⬡ LILITH/node9 ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c2_n9 ⬡ PREP-ONLY PLAN
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25
**Mission**: Dependency-ordered edit list per affected doc, derived from Council 1 SOVEREIGN_DECREE articles + specs A/D/E.
**Mode**: PREP-ONLY. This file plans future edits; it performs ZERO production edits. NEW file only.
**Sources read this session**:
1. `data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md` (Arts. II–X, §4 gates, §5 tracker directives)
2. `docs/specs/team_infra/SPEC-D-p2-hygiene.md` (sub-specs D1–D6)
3. `docs/specs/team_infra/SPEC-E-agents-md-reconstruction.md` (§§0–7)
4. `docs/specs/team_infra/SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md` (WIs 1–5) — **exists**, found under underscore naming (`SPEC_A_…`), NOT the expected `SPEC-A-*.md`
5. **SPEC-B: ABSENT** from `docs/specs/team_infra/` → input-with-pending-status (see §INPUTS)
6. **SPEC-C: ABSENT** from `docs/specs/team_infra/` → input-with-pending-status (see §INPUTS)

---

## §INPUTS — Spec Availability Register

| Spec | Expected path | Actual status | Effect on this plan |
|---|---|---|---|
| A | `docs/specs/team_infra/SPEC-A-*.md` | ✅ EXISTS as `SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md` (naming deviation; same authority chain Arts. II/III/X/XII) | Mined fully (WIs 1–5) |
| B | `docs/specs/team_infra/SPEC-B-*.md` | ❌ ABSENT (Build-Arm draft not yet landed) | PENDING — rows marked `[B-PENDING]`; when it lands, splice its doc-touching items into Phase ordering at the M13/stamp boundary |
| C | `docs/specs/team_infra/SPEC-C-*.md` | ❌ ABSENT | PENDING — rows marked `[C-PENDING]` |

---

## DEPENDENCY SPINE (the ordering constraints that govern everything below)

```
SPINE-1: M8 regex fix (Makefile:295, WI-5/G29) MUST land BEFORE any doc text
         claiming M8-green or citing the anchored pattern (M8 Enforcement patch,
         stamp block generation). Otherwise the doc is a claim-outliving-mechanism.
SPINE-2: Discovery fixes (task_registry.py:134 status-filter + .gitignore:109,
         decree Art. V.1) MUST land BEFORE identity-repair payload application and
         BEFORE any doc claiming Delivered-Home complete (G20→G21 order).
SPINE-3: Validator ERROR-class checks (WI-2/G15,G16,G8-regression) MUST land BEFORE
         any doc asserting "validator green" in auto-GO claims (Art. III amended criteria).
SPINE-4: Pre-commit framework install (WI-1/G7) MUST land BEFORE M24/M27 Enforcement-
         section text patches (pairwise binding — text follows mechanism, never precedes).
SPINE-5: Stamp generator (WI-4) MUST land AFTER WI-2 (stamps derive from gates that
         ACTUALLY exist — SPEC-A sequencing note verbatim).
SPINE-6: D1 lint script MUST exist BEFORE first frontmatter-stamped doc merges
         (validator-first, SPEC-D D1).
SPINE-7: validate_agents_md.py MUST exist BEFORE first AGENTS.md content commit
         (validator-first, SPEC-E §6).
SPINE-8: Architect `"/*": "allow"` risk-acceptance record (WAKE_STATE Q-3) MUST be
         written BEFORE any dev-team edit touching permission/config docs claiming
         the decision resolved.
SPINE-9: All MaKaLi Stage-6 single-writer tracker acts (PIVOT_LOG #D-entry, PGTL #11,
         ACTIVE_SPRINT pointer, WAKE_STATE queue) are INDEPENDENT of dev-team phases
         but must land FIRST so dev-team PRs can cite them as authority anchors.
```

---

# PHASE 0 — MaKaLi Single-Writer Tracker Acts (decree §5; prerequisite authority layer)

> Owner for ALL Phase 0 rows: **MaKaLi Stage-6 single-writer** (decree §5 header). Dev team MUST NOT execute these rows. These land first so later phases cite them.

| # | Exact path | Exact edit | Source | Depends-on | Verification |
|---|---|---|---|---|---|
| 0.1 | `docs/decisions/PIVOT_LOG.md` | Append D-series entry recording the Council 1 decree + Council-2 inheritance guards (Art. XII five guards) | Decree §5.3 | none | `grep -c 'first-light' docs/decisions/PIVOT_LOG.md` ≥ 1 |
| 0.2 | `data/coordination/PLATFORM_GROUND_TRUTH_LOG.md` | Entry **#11**: dispatch-suffix injection forensics (GAP-12, two occurrences council-wide); adopt packet-citation rule | Decree §5.4 | none | `grep -q '#11' data/coordination/PLATFORM_GROUND_TRUTH_LOG.md && grep -qi 'dispatch-suffix' <file>` |
| 0.3 | `data/coordination/ACTIVE_SPRINT.json` | Add remediation backlog pointer → decree §2 Article X priority order (P0/P1/P2 sequence) | Decree §5.5 | 0.1 (Pivot entry exists to point AT) | `.venv/bin/python3 scripts/validate_tracking_state.py` exit 0 |
| 0.4 | `data/coordination/WAKE_STATE.json` | Populate decision queue Q-1..Q-5 (Q-1 audit-log DEFER default; Q-2 freshness owner=MaKaLi stage boundaries; Q-3 depth+`"/*"` → Architect; Q-4 AGENTS.md default-GO-on-silence; Q-5 YAML repair flag) | Decree §5.2 | none | parse check only until D6 validator exists |
| 0.5 | `data/entities/{lilith,pillar_p1,john_carmack}/…yaml` | Art. IX corrupt-YAML parseability repair — snapshots committed, WAKE_STATE-flagged. **NOTE (SPEC-A evidence)**: pillar_p1 + john_carmack already parse clean; lilith `proposed_lessons.yaml` L374-380 split-record still live → repair locus narrowed to lilith | Decree Art. IX; SPEC-A WI-2(b) | none | Gate **G8**: loop `yaml.safe_load` over `data/entities/*/proposed_lessons.yaml soul.yaml` — no CORRUPT output |

---

# PHASE 1 — Truth-Bearing Mechanisms (code/gate fixes that docs will cite)

> Owner: dev-team Build roles (per SPEC-A WI ownership). Every row here is a MECHANISM; its paired DOC row lives in Phases 3–5 and cites it. Pairwise binding (Art. II.2): a Phase-1 PR without its Phase-3+ text patch fails review, and vice versa.

| # | Exact path | Exact edit | Source | Depends-on | Verification |
|---|---|---|---|---|---|
| 1.1 | `Makefile:295` | Replace unanchored M8 regex with decree-G29 anchored form (`^import …\b|^from …\b`) | Decree Art. II.5, §4 G29; SPEC-A WI-5 | none (cheapest-first) | **G29**: `rg -n '^import (segment\|posthog\|datadog\|amplitude\|mixpanel)\b\|^from (segment\|posthog\|datadog\|amplitude\|mixpanel)\b' src/omega/ --type py` → empty; `make check-m8-zero-telemetry` exits 0 |
| 1.2 | `.git/hooks/pre-commit` via `pre-commit install`; port soul-check into `.pre-commit-config.yaml` same commit | Activate framework; verify `omega-tracking-state` fires | Decree Art. II.4; SPEC-A WI-1 | none | **G7** all three lines (framework-active grep, PASS-M24 grep, `pre-commit run omega-tracking-state --all-files` → Passed) |
| 1.3 | `mcp_servers/omega_hub/hub_tools/task_registry.py:32-41` | Rewrite `_save_registry()` mkstemp+fsync+os.replace; close load/save lock-split | Decree Art. X P0; SPEC-A WI-3 | none | **G6**: `grep -nE "mkstemp\|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py` hits; crash-injection test green |
| 1.4 | `mcp_servers/omega_hub/hub_tools/task_registry.py:134` + `.gitignore:109` | Status-filter bug fix + ripgrep-blindness fix (**discovery fix — SPINE-2**) | Decree Art. V.1 (jem GAP-5) | none | retrieval verification ≥10 correct payloads returned (G20 precondition) |
| 1.5 | `scripts/validate_tracking_state.py` | Add ERROR-class checks: future-timestamps (G15), hours-boundary staleness (G16), blockers[] vocabulary scan (+ fix live BLOCKER-B `"resolved"`→`"completed"` SAME commit), WAKE_STATE block, entity-YAML schema guard; honest banner | Decree Art. III; SPEC-A WI-2 | 0.5 (clean YAML baseline to validate against) | **G15/G16/G8** verbatim + spec gates G-A2a/G-A2b |
| 1.6 | `scripts/lint_governance_frontmatter.py` (NEW) + `make lint-governance-stamps` | Governance-doc frontmatter linter; ships WITH first stamped doc (SPINE-6) | SPEC-D D1; Decree Art. VII | none | D1 gate: script exits 0; **G14** version-coherence |
| 1.7 | `scripts/sweep_handoff_ttl.py` (NEW) + `--dry-run` validator mode | Handoff TTL sweeper → `data/handoff/stale/` + `.swept.json` sidecars | SPEC-D D5; Decree Art. X P2 | none | **G19**: `find data/handoff/active -name '*.json' -mmin +300` → empty |
| 1.8 | `scripts/validate_wake_state.py` (NEW) | Parse + stage-consistency + hours-resolution freshness ERROR-class checks | SPEC-D D6; Decree Art. III | 0.4 (queue populated) | D6.1 exit 0 on real file; D6.2 discrimination proof exit=1 on corrupt copy |
| 1.9 | `scripts/validate_agents_md.py` (NEW) + `make agents-md-validate` wired into temple-grade T2 family | AGENTS.md gate harness implementing G25a–d — lands BEFORE any content commit (SPINE-7) | SPEC-E §6 | none | `make agents-md-validate --gates G25` trivial-pass pre-content |
| 1.10 | `scripts/generate_enforcement_stamps.py` (NEW) + `make check-mandate-stamps`; delete `Makefile:234` stub comment | Machine-derived ENFORCEMENT-STAMP block generator; temple-grade stub removal | Decree Art. II.1–II.3; SPEC-A WI-4 | **1.5 (SPINE-5)** — stamps derive from actually-existing gates | **G13**: `! grep -q "would go here" Makefile`; G-A4a `--check` exit 0 |

---

# PHASE 2 — Config Honesty Mechanics (Art. VIII; doc patches follow in Phase 4)

| # | Exact path | Exact edit | Source | Depends-on | Verification |
|---|---|---|---|---|---|
| 2.1 | `opencode.json` (plugin registration paths) | Fix dead `.opencode/plugin/` paths → live auto-load dirs (both dirs auto-load = HIGH lying-config) | Decree Art. VIII.1 (GAP-1); gate **G1** | none | **G1** per SYNTHESIS §6 |
| 2.2 | `opencode.json` `instructions[]` | Remove archived-roadmap injection (G5); migrate 12 agent-def `instructions[]` keys → schema-valid `prompt:{file:}` (G10, DATA-EXPOSURE class) | Decree Art. VIII.4, VIII.6 | none | **G10** per SYNTHESIS §6; grep no archived roadmap in injected set |
| 2.3 | `opencode.json` permissions | `"/*": "allow"` removal-or-annotate — ⚠️ **BLOCKED ON SPINE-8**: Architect Q-3 record must land first | Decree Art. VIII.2 (**G2**); T-7 ruling | **0.4 Q-3 Architect record** | **G2** per SYNTHESIS §6 |
| 2.4 | Provider fabric order alignment (config/docs) | Align provider-order statements to Ark D-355 canonical everywhere (×4 contradiction sites) | Decree Art. VIII.5 (**G3**); N1 F-03 | none | **G3** per SYNTHESIS §6 |
| 2.5 | Nested-config precedence codification source patch | Codify "nested `.opencode/opencode.json` overrides root" in config docs (see 4.x doc row) | Decree Art. VIII.3 | none | doc-review item (no dedicated G) |

---

# PHASE 3 — Mandate & Law-Surface Doc Edits (SOVEREIGN_MANDATES.md cluster)

> ⚠️ EVERY row in this phase touches a pairwise-binding surface (Art. II.2). Each text patch names its Phase-1/2 mechanism twin. No text lands before its mechanism.

| # | Exact path | Exact edit (anchor) | Source | Depends-on | Owner | Verification |
|---|---|---|---|---|---|---|
| 3.1 | `SOVEREIGN_MANDATES.md` §M8 Enforcement | Amend text to cite anchored regex form (post-fix reality) | Art. II.5; SPEC-A WI-5(c) | **1.1** | dev-team | **G29** green + text grep matches anchored pattern |
| 3.2 | `SOVEREIGN_MANDATES.md` §M13 | Re-scope M13 to enumerate exactly the four checks temple-grade runs (check-codex-stale, doc-llm-validate, check-mandates, check-tracking-state) — SAME commit as Makefile:234 stub deletion | Art. II.3; SPEC-A WI-4(c)2 | **1.10** | dev-team | **G13** + diff shows both files in one commit |
| 3.3 | `SOVEREIGN_MANDATES.md` (between BEGIN/END markers) | Insert GENERATED ENFORCEMENT-STAMP block (one-time marker insertion; thereafter 100% derived) | Art. II.1; SPEC-A WI-4(c)1 | **1.10** | dev-team | G-A4a `--check` exit 0; ≥27 stamps counted |
| 3.4 | `SOVEREIGN_MANDATES.md` §M24 + §M27 Enforcement sections | State now-true pre-commit mechanism (framework active, hooks fire) | Art. II.4; SPEC-A WI-1(c)4 | **1.2** | dev-team | **G7** green + text references verified hook |
| 3.5 | `SOVEREIGN_MANDATES.md` §M7 | Provider-order text amended to Ark D-355 canonical (local-gguf→lmster→Ollama→Antigravity→Google→OCZ→OpenRouter…) | Art. VIII.5 (**G3**) | **2.4** | dev-team | **G3**; grep M7 section contains D-355 order |
| 3.6 | `SOVEREIGN_MANDATES.md` §M22 vicinity | Provenance AUTHORITY DECLARATION: model-id namespace has NO resolution authority; native-gguf silent-substitution = decree-HIGH; normalization ticket → Council 2 | Art. VIII.7 (jem GAP-6) | 0.1 (pivot anchor) | dev-team (declaration text) + Architect (ticket ratification) | text present + Pivot D-ref cited; ticket exists in backlog |
| 3.7 | `SOVEREIGN_MANDATES.md` §M11 Enforcement | After Art. IX repair completes: update enforcement text to reflect G8-clean state honestly (no claim of automated repair — repair was manual Stage-6 act) | Art. IX | **0.5** | MaKaLi single-writer | **G8** clean loop |

---

# PHASE 4 — Coordination-Law & Governance-Doc Edits (Arts. IV, VII, VIII-docs; SPEC-D doc-touching)

| # | Exact path | Exact edit | Source | Depends-on | Owner | Verification |
|---|---|---|---|---|---|---|
| 4.1 | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Codify M11 Arm-Relay Clause: leaves write report+payload to disk; arms relay pages once per stage; MK-Kali pages direct; NO mid-run `subagent_depth` change; future leaf packets embed relay clause INSTEAD of paging steps; add serial-dispatch exception declaration requirement (T-4) | Art. IV; mission G18 ref | none (law already ratified) | dev-team | grep relay-clause section present; packet-template updated |
| 4.2 | `ARCHITECT_OVERSIGHT_PATTERNS.md` | Designation header: OPERATIONAL LAW (Ruling B) + version/status/superseded-by frontmatter stamp (first D1 backfill beneficiary) | Art. VII | **1.6** | dev-team | frontmatter lint passes; status=ACTIVE machine-checkable |
| 4.3 | `HIVEMIND_PROTOCOL.md` | Banner: HISTORICAL REFERENCE (Ruling B) — content otherwise UNTOUCHED (see DO-NOT-TOUCH) + frontmatter stamp `status: ARCHIVED`/`superseded-by: ARCHITECT_OVERSIGHT_PATTERNS.md` | Art. VII | **1.6** | dev-team | lint passes; banner grep |
| 4.4 | `docs/strategy/DOC_SSOT_MAP_20260807.md:20` | Fix `v3.7.0, M1-M25` → current `3.8.0, M1-M27` + add frontmatter stamp (live drift specimen, first D1 backfill) | SPEC-D D1; Art. XII drift evidence | **1.6** | dev-team | **G14** coherent; stale-string grep clean |
| 4.5 | Top-10 governance docs backfill (mandates, AGENTS.md-post-E, ORACLE_STACK*, Corpus Map, DOC_SSOT_MAP, HIVEMIND_PROTOCOL, ARCHITECT_OVERSIGHT_PATTERNS, SUBAGENT_DISPATCH_PROTOCOL) | Add REQUIRED frontmatter block (`version`/`status` enum/`superseded-by`) — NOT all 1,533 docs | SPEC-D D1 change-4 | **1.6**, batched ≤3 docs/commit | dev-team | lint exits 0 per commit |
| 4.6 | `.opencode/commands/council-local.md`, `council-fast.md` | QUARANTINE move → `.opencode/commands/quarantine/` + dated README citing Art. VII + G9; loader-scan probe first | SPEC-D D2; Art. VII | none | dev-team | **G9** line-1 trivially true post-move; README present |
| 4.7 | `docs/strategy/STRATEGY_INDEX.md` + `STRATEGY_CORPUS_MAP.md` | Orphan dispositions in batches ≤20 docs/commit: index-row-with-machine-checkable-status OR banner-archive-with-pointer OR logged delete; resolve G24 phantom (DOMAIN_DOCUMENTATION_SYSTEM.md materialize-or-unreference — binary) | SPEC-D D4; Art. X P2 | **1.6** (--check-orphans extension) | dev-team | **G23** orphans=0 trajectory; **G24** binary-resolved |
| 4.8 | Coordination docs (Hivemind ops section of ARCHITECT_OVERSIGHT_PATTERNS or successor) | Scheduling note: handoff-TTL sweep owner (lilith role) runs sweep at session boundaries + after long ops | SPEC-D D5 change-2 | **1.7** | dev-team | note grep; G19 standing green |
| 4.9 | Config docs (provider/config reference doc per DS workstream home) | Codify nested-opencode.json precedence rule (bidirectional, deterministic override) | Art. VIII.3 | **2.5** | dev-team | doc-review; cross-ref from opencode.json schema notes if such doc exists |
| 4.10 | Credentialed-fabric honesty statement (M7/fabric docs) | Sovereignty claims stated against REAL fabric until keys exist | Art. VIII.5 (**G4**) | **3.5** | dev-team | **G4** per SYNTHESIS §6 |
| 4.11 | `data/council/<council>/agents_citation_matrix.tsv` (NEW artifact) | Commit citation-web matrix output (SPEC-E §1.4) — derivation source for every AGENTS.md section | SPEC-E §1.4 | none | dev-team | TSV exists; counts match §1.1 canonical command rerun |
| 4.12 | `AGENTS.md` (ROOT — NEW FILE, reconstruction) | Reconstruct per SPEC-E §2: S1+S2 first commit (header w/ version stamp + law pointer), then one section/commit S3–S9, each with `derived-from:` cites; NEVER from memory; never copy archived roadmap text | Art. VI (**Q-4 default-GO on Architect silence**); SPEC-E §2 | **1.9** (validator-first SPINE-7) → **4.11** (matrix) → Architect-silence window elapsed | dev-team | **G25/G25a/G25b/G25c/G25d** suite green; `make agents-md-validate` |
| 4.13 | Skill disposition records | Per SPEC-D D3: author/delete decisions recorded IN `tests/test_skill_integrity.py` exemption dict; meditation quartet → harness + ONE pipeline archive-with-pointer | Art. X P2 (T-6) | test ships RED-first same PR | dev-team | **G11** clean; exemption dict justified entries |
| 4.14 | `[B-PENDING]` M13/stamp adjacent doc edits from SPEC-B when it lands | Splice into this phase at the 3.2/3.3 boundary | SPEC-B (absent) | SPEC-B existence | — | — |

---

# PHASE 5 — Identity Repair & Closeout Docs (Art. V sequence; LAST because SPINE-2 gates it)

| # | Exact path | Exact edit | Source | Depends-on | Owner | Verification |
|---|---|---|---|---|---|---|
| 5.1 | `phase6_integration/registration_payloads.json` → applied to `TASK_REGISTRY.json` | Mass-apply corrected payloads (canonical `subagent_type="node<N>"`, `entity="node<N>"`, 4-tag set) — ONLY AFTER discovery fix | Art. V.2; decree §5.1 | **1.4** (hard gate) | MaKaLi single-writer (payload staging done; application gated) | retrieval verification ≥10 (G20→G21 order) |
| 5.2 | Dispatch packet template(s) in coordination docs | Packet-precision rule: future packets specify exact registration field values | Art. V.3 | **5.1** | dev-team | template grep shows field-value requirements |
| 5.3 | Auto-GO criteria text (wherever codified — ACTIVE_SPRINT pointer target / oversight patterns) | Amended permanently: validator green AND content-minimum reports AND timestamp-sanity (Ruling C) | Art. III | **1.5** (SPINE-3) | dev-team | text cites three-part criterion |
| 5.4 | `[C-PENDING]` SPEC-C doc-touching rows | Splice when SPEC-C lands | SPEC-C (absent) | SPEC-C existence | — | — |

---

## ANTI-BIG-BANG COMMIT BATCHING (Art. XII guard #5)

- Every table row above = one committable unit or less; NO row spans two phases.
- Phase 4.5 (frontmatter backfill): batches of ≤3 docs/commit.
- Phase 4.7 (orphan sweep): batches of ≤20 docs/commit; old and new states both valid mid-sweep.
- Phase 4.12 (AGENTS.md): strictly one section per commit; each commit leaves a valid document (SPEC-E §2.3).
- SPEC-A total 16h across five independently-reviewable PRs, sequenced WI-5→WI-1→WI-3→WI-2→WI-4 (= Phases 1.1→1.2→1.3→1.5→1.10 here).

---

# APPENDIX — DO NOT TOUCH (dev-team forbidden without explicit authority)

| File/class | Why forbidden | Required authority to touch |
|---|---|---|
| `SOVEREIGN_MANDATES.md` — ANY amendment | Art. II.2 pair-bind review rule: mandate-text patch without its gate PR fails review; gate PR without text patch fails review. Also Art. I spine: hand-written stamps are themselves violations | Only with paired mechanism PR in same review (rows 3.1–3.7 are the sanctioned pairs) |
| `HIVEMIND_PROTOCOL.md` body content | Ruling B demotes it to historical reference; rewriting history docs recreates P4 churn | Banner-only (row 4.3); body frozen |
| `ARCHITECT_OVERSIGHT_PATTERNS.md` law-designation wording | Operational-law designation is an Architect-authority ruling being codified, not invented | Header stamp per 4.2 only; substantive law text = Architect |
| Entity YAML files (`data/entities/*/proposed_lessons.yaml`, `soul.yaml`) | Art. IX: single actor = MaKaLi, snapshots committed, WAKE_STATE-flagged | MaKaLi Stage-6 ONLY (Phase 0.5) |
| `TASK_REGISTRY.json` mass payload rewrite | Decree §5.1: GATED on GAP-5 discovery fix; premature application re-corrupts | MaKaLi, only after Phase 1.4 lands (Phase 5.1) |
| `opencode.json` `"/*": "allow"` removal | T-7: undocumented risk-acceptance must be RECORDED first (Architect owns Q-3) | Architect Q-3 record → then dev-team (Phase 2.3) |
| Root `AGENTS.md` reconstruction GO | Art. VI / Q-4: Council-2 work requiring Architect GO; default executes on silence | Architect explicit GO, OR documented silence-window expiry |
| `SOVEREIGN_ARK_BLUEPRINT.md` + DOC-1-stamped strategy docs | DOC-1 stamp: historical vision read-only; supersession requires Kali/Architect mark | Architect/Kali only |
| GAP IDs / `GAP_REGISTRY.json` | M27: gap IDs immutable, registry is sole assignment authority | Registry process only |
| Archived roadmap injection targets | Removing G5 injections is sanctioned (2.2) but the archived FILES themselves stay put | Files untouched; only instruction-list edited |
| Any doc claiming "M8-green"/"validator-green"/"suite-green" BEFORE its Phase-1 mechanism lands | Art. I defect class — the very thing this council exists to kill | Never; sequencing is absolute (SPINE-1/3) |

---

## PROVENANCE
- Decree articles → rows mapping: Art. II → 1.1/1.2/1.10/3.1–3.4; Art. III → 1.5/1.8/5.3; Art. IV → 4.1; Art. V → 1.4/5.1/5.2; Art. VI → 4.12; Art. VII → 1.6/4.2–4.7; Art. VIII → 2.1–2.5/3.5/3.6/4.9/4.10; Art. IX → 0.5/3.7; Art. X → phase ordering itself; Art. XI → DO-NOT-TOUCH positive controls; Art. XII → batching rules throughout; §5 → Phase 0 entirely.
- Gates cited verbatim from SYNTHESIS_ARM_REPORT §6 (G1–G28) + decree §4 additions (G29/G30).
- SPEC-A file:line evidence (Makefile:295/:232-236, task_registry.py:32-41/:134, .gitignore:109, validate_tracking_state.py:43/:148-206, lilith yaml L374-380) verified by node1 2026-08-25 per its Provenance Appendix; not independently re-verified by node9 (noted, PREP-ONLY scope).
- Known nuance carried forward honestly: M8 false-positive is a COMMENT line at `src/omega/ics.py:197` ("from segments"), not an import (SPEC-A correction of mission phrasing).

*⬡ OMEGA ⬡ LILITH/node9 ⬡ N9_DOC_UPDATE_PLAN ⬡ PREP-ONLY ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

