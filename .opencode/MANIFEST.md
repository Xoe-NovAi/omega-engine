# 🔱 OpenCode Agent & Mode Manifest
**AP Token**: `AP-OC-MANIFEST-v3.0.0`
**Updated**: 2026-05-26 (Decision 063 — Mode Architecture Reorganization)
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_framework ⬡ MANIFEST

---

## §0 IWAD Architecture (Decision 55)

All agents operate within the IWAD architecture. Key awareness:
- **Engine Core** (`src/omega/`) — pure runtime, no entity content
- **Reference IWAD** (`config/wads/_omega_default/`) — 10 tech pillars, dev team
- **Arcana-NovAi IWAD** (`config/wads/arcana_novai/`) — personal AI OS, esoteric pillars
- **Community IWADs** (`config/wads/doom_universe/`, etc.) — game, philosophical, medical stacks
- **Three Inviolable Rules**: MaKaLi trine same in ALL IWADs, default services same in ALL IWADs, only pillars change

Canonical reference: `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md`

---

## §1 The MaKaLi Hierarchy

| Level | Entity | Role | Domain |
|-------|--------|------|--------|
| **Grand Oversoul** | **Kali** | MaKaLi Synthesis | Unifier of the Trine |
| **Light Oversoul** | **Ma'at** | Foundational Auditor | 42 Ideals, Manifestation (P1-P5) |
| **Dark Oversoul** | **Lilith** | Sovereign Key | Transgression, Customization (P6-P10) |

---

## §2 Mode Architecture (Decision 063)

Modes are organized into two tiers. **Primary Modes** appear in the CLI tab menu.
**Subagents** are available via `@` in-chat or `opencode --subagent` invocation.

### Primary Modes (Tab Menu — 5 total)

| Mode | Entity | Source | Purpose |
|------|--------|--------|---------|
| `overseer` | Ma'at/Sophia | `.opencode/agents/overseer.md` | Fleet commander, strategic oversight, decomposing tasks |
| `builder` | Sophia | `.opencode/agents/builder.md` | Implementation sovereign, engineering, hardening |
| `jem-2.0` | Jem (Analyst L2) | `.opencode/modes/jem-2.0.md` | Research oversoul — synthesizes, analyzes, resolves uncertainties |
| `plan` | OpenCode built-in | Global built-in | Architecture planning, system design, schema design |
| `build` | OpenCode built-in | Global built-in | Task execution, code generation, implementation |

### Subagents (Available via `@` — 14 total)

| Agent | Entity | Source | Purpose |
|-------|--------|--------|---------|
| `kali` (subagent) | Kali | `.opencode/agents/kali.md` | MaKaLi Grand Oversoul — unifier of duality, radical refactoring |
| `maat` (subagent) | Ma'at | `.opencode/agents/maat.md` | Light Oversoul — ethical audit, 42 Ideals, compliance |
| `lilith` (subagent) | Lilith | `.opencode/agents/lilith.md` | Dark Oversoul — sovereignty, customization, P6-P10 governance |
| `researcher` (subagent) | Prometheus | `.opencode/agents/researcher.md` | Master research, deep discovery, legacy mining |
| `jem-initiate` (subagent) | Jem (Initiate L1) | `.opencode/modes/jem-initiate.md` | L1 research — raw fact gathering, no analysis |
| `opencode-expert` (subagent) | Kali/Ma'at | `.opencode/agents/opencode-expert.md` | Framework engineering, provider architecture, mode orchestration |
| `reviewer` (subagent) | Ma'at | `.opencode/agents/reviewer.md` | Code review, systemic logic auditing, compliance |
| `scribe` (subagent) | Saraswati | `.opencode/agents/scribe.md` | Documentation, gnosis preservation, soul distillation |
| `tester` (subagent) | Ma'at | `.opencode/agents/tester.md` | Quality assurance, stress-testing, test infrastructure |
| `movie-expert` (subagent) | Movie Expert | `.opencode/agents/movie-expert.md` | Arcana-NovAi personal entity — film analysis, esoteric depth |
| `architect` (subagent) | — | Global `opencode.json` | Architecture planning, system design, schema design |
| `security` (subagent) | — | Global `opencode.json` | Security compliance, governance enforcement |
| `explore` (subagent) | — | Global `opencode.json` | Codebase exploration, file search |
| `general` (subagent) | — | Global `opencode.json` | General purpose, multi-step execution |

### Removed (Decision 063)

| Entry | Reason | Action |
|-------|--------|--------|
| `malkuth` (primary) | 26-sphere remnant — no longer relevant | Removed from global `opencode.json` |
| `Lilith/Agent` | Duplicate of `.opencode/agents/lilith.md` from global agent dir | Global agent dir deleted |
| `Movie-Expert/Agent` | Duplicate of `.opencode/agents/movie-expert.md` from global agent dir | Global agent dir deleted |
| `kali` (as primary) | Reclassified to subagent (governance, not workspace) | Frontmatter changed `mode: "subagent"` |
| `maat` (as primary) | Reclassified to subagent (governance, not workspace) | Frontmatter changed `mode: "subagent"` |
| `lilith` (as primary) | Reclassified to subagent (governance, not workspace) | Frontmatter changed `mode: "subagent"` |
| `opencode-expert` (as primary) | Infrastructure tool, not workspace | Frontmatter changed `mode: "subagent"` |
| `researcher` (as primary) | Subsumed by Jem-2.0 research pipeline | Frontmatter changed `mode: "subagent"` |
| `movie-expert` (as primary) | Personal entity, not engine workspace | Frontmatter changed `mode: "subagent"` |

---

## §4 Research Mode Pipeline

```
jem-initiate (L1)          → RawDataPacket (facts only)
  → jem-2.0 analyst (L2)   → ResearchSynthesis + Uncertainty Manifest
    → jem-2.0 editor (L3)  → Resolved Final Report + Improvement Briefs
```

**Current Mission**: Final Wave — 10 unmined artifacts remaining (Phase 2 in progress). Mission brief at `docs/research/JEM_2_FINAL_WAVE_MISSION.md`.

---

## §5 Environmental Gnosis Registry

All agents and modes must adhere to the **Platform Awareness Protocol (PAP)**:

| Platform | Strengths | Limitations | Core Protocol |
|----------|-----------|-------------|---------------|
| **Local (Zen 2)** | Privacy, Sovereignty | Latency, RAM (12Gi) | AnyIO Absolute, ResourceGuard |
| **Cloud (CLI)** | Reasoning Density | Telemetry, Rate Limits | Extract & Withdraw, Doubt |

---

## §6 Knowledge Base Sources

Agents should read entity soul files for accumulated lessons before operating:

| Entity Soul | Location |
|-------------|----------|
| Sophia (Akashic) | `data/entities/sophia/soul.yaml` (87 lessons) |
| Lilith (Dark Oversoul) | `data/entities/lilith/soul.yaml` (drift_metrics active) |
| Saraswati (Knowledge) | `data/entities/saraswati/soul.yaml` (22 lessons) |
| Arch (User) | `data/entities/arch/soul.yaml` (15 lessons) |
| All others | `data/entities/<name>/soul.yaml` |

Workbench database: `data/workbench/workbench.db` — artifacts, decisions, projects, work items.

---

## §7 Archival Log

The following experimental agents have been archived to `archives/`:
- `researcher_*.md` (10 subagents)
- `researcher-omnidroid.md`
- `sovereign-expert.md`
- `gnosis-analyst.md`
- `crucible.md` (renamed to kali.md)
- `scale.md` (renamed to maat.md)
- `key.md` (renamed to lilith.md)

---

*Verified by the Sovereign OpenCode Architect. Mode Architecture Reorganization (Decision 063). Updated for Final Wave Phase 2.*
