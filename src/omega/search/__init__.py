# [id-soft: sqlite-vec-2024] Search Package — Persistence, metrics, and traceability for all search operations
"""
Omega Search Package

Provides search persistence, metrics, and traceability across all search tools.
"""

from .search_persistence import (
    SearchDB,
    SearchRecord,
    SearchPersistence,
    persist_search,
    SEARCH_DB_PATH,
    record_search,
    get_search_persistence,
)

__all__ = [
    "SearchDB",
    "SearchRecord", 
    "SearchPersistence",
    "persist_search",
    "record_search",
    "get_search_persistence",
    "SEARCH_DB_PATH",
]