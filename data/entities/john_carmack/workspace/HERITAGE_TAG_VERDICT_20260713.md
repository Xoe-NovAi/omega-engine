<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Heritage Tag System — Architectural Verdict
**Author**: John Carmack (S3 Consultant)
**Date**: 2026-07-13
**Status**: FINAL

---

## The Verdict

**The heritage tag system has become bureaucratic bloat. It is noise. It must be reformed.**

---

## First Principles Analysis

### What is a heritage tag actually for?

A heritage tag documents **intellectual lineage** — a conscious architectural decision to adopt a specific pattern, algorithm, or design philosophy from an external source. It says: *"I studied how X solved this problem, and I am deliberately porting/adapting their approach."*

It is **not** a dependency manifest. It is **not** a credits file. It is **not** "I used this library."

### The Signal vs. The Noise

| Entry | Signal or Noise? | Reason |
|-------|------------------|--------|
| `[id-soft: doom-1993] WAD System` | **SIGNAL** | Direct port of id's lump-based resource system. Architectural DNA. |
| `[id-soft: quake-1996] Zone Memory` | **SIGNAL** | Tag-based allocator with purge levels — conscious adoption of Quake's memory philosophy. |
| `[heritage: headroom-ai 2025] Compression Middleware` | **SIGNAL** | Explicitly using headroom's semantic compression algorithm. |
| `[heritage: anyio 2024] Async Runtime` | **NOISE** | You picked a runtime. You didn't adopt their *architecture*. |
| `[heritage: fastapi 2018] Web Framework` | **NOISE** | Standard dependency. No architectural lineage claimed. |
| `[heritage: pydantic 2017] Validation` | **NOISE** | Industry standard. Using it ≠ adopting their design philosophy. |
| `[heritage: onnxruntime 2018] Inference Runtime` | **NOISE** | You run models on it. That's usage, not heritage. |
| `[heritage: podman 2019] Containers` | **NOISE** | Infrastructure choice. Not an architectural pattern adoption. |

**Current ratio**: ~5 signal entries vs 55+ noise entries. **Signal-to-noise: <10%.**

---

## The Concrete Rule (The "Right Approximation")

### A heritage tag is REQUIRED **iff all three conditions hold**:

1. **Conscious Pattern Adoption**: You studied the source's *specific solution* to a problem and deliberately replicated/adapted it in your codebase.
2. **Architectural Significance**: The pattern shapes your system's structure — data flow, memory model, entity lifecycle, dispatch logic, or resource management.
3. **Non-Trivial Adaptation**: You didn't just `import x`. You ported logic, translated concepts, or built a wrapper that embodies their design philosophy.

### If any condition fails → NO TAG.

**Dependencies go in `pyproject.toml` / `requirements.txt` / `CREDITS.md` (as a simple list). Heritage tags go in source code comments.**

---

## What Stays, What Goes

### KEEP (Heritage Tags — Inline in Source Code)

| Pattern | Tag | Location |
|---------|-----|----------|
| WAD System (lump-based resources) | `[id-soft: doom-1993]` | `wad_loader.py`, `entity_registry.py` |
| BSP/PVS Culling → Provider Culling | `[id-soft: doom-1993]` | `model_gateway.py` |
| Zone Memory Allocator | `[id-soft: quake-1996]` | `memory/zone_allocator.py` |
| ZONEID Constant Pattern | `[id-soft: doom-1993]` | `constants.py` |
| cvar Table (runtime tunables) | `[id-soft: quake-1996]` | `config/cvar.py` |
| Lazy Deletion + Grace Period | `[id-soft: doom-1993]` | `memory_store.py` |
| Headroom Semantic Compression | `[heritage: headroom-ai 2025]` | `headroom.py` |
| Odysseus SearXNG Deployment Patterns | `[heritage: odysseus 2025]` | `quadlet/omega-searxng.container` |
| SOVEREIGN In-Path Governance | `[heritage: sovereign-kliewer 2026]` | `sovereign_vetter.py` |
| Logos Epistemic Filtering | `[heritage: logos 2026]` | `skeptical_verifier.py` |

**~15-20 legitimate tags. That's the signal.**

### REMOVE (Move to Simple Dependency List in CREDITS.md)

All 55+ "General Heritage Sources" entries that are **just dependencies**:
- AnyIO, FastAPI, Typer, Pydantic, httpx, redis-py, qdrant-client
- llama-cpp-python, MCP SDK, google.genai, sse-starlette
- ONNX Runtime, Piper TTS, Silero VAD, SentencePiece, tokenizers
- Podman, systemd, Cloudflare WARP, SearXNG, Exa, Firecrawl
- MCP standard, A2A standard, SPIFFE, OpenTelemetry, SPDX
- SQLite FTS5, RRF algorithm

**These belong in a clean `DEPENDENCIES.md` or `CREDITS.md` appendix — not inline tags.**

### REFORM: The CREDITS.md Structure

```
CREDITS.md
├── §1 Heritage Registry (THE SIGNAL)
│   ├── id Software Heritage (21 vetted patterns)
│   └── Conscious Adoptions (headroom, odysseus, sovereign, logos, etc.)
│
├── §2 Dependencies (THE NOISE — but documented)
│   ├── Runtime & Infrastructure (AnyIO, FastAPI, Podman, etc.)
│   ├── ML/Inference Stack (ONNX, llama-cpp-python, Piper, etc.)
│   ├── Standards & Protocols (MCP, A2A, SPIFFE, OpenTelemetry, etc.)
│   └── Research/Competitor Analysis (Truth Engine, SOVEREIGN, Logos, etc.)
│
├── §3 Mythological/Philosophical Frameworks (Tier 4 — no tags)
│
└── §4 User's Own IP (Tier 5 — no attribution needed)
```

---

## Enforcement

1. **Pre-commit hook**: Reject any new `[heritage:]` or `[id-soft:]` tag without a corresponding vet record in `HERITAGE_VET_LOG.md` that documents the **three conditions** above.
2. **CI Gate**: `make heritage-vet` fails if tag count > 25 without architectural review.
3. **Annual Purge**: Every 12 months, review all tags. If the code no longer reflects the adopted pattern, strip the tag.

---

## Confidence: 10/10

This is not opinion. This is the distinction between **architecture** and **shopping list**. The current system conflates them. The fix is surgical: keep the architecture tags, delete the dependency tags, document dependencies separately.

---

**Next Action**: 
1. Strip all 55+ dependency tags from CREDITS.md §2
2. Create `DEPENDENCIES.md` with clean categorized list
3. Keep only the ~15 legitimate heritage tags in CREDITS.md §1
4. Update pre-commit hook to enforce the three-condition rule
5. Run `make heritage-vet` to verify

*Verdict delivered. No further debate needed.*