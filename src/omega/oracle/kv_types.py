# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Canonical ggml KV-cache type mapping (B3 single-source fix).

Every module that needs to translate a string KV-cache type (e.g. ``"q8_0"``,
``"f16"``) into the integer ``ggml_type`` value expected by
``llama_cpp.Llama(type_k=..., type_v=...)`` MUST import from here instead of
defining its own map.

Canonical values are taken from the pinned llama-cpp-python binding's
``GGML_TYPE_*`` constants (verified 2026-08-07 against llama-cpp-python
0.3.32 / ggml.h).  Prior to this module, ``providers.py`` and
``model_gateway.py`` each defined their own partial maps and they disagreed
(e.g. ``q4_0`` was 4 in one and 2 in the other; the binding says 2).

    GGML_TYPE_F32  = 0
    GGML_TYPE_F16  = 1
    GGML_TYPE_Q4_0 = 2
    GGML_TYPE_Q5_0 = 6
    GGML_TYPE_Q8_0 = 8
    GGML_TYPE_Q6_K = 14
"""

from __future__ import annotations

from typing import Dict, Optional

# Canonical map: user-facing string → ggml_type integer.
# Values match llama_cpp.GGML_TYPE_* exactly (see module docstring).
# NOTE: q6_0 does NOT exist in ggml; the 6-bit cache type is Q6_K (=14).
# The map below intentionally omits removed types (Q4_2=4, Q4_3=5) that would
# have been accepted by the old providers.py map but crash the C backend.
KV_TYPE_MAP: Dict[str, int] = {
    "f32": 0,  # GGML_TYPE_F32
    "f16": 1,  # GGML_TYPE_F16
    "q4_0": 2,  # GGML_TYPE_Q4_0
    "q5_0": 6,  # GGML_TYPE_Q5_0 (NOT 5 — 4/5 were removed types)
    "q8_0": 8,  # GGML_TYPE_Q8_0
    "q6_k": 14,  # GGML_TYPE_Q6_K
    "q8_k": 15,  # GGML_TYPE_Q8_K
}


def kv_type_int(name: Optional[str], default: int = 8) -> int:
    """Resolve a KV-cache type name to its ggml_type integer.

    Args:
        name: User-facing type name (e.g. ``"q8_0"``, ``"f16"``).  Case- and
            whitespace-insensitive.  ``None`` or unknown names return
            ``default``.
        default: Integer returned when name is missing/unknown
            (default 8 = q8_0).

    Returns:
        The canonical ggml_type integer for the given name.
    """
    if name is None:
        return default
    key = str(name).strip().lower()
    return KV_TYPE_MAP.get(key, default)
