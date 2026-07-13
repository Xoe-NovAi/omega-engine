"""M21 Gate Integrity: YouTube Worker Contract Tests.

[M21 Mandate] Every core API boundary returning a typed result MUST be
exercised by at least one test that validates the return type.

These tests verify the YouTube worker data models, URL helpers, and
public API return types against real isinstance() checks.
"""

import pytest
from typing import Dict, List, Optional
from pathlib import Path

from omega.workers.youtube_worker import (
    IngestJob,
    SynthesisResult,
    extract_video_id,
    extract_playlist_id,
    is_youtube_url,
    is_playlist_url,
    YouTubeWorker,
    PlaylistExpander,
    TopicSearcher,
    VideoIngester,
    CrossVideoSynthesizer,
    HivemindLogger,
)


# ── Test 1: Data Model Contracts ───────────────────────────────────────────

class TestIngestJobContract:
    """M21: IngestJob dataclass contract."""

    def test_ingest_job_creation(self):
        """IngestJob can be created with required fields."""
        job = IngestJob(
            job_id="yt_abc123",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            source="queue",
        )
        assert isinstance(job.job_id, str)
        assert isinstance(job.url, str)
        assert isinstance(job.source, str)
        assert job.topic is None
        assert isinstance(job.retry_count, int)

    def test_ingest_job_with_topic(self):
        """IngestJob accepts optional topic field."""
        job = IngestJob(
            job_id="yt_def456",
            url="https://youtu.be/abc123",
            source="topic",
            topic="sovereign AI",
            priority=1,
        )
        assert job.topic == "sovereign AI"
        assert job.priority == 1

    def test_ingest_job_retry_count_increment(self):
        """IngestJob retry_count can be incremented."""
        job = IngestJob(
            job_id="yt_ghi789",
            url="https://www.youtube.com/watch?v=test123",
            source="queue",
        )
        assert job.retry_count == 0
        job.retry_count += 1
        assert job.retry_count == 1


class TestSynthesisResultContract:
    """M21: SynthesisResult dataclass contract."""

    def test_synthesis_result_creation(self):
        """SynthesisResult can be created with all fields."""
        result = SynthesisResult(
            topic="sovereign AI",
            video_count=5,
            key_insights=["AI models are getting smaller", "Local inference is viable"],
            patterns=["Trend toward on-device AI"],
            contradictions=[],
            recommendations=["Try running Gemma 4 locally"],
            source_urls=["https://youtube.com/watch?v=abc"],
        )
        assert isinstance(result.topic, str)
        assert isinstance(result.video_count, int)
        assert isinstance(result.key_insights, list)
        assert isinstance(result.patterns, list)
        assert isinstance(result.contradictions, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.source_urls, list)
        assert result.video_count == 5
        assert len(result.key_insights) == 2


# ── Test 2: URL Helper Contracts ──────────────────────────────────────────

class TestYouTubeUrlHelpers:
    """M21: URL extraction and detection helpers."""

    def test_extract_video_id_returns_string(self):
        """extract_video_id returns a string for valid URLs."""
        vid = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert isinstance(vid, str)
        assert len(vid) == 11

    def test_extract_video_id_short_url(self):
        """extract_video_id works with youtu.be short URLs."""
        vid = extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        assert vid == "dQw4w9WgXcQ"

    def test_extract_video_id_embed_url(self):
        """extract_video_id works with /embed/ URLs."""
        vid = extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert vid == "dQw4w9WgXcQ"

    def test_extract_video_id_none_for_invalid(self):
        """extract_video_id returns None for non-YouTube URLs."""
        result = extract_video_id("https://example.com")
        assert result is None

    def test_extract_video_id_none_for_empty(self):
        """extract_video_id returns None for empty string."""
        result = extract_video_id("")
        assert result is None

    def test_extract_playlist_id_returns_string(self):
        """extract_playlist_id returns a string for playlist URLs."""
        pid = extract_playlist_id(
            "https://www.youtube.com/playlist?list=PLzfP3sCXUnxFH6JIZqHTLfV40Ii8Heu3v"
        )
        assert isinstance(pid, str)
        assert pid.startswith("PL")

    def test_extract_playlist_id_from_watch_url(self):
        """extract_playlist_id extracts from watch URLs with list parameter."""
        pid = extract_playlist_id(
            "https://youtube.com/watch?v=abc123&list=PLtest123&si=xxx"
        )
        assert pid == "PLtest123"

    def test_extract_playlist_id_none(self):
        """extract_playlist_id returns None for non-playlist URLs."""
        result = extract_playlist_id("https://youtube.com/watch?v=abc")
        assert result is None

    def test_is_youtube_url(self):
        """is_youtube_url returns True for YouTube video URLs."""
        assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True
        assert is_youtube_url("https://example.com") is False

    def test_is_playlist_url(self):
        """is_playlist_url returns True for playlist URLs."""
        assert is_playlist_url(
            "https://www.youtube.com/playlist?list=PLxxx"
        ) is True
        assert is_playlist_url(
            "https://youtube.com/watch?v=abc&list=PLxxx"
        ) is True
        assert is_playlist_url("https://youtube.com/watch?v=abc") is False


# ── Test 3: Component Instantiation Contracts ────────────────────────────

class TestComponentInstantiation:
    """M21: All core components can be instantiated with correct types."""

    def test_playlist_expander_is_instantiated(self):
        """PlaylistExpander can be created."""
        expander = PlaylistExpander(timeout=30)
        assert isinstance(expander, PlaylistExpander)
        assert expander.timeout == 30

    def test_topic_searcher_is_instantiated(self):
        """TopicSearcher can be created."""
        searcher = TopicSearcher(searxng_url="http://localhost:8017")
        assert isinstance(searcher, TopicSearcher)

    def test_video_ingester_is_instantiated(self):
        """VideoIngester can be created with optional config."""
        ingester = VideoIngester(config={"request_delay": 1.0})
        assert isinstance(ingester, VideoIngester)

    def test_cross_video_synthesizer_is_instantiated(self):
        """CrossVideoSynthesizer can be created without model gateway."""
        synth = CrossVideoSynthesizer(model_gateway=None)
        assert isinstance(synth, CrossVideoSynthesizer)

    def test_hivemind_logger_is_instantiated(self):
        """HivemindLogger can be created."""
        logger = HivemindLogger(base_dir=Path("/tmp"))
        assert isinstance(logger, HivemindLogger)

    def test_youtube_worker_is_instantiated(self):
        """YouTubeWorker can be created with empty config."""
        worker = YouTubeWorker(config={})
        assert isinstance(worker, YouTubeWorker)
        assert worker.queue_name == "youtube_queue"


# ── Test 4: Synthesis Logic Contracts ─────────────────────────────────────

class TestSynthesisLogic:
    """M21: Synthesis input/output types are correct."""

    def test_synthesizer_basic_synthesis_returns_synthesisresult(self):
        """CrossVideoSynthesizer._basic_synthesis returns SynthesisResult."""
        synth = CrossVideoSynthesizer(model_gateway=None)
        result = synth._basic_synthesis(
            topic="test topic",
            video_results=[
                {"url": "https://youtube.com/watch?v=1", "title": "Video 1"},
                {"url": "https://youtube.com/watch?v=2", "title": "Video 2"},
            ],
        )
        assert isinstance(result, SynthesisResult)
        assert result.topic == "test topic"
        assert result.video_count == 2
        assert isinstance(result.key_insights, list)
        assert isinstance(result.source_urls, list)
        assert len(result.source_urls) == 2

    def test_synthesizer_empty_videos(self):
        """synthesize() returns None for empty video list."""
        synth = CrossVideoSynthesizer(model_gateway=None)
        result = synth._basic_synthesis(topic="test", video_results=[])
        assert isinstance(result, SynthesisResult)
        assert result.video_count == 0

    def test_synthesizer_parse_rejects_invalid_json(self):
        """_parse_synthesis returns None for non-JSON response."""
        synth = CrossVideoSynthesizer(model_gateway=None)
        result = synth._parse_synthesis(
            topic="test",
            response_text="not json at all",
            video_results=[],
        )
        assert result is None

    def test_synthesizer_parse_accepts_valid_json(self):
        """_parse_synthesis parses valid JSON response."""
        synth = CrossVideoSynthesizer(model_gateway=None)
        result = synth._parse_synthesis(
            topic="test",
            response_text=(
                '{"key_insights": ["i1"], "patterns": ["p1"], '
                '"contradictions": [], "recommendations": ["r1"]}'
            ),
            video_results=[{"url": "https://youtube.com/watch?v=abc"}],
        )
        assert isinstance(result, SynthesisResult)
        assert result.key_insights == ["i1"]
        assert result.patterns == ["p1"]
        assert len(result.source_urls) == 1


# ── Test 5: HivemindLogger Contracts ──────────────────────────────────────

class TestHivemindLogger:
    """M21: HivemindLogger JSONL writing contracts."""

    @pytest.mark.asyncio
    async def test_append_jsonl_no_existing(self, tmp_path):
        """_append_jsonl creates a new file and writes to it."""
        path = tmp_path / "test.jsonl"
        entry = {"cycle_id": "test", "action": "ingested", "count": 42}

        await HivemindLogger._append_jsonl(path, entry)

        assert path.exists()
        content = path.read_text()
        assert '"count": 42' in content

    @pytest.mark.asyncio
    async def test_append_jsonl_appends(self, tmp_path):
        """_append_jsonl appends to an existing file."""
        path = tmp_path / "test_append.jsonl"
        await HivemindLogger._append_jsonl(path, {"entry": 1})
        await HivemindLogger._append_jsonl(path, {"entry": 2})

        lines = path.read_text().strip().split("\n")
        assert len(lines) == 2
        assert '"entry": 1' in lines[0]
        assert '"entry": 2' in lines[1]

    @pytest.mark.asyncio
    async def test_hivemind_logger_creates_dir(self, tmp_path):
        """HivemindLogger creates the records directory."""
        base = tmp_path / "omega"
        logger = HivemindLogger(base_dir=base)
        assert logger.records_dir.exists()
