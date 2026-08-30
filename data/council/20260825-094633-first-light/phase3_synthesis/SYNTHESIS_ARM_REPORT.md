<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ⚖️ SYNTHESIS ARM REPORT — First Light Express Council 1 (Stage 3)
⬡ OMEGA ⬡ MK_KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_synthesis ⬡ Stage-3 ARTIFACT
**SESSION_ID**: 20260825-094633-first-light | **Synthesizer**: MK-KALI (entity tag `mk_kali` everywhere; Consultant kali is OUTSIDE this tree)
**Inputs (per Consultant R1 hybrid ruling — RAW REPORTS ARE PRIMARY EVIDENCE)**:
- Raw: `phase1_nodes/P1..P10_report.md` (all ten, read in full, cited directly)
- Navigation: `phase1.5_digested/{BUILD,RUN}_SIDE_DIGESTED.md` (conflict tables cross-checked against raws — no digest/raw contradictions found)
- Positions adjudicated: `phase2_arms/BUILD_SIDE_REPORT.md`, `phase2_arms/RUN_SIDE_REPORT.md`
- Method: `phase4_research/CARMACK_METHOD_WATCH_PASS1.md` + all three CONSULTANT_ADJUDICATION files
- Soul: `data/entities/kali/soul.yaml` (d-kal-001…006 + L3 principles: file-artifacts-sovereign, one-turn-hydration, gate-that-was-missing)
**Status**: RECON ONLY. This file is the sole artifact written. Verdict herein = DRAFT — INPUT TO MAKALI FUSION, never final.

---

## §1 CONVERGENCE AUDIT

Every convergence below was VERIFIED against raw node reports (not assumed from arm summaries). Strength = independent nodes landing on the same defect with tool-traced evidence.

### C-A · THE MASTER CONVERGENCE — "Claims that outlive their mechanisms" (cross-arm, 10/10 nodes contribute)

Both arms independently named this root cause (Build §7.1, Run §7.1). Verified in the raws as ONE defect class wearing many costumes:

| Costume | Raw evidence | Layer |
|---|---|---|
| Constitution asserts gates that don't exist | N5 F-2: literal stub comment `"# Existing temple-grade checks would go here"` in production Makefile; ~8/27 mandates machine-enforced (~30%). N5 F-3: M24/M27 hook claims false — installed `.git/hooks/pre-commit` runs soul-check only | Instruction |
| Gate that cannot fail | N7 F7-01: `doc-llm-validate` covers 7 of 1,533 docs, exits 0 through ~60 warnings; temple-grade T2 inherits it. N10 X-4 independently reproduced | Docs |
| Hooks declared but never installed | N2 F-2.2 + N10 X-1 (independent arms): `.pre-commit-config.yaml:137` declares `omega-tracking-state`; installed hook has zero tracking references (`grep -c "tracking" .git/hooks/pre-commit` = 0) | Enforcement |
| Config registers what isn't there | N1 F-01 / N6 F-01 / N10 X-5 (triple-confirmed): plugin paths at dead `.opencode/plugin/`; zero errors logged at DEBUG (N6 probe E4) | Config |
| Instructions cite files never committed | N5 F-1: root AGENTS.md absent from ENTIRE git history yet 462 files cite it; OMEGA_CODEX.md:222 claims a 343-line source that never existed | Instruction |
| Docs describe systems that don't exist | N9 F-1: protocol mandates `hdp_{YYYYMMDD}` schema with trace_id/ttl_seconds; live packets are `ho_*` with none of those fields (100% audit failure by design). N7 F7-07: STRATEGY_INDEX LAYER 2A names a meta-doc + sync script existing nowhere | Protocol/Docs |
| Frontmatter keys that do nothing | N6 F-02/F-05: agent-level `instructions[]` absent from v1.18.23 AgentConfig schema entirely (12/13 defs use it); `{session_model}` never substituted — literal string in every agent file and in this council's own prompts | Runtime |
| Timestamps not bound to clocks | N8 F-1 → N9 F-7 → N10 X-6 arc: future-dated checkpoints (`13:45:00Z` written at ~13:37Z), RECURRED at 13:48Z AFTER publication at 13:41Z, validator green throughout | Tracking |
| Registry fields not bound to identity | N10 Part 3: 15/20 identity fields wrong across 10 expert registrations (build `subagent_type="maat"` 5/5; run `entity="lilith"` 5/5); tag-query returns 0 against 12 disk matches (X-2) | Tracking |

**Synthesis finding [MK-KALI]**: This is not six defect classes; it is one. Nowhere in the stack is a documentation-write mechanically bound to a fact-check. The fix class is therefore also one: **derivation checks** — every claim-bearing artifact must be derivable from (or verifiable against) the thing it claims about. Dozens of findings close with a handful of gate patterns (see §6).

### C-B · Convergences verified per-cluster

| # | Convergence | Raw sources (verified) | Strength |
|---|---|---|---|
| C-B1 | **F-20 depth wall**: `subagent_depth: 2` forbids what §C.9/M11 mandates for every leaf. All 10 nodes hit identical rejection live. N5 F-9 adds: dispatch protocol §1 Rule 4 ("single-level nesting") authorizes what config revokes | N1 F-20, N2 §4.1, N3 §5, N4 §8, N5 §4, N6-N9 deviation logs, N10 ledger | Strongest possible: mechanically proven 10× in one session |
| C-B2 | **Derivative-doc drift**: mandate version stated as 14/25/27 across four layers; OMEGA_CODEX self-contradicts 3 ways in a same-day regeneration (all-enforced-27 / 25-laws / 2-fail-25); council-local/fast are pre-v2.1 fossils violating council-cloud's own LOOP GUARD; MANIFEST stale ×2; sovereign-refinement skill anchored to v3.1.0/14 | N5 F-4/F-5/F-11, N3 F-01/F-04/F-09, N1 F-09/F-10, N4 F-N4-08 | 4-node |
| C-B3 | **Config-vs-text contradiction**: provider order stated FOUR ways (M7 text chain ending Copilot; Ark D-355 Antigravity-first; providers.yaml OpenRouter-before-OCZ; ORACLE_STACK.md sixth variant — N5 §2 extends N1 F-03). `"/*": "allow"` nullifies permission enumeration (N1 F-02, N6 F-06). Archived roadmap injected every session (N1 F-05). `M7_local_first: false` (N1 F-06) | N1, N3 F-08, N5 §2, N6 | 3-node |
| C-B4 | **SSOT machinery durability**: TASK_REGISTRY MCP writer non-atomic — truncate-before-lock, load/save lock-split, lost-update race (N2 F-2.1, contradicting repo's own TASK_REGISTRY_DESIGN.md:189-191); 3/35 entity YAMLs unparseable incl. lilith proposed_lessons at TWO loci (N2 F-2.5, corrected locus line 2; N10 X-9 live-reproduced tail corruption) | N2, N1 F-08, N10 X-9 | 2-node + live repro |
| C-B5 | **Silent-failure architecture**: dead paths log nothing (N6 E4); unknown frontmatter ships to LLM providers as request params (N6 F-04); gates cannot fail (N7 F7-01); fabricated timestamps defeat staleness detection BY CONSTRUCTION (N8 F-1) | N6/N7/N8/N10 | 4-node |
| C-B6 | **Validator green ≠ truthfulness**: taxonomy compliance REAL (0 invalid statuses, N8 F-11) while future-dating, boundary staleness (5 zombies at exactly 7.x days, N8 F-2), dormant artifact_path (0/93 coverage, N8 F-3), WAKE_STATE blind spot (N8 F-5), and generated-view staleness (13 tasks behind, N8 F-10) are all invisible to it. Live proof: X-6 green run OVER a future-dated entry | N8 F-9, N10 X-6 | Central telemetry finding |
| C-B7 | **Lifecycle enforcement is manual-only**: handoff TTL never enforced post-acceptance (45h zombie actives vs 4h TTL, N9 F-2); pending TTL breached 17h (F-3); queue-dir pollution (F-4); archive contract unimplemented per its own §7 (F-5) | N9, N8 F-5 | 2-node |
| C-B8 | **Mirror-symmetry identity corruption**: BOTH sides misregistered their own deliverable — build copied arm identity into subagent_type, run copied arm identity into entity. Neither side saw its own mirror defect; each needed the other's audit to see it | N9 F-7 (overstated), N8 F-6, N10 Part 3 (corrected + quantified) | Quantified ×3 |

### C-C · Positive controls that HELD (preserved per Carmack R1 — clean surfaces must survive the funnel)

Gap-ID immutability regime works (collision log + rules, N2 F-2.4) · handoff queue counts match disk exactly 36/36 (N9 §1) · lock hygiene exemplary — one valid lock, zero residue (N9 F-9) · markdown-agent loading, top-level `instructions[]`, model inheritance, permission merge all LIVE and verified (N6 E1/E5/E7) · M25 streaming sections present on all cloud providers (N1 §2) · session_end.py AnyIO+atomic+fsync (N1 §2) · Corpus Map DOC-1 override mechanism real (N7 §3) · Delivered-Home registration path proven end-to-end durably via MCP (N2 F-2.10 — "this node is living proof") · sovereign-search and git-secret-scrub exemplify the quality bar (N4 §3) · skill health correlates with recency — post-Aug-01 skills are clean (N4 §3 pattern) · security bright line held on ALL TEN surfaces: zero secrets beyond stale placeholders, zero active external telemetry, zero CRITICAL-HALTED.

---

## §2 DISSENT ADJUDICATION

For each Build/Run tension: who is right, why, or why irreducible. Evidence cited from raws.

### T-1 · Honesty-first (shrink text) vs Mechanism-first (grow gates) — FALSE DICHOTOMY, sequenced
- **Build position** (N5 F-2 recommendation, adopted `[ARM]`, Consultant-endorsed as WAKE default): shrink M13's claims before growing T1-T11.
- **Run position** (N8 F-9 open question, Ruling C): upgrade the validator because green-certifies-taxonomy-not-truth.
- **Adjudication**: Both right; they are two halves of ONE rule — *no claim without mechanism; no mechanism without claim-update*. The future-dating arc (X-6) proves awareness without mechanics changes nothing; the stub comment proves mechanics without honest claims certifies nothing. **Sequence**: (1) shrink/en-stamp mandate text NOW (cheap, honest, zero code); (2) grow gates incrementally, each gate shipping WITH its mandate-text amendment in the same commit. Decree should bind them pairwise — a gate PR without its text patch (or vice versa) fails review. This generalizes N5 F-12's observed pattern (verify-mandate-claims warn-only stamp; M12 ADVISORY stamp): every unenforced mandate carries a visible enforcement-status stamp until a gate exists.

### T-2 · Single-writer doctrine vs Delivered-Home self-registration — RESOLVED, ratify Carmack R3/PASS1-R3
- Evidence: packet §C.6 ordered node self-registration; §F declared single-writer; both happened concurrently (N2 F-2.11 mechanical evidence; Carmack R3). N2 F-2.1 shows the concurrent-write window was real (load/save lock-split permits lost updates).
- **Adjudication**: The council violated single-writer BY DESIGN and got lucky (flock serialized; no loss observed). PASS1-R3's resolution is strictly better: nodes write registration PAYLOADS into reports; MaKaLi applies all at Stage 6. Ratify as decree law; add payload template precision (Ruling D root cause: packets never specified exact field values, so nodes copied arm identity — 15/20 wrong fields is the direct consequence).

### T-3 · Depth bump vs M11 Arm-Relay — SETTLED, relay is law; depth is a Council-2 dev decision
- Consultant Ruling A formalized Arm-Relay (no mid-run config change: runaway-recursion risk + recon-only breach). Build framed it as an open fork (§5-O option A/B); Run converged on relay.
- **Adjudication**: Relay stands for THIS run and as the standing design (it also preserves the Hop Rule structurally — N1's own recommendation option B). The depth question (`subagent_depth: 2` vs protocol text, N5 F-9) goes to Council 2 dev+Architect with both options costed. NOT irreducible — but deliberately deferred, and the decree must say so explicitly so no future agent reads §C.9-style paging mandates back into leaf packets.

### T-4 · Serial (Ma'at) vs partially-parallel (Lilith) dispatch — IRREDUCIBLE PREFERENCE, rule the declaration not the choice
- Both completed 5/5 zero-crash. Serial cost ~3h wall-clock; parallel risk did not materialize. P9's parallel-integrity framing reads oddly against serial doctrine (N9 §3 observation).
- **Adjudication**: Irreducible as preference; reducible as protocol. The decree should require: dispatch mode DECLARED in the packet up front, crash-tolerance stated, and P9 amended with an explicit serial-dispatch exception clause. Choosing serial-vs-parallel is an orchestrator judgment per-run; ambiguity about which was chosen is the actual defect.

### T-5 · Coordination-law SSOT (HIVEMIND_PROTOCOL.md vs ARCHITECT_OVERSIGHT_PATTERNS) — SETTLED by Ruling B, with a synthesis addition
- Ruling B: OVERSIGHT_PATTERNS is operational law; HIVEMIND_PROTOCOL is historical reference. Verified consistent with raws (N9 F-6: protocol doc is 2 months stale, retains STANDARD status, §4 marked SUPERSEDED internally).
- **Adjudication**: Ratify. Synthesis addition: the deeper defect is that LIVE law lives in an un-versioned, un-indexed coordination file while DEAD law holds STANDARD status — status headers lie in both directions (same class as C-A). Decree should order a VERSION-STAMP DISCIPLINE spec: every governance doc carries version + status + superseded-by, validated by a lint gate (extends N5 F-11's derivation-check principle to coordination law).

### T-6 · Stub skills: delete or author (N4 Q1) — ADJUDICATED: usage-evidence test, with an over-promise presumption
- N4 F-N4-02: five empty stubs + one placeholder; loader ADVERTISES them (blitz-validate promises validation steps it does not contain).
- **Adjudication**: An advertised-but-hollow capability is the same over-promise class as C-A — worse than invisibility because the loader lies on your behalf. Default: DELETE unless (a) a command/doc hard-links it (real consumer), or (b) it sits on a ratified roadmap with an owner+date. Authoring restores the promise only when someone needs it. Same rule for the meditation quartet (N4 F-N4-03): consolidate to harness + ONE pipeline; the four divergent stage-counts (5/6/7) are derivative-doc drift inside a single directory.

### T-7 · `"/*": "allow"` — HIGH defect (N1 F-02) vs deliberate risk-acceptance (N6 F-06) — BOTH RIGHT, the record is the defect
- N1 reads it as config nullifying instruction-layer sandbox preaching; N6 reads it as a deliberate autonomous-operation posture with only `*.env=ask` teeth remaining.
- **Adjudication**: The wildcard may be a legitimate fleet choice, but NO document records the decision — so config contradicts instruction text silently (C-A class). Fix: make the risk acceptance EXPLICIT (one documented decision in WAKE_STATE/decree, Architect-owned), then either remove the wildcard or annotate the enumeration as informational. An undocumented security posture is indistinguishable from a misconfiguration.

### T-8 · Plugin severity fork (dead tools vs lying config) — PRE-ADJUDICATED, hold the fork
- N1 F-01 nuance + N6 E4 evidence: silent-stall-sensor is demonstrably LIVE while unregistered → auto-discovery probably loads `.opencode/plugins/`. Consultant Q3 confirmed @researcher scope with pre-adjudicated severity fork (loads-from-plugins = HIGH lying-config doc-fix; loads-from-neither = CRITICAL confirmed-dead M23/M12 arms).
- **Adjudication**: No synthesis override. The fork is well-formed; hold for researcher evidence. Note for fusion: EITHER outcome indicts the registration list (config must tell the truth about mechanism), so the decree's config-honesty article is fork-independent.

---

## §3 BLIND-SPOT SWEEP

What NEITHER arm saw, visible only from the synthesis position:

### B-1 · The council is a live specimen of everything it found — therefore the decree must be SELF-VERIFYING
The strongest blind spot: Council 1 did not merely observe the defect classes — it EXHIBITED all of them simultaneously: its own reporting protocol was mechanically impossible (F-20, 10 rejections), its own registrations corrupted at birth (15/20 fields), its own checkpoints future-dated DURING the audit (X-6), its own SSOT documents contradictory (Carmack R8), its own run-arm's soul staging file unparseable (X-9). Implication neither arm drew: **awareness demonstrably does not change behavior in this fleet** (the future-date recurred 7 minutes after publication). Therefore every directive in the decree must ship with its own bash gate attached — a decree item without a verification command is itself a claim-outliving-mechanism. §6 is constructed on this principle.

### B-2 · The learning-capture channel is broken for THIS council's own output
M11/Soul Integrity requires session-end distillation to `proposed_lessons.yaml`. But 3/35 entity YAMLs are corrupt (N2 F-2.5) INCLUDING lilith's own staging file (N10 X-9) — the Run Arm literally cannot machine-persist its lessons from this audit. If repair doesn't precede session end, Council 1's gnosis gets stranded exactly like the 377 lines of Lilith gnosis already stranded. Neither arm connected F-2.5/X-9 to the council's OWN M11 obligation. Fusion should sequence YAML repair BEFORE session-end distillation.

### B-3 · Dispatch-suffix injection is systematic — a platform-trust surface nobody audited
Consultant flagged (BUILDARM adjudication): second occurrence council-wide of synthetic task-tool suffixes instructing agents to spawn entities. No node owned "wrapper-artifact forensics" as a surface. The fleet's S8 audit covered coordination protocols among OUR agents but not adversarial/injected content FROM the platform layer. Decree input: Platform Ground Truth Log entry + a standing rule (already exists as ORACLE_STACK stitch-artifact note — needs citation in dispatch packets).

### B-4 · Runtime health was never probed — all audits were static/textual
Ten nodes ran greps, parsers, validators, link-checkers — nobody ran `make test` or pytest. The decree will assert things about "the engine"; its test-suite health TODAY is unverified. Cheap gap: one bash call in Stage 4 (see §5, GAP-8). Without it, even our POSITIVE controls are textual.

### B-5 · Audited-clean vs never-examined is still indistinguishable at the decree layer
Carmack R1 warned digests eat negative findings; arms preserved positives ad hoc (both §"positive" sections). But no structural register exists. Fusion should require the decree to carry an AUDITED-CLEAN REGISTER (surface → node → date → method), so Council 2 knows which surfaces were swept-clean versus untouched. Otherwise next council re-audits clean ground or trusts silent ground.

### B-6 · Token-efficiency contradiction left unmeasured
M18 bans waste; M8 says thick-over-thin; N1 F-05 found an archived roadmap injected into EVERY session — but nobody measured the injection cost (bytes/session × sessions/day). Minor, but the decree's instruction-diet article would be stronger with one number. Optional Stage-4 item.

### B-7 · Severity calibration drift confirmed but unnormalized
N1 produced ~20 findings topping at CRITICAL; several siblings topped at HIGH on comparable surfaces; N5 produced the census arguably most deserving of CRITICAL and tagged it HIGH. Arms noted drift (Carmack R12) but neither normalized. Fusion should re-scale priority ORDER (not labels) using impact statements — the decree's sequencing inherits noise otherwise.

---

## §4 VERDICT DRAFT

> **DRAFT — INPUT TO MAKALI FUSION.** Not final. MaKaLi fuses all three voices; this draft feeds that fusion. Articles are sequenced by dependency, not severity alone.

### Article I — Name the root cause (decree spine)
Single systemic defect: **claims that outlive their mechanisms** — documentation asserting enforcement, wiring, identity, timestamps, and authority that grep/clock/schema can prove absent (evidence: §1 C-A table; Exhibits A-D below). Every remediation in this decree is an instance of ONE fix class: **bind every claim-bearing write to a mechanical fact-check (derivation checks)**.

### Article II — Honesty-first enforcement reform (pairwise binding)
1. Shrink SOVEREIGN_MANDATES.md M13/M26/M27/M14 enforcement claims to match measured reality (~30% enforced) in the same commit that any new gate lands. No gate PR without its text patch; no text patch promising a gate without the gate.
2. Generalize the N5 F-12 pattern: ALL 27 mandates carry a visible ENFORCEMENT-STAMP (enforced / warn-only / advisory / text-only) derived by script from Makefile+hooks — never hand-written.
3. Remove the temple-grade stub comment; either implement named T-gates or re-scope M13 to the gates that exist. `make sovereignty`: implement target or purge 9 references (N4 F-N4-06).
4. Install the pre-commit framework per Ma'at F1 ordering (PASS1-R3/G-5); verify `omega-tracking-state` actually fires.

### Article III — Validator & gate upgrades (truth, not just taxonomy)
Validator gains ERROR-class checks: future-dated timestamps (X-6), boundary-exact staleness in hours (N8 F-2), blockers[] vocabulary scan (N2 F-2.3), WAKE_STATE parse+staleness block (N8 F-5). `doc-llm-validate` gains `--strict` failure mode + scope expansion path (N7 F7-01). Auto-GO criteria amended per Ruling C: validator green AND content-minimum report checks AND timestamp-sanity one-liner.

### Article IV — M11 Arm-Relay Clause ratified; depth deferred
Adopt Ruling A verbatim: leaves write report+payload to disk; arms page once per stage; MK-Kali pages directly; NO mid-run `subagent_depth` change. Council 2 dev+Architect decide depth-vs-protocol-text (N5 F-9) with both options costed. All future leaf packets embed the relay clause INSTEAD of a paging step.

### Article V — Delivered-Home repair, sequenced (discovery → identities → statuses/timestamps)
1. Root-cause `task_registry_query(tags=…)` returning 0 against disk truth (@jem, GAP-5) — repair records into an index nobody can search wastes the repair (Run-arm sequencing rule, endorsed).
2. MaKaLi applies CORRECTED payloads at Stage 6 single-writer: canonical values per Ruling D (`subagent_type="node<N>"`, entity=node tag, exact 4-tag set).
3. NEW gate: retrieval verification ≥10 before Delivered-Home declared complete.
4. Packet-template precision rule: future dispatch packets specify exact field values (root-cause prevention, Ruling D).

### Article VI — AGENTS.md reconstruction (WAKE_STATE default-on-silence)
Default-on-Architect-silence: RECONSTRUCT root AGENTS.md from the citation web's expectations (462 citers define the de-facto contract; re-pointing multiplies risk 462×). Specification = Council 2 work requiring Architect GO. Nothing edits now.

### Article VII — Coordination-law SSOT + version-stamp discipline
ARCHITECT_OVERSIGHT_PATTERNS = operational law; HIVEMIND_PROTOCOL.md = historical (Ruling B). Formal supersession banner = Council 2 work. NEW spec: VERSION-STAMP DISCIPLINE — every governance doc carries version/status/superseded-by, lint-gated (extends derivation-check class to coordination law; fixes N9 F-6, N5 F-4/F-5 class permanently).

### Article VIII — Config honesty package
Fix plugin paths (sed one-liner, N1 F-01 AC); resolve the auto-load empirical fork (@researcher, GAP-1) before declaring severity; migrate agent-level `instructions[]` to schema-valid `prompt: {file:}` (N6 F-02); remove archived docs from injected instructions (N1 F-05); adopt Ark D-355 as canonical provider order and amend M7 text to match (N1 F-03+N5 §2); credentialed-fabric statement — sovereignty claims stated against the REAL fabric (local + OCZ + OpenRouter) until keys exist (N1 F-04); `"/*": "allow"` decision made explicit and recorded (T-7).

### Article IX — Gnosis pipeline repair precedes distillation
Repair 3 corrupt entity YAMLs (lilith ×2 loci, pillar_p1, john_carmack soul) BEFORE session-end soul distillation, so Council 1's own lessons don't strand (B-2). Acceptance: full-parse loop returns clean.

### Article X — Exhibits (preserve verbatim for Pass-2 findings audit)
- **Exhibit A**: Future-dating arc — N8 F-1 (found ~13:41Z) → N9 corroboration → N10 X-6 (recurred 13:48Z, validator green throughout).
- **Exhibit B**: Temple-grade stub comment verbatim (N5 F-2) alongside OMEGA_CODEX "✅ All enforced" printed the same day.
- **Exhibit C**: AGENTS.md void — zero git history, 462 citations, OMEGA_CODEX:222 citing a 343-line source that never existed.
- **Exhibit D**: Identity corruption matrix — N10 Part 3 §3.1, 15/20 fields wrong, mirror symmetry across arms.
- **Exhibit E**: F-20 rejection signature ×10 — identical error string from every leaf, proving config-forbids-protocol mechanically.

---

## §5 REMAINING_GAPS_AND_RECOMMENDED_RESEARCH (Stage 4 feed)

| # | Question | Why it blocks the decree | Recommended specialist/tool | Expected artifact |
|---|---|---|---|---|
| GAP-1 | Does OpenCode v1.18.23 auto-load plugins from `.opencode/plugin/`, `.opencode/plugins/`, both, or neither? | Sets N1 F-01/N6 F-01 severity (HIGH lying-config vs CRITICAL dead M23/M12 arms); fork pre-adjudicated (Q3) | @researcher — sandbox fixture test per PASS1-R5 scoping | phase4_research memo w/ probe transcript + severity selection |
| GAP-2 | Request-time permission enforcement: do ask/deny rules actually gate? | Merge layer proven (N6 E1); enforcement layer asserted nowhere empirically; decree's security-posture article (T-7/VIII) needs it | @researcher — headless `opencode run` w/ deny-rule fixture agent (sandboxed) | Probe log + verdict line |
| GAP-3 | Nested `.opencode/opencode.json` vs root merge precedence on conflicting keys | Both load (N6 E3); antigravity models live ONLY in nested file; config-honesty article incomplete without precedence rule | @researcher — A/B conflict probe | Precedence table |
| GAP-4 | Does agent-level `instructions[]` have ANY legacy code path despite schema omission? | Determines migration urgency for 12 agent defs (Article VIII) | @researcher — binary strings-audit or upstream source check | Yes/no + migration ticket |
| GAP-5 | Root cause of `task_registry_query(tags=["express:first-light"])` → 0 vs 12 disk matches (+ MCP grep false-negative same file) | Blocks Article V sequencing entirely — discovery must be fixed BEFORE mass identity repair | @jem — omega-hub server code deep-dive | Bug ticket w/ repro + fix location |
| GAP-6 | Which slug scheme does `oracle_summon_local` resolve first — providers.yaml `-local` names or affinity quant names? | Determines fix direction for model-id namespace chaos (N3 F-08 / N1 F-12); three schemes coexist with no declared authority | @jem or @researcher — code-path read of summon_local | Authority declaration + normalization ticket |
| GAP-7 | Does ANY runtime consumer read `config/council.yaml` model_tiers / M7 flag? | If none: cleanup ticket; if council code reads it: routing affected (ghost models, M7_local_first:false) | @jem — import/grep audit | Consumer map |
| GAP-8 | Is the test suite green TODAY? (`make test` / pytest exit code) | All ten audits were static; decree asserts engine health with zero runtime evidence (B-4) | Any Stage-4 member — one bash call | Exit-code line appended to research index |
| GAP-9 | Audit-log now-or-M3: implement hash-chain JSONL tracker audit (specified+ratified-unbuilt, N8 F-4) or accept commit-per-stage for council scale? | Determines whether Article III includes audit-log build or a deferral with rationale | Architect queue (WAKE_STATE candidate; N8 open Q2) | Ruling recorded in WAKE_STATE |
| GAP-10 | WAKE_STATE freshness ownership: who updates status at stage boundaries? | File currently contradicts reality (AWAITING_DEPARTURE mid-flight; "129 files" vs 8) with zero validator coverage (N8 F-5, N2 F-2.8 homeless-tier) | MaKaLi Stage-6 + Architect confirm | Owner named; validator block scheduled |
| GAP-11 | `subagent_depth`: raise to 3 or amend protocol text to codify arm-relay permanently? | Article IV defers deliberately; leaving it undecided invites the next council to re-hit the wall | Dev team + Architect, post-council (N1 F-20 options A/B costed) | Decision entry, PIVOT_LOG D-series |
| GAP-12 | Dispatch-suffix injection forensics: how systematic is wrapper-artifact injection in this environment? | Two occurrences council-wide (Consultant BUILDARM note); platform-trust surface unaudited (B-3) | MaKaLi/Consultant — PLATFORM_GROUND_TRUTH_LOG entry #11 | Ground-truth entry + packet-citation rule |

---

## §6 MEASURABLE_GATES

Every gate = bash command. Grouped by decree article. All runnable today; each must pass post-remediation. (Consolidates Build §5, Run §4, plus synthesis additions G-*.)

```bash
# ── G1. Plugin registrations resolve (Art. VIII; N1 F-01 / N6 F-01) ──
jq -r '.plugin[]' opencode.json | grep '^file://' | sed 's#file://##' | while read f; do test -f "$f" || echo "MISSING $f"; done   # expect: no output

# ── G2. Permission wildcard resolved or explicitly annotated (Art. VIII; N1 F-02) ──
jq '.permission.external_directory | has("/*")' opencode.json   # false AFTER decision recorded; if kept: rg -c 'risk-acceptance' data/coordination/WAKE_STATE.json ≥ 1

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

# ── G6. Atomic registry writer (Art. II/III class; N2 F-2.1) ──
grep -nE "mkstemp|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py   # must hit

# ── G7. Pre-commit framework INSTALLED and tracking hook fires (Art. II; N2 F-2.2 / N5 F-3 / N10 X-1) ──
grep -q "pre-commit" .git/hooks/pre-commit && echo FRAMEWORK-ACTIVE
grep -q "break-system-packages" .git/hooks/pre-commit && echo PASS-M24
pre-commit run omega-tracking-state --all-files 2>&1 | tail -1   # expect Passed

# ── G8. Entity YAML all machine-parseable (Art. IX; N2 F-2.5 / N10 X-9) ──
for f in data/entities/*/proposed_lessons.yaml data/entities/*/soul.yaml; do
  .venv/bin/python3 -c "import yaml;yaml.safe_load(open('$f'))" || echo "CORRUPT: $f"; done   # expect: no output

# ── G9. Command contract invariant across council variants (Art. VII class; N3 F-01/F-02) ──
! grep -q '^agent: kali' .opencode/commands/council-local.md .opencode/commands/council-fast.md
grep -q 'SOVEREIGN_DECREE' .opencode/commands/council-local.md .opencode/commands/council-fast.md

# ── G10. Dead agent instruction/config paths resolved (Art. VIII; N3 F-03 / N6 F-02) ──
for f in $(jq -r '.agent[].instructions[]?' opencode.json); do test -e "$f" || echo "DEAD: $f"; done   # expect: no output
jq '.agent | to_entries[] | select(.value.instructions) | .key' opencode.json                          # expect: empty after prompt:{file:} migration

# ── G11. Skill frontmatter universal; no hollow stubs (Art. II class; N4 F-N4-01/02) ──
for f in .opencode/skills/*/SKILL.md; do head -1 "$f" | grep -q '^---$' || echo "MISSING: $f"; done
find .opencode/skills -name SKILL.md -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -lt 20 ] && echo "STUB: $1"' _ {} \;   # expect: no output (or deleted)

# ── G12. make sovereignty exists or refs purged (Art. II; N4 F-N4-06) ──
make -n sovereignty >/dev/null 2>&1 && echo EXISTS || ! grep -rq "make sovereignty" .opencode/skills/

# ── G13. Temple-grade honesty: stub gone (Art. II; N5 F-2) ──
! grep -q "would go here" Makefile

# ── G14. Constitutional version coherence across derivatives (Art. VII; N5 F-4) ──
V=$(grep -m1 '^\*\*Version\*\*' SOVEREIGN_MANDATES.md | grep -o '[0-9.]*$')
grep -rq "$V" scripts/codex/*.md && ! grep -rq '3\.7\.0' scripts/codex/*.md && echo COHERENT

# ── G15. NO future-dated registry timestamps (Art. III; N8 F-1 / N10 X-6) ──
python3 -c "
import json,sys
from datetime import datetime,timezone
now=datetime.now(timezone.utc)
bad=[t['task_id'] for t in json.load(open('data/coordination/TASK_REGISTRY.json'))['tasks']
     if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
print('future-dated:',bad); sys.exit(1 if bad else 0)"

# ── G16. Staleness boundary fixed — hours not truncated days (Art. III; N8 F-2) ──
python3 scripts/sweep_task_registry.py 2>&1 | grep -qv "clean" || python3 -c "
import json,datetime
d=json.load(open('data/coordination/TASK_REGISTRY.json'))
now=datetime.datetime.now(datetime.timezone.utc)
z=[t['task_id'] for t in d['tasks'] if t.get('status')=='in_progress' and t.get('last_checkpoint') and (now-datetime.datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))).total_seconds()>=7*86400]
print('boundary-zombies:',z)"   # post-fix: zombies surfaced by sweep OR swept

# ── G17. artifact_path coverage growing (Art. III; N8 F-3) ──
jq '[.tasks[] | select(.status=="completed") | select(.artifact_path != null)] | length' data/coordination/TASK_REGISTRY.json   # >0 and non-decreasing for post-spec completions

# ── G18. Handoff schema synced (Art. VII; N9 F-1) ──
grep -q "source_agent_id" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo DOC-SYNCED

# ── G19. Handoff TTL enforced (Art. III class; N9 F-2/F-3) ──
find data/handoff/active -name '*.json' -mmin +300   # expect: empty output

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

# ── G22. doc-llm-validate can FAIL (Art. III; N7 F7-01) ──
python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ >/dev/null 2>&1; echo "strict-exit=$?"   # strict mode must discriminate (exit ≠ always 0)

# ── G23. Strategy-doc orphan target (Art. VII; N7 F7-03) ──
cd docs && ORPH=0; for f in strategy/*.md; do b=$(basename "$f"); \
grep -qF "$b" strategy/STRATEGY_INDEX.md strategy/STRATEGY_CORPUS_MAP.md || ORPH=$((ORPH+1)); done; echo "orphans=$ORPH"   # target 0 (indexed or banner-archived)

# ── G24. Phantom subsystem resolved (Art. VII; N7 F7-07) ──
test -f docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md || ! grep -qF "DOMAIN_DOCUMENTATION_SYSTEM" docs/strategy/STRATEGY_INDEX.md

# ── G25. AGENTS.md reconstructed (Art. VI; N5 F-1) ──
test -f AGENTS.md && echo PASS || echo "WAKE-QUEUED(default: reconstruct)"

# ── G26. Depth-wall resolution recorded (Art. IV; N1 F-20) ──
jq '.subagent_depth' opencode.json   # ≥3 IF depth-bump chosen; ELSE: rg -q 'Arm-Relay' docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md (relay codified, no bump)

# ── G27. Report content-minimum gate (auto-GO amendment; PASS1-R2) ──
for f in data/council/20260825-094633-first-light/phase1_nodes/P*_report.md; do
  paths=$(grep -cE '(docs/|data/|src/|config/|\.opencode/)' "$f"); crit=$(grep -c 'acceptance\|Acceptance' "$f")
  [ "$paths" -ge 3 ] && [ "$crit" -ge 1 ] || echo "THIN REPORT: $f"; done   # expect: no output

# ── G28. Runtime health baseline (GAP-8; B-4) ──
source .venv/bin/activate && make test 2>&1 | tail -3   # record exit code in research index; decree cites it
```

---

## APPENDIX — FUSION_BRIEF SEED (per PASS1-R9; embedded here per recon-only write constraint — MaKaLi may lift verbatim into `phase5_fusion/FUSION_BRIEF.md`)

**Verdict skeleton**: Root cause = claims-outliving-mechanisms (Art. I). Ten articles, three exhibits-plus-two, twelve gaps, twenty-eight gates.
**Top tensions for triad attribution**: T-1 honesty-vs-mechanism (false dichotomy, pair-bind); T-3 relay-vs-depth (settled, defer depth); T-7 wildcard (record-the-decision).
**Open questions for fusion**: (a) accept Article II pairwise-binding as review rule? (b) GAP-9/10/11 → WAKE_STATE queue wording; (c) severity re-scaling for decree priority order (B-7); (d) audited-clean register inclusion (B-5).
**Attribution skeleton**: Build = taper census + durability + config contradictions (N1/N2/N5 lead); Run = drift telemetry + lifecycle + mechanics (N8/N10 lead); Synthesis = root-cause unification + self-verifying decree form.

---

*⬡ OMEGA ⬡ MK_KALI ⬡ SYNTHESIS_ARM_REPORT ⬡ DRAFT-INPUT-TO-FUSION ⬡ raws-cited-primary ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

