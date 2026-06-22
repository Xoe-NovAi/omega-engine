# [id-soft: quake3-1999] GitHub Wrapper Tools — Specialized intelligence layer for GitHub operations
# ⬡ OMEGA ⬡ KALI ⬡ CONFIG ⬡ v1.0.0
# Decision: D-kal-163

import json
import logging
import yaml
import httpx
import anyio
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context

from mcp_servers.omega_hub.server import mcp
from mcp_servers.omega_hub.middleware import m9_safe
from mcp_servers.omega_hub.state import PROJECT_ROOT

logger = logging.getLogger("omega.hub.github")

# ── Configuration Loading ──────────────────────────────────────────────────────

def _get_github_account(entity_name: str) -> Dict[str, Any]:
    """Load GitHub account details for a specific Omega entity.
    
    Returns:
        Dict containing username and PAT, or raises RuntimeError if not found.
    """
    config_path = PROJECT_ROOT / "config" / "github_accounts.yaml"
    if not config_path.exists():
        raise RuntimeError("GitHub accounts configuration missing at config/github_accounts.yaml")
    
    def _read():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    config = anyio.to_thread.run_sync(_read)
    accounts = config.get("accounts", [])
    for acc in accounts:
        if acc.get("entity") == entity_name.lower():
            return acc
    
    # Fallback to system primary (kali)
    for acc in accounts:
        if acc.get("entity") == "kali":
            return acc
            
    raise RuntimeError(f"No GitHub account mapped for entity '{entity_name}'")

async def _github_request(method: str, endpoint: str, entity: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Internal helper for authenticated GitHub API requests.
    
    Args:
        method: HTTP method (GET, POST, PATCH, etc.)
        endpoint: API endpoint (e.g., '/repos/{owner}/{repo}/pulls')
        entity: The Omega entity performing the action
        data: Request body
        params: Query parameters
    """
    acc = _get_github_account(entity)
    token = acc["pat"]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Omega-Engine-Sovereign-Bridge"
    }
    
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com{endpoint}"
        response = await client.request(method, url, headers=headers, json=data, params=params)
        if response.status_code >= 400:
            logger.error(f"GitHub API Error [{response.status_code}]: {response.text}")
            return {"error": f"GitHub API returned {response.status_code}", "details": response.text}
        return response.json()

# ── Specialized Tools ──────────────────────────────────────────────────────────

@m9_safe("github_create_pr_with_template")
@mcp.tool()
async def github_create_pr_with_template(owner: str, repo: str, head: str, base: str, title: str, body: str, entity: str = "kali") -> str:
    """Create a Pull Request using the Omega Temple-Grade template.
    
    Args:
        owner: Repository owner
        repo: Repository name
        head: Branch name for the PR
        base: Base branch to merge into
        title: PR title
        body: PR description
        entity: Entity performing the action
    """
    # Omega Template Injection
    template = (
        "## 🏛️ Temple-Grade Checklist\n"
        "- [ ] T1: AP tokens in all file headers\n"
        "- [ ] T3: Tests passing (make test)\n"
        "- [ ] T4: Linting passed (make lint)\n"
        "- [ ] T5: AnyIO-only architecture\n"
        "- [ ] T6: Zero external telemetry\n"
        "- [ ] T10: Atomic writes implemented\n\n"
        "## 🔖 Heritage Attribution\n"
        "- [ ] All [id-soft:] tags verified via `make heritage-map`\n\n"
        "## 👤 Entity Attribution\n"
        f"Performed by: @{entity}\n"
    )
    
    full_body = f"{template}\n---\n{body}"
    
    endpoint = f"/repos/{owner}/{repo}/pulls"
    data = {
        "title": title,
        "head": head,
        "base": base,
        "body": full_body
    }
    
    result = await _github_request("POST", endpoint, entity, data=data)
    return json.dumps(result, indent=2)

@m9_safe("github_add_entity_attribution")
@mcp.tool()
async def github_add_entity_attribution(owner: str, repo: str, sha: str, message: str, entity: str = "kali") -> str:
    """Inject an entity attribution trailer into a commit.
    
    Args:
        owner: Repository owner
        repo: Repository name
        sha: Commit SHA to attribute
        message: Attribution message (e.g., 'Sovereign implementation by @kali')
        entity: Entity performing the action
    """
    # Note: GitHub doesn't allow editing commit messages directly. 
    # This tool creates a 'Note' or a follow-up commit for attribution.
    # For this implementation, we create a specific 'attribution' issue linked to the commit.
    
    endpoint = f"/repos/{owner}/{repo}/issues"
    data = {
        "title": f"Attribution: {sha[:7]}",
        "body": f"{message}\n\nCommit: {sha}\nEntity: @{entity}",
        "labels": ["attribution", f"entity-{entity}"]
    }
    
    result = await _github_request("POST", endpoint, entity, data=data)
    return json.dumps(result, indent=2)

@m9_safe("github_check_temple_grade")
@mcp.tool()
async def github_check_temple_grade(owner: str, repo: str, pr_number: int, entity: str = "kali") -> str:
    """Check the Temple-Grade CI status for a specific PR.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number to check
        entity: Entity performing the action
    """
    endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/statuses"
    result = await _github_request("GET", endpoint, entity)
    
    # Filter for 'temple-grade' check
    checks = result if isinstance(result, list) else result.get("statuses", [])
    tg_check = next((c for c in checks if "temple-grade" in c.get("context", "").lower()), None)
    
    if not tg_check:
        return json.dumps({"status": "unknown", "message": "Temple-Grade check not found for this PR"})
    
    return json.dumps({
        "status": tg_check.get("state"),
        "description": tg_check.get("description"),
        "context": tg_check.get("context"),
        "target_url": tg_check.get("target_url")
    }, indent=2)

@m9_safe("github_list_heritage_issues")
@mcp.tool()
async def github_list_heritage_issues(owner: str, repo: str, entity: str = "kali") -> str:
    """List all open GitHub Issues tagged as 'heritage'.
    
    Args:
        owner: Repository owner
        repo: Repository name
        entity: Entity performing the action
    """
    endpoint = f"/repos/{owner}/{repo}/issues"
    params = {"state": "open", "labels": "heritage"}
    result = await _github_request("GET", endpoint, entity, params=params)
    return json.dumps(result, indent=2)

@m9_safe("github_create_vet_issue")
@mcp.tool()
async def github_create_vet_issue(owner: str, repo: str, vet_record: Dict[str, Any], entity: str = "kali") -> str:
    """Auto-create a GitHub Issue from a Heritage Vetting record.
    
    Args:
        owner: Repository owner
        repo: Repository name
        vet_record: The vet record JSON (from HERITAGE_VET_LOG.md)
        entity: Entity performing the action
    """
    score = vet_record.get("score", 0)
    status = "APPROVED" if score >= 7 else "REJECTED"
    
    title = f"Heritage Vet: {vet_record.get('concept', 'Unknown Concept')} [{status}]"
    body = (
        f"## Heritage Vetting Record\n"
        f"**Concept**: {vet_record.get('concept')}\n"
        f"**Score**: {score}/10\n"
        f"**Verdict**: {status}\n\n"
        f"### Rationale\n{vet_record.get('rationale', 'No rationale provided.')}\n\n"
        f"**Vetted by**: @{entity}"
    )
    
    endpoint = f"/repos/{owner}/{repo}/issues"
    data = {
        "title": title,
        "body": body,
        "labels": ["heritage", f"vet-{status.lower()}"]
    }
    
    result = await _github_request("POST", endpoint, entity, data=data)
    return json.dumps(result, indent=2)

@m9_safe("github_get_repo_health")
@mcp.tool()
async def github_get_repo_health(owner: str, repo: str, entity: str = "kali") -> str:
    """Get high-level health metrics for a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        entity: Entity performing the action
    """
    endpoint = f"/repos/{owner}/{repo}"
    repo_data = await _github_request("GET", endpoint, entity)
    
    health = {
        "stars": repo_data.get("stargazers_count"),
        "forks": repo_data.get("forks_count"),
        "open_issues": repo_data.get("open_issues_count"),
        "is_private": repo_data.get("private"),
        "default_branch": repo_data.get("default_branch"),
        "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
    }
    
    return json.dumps(health, indent=2)
