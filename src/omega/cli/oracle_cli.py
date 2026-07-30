# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Omega CLI — Oracle Commands
# AP: AP-ORACLE-CLI-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: HERMES | CONTEXT: CLI-COMMANDS]


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import anyio
import logging
import sys
from pathlib import Path
from typing import Optional

from omega.cvar_table import cvar_get, cvar_namespace

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    import typer
    from rich.console import Console
    from rich.table import Table

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    typer = None

from omega.oracle import Oracle, OracleResponse, EntityRegistry, Entity, Orchestrator, ModelGateway
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
from omega.request_queue import RequestQueue
from omega.oracle.feed_utils import load_demand_signals, transition_demand, summarize_feed
from omega.ics import render as ics_render  # [id-soft: vet-071] netchan header

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="🔱 Omega Engine CLI")

# ── YouTube Research sub-commands (§3.2 — Track 2) ──────────────────────
try:
    from omega.cli.youtube_cli import app as youtube_app
    app.add_typer(youtube_app, name="youtube", help="YouTube Research operations")
except ImportError:
    pass  # youtube-transcript-api not installed — subcommand unavailable

# ── Bundle sub-commands (P0-4 Sovereign Export Bundle) ──────────────────
try:
    from omega.cli.bundle import app as bundle_app
    app.add_typer(bundle_app, name="bundle", help="Sovereign Bundle — export/import entity state as .omega bundles")
except ImportError:
    pass  # bundle module not available

# ── Vault sub-commands (V-1 VaultCore MVP) ───────────────────────────────
try:
    from omega.cli.vault import vault as vault_app
    app.add_typer(vault_app, name="vault", help="Sovereign credential vault (age + Argon2id)")
except ImportError:
    pass  # vault module not available

# ── Local Queue sub-commands (Phase 2 Local Worker Pool) ─────────────────
try:
    from omega.cli.local_queue import app as local_queue_app
    app.add_typer(local_queue_app, name="local-queue", help="Fire-and-forget local inference queue")
except ImportError:
    pass  # local_queue module not available

def _load_config() -> dict:
    """Load core omega config."""
    config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
    if not config_path.exists():
        return {}
    import yaml
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}


def _save_config(config: dict):
    """Save core omega config."""
    config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


# ── TALK — Route automatically ──────────────────────────────────────────
@app.command()
def talk(
    query: str = typer.Argument(..., help="Your question for the Oracle"),
    transient: bool = typer.Option(False, "--transient", "-t", help="Run in transient mode (no soul updates)"),
    iwad: Optional[str] = typer.Option(None, "--iwad", "-w", help="IWAD stack to load"),
):
    """Ask the Oracle anything. Routes to the best entity automatically."""
    async def _run():
        oracle = Oracle()
        try:
            result = await oracle.talk(query, transient=transient)
            _display_response(result)
        finally:
            pass  # Oracle has async context management; no explicit close needed
    anyio.run(_run)


# ── SUMMON — Direct entity summon ───────────────────────────────────────
@app.command()
def summon(
    entity: str = typer.Argument(..., help="Entity name to summon"),
    query: str = typer.Argument(..., help="Your question for this entity"),
    transient: bool = typer.Option(False, "--transient", "-t", help="Run in transient mode (no soul updates)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="[D118] Model override — bypass TriageRouter and use specific model (e.g., qwen3-1.7b)"),
    iwad: Optional[str] = typer.Option(None, "--iwad", "-w", help="IWAD stack to load"),
):
    """Summon a specific entity by name.
    
    [D118 Dual-Inference Mandate] Use --model to bypass TriageRouter and route
    to a specific model. Example: omega summon roc_racoon "hello" --model qwen3-1.7b
    """
    async def _run():
        oracle = Oracle()
        try:
            result = await oracle.summon(entity, query, transient=transient, model_override=model)
            _display_response(result)
        finally:
            pass  # Oracle has async context management; no explicit close needed
    anyio.run(_run)


# ── DEFAULT-ENTITY — Set the default entity ──────────────────────────────
@app.command(name="default-entity")
def default_entity(
    name: str = typer.Argument(..., help="Entity name to set as default"),
):
    """Set the default entity for the Oracle."""
    registry = EntityRegistry()
    if not registry.get(name):
        console.print(f"[red]Error: Entity '{name}' not found in pantheon.[/red]")
        raise typer.Exit(1)
    
    config = _load_config()
    config.setdefault("omega", {}).setdefault("entity", {})["default"] = name
    _save_config(config)
    console.print(f"[green]✅ Default entity set to: {name}[/green]")

# ── ENTITY — Show detailed information about a specific entity ──────────
@app.command(name="entity")
@app.command(name="entity-info")
def entity_cmd(
    name: str = typer.Argument(..., help="Entity name to inspect"),
):
    """Show detailed information about a specific entity."""
    entity = EntityRegistry().get(name)
    if entity is None:
        console.print(f"[red]Error: Entity '{name}' not found in pantheon.[/red]")
        available = [e.name for e in EntityRegistry().list()]
        if available:
            console.print(f"[dim]Available entities: {', '.join(available[:10])}{'...' if len(available) > 10 else ''}[/dim]")
        raise typer.Exit(1)

    table = Table(title=f"🔱 Entity: {entity.name}", show_header=True, header_style="bold cyan")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Name", entity.name)
    table.add_row("Slots", ", ".join(entity.slots) if entity.slots else "—")
    table.add_row("Domains", ", ".join(entity.domains) if entity.domains else "—")
    table.add_row("Model", entity.model or "—")
    table.add_row("Temperature", str(entity.temperature))
    table.add_row("Container", str(entity.container) if entity.container else "—")
    if entity.personality:
        personality_preview = entity.personality[:200] + ("..." if len(entity.personality) > 200 else "")
        table.add_row("Personality", personality_preview)

    console.print(table)


# ── ENTITY WORKSPACE STATUS — Block utilization ────────────────────────
@app.command()
def entity_workspace_status(
    entity: str = typer.Argument(..., help="Entity name to inspect workspace for"),
):
    """Show workspace block utilization for an entity (knowledge + workspace).
    
    Reads data/entities/{entity}/knowledge/ and data/entities/{entity}/workspace/
    and calculates character counts per file, per-domain breakdowns, and
    total utilization. Block limits are displayed if defined in entity config.
    """
    DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
    entity_dir = DATA_DIR / "entities" / entity.lower()

    if not entity_dir.exists():
        console.print(f"[red]Error: Entity directory not found: {entity_dir}[/red]")
        registry = EntityRegistry()
        available = [e.name for e in registry.list()]
        if available:
            console.print(f"[dim]Available entities: {', '.join(available[:15])}{'...' if len(available) > 15 else ''}[/dim]")
        raise typer.Exit(1)

    knowledge_dir = entity_dir / "knowledge"
    workspace_dir = entity_dir / "workspace"
    soul_path = entity_dir / "soul.yaml"

    def _count_chars(directory: Path) -> list:
        """Count characters in all files under a directory."""
        file_stats = []
        if not directory.exists():
            return file_stats
        for f in sorted(directory.rglob("*")):
            if f.is_file():
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                    file_stats.append({
                        "path": str(f.relative_to(entity_dir)),
                        "chars": len(text),
                        "lines": text.count("\n") + 1,
                    })
                except (OmegaError, RuntimeError, OSError) as e:
                    file_stats.append({
                        "path": str(f.relative_to(entity_dir)),
                        "chars": 0,
                        "lines": 0,
                        "error": str(e),
                    })
        return file_stats

    knowledge_files = _count_chars(knowledge_dir)
    workspace_files = _count_chars(workspace_dir)

    # Soul file counts toward entity total
    soul_stats = None
    if soul_path.exists():
        text = soul_path.read_text(encoding="utf-8", errors="replace")
        soul_stats = {
            "path": str(soul_path.relative_to(entity_dir)),
            "chars": len(text),
            "lines": text.count("\n") + 1,
        }
        all_files = knowledge_files + workspace_files + [soul_stats]
    else:
        all_files = knowledge_files + workspace_files

    knowledge_chars = sum(f["chars"] for f in knowledge_files)
    workspace_chars = sum(f["chars"] for f in workspace_files)
    soul_chars = soul_stats["chars"] if soul_stats else 0
    total_chars = knowledge_chars + workspace_chars + soul_chars

    # Check for block limits in entity registry
    registry = EntityRegistry()
    entity_obj = registry.get(entity)
    block_limit = None
    if entity_obj:
        if hasattr(entity_obj, "config"):
            block_limit = getattr(entity_obj.config, "block_limit", None)
        elif hasattr(entity_obj, "block_limit"):
            block_limit = entity_obj.block_limit

    table = Table(title=f"Workspace Block Utilization: {entity}", show_header=True, header_style="bold cyan")
    table.add_column("Domain", style="cyan")
    table.add_column("Files", style="white")
    table.add_column("Characters", style="yellow")
    table.add_column("Lines", style="green")
    table.add_column("Block Limit", style="magenta")

    n_knowledge = len(knowledge_files)
    n_workspace = len(workspace_files)
    k_lines = sum(f["lines"] for f in knowledge_files)
    w_lines = sum(f["lines"] for f in workspace_files)
    s_lines = soul_stats["lines"] if soul_stats else 0

    table.add_row("knowledge/", str(n_knowledge), f"{knowledge_chars:,}", f"{k_lines:,}", str(block_limit or "N/A"))
    table.add_row("workspace/", str(n_workspace), f"{workspace_chars:,}", f"{w_lines:,}", str(block_limit or "N/A"))
    table.add_row("soul.yaml", "1" if soul_stats else "0", f"{soul_chars:,}", f"{s_lines:,}", "—")
    table.add_row("", "", "", "", "")
    table.add_row("TOTAL", str(len(all_files)), f"{total_chars:,}", f"{k_lines + w_lines + s_lines:,}", str(block_limit or "N/A"))

    console.print(table)

    # Per-file detail
    if knowledge_files or workspace_files:
        detail_table = Table(title="File Detail", show_header=True, header_style="dim")
        detail_table.add_column("Path", style="cyan")
        detail_table.add_column("Chars", style="yellow")
        detail_table.add_column("Lines", style="green")
        for f in (knowledge_files + workspace_files):
            detail_table.add_row(
                f["path"],
                f"{f['chars']:,}",
                f"{f['lines']:,}",
            )
        if soul_stats:
            detail_table.add_row(
                soul_stats["path"],
                f"{soul_stats['chars']:,}",
                f"{soul_stats['lines']:,}",
            )
        console.print(detail_table)


# ── TRANSIENT — Toggle transient mode ──────────────────────────────────
@app.command()
def transient(
    mode: Optional[str] = typer.Argument(None, help="Set transient mode (on/off)"),
):
    """Get or set the default transient mode."""
    config = _load_config()
    if mode is None:
        current = cvar_get("config.entity.allow_transient", True)
        console.print(f"Transient mode is currently: [bold cyan]{'ON' if current else 'OFF'}[/bold cyan]")
        return

    if mode.lower() in ["on", "true", "1"]:
        config.setdefault("omega", {}).setdefault("entity", {})["allow_transient"] = True
        console.print("[green]✅ Transient mode enabled by default.[/green]")
    else:
        config.setdefault("omega", {}).setdefault("entity", {})["allow_transient"] = False
        console.print("[yellow]⚠️ Transient mode disabled by default.[/yellow]")
    
    _save_config(config)


# ── HEADER — Toggle header display ─────────────────────────────────────
@app.command()
def header(
    mode: Optional[str] = typer.Argument(None, help="Set header mode (full/compact/off)"),
):
    """Get or set the session header mode."""
    config = _load_config()
    if mode is None:
        current = cvar_get("config.session_header.mode", "compact")
        console.print(f"Header mode is currently: [bold cyan]{current}[/bold cyan]")
        return

    if mode.lower() in ["full", "compact", "off"]:
        config.setdefault("omega", {}).setdefault("session_header", {})["mode"] = mode.lower()
        console.print(f"[green]✅ Header mode set to: {mode.lower()}[/green]")
    else:
        console.print("[red]Error: Invalid mode. Use 'full', 'compact', or 'off'.[/red]")
        raise typer.Exit(1)
    
    _save_config(config)


# ── LIST-ENTITIES — Show the pantheon ──────────────────────────────────
@app.command()
def list_entities():
    """List all entities in the current pantheon."""
    registry = EntityRegistry()
    table = Table(title="🔱 Omega Entity Registry")

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Slots", style="magenta")
    table.add_column("Model", style="blue")
    table.add_column("Temperature")

    for entity in registry.list():
        if entity.container:
            # Nova gets special display
                table.add_row(
                    entity.name,
                    "Voice Interface",
                    entity.model,
                    str(entity.temperature),
                )
        else:
            table.add_row(
                entity.name,
                ", ".join(entity.slots) if entity.slots else "—",
                entity.model,
                str(entity.temperature),
            )

    console.print(table)
    console.print(f"\n[{len(registry.list())} entities in registry]")


# ── ADD-ENTITY — Interactive entity creation ────────────────────────────
@app.command()
def add_entity():
    """Add a new entity to the pantheon (interactive)."""
    name = typer.prompt("Entity name")
    domains = typer.prompt("Domains (comma-separated)")
    model = typer.prompt("Model name", default="qwen3-1.7b-q6_k")
    personality = typer.prompt("Personality prompt (system prompt)")
    temperature = typer.prompt("Temperature (0.0-1.0)", type=float, default=0.7)

    entity = Entity(
        name=name,
        domains=[d.strip() for d in domains.split(",")],
        model=model,
        personality=personality,
        temperature=temperature,
    )

    registry = EntityRegistry()
    async def _run():
        await registry.add(entity)
    anyio.run(_run)
    console.print(f"[green]✅ {name} added to pantheon![/green]")
    console.print("[dim]Edit ~/omega/config/entities.yaml to add pillar mappings, sigils, etc.[/dim]")


# ── REMOVE-ENTITY — Delete an entity ───────────────────────────────────
@app.command()
def mcp_restart(
    service: str = typer.Argument(..., help="The service name to restart (e.g., omega-research)")
):
    """Restart a specific MCP service."""
    async def _run():
        console.print(f"[yellow]🔄 Restarting {service}...[/yellow]")
        import subprocess
        try:
            await anyio.to_thread.run_sync(subprocess.run, ["systemctl", "--user", "restart", f"{service}.service"], check=True)
            console.print(f"[green]✅ {service} restarted.[/green]")
        except OmegaError as e:
            console.print(f"[red]OmegaError restarting {service}: {e}[/red]")
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Unexpected error restarting {service}: {e}", exc_info=True)
            console.print(f"[red]Unexpected error restarting {service}: {e}[/red]")
    anyio.run(_run)



# ── BACKENDS — Provider Fabric Status ────────────────────────────────────
@app.command()
def backends():
    """Show the current provider fabric and health status."""
    async def _run():
        gateway = ModelGateway()
        providers = gateway.list_providers()
        table = Table(title="🔱 Provider Fabric", show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="cyan")
        table.add_column("Priority", style="yellow")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="green")
        for p in providers:
            status = "[green]HEALTHY[/green]" if p["healthy"] else "[red]DEAD/UNKNOWN[/red]"
            table.add_row(p["name"], str(p["priority"]), p["type"], status)
        console.print(table)
    anyio.run(_run)


@app.command(name="model-status")
def model_status():
    """Show all configured models and their specifications."""
    async def _run():
        gateway = ModelGateway()
        models = gateway.list_models()
        table = Table(title="🤖 Configured Models", show_header=True, header_style="bold cyan")
        table.add_column("Model", style="cyan")
        table.add_column("Context", style="yellow")
        table.add_column("Threads", style="green")
        table.add_column("KV Cache", style="magenta")
        for m in models:
            table.add_row(
                m["name"],
                str(m.get("context_window", "N/A")),
                str(m.get("threads", "N/A")),
                str(m.get("kv_cache", "N/A"))
            )
        console.print(table)
    anyio.run(_run)


# ── VET — Sovereign Mandate Compliance Check ───────────────────────────────
# ── Display helper ─────────────────────────────────────────────────────
def _display_response(result: OracleResponse):
    """Format and display an Oracle response."""
    config = _load_config()
    header_mode = cvar_get("config.session_header.mode", "compact")

    if header_mode != "off":
        # [id-soft: vet-071] netchan — ICS-S header via ics.py (single source of truth)
        header = ics_render(
            entity=result.entity,
            model=result.model,
            channel="cli",
            trace_id=result.trace_id[:8] if result.trace_id else None,
            phase=None,  # Phase retrieved dynamically from session context
            mode=header_mode,
        )
        if header:
            console.print(f"[dim]{header}[/dim]")

    prefix = f"[bold cyan]{result.entity}[/bold cyan]"
    if result.slots:
        prefix += f" [dim]({', '.join(str(s) for s in result.slots)})[/dim]"
    # Sigil and pantheon are in the response text (via Entity.metadata) and are
    # no longer carried in OracleResponse — they are WAD content, not engine data.

    console.print(f"{prefix}")
    
    output_text = result.text
    if result.cost_warning:
        output_text += f"\n\n[bold yellow]{result.cost_warning}[/bold yellow]"
        
    console.print(f"{output_text}\n")


# ── REQUEST QUEUE COMMANDS ──────────────────────────────────────────────

@app.command()
def queue_status():
    """Show pending queued/review items."""
    async def _run():
        q = RequestQueue()
        stats = await q.stats()
        console.print("[bold]Request Queue Status[/bold]")
        console.print(f"  Queued:       {stats['queued']}")
        console.print(f"  Pending Review: {stats['pending_review']}")
        console.print(f"  Completed:    {stats['completed']}")
        if stats['queued'] > 0:
            requests = await q.get_queued_requests()
            table = Table(title="Queued Requests")
            table.add_column("ID", style="cyan")
            table.add_column("Priority", style="yellow")
            table.add_column("Query", style="white")
            table.add_column("Created", style="green")
            for r in requests[:20]:
                table.add_row(
                    r.get("id", "?"),
                    r.get("priority", "P2"),
                    r.get("query", "?")[:60],
                    r.get("created_at", "?")[:19],
                )
            console.print(table)
    anyio.run(_run)

@app.command()
def process_queue():
    """Process all queued research requests."""
    async def _run():
        q = RequestQueue()
        requests = await q.get_queued_requests()
        if not requests:
            console.print("[yellow]No queued requests to process.[/yellow]")
            return
        console.print(f"[bold]Processing {len(requests)} queued requests...[/bold]")
        for req in requests:
            console.print(f"  Processing {req['id']}: {req['query'][:60]}...")
            result = {"status": "processed", "note": "Implement execution logic in Phase C"}
            await q.complete_request(req["id"], result)
        console.print("[green]Done.[/green]")
    anyio.run(_run)

@app.command()
def review_pending():
    """Process all pending cloud review requests."""
    async def _run():
        q = RequestQueue()
        reviews = await q.get_review_requests()
        if not reviews:
            console.print("[yellow]No pending review requests.[/yellow]")
            return
        console.print(f"[bold]Processing {len(reviews)} review requests...[/bold]")
        for rev in reviews:
            console.print(f"  Reviewing {rev['id']}: {rev.get('work_product_path', '?')}")
            result = {"status": "reviewed", "note": "Implement review logic in Phase C"}
            await q.complete_request(rev["id"], result)
        console.print("[green]Done.[/green]")
    anyio.run(_run)

@app.command()
def queue_prune(
    days: int = typer.Option(7, "--stale", "-s", help="Prune requests older than N days"),
):
    """Archive stale requests older than N days."""
    async def _run():
        q = RequestQueue()
        pruned = await q.prune_stale(days)
        console.print(f"[green]Pruned {pruned} stale requests (>{days} days).[/green]")
    anyio.run(_run)

# ── LIBRARY COMMANDS ────────────────────────────────────────────────────

@app.command()
def library_curate(
    domain: str = typer.Option("all", "--domain", "-d", help="Domain to curate (e.g., P7, all)"),
):
    """Run domain curation."""
    async def _run():
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog()
        await c.ensure_db()
        console.print(f"[bold]Library curation triggered for domain: {domain}[/bold]")
        console.print("[yellow]Curator dispatch logic — implement agent dispatch here[/yellow]")
    anyio.run(_run)

@app.command()
def library_status():
    """Show library catalog statistics."""
    async def _run():
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog()
        stats = await c.stats()
        console.print("[bold]Library Catalog Status[/bold]")
        console.print(f"  Total Documents: {stats['total_documents']}")
        console.print(f"  Average Quality: {stats['avg_quality']}")
        console.print("  By Domain:")
        for domain, count in stats.get("by_domain", {}).items():
            console.print(f"    {domain}: {count}")
    anyio.run(_run)

@app.command()
def library_search(
    query: str = typer.Argument(..., help="Search query"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Filter by domain"),
):
    """Search the library catalog."""
    async def _run():
        from omega.library.catalog import LibraryCatalog
        c = LibraryCatalog()
        results = await c.search(domain=domain, query=query)
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return
        table = Table(title=f"Search Results: {query}")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Domain", style="yellow")
        table.add_column("Quality", style="green")
        for r in results:
            table.add_row(
                r.get("id", "?")[:20],
                r.get("title", "Untitled")[:40],
                r.get("domain", "?"),
                str(round(r.get("avg_quality", 0), 2)),
            )
        console.print(table)
    anyio.run(_run)

# ── BENCHMARK COMMANDS ───────────────────────────────────────────────────

@app.command()
def bench_run(
    model: str = typer.Argument(..., help="Model ID to benchmark"),
    role: str = typer.Argument(..., help="Agent role to benchmark"),
    samples: int = typer.Option(10, "--samples", "-s", help="Number of samples to run"),
):
    """Run a benchmark for a specific model and role."""
    async def _run():
        from omega.benchmarks.runner import BenchmarkRunner
        runner = BenchmarkRunner()
        result = await runner.run(model, role, samples=samples)
        console.print(f"[bold]Benchmark Complete: {model} for {role}[/bold]")
        console.print(f"  TTFT: {result.ttft_ms}ms")
        console.print(f"  TPS: {result.tokens_per_sec} tok/s")
        console.print(f"  Peak RAM: {result.peak_ram_mb}MB")
        console.print(f"  Avg Quality: {result.avg_quality_score}")
        console.print(f"  Scores: {result.scores}")
    anyio.run(_run)

@app.command()
def bench_compare(
    role: str = typer.Argument(..., help="Role to compare models for"),
):
    """Compare all benchmarked models for a specific role."""
    async def _run():
        from omega.benchmarks.runner import BenchmarkRunner
        runner = BenchmarkRunner()
        results = await runner.compare(role)
        if not results:
            console.print("[yellow]No benchmarks found for this role.[/yellow]")
            return
        table = Table(title=f"Benchmark Comparison: {role}")
        table.add_column("Model", style="cyan")
        table.add_column("TTFT (ms)", style="yellow")
        table.add_column("TPS", style="green")
        table.add_column("RAM (MB)", style="magenta")
        table.add_column("Quality", style="blue")
        for r in results:
            table.add_row(r.model, str(r.ttft_ms), str(r.tokens_per_sec), str(r.peak_ram_mb), str(r.avg_quality_score))
        console.print(table)
    anyio.run(_run)

@app.command()
def bench_rank(
    role: str = typer.Argument(..., help="Role to rank models for"),
):
    """Show the best model for a specific role based on quality."""
    async def _run():
        from omega.benchmarks.runner import BenchmarkRunner
        runner = BenchmarkRunner()
        ranked = await runner.rank(role)
        if not ranked:
            console.print("[yellow]No benchmarks found for this role.[/yellow]")
            return
        console.print(f"[bold]Best model for {role}: {ranked[0].model}[/bold]")
        table = Table(title=f"Ranking: {role}")
        table.add_column("Rank", style="cyan")
        table.add_column("Model", style="white")
        table.add_column("Quality", style="green")
        for i, r in enumerate(ranked, 1):
            table.add_row(str(i), r.model, str(r.avg_quality_score))
        console.print(table)
    anyio.run(_run)

@app.command()
def bench_list():
    """List all completed benchmark runs."""
    async def _run():
        from omega.benchmarks.runner import BenchmarkRunner
        runner = BenchmarkRunner()
        results = await runner.list_runs()
        if not results:
            console.print("[yellow]No benchmark runs yet.[/yellow]")
            return
        table = Table(title="All Benchmark Runs")
        table.add_column("Model", style="cyan")
        table.add_column("Role", style="white")
        table.add_column("Date", style="green")
        for r in results:
            table.add_row(r.model, r.role, r.timestamp[:10])
        console.print(table)
    anyio.run(_run)

# ── CROSS-POLLINATION COMMANDS ───────────────────────────────────────────
@app.command(name="check-feed")
def check_feed_cmd(
    agent: str = typer.Option("sophia", "--agent", "-a", help="Agent name to check feed for"),
    consume: bool = typer.Option(False, "--consume", "-c", help="Mark unconsumed signals as consumed"),
):
    """Check knowledge feed and demand signals for unconsumed content."""
    from omega.oracle.feed_utils import (
        load_knowledge_signals,
        load_demand_signals,
        find_new_signals,
        summarize_feed,
        consume_signal,
        write_knowledge_signal,
        write_cross_reference,
    )
    from rich.table import Table

    signals = load_knowledge_signals()
    demands = load_demand_signals()
    unconsumed = find_new_signals(agent, signals)
    summary = summarize_feed(signals, demands)

    if unconsumed:
        table = Table(title=f"📡 New Knowledge Signals for {agent}", border_style="cyan")
        table.add_column("Signal", style="cyan")
        table.add_column("Producer", style="magenta")
        table.add_column("Domain", style="yellow")
        table.add_column("Priority", style="red")
        table.add_column("Title", style="white")
        for sig in unconsumed:
            table.add_row(
                sig.get("signal_id", "?")[:32],
                sig.get("producer", "?"),
                sig.get("domain", "?"),
                sig.get("priority", "?"),
                sig.get("title", "?")[:60],
            )
        console.print(table)

        if consume:
            for sig in unconsumed:
                consume_signal(sig, agent)
                write_knowledge_signal(sig)
                write_cross_reference(agent, sig)
            console.print(f"[green]Consumed {len(unconsumed)} new signals for {agent}.[/green]")
    else:
        console.print(f"[dim]No new knowledge signals for {agent}.[/dim]")

    consumed_count = summary["total_signals"] - len(unconsumed)
    console.print(f"  KSIGs: {summary['total_signals']} ({consumed_count} consumed, {len(unconsumed)} new)")
    console.print(f"  DEMs: {summary['total_demands']} ({summary['open_demands']} open)")


@app.command(name="demand-status")
def demand_status(
    status_filter: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
):
    """Show demand signal lifecycle status."""
    demands = load_demand_signals()
    if not demands:
        console.print("[dim]No demand signals found.[/dim]")
        return
    if status_filter:
        demands = [d for d in demands if d.get("status", "").upper() == status_filter.upper()]
    table = Table(title="Demand Signal Status", border_style="yellow")
    table.add_column("Demand ID", style="cyan")
    table.add_column("Requester", style="magenta")
    table.add_column("Priority", style="red")
    table.add_column("Status", style="green")
    table.add_column("Assigned To", style="blue")
    table.add_column("Title", style="white")
    for d in demands:
        status_style = {
            "OPEN": "[yellow]OPEN[/yellow]",
            "ASSIGNED": "[blue]ASSIGNED[/blue]",
            "IN_PROGRESS": "[cyan]IN_PROGRESS[/cyan]",
            "FULFILLED": "[green]FULFILLED[/green]",
            "FAILED": "[red]FAILED[/red]",
            "EXPIRED": "[dim]EXPIRED[/dim]",
            "CLOSED": "[dim]CLOSED[/dim]",
        }.get(d.get("status", "").upper(), d.get("status", ""))
        table.add_row(
            d.get("demand_id", "?")[:24],
            d.get("requester", "?"),
            d.get("priority", "?"),
            status_style,
            d.get("assigned_to") or "—",
            d.get("title", "?")[:50],
        )
    console.print(table)
    summary = summarize_feed(demands=demands)
    console.print("\n[bold]Summary:[/bold]")
    for status, count in sorted(summary.get("demand_status_counts", {}).items()):
        console.print(f"  {status}: {count}")

@app.command(name="demand-claim")
def demand_claim(
    demand_id: str = typer.Argument(..., help="Demand ID to claim"),
    agent: str = typer.Option("roc_racoon", "--agent", "-a", help="Agent claiming the demand"),
):
    """Claim an open demand signal (OPEN → ASSIGNED)."""
    result = transition_demand(demand_id, "ASSIGNED", assigned_to=agent)
    if result is None:
        console.print(f"[red]Demand not found or invalid: {demand_id}[/red]")
        raise typer.Exit(1)
    if result.get("status") != "ASSIGNED":
        console.print(f"[yellow]Demand is not OPEN (current: {result.get('status', '?')})[/yellow]")
        return
    console.print(f"[green]✓ Demand {demand_id} claimed by {agent} (OPEN → ASSIGNED)[/green]")

@app.command(name="demand-fulfill")
def demand_fulfill(
    demand_id: str = typer.Argument(..., help="Demand ID to fulfill"),
    signal_id: str = typer.Option(..., "--signal", "-s", help="KSIG that fulfills this demand"),
):
    """Mark a demand as fulfilled (IN_PROGRESS → FULFILLED → CLOSED)."""
    result = transition_demand(demand_id, "FULFILLED", fulfilled_signal_id=signal_id)
    if result is None:
        console.print(f"[red]Demand not found: {demand_id}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ Demand {demand_id} fulfilled by signal: {signal_id}[/green]")

# ── WORKER COMMANDS ───────────────────────────────────────────────────────
@app.command()
def worker_spawn(
    task_id: str = typer.Argument(..., help="Unique identifier for the worker task"),
    model: str = typer.Argument(..., help="Target Gemma 4 model (e.g., gemma-4-31b-it)"),
    prompt: str = typer.Argument(..., help="The sensing/discovery prompt"),
    context: str = typer.Option("", "--context", "-c", help="Optional background context"),
):
    """
    Spawn a background worker for high-throughput sensing.
    [Sovereign Workhorse Protocol: pw_model_15]
    """
    async def _run():
        orchestrator = Orchestrator()
        try:
            result = await orchestrator.spawn_background_worker(
                task_id=task_id,
                model=model,
                prompt=prompt,
                context=context
            )
            console.print(f"[green]✅ {result}[/green]")
        except OmegaError as e:
            console.print(f"[red]OmegaError spawning worker: {e}[/red]")
        except (OmegaError, RuntimeError, OSError) as e:
            console.print(f"[red]Unexpected error spawning worker: {e}[/red]")
    anyio.run(_run)

# ── HARDWARE STATS ───────────────────────────────────────────────────────────
@app.command(name="hardware-stats")
def hardware_stats(
    watch: float = typer.Option(0, "--watch", "-w", help="Continuous monitoring interval in seconds (0 = one-shot)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output raw JSON"),
    oom_check: bool = typer.Option(False, "--oom", "-o", help="Quick OOM risk check only"),
):
    """📊 Show real-time hardware stats: per-core CPU, memory pressure, OOM risk, thermal.

    Uses HardwareMonitor (psutil-based with /proc fallback). Always available.

    Examples:
        omega hardware-stats              # One-shot summary
        omega hardware-stats --watch 2    # Poll every 2 seconds
        omega hardware-stats --oom        # Quick OOM risk check
        omega hardware-stats --json       # Structured JSON output
    """
    try:
        from omega.monitoring import HardwareMonitor
    except ImportError:
        console.print("[red]HardwareMonitor not available. Install: pip install psutil[/red]")
        raise typer.Exit(1)

    hm = HardwareMonitor()

    if oom_check:
        risk = hm.get_oom_risk_level()
        mem = hm.get_memory_status()
        console.print(f"[bold]OOM Risk:[/bold] [{'red' if risk in ('HIGH','CRITICAL') else 'yellow' if risk == 'MODERATE' else 'green'}]{risk}[/]")
        console.print(f"Memory: {mem['used_mb']:.0f}/{mem['total_mb']:.0f}MB ({mem['percent']:.1f}%)")
        console.print(f"Available: {mem['available_mb']:.0f}MB")
        console.print(f"Swap: {mem['swap_used_mb']:.0f}/{mem['swap_total_mb']:.0f}MB ({mem['swap_percent']:.1f}%)")
        return

    def _show():
        stats = hm.collect_all()
        if json_output:
            import json
            console.print(json.dumps(stats, indent=2, default=str))
            return

        cpu = stats["cpu"]
        mem = stats["memory"]
        temps = stats["temperatures"]
        topo = stats["topology"]

        console.print("[bold cyan]══════════════════════════════════════════[/]")
        console.print(f"[bold cyan]  OMEGA HARDWARE MONITOR[/]")
        console.print(f"[bold cyan]  {topo.get('model', '')}[/]")
        console.print("[bold cyan]══════════════════════════════════════════[/]")

        console.print(f"\n[bold]CPU:[/] {topo.get('physical_cores', '?')}C/{topo.get('logical_threads', '?')}T "
                      f"| L3: {topo.get('l3_cache_mb', '?')}MB ({topo.get('l3_instances', '?')} instances)")
        console.print(f"   Avg: {cpu['avg_percent']:.1f}%  "
                      f"Load: {cpu['load'].get('load_1min', 0):.2f}/{cpu['load'].get('load_5min', 0):.2f}/{cpu['load'].get('load_15min', 0):.2f}")

        per_core = cpu.get("per_core_percent", {})
        if per_core:
            lines = []
            for i in range(0, 16, 4):
                parts = []
                for j in range(i, min(i + 4, 16)):
                    key = f"cpu{j}"
                    val = per_core.get(key, 0)
                    # Color code: green < 50%, yellow 50-80%, red > 80%
                    color = "green" if val < 50 else "yellow" if val < 80 else "red"
                    parts.append(f"[{color}]CPU{j}:{val:5.1f}%[/]")
                lines.append("  " + "  ".join(parts))
            for line in lines:
                console.print(line)

        if cpu.get("thermal_throttling"):
            console.print("   [red]⚠ THERMAL THROTTLING ACTIVE[/red]")

        if temps.get("available") and temps["celsius"]:
            temp_parts = [f"{t['label']}: {t['temp']:.0f}°C" for t in temps["celsius"]]
            console.print(f"   Temp: {' | '.join(temp_parts)}")

        # Memory with color
        mem_pct = mem["percent"]
        mem_color = "green" if mem_pct < 60 else "yellow" if mem_pct < 80 else "red"
        console.print(f"\n[bold]Memory:[/] [{mem_color}]{mem['used_mb']:.0f}/{mem['total_mb']:.0f}MB ({mem_pct:.1f}%)[/]")
        console.print(f"   Available: {mem['available_mb']:.0f}MB"
                      f"  Swap: {mem['swap_used_mb']:.0f}/{mem['swap_total_mb']:.0f}MB ({mem['swap_percent']:.1f}%)")

        oom = mem.get("oom_risk", {})
        oom_color = "green" if oom.get("risk_level") == "SAFE" else "yellow" if oom.get("risk_level") == "LOW" else "red"
        console.print(f"   OOM Risk: [{oom_color}]{oom.get('risk_level', 'UNKNOWN')}[/]"
                      f"  Pressure: {stats.get('memory_pressure', 0):.3f}")

        thread_info = stats.get("threads", {})
        if thread_info:
            console.print(f"\n[bold]Threads:[/] Python total: {thread_info.get('total_python_threads', 0)}")

        console.print(f"\n[dim]Disk I/O: nvme0 reads: {stats.get('disk_io', {}).get('nvme0n1', {}).get('reads_completed', 0)} | "
                      f"writes: {stats.get('disk_io', {}).get('nvme0n1', {}).get('writes_completed', 0)}[/]")
        console.print("[bold cyan]══════════════════════════════════════════[/]")

    if watch > 0:
        try:
            while True:
                _show()
                import time
                time.sleep(watch)
        except KeyboardInterrupt:
            console.print("\n[dim]Stopped.[/]")
    else:
        _show()


@app.command()
def soul_stage(entity: str):
    """Sovereign Soul Staging Gate TUI.
    
    Review and approve proposed L3 principles for an entity.
    """
    from omega.cli.soul_stage import SoulStageApp
    app_tui = SoulStageApp(entity_name=entity)
    app_tui.run()


# ── Entry point ─────────────────────────────────────────────────────────


def main():
    if not TYPER_AVAILABLE:
        console.print("[red]Error: typer and rich are required. Install with: pip install typer rich[/red]")
        sys.exit(1)
    app()


if __name__ == "__main__":
    main()
