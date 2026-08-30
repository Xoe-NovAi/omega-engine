# 🔱 Omega Engine — Background Researcher Worker (Jem Phase 1)
# AP: AP-BACKGROUND-RESEARCHER-v2.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ jem ⬡ background_researcher ⬡ PHASE-1
#
# Autonomous, sovereign research worker that deepens, verifies, and expands
# the Omega Engine's knowledge base. Runs as a systemd timer every 15 min.
#
# Architecture (Jem 3-Tier):
#   [IDLE] → [TRIAGE] → [SEARCH] → [EXTRACT] → [JEM PIPELINE] → [UPDATE] → [IDLE]
#     │          │           │           │       ┌────────────┐       │
#     ▼          ▼           ▼           ▼       │ T1: lmster │       ▼
#   skip,     Qwen3-1.7B  SearXNG     Firecrawl  │ T2: MiniMax│    soul.yaml
#   defer     triage      + fleet     + Jina      │ T3: Gemini │    + docs/
#                                                 └────────────┘
# Every cycle produces a synthetic training triple (T1, T2, T3).

from .loop import BackgroundResearcherLoop
from .models import ResearchTask, TriageResult, GnosisPacket
from .distiller import (
    Distiller,
    JemCircuitBreaker,
    CircuitBreakerState,
    LmsterBackend,
    T2Backend,
    T3Backend,
    TrainingTripleSaver,
    list_prompt_modes,
)

__all__ = [
    "BackgroundResearcherLoop",
    "ResearchTask",
    "TriageResult",
    "GnosisPacket",
    "Distiller",
    "JemCircuitBreaker",
    "CircuitBreakerState",
    "LmsterBackend",
    "T2Backend",
    "T3Backend",
    "TrainingTripleSaver",
    "list_prompt_modes",
]
