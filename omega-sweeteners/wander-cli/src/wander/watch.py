"""Watch command — core monitoring logic for GitHub Actions."""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

from .github import GitHubClient
from .agent_trigger import trigger_agent

console = Console()


class WorkflowMonitor:
    """Monitors GitHub Actions workflow runs for specified repositories."""
    
    def __init__(
        self,
        repos: list[str],
        token: str,
        notify: bool = True,
        agent_trigger: bool = True,
        poll_interval: int = 30,
    ):
        self.repos = repos
        self.token = token
        self.notify = notify
        self.agent_trigger = agent_trigger
        self.poll_interval = poll_interval
        self.seen_runs: dict[str, set[int]] = {repo: set() for repo in repos}
        self.running = True
        self._setup_signals()
    
    def _setup_signals(self) -> None:
        """Handle graceful shutdown."""
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._shutdown)
    
    def _shutdown(self, signum, frame) -> None:
        console.print("\n[yellow]Shutting down...[/yellow]")
        self.running = False
    
    async def check_repo(self, client: GitHubClient, repo: str) -> list[dict]:
        """Check for new workflow runs in a repository."""
        try:
            runs = await client.get_workflow_runs(repo, per_page=10)
            new_runs = []
            for run in runs:
                run_id = run["id"]
                if run_id not in self.seen_runs[repo]:
                    self.seen_runs[repo].add(run_id)
                    new_runs.append(run)
            return new_runs
        except Exception as e:
            console.print(f"[red]Error checking {repo}:[/red] {e}")
            return []
    
    def send_notification(self, title: str, message: str) -> None:
        """Send macOS notification."""
        if not self.notify or sys.platform != "darwin":
            return
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
        except Exception:
            pass
    
    async def process_new_runs(self, client: GitHubClient, new_runs: list[dict]) -> None:
        """Process newly detected workflow runs."""
        for run in new_runs:
            repo = run["repository"]["full_name"]
            run_id = run["id"]
            conclusion = run.get("conclusion") or run.get("status") or "unknown"
            workflow_name = run.get("name", "Unknown workflow")
            branch = run.get("head_branch", "unknown")
            actor = run.get("actor", {}).get("login", "unknown")
            html_url = run.get("html_url", "")
            
            # Status emoji
            status_emoji = {
                "success": "✅",
                "failure": "❌",
                "cancelled": "⏹️",
                "in_progress": "🔄",
                "queued": "⏳",
            }.get(conclusion, "❓")
            
            # Console output
            color = "green" if conclusion == "success" else "red" if conclusion == "failure" else "yellow"
            console.print(
                f"{status_emoji} [{color}]{conclusion}[/{color}] "
                f"[bold]{repo}[/bold] | {workflow_name} | {branch} | @{actor}"
            )
            
            # Notification
            self.send_notification(
                f"GitHub Actions: {workflow_name}",
                f"{repo}@{branch}: {conclusion} ({actor})"
            )
            
            # Agent trigger
            if self.agent_trigger and conclusion in ("failure", "success"):
                await self._trigger_agent(
                    repo=repo,
                    run_id=run_id,
                    conclusion=conclusion,
                    workflow_name=workflow_name,
                    branch=branch,
                    actor=actor,
                    html_url=html_url,
                )
    
    async def _trigger_agent(
        self,
        repo: str,
        run_id: int,
        conclusion: str,
        workflow_name: str,
        branch: str,
        actor: str,
        html_url: str,
    ) -> None:
        """Trigger agent with CI context."""
        try:
            await trigger_agent(
                repo=repo,
                run_id=run_id,
                conclusion=conclusion,
                workflow_name=workflow_name,
                branch=branch,
                actor=actor,
                html_url=html_url,
            )
        except Exception as e:
            console.print(f"[red]Agent trigger failed:[/red] {e}")
    
    async def run(self) -> None:
        """Main monitoring loop."""
        async with GitHubClient(self.token) as client:
            # Initialize seen runs
            console.print(f"[cyan]Initializing...[/cyan]")
            for repo in self.repos:
                runs = await client.get_workflow_runs(repo, per_page=5)
                self.seen_repos[repo] = {run["id"] for run in runs}
            
            console.print(f"[green]Monitoring {len(self.repos)} repo(s) every {self.poll_interval}s[/green]")
            console.print("Press Ctrl+C to stop\n")
            
            while self.running:
                for repo in self.repos:
                    if not self.running:
                        break
                    new_runs = await self.check_repo(client, repo)
                    if new_runs:
                        await self.process_new_runs(client, new_runs)
                
                if self.running:
                    await asyncio.sleep(self.poll_interval)
    
    async def run_once(self) -> None:
        """Single check cycle (for testing/daemon)."""
        async with GitHubClient(self.token) as client:
            for repo in self.repos:
                new_runs = await self.check_repo(client, repo)
                if new_runs:
                    await self.process_new_runs(client, new_runs)


def watch(
    repos: list[str],
    token: str,
    notify: bool = True,
    agent_trigger: bool = True,
    daemon: bool = False,
) -> None:
    """Main watch entry point."""
    
    async def _run():
        monitor = WorkflowMonitor(
            repos=repos,
            token=token,
            notify=notify,
            agent_trigger=agent_trigger,
        )
        
        if daemon:
            # Run in background
            console.print("[yellow]Daemon mode not fully implemented — running foreground[/yellow]")
        
        await monitor.run()
    
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {e}")
        sys.exit(1)