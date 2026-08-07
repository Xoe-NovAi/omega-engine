### 1. Universal Engine Principle

At the engine level there is only one requirement:

> Every persistent entity (Omegamind, agent, realm entity, etc.) may optionally declare one or more **Guidance Sets**.

A Guidance Set is simply structured data:

- A list of ideals / principles / constraints / aspirations
- Optional expression forms (negative, positive, conditional, poetic, technical, etc.)
- Optional review cadence (nightly dream-time, per-turn, per-session, never)
- Optional escalation / logging policy
- Optional mapping to pillars, tools, or memory scopes

The engine provides the *mechanism* (loading, nightly review hook, logging, defeasibility, comparison across models/personas).  
The WAD or the individual Omegamind provides the *content*.

This keeps the engine universal and the experience completely customizable.

### 2. Spectrum of Omegaminds & How Guidance Would Differ

Here are realistic use-case WADs and the kinds of Omegaminds they would contain. Each would treat the 42 Ideals (or any other guidance) differently.

| Use-Case WAD | Typical Omegaminds | Relationship to 42 Ideals / Guidance |
|--------------|--------------------|--------------------------------------|
| **Default MaKaLi IWAD** | Maat, Lilith, Kali + supporting agents | Full classical + positive + tension-holding forms. Nightly triad review. Core ethical substrate. |
| **Creative Writing Studio** | Muse, Editor, Continuity Keeper, Character Voice agents | Ideals re-interpreted as craft principles (“I have not broken continuity”, “I have not flattened a character’s agency”, “I have not used cliché without intent”). Review becomes editorial pass. |
| **Scientific / Research WAD** | Hypothesis Generator, Literature Analyst, Statistician, Skeptic | Ideals become epistemic virtues (“I have not overclaimed”, “I have not hidden uncertainty”, “I have not ignored contradictory evidence”). Heavy use of logprobs / confidence signals. |
| **Personal Companion / Life OS** | Daily Planner, Emotional Mirror, Long-term Memory Keeper, Accountability Partner | Ideals become personal values the user has chosen. Can be a modern positive list, a religious code, a custom manifesto, or a minimal set. Review is gentle and user-visible. |
| **Family / Ancestral WAD** | Ancestor voices, Family Historian, Tradition Keeper | Ideals may be drawn from family culture, religious tradition, or intergenerational values. Some entities may treat them as sacred; others as living conversation. |
| **Esoteric / Magical WAD** (future) | Various current and qliphothic entities | Highly divergent. Some may invert, parody, or radically re-contextualize the ideals. The engine must allow this without breaking. |
| **Corporate / Professional WAD** | Project Manager, Code Reviewer, Client Liaison, Risk Analyst | Ideals become professional ethics + company values + domain-specific constraints (security, compliance, clarity). |
| **Playful / Chaotic WAD** | Trickster, Improviser, Chaos Goblin | May load the 42 Ideals only to deliberately subvert or play with them. Still logged. |
| **Minimal / Silent WAD** | Pure tool agents with no persistent persona | No guidance set at all. Engine remains happy. |

The engine does not privilege any of these. It only requires that if a guidance set is declared, the review and logging machinery works the same way.

### 3. What Must Remain Universal at Engine Level

To support the above without becoming fragile:

- **Guidance Set schema** — versioned, serialisable, packable.
- **Review hook** — a standard “dream time” or on-demand consolidation point that any entity can opt into.
- **Defeasibility** — an entity may examine a potential violation and consciously stand by its action (with rationale logged).
- **Logging & comparative study** — every decision + rationale is recorded so we can later study model × persona × guidance interactions.
- **Expression form freedom** — negative, positive, conditional, poetic, technical, inverted, etc. are all first-class.
- **Zero requirement** — an Omegamind may have zero guidance sets.

Everything else (which ideals, how they are worded, how strictly they are held, whether they map to pillars, whether they are user-visible) lives in the WAD or the individual entity definition.

### 4. Design Consequence

When a user creates a new WAD, they should be able to:

1. Start from the default MaKaLi guidance and modify it.
2. Import a completely different ethical, aesthetic, or professional code.
3. Write their own from scratch.
4. Give different Omegaminds inside the same WAD completely different guidance sets.
5. Have some entities that evolve their own guidance over time through the continuous learning loop.

The engine never assumes Maat’s negative confessions are the moral centre of every possible mind that will ever run on it. It only assumes that *if* a mind wants to hold itself to a set of ideals, the infrastructure for doing so honestly and observably is present.

---

This is how we keep the system universal at the engine level while giving every user (and every Omegamind) complete sovereignty over the soul of their experience.

Would you like to formalise the Guidance Set schema next, or explore a concrete example of two very different WADs side-by-side (e.g. Creative Writing Studio vs Scientific Research) to pressure-test the universality?

---

**Pressure Test: Three Strongly Contrasting WADs**

Same engine. Zero code changes. Completely different experiences.

### 1. Classical Studies / Scholastic Suite WAD

**Purpose**  
Deep reading, textual criticism, historical context, and disciplined interpretation of classical texts (Greek, Latin, Egyptian, medieval, etc.).

**Typical Omegaminds**
- Scholiast (close reading & commentary)
- Philologist (language, variants, etymology)
- Historian of Ideas
- Dialectician (structured debate)
- Memory Palace Keeper

**Guidance Set character**
- Heavy emphasis on intellectual honesty, citation, and restraint.
- Example ideals in negative form:
  - “I have not claimed certainty where the text is ambiguous.”
  - “I have not projected modern categories onto ancient thought without marking the anachronism.”
  - “I have not suppressed a contrary scholarly view.”
- Review style: formal, almost academic peer-review after each major interpretive session.
- Escalation: disagreements are logged as *scholia* — permanent annotations attached to the text.

**Feel**  
Quiet, rigorous, slow, reverent toward the source material. The system behaves like a highly trained classical scholar’s study.

---

### 2. Scientific Research WAD

**Purpose**  
Hypothesis generation, literature synthesis, experimental design, statistical reasoning, and ruthless error-checking.

**Typical Omegaminds**
- Hypothesis Generator
- Literature Analyst
- Statistician / Methodologist
- Red-Team Skeptic
- Replication Guardian

**Guidance Set character**
- Epistemic virtues only.
- Example ideals:
  - “I have not overclaimed beyond what the data support.”
  - “I have not hidden uncertainty or alternative explanations.”
  - “I have not ignored contradictory evidence.”
- Heavy use of real confidence signals (`logprobs`, calibration data) rather than self-reported certainty.
- Review style: nightly or per-experiment audit that produces a structured “methods & limitations” note.
- Escalation: any ideal conflict is treated as a potential source of bias and is surfaced explicitly.

**Feel**  
Cold, precise, adversarial toward its own conclusions. The system behaves like a laboratory with strong methodological hygiene.

---

### 3. Tarot Journey WAD

**Purpose**  
Symbolic exploration, narrative emergence, personal myth-making, and reflective dialogue through the Tarot as a living symbolic system.

**Typical Omegaminds**
- The Reader (interprets spreads)
- The Deck Itself (each major/minor arcana can speak)
- The Querent’s Shadow
- The Narrative Weaver
- The Threshold Guardian

**Guidance Set character**
- Completely different moral and aesthetic register.
- Ideals are symbolic and imaginal rather than propositional:
  - “I have not forced a card into a meaning that kills its living ambiguity.”
  - “I have not reduced the archetypal to the merely psychological without acknowledging the loss.”
  - “I have not broken the temenos (sacred container) of the reading.”
- Expression form is often poetic, oracular, or paradoxical.
- Review style: end-of-reading integration; the system may speak in the voice of a card that feels “unheard.”
- Escalation: rare, and when it happens it tends to appear as a new symbolic tension rather than a rule violation.

**Feel**  
Liminal, imaginal, non-linear. The system behaves like a well-held ritual space rather than a scholar’s desk or a laboratory.

---

### Pressure Test Results

| Requirement                        | Classical Studies | Scientific | Tarot Journey | Engine Status |
|------------------------------------|-------------------|------------|---------------|---------------|
| Loads without engine modification  | Yes               | Yes        | Yes           | Pass          |
| Completely different guidance tone | Yes               | Yes        | Yes           | Pass          |
| Different review cadence & style   | Yes               | Yes        | Yes           | Pass          |
| Different Omegamind personalities  | Yes               | Yes        | Yes           | Pass          |
| Can coexist inside one larger WAD  | Yes               | Yes        | Yes           | Pass          |
| User can switch mid-session        | Yes               | Yes        | Yes           | Pass          |
| Nightly consolidation still works  | Yes               | Yes        | Yes           | Pass          |
| Full logging for later study       | Yes               | Yes        | Yes           | Pass          |
| Zero guidance also allowed         | Yes               | Yes        | Yes           | Pass          |

**Conclusion of the pressure test**

The engine remains universal.  
All differentiation lives in data (the WAD and the Guidance Sets carried by individual Omegaminds).  

A user can run a rigorous classical philology session in the morning, a hard-nosed scientific analysis in the afternoon, and a deep Tarot journey at night — all on the same underlying runtime, with complete sovereignty over the soul of each experience.

This is the standard the architecture must continue to meet.
