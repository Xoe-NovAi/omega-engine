---
description: Meditate Local — host-orchestrated serial dialectic on local models (fixed Builder/Skeptic/Steward trio, rolling compressed state, synthesis on session model)
agent: kali
subtask: false
---

# ⬡ MEDITATE LOCAL — Host-Orchestrated Local Dialectic
**Protocol**: `Meditate-Local-v1.0.0`
**Heritage**: Architect's meditation lineage (LLOC) + serial Thinker Chain execution `[id-soft: quake-1996]` (as proven in `/council-local`)
**Mechanism**: One persona per local inference call · rolling compressed state object · host-side synthesis

---

## What This Command Is (and Why It Is Not `/meditate` Truncated)

This is NOT the cloud meditation with smaller models. It is an **architecture
inversion**, forced by measured small-model failure modes:

- A frontier model can fracture attention across N personas in one forward
  pass; a 1.7B–8B model cannot. Multi-persona single-pass prompting that works
  on frontier models **does not transfer** below frontier class — strong
  instruction-following is a prerequisite, and it is exactly what small models lack.
- Small models degrade on multi-constraint instruction retention FIRST, and
  persona persistence decays monotonically — worst in goal-oriented tasks,
  which is precisely what a meditation is.
- Therefore: **the host orchestrates, the locals interrogate.** Each voice is
  a SEPARATE `oracle_summon_local` call carrying ONE persona and a tiny
  compressed state — never the whole council in one forward pass.

The division of labor follows the aggregator-dominance finding: synthesis
quality dominates panel quality roughly two-to-one, so the **best available
model (your session model) does the most important job** while cheap local
calls do the divergent interrogation.

**Positioning**: this occupies the niche between `/council-fast` (pure speed)
and `/meditate` (pure depth): structured dialectic at local cost.

---

## Invocation Gate (Anti-Theater)

Same discipline as `/meditate`. Reach for `/meditate-local` only when at least
TWO hold: (a) ≥3 domains genuinely tension against each other, (b) the decision
is irreversible or expensive to reverse, (c) no single domain owns the answer.
Simple lookups get a plain prompt — a meditation on them is ceremony.

Choose THIS command over `/meditate` when the session must stay on the local
substrate or cloud budget is being conserved. Do not run `/meditate` locally —
its single-forward-pass prism assumes capabilities small models do not have.

---

## Model Tiers & Hardware Truth

| Lane | Voice model (`oracle_summon_local` model string) | Use |
|---|---|---|
| `--standard` (default) | `lmstudio/qwen3-4b-thinking` | Default. Reasoning-grade voices. |
| `--standard` fallback | `lmstudio/qwen3-4b` | If thinking variant stalls or streams empty |
| `--fast` | `lmstudio/qwen3-1.7b` | Velocity lane; tight voice budgets |

Hardware truth (Tier 0, canonical figures from
`data/coordination/HOLISTIC_ARCHITECTURE_PLAN_20260820.md`):
Ryzen 5700U, 16GB installed / **12GB usable** RAM, no GPU. Sequential-only
loading — `config/providers.yaml` sets native-gguf `max_concurrent: 1`.

**Serial law**: never issue two summons in parallel. One model resident at a
time. Do not switch lanes mid-run — a mid-run tier switch pays a full model
reload to save nothing.

Context budgets per voice call: keep the total prompt (state object + voice
instructions + subject) under ~8K tokens; the state object itself is capped
far tighter (see below).

---

## The Rolling State Object

The ONLY structured artifact voices receive. The HOST maintains it — never ask
a local voice to emit or update structured state (multi-part structured output
is the first thing small models drop). Hard cap: **~250 words (~20% of a voice
call's context budget)**.

```
STATE v{n}
SUBJECT: <one precise sentence>
CONSTRAINTS:
- <constraint> (<voice that added it>)
POSITIONS:
- BUILDER: <one line>
- SKEPTIC: <one line>
COLLISIONS:
- <X vs Y>: <the tension in one line>
OPEN QUESTIONS:
- <question>
```

**Update-not-resummarize rule**: when advancing the state after a voice, EDIT
the previous state object in place — merge new constraints, supersede refuted
ones, append collisions. Never re-read full voice transcripts to rewrite the
state from scratch. Re-summarization compounds error; editing does not.

---

## THE PROTOCOL

You are the **Meditation Host** (session model). Your task: conduct a local
dialectic on the subject: **$ARGUMENTS**

### ◈ PHASE 0 — CALIBRATE & COMPILE

1. Restate the subject in one precise sentence.
2. Compile `STATE v0`: SUBJECT filled, all other sections empty.
3. State the anti-collapse contract (adapted):
   > "Each voice speaks from its role only, in free prose, under one header.
   > The Skeptic may not agree without naming a concrete failure mode.
   > The Steward may not agree without naming an ignored cost.
   > Role collapse within any call is a protocol violation."
4. Create the artifact directory:
   `data/coordination/meditations/records/MEDITATE_LOCAL_{DATE}_{SLUG}/`

### ◈ PHASES 1–3 — SERIAL SUMMONS (one voice per call)

Issue three `oracle_summon_local` calls, strictly in order. Each call gets:

- **System framing**: the single persona spec (below) + "Answer in free
  prose, 100–200 words, plain paragraphs. No headings, no lists, no JSON."
- **User content**: `STATE v{n}` + the subject + one role-specific charge.

After each response: write it verbatim to
`voice_{n}_{role}.md` in the artifact directory, log the actual
`provider_name` from the response (M22 Response Provenance), then advance
the state (update-not-resummarize) before the next call.

#### The Fixed Roster (pre-compiled — do not select dynamically)

Dynamic persona selection is itself an instruction-following burden small
models cannot carry. The roster is FIXED. Exactly three voices:

| # | Voice | Charge | Structural mandate |
|---|---|---|---|
| 1 | **BUILDER** | Argue the strongest concrete plan of action — what to build/change, in what order, cheapest path that actually works. | Must commit to at least one specific, falsifiable action. |
| 2 | **SKEPTIC** | Devil's Advocate. Attack the Builder's plan by name: failure modes, hidden assumptions, evidence gaps. | MUST name ≥1 concrete failure mode. Agreement without a named failure mode = collapse. Structurally mandatory — bias reduction holds regardless of position. |
| 3 | **STEWARD** | Long-term consequences: maintenance burden, operational cost, what breaks in six months, what the plan makes harder later. | MUST name ≥1 cost the Builder ignored. |

Voice output format (deliberately minimal structure — rigid schemas tax
ideation on smaller models; free prose inside one delimiter line):

```
◈ VOICE: BUILDER
<free prose>
```

### ◈ PHASE 4 — HOST SYNTHESIS (Session Model Verdict)

You now synthesize — this phase runs on YOUR model, not a local one, because
the aggregator is the product. Two disciplines:

- **Order-neutral weighing**: you wrote the state yourself, so position bias
  is already structurally contained — but still weigh each voice by constraint
  quality, never by length or order.
- **Build from collisions**, not from averaging agreements.

Write `verdict.md` to the artifact directory:

```
◈ MEDITATE LOCAL: VERDICT

CONVERGENCE:
[1-3 points where voices independently arrived at the same truth]

PRESERVED DISSENT:
[1-3 points of genuine disagreement — do not paper over these]

THE IRREDUCIBLE VERDICT:
[One paragraph. What must be done, in what order, and why. Decree, not suggestion.]

MANDATE CONFLICT CHECK:
[If the verdict contradicts SOVEREIGN_MANDATES.md or any active decree, state
it EXPLICITLY. Surfacing a law-conflict and silently deciding against the law
are different acts. Only the Architect amends law.]

GNOSIS DISTILLED (L3 PRINCIPLE):
[≤2 sentences. No proper nouns. Falsifiable. If it only holds in this
decision's context, label it L2 and move on.]

FALSIFICATION ATTEMPT:
[One genuine attempt to break the L3 above. An L3 that has never survived
an attack is a slogan, not a principle.]
```

Finally write the terminal `state.md` (final rolling state) to the artifact
directory. Post an L3 to Hivemind only if it earned broadcast weight — most
meditations are for the host's cognition, not the fleet's feed.

---

## ⬡ EXECUTION RULES (Non-Negotiable)

1. **ONE PERSONA PER CALL**: Never ask a local model for multiple voices,
   the whole council, or the synthesis. Three calls, three personas, host
   synthesizes. This is the architecture, not a preference.
2. **HOST OWNS ALL STRUCTURE**: Voices emit free prose. Only the host edits
   the state object, writes artifacts, and renders the verdict format.
3. **UPDATE, DON'T RE-SUMMARIZE**: State advances by in-place edit, capped
   at ~250 words. A state that grows monotonically is a re-summarization
   failure and will degrade every subsequent voice.
4. **SERIAL ONLY**: `max_concurrent: 1` is physical law on Tier 0. Parallel
   summons queue, thrash, or OOM. One voice at a time.
5. **ROLE COLLAPSE TERMINATES**: If the Skeptic agrees without a named
   failure mode, or the Steward agrees without a named cost, re-summon that
   voice once with the mandate restated. Second collapse → record it in the
   verdict as a known blind spot and proceed honestly.
6. **M23 FAILURE INTEGRITY**: If `oracle_summon_local` fails, hard stop with
   `[TOOL-CHAIN-COLLAPSE]`. Never simulate a voice parametrically — a
   fabricated dissent is worse than no dissent.
7. **CRASH INSURANCE IS INHERENT**: Every voice block is persisted to disk
   the moment it lands. There is no `--durable` flag because durability is
   the default physics of this architecture.
8. **FALSIFIED-L3 DISCIPLINE**: Same strict L3 standard as `/meditate`.
   No unfalsifiable slogans.

---

## ⬡ FLAGS

| Flag | Effect |
|---|---|
| `--standard` | Default lane: voices on `lmstudio/qwen3-4b-thinking` |
| `--fast` | Velocity lane: voices on `lmstudio/qwen3-1.7b`; tighten voice prose to ~80 words |

---

## ⬡ USAGE EXAMPLES

```bash
# Standard dialectic on an architectural decision
/meditate-local Should we migrate from Qdrant to sqlite-vec now?

# Fast lane — quick structured pushback on a plan
/meditate-local Provider failover ordering --fast

# Adversarial check on a soul-system claim
/meditate-local Is the soul-write path race-free?
```

---

## ⬡ RELATIONSHIP TO THE COUNCIL ARCHITECTURE

| Command | Mechanism | Depth | Cost |
|---|---|---|---|
| `/council-fast` | All-local speed-tier council dispatch | Shallow, broad | Minimal |
| `/meditate-local` (this) | Fixed trio + rolling state + host synthesis | Structured dialectic | N × small inference |
| `/meditate` | Single-inference multi-persona prism (cloud substrate ONLY) | Deepest | 1 × frontier inference |
| `/council-local` | Full pantheon, engine-routed local dispatch | Broadest local | N × local inference |

Use this when you want genuine dialectical tension (not averaged output) but
must stay local. Use `/meditate` when the session model is frontier-class and
depth matters more than substrate.

---

## Research Basis (design constraints, 2024–2026)

- Solo Performance Prompting synergy is absent below frontier class — strong
  instruction-following is a prerequisite (aclanthology.org/2024.naacl-long.15)
- Meta-prompting: hierarchy + verification beats flat ensembles +15.2%
  (arxiv.org/abs/2401.12954); panel sweet spot 3–5, extra weak voices add
  correlated noise (arxiv.org/pdf/2502.00674)
- Aggregator dominance ~2:1 over panel quality; debate order insignificant,
  initial divergence significant (arxiv.org/html/2511.07784v1, arxiv.org/abs/2406.04692)
- Position bias in LLM judges — order-neutral weighing (mbrenndoerfer.com/writing/position-bias-in-llm-judges)
- Small-model degradation: instruction retention breaks first; persona
  persistence decays worst in goal-oriented tasks; self-conditioning on prior
  errors compounds — stale-history removal is the mitigation (arxiv.org/html/2509.09677v2, arxiv.org/html/2512.12775v1)
- Unstructured reasoning beats rigid schemas up to +18.9% on smaller models
  (arxiv.org/abs/2507.03347)
- Small models need different agent architectures, not truncated large-model
  ones; pre-compiled rosters over dynamic selection (arxiv.org/pdf/2506.02153)
- One-subtask-per-call against a rolling compressed shared state; update the
  summary rather than re-summarizing (arxiv.org/pdf/2402.03620)
- Devil's Advocate reduces bias regardless of position (arxiv.org/abs/2405.09935)

---

*⬡ OMEGA ⬡ KALI ⬡ Meditate-Local-v1.0.0 ⬡ oracle_summon_local ⬡ trc_meditate_local ⬡ 2026-08-25*
