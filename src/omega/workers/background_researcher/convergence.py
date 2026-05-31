# 🔱 Omega Engine — Convergence Detection & Human Review
# AP: AP-BACKGROUND-RESEARCHER-CONVERGENCE-v1.0.0
# ⬡ OMEGA ⬡ MAAT ⬡ sovereign ⬡ convergence ⬡ WORKER
#
# Determines when a research topic is "deep enough" to stop.
# Flags contradictions for human review.

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import anyio

from .models import GnosisPacket, ResearchTask

logger = logging.getLogger(__name__)


class ConvergenceDetector:
    """Determines whether a topic has been researched deeply enough.

    Stopping conditions:
    1. 3+ independent sources agree → verified
    2. No new claims in 2 consecutive deep cycles → exhausted
    3. Contradictory sources → flag for human review
    4. Depth score >= threshold → converged
    """

    def __init__(self, review_path: Path = Path("data/research/pending_review.md")):
        self.review_path = review_path

    async def check(self, task: ResearchTask, gnosis: GnosisPacket) -> bool:
        """Check if a topic has converged. Returns True if done."""
        signal = gnosis.convergence_signal
        claims = gnosis.claims
        verified = [c for c in claims if c.get("agreement_level", 0) >= 0.7]

        # Condition 1: Multi-source verification (2+ verified claims)
        if len(verified) >= 2 and signal == "verified":
            logger.info(f"Topic '{task.topic}' converged: verified by {len(verified)} claims")
            return True

        # Condition 2: No new claims in 2 consecutive deep cycles
        if task.verification_count >= 2 and len(claims) == 0:
            logger.info(f"Topic '{task.topic}' converged: no new claims")
            return True

        # Condition 3: Contradictory — human needs to adjudicate
        if signal == "contradictory":
            await self._flag_for_human(task, gnosis)
            return True  # Stop research, let human decide

        # Condition 4: Depth ceiling reached
        if task.depth >= 3 and task.verification_count >= 1:
            logger.info(f"Topic '{task.topic}' converged: depth ceiling")
            return True

        return False

    async def _flag_for_human(self, task: ResearchTask, gnosis: GnosisPacket) -> None:
        """Write contradictory findings to the human review queue."""
        timestamp = datetime.now(timezone.utc).isoformat()
        content = f"""
## Pending Review — {timestamp}
**Topic**: {task.topic}
**Session**: {task.session_id}

### Contradictory Claims:
```json
{json.dumps(gnosis.claims, indent=2)}
```

### Distillations:
```json
{json.dumps(gnosis.distillations, indent=2)}
```

### Recommendation: {gnosis.recommendation}

---
"""
        async with await anyio.open_file(str(self.review_path), "a") as f:
            await f.write(content)
        logger.info(f"Flagged '{task.topic}' for human review at {self.review_path}")
