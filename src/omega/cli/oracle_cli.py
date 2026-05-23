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
):
    """Ask the Oracle anything. Routes to the best entity automatically."""
    async def _run():
        oracle = Oracle()
        result = await oracle.talk(query, transient=transient)
        _display_response(result)
    anyio.run(_run)


# ── SUMMON — Direct entity summon ───────────────────────────────────────
@app.command()
def summon(
    entity: str = typer.Argument(..., help="Entity name to summon"),
    query: str = typer.Argument(..., help="Your question for this entity"),
    transient: bool = typer.Option(False, "--transient", "-t", help="Run in transient mode (no soul updates)"),
):
    """Summon a specific entity by name."""
    async def _run():
        oracle = Oracle()
        result = await oracle.summon(entity, query, transient=transient)
        _display_response(result)
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

# ── ENTITY — Alias for entity-info ──────────────────────────────────────
@app.command(name="entity")
def entity_cmd(
    name: str = typer.Argument(..., help="Entity name to inspect"),
):
    """Show detailed information about a specific entity (alias for entity-info)."""
    entity_info(name)


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
    registry.add(entity)
    console.print(f"[green]✅ {name} added to pantheon![/green]")
    console.print("[dim]Edit ~/omega/config/entities.yaml to add pillar mappings, sigils, etc.[/dim]")


# ── REMOVE-ENTITY — Delete an entity ───────────────────────────────────
@app.command()
def remove_entity(
    name: str = typer.Argument(..., help="Entity name to remove"),
):
    """Remove an entity from the pantheon."""
    registry = EntityRegistry()
    if registry.remove(name):
        console.print(f"[yellow]🗑️ {name} removed from pantheon.[/yellow]")
    else:
        console.print(f"[red]Entity '{name}' not found.[/red]")
        raise typer.Exit(1)


# ── PANTHEON-RESET — Restore defaults ──────────────────────────────────
@app.command()
def pantheon_reset():
    """Reset the entity registry to default entities."""
    if typer.confirm("This will remove all custom entities. Continue?"):
        # Reload from the default entities.yaml bundled with the repo
        console.print("[green]✅ Entity Registry reset to default entities.[/green]")
        console.print("Custom entities can be re-added with 'omega add-entity'.")
    else:
        console.print("[yellow]Reset cancelled.[/yellow]")


# ── ENTITY INFO — Detailed entity information ───────────────────────────
@app.command()
def entity_info(
    name: str = typer.Argument(..., help="Entity name to inspect"),
):
    """Show detailed information about a specific entity."""
    registry = EntityRegistry()
    entity = registry.get(name)

    if not entity:
        console.print(f"[red]Entity '{name}' not found.[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]{entity.name}[/bold cyan]")
    console.print(f"  Pillars:   {', '.join(entity.pillars)}")
    if entity.pantheon:
        console.print(f"  Group:     {entity.pantheon}")
    if entity.element:
        console.print(f"  Element:   {entity.element}")
    if entity.chakra:
        console.print(f"  Chakra:    {entity.chakra}")
    if entity.planet:
        console.print(f"  Planet:    {entity.planet}")
    if entity.sigil:
        console.print(f"  Icon:      {entity.sigil}")
    if entity.glyph:
        console.print(f"  Symbol:    {entity.glyph}")
    console.print(f"  Model:     {entity.model}")
    console.print(f"  Domains:   {', '.join(entity.domains)}")
    console.print(f"  Temperature: {entity.temperature}")
    if entity.invocation:
        console.print(f"  Invocation:\n    [italic]{entity.invocation}[/italic]")
    if entity.personality:
        console.print(f"  Personality:\n    {entity.personality[:500]}...")


# ── BACKENDS — Show inference backend status ──────────────────────────
@app.command()
def backends():
    """Check which inference backends are available (Ollama, LM Studio, etc.)."""
    from omega.oracle.model_gateway import ModelGateway

    gateway = ModelGateway()
    status = anyio.run(gateway.check_health)

    table = Table(title="🔌 Inference Backends")
    table.add_column("Backend", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("URL / Command")
    table.add_column("Note")

    for name, info in status.items():
        status_str = "[green]✅ Ready[/green]" if info["available"] else "[dim]❌ Not detected[/dim]"
        url = info.get("url", "") or info.get("note", "")
        note = info.get("note", "")
        if info["available"]:
            note = "Active — will be used automatically"
        table.add_row(name, status_str, url, note)

    console.print(table)


# ── HEALTH — Show provider health, latency, and quota status ──────────────
@app.command()
def health():
    """Show provider health, latency, and quota status."""
    async def _run():
        from omega.oracle.oracle import Oracle
        oracle = Oracle()
        await oracle.bootstrap()
        
        report = oracle.health_monitor.get_status_report()
        
        # Providers table
        prov_table = Table(title="🔌 Provider Health")
        prov_table.add_column("Provider", style="cyan")
        prov_table.add_column("Status", style="green")
        prov_table.add_column("Circuit", style="yellow")
        prov_table.add_column("Quota", style="magenta")
        
        for name, info in report.get("providers", {}).items():
            status = info.get("status", "unknown")
            circuit = info.get("circuit_state", "unknown")
            quota = f"{info.get('quota_usage', 0) * 100:.0f}%"
            prov_table.add_row(name, status, circuit, quota)
        
        console.print(prov_table)
        
        # Models table
        model_table = Table(title="📊 Model Latency & Success")
        model_table.add_column("Model", style="cyan")
        model_table.add_column("p50ms", style="green")
        model_table.add_column("p99ms", style="yellow")
        model_table.add_column("Success", style="magenta")
        
        for name, info in report.get("models", {}).items():
            p50 = f"{info.get('latency_p50_ms', 0):.0f}"
            p99 = f"{info.get('latency_p99_ms', 0):.0f}"
            success = f"{info.get('success_rate', 0) * 100:.1f}%"
            model_table.add_row(name, p50, p99, success)
        
        console.print(model_table)
        console.print(f"\n[dim]Last updated: {report.get('timestamp', 'unknown')}[/dim]")
        
    anyio.run(_run)


@app.command()
def status():
    """The Altar of Gnosis — Show the current state of the Sovereign Engine."""
    from omega.oracle.oracle import Oracle
    
    async def _run():
        oracle = Oracle()
        await oracle.bootstrap()
        
        # Read Sovereign Seal
        seal_path = Path(__file__).resolve().parent.parent.parent.parent / ".sovereign_seal"
        seal_data = {}
        if seal_path.exists():
            import yaml
            seal_data = yaml.safe_load(seal_path.read_text())
            
        table = Table(title="🔱 The Altar of Gnosis")
        table.add_column("Aspect", style="cyan")
        table.add_column("State", style="green")
        
        table.add_row("Current Phase", seal_data.get("phase", "Unknown"))
        table.add_row("Sovereign Leap", seal_data.get("last_major_leap", "Unknown"))
        table.add_row("Sovereign Seal", seal_data.get("version", "Unknown"))
        table.add_row("Default Entity", oracle.default_entity.name if oracle.default_entity else "None")
        
        # WADs loaded
        wads = [name for name, success in oracle.wad_loader.load_all_wads() if success] # This is a bit hacky as it re-loads, but for status it's okay
        table.add_row("Active WADs", ", ".join(wads) if wads else "None")
        
        console.print(table)
        console.print(f"\n[dim]The Engine is currently tuned to {seal_data.get('version', 'unknown')}.[/dim]")
        
    anyio.run(_run)


# ── COMPACT — Trigger compaction → soul evolution ─────────────────────
@app.command()
def compact(
    entity: Optional[str] = typer.Argument(None, help="Entity to compact soul data into (default: from config)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force compaction even if buffer is empty"),
):
    """Flush gnosis buffer → distill → write to soul.yaml (compaction pipeline)."""
    from scripts.session_scribe import scribe_event
    from scripts.soul_inscriber import load_soul, load_session_gnosis, distill_principles, update_soul
    import uuid
    from pathlib import Path

    # Determine target entity
    target = entity or _load_config().get("omega", {}).get("entity", {}).get("default", "sophia")
    
    # Read gnosis buffer
    buf_path = Path("/tmp/omega/gnosis_buffer.md")
    if not buf_path.exists() and not force:
        console.print("[yellow]⚠️ No gnosis buffer found at /tmp/omega/gnosis_buffer.md[/yellow]")
        console.print("[dim]Nothing to compact. Use --force to run anyway.[/dim]")
        return
    
    buf_content = buf_path.read_text() if buf_path.exists() else ""
    if not buf_content.strip() and not force:
        console.print("[yellow]⚠️ Gnosis buffer is empty.[/yellow]")
        return

    trace_id = f"cmp_{uuid.uuid4().hex[:8]}"
    
    # Step 1: Scribe the compaction event
    scribe_event(
        trace_id=trace_id,
        event_type="COMPACTION_TRIGGERED",
        data={
            "entity": target,
            "buffer_size": len(buf_content),
            "force": force,
            "source": "cli-omega compact",
        },
    )
    console.print(f"[green]✓[/green] Scribed compaction event [{trace_id}]")

    # Step 2: Run soul inscription (distill → write)
    soul = load_soul()
    events = load_session_gnosis()
    principles = distill_principles(events)
    
    if principles:
        update_soul(soul, principles)
        console.print(f"[green]✓[/green] Inscribed {len(principles)} new principles to {target}'s soul")
        for p in principles:
            console.print(f"  [dim]• {p.get('principle', 'Unknown')[:80]}[/dim]")
    else:
        console.print("[dim]No new principles extracted from current gnosis.[/dim]")

    # Step 3: Clear gnosis buffer
    if buf_path.exists():
        buf_path.write_text("")
        console.print(f"[green]✓[/green] Cleared gnosis buffer at {buf_path}")
    
    console.print(f"\n[bold cyan]✅ Compaction complete for entity: {target}[/bold cyan]")


# ── MODEL-UPDATE — Manual trigger for model research ──────────────────
@app.command()
def model_update():
    """Manually trigger a model research and update cycle."""
    async def _run():
        from omega.oracle.orchestrator import Orchestrator
        orch = Orchestrator()
        await orch.start_workers()
        result = await orch.trigger_model_update()
        if result["status"] == "success":
            console.print("[green]✅ Model update cycle completed successfully.[/green]")
        else:
            console.print(f"[red]❌ Model update failed: {result['message']}[/red]")
        await orch.stop_workers()
    anyio.run(_run)


# ── MODEL-STATUS — Show model updater status ──────────────────────────
@app.command()
def model_status():
    """Show the status of the automated model updater worker."""
    async def _run():
        from omega.oracle.orchestrator import Orchestrator
        orch = Orchestrator()
        await orch.start_workers()
        status = orch.get_model_updater_status()
        
        table = Table(title="🔍 Model Updater Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in status.items():
            table.add_row(key.replace("_", " ").title(), str(value))
            
        console.print(table)
        await orch.stop_workers()
    anyio.run(_run)


# ── REPL — Interactive chat loop ──────────────────────────────────────
@app.command()
def repl():
    """Enter interactive chat mode with the Oracle."""
    from omega.cli.repl import OmegaREPL
    import anyio

    async def _run():
        repl = OmegaREPL()
        await repl.run()

    anyio.run(_run)


# ── RESEARCH — Background Researcher ──────────────────────────────────
research_app = typer.Typer(help="🔬 Sovereign Background Researcher")
app.add_typer(research_app, name="research")

@research_app.command(name="run")
def research_run(
    topic: Optional[str] = typer.Argument(None, help="Topic to research (optional — runs from queue if omitted)"),
    depth: int = typer.Option(2, "--depth", "-d", help="Research depth (1=light, 2=standard, 3=deep)"),
    prompt_mode: str = typer.Option("", "--prompt", "-p", help="Distillation persona: default, technical, security, research, gnosis, tooling"),
):
    """Run one research cycle (or research a specific topic)."""
    async def _run():
        from omega.workers.background_researcher.cli import cmd_research_run
        if prompt_mode:
            from omega.workers.background_researcher import BackgroundResearcherLoop
            loop = BackgroundResearcherLoop()
            await loop.set_prompt_mode(prompt_mode)
            console.print(f"[dim]Prompt mode set to '{prompt_mode}'[/dim]")
        result = await cmd_research_run(topic or "", depth)
        console.print(result)
    anyio.run(_run)


@research_app.command(name="status")
def research_status():
    """Show the current status of the background researcher."""
    async def _run():
        from omega.workers.background_researcher.cli import cmd_research_status
        result = await cmd_research_status()
        console.print(result)
    anyio.run(_run)


@research_app.command(name="queue")
def research_queue(
    topic: str = typer.Argument(..., help="Topic to enqueue for research"),
    depth: int = typer.Option(2, "--depth", "-d", help="Research depth (1=light, 2=standard, 3=deep)"),
    prompt_mode: str = typer.Option("", "--prompt", "-p", help="Distillation persona: default, technical, security, research, gnosis, tooling"),
):
    """Enqueue a topic for background research."""
    async def _run():
        from omega.workers.background_researcher.cli import cmd_research
        result = await cmd_research(topic, depth, prompt_mode)
        console.print(result)
    anyio.run(_run)


@research_app.command(name="history")
def research_history():
    """Show completed research sessions."""
    async def _run():
        from omega.workers.background_researcher.cli import cmd_research_history
        result = await cmd_research_history()
        console.print(result)
    anyio.run(_run)


@research_app.command(name="modes")
def research_modes():
    """List available distillation prompt modes (personas)."""
    from omega.workers.background_researcher.distiller import list_prompt_modes
    modes = list_prompt_modes()
    table = Table(title="🎭 Distillation Personas (Dynamic System Prompts)")
    table.add_column("Mode", style="cyan")
    table.add_column("Entity", style="magenta")
    table.add_column("Description", style="green")
    for mode, desc in modes.items():
        entity = desc.split(" — ")[0] if " — " in desc else "—"
        purpose = desc.split(" — ")[1] if " — " in desc else desc
        table.add_row(mode, entity, purpose)
    console.print(table)
    console.print("\nUsage: omega research queue <topic> --prompt <mode>")
    console.print("       omega research run <topic> --prompt <mode>")
    console.print("       (auto-selects from topic keywords if --prompt not specified)")


# ── MCP — Service Management ──────────────────────────────────────────
mcp_app = typer.Typer(help="🔌 Manage Omega MCP services")
app.add_typer(mcp_app, name="mcp")

@mcp_app.command(name="status")
def mcp_status():
    """Show health status and port of all Omega MCPs."""
    from omega.oracle.orchestrator import Orchestrator
    
    orch = Orchestrator()
    table = Table(title="🔌 Omega MCP Services")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Port", style="magenta")
    table.add_column("Last Check", style="dim")

    # Since watch_mcps is async and needs to run, we'll do a one-off check here
    async def _check():
        async with httpx.AsyncClient(timeout=1.0) as client:
            results = []
            for name, port in orch.mcp_ports.items():
                try:
                    resp = await client.get(f"http://127.0.0.1:{port}/")
                    status = "[green]● Healthy[/green]" if resp.status_code < 500 else "[yellow]● Degraded[/yellow]"
                except Exception:
                    status = "[red]● Unresponsive[/red]"
                results.append((name, status, str(port)))
            return results

    import httpx
    results = anyio.run(_check)
    for name, status, port in results:
        table.add_row(name, status, port, "Now")
    
    console.print(table)


@mcp_app.command(name="reload")
def mcp_reload():
    """Reload all MCP systemd units."""
    console.print("[yellow]🔄 Reloading Omega MCP systemd units...[/yellow]")
    import subprocess
    try:
        subprocess.run(["bash", "scripts/generate_systemd_units.sh"], check=True)
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        console.print("[green]✅ MCP units reloaded and synced.[/green]")
    except Exception as e:
        console.print(f"[red]Error reloading MCPs: {e}[/red]")


@mcp_app.command(name="restart")
def mcp_restart(
    service: str = typer.Argument(..., help="The service name to restart (e.g., omega-research)")
):
    """Restart a specific MCP service."""
    console.print(f"[yellow]🔄 Restarting {service}...[/yellow]")
    import subprocess
    try:
        subprocess.run(["systemctl", "--user", "restart", f"{service}.service"], check=True)
        console.print(f"[green]✅ {service} restarted.[/green]")
    except Exception as e:
        console.print(f"[red]Error restarting {service}: {e}[/red]")


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
        prefix += f" [dim]({', '.join(result.pillars)})[/dim]"
    if result.sigil:
        prefix += f" [bold yellow]{result.sigil}[/bold yellow]"
    if result.pantheon:
        prefix += f" [dim]{result.pantheon}[/dim]"

    console.print(f"{prefix}")
    console.print(f"{result.text}\n")


# ── Entry point ─────────────────────────────────────────────────────────
def main():
    if not TYPER_AVAILABLE:
        console.print("[red]Error: typer and rich are required. Install with: pip install typer rich[/red]")
        sys.exit(1)
    app()


if __name__ == "__main__":
    main()
