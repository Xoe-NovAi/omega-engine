<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ Omega Meditation — Autonomous Meditation Pipeline

**Problem → Prompt Crafting → Meditation → Synthesis → Research → Grounded Update → Gnosis → Integration**

Fully autonomous 7-stage pipeline that transforms any problem statement into a research-grounded, production-ready architecture with zero human intervention.

## Features

- **Stage 0**: Agent crafts optimal `/meditate` prompt for the problem
- **Stage 1**: Executes meditation via `/meditate` command
- **Stage 2**: Produces intuitive synthesis (Kali Verdict)
- **Stage 3**: Crafts research prompt for gaps/verification
- **Stage 4**: Executes tiered research (T0-T5: local → websearch → webfetch → SearXNG → Exa → Firecrawl)
- **Stage 5**: Produces research-grounded updated report
- **Stage 6**: Distills L1→L2→L3 gnosis → `proposed_lessons.yaml`
- **Stage 7**: Integrates into project governance (PIVOT_LOG, workbench, Temple-Grade gates)

## Installation

```bash
pip install omega-meditation
# or with platform support
pip install omega-meditation[opencode]  # OpenCode environment
pip install omega-meditation[cli]       # CLI environment
```

## Usage

```bash
# Fully autonomous run
omega-meditation "Unified credential vault for local AI tooling"

# Resume from specific stage
omega-meditation "problem" --resume-from 3

# Dry run (no external calls)
omega-meditation "problem" --dry-run

# Specify platform
omega-meditation "problem" --platform opencode
omega-meditation "problem" --platform cli
omega-meditation "problem" --platform standalone
```

## Outputs

Every run produces 8 structured datapoints in `data/autonomous/`:

```
data/autonomous/
├── {timestamp}_00_prompt_crafted.md      # Agent's self-prompt
├── {timestamp}_01_meditation_raw.md      # Raw /meditate output
├── {timestamp}_02_synthesis.md           # Intuitive briefing
├── {timestamp}_03_research_prompt.md     # Research self-prompt
├── {timestamp}_04_research_raw.md        # 15+ deep searches
├── {timestamp}_05_grounded_report.md     # Verified architecture
├── {timestamp}_06_gnosis.md              # 14 L3 principles
└── {timestamp}_07_integration.md         # PIVOT_LOG + gates
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│  PROBLEM → PROMPT CRAFT → MEDITATE → SYNTHESIZE → RESEARCH  │
│       ↓           ↓           ↓           ↓           ↓     │
│   CRAFTED      /meditate    KALI        RESEARCH      GROUNDED│
│   PROMPT       EXECUTION    VERDICT     PROMPT         REPORT │
│       ↓           ↓           ↓           ↓           ↓     │
│   RECORDED    RECORDED     RECORDED    RECORDED      RECORDED │
│       ↓           ↓           ↓           ↓           ↓     │
│   GNOSIS DISTILLATION → INTEGRATION (PIVOT_LOG, GATES)      │
└─────────────────────────────────────────────────────────────┘
```

## Platform Integration

The core pipeline is **platform-agnostic** (M16 compliant). Platform-specific clients are injected at runtime:

| Platform | Factory | Clients |
|----------|---------|---------|
| OpenCode | `create_pipeline_opencode()` | MCP Hub tools (`omega_hub_oracle_talk`, `omega_hub_library_web_search`, etc.) |
| CLI | `create_pipeline_cli()` | Subprocess calls to `opencode`, `websearch` |
| Standalone | `create_pipeline_standalone()` | Null clients (dry-run only) |

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Lint
ruff check .

# Type check
mypy src/omega_meditation
```

## Heritage

- **Meditation Protocol**: Architect's Gemini CLI experiments (2025) → Strike 11.5 Council Dispatcher → `/meditate` command (2026-07-16)
- **Sovereign Search**: Omega Engine T0-T5 tiered escalation
- **Gnosis Distillation**: Soul Architecture Protocol (M11) → Verity agent
- **Integration**: Ma'at governance → PIVOT_LOG, workbench, Temple-Grade

## License

MIT