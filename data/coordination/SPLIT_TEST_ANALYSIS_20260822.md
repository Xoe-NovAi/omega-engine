<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Split Test Analysis — Three-Way Researcher Comparison (v1/v2/v3)
**AP Token**: `AP-SPLIT-TEST-ANALYSIS-v1.1.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_split_test ⬡ ANALYSIS

**Date**: 2026-08-22
**Purpose**: Capture methodology findings, model differences, and lessons from the three-way dispatch experiment run during the Pillar→Node migration-planning mission. This is itself a rehearsal artifact — the experiment discipline practiced here is the same discipline the Migration Playbook prescribes.
**Tags**: split-test, dispatch-protocol, priming, model-comparison, M18, M21, M22

---

## Answer First

A three-way same-prompt test compared: (1) **fresh** Researcher session, (2) **primed** original session (full Wave 1–3 context), (3) **freshly primed** new session with full context loading. Result: the **freshly primed session (v3)** produced a **production-ready, M26-compliant playbook** at ~5× the depth of v1/v2 — with full M26 frontmatter, self-contained code examples, Mermaid DAGs, executable codemod specs, and a 5-drill rehearsal program. The v1 (fresh) and v2 (primed) runs produced complementary but shallow research summaries; v3 produced a **validated, rehearsable artifact**. The test was **confounded** (model × thinking × priming all differ across runs), so conclusions are joint.

---

## §1 Test Conditions (Three-Way)

| Variable | Run A: v1 (Fresh) | Run B: v2 (Primed Original) | Run C: v3 (Freshly Primed) |
|---|---|---|---|
| Session | Fresh spawn `ses_fd5018…` | Original `ses_fd81c19…` (Wave 1–3 context) | Fresh spawn `ses_fd4cc4…` + **explicit context loading** (read 20+ files) |
| Model | `x-preview-f-free` (Ox Alpha) | `nemotron-3-ultra-free` | `nemotron-3-ultra-free` |
| Thinking | **low** | **high** | **high** |
| Prompt | Identical mission | Identical + `_v2` filenames + isolation guard | Identical + `_v3` filenames + isolation guard + **explicit "do not read v1/v2"** |
| Context loading | None (fresh) | Implicit (session history) | **Explicit: read 20+ files** (Roc audit, charters, prior research, standards) |
| Output size | 347 lines / ~4,050 words | 262 lines / ~3,140 words | **1,788 lines / ~9,941 words (5.2× v1/v2)** |
| M26 frontmatter | ❌ | ❌ | ✅ Full (schema_version, acceptance_gates, cross_refs, llm_metadata) |
| Self-contained code | ❌ | ❌ | ✅ libcst transformer, ast-grep rules, deprecation tracker, Mermaid DAGs |
| Rehearsal program | 6 hypotheses | 5 predictions + DoD | **5-drill program** with phase gates, rollback, risk register, go/no-go |

**⚠️ Confound declaration (unchanged)**: three variables differ (session priming, model, thinking). v2 and v3 share model+thinking but differ in priming method (implicit history vs explicit loading). v3 is the only run with **explicit context loading** as a controlled step.

**⚠️ DB-verified model mapping**: v1 = Ox Alpha low; v2 = Nemotron Ultra high; v3 = Nemotron Ultra high. Verified via `opencode.db` per-message.

---

## §2 Three-Way Results — Three Lenses

### Lens 1: Structural

| Dimension | v1 (Fresh) | v2 (Primed Original) | v3 (Freshly Primed) |
|---|---|---|---|
| **Output scale** | 347 lines / 4K words | 262 lines / 3K words | **1,788 lines / 9.9K words (5.2×)** |
| **M26 compliance** | ❌ No frontmatter | ❌ No frontmatter | ✅ Full: schema_version, acceptance_gates, cross_refs, llm_metadata |
| **Lifecycle model** | 7 phases (A–G) | 5 phases (Introduce→Learn) | **5 phases + Mermaid DAG + machine-readable YAML DAG** |
| **Gap analysis vs Roc** | ✅ Explicit Instantiation Map | ❌ Inline only | ✅ **Pre-Drill Gate checklist (11 items)** |
| **Ownership** | Gates only | Roles → N-nodes | **Roles + phase gates + owners per phase** |
| **Timeline policy** | Single floor | Tiered (GA/Beta/Alpha) | **Tiered + Omega-specific monthly minors + LTS anchor** |
| **Evidence rigor** | URLs inline | Source Register (SR-C1–13) | **Evidence Traceability Matrix (10 rows mapping playbook→cases)** |
| **Code artifacts** | None | None | **libcst transformer, ast-grep YAML, deprecation tracker, Mermaid DAG, YAML DAG** |
| **Rehearsal program** | 6 hypotheses | 5 predictions + DoD | **5-drill program** with phase gates, rollback, risk register, go/no-go |
| **MCP tool specifics** | Generic | 12-month window | **Drill 2 dedicated** (external client impact, 12-month window) |

### Lens 2: Substantive — Unique Finds per Run

| Run | Unique Substantive Contributions |
|---|---|
| **v1 (Fresh)** | Home Assistant case study w/ URLs · PEP 702 mechanics + "~1,900 of top-5000 PyPI packages" stat · pydantic Python-3.14 forced shim death · k8s `--runtime-config` removal-rehearsal · "ecosystem writes your migration tooling" · ADR-sprawl anti-pattern + Etsy Morgue · **numeric falsifiers on 6 hypotheses** · 9-row metrics ledger with M23 no-vanity-numbers |
| **v2 (Primed Original)** | Refused to cite HA/Zed/Tauri without primary sources ("NOT cited rather than padded in") · changelog taxonomy + `[omega-deprecation]` warning string · versioned docs tree (`docs/migrations/v<MAJOR>/`) · quarterly Meta-Review cadence (Loon) · "reactive migration mode" · `rehearsal_surprises.jsonl` · timebox-honesty · tabletop dry-run DoD ("rename oracle.talk()") |
| **v3 (Freshly Primed)** | **Full M26 frontmatter + acceptance gates** · **Self-contained executable code** (libcst transformer, ast-grep YAML rules, deprecation tracker class, Mermaid DAG, YAML phase DAG) · **5-drill rehearsal program** with phase gates, rollback procedures, risk register, go/no-go gate · **Drill 2 (MCP tool rename)** with external client impact · **Drill 3 (WAD config)** with namespace hygiene · **Drill 4 (Soul files)** with SO-10a tagging · **Drill 5 (synthetic CLI)** · **Evidence Traceability Matrix** (10 rows playbook→cases) · **Cross-case synthesis** (window norms, tooling convergence, communication convergence, tracking convergence) · **Full codemod specs** with test fixtures (libcst + ast-grep) · **Full deprecation tracker implementation** · **Rollback procedures per drill** · **Risk register** with likelihood/impact/mitigation · **Go/No-Go gate** for playbook graduation |

**Converged across ALL THREE (highest confidence)**: Expand-Contract dual-name shims · guide written BEFORE breaking code · policy-bound removal timing · local-only signals as M8 answer · ast-grep > libcst/OpenRewrite at our scale · ~20-site codemod threshold · blameless postmortem → PIVOT_LOG/soul distillation.

### Lens 3: Efficiency & Quality

| Metric | v1 | v2 | v3 |
|---|---|---|---|
| Lines per artifact | 115 avg | 87 avg | **596 avg** |
| Words per artifact | 1,350 avg | 1,046 avg | **3,314 avg** |
| M26 frontmatter | 0/3 | 0/3 | **3/3** |
| Self-contained code blocks | 0 | 0 | **12+** (libcst, ast-grep, tracker, deprecation, Mermaid, YAML DAG) |
| Mermaid diagrams | 0 | 0 | **2** (phase DAG + execution DAG) |
| Machine-readable specs | 0 | 0 | **2 YAML DAGs** (phase DAG + phase table) |
| Codemod test fixtures | 0 | 0 | **4** (before/after Python + YAML) |
| Rollback procedures | 0 | 0 | **Per-drill + universal** |
| Risk register | 0 | 0 | **6 risks** with likelihood/impact/mitigation |
| Go/No-Go gate | 0 | 1 (tabletop dry-run) | **Full graduation gate** (6 criteria) |

---

## §3 Substantive Convergence & Divergence

### Converged (All Three — Highest Confidence)
- Expand-Contract dual-name shims
- Guide written BEFORE breaking code
- Policy-bound removal timing (not mood-bound)
- Local-only signals as the M8-compliant tracking answer
- ast-grep > libcst/OpenRewrite at our scale
- ~20-site codemod threshold
- Blameless postmortem → PIVOT_LOG/soul distillation

### v1+v2 only (v3 omitted)
- PEP 702 adoption stat (~1,900 PyPI packages)
- pydantic Python 3.14 forced shim death
- Etsy Morgue tool
- ADR-sprawl anti-pattern
- Numeric falsifiers on hypotheses (v1) / predictions (v2)

### v2+v3 only (v1 omitted)
- Changelog taxonomy vocabulary (`DEPRECATED:`/`MIGRATION:`)
- Standardized `[omega-deprecation]` warning format
- Versioned docs tree (`docs/migrations/v<MAJOR>/`)
- Quarterly Meta-Review cadence (Loon)
- Reactive migration mode for upstream breaks
- `rehearsal_surprises.jsonl` / timebox-honesty

### v1+v3 only (v2 omitted)
- Home Assistant case study (v2 refused to cite)
- PEP 702 mechanics detail
- k8s `--runtime-config` removal rehearsal
- "Ecosystem writes your tooling" observation
- Etsy Morgue tool

### Unique to v3 (not in v1 or v2)
- Full M26 frontmatter with acceptance gates
- Executable libcst transformer + ast-grep rules + deprecation tracker
- Mermaid + YAML DAGs for phase DAGs
- 5-drill rehearsal program with phase gates
- Drill 2 (MCP tool rename) with external client focus
- Drill 3 (WAD config) with namespace hygiene
- Drill 4 (Soul files) with SO-10a tagging
- Drill 5 (synthetic CLI) for post-rehearsal validation
- Evidence Traceability Matrix (playbook→case mapping)
- Cross-case synthesis tables (window norms, tooling, comms, tracking convergence)
- Full codemod test fixtures (before/after Python + YAML)
- Full deprecation tracker implementation
- Per-drill rollback procedures + universal rollback
- Risk register with likelihood/impact/mitigation
- Go/No-Go graduation gate (6 criteria)
- MCP tool 12-month window rationale
- SPIFFE path codemod gap identified
- External client notification pattern

---

## §4 Lessons Learned (Updated with v3)

| # | Lesson | L2 Insight | L3 Candidate / Action |
|---|---|---|---|
| 1 | **Provenance headers lied**: ALL runs stamped `x-preview-f-free` regardless of actual model | Static header placeholders defeat provenance (M22) | ICS `{session_model}` must bind at inference time; file hub ticket |
| 2 | **Mid-flight snapshots masquerade as stalls** | Never analyze artifacts before completion signal | Dispatch protocol: completion marker check precedes consumption |
| 3 | **Prompt-closure wording routes comms** | Last line = routing instruction | Add standard closure line to dispatch protocol |
| 4 | **Explicit context loading > implicit history** | v3 (explicit 20-file load) produced 5× depth vs v2 (implicit history) | **Prime by explicit file reads, not session history** — controllable, auditable, reproducible |
| 5 | **Priming method matters more than model** | v2 (primed+strong) = 262 lines; v3 (primed+strong+explicit load) = 1,788 lines | **Explicit context loading is the force multiplier** — not model strength |
| 6 | **M26 frontmatter is a quality gate** | Only v3 produced M26-compliant artifacts | Make M26 frontmatter a dispatch requirement for research missions |
| 7 | **Self-contained code = executable specification** | v3's libcst/ast-grep/tracker code is directly reusable | Require self-contained code blocks in research deliverables |
| 8 | **Confounded A/Bs still have value** if confounds declared | Screening tests guide strategy | Always declare confound matrix in analysis header |
| 9 | **Isolation guards work** | `_v2`/`_v3` filenames + do-not-read prevented contamination | Reuse pattern for future A/B/C dispatches |
| 10 | **Explicit context loading is auditable** | v3's priming step read 20+ files — traceable | Log priming reads to Hivemind for reproducibility |

---

## §5 Disposition

- **Canonical merged artifacts** (v1+v2 merge): `MIGRATION_PLAYBOOK_SPEC_20260822_MERGED.md` + `REHEARSAL_LEARNING_PLAN_20260822_MERGED.md` (researcher workspace) — **superseded by v3** which is more complete and M26-compliant.
- **v3 artifacts** (researcher workspace): `MIGRATION_PLAYBOOK_SPEC_20260822_v3.md`, `MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v3.md`, `REHEARSAL_LEARNING_PLAN_20260822_v3.md` — **these are the canonical versions for ratification**.
- **Source artifacts retained** unmodified for provenance (M22): v1, v2, v3 all retained.
- **Follow-ups**: (a) HA/FastAPI citation spot-checks; (b) ICS provenance-binding ticket; (c) dispatch-protocol amendment (lessons 3, 4, 6); (d) promote v3 artifacts to `docs/migrations/` after Kali ratification.

---

## §6 Key Takeaway for Fleet Dispatch

**Explicit context loading (v3) dominated both fresh (v1) and implicit-history priming (v2).** The force multiplier was not model strength (v2 and v3 used the same Nemotron Ultra High) nor priming per se (v2 had full implicit history) — it was the **explicit, auditable context-loading step** that forced the session to internalize and cross-reference 20+ source files before writing.

**Recommendation**: For all high-stakes research missions, mandate an explicit "Context Loading" phase where the agent reads and synthesizes a defined file list before the research prompt. This is controllable, auditable, and produces 5× output quality at the same model cost.

---

## §7 Four-Way Extension: Model Isolation Test (v4)

### Design
To isolate the model variable, a fourth run repeated the EXACT v3 protocol (same explicit priming prompt, same 27-file load, same mission text, `_v4` filenames + isolation guard) on **Ox Alpha (`x-preview-f-free`), low thinking**. Priming phase ran on Nemotron Ultra High (matching v3's priming conditions); the Architect then switched the active model to Ox Alpha Low before dispatching the mission.

### Four-Way Matrix

| Run | Priming | Model / Thinking | Lines | Words | M26 FM | Code | Mermaid | YAML-DAG | Table rows |
|---|---|---|---|---|---|---|---|---|---|
| v1 | none (fresh) | Ox Alpha / low | 347 | 4,051 | 0/3 | 0 | 0 | 0 | 52 |
| v2 | implicit history | Nemotron U / high | 262 | 3,139 | 0/3 | 0 | 0 | 0 | 55 |
| v3 | explicit load | Nemotron U / high | 1,788 | 9,941 | 3/3 | 22 | 2 | 3 | 362 |
| **v4** | **explicit load** | **Ox Alpha / low** | **398** | **3,636** | **3/3** | **5** | **0** | **3** | **66** |

### Result: The Variable Decomposes

The Architect's hypothesis — *"with the same priming, Ox Low output should be closer to v3"* — is **confirmed for structure, refuted for depth**:

1. **STRUCTURE TRANSFERS VIA PRIMING**: v4 is the ONLY run besides v3 with full M26 frontmatter (3/3) AND machine-readable YAML DAGs (3). Neither v1 nor v2 produced these. Explicit priming taught the weak model the *conventions* — format compliance transferred perfectly across models.
2. **DEPTH REQUIRES COMPUTE**: v4 landed at 398 lines / 5 code blocks / 66 table rows — in the v1/v2 band, nowhere near v3's 1,788 / 22 / 362. Executable-code density, diagram generation, and exhaustive synthesis scale with model strength + thinking budget, not priming.
3. **BEHAVIORAL LESSONS TRANSFER TOO**: v4 hit a payload-size write failure and self-recovered using the **M15 skeleton-first + incremental-append technique** — a lesson it had read ~40 minutes earlier during priming (WAVE_2_3_GENESIS_TIPS). Priming transferred not just facts but *procedures*.

### Decomposition Table

| Output property | Driven by | Evidence |
|---|---|---|
| M26 frontmatter, YAML DAGs, doc-standard compliance | **Priming** (explicit load) | v4 = 3/3 FM despite weakest model; v1/v2 = 0/3 despite one having strongest model |
| Volume, code density, diagrams, exhaustive cross-referencing | **Model + thinking budget** | Only Nemotron-High runs exceeded 400 lines; v4 tracked v1/v2 band |
| Recovery procedures, protocol adherence (M15, isolation guards) | **Priming** | v4 applied M15 unprompted; all guarded runs respected do-not-read |
| Case-study breadth | Either (weak effect) | All runs found Pydantic/k8s/MCP/Django core; breadth beyond core varied |

### Refined Dispatch Doctrine

> **Prime for correctness of form; pay compute for depth of content.**
> - Weak-model sessions + explicit priming = conventionally-correct, moderately-sized deliverables (v4 profile) — ideal for routine tickets, doc updates, bounded research.
> - Strong-model sessions + explicit priming = production-grade, executable-specification deliverables (v3 profile) — reserve for canonical artifacts, playbook specs, anything downstream agents will execute against.
> - Unprimed sessions (any model) = exploration and evidence-gathering only (v1 profile); never ship their output as canonical without a primed pass.

---

## §8 Five-Way Extension: Thinking-Budget Dose-Response (v5)

### Design
Fifth run repeated the EXACT v3/v4 protocol (identical priming prompt + 27-file load + mission text, `_v5` filenames + isolation guard) on **Ox Alpha (`x-preview-f-free`) at MAX thinking** — DB-verified (`get-session`: variant `max`). This completes the cleanest controlled pair in the series: v4 vs v5 share model family AND priming protocol; only the thinking budget differs.

### Complete Five-Way Matrix

| Run | Priming | Model / Thinking | Lines | Words | M26 FM | Code | Mermaid | YAML-DAG | Table rows |
|---|---|---|---|---|---|---|---|---|---|
| v1 | none | Ox Alpha / low | 347 | 4,051 | 0/3 | 0 | 0 | 0 | 52 |
| v2 | implicit | Nemotron U / high | 262 | 3,139 | 0/3 | 0 | 0 | 0 | 55 |
| v3 | explicit | Nemotron U / high | 1,788 | 9,941 | 3/3 | 22 | 2 | 3 | 362 |
| v4 | explicit | Ox Alpha / low | 398 | 3,636 | 3/3 | 5 | 0 | 3 | 66 |
| **v5** | **explicit** | **Ox Alpha / max** | **777** | **7,620** | **1/3** | **6** | **0** | **1** | **115** |

### Finding 1: Thinking Budget Scales Depth (Clean Dose-Response)

With priming and model held constant (Ox Alpha, explicit load):
- **low → max = +95% lines** (398 → 777), +110% words, +74% table rows
- Extrapolated ladder across all runs: Ox-low 398 → Ox-max 777 → Nemotron-high 1,788

Depth scales monotonically with compute. v5 also produced the most *novel synthesis* of any Ox run: DEP-ID minting registry, k8s storage-vs-serving split ("stop writing legacy formats long before stopping reading"), Bevy's compile→rewrite→verify loop, "migrating FROM version" issue-template field, and the insight that our full-deployment visibility makes periodic census greps viable where Kubernetes must rely on telemetry.

### Finding 2: Format Compliance Is NOT Monotonic With Compute ⚠️

The surprise: v5's M26 frontmatter **regressed to 1/3** (v4: 3/3), YAML-DAGs dropped to 1 (v4: 3). Higher thinking spent its budget on substance and let structural convention slip — or compliance is stochastic when not reinforced. Either way:

> **Format compliance does not reliably increase with model capability. Explicit priming transfers conventions, but retention under high thinking budgets is fragile — dispatch prompts should carry hard format requirements rather than trusting primed conventions to survive.**

Practical rule: put "M26 frontmatter mandatory on all three artifacts" IN the mission prompt for high-thinking runs; priming alone carried it at low thinking but not at max.

### Finding 3: The Full Decomposition (Final)

| Output property | Driver | Evidence across 5 runs |
|---|---|---|
| Whether conventions appear AT ALL | Priming (explicit > implicit > none) | FM: 0/3 unprimed, 3/3+1/3 primed-explicit |
| How much content depth | Compute (model × thinking) | 398 → 777 → 1,788 monotonic ladder |
| Novel synthesis quality | Compute (thinking budget) | v5 (max) most novel Ox run; v3 (Nemotron high) overall |
| Convention RETENTION under load | Prompt enforcement (not priming alone) | v4 low-think kept 3/3; v5 max-think slipped to 1/3 |
| Procedural lessons (M15 recovery, isolation guards) | Priming | v4 applied M15 unprompted; all guarded runs respected do-not-read |

### Final Dispatch Doctrine (v2)

> 1. **Always prime explicitly** for anything canonical — priming is the gate for conventions and procedures.
> 2. **Match compute to consequence** — depth scales with the compute ladder (Ox-low < Ox-max < Nemotron-high); pay accordingly.
> 3. **Never rely on primed conventions surviving high-thinking runs** — restate hard format requirements in the mission prompt itself.
> 4. **DB-verify every run's model/variant** — recollection was wrong once already; `opencode.db` per-message metadata is the only provenance anchor.

---

## §9 Six-Way Extension: The High-Thinking Sweet Spot (v6)

### Design

Sixth run repeated the exact protocol (identical priming + mission, `_v6` filenames + isolation guard) on **Ox Alpha (`x-preview-f-free`) at HIGH thinking** — DB-verified (`get-session`: variant `high`). This completes the Ox Alpha dose-response curve: **low, high, max** — all with identical explicit priming.

### Complete Six-Way Matrix

| Run | Priming | Model / Thinking | Lines | Words | M26 FM | Code | YAML-DAG | Table rows |
|---|---|---|---|---|---|---|---|---|
| v1 | none | Ox Alpha / low | 347 | 4,051 | 0/3 | 0 | 0 | 52 |
| v2 | implicit | Nemotron U / high | 262 | 3,139 | 0/3 | 0 | 0 | 55 |
| v3 | explicit | Nemotron U / high | 1,788 | 9,941 | 3/3 | 22 | 3 | 362 |
| v4 | explicit | Ox Alpha / low | 398 | 3,636 | 3/3 | 5 | 3 | 66 |
| v5 | explicit | Ox Alpha / max | 777 | 7,620 | 1/3 | 6 | 1 | 115 |
| **v6** | **explicit** | **Ox Alpha / high** | **761** | **6,914** | **2/3** | **4** | **2** | **90** |

### Finding 1: High Is the Ox Alpha Sweet Spot — Depth Saturates

The dose-response on Ox Alpha with constant priming is **not linear; it saturates**:

```
lines:  low 398  --(+91%)-->  high 761  --(+2%)-->  max 777
FM:         3/3  -->            2/3   -->           1/3
```

- **low to high doubles depth (+91%)**; **high to max adds nothing (+2%)**. MAX thinking buys no measurable volume over HIGH on this model.
- Meanwhile format compliance declines **strictly monotonically** with thinking budget (3/3 -> 2/3 -> 1/3) — now confirmed with three points, not two.

> **Doctrine refinement**: On Ox Alpha, HIGH thinking is the efficiency frontier — full depth benefit, half the format-compliance damage of MAX. MAX is strictly dominated (same depth, worst convention retention). Reserve MAX for tasks where reasoning depth per-step matters more than artifact production.

### Finding 2: Substantive Quality at High Thinking

v6 delivered strong novel synthesis despite mid-pack volume: anti-permashim CI gate (shims tagged `# DEPRECATED-SHIM <id> removal=<v>`, CI fails past-date shims — KEP-1635 analogue), `omega doctor --deprecations` self-diagnostic (HA Repairs-dashboard analogue), the akasa shim-library war story, the kodare `'ß'.upper()` production incident as silent-change evidence, and four open questions correctly routed to Architect ruling instead of guessed. High thinking produced judgment quality comparable to v5's novelty while retaining better format discipline.

### Finding 3: Final Decomposition (Six Runs)

| Output property | Driver | Evidence |
|---|---|---|
| Whether conventions appear AT ALL | Priming (explicit > implicit > none) | FM 0/3 unprimed vs 1-3/3 primed |
| Content depth | Compute, saturating per model | Ox: 398/761/777 saturates at high; Nemotron-high 1,788 still king |
| Convention retention | Inversely correlated with thinking budget | FM monotonic decline 3/3 -> 2/3 -> 1/3 on Ox ladder |
| Judgment/novelty quality | Thinking budget (high sufficient) | v5 and v6 both novel; v6 with less format damage |
| Procedural lessons (M15 recovery, guards) | Priming | All guarded runs compliant |

### Final Dispatch Doctrine (v3)

> 1. **Always prime explicitly** for canonical work — priming gates conventions and procedures.
> 2. **HIGH thinking is the default frontier** — on Ox Alpha it captures ~100% of available depth; MAX is strictly dominated for artifact production.
> 3. **Restate hard format requirements in the mission prompt** — convention retention declines monotonically with thinking budget regardless of priming.
> 4. **Nemotron-class models remain the tier for canonical specs** (v3 profile) when depth density matters more than latency/cost.
> 5. **DB-verify every run's model/variant** — provenance lives in `opencode.db`, nowhere else.

---

## §10 Post-Series Confound Discovery: Search Tooling (Variable #4)

**Spotted by the Architect at series close**: runs did NOT use uniform search tooling — v1 ran the parallel-search fleet; v5 hit an Exa 401 and fell back; v6 ran Exa-led. Search tier plausibly affects evidence breadth, citation mix, and source quality — meaning **V4 (search tooling) was uncontrolled across all six runs** and joins model/thinking/priming in the confound matrix.

**Impact assessment**: The core Laws (1–6) rest on convergent, mechanically-measured markers (volume, frontmatter, code density) that are unlikely to be search-tool-sensitive. But *evidence-rigor* findings (citation counts, source registers, refusal-to-pad behavior) are now suspect until Series 2 isolates V4.

**Disposition**: Series 2 (search-tool isolation) is now the mandated next experiment — protocol codified in `SPLIT_TESTING_MANUAL_20260822.md` §6. All future series must pin the search tier as a controlled variable.

---

*Analysis by Kali, 2026-08-22. Method: full read of all eighteen artifacts (6 runs x 3 files); no sampling. Quality markers counted via grep across artifact set. Models DB-verified per run.*

*⬡ OMEGA ⬡ SPLIT-TEST-ANALYSIS ⬡ v1.4.0 ⬡ 2026-08-22*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
