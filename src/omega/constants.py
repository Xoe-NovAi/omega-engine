# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PR-READINESS-v1.0.0
"""Shared constants for Omega Engine.

⚠️ NOTICE: All constants have moved to ``omega.cvar_table``.
This module is now a backward-compatible re-export layer.
New code should import from ``omega.cvar_table`` directly.

The unified cvar table provides typed CvarDef entries, modification tracking,
and a single source of truth for ALL engine configuration:
  - ``zoneid.*`` namespace: Magic constants (from id Software ZONEID pattern)
  - ``config.*`` namespace: User-tunable knobs (YAML-backed, hot-reloadable)

See ``omega.cvar_table.cvar_get()``, ``cvar_set()``, ``cvar_namespace()``.

Heritage:
    [id-soft: vet-015] ZONEID Pattern — magic constants re-export from cvar_table
    [id-soft: vet-016] Cvar System — cvar table unified module entry point
"""
# DocRef: docs/standards/DOC_STYLE_GUIDE.md

# ── Local constants (NOT in cvar table — session/config values) ─────
# These are simple Python constants, not tunable engine parameters.
# They remain here for backward compatibility with memory_store.py etc.
DEFAULT_CONTEXT_LIMIT = 6
MAX_HISTORY_EXCHANGES = 20


# ── All other exports moved to omega.cvar_table ─────────────────
# Re-export everything for backward compatibility.
from omega.cvar_table import (
    # ZONEID constants
    ZONEID_MEMORY,
    ZONEID_ENTITY,
    ZONEID_BREAKER,
    ZONEID_TRACE,
    ZONEID_PROBE,
    ZONEID_HANDOFF,
    ZONEID_PRESENCE,
    ZONEID_KNOWLEDGE,
    ZONEID_DEMAND,
    ZONEID_VERIFICATION,
    ZONEID_ATOMIC,
    ZONEID_EMBEDDING,
    ZONEID_TOMBSTONE,
    # Validation
    validate_zoneid,
    # Tables
    ZONEID_TABLE,
    CVAR_TABLE,
    # Access helpers
    CvarDef,
    cvar_get,
    cvar_set,
    cvar_namespace,
    cvar_modification_count,
    cvar_by_subsystem,
    cvar_list,
    cvar_summary,
    # Kwarg validation (port 1.1)
    validate_llama_kwargs,
    LLAMA_CPP_VALID_KWARGS,
)

__all__ = [
    "ZONEID_MEMORY", "ZONEID_ENTITY", "ZONEID_BREAKER",
    "ZONEID_TRACE", "ZONEID_PROBE",
    "ZONEID_HANDOFF", "ZONEID_PRESENCE",
    "ZONEID_KNOWLEDGE",     "ZONEID_DEMAND",
    "ZONEID_VERIFICATION",
    "ZONEID_EMBEDDING",
    "ZONEID_TOMBSTONE",
    "validate_zoneid",
    "ZONEID_TABLE", "CVAR_TABLE",
    "CvarDef",
    "cvar_get", "cvar_set", "cvar_namespace",
    "cvar_modification_count", "cvar_by_subsystem",
    "cvar_list", "cvar_summary",
    "validate_llama_kwargs", "LLAMA_CPP_VALID_KWARGS",
]
