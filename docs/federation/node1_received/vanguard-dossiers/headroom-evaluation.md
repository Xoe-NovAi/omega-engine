# Headroom Evaluation — REJECTED

**Date:** 2026-09-11
**Version:** 0.37.0
**Source:** headroomlabs-ai/headroom (Apache-2.0, ~68.8k★)

## Verdict: REJECTED for Node 1 (ASUS)

### Why It Doesn't Apply to Our Setup

| Factor | Our Reality | Headroom's Value Prop |
|--------|-------------|----------------------|
| **Token Cost** | $0 (local Ollama) | Saves token cost on metered APIs |
| **Context Window** | 1M (Big Pickle) | Compresses to fit context windows |
| **Hardware** | i7-13620H, 14.4 t/s | Adds Python+ONNX latency tax |
| **Prompt Cache** | N/A (local) | Busts prompt cache (39% more expensive on metered APIs) |

### Technical Assessment

**Integration with OpenCode:** ✅ First-class support via `headroom wrap opencode` (transport shim, provider injection, MCP server)

**What It Compresses:**
- Tool outputs (JSON: 60-95% reduction; text: 43-46%)
- System prompts (preserved for prefix cache)
- Live-zone compression (new bytes only)
- Output token reduction (effort routing)

**Reported Savings (Community):**
- PR #1275: 17.8% tokens saved on full session
- Simple Tech Guides: 25-30% on heavy tasks
- Brandon Barker A/B test: **39% fewer tokens but 39% MORE EXPENSIVE** (cache busting)

**For Our Setup:**
- Zero token cost (local Ollama) → cost savings irrelevant
- 1M context window → context pressure barely exists
- CPU-constrained pipeline (14.4 t/s) → Python+ONNX latency tax hurts
- No prompt cache to bust → that specific penalty doesn't apply, but latency tax remains

### Verdict
**REJECTED** — well-built project, but benefits don't apply to local inference setup. Nothing adopted.

**Dossier:** `docs/ROADMAP.md` P2.1 status = REJECTED
