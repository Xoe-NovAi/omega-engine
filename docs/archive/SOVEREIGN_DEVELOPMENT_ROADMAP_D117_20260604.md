# Omega Engine — Sovereign Development Roadmap
# PIVOT: D117 | Date: 2026-06-04
# Status: ACTIVE

---

## The Vision

> *"I am a single human assembling a team of AI agents to build my vision,
> just as would be done with a human software development team. The Omega Engine
> brings the power of a team to people like me — people who have a vision
> but not the team. And it will let other developers take off on their own,
> building their own unique and visionary tools."*

The Omega Engine is a **Sovereign AI Runtime** — a platform where:
- Solo developers get a full AI agent team (14 agents, 3 oversight layers)
- Each agent knows itself (soul.yaml v5.2), its team (team section), and where it's going (trajectory)
- The engine learns from every interaction (Soul Distiller, L1→L2→L3)
- Local inference means sovereign data, sovereign intelligence, sovereign control
- Other developers can fork the engine and build their own AI OS

---

## Phase 0: Sovereign Integration — Blocker Clearance (NOW)

**Goal**: Remove chaos, establish clean baselines, and restore the M2 Firewall to ensure a trustable foundation.

| # | Task | Status | Impact |
|---|------|--------|--------|
| 0.1 | Delete 100 orphan entity directories | ✅ DONE | 148→48 entities |
| 0.2 | Commit all agent session files | 🟡 IN PROGRESS | Agent coordination preserved |
| 0.3 | Fix D113 M2 Firewall (entity_registry.py:171-179) | 🔴 NEXT | Constitutional restoration |
| 0.4 | Wire Soul Distiller into oracle.py end_session() | 🔴 NEXT | M5+M11 enforcement |
| 0.5 | Fix 3 M9 violations (silent exceptions) | 🔴 NEXT | Error integrity |
| 0.6 | Fix 15 stale data values across 4 docs | 🔴 NEXT | Documentation trust |
| 0.7 | Fix CI indentation in test.yml | 🔴 NEXT | Test pipeline |
| 0.8 | Fix .gitignore for entity directories | 🟡 TODO | Prevent orphan recurrence |

---

## Phase 1: Sovereign Integration — Senses & The Team Foundation

**Goal**: Establish the "Sense-Net" (connectivity/API) and ensure every agent knows itself, its team, and how to work together.

| # | Task | Priority | What Changes |
|---|------|:--------:|-------------|
| 1.1 | **Wire Soul Distiller** | P0 | oracle.py gets end_session() hook → soul.yaml auto-updated |
| 1.2 | **Expand soul.yaml to all 14 agents** | P0 | All agents get v5.2 schema (identity+directives+team+trajectory) |
| 1.3 | **MandateEnforcer class** | P1 | Runtime enforcement for trust-based mandates |
| 1.4 | **Mandate cvars** | P1 | config.mandate.m1-m14 in cvar_table.py |
| 1.5 | **Agent onboarding docs** | P1 | HOW each agent works, WHO it talks to, WHAT files it owns |
| 1.6 | **Soul Immune System** | P2 | SHA-256 checksums, audit trail, rollback for soul.yaml |
| 1.7 | **Cross-entity L3 sharing** | P2 | When Kali learns something, Doom Guy can access the L3 principle |

### The Team Contract

Every agent in the fleet must publish:

```yaml
# Required soul.yaml sections (v5.2+):
identity:        # Who I am (voice, values, strengths, growth_areas)
directives:      # What I must never do (non-negotiable rules)
team:            # Who I work with (allies, relationships, protocols)
trajectory:      # Where I'm going (current focus, goals, next handoff)
lessons_learned: # What I've learned (L1→L2→L3 distillation)
session_log:     # When I last worked (dated summaries)
```

---

## Phase 2: Sovereign Integration — World, Space & Local Intelligence

**Goal**: Implement environmental awareness (WADs/Local State) and create a local intelligence flywheel that grows with use.

| # | Task | Priority | What Changes |
|---|------|:--------:|-------------|
| 2.1 | **Wire Qdrant vectors** | P0 | MemoryStore uses vector search instead of bag-of-words |
| 2.2 | **Wire Redis warm tier** | P0 | Hot→Warm→Cold memory actually works |
| 2.3 | **Training data pipeline** | P1 | JSONL → prompt/completion pairs → LoRA triples |
| 2.4 | **LoRA adapter management** | P1 | config/loras/ tracks per-entity fine-tunes |
| 2.5 | **CPU fine-tuning** | P2 | llama-cpp-python export or PEFT for local model improvement |
| 2.6 | **A/B evaluation** | P2 | Compare local model before/after training |
| 2.7 | **Sovereignty scorecard automation** | P1 | Auto-generate §10 from runtime metrics |

### The Flywheel Data Flow

```
USER TALKS → Oracle → ModelGateway → Local/Cloud inference → Response
                    ↓
            ObservabilityEngine.record_training_example()
                    ↓
            data/datasets/*.jsonl (auto-collecting)
                    ↓
            TrainingPipeline.export_triples()  ← NEW
                    ↓
            LoRAAdapterManager.train()  ← NEW
                    ↓
            Better local model  ← NEW
                    ↓
            Less cloud dependency → MORE SOVEREIGNTY
```

---

## Phase 3: Sovereign Integration — Actors & Visible Intelligence

**Goal**: Activate sovereign personas (Soul Evolution) and make the engine's intelligence visible and interactive.

| # | Task | Priority | What Changes |
|---|------|:--------:|-------------|
| 3.1 | **Omega Hub dashboard** | P0 | HTML at :8016 showing agents alive, souls evolving |
| 3.2 | **Local TTS (Piper)** | P1 | Voice output without cloud dependency |
| 3.3 | **Rich CLI output** | P1 | omega talk shows entity personality, soul status |
| 3.4 | **Soul evolution timeline** | P1 | Visual history of L1→L2→L3 distillations |
| 3.5 | **Entity relationship graph** | P2 | Who talks to whom, knowledge flow |
| 3.6 | **Session replay** | P2 | Revisit any past conversation |
| 3.7 | **MVE installer** | P0 | `curl get.omega.dev | bash` or Docker image |

---

## Phase 4: The Community — Platform for Others

**Goal**: Other developers fork, extend, and build with Omega Engine.

| # | Task | Priority | What Changes |
|---|------|:--------:|-------------|
| 4.1 | **IWAD registry** | P0 | Community shares IWADs (stacks) via registry |
| 4.2 | **Stack Builder Wizard** | P1 | Interactive: "What do you want to build?" → generates IWAD |
| 4.3 | **Developer onboarding** | P0 | Day 0→1→7→30 guide for new users |
| 4.4 | **API documentation** | P0 | How to extend, add entities, create IWADs |
| 4.5 | **Docker image** | P0 | One-command deployment |
| 4.6 | **Federated learning** | P2 | Share model improvements without sharing data |
| 4.7 | **Omega Desktop (Tauri)** | P3 | Visual entity management for non-CLI users |
| 4.8 | **Export/Import** | P1 | `omega export` / `omega import` for full engine state |

### The Community Flywheel

```
Developer forks Omega Engine → Builds custom IWAD
    → Shares IWAD in registry → Others use it
        → Feedback improves engine → Better platform
            → More developers → More IWADs → More sovereignty
```

---

## The 14 Constitutional Laws (v3.1.0)

| # | Law | What It Means | Status |
|---|-----|---------------|--------|
| M1 | AnyIO Absolute | No asyncio. Runtime portability. | ✅ CI-enforced |
| M2 | Engine-Stack Firewall | Engine knows slots, WADs know meanings | ✅ Restored (D113) |
| M3 | Iris Constant | Messenger, not a Pillar | ✅ Trust-based |
| M4 | Sequentiality | Plan→Verify→Execute | ✅ Trust-based |
| M5 | Gnosis Preservation | L1→L2→L3 from every session | 🟡 Distiller orphaned |
| M6 | Podman Sovereignty | keep-id, no :U flag | ✅ Trust-based |
| M7 | Local-First | Cloud is teacher, not dependency | 🟡 Config-only |
| M8 | Zero Telemetry | No phone-home. Ever. | ✅ CI-enforced |
| M9 | Error Integrity | Typed, traceable, testable exceptions | 🟡 3 violations |
| M10 | Fleet Integrity | 14 agent cap | ✅ CI-enforced |
| M11 | Soul Integrity | Session end → soul.yaml update | 🔴 No hook exists |
| M12 | Queue Integrity | Every request reaches terminal state | ✅ Trust-based |
| M13 | Temple-Grade | T1-T11 gates (T11 exempted) | ✅ CI-enforced |
| M14 | Heritage Vetting | Every [id-soft:] needs vet record | ✅ CI-enforced |

---

## The Sovereignty Scorecard

| Metric | Target | Current | Gap |
|--------|:------:|:-------:|-----|
| Local inference ratio | ≥80% | ~30% | 🟡 Qdrant/Redis unwired |
| Cloud dependency (basic ops) | 0 | 0 | ✅ |
| Data residency | 100% | 100% | ✅ |
| Telemetry events | 0 | 0 | ✅ |
| Agents with soul v2 | All 14 | 2/14 | 🟡 Only Kali + Doom Guy |
| Soul distillation rate | ≥1 L3/3 sessions | 0 | 🔴 Distiller orphaned |
| Mandates enforced by code | ≥10/14 | 6/14 | 🟡 Trust-based gaps |
| Hub dashboard | Live HTML | REST only | 🟡 No UI |
| MVE works on fresh machine | Yes | No | 🔴 Mock mode only |
| Community IWADs | ≥3 | 0 | 🔴 No distribution |

---

## Sprint Schedule (Honest Timelines)

| Sprint | Focus | Duration | Dependencies |
|:------:|-------|----------|-------------|
| **S1** | Clean Slate (Phase 0) | 1 day | None |
| **S2** | Soul Wiring (Phase 1) | 3 days | S1 |
| **S3** | Local Intelligence (Phase 2) | 1 week | S2 |
| **S4** | Visible Intelligence (Phase 3) | 1 week | S2 |
| **S5** | MVE + Docker | 3 days | S2 |
| **S6** | Community Platform (Phase 4) | 2 weeks | S3, S4, S5 |
| **S7** | Federated Learning | 2 weeks | S6 |
| **S8** | Omega Desktop | 3 weeks | S4 |

---

## The Architect's Strength (Not Weakness)

The single-developer model is not a weakness — it's the **proof of concept**.

The Omega Engine exists because one person had a vision and assembled
a team of AI agents to build it. The engine IS the tool that makes
this possible. When other developers fork it, they get:

- 14 pre-configured agents with personalities and expertise
- 14 constitutional laws that prevent common AI mistakes
- A soul system that makes agents learn and evolve
- A coordination layer (Hivemind) that keeps agents in sync
- A WAD system that lets them customize everything without breaking the engine

The Architect's role evolves from "sole developer" to "founder of a movement."
The engine's job is to make the Architect's vision reproducible for others.

---

*Roadmap v1.0 | PIVOT D117 | Author: Cline-M3 | Date: 2026-06-04*
*This document supersedes the ad-hoc sprint plans in OMEGA_ENGINE.md §8.*
*The canonical sprint plan is now this file + HARDENING_REPORT.md + SOVEREIGN_HARDENING_PLAN.md.*
