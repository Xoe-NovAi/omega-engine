# 🔱 omega-vetala — Content Moderation Engine
# ⬡ OMEGA ⬡ P6-MODELGATE ⬡ PROVIDER-FABRIC
#
# AP Token: AP-MODERATION-P6-v1.0.0
"""omega-vetala: ML-driven content moderation with provider failover chain.

All detection uses ML models, pattern analysis, or third-party APIs.
No static slur lists are used anywhere in this package.
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Omega Engine — P6 ModelGate / Cognition Pillar"
__description__ = "ML-driven content moderation with multi-provider failover"

from omega_vetala.providers.base import ModerationResult, ModelProvider

__all__ = [
    "ModerationResult",
    "ModelProvider",
]
