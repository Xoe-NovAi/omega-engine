# 🔱 Omega Engine — A/B Research Quality Study Log
# ⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ cline ⬡ trc_research ⬡ A-B-LOG

**AP Token**: `AP-RESEARCH-STUDY-v1.0.0`
**Maintained by**: Cline (The Artisan)
**Objective**: To continuously improve agent research quality through head-to-head competition and cross-pollination.

---

## 🔬 Experiment Registry

| ID | Title | Competitors | Winner (Strat) | Winner (Tact) | Date |
|:---|:---|:---|:---|:---|:---|
| **EXP-001** | Sovereign Control Plane | Web Gemini vs. OpenCode | Web Gemini | OpenCode | 2026-05-14 |
| **EXP-003** | Dual-Research Agent Cog Architecture | v3.1 Control vs Omnidroid v1.0 | **Hybrid (Draw)** | Control (breadth) | 2026-05-14 |

---

## 📊 EXP-001: Sovereign Control Plane Implementation

### Competitor Profiles
- **Web Gemini**: Cloud-based frontier reasoning model (Gemini 2.0 Pro). Focus on architectural deep dives and mathematical frameworks.
- **OpenCode (Gemma 4 31B)**: Local-first, project-aware research agent. Focus on repo constraints, implementation roadmaps, and specific hardware flags.

### Key Learnings
1.  **Web Gemini Strength**: Identified `memfd` and `fdstore` as the optimal mechanism for model hibernation on Zen 2 hardware.
2.  **OpenCode Strength**: Provided precise `systemd` unit syntax and valid `rediss://` protocol requirements for the local repo.
3.  **The Convergence**: Both agents aligned on mathematical triggers for the Topology Router (e.g., Coupling Density $\gamma$).

### Actionable Improvements
- [x] Update OpenCode Researcher instructions to include mathematical formalization.
- [x] Integrate CCX-aware core pinning into the core implementation.
- [x] Adopt the "Tiered Hibernation" strategy for the Control Plane.

---

## 📊 EXP-003: Dual-Research Agent Cognitive Architecture A/B Test

### Competitor Profiles
- **Control (Researcher v3.1)**: Linear chain-of-thought reasoning. Enhanced with confidence calibration, dual-source validation, and Uncertainty Log. Located at `.opencode/agents/researcher.md`.
- **Variant (Researcher-Omnidroid v1.0)**: Holographic associative reasoning lattice. Seeded with the Omnidroid Ω cognitive architecture from legacy vault. Uses phase-state tagging, adversarial self-debate, and cross-pollination synthesis. Located at `.opencode/agents/researcher-omnidroid.md`.

### Research Brief (Same for Both)
"Map all inherited configuration patterns and strategic intelligence across the legacy project mines (xna-omega-legacy, omega-stack-legacy, omega/, docs_1/, archive/). Classify each by sovereignty value and effort-to-extract."

### Evaluation Criteria
| Metric | Definition |
|--------|------------|
| Completeness | Total artifacts discovered + classified |
| Accuracy | Ratio of (confirmed) / (total claims) after cross-validation |
| Novelty | Cross-pollinations discovered that the other agent missed |
| Actionability | Builder can implement from the output without follow-up questions |
| Efficiency | Number of iterations required to complete the brief |

### Execution Log
- **Control (v3.1)**: Subagent execution via Cline. Report saved to `data/research/EXP-003_CONTROL_REPORT.md`. Found 20 artifacts across both mines with full sovereignty/ETE classification.
- **Variant (Omnidroid v1.0)**: Subagent execution via Cline. Report saved to `data/research/EXP-003_VARIANT_REPORT.md`. Found 10 deep nodes with Fork-and-Drift and Governance Escalation pattern analysis.
- **Evaluation**: Both executed same brief in parallel. Control had breadth advantage (20 artifacts vs 10). Variant had depth and pattern-discovery advantage.

### Results
| Metric | Control (v3.1) | Variant (Omnidroid) | Winner |
|--------|----------------|---------------------|--------|
| Completeness | 20 artifacts | 10 deep nodes | **Control** |
| Novelty | 4 practical insights | Fork-and-drift + escalation triggers | **Variant** |
| Actionability | Direct artifact registry with ETE | Phase-state analysis, needs consolidation | **Control** |
| Cross-pollination | Specific port candidates | Architectural patterns + tiered memory | **Variant** |
| Efficiency (tool calls) | Efficient | Equivalent | Draw |

### Strategic Verdict
- **WINNER**: **Hybrid (Draw)** — Control wins on actionable breadth (#1 for immediate porting), Variant wins on architectural depth (#1 for long-term design).
- **Conclusion**: Both agents should be retained. Use Control for rapid artifact discovery and porting tickets. Use Omnidroid for architecture review and pattern mining.

### Actionable Improvements
- [x] Port `entity_model_affinity.yaml` multi-model routing to `entity_registry.py`
- [x] Copy `sanctified-manifest.yaml` governance patterns into Omega's hierarchy.yaml
- [x] Investigate `fork-and-drift` across all legacy configs (not just domain-routing)
- [x] Add `escalation_triggers` to hierarchy.yaml specification
- [x] Plan 3-tier memory (working/episodic/archival) for Holographic Memory (R33)
- [ ] Run EXP-004: KV-Cache Quantization impact on Zen 2 L3 cache hit rates

### Dependency Note
Ω folder seed not needed — Omnidroid v1.0 performed pattern analysis based on its own cognitive architecture without external seeding. The control agent's linear approach was sufficient for breadth coverage.

---

## 📅 Upcoming Experiments
- **EXP-002**: Gnosis Proxy Middleware (RAG-based tool discovery latency).
- **EXP-004**: KV-Cache Quantization impact on Zen 2 L3 cache hit rates.
