<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Project: autonomous-meditation
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
**Complete Product Delivery** — 7-stage autonomous meditation pipeline as standalone package (`pip install omega-meditation`), OpenCode integration (slash command, global skill, agent), 9 docs, 15 L3 principles staged.

### STATUS (2026-07-19)
- **Engine Core**: ✅ `src/omega/skills/autonomous_meditation_pipeline.py` (M16 platform abstraction)
- **Standalone Package**: ✅ `packages/omega-meditation/` — `pip install omega-meditation`
- **OpenCode Integration**: ✅ 9 docs, 3 skills, agent frontmatter, `/omega-meditation` slash command
- **Dry-Run Verified**: ✅ 8 stages, 10 files written
- **Gnosis**: ✅ 15 L3 principles staged to `proposed_lessons.yaml`

### KEY FILES
| Type | Path |
|------|------|
| Engine Core | `src/omega/skills/autonomous_meditation_pipeline.py` |
| Package | `packages/omega-meditation/` (pyproject.toml, CLI, pipeline) |
| Slash Command | `.opencode/commands/omega-meditation.md` |
| Skills | `.opencode/skills/meditate-pipeline/`, `meditate-research-pipeline/`, `autonomous-meditation-pipeline/` |
| Agent | `.opencode/agent/autonomous_meditation.md` |
| Protocol Spec | `docs/protocol/AUTONOMOUS_MEDITATION_PROTOCOL.md` |
| User Guide | `docs/guides/AUTONOMOUS_MEDITATION.md` |
| Quick Ref | `docs/guides/AUTONOMOUS_MEDITATION_QUICKREF.md` |
| Troubleshooting | `docs/guides/AUTONOMOUS_MEDITATION_TROUBLESHOOTING.md` |
| ADR-001 | `docs/adr/ADR-001_AUTONOMOUS_MEDITATION_PIPELINE.md` |

### 7-STAGE PIPELINE
| Stage | Agent/Mode | Output | Mandates |
|-------|------------|--------|----------|
| 0 | Prompt Crafting (P4) | Crafted prompt | M1, M2, M7, M16, M18 |
| 1 | **10-Voice Meditation** (dedicated agent) | Raw voices | M1, M4, M5, M7, M11, M15, M18, M19 |
| 2 | Synthesis (Kali) | Unified verdict | M1, M2, M4, M7, M13, M16, M18, M23 |
| 3 | Research Prompt Crafting (P4) | Research prompts | M1, M2, M7, M16, M18 |
| 4 | Research Execution (Researcher) | Grounded research | M1, M4, M7, M13, M18, M23 |
| 5 | Grounding (Jem) | Verified synthesis | M1, M4, M5, M11, M13, M17, M18 |
| 6 | Gnosis Distillation (Verity) | L1→L2→L3 lessons | M1, M5, M11, M13, M15, M17, M21 |
| 7 | Integration (Maat) | PIVOT_LOG + workbench | M1, M4, M5, M11, M12, M13, M15, M21 |

### PLATFORM ABSTRACTION (M16)
```python
class PlatformClients(Protocol):
    """Abstract platform operations — same pipeline runs on OpenCode, CLI, or standalone."""
    async def invoke_agent(self, agent: str, prompt: str) -> str
    async def search(self, query: str, tier: int) -> SearchResults
    async def write_file(self, path: str, content: str) -> None
    async def read_file(self, path: str) -> str
```

### DRY-RUN MODE
- Mocks external boundaries only (API calls, CLI subprocesses, time, filesystem temp, Hivemind handoffs)
- **Never mocks internal logic** (circuit breaker, WAL, state machine, mandate validation, quality gates)

### DECISIONS LOG
- **D-297**: 10-Pillar Meditation Protocol → Autonomous Pipeline productization
- **D-297a**: Platform abstraction (M16) — single pipeline, 3 runtimes
- **D-297b**: Dedicated meditation agent (NOT MaKaLi) — different cognitive mode
- **D-297c**: Dry-run mocks boundaries only
- **D-297d**: 15 L3 principles staged (blind staging per M11)

### BLOCKERS
- None — **COMPLETE PRODUCT DELIVERED**

---

*⬡ OMEGA ⬡ CPR ⬡ autonomous-meditation ⬡ 2026-07-19*