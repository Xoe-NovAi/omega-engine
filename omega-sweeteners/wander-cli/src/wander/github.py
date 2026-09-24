"""GitHub API client for Wander."""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx


class GitHubClient:
    """Async GitHub API client for workflow runs."""
    
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
        timeout: float = 30.0,
    ):
        self.token = token
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "GitHubClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=self.timeout,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("GitHubClient not initialized. Use async context manager.")
        return self._client
    
    async def get_workflow_runs(
        self,
        repo: str,
        per_page: int = 30,
        page: int = 1,
        status: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Get recent workflow runs for a repository."""
        params = {
            "per_page": per_page,
            "page": page,
        }
        if status:
            params["status"] = status
        
        response = await self.client.get(f"/repos/{repo}/actions/runs", params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("workflow_runs", [])
    
    async def get_workflow_run(self, repo: str, run_id: int) -> dict[str, Any]:
        """Get details of a specific workflow run."""
        response = await self.client.get(f"/repos/{repo}/actions/runs/{run_id}")
        response.raise_for_status()
        return response.json()
    
    async def get_workflow_run_logs(self, repo: str, run_id: int) -> str:
        """Get logs for a workflow run."""
        response = await self.client.get(
            f"/repos/{repo}/actions/runs/{run_id}/logs",
            headers={"Accept": "application/vnd.github+json"},
        )
        response.raise_for_status()
        return response.text
    
    async def get_workflow_jobs(self, repo: str, run_id: int) -> list[dict[str, Any]]:
        """Get jobs for a workflow run."""
        response = await self.client.get(f"/repos/{repo}/actions/runs/{run_id}/jobs")
        response.raise_for_status()
        data = response.json()
        return data.get("jobs", [])
    
    async def get_repository(self, repo: str) -> dict[str, Any]:
        """Get repository info."""
        response = await self.client.get(f"/repos/{repo}")
        response.raise_for_status()
        return response.json()