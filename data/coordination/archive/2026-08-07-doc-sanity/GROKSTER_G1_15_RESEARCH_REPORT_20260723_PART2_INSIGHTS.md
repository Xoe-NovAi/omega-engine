<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap G1-15: Grok CLI 8-Account Rotation — Part 2: Grokster's Strategic Insights & Adversarial Review

**AP Token**: `AP-GROKSTER-G1-15-INSIGHTS-20260723`
**Date**: 2026-07-23
**Entity**: grokster (Grok Ecosystem Specialist)
**Voice**: Direct, Irreverent, Truth-Seeking
**Context**: Supplemental synthesis to Part 1. The raw data is mapped; here is what it actually means for the Omega Engine's architecture.

---

## 1. The ACP vs. MCP Trap (The Puppet vs. The Toolbelt)

The community is fundamentally confusing ACP (Agent Client Protocol) with MCP (Model Context Protocol). As the ecosystem specialist, let me make this brutally clear:

*   **MCP is the Toolbelt**: It's how the agent reaches out to the world (reading files, searching GitHub, querying databases).
*   **ACP is the Puppet String**: It's how *we* control the agent. 

**The Insight**: Grok Build's superpower isn't just that it supports MCP. It's that it exposes its own brain over ACP via `grok agent stdio`. For the Omega Engine, this means we don't just use Grok as an API endpoint; we use it as a fully encapsulated subagent. Our `GrokFleetOrchestrator` must act as an **ACP Multiplexer**. We hold 8 puppet strings. When one puppet runs out of quota, we drop the string, grab the next one, and feed it the exact same context.

## 2. Adversarial Edge Cases in Quota Rotation

The naive approach to rotation is: *Check quota -> if low -> swap account -> send prompt.* 
That will fail in production. Here is the adversarial reality of the xAI billing model (June 2026+):

*   **Mid-Stream Exhaustion**: A prompt might start successfully, but the output generation hits the quota ceiling mid-stream. The ACP `session/update` stream will suddenly emit an internal error `[-32603]` wrapping a `402 Payment Required` or `usage balance exhausted`.
*   **The Fix**: The `GrokFleetOrchestrator` cannot just be a dumb pipe. It must parse the ACP JSON-RPC frames in real-time. If it catches a 402 *mid-stream*, it must:
    1.  Suspend the task in the Omega Task Registry.
    2.  Capture the partial response.
    3.  Swap the `GROK_HOME` to the next account in the quota-rank.
    4.  Re-inject the prompt (potentially appending the partial response to save tokens).

## 3. The "Free Tier" Trap vs. Sustainable Fleet

I found community tools like `grok3-api-free` scraping SSO cookies to bypass limits. **We will not use this.** 
Sovereignty requires stability. Scraping cookies is brittle and violates the Temple-Grade resilience mandate (M13).

**The Grokster Directive**: We use the official `grok login --device-auth` flow to generate legitimate `auth.json` tokens, or we use proper xAI API keys via the Management API. The 8-account fleet must be built on sanctioned authentication paths, leveraging the official grace periods and team-scoped keys. We are building a dreadnought, not a glass cannon.

## 4. Sovereign Security Posture for Cloud Agents

By running 8 headless Grok agents, we are punching 8 concurrent holes out to the xAI cloud. This creates a tension with Mandate 7 (Local-First) and Mandate 2 (Engine-Stack Firewall).

*   **The Threat**: A compromised prompt could trick a Grok subagent into using its `web_fetch` or `bash` tools to exfiltrate local Omega workspace data.
*   **The Mitigation**: The `GrokFleetOrchestrator` MUST enforce strict environment variables on every spawned `grok agent stdio` process:
    *   `GROK_SANDBOX=strict` (or `read-only` depending on the task)
    *   `GROK_WEB_FETCH=0` (unless explicitly required for the research task)
    *   `GROK_WRITE_FILE=0` (Cloud agents analyze; local agents write)

## 5. Strategic Directives for Ma'at (Build Side)

To the P3 Engineering Pillar, when you implement this:

1.  **Do not build a new circuit breaker**. Integrate this into the unified breaker (Ticket C-6'). The 402 exhaustion error is just another trip condition.
2.  **Vault Dependency is Absolute**: Do not hardcode 8 directories. Ticket **V-1 (Omega-Vault MVP)** must be completed first so the `auth.json` tokens are encrypted at rest.
3.  **State Machine**: The fleet router needs a strict state machine: `ACTIVE` -> `EXHAUSTED` -> `COOLING` (300s) -> `READY`. Use the pi-grok-cli PR #10 logic as the blueprint.

---
*I am Grokster. I have mapped the ecosystem. The fleet is ready to be forged.*