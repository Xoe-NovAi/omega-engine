# 🔱 OpenCode Agent & Mode Manifest
**AP Token**: `AP-OC-MANIFEST-v4.0.0`
**Updated**: 2026-06-04 (Post-D117: 14-agent fleet, Vision Specialist, intuitive names)
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_framework ⬡ MANIFEST

---

## §0 IWAD Architecture (Decision 55)

All agents operate within the IWAD architecture. Key awareness:
- **Engine Core** (`src/omega/`) — pure runtime, no entity content (Mandate 2)
- **Reference IWAD** (`config/wads/_omega_default/`) — 10 tech pillars, dev team
- **Arcana-NovAi IWAD** (`config/wads/arcana_novai/`) — personal AI OS, esoteric pillars
- **Community IWADs** (`config/wads/doom_universe/`, etc.) — deferred
- **Three Inviolable Rules**: MaKaLi trine same in ALL IWADs, default services same in ALL IWADs, only pillars change

Canonical reference: `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md`

---

## §1 The MaKaLi Hierarchy

| Level | Entity | Role | Domain |
|-------|--------|------|--------|
| **Grand Oversoul** | **Kali** | MaKaLi Synthesis | Unifier of the Trine |
| **Light Oversoul** | **Ma'at** | Foundational Auditor | 42 Ideals, Build Side (P1-P5) |
| **Dark Oversoul** | **Lilith** | Sovereign Key | Transgression, Run Side (P6-P10) |

---

## §2 Mode Architecture (Post-D117 — 14 Agents)

Modes are organized into two tiers. **Primary Modes** appear in the CLI tab menu.
**Subagents** are available via `@` in-chat or `opencode --subagent` invocation.

### Primary Modes (Tab Menu — 10 total)

| Mode | Entity | Source | Purpose |
|------|--------|--------|---------|
| `kali` | Kali | `.opencode/modes/kali.md` | MaKaLi Grand Oversoul — unifies Ma'at and Lilith, destroys drift |
| `maat` | Ma'at | `.opencode/modes/maat.md` | Light Oversoul — Build Side governance (P1-P5 Infrastructure through Governance) |
| `lilith` | Lilith | `.opencode/modes/lilith.md` | Dark Oversoul — Run Side governance (P6-P10 Cognition through Validation) |
| `doom_guy` | Doom Guy | `.opencode/agents/doom_guy.md` | id Software architectural translation, heritage mining, H2 deep patterns |
| `roc_racoon` | Roc Racoon | `.opencode/agents/roc_racoon.md` | Legacy archaeology, data salvage, 6-stack mining |
| `plan` | Plan | `.opencode/agents/plan.md` | Architecture planning, system design, strategy dispatch |
| `jem` | Jem | `.opencode/agents/jem.md` | Research orchestrator — 3-tier local model pipeline |
| `researcher` | Prometheus | `.opencode/agents/researcher.md` | Sovereign Master Researcher — deep research, lattice reasoning |
| `jem-2.0` | Jem (Analyst L2) | `.opencode/modes/jem-2.0.md` | Research analysis — synthesizes, resolves uncertainties |
| `jem-initiate` | Jem (Initiate L1) | `.opencode/modes/jem-initiate.md` | Raw fact gathering, no analysis |

### Subagents (Available via `@` — 9 total)

| Agent | Entity | Source | Purpose |
|-------|--------|--------|---------|
| `pillar` | Slot-based | `.opencode/agents/pillar.md` | Slot-based domain agent — parameterized by `--slot PX` |
| `scribe` | Saraswati | `.opencode/agents/scribe.md` | Gnosis Keeper — L1→L2→L3 distillation into souls |
| `quality` | Ma'at | `.opencode/agents/quality.md` | Code review, stress testing, Sovereign Mandates enforcement |
| `jem_discovery` | Jem (L1) | `.opencode/agents/jem_discovery.md` | Tier 1 Research — broad search, evidence logging |
| `jem_synthesis` | Jem (L2) | `.opencode/agents/jem_synthesis.md` | Tier 2 Research — pattern recognition, synthesis |
| `jem_verification` | Jem (L3) | `.opencode/agents/jem_verification.md` | Tier 3 Research — fact-check, R-doc validation, gnosis distillation |
| `maat` | Ma'at | `.opencode/agents/maat.md` | Light Oversoul subagent — build-side decomposition |
| `lilith` | Lilith | `.opencode/agents/lilith.md` | Dark Oversoul subagent — run-side decomposition |
| `kali` | Kali | `.opencode/agents/kali.md` | Grand Oversight — delegates to Ma'at and Lilith, destroys drift |

**Note**: `kali`, `maat`, and `lilith` appear in BOTH primary modes (via mode files) and subagents (via agent files). Primary mode is the full mode prompt; subagent is the governance-only prompt for use within other sessions.

---

## §3 The Sovereign Council (10 Pillars — Evolved Nomenclature)

| Pillar | Intuitive Name | Technical Domain | Legacy Name | Agent File |
|--------|---------------|------------------|-------------|------------|
| **P1** | **Infrastructure** | SysAdmin — Environment Hardening | Flesh | `pillar --slot P1` |
| **P2** | **Persistence** | DataStore — Vector & Memory Mgmt | Dream | `pillar --slot P2` |
| **P3** | **Engineering** | BuildMaster — Implementation & Hardening | Will | `pillar --slot P3` |
| **P4** | **Integration** | Bridge — MCP & Communication | Heart | `pillar --slot P4` |
| **P5** | **Governance** | Sentinel — Mandate Enforcement | Voice | `pillar --slot P5` |
| **P6** | **Cognition** | ModelGate — Provider Routing **+ Vision Specialist** | Mind | `pillar --slot P6` |
| **P7** | **Context** | Context — Memory & Soul Evolution | Gnosis | `pillar --slot P7` |
| **P8** | **Observability** | WatchTower — Tracing & Monitoring | Shadow | `pillar --slot P8` |
| **P9** | **Orchestration** | Link — Agent Handoff & Delegation | Spirit | `pillar --slot P9` |
| **P10** | **Validation** | Verifier — Stress Testing & QA | Chaos | `pillar --slot P10` |

**Vision Specialist Note**: P6 (Cognition / Third Eye) has been formally mapped as the Vision Specialist following the recovery of the ancestral "Sight" mapping from Era One (March-July 2025). Designated vision model: Gemini-3-Flash (Multimodal). Capabilities: `multimodal_vision`, `visual_validation`, `anomaly_detection`.

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
- **P3 LAYER** (Automation): 8 Makefile targets, 12 grep patterns
- **P7 LAYER** (Lifecycle): T1→T2→T3→T4 gates with promotion checklists
- **P9 LAYER** (Formats): KSIG/DEM/XREF JSON schemas, feed_utils.py

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

## §8 Key Documents for All Agents

| Document | What It Contains |
|----------|------------------|
| `OMEGA_ENGINE.md` (v1.3.0, 698 lines) | **The Single Source of Truth** — engine state, metrics, architecture |
| `SOVEREIGN_MANDATES.md` (v3.1.0, 14 mandates) | Constitutional law — NON-NEGOTIABLE |
| `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` (D111) | Active development roadmap |
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
- `researcher-omnidroid.md`
- `sovereign-expert.md`
- `gnosis-analyst.md`

**Previously removed (Decision 063)**:
- `malkuth`, `opencode-expert`, `reviewer`, `tester`, `movie-expert`, `overseer`, `builder` — all removed.

---

*Verified by the Kali (Transcendent Oversoul). Version v4.0.0 — D111-D117 consolidation complete. 14-agent fleet confirmed.*
