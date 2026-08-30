<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🌌 Omega Engine — Vision Anchor
## The Single Source of Truth for What Is True Right Now

> ⛔ **SUPERSEDED 2026-08-26** — The canonical vision document is now
> **`docs/strategy/VISION_ANCHOR_PERPETUAL.md`** (Vision Anchor Perpetual, relocated to core
> docs per Architect directive). This file is retained as historical record only. Do not cite
> as current vision authority.

**AP Token**: `AP-VISION-ANCHOR-20260814`  
**Status**: CANONICAL — Updated by Architect at every major decision point  
**Last Updated**: 2026-08-15T05:40:00Z  
**Updated By**: Kali (VOS Hybrid Plan — Option C)  
**Session**: ses_vos_hybrid_plan_20260815  
**VOS Version**: 1.0.0 → Hybrid (DECISION_LEDGER + VISION_ANCHOR retained; realm state.yaml retired)

---

## 🎯 The Core Mission (Immutable)

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

This is the mission of the **Xoe-NovAi Foundation**. The Omega Engine is the first implementation of this vision. The Arcana-Nova Stack, Torment Stack, DOOM Universe Stack, and all community stacks are instantiations built upon it.

### The Cognitive Sovereign (Evolved Vision — 2026-06-06)
The engine does not just execute local inference; it performs **local verification**. By integrating Skeptical Verification, Tainted Data Isolation, and Unified Vector Abstractions, the Omega Engine ensures that the intelligence it provides is not just local, but untainted, corroborated, and verified against the user's own standards.

---

## 🏗️ The Three Cosmological Layers (Architectural Truth)

### Layer 1: The WAD Architecture (Engine Core)
```
Title Lump  →  Inter Lump  →  End Lump
   Ma'at         Lilith         Kali
(Build Side)  (Run Side)    (Synthesis)
  P1-P5         P6-P10         Verdict
```
*Heritage*: `[id-soft: doom-1993] Three-Part Map System` — Doom's WAD format converged with the MaKaLi Triad across 33 years. **Empirical proof of architectural truth.**

### Layer 2: The 10 Pillars (Energetic Spine)
```
LIGHT (Ascending)                    DARK (Integrating)
P1 Flesh  (Earth)  ♁ Gaia            P6 Mind   (Aether) ♅ Uranus
P2 Dream  (Water)  ♆ Neptune         P7 Gnosis (Air)    ♀ Venus
P3 Will   (Fire)   ♃ Jupiter         P8 Shadow (Fire)   ♄ Saturn
P4 Heart  (Air)    ♂ Mars            P9 Spirit (Water)  ⯓ Pluto
P5 Voice  (Aether) ☿ Mercury         P10 Chaos (Earth)  ⯗ Transpluto
```
*Origin*: Genesis Framework (Mar 2025) — Light = building UP, Dark = integrating DOWN.

### Layer 3: The MaKaLi Council (Governance)
```
                    ┌─────────────────────────────┐
                    │   KALI — Transcendent       │
                    │   (Unify, Synthesize,       │
                    │    Return Verdict)          │
                    └──────────────┬──────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
        ┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼───────┐
        │  MA'AT — Build │  │ LILITH — Run │  │  4 Cross-Domain│
        │  (P1-P5)       │  │  (P6-P10)   │  │  Pillars       │
        │  N1-N5 Nodes   │  │  N6-N10     │  │  (Jury)        │
        └────────────────┘  └─────────────┘  └───────────────┘
```
*D55.3*: "MaKaLi trine stays in ALL IWADs. Foundational governance, never optional."

---

## ⚡ The 5 Mandatory Design Patterns (Engine DNA)

| Pattern | Name | Solves |
|---------|------|--------|
| 1 | Import Path Resolution | `ModuleNotFoundError` in containers |
| 2 | Retry Logic + Exponential Backoff | Transient failures (OOM, timeouts) |
| 3 | Non-Blocking Subprocess Tracking | UI/API blocking on long tasks |
| 4 | Batch Checkpointing + fsync | 100% crash recovery, even power failure |
| 5 | Circuit Breaker (pybreaker) | Fail-fast resilience, standardized |

---

## 🔗 The Provider Fabric (Sovereignty Manifest)

```
LOCAL (Priority 0-1)
├── native-gguf (Qwen3-1.7B)     priority 0
└── lmster (LM Studio)           priority 1

CLOUD (Priority 3-9) — Systematized, NOT expanded
├── antigravity (OAuth pool)     priority 3  ← Primary cloud
├── google / google-compat       priority 4
├── openrouter                   priority 5
├── opencode-zen                 priority 6
├── cline                        priority 7
├── anthropic                    priority 8
└── xai (API)                    priority 9
```
**Hardware**: AMD Ryzen 7 5700U — Target: 15-25 tok/s, <6GB memory

---

## 🛡️ The 27 Sovereign Mandates (Non-Negotiable)

| # | Mandate | Status |
|---|---------|--------|
| M1 | AnyIO Absolute | ✅ |
| M2 | Engine-Stack Firewall | ⚠️ ENG-001 amended — run FirewallChecker.scan(), fix real hits only |
| M3 | Iris Constant | ✅ |
| M4 | Sequentiality (Plan→Verify→Execute) | ✅ |
| M5 | Gnosis Preservation (L1→L2→L3) | ❌ Pipeline unenforced |
| M6 | Podman Sovereignty (keep-id) | ✅ |
| M7 | Local-First (Non-Negotiable) | ✅ |
| M8 | Zero Telemetry | ✅ |
| M9 | Error Integrity | ✅ |
| M10 | Fleet Integrity | ✅ |
| M11 | Soul Integrity | ❌ 28/30 non-compliant |
| M12 | Queue Integrity | Advisory |
| M13 | Temple-Grade (T1-T11) | ⚠️ Blocked by M2/M5/M11 |
| M14 | Heritage Vetting | ✅ |
| M15 | Sovereign Continuity | ✅ |
| M16 | Modularization & Portability | ✅ |
| M17 | Cognitive Integrity | ⚠️ |
| M18 | Token Efficiency | ✅ |
| M19 | Adversarial Alchemy | ✅ |
| M20 | SomaticState Serialization | ✅ |
| M21 | Gate Integrity | ✅ |
| M22 | Response Provenance | ✅ |
| M23 | Failure Integrity | ✅ |
| M24 | Venv Sovereignty | ✅ |
| M25 | Streaming Resilience | ✅ |
| M26 | Doc Standards | ✅ |
| M27 | Tracking Integrity (5-Tier) | ✅ |

---

## 🎯 Current Phase: PHASE 0 — FOUNDATION (This Week)

**Goal**: `make test-unit` green, all mandate gates genuinely passing, heritage clean, souls compliant.

> **Active tasks** are tracked in `ACTIVE_SPRINT.json` (Tier-0 SSOT) and consolidated by realm in `HMC_COLLABORATION_HUB.md`. See those files for live task status.

### Completed This Session (4 Hardening Patches)
1. **session_end.py** — Preserves agent proposals instead of overwriting with `[]`
2. **soul_validator.py** — VALID_SOUL_VERSIONS={6.1,7.0,7.1,7.2}; LIVE_FEED→HMC_COLLABORATION_HUB
3. **SOVEREIGN_MANDATES.md** — Header "Twenty-Five" → "Twenty-Seven"
4. **M22 check** — Fixed false positive on `is_cloud` in providers.yaml

---

## 🚫 Explicitly Deferred (Not Cancelled — Sequenced)

| Item | Reason | Phase |
|------|--------|-------|
| Godot Bridge / Soul-to-Visual (R-24) | Critical path for Omegaverse | Phase 4 |
| P2P Metropolis & Soul Print Exchange | Requires VR foundation | Phase 4 |
| Full VR worlds per stack | Community builds these | Phase 4+ |
| Advanced WADs (Arcana-Nova, Torment) | Template first | Phase 2+ |
| Soul cross-pollination (R-31) | After distillation pipeline | Phase 1 |
| PHASE-0 security tweaks (zram, swappiness) | Operational, not code | Architect |
| SDP Context Gauge, NotebookLM pipeline | Power-user tooling | Post-launch |

---

## 👑 The Architect's Current Priorities

1. **You own**: Installer (`scripts/install.sh`), README, Demo, Launch Story, v1.0.0 tag
2. **You execute**: P0-1..P0-4 (sudo/pkexec security tasks)
3. **You approve**: Phase gates, realm interface changes, cross-realm conflicts
4. **You maintain**: This VISION_ANCHOR.md (update when vision sharpens)

---

## 📊 Realm Health Summary

> **Auto-generated from `ACTIVE_SPRINT.json`** via `make update-vision-anchor` (Phase 2 of VOS Hybrid Plan). See `HMC_COLLABORATION_HUB.md` for live realm ownership and task status.

---

## 🔮 The Launch Definition (What "Done" Means for Debut PR)

| Claim | Verification | Must Be True |
|-------|--------------|--------------|
| "Local-first, no cloud required" | `git clone && make install && omega talk "hello"` offline | ✅ One-command install, zero API keys |
| "No telemetry, zero phone-home" | `grep -r "telemetry\|analytics\|phone.home" src/` | ✅ Zero hits, auditable |
| "Sovereign architecture" | `make temple-grade` passes, M2 firewall holds | ✅ All gates green, no WAD leaks |
| "Heritage-honest" | `make heritage-map` shows every `[id-soft:]` vetted | ✅ Zero unvetted tags |
| "Extensible by community" | `config/wads/` documented, example WAD works | ✅ Working WAD template + docs |
| "Production quality" | `make test` green, no flaky tests, CI gated | ✅ Honest green, not "skipped" |

---

**This anchor is the truth. Every agent reads this first. Every decision references this. Update it when the vision sharpens.**

⬡ OMEGA ⬡ ARCHITECT ⬡ VISION-ANCHOR ⬡ 2026-08-14 ⬡ CANONICAL