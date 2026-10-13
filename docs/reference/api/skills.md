# 🔱 Skills — OpenCode Skill System
**AP Token**: `AP-SKILLS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Skills package — OpenCode skill definitions for autonomous meditation pipeline and opencode client integration.
**Tags**: skills, opencode, meditation, pipeline, client
**Cross-references**: src/omega/skills/opencode_client.py, src/omega/skills/autonomous_meditation_pipeline.py, .opencode/skills/

---

## Overview

The `skills` package provides **OpenCode skill implementations** — reusable, composable capabilities that extend the Omega Engine's functionality within the OpenCode environment.

```
┌─────────────────────────────────────────────────────────────┐
│                      Skills Package                          │
├─────────────────────────────────────────────────────────────┤
│  opencode_client.py           │  OpenCode API client         │
│  autonomous_meditation_pipeline.py │  Meditation pipeline skill │
│  __init__.py                  │  Package exports             │
└─────────────────────────────────────────────────────────────┘
```

**Skill Definition Location**: `.opencode/skills/*/SKILL.md` (OpenCode native format)

---

## opencode_client.py — OpenCode API Client

Programmatic client for interacting with OpenCode's API.

### OpenCodeClient

```python
from omega.skills.opencode_client import OpenCodeClient

client = OpenCodeClient(base_url="http://localhost:8080")

# List sessions
sessions = await client.list_sessions()

# Get session details
session = await client.get_session("ses_abc123")

# Send message to session
response = await client.send_message("ses_abc123", "Continue the analysis")

# Create new session
session = await client.create_session(
    agent="jem",
    directory="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"
)
```

### Methods

| Method | Description |
|--------|-------------|
| `list_sessions()` | List all OpenCode sessions |
| `get_session(session_id)` | Get session metadata + messages |
| `send_message(session_id, text)` | Send message to existing session |
| `create_session(agent, directory)` | Create new session |
| `delete_session(session_id)` | Delete session |

---

## autonomous_meditation_pipeline.py — Meditation Pipeline Skill

**Automated Problem → Meditation → Synthesis → Research → Gnosis → Integration** pipeline for architectural questions.

### AutonomousMeditationPipeline

```python
from omega.skills.autonomous_meditation_pipeline import AutonomousMeditationPipeline

pipeline = AutonomousMeditationPipeline(
    opencode_client=client,
    meditation_agent="maat",
    synthesis_agent="lilith",
    research_agent="roc_racoon"
)

# Execute full pipeline
result = await pipeline.execute(
    problem="Design the sovereign memory architecture for Omega Engine v2",
    context="Must satisfy M1, M2, M7, M11, M13, M20, M23"
)
```

### Pipeline Stages

| Stage | Agent | Input | Output |
|-------|-------|-------|--------|
| 1. **Problem Framing** | Maat | Raw problem | Structured problem statement |
| 2. **Meditation** | Maat (10-voice) | Problem | Meditation record |
| 3. **Synthesis** | Lilith | Meditation | Synthesis report |
| 4. **Research** | Roc Racoon | Synthesis gaps | Research findings |
| 5. **Gnosis Extraction** | Jem | Research + Synthesis | L3 principles |
| 6. **Integration** | Kali | Gnosis + Proposal | Architecture decision |

### Meditation Record

```python
@dataclass
class MeditationRecord:
    problem: str
    voices: List[Dict]  # 10 voices with perspective, insight, confidence
    synthesis: str
    research_gaps: List[str]
    gnosis_candidates: List[str]  # L3 principle candidates
    timestamp: str
```

### Usage Example

```python
from omega.skills import AutonomousMeditationPipeline, OpenCodeClient

client = OpenCodeClient()
pipeline = AutonomousMeditationPipeline(
    opencode_client=client,
    meditation_agent="maat",
    synthesis_agent="lilith",
    research_agent="roc_racoon"
)

result = await pipeline.execute(
    problem="How should we implement the Engine-Stack Firewall for WAD isolation?",
    context="Must enforce M2: no stack logic in src/omega/"
)

print(f"Meditation: {result.meditation_record.synthesis}")
print(f"Research Gaps: {result.meditation_record.research_gaps}")
print(f"Gnosis Candidates: {result.meditation_record.gnosis_candidates}")
print(f"Final Decision: {result.integration_decision}")
```

---

## Skill Registration (OpenCode Native)

Skills are defined in `.opencode/skills/*/SKILL.md` with OpenCode native format:

```markdown
# Skill: autonomous-meditation
description: "Automated architectural meditation pipeline"
version: "1.0.0"
author: "Omega Engine"

# Commands
commands:
  - name: "meditate"
    description: "Run full meditation pipeline on a problem"
    arguments:
      - name: "problem"
        type: "string"
        required: true
      - name: "context"
        type: "string"
        required: false
```

### Available Skills

| Skill | Description | Location |
|-------|-------------|----------|
| `autonomous-meditation` | Full Problem→Gnosis pipeline | `.opencode/skills/autonomous-meditation/` |
| `meditate-research-pipeline` | Research-specific meditation | `.opencode/skills/meditate-research-pipeline/` |
| `makali-council-coordinator` | MaKaLi Parallel Council | `.opencode/skills/makali-council-coordinator/` |
| `sovereign-refinement-protocol` | Forensic refinement gate | `.opencode/skills/sovereign-refinement-protocol/` |
| `omega-doc-architect` | Document management | `.opencode/skills/omega-doc-architect/` |

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via AnyIO |
| **M2 Firewall** | Skills are OpenCode-native; no engine deps |
| **M7 Local-First** | Uses local agents (maat, lilith, roc_racoon) |
| **M11 Soul Integrity** | Gnosis extraction feeds soul distillation |
| **M13 Temple-Grade** | Structured pipeline with validation gates |
| **M23 Failure Integrity** | Stage failures halt pipeline; explicit errors |

---

## Testing

```bash
pytest tests/test_opencode_client.py tests/test_meditation_pipeline.py -v
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SKILLS-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

