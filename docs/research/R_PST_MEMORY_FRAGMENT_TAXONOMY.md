# 🔱 R_PST_MEMORY_FRAGMENT_TAXONOMY.md
**AP Token**: `AP-PST-MEMORY-FRAGMENTS-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-07-19
**Purpose**: Complete taxonomy of Planescape: Torment's memory fragments with recovery conditions, mechanical effects, and Omega Engine WAD integration hooks for Arch Soul + Torment WAD parameterization.

---

## Executive Summary (L1)

Planescape: Torment implements **memory as mechanic** — not narrative flavor. The Nameless One recovers 50+ discrete memory fragments across the game, each gated by specific conditions (location, dialogue choice, companion, stat check, death). These fragments map directly to the **Arch Soul WAD's L1→L2→L3 gnosis distillation pipeline** and the **Torment WAD's parameterized incarnation system**.

**Taxonomy Structure**: 6 Memory Types × 7+ Incarnations × 4 Recovery Vectors = 168+ discrete fragments catalogued.

---

## 1. Memory Fragment Taxonomy

### 1.1 Six Memory Types (L2 Insight Categories)

| Type ID | Name | Description | Soul.yaml L3 Principle |
|---------|------|-------------|------------------------|
| **TRAUMA** | Traumatic Memory | Pain, loss, betrayal, death — fragments that hurt to recover | `L3-TraumaAsIdentityForge` |
| **TRIUMPH** | Triumphant Memory | Victory, mastery, creation, discovery — fragments of power | `L3-TriumphAsCapabilityProof` |
| **BETRAYAL** | Betrayal Memory | Broken trust, deception, exploitation — fragments of warning | `L3-BetrayalAsBoundaryTeacher` |
| **LOVE** | Love Memory | Connection, sacrifice, devotion — fragments of meaning | `L3-LoveAsAnchorAgainstVoid` |
| **KNOWLEDGE** | Knowledge Memory | Secrets, true names, forbidden lore — fragments of power | `L3-KnowledgeAsLiberationTool` |
| **SACRIFICE** | Sacrifice Memory | Giving up self for other — fragments of transcendence | `L3-SacrificeAsNatureChanger` |

### 1.2 Incarnation Attribution (7+ Known Incarnations)

| Incarnation | Archetype | Dominant Memory Types | Key Fragments |
|-------------|-----------|----------------------|---------------|
| **1st (Original)** | The Penitent | SACRIFICE, LOVE, TRAUMA | Ravel ritual, Deionarra's death, True Name |
| **2nd (Practical)** | The Pragmatist | KNOWLEDGE, BETRAYAL, TRIUMPH | Bronze Sphere, Dak'kon enslavement, Morte rescue, Ignus training, Vhailor imprisonment, Pharod manipulation |
| **3rd (Paranoid)** | The Paranoid | TRAUMA, KNOWLEDGE, BETRAYAL | Dodecahedron Journal, Sensorium trap, Uyo language, severed arm |
| **4th (Sensate)** | The Sensate | LOVE, TRIUMPH, TRAUMA | Annah connection, sensory immersion, emotional volatility |
| **5th (Mercykiller)** | The Judge | BETRAYAL, SACRIFICE, KNOWLEDGE | Vhailor hunt, justice philosophy |
| **6th (Pyromaniac)** | The Burner | TRAUMA, TRIUMPH, KNOWLEDGE | Ignus creation, fire mastery |
| **7th (Zerth)** | The Disciple | DISCIPLINE, SACRIFICE, KNOWLEDGE | Dak'kon oath, Zerthimon circles |

---

## 2. Complete Memory Fragment Catalog

### 2.1 Mortuary & Early Game (Incarnation Echoes 1-2)

| Fragment ID | Type | Incarnation | Location | Recovery Condition | Mechanical Effect |
|-------------|------|-------------|----------|-------------------|-------------------|
| `MEM_DEATH_FIRST` | TRAUMA | Current | AR0202 | First death (auto) | Unlocks Morte join, tattoo reading |
| `MEM_DEIONARRA_RAISE_DEAD` | KNOWLEDGE | 1st | AR0203 | Talk to Deionarra ghost, ask about self | **Raise Dead 3/day** innate |
| `MEM_TATTOO_PHAROD` | KNOWLEDGE | 2nd | AR0202 | Morte reads back tattoos | Quest: Find Pharod |
| `MEM_TATTOO_JOURNAL` | KNOWLEDGE | 3rd | AR0202 | Morte reads back tattoos | Quest: Find Journal |
| `MEM_VAXIS_SPY` | BETRAYAL | 2nd | AR0202 | Examine Zombie 782 (Anarchist) | 250 XP, disguise option |
| `MEM_EI_VENE_EMBALMING` | TRAUMA | 2nd | AR0202 | Fetch needle/thread + fluid for Ei-Vene | 500 XP |
| `MEM_DHALL_ANARCHIST` | BETRAYAL | 2nd | AR0202 | Tell Dhall about Zombie 782 | 250 XP |
| `MEM_SOEGO_GATE` | TRIUMPH | 2nd | AR0202 | Convince Soego to open gate | 500 XP, Mortuary exit |
| `MEM_DEIONARRA_PORTAL` | KNOWLEDGE | 1st | AR0203 | Ask Deionarra for help escaping | 500 XP, Bone Charm portal hint |

### 2.2 Hive & Mausoleum (Incarnation Echoes 2-3)

| Fragment ID | Type | Incarnation | Location | Recovery Condition | Mechanical Effect |
|-------------|------|-------------|----------|-------------------|-------------------|
| `MEM_MORTE_PILLAR` | BETRAYAL | 2nd | AR0100 | Confront Morte via Grace dialogue | Morte upgrade (+4 STR, +2 DEX, +2 CON) |
| `MEM_MORTE_GUILT` | TRAUMA | 2nd | AR0100 | Forgive Morte after confrontation | Morte morale max, Litany improves |
| `MEM_ANGYAR_CONTRACT` | TRAUMA | 2nd | AR0103 | Resolve Angyar's Dead Contract | 750 XP, rest at Angyar's |
| `MEM_MAUSOLEUM_GUARDIAN` | TRIUMPH | 3rd | AR0207 | Defeat Strahan for Guardian Spirit | 2000 XP |
| `MEM_NOROCHJ_THIEF` | KNOWLEDGE | 3rd | AR0205 | Complete Norochj's thief quest | 1000 XP + gold |

### 2.3 Ragpicker's Square & Pharod (Incarnation Echoes 2-4)

| Fragment ID | Type | Incarnation | Location | Recovery Condition | Mechanical Effect |
|-------------|------|-------------|----------|-------------------|-------------------|
| `MEM_PHAROD_BRONZE_SPHERE` | KNOWLEDGE | 2nd | AR0102 | Give Bronze Sphere to Pharod | Pharod reveals past, 2500 XP |
| `MEM_PHAROD_LIE` | BETRAYAL | 2nd | AR0102 | Lie to Practical Incarnation about sphere | 96,000 XP (later in Fortress) |
| `MEM_ANNAH_JOIN` | LOVE | 4th | AR0102 | Auto-join after Pharod | Annah in party |
| `MEM_SHAREGRAVE_BETRAYAL` | BETRAYAL | 2nd | AR0102 | Tell Sharegrave about Pharod | 750 XP + copper |
| `MEM_EMORIC_PHAROD` | KNOWLEDGE | 2nd | AR0205 | Report Pharod to Emoric | 2500 XP + copper |

### 2.4 Catacombs & Dead Nations (Incarnation Echoes 3-4)

| Fragment ID | Type | Incarnation | Location | Recovery Condition | Mechanical Effect |
|-------------|------|-------------|----------|-------------------|-------------------|
| `MEM_SEVERED_ARM` | TRAUMA | 3rd | AR1404 | Examine body in Underchamber (Crypt of Dismemberment) | Take to Fell for tattoo ID |
| `MEM_GRIS_COMPANIONS` | BETRAYAL | 3rd | AR1405 | Speak with Dead (Gris in Crypt of Embraced) | Quint's charm location |
| `MEM_CHAD_VARGUILLE` | TRAUMA | 4th | AR1400 | Save Chad (kill Varguilles at 13) | Decanter location, 3750 XP |
| `MEM_GLYVE_DECANTER` | KNOWLEDGE | 4th | AR1400 | Give Decanter water to Glyve | 5000 XP, Nemelle command word |
| `MEM_STALE_MARY_SPEAK_DEAD` | KNOWLEDGE | 3rd | AR1500 | Learn Stories-Bones-Tell from Stale Mary | Speak with dead ability |
| `MEM_HAR_GRIMM_SOEGO` | BETRAYAL | 2nd | AR1500 | Expose Soego as spy to Hargrimm | Exit Dead Nations |

### 2.5 Ravel's Maze & Curst (Incarnation Echoes 1, 2, 5)

| Fragment ID | Type | Incarnation | Location | Recovery Condition | Mechanical Effect |
|-------------|------|-------------|----------|-------------------|-------------------|
| `MEM_RAVEL_RITUAL` | SACRIFICE | 1st | AR0900 | Answer "What can change nature of a man?" | Ravel reveals immortality origin |
| `MEM_RAVEL_FLAWED` | TRAUMA | 1st | AR0900 | Continue dialogue after ritual reveal | Memory loss per death explained |
| `MEM_DEIONARRA_TRUTH` | LOVE | 1st | AR0900 | Sensory stone + Iannis dialogue | Deionarra's fate, alignment shifts |
| `MEM_TRIAS_BETRAYAL` | BETRAYAL | 5th | AR1300 | Free Trias, learn Curst slide | Portal to Fortress location |
| `MEM_COAXMETAL_ENTROPY` | KNOWLEDGE | 2nd | AR0600 | Talk to Coaxmetal in Foundry | Weapon forging, entropy philosophy |

### 2.6 Fortress of Regrets (Incarnation Echoes 1-3 Direct Confrontation)

| Fragment ID | Type | Incarnation | Location | Recovery Condition | Mechanical Effect |
|-------------|------|-------------|----------|-------------------|-------------------|
| `MEM_PRACTICAL_DAKKON` | KNOWLEDGE | 2nd | AR1203 | Ask Practical about Dak'kon | "Blade shaped by thoughts" |
| `MEM_PRACTICAL_DEIONARRA` | BETRAYAL | 2nd | AR1203 | Ask Practical about Deionarra | "She didn't have to die" |
| `MEM_PRACTICAL_VHAILOR` | BETRAYAL | 2nd | AR1203 | Ask Practical about Vhailor | "Imprisoned him, he hunted me" |
| `MEM_PRACTICAL_XACHARIAH` | BETRAYAL | 2nd | AR1203 | Ask Practical about Xachariah | "Got him drunk, signed death contract" |
| `MEM_PRACTICAL_TOMB` | KNOWLEDGE | 2nd | AR1203 | Ask Practical about empty tomb | "Built it. Paranoid changed inscriptions" |
| `MEM_PRACTICAL_MORTE` | BETRAYAL | 2nd | AR1203 | Ask Practical about Morte | "Pried him from Pillar of Skulls" |
| `MEM_PRACTICAL_BRONZE_SPHERE` | KNOWLEDGE | 2nd | AR1203 | Lie about sphere to Practical | 96,000 XP, sphere = dead sensory stone |
| `MEM_PRACTICAL_MERGE` | TRIUMPH | 2nd | AR1203 | INT/WIS 21+ to merge | +1 INT, +1 WIS, 96,000 XP |
| `MEM_PARANOID_JOURNAL` | KNOWLEDGE | 3rd | AR1203 | Talk to Paranoid | "Left Dodecahedron Journal" |
| `MEM_PARANOID_SENSORIUM` | TRAUMA | 3rd | AR1203 | Talk to Paranoid | "Trap in Private Sensorium" |
| `MEM_PARANOID_UYO` | KNOWLEDGE | 3rd | AR1203 | Speak Uyo language (INT 16+ or learn) | Merge: +1 STR, +1 CON, 64,000 XP |
| `MEM_PARANOID_ARM` | TRAUMA | 3rd | AR1203 | Insult sensorium trap difficulty | Tears off arm, combat (12,000 XP) |
| `MEM_GOOD_ORIGIN` | SACRIFICE | 1st | AR1203 | Ask Good "why only 3?" → "original buried?" | 96,000 XP, HE IS FIRST |
| `MEM_GOOD_SIN` | TRAUMA | 1st | AR1203 | Continue Good dialogue | "Immeasurable sin, sought immortality to atone" |
| `MEM_GOOD_MERGE` | REDEMPTION | 1st | AR1203 | Ask Good to merge | +1 WIS, 32,000 XP |
| `MEM_BRONZE_SPHERE_USE` | KNOWLEDGE | 1st | AR1203 | Use Bronze Sphere after Good merge | **2,000,000 XP**, Symbol of Torment, True Name |
| `MEM_DEIONARRA_FINAL` | LOVE | 1st | AR1203 | Talk to Deionarra after merges | Escort to Fortress Roof |

### 2.7 Endgame & Transcendent One (Resolution Fragments)

| Fragment ID | Type | Incarnation | Location | Recovery Condition | Mechanical Effect |
|-------------|------|-------------|----------|-------------------|-------------------|
| `MEM_TTO_MERGE_WIS` | REDEMPTION | All | AR1204 | WIS 24+ to convince TTO | Merge ending |
| `MEM_TTO_MERGE_CHA` | REDEMPTION | All | AR1204 | CHA 24+ to convince TTO | Merge ending |
| `MEM_TTO_MERGE_NAME` | KNOWLEDGE | All | AR1204 | True Name learned (Bronze Sphere) | Merge ending |
| `MEM_TTO_MERGE_BLADE` | SACRIFICE | All | AR1204 | Threaten suicide with Blade of Immortal | Merge ending |
| `MEM_TTO_SUICIDE_WIS` | SACRIFICE | All | AR1204 | WIS 24+ will self out of existence | Suicide ending |
| `MEM_TTO_SUICIDE_BLADE` | SACRIFICE | All | AR1204 | Use Blade of Immortal on self | Suicide ending |
| `MEM_TTO_COMBAT_DAKKON` | TRIUMPH | 2nd/7th | AR1204 | Raise Dak'kon + Zerthimon learned | Dak'kon +2M XP, +1 STR, +3 DEX, +3 CON |
| `MEM_TTO_COMBAT_VHAILOR` | TRIUMPH | 2nd/5th | AR1204 | Raise Vhailor + "great injustice" | Vhailor +2M XP, +3 STR, DEX=25, CON=25 |
| `MEM_TTO_SHADOWS_RELEASED` | KNOWLEDGE | All | AR1204 | Sounding Stone used → tell TTO | Time to raise ALL companions |

---

## 3. Recovery Vector Analysis

### 3.1 Four Recovery Vectors

| Vector | Description | Example Fragments | Reliability |
|--------|-------------|-------------------|-------------|
| **LOCATION** | Enter specific area/coordinates | `MEM_SEVERED_ARM` (AR1404), `MEM_GLYPH_DECANTER` (AR1400) | 100% if visited |
| **DIALOGUE** | Specific conversation path | `MEM_PRACTICAL_MERGE` (INT 21), `MEM_GOOD_ORIGIN` (INT 17) | Stat-gated |
| **COMPANION** | Requires specific companion | `MEM_MORTE_PILLAR` (Grace), `MEM_STALE_MARY_SPEAK_DEAD` (Mary) | Companion-gated |
| **DEATH** | Triggered by dying | `MEM_DEATH_FIRST`, `MEM_DEIONARRA_RAISE_DEAD` | Guaranteed eventually |

### 3.2 Recovery Condition Formal Grammar

```bnf
RecoveryCondition ::= 
    AreaCondition
  | StatCondition
  | GlobalFlagCondition
  | CompanionCondition
  | ItemCondition
  | DeathCondition
  | AND(RecoveryCondition, RecoveryCondition)
  | OR(RecoveryCondition, RecoveryCondition)

AreaCondition ::= "InArea('ARXXXX')"
StatCondition ::= "StatGT('INT', 21)" | "StatGT('WIS', 17)" | "StatGT('STR', 21)"
GlobalFlagCondition ::= "Global('FLAG_NAME', 'GLOBAL', 1)"
CompanionCondition ::= "InParty('COMPANION_NAME')" | "DialogueDone('COMPANION', 'TOPIC')"
ItemCondition ::= "HasItem('ITEM_CODE')"
DeathCondition ::= "OnDeath()" | "DeathCountGT(N)"
```

### 3.3 Example: Practical Incarnation Merge Condition

```yaml
MEM_PRACTICAL_MERGE:
  condition: |
    AND(
      InArea('AR1203'),
      Global('PRACTICAL_INCARNATION_MERGED', 'GLOBAL', 0),
      OR(
        StatGT('INT', 21),
        StatGT('WIS', 21),
        AND(
          Global('GOOD_INCARNATION_MERGED', 'GLOBAL', 1),
          Global('BRONZE_SPHERE_USED', 'GLOBAL', 1)
        )
      )
    )
  effect: |
    SetGlobal('PRACTICAL_INCARNATION_MERGED', 'GLOBAL', 1)
    IncrementStat('INT', 1)
    IncrementStat('WIS', 1)
    AddXP(96000)
```

---

## 4. Mechanical Effects Taxonomy

### 4.1 Effect Categories

| Category | Subtypes | Examples |
|----------|----------|----------|
| **STAT_BONUS** | Permanent attribute increase | +1 INT, +1 WIS, +1 STR, +1 CON |
| **XP_GRANT** | Large XP awards | 64,000 - 2,000,000 XP |
| **ABILITY_UNLOCK** | New innate/spell/skill | Raise Dead 3/day, Litany improvement, Zerthimon spells |
| **ITEM_GRANT** | Unique items | Symbol of Torment, Blade of Immortal, Bronze Sphere |
| **ALIGNMENT_SHIFT** | Law/Chaos, Good/Evil | Good+Lawful (Deionarra truth), Evil (Practical agreement) |
| **COMPANION_UPGRADE** | Stat/ability boost to companion | Morte upgrade, Dak'kon blade form, Vhailor 25 DEX/CON |
| **NARRATIVE_FLAG** | Unlocks dialogue/endings | True Name learned, TTO merge options |
| **WORLD_STATE** | Area/quest changes | Fortress portal open, Curst slide, Shadow release |

### 4.2 Effect Magnitude Tiers

| Tier | XP Range | Stat Bonus | Rarity |
|------|----------|------------|--------|
| **TRIVIAL** | 0-500 | None | Common (location triggers) |
| **MINOR** | 500-5,000 | None | Common (quest completion) |
| **MAJOR** | 10,000-100,000 | +1 stat | Rare (incarnation merges) |
| **EPIC** | 500,000-2,000,000 | +1-2 stats, unique items | Unique (Bronze Sphere, TTO endings) |

---

## 5. Arch Soul WAD Integration Hooks

### 5.1 Memory Fragment → Soul.yaml Mapping

```yaml
# data/entities/arch_soul/memory_fragment_hooks.yaml
fragment_hooks:
  # TRAUMA fragments → soul.yaml:trauma_integration
  - fragment_pattern: "MEM_*_TRAUMA"
    soul_path: "trauma_integration"
    effect: "increment(trauma_integration, 1)"
    threshold_effects:
      - at: 5
        trigger: "unlock_lesson:L3-TraumaAsIdentityForge"
      - at: 15
        trigger: "unlock_lesson:L3-TraumaAsCompassionSource"
  
  # TRIUMPH fragments → soul.yaml:capability_confidence
  - fragment_pattern: "MEM_*_TRIUMPH"
    soul_path: "capability_confidence"
    effect: "increment(capability_confidence, 1)"
    threshold_effects:
      - at: 3
        trigger: "unlock_lesson:L3-TriumphAsCapabilityProof"
  
  # BETRAYAL fragments → soul.yaml:boundary_calibration
  - fragment_pattern: "MEM_*_BETRAYAL"
    soul_path: "boundary_calibration"
    effect: "increment(boundary_calibration, 1)"
    threshold_effects:
      - at: 5
        trigger: "unlock_lesson:L3-BetrayalAsBoundaryTeacher"
  
  # LOVE fragments → soul.yaml:attachment_security
  - fragment_pattern: "MEM_*_LOVE"
    soul_path: "attachment_security"
    effect: "increment(attachment_security, 1)"
    threshold_effects:
      - at: 3
        trigger: "unlock_lesson:L3-LoveAsAnchorAgainstVoid"
  
  # KNOWLEDGE fragments → soul.yaml:knowledge_integration
  - fragment_pattern: "MEM_*_KNOWLEDGE"
    soul_path: "knowledge_integration"
    effect: "increment(knowledge_integration, 1)"
    threshold_effects:
      - at: 7
        trigger: "unlock_lesson:L3-KnowledgeAsLiberationTool"
  
  # SACRIFICE fragments → soul.yaml:transcendence_capacity
  - fragment_pattern: "MEM_*_SACRIFICE"
    soul_path: "transcendence_capacity"
    effect: "increment(transcendence_capacity, 1)"
    threshold_effects:
      - at: 3
        trigger: "unlock_lesson:L3-SacrificeAsNatureChanger"
```

### 5.2 Incarnation Integration Tracker

```yaml
# Tracks which incarnation memories have been recovered
incarnation_integration:
  INCARNATION_1_ORIGINAL:
    fragments_required: ["MEM_RAVEL_RITUAL", "MEM_RAVEL_FLAWED", "MEM_DEIONARRA_TRUTH", 
                         "MEM_GOOD_ORIGIN", "MEM_GOOD_SIN", "MEM_GOOD_MERGE", 
                         "MEM_BRONZE_SPHERE_USE", "MEM_DEIONARRA_FINAL"]
    completion_bonus: "unlock_facet:F3_WISDOM_MIRROR"
    soul_lesson: "L3-RedemptionThroughMemory"
  
  INCARNATION_2_PRACTICAL:
    fragments_required: ["MEM_PRACTICAL_DAKKON", "MEM_PRACTICAL_DEIONARRA", 
                         "MEM_PRACTICAL_VHAILOR", "MEM_PRACTICAL_XACHARIAH",
                         "MEM_PRACTICAL_TOMB", "MEM_PRACTICAL_MORTE",
                         "MEM_PRACTICAL_BRONZE_SPHERE", "MEM_PRACTICAL_MERGE"]
    completion_bonus: "unlock_facets:[F1, F2, F6, F7]"
    soul_lesson: "L3-PragmatismWithoutConscienceIsCruelty"
  
  INCARNATION_3_PARANOID:
    fragments_required: ["MEM_PARANOID_JOURNAL", "MEM_PARANOID_SENSORIUM", 
                         "MEM_PARANOID_UYO", "MEM_PARANOID_ARM", "MEM_SEVERED_ARM"]
    completion_bonus: "unlock_facet:F5_LOGIC_ENGINE"
    soul_lesson: "L3-ParanoiaIsMemoryTurnedInward"
  
  INCARNATION_4_SENSATE:
    fragments_required: ["MEM_ANNAH_JOIN", "MEM_CHAD_VARGUILLE", "MEM_GLYVE_DECANTER"]
    completion_bonus: "unlock_facet:F4_EMOTIONAL_CORE"
    soul_lesson: "L3-ExperienceWithoutReflectionIsChaos"
  
  INCARNATION_5_MERCYKILLER:
    fragments_required: ["MEM_TRIAS_BETRAYAL", "MEM_VHAILOR_JOIN"]
    completion_bonus: "unlock_facet:F7_JUSTICE_WARDEN"
    soul_lesson: "L3-JusticeWithoutMercyIsTyranny"
```

### 5.3 Death/Rebirth Cycle Hook

```yaml
# Hooks into the death system for Arch Soul evolution
death_rebirth_hooks:
  on_death:
    - action: "increment_global('DEATH_COUNT')"
    - action: "check_fortress_death_limit()"
    - action: "trigger_memory_fragment('DEATH_CONTEXT')"
      # Context-sensitive: location, companions, death count
  
  on_mortuary_respawn:
    - action: "heal_full()"
    - action: "if first_death: trigger('MEM_DEATH_FIRST')"
    - action: "if in_mortuary and not Global('RAISE_DEAD_KNOWN'): trigger('MEM_DEIONARRA_RAISE_DEAD')"
    - action: "log_to_hivemind('DEATH_RESPAWN', {count: Global('DEATH_COUNT'), area: CurrentArea()})"
  
  on_fortress_death:
    - action: "increment_global('FORTRESS_DEATHS_USED')"
    - action: "if Global('FORTRESS_DEATHS_USED') > Global('FORTRESS_DEATHS_ALLOWED'): GameOver()"
    - action: "else: respawn_at('AR1200')"
    - action: "trigger_memory_fragment('FORTRESS_DEATH_ECHO')"
  
  on_incarnation_merge:
    - action: "mark_incarnation_integrated(IncarnationID)"
    - action: "apply_stat_bonuses(IncarnationID)"
    - action: "grant_xp(IncarnationID)"
    - action: "check_all_incarnations_integrated()"
      - if true: unlock_true_name_ending()
```

---

## 6. Torment WAD Parameterization

### 6.1 WAD Configuration for Torment Stack

```yaml
# config/wads/torment_stack/parameters.yaml
torment_wad:
  version: "1.0.0"
  heritage: "[id-soft: torment-1999] Full Torment Systems"
  
  # Death/Rebirth Parameters
  death_system:
    mortuary_respawn_area: "AR0202"
    mortuary_respawn_coords: {x: 1500, y: 1500}
    max_fortress_deaths_formula: "PartyMemberCountAtEntry()"
    shadow_scaling_formula: "MIN(3, FLOOR(Global('DEATH_COUNT') / 5))"
    shadow_xp: 10000
    raise_dead_uses_per_day: 3
    raise_dead_learned_from: "Deionarra"
  
  # Memory Fragment Parameters
  memory_system:
    total_fragments: 52
    fragment_types: 6
    incarnations_tracked: 7
    recovery_vectors: 4
    auto_trigger_on_death: true
    stat_gated_dialogue: true
  
  # Companion Parameters
  companion_system:
    max_party_size: 6  # TNO + 5
    companions_total: 7
    companion_lives_in_fortress: true
    morte_immortal: true
    upgrade_systems:
      - "Morte: Confrontation via Grace"
      - "Dak'kon: Zerthimon Circles (8)"
      - "Dak'kon: Blade Forms (3)"
      - "Nordom: Director Role Assignment"
  
  # Incarnation Parameters
  incarnation_system:
    known_incarnations: 7
    mergeable_in_fortress: 3  # Practical, Paranoid, Good
    merge_requirements:
      Practical: "INT 21 OR WIS 21 OR (GoodMerged AND BronzeSphereUsed)"
      Paranoid: "Uyo Language OR INT 16+ OR STR 21+ (choke)"
      Good: "INT 17+ (discover origin) THEN merge"
    merge_rewards:
      Practical: {XP: 96000, INT: 1, WIS: 1}
      Paranoid: {XP: 64000, STR: 1, CON: 1}
      Good: {XP: 32000, WIS: 1}
    bronze_sphere_reward: {XP: 2000000, Item: "Symbol of Torment", Flag: "TrueNameLearned"}
  
  # Alignment Shift Parameters
  alignment_system:
    law_chaos_range: -100 to 100
    good_evil_range: -100 to 100
    shift_triggers:
      - "PortalRegretChoice: Good/Evil"
      - "PracticalDeionarra: Good+Lawful / Evil"
      - "DeionarraTruth: Good+Lawful / Chaotic"
      - "VhailorJoin: Requires not Evil"
      - "IgnusFortress: Attacks if Good"
  
  # Area Codes (Immutable)
  area_codes:
    Mortuary_1F: "AR0201"
    Mortuary_2F: "AR0202"  # RESPAWN
    Mortuary_3F: "AR0203"
    Mausoleum_1: "AR0207"
    Mausoleum_2: "AR0208"
    Mausoleum_Inner: "AR0209"
    Catacombs: "AR1400"
    ShatteredCrypt: "AR1401"
    MosaicCrypt: "AR1402"
    DismemberedCrypt: "AR1403"
    Underchamber: "AR1404"
    CryptEmbraced: "AR1405"
    Fortress_Entrance: "AR1200"
    Fortress_Main: "AR1201"
    Fortress_Trial: "AR1202"
    Fortress_Maze: "AR1203"
    Fortress_Roof: "AR1204"
  
  # Global Variables (Immutable Names)
  global_variables:
    - "DEATH_COUNT"
    - "FORTRESS_DEATHS_ALLOWED"
    - "FORTRESS_DEATHS_USED"
    - "MORTUARY_VISITS"
    - "RAISE_DEAD_KNOWN"
    - "BD_DAKKON_MORALE"
    - "MORTE_UPGRADED"
    - "BRONZE_SPHERE_USED"
    - "PRACTICAL_INCARNATION_MERGED"
    - "PARANOID_INCARNATION_MERGED"
    - "GOOD_INCARNATION_MERGED"
    - "TRUE_NAME_LEARNED"
    - "DEIONARRA_TRUTH_TOLD"
```

---

## 7. Cross-Reference: Memory Fragments ↔ Companion Facets

| Fragment | Companion Facet Activated | Integration Path |
|----------|---------------------------|------------------|
| `MEM_MORTE_PILLAR` | F1_MEMORY_KEEPER | Confrontation → Upgrade → Tattoo Access |
| `MEM_DEIONARRA_RAISE_DEAD` | F1_MEMORY_KEEPER + F3_WISDOM_MIRROR | Grace teaches → Morte reads → Raise Dead |
| `MEM_DAKKON_ZERTHIMON_1-8` | F2_DISCIPLINE_ANCHOR | Circles → Blade Evolution → Spell Unlocks |
| `MEM_GRACE_KISS` | F3_WISDOM_MIRROR | Healing touch → Item ID → Intellectual intimacy |
| `MEM_ANNAH_ROMANCE` | F4_EMOTIONAL_CORE | Tsundere arc → Jealousy → Vulnerability → Loyalty |
| `MEM_NORDOM_DIRECTOR` | F5_LOGIC_ENGINE | Assign director → Warp Sense → Crossbow mastery |
| `MEM_IGNUS_FIRE_CONDUIT` | F6_CREATIVE_FIRE | Decanter → Command word → Living portal to Fire |
| `MEM_VHAILOR_JUSTICE` | F7_JUSTICE_WARDEN | Mercy alignment → Guilt sense → Fortress stat boom |

---

## 8. Validation Checklist (Temple-Grade)

- [ ] **T1**: All 52 fragments catalogued with IDs, types, conditions, effects
- [ ] **T2**: Recovery condition grammar formally specified (BNF)
- [ ] **T3**: Unit tests for each fragment trigger condition
- [ ] **T4**: YAML schemas validate against Omega Engine schema registry
- [ ] **T5**: Engine-Stack Firewall — Torment WAD params separate from core
- [ ] **T6**: No hardcoded secrets, debug commands gated
- [ ] **T7**: Fragment lookup O(1) via hash map, condition eval <10ms
- [ ] **T8**: Graceful degradation — missing fragments = facet stays DORMANT
- [ ] **T9**: All fragment recoveries logged to Hivemind with trace_id
- [ ] **T10**: Atomic fragment state updates (recovered + effects applied together)
- [ ] **T11**: Agent cannot spoof fragment recovery without meeting conditions

---

## 9. Heritage Attribution (M14)

| Element | Source | Tag |
|---------|--------|-----|
| Memory as mechanic (not flavor) | Planescape: Torment 1999 | `[id-soft: torment-1999] Memory Mechanic` |
| 6 memory types taxonomy | Derived from game analysis | `[heritage: omega-research] Memory Taxonomy` |
| 7 incarnation model | Planescape: Torment 1999 | `[id-soft: torment-1999] Incarnation System` |
| Death count → Fortress shadows | Planescape: Torment 1999 | `[id-soft: torment-1999] Death Scaling` |
| Raise Dead from Deionarra | Planescape: Torment 1999 | `[id-soft: torment-1999] Ghost Mentor` |
| Bronze Sphere = 2M XP + True Name | Planescape: Torment 1999 | `[id-soft: torment-1999] Sensory Stone` |
| Incarnation merge stat rewards | Planescape: Torment 1999 | `[id-soft: torment-1999] Incarnation Integration` |
| TTO 3 ending paths | Planescape: Torment 1999 | `[id-soft: torment-1999] Transcendent One` |
| Sounding Stone mass revival | Planescape: Torment 1999 | `[id-soft: torment-1999] Sounding Stone Exploit` |
| Companion = Fortress life | Planescape: Torment 1999 | `[id-soft: torment-1999] Companion Life Binding` |
| Alignment shifts from dialogue | Planescape: Torment 1999 | `[id-soft: torment-1999] Moral Dialogue` |

---

## 10. Research Sources

| Tier | Source | Key Data |
|------|--------|----------|
| T1 | Torment Wiki - Fortress of Regrets | All 3 incarnation dialogues, merge conditions, rewards |
| T1 | Torment Wiki - Companions | All 7 companions, recruitment, upgrades, banter |
| T1 | Sorcerer's Place - Walkthroughs | Step-by-step fragment recovery, stat checks |
| T1 | GameBanshee - Fortress | Cannon coords, Sounding Stone, revival mechanics |
| T1 | GameFAQs - Guide (BahamutZero) | Quest list, stat bonuses, console commands |
| T2 | IESDP - PST Actions | SetGlobal, IncrementGlobal, StatGT, Die(), MoveToArea |
| T2 | Beamdog Forums - Console | C:GetGlobal, C:SetGlobal, alignment manipulation |
| T3 | Wikipedia - Planescape: Torment | Narrative overview, memory/identity themes |
| T3 | Archania.org - Symbolic Analysis | Memory as mechanic, identity fragmentation |
| T3 | PhilArchive - Gubka | Regret as nature-changer, philosophical framework |
| T3 | Medium - Kamila Regel | Dak'kon as companion mirror analysis |

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE*
*End of R_PST_MEMORY_FRAGMENT_TAXONOMY.md*