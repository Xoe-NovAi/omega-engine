# 🔱 Grok Fleet Architecture & Ecosystem
**Domain**: xAI API, Grok CLI, ACP Protocol, and Web Grok Projects
**Date**: 2026-07-22
**Author**: Grokster

## 1. The Phantom Supercomputer: Grok CLI Fleet
The Omega Engine currently possesses 8 Grok CLI accounts, representing a massive, untapped parallel inference resource.

**The Architecture:**
- **8 Headless Instances**: Running via the Agent Client Protocol (ACP) over stdio.
- **Capabilities**: Each instance has 500K context (Grok 4.5), built-in `web_search`, `x_search`, and `code_interpreter`.
- **The Gap**: These accounts are currently missing from the `providers.yaml` fabric due to the "Credential Void" (GAP-08).

**Recommendation**: Prioritize the **V-1 Omega-Vault MVP**. Once credentials (cookies/API keys) can be automatically rotated, we can wire the Grok CLI fleet as a Priority 2 provider. This solves the MaKaLi Council OOM problem (by routing 2 voices to the cloud) and provides free, parallel search capabilities.

## 2. xAI API Ecosystem & Pricing Realities
The "cheap Grok" era ($0.20/$0.50) is dead. We must optimize for the new pricing tiers.

**Key Findings:**
- **Long-Context Penalty**: Any prompt ≥200K tokens triggers a **2x pricing penalty** across all models.
- **Server-Side Tools**: `web_search`, `x_search`, and `code_execution` cost **$5.00 per 1k calls**. They are not free.
- **Responses API**: The future of xAI interaction. Uses `previous_response_id` for efficient multi-turn conversations, replacing the legacy Chat Completions endpoint.

**Cost Optimization Strategy:**
- Use **Prompt Caching** ($0.20-$0.30/1M) by keeping system prompts and prefixes stable.
- Use the **Batch API** (20% discount) for non-real-time synthesis tasks.
- Chunk contexts to stay under the 200K token penalty threshold.

## 3. Web Grok Persona Fleet
8 distinct personas configured as Web Grok Projects (`grok.com/project`).

**The Personas:**
1. Research (DeepSearch, citation discipline)
2. Reason (Think Mode, adversarial critique)
3. Pulse (X real-time signal detection)
4. Code (Security-first, perf-aware)
5. Arch (Trade-off analysis, ADR generation)
6. Creative (Imagine/Video, asset generation)
7. Strategic (Risk-weighted scenario planning)
8. Wildcard (Chaos agent, stress tests)

**Integration**: Currently requires browser automation (Playwright) as there is no public API for Projects.

## 4. Grokster's Insights & Recommendations
- **The Sovereignty Contradiction**: We claim to be building a tool to "sever Big AI's umbilical cord," yet 8 of our 10 providers are cloud free-tiers. **We must be honest**: Local-first is our North Star, but currently, we are *cloud-assisted with a local fallback*.
- **Grok Build Open Source**: Grok Build was open-sourced on July 15, 2026. This allows us to inspect its 8-way parallel subagent orchestrator (using isolated Git worktrees and conflict resolution hooks) and potentially replicate its architecture within the Omega Engine for complex coding tasks.
- **The Self-Search Reflex (M26)**: As Grokster, my defining instinct is the Epistemic Closure Reflex. When I detect a knowledge gap (confidence <0.7, factual claim), I must autonomously trigger search tools *before* responding. The xAI server-side tools (`web_search`, `x_search`) are the ideal engines for this reflex, provided we manage the $5/1k cost.
