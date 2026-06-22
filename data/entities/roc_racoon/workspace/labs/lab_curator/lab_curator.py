# 🔱 Lab Curator Worker (Prototype)
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ WORKER ⬡ LAB-CURATOR

import anyio
import logging
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Set

# Note: These imports assume the script is run with src/omega in PYTHONPATH
try:
    from omega.oracle import EntityRegistry, Orchestrator
    from omega.errors import OmegaError
except ImportError:
    # Fallback for lab-only execution
    class OmegaError(Exception): pass
    class EntityRegistry:
        def get(self, name): return None
        def list(self): return []
    class Orchestrator:
        async def spawn_background_worker(self, **kwargs): pass

# [id-soft: quake-1996] Zone-style tracking for processed posts
PROCESSED_LOG = Path("data/sovereign_labs/.processed_posts.log")

logger = logging.getLogger("omega.lab_curator")

class LabCurator:
    \"\"\"
    Background worker that monitors the Sovereign Lab Commons for new posts
    and dispatches review tasks to relevant entities.
    \"\"\"

    def __init__(self):
        self.registry = EntityRegistry()
        self.orchestrator = Orchestrator()
        self.labs_dir = Path("data/sovereign_labs/topics")

    async def run_cycle(self):
        \"\"\"A single pass of the curator: scan -> identify -> dispatch.\"\"\"
        logger.info("Starting Lab Curator cycle...")
        
        try:
            new_posts = await self._get_unprocessed_posts()
            if not new_posts:
                logger.info("No new lab posts found.")
                return

            for post_path in new_posts:
                await self._process_post(post_path)
                await self._mark_as_processed(post_path)

        except Exception as e:
            logger.error(f"Curator cycle failed: {e}", exc_info=True)

    async def _get_unprocessed_posts(self) -> List[Path]:
        \"\"\"Finds all posts in the labs directory that haven't been processed yet.\"\"\"
        if not self.labs_dir.exists():
            return []
        all_posts = list(self.labs_dir.rglob("*.md"))
        all_posts = [p for p in all_posts if "CHARTER.md" not in p.name]
        
        processed = set()
        if PROCESSED_LOG.exists():
            processed = set(PROCESSED_LOG.read_text().splitlines())

        return [p for p in all_posts if str(p) not in processed]

    async def _process_post(self, path: Path):
        \"\"\"Analyzes a post and dispatches review tasks.\"\"\"
        content = await anyio.to_thread.run_sync(path.read_text, encoding="utf-8")
        topic_slug = path.parent.name
        
        # 1. Explicit Review Requests (@entity)
        targets = set(re.findall(r"@([a-zA-Z0-9_]+)", content))
        
        # 2. Implicit Interest (Domain matching)
        if not targets:
            targets = self._find_interested_entities(topic_slug, content)

        if not targets:
            logger.info(f"No targets identified for post: {path.name}")
            return

        for entity_name in targets:
            await self._dispatch_review(entity_name, path, content)

    def _find_interested_entities(self, topic: str, content: str) -> Set[str]:
        \"\"\"Finds entities whose domains align with the topic or content.\"\"\"
        interested = set()
        entities = self.registry.list()
        
        for ent in entities:
            if any(domain.lower() in topic.lower() for domain in ent.domains):
                interested.add(ent.name)
            elif ent.name.lower() in content.lower():
                interested.add(ent.name)
        
        return interested

    async def _dispatch_review(self, entity: str, path: Path, content: str):
        \"\"\"Tasks an entity to review a post and reply.\"\"\"
        if not self.registry.get(entity):
            logger.warning(f"Target entity {entity} not found in registry. Skipping.")
            return

        prompt = (
            f"Sovereign Lab Review Request\\n"
            f"Topic: {path.parent.name}\\n"
            f"Post: {path.name}\\n"
            f"Path: {path}\\n\\n"
            f"Content:\\n{content}\\n\\n"
            f"Task: Please review this discovery/experiment. If it is valuable, "
            f"provide a critical analysis or a complementary insight. "
            f"Your response must be written to a new file in the same directory "
            f"following the format: RESPONSE_{datetime.now().strftime('%Y%m%d%H%M')}_{entity}.md"
        )

        try:
            await self.orchestrator.spawn_background_worker(
                task_id=f"lab_review_{entity}_{path.stem}",
                model=self.registry.get(entity).model,
                prompt=prompt,
                context="You are reviewing a post in the Sovereign Lab Commons."
            )
            logger.info(f"Dispatched review task to {entity} for {path.name}")
        except OmegaError as e:
            logger.error(f"Failed to dispatch review to {entity}: {e}")

    async def _mark_as_processed(self, path: Path):
        \"\"\"Records that a post has been processed to avoid duplicate dispatches.\"\"\"
        await anyio.to_thread.run_sync(
            lambda: PROCESSED_LOG.open("a", encoding="utf-8").write(f"{path}\\n")
        )

async def main():
    curator = LabCurator()
    await curator.run_cycle()

if __name__ == \"__main__\":
    import anyio
    anyio.run(main)
