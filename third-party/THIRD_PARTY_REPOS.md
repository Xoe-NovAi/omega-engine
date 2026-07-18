# 🔱 Omega Engine — Third-Party Repository Registry
**AP Token**: `AP-THIRD-PARTY-REGISTRY-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_third_party_registry ⬡ ACTIVE

**Date**: 2026-07-17
**Purpose**: Canonical registry of all third-party repositories we depend on, learn from, or study. Organized by priority for local cloning under `third-party/`.

---

## 📊 Priority Matrix

| Priority | Category | Count | Rationale |
|----------|----------|-------|-----------|
| **P0 — Critical Dependency** | Direct runtime dependencies | 4 | We import these at runtime; must have local source for debugging, patching, heritage vetting |
| **P1 — Architecture Reference** | Core architecture patterns we emulate | 5 | We study these for patterns (WAD, spatial memory, TUI, agent runtime) |
| **P2 — Research & Mining** | Legacy/origin repos we mine for patterns | 6 | Historical patterns, id Software heritage, early Omega prototypes |
| **P3 — Ecosystem & Tooling** | Complementary tools, adjacent projects | 4 | Useful for integration, comparison, or future adoption |

---

## 🎯 P0 — Critical Runtime Dependencies
*We import these at runtime. Local clones mandatory for debugging, heritage vetting (M14), and sovereignty.*

| # | Repo | URL | Stars | License | Omega Usage | Heritage Tag |
|---|------|-----|-------|---------|-------------|--------------|
| 1 | **sqlite-vec** | `https://github.com/asg017/sqlite-vec` | 7.9k | Apache-2.0 | Vector search via `sqlite_vec` extension; core of unified fabric | `[heritage: sqlite-vec-2024]` |
| 2 | **headroom-ai** | `https://github.com/headroomlabs-ai/headroom` | 59k | Apache-2.0 | Context compression middleware (`src/omega/oracle/middleware/headroom.py`) | `[heritage: headroom-ai-2025]` |
| 3 | **llama.cpp** | `https://github.com/ggml-org/llama.cpp` | 120k | MIT | Native GGUF inference backend; SomaticState serialization (M20) | `[heritage: ggml-2023]` |
| 4 | **qdrant-client** | `https://github.com/qdrant/qdrant-client` | — | Apache-2.0 | Vector adapter for multi-tenant/remote deployments | `[heritage: qdrant-2021]` |

**Clone Commands:**
```bash
cd third-party
git clone https://github.com/asg017/sqlite-vec.git
git clone https://github.com/headroomlabs-ai/headroom.git
git clone https://github.com/ggml-org/llama.cpp.git
git clone https://github.com/qdrant/qdrant-client.git
```

---

## 🏗️ P1 — Architecture Reference Repos
*We study these for architectural patterns. We do NOT import at runtime. Local clones for deep-dive analysis.*

| # | Repo | URL | Stars | License | Pattern We Study | Heritage Tag |
|---|------|-----|-------|---------|------------------|--------------|
| 5 | **Mem Palace** | `https://github.com/mempalace/mempalace` | — | MIT | Spatial memory (Wings/Rooms/Drawers), SQLite Exact backend, Temporal KG | `[heritage: mempalace-2025]` |
| 6 | **Grok Build (xAI)** | `https://github.com/xai-org/grok-build` | 15k | Apache-2.0 | Rust TUI architecture, agent runtime, ACP protocol, tool implementations | `[heritage: xai-grok-build-2026]` |
| 7 | **id Software DOOM** | `https://github.com/id-Software/DOOM` | 12k | GPL-2.0 | WAD system, BSP culling, zone memory, cvar system, thinker chain | `[id-soft: doom-1993]` |
| 8 | **id Software Quake** | `https://github.com/id-Software/Quake` | 8.5k | GPL-2.0 | Client-server architecture, entity system, QC VM, BSP/PVS | `[id-soft: quake-1996]` |
| 9 | **Letta (MemGPT)** | `https://github.com/letta-ai/letta` | 14k | Apache-2.0 | Agent memory architecture, context management, function calling | `[heritage: letta-2024]` |

**Clone Commands:**
```bash
cd third-party
git clone https://github.com/mempalace/mempalace.git
git clone https://github.com/xai-org/grok-build.git
git clone https://github.com/id-Software/DOOM.git
git clone https://github.com/id-Software/Quake.git
git clone https://github.com/letta-ai/letta.git
```

---

## 🏛️ P2 — Research & Legacy Mining
*Historical repos we mine for patterns, heritage, and origin stories. Documented in `docs/research/`.*

| # | Repo | URL | Stars | License | Mining Target | Heritage Tag |
|---|------|-----|-------|---------|---------------|--------------|
| 10 | **id Software Quake III Arena** | `https://github.com/id-Software/Quake-III-Arena` | 6.2k | GPL-2.0 | QVM, bot AI, renderer abstraction, botlib | `[id-soft: quake3-1999]` |
| 11 | **id Software Quake II** | `https://github.com/id-Software/Quake-2` | 3.8k | GPL-2.0 | Game DLL architecture, client-side prediction | `[id-soft: quake2-1997]` |
| 12 | **id Software DOOM 3** | `https://github.com/id-Software/DOOM-3` | 2.1k | GPL-3.0 | Scripting system, GUI framework, renderer | `[id-soft: doom3-2004]` |
| 13 | **Chocolate Doom** | `https://github.com/chocolate-doom/chocolate-doom` | 1.2k | GPL-2.0 | Clean source port, vanilla accuracy, portability | `[heritage: chocolate-doom]` |
| 14 | **Omega Stack Legacy** | `https://github.com/Xoe-NovAi/omega-stack-legacy` | — | Proprietary | Era 4-5 architecture, entity registry, circuit breaker | `[heritage: xnai-2025]` |
| 15 | **XNAi Legacy** | `https://github.com/Xoe-NovAi/xna-omega-legacy` | — | Proprietary | Temple-Grade standards, 5 design patterns, quality gates | `[heritage: xnai-2025]` |

**Clone Commands:**
```bash
cd third-party
git clone https://github.com/id-Software/Quake-III-Arena.git
git clone https://github.com/id-Software/Quake-2.git
git clone https://github.com/id-Software/DOOM-3.git
git clone https://github.com/chocolate-doom/chocolate-doom.git
git clone https://github.com/Xoe-NovAi/omega-stack-legacy.git
git clone https://github.com/Xoe-NovAi/xna-omega-legacy.git
```

---

## 🔧 P3 — Ecosystem & Tooling
*Adjacent projects for integration reference, comparison, or future adoption.*

| # | Repo | URL | Stars | License | Relevance |
|---|------|-----|-------|---------|-----------|
| 16 | **sqlite-vec-hnsw** | `https://github.com/brianmacy/sqlite-vec-hnsw` | — | MIT | HNSW ANN index for sqlite-vec (Strike 10) |
| 17 | **better-sqlite3** | `https://github.com/WiseLibs/better-sqlite3` | 12k | MIT | Performance patterns, WAL tuning, checkpointing |
| 18 | **litestream** | `https://github.com/benbjohnson/litestream` | 8.5k | Apache-2.0 | SQLite WAL streaming backup (Sovereign continuity) |
| 19 | **anyio-sqlite** | `https://github.com/davidbrochart/sqlite-anyio` | 6 | MIT | AnyIO-native SQLite async (M1 compliance) |

**Clone Commands:**
```bash
cd third-party
git clone https://github.com/brianmacy/sqlite-vec-hnsw.git
git clone https://github.com/WiseLibs/better-sqlite3.git
git clone https://github.com/benbjohnson/litestream.git
git clone https://github.com/davidbrochart/sqlite-anyio.git
```

---

## 📦 Clone All (Single Command)

```bash
#!/usr/bin/env bash
# clone_all_third_party.sh — Run from omega-engine root
set -euo pipefail

mkdir -p third-party
cd third-party

# P0 — Critical Dependencies
git clone https://github.com/asg017/sqlite-vec.git
git clone https://github.com/headroomlabs-ai/headroom.git
git clone https://github.com/ggml-org/llama.cpp.git
git clone https://github.com/qdrant/qdrant-client.git

# P1 — Architecture References
git clone https://github.com/mempalace/mempalace.git
git clone https://github.com/xai-org/grok-build.git
git clone https://github.com/id-Software/DOOM.git
git clone https://github.com/id-Software/Quake.git
git clone https://github.com/letta-ai/letta.git

# P2 — Research & Legacy
git clone https://github.com/id-Software/Quake-III-Arena.git
git clone https://github.com/id-Software/Quake-2.git
git clone https://github.com/id-Software/DOOM-3.git
git clone https://github.com/chocolate-doom/chocolate-doom.git
git clone https://github.com/Xoe-NovAi/omega-stack-legacy.git
git clone https://github.com/Xoe-NovAi/xna-omega-legacy.git

# P3 — Ecosystem
git clone https://github.com/brianmacy/sqlite-vec-hnsw.git
git clone https://github.com/WiseLibs/better-sqlite3.git
git clone https://github.com/benbjohnson/litestream.git
git clone https://github.com/davidbrochart/sqlite-anyio.git

echo "✅ All 19 repos cloned to third-party/"
```

---

## 🏷️ Heritage Tagging Requirements (M14)

Every P0 and P1 repo **MUST** have a corresponding vet record in:
```
data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md
```

**Minimum vet record fields:**
- `repo_url`
- `heritage_tag` (e.g., `[id-soft: doom-1993]`)
- `file_line_locations` where tag appears in Omega source
- `specific_technique` (e.g., "ZONEID zone memory allocator")
- `hardware_constraint` that necessitated original technique
- `scope_declaration`: "This tag applies to X, NOT to Y"
- `score` (1-10, minimum 7 for implementation)

**CI Gate**: `make heritage-vet` blocks merge if any `[id-soft:]` or `[heritage:]` tag lacks a vet record.

---

## 🔍 Usage Patterns

### For Roc Racoon (Legacy Mining)
```bash
# Mine id Software patterns
@roc_racoon Mine third-party/id-Software/DOOM for ZONEID implementation
@roc_racoon Mine third-party/id-Software/Quake for thinker chain pattern
@roc_racoon Mine third-party/mempalace for spatial memory architecture
```

### For Jem (Synthesis)
```bash
# Cross-reference patterns
@jem Synthesize sqlite-vec WAL patterns from third-party/sqlite-vec + better-sqlite3
@jem Cross-reference Grok Build TUI architecture with Omega TUI requirements
```

### For Verity (Compliance)
```bash
# Verify heritage tags
@verity Audit all [id-soft:] tags in src/omega/ against HERITAGE_VET_LOG.md
@verity Verify M14 compliance for headroom-ai integration
```

---

## 📋 Maintenance Protocol

| Trigger | Action |
|---------|--------|
| New dependency added to `pyproject.toml` | Add to P0, create heritage vet record |
| New architecture pattern adopted | Add to P1, document pattern mapping |
| Heritage audit (quarterly) | Run `make heritage-vet`, update vet log |
| Upstream security advisory | Pull latest, test, update vet record with CVE note |

---

## 📍 Quick Reference: Omega Source References

| Heritage Tag | Omega Source Files |
|--------------|-------------------|
| `[id-soft: doom-1993] WAD System` | `src/omega/wad/`, `config/wads/` |
| `[id-soft: doom-1993] BSP Culling` | `src/omega/engine/bsp.py` (planned) |
| `[id-soft: doom-1993] Zone Memory` | `src/omega/memory/zone.py` (planned) |
| `[heritage: sqlite-vec-2024]` | `src/omega/memory/sqlite_vec_adapter.py` |
| `[heritage: headroom-ai-2025]` | `src/omega/oracle/middleware/headroom.py` |
| `[heritage: ggml-2023] SomaticState` | `src/omega/oracle/providers/native_gguf.py` |
| `[heritage: qdrant-2021]` | `src/omega/memory/vector_adapters.py` |
| `[heritage: mempalace-2025]` | `src/omega/memory/mempalace_adapter.py` (planned) |
| `[heritage: xai-grok-build-2026]` | `docs/research/R_GROK_CLI_ARCHITECTURE.md` |
| `[id-soft: quake-1996] Thinker Chain` | `src/omega/oracle/thinker_chain.py` (planned) |

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_third_party_registry ⬡ ACTIVE*