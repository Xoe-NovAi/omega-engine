# 🔱 omega-vetala — Policy Framework
# ⬡ OMEGA ⬡ P10-VALIDATION ⬡ POLICY-FRAMEWORK
#
# AP Token: AP-MODERATION-P10-v1.0.0
"""Policy framework for content moderation thresholds and actions.

Policies define *what* moderation actions to take based on provider
confidence scores and flag status.  They are configurable via YAML,
enabling non-developers to tune moderation behaviour without code changes.

No policy contains static slur lists — all detection is delegated to
the provider chain.
"""

from __future__ import annotations

from omega_vetala.policies.loader import PolicyLoader
from omega_vetala.policies.policy import (
    Action,
    ModerationPolicy,
    PolicyRule,
    resolve_action,
)

__all__ = [
    "ModerationPolicy",
    "PolicyRule",
    "Action",
    "PolicyLoader",
    "resolve_action",
]
