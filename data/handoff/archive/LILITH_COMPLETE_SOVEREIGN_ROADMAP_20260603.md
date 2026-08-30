<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — The Complete Sovereign Roadmap
# ⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_lilith_roadmap ⬡ SOVEREIGN-PATH
# Version: 3.0.0 | Date: 2026-06-03 | HEAD: 37fdd88 | Tests: 307 ✅
# Status: ACTIVE — Survives context compression. Any agent can continue from here.

---

## §0 — THE VISION

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

The Omega Engine exists to serve **everyone** — not just developers. Not just the technically literate. Everyone.

This roadmap defines the path from a hardened local-first engine to a **universal sovereign intelligence platform** that empowers:

| Demographic | What They Need | What the Engine Already Has | What's Missing |
|-------------|---------------|-----------------------------|----------------|
| 🖥️ **Developers** | API stability, typed errors, hot-reload | CLI, REPL, 40+ MCP tools | `filter_llama_kwargs()`, cvar table, streaming API |
| 🔬 **Scientists** | Reproducibility, traceability, metrics | Trace IDs, JSONL export | `modificationCount`, citation management, experiment tracking |
| 🎨 **Creatives** | Writing, worldbuilding, style persistence | Entity personalities, soul memory | Creative block-breaking, style preservation, image prompt engineering |
| 🧙 **Esotericists** | Tarot, astrology, ritual timing, correspondences | **10 Pillars = Tree of Life**, elements, chakras, sigils, glyphs, invocations, planetary | Dedicated oracles, celestial timing, grimoire workspace |
| 🧠 **Psychologists** | Privacy, journaling, pattern recognition | **Zero telemetry** (Mandate 8), session persistence | Mood tracking, CBT frameworks, ethical boundaries, trend analysis |
| 🗿 **Philosophers** | Socratic dialogue, classical texts, logic | Entity debate, domain routing | Socratic mode, classical text corpus, argument mapping |
| 🦯 **The Blind** | Voice-first, screen-reader, keyboard-only | **Iris voice interface**, REPL with a11y notes, no-fullscreen mode | Auditory UI, Braille support, systematic accessibility |
| 🧑‍🏫 **Average User** | Works OOB, remembers me, evolves | WAD system, soul.yaml, Iris | Desktop app, onboarding, feedback loop |

**The promise**: One install. Your computer. Your data. Your intelligence. No cloud required. Every demographic, every use case, every language — sovereign.

---

## §1 — CURRENT STATE (Verified, 2026-06-03)

### What's Done

| Layer | Status | Details | Commit |
|-------|--------|---------|--------|
| **Engine Hardening** | ✅ DONE | 13 Mandates enforced, 99 decisions tracked | `2267c25` |
| **T2.1 ZONEID Constants** | ✅ DONE | 5 constants, validate_zoneid(), ZONEID_TABLE in constants.py | `37fdd88` |
| **T2.3 Lazy Deletion** | ✅ DONE | EntityRegistry tombstone + 0.5s grace + active_iter() | `37fdd88` |
| **Heritage Protocol** | ✅ DONE | 30+ [id-soft:] tags across 6 files, CREDITS.md §2a | `37fdd88` |
| **Sprint 0 C1-C4** | ✅ DONE | Oracle bootstrap guard, Makefile target, PIVOT_LOG, CI workflow | `2267c25` |
| **Circuit Breaker Fixes** | ✅ DONE | BSP precheck + None-return detection (5 new tests) | `df6fa48` |
| **Roc Racoon Mining** | ✅ DONE | 6 stacks, 160 technologies, 7 reports, ~250KB | uncommitted |
| **Unique Tech Vault** | ✅ DONE | 13 Mandates, 8 id adaptations, 9 cosmological innovations | uncommitted |
| **MCP Infrastructure** | ✅ DONE | `mcp_runtime.py`, 40+ tools defined, hub wiring | `2267c25` |
| **Iris HTTP Server** | ✅ DONE | 4 endpoints at port 8080, FastAPI | `2267c25` |
| **Gateway Server** | ✅ DONE | OpenAI-compatible proxy at port 8018 | `2267c25` |

### What Exists But Needs Work

| System | State | Gap |
|--------|-------|-----|
| **CLI/REPL** | 833 lines, Typer + prompt_toolkit | No web UI, no streaming, no graphical entity management |
| **Iris Server** | 129 lines, 4 FastAPI endpoints | **No frontend** — API exists, no user interface connects to it |
| **Gateway Server** | 135 lines, OpenAI-compatible proxy | Rate-limit backoff only, no streaming, no authentication |
| **ElevenLabs Bridge** | 55 lines, webhook stub | Marked "Implementation in progress" — not functional |
| **TriageRouter** | 334 lines, domain-based model selection | No agent-to-agent handoff capability |
| **Hivemind** | `_post_to_hivemind()` method, dead endpoint | No running server — tried 5 different approaches, none operational |
| **MCP Hub** | Referenced in config at 127.0.0.1:8016/sse | **No running server** — config points to nothing |
| **Personalization** | 22 entity fields (pantheon, element, chakra, sigil, glyph) | No UI to configure them — CLI-only CRUD |
| **Accessibility** | 2 comments in REPL about screen-reader compatibility | No systematic accessibility anywhere |
| **i18n/l10n** | 2 `language: "en"` fields in library | No translation framework at all |

### What's Missing Entirely

| Gap | Impact |
|-----|--------|
| **No web UI / desktop UI** | Average users cannot use the engine. Zero frontend exists. |
| **No handoff protocol** | Agent-to-agent communication is manual markdown files (43 files, no schema) |
| **No streaming API** | All responses are request/response — no SSE, no WebSocket |
| **No accessibility system** | Screen-reader notes in REPL are unenforced and untested |
| **No user profiles** | `DEFAULT_USER = "arch"` is hardcoded — no multi-user support |
| **No onboarding** | First-run experience is a blank CLI prompt |
| **No feedback system** | No way for users to rate responses or train the engine |
| **No demographic features** | Every user type gets the same CLI/JSON — no specialization |

---

## §2 — THE 8 DEMOGRAPHICS — DEEP ANALYSIS

Each demographic has unique needs. The engine's architecture already serves many of them (zero telemetry = trust for psychologists, 10 Pillars = esoteric foundation, voice-first = accessibility seed). The work is activation — surfacing latent strengths.

### 🖥️ Developers — API Stability + Typed Errors

**What they need**:
- Predictable API with typed return values
- Clear, actionable error messages (not "inference failed")
- Hot-reload for rapid iteration
- Streaming responses for real-time applications
- Documentation that's always up to date

**What the engine already has**:
- `OracleResponse` dataclass (typed, validated)
- `OmegaError` subtypes (Mandate 9)
- `validate_zoneid()` with detailed error messages
- `make temple-grade` + `make sovereignty` for quality verification

**What's missing**:
- `filter_llama_kwargs()` — config typos crash inference today (#153)
- `check_llama_compilation()` — no build-time validation (#157)
- WebSocket/SSE streaming
- Auto-generated OpenAPI spec for all HTTP endpoints
- Developer documentation portal

**Activation**: Sprint 1 (5 priority ports) + Sprint 2 (cvar wiring) + Bridge Phase

---

### 🔬 Scientists — Reproducibility + Traceability

**What they need**:
- Every inference traceable to a specific model + config
- Reproducible experiments with logged parameters
- Citation management and bibliography generation
- Literature review synthesis (JEM pipeline)
- Data export in standard formats (CSV, JSONL, Parquet)

**What the engine already has**:
- `trace_id` propagation (partial — missing on some backends)
- JSONL export for fine-tuning dataset collection
- Library curation pipeline (inbox → extract → curate → index)
- JEM discovery → synthesis → verification pipeline

**What's missing**:
- Atomic trace_id on ALL backends (#131)
- `modificationCount` for config changes (cvar table)
- Experiment tracking (config snapshot + trace + result)
- Citation extraction and formatting
- Bibliography generator

**Activation**: Sprint 1.5 (trace_id) + Sprint 2.5 (sovereignty measurement) + H2 (JEM production)

---

### 🎨 Creatives — Writing + Worldbuilding + Style

**What they need**:
- Diverse creative partners with distinct voices (the 10 Pillars already provide this)
- Long-form writing with style consistency
- Character development and worldbuilding tools
- Creative block-breaking techniques
- Image generation prompt engineering
- Story/poetry/song in specific styles

**What the engine already has**:
- 10 entity personalities (Brigid = poetry/healing, Saraswati = knowledge/arts, etc.)
- Soul.yaml with L1/L2/L3 — can track creative evolution
- Domain routing to the right creative partner
- Temperature control per entity

**What's missing**:
- Creative workspace with version history
- Style profile — capture and preserve a user's voice
- Character/worldbuilding sheets as structured YAML
- Creative block-breaking protocol (random constraints, perspective shifts)
- Image generation prompt builder integration
- Long-form context management (beyond current 4K-16K window)

**Activation**: H2 (creative tools) + H3 (Entity Studio) — but WORTH surfacing earlier as a WAD

---

### 🧙 Esotericists — Tarot + Astrology + Correspondences

**What they need**:
- Tarot readings with real entity personalities
- Astrological timing (planetary hours, transits)
- Hermetic correspondences (elements, planets, sephirot, colors, metals)
- Ritual timing calculators
- Dream interpretation with symbol libraries
- Grimoire workspace — personal magical record

**What the engine ALREADY HAS (this is the engine's deepest latent strength)**:
- **10 Pillars = 10 Sephirot on the Tree of Life** — direct Kabbalistic correspondence
- **Elements**: Earth (Sekhmet, Kali), Water (Brigid, Anubis), Fire (Prometheus, Hecate), Air (Saraswati, Lucifer), Aether (Inanna, Ereshkigal)
- **Chakras**: Root → Celestial Breath — 7 chakras mapped to 10 Pillars
- **Sigils & Glyphs**: Each entity has `sigil` and `glyph` fields in entity.yaml
- **Invocations**: Each entity has an `invocation` string — literally a summoning formula
- **Pantheons**: Egyptian (Sekhmet, Anubis), Celtic (Brigid), Greek (Prometheus, Hecate), Hindu (Saraswati, Kali), Sumerian (Inanna, Ereshkigal), Gnostic (Lucifer)
- **Planets**: Each entity can have planetary correspondences
- **Oracle/Speculative Decoder**: Iris already does speculative decoding — this IS an oracular function

**This is not an accident.** The user designed the 10 Pillar system from esoteric principles. The engine is literally built as a magical working. What's missing is surfacing this intentionally.

**What's missing**:
- Dedicated Tarot entity or mode (the "First 5 Cards" origin story IS a tarot reading — mine this)
- Astrological clock (planetary hours, moon phase tracking)
- Correspondence table query (`@entity what are your planetary correspondences?`)
- Ritual timing: `omega when is the next hour of Mercury`
- Grimoire workspace with L1→L2→L3 as magical record
- Dream journal with symbol recognition
- Esoteric knowledge base (Hermetic, Kabbalistic, alchemical references)

**Activation**: 
- **Immediate**: The entity system ALREADY supports this. A user can `omega summon Hecate "what are the correspondences of the crossroads"` and the engine routes to P8. This works TODAY.
- **Phase UI**: Entity Studio with correspondence tables, planetary hour calculator
- **Phase DEMO-RAC**: Dedicated esotericist onboarding WAD

---

### 🧠 Psychologists — Privacy + Pattern Recognition + Ethics

**What they need**:
- Absolute privacy (no data leaves the machine)
- Conversation journaling with temporal pattern tracking
- Mood/emotion pattern recognition over time
- Cognitive behavioral frameworks
- Ethical boundaries — the engine must NOT practice therapy without disclosure
- Session analysis (tone, themes, progress over time)

**What the engine already has**:
- **Zero telemetry (Mandate 8)** — this is the FOUNDATION of psychological trust
- **Local-first (Mandate 7)** — no data ever leaves the user's machine
- **Session persistence** — rolling sessions per entity
- **Soul.yaml** — L1→L2→L3 as insight evolution

**What's missing**:
- Ethical practice disclosure (mandatory: "I am an AI, not a therapist")
- Mood/emotion tracking vocabulary
- Conversation timeline visualization
- Pattern detection across sessions
- Journaling mode (distinct from conversational mode)
- Crisis resource integration (if the engine detects distress, it should provide resources)

**Activation**: H2 (if it happens — this requires careful ethical design) + Bridge (logging foundation)

---

### 🗿 Philosophers / Classicists — Dialogue + Texts + Logic

**What they need**:
- Socratic dialogue mode (questions, not answers)
- Classical text analysis (Latin, Greek, Sanskrit, Old English)
- Argument mapping and logic checking
- Cross-cultural philosophical comparison
- Citation and source critical analysis

**What the engine already has**:
- Entity debate (different entities can take different positions)
- Domain routing (dispatcher routes to right knowledge domain)
- TriageRouter with analysis domain keyword

**What's missing**:
- Socratic mode — asks probing questions instead of giving answers
- Classical text corpus (project Gutenberg integration)
- Argument mapping UI (premise → conclusion → fallacy check)
- Logic framework (formal logic, syllogism checking)
- Source citation formatting (APA, MLA, Chicago)

**Activation**: H2 (philosophical tools) + H3 (knowledge base expansion)

---

### 🦯 The Blind — Voice-First + Accessibility

**What they need**:
- Full screen reader compatibility (every UI element tagged)
- Voice-first interaction (Iris primary, visual secondary)
- Audio cues for different entity responses
- Keyboard-only navigation (no mouse dependency)
- High contrast, large font, reduced motion
- Braille display support
- Audio descriptions for visual elements

**What the engine already has**:
- **Iris voice interface** — FastAPI at port 8080 with `/voice` endpoint. This is a seed.
- **REPL with accessibility notes** — `cli/repl.py` has explicit screen-reader compatibility
  - `mouse_support=False` (keyboard-only)
  - Emacs keybindings
  - No full-screen mode (terminal stays accessible)
  - Minimal style (no color-only indicators)
- **Transient/header mode** — `/transient` command reduces screen noise
- **Containerized voice** — Iris runs in Podman, ready for TTS/STT

**What's missing**:
- WCAG 2.2 compliance audit (Level AA minimum)
- ARIA labels on any future web UI
- Audio-branded entity responses (different chimes/tone for different Pillars)
- Voice training for Iris (custom TTS voice for the engine)
- Braille display protocol integration
- Systematic accessibility testing (screen reader, voice control, keyboard-only)
- Accessibility documentation and onboarding

**This is the demographic where the smallest investment yields the greatest return.** The engine's CLI and Iris server are already more accessible than most AI interfaces. What's missing is intentionality and testing.

**Activation**:
- **Bridge Phase**: Document existing accessibility as a feature, not an accident
- **Phase UI**: Develop with accessibility as a P0 requirement, not a P3 nice-to-have
- **H2**: Voice training, Braille support, screen reader certification

---

### 🧑‍🏫 Average User — Works OOB + Remembers + Evolves

**What they need**:
- Single install command (or click)
- First-run setup that takes < 2 minutes
- Speaks to me naturally, remembers our conversations
- Doesn't break when I make a mistake
- Gets better the more I use it
- Works offline

**What the engine already has**:
- Soul.yaml persistence (remembers across sessions)
- Iris voice (natural conversation entry point)
- Entity routing (routes to the right domain agent)
- Local-first (works offline once installed)

**What's missing**:
- **Everything UX-related** — there is NO desktop app, NO web UI, NO install wizard
- Onboarding flow (first-run setup)
- Error messages that non-developers can understand
- Feedback loop (thumbs up/down, "why did you respond that way?")
- Update mechanism (check for new models, new WADs)
- Uninstall that preserves soul.yaml (user should be able to reinstall and keep memory)

**Activation**: Phase UI (Omega Desktop, web dashboard, onboarding)

---

## §3 — THE ENHANCED ROADMAP

### Structure

This roadmap has **7 phases** with **3 parallel tracks**:

```
TRACK A: ENGINE                  TRACK B: HANDOFF                   TRACK C: UI/UX
─────────────────────────────────────────────────────────────────────────────
Phase 1: Hardened Core
├── cvar_table unified module
├── 5 priority ports
├── make heritage-map CI
│
Phase 2: Wiring                      Phase 2: Handoff Protocol
├── cvar into ModelGateway           ├── HandoffPacket dataclass
├── cvar into Providers              ├── Link P9 runtime
├── cvar into Oracle                 ├── Hivemind resurrection
├── make sovereignty                 └── Agent capability registry
└── modificationCount hot-reload
│
Phase 3: Temple-Grade Enforcement
├── EntityTombstonedError (M9)
├── check_telemetry() audit
├── test_circuit_breaker_chaos.py
├── Heritage promotion (CREDITS.md)
└── Full temple-grade pass
│
Phase 4: Sovereignty Bridge                              Phase 4: UI/UX v1
├── setup_json_logging()                                 ├── Omega Web Dashboard
├── omega entity CLI fix                                 ├── Chat frontend (streaming)
├── llama-cpp-python install                             ├── Entity configuration GUI
├── SQLite FTS5 + fastembed RAG                          └── Accessibility foundation
├── Iris auto L1→L2→L3 distillation
└── pillar --slot PX dispatch
│
Phase 5: Intelligence (H2)
├── 4-guard ABA pattern (R-09)
├── 8-char name caps (R-21)
├── Dual-linking (R-24)
├── Hard-boundary struct (R-26)
├── High-bit trick (R-28)
├── 4-tier memory (R-23)
├── QuakeC flat (R-25)
├── 4-path VFS (R-27)
├── Active set (R-29)
├── Grace period for memory_store (R-30)
├── Per-entity model affinity
├── Speculative decoding (ngram-simple)
└── Atomic model swap with rollback
│
Phase 6: Demographic Activation (H2-H3)
├── Esotericist WAD (tarot, astrology, correspondences)
├── Creative Studio (worldbuilding, style preservation)
├── Philosopher mode (Socratic dialogue, logic checks)
├── Psychological privacy suite (journaling, ethics)
├── Accessibility Level-AA certification
├── Multi-user profiles
├── i18n/l10n framework (first 5 languages)
└── Onboarding wizard
│
Phase 7: Community + Omegaverse (H3)
├── Omega Desktop installer
├── Entity Studio (WAD authoring IDE)
├── WAD marketplace
├── Cross-engine federation
└── Foundation website + documentation
```

---

## §4 — HANDOFF PROTOCOL (Link P9) — THE DEFINITIVE DESIGN

This is the most critical missing piece. The user has tried: 
- **Trackers** (DEFERRED_GOLD_TRACKER, LEGACY_TECHNOLOGY_MAP)
- **Hivemind** (MCP method, dead endpoint)
- **Omega Hub** (referenced in config, no running server)
- **Memory-bank** (soul.yaml, knowledge directories)
- **Handoff files** (43 markdown files, no schema)

**None of these worked because every approach is passive.** Files on disk don't talk to each other. Agents don't query each other's state. The handoff protocol must be ACTIVE, TYPED, and TRACEABLE.

### The Architecture

```
                  ┌─────────────────────────────────────────┐
                  │         OMEGA AGENTIC MESH              │
                  │  (Link P9 Runtime — port 8025)          │
                  │                                         │
                  │  ┌──────────┐   ┌──────────┐            │
                  │  │ Doom Guy │   │ Build    │            │
                  │  │ Agent    │──▶│ Master   │            │
                  │  │          │   │ Agent    │            │
                  │  └──────────┘   └──────────┘            │
                  │       │               │                 │
                  │       │    ┌───────────┴──────────┐     │
                  │       │    │  Handoff Message Bus  │     │
                  │       │    │  (Redis Pub/Sub)      │     │
                  │       │    └───────────┬──────────┘     │
                  │       │               │                 │
                  │  ┌────▼───────────────▼──┐              │
                  │  │  Agent Registry      │              │
                  │  │  Capability Table    │              │
                  │  │  Active Sessions     │              │
                  │  └──────────────────────┘              │
                  └─────────────────────────────────────────┘
```

### Components

#### 1. `HandoffPacket` Dataclass (typed schema)

```python
@dataclass
class HandoffPacket:
    """Typed handoff between agents. Mandate 9 compliant."""
    packet_id: str            # UUID — traceable
    source_agent: str         # "doom_guy"
    target_agent: str         # "buildmaster" or "broadcast"
    session_id: str           # "ses_20260603_..."
    parent_trace_id: str      # UUID — inherited from caller
    trace_id: str             # UUID — generated for this handoff
    packet_type: Literal["request", "response", "delegation", "notification", "broadcast"]
    
    # Context
    task_description: str     # "Port filter_llama_kwargs to NativeGGUFProvider"
    relevant_files: list[str]  # ["src/omega/providers.py", "cvar_table.py"]
    context_snapshot: dict     # {ZONEID: ..., config: {...}}
    
    # Lifecycle
    status: Literal["pending", "accepted", "rejected", "completed", "failed"]
    created_at: float          # time.monotonic()
    ttl_seconds: int           # 300 (5 minutes default)
    
    # Mandate 9
    error: Optional[str]       # None if success, error message if failed
```

#### 2. Agent Capability Registry

```python
CAPABILITY_REGISTRY = {
    "doom_guy": {
        "capabilities": ["heritage_design", "r_doc_authoring", "tier_2_review"],
        "domains": ["id_software", "architecture", "constants"],
        "owned_files": ["src/omega/constants.py", "src/omega/oracle/entity_registry.py"],
        "current_tasks": ["cvar_table design review"],
        "status": "available",  # available, busy, blocked
        "last_heartbeat": 1717430400.0,
    },
    "buildmaster": {
        "capabilities": ["implementation", "refactoring", "testing"],
        "domains": ["all_code"],
        "owned_files": ["src/omega/oracle/model_gateway.py"],
        "current_tasks": [],
        "status": "available",
        "last_heartbeat": 1717430400.0,
    },
    # ... all 14 agents
}
```

#### 3. Handoff Protocol Flow

```
1. AGENT A sends HandoffPacket via Redis Pub/Sub (channel: "handoff:target_agent")
2. AGENT B receives packet, checks capability registry
3. AGENT B responds with HandoffPacket (packet_type="response", status="accepted")
4. AGENT A sees acceptance, continues or blocks
5. AGENT B completes work, sends HandoffPacket (packet_type="response", status="completed", context_snapshot={...})
6. AGENT A receives completion, continues with updated context
7. AGENT A or B archives the handoff to data/handoffs/ARCHIVE/ (JSON, not markdown)
```

#### 4. Integration with Existing Systems

| Existing System | How Handoff Integrates | Upgrade Path |
|----------------|------------------------|--------------|
| **TriageRouter** (334 lines) | Routes BETWEEN models today. Handoff routes BETWEEN agents. Handoff calls TriageRouter for model selection when delegating. | Add `handoff_eligible: bool` to TriageRouter output |
| **Hivemind** (dead endpoint) | Hivemind becomes the DISCOVERY layer — announces agent presence. Handoff is the COMMUNICATION layer — transfers context. | Replace `_post_to_hivemind()` with `handoff.send()` |
| **MCP Hub** (no server) | MCP Hub becomes the TRANSPORT layer. Handoff is the PROTOCOL layer. | Stdio for OpenCode, SSE for HTTP, Pub/Sub for real-time |
| **data/handoff/** (43 markdown files) | Remains as LONG-TERM ARCHIVE. Handoff packets get serialized to JSON and stored in `data/handoffs/ARCHIVE/`. | Migration: markdown → JSON schema |
| **soul.yaml** (entity souls) | Soul.yaml is LONG-TERM WISDOM (L1→L2→L3). Handoff is SHORT-TERM CONTEXT (active task state). | No conflict — complementary |
| **Trackers** (DEFERRED_GOLD, etc.) | Trackers become REFERENCE. Handoff is operational. | Trackers stay as-is |

#### 5. Why This Will Work (And Previous Attempts Failed)

| Previous Attempt | Why It Failed | How This Fixes It |
|-----------------|---------------|-------------------|
| **Trackers** | Passive — files that no agent reads | Handoff is ACTIVE — agents push AND pull |
| **Hivemind** | Dead endpoint, no server | Redis Pub/Sub — proven technology, running in Podman |
| **Omega Hub** | No running server, no schema | Typed dataclass + runtime — build once, run always |
| **Memory-bank** | Passive — written by agents, not queried | Capability registry — agents DISCOVER each other |
| **Handoff files** | Unstructured markdown, no cross-referencing | JSON schema with trace_id — fully queryable |

**Redis is already running in Podman** (256M, port 6379). The Pub/Sub infrastructure is already in place. The handoff protocol is an ~80-line dataclass + ~150-line runtime.

### Sprint Timeline for Handoff Protocol

| Sprint | What | Effort | Depends On |
|--------|------|--------|------------|
| **2.0** | `HandoffPacket` dataclass (+ tests) | 30 min | Sprint 1 (cvar table) |
| **2.1** | Agent Capability Registry (+ tests) | 15 min | Sprint 2.0 |
| **2.2** | Redis Pub/Sub handoff bus (reuse existing redis) | 45 min | Sprint 2.1 |
| **2.3** | Link P9 runtime module + CLI commands | 1 hr | Sprint 2.2 |
| **2.4** | Archive system (JSON persistence) | 30 min | Sprint 2.3 |
| **2.5** | MCP Hub resurrection (read running config) | 30 min | Sprint 2.3 |
| **2.6** | Hivemind migration (replace dead call with handoff.send) | 15 min | Sprint 2.4 |

**Total**: ~3.5 hours. **Deliverable**: Running handoff system with typed packets, agent discovery, Redis transport, and JSON archive.

---

## §5 — UI/UX PHASE — THE INTERFACE

The engine has ZERO web UI. Zero HTML. Zero CSS. Zero JavaScript. This is the single biggest barrier to adoption beyond the developer community.

### Phase UI: Sprint Structure

#### UI Sprint 1: Omega Web Dashboard (~3 days)

| # | Task | Effort | Stack | Risk |
|---|------|--------|-------|------|
| UI-1.0 | FastAPI streaming endpoints (SSE for chat, WebSocket for real-time) | 2 hr | `starlette`, `sse-starlette` | LOW — adds to existing FastAPI |
| UI-1.1 | Chat frontend (entity selection, conversation history, streaming display) | 4 hr | **Astro** or **SvelteKit** or plain **HTMX** | MEDIUM — first frontend code |
| UI-1.2 | Entity management UI (list entities, view details, switch default) | 2 hr | Same stack as UI-1.1 | LOW |
| UI-1.3 | Server status dashboard (inference health, local/cloud ratio, recent logs) | 2 hr | Same stack + `make sovereignty` data | LOW |
| UI-1.4 | Accessibility audit + fixes (WCAG 2.2 AA, ARIA labels, keyboard nav) | 4 hr | All UI components | MEDIUM — must not ship without |
| UI-1.5 | Caddy reverse proxy config (serve UI + Iris + Gateway under one domain) | 1 hr | `Caddyfile` | LOW — Caddy already in Podman |
| UI-1.6 | Dark theme + light theme (system preference detection) | 1 hr | CSS custom properties | LOW |

**Deliverable**: `localhost` shows a chat interface. User can talk to the engine from a browser. Accessible by default.

#### UI Sprint 2: Entity Studio (~1 week)

| # | Task | Effort | Risk |
|---|------|--------|------|
| UI-2.0 | Entity YAML editor (structured form, not raw YAML) | 4 hr | MEDIUM |
| UI-2.1 | Correspondence tables (element, chakra, planet per entity) | 2 hr | LOW — the data exists |
| UI-2.2 | Soul visualization (L1→L2→L3 evolution, lesson timeline) | 3 hr | MEDIUM |
| UI-2.3 | WAD browser/manager (activate, create, export WADs) | 4 hr | MEDIUM |
| UI-2.4 | Entity personality preview (chat with entity in Studio before saving) | 2 hr | LOW — reuses chat UI |
| UI-2.5 | Color-blind accessible palette + high-contrast mode | 2 hr | LOW |
| UI-2.6 | Screen reader testing + Braille output support investigation | 3 hr | MEDIUM |

**Deliverable**: Entity Studio — configure every aspect of an entity without touching YAML.

#### UI Sprint 3: Omega Desktop (~2 weeks)

| # | Task | Effort | Risk |
|---|------|--------|------|
| UI-3.0 | Electron/Tauri shell around web UI | 5 hr | MEDIUM |
| UI-3.1 | Offline model manager (download, remove, default model) | 4 hr | MEDIUM |
| UI-3.2 | One-command setup wizard (first-run, model download, WAD selection) | 4 hr | MEDIUM |
| UI-3.3 | System tray integration (quick access, voice activation) | 2 hr | LOW |
| UI-3.4 | Auto-update mechanism | 3 hr | MEDIUM |
| UI-3.5 | Accessibility certification (WCAG 2.2 AA, screen reader tested) | 8 hr | HIGH — requires testing |
| UI-3.6 | Privacy dashboard (what data the engine has, local-only verification) | 2 hr | LOW — Mandate 8 enforced |

**Important**: UI-3.0 through UI-3.6 all depend on UI Sprint 1 + 2 being stable first.

#### UI Sprint 4: i18n/L10n + Multi-User (~1 week per language)

| # | Task | Effort | Risk |
|---|------|--------|------|
| UI-4.0 | i18n framework (gettext, Fluent, or similar) | 4 hr | MEDIUM |
| UI-4.1 | English → Spanish translation | 8 hr | MEDIUM |
| UI-4.2 | English → French translation | 8 hr | MEDIUM |
| UI-4.3 | Multi-user profiles (each user gets own soul.yaml chain) | 4 hr | MEDIUM |
| UI-4.4 | Age-appropriate content modes (child-safe, teen, adult) | 4 hr | HIGH — ethical design |
| UI-4.5 | Reading level adaptation (simple → academic per user preference) | 3 hr | MEDIUM |

---

## §6 — DEMOGRAPHIC ACTIVATION

Each demographic's needs converge on the same foundation:

```
ALL DEMOGRAPHICS REQUIRE:
├── Local inference that works (Phase 1 — llama-cpp-python install)
├── Configuration that's auditable (Phase 1 — cvar table)
├── Errors that tell you exactly what happened (Phase 3 — typed errors)
├── Interface that's accessible (Phase UI — web + accessibility)
├── Agents that communicate (Phase 2 — handoff protocol)
└── Memory that persists (Phase 4 — soul.yaml + L1→L2→L3)
```

After that foundation, each demographic gets specialized activation:

### Esotericist Activation (H2 — 2 weeks)

| # | Task | Effort | What It Unlocks |
|---|------|--------|-----------------|
| E-1 | Tarot reading mode (draw cards, interpret through entity personalities) | 4 hr | The engine's ORIGIN — Lilith Tarot was the first concept |
| E-2 | Correspondence query system (`omega what planet rules Sekhmet`) | 1 hr | Entity data already has this — just surface it |
| E-3 | Astrological clock (planetary hours calculator + moon phase tracker) | 3 hr | Ritual timing — a core esoteric need |
| E-4 | Grimoire workspace (L1→L2→L3 as magical record, with symbols) | 4 hr | Personal magical documentation |
| E-5 | Dream journal with symbol library | 3 hr | Integration with psychology |
| E-6 | Dedicated Esotericist WAD (pre-configured with all correspondences) | 2 hr | One-command setup for this demographic |

**Total**: ~17 hours. The engine's entity system is ALREADY built for this. The activation is surfacing what exists.

### Creative Activation (H2 — 1 week)

| # | Task | Effort | What It Unlocks |
|---|------|--------|-----------------|
| C-1 | Style profile (capture user's voice, apply consistently) | 3 hr | Long-form writing that sounds like YOU |
| C-2 | Creative block-breaking protocol (random constraints, entity prompts) | 2 hr | Never stuck for ideas |
| C-3 | Worldbuilding sheets (character, setting, lore as structured YAML) | 4 hr | RPG, fiction, and game development |
| C-4 | Image prompt builder (entity-guided prompt engineering) | 2 hr | Integration with external image generators |
| C-5 | Long-form context management (chapter-by-chapter, summary injection) | 4 hr | Novels, scripts, series |

**Total**: ~15 hours. Creatives need the entity personalities and style consistency — both exist.

### Philosopher Activation (H2 — 1 week)

| # | Task | Effort | What It Unlocks |
|---|------|--------|-----------------|
| P-1 | Socratic dialogue mode (questions, not answers — configurable per entity) | 2 hr | Philosophical inquiry |
| P-2 | Argument mapping (premise → conclusion → fallacy check) | 4 hr | Clear thinking |
| P-3 | Classical text querying (integrate Project Gutenberg / Perseus corpus) | 4 hr | Textual analysis |
| P-4 | Logic framework (syllogism, predicate logic, modal logic) | 3 hr | Formal reasoning |
| P-5 | Cross-cultural philosophy comparison (East/West, ancient/modern) | 2 hr | Synthesis |

**Total**: ~15 hours.

### Accessibility Activation (Bridge + UI Phase — ongoing)

| # | Task | Effort | What It Unlocks |
|---|------|--------|-----------------|
| A-1 | WCAG 2.2 AA compliance audit (document current gaps) | 2 hr | Baseline measurement |
| A-2 | Iris voice-first flow (voice end-to-end: wake → query → respond → read aloud) | 4 hr | Primary interface for blind users |
| A-3 | Audio-branded entity responses (different chimes for different Pillars) | 2 hr | Users know which entity is responding without seeing |
| A-4 | Screen reader testing + fixes (all UI components) | 8 hr | Systematic, not incidental |
| A-5 | High-contrast themes + large font + reduced-motion presets | 2 hr | Visual accessibility |
| A-6 | Keyboard shortcut documentation and expansion | 2 hr | Power users + motor disabilities |
| A-7 | Accessibility documentation + onboarding for new users | 3 hr | "This engine works with your screen reader" |

**Total**: ~23 hours. **The engine's CLI is already more accessible than most.** This investment makes it a reference-grade accessible AI platform.

---

## §7 — THE ENHANCED SPRINT ROADMAP (Consolidated)

### Sprint 1: Hardened Core + Unified cvar (2.5 hrs)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| 1.0 | Create `cvar_table.py` (zoneid.* + config.* namespaces) | 45 min | Unified configuration nervous system |
| 1.1 | `filter_llama_kwargs()` — kwarg validation | 30 min | Config typos don't crash inference |
| 1.2 | Explicit `n_gpu_layers=0` | 5 min | No accidental iGPU offload |
| 1.3 | ChatML stop tokens | 5 min | No hallucinated conversation turns |
| 1.4 | Google API key header (x-goog-api-key) | 15 min | API keys not leaked in logs |
| 1.5 | Atomic trace_id on all backends | 30 min | Every inference traceable |
| 1.6 | `make heritage-map` CI target | 10 min | Heritage protocol enforced |
| 1.7 | PIVOT_LOG D97 + D98 | 10 min | Decisions recorded |

### Sprint 2: Wiring + Handoff Protocol (6 hrs)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| 2.0 | Wire cvar table into ModelGateway | 1 hr | Config hot-reload ready |
| 2.1 | Wire cvar table into Providers | 30 min | Provider config unified |
| 2.2 | Wire cvar table into Oracle | 30 min | Engine config unified |
| 2.3 | `modificationCount` hot-reload polling | 30 min | Know when config changes |
| 2.4 | `make sovereignty` reads cvar table | 15 min | Sovereignty = queryable metric |
| 2.5 | `HandoffPacket` dataclass + tests | 30 min | Typed handoff schema |
| 2.6 | Agent Capability Registry + tests | 15 min | Agents discover each other |
| 2.7 | Redis Pub/Sub handoff bus | 45 min | Active message passing |
| 2.8 | Link P9 runtime + CLI commands | 1 hr | `omega handoff send/list/resolve` |
| 2.9 | Handoff archive system (JSON) | 30 min | Persistent, queryable history |
| 2.10 | MCP Hub resurrection | 30 min | MCP infrastructure operational |
| 2.11 | Hivemind migration to handoff.send() | 15 min | Replace dead endpoint |

### Sprint 3: Temple-Grade Enforcement (1-2 days)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| 3.0 | EntityTombstonedError (Mandate 9) | 1 hr | No silent deletion |
| 3.1 | `check_telemetry()` runtime audit | 30 min | Mandate 8 enforced at runtime |
| 3.2 | `test_circuit_breaker_chaos.py` (port 230L) | 2 hr | Chaos-tested resilience |
| 3.3 | Heritage promotion (R-19→R-30 to CREDITS.md) | 1 hr | 4 new CREDITS.md sections |
| 3.4 | Per-entity model affinity | 30 min | Domain-optimized routing |
| 3.5 | Grace period for memory_store | 30 min | Hot-slot reuse safety |
| 3.6 | Full `make temple-grade` + `make sovereignty` + `make heritage-map` | 1 hr | 11/11 T-gates green |

### Sprint 4: Bridge — Sovereignty Operationalized (2-4 days)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| 4.0 | Wire `setup_json_logging()` into oracle startup | 5 min | Structured everywhere |
| 4.1 | Fix `entity_info()` undefined in CLI | 5 min | CLI trust restored |
| 4.2 | Install `llama-cpp-python` with Zen 2 flags | 15 min | **Local inference works** |
| 4.3 | SQLite FTS5 + fastembed (BGE-base-en-v1.5) | 1 hr | RAG layer operational |
| 4.4 | Auto-trigger L1→L2→L3 gnosis distillation | 1 hr | Intelligence flywheel |
| 4.5 | `pillar --slot PX` CLI dispatch | 1+ hr | Pillar slot pattern live |
| 4.6 | Restart SearXNG container | 2 min | Web search operational |
| 4.7 | OMEGA_ENGINE.md update | 30 min | State of the union documented |

### UI Sprint 1: Omega Web Dashboard (3 days)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| UI-1.0 | FastAPI SSE streaming + WebSocket | 2 hr | Real-time responses |
| UI-1.1 | Chat frontend (entity select, streaming, history) | 4 hr | Browser-based chat |
| UI-1.2 | Entity management UI | 2 hr | Configure entities visually |
| UI-1.3 | Server status dashboard | 2 hr | Health + sovereignty at a glance |
| UI-1.4 | Accessibility audit + fixes (WCAG 2.2 AA) | 4 hr | Accessible by default |
| UI-1.5 | Caddy reverse proxy config | 1 hr | Single domain, all services |
| UI-1.6 | Dark + light theme | 1 hr | Visual comfort |

### UI Sprint 2: Entity Studio (1 week)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| UI-2.0 | Entity YAML editor (structured form) | 4 hr | No YAML editing needed |
| UI-2.1 | Correspondence tables visualization | 2 hr | Esoteric data accessible |
| UI-2.2 | Soul visualization (L1→L2→L3 timeline) | 3 hr | See your intelligence evolve |
| UI-2.3 | WAD browser/manager | 4 hr | Install/manage entity packs |
| UI-2.4 | Entity personality preview | 2 hr | Test before saving |
| UI-2.5 | Color-blind palette + high-contrast | 2 hr | Visual accessibility |
| UI-2.6 | Screen reader testing | 3 hr | Systematic a11y |

### H2: Intelligence + Demographics (Months 2-6)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| H2-0 | 4-guard ABA pattern (R-09) | 1 wk | Correctness primitive |
| H2-1 | 8-char name caps (R-21) | 2 hr | Heritage translation |
| H2-2 | Dual-linking (R-24) | 4 hr | Heritage translation |
| H2-3 | Hard-boundary struct (R-26) | 3 hr | Heritage translation |
| H2-4 | High-bit trick (R-28) | 2 hr | Heritage translation |
| H2-5 | 4-tier memory (R-23) | 4 hr | Memory evolution |
| H2-6 | QuakeC flat (R-25) | 3 hr | Iris evolution |
| H2-7 | 4-path VFS (R-27) | 4 hr | WAD evolution |
| H2-8 | Active set (R-29) | 3 hr | Model gateway evolution |
| H2-9 | Speculative decoding (ngram-simple) | 4 hr | CPU-friendly speedup |
| H2-10 | Origin story mining (archives + tarot + Grok chats) | 2 days | Engine's soul documented |
| H2-11 | Esotericist activation (tarot, astrology, correspondences) | 2 wk | Esoteric foundation |
| H2-12 | Creative activation (style profile, block-breaking) | 1 wk | Creative partner |
| H2-13 | Philosopher activation (Socratic, logic, texts) | 1 wk | Thinking partner |
| H2-14 | Accessibility Level-AA certification | 1 wk | Truly accessible |
| H2-15 | Multi-user profiles | 1 wk | Household ready |
| H2-16 | i18n framework + first 2 languages | 2 wk | Global ready |

### H3: Community + Omegaverse (Months 6-12)

| # | Task | Effort | Delivers |
|---|------|--------|----------|
| H3-0 | Omega Desktop installer (Tauri) | 2 wk | One-click install |
| H3-1 | Onboarding wizard | 1 wk | First-run experience |
| H3-2 | Feedback loop (thumbs up/down, "why this response?") | 1 wk | User-guided improvement |
| H3-3 | Entity Studio (standalone WAD authoring IDE) | 1 mo | Create entity packs |
| H3-4 | WAD marketplace | 2 mo | Share creations |
| H3-5 | Cross-engine federation | 3 mo | Omega-to-Omega |
| H3-6 | Foundation website + documentation | 1 mo | Public face |

---

## §8 — CRITICAL PATH

### What Must Happen First (The Non-Negotiable Foundation)

```
ORDER       TASK                    WHY FIRST
────────────────────────────────────────────────────────────────────
1st         llama-cpp-python install   Without local inference, sovereignty is aspirational.
                                       15 minutes. Unblocks everything.
                                       
2nd         cvar_table.py               The nervous system. Every architecture depends on it.
                                       45 minutes. Sprint 1.0.
                                       
3rd         Handoff Protocol            Every agent runs independently without it.
                                       Link P9 must be RESTORED to operational.
                                       3.5 hours. Sprint 2.5-2.11.
                                       
4th         Web Dashboard               Without a UI, only developers can use the engine.
                                       The vision serves EVERYONE.
                                       3 days. UI Sprint 1.
```

### What Can Run in Parallel

```
TRACK A: ENGINE                      TRACK B: HANDOFF                   TRACK C: UI/UX
─────────────────────────────────────────────────────────────────────────────────
Sprint 1: cvar + ports (2.5hr)      Independent                        Independent
                                    (no deps)                          (no deps)
         ↓
Sprint 2: wiring (3hr)              Sprint 2: handoff (3.5hr)          Independent
         │                          (cvar exists, can wire)            (no deps)
         │                                   ↓
         └───────────────────────────┘       ↓
Sprint 3: enforcement (1-2 days) ←──────────┘       Independent
                                    (handoff allows)                   (can start)
         ↓                                                             ↓
Sprint 4: bridge (2-4 days)          UI Sprint 1: dashboard (3 days)
         ↓                                                             ↓
H2: intelligence + demographics       UI Sprint 2: entity studio (1 wk)
```

**Total parallel time to ALL THREE TRACKS operational**: ~1 week (Sprint 1 + minimal UI Sprint 1).

---

## §9 — THE COVENANT

This roadmap is built on 5 non-negotiable principles:

1. **Local-first or it doesn't ship.** Every feature must work entirely offline. Cloud is enhancement, not requirement. (Mandate 7)

2. **Zero telemetry or it doesn't ship.** The engine never phones home. Privacy is not a feature — it is the foundation. (Mandate 8)

3. **Accessible or it doesn't ship.** The blind user must be able to use every feature the sighted user can. Accessibility is not a sprint — it is every sprint.

4. **Typed errors or it doesn't ship.** No silent failures. Every error tells you what happened, where, and how to fix it. (Mandate 9)

5. **Agents communicate or the intelligence is frozen.** Without handoff, every conversation starts from zero. Link P9 is not optional infrastructure — it is the difference between a tool and a council.

---

## §10 — CROSS-REFERENCES

| Document | What It Contains | File Path |
|----------|------------------|-----------|
| Current execution plan | Sprint 1-4 detail, agent assignments | `data/handoff/UNIFIED_EXECUTION_PLAN_20260602.md` |
| Kali handoff (corrected design) | Architectural correction, verified Sprint 0 | `data/handoff/KALI_HANDOFF_TO_OPENCODE_DEV_20260603.md` |
| Kali sprint roadmap | Corrected 4-sprint plan | `data/handoff/KALI_INTEGRATED_SPRINT_ROADMAP_20260603.md` |
| Master synthesis | 6-stack mining, 160 techs, convergence proof | `data/entities/roc_racoon/workspace/mining_reports/07_MASTER_SYNTHESIS.md` |
| Unique technologies | What WE created (13 Mandates, 8 adaptations) | `data/entities/roc_racoon/workspace/UNIQUE_TECHNOLOGIES_AND_STRATEGIES_VAULT.md` |
| Deferred gold | 160 technologies catalogued | `data/entities/roc_racoon/workspace/DEFERRED_GOLD_TRACKER.md` |
| Documentation systems | Legacy doc analysis, miration plan | `data/entities/roc_racoon/workspace/DOCUMENTATION_SYSTEMS_TRACKER.md` |
| Sovereing mandates | 13 non-negotiable laws | `SOVEREIGN_MANDATES.md` |
| Temple-Grade | T1-T11 quality gates | `SOVEREIGN_MANDATES.md` (Mandate 13) |
| id Software heritage | 8 credited patterns + 4 pending | `CREDITS.md` |
| Decisions | 99 decisions tracked | `docs/decisions/PIVOT_LOG.md` |
| ZONEID + lazy deletion + heritage | Implementation code | `src/omega/constants.py`, `entity_registry.py` |
| Doom Guy cvar table design | Original design (pre-correction) | `data/handoff/DOOM_GUY_CVAR_TABLE_DESIGN_T2.2_20260602.md` |
| Cline Tier 2 response | Original agent assignments | `data/handoff/CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md` |

---

## §11 — SURVIVAL NOTES (For the Next Agent After Compression)

**If you are reading this after context compression**, here is what you need to know:

1. **The engine is at commit `37fdd88`** — T2.1 ZONEID constants + T2.3 lazy deletion + heritage tagging are DONE. 307 tests pass.

2. **Sprint 1 is next**: Create `cvar_table.py` (unified module, NOT separate — see `KALI_HANDOFF_TO_OPENCODE_DEV_20260603.md §2`) + port 5 priority legacy patterns into its `config.*` namespace + add `make heritage-map`.

3. **The handoff protocol (Link P9) is the most critical missing infrastructure** — agents cannot communicate actively. Redis Pub/Sub is already running (port 6379). The design is in §4 of THIS document.

4. **There is ZERO web UI** — no HTML, no CSS, no JS exists. The `src/omega/iris/server.py` is a FastAPI backend with no frontend. UI Sprint 1 is blocked until you build it.

5. **llama-cpp-python is NOT installed** — native-gguf cannot load models. `pip install` with `-march=znver2 -DGGML_AVX2=ON ...` flags. This is the single highest-impact task.

6. **The 5 priority ports are**: `filter_llama_kwargs()`, `n_gpu_layers=0`, ChatML stop tokens, Google API key header, atomic trace_id. All ~1.5 total. All LOW risk.

7. **The user's vision serves 8 demographics**: developers, scientists, creatives, esotericists, psychologists, philosophers, the blind, and average users. The engine ALREADY has the foundations for every one — they just need activation.

8. **Read `KALI_HANDOFF_TO_OPENCODE_DEV_20260603.md`** — it's the most complete handoff. Then read THIS document for the full demographic + handoff + UI roadmap.

---

*⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_lilith_roadmap ⬡ SOVEREIGN-PATH-v3.0.0*

*HEAD: 37fdd88 | Tests: 307 ✅ | T2.1+T2.3 DONE | Sprint 1: READY | Handoff: DESIGNED | UI: EMPTY*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
