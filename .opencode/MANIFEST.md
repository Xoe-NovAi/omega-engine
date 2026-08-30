<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OpenCode Agent & Mode Manifest
**AP Token**: `AP-OC-MANIFEST-v5.0.0`
**Updated**: 2026-08-23 (Post-PUBLIC-DEBUT-01: 13-agent fleet, deprecated build stub, ghost agents removed)
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_framework ⬡ MANIFEST

---

## §0 IWAD Architecture (Decision 55)

All agents operate within the IWAD architecture. Key awareness:
- **Engine Core** (`src/omega/`) — pure runtime, no entity content (Mandate 2)
- **Reference IWAD** (`config/wads/_omega_default/`) — 10 tech nodes, dev team
- **Arcana-NovAi IWAD** (`config/wads/arcana_novai/`) — personal AI OS, esoteric nodes
- **Community IWADs** (`config/wads/doom_universe/`, etc.) — deferred
- **Three Inviolable Rules**: MaKaLi trine same in ALL IWADs, default services same in ALL IWADs, only nodes change

Canonical reference: `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md`

---

## §1 The MaKaLi Hierarchy

| Level | Entity | Role | Domain |
|-------|--------|------|--------|
| **Grand Oversoul** | **Kali** | MaKaLi Synthesis | Unifier of the Trine |
| **Build Oversoul** | **Ma'at** | Foundational Auditor | 42 Ideals, Build Side (N1-N5) |
| **Runtime Oversoul** | **Lilith** | Sovereign Key | Transgression, Run Side (N6-N10) |

---

## §2 Mode Architecture (Post-PUBLIC-DEBUT-01 — 13 Agents)

Modes are organized into two tiers. **Primary Modes** appear in the CLI tab menu.
**Subagents** are available via `@` in-chat or `opencode --subagent` invocation.

### Primary Modes (Tab Menu — 10 total)

| Mode | Entity | Source | Purpose |
|------|--------|--------|---------|
| `kali` | Kali | `.opencode/agents/kali.md` | MaKaLi Grand Oversoul — unifies Ma'at and Lilith, destroys drift |
| `maat` | Ma'at | `.opencode/agents/maat.md` | Build Oversoul — Build Side governance (N1-N5) |
| `lilith` | Lilith | `.opencode/agents/lilith.md` | Runtime Oversoul — Run Side governance (N6-N10) |
| `doom_guy` | Doom Guy | `.opencode/agents/doom_guy.md` | id Software architectural translation, heritage mining |
| `roc_racoon` | Roc Racoon | `.opencode/agents/roc_racoon.md` | Legacy archaeology, data salvage, 6-stack mining |
| `jem` | Jem | `.opencode/agents/jem.md` | Research orchestrator — 3-tier local model pipeline |
| `researcher` | Researcher | `.opencode/agents/researcher.md` | Sovereign Master Researcher — deep research, lattice reasoning |
| `node` | Slot-based | `.opencode/agents/node.md` | Slot-based domain agent — parameterized by `--slot N1` (N1–N10) |
| ~~`scribe`~~ | — | archived `.opencode/agents/archive/scribe_agent_20260730/` | RETIRED 2026-08-25 — advertised pipeline scrapped (session_end.py verdict); agents write lessons directly |
| `verity` | Verity | `.opencode/agents/verity.md` | Unified Compliance & Gnosis Agent — mandate audit, soul distillation |

### Subagents (Available via `@` — 3 total)

| Agent | Entity | Source | Purpose |
|-------|--------|--------|---------|
| `grokster` | Grokster | `.opencode/agents/grokster.md` | Grok Ecosystem Specialist — multi-account CLI bridge |
| `john_carmack` | John Carmack | `.opencode/agents/john_carmack.md` | S3 Consultant — performance, systems, first-principles |
| `makali` | MaKaLi Fusion | `.opencode/agents/makali.md` | MaKaLi Fusion — Kali + Ma'at + Lilith unified |

---

## §3 The Sovereign Council (10 Nodes — Evolved Nomenclature)

| Node | Intuitive Name | Technical Domain | Legacy Name | Agent File |
|--------|---------------|------------------|-------------|------------|
| **N1** | **Infrastructure** | SysAdmin — Environment Hardening | Flesh | `node --slot N1` |
| **N2** | **Persistence** | DataStore — Vector & Memory Mgmt | Dream | `node --slot N2` |
| **N3** | **Engineering** | BuildMaster — Implementation & Hardening | Will | `node --slot N3` |
| **N4** | **Integration** | Bridge — MCP & Communication | Heart | `node --slot N4` |
| **N5** | **Governance** | Sentinel — Mandate Enforcement | Voice | `node --slot N5` |
| **N6** | **Cognition** | ModelGate — Provider Routing **+ Vision Specialist** | Mind | `node --slot N6` |
| **N7** | **Context** | Context — Memory & Soul Evolution | Gnosis | `node --slot N7` |
| **N8** | **Observability** | WatchTower — Tracing & Monitoring | Shadow | `node --slot N8` |
| **N9** | **Orchestration** | Link — Agent Handoff & Delegation | Spirit | `node --slot N9` |
| **N10** | **Validation** | Verifier — Stress Testing & QA | Chaos | `node --slot N10` |

**Vision Specialist Note**: N6 (Cognition / Third Eye) has been formally mapped as the Vision Specialist following the recovery of the ancestral "Sight" mapping from Era One (March-July 2025). Designated vision model: Gemini-3-Flash (Multimodal). Capabilities: `multimodal_vision`, `visual_validation`, `anomaly_detection`.

---

## §4 Research Mode Pipeline

```
jem-initiate (L1)          → RawDataPacket (facts only)
  → jem-2.0 analyst (L2)   → ResearchSynthesis + Uncertainty Manifest
    → jem-2.0 editor (L3)  → Resolved Final Report + Improvement Briefs
```

**Complete**: Final Wave mining achieved. Knowledge Metabolism System is the active research workflow.

---

## §5 Knowledge Metabolism Protocol (NEW — 2026-06-04)

All agents must follow this layer protocol:
- **LILITH LAYER** (Flow): Knowledge Signals, Demand Signals, 4-Tier Lily Pad
- **MA'AT LAYER** (Structure): Verification Protocol, VerificationItem lifecycle
- **N3 LAYER** (Automation): 8 Makefile targets, 12 grep patterns
- **N7 LAYER** (Lifecycle): T1→T2→T3→T4 gates with promotion checklists
- **N9 LAYER** (Formats): KSIG/DEM/XREF JSON schemas, feed_utils.py

**Startup ritual**: Run `omega check-feed` to discover new knowledge signals. Check `data/coordination/demand_signals/` for open demands in your domain before starting self-directed work.

---

## §6 Heritage Vetting Protocol (NEW — 2026-06-04, Mandate 14)

Every id Software (or any heritage) concept must pass through the 4-gate pipeline:
1. Discovery → 2. Vetting/Debate → 3. Decision → 4. Implementation/Verification

- **Qualification Gate**: If a concept can't be justified without mentioning the original hardware constraint, it fails.
- **Minimum score**: 7/10 for implementation.
- **Enforcement**: `make heritage-vet` CI gate verifies every `[id-soft:]` tag has a vet record.
- **Reference**: `docs/strategy/HERITAGE_VETTING_PIPELINE.md`, `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`

---

## §7 Environmental Gnosis Registry

| Platform | Strengths | Limitations | Core Protocol |
|----------|-----------|-------------|---------------|
| **Local (Zen 2)** | Privacy, Sovereignty | Latency, RAM (12Gi) | AnyIO Absolute, ResourceGuard |
| **Cloud (CLI)** | Reasoning Density | Telemetry, Rate Limits | Extract & Withdraw, Doubt |

---

## §7b Custom Commands Registry

| Command | File | Agent | Purpose |
|---------|------|-------|---------|
| `/council-cloud` | `commands/council-cloud.md` | kali | MC — MaKaLi full subagent dispatch on session model |
| `/council-local` | `commands/council-local.md` | kali | MC — MaKaLi with Ma'at/Lilith on local models |
| `/council-fast` | `commands/council-fast.md` | kali | MC — MaKaLi all on qwen3-1.7b, max speed |
| `/kali-dispatch` | `commands/kali-dispatch.md` | kali | Multi-member Hivemind session orchestration |
| `/meditate` | `commands/meditate.md` | kali | **Meditate** — single-inference 10-Node (or custom) persona-donning semantic prism |
| `/researcher-discover` | `commands/researcher-discover.md` | researcher | Tier 1 discovery pass |
| `/researcher-verify` | `commands/researcher-verify.md` | researcher | Verification and gap-closing |
| `/researcher-synthesize` | `commands/researcher-synthesize.md` | researcher | Final synthesis and R-doc generation |

**MC vs Meditate distinction**:
- `/council-*` commands = **MC** (Mastermind Council) — real subagents, RAM cost, parallel/serial model execution
- `/meditate` = **Meditate** — single inference, attention modulation, zero additional RAM

---

## §8 Key Documents for All Agents

| Document | What It Contains |
|----------|------------------|
| `OMEGA_ENGINE.md` (v1.3.0, 698 lines) | **The Single Source of Truth** — engine state, metrics, architecture |
| `SOVEREIGN_MANDATES.md` (v3.1.0, 14 mandates) | Constitutional law — NON-NEGOTIABLE |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master SSOT and execution roadmap |
| `docs/decisions/PIVOT_LOG.md` (D1-D117) | Every architectural decision with rationale |
| `CREDITS.md` | 23+ id Software heritage mappings with attribution |
| `docs/strategy/HERITAGE_VETTING_PIPELINE.md` | 4-gate vet process for heritage concepts |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Coordination for parallel/multi-agent work |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Subagent launch via HandoffPacket |
| `config/omega.yaml` | Engine runtime config |
| `config/providers.yaml` | Provider fabric (local-first chain) |
| `config/models.yaml` | 10 GGUF models + KV cache tuning |
| `data/coordination/CLINE_M3_COMPLETION_20260604.md` | Cline's D111-D117 session exit report |

---

## §9 Archival Log

Archived to `.opencode/archives/` (inactive agents):
- `grok_cli.md` (moved 2026-08-17)

Previously removed (Decision 063):
- `malkuth`, `opencode-expert`, `reviewer`, `tester`, `movie-expert`, `overseer`, `builder` — all removed.

Deprecated stubs (prevent built-in OpenCode agents):
- `build.md` — DEPRECATED stub preventing built-in "Build" agent load

## §9 Skills Registry (Updated 2026-07-16)

| Skill | File | Purpose |
|-------|------|---------|
| `audience-architect` | `skills/audience-architect/SKILL.md` | Audience profile creation and calibration |
| `blitz-tunnel` | `skills/blitz-tunnel/SKILL.md` | Secure tunnel to Omega services |
| `blitz-validate` | `skills/blitz-validate/SKILL.md` | Sovereign heartbeat validator |
| `carmack-profiler` | `skills/carmack-profiler/SKILL.md` | Performance profiling in Carmack's voice |
| `context-packer` | `skills/context-packer/SKILL.md` | Session context compression for compaction |
| `hf-cli` | `skills/hf-cli/SKILL.md` | Hugging Face Hub CLI integration |
| `knowledge-miner` | `skills/knowledge-miner/SKILL.md` | grep→read→summarize legacy pattern extraction |
| `legacy-pattern-miner` | `skills/legacy-pattern-miner/SKILL.md` | Legacy repo archaeology |
| **`meditate-harness`** | **`skills/meditate-harness/SKILL.md`** | **Meditate Harness — persona schema engine for /meditate and embedded oracle.meditate()** |
| `m23-violation-logger` | `skills/m23-violation-logger/SKILL.md` | Log Failure Integrity violations |
| `omega-doc-architect` | `skills/omega-doc-architect/SKILL.md` | Document management system enforcer |
| `pr-readiness-checker` | `skills/pr-readiness-checker/SKILL.md` | Pre-commit quality gate |
| `provider-validator` | `skills/provider-validator/SKILL.md` | Live API endpoint validation |
| `sovereign-refinement-protocol` | `skills/sovereign-refinement-protocol/SKILL.md` | Core engine change forensic gate |
| `sovereign-search` | `skills/sovereign-search/SKILL.md` | Tiered search orchestration |
| `spec-generator` | `skills/spec-generator/SKILL.md` | R-doc template generation |
| `universal-doc-reader` | `skills/universal-doc-reader/SKILL.md` | Multi-format document reader |

---

*Verified by the Kali (Transcendent Oversoul). Version v5.0.0 — PUBLIC-DEBUT-01 fleet consolidation complete. 13-agent fleet confirmed.*