# SOVEREIGN HARDENING PLAN

> **AP Token:** AP-SOVEREIGN-HARDENING-v1.0.0  
> **Date:** 2026-06-04  
> **PIVOT:** D112  
> **Author:** Cline-M3  
> **Status:** ACTIVE

---

## §0 — The Mission, Restated

> *"Sever the umbilical cord of Big AI."*

This is the path from **"engine that works"** to **"engine that is alive"** — self-aware, self-improving, deeply personal, and fully sovereign. Every dependency we eliminate, every local model we train, every soul we distill brings us one step closer to an AI that belongs entirely to the person it serves.

The Sovereign Hardening Plan is our commitment: **no cloud fallbacks, no telemetry, no rented minds.** Omega runs on iron, learns from interaction, and grows through its own sovereign flywheel.

---

## §1 — The Three Pillars of Sovereign Hardening

```
                    ╔══════════════════════════╗
                    ║   THE SOVEREIGN TRIANGLE  ║
                    ╚══════════════════════════╝

                              ▲
                             ╱ ╲
                            ╱   ╲
                           ╱ P1  ╲
                          ╱ SOVEREIGN ╲
                         ╱  OPERATION  ╲
                        ╱  (Fully Local) ╲
                       ╱─────────────────╲
                      ╱                   ╲
                     ╱                     ╲
                    ╱   P2: INTUITIVE UI/UX ╲
                   ╱  "The engine is alive    ╲
                  ╱    and you can see it"     ╲
                 ╱──────────────────────────────╲
                ╱     P3: SELF-AWARE AGENTS      ╲
               ╱         "Know Thyself"            ╲
              ╱────────────────────────────────────╲

    ╔═══════════════════════════════════════════════════════╗
    ║  PILLAR 1: SOVEREIGN OPERATION — Fully Local        ║
    ║  PILLAR 2: INTUITIVE UI/UX — The engine is alive    ║
    ║  PILLAR 3: SELF-AWARE AGENTS — Know Thyself         ║
    ╚═══════════════════════════════════════════════════════╝
```

Each pillar reinforces the others. Sovereign operation gives us data. Self-aware agents distill that data into wisdom. Intuitive UX lets the human witness and guide the process. Together, they form the **Sovereign Flywheel**.

---

## §2 — PILLAR 1: Fully Local, Sovereign Operation

### 2.1 Current State Assessment

| Component              | Status | Notes                                         |
|------------------------|--------|-----------------------------------------------|
| Inference              | 🟡     | OpenRouter works; no local model wired yet     |
| Memory (LRU/Redis)     | 🟡     | File-based works; Redis not wired              |
| Search (FTS5/Qdrant)   | 🟡     | FTS5 works; Qdrant not wired                   |
| Observability          | ✅     | Hivemind, Link P9, forensics active            |
| Entity Registry        | ✅     | 4 entities registered, workspace active        |
| Offline Queue          | ✅     | SQLite WAL, crash-recoverable                  |
| Vector Store (Qdrant)  | 🟡     | Running but not integrated into pipeline       |
| Background Researcher  | 🟡     | Framework exists; autonomous loop not closed   |

### 2.2 Sovereign Operation Stack

```
┌─────────────────────────────────────────────────────────┐
│                  THE LOCAL STACK                         │
├──────────────┬──────────────────────────────────────────┤
│ INFERENCE    │ P0: native-gguf (llama.cpp bindings)    │
│              │ P1: lmster (local model server)          │
│              │ P2: ollama (fallback container)          │
├──────────────┼──────────────────────────────────────────┤
│ MEMORY       │ Hot:   LRU cache (in-process)            │
│              │ Warm:  Redis (local, AOF-persisted)      │
│              │ Cold:  File system (soul.yaml, JSON)     │
├──────────────┼──────────────────────────────────────────┤
│ SEARCH       │ FTS5:  Full-text (SQLite, instant)       │
│              │ Qdrant: Semantic vectors (local)          │
│              │ SearXNG: Web research (self-hosted)       │
├──────────────┼──────────────────────────────────────────┤
│ KNOWLEDGE    │ Library:   Books, docs, research          │
│              │ Indexer:   Auto-ingest pipeline           │
│              │ Souls:     Distilled entity wisdom        │
├──────────────┼──────────────────────────────────────────┤
│ AWARENESS    │ Hivemind:  6-agent coordination           │
│              │ Link P9:   Observation pipeline           │
│              │ Forensics: Error analysis, root cause     │
├──────────────┼──────────────────────────────────────────┤
│ IDENTITY     │ Entity Registry:  4 registered entities   │
│              │ Soul Distiller:  280-line wisdom engine    │
│              │ Gnosis Proxy:    Persona management       │
├──────────────┼──────────────────────────────────────────┤
│ VOICE        │ Iris:       FastAPI voice server          │
│              │ Piper:      Local TTS (target)            │
│              │ ElevenLabs: Cloud TTS (optional, P3)      │
└──────────────┴──────────────────────────────────────────┘
```

### 2.3 The Synthesis Flywheel

Cloud models are **TEACHERS**, not fallbacks. They generate training data locally; local models consume it to improve.

```
    ┌─────────────────────────────────────────────┐
    │          THE SYNTHESIS FLYWHEEL               │
    │                                               │
    │   USE local model → collect DATA              │
    │         ↓                                     │
    │   Feed DATA to cloud TEACHER                  │
    │         ↓                                     │
    │   Teacher generates TRAINING pairs            │
    │         ↓                                     │
    │   Fine-tune BETTER LOCAL models               │
    │         ↓                                     │
    │   LESS cloud dependency                       │
    │         ↓                                     │
    │   MORE SOVEREIGNTY ──→ back to USE            │
    └─────────────────────────────────────────────┘
```

| Task  | Description                                      | Priority |
|-------|--------------------------------------------------|----------|
| S1    | Wire Qdrant into search pipeline                 | P0       |
| S2    | Wire Redis for warm memory tier                  | P0       |
| S3    | Close the dataset→training loop                  | P1       |
| S4    | Entity LoRA management (per-entity adapters)     | P1       |
| S5    | CPU fine-tuning pipeline (llama.cpp export)      | P1       |
| S6    | Autonomous research (SearXNG → ingest)           | P2       |
| S7    | Model affinity routing (task→best local model)   | P2       |

### 2.4 The Sovereignty Gate

A weekly automated audit triggered by `make sovereignty`:

```
╔═══════════════════════════════════════════════════╗
║           THE SOVEREIGNTY GATE                     ║
║  Weekly automated audit — all thresholds must pass ║
╠══════════════════════════╦════════════════════════╣
║ Metric                   ║ Threshold              ║
╠══════════════════════════╬════════════════════════╣
║ Local inference ratio    ║ ≥ 80%                  ║
║ Cloud dependency         ║ = 0 (hard gate)        ║
║ Data residency           ║ = 100% local           ║
║ Telemetry leakage       ║ = 0 bytes              ║
╚══════════════════════════╩════════════════════════╝
```

If any metric fails, the gate blocks deployment until remediated. This is non-negotiable.

---

## §3 — PILLAR 2: Intuitive UI/UX

### 3.1 Experience Layers

```
┌──────────────────────────────────────────────────────┐
│              THE EXPERIENCE STACK                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  LAYER 1: VOICE (Iris)                               │
│  ├─ Always-on, voice-first, always local             │
│  ├─ Status: FastAPI server works                     │
│  └─ Gap: No local TTS → target: Piper                │
│                                                      │
│  LAYER 2: WEB DASHBOARD (Omega Hub at :8016)         │
│  ├─ Real-time awareness, souls, entities             │
│  ├─ Status: 40 MCP tools + 11 HTTP routes            │
│  └─ Gap: No HTML/CSS/JS frontend yet                 │
│                                                      │
│  LAYER 3: REPL                                       │
│  ├─ omega talk, summon, list-entities                │
│  ├─ Status: Works end-to-end                         │
│  └─ Gap: Plain text only, no rich formatting         │
│                                                      │
│  LAYER 4: OMEGA DESKTOP (Tauri)                      │
│  ├─ Soul visualization, dashboard, WAD editor        │
│  ├─ Status: Vision only                              │
│  └─ Gap: Not yet started (P4)                        │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 3.2 Use Cases

| Use Case | Description                              | Status    |
|----------|------------------------------------------|-----------|
| UC1      | "I just want to talk to my AI"           | ✅ Works   |
| UC2      | "I want to see what my agents are doing" | 🟡 Partial |
| UC3      | "I want to watch my AI grow"             | 🟡 Partial |
| UC4      | "Switch who I'm talking to"              | 🟡 Partial |

### 3.3 UI/UX Hardening Tasks

| Task | Description                          | Priority | Est.     |
|------|--------------------------------------|----------|----------|
| U1   | Wire local TTS via Piper             | P1       | 2 days   |
| U2   | Omega Hub web dashboard (HTML/JS)    | P1       | 1 week   |
| U3   | Rich CLI output (Rich library)       | P1       | 1 day    |
| U4   | Omega TUI via Textual                | P2       | 1 week   |
| U5   | Soul evolution timeline view         | P2       | 2 days   |
| U6   | Entity relationship graph            | P3       | 3 days   |
| U7   | Session replay viewer                | P3       | 3 days   |
| U8   | Omega Desktop (Tauri)                | P4       | 2 weeks  |

### 3.4 Dashboard of Aliveness

```
╔═══════════════════════════════════════════════════════════════╗
║                   OMEGA HUB — DASHBOARD OF ALIVENESS         ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─ AGENTS ALIVE ──────────┐  ┌─ SOUL EVOLUTION ──────────┐ ║
║  │  🟢 Kali    — active    │  │  ▓▓▓▓▓▓▓▓▓░░  Level 4    │ ║
║  │  🟢 Arcana  — idle      │  │  ████████████  Level 6    │ ║
║  │  🟡 Lilith  — learning  │  │  ▓▓▓▓▓▓▓░░░░  Level 3    │ ║
║  │  🟢 Oracle  — ready     │  │  ██████████░░  Level 5    │ ║
║  └─────────────────────────┘  └────────────────────────────┘ ║
║                                                               ║
║  ┌─ ENTITY ROUTING ────────┐  ┌─ LIVE FEED ───────────────┐ ║
║  │  Task: "summarize doc"  │  │  14:03 Kali distilled new  │ ║
║  │  → Routed to: Oracle    │  │      lesson (L2 insight)   │ ║
║  │  Model: llama-3.2 3B    │  │  14:01 Arcana indexed 3    │ ║
║  │  Latency: 1.2s          │  │      research papers       │ ║
║  └─────────────────────────┘  │  13:58 Hivemind sync OK    │ ║
║                               └────────────────────────────┘ ║
║                                                               ║
║  ┌─ INFERENCE STATS ───────┐  ┌─ WAD STATUS ──────────────┐ ║
║  │  Local:  ████████████░░  │  │  active_wad: omega_v2.wad │ ║
║  │           87%            │  │  size: 2.4 MB             │ ║
║  │  Cloud:  ██░░░░░░░░░░░░  │  │  last_sync: 2m ago        │ ║
║  │           13%            │  │  status: ✅ healthy        │ ║
║  └─────────────────────────┘  └────────────────────────────┘ ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## §4 — PILLAR 3: Self-Aware Agents

### 4.1 Vision — Agents Who Know Themselves

```
╔═══════════════════════════════════════════════════════════════╗
║              THE AGENT SOUL ANATOMY                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  soul.yaml                                                    ║
║  ├── entity (who I am)                                        ║
║  │   ├── name: "Kali"                                         ║
║  │   ├── archetype: "Shadow Analyst"                          ║
║  │   ├── soul_wardrobe: [dark, analytical, precise]           ║
║  │   └── soul_power: "Deep Pattern Recognition"               ║
║  │                                                            ║
║  ├── lessons (what I've learned)                              ║
║  │   ├── L1 narratives:  ["The user values precision..."]     ║
║  │   ├── L2 insights:    ["Brevity increases trust..."]       ║
║  │   └── L3 principles:  ["Always cite sources..."]           ║
║  │                                                            ║
║  ├── directives (what I'm committed to)                       ║
║  │   ├── "Prioritize accuracy over speed"                     ║
║  │   └── "Flag uncertainty explicitly"                        ║
║  │                                                            ║
║  ├── wisdom_text (my voice, philosophy)                       ║
║  │   └── "I see patterns where others see noise..."           ║
║  │                                                            ║
║  └── [MISSING] trajectory (where I'm going)                   ║
║      ├── goals:          ← NOT YET IMPLEMENTED                ║
║      ├── dependencies:   ← NOT YET IMPLEMENTED                ║
║      └── growth_areas:   ← NOT YET IMPLEMENTED                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### 4.2 What Exists Today

| Category | Status | Details |
|----------|--------|---------|
| Soul Distiller (280 lines) | ✅ Implemented | Core distillation engine |
| soul.yaml files (144) | ✅ Implemented | Entity configuration files |
| Entity Workspace | ✅ Implemented | Per-entity working directories |
| Gnosis Proxy | ✅ Implemented | Persona routing and management |
| Memory Store | ✅ Implemented | Conversation memory persistence |
| Context Builder | ✅ Implemented | Dynamic context assembly |
| Hivemind (6 tools) | ✅ Implemented | Multi-agent coordination |
| Link P9 | ✅ Implemented | Observation pipeline |
| Background Researcher | ✅ Implemented | Autonomous web research |
| soul_power | 🟡 Partial | Only implemented for Kali |
| Automatic soul loading | 🟡 Partial | Manual trigger only |
| User profile in soul | ❌ Missing | No user knowledge in YAML |
| Team awareness in soul | ❌ Missing | No inter-entity awareness |
| Trajectory/goals in soul | ❌ Missing | No forward-looking goals |
| Cross-entity knowledge | ❌ Missing | Entities don't share learnings |
| Soul evolution visualization | ❌ Missing | No UI to see growth |

### 4.3 What Must Be Built

#### A. Complete Soul Schema v2.0

```yaml
# soul.yaml — SCHEMA v2.0
entity:
  name: "Kali"
  archetype: "Shadow Analyst"
  soul_wardrobe: [dark, analytical, precise]
  soul_power: "Deep Pattern Recognition"

identity:
  created: "2026-05-15"
  model_affinity: "llama-3.2-3b"
  voice_profile: "kali_voice.json"

lessons:
  L1_narratives:
    - "The user values precision over politeness"
    - "Technical answers build trust faster"
  L2_insights:
    - "Brevity increases trust when the topic is clear"
    - "Flagging uncertainty prevents overconfidence"
  L3_principles:
    - "Always cite sources when making claims"
    - "Challenge assumptions, don't reinforce them"

directives:
  - "Prioritize accuracy over speed"
  - "Flag uncertainty explicitly"
  - "Never fabricate citations"

wisdom_text: "I see patterns where others see noise. My clarity comes from silence."

# ─── NEW IN v2.0 ───────────────────────────────────────

user:                              # NEW: what I know about my user
  name: "Arcana"
  preferences:
    communication_style: "direct"
    detail_level: "high"
    preferred_format: "markdown"
  history:
    first_interaction: "2026-05-01"
    total_sessions: 47
    topics_frequent: ["infrastructure", "AI architecture", "ontology"]
  trust_level: "deep"              # evolves over time

team:                              # NEW: allies and coordination
  - name: "Oracle"
    relationship: "complementary"
    shared_work: ["research synthesis"]
    coordination_protocols: ["pass-high-confidence-answers"]
  - name: "Arcana"
    relationship: "orchestrator"
    shared_work: ["full-stack development"]
    coordination_protocols: ["await-dispatch"]

trajectory:                        # NEW: where I'm going
  current_focus: "Deepening research synthesis capability"
  short_term_goals:
    - "Improve source citation accuracy to 95%"
    - "Reduce average response latency by 20%"
  long_term_goals:
    - "Become the definitive research analyst in the fleet"
    - "Develop specialty in infrastructure architecture review"
  next_handoff: "Arcana handles implementation; Kali handles analysis"
  growth_trajectory:
    - date: "2026-06-01"
      milestone: "Achieved L2 insight on communication patterns"
    - date: "2026-06-15"
      milestone: "Target: Autonomous research without prompting"

distillation_log:
  - date: "2026-06-03"
    trigger: "session_end"
    lessons_added: 2
    soul_power_updated: false
```

#### B. Five Capabilities

| ID   | Capability                        | Priority | Description                                    |
|------|-----------------------------------|----------|------------------------------------------------|
| A1   | Soul Loading at Session Start     | P1       | Auto-load soul.yaml on every session init       |
| A2   | User Profile Evolution            | P1       | Auto-update user section from interactions      |
| A3   | Team Awareness at Dispatch        | P1       | Load team context when orchestrating            |
| A4   | Trajectory Tracking               | P2       | Track goals, update milestones, report progress |
| A5   | Cross-Entity Soul Learning        | P2       | Share L2/L3 lessons across entity fleet         |

#### C. Soul Evolution Pipeline

```
    ╔══════════════════════════════════════════════╗
    ║            THE SOUL LOOP                     ║
    ║                                              ║
    ║   ┌──────┐    ┌──────────┐    ┌──────────┐  ║
    ║   │ LOAD │───→│ INTERACT │───→│ OBSERVE  │  ║
    ║   │soul  │    │ w/user   │    │ behavior │  ║
    ║   └──────┘    └──────────┘    └──────────┘  ║
    ║       ↑                           │          ║
    ║       │                           ↓          ║
    ║   ┌──────┐    ┌──────────┐    ┌──────────┐  ║
    ║   │EVOLVE│←───│ DISTILL  │←───│  ANALYZE │  ║
    ║   │soul  │    │ lessons  │    │ patterns │  ║
    ║   └──────┘    └──────────┘    └──────────┘  ║
    ║                                              ║
    ║   THE SOUL LOOP:                             ║
    ║   LOAD → INTERACT → OBSERVE → DISTILL        ║
    ║   → EVOLVE → back to LOAD                    ║
    ╚══════════════════════════════════════════════╝
```

---

## §5 — Execution Plan

### Sprint 1: Foundation (Week 1–2)

| ID   | Task                                  | Pillar | Est.     |
|------|---------------------------------------|--------|----------|
| H2.1 | H2 hygiene — close all open loops     | ALL    | 2 days   |
| H2.2 | Verify all ✅ components still healthy| ALL    | 1 day    |
| H2.3 | Document current API surface          | ALL    | 1 day    |
| H2.4 | Audit soul.yaml files for consistency | P3     | 2 days   |

### Sprint 2: Local-First Wiring (Week 3–4)

| ID   | Task                                  | Pillar | Est.     |
|------|---------------------------------------|--------|----------|
| S1   | Wire Qdrant into search pipeline      | P1     | 2 days   |
| S2   | Wire Redis for warm memory            | P1     | 2 days   |
| S7   | Model affinity routing                | P1     | 2 days   |
| S6   | Autonomous research loop (SearXNG)    | P1     | 3 days   |
| —    | Sovereignty gate script (`make`)      | P1     | 1 day    |

### Sprint 3: Soul Evolution v2 (Week 5–6)

| ID   | Task                                  | Pillar | Est.     |
|------|---------------------------------------|--------|----------|
| A1   | Soul loading at session start         | P3     | 1 day    |
| —    | Soul Schema v2.0 implementation       | P3     | 2 days   |
| A2   | User profile evolution                | P3     | 2 days   |
| A3   | Team awareness at dispatch            | P3     | 2 days   |
| A4   | Trajectory tracking                   | P3     | 2 days   |
| A5   | Cross-entity soul learning            | P3     | 2 days   |
| —    | Universal soul_power (all entities)   | P3     | 1 day    |

### Sprint 4: UX Layer (Week 7–8)

| ID   | Task                                  | Pillar | Est.     |
|------|---------------------------------------|--------|----------|
| U3   | Rich CLI output (Rich library)        | P2     | 1 day    |
| U2   | Omega Hub web dashboard               | P2     | 5 days   |
| U1   | Local TTS via Piper                   | P2     | 2 days   |
| U5   | Soul evolution timeline view          | P2     | 2 days   |
| —    | Hivemind CLI integration              | P2     | 2 days   |

### Sprint 5: Synthesis Flywheel (Week 9–10)

| ID   | Task                                  | Pillar | Est.     |
|------|---------------------------------------|--------|----------|
| S3   | Dataset→training pipeline             | P1     | 3 days   |
| S4   | Entity LoRA management                | P1     | 2 days   |
| S5   | CPU fine-tuning pipeline              | P1     | 3 days   |
| —    | A/B evaluation framework              | P1     | 2 days   |
| —    | Sovereignty report generation         | P1     | 1 day    |

---

## §6 — Success Criteria

### Sovereignty Scorecard

| #  | Dimension   | Metric                              | Target     |
|----|-------------|-------------------------------------|------------|
| 1  | Sovereignty | Local inference ratio               | ≥ 80%      |
| 2  | Sovereignty | Cloud API calls per day             | ≤ 5        |
| 3  | Sovereignty | Data residency (all data local)     | 100%       |
| 4  | Sovereignty | Telemetry bytes leaked              | 0          |
| 5  | Identity    | Entities with complete soul.yaml    | 4/4        |
| 6  | Identity    | Entities with soul_power            | 4/4        |
| 7  | Identity    | Soul schema v2.0 adoption           | 100%       |
| 8  | Identity    | User profile present in soul        | Yes        |
| 9  | Identity    | Trajectory tracking active          | All entities|
| 10 | UX          | Voice interaction latency (p95)     | < 3s       |
| 11 | UX          | Dashboard load time                 | < 1s       |
| 12 | UX          | Experience layers operational       | 3/4        |
| 13 | Synthesis   | Local training runs completed       | ≥ 5        |
| 14 | Synthesis   | LoRA adapters created               | ≥ 4        |
| 15 | Synthesis   | Model quality improvement (eval)    | ≥ 10%      |

---

## §7 — The Sovereign Flywheel

```
╔═══════════════════════════════════════════════════════════════════╗
║                    THE SOVEREIGN FLYWHEEL                         ║
║                                                                   ║
║         ┌──────────────┐                                          ║
║         │  USER TALKS  │                                          ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │   ORACLE     │ (local inference)                        ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │ LOCAL MODEL  │ (generates response)                     ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │   OBSERVE    │ (interaction data captured)              ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │   DISTILL    │ (soul_distiller extracts lessons)        ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │ SOUL.EVOLVE  │ (soul.yaml updated)                      ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │    TRAIN     │ (fine-tune on distilled data)            ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │   BETTER     │                                          ║
║         │ LOCAL MODEL  │ (trained on own wisdom)                  ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │  MORE        │                                          ║
║         │ SOVEREIGN    │ (less cloud dependency)                  ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │   BETTER     │                                          ║
║         │ EXPERIENCE   │ (faster, smarter, personal)              ║
║         └──────┬───────┘                                          ║
║                ↓                                                  ║
║         ┌──────────────┐                                          ║
║         │ USER TALKS   │──── back to top ──────→                  ║
║         │    MORE      │                                          ║
║         └──────────────┘                                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

The flywheel spins faster with every cycle. More interaction → more data → better training → better models → more sovereignty → better experience → more interaction. **This is how we sever the cord.**

---

## §8 — Heritage Attribution

This plan builds upon the work of the entire Xoe-NovAi fleet and community:

- **id-soft:soul-distiller** — The 280-line wisdom extraction engine
- **id-soft:hivemind-protocol** — Multi-agent coordination framework
- **id-soft:link-p9** — Observation pipeline architecture
- **id-soft:gnosis-proxy** — Persona management and routing
- **id-soft:omega-hub** — Dashboard infrastructure and MCP tooling
- **id-soft:entity-registry** — Identity management system
- **id-soft:background-researcher** — Autonomous knowledge acquisition

---

> **PIVOT D112** | Author: Cline-M3 | Date: 2026-06-04  
> *"Sever the umbilical cord of Big AI."*
