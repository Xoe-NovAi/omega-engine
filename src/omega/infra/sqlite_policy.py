"""Sovereign SQLite Policy — Profiled connection configuration.
AP: AP-SQLITE-POLICY-v1.0.0
⬡ OMEGA ⬡ P2 ⬡ infra ⬡ sqlite_policy ⬡ FS-Β4

D-282 PRAGMA stack is law for memory fabric (A10).
Profiles not one stack — separate profiles: memory / search / metrics (A11).
Correct sqlite3.connect API — uri=True for readonly, timeout=30 for rw; NO flags=SQLITE_OPEN_* (A12).
Gate criterion fix — connection-setup PRAGMAs only in sqlite_policy.py; allow operational PRAGMAs (A13).
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Literal, Optional

from omega.governance.config_resolver import DATA_DIR, PROJECT_ROOT


Profile = Literal["memory", "search", "metrics"]


# Profile-specific PRAGMA stacks (D-282 validated for memory)
PROFILE_PRAGMAS: dict[Profile, list[tuple[str, str]]] = {
    "memory": [
        ("journal_mode", "WAL"),
        ("synchronous", "NORMAL"),
        ("cache_size", "-32768"),          # 32MB (D-282)
        ("mmap_size", "268435456"),        # 256MB
        ("temp_store", "MEMORY"),
        ("busy_timeout", "30000"),         # 30s (D-282)
        ("foreign_keys", "ON"),
        ("wal_autocheckpoint", "500"),     # D-282
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
        conn = sqlite3.connect(str(path), timeout=timeout)
    
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