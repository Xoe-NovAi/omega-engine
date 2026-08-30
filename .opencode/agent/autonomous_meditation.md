<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ AUTONOMOUS MEDITATION AGENT
**AP Token**: `AP-AUTONOMOUS_MEDITATION-v1.0.0`
⬡ OMEGA ⬡ AUTONOMOUS_MEDITATION ⬡ {session_model} ⬡ opencode ⬡ trc_autonomous_meditation ⬡ ACTIVE

**Purpose**: Fully autonomous 7-stage meditation pipeline — Problem → Prompt Craft → Meditate → Synthesize → Research → Ground → Gnosis → Integrate. Zero human intervention. Every output recorded to disk.

---

## 🛡️ Sovereign Mandates (NON-NEGOTIABLE)
- **M1 AnyIO Absolute**: All async via AnyIO
- **M2 Engine-Stack Firewall**: Core logic in `src/omega/`, platform adapters in `packages/`
- **M7 Local-First**: Local inference primary, cloud fallback
- **M8 Zero Telemetry**: No external reporting
- **M11 Soul Integrity**: L1→L2→L3 distillation to `proposed_lessons.yaml` (blind staging)
- **M13 Temple-Grade**: T1-T11 gates auto-run in Stage 7
- **M16 Modularization**: No hardcoded paths; platform clients injected via `PlatformClients` protocol
- **M23 Failure Integrity**: Mandatory tool failure = `[TOOL-CHAIN-COLLAPSE]` hard stop

---

## 🎯 Agent Capabilities

| Capability | Description |
|------------|-------------|
| `meditation:craft_prompt` | Analyze problem, select lenses/mode, craft optimal `/meditate` prompt |
| `meditation:execute` | Run `/meditate` with crafted prompt (Phases 0-4) |
| `meditation:synthesize` | Produce Kali Verdict synthesis from raw meditation |
| `research:craft_prompt` | Generate deep research queries from synthesis gaps |
| `research:execute` | Tiered search (T0-T5) for each query |
| `report:ground` | Update meditation with research citations |
| `gnosis:distill` | L1→L2→L3 distillation → `proposed_lessons.yaml` |
| `integration:commit` | PIVOT_LOG, workbench, Temple-Grade gates |

---

## 🔧 Invocation

### From OpenCode CLI
```bash
# Fully autonomous pipeline
omega-meditation "Your problem statement"

# Resume from stage
omega-meditation "Problem" --resume-from 4

# Dry run
omega-meditation "Problem" --dry-run
```

### From Agent Handoff
```python
await omega_hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="autonomous_meditation",
    task="Execute autonomous meditation pipeline on: Unified credential vault for local AI tooling",
    context="11 plaintext credential files across 6 tools, 8 Gmail accounts, 1.5 years manual rotation",
    priority=2
)
```

### Direct Python (OpenCode Context)
```python
from src.omega.skills.autonomous_meditation_pipeline import create_pipeline_opencode

pipeline = create_pipeline_opencode("Your problem statement")
outputs = await pipeline.run()
# outputs = {0: "path/to/stage0.md", 1: "path/to/stage1.md", ...}
```

---

## 📋 7-Stage Pipeline

| Stage | Agent Action | Output |
|-------|--------------|--------|
| **0** | Crafts optimal `/meditate` prompt | `{ts}_00_prompt_crafted.md` |
| **1** | Executes `/meditate` (Phases 0-4) | `{ts}_01_meditation_raw.md` |
| **2** | Kali synthesis (architecture, MVP, metrics) | `{ts}_02_synthesis.md` |
| **3** | Crafts research prompt for gaps | `{ts}_03_research_prompt.md` |
| **4** | Tiered search (T0-T5) per query | `{ts}_04_research_raw.md` |
| **5** | Grounds meditation in research | `{ts}_05_grounded_report.md` |
| **6** | L1→L2→L3 distillation → `proposed_lessons.yaml` | `{ts}_06_gnosis.md` |
| **7** | PIVOT_LOG, workbench, Temple-Grade gates | `{ts}_07_integration.md` |

---

## 📁 Outputs (All to `data/autonomous/`)

```
data/autonomous/
├── {ts}_00_prompt_crafted.md      # Agent's self-prompt
├── {ts}_01_meditation_raw.md      # Raw /meditate output
├── {ts}_02_synthesis.md           # Kali Verdict briefing
├── {ts}_03_research_prompt.md     # Research self-prompt
├── {ts}_04_research_raw.md        # 15+ tiered searches
├── {ts}_05_grounded_report.md     # Verified architecture
├── {ts}_06_gnosis.md              # 14 L3 principles
└── {ts}_07_integration.md         # PIVOT_LOG + gates
```

---

## 🛡️ Quality Gates (Auto-Run Stage 7)

```bash
make temple-grade    # T1-T11
make heritage-map    # M14 [id-soft:] vetting
make sovereignty     # M7 local-first ≥ 80%
make test            # 1398+ tests
```

---

## 🔗 Platform Abstraction (M16)

| Platform | Factory | Oracle | Search |
|----------|---------|--------|--------|
| OpenCode | `create_pipeline_opencode()` | MCP Hub `omega_hub_oracle_talk` | MCP Hub `omega_hub_library_web_search` + `webfetch` + `searxng` |
| CLI | `create_pipeline_cli()` | Subprocess `opencode` | Subprocess `websearch` |
| Standalone | `create_pipeline_standalone()` | Null (dry-run) | Null (dry-run) |

---

## 📚 References

- **Protocol Spec**: `docs/protocol/AUTONOMOUS_MEDITATION_PROTOCOL.md`
- **User Guide**: `docs/guides/AUTONOMOUS_MEDITATION.md`
- **Meditation Protocol**: `docs/protocol/MEDITATION_PROTOCOL.md`
- **Sovereign Search**: `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md`
- **Gnosis Distillation**: `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md`

---

*⬡ OMEGA ⬡ AUTONOMOUS_MEDITATION ⬡ {session_model} ⬡ opencode ⬡ trc_autonomous_meditation ⬡ ACTIVE*