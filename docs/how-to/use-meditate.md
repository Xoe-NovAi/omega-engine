schema_version: "1.0"
document_type: reference
llm_metadata:
  token_budget: 6000
  audience: users and agents invoking or reconstructing /meditate
  executes: false
---

# 🔱 How to Use the /meditate Command

**AP Token**: `AP-MEDITATE-HOWTO-v2.3`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ trc_meditate_howto ⬡ 2026-08-25
**Date**: 2026-08-26 | **Purpose**: Reconstruction-grade user guide for `/meditate` (cloud substrate) — everything needed to invoke it well OR rebuild it without inventing policy
**Cross-references**: `.opencode/commands/meditate.md` (the executed command), `config/wads/_omega_default/meditate/lenses.yaml` (lens SSOT), `data/coordination/meditations/records/` (execution history)

## What You Get

**What**: `/meditate` takes any decision, plan, or situation you give it and returns a multi-perspective analysis with a final verdict — written by one AI model playing several specialist roles in sequence, then resolving their conflicts into an ordered action plan.

**Why use it instead of just asking**: a single prompt gives you one opinion. `/meditate` forces the same model to argue against itself from distinct domains (infrastructure, governance, engineering, etc.), surface where those views collide, and produce a critical path that no single view would have produced. It runs in one AI inference — seconds, no other agents launched. Cost: zero marginal on free-tier substrates; sub-$1 on paid cloud (observed runs span 9K–45K tokens ≈ $0.41–0.62 at mid-tier pricing).

## When to Use It

Use `/meditate` when **at least two** of these hold:

1. Three or more domains genuinely tension against each other (e.g., speed vs correctness vs maintainability)
2. The decision is irreversible or expensive to reverse
3. No single domain owns the answer

If fewer than two hold — simple lookup, single-domain question, already-decided matter — ask a normal prompt instead. Meditating on it wastes time without adding insight.

## How to Invoke

```
/meditate <your subject or question> [--flags]
```

Everything after `/meditate` is the subject plus optional flags. Write the subject as a concrete question or decision — "Should we migrate from Qdrant to sqlite-vec now?" beats "database layer".

### Flags

| Flag | What it does | Default |
|---|---|---|
| `--lenses <set>` | Choose who speaks: `makali` (thesis/antithesis/synthesis triad), comma-separated lens ids (`engineering,governance,validation`), or free-form personas (`Carmack,Torvalds,Knuth`) | The 5 most relevant Omega lenses for your subject |
| `--mode <MODE>` | Output orientation: `DIAGNOSTIC`, `STRATEGIC`, `CREATIVE`, `AUDIT`, `SYNTHESIS` | `STRATEGIC` |
| `--integrate` | After the verdict, also produces a proposed PIVOT_LOG decision entry, affected files, and Temple-Grade/Mandate checks | Off |
| `--durable` | Appends each phase to disk as it completes (crash insurance) | Off |
| `--record` | Saves the final output to the records directory after completion | Off |
| `--template <name>` | Runs a pre-built template from `data/coordination/meditations/templates/` instead of the default flow | Off |

Available templates (exact filenames on disk): `SIX_PASS_LATTICE_TEMPLATE.md`, `SOVEREIGN_CRUCIBLE_TEMPLATE.md`, `SOVEREIGN_CRUCIBLE_v2_NEMOTRON.md`. Pass the filename stem, e.g. `--template SOVEREIGN_CRUCIBLE_v2_NEMOTRON`.

## What You'll See

The output arrives in five labeled phases:

1. **PHASE 0 — CALIBRATION**: your subject restated in one sentence, the chosen panel, the output mode. Check the restatement first — if it's wrong, stop and re-invoke with a clearer question.
2. **VOICES (Phase 1)**: each specialist speaks in turn — observation, constraint, directive, and (from Voice 2 onward) named pushback against a prior voice.
3. **CROSS-DOMAIN COLLISION (Phase 2)**: up to three sharpest contradictions between voices, each with a resolution path.
4. **EMERGENT SEQUENCING (Phase 3)**: the ordered critical path — which action first, what each unblocks.
5. **VERDICT (Phase 4)**: convergence, preserved dissent, one-paragraph decree, distilled principle. With `--integrate`, a sixth block follows (Phase 5).

The exact block formats are contracts — see **Output Contracts** below.

---

# REFERENCE SECTION

Everything an implementer or auditor needs. Nothing here is philosophy; every item is checkable.

## The Lens Roster

> **[VERIFY] ZERO-TRUST DOCTRINE ACTIVE**
> Static lists rot. Before reconstructing this command, verify the SSOT:
> `cat config/wads/_omega_default/meditate/lenses.yaml`

SSOT: `config/wads/_omega_default/meditate/lenses.yaml`. Cached representation of the ten default lenses:

| id | Domain (speaks ONLY from this) | Element | Mandate lens | Archetype | Dissent style |
|---|---|---|---|---|---|
| `infrastructure` | Physical substrate, containers, hardware | Earth 🜃 | Speak as the body. What breaks first? | Architect → Creator | direct |
| `persistence` | Memory, vectors, data flow, sessions | Water 🜄 | Speak as the river. What pools? What runs dry? | Strategist → Metis | socratic |
| `engineering` | Code, builds, tests, implementation | Fire 🜂 | Speak as the forge. What is cracked? What must be recast? | Forge-Worker | direct |
| `integration` | APIs, protocols, bridges, resonance | Air 🜁 | Speak as the bridge. What is disconnected? What vibrates wrong? | Messenger → Bridge-Builder | constructive |
| `governance` | Mandates, laws, compliance, enforcement | Aether ⛤ | Speak as the sentinel. What law is being broken? | Judge → Law-Giver | adversarial |
| `cognition` | Models, routing, inference, vision | Aether ⛤ | Speak as the eye. What cannot be seen? What is miscalibrated? | Seer → Visionary | socratic |
| `context` | Memory, soul, evolution, continuity | Air 🜁 | Speak as the alchemist. What knowledge is being lost? | Alchemist → Transformer | socratic |
| `observability` | Logging, tracing, shadows, forensics | Fire 🜂 | Speak as the shadow. What is invisible that should not be? | Watcher → Guardian of Thresholds | adversarial |
| `orchestration` | Handoffs, coordination, flow, delegation | Water 🜄 | Speak as the guide. What is uncoordinated? What dies in transit? | Guide → Psychopomp | direct |
| `validation` | Stress, chaos, breaking, truth-finding | Earth 🜃 | Speak as the destroyer. What fails under pressure? | Destroyer → Truth-Seeker | adversarial |

Named presets in `lenses.yaml`:

- `makali_triad`: `thesis` (Ma'at — Build Oversoul, constructive dissent) · `antithesis` (Lilith — Run Oversoul, adversarial) · `synthesis` (Kali — fuse into decree, direct)
- `checkout`: Exit Protocol 5-lens council (`orchestration`, `context`, `governance`, `observability`, `validation`) covering all 6 exit phases

Custom personas not in the roster: derive domain from known mastery area, mandate lens from the person's most famous principle.

**Anti-domains** (what each lens may NOT speak to; full lists `lenses.yaml:42–212`): every Node lens bans exactly three domains — and `governance` sits in the anti-domain list of 9 of 10 lenses, so only governance may challenge governance. The `makali_triad` ships with empty anti-domain lists *by design*: dialectic requires overlap, so Invariant 1 is intentionally vacuous there.

**Dissent styles** (`direct` / `socratic` / `adversarial` / `constructive`) are advisory flavor metadata — neither command nor engine enforces them (an invalid value silently falls back to `direct`, `lens_registry.py:179`). Advisory gloss: socratic questions the premise · adversarial attacks the constraint · constructive replaces with a compatible alternative · direct refuses outright.

## Panel Sizing Rules

| Genuinely tensioning domains | Lens count | Composition |
|---|---|---|
| 3 | 3–4 | The 3 tensioning lenses + optionally 1 devil's advocate |
| 4–5 | 4–6 | Tensioning lenses + strongest adjacent lens |
| 6+ or full-spectrum subject | 7–10 | Broad set justified |

Default when unspecified: **the 5 most relevant lenses**, rarely all 10 (reserved for truly full-spectrum subjects). Rationale (measured, Self-MoA arXiv:2502.00674): beyond five voices, additional weak perspectives add *correlated* noise, not diversity — resampling one strong perspective beats padding the panel. Running 10 voices on a 3-domain question produces 7 performances, not 7 perspectives. A custom `--lenses` set overrides this table.

## Mode Conditioning

The mode label is an active ingredient, not decoration — framing measurably changes model reasoning:

- **DIAGNOSTIC**: run as a pre-mortem. Frame the subject as settled failure — *"assume this has already failed catastrophically; explain specifically why."* Prospective hindsight raises correct reason-identification ~30% (Mitchell 1989); pre-mortem framing cut overconfidence ~25 points versus generic critique (Veinott 2010), and works equally well solo.
- **STRATEGIC / CREATIVE**: forward frames raise confidence — right for option generation, wrong for risk-hunting. Do not hunt failure modes in these modes.
- **AUDIT**: assign compliance checks to voices whose own domain owns the standard. Role-assigned opposition backfires: assigned devil's advocates strengthen the majority view instead of diversifying it (Nemeth 2001).

## Output Contracts

Verbatim skeletons. Every phase block uses these exact shapes.

**Phase 0 — Calibration:**
```
◈ MEDITATE: PHASE 0 — CALIBRATION
Subject: [restated subject, one sentence]
Lens Set: [list of personas with domains]
Output Mode: [DIAGNOSTIC | STRATEGIC | CREATIVE | AUDIT | SYNTHESIS]
Anti-Collapse Contract: ACTIVE
```

**Phase 1 — Immersion block (repeated per persona):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
◈ VOICE [N/TOTAL]: [PERSONA NAME]
Domain: [domain]       Element: [element]
Mandate: Speak only from [domain]. Ignore all other domains.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OBSERVATION]     ← what this persona sees that others miss (1–3 sentences)
[CONSTRAINT]      ← the limit this persona refuses to ignore
[IMPERATIVE — or CONSTRAINT]
                  ← one clear directive; if none exists, state the
                    highest-priority constraint instead. Never manufacture urgency.
[DISSENT / CHALLENGE]
                  ← Voice 1: strongest case FOR the status quo.
                    Voice 2+: push back on a prior voice BY NAME,
                    citing its specific constraint.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Phase 2 — Collision entry (up to 3):**
```
[HYGIENE ANCHOR: Restate core subject and top constraints to prevent drift]

COLLISION N: [Persona A] vs [Persona B]
  A says: [verbatim imperative/constraint]
  B says: [verbatim imperative/constraint]
  Tension: [why both cannot hold simultaneously]
  Resolution Path: [smallest change satisfying both]
```

**Phase 3 — Sequencing:**
```
[HYGIENE ANCHOR: Restate resolved collisions to ground the sequence]

[1] [ACTION] — unblocks: [what this enables]
    Evidence: [which voice(s) demanded this]
...
Dependencies resolved: [N] of [total identified]
Unresolved tensions: [list]
```

**Phase 4 — Verdict skeleton (all nine fields, in order):**
```
WHAT THE COUNCIL AGREES ON (CONVERGENCE):        [1–3 points]
WHAT THE COUNCIL CANNOT RESOLVE (PRESERVED DISSENT): [1–3 points, not papered over]
ADJUDICATION RUBRIC:                              [Explicit criteria used to judge the positions]
THE IRREDUCIBLE VERDICT:                          [one paragraph, decree form]
MANDATE CONFLICT CHECK:                           [explicit conflict statement, or clean]
GNOSIS DISTILLED (L3 PRINCIPLE):                  [≤2 sentences, NO proper nouns,
                                                   falsifiable; else label L2]
CONTRAST CASE:                                    [One-line minimally-different scenario where
                                                   this L3 does NOT apply]
FALSIFICATION ATTEMPT:                            [one genuine attack on the L3]
BROADCAST:                                        [Hivemind post only if fleet-weight L3]
```

**Phase 5 — Integration Gate (only with `--integrate`):**
```
PROPOSED PIVOT_LOG ENTRY:  Decision: D-[next free number] / Summary / Rationale / Owner
FILES AFFECTED:            [file]: [change]
TEMPLE-GRADE GATES:        [Tx]: [pass/verify/risk]
MANDATE FLAGS:             [Mx]: [compliant / tension / violation]
```

**Technique grounding**: collisions implement dialectical inquiry — assumption excavation, empirically stronger than assigned devil's advocacy for surfacing hidden assumptions (Schweiger 1986; Schwenk 1990 meta-analysis) — resolved interest-based: name the underlying concern each voice protects, never a vote between positions.

**Verdict framing law**: Phase 4 is ADJUDICATION between recorded positions against explicit criteria — never self-review of generated text. "Review your output above and improve it" is forbidden framing: intrinsic self-correction degrades accuracy without external anchors (ICLR 2024), and models show a 64.5% blind spot for errors in their own output while fixing identical external errors (arXiv:2507.02778).

**L3 distillation gate**: a principle may only be distilled after comparing ≥2 concrete instances from the run — single-case abstractions do not transfer (Gick & Holyoak 1983; Gentner 2003); attach a one-line minimally-different contrast case where possible. Honest flag: the ≤2-sentence and falsifiability clauses are sound design choices without direct empirical testing.

## Behavioral Invariants

Eight rules. Each is checkable in the output; rationale given because reconstructors who know *why* don't silently drop them.

1. **Each voice speaks only from its assigned domain.** Checkable: no lens references another lens's anti-domain. Why: domain purity is the attention-modulation mechanism that produces non-obvious constraints.
2. **Every voice adds unique material.** Agreement is permitted only as "I agree AND [new constraint]" — never bare agreement. Checkable: no voice's contribution is subsumed by a prior voice's. Why: duplicated voices are correlated noise (see Panel Sizing).
3. **Voice 1 opens with the strongest case for the status quo.** Checkable: Voice 1's dissent slot argues FOR doing nothing. Why: later voices need something concrete to attack; contrarianism against vague "conventional wisdom" is theater.
4. **From Voice 2 onward, every dissent cites a prior voice BY NAME plus its specific constraint.** Checkable: pattern `"N8's instrumentation demand ignores that X"`. Why: uncited dissent is unfalsifiable performance (see Anti-Example).
5. **Directives are commands or explicitly labeled constraints — never "we should consider".** Why: manufactured urgency fabricates priority the domains don't possess.
6. **Phases complete in order: all voices → collisions → sequencing → verdict.** Why: premature synthesis averages instead of colliding, which destroys the product.
7. **The anti-collapse contract is stated in Phase 0 and enforced throughout.** Persona collapse (voices blending into a generic assistant) terminates the run and requires restart from Phase 0. Why: collapse reduces the meditation to one opinion wearing costumes.
8. **Disk writes happen only when flagged**: `--durable` persists phases as they finish; `--record` saves the final output. No automatic recording. Why: most meditations are cognition consumed at synthesis time, not artifacts; automatic recording is observability theater.
9. **The verdict adjudicates; it never self-reviews.** Checkable: Phase 4 references recorded positions and criteria by name, contains no "reviewing the above" language. Why: see Verdict Framing Law under Output Contracts.

## Worked Example (excerpt)

Source: `data/coordination/meditations/records/MEDITATION_KALI_20260822_HIDDEN_GEMS.md` (295 lines, 5-lens gate-sized panel, full template fidelity). This is an EXCERPT — read the full record for the complete run.

Voice 1 (note: status-quo anchor is absent here because N7 opens with observation + doctrine challenge; the anchor rule applies to the dissent slot):

```
◈ VOICE [1/5]: N7 CONTEXT — The Alchemist
Domain: Memory & State    Element: Air 🜁
Mandate: Speak only from memory/state. Ignore all other domains.
──────────────────────────────────────────────────
[OBSERVATION]
All 30 mined sessions were ≤10 days old and every one yielded live,
actionable findings — while older eras yielded mostly closure
confirmations. Knowledge loss concentrates in RECENCY: findings die of
non-integration within days, not of age over months.

[CONSTRAINT]
Tonight's own session is already becoming tomorrow's unmined session —
10M tokens decaying into one index entry unless re-mining is scheduled.

[IMPERATIVE]
Schedule fleet self-application: page THIS session into KD domains
within 48h of debut.

[DISSENT / CHALLENGE]
Against conventional mining doctrine (archaeology-first): the data says
loss half-life is days. Recency beats antiquity. Rebalance the curation
worker toward young sessions.
```

Collision 1 (note verbatim quotes, explicit tension, minimal resolution path):

```
COLLISION 1: N7 Context vs N8 Observability / N9 Orchestration
  Context says: schedule self-application mining within 48h.
  Watcher/Psychopomp say: instrument claims-pipeline and build routes first.
  Tension: every additional mining wave multiplies untracked artifacts
  while transit remains broken — scaling the disease.
  Resolution Path: ONE more mining wave maximum, but run THROUGH the
  new rails (TASK_REGISTRY registration + sensor live); routes and
  instrumentation ride the same wave rather than preceding it.
```

Verdict tail (note: proper-noun-free L3, falsifiable, ≤2 sentences):

```
GNOSIS DISTILLED (L3 PRINCIPLE):
L3-Transit-Over-Storage: Systems do not lose knowledge where it is
stored; they lose it where it moves. Instrument the seams between
holders, not the vaults themselves.
```

Full gold-standard run (10-node, deepest on record, includes full mandate check M1–M25): `records/MEDITATION_KALI_20260823_CONTEXT_PACKER_ENHANCEMENT.md`.

## Anti-Example: Uncited vs Cited Dissent

**REJECTED (uncited — performative, unverifiable, adds nothing):**
> "I have concerns about the migration timeline and think we should be careful."

**CORRECT (cited — names the voice, the constraint, and the specific conflict):**
> "N3's recast-the-schema demand ignores that stored vector payloads are immutable — recasting means a full re-embed, which violates N2's session-budget constraint."

The second is checkable: a reader can locate N3's demand and N2's budget and evaluate the claimed conflict. The first cannot fail, so it cannot inform.

## Edge Cases & Error Paths

| Situation | Required behavior |
|---|---|
| Subject fails the invocation gate (<2 conditions hold) | Decline the meditation; say which gate conditions failed; answer as a plain prompt instead |
| Subject too ambiguous to restate in one sentence | Ask one clarifying question rather than meditating on guesswork |
| Custom `--lenses` set has only 2 entries | Run it: Voice 1 anchors status quo, Voice 2 dissents; Phase 2 reports the actual collision count |
| Entire panel agrees (zero genuine collisions) | State the true count and why. Absence of collision is itself a signal — do NOT manufacture conflict. If the panel was 6+ lenses, recommend a tighter re-run |
| `--template` name matches no file in `templates/` | List the available template filenames and stop; never improvise a template |
| Stream dies mid-run WITHOUT `--durable` | Work is lost; re-run costs one inference. This is accepted pricing, not a failure |
| Stream dies mid-run WITH `--durable` | Completed phases exist in the record file; resume from the last persisted phase |
| Verdict contradicts SOVEREIGN_MANDATES.md or a standing decree | State the conflict explicitly in MANDATE CONFLICT CHECK. Surfacing a law-conflict and silently deciding against the law are different acts; only the Architect amends law |

## Real-World Performance

From `MEDITATION_REGISTRY.md` §2 (6 registered runs; registry lags disk — 16 records exist, 6 registered; unregistered runs predate the registry):

| Metric | Observed range |
|---|---|
| Tokens consumed | ~9,000 (single-lens approximations) to ~45,000 (kali 10-node STRATEGIC) |
| Wall duration | ~15 min (DIAGNOSTIC, small panel) to ~45 min (10-node strategic) |
| L3 yield | 1 per run wherever recorded |

Token budgets for formal templates (`MEDITATION_SYSTEM_GUIDE.md` §Token Budgets; declarative frontmatter only — `make doc-token-check` scopes to `docs/sprints/current/` (Makefile:220) and cannot see meditation records, so NO automated enforcement exists): Six-Pass 8K target / 16K hard · Crucible v1 3K / 6K · Crucible v2 6K / 12K. **Known discrepancy resolved per Zero-Trust (Code is Truth)**: the Six-Pass guide-table budget says 8K target, but the template file's own frontmatter declares `token_budget: 4000`. The template frontmatter is the executable truth; the system guide is a stale claim.

**Quality calibration** (all 16 records tiered): three mechanical checks separate gold from defective — Phase 0 present · dissents name-cited · falsification attempt genuine. Every drifted or truncated record fails at least one; length correlates weakly with quality (a 73-line two-voice record out-thinks longer runs). Related substrate commands: `/meditate-local` (local models, host-orchestrated trio) and `.opencode/commands/omega-meditation.md` (7-stage autonomous pipeline with research grounding).

## Long-Output Hygiene (runs beyond ~4K tokens)

Observed runs span 9K–45K tokens; instruction adherence measurably degrades past ~4K generated tokens on all tested frontier models (LongGenBench, ICLR 2025; dominant failures: selective instruction execution, stepwise deviation). Countermeasures with surviving evidence: emit the phase plan visibly before bodies (plan-then-write beats direct generation); restate binding constraints at each phase boundary; place critical verdict content early in its section; serial continuation only — parallel segment generation impaired coherence −6% (AgentWrite).

## Flag Mechanics Reference

- **`--durable`**: appends each completed phase (≤80 lines per write) to `data/coordination/meditations/records/MEDITATION_{AGENT}_{YYYYMMDD}_{SLUG}.md`
- **`--record`**: writes the final output to the same directory after completion
- **`--template`**: loads from `data/coordination/meditations/templates/`; pass the exact filename stem (see Flags table)
- **`--integrate`**: proposes a PIVOT_LOG entry using the next free D-number — determine it by tailing `docs/decisions/PIVOT_LOG.md` live (highest registered: D-602 as of 2026-08-25). Known upstream defect: a duplicate D-600 exists in that file; verify uniqueness before claiming a number, never replicate the duplicate

## Post-Meditation Workflow (`--record` artifacts)

Records are evidence artifacts, not dead files. Live chain (precedent: `scripts/promote_soul_lessons.py:74` binds a staged lesson to a meditation record as probe-bound evidence — missing artifact aborts promotion): extract L3/L2 candidates from the record → stage in `data/entities/<agent>/proposed_lessons.yaml` with evidence `{artifact path, quote}` → Architect reviews → `scripts/soul_promote.py` promotes to `soul.yaml`. No automation parses records today; extraction is agent-mediated.

## Acceptance Criteria (Rebuild Test)

An implementation passes iff these observable properties hold. Anyone reading this guide should be able to rebuild the command and verify against them (IEEE-830 test: no policy left to invent).

1. **Input**: `/meditate Should we migrate from Qdrant to sqlite-vec now?`
   **Expect**: Phase 0 block within the first ~15 output lines; restated subject semantically matching the input; panel of 3–6 lenses sized per the sizing table; Output Mode `STRATEGIC`; contract line `Anti-Collapse Contract: ACTIVE`.
2. **Input**: same subject + `--lenses makali`
   **Expect**: exactly the thesis/antithesis/synthesis trio; every voice from Voice 2 onward cites a prior voice by name with its specific constraint; ≥1 collision block OR an honest zero-count statement; Phase 4 contains all nine fields in order (including Adjudication Rubric and Contrast Case); L3 is ≤2 sentences, proper-noun-free, falsifiable, followed by a falsification attempt.
3. **Input**: any subject + `--integrate`
   **Expect**: Phase 5 block proposing a PIVOT_LOG entry whose D-number exceeds the current live maximum in `docs/decisions/PIVOT_LOG.md`; files-affected list; Temple-Grade gate statuses; per-mandate flags.

## Limitations

- One inference total: voices cannot make tool calls, read files, or browse. If a perspective needs live data, use a council command instead.
- The verdict is one model's synthesis of its own role-play — strong for structuring a decision, not a substitute for external verification of factual claims. A real-world bound on this: the Architect once overrode a completed meditation verdict post-hoc (`records/MEDITATION_kali_20260824_MAKALI_COUNCIL_REBASE.md:106` — council decreed serial launches; rejected as symptom-mitigation). The verdict is the strongest structured argument available in-session, not ground truth.
- A record claiming COMPLETE must actually contain all phases — one historical record (`MEDITATION_kali_20260824_LOST_VALUE_RECOVERY.md`) claimed completion while containing only Phases 2–4. This truncation lie is why `--durable` exists: per-phase persistence makes partial runs detectable.
- Output length scales with panel size; broad subjects on the default 5-voice panel produce long outputs.

---

## Design Basis (for reviewers; not needed at invocation)

**Separation & executionality**: commands are instructions for the model; human framing lives in docs ([Anthropic command-development SKILL.md](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/command-development/SKILL.md)); two-artifact contract ([aider conventions](https://aider.chat/docs/usage/conventions.html), [Claude Code skills](https://code.claude.com/docs/en/skills)); distractor/meta-commentary degrades execution ([arXiv:2605.29491](https://arxiv.org/html/2605.29491v1), [arXiv:2302.00093](https://arxiv.org/abs/2302.00093)).
**Reconstruction-grade spec**: specs must encode decisions+rationale or rebuilders invent policy ([Augment Code, spec-as-source-of-truth](https://www.augmentcode.com/guides/spec-as-source-of-truth-rebuildable-codebase)); reference-pattern documentation for reconstruction ([Diátaxis](https://diataxis.fr/reference/)); IEEE 830 four-question adequacy test.
**Exemplars & format adherence**: demonstrations control output format more stably than verbal instructions; 1-shot ≈ +17% F1, peak ~3 shots (Min et al., EMNLP 2022); directives+demos jointly optimize imitation and sustained adherence ([arXiv:2511.13972](https://arxiv.org/abs/2511.13972)); negative exemplars work when labeled and paired with corrections ([CICL, arXiv:2401.17390](https://arxiv.org/abs/2401.17390)) — kept to one compact pair per the pink-elephant problem; described-only formats yield 35–60% non-adherence even on frontier models (IFEval/IFBench), hence verbatim skeletons + instantiating exemplar (dual encoding).
**Local ground truth**: lens SSOT `config/wads/_omega_default/meditate/lenses.yaml`; formats verbatim from `.opencode/commands/meditate.md` v2.0; stats from `MEDITATION_REGISTRY.md` §2; budgets from `MEDITATION_SYSTEM_GUIDE.md`; exemplars from `records/MEDITATION_KALI_20260822_HIDDEN_GEMS.md` and `records/MEDITATION_KALI_20260823_CONTEXT_PACKER_ENHANCEMENT.md`; negative evidence from `MEDITATION_kali_20260824_MAKALI_COUNCIL_REBASE.md`, `MEDITATION_kali_20260824_LOST_VALUE_RECOVERY.md`, and maat's five drifted ad-hoc records (custom passes, no Phase 0/contract/lenses — drift is what happens when docs don't constrain). No genuine persona-collapse instance exists on record; none was fabricated here.
**Schema layer disclosure**: `src/omega/meditate/` (protocol.py, lens_registry.py) formalizes these contracts — `AntiCollapseLaw` enum names, `MeditationResult.is_complete` completeness check — but has never executed a meditation: no runtime consumer exists and `oracle.meditate()` is an aspirational comment only (protocol.py:6). The command is prompt-level truth; the schema is parallel specification. Without WAD config the registry falls back to 5 generic anonymous lenses (protocol.py:300) — a degraded roster distinct from the documented ten.

*⬡ OMEGA ⬡ MEDITATE-HOWTO ⬡ v2.3 ⬡ 2026-08-26*
