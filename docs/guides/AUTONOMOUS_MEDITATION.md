# ⬡ AUTONOMOUS MEDITATION PIPELINE — User Guide
**Version**: 1.0.0 | **Audience**: Omega Engine Users & Contributors
**Purpose**: Complete guide to running the autonomous meditation pipeline

---

## 🎯 What Is This?

The **Autonomous Meditation Pipeline** transforms any problem statement into a **research-grounded, production-ready architecture** with **zero human intervention**.

It runs 7 stages automatically:
```
PROBLEM → PROMPT CRAFT → MEDITATE → SYNTHESIZE → RESEARCH → GROUND → GNOSIS → INTEGRATE
```

Every output is recorded to disk as structured datapoints for future mining.

---

## 🚀 Quick Start

### Prerequisites
- Omega Engine installed (`pip install -e .` from repo root)
- OpenCode environment (for full autonomous mode)

### Run It
```bash
# Fully autonomous (recommended)
omega-meditation "Your problem statement here"

# Examples:
omega-meditation "Unified credential vault for local AI tooling — 11 plaintext files, 6 tools, 8 Gmail accounts"
omega-meditation "Fix Gemma 4 thinking levels on OpenCode Google provider"
omega-meditation "Design local-first observability without telemetry"

# Resume from specific stage (0-7)
omega-meditation "Problem" --resume-from 4

# Dry run (no external API calls)
omega-meditation "Problem" --dry-run
```

---

## 📋 Stage Breakdown

| Stage | Name | What Happens | Output |
|-------|------|--------------|--------|
| **0** | **Prompt Crafting** | Agent analyzes problem, selects optimal lenses/mode, crafts `/meditate` prompt | `{ts}_00_prompt_crafted.md` |
| **1** | **Meditation** | Executes `/meditate` with crafted prompt (10 voices, collisions, verdict) | `{ts}_01_meditation_raw.md` |
| **2** | **Synthesis** | Kali produces intuitive briefing: architecture, non-negotiables, MVP, metrics | `{ts}_02_synthesis.md` |
| **3** | **Research Prompt** | Agent crafts deep research queries for gaps/verification | `{ts}_03_research_prompt.md` |
| **4** | **Research** | Tiered search (T0-T5) for each query: local → websearch → webfetch → SearXNG → Exa → Firecrawl | `{ts}_04_research_raw.md` |
| **5** | **Grounded Report** | Updates meditation with research citations, corrects assumptions, adds prior art | `{ts}_05_grounded_report.md` |
| **6** | **Gnosis** | L1→L2→L3 distillation → `proposed_lessons.yaml` (blind staging per M11) | `{ts}_06_gnosis.md` |
| **7** | **Integration** | PIVOT_LOG entry, workbench items, Temple-Grade gates auto-run | `{ts}_07_integration.md` |

---

## 📁 Outputs

All outputs in `data/autonomous/`:
```
data/autonomous/
├── 20260718_143000_00_prompt_crafted.md
├── 20260718_143005_01_meditation_raw.md
├── 20260718_143010_02_synthesis.md
├── 20260718_143015_03_research_prompt.md
├── 20260718_143500_04_research_raw.md
├── 20260718_143510_05_grounded_report.md
├── 20260718_143515_06_gnosis.md
└── 20260718_143520_07_integration.md
```

---

## 🔧 Advanced Usage

### Platform Modes
```bash
# OpenCode (default - uses MCP Hub tools)
omega-meditation "Problem" --mode opencode

# CLI (subprocess calls to opencode/websearch)
omega-meditation "Problem" --mode cli

# Standalone (dry-run only, no platform clients)
omega-meditation "Problem" --mode standalone --dry-run
```

### Custom Output Directory
```bash
omega-meditation "Problem" --output-dir /custom/path
```

### Resume Interrupted Run
```bash
# Stages 0-3 complete, resume from research
omega-meditation "Problem" --resume-from 4
```

---

## 🧠 From OpenCode Agent

```python
# In any OpenCode agent context
from src.omega.skills.autonomous_meditation_pipeline import create_pipeline_opencode

pipeline = create_pipeline_opencode("Your problem statement")
outputs = await pipeline.run()

# outputs = {0: "path/to/stage0.md", 1: "path/to/stage1.md", ...}
```

---

## 🛡️ Quality Gates (Auto-Run in Stage 7)

| Gate | Command | Purpose |
|------|---------|---------|
| Temple-Grade | `make temple-grade` | T1-T11 compliance |
| Heritage Map | `make heritage-map` | M14 `[id-soft:]` tag vetting |
| Sovereignty | `make sovereignty` | M7 local-first ratio ≥ 80% |
| Tests | `make test` | 1398+ tests pass |

---

## 🔗 Related Commands

| Command | Purpose |
|---------|---------|
| `/meditate "topic"` | Single meditation session (Phases 0-4) |
| `omega-meditation "problem"` | Full 7-stage autonomous pipeline |
| `make temple-grade` | Verify all quality gates |

---

## 📚 See Also

- **Protocol Spec**: `docs/protocol/AUTONOMOUS_MEDITATION_PROTOCOL.md`
- **Meditation Protocol**: `docs/protocol/MEDITATION_PROTOCOL.md`
- **Sovereign Search**: `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md`
- **Gnosis Distillation**: `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md`

---

*⬡ OMEGA ⬡ AUTONOMOUS-MEDITATION v1.0 ⬡ trc_user_guide*