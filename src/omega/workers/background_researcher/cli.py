# 🔱 Omega Engine — Background Researcher CLI
# AP: AP-BACKGROUND-RESEARCHER-CLI-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ sovereign ⬡ cli ⬡ WORKER
#
# CLI commands for the background researcher.
# Integrated into oracle_cli.py via the 'research' command group.

"""
Usage:
    omega research "topic"            # Enqueue a research topic
    omega research status             # Show researcher status
    omega research run                # Run one cycle now
    omega research history            # Show completed research
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .loop import BackgroundResearcherLoop

logger = logging.getLogger(__name__)


async def cmd_research(topic: str, depth: int = 2, prompt_mode: str = "") -> str:
    """Enqueue a user-requested research topic."""
    loop = BackgroundResearcherLoop()
    if prompt_mode:
        from .distiller import SYSTEM_PROMPTS
        if prompt_mode in SYSTEM_PROMPTS:
            await loop.set_prompt_mode(prompt_mode)
        else:
            return f"⚠️ Unknown prompt mode '{prompt_mode}'. Available: {', '.join(SYSTEM_PROMPTS.keys())}"
    await loop.enqueue_user_request(topic, depth=depth)
    mode_info = f" [prompt: {prompt_mode or 'auto'}]"
    return f"✅ Queued: '{topic}' (depth={depth}){mode_info}"


async def cmd_research_status() -> str:
    """Show current researcher status."""
    loop = BackgroundResearcherLoop()
    status = await loop.get_status()

    lines = [
        "╔══════════════════════════════════════════╗",
        "║   🔬 Omega Background Researcher Status  ║",
        "╚══════════════════════════════════════════╝",
        "",
        f"Running:          {status['running']}",
        f"Cycle count:      {status['cycle_count']}",
        f"Queue size:       {status['queue_size']}",
        f"SearXNG healthy:  {status['searxng_healthy']}",
        "",
        "── Monthly Budget ──",
    ]
    for provider, budget in status.get("budget", {}).get("budgets", {}).items():
        pct = ((budget["total"] - budget["remaining"]) / budget["total"]) * 100 if budget["total"] > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        lines.append(f"  {provider:12s} [{bar}] {budget['remaining']}/{budget['total']} ({pct:.0f}%)")

    daily = status.get("budget", {}).get("daily_used", {})
    if daily:
        lines.extend([
            "",
            "── Daily Usage ──",
        ])
        for op, count in daily.items():
            lines.append(f"  {op:20s}: {count}")

    return "\n".join(lines)


async def cmd_research_run(topic: str = "", depth: int = 2) -> str:
    """Run a research cycle now."""
    loop = BackgroundResearcherLoop()

    if topic:
        await loop.enqueue_user_request(topic, depth=depth)

    result = await loop.run_cycle()

    if result.get("skipped"):
        return f"⏭️ Cycle skipped: {result.get('reason', 'unknown')}"

    return (
        f"✅ Research cycle complete\n"
        f"   Topic: {result.get('task', 'N/A')}\n"
        f"   Sources: {result.get('sources_found', 0)}\n"
        f"   Claims: {result.get('claims', 0)}\n"
        f"   Distillations: {result.get('distillations', 0)}\n"
        f"   Converged: {result.get('converged', False)}"
    )


async def cmd_research_history() -> str:
    """Show completed research from checkpoints."""
    checkpoint_dir = Path("data/research/checkpoints")
    if not checkpoint_dir.exists():
        return "No research history found."

    done_tasks = []
    for path in sorted(checkpoint_dir.glob("*.json"), reverse=True)[:20]:
        try:
            data = json.loads(path.read_text())
            if data.get("state") == "done":
                done_tasks.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    if not done_tasks:
        return "No completed research found."

    lines = ["📚 Completed Research Sessions:", ""]
    for t in done_tasks:
        lines.append(f"  • {t['topic']}")
        lines.append(f"    Depth: {t['depth']} | Sources: {len(t.get('sources', []))} | {t.get('last_attempt', '?')[:10]}")
        lines.append("")

    return "\n".join(lines)
