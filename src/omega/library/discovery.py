"""Discovery Orchestrator — Tiered external research pipeline.

AP: AP-DISCOVERY-ORCHESTRATOR-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: PROMETHEUS | CONTEXT: DISCOVERY-PIPELINE]

Implements the 4-phase research pipeline using FREE tools:
  1. Reconnaissance (Gemini 2.0 Flash) -> High-level synthesis
  2. Semantic Discovery (Exa) -> Gold-standard sources
  3. Broad Validation (Brave Search) -> Verification
  4. Deep Extraction (Tavily/Exa Fetch) -> High-fidelity content
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import anyio

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get(
    "OMEGA_DATA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "data")
))
JOBS_DIR = DATA_DIR / "jobs"
JOBS_PENDING_DIR = JOBS_DIR / "pending"
JOBS_RUNNING_DIR = JOBS_DIR / "running"
JOBS_COMPLETED_DIR = JOBS_DIR / "completed"
JOBS_FAILED_DIR = JOBS_DIR / "failed"

for d in [JOBS_PENDING_DIR, JOBS_RUNNING_DIR, JOBS_COMPLETED_DIR, JOBS_FAILED_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class DiscoveryReport:
    """Consolidated report from the discovery pipeline."""
    query: str
    recon_summary: str = ""
    subtopics: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    validation_notes: List[str] = field(default_factory=list)
    extracted_content: List[Dict[str, Any]] = field(default_factory=list)
    final_synthesis: str = ""
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "status": self.status,
            "recon_summary": self.recon_summary,
            "subtopics": self.subtopics,
            "sources": self.sources,
            "validation_notes": self.validation_notes,
            "extracted_content": self.extracted_content,
            "final_synthesis": self.final_synthesis,
            "created_at": self.created_at,
        }


class DiscoveryOrchestrator:
    """Orchestrates multiple search providers into a unified discovery report."""

    def __init__(self, model_gateway: Optional[Any] = None):
        from omega.oracle.model_gateway import ModelGateway
        self.model_gateway = model_gateway or ModelGateway()
        self.exa_key = os.getenv("EXA_API_KEY")
        self.brave_key = os.getenv("BRAVE_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self._jobs: Dict[str, DiscoveryReport] = {}
        self._load_jobs()

    def _job_path(self, job_id: str, status: str = "") -> Path:
        """Get the path for a job file based on its status."""
        if status == "pending":
            return JOBS_PENDING_DIR / f"{job_id}.json"
        elif status == "running":
            return JOBS_RUNNING_DIR / f"{job_id}.json"
        elif status == "complete" or status == "completed":
            return JOBS_COMPLETED_DIR / f"{job_id}.json"
        elif status == "failed":
            return JOBS_FAILED_DIR / f"{job_id}.json"
        return JOBS_PENDING_DIR / f"{job_id}.json"

    def _load_jobs(self) -> None:
        """Load existing jobs from disk into memory."""
        for status_dir, status_val in [
            (JOBS_PENDING_DIR, "pending"),
            (JOBS_RUNNING_DIR, "running"),
            (JOBS_COMPLETED_DIR, "complete"),
            (JOBS_FAILED_DIR, "failed"),
        ]:
            for path in status_dir.glob("*.json"):
                try:
                    with open(str(path)) as f:
                        data = json.load(f)
                    report = DiscoveryReport(
                        query=data.get("query", ""),
                        recon_summary=data.get("recon_summary", ""),
                        subtopics=data.get("subtopics", []),
                        sources=data.get("sources", []),
                        validation_notes=data.get("validation_notes", []),
                        extracted_content=data.get("extracted_content", []),
                        final_synthesis=data.get("final_synthesis", ""),
                        status=status_val,
                        created_at=data.get("created_at", ""),
                    )
                    job_id = path.stem
                    self._jobs[job_id] = report
                except Exception as e:
                    logger.warning(f"Failed to load discovery job {path}: {e}")
        if self._jobs:
            logger.info(f"Loaded {len(self._jobs)} discovery jobs from disk")

    def _persist_job(self, job_id: str, report: DiscoveryReport) -> None:
        """Save a job to disk as JSON."""
        try:
            path = self._job_path(job_id, report.status)
            with open(str(path), "w") as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
            # Remove from old status directories
            for old_status in ["pending", "running", "complete", "failed"]:
                if old_status != report.status:
                    old_path = self._job_path(job_id, old_status)
                    if old_path.exists():
                        old_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to persist discovery job {job_id}: {e}")

    async def start_discovery(self, query: str) -> str:
        """Start a background discovery job and return the job ID."""
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        report = DiscoveryReport(query=query, status="running")
        self._jobs[job_id] = report
        self._persist_job(job_id, report)
        
        # In a real system, we'd use a task queue or a persistent store.
        # For now, we'll use the event loop.
        return job_id

    async def run_discovery_task(self, job_id: str):
        """Internal task to run the full discovery pipeline for a job."""
        if job_id not in self._jobs:
            return
            
        report = self._jobs[job_id]
        try:
            # Phase 1: Recon & Decomposition
            report.recon_summary = await self._phase_recon(report.query)
            subtopics = await self._phase_decompose(report.query, report.recon_summary)
            report.subtopics = subtopics

            # Phase 2: Parallel Subtopic Research
            async with anyio.create_task_group() as tg:
                for st in subtopics:
                    tg.start_soon(self._research_subtopic, report, st)
            
            # Phase 3: Final Synthesis
            report.final_synthesis = await self._phase_synthesize(report)
            report.status = "complete"
            self._persist_job(job_id, report)
            
        except Exception as e:
            logger.error(f"Discovery job {job_id} failed: {e}")
            report.status = "failed"
            report.final_synthesis = f"Error: {e}"
            self._persist_job(job_id, report)

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the current status of a discovery job."""
        report = self._jobs.get(job_id)
        if not report:
            return {"status": "not_found"}
        return report.to_dict()

    async def discover(self, query: str, depth: int = 2) -> DiscoveryReport:
        """Run the full discovery pipeline synchronously (legacy/blocking)."""
        # This is now a wrapper around the new logic for backward compatibility
        job_id = await self.start_discovery(query)
        await self.run_discovery_task(job_id)
        return self._jobs[job_id]

    async def _phase_recon(self, query: str) -> str:
        """Phase 1: High-level synthesis via Gemini 2.0 Flash (Free Tier)."""
        context = ""
        if self.brave_key:
            brave_results = await self._phase_validation(query, [])
            context = "\n".join(brave_results[:3])

        system_prompt = (
            "You are a reconnaissance agent. Provide a high-level synthesis of the query, "
            "identifying key entities, dates, and technical terms. Focus on providing a "
            "structured summary suitable for deep research."
        )
        user_prompt = f"Query: {query}\n\nInitial Search Context:\n{context}"
        
        try:
            response = await self.model_gateway.generate(
                model_name="gemini-2.0-flash",
                system_prompt=system_prompt,
                user_query=user_prompt,
                temperature=0.2,
                max_tokens=1024
            )
            return response
        except Exception as e:
            logger.error(f"Gemini Recon Phase failed: {e}")
            return f"Error during Gemini recon: {e}"

    async def _phase_decompose(self, query: str, recon_summary: str) -> List[Dict[str, Any]]:
        """Decompose the main query into 3-5 specific subtopics for deeper research."""
        system_prompt = (
            "You are a research supervisor. Based on the query and reconnaissance summary, "
            "decompose the topic into 3-5 distinct sub-queries that cover different angles "
            "(technical, historical, practical, etc.). Output ONLY a JSON list of strings."
        )
        user_prompt = f"Query: {query}\n\nRecon Summary:\n{recon_summary}"
        
        try:
            response = await self.model_gateway.generate(
                model_name="gemini-2.0-flash",
                system_prompt=system_prompt,
                user_query=user_prompt,
                temperature=0.1
            )
            # Try to extract JSON if there's markdown
            clean = response.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            
            topics = json.loads(clean)
            return [{"query": t, "status": "pending"} for t in topics]
        except Exception as e:
            logger.error(f"Decomposition failed: {e}")
            return [{"query": query, "status": "pending"}]

    async def _research_subtopic(self, report: DiscoveryReport, subtopic: Dict[str, Any]):
        """Run discovery for a single subtopic."""
        sub_query = subtopic["query"]
        subtopic["status"] = "running"
        
        try:
            # Simplified pipeline for subtopics
            sources = await self._phase_discovery(sub_query)
            report.sources.extend(sources)
            
            # Extract content for the top 2 sources of each subtopic
            extracted = await self._phase_extraction(sources[:2])
            report.extracted_content.extend(extracted)
            
            subtopic["status"] = "complete"
        except Exception as e:
            logger.error(f"Subtopic research failed for '{sub_query}': {e}")
            subtopic["status"] = "failed"

    async def _phase_synthesize(self, report: DiscoveryReport) -> str:
        """Final synthesis of all gathered research."""
        system_prompt = (
            "You are the Sovereign Researcher. Synthesize the gathered research into a "
            "comprehensive report. Include sections for Key Findings, Technical Details, "
            "and Sources. Focus on high-fidelity, actionable insights."
        )
        # Construct context from sources and extracted content
        context = f"Main Query: {report.query}\n\n"
        context += f"Recon: {report.recon_summary}\n\n"
        context += "Extracted Evidence:\n"
        for ex in report.extracted_content[:5]:
            context += f"- {ex.get('title')}: {ex.get('content', '')[:500]}...\n"
        
        try:
            response = await self.model_gateway.generate(
                model_name="gemini-2.0-flash",
                system_prompt=system_prompt,
                user_query=context,
                temperature=0.3,
                max_tokens=2048
            )
            return response
        except Exception as e:
            logger.error(f"Final synthesis failed: {e}")
            return f"Error during synthesis: {e}"

    async def _phase_discovery(self, query: str) -> List[Dict[str, Any]]:
        """Phase 2: Semantic discovery via Exa (Free Tier)."""
        if not self.exa_key:
            logger.warning("EXA_API_KEY missing. Using mock discovery.")
            return [{"title": "Mock Source", "url": "https://example.com", "score": 0.9}]
        
        url = "https://api.exa.ai/search"
        headers = {
            "x-api-key": self.exa_key,
            "Content-Type": "application/json"
        }
        # type: "deep" is recommended for research. useAutoprompt is deprecated.
        payload = {
            "query": query,
            "type": "deep",
            "numResults": 10,
            "contents": {
                "highlights": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"Exa Phase failed: {e}")
            return []

    async def _phase_validation(self, query: str, sources: List[Dict[str, Any]]) -> List[str]:
        """Phase 3: Broad validation via Brave Search (Free Tier)."""
        if not self.brave_key:
            return ["Brave API key missing. Validation skipped."]
        
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": self.brave_key,
            "Accept": "application/json"
        }
        params = {"q": query, "count": 5}
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()
                results = data.get("web", {}).get("results", [])
                return [f"{r.get('title')}: {r.get('description')}" for r in results]
        except Exception as e:
            logger.error(f"Brave Phase failed: {e}")
            return [f"Error during Brave validation: {e}"]

    async def _phase_extraction(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Phase 4: Content extraction via Tavily (Free Tier)."""
        if not self.tavily_key:
            return []
        
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_key,
            "query": "Extracted content for identified sources",
            "search_depth": "advanced",
            "include_content": True,
            "urls": [s["url"] for s in sources[:3] if "url" in s]
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"Tavily Phase failed: {e}")
            return []
