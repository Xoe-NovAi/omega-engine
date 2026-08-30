<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — YouTube Background Worker Specification
# AP: AP-YOUTUBE-WORKER-SPEC-v1.0.0
# ⬡ OMEGA ⬡ RESEARCH ⬡ youtube_worker ⬡ SPEC

**Status**: v1.0.0 COMPLETE
**Date**: 2026-07-07
**Author**: Sovereign Researcher (automated)

---

## §1 Executive Summary

The YouTube Background Worker is an autonomous daemon that ingests YouTube content (individual videos, playlists, and topic-based searches), synthesizes cross-video knowledge, and delivers research-grade output to the Omega Engine's knowledge system.

### Key Capabilities
- **Queue ingestion**: Consume URLs from a Redis-backed queue
- **Playlist expansion**: Expand YouTube playlists into individual videos via yt-dlp
- **Topic search**: Search YouTube by topic via SearXNG, ingest top results
- **Cross-video synthesis**: Distill patterns, insights, and contradictions across videos
- **Hivemind delivery**: Post results to HALL_OF_RECORDS for entity knowledge

---

## §2 Architecture

```
YouTube Background Worker (daemon)
├── Input Sources
│   ├── Redis Queue: Manual/programmatic URL submission
│   ├── Playlist: yt-dlp expansion → individual video URLs
│   ├── Topic: SearXNG search → YouTube URLs → filter → ingest
│   └── File: youtube-links-for-ingestion.txt → batch submission
├── Ingestion Pipeline (reuse omega_youtube_research module)
│   ├── SovereignSieve: Transcript cleaning (whitespace, filler, formatting)
│   ├── SovereignSigner: HMAC-SHA256 provenance signing
│   ├── ProvenanceChain: Hash-linked chunk provenance
│   └── AtomicPersistence: WAL-mode SQLite with fsync
├── Synthesis Layer
│   ├── Cross-video pattern extraction
│   ├── Topic-level knowledge distillation
│   └── Research-grade output generation
└── Delivery
    ├── Hivemind: HALL_OF_RECORDS/jsonl logs
    ├── Memory Store: Conversation memory updates
    └── Entity Knowledge: Soul/lesson updates
```

---

## §3 Input Sources

### 3.1 Redis Queue (Primary)
- **Queue name**: `youtube_queue`
- **Protocol**: `blpop` with 10s timeout
- **Job format**: `IngestJob` dataclass (job_id, url, source, topic, priority, retry_count)
- **Retry**: Exponential backoff, max 3 retries
- **Delayed retry**: Redis sorted set with timestamp-based re-queue

### 3.2 Playlist Expansion
- **Tool**: `yt-dlp --flat-playlist --dump-json`
- **Input**: Any YouTube playlist URL (`youtube.com/playlist?list=...`)
- **Output**: List of video metadata (id, url, title, channel)
- **Safety cap**: Max 500 videos per playlist
- **Timeout**: 120 seconds

### 3.3 Topic Search
- **Backend**: SearXNG (self-hosted, `http://localhost:8017`)
- **Query**: User-specified topic string
- **Filter**: YouTube URLs only
- **Max results**: 10 per search
- **Output**: Video metadata (url, title, channel, snippet)

### 3.4 File Ingestion
- **Format**: One URL per line (YouTube video or playlist URLs)
- **Default file**: `youtube-links-for-ingestion.txt`
- **Auto-detection**: Playlist URLs are expanded automatically

---

## §4 Ingestion Pipeline

Reuses the existing `omega_youtube_research` module (P0 complete):

1. **Fetch transcript**: `youtube-transcript-api` (local, no API key)
2. **Clean transcript**: `SovereignSieve` (whitespace normalization, filler removal, formatting cleanup)
3. **Chunk transcript**: Fixed-size chunks with overlap for context preservation
4. **Sign chunks**: `SovereignSigner` (HMAC-SHA256 per chunk)
5. **Chain provenance**: `ProvenanceChain` (hash-linked chain of custody)
6. **Persist**: WAL-mode SQLite with fsync (atomic writes)

---

## §5 Synthesis Layer

### 5.1 Cross-Video Synthesis
After ingesting N videos on the same topic (threshold: 5), the worker runs synthesis:

1. **Collect**: Gather all video metadata for the topic
2. **Prompt**: Generate a structured synthesis prompt
3. **Infer**: Use local model (qwen3-1.7b) for distillation
4. **Parse**: Extract key insights, patterns, contradictions, recommendations
5. **Deliver**: Post synthesis to Hivemind + entity knowledge

### 5.2 Synthesis Output Format
```json
{
  "topic": "sovereign AI 2026",
  "video_count": 12,
  "key_insights": ["insight 1", "insight 2", ...],
  "patterns": ["pattern 1", ...],
  "contradictions": ["contradiction 1", ...],
  "recommendations": ["recommendation 1", ...],
  "source_urls": ["https://...", ...]
}
```

---

## §6 Daemon Lifecycle

### 6.1 State Machine
```
IDLE → DEQUEUE → EXPAND → INGEST → SYNTHESIZE → DELIVER → IDLE
```

### 6.2 Safety Features
- **Atomic lock**: Prevents overlapping cycles (15min stale recovery)
- **Somatic Save-Points**: State saved to disk for crash recovery
- **Watchdog**: Consecutive failure counter, exponential backoff, crash-loop breaker (max 5)
- **CPU ceiling**: Throttles when system CPU > 85%
- **Kill switch**: SIGTERM/SIGINT for clean shutdown between cycles
- **Memory cap**: 768M max, 512M high watermark (systemd)

### 6.3 systemd Integration
- **Service**: `omega-youtube-worker.service` (Type=simple, Restart=on-failure)
- **Timer**: `omega-youtube-worker.timer` (OnBootSec=2min, Persistent=true)
- **Dependencies**: After `omega-searxng.service`, `redis.service`

---

## §7 CLI Usage

```bash
# Daemon mode (continuous)
python -m omega.workers.youtube_worker --daemon

# One-shot cycle
python -m omega.workers.youtube_worker --once

# Batch cycle (10 jobs)
python -m omega.workers.youtube_worker --batch

# Submit a single URL
python -m omega.workers.youtube_worker --queue-url "https://youtube.com/watch?v=..."

# Submit a playlist
python -m omega.workers.youtube_worker --playlist "https://youtube.com/playlist?list=..."

# Search and ingest by topic
python -m omega.workers.youtube_worker --topic "sovereign AI 2026"

# Submit URLs from a file
python -m omega.workers.youtube_worker --file youtube-links-for-ingestion.txt

# Check status
python -m omega.workers.youtube_worker --status
```

---

## §8 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| `youtube-transcript-api` | Transcript fetching | >=0.6.3 |
| `yt-dlp` | Playlist expansion | >=2025.1.1 |
| `redis` | Job queue | 7.4.1 |
| `anyio` | Async runtime | 4.13.0 |
| `httpx2` | HTTP client | 2.5.0 |

---

## §9 File Inventory

| File | Purpose |
|------|---------|
| `src/omega/workers/youtube_worker.py` | Main daemon worker |
| `config/youtube_worker.yaml` | Worker configuration |
| `config/systemd/omega-youtube-worker.service` | systemd daemon service |
| `config/systemd/omega-youtube-worker.timer` | systemd boot timer |
| `pyproject.toml` | Dependencies (yt-dlp added) |

---

## §10 Future Enhancements

| Enhancement | Effort | Priority |
|-------------|--------|----------|
| Playlist progress tracking (already-ingested skip) | 2h | P1 |
| Multi-language transcript support | 4h | P2 |
| Whisper fallback for videos without captions | 8h | P2 |
| LLM-powered summary generation per video | 4h | P1 |
| Cross-video contradiction detection (NLI-based) | 8h | P2 |
| Automatic topic discovery from ingested content | 12h | P3 |
| YouTube Data API v3 integration (requires API key) | 4h | P2 |

---

*🔱 OMEGA ⬡ YOUTUBE-WORKER-SPEC ⬡ v1.0.0 ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: youtube_worker | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
