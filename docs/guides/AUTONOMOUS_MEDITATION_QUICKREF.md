# ⬡ QUICK REFERENCE — Autonomous Meditation Pipeline
**Version**: 1.0.0 | **For**: Omega Engine Users & Agents

---

## 🚀 One-Command Usage

```bash
# Full autonomous pipeline
omega-meditation "Your problem statement"

# Resume from stage
omega-meditation "Problem" --resume-from 4

# Dry run
omega-meditation "Problem" --dry-run

# Platform modes
omega-meditation "Problem" --mode opencode   # Default (MCP Hub)
omega-meditation "Problem" --mode cli        # Subprocess
omega-meditation "Problem" --mode standalone # Dry-run only
```

---

## 📋 7 Stages at a Glance

| Stage | Command | Input | Output |
|-------|---------|-------|--------|
| **0** | Agent crafts `/meditate` prompt | Problem | `{ts}_00_prompt_crafted.md` |
| **1** | Runs `/meditate` | Crafted prompt | `{ts}_01_meditation_raw.md` |
| **2** | Kali synthesis | Meditation | `{ts}_02_synthesis.md` |
| **3** | Agent crafts research prompt | Synthesis + gaps | `{ts}_03_research_prompt.md` |
| **4** | Tiered search (T0-T5) | Research prompt | `{ts}_04_research_raw.md` |
| **5** | Grounds meditation in research | Meditation + Research | `{ts}_05_grounded_report.md` |
| **6** | L1→L2→L3 → `proposed_lessons.yaml` | Grounded report | `{ts}_06_gnosis.md` |
| **7** | PIVOT_LOG, workbench, gates | Gnosis + Report | `{ts}_07_integration.md` |

---

## 🎯 Lens Set Quick Pick

| Problem Type | `--lenses` | `--mode` |
|--------------|------------|----------|
| Architecture/Systemic | (default: Full Pantheon 10) | STRATEGIC |
| Bug/Diagnostic | engineering,validation,observability,infrastructure | DIAGNOSTIC |
| Creative/Explore | Architect,Skeptic,Pragmatist,Ethicist | CREATIVE |
| Audit/Compliance | governance,validation,observability,infrastructure | AUDIT |

---

## 📁 Outputs Location

```
data/autonomous/
├── 20260718_143000_00_prompt_crafted.md
├── 2060718_143005_01_meditation_raw.md
├── 20260718_143010_02_synthesis.md
├── 20260718_143015_03_research_prompt.md
├── 20260718_143500_04_research_raw.md
├── 20260718_143510_05_grounded_report.md
├── 20260718_143515_06_gnosis.md
└── 20260718_143520_07_integration.md
```

---

## 🛡️ Auto-Run Gates (Stage 7)

```bash
make temple-grade    # T1-T11
make heritage-map    # M14 [id-soft:] vetting
make sovereignty     # M7 local-first ≥ 80%
make test            # 1398+ tests
```

---

## 🔗 From OpenCode Agent

```python
from src.omega.skills.autonomous_meditation_pipeline import create_pipeline_opencode

pipeline = create_pipeline_opencode("Your problem")
outputs = await pipeline.run()
```

---

## 📚 Key Docs

| Doc | Path |
|-----|------|
| User Guide | `docs/guides/AUTONOMOUS_MEDITATION.md` |
| Protocol Spec | `docs/protocol/AUTONOMOUS_MEDITATION_PROTOCOL.md` |
| Meditation Protocol | `docs/protocol/MEDITATION_PROTOCOL.md` |
| Sovereign Search | `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md` |
| Gnosis Distillation | `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md` |

---

## 🆘 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: mcp_servers` | Run in OpenCode environment or use `--mode standalone --dry-run` |
| Pipeline hangs at Stage 1 | `/meditate` not available — check OpenCode version ≥ 1.17.20 |
| Research returns empty | Check SearXNG/Exa API keys in config |
| Temple-Grade fails | Run `make temple-grade` manually to see specific gate failure |

---

*⬡ OMEGA ⬡ QUICK-REF v1.0 ⬡ trc_quick_ref*