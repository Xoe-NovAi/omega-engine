# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Privacy Module — CPE Scoring & Local Privacy Kernel
AP: AP-PRIVACY-v1.0.0
⬡ OMEGA ⬡ P3/P6 ⬡ privacy ⬡ CAMP-CLOAKBOT
"""

from omega.privacy.cpe_scorer import (
    CPESession,
    CPEAction,
    PIIEntity,
    CPEResult,
    create_cpe_session,
)
from omega.privacy.kernel import (
    PrivacyKernel,
    PrivacyHooks,
    PrivacyVault,
    DetectionResult,
    create_privacy_kernel,
    create_privacy_hooks,
)

__all__ = [
    # CPE Scorer
    "CPESession",
    "CPEAction",
    "PIIEntity",
    "CPEResult",
    "create_cpe_session",
    # Privacy Kernel
    "PrivacyKernel",
    "PrivacyHooks",
    "PrivacyVault",
    "DetectionResult",
    "create_privacy_kernel",
    "create_privacy_hooks",
]
