"""Wander CLI — Zero-polling GitHub Actions monitor with mandatory agent auto-trigger."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .watch import watch
from .config import load_config, Config

console = Console()


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Config file path",
)
@click.option(
    "--repo",
    "-r",
    multiple=True,
    help="Repository to watch (owner/repo). Can specify multiple.",
)
@click.option(
    "--token",
    "-t",
    envvar="GITHUB_TOKEN",
    help="GitHub token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--notify/--no-notify",
    default=True,
    help="Enable macOS notifications",
)
@click.option(
    "--agent-trigger/--no-agent-trigger",
    default=True,
    help="Auto-trigger agent on CI events",
)
@click.option(
    "--daemon/--foreground",
    default=False,
    help="Run as background daemon",
)
@click.pass_context
def cli(
    ctx: click.Context,
    config: Path | None,
    repo: tuple[str, ...],
    token: str | None,
    notify: bool,
    agent_trigger: bool,
    daemon: bool,
) -> None:
    """Wander — Zero-polling GitHub Actions monitor with mandatory agent auto-trigger."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["repos"] = list(repo)
    ctx.obj["token"] = token
    ctx.obj["notify"] = notify
    ctx.obj["agent_trigger"] = agent_trigger
    ctx.obj["daemon"] = daemon


@cli.command()
@click.pass_context
def watch_cmd(ctx: click.Context) -> None:
    """Watch GitHub Actions for configured repositories."""
    config = load_config(ctx.obj["config_path"])
    
    # CLI args override config
    repos = ctx.obj["repos"] or config.repos
    token = ctx.obj["token"] or config.token or os.environ.get("GITHUB_TOKEN")
    notify = ctx.obj["notify"]
    agent_trigger = ctx.obj["agent_trigger"]
    daemon = ctx.obj["daemon"]
    
    if not repos:
        console.print("[red]Error:[/red] No repositories specified. Use --repo or config file.")
        sys.exit(1)
    
    if not token:
        console.print("[red]Error:[/red] GitHub token required. Set GITHUB_TOKEN or use --token.")
        sys.exit(1)
    
    watch(
        repos=repos,
        token=token,
        notify=notify,
        agent_trigger=agent_trigger,
        daemon=daemon,
    )


@cli.command()
@click.option("--repo", "-r", multiple=True, help="Repository to check (owner/repo)")
@click.pass_context
def status(ctx: click.Context, repo: tuple[str, ...]) -> None:
    """Show current workflow run status for repositories."""
    config = load_config(ctx.obj["config_path"])
    repos = ctx.obj["repos"] or config.repos
    token = ctx.obj["token"] or config.token or os.environ.get("GITHUB_TOKEN")
    
    if not repos:
        console.print("[red]Error:[/red] No repositories specified.")
        sys.exit(1)
    
    if not token:
        console.print("[red]Error:[/red] GitHub token required.")
        sys.exit(1)
    
    # Quick status check - just show latest run
    from .github import GitHubClient
    import asyncio
    
    async def check_status():
        async with GitHubClient(token) as client:
            for repo_name in repos:
                runs = await client.get_workflow_runs(repo_name, per_page=5)
                if runs:
                    latest = runs[0]
                    status_text = latest.get("conclusion") or latest.get("status") or "unknown"
                    color = "green" if status_text == "success" else "red" if status_text == "failure" else "yellow"
                    console.print(f"[bold]{repo_name}[/bold]: [{color}]{status_text}[/{color}] - {latest.get('display_title', 'N/A')}")
                else:
                    console.print(f"[bold]{repo_name}[/bold]: [dim]no runs[/dim]")
    
    asyncio.run(check_status())


@cli.command()
@click.pass_context
def config_cmd(ctx: click.Context) -> None:
    """Show current configuration."""
    config = load_config(ctx.obj["config_path"])
    
    table = Table(title="Wander Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Repos", ", ".join(config.repos) if config.repos else "(none)")
    table.add_row("Token", "***" if config.token else "(from env)")
    table.add_row("Notify", str(config.notify))
    table.add_row("Agent Trigger", str(config.agent_trigger))
    table.add_row("Config File", str(ctx.obj["config_path"]) if ctx.obj["config_path"] else "(auto-detected)")
    
    console.print(table)


def main() -> None:
    cli(obj={})


if __name__ == "__main__":
    main()