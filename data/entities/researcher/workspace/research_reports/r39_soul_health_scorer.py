#!/usr/bin/env python3
"""
SoulHealthScorer — Computes sovereign entity health scores from soul.yaml fields.

Part of R39 (Agent Fleet Health Dashboard). Design per AGENTS.md §8.8.

M1 AnyIO: No asyncio — pure dict operations.
M11 Soul Integrity: Scores computed from persisted soul.yaml + proposed_lessons.yaml.
M13 Temple-Grade: Transparent weighted scoring with breakdown.

Usage:
    from soul_health_scorer import SoulHealthScorer, compute_fleet_health
    scorer = SoulHealthScorer(entity_data)
    health = scorer.compute()
    fleet = compute_fleet_health(entity_datas)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SoulHealthScorer:
    """
    Computes a composite health score (0-100) from entity soul.yaml fields.

    The score combines 6 dimensions with transparent weights:
        - soul_version:     Recency of soul architecture (newer = more maintained)
        - hierarchy_level:  Depth in the sovereign hierarchy (deeper = more structured)
        - sovereignty_level: Authority level (higher = more important)
        - lessons_count:    Number of L3 principles (more = more gnosis)
        - last_updated:     Recency of last update (recent = alive)
        - entity_name:      Named entities = intentional design
    """

    WEIGHTS = {
        "entity_name": 0.25,       # Identity: named entities = intentional (most basic)
        "soul_version": 0.20,      # Recency: newer = more maintained
        "hierarchy_level": 0.15,   # Depth: deeper = more structured
        "sovereignty_level": 0.15, # Authority: higher = more important
        "lessons_count": 0.15,     # Knowledge: more L3 principles = more gnosis
        "last_updated": 0.10,      # Activity: recent updates = alive
    }

    def __init__(self, entity_data: Dict[str, Any]):
        self.entity_data = entity_data
        self.score: float = 0.0
        self.breakdown: Dict[str, Any] = {}

    def compute(self) -> float:
        """Compute composite health score (0-100)."""
        scores: Dict[str, float] = {}

        # --- soul_version: newer versions score higher ---
        sv = self.entity_data.get("soul_version", "0.0")
        try:
            v = float(str(sv).replace("v", "").replace("'", ""))
            scores["soul_version"] = min(v * 10, 25.0)  # v7.1 → 71 → capped at 25
        except (ValueError, AttributeError):
            scores["soul_version"] = 0.0
            self.breakdown["soul_version"] = "missing/invalid"

        # --- hierarchy_level: deeper = more structured ---
        hl = self.entity_data.get("hierarchy_level", 0)
        try:
            hl_val = float(hl)
        except (ValueError, TypeError):
            hl_val = 0.0
        scores["hierarchy_level"] = min(hl_val * 10, 25.0)  # level 3 → 30 → capped at 25

        # --- sovereignty_level: higher = more important ---
        sl = self.entity_data.get("sovereignty_level", 0)
        try:
            sl_val = float(sl)
        except (ValueError, TypeError):
            sl_val = 0.0
        scores["sovereignty_level"] = min(sl_val * 5, 25.0)  # level 7 → 35 → capped at 25

        # --- lessons_count: more L3 principles = more gnosis ---
        lc = len(self.entity_data.get("lessons_learned", []))
        scores["lessons_count"] = min(lc * 5, 25.0)  # 5 lessons → 25

        # --- last_updated: recent = alive ---
        lu = self.entity_data.get("last_updated", "")
        if lu:
            try:
                dt = datetime.fromisoformat(str(lu).replace("Z", "+00:00"))
                days_old = (datetime.now(timezone.utc) - dt).days
                scores["last_updated"] = max(0.0, 25.0 - days_old // 7)  # decays over weeks
            except (ValueError, TypeError):
                scores["last_updated"] = 5.0  # default moderate
                self.breakdown["last_updated"] = "invalid timestamp"
        else:
            scores["last_updated"] = 0.0
            self.breakdown["last_updated"] = "missing"

        # --- entity_name: named entities = intentional ---
        # After load_entity_data(), entity.name is merged to top level as "name"
        name = self.entity_data.get("name", "")
        if not name:
            # Fallback: check nested entity block
            en = self.entity_data.get("entity", {})
            if isinstance(en, dict):
                name = en.get("name", "")
        scores["entity_name"] = 25.0 if name else 0.0

        # Compute weighted composite
        self.score = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        self.breakdown = scores
        return round(self.score, 2)


def compute_fleet_health(entity_datas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute fleet-wide health metrics.

    Fleet average is weighted by sovereignty_level (higher sovereignty = more weight).
    """
    scores: List[float] = []
    for ed in entity_datas:
        scorer = SoulHealthScorer(ed)
        scores.append(scorer.compute())

    # Weight by sovereignty_level for fleet average
    weighted_sum = 0.0
    total_weight = 0.0
    for i, ed in enumerate(entity_datas):
        sl = ed.get("sovereignty_level", 0) or 1  # avoid divide by zero
        try:
            sl_val = float(sl)
        except (ValueError, TypeError):
            sl_val = 1.0
        weighted_sum += scores[i] * sl_val
        total_weight += sl_val

    fleet_avg = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0

    # Count entities by health tier
    critical = sum(1 for s in scores if s >= 80)
    high = sum(1 for s in scores if 60 <= s < 80)
    medium = sum(1 for s in scores if 40 <= s < 60)
    low = sum(1 for s in scores if s < 40)

    # Per-entity breakdown
    entity_breakdown: Dict[str, Any] = {}
    for i, ed in enumerate(entity_datas):
        scorer = SoulHealthScorer(ed)
        scorer.compute()
        en = ed.get("entity", {})
        name = en.get("name", f"entity_{i}") if isinstance(en, dict) else f"entity_{i}"
        entity_breakdown[name] = {
            "score": scorer.score,
            "breakdown": scorer.breakdown,
        }

    return {
        "fleet_health_score": fleet_avg,
        "entity_count": len(scores),
        "critical_entities": critical,
        "high_entities": high,
        "medium_entities": medium,
        "low_entities": low,
        "entity_breakdown": entity_breakdown,
        "average_raw_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
    }


def load_entity_data(soul_path: Path) -> Dict[str, Any]:
    """Load entity data from soul.yaml, handling missing fields gracefully."""
    import yaml

    try:
        with open(soul_path) as f:
            data = yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}

    # Flatten entity block to top level for scorer
    entity = data.get("entity", {})
    if isinstance(entity, dict):
        merged = dict(entity)
    elif isinstance(entity, str):
        # entity: "name" (string form)
        merged = {"name": entity}
    else:
        merged = {}

    # Add top-level fields
    for key in ("soul_version", "hierarchy_level", "sovereignty_level",
                "lessons_learned", "last_updated", "version", "name"):
        if key in data and key not in merged:
            merged[key] = data[key]

    # Handle legacy 'lessons' field
    if "lessons" in data and "lessons_learned" not in merged:
        merged["lessons_learned"] = data["lessons"]

    # Handle 'metadata.health_score' if present
    metadata = data.get("metadata", {})
    if isinstance(metadata, dict) and "health_score" in metadata:
        merged["health_score"] = metadata["health_score"]

    return merged


if __name__ == "__main__":
    # Demo: scan all entity soul.yaml files
    entities_dir = Path("/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities")
    entity_datas: List[Dict[str, Any]] = []

    for soul_path in entities_dir.glob("*/soul.yaml"):
        entity_data = load_entity_data(soul_path)
        if entity_data:
            entity_datas.append(entity_data)

    fleet = compute_fleet_health(entity_datas)
    print(json.dumps(fleet, indent=2, default=str))
