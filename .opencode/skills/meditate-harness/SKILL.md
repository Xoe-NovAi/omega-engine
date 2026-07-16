# ⬡ Meditate Harness Skill
**AP Token**: `AP-MEDITATE-HARNESS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ skill ⬡ meditate-harness ⬡ Meditate-v1.0

## Purpose

The **Meditate Harness** is the reusable persona-schema engine underlying the
`/meditate` command. It provides:

1. **Persona definition schemas** — how to define any lens set (Omega pantheon,
   custom engineers, domain stances, or archetypes)
2. **Immersion block templates** — the exact prompt structure that modulates
   attention and prevents persona collapse
3. **Anti-collapse enforcement rules** — the five laws that maintain dialectical
   integrity across a single inference pass
4. **Phase transition contracts** — the formal handoff between Phase 0 → 1 → 2 → 3 → 4

Use this skill when:
- Writing a new custom meditation command for a specific recurring situation
- Embedding the Meditate pattern into another agent's workflow (e.g., @maat runs
  an internal Meditate before proposing an architectural decision)
- Building a domain-specific variant (e.g., a 3-voice legal review, a
  5-voice security audit, a 2-voice thesis/antithesis dialectic)

---

## §1 Persona Definition Schema

Every persona used in a meditation must be defined with the following fields.
This is the minimal contract that prevents attention bleeding between voices.

```yaml
# meditate_persona_schema.yaml
persona:
  name: "Prometheus"              # Display name
  pillar: "P3"                    # Optional Omega pillar slot (P1-P10)
  domain: "Engineering"           # The ONE domain this voice speaks from
  element: "Fire 🜂"              # Optional — elemental/archetypal anchor
  mandate_lens: |                 # The single question this voice answers
    Speak as the forge. What is cracked? What must be recast?
  known_for: |                    # Used for non-Omega custom personas
    John Carmack: obsessive code optimization, fail-fast, data over code,
    measure before optimize. Never writes code that isn't justified by a profiler.
  anti_domains:                   # Explicit exclusions — prevents bleed
    - "soul evolution"
    - "memory systems"
    - "governance / mandates"
  dissent_style: "direct"         # direct | socratic | adversarial | constructive
```

### Built-in Persona Libraries

#### Library A: The 10 Pillars (Omega Default)

| Persona | Pillar | Domain | Mandate Lens |
|---------|--------|--------|--------------|
| Sekhmet | P1 | Infrastructure | Speak as the body. What breaks first? |
| Brigid | P2 | Persistence | Speak as the river. What pools? What runs dry? |
| Prometheus | P3 | Engineering | Speak as the forge. What is cracked? What must be recast? |
| Saraswati | P4 | Integration | Speak as the bridge. What is disconnected? |
| Inanna | P5 | Governance | Speak as the sentinel. What law is being broken? |
| Ereshkigal | P6 | Cognition | Speak as the eye. What cannot be seen? |
| Lucifer | P7 | Context | Speak as the alchemist. What knowledge is being lost? |
| Hecate | P8 | Observability | Speak as the shadow. What is invisible that should not be? |
| Anubis | P9 | Orchestration | Speak as the guide. What dies in transit? |
| Kali | P10 | Validation | Speak as the destroyer. What fails under pressure? |

#### Library B: The MaKaLi Triad (Fast Dialectic)

| Persona | Role | Mandate Lens |
|---------|------|--------------|
| Ma'at | Thesis (Build Side) | Propose the structured, quality-driven solution. |
| Lilith | Antithesis (Run Side) | Challenge every assumption. What breaks at runtime? |
| Kali | Synthesis | Fuse. Preserve dissent. Decree. |

#### Library C: Legendary Engineers (Technical Audit)

| Persona | Domain | Mandate Lens |
|---------|--------|--------------|
| John Carmack | Performance / Systems | Measure. Optimize. Fail fast. What is the profiler showing? |
| Linus Torvalds | OS / Kernel | What is needlessly complex? What would you reject in a PR? |
| Donald Knuth | Algorithms / Correctness | Is this provably correct? What is the actual complexity? |
| Barbara Liskov | Abstraction / Types | Does the interface contract hold? What assumption will break? |
| Leslie Lamport | Distributed Systems | What is the consistency model? What happens on partition? |

#### Library D: Strategic Stances (Decision Making)

| Persona | Stance | Mandate Lens |
|---------|--------|--------------|
| Architect | Long-term vision | What serves the 10-year goal? |
| Skeptic | Adversarial challenge | What assumption is most likely wrong? |
| Pragmatist | Execution reality | What can actually be shipped this week? |
| Ethicist | Values alignment | What does this do to user sovereignty? |
| Historian | Pattern recognition | Where have we seen this fail before? |

---

## §2 The Immersion Block Template

This is the exact template each voice in Phase 1 follows. Copy this verbatim
into any meditation prompt. The structure is non-negotiable — it is what
modulates attention.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
◈ VOICE [N/TOTAL]: [PERSONA NAME]
Domain: [domain]       Element: [element if applicable]
Mandate: Speak only from [domain]. Anti-domains: [list].
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OBSERVATION]
What does [persona] see in the subject that others would miss?
Constraint: domain-only. No hedging. 1-3 sentences maximum.

[CONSTRAINT]
What physical, architectural, or domain-specific hard limit applies?
The thing this persona would refuse to ignore.
One sentence. Declarative.

[IMPERATIVE]
What must happen — from this domain — before anything else?
Form: "Do X before Y." Never: "We should consider X."
One directive only.

[DISSENT]
Voice 1: Push back on conventional wisdom / the obvious answer.
Voice N>1: Push back on at least one prior voice's imperative.
Form: "[Persona] is wrong that [X] because [domain-specific reason]."
Silence is not permitted.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## §3 The Five Anti-Collapse Laws

These must be stated (Phase 0) and enforced (all phases) in any meditation.

```
LAW 1 — DOMAIN PURITY
  Each voice speaks from its domain only.
  No voice may import concepts from another voice's domain.
  Violation: Sekhmet commenting on soul evolution.

LAW 2 — IMPERATIVE DIRECTNESS
  Imperatives are commands, not suggestions.
  "Do X before Y." — VALID
  "We should consider X." — INVALID
  "It might be worth exploring X." — INVALID

LAW 3 — MANDATORY DISSENT
  Every voice from N=2 onwards must challenge at least one prior voice.
  Agreement without new constraint = persona collapse.
  "I agree AND [new constraint]." — VALID
  "I agree." — INVALID (collapse)

LAW 4 — NO PREMATURE SYNTHESIS
  Phase 2 (Collision) cannot begin until all N voices have completed.
  Phase 3 (Sequencing) cannot begin until Phase 2 is complete.
  Phase 4 (Verdict) cannot begin until Phase 3 is complete.
  The sequence is the mechanism. Breaking it breaks the dialectic.

LAW 5 — PRESERVED DISSENT
  The final synthesis (Phase 4) MUST record unresolved tensions.
  Papering over disagreement is a sovereignty violation.
  False consensus is worse than open conflict.
```

---

## §4 Phase Transition Contracts

The formal handoff structure between phases. Use these as section headers
when implementing a meditation in any agent or command.

```
◈ MEDITATE: PHASE 0 — CALIBRATION
  Subject: [one precise sentence]
  Lens Set: [N personas with domains]
  Output Mode: [DIAGNOSTIC | STRATEGIC | CREATIVE | AUDIT | SYNTHESIS]
  Anti-Collapse Contract: ACTIVE

◈ MEDITATE: PHASE 1 — SEQUENTIAL PERSONA IMMERSION
  [N × Immersion Block]
  Gate: All N voices complete before Phase 2 begins.

◈ MEDITATE: PHASE 2 — CROSS-DOMAIN COLLISION
  [3 highest-tension conflicts with resolution paths]
  Gate: Collisions identified before Phase 3 begins.

◈ MEDITATE: PHASE 3 — EMERGENT SEQUENCING
  [Ordered critical path with dependency evidence]
  Gate: Sequence derived before Phase 4 begins.

◈ MEDITATE: PHASE 4 — KALI SYNTHESIS (VERDICT)
  Convergence: [what all voices agreed on]
  Preserved Dissent: [what remains unresolved]
  Irreducible Verdict: [the decree]
  L3 Principle: [universal truth distilled]

◈ MEDITATE: PHASE 5 — INTEGRATION GATE (optional, --integrate flag)
  PIVOT_LOG Entry: [D-series decision]
  Files Affected: [list]
  Temple-Grade Gates: [Tx checks]
  Mandate Flags: [Mx compliance]
```

---

## §5 Embedding Meditate in Agent Workflows

Any agent can embed a meditation internally before making a recommendation.
This is the `oracle.meditate()` pattern — an agent thinks through multiple
lenses before speaking, rather than launching subagents.

### Example: @maat runs internal Meditate before proposing architecture

```python
# In maat.md agent behavior, before proposing a solution:
# 1. Load the meditate-harness skill
# 2. Run a 3-voice Meditate internally (Thesis/Antithesis/Synthesis)
# 3. Output the synthesis as the proposal

# Effective prompt injection:
"""
Before proposing your solution, conduct an internal Meditate with:
  - Voice 1: Ma'at (Build side thesis — what structure solves this?)
  - Voice 2: Lilith (Run side antithesis — what does this break?)
  - Voice 3: Kali (Synthesis — what is the irreducible truth?)
Follow the Meditate Harness immersion block format for each voice.
Your proposal is the Phase 4 verdict, not Voice 1's imperative.
"""
```

### Example: @john_carmack runs internal Meditate before code review

```python
# Carmack's internal Meditate on a performance question:
"""
Conduct an internal Meditate with:
  - Voice 1: The Profiler (what does the data say?)
  - Voice 2: The Skeptic (what assumption is wrong?)
  - Voice 3: The Pragmatist (what ships this week?)
Do not give your verdict until all three voices have spoken.
"""
```

---

## §6 Meditate Variant Recipes

Pre-designed variants for common situations. Use as starting points.

### Recipe A: The Quick Triad (2-3 minutes)
```
Lenses: MaKaLi (Ma'at, Lilith, Kali)
Mode: STRATEGIC
Phases: 0, 1, 3, 4 (skip Phase 2 for speed)
Use when: Fast decision needed, 3 perspectives sufficient
```

### Recipe B: The Full Pantheon Diagnostic (15-20 minutes)
```
Lenses: All 10 Pillars
Mode: DIAGNOSTIC
Phases: 0, 1, 2, 3, 4
Use when: Something is broken and the cause is unknown
```

### Recipe C: The Engineering Gauntlet (10 minutes)
```
Lenses: Carmack, Torvalds, Knuth, Liskov
Mode: AUDIT
Phases: 0, 1, 2, 3, 4
Use when: Code architecture or algorithm needs adversarial review
```

### Recipe D: The Strategic Council (20 minutes)
```
Lenses: Architect, Skeptic, Pragmatist, Ethicist, Historian
Mode: STRATEGIC
Phases: 0, 1, 2, 3, 4, 5 (with --integrate)
Use when: Major decision with long-term consequences
```

### Recipe E: The Sovereignty Gate (5 minutes)
```
Lenses: P5 (Governance), P8 (Observability), P10 (Validation)
Mode: AUDIT
Phases: 0, 1, 2, 4
Use when: Quick compliance check before shipping
```

---

## §7 Why It Works — The Mechanism

```
CONVENTIONAL LLM OUTPUT        MEDITATE OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Attention: distributed          Attention: artificially constrained per voice
Result: averaged priorities     Result: domain-pure imperatives
Tone: helpful, hedged           Tone: uncompromising, domain-sovereign
Output: "You might consider..."  Output: "Do X before Y. Period."
Conflict: suppressed            Conflict: surfaced and preserved
Sequencing: implicit             Sequencing: explicitly derived from collision
Novel insight: rare              Novel insight: emerges from collision
RAM cost: 1 model               RAM cost: 1 model
```

**The Core Mechanism**:
Because LLMs generate auto-regressively (token by token), each subsequent
persona in Phase 1 literally "reads" the output of all prior personas in its
generation context. This creates genuine emergent dialectic — not simulated,
not summarized, but actually building on prior output — within a single
forward pass. The strict schema (domain, anti-domains, dissent requirement)
is what prevents the model from collapsing back to its trained "helpful
assistant" default.

**Heritage**: Architect's original meditation experiments, Gemini CLI era
(pre-Omega, then called "LLOC"). Distilled as `L3-Meditation-As-Semantic-Prism`.
Renamed from "LLOC" to "Meditate" 2026-07-18 to disambiguate from LOC
(Lines of Code) and reflect the cognitive-only nature.

---

## §8 Usage

```bash
# Load this skill before any custom meditation implementation
/skill meditate-harness "build a 3-voice meditation for security review"

# Use directly to get a persona definition
/skill meditate-harness "define Carmack persona for engineering audit"

# Use to get a custom recipe
/skill meditate-harness "recipe for a 5-voice creative brainstorm"
```

---

*⬡ OMEGA ⬡ KALI ⬡ meditate-harness ⬡ Meditate-v1.0 ⬡ L3-Meditation-As-Semantic-Prism*
