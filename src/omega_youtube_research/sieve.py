# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# SovereignSieve — YouTube Data API v3 search (firehose filtering) + transcript cleaning.
#
# Heritage:
#   [heritage: anyio 2024] Network + blocking I/O wrapped in anyio.to_thread.run_sync
#   [heritage: httpx2 2025] Sovereign HTTP client for the YouTube Data API v3

"""SovereignSieve — search filtering and transcript cleaning engine.

The Sieve performs two distinct jobs in the Sieve-and-Sign pipeline:

1. **Search (firehose filtering)** — query the YouTube Data API v3 ``search.list``
   endpoint and apply relevance / language / date filters to discard noise from the
   firehose of results.
2. **Clean** — strip YouTube-specific transcript noise (timestamps, speaker labels,
   control characters, URLs) while *preserving* cognitive hesitations (``um``, ``uh``,
   ``hmm``) that carry semantic signal.

Mandate 18 (Token Efficiency) sane-boundary: cleaning rules are ordered and
non-overlapping so each character is touched at most once. No slur lists are used —
all filtering is structural (regex / token-overlap), never lexical denylisting.
"""

import re
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from .config import SieveConfig
from .errors import SieveError, YouTubeAPIError, YouTubeAuthError

# ── Regex cleaning rules (ordered, non-overlapping) ──────────────────────────
# Timestamps: [00:00:00] or [00:00]
_RE_TIMESTAMP = re.compile(r"\[\d{2}:\d{2}(?::\d{2})?\]")
# Speaker labels at line start: "  Speaker Name:  "
_RE_SPEAKER = re.compile(r"^\s*[\w\s'’\-]+:\s*", re.MULTILINE)
# Control characters (C0 + DEL + C1)
_RE_CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")
# URLs
_RE_URL = re.compile(r"https?://\S+")
# Collapse 2+ whitespace runs to a single space
_RE_WS = re.compile(r"\s{2,}")
# Cognitive hesitations — preserved, never removed (counted for metadata)
_RE_HESITATION = re.compile(r"\b(um|uh|uhm|er|ah|eh|hmm)\b", re.IGNORECASE)


class YouTubeVideo(BaseModel):
    """A single filtered YouTube search result."""

    video_id: str
    title: str
    description: str
    channel_id: str = ""
    channel_title: str = ""
    published_at: str = ""
    url: str

    @classmethod
    def from_api_item(cls, item: Dict[str, Any]) -> "YouTubeVideo":
        """Build a ``YouTubeVideo`` from a YouTube Data API ``search.list`` item.

        Args:
            item: One entry from the API ``items`` array.

        Returns:
            A validated ``YouTubeVideo``.
        """
        vid = item.get("id", {})
        snippet = item.get("snippet", {})
        video_id = vid.get("videoId", "") if isinstance(vid, dict) else ""
        return cls(
            video_id=video_id,
            title=snippet.get("title", ""),
            description=snippet.get("description", ""),
            channel_id=snippet.get("channelId", ""),
            channel_title=snippet.get("channelTitle", ""),
            published_at=snippet.get("publishedAt", ""),
            url=f"https://www.youtube.com/watch?v={video_id}",
        )


class SieveMetadata(BaseModel):
    """Per-cleaning statistics produced by the Sieve."""

    original_length: int
    cleaned_length: int
    patterns_removed: Dict[str, int] = Field(default_factory=dict)
    hesitations_preserved: int = 0


class SieveResult(BaseModel):
    """Output of a transcript cleaning pass."""

    cleaned_text: str
    metadata: SieveMetadata


class SovereignSieve:
    """Search filtering + transcript cleaning engine.

    Args:
        config: ``SieveConfig`` controlling cleaning + relevance-gate behaviour.
    """

    SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search"

    def __init__(self, config: Optional[SieveConfig] = None):
        self._config = config or SieveConfig()

    # ── Cleaning (pure, CPU-bound) ───────────────────────────────────────────
    def clean_transcript(self, raw: str) -> SieveResult:
        """Clean a raw YouTube transcript.

        Removes timestamps, speaker labels, control characters, and URLs; collapses
        whitespace; and preserves cognitive hesitations (``um``/``uh``/``hmm``).

        Args:
            raw: The raw transcript text.

        Returns:
            A ``SieveResult`` containing the cleaned text and cleaning statistics.

        Raises:
            SieveError: If ``raw`` is not a string.
        """
        if not isinstance(raw, str):
            raise SieveError(f"clean_transcript expects str, got {type(raw).__name__}")

        cfg = self._config
        text = raw
        removed: Dict[str, int] = {}

        if cfg.remove_timestamps:
            text, n = _RE_TIMESTAMP.subn("", text)
            removed["timestamps"] = n

        # URLs FIRST: the speaker-label regex below would otherwise mis-match the
        # colon inside "https://" and strip the scheme prefix before we can rewrite
        # the URL to the [URL] placeholder.
        text, n_url = _RE_URL.subn(cfg.url_replacement, text)
        removed["urls"] = n_url

        text, n_ctrl = _RE_CONTROL.subn("", text)
        removed["control_chars"] = n_ctrl

        if cfg.remove_speaker_labels:
            text, n = _RE_SPEAKER.subn("", text)
            removed["speaker_labels"] = n

        # Preserve hesitations: count them, leave them in place.
        hesitations = len(_RE_HESITATION.findall(text)) if cfg.preserve_hesitations else 0

        # Whitespace normalisation last so collapsed runs don't re-introduce noise.
        text = _RE_WS.sub(" ", text).strip()

        return SieveResult(
            cleaned_text=text,
            metadata=SieveMetadata(
                original_length=len(raw),
                cleaned_length=len(text),
                patterns_removed=removed,
                hesitations_preserved=hesitations,
            ),
        )

    # ── Search (network, AnyIO) ──────────────────────────────────────────────
    async def search_videos(
        self,
        query: str,
        *,
        relevance_language: Optional[str] = None,
        published_after: Optional[datetime] = None,
        max_results: int = 10,
        api_key: Optional[str] = None,
        transport: Optional[Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None,
    ) -> List[YouTubeVideo]:
        """Search YouTube and apply firehose filters.

        Args:
            query: The search query.
            relevance_language: ISO 639-1 language code (e.g. ``"en"``) to restrict
                results via the API ``relevanceLanguage`` parameter.
            published_after: Only return videos published at/after this timestamp.
            max_results: Maximum number of results (1-50).
            api_key: YouTube Data API v3 key. Required unless ``transport`` is a stub.
            transport: Injectable async transport ``async (url, params) -> dict``.
                Defaults to a real ``httpx2`` GET. Injected in tests to avoid network.

        Returns:
            A list of ``YouTubeVideo`` that survived the relevance gate.

        Raises:
            YouTubeAuthError: If no ``api_key`` is supplied and a real transport is used.
            YouTubeAPIError: If the API returns an error payload.
        """
        if not api_key and transport is None:
            raise YouTubeAuthError(
                "YouTube Data API key required for live search "
                "(or inject a `transport` stub in tests)."
            )

        params: Dict[str, Any] = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "relevance",
            "maxResults": max(1, min(50, max_results)),
        }
        if relevance_language:
            params["relevanceLanguage"] = relevance_language
        if published_after:
            params["publishedAfter"] = published_after.astimezone(timezone.utc).isoformat()

        do_request = transport or self._default_transport
        payload = await do_request(self.SEARCH_ENDPOINT, params)
        if isinstance(payload, dict) and payload.get("error"):
            err = payload["error"]
            raise YouTubeAPIError(
                f"YouTube API error: {err.get('message', 'unknown')}",
                status_code=err.get("code"),
                body=err,
            )

        items = payload.get("items", []) if isinstance(payload, dict) else []
        videos = [YouTubeVideo.from_api_item(it) for it in items]
        return self._relevance_gate(videos, query)

    def _relevance_gate(
        self, videos: List[YouTubeVideo], query: str
    ) -> List[YouTubeVideo]:
        """Drop search hits that do not overlap the query (firehose noise filter)."""
        min_len = self._config.min_token_len
        tokens = {t.lower() for t in re.findall(r"\w+", query) if len(t) >= min_len}
        if not tokens:
            return videos
        kept: List[YouTubeVideo] = []
        for v in videos:
            haystack = f"{v.title} {v.description}".lower()
            if any(tok in haystack for tok in tokens):
                kept.append(v)
        return kept

    @staticmethod
    async def _default_transport(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Default HTTP transport using the sovereign ``httpx2`` client.

        Args:
            url: Request URL.
            params: Query parameters (must include the API ``key``).

        Returns:
            Parsed JSON response dict.
        """
        import httpx2

        async with httpx2.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
