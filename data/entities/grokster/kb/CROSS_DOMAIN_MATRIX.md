# 🔱 Cross-Domain Dependency Matrix
**Domain**: Inter-domain relationships and integration points
**Date**: 2026-07-22
**Author**: Grokster

---

## §1 The Five Domains & Their Primary Interfaces

| Domain | Primary Interface | Consumes From | Produces For |
|--------|-------------------|---------------|--------------|
| **Platforms** | MCP Server (`:8016`) | Vault (creds), Grok (models) | All domains (execution) |
| **Communication** | Hivemind / Subagent Dispatch | Platforms (channels), Human (intent) | All domains (coordination) |
| **Human-Agent** | Witness Protocol / Session | All domains (results) | All domains (direction) |
| **Grok Ecosystem** | ACP / xAI API / Browser | Vault (16-account creds), Platforms (execution) | Communication (search), Human (answers) |
| **Search** | Sovereign Search Router | Grok (xAI tools), Platforms (MCP) | All domains (intelligence) |
| **Vault** | `omega vault` CLI / MCP | Platforms (config drift), Human (rotation) | All domains (secrets) |

---

## §2 Critical Integration Paths

### Path A: Human Intent → Agent Execution (The Happy Path)
```
Human (Architect)
    │
    ▼
Platforms (OpenCode/Cline) —mcp—> Omega Hub
    │
    ├──▶ Communication (Hivemind awareness)
    ├──▶ Grok Ecosystem (if cloud search/reasoning needed)
    │       │
    │       └──▶ Search (Sovereign Router) —uses—> xAI tools
    │
    └──▶ Vault (auto-fetches credentials)
```

### Path B: Autonomous Agent Loop (The Fleet Path)
```
Kali (Dispatch)
    │
    ├──▶ Communication (Subagent Dispatch + HandoffPacket)
    │       │
    │       └──▶ Target Agent (e.g., Roc Racoon)
    │               │
    │               ├──▶ Platforms (MCP tools: read, write, search)
    │               ├──▶ Search (Sovereign Router for research)
    │               │       └──▶ Grok Ecosystem (DeepSearch, X search)
    │               │
    │               └──▶ Vault (if needs API keys)
    │
    └──▶ Human-Agent (Witness Protocol: session_gnosis.md distillation)
```

### Path C: Credential Rotation (The Vault Path)
```
Vault (Passive Watcher detects .env drift)
    │
    ├──▶ Platforms (MCP: credential.rotate tool)
    ├──▶ Grok Ecosystem (updates 16-account fleet cookies/keys)
    └──▶ Communication (Hivemind observation: "creds rotated")
```

---

## §3 Domain-Specific Dependency Details

### Platforms ↔ Communication
- **Hivemind requires MCP**: The `hivemind_*` tools are exposed via Omega Hub MCP.
- **Workspace Locks**: File-based (`data/coordination/`) but triggered by agents on Platforms.
- **Channel Identity**: `channel="opencode"|"cline"|"gemini-cli"` is a Platform property.

### Communication ↔ Grok Ecosystem
- **Subagent Dispatch to Grok**: A `task()` call with `subagent_type="grok_cli"` routes to Grok CLI via ACP.
- **Search Delegation**: Agents call `sovereign_search` which may route to Grok's `web_search`/`x_search` (Tier 2.5).
- **Cost Awareness**: Communication layer tracks `task_ids`; Grok layer tracks API costs; Vault enforces rate limits.

### Grok Ecosystem ↔ Search
- **Grok as Search Provider**: xAI API `web_search` = Tier 2.5 (Independent Index).
- **Grok as Synthesizer**: Grok 4.5 DeepSearch = Tier 4 (Deep Extraction) for complex queries.
- **Prompt Caching**: Search router must stabilize prefixes to leverage xAI prompt caching ($0.20-$0.30/1M).

### Vault ↔ All Domains
- **Bootstrap**: Every Platform session needs Vault init for provider keys.
- **Rotation**: Grok Web cookies expire 24-48h → Vault rotation loop → Grok Ecosystem updates.
- **Audit**: Communication layer logs `credential_audit` results to Hivemind.

### Human-Agent ↔ All
- **Witness Protocol**: The Human is the ultimate `trace_id` source. Every session gets a human-initiated intent.
- **Distillation**: Human reviews `proposed_lessons.yaml` → approves → becomes `soul.yaml` (M11).
- **Novelty Injection**: Human provides the "external signal" that prevents fleet convergence (GAP-S-05).

---

## §4 Anti-Patterns (What Breaks the Chain)

| Anti-Pattern | Broken Link | Symptom | Fix |
|--------------|-------------|---------|-----|
| **Ghost Fleet** | Vault → Grok | 8 accounts exist but 0 in `fleet_config.yaml` | Vault `fleet init` mandatory |
| **Search Black Hole** | Search → Grok | Queries route to Grok but no API key | Vault `credential_audit` on boot |
| **Silent Drift** | Platforms → Vault | `.env` updated, Vault stale | Passive Watcher + MCP `credential_read` validation |
| **Context Amnesia** | Communication → Human | Subagent returns empty result | Inline Context Mandate (SUBAGENT_DISPATCH §0) |
| **Convergence Trap** | Human-Agent → Fleet | All agents agree, no novelty | Human injects chaos / Grokster adversarial review |

---

## §5 Integration Test Scenarios (For CI)

| Scenario | Domains Involved | Success Criteria |
|----------|------------------|------------------|
| **Cold Boot** | Platforms, Vault, Communication | `omega talk "hello"` works with local model |
| **Cloud Burst** | Platforms, Communication, Grok, Search, Vault | `@kali` dispatches to `@grok_cli` for DeepSearch |
| **Credential Rotation** | Vault, Grok, Communication | Web Grok cookie expires → Vault rotates → Fleet continues |
| **Parallel Sprint** | Platforms (OpenCode+Cline), Communication, Vault | Two agents edit different files, locks prevent conflict |
| **Session Death** | Human-Agent, Communication, Platforms | Compaction → Hydration Sequence (AGENTS.md) restores context |

---

*⬡ OMEGA ⬡ GROKSTER KB ⬡ CROSS_DOMAIN_MATRIX ⬡ 2026-07-22*