# 🔱 Omega Engine — YouTube Research CLI
# AP: AP-YOUTUBE-CLI-v1.0.0
# ⬡ OMEGA ⬡ P3 ⬡ opencode ⬡ trc_youtube_cli ⬡ IMPLEMENTATION
#
# Opus remediation applied (2026-07-11):
#   Bug 2: MemoryStore.add_exchange() requires session_id (added) and uses
#           param name `response` not `assistant_response` (corrected).
#   Bug 3: add_exchange() is async — call with `await` directly, NOT via
#           anyio.to_thread.run_sync() which cannot execute coroutines.
#   Bug 4: anyio.run() accepts only one positional argument. `ingest` command
#           now uses a zero-argument wrapper closure to forward its args.
#   Bug 7: batch mode now creates YouTubeResearchModule ONCE and reuses it
#           across all URLs instead of opening/closing SQLite per URL (75x).
#
# Heritage:
#   [heritage: anyio 2024] All async I/O via anyio
#   [heritage: typer 2020] CLI framework consistent with omega CLI patterns

"""YouTube Research CLI — ingest transcripts into the sovereign Gnosis pipeline.

Commands:
    omega youtube ingest <video_url>   — ingest a single video
    omega youtube batch <file>         — ingest all URLs from a file (one per line)
    omega youtube verify <source_id>   — verify provenance chain for a source
"""

import sys
from pathlib import Path
from typing import Optional

import anyio
import typer

app = typer.Typer(name="youtube", help="YouTube Research Module ingestion commands.")


def _fetch_transcript(video_id: str) -> str:
    """Fetch raw transcript text from YouTube via youtube-transcript-api.

    Uses the v1.x instance-based API (v1.2.4+). Each call creates its own
    YouTubeTranscriptApi instance — NOT thread-safe, so per-call instantiation
    is required per research finding.

    Raises:
        RuntimeError: If no transcript is available for the video.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise RuntimeError(
            "youtube-transcript-api not installed. "
            "Run: pip install 'youtube-transcript-api>=0.6.3'"
        )

    try:
        # v1.x API: instance-based, .fetch() returns FetchedTranscript (iterable)
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=["en", "en-US"])
        # Each entry is a FetchedTranscriptSnippet with .text attribute
        return " ".join(entry.text for entry in transcript)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch transcript for {video_id}: {exc}") from exc


def _extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from a URL or return it if already an ID."""
    import re
    # Handle: https://www.youtube.com/watch?v=VIDEO_ID
    # Handle: https://youtu.be/VIDEO_ID
    # Handle: VIDEO_ID directly
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_\-]{11})",
        r"^([A-Za-z0-9_\-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Cannot extract video ID from: {url!r}")


async def _ingest_one(
    video_url: str,
    mod,           # YouTubeResearchModule — caller owns lifecycle (init/close)
    quiet: bool = False,
) -> Optional[str]:
    """Ingest a single YouTube URL using a pre-initialised module.

    Returns source_id on success, None on failure.
    The module is NOT closed here — the caller is responsible for lifecycle.
    """
    # Import here to keep CLI startup fast
    _src = str(Path(__file__).resolve().parent.parent.parent)
    if _src not in sys.path:
        sys.path.insert(0, _src)

    from omega_youtube_research import IngestResult

    video_url = video_url.strip()
    if not video_url or video_url.startswith("#"):
        return None  # skip empty lines and comments

    try:
        video_id = _extract_video_id(video_url)
    except ValueError as exc:
        typer.echo(f"  ⚠️  Skipping invalid URL: {exc}", err=True)
        return None

    if not quiet:
        typer.echo(f"  📥 Fetching transcript: {video_id} ({video_url})")

    try:
        raw_transcript = await anyio.to_thread.run_sync(
            lambda: _fetch_transcript(video_id)
        )
    except RuntimeError as exc:
        typer.echo(f"  ❌ Transcript fetch failed: {exc}", err=True)
        return None

    if not quiet:
        typer.echo(f"  🔍 Sieving + signing: {video_id}")

    try:
        result: IngestResult = await mod.ingest_transcript(
            video_id=video_id,
            raw_transcript=raw_transcript,
            source_url=video_url,
        )

        # ── Provenance Chain Fix: wire to MemoryStore (M22) ──────────────────
        # Opus Bug 2 fix: add_exchange() requires `session_id` as the 2nd param.
        # Opus Bug 3 fix: add_exchange() is async — await it directly, never
        #                 wrap a coroutine in anyio.to_thread.run_sync().
        try:
            from omega.memory_store import MemoryStore
            store = MemoryStore()
            metadata = mod.to_memory_metadata(result)
            # session_id convention: use source_id so ingest events are grouped
            # under the video's own session rather than polluting a user session.
            await store.add_exchange(
                entity_name="omega_youtube_research",
                session_id=result.source_id,          # REQUIRED — was missing
                user_message=f"Ingested YouTube transcript: {video_url}",
                response=result.attestation.cleaned_text_hash,  # param is `response`
                metadata=metadata,
            )
            if not quiet:
                typer.echo(f"  🔗 Provenance wired to MemoryStore")
        except Exception as mem_exc:
            # Non-fatal: provenance is already in SQLite; MemoryStore wire is best-effort
            typer.echo(
                f"  ⚠️  MemoryStore wire failed (non-fatal): {mem_exc}", err=True
            )

        if not quiet:
            typer.echo(
                f"  ✅ Ingested: {result.source_id} "
                f"| chunks={result.chunk_count} "
                f"| hash={result.provenance_hash[:24]}..."
            )
        return result.source_id

    except Exception as exc:
        typer.echo(f"  ❌ Ingest failed for {video_id}: {exc}", err=True)
        return None


@app.command("ingest")
def ingest(
    video_url: str = typer.Argument(..., help="YouTube video URL or video ID"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
):
    """Ingest a single YouTube video transcript into the Gnosis pipeline."""
    typer.echo(f"🔱 YouTube Research — Ingest")
    typer.echo(f"   URL: {video_url}")

    from omega_youtube_research.config import YouTubeResearchConfig
    from omega_youtube_research import YouTubeResearchModule

    # Opus Bug 4 fix: anyio.run() takes exactly ONE positional arg (the callable).
    # Use a zero-argument async closure to forward local variables into the coroutine.
    async def _run() -> Optional[str]:
        config = YouTubeResearchConfig.load()
        mod = YouTubeResearchModule(config=config)
        await mod.init()
        try:
            return await _ingest_one(video_url, mod, quiet)
        finally:
            await mod.close()

    source_id = anyio.run(_run)

    if source_id:
        typer.echo(f"\n✅ Success — source_id: {source_id}")
        raise typer.Exit(0)
    else:
        typer.echo(f"\n❌ Ingestion failed — see errors above", err=True)
        raise typer.Exit(1)


@app.command("batch")
def batch(
    file: Path = typer.Argument(
        ...,
        help="Path to file containing YouTube URLs (one per line). "
             "Defaults to youtube-links-for-ingestion.txt",
        exists=True,
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress per-video output"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Max videos to process"),
    skip: int = typer.Option(0, "--skip", help="Skip first N URLs"),
):
    """Batch-ingest all YouTube URLs from a file into the Gnosis pipeline."""
    typer.echo(f"🔱 YouTube Research — Batch Ingest")
    typer.echo(f"   File: {file}")

    urls = [
        line.strip()
        for line in file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if skip:
        urls = urls[skip:]
        typer.echo(f"   Skipping first {skip} URLs")

    if limit:
        urls = urls[:limit]

    typer.echo(f"   Processing: {len(urls)} URLs\n")

    success_ids = []
    failed = []

    # Opus Bug 7 fix: create the module ONCE and reuse it for all URLs.
    # The original code opened and closed SQLite once per URL (75 opens for 75 URLs).
    from omega_youtube_research.config import YouTubeResearchConfig
    from omega_youtube_research import YouTubeResearchModule

    async def _run_batch():
        config = YouTubeResearchConfig.load()
        mod = YouTubeResearchModule(config=config)
        await mod.init()
        try:
            for i, url in enumerate(urls, 1):
                typer.echo(f"[{i}/{len(urls)}] {url}")
                source_id = await _ingest_one(url, mod, quiet=quiet)
                if source_id:
                    success_ids.append(source_id)
                else:
                    failed.append(url)
        finally:
            await mod.close()

    anyio.run(_run_batch)

    typer.echo(f"\n{'='*60}")
    typer.echo(f"✅ Succeeded: {len(success_ids)}")
    typer.echo(f"❌ Failed:    {len(failed)}")
    if failed:
        typer.echo(f"\nFailed URLs:")
        for url in failed:
            typer.echo(f"  - {url}")

    raise typer.Exit(0 if not failed else 1)


@app.command("verify")
def verify(
    source_id: str = typer.Argument(..., help="Source ID to verify (e.g. yt_VIDEO_ID_TIMESTAMP)"),
):
    """Verify the provenance chain for an ingested transcript."""
    typer.echo(f"🔱 YouTube Research — Verify Provenance")
    typer.echo(f"   Source ID: {source_id}")

    async def _verify():
        from omega_youtube_research import AtomicPersistence, ProvenanceChain, ProvenanceChunk
        from omega_youtube_research.config import YouTubeResearchConfig
        from omega_youtube_research.persistence import ProvenanceChunkRecord

        config = YouTubeResearchConfig.load()
        pers = AtomicPersistence(db_path=Path(config.persistence.db_path))
        await pers.init()
        try:
            attestation = await pers.get_attestation(source_id)
            if attestation is None:
                typer.echo(f"  ❌ No attestation found for: {source_id}", err=True)
                return False

            chunks: list[ProvenanceChunkRecord] = await pers.get_chunks(source_id)
            if not chunks:
                typer.echo(f"  ❌ No provenance chunks found for: {source_id}", err=True)
                return False

            chain = ProvenanceChain(source_id=source_id, source_url=attestation.source_url)
            prov_chunks = [ProvenanceChunk(**c.model_dump()) for c in chunks]
            valid = chain.verify(prov_chunks)

            if valid:
                typer.echo(f"  ✅ Chain VALID — {len(chunks)} chunks, "
                           f"hash={attestation.provenance_hash[:32]}...")
            else:
                typer.echo(f"  ❌ Chain INVALID — tamper or reorder detected!", err=True)
            return valid
        finally:
            await pers.close()

    result = anyio.run(_verify)
    raise typer.Exit(0 if result else 1)


if __name__ == "__main__":
    app()
