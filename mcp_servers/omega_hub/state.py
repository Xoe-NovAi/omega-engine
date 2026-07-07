# [id-soft: quake3-1999] Hub State — netchan-inspired session/state management for MCP transport layer

"""Omega Hub — Module-level state and service initialization.

AP: AP-OMEGA-HUB-STATE-v1.0.0

Holds all service singletons, initialization guards, hivemind hot/cold
store state, and shared filesystem paths used by background.py and the
tools/ package. This is the leaf module — it has no dependencies on any
other extracted mcp_servers.omega_hub module.
"""

import sys
import os
import json
import logging
import threading
import contextvars
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import anyio

# --- Path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

# --- Domain imports (these live in src/omega/) ---
from omega.oracle.oracle import Oracle
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.sovereign_search_service import SovereignSearchService
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.hierarchy import SovereignHierarchy
from omega.oracle.health_monitor import get_health_monitor
from omega.errors import OmegaError

from mcp_servers.omega_hub.mcp_client import SovereignMCPClient

from omega.library.inbox import InboxManager
from omega.library.curator import CurationPipeline
from omega.library.library import Library
from omega.library.indexer import Indexer
from omega.library.discovery import DiscoveryOrchestrator
from omega.library.research import ResearchEngine
from omega.memory_store import get_memory_store

if TYPE_CHECKING:
    # Avoids a runtime circular import: gateway.py will import names from
    # state.py, so state.py must not import gateway.py at module load time.
    from mcp_servers.omega_hub.gateway import SovereignGateway

logger = logging.getLogger("omega.hub")


# ══════════════════════════════════════════════════════════════════════════════
# INITIALIZATION STATE
# ═══════════════════════════════════════════════════════════════════════════

_init_complete: bool = False
_init_error: Optional[str] = None
_init_in_progress: bool = False
_init_lock: anyio.Lock = anyio.Lock()


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE SINGLETONS (12 — all Optional, set by _init_services())
# ═══════════════════════════════════════════════════════════════════════════

registry: Optional[EntityRegistry] = None
model_gateway: Optional[ModelGateway] = None
oracle: Optional[Oracle] = None
hierarchy: Optional[SovereignHierarchy] = None
inbox: Optional[InboxManager] = None
curator: Optional[CurationPipeline] = None
library: Optional[Library] = None
indexer: Optional[Indexer] = None
discovery: Optional[DiscoveryOrchestrator] = None
research_engine: Optional[ResearchEngine] = None
sovereign_search_service: Optional[SovereignSearchService] = None
gateway: Optional["SovereignGateway"] = None
mcp_client: Optional[SovereignMCPClient] = None


def _require_service() -> None:
    """Raise if services not ready. Called at the top of every tool."""
    if _init_error:
        raise RuntimeError(f"Hub services failed to initialize: {_init_error}")
    if not _init_complete:
        raise RuntimeError(
            "Hub services are still initializing in the background. "
            "Retry in a few seconds."
        )


async def _init_services() -> None:
    """Initialize all Hub services as a background task.

    Runs concurrently with the SSE listener. Sets _init_complete when done.

    NOTE: All ``global`` declarations below are intentional — they bind to
    this module's own namespace (Mandate-compliant, see §4 of the v2 spec).
    """
    global _init_complete, _init_error
    global registry, model_gateway, oracle, hierarchy
    global inbox, curator, library, indexer, discovery
    global research_engine, sovereign_search_service, gateway, mcp_client

    try:
        logger.info("Background service initialization starting...")

        hm = get_health_monitor()
        registry = await anyio.to_thread.run_sync(EntityRegistry)
        model_gateway = await anyio.to_thread.run_sync(
            lambda: ModelGateway(health_monitor=hm)
        )
        oracle = await anyio.to_thread.run_sync(
            lambda: Oracle(registry=registry, model_gateway=model_gateway)
        )
        hierarchy = await anyio.to_thread.run_sync(SovereignHierarchy)

        inbox = await anyio.to_thread.run_sync(InboxManager)
        curator = await anyio.to_thread.run_sync(CurationPipeline)
        library = await anyio.to_thread.run_sync(Library)
        indexer = await anyio.to_thread.run_sync(Indexer)
        discovery = await anyio.to_thread.run_sync(
            lambda: DiscoveryOrchestrator(model_gateway=model_gateway)
        )

        research_engine = await anyio.to_thread.run_sync(
            lambda: ResearchEngine(library=library, indexer=indexer)
        )

        # Load search keys from Sovereign KeyVault with opencode.json fallback
        try:
            from omega.vault import KeyVault
            vault = KeyVault()
            _fc_key = vault.resolve("firecrawl")
            _exa_key = vault.resolve("exa")
            logger.info("Search keys successfully resolved from Sovereign KeyVault")
        except Exception as vault_err:
            logger.warning("Failed to resolve search keys from KeyVault, checking environment variables: %s", vault_err)
            _fc_key = os.environ.get("FIRECRAWL_API_KEY")
            _exa_key = os.environ.get("EXA_API_KEY")
            
            if not _fc_key or not _exa_key:
                try:
                    with open(PROJECT_ROOT / "opencode.json") as f:
                        _cfg = json.load(f)
                    _fc_key = _fc_key or (
                        _cfg.get("mcp", {})
                        .get("firecrawl", {})
                        .get("environment", {})
                        .get("FIRECRAWL_API_KEY")
                    )
                    _exa_key = _exa_key or (
                        _cfg.get("mcp", {})
                        .get("exa", {})
                        .get("headers", {})
                        .get("x-api-key")
                    )
                except Exception as e:
                    logger.warning("Failed to load search keys from opencode.json fallback: %s", e)
                    if not _fc_key or not _exa_key:
                        _fc_key = _exa_key = None

        sovereign_search_service = await anyio.to_thread.run_sync(
            lambda: SovereignSearchService(
                memory_store=get_memory_store(),
                model_gateway=model_gateway,
                indexer=indexer,
                firecrawl_key=_fc_key,
                exa_key=_exa_key,
            )
        )
        
        # Phase 1 MCP Client: Connect to SearXNG MCP server
        mcp_client = SovereignMCPClient(server_url="http://127.0.0.1:8018/sse")
        # Note: We don't 'await' the context manager here because it's a singleton.
        # Tools will use 'async with state.mcp_client as client:' to ensure session lifecycle.
        
        # SovereignGateway is imported from gateway.py (P1a-4).

        # At runtime, gateway.py is already available — the forward-ref
        # in this module (TYPE_CHECKING) is only for static analysis.
        from mcp_servers.omega_hub.gateway import SovereignGateway as _SG
        gateway = _SG()

        _init_complete = True
        logger.info("All Hub services initialized (background)")
    except Exception as e:
        _init_error = str(e)
        logger.error("Hub service initialization FAILED: %s", e)
    finally:
        _init_in_progress = False


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT TRACKING (P1-A — ContextVar for _current_entity)
# ═══════════════════════════════════════════════════════════════════════════

_current_entity: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "_current_entity", default=None
)  # Tracks the last entity used by oracle_talk/oracle_summon per-context


# ═══════════════════════════════════════════════════════════════════════════
# INTENT MATCHER SINGLETON (P0-B)
# ═══════════════════════════════════════════════════════════════════════════

_intent_matcher: Optional[object] = None
_intent_matcher_lock = threading.Lock()


def _get_intent_matcher():
    """Module-level singleton accessor for IntentMatcher (P0-B)."""
    global _intent_matcher
    if _intent_matcher is None:
        with _intent_matcher_lock:
            if _intent_matcher is None:
                from omega.iris.matcher import IntentMatcher
                _intent_matcher = IntentMatcher()
    return _intent_matcher


# ═══════════════════════════════════════════════════════════════════════════
# HIVEMIND HOT/COLD STORE
# ═══════════════════════════════════════════════════════════════════════════

HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)

# ── Sharded hot store (power of 2 for fast modulo) ──
# [id-soft: quake-1996] Zone Memory — tagged allocation → tagged sharding.
_HOT_STORE_SHARDS = 16
_hot_store_shards: List[Dict[str, Dict[str, Any]]] = [{} for _ in range(_HOT_STORE_SHARDS)]
_hot_store_locks: List[anyio.Lock] = [anyio.Lock() for _ in range(_HOT_STORE_SHARDS)]

# Backward compat — DO NOT REMOVE yet (tools.py imports _hot_store, _hot_store_lock)
# These become read-only aliases pointing to shard 0. Remove after all consumers migrate.
_hot_store = _hot_store_shards[0]  # DEPRECATED — use hot_store_get/set
_hot_store_lock = _hot_store_locks[0]  # DEPRECATED — use hot_store_get/set

_awareness: Dict[str, Dict[str, Any]] = {}


def _hot_store_shard_key(key: str) -> int:
    """Deterministic shard from key. FNV-1a 32-bit hash.

    [id-soft: quake-1996] Zone Memory — tagged allocation → tagged sharding.
    """
    hash_val = 0x811c9dc5
    for byte in key.encode('utf-8'):
        hash_val ^= byte
        hash_val = (hash_val * 0x01000193) & 0xffffffff
    return hash_val & (_HOT_STORE_SHARDS - 1)


async def hot_store_set(key: str, value: Dict[str, Any]) -> None:
    """Set value in sharded hot store. Thread-safe via per-shard lock."""
    shard = _hot_store_shard_key(key)
    async with _hot_store_locks[shard]:
        _hot_store_shards[shard][key] = value


async def hot_store_get(key: str) -> Optional[Dict[str, Any]]:
    """Get value from sharded hot store."""
    shard = _hot_store_shard_key(key)
    async with _hot_store_locks[shard]:
        return _hot_store_shards[shard].get(key)


async def hot_store_get_all() -> List[Dict[str, Any]]:
    """Get all values across shards. For awareness listing."""
    results = []
    for i in range(_HOT_STORE_SHARDS):
        async with _hot_store_locks[i]:
            results.extend(_hot_store_shards[i].values())
    return results


async def hot_store_prune_stale(ttl_seconds: int) -> int:
    """Prune stale entries across all shards. Returns count pruned."""
    now = datetime.now(timezone.utc)
    pruned = 0
    for i in range(_HOT_STORE_SHARDS):
        async with _hot_store_locks[i]:
            stale_keys = [
                k for k, snap in _hot_store_shards[i].items()
                if snap.get("timestamp")
                and (now - datetime.fromisoformat(snap["timestamp"])).total_seconds() > ttl_seconds
            ]
            for k in stale_keys:
                del _hot_store_shards[i][k]
                pruned += 1
    return pruned


_awareness_lock = anyio.Lock()

# [D-122] HEARTBEAT_TTL — 45 minutes (2700s) for active agent presence
HEARTBEAT_TTL = 2700

# ── Cold-store awareness cache (P0-4) ──
# [id-soft: doom-1993] Precomputed Lookup — pay I/O cost once, serve from cache.
_AWARENESS_CACHE_TTL = 5.0  # seconds
_awareness_cache: Dict[str, tuple] = {}  # "cold" -> (monotonic_timestamp, data_list)
_awareness_cache_lock = anyio.Lock()


async def _scan_cold_store() -> List[Dict[str, Any]]:
    """Scan HALL_OF_RECORDS for active agents. Extracted from tools.py L594-622."""
    now = datetime.now(timezone.utc)
    recovered: List[Dict[str, Any]] = []
    if not HALL_OF_RECORDS.exists():
        return recovered
    for agent_dir in HALL_OF_RECORDS.iterdir():
        if not agent_dir.is_dir():
            continue
        json_files = sorted(
            agent_dir.glob("ses_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if not json_files:
            continue
        latest = json_files[0]
        mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
        age = (now - mtime).total_seconds()
        if age <= HEARTBEAT_TTL:
            try:
                def _read_session():
                    with latest.open() as f:
                        return json.load(f)
                snap = await anyio.to_thread.run_sync(_read_session)
                recovered.append({
                    "agent_id": snap.get("agent_id", agent_dir.name),
                    "channel": snap.get("channel", ""),
                    "entity": snap.get("entity", agent_dir.name),
                    "model": snap.get("model", "unknown"),
                    "task_current": snap.get("task_current", ""),
                    "last_seen": snap.get("timestamp", mtime.isoformat()),
                    "source": "cold_store",
                })
            except Exception as exc:
                logger.debug("Failed to load cold session %s: %s", latest.name, exc)
    return recovered


async def get_cached_cold_awareness() -> List[Dict[str, Any]]:
    """Get cold-store awareness with 5-second TTL cache.

    [id-soft: doom-1993] Precomputed Lookup — pay I/O cost once, serve from cache.
    """
    now = time.monotonic()
    async with _awareness_cache_lock:
        if "cold" in _awareness_cache:
            ts, data = _awareness_cache["cold"]
            if now - ts < _AWARENESS_CACHE_TTL:
                return data

    # Cache miss — scan outside the cache lock
    data = await _scan_cold_store()

    async with _awareness_cache_lock:
        _awareness_cache["cold"] = (now, data)
    return data


async def invalidate_awareness_cache() -> None:
    """Call when hot store is updated (post_context, heartbeat)."""
    async with _awareness_cache_lock:
        _awareness_cache.clear()

# Background pruning cycle tracker
_last_pruning_cycle: Optional[str] = None
METRICS_PATH: Path = PROJECT_ROOT / "data" / "coordination" / "metrics.json"


# ═══════════════════════════════════════════════════════════════════════════
# HEARTBEAT / EXTENDED SESSIONS
# ═══════════════════════════════════════════════════════════════════════════

_extended_sessions: Dict[str, Dict[str, Any]] = {}  # cli -> {ttl_seconds, registered_at, reason}
_extended_sessions_lock = anyio.Lock()
EXTENDED_SAFETY_TTL_DEFAULT = 3 * 60 * 60  # 3 hours = 10800s
EXTENDED_SESSIONS_FILE = HALL_OF_RECORDS / "extended_sessions.json"


def _load_extended_sessions() -> Dict[str, Dict[str, Any]]:
    """Load extended sessions from disk."""
    if not EXTENDED_SESSIONS_FILE.exists():
        return {}
    try:
        with open(EXTENDED_SESSIONS_FILE) as f:
            return dict(json.load(f))
    except Exception as e:
        logger.warning("Failed to load extended sessions: %s", e)
        return {}


def _save_extended_sessions(sessions: Dict[str, Dict[str, Any]]) -> None:
    """Save extended sessions to disk atomically."""
    EXTENDED_SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = EXTENDED_SESSIONS_FILE.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(sessions, f, indent=2)
    os.replace(str(tmp_path), str(EXTENDED_SESSIONS_FILE))


# Load persistent extended sessions on module start
_saved = _load_extended_sessions()
_extended_sessions.update(_saved)
if _saved:
    logger.info("Restored %d extended session(s) from disk", len(_saved))


# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND TASK REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

_background_tasks: list = []  # NOTE: no `anyio.Task` annotation (removed P0-2)


# ═══════════════════════════════════════════════════════════════════════════
# HIVEMIND HANDOFF QUEUE PATHS
# ═══════════════════════════════════════════════════════════════════════════

HANDOFF_BASE = PROJECT_ROOT / "data" / "handoff"
HANDOFF_PENDING = HANDOFF_BASE / "pending"
HANDOFF_ACTIVE = HANDOFF_BASE / "active"
HANDOFF_COMPLETED = HANDOFF_BASE / "completed"
HANDOFF_STALE = HANDOFF_BASE / "stale"
HANDOFF_ARCHIVE = HANDOFF_BASE / "archive"

for _d in (HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE):
    _d.mkdir(parents=True, exist_ok=True)
del _d

# ── Handoff packet index: packet_id → queue_name ──
# [id-soft: doom-1993] WAD System — hash table for O(1) resource lookup
_handoff_index: Dict[str, str] = {}  # packet_id -> queue_name


def handoff_index_add(packet_id: str, queue: str) -> None:
    """Add packet to index. Call on submit/move."""
    _handoff_index[packet_id] = queue


def handoff_index_move(packet_id: str, new_queue: str) -> bool:
    """Move packet in index. Returns True if found."""
    if packet_id in _handoff_index:
        _handoff_index[packet_id] = new_queue
        return True
    return False


def handoff_index_remove(packet_id: str) -> bool:
    """Remove packet from index. Returns True if found."""
    return _handoff_index.pop(packet_id, None) is not None


async def handoff_index_rebuild() -> int:
    """Rebuild index from filesystem on startup. Returns count."""
    _handoff_index.clear()
    count = 0
    for q_name, q_path in [
        ("pending", HANDOFF_PENDING),
        ("active", HANDOFF_ACTIVE),
        ("completed", HANDOFF_COMPLETED),
        ("stale", HANDOFF_STALE),
        ("archive", HANDOFF_ARCHIVE),
    ]:
        for f in q_path.glob("*.json"):
            _handoff_index[f.stem] = q_name
            count += 1
    return count


# ═══════════════════════════════════════════════════════════════════════════
# WORKSPACE LOCK BASE PATH
# ═══════════════════════════════════════════════════════════════════════════

LOCKS_BASE = PROJECT_ROOT / "data" / "coordination" / "locks"
LOCKS_BASE.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (used by tools and server.py)
# ═══════════════════════════════════════════════════════════════════════════

def _make_agent_id(channel: str, entity: str) -> str:
    """Build a canonical agent identifier from channel and entity.

    The agent_id uniquely identifies WHO is running WHERE.
    Format: '{channel}/{entity}'
    """
    return f"{channel}/{entity}"


def _cold_path(agent_id: str, session_id: str) -> Path:
    safe_id = agent_id.replace(" ", "_").replace("/", "_")
    safe_sid = session_id.replace("/", "_").replace(":", "_")
    return HALL_OF_RECORDS / safe_id / f"{safe_sid}.json"


def _latest_path() -> Path:
    return HALL_OF_RECORDS / "latest.yaml"


def _find_packet_path(packet_id: str) -> Optional[Path]:
    """Find a packet file using in-memory index (O(1)), fallback to scan.

    [id-soft: doom-1993] WAD System — hash table for O(1) resource lookup.
    """
    queue_name = _handoff_index.get(packet_id)
    if queue_name:
        queue_map = {
            "pending": HANDOFF_PENDING, "active": HANDOFF_ACTIVE,
            "completed": HANDOFF_COMPLETED, "stale": HANDOFF_STALE,
            "archive": HANDOFF_ARCHIVE,
        }
        path = queue_map.get(queue_name, HANDOFF_PENDING) / f"{packet_id}.json"
        if path.exists():
            return path
        logger.warning("Handoff index stale for %s (queue=%s), scanning", packet_id, queue_name)

    # Fallback: linear scan (should be rare)
    for q in [HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE]:
        path = q / f"{packet_id}.json"
        if path.exists():
            _handoff_index[packet_id] = q.name  # Update index
            return path
    return None


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # init state
    "_init_complete", "_init_error", "_require_service", "_init_services",
    # service singletons
    "registry", "model_gateway", "oracle", "hierarchy",
    "inbox", "curator", "library", "indexer", "discovery",
    "research_engine", "sovereign_search_service", "gateway", "mcp_client",
    # context tracking
    "_current_entity", "_get_intent_matcher",
    # hivemind store (sharded)
    "HALL_OF_RECORDS",
    "_HOT_STORE_SHARDS", "_hot_store_shards", "_hot_store_locks",
    "_hot_store_shard_key", "hot_store_set", "hot_store_get", "hot_store_get_all", "hot_store_prune_stale",
    "_hot_store", "_hot_store_lock",  # DEPRECATED aliases
    "_awareness", "_awareness_lock",
    # cold-store cache
    "_AWARENESS_CACHE_TTL", "get_cached_cold_awareness", "invalidate_awareness_cache",
    # heartbeat / extended sessions
    "HEARTBEAT_TTL", "_extended_sessions", "_extended_sessions_lock",
    "EXTENDED_SAFETY_TTL_DEFAULT", "EXTENDED_SESSIONS_FILE",
    "_load_extended_sessions", "_save_extended_sessions",
    # pruning cycle
    "_last_pruning_cycle", "METRICS_PATH",
    # background tasks
    "_background_tasks",
    # handoff queue paths
    "HANDOFF_BASE", "HANDOFF_PENDING", "HANDOFF_ACTIVE",
    "HANDOFF_COMPLETED", "HANDOFF_STALE", "HANDOFF_ARCHIVE",
    # locks
    "LOCKS_BASE",
    # shared constants
    "PROJECT_ROOT",
    # helpers
    "_make_agent_id", "_cold_path", "_latest_path", "_find_packet_path",
    # handoff index (P1-6)
    "_handoff_index", "handoff_index_add", "handoff_index_move",
    "handoff_index_remove", "handoff_index_rebuild",
]
