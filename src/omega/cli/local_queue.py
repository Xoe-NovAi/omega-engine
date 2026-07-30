# AP: AP-LOCAL-QUEUE-CLI-v1.0.0
# 🔱 Local Queue CLI — Fire-and-Forget Local Inference Management
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ trc_local_worker ⬡ CLI

import typer
import json
import anyio
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from datetime import datetime

from omega.observability import DATA_DIR
from omega.oracle.local_worker_pool import (
    queue_local_task,
    get_local_task_status,
    get_local_task_result,
    list_local_tasks,
    TaskStatus,
)

app = typer.Typer(
    name="local-queue",
    help="Fire-and-forget local inference queue management",
    no_args_is_help=True,
)

console = Console()


@app.command("queue")
def queue_task(
    prompt: str = typer.Argument(..., help="Prompt for local inference"),
    model: str = typer.Option("qwen3-1.7b", "--model", "-m", help="Model to use"),
    system: str = typer.Option("", "--system", "-s", help="System prompt"),
    max_tokens: int = typer.Option(1024, "--max-tokens", "-t", help="Max tokens to generate"),
    temperature: float = typer.Option(0.7, "--temperature", help="Sampling temperature"),
    top_p: float = typer.Option(0.95, "--top-p", help="Top-p sampling"),
    entity: str = typer.Option("roc_racoon", "--entity", "-e", help="Entity name for tracking"),
) -> None:
    """Queue a local inference task (fire-and-forget). Returns task_id immediately."""
    
    async def _queue():
        task_id = await queue_local_task(
            prompt=prompt,
            model=model,
            system_prompt=system,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            entity=entity,
        )
        console.print(f"[green]✓[/green] Queued task: [bold]{task_id}[/bold]")
        console.print(f"  Model: {model}")
        console.print(f"  Entity: {entity}")
        console.print(f"  Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    
    anyio.run(_queue)


@app.command("status")
def task_status(
    task_id: str = typer.Argument(..., help="Task ID to check"),
) -> None:
    """Get status of a local task."""
    
    async def _status():
        status = await get_local_task_status(task_id)
        if not status:
            console.print(f"[red]Task not found: {task_id}[/red]")
            return
        
        table = Table(title=f"Task Status: {task_id}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in status.items():
            table.add_row(key, str(value))
        
        console.print(table)
    
    anyio.run(_status)


@app.command("cat")
def task_result(
    task_id: str = typer.Argument(..., help="Task ID to retrieve result"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Output raw JSON"),
) -> None:
    """Get result of a completed local task."""
    
    async def _cat():
        result = await get_local_task_result(task_id)
        if not result:
            console.print(f"[red]Result not found: {task_id}[/red]")
            console.print("Task may not be completed yet. Check status first.")
            return
        
        if raw:
            console.print_json(result.to_json())
        else:
            # Pretty print
            console.print(Panel(
                result.text,
                title=f"Result: {task_id}",
                subtitle=f"Model: {result.model} | Provider: {result.provider_name} | Tokens: {result.tokens_generated} | Latency: {result.latency_ms}ms",
                border_style="green",
            ))
            
            # Show metadata
            meta_table = Table(title="Metadata")
            meta_table.add_column("Field", style="cyan")
            meta_table.add_column("Value", style="white")
            meta_table.add_row("Task ID", result.task_id)
            meta_table.add_row("Model", result.model)
            meta_table.add_row("Provider", result.provider_name)
            meta_table.add_row("Tokens Generated", str(result.tokens_generated))
            meta_table.add_row("Latency (ms)", str(result.latency_ms))
            meta_table.add_row("Entity", result.entity)
            meta_table.add_row("Trace ID", result.trace_id)
            meta_table.add_row("Completed At", result.completed_at)
            console.print(meta_table)
    
    anyio.run(_cat)


@app.command("list")
def list_tasks(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (queued/completed/dead)"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max tasks to show"),
    entity: Optional[str] = typer.Option(None, "--entity", "-e", help="Filter by entity"),
) -> None:
    """List local tasks with optional filters."""
    
    async def _list():
        status_enum = None
        if status:
            try:
                status_enum = TaskStatus(status.lower())
            except ValueError:
                console.print(f"[red]Invalid status: {status}. Use: queued, completed, dead[/red]")
                return
        
        tasks = await list_local_tasks(status=status_enum, limit=limit, entity=entity)
        
        if not tasks:
            console.print("[yellow]No tasks found[/yellow]")
            return
        
        table = Table(title=f"Local Tasks ({len(tasks)} found)")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Model", style="green")
        table.add_column("Entity", style="magenta")
        table.add_column("Created", style="dim")
        table.add_column("Prompt Preview", style="white")
        
        for task in tasks:
            # Format timestamp
            try:
                dt = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
                created_str = dt.strftime("%m-%d %H:%M")
            except (ValueError, AttributeError, KeyError):
                created_str = task["created_at"][:16]
            
            table.add_row(
                task["task_id"],
                task["status"],
                task["model"],
                task["entity"],
                created_str,
                task["prompt_preview"],
            )
        
        console.print(table)
    
    anyio.run(_list)


@app.command("daemon")
def run_daemon(
    interval: float = typer.Option(2.0, "--interval", "-i", help="Poll interval in seconds"),
    max_concurrent: int = typer.Option(1, "--max-concurrent", "-c", help="Max concurrent tasks"),
) -> None:
    """Run the local worker pool daemon (background processor)."""
    console.print("[yellow]Starting Local Worker Pool daemon...[/yellow]")
    console.print(f"  Poll interval: {interval}s")
    console.print(f"  Max concurrent: {max_concurrent}")
    console.print("  Press Ctrl+C to stop")
    
    from omega.oracle.local_worker_pool import LocalWorkerPool
    from omega.oracle.model_gateway import ModelGateway
    from omega.oracle.health_monitor import HealthMonitor
    from omega.oracle.resource_guard import ResourceGuard
    
    async def _daemon():
        pool = LocalWorkerPool(
            model_gateway=ModelGateway(health_monitor=HealthMonitor()),
            resource_guard=ResourceGuard(),
            poll_interval=interval,
            max_concurrent=max_concurrent,
        )
        
        try:
            await pool.start()
            # Keep running until cancelled
            while True:
                await anyio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            await pool.stop()
            console.print("[green]Daemon stopped[/green]")
    
    anyio.run(_daemon)


@app.command("clean")
def clean_tasks(
    status: str = typer.Option("dead", "--status", "-s", help="Status to clean (dead/completed/queued/all)"),
    older_than_days: int = typer.Option(7, "--older-than", "-d", help="Only clean tasks older than N days"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Dry run (default) or execute"),
) -> None:
    """Clean old task files and artifacts."""
    from pathlib import Path
    import time
    
    status_dirs = {
        "queued": DATA_DIR / "requests" / "local_worker_queue" / "queued",
        "completed": DATA_DIR / "requests" / "local_worker_queue" / "completed",
        "dead": DATA_DIR / "requests" / "local_worker_queue" / "dead",
    }
    
    artifact_dir = DATA_DIR / "artifacts" / "local_worker"
    
    cutoff_time = time.time() - (older_than_days * 86400)
    cleaned = 0
    
    dirs_to_clean = [status_dirs[status]] if status != "all" else list(status_dirs.values())
    
    for task_dir in dirs_to_clean:
        for task_file in task_dir.glob("*.json"):
            if task_file.stat().st_mtime < cutoff_time:
                if dry_run:
                    console.print(f"[dim]Would remove: {task_file}[/dim]")
                else:
                    task_file.unlink()
                    # Also clean artifact
                    task_id = task_file.stem
                    artifact_task_dir = artifact_dir / task_id
                    if artifact_task_dir.exists():
                        import shutil
                        shutil.rmtree(artifact_task_dir)
                    console.print(f"[green]Removed: {task_file}[/green]")
                cleaned += 1
    
    if dry_run:
        console.print(f"\n[yellow]Dry run: {cleaned} files would be removed[/yellow]")
        console.print("Run with --execute to actually clean")
    else:
        console.print(f"\n[green]Cleaned {cleaned} files[/green]")


if __name__ == "__main__":
    app()