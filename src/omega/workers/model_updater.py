# 🔱 Omega Engine — Automated Model Research & Update Worker
# AP: AP-MODEL-UPDATER-v1.0.0
# ICS: [NODE: SOPHIA | ARCHETYPE: AUTOMATED_RESEARCHER | CONTEXT: MODEL_UPDATER]
#
# Scheduled background worker that uses Gemma 4-31B to research
# and verify free model offerings across all providers.
# Fully AnyIO-compliant, ResourceGuard-protected, and audit-ready.

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import anyio
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from omega.observability import ObservabilityEngine, EventType
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.resource_guard import ResourceGuard

logger = logging.getLogger(__name__)

# Provider API endpoints for model listing
PROVIDER_ENDPOINTS = {
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/models",
        "auth": None,  # Public endpoint
        "parser": "openrouter",
    },
    "google": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "auth": "query:key",
        "env_key": "GOOGLE_API_KEY",
        "parser": "google",
    },
    "opencode": {
        "url": "https://opencode.ai/zen/v1/models",
        "auth": None,  # Public endpoint
        "parser": "opencode",
    },
}


class ModelUpdaterWorker:
    """Robust, AnyIO-compliant background worker for model research.

    Fetches free-model catalogs from provider APIs, uses Gemma 4-31B
    for verification, diffs against the local DB, and applies updates.
    """

    def __init__(
        self,
        model_gateway: ModelGateway,
        observability: ObservabilityEngine,
        config: Dict,
        guard: ResourceGuard,
    ):
        self.model_gateway = model_gateway
        self.observability = observability
        self.guard = guard
        self.cfg = config
        self.scheduler = AsyncIOScheduler()
        self.db_path = Path("docs/research/model_db/CURRENT_MODELS.json")
        self.audit_dir = Path("data/audit/model_updater")
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.lock = anyio.Lock()           # protects DB writes
        self._running = anyio.Lock()       # guards against concurrent cycles

    # ── Lifecycle ────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Schedule the periodic job and start the APScheduler."""
        if not self.cfg.get("enabled", True):
            logger.info("ModelUpdaterWorker disabled by config.")
            return

        trigger = CronTrigger.from_crontab(self.cfg["schedule"], timezone="UTC")
        self.scheduler.add_job(
            self.run_update_cycle,
            trigger=trigger,
            id="model_updater",
            name="Gemma-4-31B Model Research Cycle",
            replace_existing=True,
        )
        self.scheduler.start()
        trace_id = str(uuid.uuid4())
        self.observability.log_event(
            EventType.WORKER_START,
            trace_id,
            {"event": "model_updater_started", "schedule": self.cfg["schedule"]},
        )
        job = self.scheduler.get_job("model_updater")
        logger.info(f"ModelUpdaterWorker started. Next run: {job.next_run_time}")

    async def stop(self) -> None:
        """Stop the scheduled worker gracefully."""
        if self.scheduler.get_job("model_updater"):
            self.scheduler.remove_job("model_updater")
        self.scheduler.shutdown(wait=False)
        logger.info("ModelUpdaterWorker stopped.")

    # ── Single cycle ─────────────────────────────────────────────────────

    async def run_update_cycle(self) -> None:
        """One full research → diff → update cycle.

        Uses a concurrency guard to prevent overlapping runs.
        """
        # Acquire the running lock; if already in a cycle, skip silently.
        if not self._running.locked():
            async with self._running:
                await self._run_full_cycle()
        else:
            logger.warning("Model update cycle already in progress. Skipping.")

    async def _run_full_cycle(self) -> None:
        trace_id = str(uuid.uuid4())
        self.observability.log_event(
            EventType.WORKER_START,
            trace_id,
            {"event": "model_update_cycle_started"},
        )
        try:
            # 1️⃣ Fetch provider data
            provider_data = await self._fetch_all_providers(trace_id)
            # 2️⃣ Research with Gemma (guarded inference)
            research = await self._research_with_gemma(provider_data, trace_id)
            # 3️⃣ Compute diffs
            changes = await self._compute_diffs(research, trace_id)
            # 4️⃣ Apply changes (if any)
            if changes:
                await self._apply_changes(changes, trace_id)
                await self._render_markdown_report(trace_id)
            # 5️⃣ Emit completion
            self.observability.log_event(
                EventType.WORKER_COMPLETE,
                trace_id,
                {
                    "event": "model_update_cycle_completed",
                    "changes": len(changes),
                    "models_fetched": len(provider_data),
                },
            )
        except Exception as exc:
            self.observability.log_event(
                EventType.ERROR,
                trace_id,
                {"event": "model_update_cycle_failed", "error": str(exc)},
            )
            raise

    # ── 1️⃣ Provider data fetching ──────────────────────────────────────

    async def _fetch_all_providers(self, trace_id: str) -> List[Dict]:
        """Fetch model lists from all enabled provider APIs in parallel."""
        results = []

        async def _fetch_single(name: str) -> None:
            """Fetch one provider's model list with retry & back-off."""
            ep = PROVIDER_ENDPOINTS.get(name)
            if not ep:
                logger.warning(f"No endpoint definition for provider '{name}'. Skipping.")
                return
            url = ep["url"]
            headers = {"User-Agent": "Omega-Engine/1.0"}
            # Build auth query parameter if needed
            params = {}
            if ep["auth"] == "query:key":
                key = os.environ.get(ep.get("env_key", ""))
                if key:
                    params["key"] = key
                else:
                    logger.warning(f"No API key for provider '{name}'. Skipping.")
                    return

            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        resp = await client.get(url, headers=headers, params=params)
                        resp.raise_for_status()
                    data = resp.json()
                    # Parse per provider type
                    parsed = self._parse_provider_models(name, data)
                    results.extend(parsed)
                    return
                except Exception as e:
                    await anyio.sleep(2**attempt)
                    self.observability.log_event(
                        EventType.ERROR,
                        trace_id,
                        {
                            "event": "provider_fetch_retry",
                            "provider": name,
                            "attempt": attempt + 1,
                            "error": str(e),
                        },
                    )
            raise RuntimeError(f"Provider {name} unreachable after retries")

        providers = [p["name"] for p in self.cfg.get("providers", []) if p.get("enabled", True)]
        if not providers:
            return []

        async with anyio.create_task_group() as tg:
            for name in providers:
                tg.start_soon(_fetch_single, name)

        return results

    @staticmethod
    def _parse_provider_models(provider: str, data: Dict) -> List[Dict]:
        """Parse provider-specific JSON model list into uniform format."""
        models = []
        if provider == "openrouter":
            for m in data.get("data", []):
                models.append({
                    "name": m["id"],
                    "provider": "openrouter",
                    "context_window": m.get("context_length", 0),
                    "pricing": m.get("pricing", {}),
                })
        elif provider == "google":
            for m in data.get("models", []):
                name = m["name"].replace("models/", "")
                models.append({
                    "name": name,
                    "provider": "google",
                    "context_window": m.get("inputTokenLimit", 0),
                    "supported_actions": m.get("supportedActions", []),
                })
        elif provider == "opencode":
            for m in data.get("data", []):
                models.append({
                    "name": m["id"],
                    "provider": "opencode",
                    "context_window": m.get("context_length", 0),
                    "pricing": m.get("pricing", {}),
                })
        return models

    # ── 2️⃣ Gemma research ─────────────────────────────────────────────

    async def _research_with_gemma(
        self, provider_data: List[Dict], trace_id: str
    ) -> Dict:
        """Use Gemma 4-31B to verify and enrich the fetched model data."""
        prompt = self._build_research_prompt(provider_data)
        async with self.guard.lock():
            response_str = await self.model_gateway.generate(
                model_name=self.cfg.get("model", "gemma-4-31b-it"),
                system_prompt="You are a model database researcher. Return ONLY valid JSON.",
                user_query=prompt,
                temperature=0.1,
                max_tokens=4096,
            )
        # Parse the response string as JSON (may be wrapped in ```json ... ```)
        try:
            content = response_str.strip()
            if content.startswith("```"):
                # Strip markdown code fences
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(content)
        except Exception as e:
            raise RuntimeError(
                f"Gemma returned non-JSON content: {response_str[:200]}... Error: {e}"
            )

    def _build_research_prompt(self, provider_data: List[Dict]) -> str:
        return f"""Verify the free-tier model catalog.

Current provider payload (truncated):
{json.dumps(provider_data[:50], indent=2)[:2000]}

Tasks:
1. Confirm each model's context window, token quota, and availability.
2. Detect any new free models added recently.
3. Detect deprecated or migrated models.
4. Flag any discrepancies (e.g., mismatched context size).
5. Return ONLY JSON with these keys:
   - verified_models: [{{"name": str, "provider": str, "context_window": int, "quota_per_day": int, "status": "active"}}]
   - new_models: [...]
   - deprecated_models: [...]
   - discrepancies: [{{"model": str, "field": str, "old_value": any, "new_value": any, "confidence": float}}]

All confidence scores must be >= {self.cfg.get("confidence_minimum", 0.85)}."""

    # ── 3️⃣ Diff engine ─────────────────────────────────────────────────

    async def _compute_diffs(
        self, research: Dict, trace_id: str
    ) -> List[Dict]:
        """Compare research results against the current database."""
        async with self.lock:
            current = await self._load_current_db()
        changes = []

        def _exists(name: str) -> bool:
            for prov in current.get("providers", {}).values():
                if any(m.get("name") == name for m in prov):
                    return True
            return False

        for m in research.get("new_models", []):
            if not _exists(m.get("name", "")):
                changes.append({"type": "add", "model": m})

        for m in research.get("deprecated_models", []):
            if _exists(m.get("name", "")):
                changes.append({"type": "remove", "model": m})

        for d in research.get("discrepancies", []):
            if d.get("confidence", 0) >= self.cfg.get("confidence_minimum", 0.85):
                changes.append({
                    "type": "update",
                    "model_name": d.get("model", ""),
                    "field": d.get("field", ""),
                    "old": d.get("old_value"),
                    "new": d.get("new_value"),
                })

        max_changes = self.cfg.get("max_changes_per_cycle", 30)
        if len(changes) > max_changes:
            self.observability.log_event(
                EventType.WORKER_UPDATE,
                trace_id,
                {
                    "event": "model_updater_change_cap_exceeded",
                    "requested": len(changes),
                },
            )
            changes = changes[:max_changes]

        return changes

    # ── 4️⃣ Apply changes ──────────────────────────────────────────────

    async def _apply_changes(
        self, changes: List[Dict], trace_id: str
    ) -> None:
        """Persist verified changes to the DB atomically."""
        async with self.lock:
            db = await self._load_current_db()
            ts = datetime.now(timezone.utc).isoformat()

            for c in changes:
                if c["type"] == "add":
                    prov = c["model"].get("provider", "unknown")
                    db.setdefault("providers", {}).setdefault(prov, []).append(
                        {**c["model"], "added_at": ts}
                    )
                elif c["type"] == "remove":
                    for prov_models in db.get("providers", {}).values():
                        for m in prov_models:
                            if m.get("name") == c["model"].get("name"):
                                m["status"] = "deprecated"
                                m["deprecated_at"] = ts
                elif c["type"] == "update":
                    for prov_models in db.get("providers", {}).values():
                        for m in prov_models:
                            if m.get("name") == c["model_name"]:
                                m[c["field"]] = c["new"]
                                m["last_verified"] = ts

            # Atomic write via thread pool
            def _atomic_write():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                tmp = self.db_path.with_suffix(".tmp")
                tmp.write_text(json.dumps(db, indent=2))
                tmp.replace(self.db_path)

            await anyio.to_thread.run_sync(_atomic_write)

            # Audit snapshot
            def _write_audit():
                path = self.audit_dir / f"{ts}_{trace_id}.json"
                path.write_text(
                    json.dumps({"changes": changes, "db_snapshot": db}, indent=2)
                )

            await anyio.to_thread.run_sync(_write_audit)

        self.observability.log_event(
            EventType.WORKER_UPDATE,
            trace_id,
            {"event": "model_updater_changes_applied", "count": len(changes)},
        )

    # ── 5️⃣ Markdown report ────────────────────────────────────────────

    async def _render_markdown_report(self, trace_id: str) -> None:
        """Generate a human-readable markdown report from the DB."""
        async with self.lock:
            db = await self._load_current_db()

        md_lines = [
            f"# 📊 Model Catalog – {datetime.now(timezone.utc).date()}",
            "",
            "| Provider | Model | Context | Daily Quota | Status |",
            "|----------|-------|---------|------------|--------|",
        ]
        for provider, models in db.get("providers", {}).items():
            for m in models:
                status = m.get("status", "active")
                md_lines.append(
                    f"| {provider} | {m.get('name', '?')} | {m.get('context_window', '?')} | "
                    f"{m.get('quota_per_day', '?')} | {status} |"
                )
        report_path = Path("docs/research/model_db/CURRENT_MODELS.md")
        await anyio.to_thread.run_sync(report_path.write_text, "\n".join(md_lines))
        self.observability.log_event(
            EventType.WORKER_REPORT,
            trace_id,
            {"event": "model_updater_report_generated", "path": str(report_path)},
        )

    # ── Database helpers ─────────────────────────────────────────────────

    async def _load_current_db(self) -> Dict:
        """Load the current model database via thread pool."""
        if self.db_path.exists():
            return await anyio.to_thread.run_sync(
                lambda: json.loads(self.db_path.read_text())
            )
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "providers": {}}

    # ── Status ───────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        """Return current scheduler status."""
        job = self.scheduler.get_job("model_updater")
        return {
            "enabled": self.cfg.get("enabled", True),
            "schedule": self.cfg.get("schedule"),
            "next_run": str(job.next_run_time) if job else None,
            "paused": bool(job and job.next_run_time is None),
        }
