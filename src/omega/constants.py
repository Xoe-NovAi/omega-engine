"""Shared constants for Omega Engine.

Heritage: The ZONEID magic constants derive from id Software's ZONEID pattern
([ZONEID Pattern: id Software 1993, unchanged 1996]). The original constant
0x1d4a11 was embedded in every allocated memory block and verified on every
access — it caught use-after-free, double-free, and uninitialized memory bugs
at zero runtime cost. See :doc:`/docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md`
§R-19 for full analysis.
"""

DEFAULT_CONTEXT_LIMIT = 6
MAX_HISTORY_EXCHANGES = 20

# ── id Software Heritage: ZONEID Magic Constants ─────────────────────────
# Source: DOOM 1993 linuxdoom-1.10/z_zone.c:33, Quake 1996 WinQuake/zone.c:24
# Pattern: Embed in every significant data structure; validate on every access.
# Python adaptation: Magic constant lives in dataclass/instance, checked on
# critical operations (load, save, state transition). Catches serialization
# corruption, stale references, and wrong-type-wrong-place bugs.
#
# The 0x1d4a prefix is the original id Software magic. Suffixes (11-15)
# identify the subsystem. 0xDEAD_ENTITY is the tombstone sentinel for lazy
# deletion (R-20).

# [id-soft: doom-1993] ZONEID Pattern — MemoryStore entry validation
ZONEID_MEMORY = 0x1d4a11

# [id-soft: doom-1993] ZONEID Pattern — EntityRegistry entity validation
ZONEID_ENTITY = 0x1d4a12

# [id-soft: doom-1993] ZONEID Pattern — circuit breaker state marker
ZONEID_BREAKER = 0x1d4a13

# [id-soft: doom-1993] ZONEID Pattern — trace/session lineage marker
ZONEID_TRACE = 0x1d4a14

# [id-soft: doom-1993] ZONEID Pattern — ResourceGuard critical section guard
ZONEID_PROBE = 0x1d4a15

# ── Tombstone Sentinel (Lazy Deletion) ────────────────────────────────────
# [id-soft: doom-1993] Lazy Deletion — sentinel marker for P_RemoveThinker
# Derived from DOOM 1993 p_tick.c:62-103: P_RemoveThinker marks thinkers
# with sentinel function pointer (-1) instead of freeing immediately.
# Combined with [id-soft: quake-1996] Grace Period (0.5s realloc delay).
#
# Python: An entity with ZONEID_TOMBSTONE has been deregistered but not yet
# reaped. Callers that hold stale references can detect the tombstone and
# raise EntityTombstonedError instead of silently getting wrong data.
# [id-soft: doom-1993] Lazy Deletion — sentinel value for tombstoned entities
# 0xDEADBEEF is the canonical sentinel hex pattern used since the 1980s
# on IBM RS/6000, Motorola 68000, and id Software's DOOM engine.
ZONEID_TOMBSTONE = 0xDEADBEEF

# ── ZONEID Validation Helper ──────────────────────────────────────────────

def validate_zoneid(value: int, expected: int, context: str = "") -> None:
    """Validate a ZONEID magic constant.

    [id-soft: doom-1993] ZONEID Pattern — runtime integrity check
    Direct translation of id Software's z_magic/ZONEID check.
    In C, this was ``if (block->z_magic != ZONEID)`` — a 4-byte comparison
    that caught 90% of memory corruptions.

    Args:
        value: The magic constant found on the object.
        expected: The expected magic constant.
        context: Optional description for error messages (e.g., "EntityRegistry.get").

    Raises:
        ValueError: If the magic constants don't match.
    """
    if value != expected:
        ctx = f" in {context}" if context else ""
        raise ValueError(
            f"ZONEID mismatch{ctx}: expected 0x{expected:08x}, got 0x{value:08x}. "
            f"Possible data corruption, stale reference, or wrong-type load. "
            f"See ZONEID constants in omega.constants"
        )

# ── Predefined ZONEID Constants Table ─────────────────────────────────────
# cvar-style table of all known ZONEID constants (see R-22 cvar table pattern).
ZONEID_TABLE = {
    "memory": {"id": ZONEID_MEMORY, "subsystem": "MemoryStore", "description": "Memory load/save integrity"},
    "entity": {"id": ZONEID_ENTITY, "subsystem": "EntityRegistry", "description": "Entity dataclass validation"},
    "breaker": {"id": ZONEID_BREAKER, "subsystem": "HealthMonitor", "description": "Circuit breaker state marker"},
    "trace": {"id": ZONEID_TRACE, "subsystem": "ObservabilityEngine", "description": "Trace/session lineage"},
    "probe": {"id": ZONEID_PROBE, "subsystem": "ResourceGuard", "description": "Critical section guard"},
    "tombstone": {"id": ZONEID_TOMBSTONE, "subsystem": "EntityRegistry", "description": "Lazy deletion sentinel"},
}
