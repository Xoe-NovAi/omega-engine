"""Sovereign SQLite Policy — Profiled connection configuration.
AP: AP-SQLITE-POLICY-v1.0.0
⬡ OMEGA ⬡ P2 ⬡ infra ⬡ sqlite_policy ⬡ FS-Β4

D-282 PRAGMA stack is law for memory fabric (A10).
Profiles not one stack — separate profiles: memory / search / metrics (A11).
Correct sqlite3.connect API — uri=True for readonly, timeout=30 for rw; NO flags=SQLITE_OPEN_* (A12).
Gate criterion fix — connection-setup PRAGMAs only in sqlite_policy.py; allow operational PRAGMAs (A13).
"""

import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Literal, Optional

from omega.governance.config_resolver import DATA_DIR, PROJECT_ROOT


Profile = Literal["memory", "search", "metrics", "reader"]


# Profile-specific PRAGMA stacks (D-282 validated for memory)
# 2026 Production Hardening: wal_autocheckpoint=10000 for writers, journal_size_limit=64MB for all
# Readers should use wal_autocheckpoint=0 to avoid accidental checkpoint contention
PROFILE_PRAGMAS: dict[Profile, list[tuple[str, str]]] = {
    "memory": [
        ("journal_mode", "WAL"),
        ("synchronous", "NORMAL"),
        ("cache_size", "-32768"),          # 32MB (D-282)
        ("mmap_size", "268435456"),        # 256MB
        ("temp_store", "MEMORY"),
        ("busy_timeout", "30000"),         # 30s (D-282)
        ("foreign_keys", "ON"),
        ("wal_autocheckpoint", "10000"),   # 2026: writer profile — 10k pages (~40MB) before autocheckpoint
        ("journal_size_limit", "67108864"), # 64MB (D-282)
        ("page_size", "4096"),
    ],
    "search": [
        ("journal_mode", "WAL"),
        ("synchronous", "NORMAL"),
        ("cache_size", "-65536"),          # 64MB
        ("mmap_size", "268435456"),
        ("temp_store", "MEMORY"),
        ("busy_timeout", "30000"),         # 30s for search concurrency
        ("foreign_keys", "ON"),
        ("wal_autocheckpoint", "10000"),   # 2026: writer profile
        ("journal_size_limit", "67108864"), # 64MB
        ("page_size", "4096"),
    ],
    "metrics": [
        ("journal_mode", "WAL"),
        ("synchronous", "NORMAL"),
        ("cache_size", "-32768"),
        ("mmap_size", "134217728"),        # 128MB
        ("temp_store", "MEMORY"),
        ("busy_timeout", "10000"),         # 10s
        ("foreign_keys", "ON"),
        ("wal_autocheckpoint", "10000"),   # 2026: writer profile
        ("journal_size_limit", "67108864"), # 64MB
        ("page_size", "4096"),
    ],
    "reader": [
        ("journal_mode", "WAL"),
        ("synchronous", "NORMAL"),
        ("cache_size", "-32768"),
        ("mmap_size", "268435456"),
        ("temp_store", "MEMORY"),
        ("busy_timeout", "30000"),
        ("foreign_keys", "ON"),
        ("wal_autocheckpoint", "0"),       # 2026: readers NEVER trigger checkpoints
        ("journal_size_limit", "67108864"),
        ("page_size", "4096"),
    ],
}


def get_sqlite_connection(
    path: Path,
    profile: Profile = "memory",
    readonly: bool = False,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """Get a standardized SQLite connection with profiled PRAGMA stack.
    
    Args:
        path: Database file path
        profile: Profile name — "memory", "search", or "metrics"
        readonly: If True, open read-only via URI (portable stdlib pattern)
        timeout: Connection timeout in seconds (default 30s for rw)
    
    Returns:
        Configured sqlite3.Connection with row_factory=sqlite3.Row
    
    Raises:
        sqlite3.Error: If connection fails
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if readonly:
        # Read-only via URI (portable stdlib pattern) — A12
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=timeout)
    else:
        conn = sqlite3.connect(str(path), timeout=timeout, check_same_thread=False)
    
    conn.row_factory = sqlite3.Row
    
    # Apply profile-specific PRAGMA stack
    pragmas = PROFILE_PRAGMAS.get(profile, PROFILE_PRAGMAS["memory"])
    for pragma, value in pragmas:
        conn.execute(f"PRAGMA {pragma} = {value}")
    
    return conn


@contextmanager
def sqlite_transaction(
    path: Path,
    profile: Profile = "memory",
    readonly: bool = False,
    timeout: float = 30.0,
):
    """Context manager for atomic SQLite transactions.
    
    Args:
        path: Database file path
        profile: Profile name — "memory", "search", or "metrics"
        readonly: If True, open read-only (no commit/rollback)
        timeout: Connection timeout in seconds
    
    Yields:
        sqlite3.Connection with profiled PRAGMAs applied
    
    Example:
        with sqlite_transaction(path, profile="search") as conn:
            conn.execute("INSERT INTO ...")
            # Auto-commits on success, rolls back on exception
    """
    conn = get_sqlite_connection(path, profile, readonly, timeout)
    try:
        yield conn
        if not readonly:
            conn.commit()
    except Exception:
        if not readonly:
            conn.rollback()
        raise
    finally:
        conn.close()


def init_database(path: Path, schema_sql: str, profile: Profile = "memory") -> None:
    """Initialize database with schema (idempotent).
    
    Args:
        path: Database file path
        schema_sql: SQL schema script (CREATE TABLE, etc.)
        profile: Profile name for PRAGMA stack
    """
    with sqlite_transaction(path, profile) as conn:
        conn.executescript(schema_sql)


def verify_pragmas(conn: sqlite3.Connection, profile: Profile = "memory") -> dict[str, any]:
    """Verify that connection has the expected PRAGMAs applied.
    
    Used by contract tests to validate profile compliance.
    
    Args:
        conn: SQLite connection to verify
        profile: Expected profile name
    
    Returns:
        Dict of pragma_name -> actual_value
    """
    pragmas = PROFILE_PRAGMAS.get(profile, PROFILE_PRAGMAS["memory"])
    results = {}
    for pragma, expected in pragmas:
        cursor = conn.execute(f"PRAGMA {pragma}")
        actual = cursor.fetchone()[0]
        results[pragma] = {"expected": expected, "actual": actual, "match": str(actual) == str(expected)}
    return results


def optimize_connection(conn: sqlite3.Connection) -> None:
    """Run PRAGMA optimize on connection (call before close for query planner stats).
    
    Per SQLite docs: run just before closing each connection, or on a timer for long-running apps.
    Updates sqlite_stat1/sqlite_stat4 for better query plans.
    """
    conn.execute("PRAGMA optimize=0x10002")


def get_writer_connection(path: Path, timeout: float = 30.0) -> sqlite3.Connection:
    """Get a writer connection with writer profile (wal_autocheckpoint=10000)."""
    return get_sqlite_connection(path, profile="memory", readonly=False, timeout=timeout)


def get_reader_connection(path: Path, timeout: float = 30.0) -> sqlite3.Connection:
    """Get a reader connection with reader profile (wal_autocheckpoint=0)."""
    return get_sqlite_connection(path, profile="reader", readonly=True, timeout=timeout)


# ── Periodic Optimize Timer ──────────────────────────────────────────────
# Per SQLite docs: run PRAGMA optimize before close, or on a timer for long-running apps.
# Updates sqlite_stat1/sqlite_stat4 for better query plans.

_optimize_timer: Optional[threading.Thread] = None
_optimize_stop = threading.Event()


def start_optimize_timer(interval_seconds: int = 3600) -> None:
    """Start background thread that runs PRAGMA optimize on all open connections periodically.
    
    Args:
        interval_seconds: Interval between optimize runs (default 1 hour)
    """
    global _optimize_timer
    if _optimize_timer is not None and _optimize_timer.is_alive():
        return  # Already running
    
    _optimize_stop.clear()
    
    def _optimize_loop():
        while not _optimize_stop.wait(interval_seconds):
            # Note: In a real implementation, you'd track open connections
            # For now, this is a placeholder for the pattern
            pass
    
    _optimize_timer = threading.Thread(target=_optimize_loop, daemon=True, name="sqlite-optimize")
    _optimize_timer.start()


def stop_optimize_timer() -> None:
    """Stop the periodic optimize timer."""
    global _optimize_timer
    if _optimize_timer is not None:
        _optimize_stop.set()
        _optimize_timer.join(timeout=5.0)
        _optimize_timer = None