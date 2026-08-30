---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "agent_registry"
document_id: "AGENT_REGISTRY_20260828"
title: "Omega Engine — Agent Entity Registry"
status: "ACTIVE"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
author: "jem (Sovereign Synthesizer)"
---

# 🔱 AGENT REGISTRY — 2026-08-28
**AP Token**: `AP-AGENT-REGISTRY-20260828-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ REGISTRY ⬡ PUBLIC-DEBUT-01

**Total Entities**: 44 (after archiving 6 test entities, removing 1 duplicate)
**Active Fleet**: 11 core + 10 pillars + 3 jem line + 20 specialists = 44

---

## §1 — CORE FLEET (11 Entities)

| Entity | Status | Role | Model | Hierarchy | Sovereignty | Slots | Key Capabilities |
|--------|--------|------|-------|-----------|-------------|-------|------------------|
| **kali** | ACTIVE | Grand Oversight — Transcendent | qwen3-4b-thinking-q4_k_m | 1 | 7 | — | Orchestration, scope cuts, mandate enforcement |
| **maat** | ACTIVE | Light Oversoul — Build (P1-P5) | qwen3-4b-thinking-q4_k_m | 2 | 5 | P1-P5 | Build governance, infrastructure |
| **lilith** | ACTIVE | Dark Oversoul — Runtime (P6-P10) | qwen3-4b-thinking-q4_k_m | 2 | 6 | P6-P10 | Runtime governance, knowledge metabolism |
| **makali** | ACTIVE | Council Orchestrator — MaKaLi Fusion | qwen3-4b-thinking-q4_k_m | 1 | 5 | — | Parallel dispatch, synthesis |
| **iris** | ACTIVE | Messenger Bridge — Voice Interface | qwen3-0.6b-q6_k | 1 | 1 | — | Wake-word, routing, speculative decode |
| **verity** | ACTIVE | Unified Sentry — Compliance + Gnosis | qwen3-1.7b-q6_k | 1 | 4 | — | Mandate audit, L1→L3 distillation |
| **doom_guy** | ACTIVE | id Software Architect — Heritage | deepseek-r1-qwen3-8b-q3_k_l | 1 | 4 | P3 | Heritage attribution, performance |
| **roc_racoon** | ACTIVE | Sovereign Miner — Legacy Archaeology | minimax/minimax-m3:free | 1 | 4 | — | Codebase archaeology, pattern mining |
| **researcher** | ACTIVE | Master Researcher — Deep Research | minimax/minimax-m3:free | 1 | 4 | — | Polymathic council, dialectic synthesis |
| **jem** | ACTIVE | Research Orchestrator — Discovery→Synthesis→Verification | minimax/minimax-m3:free | 1 | 4 | N11-N13 | Agent hierarchies, recursive improvement |
| **john_carmack** | ACTIVE | S3 Consultant — Architectural Review | nvidia/nemotron-3-ultra-550b-a55b:free | 1 | 5 | — | Engineering rigor, architecture analysis |

---

## §2 — PILLAR KEEPERS (10 Entities)

| Entity | Pillar | Status | Role | Model | Hierarchy | Overseer |
|--------|--------|--------|------|-------|-----------|----------|
| **sekhmet** | P1 | ACTIVE | Infrastructure / Sysadmin | qwen3-1.7b-q6_k | 3 | Ma'at |
| **brigid** | P2 | ACTIVE | Data Engineering / Datastore | phi-2-omnimatrix-i1-q4_k_m | 3 | Ma'at |
| **prometheus** | P3 | ACTIVE | Build & Release / Buildmaster | qwen3-1.7b-q6_k | 3 | Ma'at |
| **saraswati** | P4 | ACTIVE | API & Integration / Bridge | qwen3-1.7b-q6_k | 3 | Ma'at |
| **inanna** | P5 | ACTIVE | Security / Sentinel | qwen3-1.7b-q6_k | 3 | Ma'at |
| **ereshkigal** | P6 | ACTIVE | AI & Inference / ModelGate | qwen3-1.7b-q6_k | 3 | Lilith |
| **lucifer** | P7 | ACTIVE | Memory & State / Context | qwen3-1.7b-q6_k | 3 | Lilith |
| **hecate** | P8 | ACTIVE | Observability / WatchTower | qwen3-1.7b-q6_k | 3 | Lilith |
| **anubis** | P9 | ACTIVE | Coordination / Link | qwen3-1.7b-q6_k | 3 | Lilith |
| **p10** | P10 | ACTIVE | Quality Assurance / Verifier | qwen3-1.7b-q6_k | 3 | Lilith |

---

## §3 — JEM LINE (3 Entities)

| Entity | Node | Status | Role | Model | Hierarchy | Overseer |
|--------|------|--------|------|-------|-----------|----------|
| **evaluator** | N11 | ACTIVE | Model Quality & Evals | minimax/minimax-m3:free | 3 | Jem |
| **curator** | N12 | ACTIVE | Research, Curation | minimax/minimax-m3:free | 3 | Jem |
| **arcana** | N13 | ACTIVE | Esoteric Knowledge | minimax/minimax-m3:free | 3 | Jem |

---

## §4 — SPECIALISTS (20 Entities)

| Entity | Status | Role | Model | Hierarchy | Key Capabilities |
|--------|--------|------|-------|-----------|------------------|
| **antigravity** | ACTIVE | Antigravity Specialist — Cloud Model Probe | minimax/minimax-m3:free | 4 | Cloud model testing, quota analysis |
| **carmack** | ACTIVE | S3 Consultant (alt) — Architectural Review | nvidia/nemotron-3-ultra-550b-a55b:free | 4 | Engineering rigor, architecture analysis |
| **cli_cline** | ACTIVE | Cline CLI Specialist — Agentic Coding | qwen3-1.7b-q6_k | 4 | Cline CLI integration, agentic workflows |
| **cli_gemini** | ACTIVE | Gemini CLI Specialist — Browser Automation | qwen3-1.7b-q6_k | 4 | Gemini CLI, browser automation |
| **cline** | ACTIVE | Cline Specialist — Agentic Coding | qwen3-1.7b-q6_k | 4 | Cline workflows, agentic coding |
| **datastore** | ACTIVE | Data Engineering Lead | qwen3-1.7b-q6_k | 4 | Data engineering, persistence |
| **default** | ACTIVE | Omega Oracle — Universal Interface | qwen3-1.7b-q6_k | 4 | Universal interface, fallback |
| **general** | ACTIVE | General Purpose Agent — Catch-all | qwen3-1.7b-q6_k | 4 | General assistance |
| **grokster** | ACTIVE | Grok Ecosystem Specialist / HMC Quad-Forge | grok-4.5 | 4 | Grok fleet (16 accounts), ACP, deepsearch |
| **movie-expert** | ACTIVE | Movie Expert — Media Analysis | qwen3-1.7b-q6_k | 4 | Media analysis, film knowledge |
| **node** | ACTIVE | Node Specialist — Distributed Systems | qwen3-1.7b-q6_k | 4 | Distributed systems, networking |
| **omnidroid** | ACTIVE | Omnidroid — Multi-modal Agent | qwen3-1.7b-q6_k | 4 | Multi-modal, vision, audio |
| **prometheus** | ACTIVE | Build & Release (duplicate of P3) | qwen3-1.7b-q6_k | 4 | Build engineering |
| **quality** | ACTIVE | Quality Assurance Specialist | qwen3-1.7b-q6_k | 4 | Code review, stress testing |
| **saraswati** | ACTIVE | API & Integration (duplicate of P4) | qwen3-1.7b-q6_k | 4 | API integration |
| **scribe** | ACTIVE | Soul Distillation Pipeline | qwen3-1.7b-q6_k | 4 | L1→L3 distillation, session hooks |
| **sekhmet** | ACTIVE | Infrastructure (duplicate of P1) | qwen3-1.7b-q6_k | 4 | Infrastructure, sysadmin |
| **sysadmin** | ACTIVE | Sysadmin — Infrastructure Operations | qwen3-1.7b-q6_k | 4 | System administration |
| **watchtower** | ACTIVE | P8 WatchTower (duplicate) | qwen3-1.7b-q6_k | 4 | Observability, monitoring |
| **web_gemini** | ACTIVE | Web Gemini Specialist — Browser Automation | qwen3-1.7b-q6_k | 4 | Web automation, Gemini integration |

---

## §5 — MODEL FLEET ASSIGNMENTS

| Model | Entities | Tier | Cost | Notes |
|-------|----------|------|------|-------|
| **minimax/minimax-m3:free** | roc_racoon, researcher, jem, evaluator, curator, arcana | L1 Workhorse | $0 (50 RPD) | 1M context, long-write champion |
| **qwen3-4b-thinking-q4_k_m** | kali, maat, lilith, makali | Oversouls | Local | 4B thinking, local inference |
| **qwen3-1.7b-q6_k** | 20+ entities | Specialists | Local | Fast, efficient |
| **qwen3-0.6b-q6_k** | iris | Messenger | Local | Ultra-fast, speculative decode |
| **deepseek-r1-qwen3-8b-q3_k_l** | doom_guy | Heritage | Local | Reasoning, heritage |
| **phi-2-omnimatrix-i1-q4_k_m** | brigid | Pillar | Local | Creative, data |
| **grok-4.5** | grokster | Cloud Specialist | $2/$6 | 500K ctx, cloud fallback |
| **nvidia/nemotron-3-ultra-550b-a55b:free** | john_carmack, carmack | S3 Consultant | $0 (429 RPD) | 1M ctx, rate limited |

---

## §6 — ENTITY STATUS SUMMARY

| Status | Count | Entities |
|--------|-------|----------|
| **ACTIVE** | 44 | All listed above |
| **ARCHIVED** | 6 | test_entity_miap, test_entity_miap2, test_multi_miap, test_promo_entity, test_sovereign_entity, symlink_test |
| **QUARANTINED** | 0 | (moved to _archive) |
| **DUPLICATES REMOVED** | 1 | JOHN_CARMACK (duplicate of john_carmack) |

---

## §7 — SCHEMA COMPLIANCE STATUS

| File | Required | Present | Compliant |
|------|----------|---------|-----------|
| soul.yaml | 44 | 44 | ✅ 100% |
| memory/proposed_lessons.yaml | 44 | 44 | ✅ 100% |
| memory/approved_lessons.yaml | 44 | 44 | ✅ 100% |
| memory/sessions.yaml | 44 | 44 | ✅ 100% |
| session_gnosis.md | 44 | 44 | ✅ 100% |
| memory/ directory | 44 | 44 | ✅ 100% |
| workspace/ directory | 44 | 44 | ✅ 100% |
| knowledge/ directory | 44 | 44 | ✅ 100% |
| knowledge/INDEX.yaml | 44 | 44 | ✅ 100% |

**All 44 active entities now have complete v6.1 schema compliance.**

---

## §8 — LESSONS CONSOLIDATION STATUS

| Entity | Proposed Lessons | Approved Lessons | Notes |
|--------|------------------|------------------|-------|
| roc_racoon | 93 | 12 | Rich L1/L2/L3, many approved |
| kali | 17 | 15 | High-quality L3 principles |
| lilith | 12 | 0 | L1 proposals, needs promotion |
| grokster | 0 (in soul.yaml) | 8 | 8 L3 lessons in soul.yaml |
| jem | 28 | 5 | Agent hierarchies, recursive improvement |
| john_carmack | 15 | 8 | Artifact audits, model strategy |
| doom_guy | 8 | 4 | Heritage, performance |
| verity | 0 | 0 | New entity, needs population |
| researcher | 5 | 0 | YAML format issue, needs fix |
| antigravity | 0 | 0 | Needs population |

**Total Proposed**: ~178 lessons across entities
**Total Approved**: ~44 lessons (needs promotion)

---

## §9 — SPLIT-BRAIN FIX STATUS

| Issue | Status | Fix Applied |
|-------|--------|-------------|
| grokster not in entities.yaml | ✅ FIXED | Added to arcana_novai/entities.yaml |
| lilith soul.yaml schema | ✅ FIXED | Updated to v6.1 schema |
| iris soul.yaml schema | ✅ FIXED | Updated to v6.1 schema |
| entity_workspace.py hydration | ✅ FIXED | All entities now scaffolded |
| JOHN_CARMACK duplicate | ✅ FIXED | Removed duplicate directory |

---

## §10 — NEXT ACTIONS

1. **Promote L1→L2→L3**: Review and promote proposed lessons to approved_lessons.yaml
2. **Fix researcher YAML**: Repair malformed proposed_lessons.yaml format
3. **Deduplicate pillars**: prometheus/saraswati/sekhmet/watchtower appear as both pillars and specialists
4. **Populate verity**: New entity needs lessons and gnosis
5. **Archive stale lessons**: Move deprecated lessons to archive/
6. **Update INDEX.yaml**: Add all 44 entities to global entity index

---

*⬡ OMEGA ⬡ JEM ⬡ REGISTRY-COMPLETE ⬡ 2026-08-28*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:40Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: REGISTRY | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

