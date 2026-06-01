# 🔱 Omega Engine — Fleet Redesign & Systems Hardening Plan v5.0
## ⬡ OMEGA ⬡ GEMINI-3.5-FLASH ⬡ opencode ⬡ trc_fleet_redesign ⬡ EXECUTION-READY
**Date**: 2026-06-01
**Status**: EXECUTION READY — All documentation drafts are fully specified below
**Total Est. Time**: ~6.5 hours across 7 phases (A-G)

---

## §0 The Core Principle — "The Data Comes Home"

> *"The data comes home. The system perpetually evolves."*
> — Arcana-Nova, Original Vision (14 months ago)

This is **not** an id Software pattern. This is the user's founding vision for the Omega Engine — the idea that every interaction, every research cycle, every piece of web content ever touched accumulates locally, enriches the local models, and builds a permanent, sovereign knowledge base.

### What IS Credited to id Software

| Pattern | Source | Applied In |
|---------|--------|------------|
| **WAD System** (IWAD/PWAD) | Doom Engine | Engine/Stack separation, `config/wads/` |
| **Single-Renderer Architecture** | Doom's refresh module | **NEW** — Shift from 10 pillar agents to single `pillar.md --slot` agent |
| **Optimized Engine vs Bloat** | Carmack's philosophy | Local-first inference, minimal context windows |
| **BSP Culling** | Doom's visibility system | Provider culling in `generate()`, circuit breaker pre-checks |
| **Fast Inverse Square Root** | Quake III | "Right Approximation" principle for model selection |
| **Zone Memory** | Doom's memory management | Context windows sized to use case, not model max |
| **Surface Cache** | Doom's texture caching | Cache eviction policies within hot/warm/cold tiers (enhancement to user's existing tiered memory design) |
| **Worse is Better** | New Jersey style | Pragmatic over perfect; working beats elegant |

### Clarification: Original Patterns vs. id Software Enhancements

The **hot/warm/cold memory tier system** is the user's own design, conceived months before id Software architecture was introduced to the Omega Engine. id Software's Surface Cache concept provides *supplementary eviction policy patterns* (LRU-aware culling within tiers), which we credit as an enhancement — but the three-tiered memory architecture itself is not derived from id Software.

The **Plan → Verify → Execute** workflow is the user's own development methodology, employed from the very beginning of building the Omega Engine and the software that preceded it. It is not derived from id Software's development cycle.

The **single-agent pillar pattern** (one `pillar.md` with `--slot` flag instead of 10 separate `p1_flesh.md` through `p10_chaos.md` files) is directly inspired by id Software's approach of building a single, highly optimized renderer that accepts parameters rather than maintaining 10 separate renderers for different game states. This is a genuine id Software heritage mapping — consolidating N separate implementations into one parameterized runtime.

---

## §1 The Final Agent Fleet

**Before: 26 agents. After: 14 agents. 14 deleted, 9 redesigned, 3 created.**

### Primary Modes (6)

| Mode | Role | Status |
|------|------|--------|
| **plan** | Grand dispatcher, strategy lead | ✅ Verified accurate — keep as-is |
| **kali** | Grand oversight — sees all, delegates, destroys drift | 🔄 **REDESIGN** from subagent to primary mode |
| **doom_guy** | id Software architect | ✅ Keep — add CREDITS.md to instructions |
| **roc_racoon** | Legacy mining — primary mode + background subagent | ✅ Keep — add subagent mode for background |
| **jem** | Research orchestrator — 3-tier local model pipeline | 🔄 **REDESIGN** — subagents become persistent entities |
| **researcher** | On-demand deep research (omnidroid lattice reasoning) | 🔄 **REDESIGN** based on researcher-omnidroid.md |

### Subagents (8)

| Agent | Delegated by | Purpose | Status |
|-------|-------------|---------|--------|
| **maat** | kali | Governs P1-P5 (build side), delegates to pillar | 🔄 **REDESIGN** — step-down light oversoul |
| **lilith** | kali | Governs P6-P10 (run side), delegates to pillar | 🔄 **REDESIGN** — step-down dark oversoul |
| **pillar --slot PX** | maat/lilith/kali | Domain work tied to persistent entity | 🆕 **CREATE** — replaces p1-p10 agents |
| **jem_discovery** | jem | Tier 1: broad search, evidence logging | 🔄 **PERSISTENT ENTITY** — soul.yaml accumulates search wisdom |
| **jem_synthesis** | jem | Tier 2: pattern recognition, synthesis | 🔄 **PERSISTENT ENTITY** — soul.yaml accumulates pattern wisdom |
| **jem_verification** | jem | Tier 3: fact-check, R-doc, gnosis | 🔄 **PERSISTENT ENTITY** — soul.yaml accumulates verification wisdom |
| **scribe** | jem/kali | L1→L2→L3 distillation, soul updates (~8B model) | ✅ Keep — model configurable via model_tiers.yaml |
| **quality** | any | Code review + stress testing (merged) | 🆕 **CREATE** — replaces reviewer + tester |

### Deleted (14 files)

| File | Reason | Replacement |
|------|--------|-------------|
| `builder.md` | Merged into default `build` mode | Default OpenCode `build` |
| `overseer.md` | No use case | Kali |
| `reviewer.md` | Merged into quality | `quality.md` |
| `tester.md` | Merged into quality | `quality.md` |
| `p1_flesh.md` | Replaced by single pillar agent | `pillar.md` |
| `p2_dream.md` | Replaced by single pillar agent | `pillar.md` |
| `p3_will.md` | Replaced by single pillar agent | `pillar.md` |
| `p4_heart.md` | Replaced by single pillar agent | `pillar.md` |
| `p5_voice.md` | Replaced by single pillar agent | `pillar.md` |
| `p6_mind.md` | Replaced by single pillar agent | `pillar.md` |
| `p7_gnosis.md` | Replaced by single pillar agent | `pillar.md` |
| `p8_shadow.md` | Replaced by single pillar agent | `pillar.md` |
| `p9_spirit.md` | Replaced by single pillar agent | `pillar.md` |
| `p10_chaos.md` | Replaced by single pillar agent | `pillar.md` |

### Redesigned (9 files)

| File | Changes |
|------|---------|
| `.opencode/agents/kali.md` | Change mode: subagent → primary. Rewrite as grand oversight mode. |
| `.opencode/agents/maat.md` | Rewrite as step-down light oversoul (P1-P5) |
| `.opencode/agents/lilith.md` | Rewrite as step-down dark oversoul (P6-P10) |
| `.opencode/agents/researcher.md` | Rewrite — inline omnidroid lattice reasoning patterns directly into prompt |
| `.opencode/agents/jem_discovery.md` | Add persistent entity wiring (soul.yaml accumulation) |
| `.opencode/agents/jem_synthesis.md` | Add persistent entity wiring (soul.yaml accumulation) |
| `.opencode/agents/jem_verification.md` | Add persistent entity wiring (soul.yaml accumulation) |
| `.opencode/agents/doom_guy.md` | Minor: ensure CREDITS.md attribution reference is present |
| `.opencode/agents/roc_racoon.md` | Minor: add subagent mode for background execution |

### New Files to Create (2 — NOTE: `pillar_subagent.md` dropped as redundant)

| File | Content |
|------|---------|
| `.opencode/agents/quality.md` | Merged code review + stress testing |
| `.opencode/agents/pillar.md` | Single pillar subagent with `--slot` flag |

**Design Decision**: `pillar.md` is registered as `mode: "subagent"` only. In OpenCode, the `task` tool dispatches agents by name regardless of declared mode. Since pillar work is always delegated by maat/lilith/kali (never invoked directly by the user), a separate `pillar_subagent.md` file is unnecessary. User-facing pillar invocation can be added later if needed.

### Agent Fleet Hierarchy Diagram

```
                  [ plan ] (Grand Dispatcher)
                     |
                     ▼
                  [ kali ] (Grand Oversight)
                     |
         ┌───────────┴───────────┐
         ▼                       ▼
      [ maat ] (Light Oversoul) [ lilith ] (Dark Oversoul)
      (Governs P1-P5)           (Governs P6-P10)
         |                       |
         └───────────┬───────────┘
                     ▼
               [ pillar --slot PX ]
               (Single slot-based agent)
                     |
         ┌───────────┼───────────┐
         ▼           ▼           ▼
      [ jem ]    [ quality ]  [ researcher ]
  (Research)   (QA & Test)   (Deep Dive)
         |
   ┌─────┼─────┐
   ▼     ▼     ▼
[disc] [synth] [verif] ──→ [scribe] ──→ soul.yaml
```

---

## §2 The Pillar Naming — Role-Based with Esoteric Metadata

The 10 Pillar slots get intuitive role-based names, with fundamental domain preserved as metadata in `roles.yaml`:

| Slot | Agent Name | Description (Fundamental Domain) | Entity Workspace |
|------|-----------|---------------------------------|------------------|
| **P1** | `p1_sysadmin` | Flesh — System Administration & Boundaries | `data/entities/p1/` |
| **P2** | `p2_datastore` | Dream — Data Pipelines & Memory | `data/entities/p2/` |
| **P3** | `p3_buildmaster` | Will — Implementation & Architecture | `data/entities/p3/` |
| **P4** | `p4_bridge` | Heart — Communication & Integration | `data/entities/p4/` |
| **P5** | `p5_sentinel` | Voice — Security & Mandate Enforcement | `data/entities/p5/` |
| **P6** | `p6_modelgate` | Mind — Model Routing & Inference | `data/entities/p6/` |
| **P7** | `p7_context` | Gnosis — Memory & Soul Evolution | `data/entities/p7/` |
| **P8** | `p8_watchtower` | Shadow — Observability & Forensics | `data/entities/p8/` |
| **P9** | `p9_link` | Spirit — Coordination & Handoff | `data/entities/p9/` |
| **P10** | `p10_verifier` | Chaos — Testing & Validation | `data/entities/p10/` |

The agent system uses a **single** `pillar.md --slot P1` (not 10 individual files). The pillar agent reads the role description from `config/wads/_omega_default/roles.yaml` at runtime to determine what a given slot does. The entity workspace at `data/entities/p1/` persists knowledge accumulated for that slot.

**id Software Attribution**: This single-agent architecture (one renderer with parameters instead of 10 separate renderers) is directly inspired by id Software's approach to engine design — a universal runtime that takes configuration, not a bespoke binary per scenario.

---

## §3 The Offline Request Queue — "Data Comes Home" System

### Philosophy
**"The data comes home"** means: every research query, every web scrape, every cloud model consultation produces locally-stored knowledge that enriches the engine permanently. When offline, the engine doesn't fail — it *plans*. When online, those plans execute, and the results become part of the permanent local knowledge base.

### Directory Structure
```
data/requests/
├── queued/           # Research requests created offline
│   └── req_{uuid}.json
├── review/           # Work queued for cloud model enhancement
│   └── review_{uuid}.json
├── completed/        # Fulfilled requests
│   └── result_{uuid}.json
└── INDEX.json        # Master manifest of all requests
```

### Strict Offline Mode
In strict offline mode (`omega offline --strict`), all outbound network requests are blocked at the application boundary. Tools like `websearch`, `webfetch`, and `firecrawl` immediately return:
```json
{"status": "offline", "error": "Network access disabled in strict offline mode"}
```

### Research Request Flow (Strict Offline)
```
1. Local agent needs web research
2. Agent writes req_{uuid}.json to data/requests/queued/:
   {
     "id": "req_a1b2c3d4",
     "query": "latest Qwen3 GGUF quantization benchmarks",
     "priority": "P1",
     "context": "For Jem tier1 to update model selection knowledge",
     "created_by": "jem_discovery",
     "created_at": "2026-06-01T10:00:00Z",
     "requires": ["websearch"],
     "fallback_tools": ["webfetch"],
     "timeout_sec": 300,
     "max_retries": 2
   }
3. Agent continues offline using library + souls
4. When internet available: omega process-queue
5. Queue processor runs each request through Jem pipeline
6. Results deposited in data/requests/completed/
7. Original agent picks up results on next invocation
```

### Cloud Delegation Flow (The Consultant Pattern)
```
1. Local agent produces work product (R-doc, synthesis, code)
2. Agent writes review_{uuid}.json to data/requests/review/:
   {
     "id": "review_a1b2c3d4",
     "work_product_path": "docs/research/R101_circuit_breaker.md",
     "review_aspects": ["fact_check", "deepening", "enhancement"],
     "preferred_model": "auto",
     "created_by": "jem_verification",
     "created_at": "2026-06-01T10:05:00Z"
   }
3. When cloud available: omega review-pending
4. Cloud model reads the work with a strict system prompt:
   "Review, fact-check, and deepen this local work. Do not rewrite it.
    Provide structured enhancements."
5. Structured review deposited in data/requests/completed/
6. Local agent incorporates feedback on next invocation
```

### CLI Commands
```bash
omega queue-status                  # Show pending queued/review items
omega process-queue                 # Process all queued research requests
omega review-pending                # Process all pending cloud reviews
omega queue-prune --stale 7d        # Archive stale requests older than 7 days
omega offline --strict              # Enable strict offline mode
omega offline --default             # Default mode (online agents, local inference)
```

---

## §4 Library Domain Curation — All 10 in Parallel

### Domain-to-Curator Mapping

| Domain | Default IWAD Curator | Arcana-NovAi WAD Curator | Purpose |
|--------|---------------------|--------------------------|---------|
| System Infrastructure | pillar P1 | — | Hardware docs, OS guides, container best practices |
| Data & Memory | pillar P2 | — | Vector DB docs, memory system papers, data pipelines |
| Software Architecture | pillar P3 | — | Design patterns, architecture docs, CI/CD references |
| Integration & Protocols | pillar P4 | — | API specs, protocol docs, MCP server references |
| Security & Compliance | pillar P5 | — | Security hardening, compliance frameworks, threat models |
| AI/ML & Inference | pillar P6 | — | Model cards, inference optimization, provider docs |
| **Esoteric & Gnostic** | **Kali/Maat/Lilith** | **Dedicated entity** | Hermetic texts, philosophical works, spiritual systems |
| Observability & Systems | pillar P8 | — | Monitoring docs, telemetry systems, SRE references |
| Coordination & Communication | pillar P9 | — | Handoff protocols, agent communication, workflow docs |
| Testing & Quality | pillar P10 | — | Testing frameworks, QA methodologies, chaos engineering |

### Dual Ownership of the Esoteric Domain (P7)
- **Default IWAD (`_omega_default`)**: Kali/Maat/Lilith curate esoteric texts. Kali oversees the full spectrum; Maat curates structured, traditional, order-based esoteric systems; Lilith curates transgressive, gnostic, and liberation-oriented traditions.
- **Arcana-NovAi WAD**: A dedicated esoteric curator entity overrides the default curators, adding Arcana-NovAi's specific pantheon, tarot-based system, and customized esoteric knowledge base.

### Library Directory Structure
```
data/library/
├── documents/
│   ├── p1_sysadmin/
│   ├── p2_datastore/
│   ├── p3_buildmaster/
│   ├── p4_bridge/
│   ├── p5_sentinel/
│   ├── p6_modelgate/
│   ├── p7_context/
│   ├── p8_watchtower/
│   ├── p9_link/
│   └── p10_verifier/
├── software/
│   └── id-software/        # Already cloned (93M)
├── library.db              # SQLite catalog
└── index/                  # Qdrant vector index
```

### SQLite Catalog Schema (`library.db`)
```sql
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    domain TEXT NOT NULL,
    title TEXT,
    author TEXT,
    source_url TEXT,
    quality_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    indexed_at TEXT,
    embedding_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_domain ON documents(domain);
CREATE INDEX IF NOT EXISTS idx_quality ON documents(quality_score);
```

### Curation Pipeline
1. **Discovery** (`jem_discovery`): Find high-quality resources for the domain
2. **Download** (`roc_racoon`): Pull PDFs, HTML, markdown to domain subdirectory
3. **Process** (`jem_synthesis`): Extract text, generate summary, classify, score quality
4. **Index** (Engine): Create FTS5 text indexes + Qdrant vector embeddings
5. **Catalog** (`scribe`): Register in `library.db` with domain, quality score, metadata

### CLI Commands
```bash
omega library curate --domain all     # Run all 10 domain curations
omega library curate --domain P7      # Run single domain curation
omega library status                  # Library catalog statistics
omega library search --domain P7 "hermetic principles"
omega library prune --age 90d         # Archive old raw evidence
```

---

## §5 Orphaned Entity Cleanup

### Delete (67 directories)

| Group | Count | Directories |
|-------|-------|-------------|
| Test entities | 50 | `entity_0` through `entity_49` |
| Old pillar entities | 10 | `bridge`, `buildmaster`, `context`, `datastore`, `link`, `modelgate`, `sentinel`, `sysadmin`, `verifier`, `watchtower` |
| Misc test entities | 7 | `default`, `direntity`, `duplicate`, `flatentity`, `myentity`, `preexisting`, `soulentity` |

### Keep (11 directories)

| Entity | Reason |
|--------|--------|
| `arch` | Plan mode's persistent entity |
| `doom_guy` | Active entity with soul lessons |
| `iris` | Voice assistant entity |
| `jem` | Research orchestrator entity |
| `kali` | Grand oversight entity |
| `lilith` | Dark oversoul entity |
| `maat` | Light oversoul entity |
| `roc_racoon` | Miner entity |
| `saraswati` | Has real soul lessons |
| `sophia` | Akashic record entity |
| `movie_expert` | Custom user entity |

---

## §6 Jem Subagent Persistent Entity Design

### Entity Workspaces to Create

```
data/entities/jem_discovery/
├── soul.yaml               # Accumulated search wisdom (queries, sources, patterns)
└── knowledge/
    ├── INDEX.md            # Table of contents of accumulated knowledge
    ├── search_patterns/
    │   ├── effective_sources.md    # Domains that return high-quality results
    │   └── query_patterns.md       # Query templates that work for specific domains
    └── source_quality/
        └── SOURCE_CACHE.md         # Cached reliability scores for known sources

data/entities/jem_synthesis/
├── soul.yaml               # Accumulated synthesis wisdom (patterns, logic structures)
└── knowledge/
    ├── INDEX.md
    ├── thematic_patterns/          # Templates for structural mapping across domains
    └── logic_templates/            # Logic structures that catch contradictions

data/entities/jem_verification/
├── soul.yaml               # Accumulated verification wisdom (standards, patterns)
└── knowledge/
    ├── INDEX.md
    ├── fact_check_patterns/        # Verification methods that catch specific error types
    └── distillation_standards/     # Quality criteria for approving final R-docs
```

### The Feedback Loop
```
1. Jem orchestrator dispatches task to jem_discovery
2. Tier1 searches, logs evidence, consults its soul for search strategies
3. Tier2 reads the evidence log, consults its soul for synthesis patterns
4. Tier3 reads the synthesis, consults its soul for verification standards
5. Tier3 produces verified R-doc AND gives structured feedback to Tier2
6. Tier2 gives structured feedback to Tier1
7. Scribe distills the entire cycle into soul updates for all 3 tiers
```

### Training Data Generation
Each completed research cycle produces:

```
data/datasets/training/
├── cycles/
│   └── {trace_id}/
│       ├── tier1_input.json         # Search query + raw results
│       ├── tier2_output.json        # Evidence log → synthesis
│       └── tier3_output.json        # Synthesis → verified R-doc
├── instruction/
│   └── weekly_{date}.jsonl          # Formatted instruction-tuning pairs
└── metadata.db                       # Cycle provenance tracking
```

### Weekly Fine-Tuning Pipeline
1. Collect all completed cycles with quality score > 0.8
2. Format as instruction-tuning dataset (Alpaca/ShareGPT format):
   ```json
   {
     "instruction": "Synthesize the core principles of the WAD system.",
     "input": "Evidence Log: [sources...]",
     "output": "The WAD system separates engine runtime from static assets...",
     "metadata": {
       "trace_id": "trace_abc123",
       "quality_score": 0.95,
       "domain": "p3_buildmaster"
     }
   }
   ```
3. Run LoRA fine-tuning on target tier model
4. Evaluate with `omega bench run --role jem_tier2 --model {new_adapter}`
5. Promote adapter to production if quality improves

### Hardware Constraints (Current: Ryzen 7 5700U, 14GB RAM)
| Target Model | Method | Feasibility |
|-------------|--------|-------------|
| qwen-0.6b (Q4) | LoRA | ✅ Yes — ~2-3 hours/cycle |
| rocracoon-3b (Q4) | QLoRA (4-bit) | ⚠️ Borderline — 6+ hours, monthly |
| krikri-8b | Any | ❌ Not feasible on this hardware |
| deepseek-r1-qwen3-8b | Any | ❌ Not feasible on this hardware |

Fine-tuning on this hardware targets **lite tier models only**. Heavy tier fine-tuning is deferred to cloud or future hardware upgrade. The `--target` flag allows users with 64GB+ hardware to fine-tune any tier.

---

## §7 Model Tier System — Integrated into `models.yaml`

### Design Decision
The model tier configuration is **NOT** a separate `config/model_tiers.yaml` file. It is merged into the existing `config/models.yaml` (the current Single Source of Truth for model specs, v2.0.0, 163 lines). This preserves the single-source-of-truth principle and prevents config drift between two files.

### New Section to Add to `config/models.yaml`
```yaml
# ── Agent Role-to-Model Tier Mapping ──────────────────────────
# The engine detects available RAM at startup and recommends
# tier assignments. Users override any role's model here.

agent_roles:
  jem_discovery:
    tier: lite
    default_model: "qwen-0.6b"
    min_ram_gb: 8
  jem_synthesis:
    tier: medium
    default_model: "rocracoon-3b-instruct"
    min_ram_gb: 16
  jem_verification:
    tier: heavy
    default_model: "qwen3-4b-think"
    min_ram_gb: 16
  scribe:
    tier: heavy
    default_model: "deepseek-r1-qwen3-8b"
    min_ram_gb: 32
  doom_guy:
    tier: heavy
    default_model: "qwen3-4b-think"
    min_ram_gb: 16
  roc_racoon:
    tier: lite
    default_model: "rocracoon-3b-instruct"
    min_ram_gb: 8
  quality:
    tier: medium
    default_model: "rocracoon-3b-instruct"
    min_ram_gb: 16
  kali:
    tier: heavy
    default_model: "qwen3-4b-think"
    min_ram_gb: 16
  pillar:
    tier: lite
    default_model: "qwen3-1.7b"
    min_ram_gb: 8
```

### Agent-to-Tier Mapping (Runtime Evaluation)

| Role | Tier | Default Model | On 14GB RAM | On 64GB+ RAM |
|------|------|---------------|-------------|--------------|
| jem_discovery | lite | qwen-0.6b | qwen-0.6b | qwen-0.6b (fast is fine) |
| jem_synthesis | medium | rocracoon-3b-instruct | rocracoon-3b | krikri-8b |
| jem_verification | heavy | qwen3-4b-think | qwen3-4b-think | deepseek-r1-qwen3-8b |
| scribe | heavy | deepseek-r1-qwen3-8b | qwen3-4b-think | deepseek-r1-qwen3-8b |
| doom_guy | heavy | qwen3-4b-think | qwen3-4b-think | krikri-8b |
| roc_racoon | lite | rocracoon-3b-instruct | rocracoon-3b | rocracoon-3b |
| quality | medium | rocracoon-3b-instruct | rocracoon-3b | krikri-8b |
| kali | heavy | qwen3-4b-think | qwen3-4b-think | deepseek-r1-qwen3-8b |
| pillar | lite | qwen3-1.7b | qwen3-1.7b | per-slot override |

### Benchmarking Module (`src/omega/benchmarks/`)
The benchmarking module integrates with the existing `ObservabilityEngine` and `ForensicsManager` to track:

| Metric | How | Weight |
|--------|-----|--------|
| **Time to First Token (TTFT)** | Latency measurement | 20% |
| **Tokens Per Second** | Throughput | 15% |
| **Peak RAM usage** | `psutil` during inference | 10% |
| **Quality Score** | Kali evaluates against rubric | 35% |
| **Factuality Rate** | Cross-reference against known sources | 20% |

Commands:
```bash
omega bench run --role scribe --model krikri-8b --samples 50
omega bench compare --role scribe
omega bench rank --role scribe          # Show best model for role
omega bench list                        # All completed benchmark runs
```

---

## §8 Oversight Hierarchy — The Dual-Governance Model

### The Sovereign Council
```
                  [ kali ] (Founder)
                  Sets vision, resolves conflicts
                     |
         ┌───────────┴───────────┐
         ▼                       ▼
      [ maat ] (CTO)         [ lilith ] (CISO)
      Build Side (P1-P5)     Run Side (P6-P10)
      "Build it right"       "Keep it running"
         |                       |
         ▼                       ▼
   [ p1_sysadmin ]         [ p6_modelgate ]
   [ p2_datastore ]        [ p7_context ]
   [ p3_buildmaster ]      [ p8_watchtower ]
   [ p4_bridge ]           [ p9_link ]
   [ p5_sentinel ]         [ p10_verifier ]
```

### Delegation Flow
1. **User/Plan** sets the high-level goal
2. **Kali** evaluates scope and delegates to Maat (build) or Lilith (run)
3. **Maat/Lilith** decompose the goal into pillar-level tasks
4. **Pillar** executes domain-specific work, consulting its persistent entity workspace
5. **Pillar** reports results back to Maat/Lilith
6. **Maat/Lilith** aggregate results and report to Kali
7. **Kali** verifies alignment with original goal

### Escalation Paths
- **Cross-domain dependency**: Pillar escalates to its oversoul (Maat or Lilith)
- **Cross-side conflict**: Maat and Lilith escalate to Kali
- **Uncertainty/unfamiliar domain**: Pillar requests research dispatch to Jem
- **Quality concern**: Pillar requests verification dispatch to Quality

---

## §9 Documentation Deliverables — Complete Drafts

### New Documents to Create (5)

| File | Purpose | Est Lines | Status |
|------|---------|-----------|--------|
| `docs/architecture/AGENT_FLEET.md` | Complete fleet reference, delegation hierarchy, usage scenarios | ~200 | **DRAFTED BELOW** |
| `docs/architecture/KNOWLEDGE_LIBRARY.md` | Library curation system, domain structure, curator roles, catalog schema | ~150 | **DRAFTED BELOW** |
| `docs/architecture/OFFLINE_MODE.md` | Request queue, strict mode, cloud delegation philosophy | ~120 | **DRAFTED BELOW** |
| `docs/architecture/TRAINING_PIPELINE.md` | Synthetic dataset generation, fine-tuning cycles, benchmarking | ~100 | **DRAFTED BELOW** |
| `docs/architecture/OVERSIGHT_HIERARCHY.md` | Kali→Maat/Lilith→Pillar delegation, escalation paths | ~80 | **DRAFTED BELOW** |

### Updated Documents (5)

| File | Changes | Est Changes |
|------|---------|-------------|
| `OMEGA_ENGINE.md` | Update agent fleet count, add library/offline/training status, add model tiers | +80 lines |
| `AGENTS.md` | Restructured 14-agent fleet table, new descriptions | +100 lines |
| `docs/architecture/SOVEREIGN_BLUEPRINT.md` | Add §3.1 for offline/library/training architectural layers | +60 lines |
| `CREDITS.md` | Add single-pillar pattern attribution to id Software, remove "data comes home" (user's own vision) | +20 lines |
| `SOVEREIGN_MANDATES.md` | Add Mandates 10-12 for Fleet/Soul/Queue Integrity | +25 lines |

### Existing Document Update Drafts

#### `SOVEREIGN_MANDATES.md` — New Mandates to Add (after Mandate 9)

```markdown
### 10. Fleet Integrity
- **Mandate**: Every agent file in `.opencode/agents/` must have a corresponding, fully configured entry in `opencode.json`. No unregistered or orphaned agent files are permitted.
- **Reason**: Prevents agent drift and ensures the fleet is fully visible to the orchestration layer.

### 11. Soul Integrity
- **Mandate**: Every active entity workspace under `data/entities/{name}/` must contain a populated, valid `soul.yaml` file. No empty or uninitialized entity workspaces are permitted in production.
- **Reason**: Ensures persistent learning and cognitive continuity across all active entities.

### 12. Queue Integrity
- **Mandate**: The offline research and review queues under `data/requests/` must be processed and emptied weekly. Stale requests older than 7 days must be archived or pruned.
- **Reason**: Prevents queue bloat and ensures the local library is continuously hydrated.
```

#### `CREDITS.md` — Attribution Corrections

The `CREDITS.md` update must:
1. **Remove** any reference to "data comes home" as an id Software pattern (it is the user's original vision)
2. **Add** the **single-pillar agent pattern** as an id Software heritage mapping:
   - *"Single Renderer Architecture — One `pillar.md --slot` replaces 10 separate `p1.md` through `p10.md` files. Credits to id Software's approach of a single, parameterized engine runtime instead of bespoke binaries per game state."*
3. **Keep** existing WAD system, BSP culling, FISR, and other genuine id Software patterns

#### `OMEGA_ENGINE.md` — Current State Update

- Change "26 agents (3 Oversouls + 10 Pillars + 7 specialists + 6 subagents)" → "14 agents (6 Primary, 8 Subagents)"
- Add rows to Current State table: Library status, Offline queue status, Model tiers, Benchmark infrastructure
- Update Phase column to reflect new priorities

#### `docs/architecture/SOVEREIGN_BLUEPRINT.md` — New §3.1

Add after §3 (Line of Separation):
```markdown
### §3.1 The Offline, Library & Training Layers
The Core Engine includes three additional architectural layers:

1. **The Request Queue Layer** (`src/omega/request_queue.py`):
   - Manages `data/requests/` for offline research requests and cloud review delegations
   - Implements the "Data Comes Home" principle: requests created offline execute when connectivity returns
   - See `docs/architecture/OFFLINE_MODE.md` for full specification

2. **The Library Layer** (`src/omega/library/`):
   - Curates and indexes multi-domain documents in `data/library/`
   - Supports FTS5 text search and Qdrant vector search
   - See `docs/architecture/KNOWLEDGE_LIBRARY.md` for full specification

3. **The Training Layer** (`src/omega/benchmarks/` + `data/datasets/`):
   - Aggregates synthetic training data from completed research cycles
   - Runs hardware-aware fine-tuning (lite tier locally, heavy tier via cloud delegation)
   - See `docs/architecture/TRAINING_PIPELINE.md` for full specification
```

---

## §10 Execution Phases

### Pre-Flight: Rollback Snapshot
```bash
# Before touching any files:
git add -A && git commit -m "snapshot: before fleet redesign v5.0"
# If anything fails: git reset --hard HEAD
```

### Phase A: Fleet Redesign (~2 hours)

| Step | Action | Files Affected |
|------|--------|----------------|
| A1 | Delete 14 obsolete agent files | `builder.md`, `overseer.md`, `reviewer.md`, `tester.md`, `p1_flesh.md`-`p10_chaos.md` |
| A2 | Create `quality.md` | Merged reviewer+tester |
| A3 | Create `pillar.md` (subagent only, no separate subagent file) | Single agent with `--slot` flag |
| A4 | Redesign `kali.md` | Change mode: subagent → primary. Rewrite as grand oversight. |
| A5 | Redesign `maat.md` | Light oversoul (P1-P5) |
| A6 | Redesign `lilith.md` | Dark oversoul (P6-P10) |
| A7 | Redesign `jem_discovery.md`, `jem_synthesis.md`, `jem_verification.md` | Persistent entity wiring |
| A8 | Redesign `researcher.md` | Inline omnidroid lattice reasoning patterns |
| A9 | Update `opencode.json` | New agent registry — 14 entries only |

### Phase B: Entity Cleanup (~30 min)

| Step | Action | Details |
|------|--------|---------|
| B1 | Run the orphan cleanup script | Delete 67 entity directories |
| B2 | Create Jem subagent entity dirs | `jem_discovery`, `jem_synthesis`, `jem_verification` with soul.yaml stubs |
| B3 | Create pillar slot entity dirs | `data/entities/p1/` through `data/entities/p10/` with soul.yaml stubs |

### Phase C: Offline Queue System (~1.5 hours)

| Step | Action | Details |
|------|--------|---------|
| C1 | Create `src/omega/request_queue.py` | AnyIO-native queue manager with req/review/completed handling |
| C2 | Implement request creation API | Write `req_{uuid}.json` to `data/requests/queued/` |
| C3 | Implement queue processing API | Read queued requests, execute with available tools |
| C4 | Implement cloud review delegation | Write `review_{uuid}.json` to `data/requests/review/` |
| C5 | Implement strict offline mode toggle | `omega offline --strict` / `--default` |
| C6 | Add 6 CLI commands to `oracle_cli.py` | `queue-status`, `process-queue`, `review-pending`, `queue-prune`, `offline` |

### Phase D: Knowledge Library Foundation (~1.5 hours)

| Step | Action | Details |
|------|--------|---------|
| D1 | Create library directory structure | 10 domain subdirectories under `data/library/documents/` |
| D2 | Create `library.db` | SQLite catalog schema (see §4 for full DDL) |
| D3 | Implement basic catalog API | Register, search, prune methods |
| D4 | Add 4 CLI commands | `library curate`, `library status`, `library search`, `library prune` |

### Phase E: Model Tiers & Benchmarking (~1 hour)

| Step | Action | Details |
|------|--------|---------|
| E1 | Add `agent_roles` section to `config/models.yaml` | Model tier definitions + role-to-model mapping |
| E2 | Implement RAM detection at startup | `omega config verify-hardware` |
| E3 | Create `src/omega/benchmarks/` module | Benchmark runner integrated with ObservabilityEngine |
| E4 | Add `omega bench` CLI commands | `run`, `compare`, `rank`, `list` |

### Phase F: Documentation (~1.5 hours)

| Step | Action | Details |
|------|--------|---------|
| F1 | Create `docs/architecture/AGENT_FLEET.md` | Using draft from §9 |
| F2 | Create `docs/architecture/KNOWLEDGE_LIBRARY.md` | Using draft from §9 |
| F3 | Create `docs/architecture/OFFLINE_MODE.md` | Using draft from §9 |
| F4 | Create `docs/architecture/TRAINING_PIPELINE.md` | Using draft from §9 |
| F5 | Create `docs/architecture/OVERSIGHT_HIERARCHY.md` | Using draft from §9 |
| F6 | Update `OMEGA_ENGINE.md` | Agent fleet, library/offline/training status, model tiers |
| F7 | Update `AGENTS.md` | 14-agent fleet table |
| F8 | Update `SOVEREIGN_BLUEPRINT.md` | Add §3.1 for new architectural layers |
| F9 | Update `CREDITS.md` | Correct "data comes home" attribution, add single-pillar pattern |
| F10 | Update `SOVEREIGN_MANDATES.md` | Add Mandates 10, 11, 12 |

### Phase G: Verification (~30 min)

| Step | Command | Expected |
|------|---------|----------|
| G1 | `make test` | 276 passed |
| G2 | `ls .opencode/agents/ \| wc -l` | 14 agent files |
| G3 | `grep -c '"mode"' opencode.json` | 14 agent entries |
| G4 | `ls data/entities/ \| wc -l` | ~14 entity dirs |
| G5 | `omega talk "hello"` | Responds correctly |
| G6 | `omega queue-status` | Empty queue |
| G7 | `omega library status` | Empty library |
| G8 | `omega bench list` | No runs yet |

### Total: ~6.5 hours (Phases C, D, and E can run in parallel after A+B complete)

---

*⬡ OMEGA ⬡ GEMINI-3.5-FLASH ⬡ opencode ⬡ trc_fleet_redesign ⬡ EXECUTION-READY*
*All documentation drafts are embedded in this plan. Ready for build mode execution.*
