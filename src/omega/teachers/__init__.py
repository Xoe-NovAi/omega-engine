# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Engine Teacher Modules — DPO Pair Generation and Model Distillation.

AP: AP-TEACHERS-v1.0.0
⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_teacher_pipeline ⬡ ACTIVE

This package contains teacher pipelines for generating DPO training pairs
using frontier models as teachers to improve local model performance.
"""

from omega.teachers.nemotron_pipeline import NemotronTeacherPipeline, DPOPair

__all__ = ["NemotronTeacherPipeline", "DPOPair"]
