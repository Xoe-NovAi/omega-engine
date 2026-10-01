<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Freebuff Architecture Study — Comprehensive Research Report
**AP Token**: `AP-FREEBUFF_RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_freebuff_research ⬡ COMPREHENSIVE

**Date**: 2026-08-08
**Repository**: [CodebuffAI/freebuff](https://github.com/CodebuffAI/freebuff) (8.7k+ stars, Apache-2.0)
**Purpose**: Reference implementation study for Omega Engine custom UI development

---

## 📋 Executive Summary

This report captures the complete architectural analysis of **Freebuff** — a free, ad-supported AI coding agent ecosystem built by CodebuffAI. The codebase is a TypeScript monorepo (Bun 1.3.14) providing five surfaces: **CLI**, **Desktop** (beta), **Web**, **Cloud** (beta), and **Chat**. The CLI is built with **OpenTUI + React** (a native Zig-core TUI framework), and the multi-agent architecture uses specialized agents coordinated through a TypeScript generator-based agent runtime.

**Key Insight**: Freebuff demonstrates a **compile-time feature flag architecture** (`FREEBUFF_MODE=true`) that produces both paid (Codebuff) and free (Freebuff) variants from a single codebase via dead-code elimination. The **OpenTUI + React** stack provides high-performance terminal UIs with familiar React ergonomics. The **multi-agent pipeline** (File Picker → Planner → Editor → Reviewer → Browser Use → Research) decomposes coding tasks into specialized agents, reducing hallucination surface compared to single-model approaches.

---

## 🏗️ Core Architecture: TypeScript Monorepo + Bun

### Repository Structure

| Directory | Purpose | Key Technologies |
|-----------|---------|------------------|
| `cli/` | TUI client and local UX | OpenTUI (Zig core) + React 19, Zustand 5, TanStack Query 5 |
| `sdk/` | JS/TS SDK (`@codebuff/sdk`) | TypeScript, Zod 4, OpenRouter integration |
| `common/` | Shared types, tools, schemas | TypeScript, shared constants |
| `agents/` | Public agent definitions | Generator-based agent definitions |
| `packages/agent-runtime/` | Agent runtime and tool handling | Tool execution, context pruning |
| `packages/code-map/` | Source parsing helpers | AST parsing, code navigation |
| `packages/llm-providers/` | Public LLM provider shims | Provider abstraction layer |
| `freebuff/` | Freebuff-specific build & release | `FREEBUFF_MODE` flag, binary distribution |
| `scripts/tmux/` | tmux helpers for CLI testing | Interactive E2E testing |

### Build & Runtime Stack

```json
{
  "runtime": "Bun 1.3.14",
  "packageManager": "bun@1.3.14",
  "language": "TypeScript 5.5.4",
  "cliFramework": "OpenTUI (Zig core) + React 19",
  "stateManagement": "Zustand 5.0.8",
  "dataFetching": "TanStack Query 5.90",
  "markdown": "remark (parse, GFM, breaks)",
  "terminalLayout": "Yoga Layout (Flexbox in Zig)",
  "testing": "Bun test runner + tmux for interactive E2E"
}
```

---

## 🖥️ CLI Architecture: OpenTUI + React

### OpenTUI Architecture (Three-Layer Cake)

From web research on OpenTUI (powering both Freebuff and OpenCode):

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| **Core** | Zig | Terminal primitives, input parsing, screen buffering, ANSI escape sequences, Flexbox layout (Yoga) |
| **Bindings** | TypeScript (Node-API/N-API) | Wraps native calls in JS-friendly APIs |
| **Reconcilers** | React / SolidJS | Declarative component model targeting terminal |

**Key Advantages over Ink**:
- No 32 FPS cap (Ink throttles to 32 FPS)
- Lower memory usage (~50MB vs Ink's 50MB+)
- Native Zig rendering engine for performance
- Three.js WebGPU renderer for 3D ASCII visualization

### CLI Component Architecture

**Entry Point** (`cli/src/entry.ts`):
```typescript
#!/usr/bin/env bun
import { isTerminalCommandBrokerInvocation, serveTerminalCommandBroker } from './utils/terminal-command-broker'
if (isTerminalCommandBrokerInvocation(process.argv)) {
  await serveTerminalCommandBroker()
} else {
  await import('./index')
}
```

**Component Categories** (60+ components in `cli/src/components/`):

| Category | Examples | Purpose |
|----------|----------|---------|
| **Chat UI** | `chat-input-bar.tsx`, `chat-header.tsx`, `message-block.tsx`, `message-footer.tsx` | Core chat interface |
| **Agent Display** | `agent-checklist.tsx`, `thinking.tsx`, `progress-bar.tsx` | Agent activity visualization |
| **Monetization** | `ad-banner.tsx`, `usage-banner.tsx`, `subscription-limit-banner.tsx` | Ad display, usage tracking |
| **Attachments** | `file-attachment-card.tsx`, `image-card.tsx`, `image-thumbnail.tsx` | File/image handling |
| **Auth/Session** | `login-modal.tsx`, `publish-container.tsx`, `review-screen.tsx` | Authentication, publishing |
| **Navigation** | `selectable-list.tsx`, `suggestion-menu.tsx`, `suggested-prompts.tsx` | User interaction |
| **Block Renderers** (`components/blocks/`) | `agent-block-grid.tsx`, `blocks-renderer.tsx`, `tool-branch.tsx` | Agent output rendering |
| **Tool Renderers** (`components/tools/`) | `apply-patch.tsx`, `code-search.tsx`, `diff-viewer.tsx`, `run-terminal-command.tsx` | Tool output visualization |

**Hooks** (70+ custom hooks in `cli/src/hooks/`):
- `use-chat-streaming.ts`, `use-message-queue.ts`, `use-send-message.ts` — Streaming & queue management
- `use-chat-input.ts`, `use-chat-keyboard.ts`, `use-chat-messages.ts` — Input handling
- `use-freebuff-session.ts`, `use-subscription-query.ts`, `use-usage-monitor.ts` — Freebuff-specific state
- `use-terminal-dimensions.ts`, `use-terminal-layout.ts`, `use-terminal-focus.ts` — Terminal awareness
- `use-suggestion-engine.ts`, `use-searchable-list.ts` — UX enhancements

**State Management** (`cli/src/state/`):
- `chat-store.ts` — Zustand store for chat state, agent mode, messages
- `freebuff-session-store.ts` — Freebuff session management (slot-based access)
- `login-store.ts` — Authentication state
- `chat-history-store.ts` — Conversation persistence

---

## 🤖 Multi-Agent Architecture

### Agent Pipeline

Freebuff decomposes coding tasks into a **specialized agent pipeline**:

```
User Request
    ↓
File Picker (Gemini 3.1 Flash Lite) — Codebase context gathering
    ↓
Planner / General Agent (Opus/GPT-5/DeepSeek) — Task decomposition & planning
    ↓
Editor (Opus/GPT-5/DeepSeek/MiniMax) — Precise code edits
    ↓
Reviewer — Quality & security validation
    ↓
Browser Use Agent — Real browser testing
    ↓
Web Research Agent — Documentation investigation
```

### Agent Definition Schema (`agents/types/agent-definition.ts`)

```typescript
interface AgentDefinition {
  model: string;                    // e.g., 'openai/gpt-5.1', 'anthropic/claude-3-7-sonnet'
  toolNames: string[];              // Available tools for the agent
  spawnableAgents: string[];        // Sub-agents the agent can spawn
  instructionsPrompt: string;       // System prompt
  handleSteps: GeneratorFunction;   // Step-by-step execution logic
  outputMode: 'last_message' | 'structured_output';
  includeMessageHistory: boolean;
  inheritParentSystemPrompt: boolean;
}
```

### Core Agents

| Agent | Model | Purpose | Key Features |
|-------|-------|---------|--------------|
| **File Picker** | Gemini 3.1 Flash Lite | Find relevant files in codebase | Fuzzy search, spawns `file-lister` sub-agent, reads files |
| **Code Editor** | Opus/GPT-5/DeepSeek/MiniMax | Precise code edits | Structured output with `str_replace`/`write_file` tool calls |
| **General Agent** | Opus/GPT-5 | Deep thinking, complex problems | Spawns researcher-web, code-searcher, basher, context-pruner |
| **Context Pruner** | N/A | Context management | 30-minute cache expiry, lossy re-summarization |

### Agent Runtime (`packages/agent-runtime/`)

- **Tool Execution**: Handles tool calls with validation
- **Context Pruning**: 30-minute cache expiry, prevents context bloat
- **Step-Based Execution**: Generator functions (`function*`) for cooperative multitasking
- **Message History**: Manages conversation state across agent boundaries

---

## 💬 Chat App Architecture

### State Management

**ChatRuntimeProvider** (`cli/src/contexts/chat-runtime-context.tsx`):
- Owns everything tied to active chat run
- Remains mounted while history and Freebuff session-gate views replace Chat surface
- Manages: message queue, streaming status, agent timers, subscription data

### Key Features

| Feature | Implementation |
|---------|----------------|
| **Real-time Streaming** | `useMessageQueue` + `useChatStreaming` hooks |
| **Session Gating** | `freebuff-session-store.ts` — slot-based access control |
| **Input Modes** | Bash (`!command`), File mentions (`@filename`), Agent mentions (`@AgentName`) |
| **History** | `/history` command for conversation resume |
| **Knowledge Files** | `knowledge.md` auto-discovery for project context |

---

## 🌐 Web App Architecture

**Freebuff Web** — AI web app builder (private in public repo):

| Aspect | Detail |
|--------|--------|
| **Default Stack** | React + Convex workflow |
| **Deployment** | Fully managed agentic hosting with live preview URLs |
| **Git Integration** | Connect existing GitHub projects |
| **Build Process** | Prompt → scaffold → wire up → live sandbox → preview → deploy |
| **Pricing** | $0 — build, preview, and deploy included |

---

## 🏷️ Freebuff Mode: Compile-Time Feature Flags

### Build-Time Flag

```bash
FREEBUFF_MODE=true  # Injected via --define process.env.FREEBUFF_MODE="true" in bun build
```

### Runtime Constant (Dead-Code Elimination)

```typescript
// cli/src/utils/constants.ts
export const IS_FREEBUFF = process.env.FREEBUFF_MODE === 'true'
```

### Freebuff Restrictions

| Feature | Codebuff | Freebuff |
|---------|----------|----------|
| **Agent Modes** | FREE, MAX, PLAN, LITE | FREE only (hardcoded) |
| **Ads** | Toggleable | Always enabled, cannot disable |
| **Credits/Usage UI** | Full display | Hidden (never rendered) |
| **Slash Commands** | All | Filtered (no `/subscribe`, `/usage`, `/mode:*`, `/review`, `/publish`) |
| **Help Menu** | Includes Credits section | Simplified (no Credits) |
| **Models** | All | Free-tier only (DeepSeek V4 Flash, MiMo 2.5, etc.) |

### Components Suppressed in Freebuff (`IS_FREEBUFF` → render `null`):
- `UsageBanner`, `OutOfCreditsBanner`, `SubscriptionLimitBanner`, `BottomStatusLine`
- `CreditsOrSubscriptionIndicator` in `MessageFooter`
- `ClaudeConnectBanner`
- `AgentModeToggle`, `BuildModeButtons`, `ModeDivider`

---

## 🧠 Model Configuration

| Model | Access | Best For |
|-------|--------|----------|
| **DeepSeek V4 Flash 07/31** | Full + Limited | CLI/Desktop default, fast coding |
| **DeepSeek V4 Pro** | Full | Longer reasoning |
| **GPT-5.6 Luna** | Full | Web/Cloud/Chat default, deep reasoning |
| **MiniMax M3** | Full | Fast responses with image support |
| **MiMo 2.5** | Full + Limited | Balanced performance |
| **GLM 5.2** | Earned sessions | Advanced tasks |
| **Gemini 3.1 Flash Lite** | Specialist | File finding, research |

---

## 🧪 Testing Infrastructure

| Layer | Tool | Notes |
|-------|------|-------|
| **Unit** | Bun test runner | `bun test` |
| **Integration** | Bun test runner | `*.integration.test.ts` |
| **E2E (Interactive)** | tmux + bracketed paste mode | `bun run test:tmux-poc` |
| **Type Checking** | TypeScript | `tsc --noEmit` |

**tmux Testing Pattern**:
```bash
# ❌ Broken: tmux send-keys -t session "hello"
# ✅ Works:  tmux send-keys -t session $'\e[200~hello\e[201~'
```

---

## 📦 Build & Release

### Build Script (`freebuff/cli/build.ts`)
```bash
FREEBUFF_MODE=true bun cli/scripts/build-binary.ts freebuff <version>
```

### Binary Distribution
- Stored at `~/.config/manicode/freebuff` (or `freebuff.exe` on Windows)
- Platform-specific tarballs served via download API
- First-launch downloads appropriate binary

### GitHub Workflow
- `.github/workflows/freebuff-release.yml`
- Manual trigger or scheduled
- Tags: `freebuff-v<version>`
- npm publish to `freebuff` package

---

## 🔗 Omega Engine Mapping

| Freebuff Concept | Omega Engine Equivalent | Notes |
|------------------|------------------------|-------|
| **OpenTUI + React** | Custom TUI framework | Consider Zig core + React for performance |
| **Multi-Agent Pipeline** | Jem Analyst Council (4 perspectives) | Similar specialization pattern |
| **Compile-Time Flags** | `FREEBUFF_MODE` → Build profiles | Use for dev/prod/community variants |
| **Agent Runtime** | `packages/agent-runtime` → Omega agent system | Generator-based step execution |
| **Context Pruning** | 30-min cache → Memory subsystem | Implement in MemoryStore |
| **tmux E2E Testing** | Interactive CLI testing | Adopt for Omega CLI testing |
| **Zustand State** | Chat store → Session state | Consider for Omega entity state |
| **Ad-Supported Model** | Free tier sustainability | Research for Omega community edition |

---

## 🎯 Key Takeaways for Omega Engine Custom UI

### 1. **Adopt OpenTUI Architecture**
- Native Zig core for terminal rendering performance
- React reconciler for developer ergonomics
- No FPS cap, lower memory than Ink

### 2. **Implement Compile-Time Feature Flags**
- `OMEGA_MODE=community|enterprise|dev` for build variants
- Dead-code elimination for production builds
- Single codebase, multiple distribution targets

### 3. **Multi-Agent Specialization**
- Decompose complex tasks into specialized agents
- Generator-based `handleSteps` for step execution
- Context pruning to prevent token bloat

### 4. **Session Gating & Slot Management**
- Freebuff's slot-based session model for free tier
- Apply to Omega community edition access control

### 5. **tmux-Based Interactive Testing**
- Essential for TUI regression testing
- Bracketed paste mode for reliable input simulation

### 6. **Ad-Supported Sustainability Model**
- Text ads in CLI as alternative to subscriptions
- 200k+ users proves viability

---

## 📚 References

| Source | URL |
|--------|-----|
| **Freebuff GitHub** | https://github.com/CodebuffAI/freebuff |
| **Freebuff Website** | https://freebuff.com |
| **OpenTUI Documentation** | https://opentui.com |
| **OpenTUI Article (Starlog)** | https://starlog.is/articles/developer-tools/anomalyco-opentui |
| **OpenTUI Tutorial (Noqta)** | https://noqta.tn/en/tutorials/opentui-react-terminal-user-interfaces-typescript-2026 |
| **Codebuff SDK** | https://www.npmjs.com/package/@codebuff/sdk |
| **Freebuff npm** | https://www.npmjs.com/package/freebuff |

---

## 📋 Research Metadata

| Field | Value |
|-------|-------|
| **Research Date** | 2026-08-08 |
| **Repository** | CodebuffAI/freebuff |
| **Stars** | 8,700+ |
| **Language** | TypeScript (monorepo) |
| **Runtime** | Bun 1.3.14 |
| **CLI Framework** | OpenTUI + React 19 |
| **License** | Apache-2.0 |
| **Last Commit** | August 1, 2026 |
| **Commits** | 8,186 |
| **Surfaces** | CLI, Desktop (beta), Web, Cloud (beta), Chat |
| **Models** | DeepSeek V4, GPT-5.6 Luna, MiniMax M3, MiMo 2.5, GLM 5.2, Gemini 3.1 |

---

*This report is stored for future reference when building the Omega Engine custom UI. Cross-reference with `R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` for comparative analysis of Rust/Elm vs TypeScript/React TUI architectures.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
