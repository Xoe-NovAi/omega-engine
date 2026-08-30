# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-D283-MNEMOSYNE-v1.0.0
# 🔱 Sleep-Time Agent — Off-Critical-Path Consolidation
# ⬡ OMEGA ⬡ MEMORY ⬡ sleep_time.py
#
# Implements Letta 2026 sleep-time compute pattern:
# - Runs off critical path (no latency cost on primary responses)
# - Uses stronger model for consolidation
# - Natural consolidation window (user not waiting)
# - Deduplication, summarization, contradiction invalidation
#
# Safety Rules (Letta 2026):
# - Sleep-time agents = UNTRUSTED writers for Persona/Safety blocks
# - Require SECOND-AGENT REVIEW before committing to core identity blocks
# - Version blocks and surface diffs in trace

import logging
import anyio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .block_tools import BlockTools, BlockOperationResult
from .archival import ArchivalMemory, get_archival_memory
from .recall import RecallStore

logger = logging.getLogger(__name__)


@dataclass
class ConsolidationResult:
    """Result of a sleep-time consolidation cycle."""

    blocks_appended: Dict[str, str] = field(default_factory=dict)  # label -> status
    blocks_summarized: Dict[str, str] = field(default_factory=dict)
    archival_invalidated: int = 0
    contradictions_found: int = 0
    errors: List[str] = field(default_factory=list)


class SleepTimeAgent:
    """
    Off-critical-path consolidation agent.

    Per Letta 2026: A second agent that runs after user interaction to:
    1. Analyze conversation transcript for learned patterns
    2. Write to shared blocks (append-safe)
    3. Summarize near-limit blocks (exclusive access)
    4. Invalidate stale archival records
    5. Detect and flag contradictions

    Benefits:
    - No latency cost on primary responses
    - Stronger model allowed (no latency constraint)
    - Natural consolidation window
    - Deduplication + contradiction invalidation
    """

    def __init__(
        self,
        block_tools: BlockTools,
        archival: Optional[ArchivalMemory] = None,
        recall_store: Optional[RecallStore] = None,
        stronger_model: str = "gemma-4-31b",  # Or any stronger model
        review_agent: Optional["SleepTimeAgent"] = None,
        entity_name: str = "sleep_time_agent",
    ):
        self.tools = block_tools
        self.archival = archival or get_archival_memory()
        self.recall = recall_store
        self.stronger_model = stronger_model
        self.review_agent = review_agent
        self.entity_name = entity_name
        self._running = False
        self._task: Optional[anyio.abc.Task] = None

    async def consolidate(
        self,
        transcript: List[Dict[str, str]],  # [{"role": "user/assistant", "content": "..."}]
        requester_entity: str,
    ) -> ConsolidationResult:
        """
        Analyze transcript and write learned context to shared blocks.

        This is the main entry point called after a conversation turn or session.
        """
        result = ConsolidationResult()

        try:
            # 1. Extract learned patterns (would use stronger_model in production)
            learned = await self._extract_patterns(transcript)

            # 2. Write to appropriate blocks (append-safe)
            for block_label, content in learned.items():
                op_result = await self.tools.block_append(
                    label=block_label,
                    text=content,
                    requester_entity=requester_entity,
                )
                if op_result.success:
                    result.blocks_appended[block_label] = "appended"
                else:
                    result.errors.append(f"{block_label}: {op_result.error}")

            # 3. Summarize near-limit blocks (sleep-time exclusive)
            blocks = await self.tools.list_blocks(requester_entity)
            for block in blocks:
                if block.is_near_limit() and not block.read_only:
                    op_result = await self.tools.block_rethink(
                        label=block.label,
                        requester_entity=requester_entity,
                        summarizer_model=self.stronger_model,
                    )
                    if op_result.success:
                        result.blocks_summarized[block.label] = "summarized"
                    else:
                        result.errors.append(f"{block.label}_rethink: {op_result.error}")

            # 4. Invalidate stale archival records
            invalidated = await self._invalidate_stale_archival()
            result.archival_invalidated = invalidated

            # 5. Detect contradictions (placeholder - would use LLM in production)
            contradictions = await self._detect_contradictions(transcript, requester_entity)
            result.contradictions_found = len(contradictions)

            # 6. Run recall decay pass (power-law recalibration)
            if self.recall is not None:
                try:
                    decay_stats = await self.recall.decay_pass()
                    logger.info(
                        "Recall decay pass: %d turns across %d entities",
                        decay_stats.turns_updated,
                        decay_stats.entities_processed,
                    )
                    if decay_stats.errors:
                        for err in decay_stats.errors:
                            result.errors.append(f"decay_pass: {err}")
                except Exception as e:
                    logger.error(f"Recall decay pass failed: {e}")
                    result.errors.append(f"decay_pass: {str(e)}")

        except Exception as e:
            logger.error(f"Sleep-time consolidation failed: {e}", exc_info=True)
            result.errors.append(f"consolidation: {str(e)}")

        return result

    async def _extract_patterns(self, transcript: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Extract patterns from conversation transcript.

        In production, this would call the stronger_model LLM.
        For now, simple heuristic extraction.
        """
        patterns = {}

        for turn in transcript:
            content = turn.get("content", "").lower()
            role = turn.get("role", "")

            # Decisions
            if any(
                kw in content for kw in ["decided", "decision", "will ", "going to ", "plan to"]
            ):
                current = patterns.setdefault("decisions", "")
                patterns["decisions"] = current + f"\n{turn['content'][:500]}"

            # Failures/Errors
            if any(
                kw in content for kw in ["error", "failed", "bug", "issue", "problem", "broken"]
            ):
                current = patterns.setdefault("failures", "")
                patterns["failures"] = current + f"\n{turn['content'][:500]}"

            # Preferences
            if any(kw in content for kw in ["prefer", "like", "style", "convention", "format"]):
                current = patterns.setdefault("human", "")
                patterns["human"] = current + f"\n{turn['content'][:500]}"

            # Insights
            if any(
                kw in content for kw in ["insight", "realized", "learned", "discovered", "pattern"]
            ):
                current = patterns.setdefault("insights", "")
                patterns["insights"] = current + f"\n{turn['content'][:500]}"

        return patterns

    async def _invalidate_stale_archival(self) -> int:
        """
        Invalidate stale archival records.

        In production, would query vector store for records older than TTL
        with low retrieval scores and mark them inactive.
        """
        # Placeholder - would implement with actual archival store
        return 0

    async def _detect_contradictions(
        self,
        transcript: List[Dict[str, str]],
        requester_entity: str,
    ) -> List[Dict[str, Any]]:
        """
        Detect contradictions in transcript vs existing blocks.

        In production, would use LLM to compare new statements with
        existing block content and flag contradictions.
        """
        # Placeholder
        return []

    async def review_and_commit_core(
        self,
        block_label: str,
        proposed_value: str,
        requester_entity: str,
    ) -> BlockOperationResult:
        """
        Second-agent review for core identity blocks (persona, safety).

        Per Letta 2026: Sleep-time agents are UNTRUSTED writers for core blocks.
        Require second-agent review before committing.
        """
        if not self.review_agent:
            return BlockOperationResult(
                success=False, error="No review agent configured for core block commit"
            )

        # Review agent evaluates proposed change
        review = await self.review_agent._review_core_change(block_label, proposed_value)

        if review.get("approved", False):
            # Commit via replace (exclusive access)
            return await self.tools.block_replace(
                label=block_label,
                old_text="",  # Would need current value
                new_text=proposed_value,
                requester_entity=requester_entity,
            )
        else:
            return BlockOperationResult(
                success=False, error=f"Review rejected: {review.get('reason', 'unspecified')}"
            )

    async def _review_core_change(self, label: str, proposed: str) -> Dict[str, Any]:
        """Review agent evaluates proposed core block change."""
        # In production, would use LLM to evaluate
        # For now, simple heuristic
        return {
            "approved": len(proposed) > 10,
            "reason": "Auto-approved for demo" if len(proposed) > 10 else "Content too short",
        }

    # ── Background Task Management ────────────────────────────────────────────

    async def start_background(self, interval_seconds: int = 300) -> None:
        """Start periodic consolidation as background task."""
        if self._running:
            return

        self._running = True
        self._task = anyio.create_task_group().__aenter__()
        self._task.start_soon(self._background_loop, interval_seconds)
        logger.info(f"Sleep-time agent started (interval={interval_seconds}s)")

    async def stop_background(self) -> None:
        """Stop background consolidation."""
        self._running = False
        if self._task:
            await self._task.__aexit__(None, None, None)
            self._task = None
        logger.info("Sleep-time agent stopped")

    async def _background_loop(self, interval_seconds: int) -> None:
        """Background loop for periodic consolidation."""
        while self._running:
            try:
                # In production, would fetch recent transcript from MemoryStore
                # For now, just sleep
                await anyio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Sleep-time background loop error: {e}")
                await anyio.sleep(60)  # Back off on error


class DaatDaemon:
    """
    Da'at (Knowledge) Compaction Trigger — Mnemosyne's hidden sphere.

    Monitors memory pressure and triggers sleep-time consolidation when:
    - Core blocks near capacity (>85%)
    - Archival store exceeds size threshold
    - Time since last consolidation > threshold
    - Explicit trigger from Oracle

    Maps to Letta's sleep-time compute + Kabbalistic Da'at.
    """

    def __init__(
        self,
        block_tools: BlockTools,
        sleep_agent: SleepTimeAgent,
        recall_store: Optional[RecallStore] = None,
        check_interval_seconds: int = 60,
        core_block_threshold: float = 0.85,
        archival_size_threshold_mb: int = 500,
        max_consolidation_interval_hours: int = 24,
    ):
        self.tools = block_tools
        self.sleep_agent = sleep_agent
        self.recall = recall_store
        self.check_interval = check_interval_seconds
        self.core_threshold = core_block_threshold
        self.archival_threshold_mb = archival_size_threshold_mb
        self.max_interval_hours = max_consolidation_interval_hours
        self._running = False
        self._last_consolidation: Optional[datetime] = None
        self._task: Optional[anyio.abc.Task] = None

    async def start(self) -> None:
        """Start the Da'at daemon."""
        if self._running:
            return
        self._running = True
        self._task = anyio.create_task_group().__aenter__()
        self._task.start_soon(self._monitor_loop)
        logger.info("Da'at daemon started")

    async def stop(self) -> None:
        """Stop the Da'at daemon."""
        self._running = False
        if self._task:
            await self._task.__aexit__(None, None, None)
            self._task = None
        logger.info("Da'at daemon stopped")

    async def trigger_consolidation(
        self, transcript: List[Dict[str, str]], entity: str
    ) -> ConsolidationResult:
        """Explicit consolidation trigger (e.g., from Oracle on session end)."""
        self._last_consolidation = datetime.now(timezone.utc)
        result = await self.sleep_agent.consolidate(transcript, entity)
        # Also run recall decay pass if recall store is available
        if self.recall is not None:
            try:
                decay_stats = await self.recall.decay_pass()
                logger.info(
                    "Da'at recall decay pass: %d turns across %d entities",
                    decay_stats.turns_updated,
                    decay_stats.entities_processed,
                )
            except Exception as e:
                logger.error(f"Da'at recall decay pass failed: {e}")
        return result

    async def _monitor_loop(self) -> None:
        """Monitor memory pressure and trigger consolidation."""
        while self._running:
            try:
                await self._check_and_consolidate()
                await anyio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Da'at monitor error: {e}")
                await anyio.sleep(60)

    async def _check_and_consolidate(self) -> bool:
        """Check conditions and trigger consolidation if needed."""
        # Check core block capacity
        core_blocks = await self.tools.get_core_blocks(self.sleep_agent.entity_name)
        for block in core_blocks:
            if block.is_near_limit(self.core_threshold):
                logger.info(f"Da'at: Core block {block.label} near limit, triggering consolidation")
                return True

        # Check time since last consolidation
        if self._last_consolidation:
            elapsed_hours = (
                datetime.now(timezone.utc) - self._last_consolidation
            ).total_seconds() / 3600
            if elapsed_hours > self.max_interval_hours:
                logger.info(f"Da'at: {elapsed_hours:.1f}h since last consolidation, triggering")
                return True

        # Check archival size (placeholder)
        # archival_size = await self._get_archival_size_mb()
        # if archival_size > self.archival_threshold_mb:
        #     return True

        return False


# Convenience function for integration
async def create_sleep_time_system(
    entity_name: str,
    stronger_model: str = "gemma-4-31b",
) -> tuple[SleepTimeAgent, DaatDaemon]:
    """
    Create the complete sleep-time consolidation system for an entity.

    Creates a RecallStore and wires it into both SleepTimeAgent and DaatDaemon
    for automatic decay pass on every consolidation cycle.

    Returns:
        (SleepTimeAgent, DaatDaemon) tuple
    """
    from .recall import get_recall_store

    tools = BlockTools()
    recall = await get_recall_store()
    sleep_agent = SleepTimeAgent(
        block_tools=tools,
        recall_store=recall,
        stronger_model=stronger_model,
        entity_name=entity_name,
    )
    daat = DaatDaemon(
        block_tools=tools,
        sleep_agent=sleep_agent,
        recall_store=recall,
    )
    return sleep_agent, daat
