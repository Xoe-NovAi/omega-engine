# 🔱 Antigravity CLI — Master Technical Reference

**AP Token**: `AP-ANTIGRAVITY-MASTER-v2.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ research-fleet ⬡ antigravity ⬡ trc_antigravity_master_v2

**Last Updated**: 2026-05-22
**Confidence Rating**: HIGH (multi-source cross-verification + live CLI testing)

---

## §1 Overview

Antigravity CLI (`agy`) is Google's terminal-based AI coding agent, announced at Google I/O 2026 (May 19, 2026). It is the **official replacement for Gemini CLI**, which sunsets for individual users on **June 18, 2026**. [HIGH]

### Quick Facts

| Attribute | Value |
|-----------|-------|
| Binary name | `agy` |
| Installed version | **1.0.1** (verified live) |
| Binary size | 175 MB |
| Language | Go (Gemini CLI was Node.js) |
| License | **Proprietary** (Gemini CLI was Apache 2.0) |
| Repository | `github.com/google-antigravity/antigravity-cli` (docs only, no source) |
| Stars (2026-05-22) | ~346 |
| Release date | May 19, 2026 |
| Default model | Gemini 3.5 Flash |
| Installed location | `~/.local/bin/agy` |
| Auth | Google OAuth via system keyring (libsecret on Linux) |
| Auth status | ✅ **Fully functional** — email: `taylorbare27@gmail.com` |
| Context files | `GEMINI.md`, `AGENTS.md` (unchanged from Gemini CLI) |

### Architecture

Antigravity CLI is one surface of the **Google Antigravity** ecosystem, which has four distinct products:

| Product | Description |
|---------|-------------|
| **Antigravity 2.0** | Desktop app with visual agent orchestration (Manager View + Editor View) |
| **Antigravity CLI (`agy`)** | Terminal TUI with shared agent engine |
| **Antigravity SDK** | Python SDK (`pip install google-antigravity`) for programmatic agent access |
| **Antigravity IDE** | Original VS Code-fork IDE (November 2025, still maintained) |

### Architecture Principles

1. **Shared Agent Engine**: CLI and Desktop app run identical agent harness.
2. **Bidirectional Sync**: Preferences, permissions, and sessions sync between CLI and GUI.
3. **Async Subagents**: The CLI can orchestrate multiple background agents in parallel.

---

## §2 Live Verification — Headless Mode

The `--print` flag enables **non-interactive headless mode**, confirmed working:

```bash
agy --print "Your prompt here"          # Run and print response
agy --print-timeout 5m                  # Configurable timeout (default 5m)
agy -p "quick prompt"                   # Short alias
agy --dangerously-skip-permissions      # Auto-approve tool permissions
```

### Important Behavior
- **Exit code 0** always — even on quota exhaustion!
- **No stdout on failure** — quota errors go only to the log file
- **Use `--log-file`** to capture debug output

---

## §3 Authentication

### Live State (2026-05-22)
- **Method**: OAuth 2.0 with PKCE via libsecret keyring
- **Status**: ✅ **Authenticated as `taylorbare27@gmail.com`**
- **Log evidence**: `ChainedAuth: authenticated via keyring`

### Auth Flow Modes

| Environment | Flow |
|-------------|------|
| **Local desktop** | Opens browser automatically → token cached in system keyring |
| **Remote / SSH** | Detects SSH → prints authorization URL + one-time code |
| **Headless / CI** | Can set `ANTIGRAVITY_API_KEY` env var |

### Quota Status (Live)
```
RESOURCE_EXHAUSTED (code 429)
Model: Claude Opus 4.6 (Thinking)
Reset in: 166 hours (approximately 7 days)
```

---

## §4 Slash Commands — Complete Reference

| Command | Purpose |
|---------|---------|
| `/model` | Select default reasoning model |
| `/help` | List all commands and keyboard shortcuts |
| `/context` | Show token usage breakdown |
| `/usage` | Show quota and rate-limit status |
| `/rewind` | Roll back conversation to previous checkpoint |
| `/resume` | Open conversation picker |
| `/rename <name>` | Rename conversation |
| `/export` | Push session to Antigravity 2.0 GUI |
| `/agents` | Open subagents management panel |
| `/tasks` | Monitor active background tasks |
| `/skills` | Browse local and global agent skills |
| `/mcp` | Manage MCP servers |
| `/open <file>` | Open file in external editor |
| `/permissions` | Set agent autonomy level |
| `/compact` | Compact conversation context |
| `/fork` | Fork current conversation |
| `/clear` | Clear terminal screen |
| `/logout` | Log out and clear credentials |
| `/exit` | Exit CLI |

### Context References (`@` syntax)
| Command | Purpose |
|---------|---------|
| `@workspace` | Include entire project |
| `@file <path>` | Reference specific file |
| `@terminal` | Send terminal output to agent |
| `@problems` | Attach problems panel output |
| `@codebase` | Search indexed project files |
| `@ServerName` | Connect to MCP server |

---

## §5 Models Available (Live Verified)

| Model | Variants | Quota Status (Live) |
|-------|----------|---------------------|
| **Gemini 3.5 Flash** | High, Medium | ✅ Default (likely available) |
| **Gemini 3.1 Pro** | High, Low | ❌ Exhausted |
| **Claude Sonnet 4.6** | Thinking | ❌ Exhausted |
| **Claude Opus 4.6** | Thinking | ❌ **Exhausted** (was selected) |
| **GPT-OSS 120B** | Medium | ❌ Exhausted |

**Note**: Live testing showed all premium models experiencing quota exhaustion. The saved model preference was `Claude Opus 4.6 (Thinking)`.

---

## §6 Known Issues (Live-Verified)

| Issue | Status | Evidence |
|-------|--------|----------|
| Quota exhaustion on premium | ✅ **CONFIRMED** | 166h reset timer |
| Silent failure on quota | ✅ **CONFIRMED** | Exit 0, no stdout |
| MCP config parse error | ✅ **FOUND** | `mcp_config.json` was empty (0 bytes) — **FIXED** |
| Model persistence burns quota | ✅ **CONFIRMED** | Saved Opus model used for every prompt |
