# 🔱 Workers — Background Worker Framework
**AP Token**: `AP-WORKERS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Workers package — autonomous background workers for model updates, freshness checking, and YouTube ingestion.
**Tags**: workers, background, model-updater, freshness-checker, youtube, daemon
**Cross-references**: src/omega/workers/model_updater.py, src/omega/workers/freshness_checker.py, src/omega/workers/youtube_worker.py, src/omega/oracle/model_gateway.py, src/omega/oracle/resource_guard.py

---

## Overview

The `workers` package provides **autonomous background workers** that run continuously or on schedule to maintain the Omega Engine's knowledge freshness and model catalog. Each worker is designed for production deployment with:

- **AnyIO compliance** (M1) — proper async lifecycle
- **ResourceGuard protection** — OOM prevention for model inference
- **Observability integration** — structured event logging
- **Audit trails** — JSONL logs for every operation
- **Graceful degradation** — never crash the engine

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Workers Package                         │
├─────────────────────────────────────────────────────────────┤
│  model_updater.py    │  ModelUpdaterWorker — catalog sync   │
│  freshness_checker.py│  FreshnessChecker — staleness detect │
│  youtube_worker.py   │  YouTubeWorker — ingestion daemon    │
│  __init__.py         │  Exports ModelUpdaterWorker          │
└─────────────────────────────────────────────────────────────┘
```

**Shared Patterns**:
- `async start()` / `async stop()` lifecycle
- `async run_forever()` for daemon mode
- `async run_update_cycle()` for single execution
- Concurrency guards (`anyio.Lock`) against overlapping runs
- Structured observability events with trace IDs

---

## ModelUpdaterWorker

Automated model catalog researcher that fetches free-model offerings from provider APIs, verifies with Gemma 4-31B, diffs against local DB, and applies updates.

### Configuration

```python
config = {
    "enabled": True,
    "schedule": "0 * * * *",  # Hourly at minute 0
    "model": "gemma-4-31b-it",  # Verification model
    "providers": [
        {"name": "openrouter", "enabled": True},
        {"name": "google", "enabled": True},
        {"name": "opencode-zen", "enabled": True}
    ],
    "confidence_minimum": 0.85,
    "max_changes_per_cycle": 30
}
```

### Constructor

```python
ModelUpdaterWorker(
    model_gateway: ModelGateway,
    observability: ObservabilityEngine,
    config: Dict,
    guard: ResourceGuard
)
```

| Parameter | Purpose |
|-----------|---------|
| `model_gateway` | Model inference for Gemma verification |
| `observability` | Event logging (WORKER_START, WORKER_COMPLETE, ERROR) |
| `config` | Worker configuration (see above) |
| `guard` | ResourceGuard for OOM protection during inference |

### Lifecycle Methods

#### `async start() -> None`
Enable scheduled operation. Does not start background loop — caller manages via `run_forever()`.

#### `async run_forever() -> None`
Run update loop indefinitely (call inside `anyio.create_task_group()`).

#### `async stop() -> None`
Signal worker to stop on next iteration.

#### `async run_update_cycle() -> None`
Execute one full research → diff → update cycle. Safe to call manually.

**Concurrency Guard**: Uses `_running_lock` — if cycle already in progress, logs warning and skips.

### Cycle Phases

| Phase | Method | Description |
|-------|--------|-------------|
| 1️⃣ Fetch | `_fetch_all_providers()` | Parallel HTTP fetch from provider APIs |
| 2️⃣ Research | `_research_with_gemma()` | Gemma 4-31B verifies/enriches data |
| 3️⃣ Diff | `_compute_diffs()` | Compare against local DB |
| 4️⃣ Apply | `_apply_changes()` | Atomic write + audit snapshot |
| 5️⃣ Report | `_render_markdown_report()` | Generate CURRENT_MODELS.md |

### Provider Endpoints

| Provider | URL | Auth | Parser |
|----------|-----|------|--------|
| OpenRouter | `https://openrouter.ai/api/v1/models` | None (public) | `openrouter` |
| Google | `https://generativelanguage.googleapis.com/v1beta/models` | Query param `key` | `google` |
| OpenCode-Zen | `https://opencode.ai/zen/v1/models` | None (public) | `opencode` |

### Data Flow

```
Provider APIs → Raw JSON → Gemma Verification → Structured JSON
                                                    ↓
                                            Diff Engine → Changes
                                                    ↓
                                            Atomic Write (tmp→replace)
                                                    ↓
                                            Audit Snapshot + Markdown Report
```

### Database

- **Source of truth**: `docs/research/model_db/CURRENT_MODELS.json`
- **Audit dir**: `data/audit/model_updater/{timestamp}_{trace_id}.json`
- **Report**: `docs/research/model_db/CURRENT_MODELS.md`

### Usage Example

```python
from omega.workers import ModelUpdaterWorker
from omega.oracle import ModelGateway, ResourceGuard
from omega.observability import ObservabilityEngine

gateway = ModelGateway()
guard = ResourceGuard(max_ram_mb=4096)
obs = ObservabilityEngine()

config = {
    "enabled": True,
    "schedule": "0 * * * *",
    "model": "gemma-4-31b-it",
    "providers": [
        {"name": "openrouter", "enabled": True},
        {"name": "google", "enabled": True}
    ],
    "confidence_minimum": 0.85,
    "max_changes_per_cycle": 30
}

worker = ModelUpdaterWorker(gateway, obs, config, guard)

# Run once (e.g., from scheduler)
await worker.run_update_cycle()

# Or run as daemon
async with anyio.create_task_group() as tg:
    tg.start_soon(worker.run_forever)
```

### CLI

```bash
# Run one cycle
python -m omega.workers.model_updater --once

# Run as daemon (hourly)
python -m omega.workers.model_updater --daemon
```

---

## FreshnessChecker

Automated model registry staleness detection monitoring Hugging Face Hub (lastModified, sha, file changes) and Artificial Analysis (Intelligence Index version, evaluation dates).

### Thresholds

| Signal | Threshold | Description |
|--------|-----------|-------------|
| `capability` | 90 days | AA Intelligence Index scores |
| `parameter` | 180 days | HF Hub parameter data |
| `metadata` | 30 days | HF Hub tags, pipeline_tag, description |
| `validation` | 7 days | Validation status |

### Check Tiers

| Tier | Models | Use Case |
|------|--------|----------|
| `critical` | Top 10 by usage | High-priority models |
| `standard` | Next 40 | Regular maintenance |
| `low` | Next 100 | Bulk checking |
| `all` | All models | Full audit |

### Constructor

```python
FreshnessChecker(
    db_path: Path = Path("config/model_registry/index.sqlite"),
    aa_api_key: Optional[str] = None,
    hf_client: Optional[HuggingFaceHubClient] = None,
    aa_client: Optional[ArtificialAnalysisClient] = None
)
```

### Core Methods

#### `check_model(model: dict) -> ModelFreshnessResult`

Run freshness check for a single model.

**Result fields**:
- `hf_last_modified`, `hf_sha`, `hf_days_since_modified`
- `aa_intelligence_index`, `aa_last_evaluated`, `aa_days_since_eval`
- `capability_stale`, `parameter_stale`, `metadata_stale`, `overall_stale`
- `needs_revalidation`, `needs_reenrichment`

#### `run_check(tier="standard", notify=False, dry_run=False) -> FreshnessReport`

Execute full freshness check for a tier.

```python
checker = FreshnessChecker()
report = await checker.run_check(tier="critical", notify=True)

print(f"Checked: {report.models_checked}")
print(f"Stale: {report.models_stale} ({report.stale_rate:.1%})")
print(f"Errors: {report.models_errors}")
```

**Notification**: If `notify=True` and stale models found, sends Hivemind handoff to `researcher` entity.

### CLI

```bash
# Standard tier check
python -m omega.workers.freshness_checker --tier standard

# Critical tier with notification
python -m omega.workers.freshness_checker --tier critical --notify

# Dry run (no DB updates)
python -m omega.workers.freshness_checker --tier all --dry-run

# JSON output
python -m omega.workers.freshness_checker --tier standard --json
```

### Integration with Background Researcher

The freshness checker is designed to be called from the 24/7 background researcher loop:

```python
# In background_researcher loop
from omega.workers.freshness_checker import FreshnessChecker

checker = FreshnessChecker()
report = checker.run_check(tier="standard", notify=True)
# Runs every 15 min via systemd timer
```

---

## YouTubeWorker

Autonomous YouTube ingestion and synthesis daemon. Ingests URLs from queue, expands playlists, searches by topic, runs Sieve→Sign→Chain→Persist pipeline, synthesizes cross-video knowledge.

**Note**: Redis queue backend was removed (D-redis-20260928). Queue-backed methods raise `ProviderUnavailableError`. The fetch/synthesis surface remains functional.

### Configuration

```yaml
# config/youtube_worker.yaml
playlist:
  timeout: 120
searxng:
  url: "http://localhost:8017"
ingestion:
  request_delay: 2.0
synthesis:
  enabled: true
  auto_synthesize_threshold: 5
  model: "qwen3-1.7b"
  temperature: 0.3
  max_tokens: 2048
worker:
  max_batch_size: 10
```

### Core Components

| Component | Purpose |
|-----------|---------|
| `PlaylistExpander` | yt-dlp --flat-playlist for video metadata |
| `TopicSearcher` | SearXNG video search by topic |
| `TranscriptFetcher` | youtube-transcript-api with rate limiting |
| `VideoIngester` | Sieve→Sign→Chain→Persist via YouTubeResearchModule |
| `CrossVideoSynthesizer` | Local model inference (ResourceGuard-protected) |
| `HivemindLogger` | Atomic JSONL logging to HALL_OF_RECORDS |

### State Machine

```
IDLE → [DEQUEUE → FETCH → INGEST → SAVE] × N → [SYNTHESIZE if threshold] → IDLE
```

### Somatic Save-Points

Crash recovery via JSON state file (`data/workers/youtube_worker_state.json`):
- `cycle_id`, `state`, `timestamp`, `cycle_count`, `metrics`

### ResourceGuard Integration

- **2048 MB** limit for model inference (OOM protection)
- Synthesis runs inside `async with resource_guard:`

### Usage (Non-Queue Mode)

```python
from omega.workers import YouTubeWorker

config = load_yaml("config/youtube_worker.yaml")
worker = YouTubeWorker(config=config)

# Ingest single video
job = IngestJob(job_id="yt_abc123", url="https://youtube.com/watch?v=...", source="file")
result = await worker.ingester.ingest(job)

# Search by topic
results = await worker.topic_searcher.search("sovereign AI 2026", max_results=10)

# Synthesize across videos
synthesis = await worker.synthesizer.synthesize(
    topic="sovereign AI",
    video_results=ingested_videos
)

# Daemon mode (requires queue backend restoration)
# await worker.run_cycle()
```

### CLI

```bash
# Run once
python -m omega.workers.youtube_worker --once

# Daemon mode (with watchdog, CPU ceiling)
python -m omega.workers.youtube_worker --daemon --cpu-ceiling 85 --interval 5

# Submit URL (requires queue)
python -m omega.workers.youtube_worker --queue-url "https://..."

# Expand playlist
python -m omega.workers.youtube_worker --playlist "https://youtube.com/playlist?list=..."

# Search topic
python -m omega.workers.youtube_worker --topic "sovereign AI 2026"

# Batch process
python -m omega.workers.youtube_worker --batch --batch-size 10

# Status
python -m omega.workers.youtube_worker --status
```

### Systemd Deployment

```bash
cp config/systemd/omega-youtube-worker.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now omega-youtube-worker.timer
```

---

## Mandate Compliance

| Mandate | ModelUpdater | FreshnessChecker | YouTubeWorker |
|---------|--------------|------------------|---------------|
| **M1 AnyIO** | ✅ All async | ✅ All async | ✅ All async |
| **M7 Local-First** | ✅ Gemma local | ✅ Local DB first | ✅ Local synthesis |
| **M9 Error Integrity** | ✅ Typed errors | ✅ Typed errors | ✅ Typed errors |
| **M11 Soul Integrity** | N/A | N/A | N/A |
| **M13 Temple-Grade** | ✅ Atomic writes | ✅ Atomic DB updates | ✅ Save-points |
| **M23 Failure Integrity** | ✅ Hard-stop on failure | ✅ Re-raises | ✅ Watchdog + crash-loop breaker |

---

## Testing

```bash
pytest tests/test_model_updater.py tests/test_freshness_checker.py tests/test_youtube_worker.py -v
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ WORKERS-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

