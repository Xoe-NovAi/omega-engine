# 🔱 Omega Engine — Link P9 CLI Commands
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ deepseek-v4-flash ⬡ opencode ⬡ LINK-P9-CLI
# AP: LINK-P9-CLI-v1.0.0
#
# CLI commands for agent handoff and delegation.
# Standalone module — integrates into oracle_cli.py after Ma'at finishes Phase 1.
#
# [id-soft: doom3-2004] idEntity event system — CLI commands for event dispatch
# [id-soft: doom-1993] ZONEID Pattern — presence integrity checks

import json
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from omega.oracle.link_p9_runtime import LinkP9Runtime, AgentPresence
from omega.oracle.subagent_dispatcher import (
    HandoffPacket,
    CAPABILITY_REGISTRY,
    dispatch,
    get_agent_capabilities,
    list_available_agents,
)

app = typer.Typer(help="Link P9 — Agent Handoff & Delegation")
console = Console()

# ── Runtime singleton ────────────────────────────────────────────────────

_runtime: Optional[LinkP9Runtime] = None


def _get_runtime() -> LinkP9Runtime:
    global _runtime
    if _runtime is None:
        _runtime = LinkP9Runtime()
        _runtime.load_state()
    return _runtime


# ── Presence Commands ────────────────────────────────────────────────────


@app.command("heartbeat")
def heartbeat_cmd(
    agent: str = typer.Argument(..., help="Agent name"),
    session_id: str = typer.Option(None, "--session", "-s", help="Session ID"),
    ttl: float = typer.Option(300.0, "--ttl", "-t", help="TTL in seconds"),
):
    """Register or refresh agent presence."""
    runtime = _get_runtime()
    presence = runtime.heartbeat(agent, session_id=session_id, ttl_seconds=ttl)
    runtime.save_state()
    console.print(f"[green]Heartbeat registered:[/green] {agent}")
    console.print(f"  Status: {presence.status}")
    console.print(f"  TTL: {presence.ttl_seconds}s")
    if presence.session_id:
        console.print(f"  Session: {presence.session_id}")


@app.command("agents")
def agents_cmd(
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all agents including dead"),
):
    """List active agents and their status."""
    runtime = _get_runtime()
    runtime.check_timeouts()

    if show_all:
        agents = runtime.list_all()
    else:
        agents = runtime.list_active()

    if not agents:
        console.print("[yellow]No active agents.[/yellow]")
        return

    table = Table(title="Agent Presence")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Last Seen", style="dim")
    table.add_column("Current Task", style="white")
    table.add_column("Session", style="dim")

    for p in agents:
        age = time.time() - p.last_heartbeat
        if age < 60:
            last_seen = f"{age:.0f}s ago"
        elif age < 3600:
            last_seen = f"{age/60:.0f}m ago"
        else:
            last_seen = f"{age/3600:.1f}h ago"

        status_style = {
            "active": "[green]ACTIVE[/green]",
            "idle": "[yellow]IDLE[/yellow]",
            "stale": "[red]STALE[/red]",
            "dead": "[red dim]DEAD[/red dim]",
        }.get(p.status, p.status)

        table.add_row(
            p.agent_name,
            status_style,
            last_seen,
            p.current_task or "—",
            p.session_id or "—",
        )

    console.print(table)


@app.command("prune")
def prune_cmd():
    """Remove dead agents from presence tracking."""
    runtime = _get_runtime()
    pruned = runtime.prune_dead()
    runtime.save_state()
    if pruned:
        console.print(f"[yellow]Pruned {len(pruned)} dead agents:[/yellow] {', '.join(pruned)}")
    else:
        console.print("[green]No dead agents to prune.[/green]")


# ── Dispatch Commands ────────────────────────────────────────────────────


@app.command("dispatch")
def dispatch_cmd(
    source: str = typer.Argument(..., help="Source agent"),
    target: str = typer.Argument(..., help="Target agent"),
    task_type: str = typer.Argument(..., help="Task type: design|review|research|mine|verify|implement"),
    description: str = typer.Option(..., "--description", "-d", help="Task description"),
    files: str = typer.Option("", "--files", "-f", help="Comma-separated relevant files"),
    context: str = typer.Option("", "--context", "-c", help="Background context"),
    expected: str = typer.Option("", "--expected", "-e", help="Expected output"),
    ttl: int = typer.Option(600, "--ttl", help="TTL in seconds"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show prompt without sending"),
):
    """Dispatch a subagent task."""
    runtime = _get_runtime()

    # Validate agents exist
    if not get_agent_capabilities(source):
        console.print(f"[red]Unknown source agent:[/red] {source}")
        raise typer.Exit(1)
    if not get_agent_capabilities(target):
        console.print(f"[red]Unknown target agent:[/red] {target}")
        raise typer.Exit(1)

    # Build packet
    packet = HandoffPacket(
        source_agent=source,
        target_agent=target,
        task_type=task_type,  # type: ignore
        task_description=description,
        relevant_files=[f.strip() for f in files.split(",") if f.strip()],
        context=context,
        expected_output=expected,
        ttl_seconds=ttl,
    )

    if dry_run:
        prompt = dispatch(packet)
        console.print(Panel(prompt, title="Generated Prompt (dry run)", border_style="yellow"))
        return

    # Send packet
    runtime.send(packet)
    runtime.save_state()

    console.print(f"[green]Packet dispatched:[/green] {packet.packet_id}")
    console.print(f"  Source: {source} → Target: {target}")
    console.print(f"  Task: {task_type} — {description[:60]}...")
    console.print(f"\n[dim]To launch, use Task tool with:[/dim]")
    console.print(f"  subagent_type: {CAPABILITY_REGISTRY[target]['task_tool_type']}")
    console.print(f"  prompt: dispatch(packet)")


@app.command("inbox")
def inbox_cmd(
    agent: str = typer.Argument(..., help="Agent name to check inbox for"),
):
    """Check pending handoff packets for an agent."""
    runtime = _get_runtime()
    packets = runtime.receive(agent)

    if not packets:
        console.print(f"[dim]No pending packets for {agent}.[/dim]")
        return

    for p in packets:
        console.print(Panel(
            f"[cyan]From:[/cyan] {p.source_agent}\n"
            f"[cyan]Task:[/cyan] {p.task_type} — {p.task_description}\n"
            f"[cyan]Context:[/cyan] {p.context[:200]}...\n"
            f"[cyan]Expected:[/cyan] {p.expected_output[:200]}...\n"
            f"[cyan]TTL:[/cyan] {p.ttl_seconds}s\n"
            f"[cyan]Packet:[/cyan] {p.packet_id}",
            title=f"Handoff from {p.source_agent}",
            border_style="green",
        ))


@app.command("complete")
def complete_cmd(
    packet_id: str = typer.Argument(..., help="Packet ID to mark complete"),
    result: str = typer.Option(..., "--result", "-r", help="Result text"),
):
    """Mark a handoff packet as completed."""
    runtime = _get_runtime()
    packet = runtime.complete(packet_id, result)
    if packet:
        console.print(f"[green]Packet completed:[/green] {packet_id}")
    else:
        console.print(f"[red]Packet not found:[/red] {packet_id}")
    runtime.save_state()


@app.command("fail")
def fail_cmd(
    packet_id: str = typer.Argument(..., help="Packet ID to mark failed"),
    error: str = typer.Option(..., "--error", "-r", help="Error text"),
):
    """Mark a handoff packet as failed."""
    runtime = _get_runtime()
    packet = runtime.fail(packet_id, error)
    if packet:
        console.print(f"[red]Packet failed:[/red] {packet_id}")
    else:
        console.print(f"[red]Packet not found:[/red] {packet_id}")
    runtime.save_state()


@app.command("status")
def status_cmd():
    """Show Link P9 runtime status."""
    runtime = _get_runtime()
    stats = runtime.archive_stats()
    log = runtime.get_dispatch_log(10)

    console.print(Panel(
        f"[cyan]Active:[/cyan] {stats.get('active', 0)} agents\n"
        f"[cyan]Pending:[/cyan] {stats.get('pending', 0)} packets\n"
        f"[cyan]Accepted:[/cyan] {stats.get('accepted', 0)} packets\n"
        f"[cyan]Completed:[/cyan] {stats.get('completed', 0)} packets\n"
        f"[cyan]Failed:[/cyan] {stats.get('failed', 0)} packets\n"
        f"[cyan]Timed out:[/cyan] {stats.get('timed_out', 0)} packets",
        title="Link P9 Status",
        border_style="cyan",
    ))

    if log:
        console.print("\n[bold]Recent Dispatch Log:[/bold]")
        for entry in log[-5:]:
            console.print(
                f"  {entry['action']:>10} | {entry.get('packet_id', '—')[:20]} | "
                f"{entry.get('source', '')}{('→' + entry.get('target', '')) if entry.get('target') else ''}"
            )


@app.command("registry")
def registry_cmd():
    """Show the Agent Capability Registry."""
    table = Table(title="Agent Capability Registry")
    table.add_column("Agent", style="cyan")
    table.add_column("Mode", style="dim")
    table.add_column("Purpose", style="white")
    table.add_column("Capabilities", style="green")
    table.add_column("Task Type", style="yellow")

    for name, desc in CAPABILITY_REGISTRY.items():
        caps = ", ".join(desc["capabilities"][:3])
        if len(desc["capabilities"]) > 3:
            caps += f" (+{len(desc['capabilities'])-3})"
        table.add_row(
            name,
            desc["mode"],
            desc["purpose"][:50],
            caps,
            desc["task_tool_type"],
        )

    console.print(table)


@app.command("archive")
def archive_cmd(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries to show"),
):
    """Show archived handoff packets."""
    archive_dir = Path("data/handoff/archive")
    if not archive_dir.exists():
        console.print("[dim]No archive directory found.[/dim]")
        return

    json_files = sorted(archive_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not json_files:
        console.print("[dim]No archived packets.[/dim]")
        return

    table = Table(title="Archived Handoff Packets")
    table.add_column("Packet ID", style="cyan")
    table.add_column("Source → Target", style="white")
    table.add_column("Task Type", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Created", style="dim")

    for f in json_files[:limit]:
        try:
            data = json.loads(f.read_text())
            status_style = {
                "completed": "[green]completed[/green]",
                "failed": "[red]failed[/red]",
                "timed_out": "[yellow]timed_out[/yellow]",
            }.get(data.get("status", ""), data.get("status", ""))
            table.add_row(
                data.get("packet_id", "—")[:30],
                f"{data.get('source_agent', '?')} → {data.get('target_agent', '?')}",
                data.get("task_type", "—"),
                status_style,
                data.get("created_at", "—"),
            )
        except Exception:
            continue

    console.print(table)


if __name__ == "__main__":
    app()
