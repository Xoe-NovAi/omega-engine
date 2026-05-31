# 🔱 Omega Engine — Research Checkpoint Persistence
# AP: AP-BACKGROUND-RESEARCHER-CHECKPOINT-v1.0.0
# ⬡ OMEGA ⬡ ANUBIS ⬡ sovereign ⬡ checkpoint ⬡ WORKER
#
# Every state transition is checkpointed — the researcher resumes
# from exactly where it left off after any restart.

import json
import logging
from pathlib import Path
from typing import Optional

import anyio

from .models import ResearchTask

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages research task checkpoints on disk.

    Checkpoints are stored as JSON files in data/research/checkpoints/,
    one file per task session_id. This enables restart recovery.
    """

    def __init__(self, checkpoint_dir: Path = Path("data/research/checkpoints")):
        self.dir = checkpoint_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    async def save(self, task: ResearchTask) -> None:
        """Persist a task's state before every state transition."""
        path = self.dir / f"{task.session_id}.json"
        data = {
            "topic": task.topic,
            "priority": task.priority,
            "depth": task.depth,
            "state": task.state,
            "sources": task.sources,
            "claims": task.claims,
            "verification_count": task.verification_count,
            "attempts": task.attempts,
            "max_attempts": task.max_attempts,
            "session_id": task.session_id,
            "created": task.created,
            "last_attempt": task.last_attempt,
            "error": task.error,
        }
        # Write atomically via temp file + rename
        tmp = path.with_suffix(".tmp")
        await anyio.Path(tmp).write_text(json.dumps(data, indent=2))
        await anyio.to_thread.run_sync(lambda: tmp.replace(path))

    async def load_all_pending(self) -> list[ResearchTask]:
        """Load all unfinished tasks from checkpoints (restart recovery)."""
        tasks = []
        pattern = "*.json"
        for path in Path(self.dir).glob(pattern):
            if path.suffix == ".tmp":
                continue
            try:
                data = json.loads(path.read_text())
                if data["state"] not in ("done", "skip"):
                    task = ResearchTask.from_dict(data)
                    tasks.append(task)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning(f"Corrupted checkpoint {path.name}: {e}")
                continue
        logger.info(f"Loaded {len(tasks)} pending tasks from checkpoints")
        return tasks

    async def mark_done(self, task: ResearchTask) -> None:
        """Mark a task as done and save its final state."""
        task.state = "done"
        await self.save(task)

    async def mark_skip(self, task: ResearchTask) -> None:
        """Mark a task as skipped (low value)."""
        task.state = "skip"
        await self.save(task)

    async def mark_defer(self, task: ResearchTask) -> None:
        """Mark a task as deferred (no quota available)."""
        task.state = "defer"
        task.attempts += 1
        await self.save(task)

    def cleanup_old(self, max_age_days: int = 30) -> int:
        """Remove checkpoint files older than max_age_days. Returns count removed."""
        import time
        now = time.time()
        count = 0
        for path in Path(self.dir).glob("*.json"):
            if path.stat().st_mtime < now - (max_age_days * 86400):
                path.unlink()
                count += 1
        return count
