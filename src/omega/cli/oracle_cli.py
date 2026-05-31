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


# ── Entry point ─────────────────────────────────────────────────────────
def main():
    if not TYPER_AVAILABLE:
        console.print("[red]Error: typer and rich are required. Install with: pip install typer rich[/red]")
        sys.exit(1)
    app()


if __name__ == "__main__":
    main()
