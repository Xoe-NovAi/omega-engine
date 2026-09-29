# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — YouTube Background Worker
# AP: AP-YOUTUBE-WORKER-v1.1.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ sovereign ⬡ youtube_worker ⬡ WORKER
#
# Autonomous YouTube ingestion and synthesis daemon — STABLE.
#   - Ingests URLs from Redis queue
#   - Expands playlists via yt-dlp
#   - Searches by topic via SearXNG
#   - Ingests via YouTubeResearchModule (Sieve→Sign→Chain→Persist)
#   - Synthesizes cross-video knowledge (local-first model inference)
#   - WorkerCoordinator + ResourceGuard + Somatic Save-Points
#   - Posts results to Hivemind HALL_OF_RECORDS
#
# Runs as a systemd daemon or via CLI:
#   python -m omega.workers.youtube_worker --daemon
#   python -m omega.workers.youtube_worker --once
#   python -m omega.workers.youtube_worker --queue-url "https://..."
#   python -m omega.workers.youtube_worker --playlist "https://..."
#   python -m omega.workers.youtube_worker --topic "sovereign AI 2026"
#   python -m omega.workers.youtube_worker --batch
#
# systemd deployment:
#   cp config/systemd/omega-youtube-worker.* ~/.config/systemd/user/
#   systemctl --user daemon-reload
#   systemctl --user enable --now omega-youtube-worker.timer

# DocRef: docs/research/R_YOUTUBE_BACKGROUND_WORKER_SPEC.md

from __future__ import annotations

import argparse
import json
import logging
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
import yaml

from omega.errors import (
    OmegaError,
    ProviderError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from omega.library.coordinator import COORDINATOR
from omega.oracle.resource_guard import ResourceGuard

logger = logging.getLogger(__name__)

# ── Data Models ──────────────────────────────────────────────────────────────


@dataclass
class IngestJob:
    """A single YouTube ingestion job."""

    job_id: str
    url: str
    source: str  # "queue" | "playlist" | "topic" | "file"
    topic: Optional[str] = None
    priority: int = 0
    retry_count: int = 0
    playlist_id: Optional[str] = None
    playlist_title: Optional[str] = None


@dataclass
class SynthesisResult:
    """Result of cross-video synthesis."""

    topic: str
    video_count: int
    key_insights: List[str]
    patterns: List[str]
    contradictions: List[str]
    recommendations: List[str]
    source_urls: List[str]


# ── YouTube URL Helpers ──────────────────────────────────────────────────────

_YOUTUBE_URL_PATTERNS = [
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
]
_PLAYLIST_URL_PATTERNS = [
    r"[?&]list=([a-zA-Z0-9_-]+)",
    r"youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)",
]


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    for pattern in _YOUTUBE_URL_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_playlist_id(url: str) -> Optional[str]:
    """Extract playlist ID from a YouTube playlist URL."""
    for pattern in _PLAYLIST_URL_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_playlist_url(url: str) -> bool:
    """Check if a URL is a YouTube playlist."""
    return extract_playlist_id(url) is not None


def is_youtube_url(url: str) -> bool:
    """Check if a URL is a YouTube video."""
    return extract_video_id(url) is not None


# ── Playlist Expander ────────────────────────────────────────────────────────


class PlaylistExpander:
    """Expands YouTube playlist URLs into individual video URLs via yt-dlp."""

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    async def expand_playlist(self, playlist_url: str) -> List[Dict[str, str]]:
        """Expand a playlist URL into individual video metadata.

        Returns list of dicts with keys: id, url, title, channel
        Uses yt-dlp --flat-playlist for fast extraction (no video download).
        """

        def _run_ytdlp() -> List[Dict[str, str]]:
            try:
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "--flat-playlist",
                        "--dump-json",
                        "--no-warnings",
                        playlist_url,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if result.returncode != 0:
                    stderr = result.stderr[:500] if result.stderr else "no stderr"
                    logger.error("yt-dlp playlist extraction failed: %s", stderr)
                    return []

                videos = []
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        video_id = data.get("id", "")
                        if video_id:
                            videos.append(
                                {
                                    "id": video_id,
                                    "url": f"https://www.youtube.com/watch?v={video_id}",
                                    "title": data.get("title", "Unknown"),
                                    "channel": data.get("channel", data.get("uploader", "Unknown")),
                                }
                            )
                    except json.JSONDecodeError:
                        continue
                return videos
            except FileNotFoundError:
                logger.error("yt-dlp not found — install with: pip install yt-dlp")
                return []
            except subprocess.TimeoutExpired:
                logger.error("yt-dlp playlist extraction timed out (%ss)", self.timeout)
                return []
            except (OSError, RuntimeError) as e:
                logger.error("yt-dlp playlist extraction error: %s", e)
                return []

        return await anyio.to_thread.run_sync(_run_ytdlp)

    async def get_playlist_title(self, playlist_url: str) -> str:
        """Get the title of a playlist."""

        def _run_ytdlp() -> str:
            try:
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "--flat-playlist",
                        "--dump-single-json",
                        "--no-warnings",
                        playlist_url,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return data.get("title", "Unknown Playlist")
            except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
                pass
            return "Unknown Playlist"

        return await anyio.to_thread.run_sync(_run_ytdlp)


# ── Topic Searcher ───────────────────────────────────────────────────────────


class TopicSearcher:
    """Searches YouTube for videos on a given topic via SearXNG."""

    def __init__(self, searxng_url: str = "http://localhost:8017"):
        self.searxng_url = searxng_url.rstrip("/")

    async def search(self, topic: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Search YouTube for videos matching a topic via SearXNG.

        Returns list of dicts with keys: url, title, channel, snippet
        Falls back gracefully if SearXNG is unreachable.
        """
        import httpx2 as httpx

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.searxng_url}/search",
                    params={
                        "q": topic,
                        "categories": "videos",
                        "engines": "youtube",
                        "format": "json",
                    },
                )
                if resp.status_code != 200:
                    logger.warning("SearXNG search failed: HTTP %s", resp.status_code)
                    return []

                data = resp.json()
                results = []
                for item in data.get("results", [])[:max_results]:
                    url = item.get("url", "")
                    if not is_youtube_url(url):
                        continue
                    video_id = extract_video_id(url)
                    if not video_id:
                        continue
                    results.append(
                        {
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "title": item.get("title", "Unknown"),
                            "channel": item.get("engine", "Unknown"),
                            "snippet": item.get("content", "")[:300],
                        }
                    )
                return results

        except (OmegaError, httpx.HTTPError, RuntimeError) as e:
            logger.warning("Topic search via SearXNG failed: %s", e)
            return []


# ── Transcript Fetcher ───────────────────────────────────────────────────────


class TranscriptFetcher:
    """Fetches YouTube transcripts via youtube-transcript-api.

    Implements rate limiting and graceful fallback for unavailable transcripts.
    """

    def __init__(self, request_delay: float = 2.0):
        self._request_delay = request_delay
        self._last_request = 0.0

    async def fetch(self, video_id: str) -> Optional[str]:
        """Fetch transcript text for a video ID.

        Respects rate limiting by enforcing a minimum delay between requests.
        Returns None if the transcript is unavailable.
        """
        # Rate limiting
        now = time.monotonic()
        since_last = now - self._last_request
        if since_last < self._request_delay:
            await anyio.sleep(self._request_delay - since_last)
        self._last_request = time.monotonic()

        def _fetch() -> Optional[str]:
            try:
                from youtube_transcript_api import (
                    TranscriptsDisabled,
                    NoTranscriptFound,
                    VideoUnavailable,
                    YouTubeTranscriptApi,
                )

                ytt_api = YouTubeTranscriptApi()
                transcript = ytt_api.fetch(video_id)
                if transcript and transcript.snippets:
                    return " ".join(s.text.strip() for s in transcript.snippets if s.text.strip())
                return None
            except (TranscriptsDisabled, NoTranscriptFound):
                logger.warning("No transcript available for video %s", video_id)
                return None
            except VideoUnavailable:
                logger.warning("Video %s is unavailable", video_id)
                return None
            except Exception as e:
                logger.warning("Transcript fetch failed for %s: %s", video_id, e)
                return None

        return await anyio.to_thread.run_sync(_fetch)


# ── Video Ingester ───────────────────────────────────────────────────────────


class VideoIngester:
    """Ingests a single YouTube video via youtube-transcript-api + YouTubeResearchModule.

    Pipeline:
      1. Extract video ID from URL
      2. Fetch transcript (youtube-transcript-api)
      3. Sieve → Sign → Chain → Persist (YouTubeResearchModule)
    """

    def __init__(self, config: Optional[Dict] = None):
        self._module: Optional[Any] = None
        self.config = config or {}
        self._fetcher = TranscriptFetcher(request_delay=self.config.get("request_delay", 2.0))

    async def _get_module(self):
        """Lazy-load the YouTubeResearchModule with proper init."""
        if self._module is None:
            from omega_youtube_research import YouTubeResearchModule

            self._module = YouTubeResearchModule()
            await self._module.init()
        return self._module

    async def close(self):
        """Clean up the YouTubeResearchModule persistence."""
        if self._module is not None:
            await self._module.close()
            self._module = None

    async def ingest(self, job: IngestJob) -> Optional[Dict[str, Any]]:
        """Ingest a single video: fetch transcript + run Sieve-and-Sign.

        Returns dict with ingestion metadata, or None on failure.
        """
        # 1. Extract video ID
        video_id = extract_video_id(job.url)
        if not video_id:
            logger.error("Could not extract video ID from URL: %s", job.url)
            return None

        # 2. Fetch transcript
        raw_transcript = await self._fetcher.fetch(video_id)
        if not raw_transcript:
            return None

        # 3. Run Sieve-and-Sign pipeline
        try:
            module = await self._get_module()
            result = await module.ingest_transcript(
                video_id=video_id,
                raw_transcript=raw_transcript,
                source_url=job.url,
            )
            return {
                "job_id": job.job_id,
                "video_id": video_id,
                "source_id": result.source_id,
                "chunk_count": result.chunk_count,
                "provenance_hash": result.provenance_hash,
            }
        except Exception as e:
            logger.error("Sieve-and-Sign pipeline failed for %s: %s", job.url, e)
            return None


# ── Cross-Video Synthesizer ─────────────────────────────────────────────────


class CrossVideoSynthesizer:
    """Synthesizes knowledge across multiple ingested videos on the same topic.

    Uses local model inference (ResourceGuard-protected) with graceful
    fallback to title-based synthesis if the model is unavailable.
    """

    def __init__(self, model_gateway=None, resource_guard: Optional[ResourceGuard] = None):
        self.model_gateway = model_gateway
        self.resource_guard = resource_guard

    async def synthesize(
        self,
        topic: str,
        video_results: List[Dict[str, Any]],
        model_name: str = "qwen3-1.7b",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Optional[SynthesisResult]:
        """Produce a research-grade synthesis across ingested videos.

        Uses local model inference (if available) to distill patterns,
        insights, and contradictions. Falls back to title-based synthesis.
        """
        if not video_results:
            return None

        # Build the synthesis prompt from ingested video metadata
        video_summaries = []
        for vr in video_results:
            title = vr.get("title", vr.get("source_id", "Unknown"))
            url = vr.get("url", "")
            chunk_count = vr.get("chunk_count", 0)
            video_summaries.append(f"- {title} ({url}) — {chunk_count} chunks")

        prompt = (
            f"You are a sovereign research synthesizer. Analyze the following YouTube videos "
            f'ingested on the topic: "{topic}"\n\n'
            f"Videos ingested ({len(video_results)}):\n"
            + "\n".join(video_summaries)
            + """

Based on the video metadata, produce a structured synthesis:

1. KEY INSIGHTS (3-5): The most important takeaways
2. PATTERNS (2-3): Recurring themes or consistent messages
3. CONTRADICTIONS (0-2): Any conflicting perspectives
4. RECOMMENDATIONS (2-3): What to investigate further

Format your response as JSON with these exact keys:
{
  "key_insights": ["insight 1", "insight 2", ...],
  "patterns": ["pattern 1", ...],
  "contradictions": ["contradiction 1", ...],
  "recommendations": ["recommendation 1", ...]
}

Be precise, cite video titles where relevant, and prioritize signal over noise."""
        )

        # Try local model inference with ResourceGuard protection
        try:
            if self.model_gateway and self.resource_guard:
                async with self.resource_guard:
                    result = await self.model_gateway.generate(
                        model_name=model_name,
                        system_prompt="You are a research synthesizer. Return ONLY valid JSON.",
                        user_query=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                parsed = self._parse_synthesis(topic, result.text, video_results)
                if parsed:
                    return parsed
        except (OmegaError, ProviderError, ProviderTimeoutError, ProviderUnavailableError) as e:
            logger.warning("Model inference failed for synthesis: %s", e)

        # Fallback: title-based synthesis
        return self._basic_synthesis(topic, video_results)

    @staticmethod
    def _parse_synthesis(
        topic: str,
        response_text: str,
        video_results: List[Dict[str, Any]],
    ) -> Optional[SynthesisResult]:
        """Parse LLM response into a SynthesisResult."""
        try:
            content = response_text.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(content)
            return SynthesisResult(
                topic=topic,
                video_count=len(video_results),
                key_insights=data.get("key_insights", []),
                patterns=data.get("patterns", []),
                contradictions=data.get("contradictions", []),
                recommendations=data.get("recommendations", []),
                source_urls=[vr.get("url", "") for vr in video_results],
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning("Failed to parse synthesis response: %s", e)
            return None

    @staticmethod
    def _basic_synthesis(
        topic: str,
        video_results: List[Dict[str, Any]],
    ) -> SynthesisResult:
        """Generate a basic synthesis without LLM (title-based metadata)."""
        titles = [vr.get("title", vr.get("source_id", "Unknown")) for vr in video_results]
        channels = list(
            set(vr.get("channel", "Unknown") for vr in video_results if vr.get("channel"))
        )

        return SynthesisResult(
            topic=topic,
            video_count=len(video_results),
            key_insights=[
                f"Analyzed {len(video_results)} videos on '{topic}'",
            ]
            + ([f"Source channels: {', '.join(channels[:5])}"] if channels else []),
            patterns=[
                f"Videos span {max(len(channels), 1)} unique channel(s)",
            ],
            contradictions=[],
            recommendations=[
                "Review the ingested transcripts for detailed analysis",
            ],
            source_urls=[vr.get("url", "") for vr in video_results],
        )


# ── Hivemind Logger ──────────────────────────────────────────────────────────


class HivemindLogger:
    """Atomic JSONL logger for HALL_OF_RECORDS ingestion and synthesis events."""

    def __init__(self, base_dir: Path):
        self.records_dir = base_dir / "data" / "knowledge" / "HALL_OF_RECORDS" / "youtube-worker"
        self.records_dir.mkdir(parents=True, exist_ok=True)

    async def log_ingestion(self, cycle_id: str, job: IngestJob, result: Dict):
        """Append an ingestion event to the daily JSONL log."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        log_path = self.records_dir / f"ingest_{today}.jsonl"

        entry = {
            "cycle_id": cycle_id,
            "job_id": job.job_id,
            "url": job.url,
            "source": job.source,
            "topic": job.topic,
            "chunk_count": result.get("chunk_count", 0),
            "provenance_hash": result.get("provenance_hash", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._append_jsonl(log_path, entry)

    async def log_synthesis(self, result: SynthesisResult):
        """Append a synthesis event to the daily JSONL log."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        log_path = self.records_dir / f"synthesis_{today}.jsonl"

        entry = {
            "type": "synthesis",
            "topic": result.topic,
            "video_count": result.video_count,
            "key_insights": result.key_insights,
            "patterns": result.patterns,
            "contradictions": result.contradictions,
            "recommendations": result.recommendations,
            "source_urls": result.source_urls,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._append_jsonl(log_path, entry)

    @staticmethod
    async def _append_jsonl(path: Path, entry: Dict):
        """Atomic append to a JSONL file (tmp + replace)."""

        def _append():
            existing = b""
            if path.exists():
                existing = path.read_bytes()
            tmp = path.with_suffix(".tmp.jsonl")
            tmp.write_bytes(existing + (json.dumps(entry) + "\n").encode())
            tmp.replace(path)

        await anyio.to_thread.run_sync(_append)


# ── Main Worker ──────────────────────────────────────────────────────────────


class YouTubeWorker:
    """Autonomous YouTube ingestion and synthesis daemon.

    State machine:
      IDLE → [DEQUEUE → FETCH → INGEST → SAVE] × N → [SYNTHESIZE if threshold reached] → IDLE

    WorkerCoordinator integration: pause/resume lifecycle via COORDINATOR.
    ResourceGuard integration: 2048 MB OOM protection for model inference.
    Somatic Save-Points: crash recovery via JSON state file.
    """

    def __init__(
        self,
        config: Optional[Dict] = None,
        model_gateway=None,
    ):
        self.config = config or {}
        self.model_gateway = model_gateway

        # Core components
        playlist_timeout = self.config.get("playlist", {}).get("timeout", 120)
        self.playlist_expander = PlaylistExpander(timeout=playlist_timeout)

        searxng_url = self.config.get("searxng", {}).get("url", "http://localhost:8017")
        self.topic_searcher = TopicSearcher(searxng_url=searxng_url)

        self.ingester = VideoIngester(config=self.config.get("ingestion", {}))

        # ResourceGuard: 2048 MB for model inference (OOM protection)
        self.resource_guard = ResourceGuard(max_ram_mb=2048)
        self.synthesizer = CrossVideoSynthesizer(
            model_gateway=model_gateway,
            resource_guard=self.resource_guard,
        )

        # [redis-20260928] Redis queue REMOVED (Architect ruling, group B).
        # The queue keys ("queue", "queue_name", "redis") in the YAML config
        # are now ignored. Queue-backed methods raise QueueBackendRemoved
        # rather than silently doing nothing — see _require_queue().
        self.queue_name = self.config.get("queue_name", "youtube_queue")

        # Synthesis config
        synth_cfg = self.config.get("synthesis", {})
        self._synth_enabled = synth_cfg.get("enabled", True)
        self._synth_threshold = synth_cfg.get("auto_synthesize_threshold", 5)
        self._synth_model = synth_cfg.get("model", "qwen3-1.7b")
        self._synth_temperature = synth_cfg.get("temperature", 0.3)
        self._synth_max_tokens = synth_cfg.get("max_tokens", 2048)

        # Topic tracking for auto-synthesis: topic → list of ingested video metadata
        self._topic_buckets: Dict[str, List[Dict]] = defaultdict(list)

        # WorkerCoordinator integration
        self.coordinator = COORDINATOR

        # State
        self._shutdown = threading.Event()
        self._running = False
        self._cycle_count = 0
        self.lock_path = Path(tempfile.gettempdir()) / "omega" / "youtube_worker.lock"
        self.savepoint_path = Path("data/workers/youtube_worker_state.json")
        self.savepoint_path.parent.mkdir(parents=True, exist_ok=True)

        # Hivemind logger
        self._hivemind = HivemindLogger(
            base_dir=Path(__file__).resolve().parent.parent.parent.parent
        )

        # Metrics
        self.metrics = {
            "total_ingested": 0,
            "total_synthesized": 0,
            "total_errors": 0,
            "playlists_expanded": 0,
            "topics_searched": 0,
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        await self.close()

    async def close(self):
        """Graceful shutdown: release the YouTube module resources."""
        # [redis-20260928] no queue connection to close — backend excised.
        await self.ingester.close()
        logger.info("YouTube worker resources released")

    # ── Queue backend ────────────────────────────────────────────────────

    def _require_queue(self):
        """[redis-20260928] The YouTube queue backend was Redis; it is gone.

        The class, its config surface and its contract tests are retained —
        only the transport was excised. Every queue-backed method
        (submit_url, submit_playlist, submit_topic, submit_file, run_cycle,
        run_batch_cycle, get_status) now raises here.

        M23: raises rather than returning empty. A queue that silently
        accepts nothing is indistinguishable from a queue that is idle, and
        that ambiguity is the same defect class as the handoff reaper.
        The non-queue surface (fetching, synthesis, extractors) is
        unaffected and still works.
        """
        raise ProviderUnavailableError(
            provider="youtube_queue",
            message=(
                "YouTube queue backend removed with Redis "
                "(D-redis-20260928). Queue-backed operations are unavailable. "
                "The fetch/synthesis surface is unaffected. Re-implement the "
                "queue on omega_handoff / the local worker pool to restore it."
            ),
        )

    # ── Somatic Save-Points ──────────────────────────────────────────────

    async def _save_state(self, cycle_id: str, state: str):
        savepoint = {
            "cycle_id": cycle_id,
            "state": state,
            "timestamp": time.time(),
            "cycle_count": self._cycle_count,
            "metrics": self.metrics,
        }
        try:
            async with await anyio.open_file(self.savepoint_path, "w") as f:
                await f.write(json.dumps(savepoint))
        except (OSError, RuntimeError) as e:
            logger.warning("Failed to save state: %s", e)

    async def _load_state(self) -> Optional[Dict]:
        if not await anyio.Path(self.savepoint_path).exists():
            return None
        try:
            async with await anyio.open_file(self.savepoint_path, "r") as f:
                return json.loads(await f.read())
        except (OSError, RuntimeError, json.JSONDecodeError):
            return None

    # ── Queue Operations ─────────────────────────────────────────────────

    async def submit_url(self, url: str, source: str = "queue", topic: Optional[str] = None) -> str:
        """Submit a URL to the Redis queue."""
        self._require_queue()  # [redis-20260928] raises — body below is unreachable reference impl
        job = IngestJob(
            job_id=f"yt_{uuid.uuid4().hex[:12]}",
            url=url,
            source=source,
            topic=topic,
        )
        await r.lpush(self.queue_name, json.dumps(asdict(job)))
        logger.info("Submitted to queue: %s (%s)", job.job_id, url)
        return job.job_id

    async def submit_playlist(self, playlist_url: str, topic: Optional[str] = None) -> int:
        """Expand a playlist and submit all videos to the queue."""
        videos = await self.playlist_expander.expand_playlist(playlist_url)
        if not videos:
            logger.warning("No videos found in playlist: %s", playlist_url)
            return 0

        playlist_title = await self.playlist_expander.get_playlist_title(playlist_url)
        playlist_id = extract_playlist_id(playlist_url)

        self._require_queue()  # [redis-20260928] raises — body below is unreachable reference impl
        count = 0
        for video in videos:
            job = IngestJob(
                job_id=f"yt_{uuid.uuid4().hex[:12]}",
                url=video["url"],
                source="playlist",
                topic=topic or playlist_title,
                playlist_id=playlist_id,
                playlist_title=playlist_title,
            )
            await r.lpush(self.queue_name, json.dumps(asdict(job)))
            count += 1

        self.metrics["playlists_expanded"] += 1
        logger.info("Expanded playlist '%s': %d videos queued", playlist_title, count)
        return count

    async def submit_topic(self, topic: str, max_results: int = 10) -> int:
        """Search YouTube for a topic and submit results to the queue."""
        results = await self.topic_searcher.search(topic, max_results=max_results)
        if not results:
            logger.warning("No YouTube results found for topic: %s", topic)
            return 0

        self._require_queue()  # [redis-20260928] raises — body below is unreachable reference impl
        count = 0
        for video in results:
            job = IngestJob(
                job_id=f"yt_{uuid.uuid4().hex[:12]}",
                url=video["url"],
                source="topic",
                topic=topic,
            )
            await r.lpush(self.queue_name, json.dumps(asdict(job)))
            count += 1

        self.metrics["topics_searched"] += 1
        logger.info("Topic search '%s': %d videos queued", topic, count)
        return count

    async def submit_file(self, file_path: str) -> int:
        """Submit all URLs from a file (one per line)."""
        path = Path(file_path)
        if not path.exists():
            logger.error("File not found: %s", file_path)
            return 0

        content = await anyio.to_thread.run_sync(path.read_text)
        urls = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and line.strip().startswith("http")
        ]

        self._require_queue()  # [redis-20260928] raises — body below is unreachable reference impl
        count = 0
        for url in urls:
            job = IngestJob(
                job_id=f"yt_{uuid.uuid4().hex[:12]}",
                url=url,
                source="file",
            )
            await r.lpush(self.queue_name, json.dumps(asdict(job)))
            count += 1

        logger.info("File '%s': %d URLs queued", file_path, count)
        return count

    # ── Core Cycle ───────────────────────────────────────────────────────

    async def run_cycle(self) -> dict:
        """Execute one complete ingestion cycle with WorkerCoordinator.

        Flow:
          1. Register with WorkerCoordinator (idempotent)
          2. Acquire atomic lock (with stale recovery)
          3. Wrap in WorkerCoordinator pause/resume lifecycle
          4. Dequeue → Fetch transcript → Ingest (Sieve-and-Sign) → Log
          5. Auto-synthesize if topic threshold reached
          6. Release lock
        """
        cycle_id = (
            f"yt_cycle_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{self._cycle_count}"
        )
        self._cycle_count += 1

        # 0. Register with WorkerCoordinator (idempotent)
        await self.coordinator.register("youtube_worker")

        # 1. Atomic lock with stale recovery
        if self.lock_path.exists():
            try:
                lock_age = time.time() - self.lock_path.stat().st_mtime
                if lock_age > 900:  # 15 min
                    logger.warning("Stale lock (%ds) — reclaiming", lock_age)
                    self.lock_path.rmdir()
                else:
                    return {"cycle_id": cycle_id, "skipped": True, "reason": "locked"}
            except OSError:
                return {"cycle_id": cycle_id, "skipped": True, "reason": "locked"}
        try:
            self.lock_path.mkdir(parents=True)
        except FileExistsError:
            return {"cycle_id": cycle_id, "skipped": True, "reason": "locked"}

        self._running = True

        try:
            # 2. WorkerCoordinator pause/resume lifecycle
            async with self.coordinator.run("youtube_worker"):
                await self.coordinator.wait_if_paused()
                await self._save_state(cycle_id, "dequeue")

                # 3. Dequeue next job
                self._require_queue()  # [redis-20260928] raises — body below is unreachable reference impl
                result = await r.blpop(self.queue_name, timeout=10)
                if not result:
                    return {"cycle_id": cycle_id, "skipped": True, "reason": "empty_queue"}

                _, job_data = result
                job = IngestJob(**json.loads(job_data))

                # 4. Ingest the video
                await self._save_state(cycle_id, f"ingest:{job.job_id}")
                ingest_result = await self.ingester.ingest(job)

                if not ingest_result:
                    self.metrics["total_errors"] += 1
                    if job.retry_count < 3:
                        job.retry_count += 1
                        await r.lpush(self.queue_name, json.dumps(asdict(job)))
                        logger.warning(
                            "Ingestion failed for %s, re-queued (retry %d)",
                            job.url,
                            job.retry_count,
                        )
                    return {
                        "cycle_id": cycle_id,
                        "job_id": job.job_id,
                        "url": job.url,
                        "action": "retry" if job.retry_count < 3 else "failed",
                    }

                self.metrics["total_ingested"] += 1
                await self._save_state(cycle_id, f"ingested:{job.job_id}")

                # 5. Track topic for auto-synthesis
                topic = job.topic or "general"
                self._topic_buckets[topic].append(
                    {
                        "url": job.url,
                        "source_id": ingest_result.get("source_id", ""),
                        "title": job.url,  # Will be enriched by yt-dlp in future
                        "chunk_count": ingest_result.get("chunk_count", 0),
                    }
                )

                # 6. Log to Hivemind
                await self._hivemind.log_ingestion(cycle_id, job, ingest_result)

                # 7. Auto-synthesize if threshold reached
                if self._synth_enabled:
                    bucket = self._topic_buckets[topic]
                    if len(bucket) >= self._synth_threshold:
                        logger.info(
                            "Threshold reached for topic '%s' (%d videos) — synthesizing",
                            topic,
                            len(bucket),
                        )
                        synth_result = await self.synthesizer.synthesize(
                            topic=topic,
                            video_results=list(bucket),
                            model_name=self._synth_model,
                            temperature=self._synth_temperature,
                            max_tokens=self._synth_max_tokens,
                        )
                        if synth_result:
                            self.metrics["total_synthesized"] += 1
                            await self._hivemind.log_synthesis(synth_result)
                            # Clear bucket to avoid re-synthesis
                            self._topic_buckets[topic] = []
                            logger.info(
                                "Synthesis complete for topic '%s': %d insights",
                                topic,
                                len(synth_result.key_insights),
                            )

                return {
                    "cycle_id": cycle_id,
                    "job_id": job.job_id,
                    "url": job.url,
                    "source": job.source,
                    "topic": job.topic,
                    "chunk_count": ingest_result.get("chunk_count", 0),
                    "action": "ingested",
                    "synthesized": self.metrics["total_synthesized"],
                    "metrics": self.metrics.copy(),
                }

        except Exception as e:
            logger.error("YouTube worker cycle failed: %s", e, exc_info=True)
            return {"cycle_id": cycle_id, "error": str(e)}
        finally:
            self._running = False
            try:
                self.lock_path.rmdir()
            except OSError:
                pass

    # ── Batch Ingestion ──────────────────────────────────────────────────

    async def run_batch_cycle(self, max_jobs: Optional[int] = None) -> dict:
        """Process multiple jobs in a single cycle (for efficiency)."""
        if max_jobs is None:
            max_jobs = self.config.get("worker", {}).get("max_batch_size", 10)

        await self.coordinator.register("youtube_worker")

        results = []
        for _ in range(max_jobs):
            self._require_queue()  # [redis-20260928] raises — body below is unreachable reference impl
            result = await r.blpop(self.queue_name, timeout=5)
            if not result:
                break

            _, job_data = result
            job = IngestJob(**json.loads(job_data))

            ingest_result = await self.ingester.ingest(job)
            if ingest_result:
                self.metrics["total_ingested"] += 1
                results.append(
                    {
                        "job_id": job.job_id,
                        "source_id": ingest_result.get("source_id", ""),
                        "status": "ok",
                    }
                )
            else:
                self.metrics["total_errors"] += 1
                results.append(
                    {
                        "job_id": job.job_id,
                        "status": "error",
                    }
                )

        return {
            "batch_size": len(results),
            "results": results,
            "metrics": self.metrics.copy(),
        }

    # ── Synthesis Cycle ──────────────────────────────────────────────────

    async def synthesize_topic(self, topic: str) -> Optional[SynthesisResult]:
        """Run cross-video synthesis for a topic from the accumulated bucket."""
        bucket = self._topic_buckets.get(topic, [])
        if not bucket:
            logger.warning("No videos accumulated for topic '%s'", topic)
            return None

        result = await self.synthesizer.synthesize(
            topic=topic,
            video_results=list(bucket),
            model_name=self._synth_model,
            temperature=self._synth_temperature,
            max_tokens=self._synth_max_tokens,
        )
        if result:
            self.metrics["total_synthesized"] += 1
            await self._hivemind.log_synthesis(result)
            self._topic_buckets[topic] = []
        return result

    # ── Status & Health ──────────────────────────────────────────────────

    async def get_status(self) -> Dict:
        """Return current worker status."""
        self._require_queue()  # [redis-20260928] raises — body below is unreachable reference impl
        queue_len = await r.llen(self.queue_name)
        topic_counts = {topic: len(videos) for topic, videos in self._topic_buckets.items()}
        return {
            "running": self._running,
            "cycle_count": self._cycle_count,
            "queue_depth": queue_len,
            "topic_buckets": topic_counts,
            "synth_threshold": self._synth_threshold,
            "metrics": self.metrics.copy(),
        }


# ── Daemon Loop ──────────────────────────────────────────────────────────────

_SHUTDOWN = threading.Event()


def _handle_signal(signum, _frame):
    logger.info("Received signal %s — initiating clean shutdown", signum)
    _SHUTDOWN.set()


def _cpu_percent() -> float:
    try:
        import psutil  # noqa: F401 — psutil is an Omega dependency

        return float(psutil.cpu_percent(interval=0.1))
    except Exception as e:
        logger.debug("cpu_percent unavailable, falling back to 0.0: %s", e)
        return 0.0


def _load_config(path: Optional[Path] = None) -> Dict:
    """Load YAML config file, returning empty dict if unavailable."""
    if path is None:
        path = Path("config/youtube_worker.yaml")
    if not path.exists():
        logger.info("No config file at %s — using defaults", path)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        logger.info("Loaded config from %s", path)
        return dict(data)
    except (yaml.YAMLError, OSError) as e:
        logger.warning("Failed to load config from %s: %s", path, e)
        return {}


async def run_daemon(
    worker: YouTubeWorker,
    max_cycles: int = 0,
    cpu_ceiling: float = 85.0,
    cycle_interval: float = 5.0,
) -> int:
    """Run the YouTube worker continuously with watchdog and CPU ceiling.

    **Watchdog (crash-loop breaker):** each cycle is wrapped in try/except.
    After MAX_CONSECUTIVE_FAILURES crashes in a row the daemon aborts (return 1)
    so systemd Restart=on-failure can revive the process.

    **CPU ceiling:** if system CPU exceeds cpu_ceiling the daemon throttles.

    **Kill switch:** SIGTERM/SIGINT sets _SHUTDOWN for clean exit between cycles.
    """
    MAX_CONSECUTIVE_FAILURES = 5
    consecutive_failures = 0
    cycles = 0

    logger.info(
        "YouTube worker daemon started (cpu_ceiling=%.0f%%, interval=%.0fs, max_cycles=%d)",
        cpu_ceiling,
        cycle_interval,
        max_cycles,
    )

    while not _SHUTDOWN.is_set():
        # CPU ceiling — throttle instead of hammering
        if cpu_ceiling > 0:
            cpu = _cpu_percent()
            if cpu > cpu_ceiling:
                logger.warning("CPU %.0f%% exceeds ceiling — throttling 15s", cpu)
                await anyio.sleep(15)
                continue

        try:
            result = await worker.run_cycle()
            consecutive_failures = 0
            cycles += 1
            action = result.get("action") or result.get("reason") or "done"
            logger.info("Cycle %d: %s", cycles, action)
        except Exception as e:
            consecutive_failures += 1
            logger.error(
                "Cycle %d crashed (%d/%d): %s",
                cycles + 1,
                consecutive_failures,
                MAX_CONSECUTIVE_FAILURES,
                e,
                exc_info=True,
            )
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                logger.error("Crash-loop detected — aborting YouTube worker")
                return 1
            backoff = min(2**consecutive_failures, 60)
            logger.info("Watchdog backoff: %.0fs", backoff)
            await anyio.sleep(backoff)

        if max_cycles and cycles >= max_cycles:
            logger.info("Reached max-cycles %d — exiting", max_cycles)
            break

        await anyio.sleep(cycle_interval)

    logger.info("YouTube worker stopped after %d cycles", cycles)
    return 0


# ── CLI Entry Point ──────────────────────────────────────────────────────────


async def main():
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    parser = argparse.ArgumentParser(description="Omega YouTube Background Worker")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--batch", action="store_true", help="Run batch cycle")
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    parser.add_argument("--queue-url", type=str, help="Submit a URL to the queue")
    parser.add_argument("--playlist", type=str, help="Expand and ingest a playlist")
    parser.add_argument("--topic", type=str, help="Search and ingest by topic")
    parser.add_argument("--file", type=str, help="Submit URLs from a file")
    parser.add_argument("--max-cycles", type=int, default=0, help="Max cycles (0=unlimited)")
    parser.add_argument(
        "--cpu-ceiling", type=float, default=85.0, help="CPU throttle threshold (%%), daemon only"
    )
    parser.add_argument(
        "--interval", type=float, default=5.0, help="Seconds between cycles, daemon only"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config (default: config/youtube_worker.yaml)",
    )
    parser.add_argument("--batch-size", type=int, default=10, help="Max jobs for --batch")
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config) if args.config else None
    config = _load_config(config_path)

    async with YouTubeWorker(config=config) as worker:
        if args.status:
            status = await worker.get_status()
            print(json.dumps(status, indent=2))
            return

        if args.queue_url:
            job_id = await worker.submit_url(args.queue_url)
            print(f"Queued: {job_id}")
            return

        if args.playlist:
            count = await worker.submit_playlist(args.playlist)
            print(f"Playlist expanded: {count} videos queued")
            if not args.daemon:
                return

        if args.topic:
            count = await worker.submit_topic(args.topic)
            print(f"Topic search: {count} videos queued")
            if not args.daemon:
                return

        if args.file:
            count = await worker.submit_file(args.file)
            print(f"File: {count} URLs queued")
            if not args.daemon:
                return

        if args.daemon:
            code = await run_daemon(
                worker,
                max_cycles=args.max_cycles,
                cpu_ceiling=args.cpu_ceiling,
                cycle_interval=args.interval,
            )
            sys.exit(code)

        if args.batch:
            result = await worker.run_batch_cycle(max_jobs=args.batch_size)
            print(json.dumps(result, indent=2))
            return

        # Default: one-shot cycle
        result = await worker.run_cycle()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    anyio.run(main)
