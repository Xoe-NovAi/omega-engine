"""Provenance preservation checks for extractor-style outputs."""

from __future__ import annotations

from typing import Any


def provenance_present(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    prov = obj.get("provenance")
    if not isinstance(prov, dict):
        return False
    return all(isinstance(prov.get(k), str) and prov.get(k) for k in ("source_file", "recorded_at", "window_id"))


def source_quote_grounded(obj: Any, window: str) -> bool:
    """Every item's source_quote must be a substring of the input window."""
    if not isinstance(obj, dict):
        return False
    items = obj.get("items")
    if not isinstance(items, list):
        return False
    if not items:
        return True
    for it in items:
        if not isinstance(it, dict):
            return False
        quote = it.get("source_quote", "")
        if not isinstance(quote, str) or not quote or quote not in window:
            return False
    return True


def provenance_preserved(obj: Any, gold: dict | None, window: str) -> float:
    p = 1.0 if provenance_present(obj) else 0.0
    g = 1.0 if source_quote_grounded(obj, window) else 0.0
    return (p + g) / 2.0
