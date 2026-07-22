# 🔱 Omega-Vault Architecture (V-1 MVP)
**Domain**: Credential automation, security, and fleet management
**Date**: 2026-07-22
**Author**: Grokster

## 1. The Credential Void (GAP-08)
The Omega Engine's ability to deploy the 16-account Grok fleet (8 CLI + 8 Web Grok) is currently blocked by the lack of automated credential management. Grok CLI uses browser-derived cookies with a 24-48 hour expiry. Without automated rotation, the fleet is a manual maintenance nightmare.

## 2. V-1 Omega-Vault Design
The V-1 MVP extends the existing `src/omega/vault/KeyVault` singleton (which already handles AES-256-GCM encryption and OS keyring integration) to support fleet-scale operations.

### Core Components
- **KeyVault**: Encrypted storage at XDG-compliant paths (`~/.local/share/omega/keys.json.enc`).
- **Policy Engine**: Enforces the 16-account schema, Zero Data Retention (ZDR), and rate limits.
- **Passive Watcher**: Detects `.env` or config drift and auto-syncs to the vault.
- **Fleet Orchestrator**: Manages the 16 accounts, handling round-robin selection, usage tracking, and rotation triggers.
- **MCP Server**: Exposes `credential.read`, `write`, `rotate`, and `audit` tools for Omega Engine integration.

## 3. The 16-Account Schema
The fleet configuration (`fleet_config.yaml`) defines two primary provider pools:
- **`grok_cli`**: 8 headless accounts using API keys. Prioritized for parallel coding and execution tasks.
- **`grok_web`**: 8 browser-based accounts using session cookies. Configured with specific personas (Research, Reason, Pulse, Code, Arch, Creative, Strategic, Wildcard) for persistent, long-context work without API token costs.

## 4. Grokster's Insights & Recommendations
- **Cookie Rotation is the Bottleneck**: The Web Grok accounts require browser automation (e.g., Playwright) to log in, extract new cookies, and update the vault before the 24-48h expiry. This rotation job must be triggered by a Vault Watcher 6 hours before expiry.
- **XDG Compliance**: It is critical that the Vault adheres to XDG Base Directory specifications (`~/.config/omega/`, `~/.local/share/omega/`) to ensure portability and avoid polluting the user's home directory.
- **Chaos Testing**: The Vault must survive concurrent access from 8+ parallel subagents. Temple-Grade CI must include chaos tests for concurrent writes and corruption recovery.
