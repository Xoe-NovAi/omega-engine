# 🔱 Omega Engine — DPO Logging Infrastructure
# AP: AP-DPO-LOGGER-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ dpo_logger ⬡ D16-2
#
# Sovereign DPO training data collection with tripartite reward signal.
# All data passes through PII masking before persistence (M7/M8 compliance).

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum
import anyio

from omega.oracle.pii_masker import PIIMasker

logger = logging.getLogger(__name__)


class RewardSource(str, Enum):
    """Source of the reward signal for DPO pair generation."""
    ENVIRONMENTAL = "environmental"      # Test pass/fail, build success, runtime metrics
    COUNCIL = "council"                  # Oversoul evaluation (Ma'at/Lilith/Kali rejection)
    USER = "user"                        # Direct user correction/preference


class ResonanceMode(str, Enum):
    """DPO data collection mode per D16-2."""
    DISABLED = "disabled"
    EXPLICIT = "explicit"      # User explicitly marks chosen/rejected
    IMPLICIT = "implicit"      # Auto-infer from interaction patterns
    HYBRID = "hybrid"          # Both explicit and implicit


@dataclass
class DPORecord:
    """Single DPO training record in standard format."""
    prompt: str
    chosen: str
    rejected: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Lineage tracking
    lineage_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    entity_name: Optional[str] = None
    
    # Reward signals
    reward_source: Optional[RewardSource] = None
    reward_details: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Schema version for migration
    schema_version: int = 2
    
    def to_jsonl(self) -> str:
        """Serialize to JSONL line."""
        data = asdict(self)
        # Convert enums to strings
        if self.reward_source:
            data["reward_source"] = self.reward_source.value
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_jsonl(cls, line: str) -> "DPORecord":
        """Deserialize from JSONL line."""
        data = json.loads(line)
        if "reward_source" in data and data["reward_source"]:
            data["reward_source"] = RewardSource(data["reward_source"])
        return cls(**data)


@dataclass
class DPOManifestEntry:
    """Manifest entry for reproducibility (per training_setup_logs pattern)."""
    file_path: str
    sha256: str
    record_count: int
    created_at: str
    lineage_ids: List[str]
    schema_version: int = 2


class DPORecorder:
    """
    Sovereign DPO Training Data Recorder.
    
    Collects prompt/chosen/rejected triples from three reward sources:
    1. Environmental — test results, build status, runtime metrics
    2. Council — Oversoul evaluations (Ma'at/Lilith/Kali)
    3. User — Direct corrections, thumbs up/down, edits
    
    All data passes through PII masking before write (M7/M8).
    JSONL files with time-based rotation (per ChunkHashLogger pattern).
    """
    
    def __init__(
        self,
        output_dir: str = "data/training/dpo",
        rotation_interval_sec: int = 6 * 3600,  # 6 hours
        max_files: int = 100,
        queue_capacity: int = 10000,
        pii_masker: Optional[PIIMasker] = None,
        resonance_mode: ResonanceMode = ResonanceMode.DISABLED,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rotation_interval_sec = rotation_interval_sec
        self.max_files = max_files
        self.queue_capacity = queue_capacity
        self.pii_masker = pii_masker or PIIMasker()
        self.resonance_mode = resonance_mode
        
        # Async write queue
        self._send_stream, self._receive_stream = anyio.create_memory_object_stream(max_buffer_size=queue_capacity)
        self._cancel_scope: Optional[anyio.CancelScope] = None
        self._shutdown = False
        
        # Current file handle
        self._current_handle = None
        self._current_file_opened_at = 0.0
        self._current_file_path = None
        self._current_model_name = ""
        
        # Manifest for reproducibility
        self._manifest: List[DPOManifestEntry] = []
        self._manifest_path = self.output_dir / "manifest.json"
        self._load_manifest()
        
    def _load_manifest(self) -> None:
        """Load existing manifest if present."""
        if self._manifest_path.exists():
            try:
                with open(self._manifest_path) as f:
                    data = json.load(f)
                    self._manifest = [DPOManifestEntry(**entry) for entry in data]
            except Exception as e:
                logger.warning(f"Failed to load DPO manifest: {e}")
                self._manifest = []
                
    def _save_manifest(self) -> None:
        """Save manifest to disk."""
        try:
            with open(self._manifest_path, "w") as f:
                json.dump([asdict(entry) for entry in self._manifest], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save DPO manifest: {e}")
            
    async def start(self, task_group: Optional[anyio.abc.TaskGroup] = None) -> None:
        """Start the background writer task.
        
        If a task_group is provided, spawns the writer into it (structured concurrency).
        Otherwise, defers writing until a task_group is available via start_with_group().
        
        Args:
            task_group: Optional AnyIO task group for structured concurrency.
        """
        if task_group is not None:
            self._cancel_scope = task_group.cancel_scope
            task_group.start_soon(self._writer_loop)
            logger.info("DPORecorder started: %s", self.output_dir)
        else:
            # Defer: writer will be started when start_with_group() is called
            logger.info("DPORecorder initialized (deferred start): %s", self.output_dir)
            
    async def start_with_group(self, task_group: anyio.abc.TaskGroup) -> None:
        """Start the background writer within a structured task group.
        
        Call this when a task_group becomes available after deferred initialization.
        """
        if self._cancel_scope is None:
            self._cancel_scope = task_group.cancel_scope
            task_group.start_soon(self._writer_loop)
            logger.info("DPORecorder background writer started: %s", self.output_dir)
            
    async def stop(self) -> None:
        """Stop the background writer and flush queue."""
        self._shutdown = True
        if self._cancel_scope is not None:
            self._cancel_scope.cancel()
            self._cancel_scope = None
        self._close_current_file()
        self._save_manifest()
        logger.info("DPORecorder stopped")
        
    def _get_current_file_path(self, model_name: str = "") -> Path:
        """Generate current file path with timestamp and model name."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        model_suffix = f"_{model_name}" if model_name else ""
        return self.output_dir / f"dpo_pairs_{timestamp}{model_suffix}.jsonl"
        
    def _needs_rotation(self, now: float, model_name: str) -> bool:
        """Check if current file needs rotation."""
        if self._current_handle is None:
            return True
        elapsed = now - self._current_file_opened_at
        if elapsed >= self.rotation_interval_sec:
            return True
        if model_name and self._current_model_name and model_name != self._current_model_name:
            return True
        return False
        
    def _rotate_file(self, now: float, model_name: str) -> None:
        """Rotate to a new JSONL file."""
        self._close_current_file()
        
        self._current_file_path = self._get_current_file_path(model_name)
        self._current_handle = open(self._current_file_path, "a", encoding="utf-8")
        self._current_file_opened_at = now
        self._current_model_name = model_name
        
        logger.info(f"DPO log rotated: {self._current_file_path.name}")
        
    def _close_current_file(self) -> None:
        """Close current file and update manifest."""
        if self._current_handle:
            self._current_handle.close()
            self._current_handle = None
            
        if self._current_file_path and self._current_file_path.exists():
            # Calculate SHA256 and record count
            import hashlib
            sha256 = hashlib.sha256()
            record_count = 0
            lineage_ids = []
            
            with open(self._current_file_path, "rb") as f:
                for line in f:
                    sha256.update(line)
                    record_count += 1
                    try:
                        data = json.loads(line)
                        if "lineage_id" in data:
                            lineage_ids.append(data["lineage_id"])
                    except Exception:
                        pass
                        
            entry = DPOManifestEntry(
                file_path=str(self._current_file_path),
                sha256=sha256.hexdigest(),
                record_count=record_count,
                created_at=datetime.now(timezone.utc).isoformat(),
                lineage_ids=lineage_ids,
            )
            self._manifest.append(entry)
            
            # Enforce max_files retention
            if len(self._manifest) > self.max_files:
                # Remove oldest files
                while len(self._manifest) > self.max_files:
                    oldest = self._manifest.pop(0)
                    try:
                        Path(oldest.file_path).unlink(missing_ok=True)
                    except Exception:
                        pass
                        
            self._save_manifest()
            
    async def _writer_loop(self) -> None:
        """Background writer loop - processes queue and writes to JSONL."""
        async with self._receive_stream:
            async for entry in self._receive_stream:
                if self._shutdown:
                    break
                await self._write_entry(entry)
                
    async def _write_entry(self, record: DPORecord) -> None:
        """Write a single DPO record to current JSONL file."""
        now = time.time()
        model_name = record.metadata.get("model_name", "")
        
        if self._needs_rotation(now, model_name):
            self._rotate_file(now, model_name)
            
        if self._current_handle:
            # Apply PII masking to the record before writing
            masked_record = await self._mask_record(record)
            line = masked_record.to_jsonl() + "\n"
            self._current_handle.write(line)
            self._current_handle.flush()
            
    async def _mask_record(self, record: DPORecord) -> DPORecord:
        """Apply PII masking to DPO record fields."""
        # Mask prompt, chosen, rejected
        masked_prompt, _, token_map = await self.pii_masker.process_system_prompt(
            system_prompt="",  # No system prompt in DPO record
            user_query=record.prompt,
            provider_name="local",  # DPO data always stored locally
        )
        
        masked_chosen = await self.pii_masker.process_response(record.chosen, token_map)
        masked_rejected = await self.pii_masker.process_response(record.rejected, token_map)
        
        # Create masked copy
        masked = DPORecord(
            prompt=masked_prompt,
            chosen=masked_chosen,
            rejected=masked_rejected,
            metadata=record.metadata.copy(),
            lineage_id=record.lineage_id,
            trace_id=record.trace_id,
            session_id=record.session_id,
            entity_name=record.entity_name,
            reward_source=record.reward_source,
            reward_details=record.reward_details.copy(),
            created_at=record.created_at,
            schema_version=record.schema_version,
        )
        return masked
        
    async def record(
        self,
        prompt: str,
        chosen: str,
        rejected: str,
        reward_source: RewardSource,
        reward_details: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        entity_name: Optional[str] = None,
        model_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record a DPO preference pair.
        
        Returns the lineage_id for tracking.
        """
        if self.resonance_mode == ResonanceMode.DISABLED:
            return ""
            
        record = DPORecord(
            prompt=prompt,
            chosen=chosen,
            rejected=rejected,
            reward_source=reward_source,
            reward_details=reward_details or {},
            trace_id=trace_id,
            session_id=session_id,
            entity_name=entity_name,
            metadata=metadata or {},
        )
        
        if model_name:
            record.metadata["model_name"] = model_name
            
        # Non-blocking enqueue
        try:
            await self._send_stream.send(record)
        except anyio.WouldBlock:
            logger.warning("DPO recorder queue full, dropping record")
            
        return record.lineage_id
        
    # ── Convenience methods for each reward source ─────────────────────────
    
    async def record_environmental(
        self,
        prompt: str,
        chosen: str,
        rejected: str,
        test_passed: bool,
        test_name: str,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        entity_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        """Record from environmental feedback (test pass/fail)."""
        return await self.record(
            prompt=prompt,
            chosen=chosen,
            rejected=rejected,
            reward_source=RewardSource.ENVIRONMENTAL,
            reward_details={
                "test_passed": test_passed,
                "test_name": test_name,
            },
            trace_id=trace_id,
            session_id=session_id,
            entity_name=entity_name,
            model_name=model_name,
        )
        
    async def record_council(
        self,
        prompt: str,
        chosen: str,
        rejected: str,
        oversoul: str,  # "maat" | "lilith" | "kali"
        verdict: str,   # "approved" | "rejected" | "deferred"
        reason: str,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        entity_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        """Record from Council evaluation (Oversoul verdict)."""
        return await self.record(
            prompt=prompt,
            chosen=chosen,
            rejected=rejected,
            reward_source=RewardSource.COUNCIL,
            reward_details={
                "oversoul": oversoul,
                "verdict": verdict,
                "reason": reason,
            },
            trace_id=trace_id,
            session_id=session_id,
            entity_name=entity_name,
            model_name=model_name,
        )
        
    async def record_user(
        self,
        prompt: str,
        chosen: str,
        rejected: str,
        feedback_type: str,  # "thumbs_up" | "thumbs_down" | "edit" | "correction"
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        entity_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        """Record from explicit user feedback."""
        return await self.record(
            prompt=prompt,
            chosen=chosen,
            rejected=rejected,
            reward_source=RewardSource.USER,
            reward_details={
                "feedback_type": feedback_type,
            },
            trace_id=trace_id,
            session_id=session_id,
            entity_name=entity_name,
            model_name=model_name,
        )
        
    # ── Implicit inference from interaction patterns ───────────────────────
    
    async def infer_from_interaction(
        self,
        query: str,
        response: str,
        trace_id: str,
        session_id: str,
        entity_name: str,
        model_name: str,
        follow_up_query: Optional[str] = None,
        follow_up_response: Optional[str] = None,
    ) -> Optional[str]:
        """
        Infer DPO pair from interaction patterns (implicit mode).
        
        Heuristics:
        - User re-phrases same query → original response was rejected
        - User says "no, do X instead" → correction pair
        - User continues conversation naturally → chosen pair
        """
        if self.resonance_mode not in [ResonanceMode.IMPLICIT, ResonanceMode.HYBRID]:
            return None
            
        if not follow_up_query:
            return None
            
        # Simple heuristic: if follow-up is a correction/clarification
        correction_indicators = [
            "no,", "actually,", "instead,", "rather,", "correct",
            "that's wrong", "not what i meant", "try again",
            "do it differently", "change", "fix"
        ]
        
        follow_up_lower = follow_up_query.lower()
        is_correction = any(ind in follow_up_lower for ind in correction_indicators)
        
        if is_correction and follow_up_response:
            # Original response was rejected, follow-up response is chosen
            return await self.record(
                prompt=query,
                chosen=follow_up_response,
                rejected=response,
                reward_source=RewardSource.USER,
                reward_details={
                    "feedback_type": "implicit_correction",
                    "inferred": True,
                },
                trace_id=trace_id,
                session_id=session_id,
                entity_name=entity_name,
                model_name=model_name,
            )
        elif not is_correction:
            # Natural continuation → chosen
            return await self.record(
                prompt=query,
                chosen=response,
                rejected="",  # No explicit rejection
                reward_source=RewardSource.USER,
                reward_details={
                    "feedback_type": "implicit_continuation",
                    "inferred": True,
                },
                trace_id=trace_id,
                session_id=session_id,
                entity_name=entity_name,
                model_name=model_name,
            )
            
        return None
        
    def get_stats(self) -> Dict[str, Any]:
        """Get recorder statistics."""
        total_records = sum(entry.record_count for entry in self._manifest)
        return {
            "output_dir": str(self.output_dir),
            "total_files": len(self._manifest),
            "total_records": total_records,
            "current_file": str(self._current_file_path) if self._current_file_path else None,
            "queue_size": self._send_stream.statistics().current_buffer_used if hasattr(self._send_stream, 'statistics') else "unknown",
            "resonance_mode": self.resonance_mode.value,
            "rotation_interval_hours": self.rotation_interval_sec / 3600,
        }


# Global instance
_dpo_recorder: Optional[DPORecorder] = None


def get_dpo_recorder() -> DPORecorder:
    """Get or create the global DPORecorder instance."""
    global _dpo_recorder
    if _dpo_recorder is None:
        # Read resonance mode from config
        mode_str = os.environ.get("OMEGA_RESONANCE_MODE", "disabled")
        try:
            mode = ResonanceMode(mode_str)
        except ValueError:
            mode = ResonanceMode.DISABLED
            
        _dpo_recorder = DPORecorder(resonance_mode=mode)
    return _dpo_recorder


async def initialize_dpo_recorder() -> DPORecorder:
    """Initialize and start the DPO recorder."""
    recorder = get_dpo_recorder()
    await recorder.start()
    return recorder


async def shutdown_dpo_recorder() -> None:
    """Shutdown the DPO recorder."""
    global _dpo_recorder
    if _dpo_recorder:
        await _dpo_recorder.stop()
        _dpo_recorder = None