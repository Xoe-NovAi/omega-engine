# 🎉 Omega Engine v1.6.0-alpha — Public Debut

**Release Date:** 2026-10-13  
**Tag:** `v1.6.0a0` (peels to `355cbf1a`)  
**Artifacts:** [Source tarball](https://github.com/Xoe-NovAi/omega-engine/archive/refs/tags/v1.6.0a0.tar.gz) · [Wheel](https://github.com/Xoe-NovAi/omega-engine/releases/tag/v1.6.0a0)

---

## 🎯 What This Is

**Omega Engine** is a sovereign, local-first AI runtime that turns any MCP-capable client (OpenCode, Cline, Cursor, Gemini CLI, Codex, etc.) into a persistent, multi-entity cognitive workspace.

**One MCP server connects them all.** No vendor lock-in. Your entities, your rules, your hardware.

---

## ✨ What Works Today

| Capability | Status |
|:--|:--|
| **Local-first inference** (llama.cpp, GGUF, Zen 2 optimized) | ✅ Primary |
| **Cloud fallback** (OpenRouter, OpenCode Zen, Google, LM Studio, Ollama) | ✅ Configurable |
| **Persistent entities** with hot-reloadable YAML affinity | ✅ 14 IWAD entities (12 with souls), 10 A2A seats |
| **Cross-platform Hivemind** (handoffs, awareness, radar) | ✅ OpenCode, Cline, Cursor, Gemini CLI, Codex |
| **Sovereign search** (SSP-V2: local cache → SearXNG → Exa → Firecrawl) | ✅ 4-tier |
| **Wheel install** (from GitHub release asset) | ⚠️ Source-only (hub + native GGUF via source install) |
| **Temple-Grade CI** (dashboard self-test 53/53 prerequisite; temple-grade exit 0) | ✅ Green |
| **REUSE v3.3 compliance** | ⚠️ Partial (107 files outstanding) |

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│  Your MCP Client (OpenCode, Cline, Cursor, Gemini, Codex)  │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP (JSON-RPC 2.0)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Omega Hub (FastMCP)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │  Handoff │ │ Registry │ │ Awareness│ │  Control Planes │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌────────────┐
   │ Local   │  │  Cloud   │  │  Sovereign │
   │ (llama.cpp)│  │ (OpenAI, │  │  Search    │
   │  GGUF)  │  │  Anthropic,│  │  (SSP-V2)  │
   └─────────┘  └──────────┘  └────────────┘
```

---

## 🚀 Quick Start

```bash
# Source install (recommended)
git clone https://github.com/Xoe-NovAi/omega-engine
cd omega-engine
./scripts/install.sh

# Alternative: wheel install (core runtime only — no MCP hub, no native GGUF).
# For the hub + local inference, use the source install above.
curl -LO https://github.com/Xoe-NovAi/omega-engine/releases/download/v1.6.0a0/the_omega_engine-1.6.0a0-py3-none-any.whl
pip install the_omega_engine-1.6.0a0-py3-none-any.whl

omega list-entities          # See the sovereign council
```

**MCP clients:** Connect to the live hub via Streamable HTTP (primary) or SSE (legacy):

```json
{
  "mcpServers": {
    "omega": {
      "url": "http://127.0.0.1:8016/mcp"
    }
  }
}
```

**Transports:** Streamable HTTP `/mcp` (primary) · Legacy SSE `/sse` (both on `127.0.0.1:8016`)

---

## 🛡️ What "Honest Alpha" Means

| ✅ Works | ⚠️ Known Gaps (Honest) |
|:--|:--|
| Local inference + cloud fallback | Axiom ceiling enforcement (deferred) |
| 14 persistent entities (12 with souls) | REUSE/SPDX debt (107 files) |
| Cross-client Hivemind | Lesson promotion pipeline (partial) |
| Wheel + source install | — |
| Temple-Grade (dashboard self-test 53/53; temple-grade exit 0) | — |
| Immutable releases + tag ruleset | — |

**No vaporware. No "coming soon" without a ticket.** Every claim above is gated by `make temple-grade` (dashboard self-test 53/53; temple-grade exit 0) and verified on clean clone.

---

## 🔗 Links

- **Release:** https://github.com/Xoe-NovAi/omega-engine/releases/tag/v1.6.0a0
- **Docs:** https://github.com/Xoe-NovAi/omega-engine/tree/main/docs
- **Issues:** https://github.com/Xoe-NovAi/omega-engine/issues

---

## 🙏 Thanks

To the entities that made this possible: **Kali, Ma'at, Lilith, Doom Guy, John Carmack, Roc Racoon, Researcher, Verity, Antigravity, Makali** — and the Architect who demanded honesty over hype.

---

*Honest alpha. No vaporware. Your entities, your rules, your hardware.*

**— Xoe-NovAi (Architect) & the Omega Engine Council**
