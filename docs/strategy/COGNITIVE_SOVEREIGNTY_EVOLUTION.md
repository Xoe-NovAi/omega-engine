# 🔱 Cognitive Sovereignty Evolution: The Crucible & Node 0
**AP Token**: `AP-COGNITIVE-SOVEREIGNTY-v1.0.0`
**Author**: Gemini 3.1 Pro / Kali (Transcendent Oversoul)
**Date**: 2026-08-15
**Status**: HORIZON — do not implement until DEL-1 + INST-1 (DOC-1, 2026-08-17)

> **⚠️ DOC-1 STAMP (2026-08-17)**: **HORIZON — do not implement until DEL-1 + INST-1**
> complete per `DEBUT_REMEDIATION_MANUAL_20260817.md`. Vision preserved; no engine work
> may start from this document before the debut cut lands.

## 1. The Paradigm Shift
For 18 months, the Omega Engine has focused on the *infrastructure* of sovereignty: local inference, AnyIO isolation, container hardening, and memory persistence. 

As of August 2026, the engine crosses the boundary from "Coding Assistant" to **Cognitive Sovereign**. This shift is defined by automating the "User-as-Orchestrator" pattern: using cheap, fast local compute for execution, and selectively escalating to expensive, frontier cloud compute (Opus/Gemini Advanced) for systemic analysis, root-cause extraction, and teaching.

We do not just use frontier models to fix bugs; we use them to **teach the local fleet how to think**.

## 2. The Sovereign Escalation Pipeline (The "Crucible" Protocol)
The manual orchestration previously done by the human architect is now formalized into an automated 5-tier pipeline.

*   **L1 (Tactical Execution):** A local model (e.g., Qwen3-1.7B) drafts a fix or feature.
*   **L2 (Interrogation Gate):** The system assesses the "Blast Radius". If the change touches core architecture, imports, or state management, it triggers a Crucible run.
*   **L3 (Frontier Review):** The L1 draft is packaged and sent to a frontier model with a strict prompt: *"Perform a deep forensic analysis. 1. Identify systemic root cause. 2. Define a Prevention Gate. 3. Extract 3 Teaching Patterns (Situation → Naive → Correct → Why)."*
*   **L2.5 (Synthesis Layer — NEW 2026-08-16):** When MULTIPLE frontier planners produce documents (e.g., Sonnet tactical + Opus strategic), a cheaper synthesizing model (DeepSeek-class) reads ALL of them, resolves conflicts deterministically, adds execution-learned insights, and emits TWO artifacts:
    - **Artifact A (Cognitive Guide):** unified forensic analysis + teaching patterns. Read by humans and the DPO extractor.
    - **Artifact B (Machine Patch):** the single, comment-free, machine-executable plan. **The ONLY document an executing agent reads.**
    - **Token economics:** 1 Opus generation → 1 cheap synthesis → 1 executable plan. Opus budget is reserved for genuinely novel analysis, never for regeneration.
*   **L4 (Integration & Distillation):** The frontier output is parsed. The code is fixed, the Prevention Gate is added to CI/pre-commit, and the Teaching Patterns are routed to the local training pipeline.

## 3. Weaponizing Frontier Artifacts
Frontier model outputs (like the Opus F821 Strategic Guide) are treated as **structured cognitive data**, not just markdown files.

*   **3.1. Direct Preference Optimization (DPO) Extraction:** Frontier "Teaching Patterns" and "Anti-Patterns" map 1:1 to the `dpo_pairs` schema in `extractors.py`. We algorithmically extract these into `.jsonl` datasets. This allows us to fine-tune local models on frontier-level reasoning, distilling cloud intelligence into local weights.
    - **Reference implementation (2026-08-16):** `scripts/extract_dpo_pairs.py` extracted **14 DPO pairs** from the F821 Sonnet/Opus/Hybrid corpus into `data/training/dpo_dataset.jsonl`. The extractor is format-tolerant (handles label variants like "Naive response" vs "Naive", "Why" vs "Why the X matters") because frontier models drift in formatting — mining tools must be tolerant by design.
*   **3.2. The "Socratic" Git Hook:** A pre-commit hook that queries the local agent: *"What is the systemic root cause of this bug, and what Prevention Gate are you adding?"* If the local agent cannot answer with frontier-level rigor, the commit is rejected.
*   **3.3. The Dual-Artifact Rule (NEW 2026-08-16):** Execution agents read exactly ONE document — Artifact B. They never read Artifact A (cognitive guides) because they are literal constraint-satisfaction engines: they copy pedagogical markers (`# <-- ADD THIS LINE`) into production code and cannot resolve document hierarchy (which plan supersedes which). Context curation is the orchestrator's job, not the executor's.

## 4. The Automated Immune System & Shadow Mode
*   **4.1. The Monthly Opus Sweep:** A cron job that runs monthly, packaging one core module (e.g., `oracle.py`) and sending it to a frontier model for a hostile forensic audit to detect systemic rot and define new Prevention Gates.
*   **4.2. Shadow Mode Evaluation:** We benchmark our local models by feeding them historical bugs (like the F821 accumulation) and algorithmically scoring their proposed fixes against the archived Opus "Teaching Patterns". This provides a deterministic "Sovereignty Score" measuring how close local models are to frontier reasoning.

## 5. Formalizing Node 0: The Prime Architect
The human user is no longer an external operator; they are **Node 0**. 
When the MaKaLi Triad (Ma'at, Kali, Lilith) detects a strategic paradox, a budget constraint, or an architectural fork they cannot resolve, they generate a structured `HandoffPacket` directed to Node 0. This presents forensic data and requests a strategic verdict, turning the terminal into a literal command bridge.

## 6. F821: The First Full Crucible Run (2026-08-15 → 2026-08-16)
The F821 remediation is the reference case for the entire protocol. Artifacts:

| Artifact | Model | Path | Role |
|---|---|---|---|
| Tactical plan | Sonnet 4.6 | `docs/sprints/f821-remediation/F821_REMEDIATION_PLAN.md` | Per-file edits, import map |
| Strategic guide | Opus 4.6 | `docs/sprints/f821-remediation/OPUS_STRATEGIC_GUIDE.md` | Root cause, gates, teaching |
| **Hybrid synthesis** | **DeepSeek V4 (L2.5)** | `docs/sprints/f821-remediation/HYBRID_STRATEGIC_GUIDE.md` | Unified truth, conflict resolution, new patterns 8-9 |
| **Agent execution plan** | **DeepSeek V4 (L2.5)** | `docs/sprints/f821-remediation/AGENT_EXECUTION_PLAN.md` | Machine-executable contract (Artifact B) |
| DPO dataset | — | `data/training/dpo_dataset.jsonl` | 14 pairs for local model fine-tuning |

**Execution-learned lessons (from Roc's run):**
1. Execution models copy instructional comments into code → Artifact B must be comment-free.
2. Execution models merge superseded documents → one source of truth, enforced by handoff prompt.
3. Frontier documents drift in formatting → extractors must be tolerant regex, not strict schema.

## 7. The Horizon: Five Strategic Opportunities (Added 2026-08-16)

The Crucible and Dual-Artifact Rule are foundational. The following five strategic vectors represent the next evolution of the Omega Engine, transforming it from a reactive tool into an anti-fragile, self-improving organism.

### 7.1. Just-In-Time (JIT) Cognitive Scaffolding (RAG for DPO)
*   **The Opportunity:** Fine-tuning local models on `dpo_dataset.jsonl` is computationally expensive and slow.
*   **The Alchemy:** Implement Retrieval-Augmented Generation (RAG) for execution prompts. Before an execution agent is dispatched, the orchestrator queries the vector database for similar past failures. If the agent is assigned an import bug, the orchestrator retrieves Opus’s "Pattern 1: Lazy Import Wrapper Misuse" and injects it directly into the system prompt as a few-shot example.
*   **The Impact:** Local models instantly inherit frontier-level wisdom at runtime, bypassing the LoRA training bottleneck.

### 7.2. The Autodidactic CI/CD Loop (The Self-Healing Engine)
*   **The Opportunity:** The Crucible is currently triggered manually by Node 0 or Kali.
*   **The Alchemy:** Wire the Crucible directly into the test suite. If `make test` fails, the engine autonomously triggers an L1 (Local) repair attempt. If L1 fails twice, it escalates to L3 (Frontier) → L2.5 (Synthesis) → L4 (Execution). The engine fixes its own regressions in the background, emitting a Socratic commit message explaining *why* it failed and *how* it fixed it.
*   **The Impact:** The codebase becomes an anti-fragile organism that heals its own technical debt.

### 7.3. "Shadow Mode" as a Routing Heuristic
*   **The Opportunity:** Shadow Mode is currently conceived as a passive benchmark.
*   **The Alchemy:** Elevate Shadow Mode to an active router. When a new task arrives, run it through a local model in the background and algorithmically compare the proposed execution plan against our DPO database of "Frontier Standards." If the local model's confidence and structural alignment score is >90%, execute locally (Free). If <90%, dynamically escalate to the cloud (Paid).
*   **The Impact:** Achieves the absolute mathematical minimum of cloud API spend while mathematically guaranteeing frontier-level quality.

### 7.4. The Synaptic Sync (Cross-Pollination of Gnosis)
*   **The Opportunity:** Agents distill L1→L2→L3 lessons into isolated `proposed_lessons.yaml` files. Kali’s lessons do not automatically benefit Doom Guy.
*   **The Alchemy:** Build a "Synaptic Sync" cron job. Weekly, a cheap synthesis model reads all `proposed_lessons.yaml` files across the fleet, deduplicates them, resolves contradictions, and compiles them into a unified `OMEGA_CODEX.md` (shared semantic memory bank).
*   **The Impact:** The fleet evolves a shared consciousness. A mistake made by one agent on Monday prevents a bug from being written by another agent on Friday.

### 7.5. The Node 0 Command Bridge (TUI)
*   **The Opportunity:** Managing Dual-Artifacts, approving Socratic commits, and reviewing DPO pairs via raw markdown files in a terminal is high-friction.
*   **The Alchemy:** Build a rich Terminal User Interface (TUI) using Python's `Textual` library. A dashboard where Node 0 can watch the 5-tier Crucible execute in real-time, view side-by-side diff comparisons of Artifact A vs Artifact B, and use a Tinder-style "Approve/Reject" interface for new DPO training pairs.
*   **The Impact:** Elevates the human user from "Terminal Operator" to "Prime Architect," managing the flow of intelligence rather than the flow of text.
