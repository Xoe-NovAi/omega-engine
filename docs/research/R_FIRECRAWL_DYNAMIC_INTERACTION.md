# 🔱 Omega Engine — R-03 Firecrawl Dynamic Interaction
# ⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ R03

**AP Token**: `AP-RESEARCH-R03-v1.0.0`
**Author**: researcher (Sovereign Master Researcher)
**Date**: 2026-06-09
**Status**: READY

---

## Summary
This document details the capabilities of Firecrawl's `/interact` endpoint, which enables stateful browser sessions for interacting with dynamic web content. It analyzes the three execution modes (Prompt, Node.js, Python/Bash) and the mechanism for persistent browser profiles, providing a blueprint for automating complex, multi-step web workflows.

## Findings

### 1. The Interaction Lifecycle
Interaction is a three-stage process:
1. **Initialization**: A `/scrape` call is made, returning a `scrapeId`.
2. **Execution**: One or more `/interact` calls are made using the `scrapeId`. The browser session remains open, preserving state (DOM, cookies, scroll position) between calls.
3. **Termination**: A `DELETE` call to the interact endpoint stops the session and saves profile changes.

### 2. Execution Modes

| Mode | Interface | Control Level | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Prompting** | Natural Language | Low (Agentic) | Simple tasks: "Click login", "Search for X" |
| **Node.js** | Playwright API | High (Deterministic) | Complex logic, precise selectors, custom JS |
| **Python** | Playwright API | High (Deterministic) | Data science pipelines, Python-based automation |
| **Bash** | `agent-browser` CLI | Medium (LLM-Optimized) | Rapid prototyping, accessibility-tree based navigation |

### 3. `agent-browser` (Bash Mode)
The `agent-browser` tool is a specialized CLI that simplifies browser interaction for LLMs by providing an **Accessibility Tree**.
- **Element Refs**: Elements are tagged with refs (e.g., `@e1`, `@e2`).
- **Commands**:
    - `snapshot -i`: Returns only interactive elements.
    - `click @e1`: Clicks the referenced element.
    - `fill @e1 "text"`: Clears and types into a field.
    - `get text @e1`: Extracts text from an element.

### 4. Persistent Profiles
Firecrawl allows the creation of named profiles to persist browser state across different sessions.
- **Mechanism**: Pass a `profile` object (`{ "name": "my-profile", "saveChanges": true }`) to the initial `/scrape` call.
- **State Preservation**: Cookies, `localStorage`, and session data are saved when the interact session is stopped.
- **Read-Only Mode**: Setting `saveChanges: false` allows multiple concurrent sessions to use the same profile without modifying it.
- **Use Case**: Bypassing login screens by saving a session cookie.

### 5. Live View & Debugging
Every interaction returns a `liveViewUrl` and an `interactiveLiveViewUrl`.
- **Live View**: Read-only stream of the browser.
- **Interactive Live View**: Allows a human user to take control of the browser session via an embedded iframe.

## Recommendations

1. **Decompose Complex Workflows**: Instead of one massive prompt, break interactions into a sequence of small, focused `interact` calls.
2. **Use `agent-browser` for LLM-Driven Loops**: When building an autonomous agent, use Bash mode with `snapshot -i` to provide the agent with a clean, reference-based view of the page.
3. **Implement Profile Rotation**: For large-scale scraping of authenticated sites, maintain a pool of named profiles to distribute load and avoid detection.

## Sources
- [Firecrawl Interact Docs](https://docs.firecrawl.dev/features/interact) — accessed 2026-06-09
- [agent-browser GitHub](https://github.com/vercel-labs/agent-browser) — accessed 2026-06-09
- File: `.firecrawl/feature-interact.md`

## Implementation Note
_For: P6 Cognition / ModelGateway_
The `ModelGateway` should implement a `BrowserSession` class that manages the `scrapeId` and the lifecycle of the interaction. It should provide a high-level `execute_action(prompt_or_code)` method that handles the `POST` requests to the `/interact` endpoint and ensures `stop_interaction()` is called upon session expiry or task completion.
