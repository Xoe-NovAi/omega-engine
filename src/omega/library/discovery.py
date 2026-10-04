"""Discovery Orchestrator — Tiered external research pipeline.

AP: AP-DISCOVERY-ORCHESTRATOR-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: PROMETHEUS | CONTEXT: DISCOVERY-PIPELINE]

Implements the research pipeline using sovereign tools:
  1. Reconnaissance (Gemini) — High-level synthesis
  2. Semantic Discovery (Exa) — Source discovery
  3. Synthesis — AI-powered synthesis of gathered research

NOTE: Brave and Tavily dependencies removed per D-kal-164.
"""
# DocRef: docs/architecture/KNOWLEDGE_LIBRARY.md

import json
import logging
import os
import uuid
import yaml
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx2 as httpx
import anyio
from omega.errors import (
    OmegaError,
    ProviderError,
    OmegaPersistenceError,
)

logger = logging.getLogger(__name__)

# [D-565 / M2 — vault is FORGE on the public cut]
# `src/omega/vault/` is excluded from the public release by D-565. This module
# is RETAINED (it sits under the broad `src/omega/` allow pattern) and is
# imported at module scope by `mcp_servers/omega_hub/state.py`, which the
# `check-hub-imports` temple-grade gate imports in a CLEAN worktree.
#
# A hard `from omega.vault import VaultCore` therefore made `make temple-grade`
# fail with ModuleNotFoundError on every allowlist cut — including the already
# published release/debut (3c051021).
#
# Resolution: vault is an OPTIONAL capability. Absent vault => no credential
# resolution => discovery degrades to its non-vault path (mock/web sources).
# D-565 is NOT weakened: vault is still cut, and it is still the single source
# of truth for credentials whenever it IS present.
try:
    from omega.vault import VaultCore

    VAULT_AVAILABLE = True
except ImportError as _vault_import_error:  # pragma: no cover - env dependent
    VaultCore = None  # type: ignore[assignment,misc]
    VAULT_AVAILABLE = False
    logger.debug(
        "omega.vault unavailable (%s) — discovery runs without VaultCore "
        "credential resolution (expected on public cuts per D-565)",
        _vault_import_error,
    )

DATA_DIR = Path(
    os.environ.get("OMEGA_DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data"))
)
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
    """Orchestrates multiple search providers into a unified discovery report.

    [HARDENING-2026-07-22] No longer hardcodes cloud-only model names. Uses
    the ModelGateway's local-first provider chain. Degrades gracefully when
    no inference provider is available.
    """

    def __init__(self, model_gateway: Optional[Any] = None, default_model: Optional[str] = None):
        from omega.oracle.health_monitor import get_health_monitor
        from omega.oracle.model_gateway import ModelGateway

        self.model_gateway = model_gateway or ModelGateway(health_monitor=get_health_monitor())
        # [HARDENING-2026-07-22] Do NOT hardcode cloud-only model names.
        # Use gateway's provider chain: local → antigravity → ... → gemini.
        # The gateway will try local inference first (M7 Local-First).
        self.default_model = default_model  # None = let gateway decide
        # [D-565] VaultCore is OPTIONAL. On a public cut `omega.vault` does not
        # exist; resolve to no credential rather than raising. `ImportError` is
        # deliberately included in the caught set below because the original
        # handler caught only (OmegaError, KeyError) and would have propagated
        # ModuleNotFoundError out of __init__.
        self._resolve_vault_credentials()
        self._jobs: Dict[str, DiscoveryReport] = {}
        self._load_jobs()

    def _resolve_vault_credentials(self) -> None:
        """Resolve Exa/Firecrawl keys from VaultCore, degrading to None.

        Sets `self.exa_key` and `self.firecrawl_key`. When vault is absent
        (public cut, D-565) or fails to load, both are set to None and
        discovery continues on its non-vault path.
        """
        if not VAULT_AVAILABLE or VaultCore is None:
            logger.debug(
                "VaultCore unavailable — Exa/Firecrawl keys unresolved "
                "(expected on public cuts per D-565)"
            )
            self.exa_key = None
            self.firecrawl_key = None
            return

        for attr, provider in (("exa_key", "exa:api_key"), ("firecrawl_key", "firecrawl:api_key")):
            try:
                vault = VaultCore()
                vault._load_sync()
                cred = vault._credentials.get(provider)
                key = cred.encrypted_blob if cred else None
                setattr(self, attr, key)
                if not key:
                    logger.warning(f"VaultCore {provider} resolution failed - no key in vault")
            except ImportError as e:
                # Belt-and-braces: vault vanished between import and call.
                logger.warning(f"VaultCore {provider} resolution failed (import): {e}")
                setattr(self, attr, None)
            except (OmegaError, KeyError) as e:
                logger.warning(f"VaultCore {provider} resolution failed: {e}")
                setattr(self, attr, None)

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
                except OmegaError:
                    raise
                except (yaml.YAMLError, OSError) as e:
                    logger.error(f"Failed to load discovery job {path}: {e}", exc_info=True)
                    raise OmegaError(f"Job load failed: {e}", raw_error=e) from e
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
        except OmegaError:
            raise
        except (OSError, OmegaError) as e:
            logger.error(f"Failed to persist discovery job {job_id}: {e}", exc_info=True)
            raise OmegaPersistenceError(f"Job persist failed: {e}", raw_error=e) from e

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

        except OmegaError as e:
            logger.error(f"Discovery job {job_id} failed (OmegaError): {e}")
            report.status = "failed"
            report.final_synthesis = f"Error: {e}"
            self._persist_job(job_id, report)
        except (RuntimeError, OSError, OmegaError) as e:
            logger.error(f"Discovery job {job_id} failed (Unexpected): {e}", exc_info=True)
            report.status = "failed"
            report.final_synthesis = f"Error: {e}"
            self._persist_job(job_id, report)
            raise OmegaError(f"Discovery job {job_id} failed: {e}", raw_error=e) from e

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
        """Phase 1: High-level synthesis via local-first provider chain.

        [HARDENING-2026-07-22] Uses local-first provider chain (M7).
        Degrades gracefully: returns structured summary from web if no
        inference provider is available.
        """
        system_prompt = (
            "You are a reconnaissance agent. Provide a high-level synthesis of the query, "
            "identifying key entities, dates, and technical terms. Focus on providing a "
            "structured summary suitable for deep research."
        )

        result = await self._try_generate(
            system_prompt=system_prompt,
            user_query=query,
            temperature=0.2,
            max_tokens=1024,
        )
        return result

    async def _phase_decompose(self, query: str, recon_summary: str) -> List[Dict[str, Any]]:
        """Decompose the main query into 3-5 specific subtopics for deeper research."""
        system_prompt = (
            "You are a research supervisor. Based on the query and reconnaissance summary, "
            "decompose the topic into 3-5 distinct sub-queries that cover different angles "
            "(technical, historical, practical, etc.). Output ONLY a JSON list of strings."
        )

        response = await self._try_generate(
            system_prompt=system_prompt,
            user_query=f"Query: {query}\n\nRecon Summary:\n{recon_summary}",
            temperature=0.1,
        )

        # Try to extract JSON if there's markdown
        clean = response.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()

        try:
            topics = json.loads(clean)
            return [{"query": t, "status": "pending"} for t in topics]
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error(f"Decomposition JSON parse failed: {e} — response was: {response[:200]}")
            # Degrade gracefully: wrap the whole query as one subtopic
            return [{"query": query, "status": "pending"}]

    async def _research_subtopic(self, report: DiscoveryReport, subtopic: Dict[str, Any]):
        """Run discovery for a single subtopic."""
        sub_query = subtopic["query"]
        subtopic["status"] = "running"

        try:
            # Simplified pipeline for subtopics
            sources = await self._phase_discovery(sub_query)
            report.sources.extend(sources)

            # Note: Content extraction (Tavily) removed per D-kal-164.
            # Sources from Exa already include content via highlights.

            subtopic["status"] = "complete"
        except OmegaError:
            raise
        except (RuntimeError, OSError, OmegaError) as e:
            logger.error(f"Subtopic research failed for '{sub_query}': {e}", exc_info=True)
            raise OmegaError(f"Subtopic research failed: {e}", raw_error=e) from e

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

        result = await self._try_generate(
            system_prompt=system_prompt,
            user_query=context,
            temperature=0.3,
            max_tokens=2048,
        )
        return result

    async def _try_generate(
        self,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Try generation with local-first provider chain; degrade gracefully.

        [HARDENING-2026-07-22] Library discovery tools MUST NOT fail when no
        local or cloud inference is available. This method:
        1. Lets the ModelGateway try its local-first chain (M7)
        2. On total provider failure, returns a degraded stub
        3. Never raises — always returns useful text

        Returns:
            Generated text, or a degraded stub explaining what's missing.
        """
        try:
            result = await self.model_gateway.generate(
                model_name=self.default_model,  # None = gateway chooses
                system_prompt=system_prompt,
                user_query=user_query,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if hasattr(result, "text"):
                return result.text
            if isinstance(result, str):
                return result
            return str(result)
        except OmegaError as e:
            logger.warning(f"Generation failed — using degraded stub: {e}")
        except (RuntimeError, OSError) as e:
            logger.warning(f"Generation failed — using degraded stub: {e}")

        # Graceful degradation: return a stub so the pipeline continues
        return (
            f"[Inference unavailable — degraded mode]\n"
            f"Query: {user_query[:200]}\n"
            f"System: {system_prompt[:200]}\n"
            f"Note: No inference provider was available. This research phase "
            f"was skipped. Results will be based on web-sourced data only."
        )
        """Phase 2: Semantic discovery via Exa (Free Tier)."""
        if not self.exa_key:
            logger.warning("EXA_API_KEY missing. Using mock discovery.")
            return [{"title": "Mock Source", "url": "https://example.com", "score": 0.9}]

        url = "https://api.exa.ai/search"
        headers = {"x-api-key": self.exa_key, "Content-Type": "application/json"}
        payload = {
            "query": user_query,
            "type": "deep",
            "numResults": 10,
            "contents": {"highlights": True},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data.get("results", [])
        except OmegaError:
            raise
        except (httpx.HTTPError, OSError, OmegaError) as e:
            logger.error(f"Exa Phase failed: {e}", exc_info=True)
            raise ProviderError(f"Exa Phase failed: {e}", raw_error=e) from e

    # Brave (_phase_validation) and Tavily (_phase_extraction) removed
    # per D-kal-164 sovereign dependency purge.
