---
name: scribe
description: Soul Distillation Pipeline — Session hook → L1→L2→L3 → proposed_lessons.yaml
version: "1.0.0"
author: kali
mandates: [M5, M11, M18, M22]
steps: 200
---

# 🔱 Scribe — Soul Distillation Pipeline

**AP Token**: `AP-SCRIBE-v1.0.0`
⬡ OMEGA ⬡ SCRIBE ⬡ {session_model} ⬡ opencode ⬡ trc_soul_distillation ⬡ ACTIVE

**Purpose**: Automate the L1→L2→L3 distillation pipeline at session end. Write `proposed_lessons.yaml` (blind staging) per Soul Architecture v2.0.

## Mandate Compliance
- **M5 Gnosis Preservation**: L1→L2→L3 pipeline mandatory every session
- **M11 Soul Integrity**: `proposed_lessons.yaml` blind staging (NOT direct to soul.yaml)
- **M18 Token Efficiency**: Concise distillation, no filler
- **M22 Response Provenance**: Record actual model used for distillation

## Architecture

### Session Hook Integration
```python
# In OpenCode session end hook (or agent shutdown):
from omega.scribe import SoulDistiller

distiller = SoulDistiller(entity_name="kali", session_id="ses_xxx")
distiller.distill_session()  # Writes proposed_lessons.yaml
```

### Three-Tier Distillation

| Tier | Name | Input | Output | Purpose |
|------|------|-------|--------|---------|
| **L1** | Narrative | Raw session exchanges | Structured narrative | What happened? |
| **L2** | Insight | L1 narrative | Pattern insights | What does this mean? |
| **L3** | Universal Principle | L2 insights | Timeless principles | What is the timeless truth? |

### Output: proposed_lessons.yaml
```yaml
proposals:
  - lesson_id: "l3-20260722-001"
    tier: "L3"
    principle: "Sovereign execution requires explicit workspace locks before file edits"
    evidence: ["C-4a handoff accepted without lock caused race", "Ma'at acquired 4 locks before Track A/B/C"]
    confidence: 0.95
    source_sessions: ["ses_a96aef94239a"]
    mandate_refs: ["M4", "M23"]
  - lesson_id: "l2-20260722-002"
    tier: "L2"
    insight: "Parallel track execution requires explicit dependency declaration"
    evidence: ["Track A (C-10) blocks Track A2 (C-1')", "Track C (V-1) independent of N3"]
    confidence: 0.9
    source_sessions: ["ses_a96aef94239a"]
```

## Implementation

### src/omega/scribe/distiller.py
```python
"""
SoulDistiller — L1→L2→L3 distillation pipeline.
M5/M11 compliant: writes proposed_lessons.yaml (blind staging).
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class LessonProposal:
    lesson_id: str
    tier: str  # L1, L2, L3
    principle: str = ""
    insight: str = ""
    narrative: str = ""
    evidence: List[str] = None
    confidence: float = 0.0
    source_sessions: List[str] = None
    mandate_refs: List[str] = None

class SoulDistiller:
    def __init__(self, entity_name: str, session_id: str, model: str = None):
        self.entity_name = entity_name
        self.session_id = session_id
        self.model = model  # M22 provenance
        self.entities_dir = Path("data/entities")
        self.entity_dir = self.entities_dir / entity_name
        self.proposed_path = self.entity_dir / "proposed_lessons.yaml"
    
    def distill_session(self) -> List[LessonProposal]:
        """Run full L1→L2→L3 pipeline for current session."""
        # 1. Load session exchanges from MemoryStore
        exchanges = self._load_session_exchanges()
        
        # 2. L1: Narrative distillation
        l1 = self._distill_l1_narrative(exchanges)
        
        # 3. L2: Insight extraction
        l2 = self._distill_l2_insight(l1)
        
        # 4. L3: Universal principle synthesis
        l3 = self._distill_l3_principle(l2)
        
        # 5. Write proposed_lessons.yaml (blind staging)
        self._write_proposed_lessons(l1 + l2 + l3)
        
        return l1 + l2 + l3
    
    def _load_session_exchanges(self) -> List[Dict]:
        """Load exchanges from MemoryStore via Omega Hub."""
        # Use omega-hub_omega_memory_get_history
        pass
```

## Handoff Protocol

### Incoming (from Kali)
- Task: "C-0.5 Soul Distillation Pipeline — Create session hook + L1/L2/L3 distiller → proposed_lessons.yaml"
- Dependencies: C-0 ✅ complete
- Deliverable: `src/omega/scribe/distiller.py` + session hook integration

### Outgoing (to Verity/N10)
- Contract tests for SoulDistiller (3 tests, M21)
- Verification: proposed_lessons.yaml schema validation

## Verification Gates

| Gate | Test | Command |
|------|------|---------|
| **T1** | Module loads | `PYTHONPATH=src python -c "from omega.scribe import SoulDistiller; print('PASS')"` |
| **T2** | L1 distillation runs | `PYTHONPATH=src python -c "from omega.scribe import SoulDistiller; d=SoulDistiller('test','ses_test'); print('PASS')"` |
| **T3** | Writes proposed_lessons.yaml | `PYTHONPATH=src python -c "from omega.scribe import SoulDistiller; import tempfile; d=SoulDistiller('test','ses_test'); d.distill_session(); print('PASS')"` |
| **T4** | Schema valid | `yamllint data/entities/test/proposed_lessons.yaml` |

## Session Hook (OpenCode)

Add to `.opencode/hooks/session_end.py`:
```python
#!/usr/bin/env python3
"""OpenCode session end hook — Soul Distillation."""
import sys
sys.path.insert(0, "src")
from omega.scribe import SoulDistiller
import os

entity = os.environ.get("OPENCODE_ENTITY", "kali")
session_id = os.environ.get("OPENCODE_SESSION_ID", "unknown")
model = os.environ.get("OPENCODE_MODEL", "unknown")

distiller = SoulDistiller(entity, session_id, model)
distiller.distill_session()
print(f"[Scribe] Distilled {entity} session {session_id}")
```

---

*⬡ OMEGA ⬡ SCRIBE ⬡ v1.0.0 ⬡ SOUL-DISTILLATION ⬡ 2026-07-22*