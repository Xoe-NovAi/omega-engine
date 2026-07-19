# 🔱 R_PST_DEATH_REBIRTH_MECHANICS.md
**AP Token**: `AP-PST-DEATH-REBIRTH-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-07-19
**Purpose**: Comprehensive technical specification of Planescape: Torment's death/rebirth mechanics for Omega Engine WAD translation.

---

## Executive Summary (L1)

Planescape: Torment implements a **unique death-as-progression mechanic** where the Nameless One's immortality is not a reload-state but a narrative-coded system tracked via global variables, area transitions, and companion state. The system comprises:

1. **Mortuary Respawn Loop** (AR0201-AR0203) — Primary resurrection point
2. **Death Counter Global** — Tracks total deaths, scales Fortress shadows
3. **Companion-Death Binding** — Each companion = 1 Fortress life
4. **Memory Fragment Recovery** — Death triggers specific memory unlocks
5. **Fortress of Regrets Terminal Phase** — Limited deaths = game over

This document provides the complete technical specification for implementing this system in the Omega Engine's WAD architecture.

---

## 1. Mortuary Respawn System (AR0201-AR0203)

### 1.1 Area Architecture

| Area Code | Floor | Description | Key Coordinates |
|-----------|-------|-------------|-----------------|
| **AR0201** | 1st Floor | Portal room, Deionarra memorial, Vaxis false zombie | Portal: X=600 Y=1025 (Bone Charm key) |
| **AR0202** | 2nd Floor | **Player spawn point** — 8 rooms clockwise, zombie workers | Zombie 782 (Preparation Key), Soego (gate) |
| **AR0203** | 3rd Floor | Cremation, skeleton workers, 4 giant skeletons (Tome of Bone & Ash) | Central Chamber: 4 giant skeletons |

### 1.2 Respawn Trigger Conditions

The Nameless One respawns at **AR0202 (Mortuary 2nd Floor)** when:

```plaintext
IF
  Die()
  !GlobalGT("DEATH_COUNT","GLOBAL",15)  -- Not in Fortress terminal phase
  !InParty("Morte") OR Morte not in party (always true, Morte is permanent)
THEN
  RESPONSE #100
    MoveToArea("AR0202")  -- 2nd floor spawn
    SetGlobal("DEATH_COUNT","GLOBAL",<increment>)
    ApplySpellRES("RESURRECTION_EFFECT",Myself)  -- Visual effect
    Heal(Myself,999)  -- Full heal on respawn
END
```

### 1.3 Death Count Global Variable

**Variable**: `DEATH_COUNT` (GLOBAL scope)

| Death Count | Effect |
|-------------|--------|
| 1-4 | Standard Mortuary respawn |
| 5 | Fortress Main Hall: +1 Shadow wave |
| 10 | Fortress Main Hall: +2 Shadow waves |
| 15 | Fortress Main Hall: +3 Shadow waves (max) |
| >15 | No additional shadows (cap) |

**Shadow Scaling Formula**:
```
Shadows = MIN(3, FLOOR(DEATH_COUNT / 5))
XP per Shadow = 10,000
```

### 1.4 Mortuary Re-entry Methods

| Method | Condition | XP Reward |
|--------|-----------|-----------|
| **Death Respawn** | Die closer to Mortuary than other bind points | 0 |
| **Pox Smuggle** | Talk to Pox (AR0200, X=600 Y=1025) | 0 |
| **Soego Gate** | Convince Soego (AR0202) to open front gate | 500 |
| **Portal Escape** | Bone Charm + Portal (AR0201) | 500 (Deionarra hint) |

---

## 2. Fortress of Regrets Death System (AR1200-AR1204)

### 2.1 Area Codes & Structure

| Area | Name | Description | Death Limit |
|------|------|-------------|-------------|
| **AR1200** | Fortress Entrance | Deionarra, portal from Mortuary | Unlimited |
| **AR1201** | Main Hall | 7 rooms, 4 cannons, shadows scale with DEATH_COUNT | **Limited** |
| **AR1202** | Trial of Impulse | Crystal room, Ignus/Vhailor fight, Sounding Stone | **Limited** |
| **AR1203** | Maze of Reflections | 3 Incarnations, Bronze Sphere, Deionarra | **NO DEATH** |
| **AR1204** | Fortress Roof | Transcendent One, companion bodies | **NO DEATH** |

### 2.2 Companion-Death Binding Mechanic

**Core Rule**: `Max_Deaths_In_Fortress = Party_Member_Count_At_Entry`

```plaintext
// On Fortress Entry (AR1200)
SetGlobal("FORTRESS_DEATHS_ALLOWED","GLOBAL",PartyMemberCount())
SetGlobal("FORTRESS_DEATHS_USED","GLOBAL",0)

// On Death in AR1201 or AR1202
IncrementGlobal("FORTRESS_DEATHS_USED","GLOBAL",1)
IF Global("FORTRESS_DEATHS_USED","GLOBAL") > Global("FORTRESS_DEATHS_ALLOWED","GLOBAL")
THEN
  GameOver()  -- Permanent death, no respawn
ELSE
  MoveToArea("AR1200")  -- Respawn at Fortress Entrance
  Heal(Myself,999)
END
```

### 2.3 Companion Death State on Fortress Roof

Upon reaching AR1204 (Fortress Roof):

```plaintext
// All companions (except Morte) are DEAD
// Morte: STATE_PRETENDING_DEAD (special flag)
// Transcendent One present

// Revival mechanic (requires Sounding Stone from AR1202):
IF HasItem("SOUNDING_STONE") AND Global("FORTRESS_SHADOWS_RELEASED","GLOBAL",0)
THEN
  // Can resurrect ALL companions, not just one
  // Bug in vanilla: only 1 companion unless Sounding Stone used
  // Fixed in Qwinn's Tweak Pack / EE Fixpack
END
```

### 2.4 Portal Opening Sequence (AR1201)

```plaintext
// 4 Ancient War Machines (Cannons) - any order
Cannon1: (1755,1800) -> Teleport to (950,2100)
Cannon2: (4460,2720) -> Teleport to (840,1000)
Cannon3: (2925,1990) -> Teleport to (2180,1050)
Cannon4: (3745,665)  -> Teleport to (3900,2940)

// After all 4 activated:
OpenPortal(3460,450)  // To AR1202 (Trial of Impulse)
```

---

## 3. Global Variable Registry

### 3.1 Core Death/Rebirth Variables

| Variable | Scope | Type | Description |
|----------|-------|------|-------------|
| `DEATH_COUNT` | GLOBAL | INT | Total deaths across entire game |
| `FORTRESS_DEATHS_ALLOWED` | GLOBAL | INT | Max deaths in Fortress (set on entry) |
| `FORTRESS_DEATHS_USED` | GLOBAL | INT | Deaths consumed in Fortress |
| `MORTUARY_VISITS` | GLOBAL | INT | Times entered Mortuary (any method) |
| `RAISE_DEAD_KNOWN` | GLOBAL | BOOL | Whether TNO learned Raise Dead from Deionarra |

### 3.2 Companion State Variables

| Variable | Scope | Type | Description |
|----------|-------|------|-------------|
| `BD_DAKKON_MORALE` | GLOBAL | INT | Dak'kon morale (0-20), affects blade |
| `BD_ANNAH_ROMANCE` | GLOBAL | INT | Annah romance track |
| `BD_GRACE_ROMANCE` | GLOBAL | INT | Grace romance track |
| `MORTE_UPGRADED` | GLOBAL | BOOL | Morte stats upgraded via Grace confrontation |
| `DAKKON_BLADE_FORM` | GLOBAL | INT | Zerth Blade form (0=Kinstealer, 1=Chained, 2=Streaming) |

### 3.3 Memory/Incarnation Variables

| Variable | Scope | Type | Description |
|----------|-------|------|-------------|
| `BRONZE_SPHERE_USED` | GLOBAL | BOOL | 2M XP + Symbol of Torment granted |
| `PRACTICAL_INCARNATION_MERGED` | GLOBAL | BOOL | +1 INT, +1 WIS, 96K XP |
| `PARANOID_INCARNATION_MERGED` | GLOBAL | BOOL | +1 STR, +1 CON, 64K XP |
| `GOOD_INCARNATION_MERGED` | GLOBAL | BOOL | +1 WIS, 32K XP |
| `TRUE_NAME_LEARNED` | GLOBAL | BOOL | From Bronze Sphere, enables TTO merge |
| `DEIONARRA_TRUTH_TOLD` | GLOBAL | BOOL | Alignment shift (Good/Lawful) |

---

## 4. Memory Fragment Recovery on Death

### 4.1 Death-Triggered Memories

Each death can trigger specific memory fragments based on location/context:

| Death Context | Memory Fragment | Variable Set |
|---------------|-----------------|--------------|
| First death (Mortuary wake) | "You have died before" | `FIRST_DEATH_MEMORY=1` |
| Death in Mortuary | Deionarra's ghost appears | `DEIONARRA_MET=1`, `RAISE_DEAD_KNOWN=1` |
| Death near Pharod | Bronze Sphere memory | `BRONZE_SPHERE_HINT=1` |
| Death in Catacombs | Severed arm / tattoos | `SEVERED_ARM_FOUND=1` |
| Death in Fortress | Incarnation echoes | `INCARNATION_ECHO_<N>=1` |
| Death with specific companion | Companion-specific memory | `<COMPANION>_DEATH_MEMORY=1` |

### 4.2 Memory Fragment Data Structure (Omega Engine)

```yaml
# For WAD translation: data/entities/nameless_one/memory_fragments.yaml
memory_fragments:
  - id: "death_first"
    trigger: "DEATH_COUNT == 1"
    type: "TRAUMA"
    content: "You wake on a cold slab. A floating skull reads your back."
    xp_reward: 0
    unlocks: ["MORTE_JOIN", "TATTOO_READ"]
    
  - id: "deionarra_raise_dead"
    trigger: "DEATH_COUNT >= 1 AND AREA == AR0202 AND !Global('RAISE_DEAD_KNOWN')"
    type: "KNOWLEDGE"
    content: "Deionarra teaches you to pull souls back from the void."
    xp_reward: 1000
    unlocks: ["ABILITY_RAISE_DEAD"]
    
  - id: "practical_incarnation_deception"
    trigger: "GLOBAL('PRACTICAL_INCARNATION_MERGED')"
    type: "BETRAYAL"
    content: "He lied to Pharod. He used Deionarra. He enslaved Dak'kon."
    xp_reward: 96000
    stat_bonuses: {INT: 1, WIS: 1}
    
  - id: "good_incarnation_origin"
    trigger: "GLOBAL('GOOD_INCARNATION_MERGED')"
    type: "REDEMPTION"
    content: "The first man. The sin. The choice of immortality to atone."
    xp_reward: 128000  # 96K + 32K
    stat_bonuses: {WIS: 1}
```

---

## 5. Companion Resurrection Mechanics

### 5.1 Raise Dead Ability (TNO Innate)

```plaintext
// TNO Special Ability: Raise Dead
// Usable 3x/day (scales with Priest level if dual-classed)
// Only works on CURRENT party members

ABILITY: RAISE_DEAD
  Target: Party member (DEAD state)
  Effect: Resurrect at 1 HP
  Condition: Target in party, not removed from party while dead
  Visual: Golden light, body reforms
  Sound: "RESURRECT"
```

### 5.2 Fortress Roof Mass Resurrection (Endgame)

```plaintext
// Requires: Sounding Stone (from AR1202) + Deionarra dialogue
// Tricks Transcendent One into leaving to check shadows

IF HasItem("SOUNDING_STONE") 
   AND Global("FORTRESS_SHADOWS_RELEASED","GLOBAL",1)
   AND InArea("AR1204")
THEN
  // All dead companions can be raised
  // Dak'kon bonus: If Zerthimon learned -> +2M XP, +1 STR, +3 DEX, +3 CON
  // Vhailor bonus: If "great injustice" -> +2M XP, +3 STR, DEX=25, CON=25
  // Morte: Always alive (pretending)
END
```

### 5.3 Companion Death Persistence

```plaintext
// If companion dies and is REMOVED from party:
// - Cannot be raised (permanent loss)
// - Equipment lost
// - Must reload save

// If companion dies and STAYS in party:
// - Raise Dead works (3x/day)
// - Healing items work
// - Regeneration (TNO, high-CON Dak'kon) works
```

---

## 6. Alignment Shifts from Death Choices

### 6.1 Portal Opening Regret (AR1200)

| Regret Choice | Alignment Shift |
|---------------|-----------------|
| Regret something bad happened | **Good** |
| Regret not doing more bad things | **Evil** |

### 6.2 Practical Incarnation Revelation

| Response | Alignment Shift |
|----------|-----------------|
| "She didn't have to die" | **Good**, **Lawful** |
| "It was necessary" | **Evil** |

### 6.3 Deionarra Truth

| Response | Alignment Shift |
|----------|-----------------|
| Tell truth about her death | **Good**, **Lawful** |
| Lie to comfort her | **Chaotic** (or neutral) |

---

## 7. Console/Script Commands for Testing

### 7.1 Death Count Manipulation

```bash
# Get current death count
C:GetGlobal("DEATH_COUNT","GLOBAL")

# Set death count (for testing Fortress scaling)
C:SetGlobal("DEATH_COUNT","GLOBAL",10)

# Force Fortress death limit
C:SetGlobal("FORTRESS_DEATHS_ALLOWED","GLOBAL",5)
C:SetGlobal("FORTRESS_DEATHS_USED","GLOBAL",0)
```

### 7.2 Memory/Incarnation Flags

```bash
# Grant all incarnation merges
C:SetGlobal("PRACTICAL_INCARNATION_MERGED","GLOBAL",1)
C:SetGlobal("PARANOID_INCARNATION_MERGED","GLOBAL",1)
C:SetGlobal("GOOD_INCARNATION_MERGED","GLOBAL",1)
C:SetGlobal("BRONZE_SPHERE_USED","GLOBAL",1)
C:SetGlobal("TRUE_NAME_LEARNED","GLOBAL",1)

# Force Morte upgrade
C:SetGlobal("MORTE_UPGRADED","GLOBAL",1)

# Max Dak'kon morale
C:SetGlobal("BD_DAKKON_MORALE","GLOBAL",20)
```

### 7.3 Area Teleport for Testing

```bash
# Mortuary 2nd Floor (respawn point)
C:MoveToArea("AR0202")

# Fortress Entrance
C:MoveToArea("AR1200")

# Fortress Roof (endgame)
C:MoveToArea("AR1204")

# Maze of Reflections
C:MoveToArea("AR1203")
```

---

## 8. Omega Engine WAD Implementation Specification

### 8.1 WAD Structure for Death/Rebirth System

```
config/wads/_omega_default/
├── systems/
│   ├── death_rebirth.yaml          # Core system definition
│   ├── memory_fragments.yaml       # Fragment definitions
│   └── fortress_mechanics.yaml     # Fortress-specific rules
├── areas/
│   ├── AR0201_mortuary_1f.area.yaml
│   ├── AR0202_mortuary_2f.area.yaml  # RESPAWN POINT
│   ├── AR0203_mortuary_3f.area.yaml
│   ├── AR1200_fortress_entrance.area.yaml
│   ├── AR1201_fortress_main.area.yaml
│   ├── AR1202_fortress_trial.area.yaml
│   ├── AR1203_fortress_maze.area.yaml
│   └── AR1204_fortress_roof.area.yaml
├── globals/
│   ├── death_count.global.yaml
│   ├── fortress_deaths.global.yaml
│   └── memory_flags.global.yaml
├── abilities/
│   ├── raise_dead.ability.yaml
│   ├── litany_of_curses.ability.yaml
│   └── skull_mob.ability.yaml
└── scripts/
    ├── mortuary_respawn.bcs.yaml
    ├── fortress_death_limit.bcs.yaml
    └── incarnation_merge.bcs.yaml
```

### 8.2 Death Rebirth System Definition (death_rebirth.yaml)

```yaml
# config/wads/_omega_default/systems/death_rebirth.yaml
system:
  id: "death_rebirth"
  version: "1.0.0"
  heritage: "[id-soft: torment-1999] Death/Rebirth System"
  
  respawn_points:
    primary:
      area: "AR0202"
      coordinates: {x: 1500, y: 1500}  # Mortuary 2nd floor center
      conditions:
        - "!GlobalGT('DEATH_COUNT','GLOBAL',15)"
        - "!InArea('AR1200','AR1201','AR1202')"
      effects:
        - "Heal(999)"
        - "IncrementGlobal('DEATH_COUNT','GLOBAL',1)"
        - "PlayEffect('RESURRECTION_VFX')"
    
    fortress:
      area: "AR1200"
      coordinates: {x: 3960, y: 2100}  # Deionarra location
      conditions:
        - "InArea('AR1201','AR1202')"
        - "GlobalLT('FORTRESS_DEATHS_USED','GLOBAL','FORTRESS_DEATHS_ALLOWED')"
      effects:
        - "Heal(999)"
        - "IncrementGlobal('FORTRESS_DEATHS_USED','GLOBAL',1)"
      failure:
        - "GameOver()"  # Permanent death
  
  death_scaling:
    fortress_shadows:
      formula: "MIN(3, FLOOR(Global('DEATH_COUNT') / 5))"
      xp_per_shadow: 10000
      max_shadows: 3
  
  companion_binding:
    fortress_lives: "PartyMemberCountAtEntry()"
    morte_exception: true  # Morte never truly dies
  
  memory_triggers:
    - trigger: "DEATH_COUNT == 1"
      fragment: "death_first"
    - trigger: "AREA == AR0202 AND !Global('RAISE_DEAD_KNOWN')"
      fragment: "deionarra_raise_dead"
    - trigger: "Global('PRACTICAL_INCARNATION_MERGED')"
      fragment: "practical_incarnation_deception"
    - trigger: "Global('GOOD_INCARNATION_MERGED')"
      fragment: "good_incarnation_origin"
```

### 8.3 Memory Fragment Schema (memory_fragments.yaml)

```yaml
# config/wads/_omega_default/systems/memory_fragments.yaml
fragments:
  - id: "death_first"
    tier: "TRAUMA"  # TRAUMA | KNOWLEDGE | BETRAYAL | REDEMPTION | LOVE | SACRIFICE
    trigger_condition: "Global('DEATH_COUNT') == 1"
    narrative: "You wake on a cold slab. A floating skull reads the tattoos on your back."
    xp_reward: 0
    unlocks: ["MORTE_JOIN", "TATTOO_READ"]
    soul_echo: "The first death you remember. But not the first death you died."
    
  - id: "deionarra_raise_dead"
    tier: "KNOWLEDGE"
    trigger_condition: "Area('AR0202') AND !Global('RAISE_DEAD_KNOWN')"
    narrative: "Deionarra's ghost teaches you to call souls back from the void. Three times a day."
    xp_reward: 1000
    unlocks: ["ABILITY_RAISE_DEAD"]
    soul_echo: "Love persists beyond death. Even when memory fails."
    
  - id: "practical_incarnation_deception"
    tier: "BETRAYAL"
    trigger_condition: "Global('PRACTICAL_INCARNATION_MERGED')"
    narrative: "He lied to Pharod. He sacrificed Deionarra. He enslaved Dak'kon with a logic puzzle. He built the tomb beneath Sigil. He pried Morte from the Pillar."
    xp_reward: 96000
    stat_bonuses: {INT: 1, WIS: 1}
    soul_echo: "Pragmatism without conscience is not wisdom. It is cruelty wearing a mask of necessity."
    
  - id: "paranoid_incarnation_traps"
    tier: "TRAUMA"
    trigger_condition: "Global('PARANOID_INCARNATION_MERGED')"
    narrative: "He left the Dodecahedron Journal. He trapped the sensory stone. He trusts no one, not even himself. To merge, speak the Uyo language — or choke him with 21 Strength."
    xp_reward: 64000
    stat_bonuses: {STR: 1, CON: 1}
    soul_echo: "Paranoia is memory turned inward, eating its own tail."
    
  - id: "good_incarnation_origin"
    tier: "REDEMPTION"
    trigger_condition: "Global('GOOD_INCARNATION_MERGED')"
    narrative: "He was the first. He committed a sin that would damn him to the Hells. He asked Ravel for immortality to atone. But each death stole his memories, and the planes have been dying ever since."
    xp_reward: 128000
    stat_bonuses: {WIS: 1}
    soul_echo: "Regret can change the nature of a man. But only if he remembers what he regrets."
    
  - id: "bronze_sphere_true_name"
    tier: "KNOWLEDGE"
    trigger_condition: "Global('BRONZE_SPHERE_USED')"
    narrative: "The Bronze Sphere was a dead sensory stone holding the first incarnation's memories. Using it grants 2,000,000 XP, the Symbol of Torment, and your true name — though it is never spoken aloud."
    xp_reward: 2000000
    unlocks: ["SYMBOL_OF_TORMENT", "TRUE_NAME_LEARNED", "TTO_MERGE_OPTION"]
    soul_echo: "A name is not identity. But knowing it means you finally know who you were."
```

---

## 9. Heritage Attribution (M14)

| Mechanic | Source | Tag |
|----------|--------|-----|
| Death as progression (not failure) | Planescape: Torment 1999 | `[id-soft: torment-1999] Death as Progression` |
| Mortuary respawn hub | Planescape: Torment 1999 | `[id-soft: torment-1999] Mortuary Hub` |
| Companion = extra life (Fortress) | Planescape: Torment 1999 | `[id-soft: torment-1999] Companion Life Binding` |
| Shadow scaling with death count | Planescape: Torment 1999 | `[id-soft: torment-1999] Death-Count Scaling` |
| Incarnation merge = stat/XP rewards | Planescape: Torment 1999 | `[id-soft: torment-1999] Incarnation Integration` |
| Bronze Sphere = 2M XP + true name | Planescape: Torment 1999 | `[id-soft: torment-1999] Sensory Stone Memory` |
| Raise Dead 3/day innate | Planescape: Torment 1999 | `[id-soft: torment-1999] Innate Resurrection` |
| Deionarra teaches Raise Dead | Planescape: Torment 1999 | `[id-soft: torment-1999] Ghost Mentor` |
| Alignment shifts from death choices | Planescape: Torment 1999 | `[id-soft: torment-1999] Moral Death Choices` |
| Fortress portal: flesh + regret | Planescape: Torment 1999 | `[id-soft: torment-1999] Regret Portal` |

---

## 10. Validation Checklist (Temple-Grade T1-T11)

- [ ] **T1 Version Control**: All YAML files tracked in git with semantic versioning
- [ ] **T2 Documentation**: This document + inline YAML comments cover all mechanics
- [ ] **T3 Testing**: Unit tests for death count scaling, Fortress limit, memory triggers
- [ ] **T4 Code Quality**: BCS scripts compile without warnings (WeiDU/Infinity Engine)
- [ ] **T5 Architecture**: Engine-Stack Firewall respected — WAD contains no core engine code
- [ ] **T6 Security**: No hardcoded credentials, console commands gated behind debug mode
- [ ] **T7 Performance**: Global variable checks O(1), area transitions <100ms
- [ ] **T8 Resilience**: Graceful handling of missing globals (defaults to safe values)
- [ ] **T9 Observability**: Death events logged to Hivemind with trace_id
- [ ] **T10 Integrity**: Atomic global variable updates (SetGlobal + IncrementGlobal)
- [ ] **T11 Agent Security**: No agent can bypass Fortress death limit without debug mode

---

## 11. Research Sources

| Tier | Source | Key Data |
|------|--------|----------|
| T1 | Torment Wiki - Fortress of Regrets | Area codes, shadow scaling, portal mechanics, incarnation merges |
| T1 | Torment Wiki - Morte | Upgrade path, Pillar of Skulls origin, Raise Dead |
| T1 | Torment Wiki - Dak'kon | Zerth Blade forms, morale system, Unbroken Circle |
| T1 | GameBanshee - Fortress of Regrets | Cannon coordinates, Sounding Stone, companion revival |
| T1 | Sorcerer's Place Walkthrough | Step-by-step Fortress, Maze of Reflections dialogue |
| T2 | IESDP - BCS Format | Script structure, triggers, actions, global variables |
| T2 | IESDP - PST Actions | SetGlobal, IncrementGlobal, Die(), MoveToArea() |
| T2 | Beamdog Forums - Console Commands | C:GetGlobal, C:SetGlobal, C:MoveToArea |
| T3 | Wikipedia - Planescape: Torment | Narrative summary, death mechanics overview |
| T3 | Archania.org - Symbolic Analysis | Memory as mechanic, identity fragmentation |
| T3 | PhilArchive - Gubka "Regret Can Change Nature" | Philosophical framework for death/regret system |

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE*
*End of R_PST_DEATH_REBIRTH_MECHANICS.md*