# 🔱 Agent Fleet Architecture
**AP Token**: `AP-AGENT-FLEET-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06 · **Nomenclature refreshed 2026-09-20**
**Purpose**: Architecture of the 13-agent sovereign fleet and S1–S10 slot governance hierarchy.

---

# 🔱 Omega Engine — Agent Fleet Architecture
# AP: AP-AGENT-FLEET-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: FLEET | CONTEXT: AGENT-HIEARCHY]

This document defines the structure, roles, and delegation paths of the consolidated Omega Engine Agent Fleet.

> **Nomenclature (2026-09-20).** Engine language is **Slot / S1–S10** — never "Node N1–N10" and
> never the retired department labels (`SysAdmin`, `DataStore`, `BuildMaster`, `Bridge`,
> `Sentinel`, `ModelGate`, `Context`, `WatchTower`, `Link`, `Verifier`). Those ten labels were
> never entities; they were the old names for S1–S10 and were retired along with ten
> "slot-fill ghost" pseudo-entities. **"Node 0" / "Node 1" refer only to the two physical
> machines** (the HP dev laptop and the ASUS ExpertBook) — federation topology, not domains.

## 1. Fleet Philosophy: The Single Renderer Principle
Inspired by id Software's engine design, the Omega Engine uses a **parameterized agent architecture**. Instead of maintaining dozens of separate agent files with nearly identical logic, the engine utilizes a single, highly optimized **Slot Agent** that changes its behavior based on the `--slot` flag.

This ensures:
- **Consistency**: Logic updates apply to all slots simultaneously.
- **Efficiency**: Reduced configuration overhead and cognitive load.
- **Sovereignty**: Clear boundaries between core runtime and domain-specific roles.

## 2. The Fleet Hierarchy

```
                      [ plan ] (Grand Dispatcher)
                           |
                           v
                      [ kali ] (Grand Oversight)
                           |
             ┌─────────────┴─────────────┐
             v                           v
          [ maat ] (Build Oversoul)   [ lilith ] (Runtime Oversoul)
          (Governs S1-S5)             (Governs S6-S10)
             |                           |
             └─────────────┬─────────────┘
                           v
                [ slot --slot SX ]
                (Single slot-based agent)
                           |
              ┌─────────────┼──────────────┐
              v             v              v
           [ jem ]    [ scribe ]    [ researcher ]
        (Research)   (QA+Gnosis)    (Deep Dive)
              |            |
        ┌─────┴─────┐      v
        v     v     v   Mandate Audit
     [disc] [synth] [verif] ──→ soul.yaml
```

## 3. Agent Inventory

### 3.1 Primary Agents (Direct User/Plan Access)
| Agent | Mode | Purpose | Model Tier |
|-------|------|---------|------------|
| `makali` | Primary | MaKaLi Council — Parallel dispatch of Ma'at+Lilith | Heavy |
| `kali` | Primary | Grand Oversight — Unifier of Ma'at and Lilith | Heavy |
| `doom_guy` | Primary | Sovereign id Software Architect — WAD & Performance | Heavy |
| `roc_racoon` | Primary | Sovereign Miner — Legacy Archaeology | Lite |
| `researcher` | Primary | Sovereign Master Researcher — Lattice Reasoning | Heavy |
| `jem` | Primary | Research Orchestrator — 3-Tier Pipeline | Medium |

### 3.2 Subagents (Delegated Access)
| Agent | Mode | Purpose | Model Tier |
|-------|------|---------|------------|
| `maat` | Subagent | Build Oversoul — Build Side Governance (S1-S5) | Heavy |
| `lilith` | Subagent | Runtime Oversoul — Run Side Governance (S6-S10) | Heavy |
| `slot` | Subagent | Slot-based Domain Expert (S1-S10) | Lite |
| `scribe` | Subagent | Sovereign Guardian & Gnosis Keeper — Code Review, Mandate Enforcement, L1→L2→L3 Distillation | Medium |
| `slot` | Subagent | Slot-based Domain Expert (S1-S10) | Lite |

## 4. Delegation & Escalation Paths

### 4.1 The Standard Path
`User` $\rightarrow$ `plan` $\rightarrow$ `kali` $\rightarrow$ `maat/lilith` $\rightarrow$ `slot --slot SX`

### 4.2 Specialized Paths
- **Deep Research**: `kali` $\rightarrow$ `jem` $\rightarrow$ `[disc $\rightarrow$ synth $\rightarrow$ verif]` $\rightarrow$ `scribe` $\rightarrow$ `soul.yaml`
- **Quality Gate**: `slot/researcher` $\rightarrow$ `scribe` $\rightarrow$ `Sovereign Mandates Verification`
- **Lattice Deep Dive**: `researcher` $\rightarrow$ `lattice traversal` $\rightarrow$ `Reflective Verification`

## 5. Mandate Compliance
All agents must adhere to the **Sovereign Mandates**, specifically:
- **Mandate 10 (Fleet Integrity)**: No new agents without verified slot gap.
- **Mandate 11 (Soul Integrity)**: Mandatory L1→L2→L3 distillation before session close.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
