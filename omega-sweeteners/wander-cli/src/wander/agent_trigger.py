"""Agent auto-trigger logic for Wander."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class CIContext:
    """Context passed to triggered agent."""
    repo: str
    run_id: int
    conclusion: str
    workflow_name: str
    branch: str
    actor: str
    html_url: str
    timestamp: str
    logs: Optional[str] = None
    failed_jobs: Optional[list[dict]] = None


def trigger_agent(
    repo: str,
    run_id: int,
    conclusion: str,
    workflow_name: str,
    branch: str,
    actor: str,
    html_url: str,
    logs: Optional[str] = None,
    failed_jobs: Optional[list[dict]] = None,
) -> None:
    """
    Trigger agent with CI context.
    
    The agent is invoked with context about the CI run so it can:
    - Analyze failures
    - Suggest fixes
    - Create PRs with fixes
    - Run tests locally
    """
    context = CIContext(
        repo=repo,
        run_id=run_id,
        conclusion=conclusion,
        workflow_name=workflow_name,
        branch=branch,
        actor=actor,
        html_url=html_url,
        timestamp=datetime.now().isoformat(),
        logs=logs,
        failed_jobs=failed_jobs,
    )
    
    # Default: invoke opencode with CI context
    _invoke_opencode(context)


def _invoke_opencode(context: CIContext) -> None:
    """Invoke opencode with CI context."""
    
    # Build context message for the agent
    context_msg = f"""CI {context.conclusion.upper()}: {context.workflow_name} on {context.repo}@{context.branch}

Run: {context.html_url}
Actor: @{context.actor}
Time: {context.timestamp}

{("FAILED" if context.conclusion == "failure" else "PASSED")} — Agent auto-triggered by Wander.
"""
    
    if context.logs:
        context_msg += f"\n--- LOGS ---\n{context.logs[:5000]}\n"
    
    if context.failed_jobs:
        context_msg += f"\n--- FAILED JOBS ---\n"
        for job in context.failed_jobs[:3]:
            context_msg += f"- {job.get('name', 'unknown')}: {job.get('conclusion', 'unknown')}\n"
    
    context_msg += "\n\nAnalyze the failure, suggest minimal fixes, and create a PR if confident."
    
    # Invoke opencode with the context
    try:
        # Use opencode's --message flag or pipe to stdin
        cmd = [
            "opencode",
            "--message", context_msg,
        ]
        
        # Run in background so Wander continues monitoring
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except FileNotFoundError:
        # opencode not in PATH
        pass
    except Exception:
        pass


def save_context_to_file(context: CIContext, path: str) -> None:
    """Save CI context to file for later retrieval."""
    with open(path, "w") as f:
        json.dump({
            "repo": context.repo,
            "run_id": context.run_id,
            "conclusion": context.conclusion,
            "workflow_name": context.workflow_name,
            "branch": context.branch,
            "actor": context.actor,
            "html_url": context.html_url,
            "timestamp": context.timestamp,
            "logs": context.logs,
            "failed_jobs": context.failed_jobs,
        }, f, indent=2)


def load_context_from_file(path: str) -> Optional[CIContext]:
    """Load CI context from file."""
    try:
        with open(path) as f:
            data = json.load(f)
        return CIContext(
            repo=data["repo"],
            run_id=data["run_id"],
            conclusion=data["conclusion"],
            workflow_name=data["workflow_name"],
            branch=data["branch"],
            actor=data["actor"],
            html_url=data["html_url"],
            timestamp=data["timestamp"],
            logs=data.get("logs"),
            failed_jobs=data.get("failed_jobs"),
        )
    except Exception:
        return None


from datetime import datetime