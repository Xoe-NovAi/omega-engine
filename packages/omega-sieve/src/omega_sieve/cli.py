"""omega-sieve CLI — the Sovereign-Sieve command line.

Usage:
    sieve research "query"         Full research pipeline
    sieve scrape <url>             Scrape a single URL
    sieve youtube <url>            Extract YouTube video
    sieve config                   Show current config
    sieve init                     Initialize config file
    sieve providers                List available providers/tiers
"""

# AP: AP-OMEGA-SIEVE-CLI-v1.0.0

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(
    name="sieve",
    help="Sovereign-Sieve: T1→T2→T3 tiered web research & extraction",
    add_completion=False,
)
console = Console()

# Import our modules
from omega_sieve import __version__  # noqa: E402
from omega_sieve.scraper import SovereignScraper  # noqa: E402
from omega_sieve.verifier import TriangulationVerifier  # noqa: E402
from omega_sieve.guards import SovereignSentry  # noqa: E402
from omega_sieve.youtube import YouTubeSieve  # noqa: E402
from omega_sieve.research import Researcher  # noqa: E402
from omega_sieve.config import load_config, init_config, SieveConfig  # noqa: E402


def _version_callback(value: bool):
    if value:
        console.print(f"[bold]omega-sieve[/bold] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V",
        help="Show version and exit",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """Sovereign-Sieve: tiered web research & extraction."""
    pass


@app.command()
def research(
    query: str = typer.Argument(..., help="Research query"),
    max_sources: int = typer.Option(5, "--max", "-m", help="Maximum sources to scrape"),
    depth: str = typer.Option(
        "balanced", "--depth", "-d",
        help="Research depth: quick (T1), balanced (T1+T2), deep (T1+T2+T3)",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output to JSON file",
    ),
):
    """Full research pipeline: search → scrape → verify."""
    config = load_config()
    researcher = Researcher()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Researching: {query}", total=None)

        result = asyncio.run(researcher.research(query, max_sources=max_sources, depth=depth))

    if result.error:
        console.print(f"[red]Error: {result.error}[/red]")
        raise typer.Exit(1)

    # Display results
    console.print(f"\n[bold]Research:[/bold] {query}")
    console.print(f"[dim]Sources: {len(result.successful_sources)}/{len(result.sources)} | "
                  f"Latency: {result.latency_ms}ms | Depth: {depth}[/dim]\n")

    for i, source in enumerate(result.successful_sources, 1):
        console.print(f"[bold cyan]{i}.[/bold cyan] {source.url}")
        console.print(f"   [dim]Tier: {source.tier} | Provider: {source.provider_name} | "
                      f"Latency: {source.latency_ms}ms[/dim]")
        # Show first 300 chars
        preview = source.content[:300].strip()
        if preview:
            console.print(Panel(preview, border_style="dim", width=80))
        console.print()

    # Also show failed sources
    failed = [s for s in result.sources if not s.success]
    if failed:
        console.print(f"[yellow]Failed sources ({len(failed)}):[/yellow]")
        for s in failed:
            console.print(f"  [dim]{s.url}[/dim] — [red]{s.error}[/red]")

    # Output to file
    if output:
        data = {
            "query": query,
            "depth": depth,
            "sources": [
                {
                    "url": s.url,
                    "tier": s.tier,
                    "success": s.success,
                    "provider": s.provider_name,
                    "latency_ms": s.latency_ms,
                    "content": s.content,
                    "error": s.error,
                }
                for s in result.sources
            ],
            "latency_ms": result.latency_ms,
        }
        output.write_text(json.dumps(data, indent=2))
        console.print(f"[green]Written to {output}[/green]")


@app.command()
def scrape(
    url: str = typer.Argument(..., help="URL to scrape"),
    tier: str = typer.Option("auto", "--tier", "-t",
                              help="Extraction tier: auto, fast, surgical, deep"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output to file",
    ),
):
    """Scrape a single URL with auto tier-selection."""
    scraper = SovereignScraper()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Scraping: {url}", total=None)

        if tier == "auto":
            result = asyncio.run(scraper.scrape_auto(url))
        else:
            result = asyncio.run(scraper.scrape(url, tier=tier))

    if not result.success:
        console.print(f"[red]Scrape failed: {result.error}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]URL:[/bold] {result.url}")
    console.print(f"[dim]Tier: {result.tier} | Provider: {result.provider_name} | "
                  f"Latency: {result.latency_ms}ms | "
                  f"Content: {len(result.content)} chars[/dim]\n")

    # Render as markdown if it looks like prose
    if len(result.content.split()) > 20:
        console.print(Markdown(result.content[:5000]))
    else:
        console.print(result.content[:5000])

    if len(result.content) > 5000:
        console.print(f"\n[dim]... ({len(result.content) - 5000} more chars)[/dim]")

    if output:
        output.write_text(result.content)
        console.print(f"[green]Written to {output}[/green]")


@app.command()
def youtube(
    url: str = typer.Argument(..., help="YouTube URL"),
    tier: str = typer.Option("auto", "--tier", "-t",
                              help="Extraction tier: auto, metadata, captions, transcription"),
):
    """Extract YouTube video content."""
    sieve = YouTubeSieve()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Extracting: {url}", total=None)
        result = asyncio.run(sieve.extract(url, tier=tier))

    if not result.success and result.error:
        console.print(f"[red]Error: {result.error}[/red]")
        raise typer.Exit(1)

    # Metadata table
    meta = result.metadata
    table = Table(title=f"YouTube: {meta.title or result.video_id}")
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Video ID", result.video_id)
    table.add_row("Title", meta.title or "—")
    table.add_row("Channel", meta.channel or "—")
    table.add_row("Duration", f"{meta.duration}s" if meta.duration else "—")
    table.add_row("Views", f"{meta.view_count:,}" if meta.view_count else "—")
    table.add_row("Tier", result.tier)
    table.add_row("Has Content", "✅" if result.has_content else "❌")
    console.print(table)

    if result.transcript:
        console.print(f"\n[bold]Transcript ({len(result.transcript)} chars):[/bold]")
        console.print(Panel(result.transcript[:2000], border_style="green"))
        if len(result.transcript) > 2000:
            console.print(f"[dim]... ({len(result.transcript) - 2000} more chars)[/dim]")


@app.command()
def providers():
    """List available extraction providers and tiers."""
    scraper = SovereignScraper()

    table = Table(title="Available Providers & Tiers")
    table.add_column("Tier", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Status")
    table.add_column("Install")

    tiers = [
        ("T1 (Fast)", "Trafilatura", scraper.t1.available,
         "pip install omega-sieve[fast]"),
        ("T2 (Surgical)", "Trafilatura + Domain Rules", scraper.t2.available,
         "pip install omega-sieve[fast]"),
        ("T3 (Deep)", "Crawl4AI + Playwright", scraper.t3.available,
         "pip install omega-sieve[full]"),
    ]

    for tier_name, provider, available, install_cmd in tiers:
        table.add_row(
            tier_name,
            provider,
            "✅ Available" if available else "❌ Not installed",
            "" if available else install_cmd,
        )

    console.print(table)

    # YouTube tiers
    console.print("\n[bold]YouTube Tiers:[/bold]")
    yt_table = Table()
    yt_table.add_column("Tier", style="cyan")
    yt_table.add_column("Provider")
    yt_table.add_column("Status")

    try:
        import yt_dlp  # noqa: F401
        yt_dlp_ok = True
    except ImportError:
        yt_dlp_ok = False

    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # noqa: F401
        yt_trans_ok = True
    except ImportError:
        yt_trans_ok = False

    yt_table.add_row("T1 (Metadata)", "yt-dlp", "✅ Available" if yt_dlp_ok else "❌ (pip install omega-sieve[youtube])")
    yt_table.add_row("T2 (Captions)", "youtube-transcript-api", "✅ Available" if yt_trans_ok else "❌ (pip install omega-sieve[youtube])")
    yt_table.add_row("T3 (Transcribe)", "Whisper.cpp + Silero VAD", "❌ (pip install omega-sieve[transcription])")
    console.print(yt_table)


@app.command()
def config():
    """Show current configuration."""
    cfg = load_config()
    console.print("[bold]Active Configuration:[/bold]")
    console.print(json.dumps(cfg.to_dict(), indent=2))


@app.command()
def init():
    """Initialize default configuration file."""
    path = init_config()
    console.print(f"[green]Configuration initialized at: {path}[/green]")
    console.print("Edit the file to add API keys, proxy settings, etc.")


@app.command()
def verify(
    url: str = typer.Argument(..., help="URL to verify across tiers"),
):
    """Run T1 and T3 on the same URL and verify consistency."""
    scraper = SovereignScraper()
    verifier = TriangulationVerifier()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Running T1 and T3 extraction...", total=None)
        results = asyncio.run(scraper.scrape_all(url))

    t1 = results.get("fast")
    t3 = results.get("deep")

    console.print(f"[bold]Verification:[/bold] {url}\n")

    # Show T1 result
    console.print(f"[cyan]T1 (Fast):[/cyan] {'✅' if t1 and t1.success else '❌'} "
                  f"{t1.latency_ms if t1 else 0}ms, "
                  f"{len(t1.content) if t1 else 0} chars" if t1 else "N/A")

    # Show T3 result
    console.print(f"[cyan]T3 (Deep):[/cyan] {'✅' if t3 and t3.success else '❌'} "
                  f"{t3.latency_ms if t3 else 0}ms, "
                  f"{len(t3.content) if t3 else 0} chars\n" if t3 else "N/A")

    if t1 and t3 and t1.success and t3.success:
        ver = verifier.verify_t1_t3(t1, t3)
        console.print(f"[bold]Verification Result:[/bold] "
                      f"{'✅ PASSED' if ver.passed else '❌ FAILED'}")
        console.print(f"  Confidence: {ver.confidence:.2%}")
        console.print(f"  Lexical similarity: {ver.lexical_similarity:.2%}")
        console.print(f"  Content delta: {ver.content_delta}")

        if ver.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for w in ver.warnings:
                console.print(f"  ⚠ {w}")
    elif t1 and t1.success:
        console.print("[yellow]T3 unavailable — cannot triangulate[/yellow]")
    elif t3 and t3.success:
        console.print("[yellow]T1 unavailable — cannot triangulate[/yellow]")
    else:
        console.print("[red]Both extractions failed — cannot verify[/red]")

    # Show content comparison
    if t1 and t1.success and t3 and t3.success:
        console.print("\n[bold]Content Preview Comparison:[/bold]")
        preview_len = 200
        console.print(Panel(
            t1.content[:preview_len], title="T1 Preview", border_style="blue"
        ))
        console.print(Panel(
            t3.content[:preview_len], title="T3 Preview", border_style="magenta"
        ))


if __name__ == "__main__":
    app()