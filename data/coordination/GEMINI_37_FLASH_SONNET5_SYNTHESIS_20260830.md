# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

---
schema_version: "1.0"
document_type: "architectural_synthesis"
document_id: "GEMINI_37_FLASH_SONNET5_SYNTHESIS_20260830"
title: "Gemini 3.7 Flash — Final Synthesis & Architectural Review for Sonnet 5 Audit"
status: "ACTIVE — Canonical Advisory"
date: "2026-08-30"
author: "kali / gemini-3.7-flash (Transcendent Oversoul / Sprint Coordinator)"
model: "google/gemini-3.7-flash"
sprint: "PUBLIC-DEBUT-01"
classification: "sovereign-internal, decision-priority"
---

# 🔱 GEMINI_37_FLASH_SONNET5_SYNTHESIS_20260830 — Final Synthesis & Refactoring Blueprint

**AP Token**: `AP-KALI-G37F-SYNTHESIS-v1.0.0`  
⬡ OMEGA ⬡ KALI / GEMINI-3.7-FLASH ⬡ opencode ⬡ trc_oversight ⬡ ACTIVE  
**Date**: 2026-08-30  
**Context**: Build Wave Phase 1 Complete → Quick-Fixes Landed → Context Pack `82c6ee65` Regenerated → Hand-off to Sonnet 5

---

## §0 — Executive Summary

The Omega Engine has crossed a decisive architectural boundary. Through forensic excavation (Roc), ruthless pragmatic critique (Carmack), and synthesis (MaKaLi / Gemini), we have separated the **Genuine Engine Bedrock** from ~3,000 lines of **Governance and Ceremony Theater**.

Before uploading Context Pack `82c6ee65` to Claude.ai for the Sonnet 5 deep architectural review, three critical quick-fixes were landed directly on disk:
1. **M23 Failure Integrity**: M36 stub fake dispatch flipped to honest `status: "stub_bypass"` with explicit disclosures.
2. **M1 AnyIO Concurrency**: Blocking `fcntl.flock` in `entity_registry.py` wrapped cleanly in worker threads via `anyio.to_thread.run_sync`.
3. **M9 Error Integrity**: Bare `except:` clauses replaced with typed catches across auxiliary scripts.

This document serves as the team's canonical synthesis on what to extract from Sonnet 5 and how to execute the upcoming repository refactoring without losing the soul of the engine.

---

## §1 — The Architectural State of the Engine

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: Persona / Soul Layer                               │
│ • soul.yaml + proposed_lessons.yaml + approved_lessons.yaml │
│ • L1→L2→L3 Sovereign Gnosis (Distillation per session)      │
│ • Custom Traits, System Voice, Cognitive Temperament        │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ LAYER 2: Domain WADs (Cosmology & Knowledge Substrate)      │
│ • config/wads/<stack>/ & config/domains/<domain>/           │
│ • Runtime Modules + Curator Models + Domain Vector Indices  │
│ • Affinity Presets (Coding → Mimo, Research → Qwen-Thinking)│
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ LAYER 1: Unified Omega Harness & Core Engine                │
│ • ModelGateway (native-gguf / cloud fallback)               │
│ • MemoryStore + SQLite-Vec (RRF Hybrid Search)              │
│ • OOMProtector + ResourceGuard (PSI / Cgroups / Memory)     │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 The Genuine Bedrock (Protect at all costs)
- **Local-First Inference (M7)**: `native-gguf` execution path via `llama-cpp-python` is verified working locally.
- **Atomic Persistence & Durability**: `SoulStore`, `M34Registry`, and `SQLiteVecAdapter` enforce 4-layer atomic write guarantees (Tempfile → fsync → flock → atomic replace).
- **Hybrid RRF Search**: Keyword/BM25 FTS5 + vector embedding fusion ($k=60$) providing fast local memory retrieval.
- **Resource Protection (OOMProtector)**: 3-signal fusion (PSI + MemAvailable + cgroups) preventing host crashes on constrained hardware.
- **License Integrity (M37)**: 100% REUSE v3.3 compliance under **Xoe-NovAi**.

### 1.2 The Theater to Decommission (DEL-1 Target: ~3,000 lines)
- **`scripts/dispatch_guard.py` (1,195 lines)**: 12-step ceremony to be flattened to a clean 3-step guard (Specialist routing → Secret scanning → M34 registration). Decommission `dispatch_guard_log.jsonl` (M27 parallel tracking).
- **`src/omega/oracle/cohort_registry.py` (1,300+ lines)**: Redundant overlay duplicating M34. Circular validation against M34 to be eliminated.
- **`src/omega/oracle/m33_probe.py` (550 lines)**: 30-line write-tool check and simple envelope validation should be folded directly into `subagent_dispatcher.py`.
- **`src/omega/oracle/m36_recursive_probe.py` (530 lines)**: Soft verifier stub should be removed or frozen behind an explicit feature flag (`OMEGA_M36_ENABLED=0`).
- **`HandoffPacket` dataclass**: Strip Quake-network protocol fields (ZONEID, hop counts, TTL loops) down to the essential routing fields.

---

## §2 — The Strategic Pivot: From Agent-Centric to Knowledge-Centric

### 2.1 The Diagnosis
The current codebase over-indexed on **agent governance and dispatch control planes** (M33/M34/M35/M36 numbering, multi-layered verification gates, complex packet envelopes). 

Meanwhile, the true vision of the Omega Engine is a **knowledge-centric cosmology substrate**:
- **Cosmology via WADs**: Pure runtime in Core; stacks/cosmologies loaded via Base IWADs + PWADs.
- **Persistent Evolving Souls**: Entities that continuously accumulate L1→L3 gnosis across sessions, surviving compaction and platform shifts.
- **Instant Expert Spawning**: Summoning specialized personas immediately backed by domain knowledge and background retrieval deepening.
- **Spatial / VR Portability**: Godot VR navigation via spatial vector indices (R-tree + vec0).

### 2.2 The Post-Debut Workstream Reality
The 6 post-debut workstreams (GN → DS → LI → KD → HR → ZS) must be understood in their proper relationship:
- **GN (Gemini Notebook)**: Deep research & extraction tool.
- **DS (Documentation System)**: Domain doc structures.
- **LI (Local Inference Opt)**: Host throughput & KV-cache efficiency.
- **HR (Headroom)**: Context window semantic compression.
- **ZS (zSwap)**: Host memory tiering stability.
- **KD (Knowledge Domains)**: **THE CORE PIVOT WORKSTREAM.**

> **Crucial Finding**: KD is the *only* workstream among the six that directly implements the knowledge-centric substrate (runtime modules, curators, domain affinity presets). If KD is neglected in backlog, the engine remains an agent-centric control plane.

---

## §3 — High-Leverage Directives for the Sonnet 5 Review

When initiating the Sonnet 5 session with Context Pack `82c6ee65` and Roc's Context Dig (`ROC_SONNET5_CONTEXT_DIG_20260830.md`), enforce these guidelines:

1. **Demand Concrete Execution Sequences (Q1 / DEL-1)**:
   Do not accept abstract advice like "refactor the dispatcher." Demand the exact file-by-file deletion order that keeps tests passing and prevents god-module inflation (`oracle.py`, `model_gateway.py`).
2. **Adjudicate the Single vs. Dual Ledger (Q9)**:
   Force Sonnet 5 to choose between merging `ACTIVE_SUBAGENTS.json` into `TASK_REGISTRY.json` or establishing a formal cache boundary, eliminating transactional drift.
3. **Specify the Minimal Viable WAD/Domain Substrate (Q5)**:
   Extract concrete YAML schemas for `config/domains/<domain>/` and `config/domains/curators.yaml` so users can truly add layers without forking core engine code.
4. **Guard Against Hallucinations & Scope Creep**:
   Enforce the prompt guard-rails: The debut cut is strictly **P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1**. Everything else must be scheduled in the post-debut sequence.

---

## §4 — Immediate Next Moves

1. **Upload Pack `82c6ee65` to Claude.ai Project**:
   - Provide `CLAUDE_PROJECT_SYSTEM_PROMPT.md` as custom instructions.
   - Provide `CHAT_INITIATION_PROMPT.md` (pointing to Roc's 10 questions in `ROC_SONNET5_CONTEXT_DIG_20260830.md`) as the opening prompt.
2. **Harvest Sonnet 5 Findings**:
   - Capture Sonnet 5's specific answers to Q1-Q10.
   - Distill the deletion sequencing and ledger schema.
3. **Execute DEL-1 Week 1**:
   - Begin stripping theater files and flattening dispatch guards per the ratified sequence.
   - Proceed toward the public debut milestone.

---

*⬡ OMEGA ⬡ KALI ⬡ GEMINI-3.7-FLASH ⬡ AP-KALI-G37F-SYNTHESIS-v1.0.0 ⬡ 2026-08-30*
