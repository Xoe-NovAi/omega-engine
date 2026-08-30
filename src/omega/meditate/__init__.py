# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Meditate Protocol
# ⬡ OMEGA ⬡ MEDITATE ⬡ trc_meditate_protocol
# Single-inference, multi-persona semantic prism
# D-265: Portability-first, zero-dep core
# M2 COMPLIANT: Entity names loaded from WAD YAML, not hardcoded

from src.omega.meditate.protocol import (
    PersonaSpec,
    MeditationSpec,
    MeditationResult,
    AntiCollapseLaw,
    MeditatePhase,
    PersonaLibrary,
    DissentStyle,
    OutputMode,
    get_default_lenses,
)
from src.omega.meditate.lens_registry import (
    load_lens_library,
    load_all_lenses,
    load_lens_by_id,
    get_lenses_config_path,
)

__all__ = [
    "PersonaSpec",
    "MeditationSpec",
    "MeditationResult",
    "AntiCollapseLaw",
    "MeditatePhase",
    "PersonaLibrary",
    "DissentStyle",
    "OutputMode",
    "get_default_lenses",
    "load_lens_library",
    "load_all_lenses",
    "load_lens_by_id",
    "get_lenses_config_path",
]
