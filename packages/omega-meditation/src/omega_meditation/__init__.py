"""
⬡ OMEGA MEDITATION — Autonomous Meditation Pipeline
Fully autonomous Problem → Prompt Crafting → Meditation → Synthesis → Research → Grounded Update → Gnosis → Integration

Every output recorded to disk as mineable datapoints.
"""

from .pipeline import (
    AutonomousMeditationPipeline,
    create_pipeline_opencode,
    create_pipeline_cli,
    create_pipeline_standalone,
)

__version__ = "1.0.0"
__all__ = [
    "AutonomousMeditationPipeline",
    "create_pipeline_opencode",
    "create_pipeline_cli",
    "create_pipeline_standalone",
]