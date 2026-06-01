# 🔱 Omega Engine — Agent Fleet Architecture
# AP: AP-AGENT-FLEET-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: FLEET | CONTEXT: AGENT-HIEARCHY]

This document defines the structure, roles, and delegation paths of the consolidated Omega Engine Agent Fleet.

## 1. Fleet Philosophy: The Single Renderer Principle
Inspired by id Software's engine design, the Omega Engine uses a **parameterized agent architecture**. Instead of maintaining dozens of separate agent files with nearly identical logic, the engine utilizes a single, highly optimized **Pillar Agent** that changes its behavior based on the `--slot` flag.

This ensures:
- **Consistency**: Logic updates apply to all pillars simultaneously.
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
          [ maat ] (Light Oversoul)   [ lilith ] (Dark Oversoul)
          (Governs P1-P5)             (Governs P6-P10)
             |                           |
             └─────────────┬─────────────┘
                           v
                [ pillar --slot PX ]
                (Single slot-based agent)
                           |
             ┌─────────────┼─────────────┐
             v             v             v
          [ jem ]    [ quality ]   [ researcher ]
       (Research)   (QA & Test)   (Deep Dive)
             |
       ┌─────┴─────┐
       v     v     v
    [disc] [synth] [verif] ──→ [scribe] ──→ soul.yaml
```

## 3. Agent Inventory

### 3.1 Primary Agents (Direct User/Plan Access)
| Agent | Mode | Purpose | Model Tier |
|-------|------|---------|------------|
| `plan` | Primary | The Architect — Grand Dispatcher & Strategy Lead | Heavy |
| `kali` | Primary | Grand Oversight — Unifier of Ma'at and Lilith | Heavy |
| `doom_guy` | Primary | Sovereign id Software Architect — WAD & Performance | Heavy |
| `roc_racoon` | Primary | Sovereign Miner — Legacy Archaeology | Lite |
| `researcher` | Primary | Sovereign Master Researcher — Lattice Reasoning | Heavy |
| `jem` | Primary | Research Orchestrator — 3-Tier Pipeline | Medium |

### 3.2 Subagents (Delegated Access)
| Agent | Mode | Purpose | Model Tier |
|-------|------|---------|------------|
| `maat` | Subagent | Light Oversoul — Build Side Governance (P1-P5) | Heavy |
| `lilith` | Subagent | Dark Oversoul — Run Side Governance (P6-P10) | Heavy |
| `pillar` | Subagent | Slot-based Domain Expert (P1-P10) | Lite |
| `quality` | Subagent | Merged Code Review & Stress Testing | Medium |
| `scribe` | Subagent | Gnosis Keeper — L1→L2→L3 Distillation | Heavy |
| `jem_discovery` | Subagent | Tier 1: Broad Search, Evidence Logging | Lite |
| `jem_synthesis` | Subagent | Tier 2: Pattern Recognition, Synthesis | Medium |
| `jem_verification` | Subagent | Tier 3: Fact-check, R-doc, Gnosis | Heavy |

## 4. Delegation & Escalation Paths

### 4.1 The Standard Path
`User` $\rightarrow$ `plan` $\rightarrow$ `kali` $\rightarrow$ `maat/lilith` $\rightarrow$ `pillar --slot PX`

### 4.2 Specialized Paths
- **Deep Research**: `kali` $\rightarrow$ `jem` $\rightarrow$ `[disc $\rightarrow$ synth $\rightarrow$ verif]` $\rightarrow$ `scribe` $\rightarrow$ `soul.yaml`
- **Quality Gate**: `pillar/researcher` $\rightarrow$ `quality` $\rightarrow$ `Sovereign Mandates Verification`
- **Lattice Deep Dive**: `researcher` $\rightarrow$ `lattice traversal` $\rightarrow$ `Reflective Verification`

## 5. Mandate Compliance
All agents must adhere to the **Sovereign Mandates**, specifically:
- **Mandate 10 (Fleet Integrity)**: No new agents without verified slot gap.
- **Mandate 11 (Soul Integrity)**: Mandatory L1→L2→L3 distillation before session close.
