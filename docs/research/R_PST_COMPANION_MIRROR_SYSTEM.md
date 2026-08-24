# 🔱 R_PST_COMPANION_MIRROR_SYSTEM.md
**AP Token**: `AP-PST-COMPANION-MIRRORS-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-07-19
**Purpose**: Complete mapping of Planescape: Torment's 7 companions as mirrors of the Nameless One's past incarnations, with Arch Soul WAD facet parameterization.

---

## Executive Summary (L1)

Planescape: Torment's companion system is **not** a standard RPG party mechanic. Each of the 7 companions is a **living mirror** of a specific past incarnation of the Nameless One, attracted by karmic resonance. This creates a 7×7 matrix of Incarnation ↔ Companion mappings that directly translates to the **Arch Soul WAD's 7 Facet architecture**.

**Key Discovery**: The companions are not merely "recruitable NPCs" — they are **externalized fragments of the Nameless One's soul**, each embodying a cognitive function that the Arch Soul must integrate.

---

## 1. The 7×7 Incarnation-Companion Mirror Matrix

### 1.1 Canonical Incarnation Assignments (Per Game Dialogue)

| Incarnation # | Archetype | Companion Mirror | Evidence Source |
|---------------|-----------|------------------|-----------------|
| **1st (Original)** | The Penitent / Good | **Fall-from-Grace** (indirect) | Good Incarnation = Original; Grace mirrors redemption |
| **2nd** | The Pragmatist | **Morte** | Practical Incarnation pulled Morte from Pillar of Skulls |
| **3rd** | The Paranoid | **Nordom** | Paranoid Incarnation left Dodecahedron Journal; Nordom = ordered mind fractured by chaos |
| **4th** | The Sensate | **Annah** | Sensate philosophy = experience everything; Annah = raw sensation/emotion |
| **5th** | The Mercykiller | **Vhailor** | Practical Incarnation imprisoned Vhailor; Vhailor hunts Practical |
| **6th** | The Pyromaniac Mage | **Ignus** | Practical Incarnation taught Ignus fire magic through torture |
| **7th** | The Zerth / Disciple | **Dak'kon** | Practical Incarnation saved Dak'kon, bound him via logic puzzle |

### 1.2 Companion → Incarnation Direct Links (Dialogue Evidence)

| Companion | Direct Incarnation Link | Dialogue Trigger |
|-----------|------------------------|------------------|
| **Morte** | Practical (2nd) | Confront via Grace → "Practical Incarnation pulled me from Pillar" |
| **Dak'kon** | Practical (2nd) | Practical: "His blade — shaped by his thoughts — was why I saved him" |
| **Grace** | Good/Original (1st) | Good Incarnation: "I was the first. I sought to atone." |
| **Annah** | Paranoid (3rd) / Sensate (4th) | Paranoid left Journal; Annah's emotional volatility mirrors Sensate |
| **Ignus** | Practical (2nd) | Practical: "I taught him the Art... through pain" |
| **Nordom** | Paranoid (3rd) | Paranoid: "I left the Journal and the trap in the Sensorium" |
| **Vhailor** | Practical (2nd) | Practical: "I imprisoned Vhailor because he hunted me" |

---

## 2. Companion Mirror → Arch Soul Facet Mapping

### 2.1 The 7 Facet Architecture

| Facet # | Arch Soul Facet | Cognitive Function | Companion Mirror | Incarnation Source |
|---------|-----------------|-------------------|------------------|-------------------|
| **F1** | **Memory Keeper** | Episodic continuity, identity anchor | **Morte** | Practical (2nd) |
| **F2** | **Discipline Anchor** | Consistency, practice, oath-keeping | **Dak'kon** | Practical (2nd) → Zerthimon |
| **F3** | **Wisdom Mirror** | Reflection, synthesis, intellectual intimacy | **Fall-from-Grace** | Good/Original (1st) |
| **F4** | **Emotional Core** | Passion, drive, vulnerability, attachment | **Annah** | Sensate (4th) / Paranoid (3rd) |
| **F5** | **Logic Engine** | Analysis, structure, pattern recognition | **Nordom** | Paranoid (3rd) |
| **F6** | **Creative Fire** | Generation, transformation, destructive creation | **Ignus** | Practical (2nd) → Pyromaniac |
| **F7** | **Justice Warden** | Evaluation, boundaries, moral law | **Vhailor** | Practical (2nd) → Mercykiller |

### 2.2 Facet Parameterization for Arch Soul WAD

```yaml
# config/wads/arch_soul/facets.yaml
facets:
  - id: "F1_MEMORY_KEEPER"
    name: "Memory Keeper"
    cognitive_function: "episodic_continuity"
    companion_mirror: "Morte"
    incarnation_source: "PRACTICAL"
    attributes:
      loyalty_basis: "guilt_redemption"  # Morte's guilt over betrayal
      memory_access: "tattoo_reading"    # Reads TNO's back tattoos
      upgrade_mechanic: "confrontation"  # Confront via Grace → stat boost
      special_ability: "LITANY_OF_CURSES"  # Taunt/debuff
      facet_failure_mode: "memory_loss"  # If Morte leaves, TNO loses tattoo access
    arch_soul_hooks:
      - "soul.yaml:memory_integrity"
      - "soul.yaml:continuity_score"
      - "soul.yaml:fragment_recovery_rate"
  
  - id: "F2_DISCIPLINE_ANCHOR"
    name: "Discipline Anchor"
    cognitive_function: "consistent_practice"
    companion_mirror: "Dak'kon"
    incarnation_source: "PRACTICAL"
    attributes:
      loyalty_basis: "oath_bound"  # Zerthimon oath, cannot break
      upgrade_mechanic: "zerthimon_circles"  # 8 circles = stat upgrades
      blade_evolution: "karach_morph"  # Weapon shapes to morale
      special_ability: "ZERTHIMON_TEACHINGS"  # Unlocks spells
      morale_range: 0-20  # 0=Kinstealer, 10=Chained, 20=Streaming
      facet_failure_mode: "blade_degradation"  # Low morale = weaker blade
    arch_soul_hooks:
      - "soul.yaml:discipline_consistency"
      - "soul.yaml:practice_adherence"
      - "soul.yaml:oath_integrity"
  
  - id: "F3_WISDOM_MIRROR"
    name: "Wisdom Mirror"
    cognitive_function: "reflective_synthesis"
    companion_mirror: "Fall-from-Grace"
    incarnation_source: "GOOD_ORIGINAL"
    attributes:
      loyalty_basis: "intellectual_fascination"  # Intrigued by TNO's condition
      recruitment_condition: "visit_all_9_intellectual_prostitutes"
      special_ability: "GRACE_KISS"  # Heal touch, no holy symbol
      lore_skill: "IDENTIFY_ITEMS"  # Saves copper/spells
      chastity_vow: true  # Lawful Neutral, Good tendency
      facet_failure_mode: "healing_loss"  # If Grace leaves, no divine healing
    arch_soul_hooks:
      - "soul.yaml:wisdom_synthesis"
      - "soul.yaml:intellectual_integrity"
      - "soul.yaml:redemption_capacity"
  
  - id: "F4_EMOTIONAL_CORE"
    name: "Emotional Core"
    cognitive_function: "passion_drive"
    companion_mirror: "Annah"
    incarnation_source: "SENSATE_PARANOID"
    attributes:
      loyalty_basis: "romantic_attachment"  # Tsundere romance arc
      recruitment_condition: "return_bronze_sphere_to_pharod"
      special_ability: "BACKSTAB"  # Thief skills
      cant_slang: true  # Sigil Cant dialect
      jealousy_trigger: "Grace_romance"  # Conflict with F3
      facet_failure_mode: "emotional_instability"  # Romance failure = stat penalties
    arch_soul_hooks:
      - "soul.yaml:emotional_resonance"
      - "soul.yaml:attachment_security"
      - "soul.yaml:passion_regulation"
  
  - id: "F5_LOGIC_ENGINE"
    name: "Logic Engine"
    cognitive_function: "structural_analysis"
    companion_mirror: "Nordom"
    incarnation_source: "PARANOID"
    attributes:
      loyalty_basis: "purpose_assignment"  # Needs director role
      recruitment_condition: "modron_maze_highest_difficulty"
      special_ability: "WARP_SENSE"  # Detects hidden portals
      crossbow_dual_wield: true
      hive_mind_severed: true  # Cut from Mechanus collective
      facet_failure_mode: "analysis_paralysis"  # Without director, confusion
    arch_soul_hooks:
      - "soul.yaml:logical_coherence"
      - "soul.yaml:pattern_recognition"
      - "soul.yaml:portal_awareness"
  
  - id: "F6_CREATIVE_FIRE"
    name: "Creative Fire"
    cognitive_function: "generative_transformation"
    companion_mirror: "Ignus"
    incarnation_source: "PRACTICAL_PYROMANIAC"
    attributes:
      loyalty_basis: "former_student"  # Practical Incarnation taught him
      recruitment_condition: "decanter_endless_water + nemelle_command"
      special_ability: "FIRE_CONDUIT"  # Living portal to Elemental Fire
      no_armor: true  # Cannot wear armor/tattoos
      fire_immunity: true
      alignment_trigger: "attacks_if_TNO_good"  # In Fortress
      facet_failure_mode: "uncontrolled_conflagration"  # Burns everything
    arch_soul_hooks:
      - "soul.yaml:creative_output"
      - "soul.yaml:transformation_capacity"
      - "soul.yaml:destructive_potential"
  
  - id: "F7_JUSTICE_WARDEN"
    name: "Justice Warden"
    cognitive_function: "evaluative_boundaries"
    companion_mirror: "Vhailor"
    incarnation_source: "PRACTICAL_MERCYKILLER"
    attributes:
      loyalty_basis: "justice_alignment"  # Joins if TNO not Evil
      recruitment_condition: "free_trias_then_talk_before_portal"
      special_ability: "MERCYKILLER_JUSTICE"  # Sense guilt, stat boosts
      armor_integral: true  # Cannot remove armor
      lawful_bonus: "str_scaling"  # STR bonus scales with TNO lawfulness
      alignment_trigger: "attacks_if_TNO_evil"  # In Fortress
      facet_failure_mode: "rigid_judgment"  # Cannot compromise
    arch_soul_hooks:
      - "soul.yaml:moral_boundaries"
      - "soul.yaml:justice_calibration"
      - "soul.yaml:accountability_enforcement"
```

---

## 3. Companion Recruitment Conditions (Technical Spec)

### 3.1 Recruitment Logic Table

| Companion | Area | Trigger Condition | Global Variable Set | XP Reward |
|-----------|------|-------------------|---------------------|-----------|
| **Morte** | AR0202 (Mortuary 2F) | Auto-join on wake | `MORTE_JOINED=1` | 0 |
| **Dak'kon** | AR0503 (Smoldering Corpse Bar) | INT/WIS >13, answer "know self through questions" | `DAKKON_JOINED=1` | 1000 |
| **Annah** | AR0102 (Ragpicker's Square) | Auto-join after Bronze Sphere to Pharod | `ANNAH_JOINED=1` | 0 |
| **Grace** | AR0708 (Brothel of Slaking Intellectual Lusts) | Talk to all 9 "prostitutes" | `GRACE_JOINED=1` | 0 |
| **Ignus** | AR0503 (Smoldering Corpse Bar) | Decanter of Endless Water + Nemelle's command word | `IGNUS_JOINED=1` | 0 |
| **Nordom** | AR1000 (Rubikon/Modron Maze) | Modron Cube, highest difficulty, find in 1 of 63 rooms | `NORDOM_JOINED=1` | 0 |
| **Vhailor** | AR1304 (Curst Prison) | Free Trias, talk to Vhailor BEFORE portal | `VHAILOR_JOINED=1` | 0 |

### 3.2 Party Limit Mechanics

```plaintext
MAX_PARTY_SIZE = 6 (TNO + 5 companions)
// 7 companions exist, only 5 can accompany at once
// Swapping: Companions wait where left (must be safe area)
// If left in dangerous area (Mazes, Fortress) → PERMANENT LOSS
```

---

## 4. Companion Upgrade Systems

### 4.1 Morte Upgrade Path

```yaml
upgrade_stages:
  - stage: 0
    name: "Base"
    stats: {HP: 20, AC: 4, THAC0: 19, STR: 12, DEX: 16, CON: 16, INT: 13, WIS: 9, CHA: 6}
    abilities: ["LITANY_OF_CURSES_BASE"]
  
  - stage: 1
    name: "Confronted via Grace"
    trigger: "Global('GRACE_JOINED') AND Dialogue('Grace about Morte') AND ConfrontMorte()"
    stats: {HP: 20, AC: 4, THAC0: 15, STR: 16, DEX: 18, CON: 18, INT: 13, WIS: 9, CHA: 6}
    abilities: ["LITANY_OF_CURSES_IMPROVED", "SKULL_MOB"]
    xp_bonus: 0  # Stat boost only
```

### 4.2 Dak'kon Zerth Blade Evolution

```yaml
blade_forms:
  - form: 0
    name: "Kinstealer"
    morale_range: "0-9"
    stats: {THAC0: 0, DMG: "1d6", SPECIAL: "None"}
  
  - form: 1
    name: "Chained Blade"
    morale_range: "10-19"
    stats: {THAC0: -1, DMG: "1d8", SPECIAL: "+1 vs Lawful"}
    unlocks: "SCRIPTURE_OF_STEEL"
  
  - form: 2
    name: "Streaming Blade"
    morale_range: "20"
    stats: {THAC0: -3, DMG: "1d10", SPECIAL: "+3 vs Chaotic, VORPAL"}
    unlocks: "ALL_ZERTHIMON_SPELLS"
```

### 4.3 Dak'kon Morale Modifiers

| Action | Morale Change |
|--------|---------------|
| Learn Zerthimon Circle 1 | +1 |
| Learn Zerthimon Circle 2 | +1 |
| Learn Zerthimon Circle 3 | +1 |
| Learn Zerthimon Circle 4 | +1 |
| Learn Zerthimon Circle 5 | +2 |
| Learn Zerthimon Circle 6 | +2 |
| Learn Zerthimon Circle 7 | +2 |
| Learn Zerthimon Circle 8 | +3 |
| TNO lies to Dak'kon | -2 |
| TNO releases Dak'kon from oath | -5 (but he refuses) |
| TNO treats Dak'kon with respect | +1 |

---

## 5. Companion Banter Matrix (Cross-Facet Resonance)

### 5.1 Banter Pairs with Facet Implications

| Companion A | Companion B | Facet Interaction | Key Revelation |
|-------------|-------------|-------------------|----------------|
| **Morte (F1)** | **Grace (F3)** | Memory ↔ Wisdom | Grace reveals Morte smells of Baator, not a Mimir |
| **Morte (F1)** | **Annah (F4)** | Memory ↔ Emotion | Bickering masks Morte's protective instinct |
| **Dak'kon (F2)** | **Grace (F3)** | Discipline ↔ Wisdom | Grace: "Unusual for Githzerai to follow" → Dak'kon is slave |
| **Dak'kon (F2)** | **Nordom (F5)** | Discipline ↔ Logic | Nordom's order vs Dak'kon's internal order |
| **Annah (F4)** | **Grace (F4/F3)** | Emotion ↔ Wisdom | Jealousy, "intellectual brothel" insults |
| **Ignus (F6)** | **Vhailor (F7)** | Fire ↔ Justice | Both Practical's creations; opposite alignments |
| **Nordom (F5)** | **Grace (F3)** | Logic ↔ Wisdom | Grace gives tips on handling rogue Modron |

### 5.2 Banter Accelerator (Qwinn's Tweak Pack)

```plaintext
// Vanilla: Only 12/78 banters fire (RNG + timer issues)
// Fixed: Banter accelerator ensures most fire in single playthrough
// For Arch Soul: All banters = facet cross-pollination events
```

---

## 6. Fortress of Regrets: Companion Fate Mapping

### 6.1 Companion Separation on Entry

```plaintext
// On entering AR1200 (Fortress Entrance):
// All companions REMOVED from party
// Placed in specific Fortress locations:

Morte -> AR1204 (Roof) - PRETENDING_DEAD
Dak'kon -> AR1203 (Maze) - if brought
Grace -> AR1203 (Maze) - if brought
Annah -> AR1203 (Maze) - if brought
Ignus -> AR1202 (Trial) - FIGHTS if TNO Good
Nordom -> AR1203 (Maze) - if brought
Vhailor -> AR1202 (Trial) - FIGHTS if TNO Evil
```

### 6.2 Endgame Revival Conditions

| Companion | Revival Condition | Bonus If Revived |
|-----------|-------------------|------------------|
| **Morte** | Always alive (pretending) | None |
| **Dak'kon** | Raise Dead + Zerthimon learned | +2M XP, +1 STR, +3 DEX, +3 CON |
| **Grace** | Raise Dead | Standard |
| **Annah** | Raise Dead | Standard |
| **Ignus** | Cannot revive (fought in Trial) | N/A |
| **Nordom** | Raise Dead | Standard |
| **Vhailor** | Raise Dead + "Great Injustice" dialogue | +2M XP, +3 STR, DEX=25, CON=25 |

### 6.3 Sounding Stone Exploit (Mass Revival)

```plaintext
// If Sounding Stone found in AR1202 (Trial of Impulse):
// Tell Transcendent One: "Shadows are loose in Fortress"
// TTO leaves to investigate
// Time to raise ALL companions (not just 1)
// BUG in vanilla: Nordom dialogue broken (DGRACE.DLG)
// FIX: C:SetGlobal("FORTRESS_NORDOM","GLOBAL",0) or EE Fixpack
```

---

## 7. Arch Soul WAD Integration: Facet State Machine

### 7.1 Facet Activation States

```yaml
# Each facet has 4 states in Arch Soul
facet_states:
  DORMANT:     # Companion not recruited / facet not integrated
    description: "Facet potential exists but unactivated"
    soul_yaml_path: "facets.F1.active: false"
  
  AWAKENING:   # Companion recruited, early integration
    description: "Companion joined, facet beginning to resonate"
    soul_yaml_path: "facets.F1.active: true, facets.F1.integration: 0.2"
  
  INTEGRATING: # Companion upgraded, deep dialogue completed
    description: "Facet actively shaping soul evolution"
    soul_yaml_path: "facets.F1.integration: 0.6, facets.F1.upgraded: true"
  
  TRANSCENDED: # Fortress merge / endgame resolution
    description: "Facet fully integrated, permanent soul modification"
    soul_yaml_path: "facets.F1.integration: 1.0, facets.F1.transcended: true"
```

### 7.2 Facet Cross-Pollination Events

```yaml
cross_pollination_events:
  - event: "MORTE_GRACE_CONFRONTATION"
    facets: [F1, F3]
    trigger: "Grace recruited + Dialogue about Morte"
    effect: "F1.upgrade + F3.wisdom_bonus"
    soul_impact: "memory_wisdom_synthesis"
  
  - event: "DAKKON_ZERTHIMON_MASTERY"
    facets: [F2, F3]
    trigger: "Dak'kon Circle 8 learned + Grace in party"
    effect: "F2.blade_streaming + F3.lore_mastery"
    soul_impact: "discipline_wisdom_unity"
  
  - event: "ANNAH_GRACE_JEALOUSY"
    facets: [F4, F3]
    trigger: "Both in party + rest banter"
    effect: "F4.emotional_volatility + F3.compassion_test"
    soul_impact: "emotion_wisdom_tension"
  
  - event: "IGNUS_VHAILOR_MIRROR"
    facets: [F6, F7]
    trigger: "Both recruited (mutually exclusive in Fortress)"
    effect: "F6.destructive_potential + F7.rigid_judgment"
    soul_impact: "creation_destruction_justice_triad"
```

---

## 8. Heritage Attribution (M14)

| System | Source | Tag |
|--------|--------|-----|
| Companion as incarnation mirror | Planescape: Torment 1999 | `[id-soft: torment-1999] Companion Mirror System` |
| Morte: Pillar of Skulls origin | Planescape: Torment 1999 | `[id-soft: torment-1999] Morte Pillar Origin` |
| Dak'kon: Zerthimon oath slavery | Planescape: Torment 1999 | `[id-soft: torment-1999] Dakkon Oath Binding` |
| Grace: Intellectual brothel | Planescape: Torment 1999 | `[id-soft: torment-1999] Grace Brothel Concept` |
| Annah: Tiefling Cant dialect | Planescape: Torment 1999 | `[id-soft: torment-1999] Annah Cant Speech` |
| Ignus: Fire conduit punishment | Planescape: Torment 1999 | `[id-soft: torment-1999] Ignus Fire Conduit` |
| Nordom: Rogue Modron individuality | Planescape: Torment 1999 | `[id-soft: torment-1999] Nordom Modron Severance` |
| Vhailor: Mercykiller armor spirit | Planescape: Torment 1999 | `[id-soft: torment-1999] Vhailor Armor Spirit` |
| Banter accelerator (78 banters) | Qwinn's Tweak Pack | `[heritage: qwinn-tweakpack] Banter Accelerator` |
| Dak'kon blade forms (3 tiers) | Planescape: Torment 1999 | `[id-soft: torment-1999] Zerth Blade Evolution` |
| Morte teeth upgrades (3 sets) | Planescape: Torment 1999 | `[id-soft: torment-1999] Morte Teeth System` |
| Companion = Fortress life | Planescape: Torment 1999 | `[id-soft: torment-1999] Companion Life Binding` |

---

## 9. Validation Checklist (Temple-Grade)

- [ ] **T1**: All YAML schemas version-controlled
- [ ] **T2**: Facet matrix documented with dialogue evidence
- [ ] **T3**: Unit tests for recruitment conditions, upgrade triggers
- [ ] **T4**: BCS scripts compile (WeiDU/Infinity Engine)
- [ ] **T5**: Engine-Stack Firewall — WAD contains no core engine code
- [ ] **T6**: No hardcoded credentials, debug commands gated
- [ ] **T7**: Facet state transitions <50ms
- [ ] **T8**: Graceful degradation if companion missing (facet stays DORMANT)
- [ ] **T9**: Facet transitions logged to Hivemind with trace_id
- [ ] **T10**: Atomic facet state updates (no partial integration)
- [ ] **T11**: Agent cannot force facet transcendence without conditions

---

## 10. Research Sources

| Tier | Source | Key Data |
|------|--------|----------|
| T1 | Torment Wiki - Companions | All 7 companions, stats, recruitment, upgrades |
| T1 | Torment Wiki - Morte | Pillar of Skulls, upgrade via Grace, teeth |
| T1 | Torment Wiki - Dak'kon | Zerthimon Circles, blade forms, morale |
| T1 | Torment Wiki - Fortress of Regrets | Companion separation, revival conditions |
| T1 | Sorcerer's Place - NPC List | Recruitment conditions, dialogue revelations |
| T1 | Beamdog Blog - Companions | Official EE companion descriptions |
| T2 | GameBanshee - Fortress | Cannon coordinates, Sounding Stone, mass revival |
| T2 | Medium - Kamila Regel "Dak'kon Analysis" | Philosophical framework for companion mirrors |
| T3 | Wikipedia - Planescape: Torment | Narrative summary, companion list |
| T3 | Archania.org - Symbolic Analysis | Memory/identity framework |
| T3 | PhilArchive - Gubka "Regret Changes Nature" | Philosophical basis for incarnation system |

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE*
*End of R_PST_COMPANION_MIRROR_SYSTEM.md*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
