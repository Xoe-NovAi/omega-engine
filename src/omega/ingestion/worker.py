# AP: AP-INGESTION-WORKER-v1.0.0

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
import logging
import random
import anyio
import redis.asyncio as redis
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from omega.errors import OmegaError
from src.omega.oracle.resource_guard import ResourceGuard
from src.omega.ingestion.scraper import SovereignScraper
from src.omega.archive.cas import CASArchiver

# Forward reference for ResilienceContext to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.omega.ingestion.pipeline import ResilienceContext

logger = logging.getLogger("omega.ingestion.worker")

@dataclass
class CurationJob:
    job_id: str
    url: str
    tier: str
    domain_key: Optional[str] = None
    priority: int = 0
    retry_count: int = 0

class SovereignWorker:
    """
    Redis-backed background worker for the Omega Engine.
    Decouples high-latency deep crawls from the main Oracle loop.
    
    Sovereignty: Local Redis queue, ResourceGuard-throttled, Somatic Save-Points.
    """
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379", 
        queue_name: str = "curation_queue",
        resource_guard: Optional[ResourceGuard] = None,
        scraper: Optional[SovereignScraper] = None,
        cas: Optional[CASArchiver] = None,
        resilience: Optional["ResilienceContext"] = None
    ):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = queue_name
        self.resource_guard = resource_guard
        self.scraper = scraper
        self.cas = cas
        self.resilience = resilience
        self._running = False
        self.state_file = Path("data/ingestion/worker_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    async def submit_job(self, job: CurationJob):
        """Submits a job to the Redis queue."""
        await self.redis.lpush(self.queue_name, json.dumps(asdict(job)))
        logger.info(f"Job {job.job_id} submitted to {self.queue_name}")

    async def _save_somatic_state(self, job_id: str, offset: int):
        """
        Implements a Somatic Save-Point for the worker.
        Saves the current processing state to prevent restart-loops.
        """
        state = {"last_job_id": job_id, "offset": offset}
        async with await anyio.open_file(self.state_file, "w") as f:
            await f.write(json.dumps(state))

    async def _load_somatic_state(self) -> Optional[Dict]:
        """Loads the last known somatic state."""
        if not await anyio.Path(self.state_file).exists():
            return None
        async with await anyio.open_file(self.state_file, "r") as f:
            content = await f.read()
            return json.loads(content)

    async def run(self):
        """
        Main worker loop.
        Uses blpop for efficient, non-polling queue consumption.
        Also checks the delayed queue for exponential backoff jobs.
        """
        self._running = True
        logger.info(f"SovereignWorker started. Listening on {self.queue_name}...")
        
        # Load somatic state to resume if necessary
        state = await self._load_somatic_state()
        if state:
            logger.info(f"Resuming from somatic state: {state}")

        while self._running:
            try:
                # Check delayed queue for jobs ready to be re-processed
                import time
                now = time.time()
                delayed_jobs = await self.redis.zrangebyscore(
                    f"delayed_{self.queue_name}", 0, now
                )
                for job_data in delayed_jobs:
                    await self.redis.lpush(self.queue_name, job_data)
                    await self.redis.zrem(f"delayed_{self.queue_name}", job_data)
                
                # BLPOP blocks until an item is available
                # Wrap in to_thread because redis-py's blpop can be blocking
                result = await self.redis.blpop(self.queue_name, timeout=10)
                
                if not result:
                    continue
                
                _, job_data = result
                job = CurationJob(**json.loads(job_data))
                
                # Resource Guarding: Ensure we don't starve the Oracle
                if self.resource_guard:
                    async with self.resource_guard:
                        await self._process_job(job)
                else:
                    await self._process_job(job)
                
                # Save somatic state after successful job
                await self._save_somatic_state(job.job_id, 0)
                
            except anyio.CancelledError:
                self._running = False
            except (OmegaError, RuntimeError, OSError) as e:
                logger.error(f"Worker loop error: {str(e)}")
                await anyio.sleep(1)


    async def _process_job(self, job: CurationJob):
        """Executes the scrape and handles the result."""
        logger.info(f"Processing job {job.job_id}: {job.url} [{job.tier}]")
        
        if not self.scraper:
            logger.error("No scraper configured for SovereignWorker")
            return

        # Check budget via resilience context
        if self.resilience and not self.resilience.check_budget(estimated_tokens=1000):
            logger.warning(f"Job {job.job_id} skipped: budget exceeded")
            return

        result = await self.scraper.scrape(
            url=job.url, 
            tier=job.tier, 
            domain_key=job.domain_key
        )
        
        if result.success:
            # Store raw content in CAS (Sovereign Archiving)
            cid = None
            if self.cas:
                cid = await self.cas.store(result.content.encode())
            
            # Store result in Redis for the Oracle to pick up
            job_result = {
                "url": result.url,
                "content": result.content,
                "metadata": result.metadata,
                "tier": result.tier,
                "provider_name": result.provider_name,
                "latency_ms": result.latency_ms
            }
            if cid:
                job_result["cas_cid"] = cid
                
            await self.redis.set(
                f"job_result:{job.job_id}", 
                json.dumps(job_result), 
                ex=3600
            )
            
            # Update budget spend via resilience context
            if self.resilience:
                self.resilience.update_spend(tokens=len(result.content)//4 + 1000)
            
            logger.info(f"Job {job.job_id} completed successfully. CAS CID: {cid}")
        else:
            logger.error(f"Job {job.job_id} failed: {result.error}")
            # Implement exponential backoff with jitter
            if job.retry_count < 3:
                job.retry_count += 1
                # Exponential backoff: 0.1s, 0.2s, 0.4s + random jitter
                delay = min(2**job.retry_count * 0.1 + random.uniform(0, 0.1), 60)
                
                # Use Redis sorted set for delayed re-queueing
                import time
                execute_at = time.time() + delay
                await self.redis.zadd(
                    f"delayed_{self.queue_name}",
                    {json.dumps(asdict(job)): execute_at}
                )
                logger.info(f"Re-queued job {job.job_id} with {delay:.2f}s delay (Attempt {job.retry_count})")
            else:
                logger.error(f"Job {job.job_id} exceeded max retries.")

    async def stop(self):
        """Gracefully stops the worker."""
        self._running = False
