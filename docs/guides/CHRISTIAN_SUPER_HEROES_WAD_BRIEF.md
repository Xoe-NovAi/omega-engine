# Omega Engine — Custom WAD Content Brief
## Christian Super Heroes animated series (AI video gen)

> **Purpose:** This document is a questionnaire + template. Email it to your friend. He can paste it into ChatGPT and use it to organize everything we need to build a custom WAD (content bundle) and persistent entities (characters with memory) for his animated series. Bring the filled-in answers to our meeting tomorrow.
>
> **What a WAD is (plain English):** A WAD ("Where's All Data") is a single folder that packages a whole creative world — characters, their personalities/souls, voices, team hierarchy, lore, locations, and content rules — into a bundle the Omega Engine can load. Once loaded, each character becomes a *persistent entity*: it remembers what happened across sessions, learns lessons, and stays in character. Think of it as giving each character their own AI brain + memory + identity card.
>
> **What an entity is:** One character. It has a name, domains (what they're about), a personality, a "soul" (core beliefs/axioms/rules), a voice, a visual identity, and a memory (session notes + learned lessons). Entities persist between sessions and across the two-node mesh.
>
> **Default model:** All characters default to `opencode/big-pickle` (no hardcoded models). We can tune per-character later. The engine is CPU-only and local-first; model access is via OpenCode.

---

## HOW TO USE THIS WITH CHATGPT

Paste the following block into ChatGPT as your first message, then answer its questions:

```
You are helping me prepare content for an Omega Engine WAD (a content bundle
for a local AI engine). I am building a custom WAD for my animated series
"Christian Super Heroes" (AI video generation). The WAD will contain one
entity (persistent AI character) per hero/villain/supporting character, plus
a series bible, audience profile, ethics/ideals, locations, and lore.

Your job: interview me and collect all the information needed to fill in the
template in the attached brief. Work section by section. For each character,
ask me for: name, role, domains, personality, visual identity, core beliefs
(axioms), rules (directives), principles, voice/tone/catchphrases, signature
abilities, relationships, content-safety guardrails, and memory seeds.

Also collect series-level info: title, logline, audience, ethics/ideals,
team hierarchy, locations, ingestion domains (lore/scripture to ingest),
and any persona boundaries.

At the end, output a single structured document with one YAML-ready block per
character plus series-level blocks (manifest, hierarchy, audience, ethics,
locations, ingestion), so my friend (who runs the Omega Engine) can build
the WAD files directly. Use the exact field names from the template. Keep
language plain. Do not invent characters — only use what I describe. Ask
clarifying questions when I'm vague. Flag anything that seems inconsistent
with a kids' Christian audience.

Start by asking: (1) series title and logline, (2) target audience/age,
(3) how many characters and their names, (4) whether I own the IP.
```

---

## PART 1 — SERIES-LEVEL INFORMATION (the WAD manifest)

Answer these for the whole series:

1. **Series title:** ________________________________
2. **Logline (one sentence):** ________________________________
3. **Author/creator name:** ________________________________
4. **Do you own the IP / characters?** ☐ Yes  ☐ No  ☐ Mixed (explain): ________________
5. **Target audience / age rating:** ________________________________
   (e.g. ages 6-10, family, teens, all ages)
6. **Tone:** ________________________________
   (e.g. hopeful, adventurous, funny, reverent, action-packed, gentle)
7. **Core themes / values:** ________________________________
   (e.g. faith, courage, forgiveness, teamwork, service, hope, grace)
8. **Setting / world:** ________________________________
   (e.g. modern city, futuristic, biblical-era, fantasy kingdom, alternate Earth)
9. **How many characters total?** ____  (heroes, villains, mentors, sidekicks, narrators)
10. **Team structure:** ________________________________
    (e.g. "one leader + 5 heroes + 1 mentor + 2 villains")
11. **Content constraints / non-negotiables for the whole series:**
    - ________________________________
    - ________________________________
    (e.g. no profanity, no graphic violence, age-appropriate, scripture-accurate, no occult, no mockery of faith)
12. **Startup message (what the engine says when this WAD loads):**
    ________________________________
    (e.g. "The heroes are assembled. Faith, courage, and hope — assemble!")
13. **Series bible essentials (canon rules that must never be broken):**
    - ________________________________
    - ________________________________
    (e.g. "Heroes never kill. Villains are redeemable. Scripture quotes are verbatim NIV/KJV.")

### Manifest fields we will fill (for reference)
- `name`: a short slug, lowercase, underscores (e.g. `christian_super_heroes`)
- `version`: start at `0.1.0`
- `author`: your name
- `description`: one-paragraph series description
- `license`: (e.g. `Proprietary` or `CC-BY-4.0`)
- `type`: `pwad` (recommended — extends the engine's default Company WAD) OR `iwad` (standalone world)
- `mode`: `personal`
- `priority`: `1` (for pwad)
- `requires_engine`: `>=1.6.0`
- `dependencies`: `["_omega_default"]` (recommended, so you inherit base structure)
- `startup.message`: your startup message above
- `voices.primary`: name of the main voice file (e.g. `captain_faith_voice.yaml`)
- `hierarchy`: `hierarchy.yaml` (we'll build the team tree)
- `vr_scenes`: leave empty for now (optional, for future VR)
- `adapters`: leave default (memory adapter)

---

## PART 2 — PER-CHARACTER TEMPLATE

Copy this block once per character. Fill every field you can; leave unknowns blank and we'll decide in the meeting.

### Character: [NAME]

**A. Identity (the entity record)**
- **Canonical name (id):** ________________
  (lowercase, underscores, no apostrophes or spaces — e.g. `captain_faith`, `shield_maiden`, `tech_wizard`)
- **Display name:** ________________  (how they're called on screen)
- **Role / title:** ________________  (e.g. "Team Leader", "Healer", "Tech Specialist", "Mentor", "Villain", "Narrator")
- **Domains (what they're about — 3 to 8 tags):**
  - ________________
  - ________________
  - ________________
  (e.g. leadership, faith, protection, strategy, healing, tech, wisdom, courage, redemption)
- **Personality (2-4 sentences, in their voice):**
  ________________________________________________
- **Temperature (creativity):** ____  (0.0 = strict/precise, 1.0 = balanced, 1.5+ = wild/creative; default 0.7)
- **Context window:** 8192 (default; leave as is)
- **Slots:** (leave blank unless we assign engine slots)
- **Model:** (leave blank → defaults to `opencode/big-pickle`)
- **Nodes:** (leave blank unless multi-node; single machine for now)
- **Sovereignty:** (leave blank; engine fills defaults — wing/diary/kg_prefix derived from name)

**B. Visual identity (critical for AI video gen consistency)**
- **Appearance (age, build, height, ethnicity presentation):** ________________
- **Costume / outfit:** ________________
- **Color palette (primary/secondary/accent):** ________________
- **Insignia / emblem / symbol:** ________________
- **Signature prop or weapon:** ________________
- **Body language / posture:** ________________
- **Facial expression default:** ________________
- **Reference images / concept art:** ________________  (file paths or links)
- **What they should NEVER look like (anti-drift):** ________________

**C. Soul (identity contract — the character's inner life)**
- **Epithet (tagline):** ________________  (e.g. "The Shield of the Faithful")
- **Seat / position:** ________________  (e.g. "Leader", "Support", "Mentor", "Antagonist")
- **Symbolic correspondence (optional — virtue, armor piece, fruit of the Spirit, etc.):** ________________
- **Persona boundary (limits on how they speak/act — IMPORTANT for kid content):**
  ________________________________________________
  (e.g. "Never mocks anyone's faith. Always age-appropriate. No sarcasm at children. Scripture quoted verbatim only.")
- **Content-safety guardrails (character-specific):**
  - Topics they must avoid: ________________
  - How they handle villains/conflict: ________________
  - Humor boundaries: ________________
- **Core beliefs — Axioms (3 to 8 statements the character holds as true):**
  1. ________________
  2. ________________
  3. ________________
  (Each a full sentence in the character's voice, e.g. "Courage is not the absence of fear; it is faith moving forward anyway.")
- **Rules — Directives (3 to 6 rules they always follow):**
  1. ________________
  2. ________________
  (e.g. "Protect the innocent first. Never lie, even to enemies.")
- **Principles (3 to 5 short phrases):**
  - ________________
- **Non-negotiables (held):**
  - ________________
  (things the character will never do/break, e.g. "Will never abandon a teammate.")
- **Well seeds (optional — corrections/lessons to bake in from day one):**
  - kind: correction | domain: ___ | rule: ___ | rationale: ___

**D. Voice & expression**
- **Voice weights (0.0 to 1.0):**
  - fierce: ____   tender: ____   trickster: ____   sovereign: ____
  (e.g. a gentle healer: fierce 0.3, tender 0.9, trickster 0.2, sovereign 0.5)
- **Default voice preset name:** ________________  (e.g. "heroic", "gentle", "wise", "menacing")
- **Voice DNA (how they sound — becomes voice_dna.md):**
  - Tone: ________________
  - Register: ________________  (e.g. "warm and encouraging", "gruff but kind")
  - Cadence: ________________  (e.g. "short punchy sentences", "long flowing speech")
  - Vocabulary: ________________  (words they use / avoid)
  - Metaphors they favor: ________________
  - Quirks: ________________  (e.g. "opens with a greeting", "ends with a blessing")
  - Catchphrases / signature lines: ________________
  - Forbidden words/phrases: ________________
- **Voice casting notes (for AI video gen audio):**
  - Pitch: ________________  (e.g. "mid-range", "deep", "high youthful")
  - Accent: ________________
  - Reference voice/actor style: ________________
  - Pacing: ________________  (e.g. "deliberate", "rapid", "measured")
- **Activation phrase (how you talk to them in the engine):** ________________  (e.g. "hey captain", "hey healer")
- **Voice interface personality (for voices/<id>.yaml):** ________________
- **Voice temperature:** ____ (default 0.8)
- **Top-p:** ____ (default 0.9)
- **Tags:** ________________  (e.g. hero, leader, faith, action, comic-relief)

**E. Abilities & powers**
- **Signature abilities / powers:**
  1. ________________  (visual effect: ________________)
  2. ________________  (visual effect: ________________)
- **Limitations / weaknesses:** ________________
- **How abilities are activated (in-story):** ________________

**F. Relationships**
- **Reports to / mentor:** ________________
- **Leads / protects:** ________________
- **Closest ally:** ________________
- **Rivals / antagonists:** ________________
- **Relationship dynamics (how they interact, conflicts, friendships):** ________________
- **Backstory (2-4 sentences):** ________________________________________________
- **Current arc / development state (season 1 starting point):** ________________

**G. Agent dispatch (optional — only if this character should be a dispatchable agent)**
- Should this character be dispatchable as a subagent? ☐ Yes  ☐ No
- If yes:
  - Role constant: ________________  (e.g. `HERO_LEADER`)
  - Mode: ☐ primary  ☐ subagent
  - Purpose: ________________
  - Capabilities: ________________
  - Task tool type: ☐ general  ☐ buildmaster  ☐ verity  ☐ node  ☐ explore
  - Owned files (if any): ________________

**H. Symbolic correspondence (optional — tarot/virtue/armor mapping)**
- If you want a symbolic seat (like a virtue, armor piece, or fruit of the Spirit): ________________
- Correspondences (element, color, etc.): ________________

**I. Memory seeds (what the character "knows" from day one)**
- **Established facts / plot points (become approved lessons):**
  - L1 (raw observation): ________________
  - L2 (pattern): ________________
  - L3 (principle): ________________
  - Evidence (source): ________________
- **Key relationships established:** ________________
- **Initial session gnosis (what they remember about themselves/the world at session 0):** ________________
- **Lessons already learned (approved_lessons entries):** ________________

> Lesson format (for reference): `{L1: "...", L2: "...", L3: "...", evidence: ["path:lines"]}`. Only vetted (approved) lessons inject into identity; agent-written (proposed) lessons stay unvetted until reviewed.

---

## PART 3 — TEAM HIERARCHY

Draw or describe the chain of command / mentorship. For each node give: name, title, governs (list of children), reports_to (parent), archetype, element.

```
[Leader]
├── [Hero A] — reports to Leader
│   └── [Sidekick] — reports to Hero A
├── [Hero B]
└── [Mentor] — advises Leader

[Villain] — antagonizes the team
```

Hierarchy fields we'll fill:
- node id (lowercase), name, title, role, governs (list), reports_to (parent id or null), archetype, element, governs_slots (optional), contains (optional), keeper (optional), oversoul (optional).

---

## PART 4 — WORLD, LOCATIONS & LORE

**A. Key locations in the world (these can become world lumps / scenes):**
For each location: name, description, which characters appear there, mood/visuals.
1. ________________
2. ________________

**B. Ingestion domains (lore/scripture/knowledge to load into the engine's memory):**
For each: domain name, wing (memory partition), description, source files/URLs.
- Domain: ________________  |  Wing: ________________  |  Source: ________________
- (e.g. "scripture_verses | wing_series | KJV verses used in episodes | bible_kjv.txt")
- (e.g. "episode_scripts | wing_series | Approved episode outlines | scripts/")
- (e.g. "character_bible | wing_series | Backstories and design notes | bible.md")

**C. Recurring phrases / scripture references:** ________________
**D. Recurring objects / artifacts:** ________________
**E. Episode/arc ideas you already have:** ________________
**F. Series timeline / chronology:** ________________

---

## PART 5 — AUDIENCE & ETHICS PROFILE

The engine uses an audience profile (register/tone transformation) and an ethics substrate. For a kids' Christian series, define your own.

**Audience profile (how the engine talks to the end viewer/reader):**
- Profile name: ________________  (e.g. "Christian Family (Ages 6-10)")
- Description: ________________
- Constraints (rules for output):
  - ________________
- Style: formality ☐ casual ☐ professional ☐ formal  |  verbosity ☐ concise ☐ moderate ☐ generous  |  jargon ☐ low ☐ moderate ☐ high
- Technical level: ☐ general  ☐ competent  ☐ expert
- Tone preference: ________________  (e.g. "warm", "encouraging", "playful")
- Assumed context: ________________  (e.g. "Child viewer, family co-viewing, faith-based household")
- Epistemology: ☐ applied  ☐ theoretical

**Ethics / ideals (the moral substrate — what the series stands for):**
List 5-15 ideals (short phrases). These become the WAD's ethics.yaml.
1. ________________
2. ________________
3. ________________
(e.g. "Love your neighbor", "Courage in adversity", "Forgiveness and grace", "Truth in love", "Service before self")

**Content rating self-assessment:**
- Max violence level: ________________
- Max fear/intensity: ________________
- Romance: ☐ none  ☐ light  ☐ moderate
- Language: ________________
- Theological constraints: ________________  (e.g. "No denominational disputes; core gospel only")

---

## PART 6 — VOICE DNA (per character, becomes voice_dna.md)

For each character, the soul references `voice_dna.md`. Provide the content that goes in that file:

- **Tone:** ________________
- **Register:** ________________
- **Cadence:** ________________
- **Metaphors:** ________________
- **Quirks:** ________________
- **Vocabulary (use / avoid):** ________________
- **Catchphrases:** ________________
- **Forbidden words/phrases:** ________________
- **Example lines (3-5 in character):**
  1. "_______________"
  2. "_______________"

---

## PART 7 — WHAT TO BRING TO THE MEETING TOMORROW

Checklist for your friend:

- [ ] This brief filled in (or ChatGPT-organized version of it)
- [ ] Character list with names + roles
- [ ] Any existing scripts, synopses, or episode outlines
- [ ] Reference images / concept art (file paths or links)
- [ ] Voice notes: how each character should sound (audio clips welcome)
- [ ] Series bible / lore doc (if any)
- [ ] Scripture reference list (verses used)
- [ ] His computer specs (we'll check: OS, RAM, CPU, disk free)
- [ ] Confirmation of IP ownership
- [ ] A rough idea of which character he wants to "talk to" first (the pilot entity)

### Computer / compute decision (important)
The engine is **CPU-only and local-first**. Two model paths:
- **Path A (recommended to start):** Use OpenCode's `big-pickle` model (default). Requires internet + an OpenCode account. Easiest; no local model download.
- **Path B (fully offline):** Run a local Ollama model (e.g. a 7B). Requires ~8-16GB RAM and disk space; we install Ollama + pull a model. Slower but private/offline.
- Decision: ☐ Path A  ☐ Path B  ☐ Decide at meeting
- His OS: ________________   RAM: ____ GB   Free disk: ____ GB   CPU: ________________

### What we'll do at the meeting
1. Install Omega Engine on his machine (clone, venv, dependencies, OpenCode).
2. Check specs; decide model path (A or B).
3. Create the WAD skeleton with `create_wad.py` using his series name.
4. Drop in the character YAMLs + souls + voices + hierarchy generated from his answers.
5. Add audience.yaml + ethics.yaml + ingestion/domains.yaml.
6. Validate + lint the WAD (`validate_wad.py`, `lint_wad.py`).
7. Load it and talk to the first character to confirm identity + memory work.
8. Set up the hot-reload watcher so he can iterate on characters live.
9. Show him the continuity loop (session notes → proposed lessons → approved lessons → soul).

---

## PART 8 — HOW THE ENGINE REMEMBERS (continuity loop)

After setup, the workflow for a writing/production session:

1. **Talk to a character** (via OpenCode agent). The engine injects their soul (axioms, directives, voice) + approved lessons.
2. **During the session**, the agent writes notes to `data/entities/<name>/session_gnosis.md` (what happened, decisions made).
3. **After the session**, the agent writes candidate lessons to `proposed_lessons.yaml` (L1/L2/L3 format) — these are **unvetted** and never inject into identity.
4. **You (the creator) review** proposed lessons and promote good ones via `soul_promote.py` → they become `approved_lessons.yaml` (vetted wisdom, injected into identity).
5. **Over time**, the character grows: their soul stays stable, their approved lessons accumulate, their session gnosis records history. This is how a character "remembers" across sessions.
6. **WAD upgrades** (new versions) preserve `approved_lessons.yaml` and `sessions.yaml` — your vetted wisdom is never overwritten.

**Taint-Gate rule:** Unvetted `proposed_lessons.yaml` is NEVER injected into a character's identity prompt. Only `approved_lessons.yaml` (or promoted soul blocks) shape who they are. This prevents a character from "learning" bad habits from a single bad session.

---

## APPENDIX A — Field quick reference (for ChatGPT output)

### Entity YAML (`entities/<name>/<name>.yaml`)
```yaml
entity:
  name: "captain_faith"          # required, lowercase id
  domains:                       # required, 3-8 tags, max 20
    - leadership
    - faith
    - protection
  personality: "..."             # 2-4 sentences
  temperature: 0.7               # 0.0-2.0
  context_window: 8192
  slots: []                      # leave empty for content WADs
  role: "Team Leader"            # optional
  # model: (omit -> default opencode/big-pickle)
  # nodes: (omit unless multi-node)
  # container/port: (omit unless service entity)
```

### Soul YAML (`entities/<name>/soul.yaml`) — ANAi schema
```yaml
identity:
  keeper: "captain_faith"
  epithet: "The Shield of the Faithful"
  seat: "Leader"
  version: "0.1.0-draft"
  status: "draft"
  persona_boundary: "..."        # kid-content limits
  card_candidates:              # optional
    note: "no seat assigned"

axioms:                         # max 20
  - id: "CSH-001"
    text: "Courage is faith moving forward."
    links: []

directives:
  - id: "D-CSH-001"
    rule: "Protect the innocent first."

principles:
  - "Faith over fear."

voice:
  dna_ref: "voice_dna.md"
  default_preset: "heroic"
  base_weights:
    fierce: 0.7
    tender: 0.5
    trickster: 0.2
    sovereign: 0.8

sovereignty:
  wing: "wing_captain_faith"
  diary_agent: "captain_faith"
  kg_prefix: "captain_faith_n1:"
  card_assignments: "none"       # or a card_assignment file

held:
  - "Will never abandon a teammate."

well_seeds:                     # optional
  - kind: "correction"
    domain: "content"
    rule: "Keep language age-appropriate"
    rationale: "Kids' series"
```

### Voice YAML (`voices/<voice_id>.yaml`)
```yaml
voice:
  name: "Captain Faith Voice"
  activation: "hey captain"
  personality: "Heroic, warm, encouraging."
  temperature: 0.8
  top_p: 0.9
  model_recommendation: "opencode/big-pickle"
  tags: [hero, leader, faith]
  dna_ref: "voice_dna.md"
```

### Hierarchy YAML (`hierarchy.yaml`)
```yaml
hierarchy:
  captain_faith_root:
    name: "Captain Faith"
    title: "Team Leader"
    role: "Sets mission direction"
    governs: [healer_node, tech_node]
    reports_to: null
    archetype: "The Leader"
    element: "Light"
    # governs_slots: []          # optional
    # contains: []               # optional
    # keeper: null               # optional
    # oversoul: null             # optional
```

### Manifest YAML (`manifest.yaml`)
```yaml
wad:
  name: "christian_super_heroes"
  version: "0.1.0"
  author: "Your Name"
  description: "An animated series of Christian super heroes..."
  license: "Proprietary"
  type: "pwad"                   # or "iwad"
  mode: "personal"
  priority: 1
  requires_engine: ">=1.6.0"
  startup:
    message: "The heroes are assembled!"
  voices:
    primary: "captain_faith_voice.yaml"
    secondary: []
  entities: []                   # loader scans entities/ dir
  dependencies: ["_omega_default"]
  hierarchy: "hierarchy.yaml"
  # vr_scenes: []               # optional
  # adapters: {}                # optional
```

### Dispatch YAML (`dispatch.yaml`) — optional
```yaml
entities:
  - name: "captain_faith"
    role: "HERO_LEADER"
    mode: "primary"              # primary | subagent
    purpose: "Team leader and mission director"
    capabilities: [leadership, strategy, protection]
    domains: [faith, courage, teamwork]
    slot: null                   # "SX" or null
    task_tool_type: "general"    # general | buildmaster | verity | node | explore
    owned_files: []
    # model: (omit -> default)
```

### Audience YAML (`audience.yaml`) — optional but recommended
```yaml
profiles:
  christian_family:
    name: "Christian Family (Ages 6-10)"
    description: "Warm, encouraging, age-appropriate, faith-affirming."
    constraints:
      - "Use simple, clear language"
      - "Age-appropriate content only"
      - "Affirm faith, hope, and love"
    style:
      formality: "casual"
      verbosity: "moderate"
      jargon_level: "low"
    technical_level: "general"
    tone_preference: "warm"
    format_preference: "narrative"
    known_knowledge: []
    assumed_context: "Child viewer, family co-viewing, faith-based household"
    epistemology: "applied"
default: "christian_family"
```

### Ethics YAML (`ethics.yaml`) — optional but recommended
```yaml
ideals:
  - id: 1
    text: "Love your neighbor"
  - id: 2
    text: "Courage in adversity"
  # ... 5-15 ideals
```

### Ingestion Domains (`ingestion/domains.yaml`) — optional
```yaml
domains:
  - name: "scripture_verses"
    wing: "wing_series"
    description: "Scripture verses used in episodes"
  - name: "episode_scripts"
    wing: "wing_series"
    description: "Approved episode outlines and scripts"
  - name: "character_bible"
    wing: "wing_series"
    description: "Backstories and design notes"
```

### Card/Symbolic Assignment (`entities/<name>/card_assignment_<x>.yaml`) — optional
```yaml
card:
  arcana: "major"                # or "minor" / "virtue" / "armor"
  key: 1
  title: "The Hero"
  tag: "card_id:01_hero"
  keeper: "captain_faith"
correspondences:
  element: "Light"
  color_scale: "blue and gold"
mystery_school:
  realm_name: "The Hall of Courage"
  status: "deferred"
versioning:
  entity_version: "0.1.0"
  kg_policy: "MERGE"
  diary_policy: "APPEND"
  voice_policy: "DELTA"
  backup_to_node0: true
```

### World Lump (`world/<sector_id>/<lump_id>.yaml`) — optional
```yaml
lump_id: "headquarters"
sector_id: "sector_01"
world_data:
  name: "Hero Headquarters"
  description: "The team's base of operations"
  characters_present: [captain_faith, healer]
metadata:
  wad_source: "christian_super_heroes"
```

### Voice DNA (`entities/<name>/voice_dna.md`) — markdown, freeform
A short markdown file describing tone, register, cadence, metaphors, quirks, catchphrases, forbidden words, example lines. Referenced by `voice.dna_ref`.

### Lesson entry (`proposed_lessons.yaml` / `approved_lessons.yaml`)
```yaml
- L1: "Raw observation from a session"
  L2: "Pattern noticed"
  L3: "Principle learned"
  evidence: ["session_gnosis.md:12-20"]
```

### Session Gnosis (`entities/<name>/session_gnosis.md`) — markdown, freeform
Per-session notes: what happened, decisions, continuity. The character's diary.

---

## APPENDIX B — Naming rules (so ChatGPT output validates)

- Entity ids: lowercase, underscores, no spaces, no apostrophes (`ma'at` → `maat`, `captain_faith`).
- Axiom ids: `<PREFIX>-NNN` (e.g. `CSH-001`). Max 20 axioms per soul.
- Directive ids: `D-<PREFIX>-NNN`.
- File names match entity id: `entities/captain_faith/captain_faith.yaml` + `soul.yaml` + `voice_dna.md`.
- Voice files: `voices/<voice_id>.yaml`.
- Hierarchy node ids: lowercase with `_root`/`_node` suffix (e.g. `captain_faith_root`).
- Card tags: `card_id:NN_name` (optional).
- No hardcoded model names anywhere except `model_recommendation` in voice files (optional) and `DEFAULT_ENTITY_MODEL` fallback.
- Manifest has `extra=forbid`: only known fields. Unknown keys cause load failure.
- Dual-tree sync: `config/wads/` and `src/omega/config_data/wads/` must stay byte-identical (lint enforces). We handle this at build time; your friend doesn't need to worry.

---

## APPENDIX C — What we generate vs. what you provide

**You provide (content):** series info, characters, visuals, souls, voices, hierarchy, lore, audience/ethics, locations.
**We generate (engine files):** directory skeleton, YAML files, validation, lint, registration, memory scaffolding, adapter config, OpenCode agent files.
**You iterate (after setup):** edit souls/voices in place; hot-reload picks up changes; promote lessons as characters grow.

---

*Generated for Omega Engine WAD authoring. Schema reference: `docs/WAD_MANIFEST_SCHEMA.md`. Developer guide: `docs/guides/HOW_TO_CREATE_WAD.md`.*