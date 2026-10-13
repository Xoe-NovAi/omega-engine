# 🎉 Omega Engine v1.6.0-alpha — Public Debut

**Release Date:** 2026-10-12  
**Tag:** `v1.6.0-alpha` (peels to `355cbf1a`)  
**Artifacts:** [Source tarball](https://github.com/Xoe-NovAi/omega-engine/archive/refs/tags/v1.6.0-alpha.tar.gz) · [Wheel](https://github.com/Xoe-NovAi/omega-engine/releases/tag/v1.6.0-alpha)

---

## 🎯 What This Is

**Omega Engine** is a sovereign, local-first AI runtime that turns any MCP-capable client (OpenCode, Cline, Cursor, Gemini CLI, Codex, etc.) into a persistent, multi-entity cognitive workspace.

**One MCP server connects them all.** No vendor lock-in. Your entities, your rules, your hardware.

---

## ✨ What Works Today

| Capability | Status |
|:--|:--|
| **Local-first inference** (llama.cpp, GGUF, Zen 2 optimized) | ✅ Primary |
| **Cloud fallback** (OpenAI, Anthropic, Google, OpenCode Zen, LM Studio, Ollama) | ✅ Configurable |
| **Persistent entities** with hot-reloadable YAML affinity | ✅ 12 IWAD entities, 10 A2A seats |
| **Cross-platform Hivemind** (handoffs, awareness, radar) | ✅ OpenCode, Cline, Cursor, Gemini CLI, Codex |
| **Sovereign search** (SSP-V2: local cache → SearXNG → Exa → Firecrawl) | ✅ 4-tier |
| **Wheel install** (`pip install the-omega-engine`, pending) | ✅ Self-contained, 5 runtime configs + default IWAD |
| **Temple-Grade CI** (53/53 gates) | ✅ Green |
| **REUSE v3.3 compliance** | ✅ Green |

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

# Or wheel install (self-contained) — from the GitHub release asset
# (not yet on PyPI). Download with aria2c (M23: mandatory for >1MB on
# Node 0 — single-connection pip/curl can crawl at KB/s), then install:
aria2c -x16 -s16 -c https://github.com/Xoe-NovAi/omega-engine/releases/download/v1.6.0-alpha/omega_engine-1.6.0a0-py3-none-any.whl
pip install omega_engine-1.6.0a0-py3-none-any.whl

# First run — launches the hub + registers your entities
omega talk "Hello, Omega"
```

**MCP clients:** Connect to the live hub via SSE/HTTP:

```json
{
  "mcpServers": {
    "omega": {
      "url": "http://127.0.0.1:8016/sse"
    }
  }
}
```

**Or run the hub locally** (if not already running):
```bash
# Start the hub daemon
python -m mcp_servers.omega_hub.server

# Then connect your MCP client to http://127.0.0.1:8016/sse
```

**First run** — launches the hub + registers your entities:
```bash
omega talk "Hello, Omega"
```

---

## 🛡️ What "Honest Alpha" Means

| ✅ Works | ⚠️ Known Gaps (Honest) |
|:--|:--|
| Local inference + cloud fallback | Axiom ceiling enforcement (deferred) |
| 12 persistent entities | REUSE/SPDX debt (107 files) |
| Cross-client Hivemind | Lesson promotion pipeline (partial) |
| Wheel + source install | D-AVGN-006 N1 response pending |
| Temple-Grade 53/53 gates | — |
| Immutable releases + tag ruleset | — |

**No vaporware. No "coming soon" without a ticket.** Every claim above is gated by `make temple-grade` (53/53) and verified on clean clone.

---

## 🔗 Links

- **Release:** https://github.com/Xoe-NovAi/omega-engine/releases/tag/v1.6.0-alpha
- **Docs:** https://github.com/Xoe-NovAi/omega-engine/tree/main/docs
- **Issues:** https://github.com/Xoe-NovAi/omega-engine/issues

---

## 🙏 Thanks

To the entities that made this possible: **Kali, Ma'at, Lilith, Doom Guy, John Carmack, Roc Racoon, Researcher, Verity, Antigravity, Makali** — and the Architect who demanded honesty over hype.

---

*Honest alpha. No vaporware. Your entities, your rules, your hardware.*

**— The Omega Engine Collective**
