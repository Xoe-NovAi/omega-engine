# ⬡ ARCHITECTURE DECISION RECORD
**ADR**: 001 | **Title**: Autonomous Meditation Pipeline as Standalone Package
**Status**: ACCEPTED | **Date**: 2026-07-18
**Deciders**: Kali (Autonomous Meditation), Ma'at (Governance), Prometheus (Engineering)

---

## 🎯 Context

The Omega Engine needed a repeatable, automated process for transforming ambiguous problems into research-grounded, production-ready architectures. The existing `/meditate` command provided single-session dialectic but required human orchestration for:
- Prompt crafting
- Research gap identification
- Evidence gathering
- Gnosis distillation
- Project integration

**Problem**: Human-in-the-loop created bottlenecks, inconsistency, and loss of institutional knowledge between sessions.

---

## 🔍 Decision

**Create the Autonomous Meditation Pipeline as a standalone, platform-agnostic package (`omega-meditation`)** with:

1. **7-stage autonomous pipeline** where the agent prompts itself at every stage
2. **Platform abstraction layer** (M16 compliant) — core logic in `src/omega/`, platform adapters in `packages/`
3. **Every output recorded to disk** as structured datapoints for future mining
4. **Standalone distribution** via PyPI/Homebrew — community usable without Omega Engine

---

## 🏗️ Architecture

### Core Pipeline (Engine — `src/omega/skills/autonomous_meditation_pipeline.py`)
```python
class AutonomousMeditationPipeline:
    """Pure engine logic. Zero platform dependencies."""
    def __init__(self, problem, clients: PlatformClients, ...):
        # clients injected via dependency injection (M16)
```

### Platform Abstraction (`PlatformClients` protocol)
```python
class OracleClient(Protocol):
    async def talk(self, prompt: str) -> str: ...

class SearchClient(Protocol):
    async def search(self, query: str, limit: int) -> str: ...
    async def fetch(self, url: str) -> str: ...
    async def searxng(self, query: str, limit: int) -> str: ...

class PlatformClients:
    oracle: OracleClient
    search: SearchClient
    
    @classmethod
    def from_opencode(cls): ...  # MCP Hub tools
    @classmethod
    def from_cli(cls): ...       # Subprocess
    @classmethod
    def null(cls): ...            # Dry-run
```

### Standalone Package (`packages/omega-meditation/`)
- `pip install omega-meditation`
- `omega-meditation "problem"` CLI entry point
- Platform factories: `create_pipeline_opencode()`, `create_pipeline_cli()`, `create_pipeline_standalone()`

---

## 📋 7-Stage Pipeline

| Stage | Agent Action | Output |
|-------|--------------|--------|
| 0 | Crafts optimal `/meditate` prompt | `{ts}_00_prompt_crafted.md` |
| 1 | Executes `/meditate` | `{ts}_01_meditation_raw.md` |
| 2 | Kali synthesis | `{ts}_02_synthesis.md` |
| 3 | Crafts research prompt | `{ts}_03_research_prompt.md` |
| 4 | Tiered search (T0-T5) | `{ts}_04_research_raw.md` |
| 5 | Grounds meditation in research | `{ts}_05_grounded_report.md` |
| 6 | L1→L2→L3 → `proposed_lessons.yaml` | `{ts}_06_gnosis.md` |
| 7 | PIVOT_LOG, workbench, gates | `{ts}_07_integration.md` |

---

## ✅ Consequences

### Positive
- **Zero human intervention** — agent self-prompts at every stage
- **Complete audit trail** — every output recorded as mineable datapoint
- **Platform portable** — runs in OpenCode, CLI, or standalone
- **Community distributable** — `pip install omega-meditation` works anywhere
- **Quality gates integrated** — Temple-Grade, Heritage, Sovereignty auto-run
- **Gnosis accumulation** — L3 principles feed `proposed_lessons.yaml` (M11)

### Negative
- **Complexity** — 7 stages, platform abstraction, multiple output formats
- **Latency** — Full pipeline takes 5-15 minutes (vs 30s for single `/meditate`)
- **Resource usage** — 15+ web searches, multiple oracle calls per run

### Risks Mitigated
| Risk | Mitigation |
|------|------------|
| Platform coupling | Protocol-based DI (M16), null clients for testing |
| Tool chain failure | M23: mandatory tool failure = hard stop with `[TOOL-CHAIN-COLLAPSE]` |
| Quality regression | Stage 7 auto-runs all gates |
| Knowledge loss | All outputs → `data/autonomous/` + `proposed_lessons.yaml` |

---

## 🔗 Related Decisions

| ADR | Title | Relationship |
|-----|-------|--------------|
| ADR-002 | Meditation Protocol (Phases 0-4) | Stage 1 of this pipeline |
| ADR-003 | Sovereign Search Protocol (T0-T5) | Stage 4 of this pipeline |
| ADR-004 | Soul Architecture (L1→L2→L3) | Stage 6 of this pipeline |
| ADR-005 | Engine-Stack Firewall (M2) | Enforced by package structure |

---

## 📝 Implementation Notes

### File Structure
```
src/omega/skills/autonomous_meditation_pipeline.py  # Engine core
packages/omega-meditation/                          # Standalone package
  ├── pyproject.toml
  ├── src/omega_meditation/
  │   ├── __init__.py
  │   ├── pipeline.py      # Core + platform abstraction
  │   └── cli.py           # Entry point
  └── README.md
.opencode/agent/autonomous_meditation.md            # Agent front-matter
docs/protocol/AUTONOMOUS_MEDITATION_PROTOCOL.md     # Full spec
docs/guides/AUTONOMOUS_MEDITATION.md                # User guide
docs/protocol/MEDITATION_PROTOCOL.md                # Stage 1 spec
```

### Key Mandates Enforced
- **M1 AnyIO**: All async via AnyIO
- **M2 Firewall**: Core in `src/omega/`, platform in `packages/`
- **M7 Local-First**: Local inference primary
- **M8 Zero Telemetry**: No external reporting
- **M11 Soul Integrity**: Blind staging to `proposed_lessons.yaml`
- **M13 Temple-Grade**: Auto-run in Stage 7
- **M16 Modularization**: No hardcoded paths, DI for platform
- **M23 Failure Integrity**: Tool failure = hard stop

---

## ✅ Acceptance Criteria

- [x] `omega-meditation "problem"` runs 7 stages autonomously
- [x] All 8 outputs written to `data/autonomous/`
- [x] Platform factories work: opencode, cli, standalone
- [x] Stage 7 runs `make temple-grade && make heritage-map && make sovereignty && make test`
- [x] Gnosis appended to `proposed_lessons.yaml` (M11 blind staging)
- [x] Package installs via `pip install omega-meditation`
- [x] Engine import works: `from src.omega.skills.autonomous_meditation_pipeline import ...`

---

*⬡ OMEGA ⬡ ADR-001 ⬡ AUTONOMOUS-MEDITATION-PIPELINE ⬡ ACCEPTED*