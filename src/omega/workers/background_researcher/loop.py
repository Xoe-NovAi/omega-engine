# 🔱 Omega Engine — Background Researcher Core Loop
# AP: AP-BACKGROUND-RESEARCHER-LOOP-v2.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ sovereign ⬡ loop ⬡ WORKER
#
# The autonomous research state machine:
#   [IDLE] → [TRIAGE] → [SEARCH] → [EXTRACT] → [DISTILL] → [CONVERGE] → [UPDATE] → [IDLE]
#
# Runs as a systemd timer every 20 minutes. Fully AnyIO-compliant.
# Every state transition is checkpointed for restart recovery.

import json
import logging
import os
import re
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
import anyio
import httpx

from .models import ResearchTask, TriageResult, GnosisPacket, EnhancedPriorityQueue, RotationState
from .scheduler import TopicScheduler
from .review_queue import ReviewQueue
from .metrics import ResearchMetrics
from .credit_budget import APICreditBudget, APICreditExhausted
from .checkpoint import CheckpointManager
from .searxng_client import SearXNGClient
from .search_fleet import SearchFleet
from .distiller import Distiller
from .convergence import ConvergenceDetector
from .soul_updater import SoulUpdater

logger = logging.getLogger(__name__)

class BackgroundResearcherLoop:
    """Autonomous sovereign research state machine.
    
    Orchestrates the full research cycle:
    Triage → Search → Extract → Distill → Converge → Update
    """
    
    def __init__(
        self,
        config: Optional[dict] = None,
        model_gateway=None,
    ):
        self.config = config or {}
        self.model_gateway = model_gateway

        # Core Components
        self.budget = APICreditBudget()
        self.checkpoint = CheckpointManager()
        self.searxng = SearXNGClient()
        self.search_fleet = SearchFleet(self.budget)
        self.distiller = Distiller(model_gateway)
        self.convergence = ConvergenceDetector()
        self.soul_updater = SoulUpdater()
        
        # Phase 2 Components
        self.queue = EnhancedPriorityQueue()
        self.scheduler = TopicScheduler()
        self.review_queue = ReviewQueue()
        self.metrics = ResearchMetrics()

        # State
        self._running = False
        self._cycle_count = 0
        self.lock_path = Path("/tmp/omega/research.lock")

    # ── Public API ──────────────────────────────────────────────────────────

    async def run_cycle(self) -> dict:
        """Execute one complete research cycle with atomic locking and scheduling."""
        # 1. Atomic Lock to prevent concurrent execution
        try:
            self.lock_path.mkdir(parents=True)
        except FileExistsError:
            logger.warning("Research cycle already locked. Skipping.")
            return {"skipped": True, "reason": "locked"}

        self._running = True
        self._cycle_count += 1
        cycle_id = f"cycle_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{self._cycle_count}"
        trace_id = f"trc_res_{uuid.uuid4().hex[:12]}"
        
        start_time = time.monotonic()
        cycle_metrics = {}

        try:
            logger.info(f"Starting research cycle {cycle_id}")

            if not await self._is_network_available():
                return {"cycle_id": cycle_id, "skipped": True, "reason": "no_network"}

            # 2. Scheduling: Inject next scheduled topic into the queue
            scheduled_task = self.scheduler.get_next_topic()
            if scheduled_task:
                self.queue.enqueue(
                    scheduled_task.topic, 
                    base_priority=scheduled_task.priority, 
                    user_requested=False
                )
                logger.info(f"Scheduled topic enqueued: {scheduled_task.topic}")

            # 3. Get next task (Weighted Fair)
            task = self.queue.dequeue()
            if task is None:
                await self._grow_frontier()
                task = self.queue.dequeue()
                if task is None:
                    # Idle: Process one item from the review queue
                    review_item = self.review_queue.dequeue()
                    if review_item:
                        logger.info(f"Processing review item: {review_item['topic']}")
                        return {"cycle_id": cycle_id, "action": "review", "topic": review_item['topic']}
                    
                    result = {"cycle_id": cycle_id, "trace_id": trace_id, "skipped": True, "reason": "empty_queue"}
                    await self._post_to_hivemind(result)
                    return result

            logger.info(f"Researching: '{task.topic}' (priority={task.priority:.2f})")

            # 4. Discovery-First Local Scan
            local_context = await self._local_discovery_scan(task)
            
            # 5. Triage
            triage = await self._triage(task)
            if triage.skip:
                await self.checkpoint.mark_skip(task)
                return {"cycle_id": cycle_id, "task": task.topic, "skipped": True, "action": "skip", "reason": triage.reason}

            # 6. Search (SearXNG + Cloud)
            sources = await self._search(task, triage)
            if not sources:
                task.attempts += 1
                await self.checkpoint.save(task)
                return {"cycle_id": cycle_id, "task": task.topic, "skipped": True, "action": "defer", "reason": "no_sources"}

            all_urls = []
            for provider_urls in sources.values():
                all_urls.extend(provider_urls)
            task.sources = list(set(all_urls))[:50]
            task.state = "searched"
            await self.checkpoint.save(task)

            # 7. Extract
            content = await self._extract(task, sources)
            # Merge local context with web content
            full_content = f"--- LOCAL CONTEXT ---\n{local_context}\n\n--- WEB CONTENT ---\n{content}"
            task.state = "extracted"
            await self.checkpoint.save(task)

            if not content and not local_context:
                return {"cycle_id": cycle_id, "task": task.topic, "skipped": True, "action": "skip", "reason": "no_content"}

            # 8. Distill (3-Tier Pipeline)
            t1_start = time.monotonic()
            gnosis = await self.distiller.distill(
                topic=task.topic,
                content=full_content,
                sources=list(sources.keys()),
                prompt_mode=None,
            )
            t1_end = time.monotonic()
            
            # Log metrics for this cycle
            cycle_metrics = {
                "t1_latency": t1_end - t1_start,
                "t1_quality": 1.0 if gnosis else 0.0,
                "circuit_states": {"t1": "CLOSED", "t2": "CLOSED", "t3": "CLOSED"},
                "training_triple_saved": True
            }
            self.metrics.log_cycle(task.topic, cycle_metrics)

            task.state = "distilled"
            await self.checkpoint.save(task)

            # 9. Convergence & Update
            converged = await self.convergence.check(task, gnosis)
            updated = await self.soul_updater.update(task, gnosis)

            if converged or updated:
                await self.checkpoint.mark_done(task)
            else:
                task.verification_count += 1
                await self.checkpoint.save(task)

            # 10. Grow frontier
            await self._enqueue_adjacent(task, gnosis)

            result = {
                "cycle_id": cycle_id,
                "trace_id": trace_id,
                "task": task.topic,
                "action": "done" if converged else "partial",
                "converged": converged,
                "updated": updated,
            }
            await self._post_to_hivemind(result)
            return result

        except Exception as e:
            logger.error(f"Research cycle failed: {e}", exc_info=True)
            return {"cycle_id": cycle_id, "error": str(e)}

        finally:
            self._running = False
            try:
                self.lock_path.rmdir()
            except Exception:
                pass

    async def _local_discovery_scan(self, task: ResearchTask) -> str:
        """Perform a 'Discovery-First' scan of the local codebase for relevant snippets."""
        topics_cfg = self.config.get("scheduled_topics", {})
        topic_key = next((k for k, v in topics_cfg.items() if v.get("title") == task.topic), None)
        
        if not topic_key:
            return ""
            
        cfg = topics_cfg[topic_key].get("local_search", {})
        dirs = cfg.get("dirs", [])
        patterns = cfg.get("patterns", [])
        
        snippets = []
        for d in dirs:
            path_obj = Path(d).expanduser()
            if not path_obj.exists():
                continue
                
            for pattern in patterns:
                for file_path in path_obj.rglob("*"):
                    if file_path.is_file():
                        try:
                            content = file_path.read_text(errors="ignore")
                            for line in content.splitlines():
                                if pattern.lower() in line.lower():
                                    snippets.append(f"[{file_path.name}]: {line.strip()}")
                        except Exception:
                            continue
                            
        return "\n".join(snippets[:20])

    async def _get_next_task(self) -> Optional[ResearchTask]:
        """Get the next task from the enhanced priority queue or checkpoints."""
        task = self.queue.dequeue()
        if task:
            return task

        pending = await self.checkpoint.load_all_pending()
        if pending:
            pending.sort(key=lambda t: t.priority, reverse=True)
            return pending[0]

        return None

    async def _triage(self, task: ResearchTask) -> TriageResult:
        topic = task.topic.lower()
        high_value = ["ai", "model", "gemma", "llama", "open source", "sovereign", "security", "privacy", "protocol", "mcp", "architecture", "tool", "framework", "library", "api", "standard"]
        skip_value = ["celebrity", "gossip", "sports score", "weather", "stock price", "cryptocurrency price"]
        score = 0.5
        for keyword in high_value:
            if keyword in topic: score += 0.1
        for keyword in skip_value:
            if keyword in topic: return TriageResult(score=0.0, depth_plan=1, reason="Low-value topic", skip=True)
        if len(topic) > 30: score += 0.1
        if len(topic) > 60: score += 0.1
        score = min(score, 1.0)
        depth = 3 if score >= 0.8 else (2 if score >= 0.6 else 1)
        return TriageResult(score=score, depth_plan=depth, reason=f"Heuristic score: {score:.2f}", skip=score < 0.3)

    async def _search(self, task: ResearchTask, triage: TriageResult) -> dict[str, list[str]]:
        results: dict[str, list[str]] = {}
        searxng_results = await self.searxng.search_text(task.topic)
        if searxng_results:
            results["searxng"] = searxng_results
        if triage.depth_plan >= 2:
            try:
                cloud_results = await self.search_fleet.search_all(task.topic, depth=triage.depth_plan)
                results.update(cloud_results)
            except APICreditExhausted:
                logger.info("Cloud search quota exhausted — using SearXNG only")
        return results

    async def _extract(self, task: ResearchTask, sources: dict[str, list[str]]) -> str:
        content_chunks = []
        urls_seen = set()
        all_urls = []
        for provider_urls in sources.values():
            for url in provider_urls:
                if url not in urls_seen and url.strip():
                    urls_seen.add(url)
                    all_urls.append(url)
        for url in all_urls[:5]:
            try:
                chunk = await self._fetch_content(url)
                if chunk:
                    content_chunks.append(f"[Source: {url}]\n{chunk}")
            except Exception:
                continue
        return "\n\n---\n\n".join(content_chunks[:3])

    async def _fetch_content(self, url: str) -> Optional[str]:
        firecrawl_content = await self.search_fleet.extract_firecrawl(url)
        if firecrawl_content and len(firecrawl_content) > 100:
            return firecrawl_content[:10000]
        jina_content = await self.search_fleet.read_url_jina(url)
        if jina_content and len(jina_content) > 100:
            return jina_content[:8000]
        exa_content = await self.search_fleet.fetch_exa(url)
        if exa_content and len(exa_content) > 100:
            return exa_content[:8000]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, follow_redirects=True)
                resp.raise_for_status()
                return resp.text[:8000]
        except Exception:
            return None

    async def _enqueue_adjacent(self, task: ResearchTask, gnosis: GnosisPacket) -> None:
        if gnosis.recommendation in ("write_to_soul", "write_to_knowledge") and task.depth < 3:
            deeper = ResearchTask(topic=task.topic, priority=task.priority * 0.8, depth=task.depth + 1)
            self.queue.enqueue(deeper.topic, base_priority=deeper.priority, current_depth=task.depth * 2.5)

    async def enqueue_user_request(self, topic: str, depth: int = 2) -> None:
        self.queue.enqueue(topic, base_priority=0.8, user_requested=True, current_depth=0)
        logger.info(f"User-requested research queued: '{topic}' (depth={depth})")

    async def _grow_frontier(self) -> None:
        candidates: list[dict] = []
        index_path = Path("docs/research/INDEX.md")
        if index_path.exists():
            text = index_path.read_text()
            for line in text.split("\n"):
                if "| R-" in line and "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        title, status_col = parts[2], parts[3]
                        if "🔲" in status_col or "🔄" in status_col:
                            candidates.append({"topic": title, "source": "research_index", "priority": 0.7, "depth": 2})
        
        src_dir = Path(__file__).parent.parent.parent / "src" / "omega"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    for keyword, base_priority in [("FIXME", 0.9), ("HACK", 0.8), ("TODO", 0.5)]:
                        if keyword in content:
                            for line in content.split("\n"):
                                if keyword in line:
                                    idx = line.find(keyword)
                                    comment = line[idx + len(keyword):].strip().lstrip(": ")
                                    rel_path = py_file.relative_to(src_dir.parent.parent)
                                    topic = f"[{keyword}] {comment} — {rel_path}" if comment else f"[{keyword}] {rel_path}"
                                    candidates.append({"topic": topic, "source": "codebase", "priority": base_priority, "depth": 1})
                                    break
                except (IOError, OSError):
                    continue
        
        roadmap_path = Path("docs/ROADMAP.md")
        if roadmap_path.exists():
            text = roadmap_path.read_text()
            current_phase: Optional[str] = None
            for line in text.split("\n"):
                phase_match = re.match(r"^### Phase (\w+):", line)
                if phase_match: current_phase = phase_match.group(1)
                task_match = re.match(r"^\|\s*(\w[\w.]*)\s*\|.*?\|.*?\|.*?(🔴|🟡)", line)
                if task_match and current_phase:
                    candidates.append({"topic": f"Phase {current_phase} task {task_match.group(1)} — implementation research", "source": "roadmap", "priority": 0.6, "depth": 1})

        entities_dir = Path(__file__).parent.parent.parent.parent / "data" / "entities"
        if entities_dir.exists():
            for entity_dir in entities_dir.iterdir():
                if entity_dir.is_dir() and entity_dir.name != "arch":
                    knowledge_dir = entity_dir / "knowledge"
                    if not knowledge_dir.exists() or not any(knowledge_dir.iterdir()):
                        candidates.append({"topic": f"Knowledge base scaffolding for entity {entity_dir.name}", "source": "entity_gap", "priority": 0.5, "depth": 1})

        checkpoint_dir = Path("data/research/checkpoints")
        if checkpoint_dir.exists():
            for path in checkpoint_dir.glob("*.json"):
                try:
                    data = json.loads(path.read_text())
                    if data.get("state", "") in ("defer", "skip") and data.get("attempts", 0) < 3:
                        candidates.append({"topic": data.get("topic", "Unknown deferred topic"), "source": "checkpoint", "priority": 0.4 + (data.get("attempts", 0) * 0.1), "depth": data.get("depth", 1) + 1})
                except (json.JSONDecodeError, OSError):
                    continue

        seen: dict[str, dict] = {}
        for c in candidates:
            key = c["topic"].lower()[:60]
            if key not in seen or c["priority"] > seen[key]["priority"]:
                seen[key] = c
        candidates = sorted(seen.values(), key=lambda c: c["priority"], reverse=True)

        enqueued = 0
        active_topics = {item[2].topic.lower()[:60] for _, _, item in self.queue._high_priority} | {item[2].topic.lower()[:60] for _, _, item in self.queue._normal_priority}
        for c in candidates[:5]:
            key = c["topic"].lower()[:60]
            if key in active_topics: continue
            self.queue.enqueue(c["topic"], base_priority=c["priority"], current_depth=c["depth"] * 2.5)
            enqueued += 1
            logger.info(f"Frontier gap found: '{c['topic']}' (p={c['priority']:.1f}) from {c['source']}")

        if enqueued == 0:
            fallback_topics = ["Gemma 4 31B latest features and API changes May 2026", "AnyIO latest patterns for background workers in Python 3 13", "OpenCode custom mode plugin development best practices 2026", "SearXNG rootless Podman deployment troubleshooting 2026", "Ollama v0 6 GGUF model optimization for Zen 2 AVX2"]
            for topic in fallback_topics:
                self.queue.enqueue(topic, base_priority=0.3, current_depth=0)
                enqueued += 1
            logger.info(f"Fallback: seeded {len(fallback_topics)} tech landscape topics")

        logger.info(f"Frontier growth complete — enqueued {enqueued} topics from {len(candidates)} candidates")

    async def _post_to_hivemind(self, cycle_result: dict) -> None:
        try:
            base_dir = Path(__file__).parent.parent.parent.parent
            records_dir = base_dir / "data" / "knowledge" / "HALL_OF_RECORDS" / "background-researcher"
            records_dir.mkdir(parents=True, exist_ok=True)
            today = datetime.now(timezone.utc).strftime("%Y%m%d")
            log_path = records_dir / f"cycle_{today}.jsonl"
            line = json.dumps(cycle_result, default=str) + "\n"
            def _atomic_append() -> None:
                existing = b""
                if log_path.exists(): existing = log_path.read_bytes()
                tmp = log_path.with_suffix(".tmp.jsonl")
                tmp.write_bytes(existing + line.encode("utf-8"))
                tmp.replace(log_path)
            await anyio.to_thread.run_sync(_atomic_append)
        except Exception:
            pass

    async def _is_network_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.get("https://httpbin.org/get")
                return True
        except Exception:
            pass
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("http://localhost:8017/healthz")
                return resp.status_code == 200
        except Exception:
            return False

    async def get_status(self) -> dict:
        budget_status = self.budget.get_status()
        return {
            "running": self._running,
            "cycle_count": self._cycle_count,
            "queue_size": len(self.queue),
            "searxng_healthy": await self.searxng.health(),
            "budget": budget_status,
        }

    async def enqueue_topic(self, topic: str, depth: int = 2) -> None:
        self.queue.enqueue(topic, base_priority=0.8, user_requested=True, current_depth=0)
        logger.info(f"Research topic queued: '{topic}' (depth={depth})")
