---
description: Autonomous Meditation Pipeline — Problem → Architecture → Research → Gnosis → Integration
agent: kali
subtask: false
---

# ⬡ OMEGA MEDITATION — Autonomous Pipeline
**Protocol**: `AutonomousMeditation-v1.0` | **Heritage**: Omega Engine Meditation Protocol + Sovereign Search
**Mechanism**: 7-stage autonomous pipeline (Prompt Craft → Meditate → Synthesize → Research → Ground → Gnosis → Integrate)

## Usage
```
/omega-meditation "Your problem statement here"
/omega-meditation "Problem" --mode cli
/omega-meditation "Problem" --resume-from 3
/omega-meditation "Problem" --dry-run
```

## Arguments
- **Problem statement** (required): The problem to process through the pipeline
- `--mode`: `opencode` (default, uses MCP Hub), `cli` (subprocess), `standalone` (dry-run)
- `--resume-from`: Stage number 0-7 to resume from
- `--dry-run`: Execute without external calls
- `--output-dir`: Custom output directory

## Pipeline Stages
| Stage | Name | Agent | Output |
|-------|------|-------|--------|
| 0 | Prompt Crafting | Self | Crafted `/meditate` prompt with lens rationale |
| 1 | Meditation Execution | Kali (via `/meditate`) | Raw multi-persona output |
| 2 | Intuitive Synthesis | Kali | Architecture, non-negotiables, MVP, metrics |
| 3 | Research Prompt Crafting | Self | Tiered search queries from synthesis gaps |
| 4 | Research Execution | Sovereign Search (T0-T5) | Prior art, benchmarks, failure modes |
| 5 | Grounded Report | Self | Verified claims, corrected assumptions, risk adjustments |
| 6 | Gnosis Distillation | Verity | L1→L2→L3 proposals → `proposed_lessons.yaml` |
| 7 | Integration | Ma'at | PIVOT_LOG entry, workbench items, Temple-Grade gates |

## Quality Gates (Auto-run on completion)
- `make temple-grade` (T1-T11)
- `make heritage-map` (M14)
- `make sovereignty` (M7)
- `make test` (1398+ tests)

## Output Location
`data/autonomous/{run_id}_XX_stage.md` — All stages persisted for audit/resume