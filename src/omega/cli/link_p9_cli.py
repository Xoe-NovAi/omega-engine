# 🔱 Omega Engine — Link P9 CLI Commands
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ deepseek-v4-flash ⬡ opencode ⬡ LINK-P9-CLI
# AP: LINK-P9-CLI-v1.0.0
#
# CLI commands for agent handoff and delegation, plus cross-pollination
# protocol commands (check-feed, consume, demand-status).
#
# Standalone module — integrates into oracle_cli.py after Ma'at finishes Phase 1.
#
# [id-soft: doom3-2004] idEntity event system — CLI commands for event dispatch
# [id-soft: doom-1993] ZONEID Pattern — presence integrity checks
# [id-soft: doom-1993] ZONEID Pattern — knowledge signal validation (ZONEID_KNOWLEDGE)

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)

from omega.oracle.link_p9_runtime import LinkP9Runtime, AgentPresence
from omega.oracle.subagent_dispatcher import (
    HandoffPacket,
    CAPABILITY_REGISTRY,
    dispatch,
    get_agent_capabilities,
    list_available_agents,
)
from omega.oracle.feed_utils import (
    KNOWLEDGE_FEED_DIR,
    DEMAND_SIGNALS_DIR,
    CROSS_REF_DIR,
    load_knowledge_signals,
    load_demand_signals,
    find_new_signals,
    find_open_demands,
    consume_signal,
    write_knowledge_signal,
    write_cross_reference,
    transition_demand,
    summarize_feed,
)

app = typer.Typer(help="Link P9 — Agent Handoff, Delegation & Cross-Pollination")
console = Console()

# ── Runtime singleton ────────────────────────────────────────────────────

_runtime: Optional[LinkP9Runtime] = None


def _get_runtime() -> LinkP9Runtime:
    global _runtime
    if _runtime is None:
        _runtime = LinkP9Runtime()
        _runtime.load_state()
    return _runtime


# ── Cross-Pollination summary helper ─────────────────────────────────────


def _print_producer_summary() -> None:
    """Print a summary of knowledge feed producers."""
    signals = load_knowledge_signals()
    producers: dict = {}
    for sig in signals:
        p = sig.get("producer", "unknown")
        producers[p] = producers.get(p, 0) + 1
    if producers:
        console.print("\n[bold]Knowledge Feed Producers:[/bold]")
        for p, count in sorted(producers.items()):
            console.print(f"  {p}: {count} signal(s)")


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
        except Exception as e:
            logger.warning("Skipping malformed handoff record: %s", e)
            continue

    console.print(table)


# ── Cross-Pollination Commands ───────────────────────────────────────────
# [id-soft: doom-1993] ZONEID Pattern — knowledge signal validation


@app.command("check-feed")
def check_feed_cmd(
    agent: str = typer.Option("link", "--agent", "-a", help="Agent name to check feed for"),
    consume: bool = typer.Option(False, "--consume", "-c", help="Mark unconsumed signals as consumed"),
):
    """Check knowledge feed and demand signals for unconsumed content."""
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
                console.print(f"  [green]✓[/green] Consumed: {sig['signal_id'][:32]} — {sig.get('title', '?')[:50]}")
            console.print(f"[green]Consumed {len(unconsumed)} new signals for {agent}.[/green]")
    else:
        console.print(f"[dim]No new knowledge signals for {agent}.[/dim]")

    consumed_count = summary["total_signals"] - len(unconsumed)
    console.print(f"  KSIGs: {summary['total_signals']} ({consumed_count} consumed, {len(unconsumed)} new)")
    console.print(f"  DEMs: {summary['total_demands']} ({summary['open_demands']} open)\n")
    _print_producer_summary()


@app.command("consume")
def consume_cmd(
    signal_id: str = typer.Argument(..., help="Signal ID to consume"),
    agent: str = typer.Option("link", "--agent", "-a", help="Agent consuming the signal"),
):
    """Manually mark a knowledge signal as consumed by an agent."""
    signals = load_knowledge_signals()
    target = None
    for sig in signals:
        if signal_id in sig.get("signal_id", ""):
            target = sig
            break

    if target is None:
        console.print(f"[red]Signal not found: {signal_id}[/red]")
        raise typer.Exit(1)

    if agent in target.get("consumed_by", []):
        console.print(f"[yellow]Already consumed by {agent}.[/yellow]")
        return

    consume_signal(target, agent)
    write_knowledge_signal(target)
    write_cross_reference(agent, target)
    console.print(f"[green]✓ {agent} consumed {target['signal_id']}: {target.get('title', '')}[/green]")


@app.command("demand-status")
def demand_status_cmd(
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
        }.get(d.get("status", ""), d.get("status", ""))
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


@app.command("demand-claim")
def demand_claim_cmd(
    demand_id: str = typer.Argument(..., help="Demand ID to claim"),
    agent: str = typer.Option("link", "--agent", "-a", help="Agent claiming the demand"),
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


@app.command("demand-fullfill")
def demand_fullfill_cmd(
    demand_id: str = typer.Argument(..., help="Demand ID to fulfill"),
    signal_id: str = typer.Option(..., "--signal", "-s", help="KSIG that fulfills this demand"),
):
    """Mark a demand as fulfilled (IN_PROGRESS → FULFILLED → CLOSED)."""
    result = transition_demand(demand_id, "FULFILLED", fulfilled_signal_id=signal_id)
    if result is None:
        console.print(f"[red]Demand not found: {demand_id}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ Demand {demand_id} fulfilled by signal: {signal_id}[/green]")


if __name__ == "__main__":
    app()
