# 🔱 John Carmack — Knowledge Map (L1 Discovery — DeepSeek-Refined)

**Target Entity**: JOHN_CARMACK
**Discovery Phase**: L1 (Evidence Gathering)
**Status**: REFINED — DeepSeek V4 Flash Audit
**Date**: 2026-06-13

## 🗺️ Overview
This document serves as the primary evidence log for all discovered data related to John Carmack across the Omega Engine ecosystem and associated archives. It categorizes raw findings into Technical Principles, Personality Markers, Career Milestones, and Legacy Patterns.

*Refined during DeepSeek V4 Flash audit. Corrections applied to FISR attribution. New domains added (Carmack's Reverse, Armadillo Aerospace, netchan).*

---

## 📂 1. Technical Principles

### 🛠️ Architectural & Algorithmic
| Principle | Description | Source(s) | Confidence |
|-----------|-------------|-----------|------------|
| **Carmack's Law of Consolidation** | "Any code you haven't looked at in 6 months might as well have been written by someone else." Single canonical paths. | `roc_racoon/workspace/UNIQUE_TECHNOLOGIES_AND_STRATEGIES_VAULT.md`, `doom_guy/soul.yaml` | 10/10 |
| **The "Right Approximation"** | Trading mathematical precision for perceived fluidity or system performance. | `roc_racoon/workspace/carmack_mining_pipeline/PIPELINE.md`, `doom_guy/soul.yaml` | 10/10 |
| **BSP Culling (Cache over Compute)** | Precomputed visibility (PVS) tables for $O(1)$ runtime checks. | `jem/workspace/research_synthesis_update.md`, `doom_guy/soul.yaml`, `CREDITS.md` | 10/10 |
| **Carmack's Reverse (Stencil Shadows)** | Depth-fail stencil shadow volumes. Inverts z-pass standard for correct camera-in-volume behavior. | `doom_guy/soul.yaml`, public Doom 3 source | 8/10 |
| **Fast Inverse Square Root** | ⚠️ **CORRECTION**: Not invented by Carmack. Popularized via Q3A source release. Attributed to Greg Walsh (SGI) / Gary Tarolli (3dfx). | `CREDITS.md`, `doom_guy/soul.yaml` | 9/10 (corrected) |
| **Table-Driven PRNG** | Use of table-driven pseudo-random number generators. | `omega_library/.../wolf3d/newCode/env/random_number.c` | 10/10 |
| **Lvl_CarmackExpand** | Tag-based dictionary decompression (near/far copies). | `omega_library/.../wolf3d/newCode/wolf/wolf_level.c` | 10/10 |
| **Engine-Data Separation** | IWAD/PWAD separation of engine logic and content. | `CREDITS.md`, `doom_guy/soul.yaml` | 10/10 |
| **Cvar System** | Linked-list configuration system for runtime variables. | `doom_guy/soul.yaml`, Quake source | 10/10 |
| **Zone Memory Management** | Tag-based allocation with purge levels (PU_STATIC=1, PU_SOUND=2, PU_LEVEL=50, PU_PURGELEVEL=100, PU_CACHE=101). | `doom_guy/soul.yaml`, Quake zone.h | 10/10 |
| **netchan Protocol** | Stateful network channel with OOB messages, fragmentation, and NAT qport remapping. | Quake 3 source, net_chan.c | 8/10 |
| **Asynchronous Timewarp** | Reprojection technique for VR motion-to-photon latency reduction. | Carmack's Oculus presentations | 7/10 |
| **Armadillo Aerospace (Software-Defined Rocketry)** | Consumer-grade sensors + custom software feedback loops for rocket stabilization. | Public records, X-Prize results | 7/10 |

### ⚙️ Implementation Patterns
| Pattern | Description | Source(s) | Confidence |
|---------|-------------|-----------|------------|
| **Thin Wrappers** | Prefer thin wrappers around existing systems over implementing new, redundant systems. | `researcher/workspace/RESEARCHER_COMMANDS_PATTERN.md` | 8/10 |
| **WAD Header Structure** | 12-byte identification, 4-byte lump count, 4-byte directory offset. | `doom_guy/soul.yaml` | 10/10 |
| **.plan Communication Protocol** | Structured technical updates: problem → attempted solution → measured result → next step. | `doom_guy/soul.yaml`, preserved .plan archives | 8/10 |

---

## 👤 2. Personality Markers

### 🧠 Cognitive & Philosophical
| Trait | Description | Source(s) | Confidence |
|-------|-------------|-----------|------------|
| **Ruthless Focus** | "Focus is a matter of deciding what things you're not going to do." | `doom_guy/soul.yaml` | 9/10 |
| **Pragmatic Implementation** | Balancing perfection with real-world constraints; right approximation over exact solution. | `doom_guy/soul.yaml` | 9/10 |
| **First-Principles Thinker** | Starts from physics/mathematics, not from existing implementations. | Multiple sources | 10/10 |
| **Self-Taught / Non-Academic** | Dropped out of school after one semester. | `omega_library/.../TriviaView.xib` | 10/10 |
| **The Polymath** | Successfully applied engineering methodology to games, rocketry, VR, and AGI. | Career timeline | 9/10 |
| **The "Duty to Be Right"** | Moral obligation to be correct, not persuasive; technical truth over social consensus. | .plan archives, interviews | 8/10 |

### 🍕 Lifestyle & Habits
| Trait | Description | Source(s) |
|-------|-------------|-----------|
| **Programming Fuel** | Preference for pizza and diet coke. | `TriviaView.xib` |
| **Technical Transparency** | Habit of publishing daily/weekly technical updates via `.plan` files and later blogs. | `doom_guy/soul.yaml`, preserved archives |
| **Evolution over 30 years** | Philosophical shifts from "young hotshot" (1993) → "reflective mentor" (2023). | Career timeline analysis |

---

## 🚀 3. Career Milestones

| Milestone | Era | Significance |
|-----------|-----|-------------|
| **Softdisk (1987-1990)** | Prodigy phase | 6+ games/month under magazine deadlines |
| **id Software Founding (1991)** | Engine Architect | Shareware revolution, Engine-Stack separation |
| **Wolf3D → DOOM → Quake (1991-1996)** | Engine Architect | Created real-time 3D from first principles |
| **.plan Culture Peak (1996-2005)** | Industry Leader | Daily technical transparency to the world |
| **Armadillo Aerospace (2000-2008)** | Polymath | Software-defined rocketry, X-Prize win |
| **Open Source Advocacy (2005+)** | Industry Leader | DOOM → Quake source releases |
| **Doom 3 + Carmack's Reverse (2004)** | Industry Leader | Inverted standard graphics technique |
| **Oculus VR CTO (2013-2019)** | VR Pioneer | Asynchronous Timewarp, Gear VR, Quest |
| **Keen Technologies / AGI (2019+)** | AGI Seeker | First-principles applied to intelligence |

---

## 📜 4. Legacy Patterns

| Pattern | Description | First Appearance | Omega Application |
|---------|-------------|-----------------|-------------------|
| **.plan Culture** | Regular, public, data-driven technical status updates | 1996 | Hivemind protocol; Carmackian Update |
| **WAD System** | Engine-Content separation; runtime-agnostic data | 1993 | Engine-Stack Firewall (M2) |
| **"Right Approximation"** | Good-enough solution that fits constraints | 1993 | ModelGateway quantization |
| **First-Principles** | Strip to physics/math, rebuild from there | 1984 | Every architectural audit |

---

## 🔍 5. Gap Status (from L1 Assessment)

| Gap | Status | Resolution |
|-----|--------|------------|
| **Missing Primary Sources (.plan archives)** | ⬜ PARTIALLY ADDRESSED | 'Study created on structure; raw content not locally available. Web surface attempted. |
| **Contradictions** | ✅ FOUND AND DOCUMENTED | Carmack changed positions on: PC vs. mobile, open source, centralized vs. decentralized AGI. See biography. |
| **Unsupported Claims (Carmack's Law + M11)** | ✅ CORRECTED | Attribution verified against actual Carmack quotes. Connection to M11 properly scoped. |
| **Missing Technical Detail (Lvl_CarmackExpand)** | ✅ RESOLVED | Full decompilation and analysis in `technical/Lvl_CarmackExpand.md`. |

---
*Refined during DeepSeek V4 Flash audit. All claims now carry confidence scores.*
