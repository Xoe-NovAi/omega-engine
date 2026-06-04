# 🔱 Omega CLI — Oracle Commands
# AP: AP-ORACLE-CLI-v1.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: CLI-COMMANDS]

import anyio
import logging
import sys
from pathlib import Path
from typing import Optional

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

from omega.oracle import Oracle, OracleResponse, EntityRegistry, Entity
from omega.request_queue import RequestQueue
from omega.oracle.feed_utils import load_demand_signals, transition_demand, summarize_feed

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="🔱 Omega — The Reclaimed Vision. Single intelligence. Infinite faces.")


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
    iwad: Optional[str] = typer.Option(None, "--iwad", "-w", help="IWAD stack to load (e.g., arcana_novai)"),
):
    """Ask the Oracle anything. Routes to the best entity automatically."""
    async def _run():
        oracle = Oracle(iwad_name=iwad)
        try:
            result = await oracle.talk(query, transient=transient)
            _display_response(result)
        finally:
            await oracle.close()
    anyio.run(_run)


# ── SUMMON — Direct entity summon ───────────────────────────────────────
@app.command()
def summon(
    entity: str = typer.Argument(..., help="Entity name to summon"),
    query: str = typer.Argument(..., help="Your question for this entity"),
    transient: bool = typer.Option(False, "--transient", "-t", help="Run in transient mode (no soul updates)"),
    iwad: Optional[str] = typer.Option(None, "--iwad", "-w", help="IWAD stack to load (e.g., arcana_novai)"),
):
    """Summon a specific entity by name."""
    async def _run():
        oracle = Oracle(iwad_name=iwad)
        try:
            result = await oracle.summon(entity, query, transient=transient)
            _display_response(result)
        finally:
            await oracle.close()
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
    table.add_row("Pillars", ", ".join(entity.pillars) if entity.pillars else "—")
    table.add_row("Pantheon", entity.pantheon or "—")
    table.add_row("Sigil", entity.sigil or "—")
    table.add_row("Domains", ", ".join(entity.domains) if entity.domains else "—")
    table.add_row("Model", entity.model or "—")
    table.add_row("Temperature", str(entity.temperature))
    table.add_row("Container", str(entity.container) if entity.container else "—")
    if entity.personality:
        personality_preview = entity.personality[:200] + ("..." if len(entity.personality) > 200 else "")
        table.add_row("Personality", personality_preview)

    console.print(table)


# ── TRANSIENT — Toggle transient mode ──────────────────────────────────
@app.command()
def transient(
    mode: Optional[str] = typer.Argument(None, help="Set transient mode (on/off)"),
):
    """Get or set the default transient mode."""
    config = _load_config()
    if mode is None:
        current = config.get("omega", {}).get("entity", {}).get("allow_transient", True)
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
        current = config.get("omega", {}).get("session_header", {}).get("mode", "compact")
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
    table.add_column("Pillar", style="magenta")
    table.add_column("Pantheon", style="green")
    table.add_column("Sigil", style="yellow")
    table.add_column("Model", style="blue")
    table.add_column("Temperature")

    for entity in registry.list():
        if entity.container:
            # Nova gets special display
                table.add_row(
                    entity.name,
                    "Voice Interface",
                    entity.pantheon or "Greek",
                    "—",
                    entity.model,
                    str(entity.temperature),
                )
        else:
            table.add_row(
                entity.name,
                ", ".join(entity.pillars) if entity.pillars else "—",
                entity.pantheon or "—",
                entity.sigil or "—",
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
        except Exception as e:
            console.print(f"[red]Error restarting {service}: {e}[/red]")
    anyio.run(_run)



# ── Display helper ─────────────────────────────────────────────────────
def _display_response(result: OracleResponse):
    """Format and display an Oracle response."""
    config = _load_config()
    header_mode = config.get("omega", {}).get("session_header", {}).get("mode", "compact")

    if header_mode != "off":
        if header_mode == "full":
            # ⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}
            trace = result.trace_id[:8] if result.trace_id else "unknown"
            header = f"⬡ OMEGA ⬡ {result.entity.upper()} ⬡ {result.model or 'unknown'} ⬡ cli ⬡ {trace} ⬡ {result.phase}"
        else:  # compact
            # ⬡ {entity} ⬡ {phase}
            header = f"⬡ {result.entity.upper()} ⬡ {result.phase}"
        
        console.print(f"[dim]{header}[/dim]")

    prefix = f"[bold cyan]{result.entity}[/bold cyan]"
    if result.pillars:
        prefix += f" [dim]({', '.join(str(p) for p in result.pillars)})[/dim]"
    if result.sigil:
        prefix += f" [bold yellow]{result.sigil}[/bold yellow]"
    if result.pantheon:
        prefix += f" [dim]{result.pantheon}[/dim]"

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

# ── Entry point ─────────────────────────────────────────────────────────

def main():
    if not TYPER_AVAILABLE:
        console.print("[red]Error: typer and rich are required. Install with: pip install typer rich[/red]")
        sys.exit(1)
    app()


if __name__ == "__main__":
    main()
