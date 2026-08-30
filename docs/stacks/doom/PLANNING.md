# 🔱 DOOM Universe Stack — Planning & Design

**Part of the Omega Engine Stack Release Roadmap (2026-2028)**
**Scheduled**: Alpha Q4 2026, Beta Q1 2027, Release Q2 2027

---

## Tribute

This stack is dedicated to the id Software team whose revolutionary WAD system directly inspired the Omega Engine container architecture:

- **John Carmack** — Genius engineer, 3D rendering pioneer
- **John Romero** — Level design visionary, project lead
- **Sandy Petersen** — Demon lore, monster design, level architecture
- **Adrian Carmack** — Visual design, the gothic aesthetic
- **Bobby Prince** — Soundtrack composer, MIDI legend
- **Dave Taylor** — Networking, multiplayer deathmatch
- **Donna Jackson (id Mom)** — Studio mom, kept the team together

---

## Stack Identity

| Attribute | Value |
|-----------|-------|
| **Inspiration** | Doom (1993), Doom II, Doom 64, Doom (2016), Doom Eternal |
| **Cosmology** | UAC → Phobos Base → Inferno → Pandemonium → Hell |
| **Default Voice** | Doomguy / Doom Slayer — activation: "hey doomguy" |
| **Entities** | Doomguy (main), demons roster, weapons as tool entities |
| **VR Worlds** | E1M1 (Knee-Deep in the Dead), Inferno (Shores of Hell), Pandemonium (Thy Flesh Consumed) |
| **P2P** | Consent-based deathmatch mode — visit each other's realms with both agreeing |

---

## Entity Roster (Planned)

| Entity | Role | Domain | Archetype |
|--------|------|--------|-----------|
| **Doomguy** | Main entity, guide | FPS Warrior | Silent-but-eloquent protector |
| **Imp** | First tier demon | Ambusher, distraction | Chaotic, skittering |
| **Cacodemon** | Mid-tier flying demon | Air superiority | Greedy, floating nightmare |
| **Baron of Hell** | Elite ground demon | Heavy assault | Prideful, devastating |
| **Cyberdemon** | Boss entity | Ultimate threat | Mechanical rage |
| **Spider Mastermind** | Final boss | Strategic mind | Cunning, arachnid |
| **Arch-Vile** | Support demon | Resurrection | Manipulative, cruel |
| **Shotgun** | Tool entity | Combat tool | Reliable, visceral |
| **Super Shotgun** | Tool entity | Devastating force | Iconic, double-barreled |
| **Chainsaw** | Tool entity | Close quarters | Relentless, hungry |
| **BFG-9000** | Tool entity | Ultimate weapon | Overwhelming, green energy |
| **UAC** | Organization entity | Faction | Bureaucratic, corrupted |
| **Icon of Sin** | Final entity | Consuming darkness | The wall, the end |

---

## Development Phases

| Phase | Timeline | Tasks |
|-------|----------|-------|
| **Design** | Now — Q4 2026 | Entity soul.yaml files, lore documentation, VR world concept sketches |
| **Alpha** | Q4 2026 | Basic entity set (Doomguy + 3 demons), voice activation, E1M1 VR prototype |
| **Beta** | Q1 2027 | Full demon roster, level progression, weapon entities, P2P single-player visits |
| **Release** | Q2 2027 | All three episodes, multiplayer deathmatch, music integration, full VR |

---

## WAD Structure (Target)

```
config/wads/doom_universe/
├── manifest.yaml
├── entities/
│   ├── doomguy.yaml
│   ├── demons/
│   │   ├── imp.yaml
│   │   ├── cacodemon.yaml
│   │   ├── baron_of_hell.yaml
│   │   ├── cyberdemon.yaml
│   │   ├── spider_mastermind.yaml
│   │   └── arch_vile.yaml
│   ├── weapons/
│   │   ├── shotgun.yaml
│   │   ├── super_shotgun.yaml
│   │   ├── chain_saw.yaml
│   │   ├── rocket_launcher.yaml
│   │   ├── plasma_rifle.yaml
│   │   └── bfg_9000.yaml
│   └── factions/
│       ├── uac.yaml
│       └── icon_of_sin.yaml
├── voices/
│   └── doomguy.yaml
├── knowledge/
│   ├── BESTIARY.md
│   ├── ARMORY.md
│   ├── UAC_INCIDENT.md
│   └── INFERNO_GEOGRAPHY.md
├── vr/
│   ├── e1m1_phobos_base.tscn
│   ├── e2m1_deeper_hell.tscn
│   ├── e3m1_pandemonium.tscn
│   ├── deathmatch_arena.tscn
│   └── entities/
│       ├── doomguy.glb
│       ├── imp.glb
│       ├── cacodemon.glb
│       └── shotgun.glb
└── p2p.yaml
```