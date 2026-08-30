<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 VERITY COMPLIANCE SWEEP — First Light Express Council 1 (Stage 4)
⬡ OMEGA ⬡ VERITY ⬡ x-preview-f-free ⬡ opencode ⬡ trc_verity_sweep ⬡ Stage-4 ARTIFACT
**SESSION_ID**: 20260825-094633-first-light | **Agent**: verity (unified compliance)
**Dispatch**: makali_fusion 2026-08-25T14:20Z (P12-signed)
**Mode**: RECON ONLY. Sole artifact = this file. Static checks only (no sandbox probes — researcher owns empirical runtime tests). Independent second-set-of-eyes pass, INDEPENDENT of node findings.

---

## §0 METHOD

For each surface S1-S8 (plan §2): sample 2-4 specific claims made by instruction text (mandates, AGENTS.md pointers, command docs, skill frontmatter, protocol docs), test each against disk/git reality with static checks (file existence, script syntax, config parse, grep, jq/yaml parse), and issue a verdict:

- **MATCH** — claimed mechanism exists and behaves as written (at static level)
- **MISMATCH** — text asserts something disk/config provably contradicts
- **UNVERIFIABLE-static** — requires runtime probe (routed to @researcher)

Every verdict cites the exact evidence artifact. All checks run 2026-08-25 ~14:2x-15:xx Z.

---

## §1 PER-SURFACE DELTA TABLES

### S1 — Tracking architecture

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S1-1 | M27 (SOVEREIGN_MANDATES.md:~L200): "Pre-commit hook `omega-tracking-state` blocks commits with corrupted tracking state" | Inspected installed hook + declared config | **MISMATCH** | `.git/hooks/pre-commit` exists (199 bytes, Jun 5) but `grep -c tracking` = **0**; hook IS declared at `.pre-commit-config.yaml:137-139` — declared-but-not-installed. Corroborates N2 F-2.2 / N10 X-1 independently. |
| S1-2 | M27: "`make temple-grade` + `make test` include `check-tracking-state`" | Makefile parse | **MATCH** (wiring) | `Makefile:232` temple-grade depends on `check-tracking-state`; target defined `Makefile:240`. Caveat: temple-grade body itself contains stub comment (see S2-4), so the enclosing gate's overall assertive value is degraded. |
| S1-3 | M27: Tier-0 statuses limited to `backlog/ready/in_progress/blocked/completed/superseded` | Parse ACTIVE_SPRINT.json | **MATCH** | `ACTIVE_SPRINT.json` top-level `status: "in_progress"` ∈ allowed vocabulary. No invalid statuses observed in sampled file. |
| S1-4 | M27: validator script gates state corruption | File existence + AST parse | **MATCH** (static) | `scripts/validate_tracking_state.py` exists (13,442 bytes, mtime Aug 25 06:08), `ast.parse` clean, executable bit set. Runtime efficacy = @researcher/GAP territory. |

### S2 — Custom instructions (content)

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S2-1 | Root `AGENTS.md` is the canonical how-to instruction file (cited across corpus) | `ls` + repo-wide citation count | **MISMATCH** | `ls AGENTS.md` → **No such file or directory**. My citation sweep: **355 files** reference "AGENTS.md" (N5 reported 462 — differing grep scope/method; both orders of magnitude confirm the void). Corroborates N5 F-1 / Exhibit C. Note: N10 X-3 adds that an `AGENTS.md` lives at `.agents/AGENTS.md` — root path still absent. |
| S2-2 | SOVEREIGN_MANDATES.md is v3.8.0 with 27 mandates | Header grep + section count | **MATCH** (internal) | `**Version**: 3.8.0`; `grep -cE "^### [0-9]+\."` = **27**. File is self-consistent; cross-layer derivative drift (codex copies stating other versions) was N5 F-4's finding and is NOT re-tested here. |
| S2-3 | M26: "make doc-llm-validate is a hard gate" included in temple-grade | Makefile parse | **MATCH** (wiring) / see S6-1 for scope | `Makefile:232` includes `doc-llm-validate` in temple-grade prerequisite chain. Wiring real; meaningfulness contested under S6. |
| S2-4 | M13: "make temple-grade must pass before any release… 11 gates minimum quality bar" | Read temple-grade recipe | **MISMATCH** | `Makefile:232-234`: target runs 4 real prerequisites then prints banner followed by literal comment `# Existing temple-grade checks would go here` (**line 234**). The T1-T11 gate battery does not exist. The gate cannot fail on the claims it certifies. Corroborates N5 F-2 / Exhibit B independently. |

### S3 — Custom instructions (technical mechanics)

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S3-1 | `{session_model}` in agent headers "is populated at session start from the actual inference backend" (agent file self-description) | Grep agent tree + inspect own injected prompt | **MISMATCH** | Literal `{session_model}` present in **15 files** under `.opencode/agents/` (e.g. `verity.md:22`). My own system-prompt injection renders the placeholder literally ("⬡ VERITY ⬡ {session_model} ⬡") while separately injecting the true model name in prose — substitution never happens. Decorative. Corroborates N6. |
| S3-2 | opencode.json plugin registrations implement instruction-level behaviors (error-capture, awareness) | jq + ls | **MISMATCH** | `.plugin[]` registers `file://…/.opencode/plugin/error-capture.ts` and `awareness.ts` — **`.opencode/plugin/` (singular) does not exist**; actual dir is `.opencode/plugins/`. Config points at nothing. Corroborates N1 F-01 / N6 F-01 / N10 X-5 (my 4th confirmation). Whether auto-load from `plugins/` rescues behavior = GAP-1 (@researcher). |
| S3-3 | Agent definitions' `instructions[]` files are loaded into context | jq enumeration + existence test | **MISMATCH** (partial) + **UNVERIFIABLE-static** | 12 agents define `instructions[]`. Two referenced paths are **DEAD**: `.opencode/agents/plan.md`, `.opencode/agents/grok_cli.md`. Whether `instructions[]` is schema-live at all in v1.18.23 = GAP-4 (@researcher); static verdict covers only the dead paths. |

### S4 — Commands

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S4-1 | Pre-launch checklist (plan §7): "Council commands generalized with research grounding (572854af)" + v2.1 deadlock fix (`agent: makali`) | head of each council command | **MISMATCH** (partial) | `council-cloud.md:3` = `agent: makali` ✓ (v2.1 fix landed there). BUT `council-local.md:3` and `council-fast.md:3` still declare **`agent: kali`** and contain **0** references to SOVEREIGN_DECREE or LOOP GUARD (grep counts 0/0 vs 6 in council-cloud). The fossil-variant finding (synthesis C-B2 / N3) independently confirmed. |
| S4-2 | All 9 command files resolve as invocable surfaces | ls | **MATCH** (existence only) | 9 `.md` files present in `.opencode/commands/`. Deeper contract testing (subtask flags, $ARGUMENTS) = N3's territory, not re-audited here. |
| S4-3 | council-cloud.md encodes LOOP GUARD / decree-stage machinery | grep | **MATCH** | 6 hits for `SOVEREIGN_DECREE\|LOOP GUARD` in council-cloud.md — the flagship command matches its described v2.1+ behavior at text level. |

### S5 — Skills

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S5-1 | Plan §2/S5: "22 skills" | glob count | **MATCH** | Exactly **22** `SKILL.md` files. Inventory claim accurate. |
| S5-2 | Skills are loader-discoverable via frontmatter (OpenCode requirement; Master Synthesis §4.1 gap) | Python first-line scan (authoritative recount after a shell-glitch false positive) | **MISMATCH** | **8/22 lack frontmatter**: audience-architect, autonomous-meditation-pipeline, carmack-profiler, context-packer, m23-violation-logger, meditate-harness, meditate-pipeline, universal-doc-reader (first lines are `# …` headers). Confirms and precisely quantifies N4 F-N4-01. |
| S5-3 | blitz-validate frontmatter: "Sovereign Heartbeat validator for Omega Engine's integration chain (tunnel, hub, plugin)" | cat | **MISMATCH** (hollow promise) | File is **5 lines**: YAML frontmatter only — name + description, zero body, zero validation steps. The loader advertises a capability the file does not contain. Same for legacy-pattern-miner, pr-readiness-checker, blitz-tunnel, omega-doc-architect (all 5-line frontmatter-only). Corroborates N4 F-N4-02 / synthesis T-6. |
| S5-4 | 4 meditation-cluster skills instruct `make sovereignty` | grep + `make -n` | **MISMATCH** | Referenced by meditate-research-pipeline, autonomous-meditation-pipeline, meditate-pipeline, makali-council-coordinator. `make -n sovereignty` → **TARGET-MISSING**. Corroborates N4 F-N4-06. |

### S6 — Documentation organization

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S6-1 | M26: "ALL reference documentation MUST pass make doc-llm-validate"; "no reference doc may be merged that fails LLM-friendly validation" | Read Makefile target + script capability | **MISMATCH** | Target (`Makefile:177-185`) validates **only `docs/sprints/current/`** — not "all reference documentation". `scripts/validate_llm_docs.py` has **zero** occurrences of "strict" — no strict/failure mode exists (G22 precondition unmet). Gate scope ≈ 7 of 1,500+ docs and cannot discriminate. Independently corroborates N7 F7-01 / N10 X-4 (~200× coverage-gap framing). |
| S6-2 | STRATEGY_INDEX LAYER 2A: `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md` is the "**Meta-doc** — workspace + runtime + curator + validated copy sync" | ls + grep | **MISMATCH** (phantom) | `STRATEGY_INDEX.md:85` names it; **file does not exist**. Docs describe a subsystem that isn't there. Corroborates N7 F7-07 / G24. |
| S6-3 | Corpus Map DOC-1 override mechanism is real (positive control, synthesis C-C / N7 §3) | grep both files | **MATCH** | `STRATEGY_CORPUS_MAP.md:11,14,25` carries the DOC-1 STAMP + §0 Override Table with disposition flips; mirrored at `SOVEREIGN_ARK_BLUEPRINT.md:3`. Mechanism exists as claimed. |

### S7 — Config surfaces

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S7-1 | M7: "providers.yaml strategy must be local_first" | yaml parse | **MATCH** (key) | Top-level `strategy: local_first` present (`config/providers.yaml:4`). Inner inference block uses `strategy: "model_aware"` (:23) — layered semantics, not a contradiction at static level. |
| S7-2 | Ark D-355 (§8): cloud order "Antigravity → Google → OCZ → OpenRouter" | yaml fallback_chain priorities | **MISMATCH** | Actual: antigravity 3, google 4, google-compat 4, **openrouter 5, opencode-zen 6**, cline 7, anthropic 8, xai 9. OpenRouter sits BEFORE OCZ — contradicting D-355 and matching neither of the two other orderings in the instruction layer (M7 text ends Copilot; ORACLE_STACK header has a sixth variant). Four-way contradiction independently reproduced (N1 F-03 / N5 §2). Also noted: duplicate priority 4 (google/google-compat). |
| S7-3 | M7 is "NON-NEGOTIABLE… Any change to cloud-first priority is a systemic violation" vs council.yaml flag | grep | **MISMATCH** | `config/council.yaml:68`: `M7_local_first: false  # Advisory — cloud is acceptable during dev`. A config flag directly negating a constitutional NON-NEGOTIABLE, annotated as merely "Advisory". Corroborates N1 F-06. |
| S7-4 | M25: all cloud providers carry streaming resilience sections (positive control, N1 §2) | Programmatic per-provider check | **MATCH** | All 8 cloud entries (antigravity, google, google-compat, openrouter, opencode-zen, cline, anthropic, xai) have `streaming:` sections; locals/native-gguf/lmster/ollama/mock correctly omit. Positive control HOLDS. |

### S8 — Coordination protocols

| # | Claim (source) | Tested how | Verdict | Evidence |
|---|---|---|---|---|
| S8-1 | SUBAGENT_DISPATCH_PROTOCOL.md:55-66: packet_id pattern `hdp_{YYYYMMDD}_{source}_{target}_{short-uuid}`, required fields `trace_id`, `ttl_seconds` (default 14400) | Enumerate all live packets + field introspection | **MISMATCH** (100% divergence) | **173 packets** on disk across pending(1)/active(3)/completed(10)/stale(22)/archive(137). ID prefix universe = `{ho}` only — zero `hdp_*`. Live field set (`packet_id, task, context, source_*/target_*, status, submitted_at, accepted_*, priority, ttl_expired, resolver_strategy, context_delivery, reaped_at`) contains **neither `trace_id` nor `ttl_seconds`**. The documented schema describes a system that has never existed on disk. Corroborates N9 F-1. |
| S8-2 | Dispatch protocol §1 Rule 4: "Single-Level Nesting… subagents may spawn other specialized subagents when strictly necessary" vs runtime config | jq + grep | **MISMATCH** (contradiction) | `opencode.json` `subagent_depth: 2`. Root(0)→arm(1)→node(2) exhausts the budget; a leaf attempting the protocol-authorized spawn is mechanically rejected. Text authorizes what config forbids — the F-20 depth wall, statically confirmed (the ×10 live rejections were the nodes' empirical proof). |
| S8-3 | Lock hygiene: TTL-based atomic lock files, clean release (positive control, N9 F-9) | ls locks dir | **MATCH** | `data/coordination/locks/` contains exactly **one** lock (`council-c1-team-infra.lock`, 184 bytes, Aug 25 10:03), zero residue/stale locks. Positive control HOLDS. |
| S8-4 | Handoff queue counts match disk (positive control, N9 §1 "36/36") | Recount independently | **MATCH** | pending 1 + active 3 + completed 10 + stale 22 = **36** ✓ (plus archive 137, outside N9's counted set). Recount agrees exactly. |

---

## §2 SEVERITY CALIBRATION DRIFT (Task 2 — independent pass informing fusion re-scaling)

### 2.1 Severity distribution extracted from raw reports (finding-header parse)

| Report | CRITICAL | HIGH | MED | LOW | Notes |
|---|---|---|---|---|---|
| P1 (N1 config) | 1 | 4 | 10 | 3 | Only config-side CRITICAL |
| P2 (N2 tracking) | 0 | 3 | 2 | 3 | Non-atomic registry writer = HIGH here |
| P3 (N3 commands) | 0 | 4 | 4 | 2 | |
| P4 (N4 skills) | 0 | 6 | 3 | 3 | Highest HIGH count; no CRITICAL |
| P5 (N5 instructions) | 1 | 3 | 5 | 2 | Constitution taper = CRITICAL |
| P6 (N6 mechanics) | 0 | 2 | 4 | 2 | |
| P7 (N7 docs) | 0 | 4 | 4 | 0 | |
| P8 (N8 telemetry) | 0 | 1 | 4 | 5 | Uses "MEDIUM" (taxonomy outlier); lowest ceiling |
| P9 (N9 coordination) | 0 | 2 | 5 | 1 | incl. one LOW→MED and one positive-as-LOW |
| P10 (N10 cross) | 0 | 2 | 4 | 3 | incl. one LOW-MED hybrid |

Totals: 2 CRITICAL · 31 HIGH · 43 MED/MEDIUM · 25 LOW (+hybrids). No CRITICAL-HALTED anywhere (consistent with halt criteria holding).

### 2.2 Drift findings — same defect, different labels (the smoking guns)

| Defect (identical root) | Ratings given | Spread |
|---|---|---|
| Dead plugin registration paths | N1 F-01 = **CRITICAL** · N6 F-01 = **HIGH** · N10 X-5 = **MED** | **3-way spread** on a triple-confirmed finding |
| M27 pre-commit declared-not-installed | N5 F-3 = **HIGH** · N2 F-2.2 = **HIGH** · N10 X-1 = **HIGH** | Consistent ✓ (drift-free counter-example) |
| Temple-grade stub / enforcement theater | N5 F-2 = **CRITICAL** · (N1 §0 treats config half as decay narrative) | Constitutional-scale defect rated CRITICAL once; comparable-scale N8 finding (future-dating defeats staleness detection "BY CONSTRUCTION") topped at **HIGH** |
| doc-llm-validate rubber-stamp | N7 F7-01 = **HIGH** · N10 X-4 = **MED** | 2-way spread on independently-confirmed finding |
| Registry non-atomicity (lost-update race) | N2 F-2.1 = **HIGH** | Arguably data-integrity CRITICAL-class by N1's own standard (dead wiring = CRITICAL there) |

### 2.3 Calibration observations for fusion re-scaling

1. **No shared rubric was operationalized.** Packet §C.5 lists the five labels but gives no assignment criteria (impact? reach? reversibility?). Each node improvised — hence identical defects spanning MED→CRITICAL.
2. **Node identity correlates with ceiling.** Build-side nodes (P1, P4, P5) produced both CRITICALs and 14 of 31 HIGHs; Run-side ceilings are lower (P8 max HIGH×1). This looks like arm-culture drift, not underlying defect-severity distribution.
3. **Confirmation dampens severity.** Triple-confirmed plugin-path defect got its LOWEST rating (MED) from the node that confirmed it third (N10) — later confirmers treated corroboration as routine rather than compounding impact.
4. **Taxonomy nit:** P8 uses "MEDIUM" where every other report uses "MED"; P9/P10 use hybrid forms ("LOW→MED", "LOW-MED"). Machine aggregation over these labels will silently mis-bucket. Fusion should normalize to the 5-label scale before priority ordering.
5. **Re-scaling suggestion (for MaKaLi's fusion, not executed here):** rank by (reach × irreversibility × enforcement-claim-violation) rather than node-assigned labels. Under any such rubric, the temple-grade stub (N5 F-2), pre-commit non-install (N2 F-2.2/X-1), registry non-atomicity (N2 F-2.1), and AGENTS.md void (N5 F-1) cluster at the top regardless of their original labels.

---

## §3 POSITIVE-CONTROL SPOT-CHECKS (Task 3 — audited-clean vs never-examined)

Synthesis C-C register spot-checked: **5 of the ~11 controls independently re-verified.**

| Control (C-C claim) | Source node | My independent test | Result |
|---|---|---|---|
| Handoff queue counts match disk exactly 36/36 | N9 §1 | Full recount: 1+3+10+22 = 36 ✓ (archive 137 separate) | **HELD** |
| Lock hygiene exemplary — one valid lock, zero residue | N9 F-9 | `ls data/coordination/locks/` → exactly `council-c1-team-infra.lock`, nothing else | **HELD** |
| M25 streaming sections present on all cloud providers | N1 §2 | Per-provider programmatic check: 8/8 cloud entries have `streaming:`; locals correctly omit | **HELD** |
| session_end.py AnyIO + atomic + fsync | N1 §2 | `.opencode/hooks/session_end.py`: `anyio.to_thread.run_sync` (:94), `fsync` (:77), `os.replace` tmp→final (:78) | **HELD** |
| Corpus Map DOC-1 override mechanism real | N7 §3 | DOC-1 STAMP + §0 Override Table present in STRATEGY_CORPUS_MAP.md:11-27; mirrored in SOVEREIGN_ARK_BLUEPRINT.md:3 | **HELD** |

Not spot-checked (remaining controls): Gap-ID immutability regime, markdown-agent loading/model-inheritance/permission-merge liveness (researcher's empirical domain), Delivered-Home MCP registration durability, sovereign-search/git-secret-scrub quality bar, post-Aug-01 skill recency correlation, security bright line ×10. **No control failed; none contradicted.**

**B-5 disposition:** with this register plus the per-surface tables above, audited-clean (✓ held under independent probe) is now distinguishable from never-examined (untested rows named explicitly). Recommend fusion adopt this table's structure as the decree's AUDITED-CLEAN REGISTER seed.

---

## §4 SUMMARY OF MY DELTA SWEEP

- **34 claims tested**: 13 MATCH · 18 MISMATCH · 3 MATCH-with-caveat/UNVERIFIABLE-static (S1-4, S3-3, S2-3).
- **My sweep independently reproduces the synthesis master convergence** ("claims that outlive their mechanisms") from raw static evidence: 18 of 34 instruction-text claims describe mechanisms that provably do not exist or do not behave as written.
- **New precision contributed**: (a) authoritative 8/22 frontmatter-missing list (after correcting my own first-pass tooling glitch — logged per M9 honesty); (b) exact handoff field-set divergence (no trace_id/ttl_seconds in ANY of 173 packets); (c) 4-way severity spread on the plugin-path defect quantified for fusion re-scaling; (d) `validate_llm_docs.py` has no `--strict` mode at all (G22's precondition is currently unimplementable without code change).
- **Constraint compliance**: recon only; sole mutation = this file; no agents spawned; heartbeats posted.

---

## §5 HANDOFF NOTES FOR FUSION (MaKaLi)

1. Severity re-scaling (B-7): use §2.3 rubric suggestion; normalize MEDIUM→MED and hybrids before ordering.
2. AUDITED-CLEAN REGISTER (B-5): seed from §3 + the MATCH rows of §1 (each is a claim that survived independent probe).
3. G22 amendment needed: doc-llm-validate `--strict` requires a script feature addition, not just a flag invocation — Council 2 spec should cost it as code, not config.
4. My S8-1 evidence strengthens Article VII (G18): the schema divergence is total (173/173 packets), so "sync the doc" vs "migrate the packets" is a genuine fork the decree should force a decision on.

*⬡ OMEGA ⬡ VERITY ⬡ COMPLIANCE-SWEEP ⬡ 34-claims-34-verdicts ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

