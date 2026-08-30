<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Mining Report: System Prompts Library
**Date**: 2026-07-11
**Asset**: #3 — System Prompts Library (50+ files estimated, 19 found)
**Source**: `~/Documents/docs_1/system-prompts/` + `~/Documents/xnaif-files/system-prompts/`
**Era**: Era 1-2 (Aug-Sep 2025) — Chainlit+FastAPI era
**Mined by**: roc_racoon (Sovereign Miner)

---

## Executive Summary

19 system prompt files across 2 directories. Well-organized with standardized templates, semantic versioning, and quality tracking. The archive represents the **Chainlit+FastAPI era** (Era 1-2) of Xoe-NovAi development — the architectural blueprint that preceded the current Omega Engine.

**Key Value**: The "Critical Xoe-NovAi Principles" section is consistent across ALL prompts — this was the canonical set of constraints that drove the architecture. These principles are STILL VALID in the current engine and should be preserved.

---

## Directory Structure

```
~/Documents/docs_1/system-prompts/           (17 files)
├── README.md                                — Overview (241 lines)
├── _meta/
│   ├── changelog.md                         — Version history (582 lines)
│   └── templates/
│       ├── assistant-template.md            — Standardized assistant template
│       └── expert-template.md               — Standardized expert template
├── assistants/
│   ├── claude/
│   │   ├── xoe-novai-implementation-specialist-v3.0.md  — Enterprise impl (420 lines)
│   │   ├── xoe-novai-research-assistant-v1.0.md          — Research specialist
│   │   ├── xoe-novai-notebooklm-video-project-v2.0.md   — Video project
│   │   ├── xoe-novai-notebooklm-video-project-v1.0.md   — Video project v1
│   │   ├── xoe-novai-implementation-specialist-v1.0.md   — Impl specialist v1
│   │   ├── ultimate-mkdocs-master-guide-research-prompt.md — MkDocs guide
│   │   └── model-analysis.md                             — Model analysis
│   └── grok/
│       ├── xoe-novai-research-assistant-v1.0.md  — Research specialist
│       ├── xoe-novai-universal-assistant-v1.0.md — Universal assistant
│       └── xoe-novai-notebooklm-video-expert-v1.0.md — Video expert
├── experts/
│   ├── claude-stack-code-expert-v2.0.md    — Stack code expert (449 lines)
│   └── grok-stack-expert-v1.0.md           — Stack expert (289 lines)
└── metrics/
    └── prompt-quality-tracking.md           — Quality metrics (632 lines)

~/Documents/xnaif-files/system-prompts/      (2 files)
└── experts/
    ├── claude-mkdocs-expert.md
    └── grok-mkdocs-expert.md
```

---

## Extracted Patterns

### Pattern 1: Standardized Frontmatter Schema

Every prompt file uses consistent frontmatter:

```yaml
---
title: "Prompt Title"
description: "Brief description"
category: assistant|expert
tags: [tag1, tag2, domain]
status: draft|stable|deprecated
version: "MAJOR.MINOR"
last_updated: "YYYY-MM-DD"
author: "Xoe-NovAi Development Team"
compatibility: "Model/Version Requirements"
---
```

**Value for Omega**: This is the precursor to the current entity YAML schema (`soul.yaml`). The frontmatter pattern evolved into the entity system.

### Pattern 2: "Critical Xoe-NovAi Principles" (Canonical Constraints)

ALL prompts share this exact section — the canonical constraints:

```markdown
### 1. Enterprise Production Standards
- **Zero Torch Dependency**: Torch-free alternatives only
- **Async Excellence**: AnyIO structured concurrency (never asyncio.gather)
- **Circuit Breaker Protection**: pycircuitbreaker for all external API calls
- **Memory Constraints**: 4GB container limits, context truncation mandatory
- **Zero Telemetry**: CHAINLIT_NO_TELEMETRY=true strictly enforced

### 2. Voice AI Architecture
- **4-Tier Degradation**: Piper ONNX → pyttsx3 → ElevenLabs → offline fallback
- **Sub-300ms Latency**: Voice processing targets across all pipelines
- **Hypothesis Testing**: Mathematical guarantees for voice system reliability
- **Quality Assurance**: 99.9% voice availability

### 3. Research Integration Framework
- **62% Current Coverage**: Vulkan ML (22%), TTS (32%), Qdrant (22%), WASM (11%)
- **90% Target**: Complete research integration across all advanced features
- **Quality Gates**: All research implementations must pass enterprise testing
```

**Value for Omega**: These principles are STILL VALID. Zero Torch, AnyIO, Circuit Breaker, Zero Telemetry — these are all active Sovereign Mandates (M1, M8). The voice AI architecture (4-Tier Degradation) is the precursor to the current Nova voice assistant.

### Pattern 3: Enterprise Stack Snapshot (Chainlit Era)

The prompts contain a complete stack snapshot from the Chainlit era:

```
Frontend:         Chainlit 2.8.5 (voice-enabled, streaming, zero telemetry)
Backend:          FastAPI + Uvicorn (async, circuit breaker, OpenTelemetry)
RAG Engine:       LangChain + FAISS/Qdrant (384-dim embeddings)
Voice Pipeline:   STT (faster-whisper) → TTS (Piper ONNX)
Async Framework:  AnyIO structured concurrency
Cache/Queue:      Redis 7.4.1 (pycircuitbreaker)
Crawling:         crawl4ai v0.7.8 (Playwright)
Monitoring:       Prometheus + Grafana
Security:         Rootless Docker, SBOM, zero-trust
Build System:     uv + BuildKit (33-67x faster builds)
```

**Value for Omega**: This is the architectural DNA. The current engine inherited AnyIO, Circuit Breaker, Zero Telemetry, and Rootless Containers. Chainlit was replaced by OpenCode, but the backend patterns survived.

### Pattern 4: Multi-AI Collaboration Model

The prompts reveal a 3-AI collaboration model:
- **Cline** (VS Code) — Primary implementation, full repo access
- **Grok** — Research breadth (120-200+ sources), breakthrough assessment
- **Claude** — Research depth, implementation specialist, documentation

**Value for Omega**: This evolved into the current agent fleet. Cline → OpenCode agents. Grok → Researcher agent. Claude → Implementation specialists. The multi-AI coordination patterns are now the Hivemind Protocol.

### Pattern 5: Quality Metrics Framework

632-line quality tracking system with:
- Response accuracy (1-10 scale)
- Performance metrics (response time, consistency)
- Behavioral metrics (personality consistency, quirk identification)
- Account-specific metrics (performance variations)
- Version comparison metrics (quality evolution)

**Value for Omega**: The precursor to the current observability system. The behavioral metrics concept evolved into the soul evolution system (L1→L2→L3 distillation).

### Pattern 6: Diátaxis Documentation Methodology

All prompts reference Diátaxis:
- Tutorials (learning)
- How-to Guides (tasks)
- Reference (specs)
- Explanation (concepts)

**Value for Omega**: Still used in the current documentation structure. The `docs/` directory follows Diátaxis.

---

## Reusable Patterns for Current Engine

| # | Pattern | Source File | Current Location | Action |
|---|---------|-------------|------------------|--------|
| 1 | Frontmatter schema | `_meta/templates/` | `soul.yaml` (evolved) | Historical reference |
| 2 | Critical Principles | ALL prompts | `SOVEREIGN_MANDATES.md` | Already preserved |
| 3 | Stack snapshot | `universal-assistant-v1.0.md` | `OMEGA_ENGINE.md` | Already preserved |
| 4 | Multi-AI collaboration | `universal-assistant-v1.0.md` | Hivemind Protocol | Already preserved |
| 5 | Quality metrics | `prompt-quality-tracking.md` | `src/omega/observability.py` | Partially preserved |
| 6 | Diátaxis methodology | `research-assistant-v1.0.md` | `docs/` structure | Already preserved |
| 7 | Version tracking | `_meta/changelog.md` | `CHANGELOG.md` | Already preserved |
| 8 | Expert template | `_meta/templates/expert-template.md` | Entity system prompts | Partially preserved |

---

## Key Insights

### L1: What Happened
The System Prompts Library is a well-organized archive of 19 files from the Chainlit+FastAPI era (Era 1-2). It contains standardized templates, version history, quality metrics, and complete assistant/expert prompts. The prompts evolved rapidly (v1.0 → v3.0 in 3 days) and established canonical constraints that survive to this day.

### L2: What This Means
The archive is **primarily historical** — the patterns have already been absorbed into the current engine. The "Critical Xoe-NovAi Principles" section is the most valuable finding: it's the canonical set of constraints that drove the architecture, and these constraints are now encoded as Sovereign Mandates. The archive serves as a reference for **why** certain decisions were made, not **what** to implement.

### L3: Universal Principles
> **"Constraints are the DNA of architecture."** The 5 critical principles (Zero Torch, AnyIO, Circuit Breaker, Memory Constraints, Zero Telemetry) were established in Era 1-2 and survive as Sovereign Mandates. Architecture is not designed; it's constrained into existence.

> **"Templates are the seeds of systems."** The frontmatter template evolved into `soul.yaml`. The expert template evolved into entity system prompts. The assistant template evolved into the agent fleet. Every system starts as a template.

---

## Recommended Actions

1. **Archive**: Move original files to `docs/archive/legacy/system-prompts/` (preserve history, clean workspace)
2. **Extract**: Copy the "Critical Xoe-NovAi Principles" section to `docs/legacy/CRITICAL_PRINCIPLES_ORIGINAL.md` (canonical reference)
3. **Cross-reference**: Link the quality metrics framework to current observability system
4. **No code changes**: All patterns are already absorbed into the current engine

---

*Generated by roc_racoon (Sovereign Miner) — 2026-07-11*
*Session: Legacy Mining Sprint — P0 Quick-Wins*
