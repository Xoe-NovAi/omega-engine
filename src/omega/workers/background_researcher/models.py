# 🔱 Omega Engine — Background Researcher Data Models
# AP: AP-BACKGROUND-RESEARCHER-MODELS-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ sovereign ⬡ models ⬡ WORKER

from __future__ import annotations

import json
import heapq
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass(order=True)
class ResearchTask:
    """A single research topic with full lifecycle state tracking."""

    topic: str
    priority: float = 0.5
    depth: int = 1                     # 1=light, 2=standard, 3=deep
    state: str = "pending"             # pending|triaged|searched|extracted|distilled|done|skip|defer|defer_max
    sources: list[str] = field(default_factory=list, compare=False)
    claims: list[str] = field(default_factory=list, compare=False)
    verification_count: int = field(default=0, compare=False)
    attempts: int = field(default=0, compare=False)
    max_attempts: int = 3
    session_id: str = field(default="", compare=False)
    created: str = field(default="", compare=False)
    last_attempt: str | None = field(default=None, compare=False)
    error: str | None = field(default=None, compare=False)

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now(timezone.utc).isoformat()
        if not self.session_id:
            slug = self.topic[:20].replace(" ", "_").replace("/", "_")
            self.session_id = f"res_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{slug}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ResearchTask:
        return cls(**data)


@dataclass
class TriageResult:
    """Fast assessment from Qwen3-1.7B — is this worth Gemma's time?"""

    score: float = 0.0                  # 0.0-1.0
    depth_plan: int = 1                 # 1=light, 2=standard, 3=deep
    reason: str = ""
    skip: bool = False

    @classmethod
    def from_json(cls, raw: str) -> TriageResult:
        try:
            data = json.loads(raw)
            return cls(
                score=float(data.get("score", 0.0)),
                depth_plan=int(data.get("depth_plan", 1)),
                reason=str(data.get("reason", "")),
                skip=bool(data.get("skip", False)),
            )
        except (json.JSONDecodeError, ValueError, TypeError):
            return cls(score=0.3, depth_plan=1, reason="Failed to parse triage", skip=True)


@dataclass
class GnosisPacket:
    """The distilled output from a research cycle — L1/L2/L3 abstractions."""

    topic: str
    claims: list[dict] = field(default_factory=list)
    distillations: list[dict] = field(default_factory=list)
    convergence_signal: str = "inconclusive"   # verified|contradictory|inconclusive
    recommendation: str = "skip"               # write_to_soul|write_to_knowledge|flag_for_human|skip
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RotationState:
    """Tracks the state of the scheduled topic rotation."""
    current_topic_index: int = 0
    cycle_count: int = 0
    last_rotation: str = "" # ISO timestamp
    consecutive_count: int = 0
    deepening_level: int = 1

class EnhancedPriorityQueue:
    """Weighted fair priority queue to prevent starvation.
    
    Strategy:
        - High Priority Queue (HPQ): For user-requested or critical gaps.
        - Normal Priority Queue (NPQ): For scheduled topics and frontier discovery.
        - Weighted Fair: Dequeue 2 from HPQ for every 1 from NPQ.
    """
    def __init__(self, weight_ratio: tuple[int, int] = (2, 1)):
        self._high_priority: list[tuple[float, int, ResearchTask]] = []
        self._normal_priority: list[tuple[float, int, ResearchTask]] = []
        self._seq = 0
        self._weight_ratio = weight_ratio  # (high, normal)
        self._current_weight_count = 0
        self._current_queue = "high"

    def enqueue(
        self,
        topic: str,
        base_priority: float = 0.5,
        user_requested: bool = False,
        gap_multiplier: float = 1.0,
        current_depth: float = 5.0,
    ) -> ResearchTask:
        """Add a task with computed priority."""
        # Simple priority for the heap
        priority = base_priority * gap_multiplier
        task = ResearchTask(topic=topic, priority=priority)
        self._seq += 1
        
        if user_requested:
            heapq.heappush(self._high_priority, (-priority, self._seq, task))
        else:
            heapq.heappush(self._normal_priority, (-priority, self._seq, task))
        return task

    def dequeue(self) -> ResearchTask | None:
        """Get the next task using weighted fair scheduling."""
        if not self._high_priority and not self._normal_priority:
            return None

        high_weight, normal_weight = self._weight_ratio
        
        # We use a loop to ensure we return a task if any queue is non-empty
        # This handles the case where we switch queues but the target queue is empty
        while True:
            if self._current_queue == "high":
                if self._high_priority and self._current_weight_count < high_weight:
                    self._current_weight_count += 1
                    _, _, task = heapq.heappop(self._high_priority)
                    return task
                # Weight exhausted or queue empty -> switch to normal
                self._current_queue = "normal"
                self._current_weight_count = 0
            elif self._current_queue == "normal":
                if self._normal_priority and self._current_weight_count < normal_weight:
                    self._current_weight_count += 1
                    _, _, task = heapq.heappop(self._normal_priority)
                    return task
                # Weight exhausted or queue empty -> switch to high
                self._current_queue = "high"
                self._current_weight_count = 0
            else:
                # Should never happen, but reset to high as fallback
                self._current_queue = "high"
                self._current_weight_count = 0

            # If we've switched queues and still no task returned, loop again
            # This handles the case where one queue is empty and we need to check the other
            # But we must avoid infinite loops if both queues are empty
            if not self._high_priority and not self._normal_priority:
                return None

        high_weight, normal_weight = self._weight_ratio
        
        # Try to satisfy the current queue's weight
        if self._current_queue == "high":
            if self._high_priority and self._current_weight_count < high_weight:
                self._current_weight_count += 1
                _, _, task = heapq.heappop(self._high_priority)
                return task
            # Weight exhausted or queue empty -> switch to normal
            self._current_queue = "normal"
            self._current_weight_count = 0
            
        # If we switched to normal or were already in normal
        if self._current_queue == "normal":
            if self._normal_priority and self._current_weight_count < normal_weight:
                self._current_weight_count += 1
                _, _, task = heapq.heappop(self._normal_priority)
                return task
            # Weight exhausted or queue empty -> switch to high
            self._current_queue = "high"
            self._current_weight_count = 0
        
        # Final fallback: if we've cycled through and still haven't returned,
        # just take whatever is available to avoid returning None when queues aren't empty.
        if self._high_priority:
            _, _, task = heapq.heappop(self._high_priority)
            return task
        if self._normal_priority:
            _, _, task = heapq.heappop(self._normal_priority)
            return task
            
        return None

    def peek(self) -> ResearchTask | None:
        """View the highest priority task (from high queue if available)."""
        if self._high_priority:
            return self._high_priority[0][2]
        if self._normal_priority:
            return self._normal_priority[0][2]
        return None

    def __len__(self) -> int:
        return len(self._high_priority) + len(self._normal_priority)

    def is_empty(self) -> bool:
        return len(self) == 0

    def to_list(self) -> list[ResearchTask]:
        """Return all tasks sorted by priority."""
        all_items = sorted(self._high_priority + self._normal_priority, key=lambda x: x[0])
        return [item[2] for item in all_items]
