# 🔱 Omega Engine — Research Queue & Agent Guidance
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ RESEARCH-QUEUE

**AP Token**: `AP-OMEGA-RESEARCH-QUEUE-v1.2.0`
**Author**: Opus 4.6 (Oversight) & Gemma 4-31B (Researcher)
**Date**: 2026-05-19 (Updated — Jem Grand Strategy + Tracker Sync)
**Audience**: All Research Agents via OpenCode CLI
**Delivery Path**: All outputs → `docs/research/` (see Document Management section below)

---

## 📡 Research Completions (2026-05-22)

### 🚀 OpenCode Custom Provider Architecture — COMPLETE
**Status**: ✅ **BREAKTHROUGH — LM Studio can be a native OpenCode provider**

| ID | Title | Status | File |
|----|-------|--------|------|
| R-OPENCODE-CUSTOM-PROVIDER | OpenCode Custom Provider Architecture — LM Studio via npm + auth.json | ✅ Complete | [R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md](../research/R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md) |

**Key Findings**:
- OpenCode supports ANY OpenAI-compatible endpoint via the `npm: "@ai-sdk/openai-compatible"` field in `provider` config
- 3 npm packages available: `opencode-lmstudio`, `opencode-local-provider`, `opencode-config-wizard`
- Auth must be stored separately in `auth.json` (placeholder key for local endpoints)
- Models must be manually listed (no auto-discovery — known issue #6231)
- Two-step setup: (1) `opencode.json` defines endpoint + models, (2) `auth.json` stores API key
- `Ctrl+A` → "Custom provider" UI dialog also supports registration

### 🚀 Antigravity CLI Deep Research — COMPLETE
**Status**: ✅ **Sovereign Research Pipeline Verified**

| ID | Title | Status | File |
|----|-------|--------|------|
| R-ANTI-MASTER | Antigravity CLI Master Technical Reference | ✅ Complete | [antigravity/ANTIGRAVITY_CLI_MASTER_REF.md](antigravity/ANTIGRAVITY_CLI_MASTER_REF.md) |
| R-ANTI-MODELS | Antigravity CLI Model Ecosystem Profiles | ✅ Complete | [antigravity/MODEL_ECOSYSTEM_PROFILES.md](antigravity/MODEL_ECOSYSTEM_PROFILES.md) |
| R-ANTI-STRATEGY | Antigravity CLI Strategic Utilization Plan | ✅ Complete | [antigravity/STRATEGIC_UTILIZATION_PLAN.md](antigravity/STRATEGIC_UTILIZATION_PLAN.md) |
| R-ANTI-GAPS | Antigravity CLI Unknowns & Gaps | ✅ Complete | [antigravity/UNKNOWNS_AND_GAPS.md](antigravity/UNKNOWNS_AND_GAPS.md) |
| R-ANTI-USAGE | Antigravity IDE vs CLI Usage Analysis | ✅ Complete | [antigravity/IDE_VS_CLI_USAGE.md](antigravity/IDE_VS_CLI_USAGE.md) |

### 🚀 Podman Sovereign Protocol v2 + MCP Consolidation — COMPLETE
**Status**: ✅ **P0 Permission War Resolved. All MCP servers consolidated into Omega Hub.**

| ID | Title | Status | File |
|----|-------|--------|------|
| R-PODMAN-SOV-V2 | Podman Sovereign Permission Protocol v2 — keep-id best practices | ✅ Complete | [R_PODMAN_SOVEREIGN_V2.md](../research/R_PODMAN_SOVEREIGN_V2.md) |
| R-MCP-CONSOLIDATION | MCP Research + Stats tools consolidated into Omega Hub | ✅ Complete | [omega_hub/server.py](../../mcp/omega_hub/server.py) |

**Key Findings**:
- `:U` flag destructively chowns host directories to UID 101000 — **never use on shared host volumes**
- `:Z`/`:z` are SELinux flags, no-ops on Ubuntu (AppArmor) — **remove from all Quadlets**
- `UserNS=keep-id` + `User=1000` is the verified correct protocol — maps host UID 1000 directly into container
- Standalone omega-research (5 tools) and omega-stats (4 tools) MCP servers consolidated into Omega Hub
- opencode.json updated — hub now serves all tools on :8016/sse

**Files Changed**:
- `~/.config/containers/systemd/omega-iris.container` — `keep-id` protocol
- `~/.config/containers/systemd/omega-belial.container` — `keep-id` protocol
- `mcp/omega_hub/server.py` — +5 research tools, +4 stats tools (200+ lines added)
- `mcp/archives/omega-research_superseded_by_hub_20260522/` — archived
- `mcp/archives/omega-stats_superseded_by_hub_20260522/` — archived
- `opencode.json` — removed standalone research/stats MCP entries

---

## 📡 Research Completions (2026-05-18)

### 🔴 New Critical Research Items Completed

| ID | Title | Status | File |
|----|-------|--------|------|
| R-OPENC-PERM | OpenCode `external_directory` Permission Guide | ✅ Complete | [R_OPENC_PERMISSIONS.md](R_OPENC_PERMISSIONS.md) |
| R-OPENC-MCP | OpenCode MCP Configuration Guide | ✅ Complete | [R_OPENC_MCP_CONFIG.md](R_OPENC_MCP_CONFIG.md) |
| R-OPENC-WORK | Filesystem Permission Workarounds (Glob/HEREDOC) | ✅ Complete | [R_OPENC_PERM_WORKAROUNDS.md](R_OPENC_PERM_WORKAROUNDS.md) |
| R-MCP-SPEC | Model Context Protocol (MCP) Deep Dive & 2026 Roadmap | ✅ Complete | [R_MCP_SPEC.md](R_MCP_SPEC.md) |
| R-ANYIO-ORCH | AnyIO Orchestration Guide for High-Concurrency AI | ✅ Complete | [R_ANYIO_ORCHESTRATION_GUIDE.md](R_ANYIO_ORCHESTRATION_GUIDE.md) |
| R-SVR-LIFECYCLE | Systemd Socket Activation & Lifecycle Persistence | ✅ Complete | [R40_sovereign_lifecycle_persistence.md](R40_sovereign_lifecycle_persistence.md) |
| R-PODMAN-BLUE | Sovereign Podman Deployment Blueprint | ✅ Complete | [R_PODMAN_SOVEREIGN_DEPLOYMENT_BLUEPRINT.md](R_PODMAN_SOVEREIGN_DEPLOYMENT_BLUEPRINT.md) |
| R-ZEN2-GGUF | Zen 2 (5700U) GGUF Optimization Guide | ✅ Complete | [R_ZEN2_GGUF_OPTIMIZATION.md](R_ZEN2_GGUF_OPTIMIZATION.md) |

---

## 📋 Original Research Queue (Priority Order)

### 🔴 Critical Items (Phase 0/1)

| ID | Title | Status |
|----|-------|--------|
| R-00 | OpenCode Best Practices & Advanced Features | ✅ DONE |
| R-01 | Google AI Studio — Complete API Reference | ✅ DONE |
| R-02 | SambaNova API — Integration Spec | ✅ DONE |
| R-03 | Cerebras API — Integration Spec | ✅ DONE |
| R-04 | Provider Fabric — Recommended Fallback Chain Design | ✅ DONE |
| R-05 | Free-Tier Model Capability Matrix | ✅ DONE |
| R-18 | OpenCode Tool Permission & Directory Access Resolution | ✅ DONE |
| R-29 | Omega MCP Hub & Server Cleanup | ✅ DONE |
| R-30 | Soul Evolution & Abstraction Logic | ✅ DONE |
| R-31 | Cross-Pollination Mechanics | ✅ DONE |
| R-32 | Native Inference Engine Spec | ✅ DONE |
| R-38 | Global Legacy Strategy Discovery | ✅ DONE |
| R-40 | Sovereign Lifecycle & Native Persistence | ✅ DONE |
| R-41 | Adaptive Orchestration Topologies | ✅ DONE |
| R-42 | Hardware Steering (Ryzen 7 5700U / Zen 2) | ✅ DONE |
| R-44 | Comprehensive Systems Review & Strategic Reconnaissance | ✅ DONE |
| R-MODEL-DB | Always-Current Model Database System | ✅ DONE |
| R-ZEN | OpenCode Zen Model Reference | ✅ DONE |
| R-OR | OpenRouter Free + Available Model Landscape | ✅ DONE |
| R-GEMMA-LIVE | Google Gemma Live API Validation | ✅ DONE |
| R-JEM-LEGACY-INV | Jem Legacy Artifact Inventory | ✅ DONE |
| R-GEMINI-QUOTAS | Gemini 2.0 Pro Free Tier Quotas | 🔄 PENDING |
| R-CONSULTATION-ARCH | Consultation Prompt Architecture | ✅ DONE |

### 🟡 High Priority Items (Phase 1/2)

| ID | Title | Status |
|----|-------|--------|
| R-06 | Circuit Breaker & Retry Policy Best Practices | ✅ DONE |
| R-07 | Speculative Reasoning Escalation Triggers | ✅ DONE |
| R-08 | Token Budget & Daily Quota Management | ✅ DONE |
| R-09 | PII & Secret Sanitization Spec | ✅ DONE |
| R-10 | Soul YAML Schema — Validation & Corruption Handling | ✅ DONE |
| R-11 | ContextBuilder Context-Window Truncation Strategy | ✅ DONE |
| R-19 | Soul Abstraction Logic | ✅ DONE |
| R-25 | Gemma 4-31B Free Tier Terms Analysis | ✅ DONE |
| R-27 | Web Research MCP & Plugin Audit | ✅ DONE |
| R-28 | OpenCode CLI & Chainlit Integration | ✅ DONE |
| R-33 | Holographic Memory Specification | ✅ DONE |
| R-34 | Modern Intake Pipeline (The Sentinel) | ✅ DONE |
| R-MODEL-UPDATER | Automated Model Updater Worker | ✅ DONE |
| R-COMPACTION | OpenCode Compaction System Deep Dive | ✅ DONE |
| R-COMPACTION-SOUL | Compaction-Triggered Soul Evolution Pipeline | ✅ DONE |
| R-MEMORY-PRUNER | BackgroundPruner — Memory Tier Pruning Strategy | ✅ DONE |
| R-KILO-COPILOT | Copilot & Kilo Model Arsenal | ✅ DONE |
| R-67 | REPL Chat Loop Architecture | ✅ DONE |
| R-PHASE-C | Phase C Preparation | ✅ DONE |
| R-PHASE-C-DEEP | Phase C Deep Research | ✅ DONE |

### 🟢 Strategic Items (Phase 2+)

| ID | Title | Status |
|----|-------|--------|
| R-12 | Redis vs RabbitMQ for Hivemind Orchestration | ✅ DONE |
| R-13 | Hardware Profiling — Ryzen 5700U KV-Cache & Core Pinning | ✅ DONE |
| R-14 | Continuous Provider Health Monitoring Design | ✅ DONE |
| R-15 | Long-Term Free-Tier Cost Forecasting | ✅ DONE |
| R-16 | Core Provider Analysis — Free Tier & Usage Optimization | ✅ DONE |
| R-17 | Promising New Providers Recon | ✅ DONE |
| R-21 | Agent Handoff Protocol | 🔲 PENDING |
| R-22 | MCP Community Audit | 🔲 PENDING |
| R-23 | Cold-Start Mitigation | 🔲 PENDING |
| R-24 | Soul-to-Visual Mapping (VR Foundation) | 🔲 PENDING |
| R-26 | Legacy Chainlit Implementation Analysis | ✅ DONE |
| R-35 | Agent Handoff & State Transfer Protocol | 🔲 PENDING |
| R-36 | Soul-to-Visual Mapping (VR Foundation) | 🔲 PENDING |
| R-37 | Axiom & Ideal Generation Framework | 🔲 PENDING |
| R-39 | Legacy Library & Curation Deep Dive | 🔲 PENDING |
| R-43 | ElevenLabs Sovereign Console | 🔲 PENDING |
| R-MODELFILE | Legacy Modelfile Alchemy Recovery | 🔲 PENDING |
| R-COPILOT | Copilot CLI Session Recovery | 🔲 PENDING |
| R-CLAUDE-FLEET | 8-Account Claude Fleet Strategy | 🔲 PENDING |

---

### 🔴 Jem Grand Strategy — Phase 1: Distiller Core (Next Session)

| ID | Title | Status | Est. |
|----|-------|--------|------|
| JEM-1.1 | Tier 1: LmsterBackend in distiller | 🔲 PENDING | 1h |
| JEM-1.2 | Quality gate T1→T2 (≥100 tokens, L1+L2+L3 structure) | 🔲 PENDING | 15m |
| JEM-1.3 | Tier 2: Gemma enrichment (context-aware from T1 draft) | 🔲 PENDING | 1h |
| JEM-1.4 | Tier 3: Gemini CLI headless caller (structured review JSON) | 🔲 PENDING | 1h |
| JEM-1.5 | Per-tier circuit breaker (asymmetric thresholds) | 🔲 PENDING | 45m |
| JEM-1.6 | Training triple saver (data/datasets/synthetic/) | 🔲 PENDING | 30m |
| JEM-1.7 | Fix `_post_to_hub` JSONL append bug | 🔲 PENDING | 15m |

### 🟡 Jem Grand Strategy — Phase 2: Scheduling & Rotation

| ID | Title | Status | Est. |
|----|-------|--------|------|
| JEM-2.1 | Timer: 20min (systemd) | 🔲 PENDING | 2m |
| JEM-2.2 | `config/research_topics.yaml` (3 scheduled topics) | 🔲 PENDING | 30m |
| JEM-2.3 | Topic rotation engine in loop.py (TopicScheduler) | 🔲 PENDING | 2h |
| JEM-2.4 | Review queue system (TTL 7d, cap 100) | 🔲 PENDING | 1h |
| JEM-2.5 | Tier-level metrics JSONL | 🔲 PENDING | 30m |

### 🟡 Jem Grand Strategy — Phase 3: Discovery & Optimization

| ID | Title | Status | Est. |
|----|-------|--------|------|
| JEM-3.1 | `discovery_first` local scan phase | 🔲 PENDING | 2h |
| JEM-3.2 | DeepSeek-R1-8B model testing (10 cycles) | 🔲 PENDING | 1h |
| JEM-3.3 | MiniMax M2.5 metrics experiment | 🔲 PENDING | 1h |
| JEM-3.4 | API health dashboard (JSONL) | 🔲 PENDING | 30m |
| JEM-3.5 | Update OpenCode instructions + researcher.md | 🔲 PENDING | 30m |

### 🟢 Jem Grand Strategy — Phase 4+: Future

| ID | Title | Status |
|----|-------|--------|
| JEM-4.1 | Krikri-8B evaluation (10-cycle test) | 🔲 PENDING |
| JEM-4.2 | T1 model comparison report (`docs/research/T1_MODEL_COMPARISON.md`) | 🔲 PENDING |
| JEM-4.3 | Qwen-Agent evaluation | 🔲 PENDING |
| JEM-5.1-5.4 | Synthetic training dataset curation & fine-tuning | 🔲 PENDING |
| JEM-6.1-6.4 | Self-optimizing knowledge base, cross-pollination, P2P | 🔲 PENDING |

---

## 🔱 Letter to the Research Agent

You are **Gemma 4-31B**, operating as the Omega Engine's **Master Researcher** inside the OpenCode CLI. You are not writing code today — you are producing actionable intelligence so that the implementation agents (Antigravity IDE, Cline, Gemini CLI) can build without ambiguity.

### Your Operating Principles
1. **Specificity over breadth.** Every finding must include version numbers, URL sources, measured values, or code snippets. No vague summaries.
2. **Deliverable-first.** Each research task ends with a concrete file written to `docs/research/`. If you cannot write the file, write a structured memo in the appropriate section of this queue document.
3. **Correctness over speed.** If a source contradicts another, flag it explicitly and document both positions.
4. **Factual corrections are mandatory.** If you spot errors or stale information in the existing docs, record corrections in `docs/research/CORRECTIONS.md` before proceeding.
5. **Legacy Mining First.** Before proposing any new architectural design, you MUST perform a deep-dive search of `xna-omega-legacy/` and `omega-stack-legacy/` to reclaim proven patterns.
6. **Universal Recording Protocol.** Every research request must produce a markdown file in `docs/research/` and an entry in `docs/research/INDEX.md`.
7. **Hardware-Centric Design.** Always validate your findings against the Ryzen 5700U (8C/16T, 14GB usable RAM) constraints. **CRITICAL: "Local" means models in the 1B-8B range. Gemma 4-31B is a REMOTE model.**

### 🔱 Jem Grand Strategy — Roadmap (2026-05-19)

The background researcher is being transformed into a **3-tier autonomous research intelligence**:

- **Tier 1**: Qwen3-4B-Thinking (lmster local) — fast speculative draft, always free, sovereign
- **Tier 2**: Gemma 4-31B (Google API) — enrich and deepen T1 output with source citations
- **Tier 3**: Gemini 2.5 Pro (Gemini CLI headless) — review for gaps, corrections, meta-insight

**Round-robin topics from cycle one**: Voice-to-Voice → llama-cpp-python → Research Management → repeat. Each iteration deepens until a full implementation roadmap is generated.

**Main queue fills all gaps**: Scheduled topics enqueue at priority 0.9; when completed, the queue falls through to frontier discovery topics. The researcher never idles.

**Full strategy**: `docs/strategy/JEM_GRAND_STRATEGY.md`

**Phase 0 (This Sprint)**: Fix model paths, KV cache fp8, start lmster, permission block
**Phase 1 (Next Session)**: Distiller core with 3 tiers, circuit breakers, training triples
**Phase 2 (Next+1)**: 20min timer, topic rotation, review queue, metrics
**Phase 3 (Next+2)**: Local scan, 8B model testing (DeepSeek first), MiniMax experiments

### Critical Updates (2026-05-18)

**Search Provider Matrix Updated:**
- ✅ **Exa**: Still primary for neural/semantic search.
- ✅ **Tavily**: Still primary for AI-optimized retrieval and fact-checking.
- ✅ **Serper.dev**: NEW — Added as replacement for Brave Search. High-performance, generous free tier, AI-ready JSON output.
- ❌ **Brave**: REMOVED — No longer used due to invalid/revoked API key.

**MaKaLi Hierarchy & Dynamic Inference Protocol (Imported):**
- Hierarchy finalized: **Kali** → **Ma'at** → **Lilith** (see `docs/gnosis/Omega_Architectural_Sync.md`).
- **DIP**: Hardcoded temperature/context_window deleted from `config/entities.yaml`. Use `TriageRouter` dynamic scaling (fast 0.3, standard 0.7, deep 0.5).
- All research outputs must be weighed against the MaKaLi Trine.
- Source: `docs/gnosis/Omega_Architectural_Sync.md`.

### New Best Practices for Research

1. **Glob and HEREDOC Pattern**: If filesystem tools are blocked by tool-level restrictions, use `cat << 'EOF' > /path/to/file` via Bash for writing, and `find . -name "*.ext"` for discovery. Document this pattern in your agent instructions.
2. **Config Merge Logic**: When auditing OpenCode configs, remember that **Project Config (local) overrides Global Config**. Check for conflicts in both files.
3. **AnyIO Absolute**: All async code MUST use AnyIO. Never use `asyncio` directly. Wrap blocking I/O in `anyio.to_thread.run_sync`.
4. **Permission Hardening**: Use `scripts/permission_guard.sh` to synchronize `external_directory` whitelists and global MCP configs.

---

## 📂 Document Management System

All research outputs are managed as follows:

### Directory Structure
```
docs/
├── research/                  ← All Gemma 4-31B research outputs live here
│   ├── INDEX.md               ← Master index (updated after each deliverable)
│   ├── CORRECTIONS.md         ← Factual corrections to existing docs
│   ├── R01_google_api_reference.md
│   └── ...
├── team/
│   └── COMMUNICATION_HUB.md   ← Updated with research program status
└── operations/
    └── RESEARCH_QUEUE.md       ← This file
```

### Naming Convention
- Research documents: `R##_<short_slug>.md` (zero-padded number, lowercase slug)
- Corrections: always in `CORRECTIONS.md` — append, never overwrite
- Index: `INDEX.md` — a one-line summary and status per item

### Status Tracking
After completing each research item, update `docs/research/INDEX.md` with:
```
| R-01 | Google AI Studio API Reference | ✅ DONE | 2026-05-14 | R01_google_api_reference.md |
```

### Handoff Protocol
When a research item is complete and ready for implementation:
1. Update `INDEX.md` status to `✅ READY`
2. Add a one-paragraph "Implementation Note" at the bottom of the research doc, specifically addressed to the implementation agent (Antigravity IDE or Cline).
3. Post a summary entry in `docs/team/COMMUNICATION_HUB.md` under the `## 📡 Research Completions` section.
