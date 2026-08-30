# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-SECURITY-v1.0.0
# 🔱 Omega Engine — Security Package
# ⬡ OMEGA ⬡ SECURITY ⬡ v1.0.0 ⬡ 2026-08-07
"""Sovereign Security Layer — Tainted Data Protocol (TDP) Extension.

Provides transitive taint propagation rules for the existing TDP system
in omega.oracle.security. This module extends the basic taint wrapping
with full propagation tracking across the data lifecycle:

    read → session → writes → retrieval

Taint levels:
    CLEAN       — Internal, trusted data
    LOW         — External but verified (e.g., GitHub Xoe-NovAi)
    MEDIUM      — External unverified (e.g., web search results)
    HIGH        — External untrusted (e.g., arbitrary URLs)
    CONTAMINATED — Data that has mixed with HIGH/CONTAMINATED sources

Integration:
    - Ingestion: SovereignIngestionPipeline tags documents with taint levels
    - Session: Taint propagates from ingested data to session state
    - Writes: Tainted data written to memory blocks carries taint forward
    - Retrieval: Taint-aware retrieval filters or flags results

[M7 Local-First] All taint computation is local — no cloud API calls.
"""

from .taint import (
    TaintLevel,
    TaintSource,
    TaintRecord,
    TaintPropagation,
    TaintAwareIngestion,
    TaintAwareMemory,
    create_taint_propagation,
)

__all__ = [
    "TaintLevel",
    "TaintSource",
    "TaintRecord",
    "TaintPropagation",
    "TaintAwareIngestion",
    "TaintAwareMemory",
    "create_taint_propagation",
]
