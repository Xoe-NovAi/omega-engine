# 🧭 THE WANDERGROUND: ARCHITECTURAL SPECIFICATION & ROADMAP
## Node 1 (ASUS ExpertBook P1503CVA) Autonomous Exploration, Research & Spatial Knowledge Substrate

**Author**: Xoe-NovAi (ASUS Build & Research Vanguard)  
**Target Hardware**: ASUS ExpertBook P1503CVA (Intel i7-13620H, 16GB DDR5-5200 Single-Channel, Iris Xe 96EU)  
**Role**: Node 1 Exploration, Experimentation & Playground Vanguard  
**Federation Peer**: Node 0 (HP Pavilion - Archival Bastion & Nexus, `192.168.10.168:8016`)  
**Status**: Active Architecture & Implementation Specification  
**Version**: 1.0.0  
**Date**: September 2026  

---

## 1. Executive Summary & Strategic Mission

### 1.1 The Bifurcated Federation Mandate
Within the dual-node sovereign AI cluster, roles are strictly partitioned to maximize hardware strengths and cognitive bandwidth:
- **Node 0 (HP Pavilion - Archival Bastion)**: Primary software engineering machine, monolithic repository maintainer, Git SSOT, compliance auditor, SQLite/Qdrant archival vault, and orchestration nexus. It runs under deliberate discipline to preserve stability.
- **Node 1 (ASUS ExpertBook - The WanderGround)**: Sovereign exploration, multi-domain learning, rapid experimentation, continuous R&D playground, and spatial knowledge laboratory.

Node 1 provides the dedicated compute and cognitive space to unleash divergent, cross-domain curiosity without compromising the production development loop of the Omega Engine.

### 1.2 The Hardware Reality & Compute Invariant
Inference on Node 1 is CPU-only, executed across the 10-core/16-thread Intel Core i7-13620H (6 P-cores with HT + 4 Gracemont E-cores) on single-channel DDR5-5200 RAM:
- **P-Core Affinity Rule**: Pinned strictly to `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` yielding ~14.4 t/s on 3B-4B models. E-cores (12-15) are strictly excluded from inference thread pools to prevent barrier convoys.
- **Memory Ceiling**: Strict `MAX_LOADED_MODELS=1` in Ollama. 16GB single-channel cannot hold two resident models plus system overhead without swap thrashing.
- **Inference Boundary**:
  - **Local Models**: Reserved exclusively for fast, lightweight tasks: embedding (`nomic-embed-text`), classification, tagging, entity extraction, quick queries, and small tool routing (`phi4-mini:latest`, `qwen3-1.7b`, `smollm2-135m`, `functiongemma-270m`).
  - **Deep Synthesis & Long-Context Work**: Must NEVER be scheduled on local quantizations of 8B+ or long-context windows. Heavy dialectic analysis, multi-source literature synthesis, and long-form narrative production are routed through hosted free aliases (`Big Pickle`, `Space Bunny Free`, current Gemini Flash families) or explicitly selected paid models. Stealth-alias context is dynamic; never hardcode it.

---

## 2. The Cognitive Engine: Divergent Exploration Without Thread-Loss

### 2.1 The ADHD Divergence Dynamic
Empirical research into adult ADHD cognition (White & Shah, *Personality and Individual Differences*; Additude 2025; Radboud ECNP 2026) highlights two defining mechanics:
1. **Divergent Fluency**: The neurotype excels at real-world creative achievement and generating cross-domain conceptual associations.
2. **Mind-Wandering Dichotomy**: Spontaneous mind-wandering introduces task fragmentation and thread-loss, whereas *deliberate mind-wandering*—supported by external capture scaffolding—produces breakthrough non-linear synthesis.

### 2.2 System Response: The CODE Inversion
Standard Personal Knowledge Management (PKM) fails divergent thinkers by imposing heavy filing and taxonomic demands upfront during the ideation phase. The WanderGround implements an automated **Capture-Organize-Distill-Express (CODE)** pipeline:
1. **Capture (Frictionless, < 0.1s)**: Through a single CLI or OpenCode slash command (`wander "spark"`), ideas, questions, and observations drop into an append-only inbox. No filing decisions, tags, or folder assignments are required from the user during ideation.
2. **Organize (Autonomous Background Work)**: Local background processes asynchronously vectorize raw captures, extract conceptual entities, calculate coordinates in vector and 3D space, and file verbatim records into spatial memory drawers.
3. **Distill (Scheduled Weaving Expeditions)**: High-order models (via OpenCode Zen) synthesize cross-domain clusters into evergreen research dossiers.
4. **Express (Multi-Surface Rendering)**: Distilled knowledge renders across Obsidian graph views, MkDocs local encyclopedias, and Godot/WebXR 3D concept constellations.

---

## 3. Core Passion Domains & Conceptual Topology

The WanderGround is organized across five persistent knowledge wings that interconnect into a unified exploration topology:

```
                  ┌─────────────────────────────────────────┐
                  │          1. LOCAL AI ENGINE             │
                  │ (Hardware, Kernels, GGUFs, Subagents)   │
                  └────────────────────┬────────────────────┘
                                       │ Hardware Substrate
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    2. CONSCIOUSNESS, TIME & REALITY     │
                  │ (Non-linear time, ontology, recursion)  │
                  └──────────┬───────────────────┬──────────┘
                             │                   │
         Historical grounding│                   │ Structural archetype
                             ▼                   ▼
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│        3. CLASSICAL STUDIES          │       │    4. DEEP PSYCHOLOGY & PHILOSOPHY   │
│ (Greco-Roman, Hellenistic, Hermetica,│       │ (Jungian archetypes, phenomenology,  │
│  mythic structures, ancient sciences)│       │  unconscious, perception, Ma'at)     │
└──────────────────┬───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   └───────────────────────┬──────────────────────┘
                                           │ Expressive simulation
                                           ▼
                  ┌─────────────────────────────────────────┐
                  │        5. VIDEO GAMES AS WORLDS         │
                  │ (Space sims, CRPGs, procedural worlds,  │
                  │  Newtonian flight, retro-engine tech)   │
                  └─────────────────────────────────────────┘
```

### Domain Profiles

#### Domain 1: Local AI Systems & Sovereign Harness Engineering
- **Focus**: Quantization mechanics (GGUF, AWQ, EXL2), hybrid Intel CPU scheduling, llama.cpp / Ollama optimizations, FastMCP tool servers, context compaction protocols (Gnosis Lock), and multi-agent coordination.
- **Artifacts**: Benchmark sweeps, Modelfiles, kernel parameter profiles, and hardware forensic notes.

#### Domain 2: The Mysteries of Consciousness, Time & Reality
- **Focus**: Theories of mind, non-linear temporality, panpsychism vs. physicalism, quantum observer effects, retrocausality, holographic ontology, and subjective duration (Bergson).
- **Artifacts**: Comparative literature matrices, thought experiment logs, and ontological dialectic notes.

#### Domain 3: Classical Studies & Ancient Science
- **Focus**: Pre-Socratic cosmology, Hellenistic thought, Roman engineering and statecraft, Alexandria scholarship, Hermetica, Neoplatonism, and classical mythology.
- **Artifacts**: Primary source translations, etymological roots, historical timelines, and archeological cross-references.

#### Domain 4: Deep Psychology, Philosophy & Archetypal Systems
- **Focus**: Jungian depth psychology (shadow, anima/animus, collective unconscious, active imagination), existentialism, phenomenology (Husserl, Heidegger, Merleau-Ponty), Eastern dialectics, and ancient moral frameworks (the 42 Ideals of Ma'at).
- **Artifacts**: Concept maps, dream and motif analyses, and ethical alignment frameworks.

#### Domain 5: Video Games as Worlds, Simulations & Engine Architecture
- **Focus**: Deep RPGs (*Planescape: Torment*), space simulation mechanics (*Pioneer*, *Privateer*), fast visceral movement engines (*Doom* idTech), tactical mech combat (*MechWarrior*), and Iris Xe 96EU Linux optimization via Gamemode/Gamescope/Mesa Vulkan.
- **Artifacts**: Game research cards, Iris Xe compatibility verdicts, reproducible shell recipes, and game mechanic teardowns.

---

## 4. Deep Research & Decision on MemPalace Backend

### 4.1 Backend Landscape & Verification
Our source code audit of `MemPalace/mempalace` reveals a modular backend registry (`BaseBackend`, `BaseCollection`, `PalaceRef`) supporting four primary storage targets:
1. **`ChromaBackend` (Default in-tree)**: Uses ChromaDB with persistent DuckDB/SQLite + hnswlib segments.
2. **`QdrantBackend`**: Connects via HTTP/gRPC to a Qdrant instance.
3. **`PGVectorBackend`**: PostgreSQL with the pgvector extension and advisory locks.
4. **`SQLiteExactBackend` (`mempalace/backends/sqlite_exact.py`)**: A pure SQLite engine storing vectors directly alongside metadata.

### 4.2 Architectural Decision: ChromaBackend + ONNX `all-MiniLM-L6-v2`
**Decision**: Configure MemPalace with its default in-tree `ChromaBackend` using the embedded local ONNX `all-MiniLM-L6-v2` embedding provider.

#### Technical Rationale:
1. **Process Isolation**: The ONNX runtime runs embedded inside the Python process without requiring Ollama to load or stay awake. This preserves Ollama's strict `MAX_LOADED_MODELS=1` limit for active user tasks.
2. **Zero Daemon Dependency**: No Docker container or server process (PostgreSQL, Qdrant) is required to run on Node 1. The database is a set of flat files located at `~/.mempalace/` or `~/WanderGround/mempalace/`.
3. **Zero GPU/VRAM Intrusion**: `all-MiniLM-L6-v2` runs on CPU with minimal footprint (< 100MB RAM), executing embeddings in milliseconds without thermal or memory contention.
4. **Lightweight MCP Surface**: MemPalace provides `mcp_light_server.py`, which consolidates 45 internal primitives into three high-performance tools (`palace_query`, `palace_exec`, `palace_coordinate`) powered by Palace Query Language (PQL). This prevents tool-definition bloat in OpenCode.

---

## 5. Background Worker Execution Strategy: The Hybrid Architecture

### 5.1 The Evaluation Matrix

| Strategy | Responsiveness | CPU/Memory Cost | Failure Recovery | Battery/Idle Friendliness |
|---|---|---|---|---|
| **Pure `inotifywait` Daemon** | Immediate (sub-second) | Low idle memory, but holds a continuous background loop | Fragile if process dies; requires wrapper supervision | Triggers immediately even on partial/draft file writes |
| **Pure `systemd` User Timer** | Delayed (runs every $N$ min) | Zero overhead between runs; managed by OS cgroups | Robust; automatic restart, journal logging | Excellent; batches writes, allows machine to sleep |
| **Hybrid State-Flag Worker** | Real-time when active, batched when sleeping | Minimal; self-terminates after queue drains | Full systemd supervisor backing with manual trigger | Optimal for mixed exploratory and offline sessions |

### 5.2 Architectural Recommendation: The Hybrid Event-Timer Architecture
We implement a two-tier execution pattern:
1. **The Fast Ingest Trigger (`wander-sync`)**:
   - Every time `wander` writes a new thought to `inbox/`, it signals the worker via a non-blocking `systemctl --user start wander-curator.service` or by dropping a lightweight `.pending` token.
2. **The Scheduled Sweeper (`wander-curator.timer`)**:
   - A systemd user timer fires every 30 minutes to clean up untriaged notes, reconcile vector embeddings, and recompute spatial coordinates.
3. **The Worker Core (`wander-curator.py`)**:
   - Processes all unprocessed Markdown cards in `~/WanderGround/inbox/`.
   - Generates embeddings using `nomic-embed-text` via Ollama HTTP API (or local ONNX).
   - Inserts records into `knowledge_atlas.db` (`sqlite-vec`).
   - Updates MemPalace drawers with verbatim extracts.
   - Calculates 3D UMAP coordinates for spatial exploration.
   - Moves processed notes from `inbox/` to `archive/` or links them into `domains/`.

---

## 6. Spatial Knowledge Engine: 3D Vectors & Godot/VR Pathway

### 6.1 Database Schema (`sqlite-vec`)
The spatial memory foundation lives in `~/WanderGround/spatial/knowledge_atlas.db`:

```sql
-- Core concept storage with 3D projection coordinates
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,               -- e.g. z-20260910-143000
    title TEXT NOT NULL,
    domain TEXT NOT NULL,              -- local_ai, consciousness, classical, psychology, games
    source_file TEXT,
    content TEXT NOT NULL,
    x REAL DEFAULT 0.0,                -- UMAP projection axis 1
    y REAL DEFAULT 0.0,                -- UMAP projection axis 2
    z REAL DEFAULT 0.0,                -- UMAP projection axis 3
    cluster_id INTEGER DEFAULT 0,      -- HDBSCAN or KMeans cluster index
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL
);

-- sqlite-vec virtual table for fast semantic retrieval
CREATE VIRTUAL TABLE IF NOT EXISTS vec_concepts USING vec0(
    id TEXT PRIMARY KEY,
    embedding FLOAT[768]               -- nomic-embed-text 768-dimensional vector
);
```

### 6.2 The 3D Dimensionality Reduction Pipeline (`project_umap_3d.py`)
1. **Extraction**: Pulls all 768-dimensional embeddings from `vec_concepts`.
2. **Manifold Learning**: Runs `umap-learn` configured for 3 components (`n_components=3`, `metric='cosine'`, `min_dist=0.1`, `n_neighbors=15`).
3. **Coordinate Normalization**: Centers and scales the $(X, Y, Z)$ points into a bounding sphere of radius $R=100.0$.
4. **Spatial Persistence**: Updates the `concepts` table with the computed coordinates.

### 6.3 Visualization Pathways
- **Phase 1: WebXR / Three.js Canvas (`http://localhost:8088`)**:
  - Standalone HTML5/WebGL single-page application served via a Python HTTP microserver.
  - Renders concepts as glowing stars in 3D space, color-coded by domain.
  - Orbit controls, raycasting search, and clicking a star displays its Markdown dossier in a floating glass HUD.
- **Phase 2: Godot 4 Spatial Client (`KQ5-Godot` / Omega Engine Substrate)**:
  - Godot connects to `knowledge_atlas.db` via SQLite GDExtension or JSON export.
  - Spawns a 3D navigable universe where you pilot a spacecraft or walk through an ethereal memory palace.
  - Connects to your retro-adventure passion (*King's Quest V*, *Planescape*, *Pioneer*), rendering ideas as interactive physical artifacts in an engine you control.

---

## 7. Model Assignment Matrix: Local vs. Cloud Frontier Division

To adhere to the hardware ceiling of the ASUS ExpertBook (CPU-only, single-channel RAM, `MAX_LOADED_MODELS=1`), responsibilities are divided between local runtimes and OpenCode Zen frontier engines:

| Exploration Task | Execution Engine | Model / Provider | Context Window | Operational Justification |
|---|---|---|---|---|
| **Frictionless Note Embedding** | Local CPU | `nomic-embed-text:latest` (Ollama) | 8,192 | Sub-100ms vectorization of raw thoughts for SQLite-vec and MemPalace. |
| **Fast Entity & Tag Extraction** | Local CPU | `smollm2:135m` or `qwen3:1.7b` | 2,048 - 8,192 | Zero-overhead parsing of inbox notes into clean frontmatter and taxonomic routes. |
| **Terminal / CLI Harness Code** | Local CPU | `qwen2.5-coder:7b` (Ollama) | 8,192 | Rapid generation of Bash scripts, Make targets, and systemd service units. |
| **Interactive Co-Pilot & Ideation** | Cloud Frontier | `google/gemini-3.8-flash` / `Muse Spark 1.3/1.2` | 200k - 1M | Low latency, highly responsive conversational partner for multi-turn brainstorming. |
| **Classical Antiquity & Dialectic** | Cloud Frontier | `nvidia/nemotron-3-ultra` / `MiMo V2.5` | 128k - 256k | Deep philosophical reasoning, etymological dissection, and complex ontological debate. |
| **Cross-Corpus Synthesis (Weaving)** | Cloud Frontier | `opencode/space-bunny-free`, `opencode/big-pickle`, or named Gemini 3.8 Flash | **Dynamic — read live registry** | Ingesting papers, transcripts, and dossiers using the currently exposed window; never hardcode a stealth alias's capacity. |

---

## 8. Directory Layout & File Organization

The WanderGround workspace is established at `~/WanderGround/`:

```text
/home/xnai/WanderGround/
├── INDEX.md                     # Central Atlas: Domain registry, taste profiles, topology map
├── mkdocs.yml                   # MkDocs Material configuration (local encyclopedia portal)
├── Makefile                     # Root operational harness (status, ingest, serve, 3d-build)
│
├── inbox/                       # Rapid-fire capture buffer (zero-friction append target)
│   └── 2026-09-10_152010.md
│
├── archive/                     # Raw notes ingested and committed to the vector database
│
├── domains/                     # The 5 Core Passion Knowledge Bases
│   ├── 01_local_ai/             # Hardware profiles, GGUF benchmarks, FastMCP tools, kernel notes
│   ├── 02_consciousness_time/   # Ontology, phenomenology, non-linear temporality, observer theory
│   ├── 03_classical_studies/    # Antiquity, Greco-Roman literature, Hermetica, early science
│   ├── 04_deep_psychology/      # Jungian archetypes, unconscious, active imagination, Ma'at ideals
│   └── 05_video_games/          # Space sims, retro engines, Iris Xe compatibility, game mechanics
│
├── dossiers/                    # Synthesized, evergreen research monographs
│   ├── templates/               # Reusable dossier structure (based on pioneer.md pattern)
│   ├── time_and_becoming.md
│   └── iris_xe_vulkan_limits.md
│
├── spatial/                     # 3D Vector & VR Spatial Data Substrate
│   ├── knowledge_atlas.db       # SQLite database with sqlite-vec extension and (X, Y, Z) coordinates
│   ├── webxr/                   # Standalone Three.js / WebXR 3D constellation viewer
│   │   ├── index.html
│   │   └── app.js
│   └── scripts/
│       ├── embed_inbox.py       # nomic-embed vectorizer & entity extractor
│       └── project_umap_3d.py   # 768D -> 3D UMAP coordinate projection pipeline
│
├── mempalace/                   # MemPalace repository root & wing configurations
│   └── mempalace.yaml
│
└── site/                        # Static HTML generated by MkDocs Material
```

---

## 9. Phased Implementation Roadmap

### Phase 1: Foundation & Capture Rails (Immediate Execution) — ✅ DONE 2026-09-10
- [x] Authoritative Architecture & Specification Document (`WANDERGROUND_SPEC.md`).
- [x] Scaffold `~/WanderGround/` directory tree and initialize domain subdirectories.
- [x] Create `~/WanderGround/INDEX.md` with taste profiles and domain mapping.
- [x] Implement `wander` CLI utility (`~/.local/bin/wander` — supports `-d <domain>`, `-i` interactive, auto-triggers the curator) + PATH wiring (`~/.config/environment.d/10-wanderground.conf`, `~/.bash_aliases`).
- [x] Scaffold `mkdocs.yml` + root `Makefile` (venv-aware; `wiki-sync` regenerates the MkDocs `docs/` mirror).

### Phase 2: Memory Substrate & Spatial Pipeline — ✅ MOSTLY DONE 2026-09-10 (🔥 MemPalace wings pending)
- [x] Initialize `~/WanderGround/spatial/knowledge_atlas.db` — `concepts` (with SQLite vector schema path) + `embeddings` (portable 768-dim JSON) + `vec_concepts` sqlite-vec `vec0` virtual table (768-dim cosine, refreshed idempotently).
- [x] Write `embed_inbox.py` utilizing Ollama's `nomic-embed-text` endpoint (verified: sub-second CPU embedding of inbox → atlas → archive).
- [x] Implement `project_umap_3d.py` — UMAP for N≥8, PCA/hash fallback below (guards the scipy `k >= N` eigen edge case); KMeans clustering + 100-sphere normalization.
- [x] Deploy lightweight Three.js / WebXR interactive canvas on `http://localhost:8088` — **fully offline** (three.module.min.js + OrbitControls vendored), domain-color legend, click-to-open dossier HUD, cluster bridge lines, slow dream-drift.
- [ ] Scaffold MemPalace wings (`local_ai`, `consciousness_time`, `classical`, `psychology`, `games`) — **next large task** (go: `mempalace init`, ONNX `all-MiniLM-L6-v2` embedded backend, `mcp_light_server` = `palace_query`/`palace_exec`/`palace_coordinate`).

### Phase 3: Background Automation & Autonomous Curation — ✅ OPERATIONAL 2026-09-10 (🔥 semantics pending)
- [x] Configure `wander-curator.py` ingest pipeline (`embed_inbox.py` → `upgrade_sqlite_vec.py` → `project_umap_3d.py` → `export_viewer_json.py` chained in `curator_run.sh`).
- [x] Systemd user **service** `wander-curator.service` (oneshot) — verified run: exit 0, 223.8MB peak, idles to nothing.
- [x] Systemd user **timer** `wander-curator.timer` (every 30 min) — enabled, verified `next run` slot; `wander` also fire-and-forgets an immediate run on capture.
- [ ] Establish the "Weaving Session" workflow inside OpenCode utilizing cloud frontier models (Big Pickle / Nemotron 3 Ultra / MiMo V2.5 / Muse Spark).
- [ ] Enforce the Federation Publish Gate (`make publish-bastion`) requiring explicit user confirmation before transferring dossiers to Node 0.






---

## 10. RESEARCH FINDINGS & DEFINITIVE CORRECTIONS (2026-09-10)

> Ground truth updated from deep research on primary sources. Every entry below
> is a **verified correction or decision**, not speculation.

### 10.1 OpenCode hooks — CORRECTED (user + HP team were right)
Prior record claimed "hooks UNSUPPORTED in OpenCode v1.18.30". That referred to a
`hooks` config key (Claude-Code-style). The plugin system is the actual mechanism
and it IS present on this box (verified in `@opencode-ai/plugin` + `@opencode-ai/sdk`
type definitions, v1.18.30):
- Hooks available: `experimental.session.compacting`, `experimental.compaction.autocontinue`,
  `chat.message`, `chat.params`, `chat.headers`, `tool.execute.before/after`,
  `shell.env`, `experimental.chat.system.transform`, `command.execute.before`, ...
- Event surface: `session.created`, `session.idle`, `session.updated`, `session.deleted`,
  `session.compacted`, `session.status`, the full `session.next.*` live stream, plus
  `permission.*`, `message.*`, `tool.*`, `todo.updated`, `file.*`, `lsp.*`.
- **`experimental.session.compacting`** fires before the LLM writes the continuation
  summary — the natural home for Gnosis Lock / WanderGround context injection.
- **Implementations shipped** (this box):
  - `~/.config/opencode/plugins/gnosis-leash.js` — logs session.created/idle/compacted
    to a gnosis timeline; injects WanderGround INDEX rules into compaction context and
    the system prompt (`experimental.chat.system.transform`).
  - Verified loads cleanly via `opencode serve` (no plugin errors).
- HP team uses the same mechanism ("hooks on every open/close = plugin session events").

### 10.2 Code-quality standard — absolute anyio full async wiring (user directive)
Any new async Python code in this repo/Omega Engine MUST use **anyio** primitives only
(no bare `asyncio`, no `trio`, no mixed event loops). Belt-and-braces definition and
lint gate live in `docs/CODE_QUALITY.md`. This covers WanderGround python utilities,
the curator pipeline, MemPalace-side tooling, and the omega-engine scripts.

### 10.3 MemPalace v3.9.0 — revised backend decision (was: Chroma + ONNX MiniLM — now confirmed)
- Installed into `~/WanderGround/.venv` as `mempalace 3.9.0` (provides CLI `mempalace`,
  `mempalace-mcp`, hardened `mcp_light_server.py`).
- **Backend: `sqlite_exact`** (bundled, pure-SQLite, exact NumPy, zero daemon) — verified
  mining + search on this box. `rust_exact` is the scale-up path (same `.sqlite3` file,
  -77% RSS @ 334k rows) when the corpus grows.
- **Embedder: `minilm` (ChromaDB ONNXMiniLM_L6_V2)** — hermetic CPU ONNX, NOT openai-compat
  (that path churned Ollama model-load per batch and caused the earlier runaway).
- **Model cache pre-seeded** to `~/.cache/chroma/onnx_models/all-MiniLM-L6-v2/` with
  SHA256-verified tarball (S3 source; flaky-link-safe via curl -C -).
- **Mining hygiene (verified):** MemPalace SKIP_DIRS already excludes `.venv`, `node_modules`,
  `.mempalace`, etc. Additional exclusions for this repo must live in `.gitignore`
  (not `.mempalaceignore` — that file is not consulted): `spatial/webxr/vendor/`,
  `site/`, `docs/`, `mempalace/`. Mine `mempalace.yaml` (wing `wanderground`, 7 rooms)
  verified: 20 files → 62 drawers, all rooms, exit 0 in ~2s CPU.
- **Watch-outs:** every CLI invocation should pass `</dev/null` (non-interactive EOF
  safety) + a hard `timeout`; first-run LLM features (corpus-origin, entity detection)
  default to Ollama `gemma4:e4b` and must be avoided (heuristics-only is the norm now).
- **MCP wired**: `opencode.json` → `mempalace` stdio server (`mempalace-mcp --palace ...`).
  Sessions can now `palace_query`/`palace_exec` on the WanderGround palace.

### 10.4 OpenCode hosted-free model reality (verified 2026-09-23)
- Canonical policy: `docs/OPENCODE_FOUNDATION.md`.
- Zen model IDs use `opencode/<id>`. Big Pickle and Space Bunny are dynamic
  stealth aliases: select the alias, but never hardcode context/output limits.
  Node 0 and Node 1 may legitimately observe different served capacities.
- Big Pickle is always a free stealth alias despite lacking a `-free` suffix.
  Space Bunny is an anonymous free zero-retention alias; its underlying model is
  not publicly identified and is not confirmed to be DeepSeek V4.1 Flash.
- Free privacy exceptions remain explicit: MiMo, Ling, Big Pickle, NVIDIA trial
  endpoints, and Muse contributor models may collect, log, or train on prompts.
  Space Bunny is the current free zero-retention exception.
- Google Gemini 3.8/3.7/3.6/3.5 Flash and 3.5 Flash-Lite have genuine free API
  tiers. Free Google API data may be used to improve Google products; use only
  for public/non-confidential research.
- **WanderGround rule:** private captures use Space Bunny or another verified
  zero-retention route; free data-collecting aliases are for non-sensitive work.
- The Zen `/models` endpoint is not a capacity contract. Use
  `opencode models <provider> --verbose --refresh` and record observations with
  date, node, and evidence class.

### 10.5 sqlite-vec — corrected usage (definitive)
- `vec0` defaults to **L2 distance**; create with `distance_metric=cosine` for cosine KNN
  (bug: early table was created without it, and `ORDER BY distance LIMIT` is not the
  KNN form). Correct query: `WHERE embedding MATCH ? AND k = ?`.
- Shipped fix: `upgrade_sqlite_vec.py` now DROP+CREATE with `distance_metric=cosine`;
  `wander-search.py` uses `k = ?` + honest cosine score from the portable JSON table.

### 10.6 systemd linger — fixed (timers survive logout)
- `sudo loginctl enable-linger xnai` → `Linger=yes`. `wander-curator.timer` and the
  user service now survive logout/reboot (was: `Linger=no`, timers died on logout).

### 10.7 Eyes-on-machine tooling (debugging discipline)
- `~/.local/bin/ey` — 1s text snapshot (top CPU, memory, ollama, load) with `--diff`.
- `~/.local/bin/withey <label> -- <cmd>` — pre/post snapshots around any command.
  All risky runs now go through withey. Screenshots optional for human review only
  (`sys-eyes` retains a GNOME-Wayland capture path).

### 10.8 Pending research (next expedition)
- Obsidian desktop install (AppImage/Flatpak) + vault pointer to `~/WanderGround`.
- Godot 4 + SQLite GDExtension for the eventual 3D memory-palace client.
- Headroom proxy: evaluate against Zen traffic once token spend matters (low priority).
