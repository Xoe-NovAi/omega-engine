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
#   [id-soft: vet-015] ZONEID Pattern — magic constants for runtime integrity.
#     A SINGLE PATTERN applied to 13 subsystems (memory, entity, breaker, trace,
#     probe, handoff, presence, knowledge, demand, verification, atomic, somatic,
#     embedding). Each constant validates a different data structure's integrity.
#   [id-soft: vet-016] Cvar System — typed, queryable, auditable cvars
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


# DocRef: docs/standards/DOC_STYLE_GUIDE.md
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Canonical data dir resolution (mirrors observability.py and library modules).
# Inlined here to avoid circular import with constants.py.
_DATA_DIR_DEFAULT = Path.home() / "omega" / "data"
DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(_DATA_DIR_DEFAULT)))

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# §1 — CvarDef Dataclass
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class CvarDef:
    """A single cvar (console variable) entry.

    [id-soft: vet-016] Cvar System — typed, queryable, auditable cvars

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

# ZONEID constants — runtime integrity magic markers (id Software ZONEID pattern)
ZONEID_MEMORY = 0x1d4a11        # MemoryStore entry validation
ZONEID_ENTITY = 0x1d4a12        # EntityRegistry entity validation
ZONEID_BREAKER = 0x1d4a13       # Circuit breaker state marker
ZONEID_TRACE = 0x1d4a14         # Trace/session lineage marker
ZONEID_PROBE = 0x1d4a15         # ResourceGuard critical section guard
ZONEID_HANDOFF = 0x1d4a16       # SubagentHandoffPacket integrity marker
ZONEID_PRESENCE = 0x1d4a17      # Agent Presence dataclass integrity marker
ZONEID_KNOWLEDGE = 0x1d4a18     # Knowledge Signal integrity marker
ZONEID_DEMAND = 0x1d4a19        # Demand Signal integrity marker
ZONEID_VERIFICATION = 0x1d4a1a  # Verification audit trail integrity marker
ZONEID_ATOMIC = 0x1d4a1b        # Critical section atomic lock marker
ZONEID_SOMATIC = 0x1d4a1c       # Somatic snapshot integrity marker
# [id-soft: vet-023] Precomputed Lookup — embedding cache integrity marker
# Embedding provider cache validation. Validated on every embed read/write to
# catch corrupt or stale embedding vectors in the hot cache.
ZONEID_EMBEDDING = 0x1d4a1d


# [id-soft: vet-008] Lazy Deletion — sentinel value for tombstoned entities
# 0xDEADBEEF is the canonical sentinel hex pattern used since the 1980s
# on IBM RS/6000, Motorola 68000, and id Software's DOOM engine.
ZONEID_TOMBSTONE = 0xDEADBEEF


# ── ZONEID Validation Helper ─────────────────────────────────────────

def validate_zoneid(value: int, expected: int, context: str = "") -> None:
    """Validate a ZONEID magic constant.

    [id-soft: vet-015] ZONEID Pattern — runtime integrity check
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
    "presence": {"id": ZONEID_PRESENCE, "subsystem": "LinkN9Runtime", "description": "Agent presence record marker"},
    "knowledge": {"id": ZONEID_KNOWLEDGE, "subsystem": "CrossPollination", "description": "Knowledge signal integrity marker"},
    "demand": {"id": ZONEID_DEMAND, "subsystem": "CrossPollination", "description": "Demand signal integrity marker"},
    "tombstone": {"id": ZONEID_TOMBSTONE, "subsystem": "EntityRegistry", "description": "Lazy deletion sentinel"},
    "verification": {"id": ZONEID_VERIFICATION, "subsystem": "Sentinel", "description": "Verification audit trail integrity marker"},
    "somatic": {"id": ZONEID_SOMATIC, "subsystem": "SomaticState", "description": "Somatic snapshot integrity marker (Phase C)"},
    "embedding": {"id": ZONEID_EMBEDDING, "subsystem": "EmbeddingProvider", "description": "Embedding cache integrity marker"},
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
        "Agent presence record marker (Link N9 Runtime)", "LinkN9Runtime",
    ),
    "zoneid.tombstone": CvarDef(
        "zoneid.tombstone", ZONEID_TOMBSTONE, "zoneid",
        "Lazy deletion sentinel", "EntityRegistry",
    ),
    "zoneid.verification": CvarDef(
        "zoneid.verification", ZONEID_VERIFICATION, "zoneid",
        "Verification audit trail integrity marker (N5 Sentinel)", "Sentinel",
    ),
    "zoneid.atomic": CvarDef(
        "zoneid.atomic", ZONEID_ATOMIC, "zoneid",
        "Critical section atomic lock marker", "ResourceGuard",
    ),
    "zoneid.somatic": CvarDef(
        "zoneid.somatic", ZONEID_SOMATIC, "zoneid",
        "Somatic snapshot integrity marker (Phase C Cognitive Substrate)", "SomaticState",
    ),
    "zoneid.embedding": CvarDef(
        "zoneid.embedding", ZONEID_EMBEDDING, "zoneid",
        "Embedding cache integrity marker (LocalGGUFEmbeddingProvider)", "EmbeddingProvider",
    ),

    # ── config.entity.* — Entity Registry knobs ─────────────────
    "config.entity.default": CvarDef(
        "config.entity.default", "default", "str",
        "Default entity name for Oracle talk/summon", "EntityRegistry",
    ),
    "config.entity.user": CvarDef(
        "config.entity.user", "arch", "str",
        "Default user name for entity workspace paths", "EntityRegistry",
    ),
    "config.entity.allow_transient": CvarDef(
        "config.entity.allow_transient", True, "bool",
        "Allow transient sessions that aren't recorded to soul", "EntityRegistry",
    ),

    # ── config.data.* — Global data paths ──────────────────────
    "config.data.dir": CvarDef(
        "config.data.dir", str(DATA_DIR), "str",
        "Root directory for all engine data (entities, sessions, logs)", "EntityRegistry",
    ),

    # ── config.resource_guard.* — Resource Guard knobs ─────────
    "config.resource_guard.max_ram_mb": CvarDef(
        "config.resource_guard.max_ram_mb", 12288, "int",
        "Global max RAM (MB) for concurrent model inference", "ResourceGuard",
    ),

    # ── config.hivemind.* — Hivemind/Hub knobs ─────────────────
    "config.hivemind.enabled": CvarDef(
        "config.hivemind.enabled", True, "bool",
        "Enable cross-agent awareness via Omega Hub", "LinkN9Runtime",
    ),
    "config.hivemind.endpoint": CvarDef(
        "config.hivemind.endpoint", "http://127.0.0.1:8016", "str",
        "Base URL for the Omega Hub MCP server", "LinkN9Runtime",
    ),

    # ── config.session_header.* — ICS/Session header knobs ─────────
    "config.session_header.mode": CvarDef(
        "config.session_header.mode", "compact", "str",
        "Session header display mode (compact|verbose|off)", "Oracle",
    ),

    # ── config.hivemind.retention.* — TTL Alignment (D-kal-045) ────
    # N7 Dark Council Synthesis: workspace (was 7d) and observation log (30d)
    # had a 23-day silent data loss zone. Aligned both to 30d with 25% grace.
    "config.hivemind.retention.workspace_days": CvarDef(
        "config.hivemind.retention.workspace_days", 30, "int",
        "Workspace file retention (days) — aligned with observation log", "LinkN9Runtime",
    ),
    "config.hivemind.retention.observation_days": CvarDef(
        "config.hivemind.retention.observation_days", 30, "int",
        "Observation log retention (days)", "LinkN9Runtime",
    ),
    "config.hivemind.retention.grace_ratio": CvarDef(
        "config.hivemind.retention.grace_ratio", 0.25, "float",
        "Grace period as ratio of base TTL (id Software Quake 1996 pattern)", "LinkN9Runtime",
    ),
    "config.hivemind.retention.warm_ttl_hours": CvarDef(
        "config.hivemind.retention.warm_ttl_hours", 24, "int",
        "Warm awareness tier retention (hours)", "LinkN9Runtime",
    ),
    "config.hivemind.retention.hot_ttl_minutes": CvarDef(
        "config.hivemind.retention.hot_ttl_minutes", 5, "int",
        "Hot presence tier retention (minutes) — in-memory", "LinkN9Runtime",
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
        "KV cache key quantization type (8=q8_0, 1=f16, 2=q4_0, 0=F32)",
        "NativeGGUFProvider",
    ),
    "config.gguf.type_v": CvarDef(
        "config.gguf.type_v", 8, "int",
        "KV cache value quantization type (8=q8_0, 1=f16, 2=q4_0, 0=F32)",
        "NativeGGUFProvider",
    ),

    # ── config.sampling.* — Global inference sampling defaults ─────
    "config.sampling.temperature": CvarDef(
        "config.sampling.temperature", 0.7, "float",
        "Global default temperature for all providers (0.0=greedy, higher=more random)",
        "ModelGateway",
    ),
    "config.sampling.top_p": CvarDef(
        "config.sampling.top_p", 0.95, "float",
        "Global default top-p (nucleus sampling) for all providers",
        "ModelGateway",
    ),
    "config.sampling.top_k": CvarDef(
        "config.sampling.top_k", 40, "int",
        "Global default top-k sampling for all providers (0=disabled)",
        "ModelGateway",
    ),
    "config.sampling.repetition_penalty": CvarDef(
        "config.sampling.repetition_penalty", 1.0, "float",
        "Global default repetition penalty for all providers (1.0=disabled)",
        "ModelGateway",
    ),
    "config.sampling.min_p": CvarDef(
        "config.sampling.min_p", 0.0, "float",
        "Global default min-p sampling for all providers (0.0=disabled)",
        "ModelGateway",
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

    # ── config.somatic.* — Phase C Somatic / Dreaming / Symmetry knobs ──
    "config.somatic.enable": CvarDef(
        "config.somatic.enable", False, "bool",
        "MASTER KILL SWITCH — disables ALL Phase C features (Somatic, Dreaming, Symmetry)",
        "PhaseC",
    ),
    "config.somatic.snapshot_on_turn": CvarDef(
        "config.somatic.snapshot_on_turn", False, "bool",
        "Per-turn snapshot vs interruption-only (default: interruption-only, lower NVMe wear)",
        "PhaseC",
    ),
    "config.somatic.max_snapshots_per_entity": CvarDef(
        "config.somatic.max_snapshots_per_entity", 3, "int",
        "Max snapshot files retained per entity (FIFO eviction on overflow)",
        "PhaseC",
    ),
    "config.somatic.memory_budget_mb": CvarDef(
        "config.somatic.memory_budget_mb", 1024, "int",
        "Per-snapshot memory budget (MB) — snapshot exceeds this → discard",
        "PhaseC",
    ),
    "config.somatic.page_size_mb": CvarDef(
        "config.somatic.page_size_mb", 2, "int",
        "mmap page size for somatic snapshots (MB). 2MB = Zen 2 hugepage alignment",
        "PhaseC",
    ),
    "config.somatic.ctypes_safe_mode": CvarDef(
        "config.somatic.ctypes_safe_mode", True, "bool",
        "Use llama-cpp-python save_state/load_state instead of raw ctypes CDLL",
        "PhaseC",
    ),

    # ── config.dreaming.* — Dreaming Cycle knobs ─────────────────
    "config.dreaming.enable": CvarDef(
        "config.dreaming.enable", False, "bool",
        "Sub-switch — enable the Dreaming Cycle background process",
        "PhaseC",
    ),
    "config.dreaming.model": CvarDef(
        "config.dreaming.model", "qwen3-0.6b", "str",
        "Model for Dreaming Cycle (MUST be small — 0.6B, not the primary model)",
        "PhaseC",
    ),
    "config.dreaming.n_ctx": CvarDef(
        "config.dreaming.n_ctx", 4096, "int",
        "Context window for Dreaming Cycle. Short — distillation doesn't need full history",
        "PhaseC",
    ),
    "config.dreaming.max_rss_mb": CvarDef(
        "config.dreaming.max_rss_mb", 1500, "int",
        "Hard memory cap for Dreaming Cycle process (MB). OOM-killed if exceeded",
        "PhaseC",
    ),
    "config.dreaming.max_hours_per_day": CvarDef(
        "config.dreaming.max_hours_per_day", 4, "int",
        "Max active distillation hours per day. Budget tracked in data/state/dreaming_usage.json",
        "PhaseC",
    ),
    "config.dreaming.session_minutes": CvarDef(
        "config.dreaming.session_minutes", 30, "int",
        "Max duration of a single dreaming session (minutes). Beyond this → cool-down",
        "PhaseC",
    ),
    "config.dreaming.cooldown_minutes": CvarDef(
        "config.dreaming.cooldown_minutes", 60, "int",
        "CPU cool-down period between dreaming sessions. Allows 5700U to drop to 45-50°C",
        "PhaseC",
    ),
    "config.dreaming.preferred_window": CvarDef(
        "config.dreaming.preferred_window", "02:00-06:00", "str",
        "Preferred overnight distillation window (HH:MM-HH:MM, local time)",
        "PhaseC",
    ),
    "config.dreaming.poll_interval_ms": CvarDef(
        "config.dreaming.poll_interval_ms", 100, "int",
        "archon_active file poll interval during inference (ms). 100ms = token-level yield",
        "PhaseC",
    ),

    # ── config.symmetry.* — Symmetry-Break Audit knobs ──────────
    "config.symmetry.enable": CvarDef(
        "config.symmetry.enable", False, "bool",
        "Sub-switch — enable the Symmetry-Break Audit (C.3.x)",
        "PhaseC",
    ),
    "config.symmetry.mode": CvarDef(
        "config.symmetry.mode", "fast", "str",
        "Symmetry mode: 'fast' (Lilith only), 'slow' (Ma'at + Lilith, sequential)",
        "PhaseC",
    ),
    "config.symmetry.max_attempts": CvarDef(
        "config.symmetry.max_attempts", 2, "int",
        "Skeptical Circuit Breaker — max verification attempts before fallback",
        "PhaseC",
    ),
    "config.symmetry.semantic_delta_threshold": CvarDef(
        "config.symmetry.semantic_delta_threshold", 0.3, "float",
        "Semantic delta threshold for SymmetryBreakError (0.0-1.0). Empirical — needs validation",
        "PhaseC",
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

    [id-soft: vet-016] Cvar System — config validation is a cvar boundary
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
