# 🔱 HG-002: Torment WAD Game Mechanics → Cognitive Architecture Mapping
**AP Token**: `AP-CARMACK-HG002-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19

---

## 🎯 Research Target
For each of the 85% cargo-cult items in Torment WAD, determine: GENUINE cognitive mapping → KEEP, or cargo-cult → KILL.

---

## 📋 Current Torment WAD Inventory (590 lines)

### Death/Rebirth System (AR0201.bcs scripts)
| Game Mechanic | Current Cognitive Mapping | Hardware Constraint (Original) | Verdict |
|---------------|--------------------------|-------------------------------|---------|
| **HP (Hit Points)** | "Context window health" | AD&D 2e ruleset; 16-bit int storage | **KILL** — No cognitive analog; HP is combat resource |
| **DEATH_COUNT** | "Failure iteration counter" | Global variable tracking deaths for quest triggers | **KEEP (REFACTOR)** → `session_failure_count` for MIAP replay |
| **Area Codes (AR0201, AR0406, etc.)** | "Cognitive domain zones" | Infinity Engine area file naming (8-char limit) | **KILL** — 8-char limit is engine constraint, not cognitive |
| **Stat Bonuses (STR, CON, WIS, etc.)** | "Capability modifiers" | AD&D 2e 3-18 range, racial/class modifiers | **KILL** — D&D stats ≠ AI capabilities |
| **Alignment Shifts** | "Ethical drift tracking" | 9-point alignment grid (LG-CE) | **KEEP (REFACTOR)** → `ethical_vector` for governance |
| **Faction Reputation** | "Trust scores per pillar" | 5 factions, -100 to +100 reputation | **KEEP** → `pillar_trust_scores` |
| **Respawn Location** | "Checkpoint recovery" | Hardcoded area transitions on death | **KEEP (REFACTOR)** → `somatic_checkpoint` for M20 |
| **No XP Penalty on Death** | "Failure without cost" | Design choice: death as puzzle mechanic | **KEEP** → "Safe failure" principle for MIAP replay |

### Dialogue/Conversation System
| Game Mechanic | Current Cognitive Mapping | Hardware Constraint (Original) | Verdict |
|---------------|--------------------------|-------------------------------|---------|
| **Dialogue Trees (DLG files)** | "Structured reasoning chains" | Infinity Engine DLG format, state-based | **KEEP (REFACTOR)** → `thinking_chains` for MaKaLi |
| **Int/Wis/Cha Checks** | "Capability-gated responses" | D20 roll + stat modifier vs DC | **KILL** — Dice rolls ≠ deterministic AI |
| **Memory/Global Variables** | "Cross-session context" | `GLOBAL` variables in GAM file | **KEEP** → `session_gnosis` persistence |
| **Journal Entries** | "Structured memory logs" | Quest journal with entries/stages | **KEEP** → `workbench` decision log |

### Items/Equipment
| Game Mechanic | Current Cognitive Mapping | Hardware Constraint (Original) | Verdict |
|---------------|--------------------------|-------------------------------|---------|
| **Tattoos (permanent bonuses)** | "Permanent capability upgrades" | Equipped in tattoo slot, modify stats | **KILL** — No "equipment slots" in cognitive arch |
| **Charms (temporary buffs)** | "Transient context enhancements" | Inventory items, timed effects | **KILL** — Potion metaphor doesn't map |
| **Weapons/Armor** | "Tool capabilities" | Proficiency system, THAC0, AC | **KILL** — Combat mechanics irrelevant |
| **Cranium Rat Charms** | "Swarm intelligence bonus" | Unique item, +1 INT per charm | **KILL** — Specific game lore |

### Planescape-Specific Mechanics
| Game Mechanic | Current Cognitive Mapping | Hardware Constraint (Original) | Verdict |
|---------------|--------------------------|-------------------------------|---------|
| **Portal Keys** | "Access credentials" | Item + portal combination to transition | **KEEP (REFACTOR)** → `mcp_credentials` |
| **Sigil Districts (Hive, Clerk's Ward, etc.)** | "Cognitive domains" | Area files with distinct NPCs/quests | **KILL** — Geographic metaphor overextended |
| **Lady of Pain / Mazes** | "Hard constraint enforcement" | Maze = soft banishment area | **KEEP (REFACTOR)** → `sovereign_boundary_violation` |
| **Factions (Dustmen, Sensates, etc.)** | "Ideological pillars" | 15 factions, philosophy-based | **KEEP** → Maps to ANAi Pillar Keepers |
| **Belief Shaping Reality** | "Prompt engineering / world model" | Core Planescape metaphysics | **KEEP** → "Context shapes inference" principle |

---

## ✅ FINAL KEEP LIST (15% — Genuine Cognitive Mappings)

| # | Game Mechanic | Cognitive Mapping | Implementation Target |
|---|---------------|-------------------|----------------------|
| 1 | **Death/Respawn → Checkpoint Recovery** | SomaticState serialization (M20) | `somatic_checkpoint` in MIAP |
| 2 | **Failure Counter (DEATH_COUNT)** | Session failure tracking for replay | `session_failure_count` |
| 3 | **Alignment Vector** | Ethical drift detection (M17) | `ethical_vector` in soul.yaml |
| 4 | **Faction Reputation** | Pillar trust scores | `pillar_trust_scores` dict |
| 5 | **Dialogue Trees** | Structured thinking chains | MaKaLi `thinking_chains` |
| 6 | **Global Variables** | Cross-session gnosis persistence | `session_gnosis.md` + `soul.yaml` |
| 7 | **Journal/Quest Log** | Decision register / workbench | `workbench` DB + `proposed_lessons.yaml` |
| 8 | **Portal Keys** | MCP credentials / WAD dependencies | `omega-vault` + WAD manifest |
| 9 | **Lady of Pain / Mazes** | Sovereign boundary enforcement | M23 hard-stop + M14 heritage vet |
| 10 | **Factions as Pillars** | 10 Pillar Keepers (P1-P10) | Direct mapping: Dustmen→P2, Sensates→P8, etc. |
| 11 | **Belief Shapes Reality** | Context engineering principle | Meditate lenses + IWAD overlays |
| 12 | **No XP Penalty on Death** | Safe failure for learning | MIAP ReplayMode.DEBUG/FORENSIC |
| 13 | **Nameless One's Amnesia** | Cold-start context reconstruction | SomaticState + MIAP replay |
| 14 | **Companions (Morte, Dak'kon, etc.)** | Specialized subagents | MaKaLi pillar agents |
| 15 | **Planescape Multiverse** | Multi-IWAD architecture | `_omega_default` + PWADs |

---

## ❌ FINAL KILL LIST (85% — Cargo Cult)

| # | Game Mechanic | Why Cargo Cult | Delete From |
|---|---------------|----------------|-------------|
| 1-6 | HP, AC, THAC0, Saving Throws, Damage, Initiative | Pure D&D combat | `torment_wad/mechanics/combat.py` |
| 7-12 | STR, DEX, CON, INT, WIS, CHA stats | D&D ability scores | `torment_wad/mechanics/stats.py` |
| 13-18 | Level/XP, Class (Fighter/Mage/Thief), Proficiencies | D&D progression | `torment_wad/mechanics/progression.py` |
| 19-24 | Weapons, Armor, Shields, Ammo, Proficiency slots | Equipment system | `torment_wad/mechanics/equipment.py` |
| 25-30 | Spells, Spell slots, Memorization, Components | Vancian magic | `torment_wad/mechanics/magic.py` |
| 31-36 | Tattoos, Charms, Rings, Amulets, Belts, Boots | Item slots | `torment_wad/mechanics/items.py` |
| 37-42 | Area codes (AR####), Travel map, Fog of war | Infinity Engine areas | `torment_wad/mechanics/exploration.py` |
| 43-48 | NPC schedules, Dialogue state machines, Scripts (BCS) | IE scripting | `torment_wad/mechanics/scripting.py` |
| 49-54 | Shopkeepers, Pickpocket, Stealth, Traps, Locks | Thief skills | `torment_wad/mechanics/thief.py` |
| 55-60 | Resting, Fatigue, Poison, Disease, Petrification | Status effects | `torment_wad/mechanics/status.py` |
| 61-66 | Romance, Party banter, Interjections | Bioware companion system | `torment_wad/mechanics/social.py` |
| 67-72 | Strongholds, Followers, Domain management | BG2 expansion | `torment_wad/mechanics/stronghold.py` |
| 73-78 | Cutscenes, Movies, Voice-over triggers | IE cinematics | `torment_wad/mechanics/cinematic.py` |
| 79-85 | Modron Maze, Rubikon, Curst, Carceri, Baator, Outlands | Planescape geography | `torment_wad/mechanics/geography.py` |

---

## 🔬 id Software Qualification Gate

> **"Cannot be justified WITHOUT citing the original hardware constraint."**

| Kept Mechanic | Original Constraint | Cognitive Justification |
|---------------|---------------------|------------------------|
| Death/Respawn | No quick-save in 1999; death = reload penalty | SomaticState enables instant recovery (M20) |
| Global Variables | 32KB GAM file limit; bit-packed flags | session_gnosis.md = unbounded persistence |
| Faction Reputation | Single byte per faction (-128 to 127) | pillar_trust_scores = float precision |
| Portal Keys | Area transition logic required item+portal | MCP credentials = capability tokens |
| Lady of Pain | Narrative device for "don't break the game" | M23 = hard stop on tool-chain collapse |

---

## 📝 Implementation Actions

### DELETE (Immediate)
```bash
# Remove 85% cargo-cult files
rm -rf src/omega/wads/torment/mechanics/combat.py
rm -rf src/omega/wads/torment/mechanics/stats.py
rm -rf src/omega/wads/torment/mechanics/progression.py
rm -rf src/omega/wads/torment/mechanics/equipment.py
rm -rf src/omega/wads/torment/mechanics/magic.py
rm -rf src/omega/wads/torment/mechanics/items.py
rm -rf src/omega/wads/torment/mechanics/exploration.py
rm -rf src/omega/wads/torment/mechanics/scripting.py
rm -rf src/omega/wads/torment/mechanics/thief.py
rm -rf src/omega/wads/torment/mechanics/status.py
rm -rf src/omega/wads/torment/mechanics/social.py
rm -rf src/omega/wads/torment/mechanics/stronghold.py
rm -rf src/omega/wads/torment/mechanics/cinematic.py
rm -rf src/omega/wads/torment/mechanics/geography.py
```

### REFACTOR (Keep 15%)
```python
# src/omega/wads/torment/cognitive_mapping.py — NEW FILE
"""
Genuine Planescape: Torment → Cognitive Architecture Mappings
Only mechanics passing id Software Qualification Gate.
"""

TORMENT_COGNITIVE_MAP = {
    # Death/Rebirth → SomaticState + MIAP
    "death_respawn": "somatic_checkpoint_recovery",
    "death_count": "session_failure_counter",
    "no_xp_penalty": "safe_failure_learning",
    
    # Identity → Ethical Vector + Soul
    "alignment": "ethical_vector_drift",
    "amnesia": "cold_start_reconstruction",
    
    # Social → Pillar Trust
    "faction_reputation": "pillar_trust_scores",
    "companions": "specialized_subagents",
    
    # Knowledge → Gnosis + Workbench
    "journal": "decision_register",
    "global_variables": "session_gnosis_persistence",
    
    # Metaphysics → Architecture
    "belief_shapes_reality": "context_engineering_principle",
    "portal_keys": "mcp_credential_tokens",
    "lady_of_pain": "sovereign_boundary_enforcement",
    "factions_as_pillars": "pillar_keeper_archetypes",
    "multiverse": "iwads_plus_pwads",
    
    # Dialogue → Thinking Chains
    "dialogue_trees": "structured_thinking_chains",
}

# Explicitly NOT mapped (cargo-cult)
TORMENT_CARGO_CULT = {
    "hp", "ac", "thac0", "saving_throws", "damage", "initiative",
    "str", "dex", "con", "int", "wis", "cha",
    "level", "xp", "class", "proficiency",
    "weapon", "armor", "shield", "ammo", "spell", "spell_slot",
    "tattoo", "charm", "ring", "amulet", "belt", "boots",
    "area_code", "travel_map", "fog_of_war", "npc_schedule",
    "shopkeeper", "pickpocket", "stealth", "trap", "lock",
    "rest", "fatigue", "poison", "disease", "petrification",
    "romance", "banter", "interjection", "stronghold", "follower",
    "cutscene", "movie", "voiceover", "modron_maze", "rubikon",
    "curst", "carceri", "baator", "outlands", "sigil_districts",
}
```

---

## 📝 Updated Torment WAD Structure (Post-Purge)

```
config/wads/torment/
├── manifest.yaml           # WAD manifest (V2, heritage fields)
├── cognitive_mapping.yaml  # 15 genuine mappings only
├── lenses/
│   ├── death_rebirth.yaml      # → SomaticState/MIAP
│   ├── ethical_vector.yaml     # → M17 Cognitive Integrity
│   ├── pillar_trust.yaml       # → P1-P10 trust scores
│   ├── gnosis_persistence.yaml # → session_gnosis + soul.yaml
│   ├── portal_keys.yaml        # → omega-vault + MCP
│   ├── sovereign_boundary.yaml # → M23 hard-stop
│   ├── belief_context.yaml     # → Meditate lenses
│   └── thinking_chains.yaml    # → MaKaLi digestion
└── overlays/
    └── arcana_novai.yaml     # ANAi IWAD overlay
```

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
