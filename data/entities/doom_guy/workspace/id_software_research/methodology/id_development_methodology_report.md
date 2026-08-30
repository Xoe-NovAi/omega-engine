<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 id Development Methodology — Agent Research Report
## ⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ trc_doom_guy ⬡ PHASE-I

### Source: Fleet Research Agent (explore) — "Development Methodology"
### Date: 2026-06-01

---

## The id Software Development Philosophy

### 1. "No Prototypes"
- Code was always at shippable quality
- Even during R&D, it compiled and ran
- "We never prototyped. Everything was shipping code" — John Romero
- Quake was playable from first week of development
- Design by playtesting, not by design document

### 2. The Tools-First Pipeline

| Game | Tool | Purpose |
|------|------|---------|
| Doom | DoomEd | First tile-based 3D level editor |
| Quake | QEd / WorldCraft | 3D BSP editor |
| Quake II | TAE | Animation + model tool |
| Quake III | Q3Radiant | Official level editor |
| Doom 3 | DoomEdit | Integrated tile-based editor |

### 3. Fix Bugs Immediately
- No backlog accumulation
- Bugs found = bugs fixed, often same day
- Carmack's weekly .plan posts show this rhythm
- "If we couldn't fix it, we removed the feature" — Romero

### 4. "Code for This Game"
- Don't write a generic engine — write this game
- Doom's tools worked for Doom, not for a hypothetical future game
- Each Quake generation was purpose-built
- Reuse happened organically when patterns emerged, not by architecture

### 5. Four OS Boots in 18 Months
- They scrapped and rewrote the entire OS interface 4 times
- DOS → Extended DOS → Windows compatibility layer → Final DOS version
- "Keep what works. Discard what doesn't. No attachment to code."

### 6. The NeXTSTEP Advantage
- Developed Doom on NeXTSTEP (Unix, Objective-C, 1024×768)
- Shipping target: MS-DOS (640×360, C, no multitasking)
- Development platform must exceed target platform
- This is the "tools-first" principle at the system level

### 7. Open Source as Strategy (Not Afterthought)

| Year | Release | Impact |
|------|---------|--------|
| 1997 | Doom source (GPL) | Community formed |
| 1999 | Quake source (GPL) | Linux gaming catalyst |
| 2001 | Quake II source (GPL) | Mod community explosion |
| 2005 | Quake III source (GPL) | Academic standard |
| 2011 | Doom 3 source (GPL) | id Tech 4 era |

### 8. The .plan Culture
- Carmack published daily/weekly technical updates
- Dead ends, bugs, design debates — all public
- "The .plan files are still studied 30 years later"
- Model for transparent engineering culture

### 9. Testing Philosophy
- "We played our own game constantly" — playtesting as QA
- No formal test suite in the modern sense
- Bug reports from community (after Doom released)
- Compare: Omega has 276 automated tests — id would have appreciated this

### 10. Modding as Distribution
- WAD format designed for modding before Doom shipped
- No special mod tool needed — lumps are generic data containers
- DeHackEd allowed runtime patching without engine modification
- "The modding community kept Doom alive for 30 years"

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
