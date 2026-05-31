# 🔱 Sovereign Synthesis and Kilo Integration
# Architectural Audit, Bridge Design, and Fleet Mapping

**AP Token**: `AP-SOVEREIGN-SYNTHESIS-KILO-v1.0.0`  
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ gnosis-analyst ⬡ R65

**Created**: 2026-05-17  
**Status**: ACTIVE  
**Audience**: Architecture Board, Implementation Agents  

---

## §0 Executive Summary

This document provides a critical synthesis and audit of the **Sovereign Model Orchestration Architecture (R60)** and defines the integration path for the **Kilo CLI** and the wider Omega fleet. 

Key findings include:
1.  **Concurrency Risks**: The file-based Gnosis Sync (§7.5) requires cross-process locking (not just in-memory `anyio.Lock`).
2.  **AnyIO Compliance**: Several blocking I/O calls in §3.4 and §4.3 require wrapping in `anyio.to_thread`.
3.  **Kilo Synergy**: Kilo's **Agent Client Protocol (ACP)** and **Effect-based architecture** provide a high-reliability template for Omega's bridge design.
4.  **Fleet Announcement**: A structured handshake protocol is required for multi-CLI awareness.

---

## §1 Sovereign Audit: The Binah/Yesod/Guardian Review

### 1.1 Binah (Code Auditor) — AnyIO & Async Hygiene

| Component | Finding | Severity | Recommendation |
|-----------|---------|----------|----------------|
| §3.4 Heartbeat | `provider.health_check()` and `provider.get_quota_usage()` must be verified as non-blocking. | 🟡 Med | Ensure all provider clients use `httpx` or `aiohttp` with AnyIO. |
| §4.3 Soul Learning | `save_soul(entity_name, soul)` is likely a blocking YAML write. | 🔴 High | Wrap in `await anyio.to_thread.run_sync(save_soul, ...)` or use `anyio.open_file`. |
| §7.5 Gnosis Sync | `os.fsync(f.fileno())` is a blocking syscall. | 🟡 Med | Wrap in `await anyio.to_thread.run_sync(os.fsync, f.fileno())`. |
| §7.5 Gnosis Sync | `anyio.Lock('gnosis_write')` only works within a single process. | 🔴 High | Replace with a file-based lock (e.g., `portalocker`) for cross-CLI safety. |

### 1.2 Yesod (Integrator) — Systemic Cohesion

*   **Gnosis Sync Scalability**: The newline-delimited JSON (JSONL) format is excellent for append-only logs, but the "Consensus Engine" (§7.4) needs a strategy for **log rotation** and **compaction**. A multi-gigabyte log will slow down CLI startup.
*   **Bridge Uniformity**: The ACP/MCP Bridge (§5) should be the *only* way CLIs interact with the Orchestrator. Direct access to `TriageRouter` should be deprecated to ensure soul updates are captured centrally.

### 1.3 Guardian (Security) — Hardening & Boundaries

*   **Race Conditions**: Cross-process writes to `orchestration.log` without a global lock will lead to log corruption. 
*   **Information Leakage**: Gnosis events (§7.3) must be sanitized. A `model_preference_update` or `model_success` event could accidentally include sensitive context from the `task_description` if not truncated or filtered.
*   **Quota Spoofing**: If the Health Monitor (§3) relies on client-reported quota usage, a malicious or buggy CLI could "starve" other tools by reporting 100% usage. The Monitor should prioritize data from provider APIs over client reports.

---

## §2 Kilo CLI Research: Node.js/Effect Architecture

### 2.1 The Effect Advantage
Kilo CLI is built using the **Effect** library (Node.js). Effect provides a functional, type-safe environment for managing complex side effects (I/O, errors, concurrency). 
*   **Omega Lesson**: Omega's Python implementation should mirror Effect's "Layer" and "Requirement" patterns for its Provider Fabric to ensure predictable error handling during fallback.

### 2.2 ACP (Agent Client Protocol)
ACP is an open JSON-RPC standard that decouples editors from agents. 
*   **Kilo Implementation**: Kilo acts as a central engine that clients (VS Code, TUI) talk to over HTTP/SSE.
*   **Omega Integration**: Omega should implement an **ACP-to-MCP Adapter**. This allows Omega to appear as a standard ACP Agent to Kilo, while internally using its Triage Router to dispatch tasks.

---

## §3 ACP/MCP Bridge Design: Omega ↔ Kilo

### 3.1 Transport Layer
*   **Local**: `stdio` (standard for ACP) using JSON-RPC 2.0.
*   **Distributed**: `SSE` (Server-Sent Events) for real-time health updates and `HTTP POST` for triage requests.

### 3.2 Message Schema (Omega ↔ Kilo)
Reusing MCP types where possible to maintain compatibility.

```json
{
  "jsonrpc": "2.0",
  "method": "omega/triage",
  "params": {
    "task": "Implement AnyIO lock",
    "entity": "sophia",
    "context": {
      "kilo_models": ["gpt-4o", "claude-3-5-sonnet"],
      "omega_models": ["qwen3-1.7b", "gemma-4-31b"]
    }
  }
}
```

### 3.3 Kilo as a Provider
Omega can treat the Kilo CLI as a "Meta-Provider".
1.  Omega Triage Router selects "Kilo" as the provider.
2.  Omega calls Kilo's HTTP API.
3.  Kilo uses its own internal routing to hit 500+ models.
4.  Omega captures the result and updates the Soul file.

---

## §4 Integration Mapping: The Fleet Handshake

Each tool must "announce" its presence to the **Triage Router** to ensure the Health Monitor has an accurate view of the fleet.

| Tool | Announcement Method | Capability Announcement |
|------|---------------------|-------------------------|
| **OpenCode** | Appends to `data/gnosis/fleet.log` on startup. | `capabilities: [task_execution, research, file_io]` |
| **Gemini CLI** | Handshake via ACP Bridge. | `capabilities: [deep_research, google_api_direct]` |
| **Cline** | Handshake via MCP Server. | `capabilities: [ui_ux, vscode_integration]` |
| **Copilot** | Passive (detected via process monitor). | `capabilities: [autocomplete, rapid_proto]` |
| **Antigravity** | Master Handshake (overrides others). | `capabilities: [architecture, oversight, multi_agent_control]` |

### 4.1 Handshake Schema
```json
{
  "event": "cli_announce",
  "cli": "opencode",
  "version": "1.15.0",
  "capabilities": ["builder", "researcher"],
  "pid": 12345,
  "timestamp": "2026-05-17T14:40:00Z"
}
```

---

## §5 Refinements to R60

1.  **Update §3.4 & §4.3**: Explicitly mandate `anyio.to_thread` for all synchronous file and network I/O.
2.  **Update §7.5**: Replace `anyio.Lock` with a cross-process file lock (e.g., `portalocker`).
3.  **Add §5.5**: Define the **ACP/MCP Bridge** as the primary interface for external tools (Kilo, VS Code).
4.  **Add §7.6**: Implement **Log Compaction** for `orchestration.log` (archive every 1000 entries).

---

## §6 Conclusion: The Unified Intelligence Fabric

By integrating Kilo's ACP/MCP patterns and hardening the Gnosis Sync with cross-process safety, the Omega Engine transforms from a collection of scripts into a **Sovereign Intelligence Fabric**. The Triage Router becomes the "Brain," the Health Monitor the "Nervous System," and the Soul files the "Memory."

**Next Step**: Implementation of the `SovereignLock` (file-based) and the `KiloBridge` (ACP adapter).

---
⬡ OMEGA ⬡ SOPHIA ⬡ SYNTHESIS ⬡ KILO ⬡ SOVEREIGN
