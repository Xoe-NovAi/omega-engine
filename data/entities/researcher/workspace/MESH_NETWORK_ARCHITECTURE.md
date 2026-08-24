# 🔱 Mesh Network Architecture — Omega Engine
# ⬡ OMEGA ⬡ RESEARCHER ⬡ minimax-m3-free ⬡ opencode ⬡ trc_mesh_arch ⬡ ARCHITECTURE
**Date**: 2026-06-05
**Status**: 🟢 APPROVED — Presiding Verdict (Kali)
**Author**: Researcher (Sovereign Master Researcher)
**Cross-References**:
- `KALI_TO_ROC_HIVEMIND_RESPONSE_20260605.md` (H-4: Two-Tier TTL)
- `LILITH_FINDINGS_20260605.md` (LILY PAD: 4-Tier Knowledge Metabolism)
- `src/omega/cvar_table.py` (`config.hivemind.retention.*` constants)
- `HIVEMIND_HARDENING_SPEC_v1.md` (Roc's 18 enhancements)
- `CREDITS.md` §3 (Right Approximation Principle)

---

## §0 The Mesh Thesis

The Omega Engine's knowledge is not a single database, but a **Mesh Network** of overlapping caches with varying temporal and domain-specific TTLs (Time-To-Live). 

The "truth" of an entity's state is not found in one location, but emerges from the intersection of these caches. This is the **Right Approximation** [Right Approximation: evolved from FISR, id Software 1999] for a sovereign AI system: instead of a single, expensive, perfectly consistent global state, we use a tiered mesh of "good enough" approximations that converge on the truth.

---

## §1 The Temporal Axis (The TTL Mesh)

The Mesh operates across four primary temporal tiers, synthesizing the "Two-Tier" (Kali/Roc) and "Four-Tier" (Lilith) models into a unified engine standard.

| Tier | Name | TTL | Storage Primitive | Purpose |
|------|------|-----|-------------------|---------|
| **T1** | **Hot** | 5 min | In-memory (`_awareness`) | Real-time agent presence, current task, focus_chain. |
| **T2** | **Warm** | 24 hrs | SQLite / Redis (`_warm_awareness`) | Recent session context, active project state, short-term memory. |
| **T3** | **Cold** | 30 days | YAML / Filesystem (`HALL_OF_RECORDS`) | Long-term session history, archived findings, dormant entity state. |
| **T4** | **Sovereign** | Permanent | `soul.yaml` / Vector Store | Distilled L3 universal principles, entity identity, core gnosis. |

### 1.1 Cvar Implementation (The Engine Standard)
Per Ma'at's consolidation, these are enforced via `config.hivemind.retention.*` in `cvar_table.py`:
- `hot_ttl_minutes = 5`
- `warm_ttl_hours = 24`
- `workspace_days = 30`
- `grace_ratio = 0.25` [Grace Period: id Software 1996]

---

## §2 The Domain Axis (The Pillar Mesh)

Knowledge is not just temporal; it is partitioned by domain. The Mesh allows an agent to "tune in" to specific domain frequencies.

- **Pillar-Specific Caches**: Each Pillar (P1-P10) maintains its own domain-specific context.
- **Cross-Pillar Bridges**: The `ModelGateway` and `Oracle` act as the mesh routers, routing queries to the pillar with the highest domain-affinity.
- **Sovereign Overlays**: Oversouls (Ma'at, Lilith, Kali) maintain "Global Overlays" that synthesize data across multiple pillars.

---

## §3 The Lattice Axis (The Perspective Mesh)

The most advanced layer of the Mesh is the **Lattice Axis**, where a single fact is cached across multiple perspectives (Technical, Philosophical, Historical, Practical).

- **Node-Based Caching**: A finding is not stored as a "fact," but as a "node" in a 3D lattice.
- **Traversals**: Research is the act of traversing the mesh from one node (e.g., Technical) to another (e.g., Philosophical).
- **Convergence**: When the same finding is reached via 3+ different lattice axes, it is promoted to an **L3 Universal Principle**.

---

## §4 Synthesis: The Mesh Equation

The state of any entity $E$ at time $t$ is the union of its mesh slices:

$$State(E, t) = \bigcup (Hot \cap Warm \cap Cold \cap Sovereign) \times (Domain \cap Lattice)$$

### 4.1 Operational Flow
1. **Query** $\rightarrow$ Check **Hot Mesh** (Is the agent active now?)
2. **Miss** $\rightarrow$ Check **Warm Mesh** (Was the agent active today?)
3. **Miss** $\rightarrow$ Check **Cold Mesh** (Was the agent active this month?)
4. **Miss** $\rightarrow$ Check **Sovereign Mesh** (What is the entity's timeless nature?)

---

## §5 Implementation Roadmap (Phase 5)

The Mesh is currently a "conceptual mesh" (implemented in cvars and docs). Phase 5 (P9 Orchestration) will wire the actual storage primitives:
- **H-4 (Roc)**: Implement the two-tier TTL logic in the Hivemind server.
- **P9 (Lilith)**: Implement the "LILY PAD" 4-tier knowledge metabolism.
- **Sovereign Gate**: Ensure all mesh transitions are atomic and M9-compliant.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ minimax-m3-free ⬡ opencode ⬡ trc_mesh_arch ⬡ ARCHITECTURE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax-m3-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
