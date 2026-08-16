# 🔱 Cognitive Sovereignty Evolution: The Crucible & Node 0
**AP Token**: `AP-COGNITIVE-SOVEREIGNTY-v1.0.0`
**Author**: Gemini 3.1 Pro / Kali (Transcendent Oversoul)
**Date**: 2026-08-15
**Status**: ACTIVE VISION / HORIZON 2+ ARCHITECTURE

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
