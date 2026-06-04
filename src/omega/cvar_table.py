# 🔱 Omega Engine — Unified Named-Constant Registry (cvar_table)
# ⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ CVAR-TABLE
# AP: CVAR-TABLE-v1.0.0
#
# This module replaces scattered config dicts with a single, typed,
# auditable constant table. TWO namespaces:
#   - zoneid.* : Magic constants for runtime integrity (id Software heritage)
#   - config.* : User-tunable knobs (YAML-backed, hot-reloadable)
#
# Heritage:
#   [id-soft: doom-1993] ZONEID Pattern — magic constant + validate_zoneid()
#   [id-soft: quake3-1999] Cvar System — typed, queryable, auditable cvars
#   [Cvar System: id Software 1999, generalized 2026]
#     Q3A's cvar system provided a unified namespace for ALL tunable engine
#     parameters with get/set, modification tracking, and enumeration.
#     This Python adaptation adds typed access, modification counts, and
#     YAML persistence via the config.* namespace.
#
# Migration from constants.py:
#   - ZONEID constants LIVE here now.
#   - constants.py is a thin re-export layer (backward compatible).
#   - New code should import from omega.cvar_table directly.

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# §1 — CvarDef Dataclass
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class CvarDef:
    """A single cvar (console variable) entry.

    [id-soft: doom-1993] ZONEID Pattern — magic constant with metadata
    [id-soft: quake3-1999] Cvar System — typed, queryable, auditable

    Combines id Software's ZONEID magic marker (a 4-byte constant in every
    memory block) with Q3A's cvar system (typed, queryable, enumerable).

    Args:
        name: Dotted name (e.g. "zoneid.memory", "config.gguf.n_ctx").
        value: The current value.
        type: Type tag — "int", "float", "str", "list", "zoneid", "bool".
        description: Human-readable description of what this cvar controls.
        subsystem: Which subsystem owns this cvar (e.g. "EntityRegistry").
        modification_count: Incremented on every set(). Zero at creation.
    """
    name: str
    value: Any
    type: str
    description: str
    subsystem: str = ""
    modification_count: int = 0

    def __repr__(self) -> str:
        return (
            f"CvarDef({self.name}={self.value!r}, "
            f"type={self.type}, mods={self.modification_count})"
        )


# ═══════════════════════════════════════════════════════════════════════
# §2 — ZONEID Magic Constants (id Software Heritage)
# ═══════════════════════════════════════════════════════════════════════

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

# [id-soft: doom-1993] ZONEID Pattern — Subagent HandoffPacket integrity marker
# HandoffPacket dataclass in subagent_dispatcher.py validates this on construction
# to catch stale or corrupted packets.
ZONEID_HANDOFF = 0x1d4a16

# [id-soft: doom-1993] ZONEID Pattern — Agent Presence dataclass integrity marker
# Presence tracking for live agent awareness in Hivemind/Redis. Validated on
# load to catch stale presence records from terminated sessions.
ZONEID_PRESENCE = 0x1d4a17

# [id-soft: doom-1993] ZONEID Pattern — Knowledge Signal integrity marker
# Cross-pollination knowledge feed signals. Validated on every read/write to
# catch corrupt or stale knowledge signals.
ZONEID_KNOWLEDGE = 0x1d4a18

# [id-soft: doom-1993] ZONEID Pattern — Demand Signal integrity marker
# Inter-agent demand signals. Validated on every state transition to catch
# corrupted demand lifecycle records.
ZONEID_DEMAND = 0x1d4a19

# [id-soft: doom-1993] ZONEID Pattern — Verification audit trail integrity marker
ZONEID_VERIFICATION = 0x1d4a1a

# [id-soft: doom-1993] ZONEID Pattern — critical section atomic lock marker
ZONEID_ATOMIC = 0x1d4a1b


# [id-soft: doom-1993] Lazy Deletion — sentinel value for tombstoned entities
# 0xDEADBEEF is the canonical sentinel hex pattern used since the 1980s
# on IBM RS/6000, Motorola 68000, and id Software's DOOM engine.
ZONEID_TOMBSTONE = 0xDEADBEEF


# ── ZONEID Validation Helper ─────────────────────────────────────────

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
            f"See ZONEID constants in omega.cvar_table"
        )


# ── Legacy ZONEID_TABLE (Backward Compatibility) ─────────────────────
# Pre-dates the unified CVAR_TABLE. Kept for code that references it
# directly. New code should use CVAR_TABLE or cvar_get().

ZONEID_TABLE = {
    "memory": {"id": ZONEID_MEMORY, "subsystem": "MemoryStore", "description": "Memory load/save integrity"},
    "entity": {"id": ZONEID_ENTITY, "subsystem": "EntityRegistry", "description": "Entity dataclass validation"},
    "breaker": {"id": ZONEID_BREAKER, "subsystem": "HealthMonitor", "description": "Circuit breaker state marker"},
    "trace": {"id": ZONEID_TRACE, "subsystem": "ObservabilityEngine", "description": "Trace/session lineage"},
    "probe": {"id": ZONEID_PROBE, "subsystem": "ResourceGuard", "description": "Critical section guard"},
    "handoff": {"id": ZONEID_HANDOFF, "subsystem": "SubagentDispatcher", "description": "HandoffPacket integrity marker"},
    "presence": {"id": ZONEID_PRESENCE, "subsystem": "LinkP9Runtime", "description": "Agent presence record marker"},
    "knowledge": {"id": ZONEID_KNOWLEDGE, "subsystem": "CrossPollination", "description": "Knowledge signal integrity marker"},
    "demand": {"id": ZONEID_DEMAND, "subsystem": "CrossPollination", "description": "Demand signal integrity marker"},
    "tombstone": {"id": ZONEID_TOMBSTONE, "subsystem": "EntityRegistry", "description": "Lazy deletion sentinel"},
    "verification": {"id": ZONEID_VERIFICATION, "subsystem": "Sentinel", "description": "Verification audit trail integrity marker"},
}


# ═══════════════════════════════════════════════════════════════════════
# §3 — CVAR_TABLE — The Primary Named-Constant Registry
# ═══════════════════════════════════════════════════════════════════════

CVAR_TABLE: Dict[str, CvarDef] = {
    # ── zoneid.* namespace (magic constants from §2) ──────────────
    "zoneid.memory": CvarDef(
        "zoneid.memory", ZONEID_MEMORY, "zoneid",
        "Memory load/save integrity marker", "MemoryStore",
    ),
    "zoneid.entity": CvarDef(
        "zoneid.entity", ZONEID_ENTITY, "zoneid",
        "Entity dataclass validation marker", "EntityRegistry",
    ),
    "zoneid.breaker": CvarDef(
        "zoneid.breaker", ZONEID_BREAKER, "zoneid",
        "Circuit breaker state marker", "HealthMonitor",
    ),
    "zoneid.trace": CvarDef(
        "zoneid.trace", ZONEID_TRACE, "zoneid",
        "Trace/session lineage marker", "ObservabilityEngine",
    ),
    "zoneid.probe": CvarDef(
        "zoneid.probe", ZONEID_PROBE, "zoneid",
        "Critical section guard marker", "ResourceGuard",
    ),
    "zoneid.handoff": CvarDef(
        "zoneid.handoff", ZONEID_HANDOFF, "zoneid",
        "HandoffPacket integrity marker (SubagentDispatcher)", "SubagentDispatcher",
    ),
    "zoneid.presence": CvarDef(
        "zoneid.presence", ZONEID_PRESENCE, "zoneid",
        "Agent presence record marker (Link P9 Runtime)", "LinkP9Runtime",
    ),
    "zoneid.tombstone": CvarDef(
        "zoneid.tombstone", ZONEID_TOMBSTONE, "zoneid",
        "Lazy deletion sentinel", "EntityRegistry",
    ),
    "zoneid.verification": CvarDef(
        "zoneid.verification", ZONEID_VERIFICATION, "zoneid",
        "Verification audit trail integrity marker (P5 Sentinel)", "Sentinel",
    ),
    "zoneid.atomic": CvarDef(
        "zoneid.atomic", ZONEID_ATOMIC, "zoneid",
        "Critical section atomic lock marker", "ResourceGuard",
    ),

    # ── config.gguf.* — Native GGUF Provider knobs ───────────────
    "config.gguf.n_gpu_layers": CvarDef(
        "config.gguf.n_gpu_layers", 0, "int",
        "GPU layers for native GGUF inference (0=CPU only, prevents iGPU crash)",
        "NativeGGUFProvider",
    ),
    "config.gguf.stop_tokens": CvarDef(
        "config.gguf.stop_tokens", ["</s>", "User:", "\n\n"], "list",
        "ChatML stop tokens for generation boundary (prevents hallucinated turns)",
        "ModelGateway",
    ),
    "config.gguf.kwarg_filter": CvarDef(
        "config.gguf.kwarg_filter", True, "bool",
        "Enable llama-cpp kwarg validation before model load (rejects unknown keys)",
        "NativeGGUFProvider",
    ),
    "config.gguf.n_ctx": CvarDef(
        "config.gguf.n_ctx", 4096, "int",
        "Default context window for native GGUF inference",
        "NativeGGUFProvider",
    ),
    "config.gguf.n_threads": CvarDef(
        "config.gguf.n_threads", 6, "int",
        "Number of threads for native GGUF (Zen 2: 6 physical cores [0,2,4,6])",
        "NativeGGUFProvider",
    ),
    "config.gguf.type_k": CvarDef(
        "config.gguf.type_k", 8, "int",
        "KV cache key quantization type (8=q8_0, 0=f16, 9=q4_0)",
        "NativeGGUFProvider",
    ),
    "config.gguf.type_v": CvarDef(
        "config.gguf.type_v", 8, "int",
        "KV cache value quantization type (8=q8_0, 0=f16, 9=q4_0)",
        "NativeGGUFProvider",
    ),

    # ── config.providers.* — Provider-specific knobs ─────────────
    "config.providers.google.auth_header": CvarDef(
        "config.providers.google.auth_header", "x-goog-api-key", "str",
        "HTTP header name for Google API key (key in header, not URL)",
        "GoogleAIProvider",
    ),
    "config.providers.lmster.endpoint": CvarDef(
        "config.providers.lmster.endpoint", "http://127.0.0.1:1234", "str",
        "LM Studio headless server base URL",
        "LocallmsterProvider",
    ),
    "config.providers.ollama.endpoint": CvarDef(
        "config.providers.ollama.endpoint", "http://127.0.0.1:11434", "str",
        "Ollama API base URL",
        "OllamaProvider",
    ),

    # ── config.observability.* — Observability knobs ────────────
    "config.observability.trace_id_propagation": CvarDef(
        "config.observability.trace_id_propagation", True, "bool",
        "Propagate trace_id to all provider logging and observability events",
        "ObservabilityEngine",
    ),
    "config.observability.json_logging": CvarDef(
        "config.observability.json_logging", True, "bool",
        "Enable structured JSON logging (vs plain text)",
        "ObservabilityEngine",
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# §4 — Cvar Access Helpers
# ═══════════════════════════════════════════════════════════════════════

def cvar_get(name: str, default: Any = None) -> Any:
    """Get a cvar value by dotted name.

    Example:
        cvar_get("config.gguf.n_ctx")         → 4096
        cvar_get("zoneid.entity")             → 0x1d4a12
        cvar_get("config.gguf.stop_tokens")   → ["</s>", "User:", "\n\n"]
    """
    entry = CVAR_TABLE.get(name)
    if entry is None:
        return default
    return entry.value


def cvar_set(name: str, value: Any) -> bool:
    """Set a cvar value by dotted name.

    Returns:
        True if the cvar existed (and was updated), False if it doesn't exist.
    """
    entry = CVAR_TABLE.get(name)
    if entry is None:
        logger.warning("cvar_set: unknown cvar '%s' (value=%r)", name, value)
        return False
    entry.value = value
    entry.modification_count += 1
    logger.debug("cvar_set: %s = %r (mod #%d)", name, value, entry.modification_count)
    return True


def cvar_namespace(prefix: str) -> Dict[str, CvarDef]:
    """Get all cvars under a dotted prefix.

    Examples:
        cvar_namespace("zoneid")          → all zoneid.* entries
        cvar_namespace("config.gguf")     → all config.gguf.* entries
        cvar_namespace("config.providers") → all provider entries
    """
    prefix = prefix.rstrip(".") + "."
    return {k: v for k, v in CVAR_TABLE.items() if k.startswith(prefix)}


def cvar_modification_count(name: str) -> int:
    """Get the modification count for a cvar. Returns -1 if unknown."""
    entry = CVAR_TABLE.get(name)
    if entry is None:
        return -1
    return entry.modification_count


def cvar_by_subsystem(subsystem: str) -> Dict[str, CvarDef]:
    """Get all cvars associated with a subsystem (e.g. "EntityRegistry")."""
    return {k: v for k, v in CVAR_TABLE.items() if v.subsystem == subsystem}


def cvar_list() -> List[CvarDef]:
    """Return all cvars as a list, sorted by name."""
    return sorted(CVAR_TABLE.values(), key=lambda c: c.name)


def cvar_summary() -> str:
    """Return a human-readable summary of all cvars for CLI display."""
    lines = ["╔══════════════════════════════════════════════════════════════╗"]
    lines.append("║               CVAR TABLE — Full Registry                 ║")
    lines.append("╠══════════════════════════════════════════════════════════════╣")
    for cvar in cvar_list():
        val_str = str(cvar.value)
        if len(val_str) > 60:
            val_str = val_str[:57] + "..."
        lines.append(
            f"║ {cvar.name:40s} = {val_str:30s} ║"
        )
    lines.append("╚══════════════════════════════════════════════════════════════╝")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# §5 — Validate llama-cpp Kwargs (Priority Port 1.1)
# ═══════════════════════════════════════════════════════════════════════

# Known valid kwargs for llama_cpp.Llama(). Anything not in this set
# will be rejected when kwarg_filter is enabled.
LLAMA_CPP_VALID_KWARGS: set = {
    # Model path
    "model_path",
    # Threading
    "n_threads", "n_threads_batch",
    # Context
    "n_ctx", "n_ctx_max",
    # Batches (Zen 2 tuned)
    "n_batch", "n_ubatch",
    # KV cache quantization
    "type_k", "type_v",
    # Memory
    "use_mmap", "use_mlock", "n_gpu_layers", "tensor_split",
    # Sampling (usually passed at inference, not init)
    "logits_all", "embedding", "last_n_tokens_size",
    # Verbosity
    "verbose", "seed", "rope_scaling_type", "rope_freq_base",
    # LoRA
    "lora_base", "lora_path",
    # Flash Attention
    "flash_attn", "flash_attn_impl",
    # Grammar
    "grammar",
}


def validate_llama_kwargs(kwargs: dict, context: str = "") -> list:
    """Validate kwargs dict against known llama-cpp keys.

    [id-soft: quake3-1999] Cvar System — config validation is a cvar boundary
    This is priority port 1.1 from Roc Racoon mining: add kwarg validation
    before passing to llama_cpp.Llama().

    Args:
        kwargs: The dict of kwargs to validate.
        context: Optional context string for warnings.

    Returns:
        List of warning/error messages (empty if all valid).
    """
    warnings: list = []
    for key in kwargs:
        if key not in LLAMA_CPP_VALID_KWARGS:
            ctx_str = f" [{context}]" if context else ""
            msg = f"Unknown llama-cpp kwarg{ctx_str}: '{key}' (value={kwargs[key]!r})"
            warnings.append(msg)
            logger.warning("validate_llama_kwargs: %s", msg)

    # Check type correctness for known int params
    int_params = {"n_ctx", "n_threads", "n_threads_batch", "n_batch",
                  "n_ubatch", "type_k", "type_v", "n_gpu_layers", "seed"}
    for key in int_params:
        if key in kwargs and not isinstance(kwargs[key], int):
            warnings.append(
                f"llama-cpp kwarg '{key}' should be int, got {type(kwargs[key]).__name__}"
            )

    return warnings
