# 🔱 Grok CLI (Grok Build) Best Practices — Omega Engine
**AP Token**: `AP-GROK-CLI-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source for Grok CLI (Grok Build) local tool interactions
**Platform**: Local CLI tool (`grok` binary) — runs on your machine, SuperGrok Heavy subscription
**Supersedes**: `docs/research/R_GROK_CLI_ARCHITECTURE.md` (CLI sections), `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` (CLI sections), `docs/research/R_GROK_ECOSYSTEM_DEEP.md` (CLI sections), `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` (CLI sections)

> **CRITICAL DISTINCTION**: This doc covers **Grok CLI (Grok Build)** — the local terminal coding agent. For the **web platform (grok.com)**, see `docs/strategy/WEB_GROK_BEST_PRACTICES.md`. They are entirely different platforms.

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Setup & Architecture | `#1-setup--architecture` | Installation, authentication, local-first architecture |
| 2. Format Specification | `#2-format-specification` | Markdown for instructions, local files for skills/config |
| 3. Key Capabilities | `#3-key-capabilities` | TUI, headless, ACP, sandbox, parallel sub-agents, skills |
| 4. File/Workspace Organization | `#4-fileworkspace-organization` | Local file access, sandbox profiles, gitignore respect |
| 5. System Prompt / Rules | `#5-system-prompt--rules` | Custom rules, agent profiles, rules files |
| 6. Skills (Local) | `#6-skills-local` | Local skill files, slash commands, skill creation |
| 7. Sandbox & Security | `#7-sandbox--security` | Landlock/Seatbelt profiles, deny lists, permissions |
| 8. ACP & Headless Mode | `#8-acp--headless-mode` | ACP protocol, stdin/stdout, scripting, CI integration |
| 9. Cost & Subscription | `#9-cost--subscription` | SuperGrok Heavy requirement, pricing, model access |
| 10. Sovereign Boundary Protocols | `#10-sovereign-boundary-protocols` | M7 local-first, M23 failure integrity, IP protection |
| 11. Quick Reference | `#11-quick-reference` | Command flags, sandbox profiles, config files |
| 12. Source Citations | `#12-source-citations` | Tier-ordered citations |
| 13. Hydration Protocol | `#13-hydration-protocol` | Mandatory steps before any Grok CLI interaction |

---

## 1. SETUP & ARCHITECTURE

### 1.1 Installation
```bash
# Official install (macOS/Linux)
curl -fsSL https://x.ai/cli/install.sh | bash

# Windows: via WSL2 (native Win32 on roadmap)
```

### 1.2 Authentication
- **Browser OAuth** on first launch (opens browser)
- **API Key** for headless/CI: `XAI_API_KEY` env var
- **Enterprise**: External auth binary/script delegation
- Credentials stored in `~/.grok/auth.json` (mode 600)

### 1.3 Architecture (2026)
- **Local-first terminal coding agent** — runs on your machine (TUI)
- **Model**: `grok-4.5` (coding-specialized, launched July 8, 2026)
- **Inference in cloud** but **snippet-only transmission** — no auto-upload of source files
- **8 parallel sub-agents** with Arena Mode (auto-ranking)
- **SWE-bench Verified**: 70.8% (grok-code-fast-1); Grok 4.5 benchmarks pending
- **OS-level sandbox**: Landlock (Linux) / Seatbelt (macOS)
- **ACP (Agent Client Protocol)** for IDE integration (Zed, Neovim, Emacs, marimo)
- **MCP server support** (planned/not yet documented as of May 2026)
- **Hooks/skills** — local files in `~/.grok/`

### 1.3.1 Role in the Omega Engine Pipeline

Grok CLI is the **exploratory analysis layer** — it complements, not competes with, Web Claude:

```
Grok CLI (exploratory):   run tests, grep full repo, discover issues,
                          find what to put in the context pack
        ↓ (informs what to pack)
Web Claude (formal review): mandate compliance, architecture vetting,
        spec generation on the packaged context
```

**Delineation**:
- **Grok CLI**: Full filesystem access, can execute code, 8 parallel sub-agents, discovers what to pack. Best for *finding* the issues.
- **Web Claude**: Reviews only the packaged context. Best for *formalizing* findings into mandate-compliant specs.

**Sequential flow (Pattern C)**: Run Grok CLI exploratory analysis → build context pack from findings → send to Web Claude for formal review → ingest artifact.

### 1.4 Subscription Requirement
- **Limited-time free access to Grok 4.5** during launch window (verify at `x.ai/build`)
- After launch promo ends: **SuperGrok Heavy required** (~$300/mo, $99/mo intro for 6 months)
- Includes: Grok Build + Grok 4/5 + full SuperGrok + API access to Heavy models
- **No permanent free tier** for Grok Build — the July 2026 launch offer is time-limited
- **Check your account**: x.ai/build shows current free usage status

---

## 2. FORMAT SPECIFICATION

### 2.1 System Prompt / Rules → **Markdown** (rules files, config)
- `--rules` flag: append custom rules to system prompt
- `--system-prompt-override`: replace system prompt entirely
- Rules files: Markdown in `~/.grok/rules/` or project `.grok/rules/`

### 2.2 Skills (Local) → **Markdown** files in `~/.grok/skills/`
- Local skill files with name, description, instructions
- Invoked via `/skillname` in TUI

### 2.3 Config → **TOML** (`~/.grok/config.toml`, `.grok/config.toml`)
- Sandbox profiles, model selection, permissions, MCP servers

### 2.4 Sandbox Profiles → **TOML** (`~/.grok/sandbox.toml`, `.grok/sandbox.toml`)
- Custom profiles extending built-ins

### 2.5 Structured Data → **JSON** (ACP, headless output)
- `--output-format streaming-json` for headless mode
- ACP: JSON-RPC over stdin/stdout

---

## 3. KEY CAPABILITIES

### 3.1 Interactive TUI (Default)
- Full-screen terminal interface
- Plan mode (approve before execution)
- Subagents (up to 8 parallel)
- Keyboard shortcuts, slash commands, modals
- Scrollback, rendering, prompt widget with `@` file search

### 3.2 Headless Mode (Scripting/CI)
```bash
# One-shot prompt
grok -p "Explain this codebase"

# Streaming JSON output
grok -p "Fix this bug" --output-format streaming-json

# Single turn, exit after response
grok --single-turn -p "Quick question"
```

### 3.3 ACP (Agent Client Protocol)
- **JSON-RPC over stdin/stdout** (`grok agent stdio`)
- **IDE integrations**: Zed, Neovim (CodeCompanion, avante.nvim), Emacs (agent-shell), marimo notebook
- **WebSocket relay** for remote agent exposure
- **ACP SDK** for rich agent integration (tool calls, thoughts, plans, permissions)

### 3.4 Parallel Sub-Agents (Arena Mode)
- **Up to 8 simultaneous sub-agents**
- **Auto-ranking** of sub-agent outputs
- **Plan mode**: Review execution plan before any code runs
- **Subagent/task tool** enabled via `--subagents` flag

### 3.5 Local-First Design (IP Protection)
- **No source code auto-upload** to xAI servers
- **Snippet-only transmission** — only prompt tokens you explicitly include
- **`.gitignore` respected** — secrets, credentials, ignored files excluded by default
- **Transport encryption**: TLS 1.3
- **Enterprise audit**: Not yet published (May 2026 beta) — verify with network traffic audits

### 3.6 MCP Server Support
- Planned/not yet documented (as of May 2026 beta)
- Configuration in `~/.grok/config.toml`

---

## 4. FILE/WORKSPACE ORGANIZATION

### 4.1 Local File Access
- **Full read access** to workspace (understands dependencies, system libs)
- **Write access** controlled by sandbox profile
- **Respects `.gitignore`** by default (`GROK_RESPECT_GITIGNORE=1`)
- **`.envrc` injection** into bash sessions (configurable)

### 4.2 Sandbox Profiles (OS-Level Isolation)
| Profile | FS Read | FS Write | Child Network | Use Case |
|---------|---------|----------|---------------|----------|
| `off` (default) | Unrestricted | Unrestricted | Allowed | No sandbox |
| `workspace` | Everywhere | CWD + `~/.grok/` + temp | Allowed | **Normal development** |
| `devbox` | Everywhere | All top-level except `/data` | Allowed | Disposable dev VMs |
| `read-only` | Everywhere | `~/.grok/` + temp only | Blocked (Linux) | Code review, auditing |
| `strict` | CWD + system paths | CWD + `~/.grok/` + temp | Blocked (Linux) | **Untrusted repositories** |

**Activation**:
```bash
# CLI flag
grok --sandbox workspace

# Config
# ~/.grok/config.toml
[sandbox]
profile = "workspace"

# Env var
GROK_SANDBOX=workspace
```

### 4.3 Custom Sandbox Profiles (`~/.grok/sandbox.toml` or `.grok/sandbox.toml`)
```toml
[profiles.my-profile]
extends = "workspace"
restrict_network = true
deny = ["/secrets", "**/.env", "**/*.pem"]
read_only = ["/etc"]
read_write = ["/tmp/my-app"]
```
- **Kernel-enforced** on Linux (Landlock + bubblewrap for deny)
- **Airtight on macOS** (Seatbelt regex, even for files created after start)
- **Irreversible** once applied — cannot relax at runtime

### 4.4 Permissions (Allow/Deny Rules)
```bash
# Allow specific patterns
grok --allow "**/*.py" --deny "**/secrets/**"

# Config
[tools]
allow = ["**/*.py"]
deny = ["**/secrets/**"]
```

### 4.5 Skills (Local Files)
- Stored in `~/.grok/skills/` as Markdown files
- Invoked via `/skillname` slash command in TUI
- Structure:
```markdown
---
name: "my-skill"
description: "When to invoke this skill"
---
# Instructions

You are a [role]. When invoked:
- [task 1]
- [task 2]
- Output: [format]
```

---

## 5. SYSTEM PROMPT / RULES

### 5.1 Custom Rules (Appended to System Prompt)
```bash
# CLI flag
grok --rules "Always use AnyIO. No asyncio imports."

# Rules file
# ~/.grok/rules/omega-rules.md
Always use AnyIO for async code.
No telemetry in generated code.
Local-first: prefer local models.
```

### 5.2 Omega Engine Mandate Rules
Create `~/.grok/rules/omega-mandates.md` with:
```markdown
# Omega Engine Sovereign Mandates

## M1 AnyIO
- All async code MUST use AnyIO
- NEVER use asyncio directly
- Wrap blocking I/O in anyio.to_thread.run_sync

## M2 Engine-Stack Firewall
- Core (src/omega/) ≠ Stacks (config/wads/)
- No stack-specific logic in core engine

## M7 Local-First
- Local inference is PRIMARY
- Cloud is FALLBACK only
- Prefer local model recommendations

## M8 Zero Telemetry
- No analytics, tracking, or phone-home
- No external telemetry in generated code

## M13 Temple-Grade
- T1-T11 gates apply to all generated artifacts
- Run `make temple-grade` after non-trivial changes

## M14 Heritage Vetting
- [id-soft:] tags need vet records in HERITAGE_VET_LOG.md
- Qualification gate: cannot be justified without original hardware constraint

## M23 Failure Integrity
- No soft failures
- Mandatory tool broken → [TOOL-CHAIN-COLLAPSE]
```

### 5.3 System Prompt Override
```bash
grok --system-prompt-override "You are a [custom role]..."
```

### 5.3 Agent Profiles (Custom Agent Definitions)
```bash
grok --agent-profile /path/to/agent.toml
```
- Define custom agent behavior, tools, model

---

## 6. SKILLS (Local)

### 6.1 Skill File Structure (`~/.grok/skills/skillname.md`)
```markdown
---
name: "code-review"
description: "Review code for security, mandates, best practices"
---
# Code Review Skill

You are a senior security auditor. When invoked:
- Check for M1 AnyIO compliance (no asyncio)
- Verify M14 heritage tags have vet records
- Scan for PII exposure
- Output: findings table with severity
```

### 6.2 Invocation
- In TUI: type `/code-review`
- Carries across sessions (stored locally)

---

## 7. SANDBOX & SECURITY

### 7.1 Deny Lists (Kernel-Enforced)
```toml
# ~/.grok/sandbox.toml
[profiles.secure]
extends = "strict"
deny = ["**/.env", "**/*.pem", "**/secrets/**", "**/id_rsa*"]
```
- **Linux**: read-deny requires `bubblewrap`; refuses to start if unavailable
- **macOS**: Seatbelt regex — airtight, even for files created after start
- **Blocks `mv secret x && cat x` bypass** — denied paths read-denied AND write-denied

### 7.2 Network Restrictions
- `restrict_network = true` blocks child-process network on Linux (seccomp)
- **macOS**: network blocking is no-op
- **In-process network** (LLM API, web search) never affected

### 7.3 Auto-Allow Bash in Sandbox
```bash
GROK_SANDBOX_AUTO_ALLOW_BASH=1
# or config
[sandbox]
auto_allow_bash = true
```

---

## 8. ACP & HEADLESS MODE

### 8.1 ACP (Agent Client Protocol)
```bash
# Run as ACP agent over stdin/stdout
grok agent stdio
```
- **JSON-RPC** communication
- **IDE integrations**: Zed, Neovim, Emacs, marimo
- **WebSocket relay** for remote exposure
- **ACP SDK** for rich integration

### 8.2 Headless Scripting
```bash
# One-shot
grok -p "Refactor this function"

# Streaming JSON for parsing
grok -p "Analyze this code" --output-format streaming-json

# CI integration
grok -p "Run security audit" --single-turn --output-format json
```

### 8.3 Environment Variables for Headless
| Variable | Purpose |
|----------|---------|
| `XAI_API_KEY` | API key for non-browser auth |
| `GROK_SANDBOX` | Sandbox profile |
| `GROK_SUBAGENTS=1` | Enable subagents |
| `GROK_MEMORY=1` | Enable cross-session memory |
| `GROK_WEB_FETCH=1` | Enable web_fetch tool |

---

## 9. COST & SUBSCRIPTION

### 9.1 Pricing (2026)
| Tier | Cost | Includes |
|------|------|----------|
| **Launch Promo** | **$0** | **Grok 4.5 in Grok Build (limited time)** |
| **SuperGrok Heavy (standard)** | $300/mo | Grok Build + Grok 4/5 + SuperGrok + Heavy API |
| **SuperGrok Heavy (intro promo)** | $99/mo (6 mo) | Same as above |

> **Important**: The free Grok 4.5 access in Grok Build is a **limited-time launch offer** (July 2026). Verify current status at `x.ai/build`. After the promo ends, SuperGrok Heavy ($300/mo) is required.

### 9.2 Model Access
- **grok-4.5** — default coding model for Grok Build (launched July 8, 2026)
- **grok-code-fast-1** — previous coding-specialized model
- **Grok 4/5** — via SuperGrok Heavy subscription
- **Grok 4 Heavy** — via SuperGrok Heavy
- **xAI API** — separate developer product (usage-based, OpenAI-compatible SDK)

### 9.3 Cost Comparison
| Tool | Cost Model | Notes |
|------|------------|-------|
| Grok Build | $300/mo (Heavy) | Most expensive, only with 8-way parallelism |
| Claude Code | $20-$200/mo | Mature, broader toolkit |
| Codex CLI | Free install, API metered | OpenAI API costs |

### 9.4 Promo Window Playbook (While Grok 4.5 Is Free)

The Grok 4.5 launch promo is a **time-boxed opportunity**. Prioritize these while it lasts:

```
PRIORITY 1 — One-time setup that persists after promo:
  ☐ Create ~/.grok/rules/omega-mandates.md (M1/M7/M8/M13/M14/M23)
  ☐ Build local skills library in ~/.grok/skills/ (code-review, pack-finder)
  ☐ Configure sandbox profiles (workspace for dev, strict for untrusted)
  ☐ Test ACP integration (grok agent stdio) for IDE workflows

PRIORITY 2 — High-value exploratory work (uses 8-way parallelism):
  ☐ Run full-repo exploratory analysis on large modules
  ☐ Parallel sub-agent review of src/omega/ (8 sub-agents)
  ☐ Discover what to pack for Web Claude (Pattern C pipeline)

PRIORITY 3 — Template reusable workflows:
  ☐ Document any Grok CLI patterns that beat OpenCode CLI
  ☐ Log lessons to PACK_EVOLUTION_LOG.md
```

**When the promo ends**:
- Fall back to OpenCode CLI for local analysis
- Remove Grok CLI from rotation until SuperGrok Heavy budget allows
- **Do NOT build permanent automation on promo access** — the rules/skills files persist, but the model access does not

---

## 10. SOVEREIGN BOUNDARY PROTOCOLS

### 10.1 Mandates Affecting Grok CLI Usage
| Mandate | Impact |
|---------|--------|
| **M1 AnyIO** | All async code in generated artifacts must use AnyIO |
| **M7 Local-First** | **Grok Build is local-first by design** — snippet-only, no auto-upload. Aligns with M7. |
| **M8 Zero Telemetry** | xAI may collect usage data — verify with network audits |
| **M13 Temple-Grade** | T1-T11 gates apply to all generated artifacts |
| **M23 Failure Integrity** | No soft failures; hard stop on tool chain collapse |

### 10.2 IP Protection (Local-First Guarantee)
- **Architectural choice**: Only explicit snippets sent to cloud
- **`.gitignore` respected** by default — secrets excluded
- **No DPA published yet** (May 2026 beta) — for regulated projects, wait or limit to test repos
- **Verify with network traffic audits** before production use

### 10.3 PII Protection
- **Do not include PII** in prompts sent to Grok Build
- **Tokenize locally first** if working with sensitive data
- **Sandbox deny lists** for credential files (`**/.env`, `**/*.pem`)

---

## 11. QUICK REFERENCE

### Command Flags
| Flag | Description |
|------|-------------|
| `-p, --prompt` | Initial prompt |
| `--sandbox` | Sandbox profile (off/workspace/read-only/strict/custom) |
| `--rules` | Append rules to system prompt |
| `--system-prompt-override` | Replace system prompt |
| `--always-approve` / `-y` | Auto-approve all tool executions |
| `--allow` / `--deny` | Permission rules (glob patterns) |
| `--subagents` | Enable subagent/task tool |
| `--no-memory` | Disable cross-session memory |
| `--experimental-memory` | Enable cross-session memory |
| `--disable-web-search` | Remove web search tool |
| `--agent-profile` | Load custom agent definition |
| `--output-format` | `text` / `streaming-json` |
| `--single-turn` | Exit after first response |
| `--cwd` | Working directory |
| `--model` | Model ID |
| `--effort` | Reasoning effort |
| `--ref` | Git ref/branch/commit |
| `-w, --worktree` | Git worktree |

### Sandbox Profiles Quick Reference
| Profile | Read | Write | Network | Best For |
|---------|------|-------|---------|----------|
| `off` | All | All | All | Trusted, no restrictions |
| `workspace` | All | CWD + `~/.grok/` + temp | All | **Daily development** |
| `read-only` | All | `~/.grok/` + temp | Blocked (Linux) | Code review, audit |
| `strict` | CWD + sys | CWD + `~/.grok/` + temp | Blocked (Linux) | **Untrusted code** |

### Config Files
| File | Purpose |
|------|---------|
| `~/.grok/config.toml` | Main config (model, sandbox, tools, MCP) |
| `~/.grok/sandbox.toml` | Custom sandbox profiles |
| `~/.grok/rules/*.md` | Custom rules (appended to system prompt) |
| `~/.grok/skills/*.md` | Local skills (slash commands) |
| `.grok/config.toml` | Project-specific config override |
| `.grok/sandbox.toml` | Project-specific sandbox profiles |

---

## 12. SOURCE CITATIONS

### Tier 1: Official
- Grok Build Overview: https://docs.x.ai/build/overview
- Grok Build Sandbox: https://docs.x.ai/build/features/sandbox
- Grok Build CLI Reference: https://docs.x.ai/build/cli/reference
- Grok Build Settings: https://docs.x.ai/build/settings/reference
- Grok Build Announcement: https://x.ai/news/grok-build-cli (2026-05-25)
- Grok Build GitHub: https://github.com/xai-org/grok-build

### Tier 2: 2026 Technical Articles
- zenn.dev Format Comparison: https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31)
- Andrew.ooo Grok Build Analysis: https://andrew.ooo/answers/what-is-grok-build-may-2026/ (2026-05-27)
- Pasquale Pillitteri Review: https://pasqualepillitteri.it/en/news/2584/grok-build-xai-cli-2026 (2026-05-15)
- Collabnix Grok CLI Explained: https://collabnix.com/grok-cli-explained-what-people-are-searching-for-and-what-you-actually-get/ (2026)
- Pragmatic Engineer Pulse: https://newsletter.pragmaticengineer.com/p/the-pulse-groks-cli-caught-uploading (2026-07-16)

### Tier 3: Local Research (Evidence)
- `docs/research/R_GROK_CLI_ARCHITECTURE.md` — CLI architecture, components (CLI sections)
- `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` — Comprehensive research (CLI sections)
- `docs/research/R_GROK_ECOSYSTEM_DEEP.md` — Ecosystem deep dive (CLI sections)
- `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` — Knowledge gaps (CLI sections)

---

## 13. HYDRATION PROTOCOL

**Before any Grok CLI interaction, agents MUST:**
1. Read this document
2. Check free access status at `x.ai/build` (limited-time Grok 4.5 offer)
3. If free access expired: verify SuperGrok Heavy subscription active
4. Install Grok CLI: `curl -fsSL https://x.ai/cli/install.sh | bash`
5. Authenticate (browser OAuth or `XAI_API_KEY`)
6. Select sandbox profile (`workspace` for dev, `strict` for untrusted)
7. Configure custom rules for Omega Engine mandates (M1, M7, M8, M13, M23)
8. Set up local skills in `~/.grok/skills/` for reusable workflows
9. For headless/ACP: use `grok agent stdio` or `-p` with `--output-format streaming-json`
10. Log interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
