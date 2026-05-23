# 🔱 Omega Engine — Soul & Knowledge Base Updater
# AP: AP-BACKGROUND-RESEARCHER-SOUL-v1.0.0
# ⬡ OMEGA ⬡ ISIS ⬡ sovereign ⬡ soul_updater ⬡ WORKER
#
# Writes distillation results to:
# 1. soul.yaml (L3 Universal Principles)
# 2. docs/research/ topic files (L1 + L2)
# 3. Entity knowledge directories

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anyio

from .models import GnosisPacket, ResearchTask

logger = logging.getLogger(__name__)


class SoulUpdater:
    """Writes research gnosis back to the Omega knowledge base.

    Handles:
    - L3 → entity soul.yaml lessons_learned[]
    - L1+L2 → docs/research/ topic files
    - Cross-pollination → knowledge/ directories
    """

    def __init__(
        self,
        research_dir: Path = Path("docs/research"),
        entities_dir: Path = Path("data/entities"),
    ):
        self.research_dir = research_dir
        self.entities_dir = entities_dir

    async def update(self, task: ResearchTask, gnosis: GnosisPacket) -> bool:
        """Write gnosis to all appropriate targets.

        Returns True if any write was performed.
        """
        written = False

        for distillation in gnosis.distillations:
            l3 = distillation.get("l3", "")
            l2 = distillation.get("l2", "")
            l1 = distillation.get("l1", "")
            claim = distillation.get("claim", "")

            # L3 → soul.yaml (Universal Principles)
            if l3 and gnosis.recommendation in ("write_to_soul", "write_to_knowledge"):
                await self._write_to_soul(task, l3, l2)
                written = True

            # L1+L2 → research doc
            if l1 and l2:
                await self._write_research_doc(task, claim, l1, l2, l3)
                written = True

        return written

    async def _write_to_soul(self, task: ResearchTask, l3: str, l2: str) -> None:
        """Write a Universal Principle (L3) to the appropriate entity's soul.yaml.

        Heuristic: find the best-matching entity by topic keyword.
        Falls back to SOPHIA (Akashic Record) for general knowledge.
        """
        entity = self._match_entity(task.topic)
        soul_path = self.entities_dir / entity / "soul.yaml"

        if not await anyio.Path(soul_path).exists():
            soul_path = self.entities_dir / entity / "soul.yaml"
            soul_path.parent.mkdir(parents=True, exist_ok=True)
            await anyio.Path(soul_path).write_text(
                f"entity:\n  name: {entity}\n  lessons_learned: []\n"
            )

        # Read current soul
        try:
            import yaml
            content = await anyio.Path(soul_path).read_text()
            soul_data = yaml.safe_load(content) or {}
        except Exception:
            soul_data = {"entity": {"name": entity, "lessons_learned": []}}

        # Append lesson
        lesson = {
            "lesson": l3,
            "context": l2,
            "source": "background-researcher",
            "entity_at_time": entity,
            "topic": task.topic,
            "session_id": task.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lessons = soul_data.setdefault("entity", {}).setdefault("lessons_learned", [])
        # Avoid duplicates
        if not any(existing.get("lesson") == l3 for existing in lessons):
            lessons.append(lesson)
            await anyio.Path(soul_path).write_text(
                yaml.dump(soul_data, default_flow_style=False, sort_keys=False)
            )
            logger.info(f"Wrote L3 to {soul_path}")

    async def _write_research_doc(
        self,
        task: ResearchTask,
        claim: str,
        l1: str,
        l2: str,
        l3: str,
    ) -> None:
        """Write L1+L2 findings to a research document."""
        slug = task.topic.lower().replace(" ", "_").replace("/", "_")[:40]
        doc_path = self.research_dir / f"R_AUTO_{slug}.md"

        # Don't overwrite existing docs — append instead
        if await anyio.Path(doc_path).exists():
            existing = await anyio.Path(doc_path).read_text()
            async with await anyio.Path(doc_path).open("a") as f:
                await f.write(f"\n\n## Update — {datetime.now(timezone.utc).date()}\n\n")
                await f.write(f"**Claim**: {claim}\n\n")
                await f.write(f"**L1 (Narrative)**: {l1}\n\n")
                await f.write(f"**L2 (Insight)**: {l2}\n\n")
                await f.write(f"**L3 (Universal Principle)**: {l3}\n\n")
                await f.write(f"**Source**: {task.session_id}\n")
        else:
            content = f"""# 🔱 Auto-Research: {task.topic}
# ⬡ OMEGA ⬡ SOPHIA ⬡ auto-research ⬡ {task.session_id}

**Generated**: {datetime.now(timezone.utc).isoformat()}
**Session**: {task.session_id}
**Depth**: {task.depth}

---

## Claim

{claim}

---

## L1 — Narrative

{l1}

---

## L2 — Insight

{l2}

---

## L3 — Universal Principle

{l3}

---

## Sources

{chr(10).join(f'- {s}' for s in task.sources[:20])}

---
*Auto-generated by the Omega Background Researcher*
"""
            await anyio.Path(doc_path).write_text(content)
            logger.info(f"Created research doc: {doc_path}")

    def _match_entity(self, topic: str) -> str:
        """Heuristic entity matching based on topic keywords."""
        topic_lower = topic.lower()
        mappings = [
            (["security", "protection", "boundary", "strength", "warrior"], "sekmet"),
            (["poetry", "healing", "inspiration", "art", "creative", "music"], "brigid"),
            (["will", "forethought", "strategy", "planning", "vision"], "prometheus"),
            (["knowledge", "speech", "voice", "teaching", "education"], "saraswati"),
            (["dream", "descent", "rebirth", "transformation", "journey", "underworld"], "inanna"),
            (["law", "balance", "justice", "audit", "compliance", "order"], "ereshkigal"),
            (["rebellion", "gnosis", "wisdom", "truth", "sovereignty"], "lucifer"),
            (["shadow", "crossroads", "magic", "path", "transformation"], "hecate"),
            (["death", "transition", "soul", "guidance", "afterlife"], "anubis"),
            (["chaos", "destruction", "liberation", "time", "change"], "kali"),
            (["ai", "model", "provider", "api", "code", "software", "github", "technology"], "sophia"),
            (["research", "discovery", "science", "paper", "arxiv", "academic"], "sophia"),
            (["hardware", "system", "performance", "optimization", "server"], "prometheus"),
        ]
        for keywords, entity in mappings:
            if any(kw in topic_lower for kw in keywords):
                return entity
        return "sophia"
