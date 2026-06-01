# 🔱 Omega Engine — Training Pipeline & Synthesis Flywheel
# AP: AP-TRAINING-PIPELINE-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: FLYWHEEL | CONTEXT: SOVEREIGN-EVOLUTION]

The Training Pipeline is the mechanism by which the Omega Engine evolves from a stateless tool into a stateful sovereign intelligence.

## 1. The Synthesis Flywheel
The engine uses a "Cloud $\rightarrow$ Local" knowledge transfer loop:
1. **Cloud Teaching**: Heavy models produce high-reasoning chains and preference pairs.
2. **Local Capture**: These are stored as synthetic training data in `data/datasets/`.
3. **Local Adaptation**: Lite-tier models are fine-tuned on this data via LoRA.
4. **Sovereignty Increase**: Over time, the local model's performance approaches the cloud teacher.

## 2. The JEM 3-Tier Pipeline
The synthesis of training data follows the JEM protocol:
- **Discovery (L1)**: Broad search, evidence logging.
- **Synthesis (L2)**: Pattern recognition, structural mapping.
- **Verification (L3)**: Fact-check, Gnosis distillation.

The final output is a **Training Triple**: `(Instruction, Context, Verified Response)`.

## 3. Benchmarking & Validation
Before any new model version is promoted to an entity, it must pass a rigorous benchmark:

### 3.1 LLM-as-a-Judge
Evaluation is performed by a "Judge" model using:
- **3-Point Scale**: `fail` / `pass` / `excellent`.
- **Per-Criterion Scoring**: Separate scores for Accuracy, Adherence, Conciseness, and Structure.
- **Position Randomization**: A/B swap to eliminate position bias.
- **Calibration Loop**: The judge's performance is measured against a gold set of 50-200 labeled examples.

### 3.2 Metrics
- **TTFT (Time to First Token)**: Measures responsiveness.
- **TPS (Tokens Per Second)**: Measures throughput.
- **Peak RAM**: Ensures the model fits within the 12GB budget.
- **Avg Quality Score**: The normalized aggregate of the 3-point criteria.

## 4. Hardware Constraints (Zen 2)
- **Lite Tier (0.6B-1.7B)**: Fine-tunable locally on 14GB RAM.
- **Medium Tier (3B-4B)**: Inference only.
- **Heavy Tier (8B+)**: Inference only (or cloud-delegated fine-tuning).
