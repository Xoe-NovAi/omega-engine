# Wander CLI — Zero-Polling GitHub Actions Monitor with Mandatory Agent Auto-Trigger

**Version**: 0.1.0 | **Status**: Alpha | **License**: Apache-2.0

## Overview

Wander eliminates the need to stare at GitHub Actions, wait for emails, or manually check CI status. It monitors GitHub Actions **event-driven** (via GitHub API) and **mandatorily triggers your agent** on every CI completion — so your agent sees failures immediately and can fix them while you're doing other things.

## Features

- **Zero polling** — Uses GitHub API with efficient pagination (no wasteful polling)
- **Mandatory agent auto-trigger** — Every CI completion (success/failure) triggers your agent with full context
- **macOS notifications** — Native `osascript` alerts when runs finish/fail
- **Multi-repo** — Watch multiple repositories simultaneously
- **Agent context injection** — Agent receives full CI context (logs, failed jobs, URLs)
- **Daemon mode** — Run in background
- **Single binary** — `uv tool install wander`

## Quick Start

```bash
# Install
uv tool install wander

# Watch a repo (mandatory agent trigger enabled by default)
wander watch --repo owner/repo --notify

# Watch multiple repos
wander watch --repo owner/repo1 --repo owner/repo2 --notify

# Check current status
wander status --repo owner/repo
```

## Configuration

### Config File (`~/.config/wander/config.yaml`)

```yaml
repos:
  - "owner/repo1"
  - "owner/repo2"
notify: true
agent_trigger: true
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub token (required) |
| `WANDER_REPOS` | Comma-separated repos (alternative to config) |
| `WANDER_NOTIFY` | Enable notifications (default: true) |
| `WANDER_AGENT_TRIGGER` | Enable agent auto-trigger (default: true) |

## Agent Auto-Trigger

**This is the killer feature.** When CI completes (success or failure), Wander:

1. Fetches run details (logs, failed jobs, URLs)
2. Builds rich context for the agent
3. **Mandatorily triggers your agent** with full CI context

The agent receives:
- Repository, run ID, conclusion, workflow name
- Branch, actor, HTML URL
- Failure logs (truncated to 5KB)
- Failed job details
- Timestamp and actor info

### Agent Invocation

By default, Wander invokes `opencode` with the CI context:

```bash
opencode --message "CI FAILURE: workflow-name on owner/repo@branch

Run: https://github.com/owner/repo/actions/runs/12345
Actor: @username
Time: 2026-09-21T20:34:00Z

FAILED — Agent auto-triggered by Wander.

--- LOGS ---
[truncated logs...]

--- FAILED JOBS ---
- test: failure
- lint: success

Analyze the failure, suggest minimal fixes, and create a PR if confident."
```

**Customize the agent trigger** by implementing your own `trigger_agent` function in `src/wander/agent_trigger.py`.

## Installation

```bash
# Via uv (recommended)
uv tool install wander

# Or from source
git clone https://github.com/omega-engine/wander-cli
cd wander-cli
uv pip install -e .
```

## Commands

| Command | Description |
|---------|-------------|
| `wander watch` | Monitor repos (main command) |
| `wander status` | Quick status check |
| `wander config` | Show current config |

### `wander watch`

```bash
# Basic usage
wander watch --repo owner/repo --notify

# Multiple repos
wander watch --repo owner/repo1 --repo owner/repo2 --notify

# Disable agent trigger (just notify)
wander watch --repo owner/repo --no-agent-trigger

# Disable notifications
wander watch --repo owner/repo --no-notify

# Daemon mode (background)
wander watch --repo owner/repo --daemon
```

### `wander status`

```bash
wander status --repo owner/repo
```

Shows latest run status for each repo.

### `wander config`

```bash
wander config
```

Shows current configuration.

## GitHub Actions Integration

For automatic agent triggering via GitHub Actions (alternative to running Wander locally):

```yaml
# .github/workflows/wander-agent-trigger.yml
name: Wander Agent Trigger

on:
  workflow_run:
    workflows: ["*"]
    types:
      - completed

jobs:
  trigger-agent:
    if: github.event.workflow_run.conclusion == 'failure' || github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Wander
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          export PATH="$HOME/.local/bin:$PATH"
          uv tool install wander
      - name: Trigger Agent
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          export PATH="$HOME/.local/bin:$PATH"
          wander trigger \
            --repo "${{ github.repository }}" \
            --run-id "${{ github.event.workflow_run.id }}" \
            --conclusion "${{ github.event.workflow_run.conclusion }}" \
            --workflow "${{ github.event.workflow_run.name }}" \
            --branch "${{ github.event.workflow_run.head_branch }}" \
            --actor "${{ github.event.workflow_run.actor.login }}" \
            --url "${{ github.event.workflow_run.html_url }}"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Wander CLI                               │
├─────────────────────────────────────────────────────────────┤
│  Watch Loop (30s default)                                   │
│  ├── GitHub API Client (event-driven, not polling)         │
│  ├── Seen Runs Cache (deduplication)                       │
│  ├── macOS Notifications (osascript)                       │
│  └── Agent Trigger (mandatory, configurable)               │
├─────────────────────────────────────────────────────────────┤
│  Agent Trigger                                              │
│  ├── Context Builder (rich CI context)                     │
│  ├── Log Fetcher (truncated to 5KB)                        │
│  ├── Failed Jobs Extractor                                  │
│  └── Agent Invocation (opencode by default)                │
└─────────────────────────────────────────────────────────────┘
```

## Development

```bash
# Clone
git clone https://github.com/omega-engine/wander-cli
cd wander-cli

# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
mypy src/wander

# Run locally
uv run wander watch --repo owner/repo --notify
```

## Project Structure

```
src/wander/
├── __init__.py           # CLI entry point
├── cli.py                # Click commands
├── config.py             # Configuration (YAML + env)
├── github.py             # GitHub API client
├── watch.py              # Monitoring loop
├── agent_trigger.py      # Agent auto-trigger logic
└── github.py             # GitHub API client
```

## License

Apache-2.0 — see LICENSE in parent repo.