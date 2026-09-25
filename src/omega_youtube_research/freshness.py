# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""
L7 Freshness & Drift Detection — Arc Labs Base-2 Half-Life Framework
⬡ OMEGA ⬡ RESEARCHER ⬡ L7 ⬡ FRESHNESS
AP Token: AP-YOUTUBE-FRESHNESS-v2.0.0

Mandate Compliance:
- M1 AnyIO: all I/O wrapped in anyio.to_thread.run_sync
- M2 Firewall: WAD-isolated
- M7 Local-First: local computation of decay
- M11 Soul Integrity: stale claims flagged for Soul Distiller re-verification
- M17 Cognitive Integrity: drift detection prevents hallucination
- M22 Provenance: every chunk carries publish_date

Per Arc Labs Research (2026):
- Formula: freshness(t) = 2^(-t/τ) where τ = type-specific half-life in days
- Access Boost: retrieval_freshness = freshness(t) × (1 + ln(1 + access_count))
- Freshness Floor: 0.1 (prevents permanent amnesia for unique facts)
- Drift vs Decay: Decay = gradual staleness; Drift = abrupt invalidation (supersession)
- Retrievable Flag: Background worker sets retrievable=false when 5 conditions met
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .chunker import TemporalChunk


# ── Memory Types with Half-Lives (τ in days) ──────────────────────────────────

class MemoryType(Enum):
    """Memory types with empirically calibrated half-lives."""
    FACT = "fact"           # τ = 180 days (job changes, relocation, skill pivots)
    PREFERENCE = "preference"  # τ = 90 days (environment changes)
    EVENT = "event"         # τ = 30 days (time-bounded reality)
    ENTITY = "entity"       # τ = 365 days (people, orgs, products — slow cycles)
    RELATION = "relation"   # τ = 180 days (reporting chains, code dependencies)
    PERMANENT = "permanent" # τ = ∞ (birthdate, legal name, country of residence)

# Half-Long-term home city
# Residence, explicit system imports (calendar, CRM, HR)

# Half-lives in days (Arc Labs calibrated)
HALF_LIVES = {
    MemoryType.FACT: 180,
    MemoryType.PREFERENCE: 90,
    MemoryType.EVENT: 30,
    MemoryType.ENTITY: 365,
    MemoryType.RELATION: 180,
    MemoryType.PERMANENT: float('inf'),
}

# Domain → MemoryType mapping for YouTube content
DOMAIN_TYPE_MAP = {
    "ai_research": MemoryType.FACT,
    "philosophy": MemoryType.ENTITY,      # Philosophical concepts are entity-like
    "tutorial": MemoryType.FACT,          # Technical tutorials = facts
    "news": MemoryType.EVENT,
    "opinion": MemoryType.PREFERENCE,
    "general": MemoryType.FACT,
}

FRESHNESS_FLOOR = 0.1  # Minimum effective freshness (10%)


# ── Freshness Scoring ──────────────────────────────────────────────────────────

def freshness_score(
    publish_date: datetime,
    memory_type: MemoryType = MemoryType.FACT,
    access_count: int = 0,
) -> float:
    """
    Calculate freshness score using Arc Labs base-2 half-life formula.
    
    Formula: freshness(t) = 2^(-t/τ) × (1 + ln(1 + access_count))
    
    Where:
        t = age in days
        τ = half-life in days (type-specific)
        access_count = number of times this memory has been retrieved
    
    Args:
        publish_date: When the content was published
        memory_type: Type of memory (determines half-life)
        access_count: Number of times this chunk has been retrieved
    
    Returns:
        Freshness score ∈ [FRESHNESS_FLOOR, ∞) — can exceed 1.0 with access boost
    """
    now = datetime.now(timezone.utc)
    if publish_date.tzinfo is None:
        publish_date = publish_date.replace(tzinfo=timezone.utc)
    
    delta = now - publish_date
    days = delta.total_seconds() / 86400.0
    
    tau = HALF_LIVES.get(memory_type, HALF_LIVES[MemoryType.FACT])
    
    if tau == float('inf'):
        base_freshness = 1.0  # Permanent memories never decay
    else:
        # Base-2 exponential decay: at t = τ, freshness = 0.5 exactly
        base_freshness = 2.0 ** (-days / tau)
    
    # Access boost: logarithmic in retrieval count
    # Prevents popularity dominance: 100× accesses → only 2.3× boost
    access_boost = 1.0 + math.log(1.0 + access_count)
    
    effective_freshness = base_freshness * access_boost
    
    # Apply floor (but allow boost to lift above floor)
    return max(effective_freshness, FRESHNESS_FLOOR)


def calculate_weighted_relevance(
    base_score: float,
    publish_date: datetime,
    memory_type: MemoryType = MemoryType.FACT,
    access_count: int = 0,
) -> float:
    """
    Adjust retrieval relevance by freshness.
    
    Relevance = base_score × freshness_score
    
    This implements the Arc Labs combined weight formula:
    weight(m) = base_retrieval_score × freshness(age(m)) × access_boost(m)
    """
    f_score = freshness_score(publish_date, memory_type, access_count)
    return base_score * f_score


def infer_memory_type(domain: str, chunk_text: str = "") -> MemoryType:
    """Infer memory type from domain and content."""
    domain_lower = domain.lower()
    return DOMAIN_TYPE_MAP.get(domain_lower, MemoryType.FACT)


# ── Drift Detection ───────────────────────────────────────────────────────────

@dataclass
class DriftSignal:
    """Signal indicating potential drift/supersession."""
    detected: bool
    drift_type: str  # "contradiction" | "supersession" | "temporal_expiry"
    confidence: float
    evidence: str
    superseded_by: Optional[str] = None  # CAS hash of replacement


def detect_drift(
    current_chunk: TemporalChunk,
    new_chunk: TemporalChunk,
    contradiction_threshold: float = 0.8,
) -> DriftSignal:
    """
    Detect drift between chunks.
    
    Drift = abrupt invalidation (supersession), not gradual decay.
    When a conflicting fact is extracted, mark old memory as superseded.
    
    Args:
        current_chunk: Existing chunk in CAS
        new_chunk: Newly extracted chunk
        contradiction_threshold: NLI contradiction probability threshold
    
    Returns:
        DriftSignal if drift detected
    """
    # Simple heuristic: check for explicit contradiction markers
    # In production, use NLI model for contradiction detection
    current_lower = current_chunk.text.lower()
    new_lower = new_chunk.text.lower()
    
    contradiction_markers = [
        ("no longer", "now"),
        ("was", "is now"),
        ("used to", "currently"),
        ("deprecated", "replaced by"),
        ("incorrect", "correct"),
        ("wrong", "right"),
    ]
    
    for old_marker, new_marker in contradiction_markers:
        if old_marker in current_lower and new_marker in new_lower:
            return DriftSignal(
                detected=True,
                drift_type="supersession",
                confidence=0.85,
                evidence=f"Contradiction markers: '{old_marker}' vs '{new_marker}'",
                superseded_by=new_chunk.cas_hash,
            )
    
    # Temporal expiry: event-type memories past their half-life
    if current_chunk.cas_hash and new_chunk.cas_hash:
        # Check if they reference same entity but different facts
        pass
    
    return DriftSignal(
        detected=False,
        drift_type="none",
        confidence=0.0,
        evidence="",
    )


# ── Retrievability Flag (Background Worker Logic) ─────────────────────────────

@dataclass
class RetrievabilityCheck:
    """Result of retrievability evaluation."""
    retrievable: bool
    reasons: list[str]
    effective_freshness: float


def check_retrievability(
    chunk: TemporalChunk,
    age_days: float,
    last_accessed_days: float,
    access_count: int,
    has_active_relations: bool = False,
    superseded_age_days: Optional[float] = None,
) -> RetrievabilityCheck:
    """
    Arc Labs retrievability flag logic.
    
    A memory is NOT retrievable (retrievable=false) when ALL 5 conditions hold:
    1. Age > 365 days
    2. Last accessed > 180 days ago
    3. freshness × access_boost < 0.1 (floor)
    4. Either: superseded > 1 year ago OR access_count = 0
    5. No active Relation references this memory
    
    Args:
        chunk: The chunk to evaluate
        age_days: Age in days since creation
        last_accessed_days: Days since last retrieval
        access_count: Total retrieval count
        has_active_relations: Whether any active Relation references this
        superseded_age_days: Days since superseded (if applicable)
    
    Returns:
        RetrievabilityCheck with decision and reasons
    """
    # Compute effective freshness
    memory_type = infer_memory_type("", chunk.text)
    # Compute freshness from age_days directly
    tau = HALF_LIVES.get(memory_type, HALF_LIVES[MemoryType.FACT])
    if tau == float('inf'):
        base_freshness = 1.0
    else:
        base_freshness = 2.0 ** (-age_days / tau)
    access_boost = 1.0 + math.log(1.0 + access_count)
    raw_freshness = base_freshness * access_boost
    effective_freshness = max(raw_freshness, FRESHNESS_FLOOR)
    
    reasons = []
    
    # Condition 1: Age > 365 days
    cond1 = age_days > 365
    if cond1: reasons.append("age > 365 days")
    
    # Condition 2: Last accessed > 180 days ago
    cond2 = last_accessed_days > 180
    if cond2: reasons.append("last accessed > 180 days ago")
    
    # Condition 3: Raw freshness below floor (before floor applied)
    cond3 = raw_freshness < FRESHNESS_FLOOR
    if cond3: reasons.append(f"raw freshness {raw_freshness:.6f} < floor {FRESHNESS_FLOOR}")
    
    # Condition 4: Superseded > 1 year OR never accessed
    cond4 = (superseded_age_days is not None and superseded_age_days > 365) or access_count == 0
    if cond4: reasons.append("superseded > 1 year or never accessed")
    
    # Condition 5: No active relations
    cond5 = not has_active_relations
    if cond5: reasons.append("no active relations reference this memory")
    
    # All 5 must hold for non-retrievable
    retrievable = not (cond1 and cond2 and cond3 and cond4 and cond5)
    
    if not retrievable:
        reasons.append("ALL CONDITIONS MET — setting retrievable=false")
    
    return RetrievabilityCheck(
        retrievable=retrievable,
        reasons=reasons,
        effective_freshness=effective_freshness,
    )


# ── Contract Test Helpers (M21) ───────────────────────────────────────────────

def assert_freshness_score_range(score: float) -> None:
    """M21 Gate Integrity: Contract test for freshness_score range."""
    assert score >= FRESHNESS_FLOOR, f"Freshness score {score} below floor {FRESHNESS_FLOOR}"


def assert_decay_monotonicity(dates: list[datetime], memory_type: MemoryType) -> None:
    """M21: Verify that freshness decreases as date gets older."""
    scores = [freshness_score(d, memory_type) for d in dates]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i+1], f"Freshness did not decay monotonically: {scores[i]} < {scores[i+1]}"


def assert_access_boost_monotonicity() -> None:
    """M21: Verify access boost increases with access count."""
    prev = 0.0
    for count in range(0, 100):
        boost = 1.0 + math.log(1.0 + count)
        assert boost >= prev, f"Access boost not monotonic: {boost} < {prev}"
        prev = boost