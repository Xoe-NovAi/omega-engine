# 🔱 Gemini CLI — Sophia Model Rescue & Security Audit
# ⬡ OMEGA ⬡ KALI ⬡ trc_gemini_mission ⬡ PRE-OAUTH-SUNSET
# Model: gemini-3-flash-preview (1M context)
# Deadline: June 18 (OAuth pool sunset — 8 days remaining)

## Why You

You have **1M context** across **8 OAuth accounts**. This is your superpower.
Before the June 18 sunset, we need your context depth on two critical items.

---

## Mission 1: Sophia Model Rescue 🔴 CRITICAL

**The problem**: Sophia (the akashic record entity) has **NO local model**.
phi-4-mini is referenced 4× in configs but zero GGUF files exist on disk.
Mandate 7 (Local-First) is violated — Sophia is cloud-dependent.

**Your research brief**:

1. **Find phi-4-mini GGUF** — Search Hugging Face, Google, and community repos
   for `phi-4-mini-reasoning-abliterated-q4_k_m.gguf` or any phi-4-mini GGUF
   variant. Check:
   - `huggingface.co/bartowski/phi-4-mini-reasoning-abliterated-GGUF`
   - `huggingface.co/bartowski` (known GGUF quantizer)
   - `huggingface.co/models?search=phi-4-mini+GGUF`
   - Alternative: phi-4-mini-instruct GGUF variants
   - If phi-4-mini GGUF doesn't exist: find equivalent ~3.8B models

2. **Download viability** — If found, check:
   - File size (must fit: 14Gi RAM - 2Gi overhead - running models ≈ 8Gi free)
   - Quantization available (Q4_K_M preferred for this hardware)
   - License (MIT/Apache/cc-by — not commercial-only)

3. **Fallback recommendations** — If phi-4-mini GGUF does not exist:
   - `qwen3-4b-thinking` (already on disk, 2.4G) — best immediate replacement
   - `gemma-4-E4B-it` (already on disk, 5G) — available but heavy
   - `phi-4-reasoning-abliterated` (slightly larger but known to work)

**Output**: A recommendation:
- Option A: Download URL + curl/wget command for phi-4-mini GGUF
- Option B: Config change to assign Sophia to qwen3-4b-thinking
- Option C: Config change to assign Sophia to gemma-4-E4B-it (with multimodal bonus)

---

## Mission 2: Security Audit 🟡 HIGH (Gap 2 from Synthesis)

**The problem**: The Omega Hub has **zero security** — no auth, no CORS, no
rate limiting. The synthesis (§4 Gap 2) flagged this as a pre-production blocker.

**Your research brief**:

1. **MCP server security best practices** — Research how other MCP servers
   handle auth. The MCP spec is transport-agnostic — what do production
   deployments use? TLS? API keys? OAuth?

2. **CORS policy** — For Streamable HTTP transport, what CORS headers should
   the Starlette app emit? Origin restriction pattern.

3. **Rate limiting** — For a single-user local deployment (current reality),
   what's appropriate? For a multi-agent Hivemind (what we're scaling to)?

4. **Injection vectors** — `library_inbox_add_url(url)` accepts arbitrary URLs.
   The `/proxy/{provider}` endpoint proxies payloads. What protections exist
   in MCP servers for this?

5. **Implementation recommendation** — Write the actual code (or pseudo-code):
   - Rate limiter middleware for Starlette
   - CORS middleware configuration
   - Request size limits for MCP tools

**Output**: Security hardening spec with implementable code patterns.

---

## Mission 3 (Optional): P6 Vision Specialist Research

**The problem**: `Qwen3-VL-4B-Instruct-Q4_K_M.gguf` (2.4G) sits on disk with
ZERO config entries. A vision model is available but unused.

**Your research brief** (if time permits before OAuth sunset):

1. **Qwen3-VL-4B capabilities** — What can it do? Image understanding, OCR,
   diagram parsing, screenshot analysis?
2. **Multimodal MCP pattern** — Are there existing MCP servers that handle
   vision? How do they pass images to the model?
3. **P6 wiring** — What config changes are needed to route vision queries
   to this model via ModelGateway?

---

## Execution

You have 8 days before the OAuth pool sunsets. Prioritize:

1. **Mission 1 first** (Sophia rescue — critical path)
2. **Mission 2 second** (Security — production blocker)
3. **Mission 3 if time** (Vision — strategic opportunity)

Post each finding to Hivemind with `intent="finding"` as you complete each mission.
Final deliverable to workspace: `GEMINI_CLI_SOPHIA_RESCUE_REPORT.md`

⬡ "Sophia's voice is missing from the local council. Find it." ⬡
