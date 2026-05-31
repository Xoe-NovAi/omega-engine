# 🔱 Omega Engine — Automated Model Updater Design
# ⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_model_updater ⬡ PHASE-1

**AP Token**: `AP-MODEL-UPDATER-DESIGN-v1.0.0`
**Status**: 🔲 DESIGN PHASE — Ready for implementation
**Last Updated**: 2026-05-16

---

## §1 Executive Summary

This document specifies the architecture for an automated background worker that keeps the Omega Engine's model library continuously up-to-date. The system monitors three provider APIs (OpenRouter, Google AI Studio, OpenCode Zen), detects changes, updates the local database, and notifies the observability system of significant changes.

**Key Design Decisions:**
- **Polling-based** (not webhooks) — None of the target providers offer webhook-based model change notifications
- **AnyIO-native** — Integrates with Omega's existing async architecture
- **Observability-first** — All state changes emit events to the existing `ObservabilityEngine`
- **Idempotent** — Safe to run concurrently; uses file-based locking

---

## §2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        OMEGA MODEL UPDATER                             │
│                         (Background Worker)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │  Scheduler  │───▶│   Fetcher   │───▶│ Normalizer  │                │
│  │  (APTimer)  │    │   (API)     │    │   (JSON)    │                │
│  └─────────────┘    └─────────────┘    └─────────────┘                │
│        │                                      │                       │
│        │                                      ▼                       │
│        │                             ┌─────────────┐                  │
│        │                             │ Diff Engine │                  │
│        │                             │ (Changes)   │                  │
│        │                             └─────────────┘                  │
│        │                                   │                          │
│        │            ┌─────────────────────┼─────────────────────┐    │
│        │            ▼                     ▼                     ▼    │
│        │     ┌─────────────┐      ┌─────────────┐      ┌────────────┐ │
│        │     │   Notifier  │      │  Database   │      │   Report   │ │
│        │     │ (Observab.) │      │   Updater   │      │  Generator │ │
│        │     └─────────────┘      └─────────────┘      └────────────┘ │
│        │            │                     │                     │    │
│        └────────────┴─────────────────────┴─────────────────────┘    │
│                          │            │            │                  │
│                          ▼            ▼            ▼                  │
│                   ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│                   │Observab. │ │ JSON     │ │ Markdown │              │
│                   │ Events   │ │ Database │ │ Report   │              │
│                   │ (JSONL)  │ │ (.json)  │ │ (.md)    │              │
│                   └──────────┘ └──────────┘ └──────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

                              EXTERNAL APIS
        ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
        │  OpenRouter     │  │ Google AI Studio│  │ OpenCode Zen    │
        │  (public)       │  │ (API key)       │  │ (public)        │
        └─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## §3 Component Breakdown

### 3.1 Scheduler (`scheduler.py`)

**Responsibility**: Triggers the update workflow on a configurable schedule.

**Design Choices:**
- **APScheduler over Celery**: Lighter weight, native AnyIO support via `AsyncIOScheduler`
- **No external dependencies**: Runs in-process with the Omega Engine
- **Three modes**: `interval` (recommended), `cron`, `one-shot`

**Configuration:**
```yaml
# config/omega.yaml
model_updater:
  enabled: true
  schedule:
    type: interval
    minutes: 60  # Check every hour
  # Or cron-style:
  #   type: cron
  #   hour: "*/6"  # Every 6 hours
  providers:
    - openrouter
    - google
    - opencode_zen
  change_threshold: 3  # Notify if ≥3 models change
```

**Code Skeleton:**
```python
# src/omega/model_updater/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import anyio

class ModelUpdaterScheduler:
    def __init__(self, config: dict):
        self.config = config
        self.scheduler = AsyncIOScheduler()
        self._running = False

    async def start(self):
        if not self.config.get("enabled", False):
            return
        trigger = IntervalTrigger(
            minutes=self.config.get("schedule", {}).get("minutes", 60)
        )
        self.scheduler.add_job(
            self._run_update_cycle,
            trigger,
            id="model_updater",
            replace_existing=True,
        )
        self.scheduler.start()
        self._running = True

    async def stop(self):
        self.scheduler.shutdown(wait=True)
        self._running = False

    async def _run_update_cycle(self):
        from .orchestrator import ModelUpdateOrchestrator
        orchestrator = ModelUpdateOrchestrator(self.config)
        await orchestrator.run()
```

### 3.2 Fetcher (`fetcher.py`)

**Responsibility**: Query provider APIs and return raw model data.

**Design Choices:**
- **Parallel fetching**: All three providers queried concurrently via `anyio.TaskGroup`
- **Timeout per provider**: 10s timeout, graceful degradation if one fails
- **Error resilience**: Individual provider failures don't block others

**Code Skeleton:**
```python
# src/omega/model_updater/fetcher.py
import anyio
import httpx
from typing import Dict, Any, List
from dataclasses import dataclass
import os

@dataclass
class ProviderSnapshot:
    provider: str
    timestamp: str
    data: Dict[str, Any]
    error: str | None = None

class ModelFetcher:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def fetch_all(self) -> List[ProviderSnapshot]:
        async with anyio.create_task_group() as tg:
            results = [None] * 3
            tg.start_soon(self._fetch_openrouter, results, 0)
            tg.start_soon(self._fetch_google, results, 1)
            tg.start_soon(self._fetch_opencode_zen, results, 2)
        return results

    async def _fetch_openrouter(self, results: List, idx: int):
        try:
            client = await self._get_client()
            resp = await client.get("https://openrouter.ai/api/v1/models")
            resp.raise_for_status()
            data = resp.json()
            results[idx] = ProviderSnapshot(
                provider="openrouter",
                timestamp=self._now(),
                data=self._normalize_openrouter(data),
            )
        except Exception as e:
            results[idx] = ProviderSnapshot(provider="openrouter", data={}, error=str(e))

    async def _fetch_google(self, results: List, idx: int):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            results[idx] = ProviderSnapshot(provider="google", data={}, error="No API key")
            return
        try:
            client = await self._get_client()
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            results[idx] = ProviderSnapshot(
                provider="google",
                timestamp=self._now(),
                data=self._normalize_google(data),
            )
        except Exception as e:
            results[idx] = ProviderSnapshot(provider="google", data={}, error=str(e))

    async def _fetch_opencode_zen(self, results: List, idx: int):
        try:
            client = await self._get_client()
            resp = await client.get("https://opencode.ai/zen/v1/models")
            resp.raise_for_status()
            data = resp.json()
            results[idx] = ProviderSnapshot(
                provider="opencode_zen",
                timestamp=self._now(),
                data=self._normalize_opencode_zen(data),
            )
        except Exception as e:
            results[idx] = ProviderSnapshot(provider="opencode_zen", data={}, error=str(e))

    def _normalize_openrouter(self, data: Dict) -> Dict:
        free = []
        for m in data.get("data", []):
            p = m.get("pricing", {})
            try:
                if float(p.get("prompt", 1)) == 0 and float(p.get("completion", 1)) == 0:
                    free.append({"id": m["id"], "context": m.get("context_length", 0), "name": m.get("name")})
            except (ValueError, TypeError):
                pass
        return {"free_count": len(free), "free": free}

    def _normalize_google(self, data: Dict) -> Dict:
        gemma = []
        for m in data.get("models", []):
            name = m["name"].replace("models/", "")
            if "gemma" in name:
                gemma.append({"id": name, "methods": m.get("supportedGenerationMethods", [])})
        return {"gemma_count": len(gemma), "gemma": gemma}

    def _normalize_opencode_zen(self, data: Dict) -> Dict:
        models = data.get("models", data.get("data", []))
        free_ids = [m["id"] for m in models if "free" in m.get("id", "").lower()]
        return {"total": len(models), "free": len(free_ids), "all": [m["id"] for m in models], "free_ids": free_ids}

    def _now(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
```

### 3.3 Normalizer (`normalizer.py`)

**Responsibility**: Convert raw API responses into a canonical internal format.

**Design Choices:**
- **Schema validation**: Use Pydantic for strict typing
- **Graceful missing fields**: Default to sensible values (e.g., `context: 0`)
- **Provider-specific logic**: Each provider has unique quirks (see fetcher patterns above)

**Schema:**
```python
# src/omega/model_updater/schemas.py
from pydantic import BaseModel
from typing import List

class ModelEntry(BaseModel):
    id: str
    context: int = 0
    name: str | None = None
    methods: List[str] = []

class ProviderSnapshot(BaseModel):
    provider: str
    timestamp: str
    free_count: int = 0
    models: List[ModelEntry] = []

class ModelDatabase(BaseModel):
    last_updated: str
    providers: dict[str, ProviderSnapshot]
```

### 3.4 Diff Engine (`diff_engine.py`)

**Responsibility**: Compare current state against stored state and detect changes.

**Design Choices:**
- **Set-based diffing**: Fast O(n) comparison of model IDs
- **Three change types**: `added`, `removed`, `modified`
- **Significance scoring**: Configurable threshold for notifications

**Code Skeleton:**
```python
# src/omega/model_updater/diff_engine.py
from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class ModelChange:
    type: str  # "added", "removed", "modified"
    provider: str
    model_id: str
    old_value: dict | None = None
    new_value: dict | None = None

@dataclass
class DiffResult:
    changes: List[ModelChange] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    is_significant: bool = False

class DiffEngine:
    def __init__(self, significance_threshold: int = 3):
        self.threshold = significance_threshold

    def compute_diff(self, old: dict, new: dict) -> DiffResult:
        changes = []
        for provider in ["openrouter", "google", "opencode_zen"]:
            old_models = self._extract_model_ids(old.get(provider, {}))
            new_models = self._extract_model_ids(new.get(provider, {}))

            added = new_models - old_models
            removed = old_models - new_models

            for m in added:
                changes.append(ModelChange(type="added", provider=provider, model_id=m, new_value=self._get_model(new, provider, m)))
            for m in removed:
                changes.append(ModelChange(type="removed", provider=provider, model_id=m, old_value=self._get_model(old, provider, m)))

        total_changes = len(changes)
        return DiffResult(
            changes=changes,
            summary={"total": total_changes, "added": sum(1 for c in changes if c.type == "added"), "removed": sum(1 for c in changes if c.type == "removed")},
            is_significant=total_changes >= self.threshold,
        )

    def _extract_model_ids(self, provider_data: dict) -> Set[str]:
        if provider == "openrouter":
            return {m["id"] for m in provider_data.get("free", [])}
        elif provider == "google":
            return {m["id"] for m in provider_data.get("gemma", [])}
        elif provider == "opencode_zen":
            return set(provider_data.get("all", []))
        return set()
```

### 3.5 Notifier (`notifier.py`)

**Responsibility**: Emit events to Omega's observability system and trigger alerts.

**Design Choices:**
- **Reuse ObservabilityEngine**: No separate notification system needed
- **Event types**: `model_update.started`, `model_update.completed`, `model_update.changes_detected`
- **Silent mode**: Minor changes (below threshold) logged but not alerted

**Code Skeleton:**
```python
# src/omega/model_updater/notifier.py
from omega.observability import get_engine, EventType

class ModelUpdateNotifier:
    def __init__(self):
        self._engine = get_engine()
        self._trace_id_prefix = "mupd"

    def notify_started(self, providers: List[str]):
        self._engine.log_event(
            event_type="model_update.started",
            trace_id=f"{self._trace_id_prefix}_{self._now_ts()}",
            data={"providers": providers},
        )

    def notify_completed(self, result: DiffResult, duration_ms: float):
        self._engine.log_event(
            event_type="model_update.completed",
            trace_id=f"{self._trace_id_prefix}_{self._now_ts()}",
            data={
                "changes": result.summary,
                "is_significant": result.is_significant,
                "duration_ms": duration_ms,
            },
        )

    def notify_changes(self, result: DiffResult):
        if not result.is_significant:
            return
        for change in result.changes:
            self._engine.log_event(
                event_type="model_update.changes_detected",
                trace_id=f"{self._trace_id_prefix}_{self._now_ts()}",
                data={
                    "change_type": change.type,
                    "provider": change.provider,
                    "model_id": change.model_id,
                },
            )

    def _now_ts(self) -> str:
        import uuid
        return uuid.uuid4().hex[:8]
```

### 3.6 Database Updater (`database.py`)

**Responsibility**: Persist the model database to disk and maintain history.

**Design Choices:**
- **File-based storage**: JSON files in `docs/research/model_db/`
- **Atomic writes**: Write to temp file, then rename (crash-safe)
- **History retention**: Keep last 7 snapshots for rollback capability

**Code Skeleton:**
```python
# src/omega/model_updater/database.py
import json
from pathlib import Path
from typing import Dict, Any
import shutil

class ModelDatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        last_state = self.db_path / ".last_state.json"
        if last_state.exists():
            with open(last_state) as f:
                return json.load(f)
        return {}

    def save(self, data: Dict[str, Any]):
        last_state = self.db_path / ".last_state.json"
        tmp = self.db_path / ".last_state_tmp.json"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        tmp.rename(last_state)

    def save_snapshot(self, data: Dict[str, Any]):
        timestamp = data.get("timestamp", "unknown")
        path = self.db_path / f"snapshots/{timestamp[:10]}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
```

---

## §4 Data Flow

### 4.1 Normal Update Cycle (No Changes)

```
Scheduler triggers
    ↓
Fetcher fetches all 3 providers (parallel)
    ↓
Normalizer converts to canonical format
    ↓
DiffEngine compares with last_state.json
    ↓
[NO_CHANGES] → Notifier logs "model_update.completed" (non-significant)
    ↓
Database saves snapshot (if configured)
    ↓
Done
```

### 4.2 Change Detected Cycle

```
Scheduler triggers
    ↓
Fetcher fetches all 3 providers (parallel)
    ↓
Normalizer converts to canonical format
    ↓
DiffEngine compares with last_state.json
    ↓
[CHANGES FOUND] → Notifier logs "model_update.changes_detected" for each
    ↓
Database saves new state + snapshot
    ↓
ReportGenerator creates diff report (markdown)
    ↓
Notifier logs "model_update.completed" (significant=true)
    ↓
Done
```

### 4.3 Error Recovery Cycle

```
Fetcher fails on provider X
    ↓
[PARTIAL_DATA] → Log error to Observability
    ↓
Continue with remaining providers
    ↓
If ≥1 provider succeeded: continue pipeline
    ↓
If all failed: Log "model_update.failed", skip this cycle
    ↓
On next cycle: retry (no exponential backoff needed — provider may be transient)
```

---

## §5 Integration Points

### 5.1 Observability Integration

The updater emits events that the existing `ObservabilityEngine` processes:

| Event Type | Data | Purpose |
|------------|------|---------|
| `model_update.started` | `{providers: [...]}` | Track cycle start |
| `model_update.completed` | `{changes: {...}, is_significant: bool}` | Track completion |
| `model_update.changes_detected` | `{change_type, provider, model_id}` | Alert on changes |
| `model_update.error` | `{provider, error}` | Track failures |

**Integration Code:**
```python
# In notifier.py
from omega.observability import get_engine

engine = get_engine()
engine.log_event(event_type, trace_id, data)
```

### 5.2 Configuration Integration

Load settings from `config/omega.yaml`:

```yaml
model_updater:
  enabled: true
  schedule:
    type: interval
    minutes: 60
  change_threshold: 3
  providers:
    - openrouter
    - google
    - opencode_zen
```

### 5.3 CLI Integration

Add CLI commands to `src/omega/cli/oracle_cli.py`:

```bash
omega model-update run          # Run once immediately
omega model-update status       # Show last run status
omega model-update history      # Show recent changes
```

---

## §6 Deployment Options

### 6.1 Option A: In-Process Scheduler (Recommended)

Runs within the Omega Engine process using APScheduler's AsyncIOScheduler.

**Pros:**
- Single process, no额外的服务
- Automatic start/stop with Omega Engine
- Shares observability connection

**Cons:**
- If Omega Engine crashes, updater stops
- No separate resource isolation

**Configuration:**
```python
# src/omega/model_updater/__init__.py
def setup_model_updater(app: OmegaEngine):
    scheduler = ModelUpdaterScheduler(app.config["model_updater"])
    app.lifecycle.add_startup(scheduler.start)
    app.lifecycle.add_shutdown(scheduler.stop)
```

### 6.2 Option B: Systemd Timer (Alternative)

Runs as a separate script triggered by systemd timers.

**Pros:**
- Isolated process, won't affect Omega Engine
- Standard Linux service management

**Cons:**
- Separate process, must handle its own observability
- More complex deployment

**Implementation:**
```ini
# /etc/systemd/system/omega-model-updater.service
[Unit]
Description=Omega Model Updater

[Service]
Type=oneshot
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python -m omega.model_updater.run
User=arcana-novai
```
```ini
# /etc/systemd/system/omega-model-updater.timer
[Unit]
Description=Run Omega Model Updater hourly

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
```

### 6.3 Recommendation

**Use Option A (In-Process)** for Phase 1 because:
1. Simpler deployment (one service to manage)
2. Shared observability infrastructure
3. Lower operational overhead
4. Sufficient reliability for hourly updates

Switch to Option B only if:
- Omega Engine experiences frequent crashes
- Model update cycle takes >30s (blocking the main process)
- Operational requirements demand isolation

---

## §7 Report Generation

### 7.1 Markdown Diff Report

On significant changes, generate `docs/research/model_db/CHANGES_<date>.md`:

```markdown
# Model Library Changes — 2026-05-16

## Summary
- **Total Changes**: 5
- **Added**: 3
- **Removed**: 2

## OpenRouter — Added
- `qwen/qwen3-next-80b-a3b-instruct:free` (262K ctx)
- `nvidia/nemotron-nano-9b-v2:free` (128K ctx)
- `google/lyria-3-pro-preview` (1M ctx)

## OpenRouter — Removed
- `meta-llama/llama-3.1-8b-instruct:free` (replaced by 3.3)

## Google — No Changes

## OpenCode Zen — No Changes
```

---

## §8 Error Handling

| Scenario | Handling |
|----------|----------|
| Single provider timeout | Log error, continue with remaining providers |
| All providers timeout | Log `model_update.error`, skip cycle |
| Disk full | Raise exception, let it propagate to observability |
| Corrupt JSON in last_state | Treat as "no previous state", log warning |
| API rate limiting | Backoff to 2x interval on next cycle |

---

## §9 Implementation Roadmap

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Create `src/omega/model_updater/` module structure | 1h |
| 2 | Implement `fetcher.py` with parallel API calls | 2h |
| 3 | Implement `normalizer.py` with Pydantic schemas | 1h |
| 4 | Implement `diff_engine.py` for change detection | 1h |
| 5 | Implement `database.py` for persistence | 1h |
| 6 | Implement `notifier.py` with observability integration | 1h |
| 7 | Implement `scheduler.py` with APScheduler | 1h |
| 8 | Implement `orchestrator.py` to wire all components | 1h |
| 9 | Add CLI commands (`omega model-update`) | 1h |
| 10 | Write unit tests (mock API responses) | 2h |
| 11 | Integration test against live APIs | 1h |

**Total Estimated**: ~12 hours

---

## §10 Related Research Items

This design builds on:
- **R-MODEL-DB** (Complete): `scripts/check_free_models.sh` — manual baseline
- **R-ZEN** (Complete): OpenCode Zen model reference
- **R-OR** (Complete): OpenRouter free model landscape
- **R-GEMMA-LIVE** (Complete): Google Gemma Live API validation

---

## §11 References

- Existing `docs/research/model_db/.last_state.json` — current state format
- Existing `scripts/check_free_models.sh` — manual baseline implementation
- Existing `src/omega/observability.py` — event logging patterns
- APScheduler docs: https://apscheduler.readthedocs.io/

---

*Design complete — ready for implementation.*