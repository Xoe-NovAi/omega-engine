"""YouTubeSieve — T1→T2→T3 tiered YouTube extraction.

T1: yt-dlp --flat-playlist (metadata only, ~1s)
T2: youtube-transcript-api (auto-captions, ~2s)
T3: yt-dlp audio extract → Silero VAD → Whisper.cpp (sovereign, ~10-30s)
"""

# AP: AP-OMEGA-SIEVE-YOUTUBE-v1.0.0

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .errors import YouTubeError

logger = logging.getLogger("omega_sieve.youtube")


@dataclass
class YouTubeMetadata:
    """Metadata extracted from a YouTube video."""
    video_id: str
    title: str = ""
    channel: str = ""
    duration: int = 0  # seconds
    view_count: int = 0
    description: str = ""
    tags: list[str] = field(default_factory=list)
    upload_date: str = ""

    @property
    def is_short(self) -> bool:
        return self.duration < 60


@dataclass
class YouTubeResult:
    """Result of YouTube extraction."""
    video_id: str
    metadata: YouTubeMetadata
    transcript: str = ""
    tier: str = ""  # "metadata" | "captions" | "transcription"
    success: bool = False
    error: Optional[str] = None
    latency_ms: int = 0

    @property
    def has_content(self) -> bool:
        return bool(self.transcript.strip())


class YouTubeSieve:
    """Tiered YouTube video extraction.

    Usage:
        sieve = YouTubeSieve()
        result = await sieve.extract("https://youtube.com/watch?v=...")
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("/tmp/omega-sieve-youtube")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def extract(self, url: str, tier: str = "auto") -> YouTubeResult:
        """Extract YouTube video content with auto tier selection.

        Args:
            url: YouTube video URL.
            tier: "auto" (T1→T2→T3), "metadata" (T1), "captions" (T2), "transcription" (T3).

        Returns:
            YouTubeResult.
        """
        video_id = self._extract_video_id(url)
        if not video_id:
            return YouTubeResult(
                video_id="", metadata=YouTubeMetadata(video_id=""),
                success=False, error=f"Could not extract video ID from: {url}",
            )

        start = time.monotonic()

        if tier == "auto":
            # T1: Metadata
            meta = await self._get_metadata(video_id)
            latency = int((time.monotonic() - start) * 1000)
            result = YouTubeResult(
                video_id=video_id, metadata=meta,
                tier="metadata", success=True, latency_ms=latency,
            )

            # T2: Captions (always try)
            transcript, captions_ok = await self._get_captions(video_id)
            if captions_ok:
                result.transcript = transcript
                result.tier = "captions"

            # T3: Sovereign transcription (only if captions fail or quality < 0.5)
            if not captions_ok or len(transcript.split()) < 20:
                sov_transcript, sov_ok = await self._transcribe(video_id)
                if sov_ok:
                    result.transcript = sov_transcript
                    result.tier = "transcription"

            result.latency_ms = int((time.monotonic() - start) * 1000)
            return result

        elif tier == "metadata":
            meta = await self._get_metadata(video_id)
            latency = int((time.monotonic() - start) * 1000)
            return YouTubeResult(
                video_id=video_id, metadata=meta, tier="metadata",
                success=True, latency_ms=latency,
            )

        elif tier == "captions":
            meta = await self._get_metadata(video_id)
            transcript, ok = await self._get_captions(video_id)
            latency = int((time.monotonic() - start) * 1000)
            return YouTubeResult(
                video_id=video_id, metadata=meta, transcript=transcript,
                tier="captions", success=ok, latency_ms=latency,
                error=None if ok else "No captions available",
            )

        elif tier == "transcription":
            meta = await self._get_metadata(video_id)
            transcript, ok = await self._transcribe(video_id)
            latency = int((time.monotonic() - start) * 1000)
            return YouTubeResult(
                video_id=video_id, metadata=meta, transcript=transcript,
                tier="transcription", success=ok, latency_ms=latency,
                error=None if ok else "Transcription failed",
            )

        else:
            raise YouTubeError(f"Unknown tier: {tier}")

    async def _get_metadata(self, video_id: str) -> YouTubeMetadata:
        """T1: Get video metadata via yt-dlp."""
        import anyio

        try:
            result = await anyio.to_thread.run_sync(
                self._run_ytdlp,
                ["--dump-json", "--no-download", f"https://youtube.com/watch?v={video_id}"],
            )
            data = json.loads(result)
            return YouTubeMetadata(
                video_id=video_id,
                title=data.get("title", ""),
                channel=data.get("channel", ""),
                duration=data.get("duration", 0),
                view_count=data.get("view_count", 0),
                description=data.get("description", ""),
                tags=data.get("tags", []),
                upload_date=data.get("upload_date", ""),
            )
        except Exception as e:
            logger.warning(f"Failed to get metadata for {video_id}: {e}")
            return YouTubeMetadata(video_id=video_id)

    async def _get_captions(self, video_id: str) -> tuple[str, bool]:
        """T2: Fetch auto-generated captions."""
        import anyio

        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            transcript_list = await anyio.to_thread.run_sync(
                YouTubeTranscriptApi.get_transcript, video_id,
            )
            text = "\n".join(
                entry.get("text", "") for entry in transcript_list
            )
            return text, True
        except Exception as e:
            logger.debug(f"No captions for {video_id}: {e}")
            return "", False

    async def _transcribe(self, video_id: str) -> tuple[str, bool]:
        """T3: Sovereign transcription via VAD-gated Whisper.

        Download audio → VAD segmentation → Whisper on speech segments only.
        """
        import anyio

        audio_path = self.data_dir / f"{video_id}.mp3"

        try:
            # Download audio
            await anyio.to_thread.run_sync(
                self._run_ytdlp,
                ["-x", "--audio-format", "mp3", "-o", str(audio_path),
                 f"https://youtube.com/watch?v={video_id}"],
            )

            if not audio_path.exists():
                return "", False

            # VAD + Whisper
            text = await self._transcribe_audio(str(audio_path))

            # Cleanup
            audio_path.unlink(missing_ok=True)

            return text, bool(text.strip())

        except Exception as e:
            logger.warning(f"Transcription failed for {video_id}: {e}")
            if audio_path.exists():
                audio_path.unlink(missing_ok=True)
            return "", False

    async def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using VAD-gated Whisper.

        Note: Requires whisper-cpp-python and silero-vad.
        Falls back to a message if not installed.
        """
        try:
            import anyio

            # Check if VAD+Whisper is available
            try:
                import silero_vad  # noqa: F401
                import whisper_cpp_python  # noqa: F401
            except ImportError:
                return "[Transcription requires: pip install omega-sieve[transcription]]"

            # VAD segmentation (Silero)
            from silero_vad import load_silero_vad, get_speech_timestamps, read_audio

            vad_model = load_silero_vad()
            audio = await anyio.to_thread.run_sync(read_audio, audio_path)
            speech_segments = await anyio.to_thread.run_sync(
                get_speech_timestamps, audio, vad_model,
            )

            if not speech_segments:
                return "[No speech detected in audio]"

            # Whisper transcription of full audio
            from whisper_cpp_python import Whisper

            whisper = Whisper()
            result = await anyio.to_thread.run_sync(
                whisper.transcribe, audio_path,
            )
            return result.get("text", "")

        except Exception as e:
            logger.warning(f"Transcription failed: {e}")
            return f"[Transcription error: {e}]"

    def _run_ytdlp(self, args: list[str]) -> str:
        """Run yt-dlp and return stdout."""
        import subprocess
        cmd = ["yt-dlp"] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise YouTubeError(f"yt-dlp failed: {result.stderr[:200]}")
        return result.stdout

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        import re
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
            r'(?:^|(?:\s))([a-zA-Z0-9_-]{11})(?:\s|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None