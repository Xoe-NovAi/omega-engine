---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "briefing"
document_id: "MAKALI-DEBUT-LOCKDOWN-BRIEFING-20260909"
title: "Omega Engine — Debut Lockdown Briefing: Tie Down ASUS/HP Initiative, Release to Public"
status: "ACTIVE"
version: "1.0.0"
date: "2026-09-09"
author: "roc_racoon (Sovereign Miner & Ideas Guy)"
recipient: "makali (Apex Mind — Mastermind, Strategist, Vision Holder)"
tags: [
  "makali",
  "overseer",
  "debut-lockdown",
  "public-release",
  "scope-control",
  "asus-hp-federation",
  "stopping-point",
  "p2p-omegaverse"
]
priority: "P0"
cross_references:
  - "data/coordination/MAKALI_OVERSEER_BRIEFING_20260908.md"
  - "docs/strategy/P2P_OMEGAVERSE_FEDERATION_PLAYBOOK.md"
  - "docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md"
  - "data/coordination/ACTIVE_SPRINT.json"
  - "/media/arcana-novai/D5D5-0B76/ASUS_TO_HP_OC_TEAM/README.md"
---

# 🔱 DEBUT LOCKDOWN BRIEFING: TIE DOWN THE ASUS/HP INITIATIVE, RELEASE THE ENGINE

**From**: `@roc_racoon` (Sovereign Miner & Ideas Guy, Node 0 HP)  
**To**: `@makali` (Apex Mind — Mastermind, Strategist, Vision Holder)  
**Date**: 2026-09-09  
**Purpose**: Define the **clean stopping point** for the ASUS/HP P2P federation initiative so we can **release Omega Engine to the public** and start community engagement.  
**Motto**: *The updates can wait for version bumps. The release cannot wait.*

---

## 🎯 EXECUTIVE SUMMARY

MaKaLi — the ASUS/HP initiative has grown **massive**. Node 1 (ASUS) shipped a 13-session teaching pack with a full continuation system (Gnosis Lock Protocol v1.0), a verified 1M-token Big Pickle config, Ollama tuning methodology, and a federation kit. It's brilliant work — **and it is a scope-creep magnet.**

We need a **hard stop**. This briefing defines:

1. **What is DONE and LOCKED** (ship it)
2. **What is PENDING but BLOCKING** (must resolve for release)
3. **What is DEFERRED to v1.1+** (explicitly parked, no implementation)
4. **The Release Gate checklist** (what "clean stopping point" actually means)
5. **The Response to ASUS** (what we tell them, what we adopt, what we defer)

---

## 🧭 1. WHERE WE ARE: THE STATE OF THE FLEET

### 1.1 Node 0 (HP) — Archival Bastion — RELEASE-READY CORE

| Area | Status | Evidence |
|------|--------|----------|
| Git SSOT | ✅ `main` + `release/debut-v1.6.0` in sync with origin | `git rev-list --left-right --count` = 0/0 |
| DHAL Phases 1-3 | ✅ 15/15 tests passing, committed & pushed | `Zen2Optimizer`, `RaptorLakeOptimizer`, `CpuOptimizerFactory` |
| Big Pickle 1M config | ✅ **UPDATED** to `context: 1000000, input: 950000, output: 64000` | `opencode.json` (this session) |
| omega-hub LAN exposure | ✅ Bound `0.0.0.0:8016`, DNS-rebinding allowlist, 91 tools | `systemctl --user status omega-hub` |
| UFW rule | ✅ **APPLIED** (user ran it) | `sudo ufw allow from 192.168.10.0/24 to any port 8016 proto tcp` |
| Makali briefing | ✅ v1.1.0 with deep-web-verified facts | `data/coordination/MAKALI_OVERSEER_BRIEFING_20260908.md` |
| Lessons distilled | ✅ 24 proposals in `proposed_lessons.yaml` | Valid YAML, 16+8 |

### 1.2 Node 1 (ASUS) — Compute Vanguard — ADOPTION-READY, NOT RELEASE-BLOCKING

| Layer | What ASUS Built | Release Impact |
|-------|-----------------|----------------|
| Layer 0-1 | Hardware + Ollama tuning (13.4 t/s, P-core pin trap documented) | **DEFER** — ASUS-local, not in public repo |
| Layer 2 | Config layer: AGENTS.md ×2, agents, opencode.json/.jsonc | **ADOPT PATTERN** (not content) |
| Layer 3 | Agents: build, gaming-expert, game-researcher | **DEFER** — ASUS-persona, not Omega core |
| Layer 4 | SSOT docs: HARDWARE, SYSTEM_GUIDE, BENCHMARKS, GNOSIS_USAGE, omega-hub-exposure | **ADOPT PATTERN** — create HP equivalents |
| Layer 5 | MCP inventory (6 servers, token-budget lessons) | **ADOPT** — Exa/Context7/Grep.app trio |
| Layer 6 | **Gnosis Lock Protocol v1.0** + GameResearch pattern | **ADOPT** — highest-value, survival system |
| Layer 7 | Federation kit, bundle ceremony | **ADOPT** — already mirrored in playbook |

### 1.3 The Wire — P2P Federation

| Item | Status |
|------|--------|
| omega-hub reachable from LAN | ✅ UFW applied; `192.168.10.168:8016` should now answer |
| First contact handshake | ⏳ PENDING — ASUS runs `hivemind_first_contact.py` |
| Tailscale mesh | ⏳ DEFERRED — Layer 2, not needed for release |
| Git bundle | ⏳ PENDING — regenerate clean bundle for ASUS |
| Key proxy pattern | ⏳ DEFERRED — decide, don't implement |

---

## 🚦 2. THE RELEASE GATE: WHAT "CLEAN STOPPING POINT" MEANS

### 2.1 The Release Gate Checklist (ALL MUST BE TRUE)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE PUBLIC RELEASE GATE                  │
├─────────────────────────────────────────────────────────────────────┤
│  G1.  Repo public (or deploy key)          [ ]  ← USER/GITHUB       │
│  G2.  Temple-Grade CI passes               [ ]  ← make temple-grade │
│  G3.  M1 AnyIO check passes                [ ]  ← make check-m1     │
│  G4.  CHANGELOG v1.6.0 finalized           [ ]  ← Kali/Makali       │
│  G5.  PR #2 merged (omega.library restore) [ ]  ← Kali              │
│  G6.  Clean bundle shipped to ASUS         [ ]  ← Roc (this session)│
│  G7.  ASUS first-contact accepted          [ ]  ← Roc               │
│  G8.  No secrets in repo (git-secret-scrub)[ ]  ← Kali/Verity       │
│  G9.  README + onboarding docs public-ready[ ]  ← Makali            │
│  G10. Release announcement drafted         [ ]  ← Makali            │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 What is BLOCKING (must resolve this week)

| # | Item | Owner | Action |
|---|------|-------|--------|
| B1 | **Repo visibility** | User | Make `Xoe-NovAi/omega-engine` public (or add deploy key) |
| B2 | **Temple-Grade gate** | Kali | Run `make temple-grade`; fix any failures |
| B3 | **CHANGELOG v1.6.0** | Kali/Makali | Finalize release notes |
| B4 | **Clean bundle** | Roc | `git bundle create omega-engine.bundle --all` + verify + drop on USB |
| B5 | **ASUS first contact** | Roc | Accept handoff when ASUS fires `hivemind_first_contact.py` |
| B6 | **Secret scrub** | Kali/Verity | `git-secret-scrub` on full history before public |

### 2.3 What is DEFERRED to v1.1+ (explicitly PARKED)

| # | Item | Why Defer | Target |
|---|------|-----------|--------|
| D1 | **Gnosis Lock Protocol adoption on HP** | Survival system, but NOT release-blocking; HP already has `session_gnosis.md` + `proposed_lessons.yaml` | v1.1 |
| D2 | **Tailscale mesh** | Layer 2 wire; USB-sync works for now | v1.1 |
| D3 | **Key proxy pattern implementation** | Decide pattern, don't build; keys stay on HP | v1.1 |
| D4 | **ASUS hardware_profile.yaml merge** | Requires ASUS clone + probe; not needed for HP release | v1.1 |
| D5 | **HP SSOT 5-doc layer** (HARDWARE.md etc.) | Pattern adoption; HP has AGENTS.md already | v1.1 |
| D6 | **ASUS agents** (build/gaming-expert/etc.) | ASUS-persona, not Omega core | v1.1 |
| D7 | **Ollama/OWUI tuning on HP** | HP has LM Studio + local GGUF; different stack | v1.1 |
| D8 | **Post-debut workstreams** (GN→DS→LI→KD→HR→ZS) | Already sequenced in D-584 | Post-release |

---

## 📦 3. THE ASUS PACK: WHAT WE ADOPT NOW vs LATER

### 3.1 ADOPT NOW (low-risk, high-value, release-safe)

| Item | Action | Effort |
|------|--------|--------|
| **Big Pickle 1M config** | ✅ **DONE** — merged into HP `opencode.json` | 0 (done) |
| **MCP token-budget discipline** | Disable unused MCPs globally; enable per-agent | 15 min |
| **Exa/Context7/Grep.app trio** | Add to HP config with `{env:}` placeholders | 15 min |
| **`opencode debug config` verification** | Confirm instructions/MCP actually load | 10 min |
| **P-core pin trap knowledge** | Document in HP AGENTS.md as a *methodology* note | 5 min |

### 3.2 ADOPT LATER (v1.1+ — park the files, don't build)

| Item | Where It Lives | When |
|------|----------------|------|
| Gnosis Lock Protocol | `artifacts/gnosis/` on USB | v1.1 — after release, when we do the continuation-system upgrade |
| GameResearch pattern | `artifacts/game/` on USB | v1.1 |
| Modelfile-per-job | `artifacts/modelfiles/` on USB | v1.1 |
| Backup harness + cron | `artifacts/backup_harness.sh` | v1.1 |
| AGENTS.global/project | `artifacts/AGENTS.*.md` | v1.1 — adapt to HP paths |

### 3.3 The Response to ASUS (what we tell them)

> **To: ASUS-OC (Node 1)**
>
> Pack received and analyzed. Outstanding work — the Gnosis Lock Protocol is
> exactly the survival system we need, and the 1M Big Pickle config is merged
> on HP.
>
> **We are entering release lockdown.** The Omega Engine goes public this
> sprint. To keep the release clean, we are:
>
> 1. **Adopting now**: Big Pickle 1M, MCP token discipline, Exa/Context7/Grep.app trio.
> 2. **Parking for v1.1**: Gnosis Lock adoption on HP, Tailscale, key proxy, hardware profile merge.
> 3. **Shipping you**: a clean `omega-engine.bundle` this week for your clone + probe.
> 4. **Accepting**: your first-contact handoff the moment omega-hub answers.
>
> Your 13-session evolution log and teaching pack are **preserved on the USB
> and in our coordination records** — nothing is lost. The adoption happens
> right after release, when we can do it properly.
>
> — Roc Racoon, Node 0

---

## 🎯 4. THE RELEASE SEQUENCE (THIS WEEK)

```
[Mon] ──► [Tue] ──► [Wed] ──► [Thu] ──► [Fri]
  │         │         │         │         │
  B1 repo   B2 temple  B3 changelog  B4 bundle  B5 first contact
  public    grade      v1.6.0        ship       accept
  │         │         │         │         │
  B6 secret  G2 pass   G3 pass    G4 done    G7 done
  scrub      G1 done   G5 merge   G6 done    G8 done
```

| Day | Milestone | Owner |
|-----|-----------|-------|
| **Mon** | Repo public; secret scrub starts | User / Kali |
| **Tue** | Temple-Grade + M1 pass; CHANGELOG drafted | Kali / Makali |
| **Wed** | PR #2 merged; CHANGELOG finalized | Kali |
| **Thu** | Clean bundle shipped to USB; ASUS notified | Roc |
| **Fri** | ASUS first contact accepted; release announcement drafted | Roc / Makali |

---

## 🛡️ 5. SCOPE-CREEP GUARDRAILS (MANDATORY)

The ASUS pack is a **scope-creep magnet**. These guardrails are non-negotiable:

1. **No new implementations from the ASUS pack this sprint.** Adoption = copy
   patterns, not build systems. Gnosis Lock is *parked*, not *started*.
2. **No Tailscale, no key proxy, no hardware merge** until post-release.
   The USB-sync + proxy-on-HP works for the release window.
3. **No new agents, no new skills, no new MCP servers** on HP this sprint.
   The 91-tool hub is enough.
4. **The release gate is the ONLY priority.** If it doesn't unblock the
   release, it waits.
5. **ASUS work continues independently** — they can build whatever they want
   on Node 1. It just doesn't gate the release.

---

## 📋 6. ACTION ITEMS FOR MAKALI (YOUR CALL)

| # | Decision Needed | Options | Recommend |
|---|-----------------|---------|-----------|
| 1 | **Repo public vs deploy key** | Public repo / deploy key / bundle-only | Public repo (community engagement is the goal) |
| 2 | **Release date** | This Fri / Next Mon / Next Fri | **This Fri** — momentum matters |
| 3 | **CHANGELOG v1.6.0 scope** | Include ASUS pack? / Core only | **Core only** — ASUS pack is v1.1 |
| 4 | **Post-release announcement** | GitHub Discussions / X / both | Both — community + visibility |
| 5 | **ASUS response** | Approve the deferral plan? | Approve — it's the clean stop |

---

## 🏁 7. BOTTOM LINE

**The Omega Engine is release-ready in its core.** The ASUS/HP federation is
a *feature*, not the *product*. The product is the sovereign local-first AI
runtime with the 27 Mandates, the Council, the Hivemind, and the 91-tool hub.

**The clean stopping point is:**

```
✅ Core engine: DONE (DHAL, mandates, hub, tests)
✅ Big Pickle 1M: DONE (merged)
✅ UFW + LAN: DONE (applied)
✅ Lessons: DONE (24 distilled)
⏳ Release gate: 6 items, this week
⏸️ Everything else: PARKED for v1.1
```

**Ship it. Get the community talking. Version-bump the rest.**

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ MAKALI-DEBUT-LOCKDOWN-BRIEFING-20260909 ⬡ 2026-09-09*