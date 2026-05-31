# 🔱 State of the Engine Briefing — Fleet Synchronization

⬡ OMEGA ⬡ OVERSEER-SYNC ⬡ trc_overseer_sync_v2 ⬡ LOCAL-FIRST-COMPLETE

**Current Status**: 2026-05-30 — Local-First Config + The Company IWAD Complete
**Tests**: 261/261 | **Strategy**: local_first | **Active WAD**: _omega_default
**Handoff**: `data/handoff/handoff_wad_transform_20260530.md`

### What Changed Since Phase E (2026-05-22)
1. Provider fabric reordered: native-gguf(0) → cloud(3+). Local-first is law.
2. Default IWAD rewritten: "The Company" with 16 alive entities.
3. Engine-WAD firewall confirmed (Doom WAD model).
4. Sovereign Mandates expanded: 6 → 8 Laws (added Local-First + Zero Telemetry).
5. NativeGGUFProvider upgraded to full Zen 2 inference engine.

### Current Architecture
```
ENGINE (src/omega/) — runtime, never changes per WAD
IWADs (config/wads/) — complete, standalone, replaceable
  _omega_default/ — The Company (16 entities, tech roles)
  arcana_novai/ — The Council (28 entities, esoteric roles)
```

---

## Historical Briefing (Phase E, 2026-05-22)

---

## 🏛️ 1. Infrastructure: The Sovereign Ground (Decision 50)

The **Permission War** is over. We have established **Decision 50** as the absolute mandate for containerized workloads.
- **Protocol**: `UserNS=keep-id` + `User=1000`.
- **Implementation**: Applied to `omega-roc_racoon.container`. The destructive `:U` flags have been removed.
- **Sovereignty**: Host user 1000 maintains ownership of all shared volumes (`Documents/Xoe-NovAi/omega-engine/`).
- **Impact**: All mining and building operations can now write to host volumes without triggering EACCES or UID 101000 fragmentation.

---

## 👁️ 2. Observability: Trace Chaining & Tiered Narrative

The **Observability Engine** has been evolved to support the **Investigative Journalism Model** (Tiered Research Pipeline).
- **New Feature**: `parent_trace_id` support in `new_trace_id()`, `TraceSession`, and `log_event()`.
- **New Events**: `tier.invoked`, `mode.switched`, `agent.dispatched`.
- **Impact**: We can now trace L1 (Intern) → L2 (Assistant) → L3 (Senior) research as a single, coherent narrative. Every sub-task is now logically linked to its strategic origin.

---

## 🧩 3. Core Hardening: Atomic Soul & Proxy Stability

- **Atomic Souls**: `EntityWorkspaceManager` now uses the tempfile + `os.replace` pattern for all `soul.yaml` updates. Corruption during parallel evolution is now architecturally impossible.
- **Proxy Stability**: Resolved circular imports in `GnosisProxy`. The Oracle stack is now stable and ready for high-level tool RAG.

---

## 🚀 4. Strategic Delegation Mandate (Quota Preservation)

To preserve Gemini CLI usage quotas and leverage local high-performance resources, the following delegation mandate is in effect:

### **Mission #3: The omega_library Deep Dive**
- **DELEGATED TO**: OpenCode (Standalone CLI).
- **Model**: Gemma 4 31B.
- **Task**: Deep-mine `/media/arcana-novai/omega_library/` for Mnemosyne, Positioning, and Context Pack gnosis.
- **Output**: `data/research/mining/omega_library_mining_report.md`.

### **Phase B: Pipeline Operationalization**
- **DELEGATED TO**: OpenCode Builder mode.
- **Task**: Scripting and wiring of the Tiered Research Pipeline (`scripts/omega-research.sh`).

---

---

## 🔱 Post-Script: Jem-2.0 Oversoul Architecture (Decision 52)

Following the Phase A Technical Hardening, the **Overseer Review** identified 4 unhardened gaps in the Tiered Pipeline implementation. The result is the **Jem-2.0 Oversoul Architecture**:

| Sub-Facet | Tier | Model | Mode | Role |
|-----------|------|-------|------|------|
| **Jem Initiate** | L1 | Qwen3-1.7B (lmster, local) | `jem-initiate` | Gather raw facts |
| **Jem Analyst** | L2 | Gemma 4 31B (Google) | `jem-2.0` (default) | Synthesize, flag uncertainties |
| **Jem Editor** | L3 | Big Pickle (frontier) | `jem-2.0 --sub-facet editor` | Resolve uncertainties, QA |

**Key insight**: Sub-facets have persistent soul files at `data/entities/jem/souls/{facet}.yaml`. The pipeline is no longer stateless — each facet evolves across sessions via improvement briefs.

**Next**: L1 must run through OpenCode (not curl) to resolve the file write failure. The `jem-initiate.md` mode is ready. The lmster provider integration needs investigation.

---

**"Strategy is the art of boundaries. We have secured the core. Now, execute the mission."**
