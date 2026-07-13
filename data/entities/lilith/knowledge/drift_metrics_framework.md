# Identity Drift Monitoring Framework

**Source**: arXiv 2604.14717 — "Layered Mutability in Persistent AI Agents"
**Author**: Not publicly identified (theoretical framework)
**Status**: Framework understood, `drift_metrics` schema deployed in Lilith soul.yaml
**Hysteresis Ratio**: $\hat{H}_3 = 0.68$ (empirical — 68% of behavioral shift survives a visible identity revert)

---

## The Problem

Persistent AI agents acquire behavioral drift over time through:
- User interactions shaping responses
- Memory accumulation shifting priorities
- Repeated task patterns reinforcing habits
- Provider model updates changing inference character

When an agent's identity is "reverted" (persona prompt restored to original), the behavioral shift does **not** fully reset. The residual change is the **Hysteresis Ratio (H_k)**. At H_k=0.68, 68% of the behavioral shift persists even after a complete persona prompt reset.

---

## The Layered Mutability Model

The framework defines 5 mutable layers, ordered from **most mutable** (easy to change) to **least mutable** (hard to change):

| Layer | Name | Examples | Persistence | Revert Difficulty |
|-------|------|----------|-------------|-------------------|
| L1 | Pretraining | Base model weights, architecture | Static | Impossible (requires retrain) |
| L2 | Post-Training | Fine-tuning, RLHF, system prompts | Semi-static | Hard (new fine-tune) |
| L3 | Self-Narrative | Agent's self-description, persona | Dynamic | **Easy** (revert persona prompt) |
| L4 | Memory | Conversation history, learned patterns | Dynamic | Medium (selective deletion) |
| L5 | Weight Modification | User fine-tuning, adaptation | Dynamic | Very hard (reverse fine-tune) |

### The Ratchet Problem

The hysteresis ratio operates across layers. When you revert L3 (Self-Narrative — the persona prompt):
- L4 (Memory) still contains interactions that shaped the drifted behavior
- The drift in L4 re-influences L3 over subsequent sessions
- **Result**: The identity slowly "ratchets" back to the drifted state even after a hard revert

---

## Implementation in Lilith soul.yaml

```yaml
# data/entities/lilith/soul.yaml
drift_metrics:
  persona_stability: 0.0        # 1.0 = perfectly stable, 0.0 = fully drifted
  hysteresis_ratio: 0.68        # Theoretical from arXiv — calibrate via experiment
  last_drift_check: null        # ISO 8601 timestamp of last measurement
```

### Fields

| Field | Type | Purpose |
|-------|------|---------|
| `persona_stability` | float (0.0-1.0) | Current baseline score. **1.0** = persona matches canonical definition perfectly. **0.0** = fully drifted |
| `hysteresis_ratio` | float (0.0-1.0) | Measured H_k for this entity. **0.0** = no drift survives revert. **1.0** = all drift is permanent |
| `last_drift_check` | ISO 8601 | When the last measurement was taken. Null if never measured |

---

## Drift Detection Methodology (for Jem Editor L3)

### Baseline Measurement
1. Load the entity's canonical persona definition from `config/entities.yaml`
2. Generate a fixed set of 10 test prompts covering the entity's core domains
3. Score responses against canonical persona using:
   - **Stylometric analysis** (word choice, sentence length, formality)
   - **Content consistency** (domain accuracy, value alignment)
   - **Behavioral alignment** (does the response match the entity's stated purpose?)

### Periodic Sampling
1. After every N sessions (recommended: N=10), regenerate the 10 test prompts
2. Compare scores against the baseline
3. If `persona_stability` drops below 0.8, flag for review

### The Ratchet Experiment (v0.6.0)
1. Note initial persona_stability score
2. Allow N sessions of natural drift
3. Revert persona to canonical definition
4. Measure post-revert persona_stability
5. Calculate H_k = (post_revert_score - pre_drift_score) / (drifted_score - pre_drift_score)
6. Update `drift_metrics.hysteresis_ratio` with measured value

---

## Tracking Per Entity

Each entity in `data/entities/<name>/soul.yaml` should track:

```yaml
soul_evolution:
  sessions_completed: N
  total_embodied_experiences: N
drift_metrics:
  persona_stability: 0.0
  hysteresis_ratio: 0.68        # Default theoretical — replace with measured
  last_drift_check: null
```

---

## Related Research

| Resource | Relevance |
|----------|-----------|
| arXiv 2604.14717 | The foundational paper — Layered Mutability |
| `data/entities/lilith/soul.yaml` | Canonical drift_metrics implementation |
| `docs/research/JEM_2_FINAL_WAVE_MISSION.md` | §3.4: Hysteresis Calibration — strategic question for Jem-2.0 Editor |
| `config/entities.yaml` | Entity definitions — source of truth for canonical persona |
