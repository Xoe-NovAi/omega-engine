# 🚨 ARCHITECT RUNME — G-1 Workhorse + W-1 WARP (2026-07-22)

**Status**: Waiting on **your sudo password once** for W-1; G-1 needs billing and/or OAuth in browser.  
**Ops SSOT**: `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`  
**Forensic**: `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`

---

## Why two tickets

| Ticket | Unlocks | Does NOT unlock |
|--------|---------|-----------------|
| **W-1 WARP** | Multi-IP **OpenCode Zen** / IP-keyed cloud | Free Gemma 16k TPM |
| **G-1 Workhorse** | Usable fat OpenCode sessions again | WARP tunnels |

Agents **cannot** enter your sudo password or complete Google OAuth for you.

---

## Command 1 — W-1 WARP (one password)

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
bash scripts/fix_warp_ns_setup_and_restart.sh
```

**What it fixes**: truncated `/usr/local/bin/warp-ns-setup` (root cause of `warp-ns-prep@*` failed since Jul 18), then starts prep → node → reg → bridges for nodes 1–3.

**Success looks like**:
```text
ss -lntp | rg '808[1-3]'   # three listeners
# validate script prints three Cloudflare exit IPs (ideally distinct)
```

**Already done without you**:
- `warp-proxy-pool` installed in `.venv`
- strategy/Ark/index/corpus/forensic all linked (G-1, W-1, D-377…D-381)

---

## Command 2 — G-1b Antigravity (fastest non-Gemma workhorse)

```bash
opencode auth login
# pick Google / Antigravity OAuth
opencode run -m google/antigravity-gemini-3-flash "Reply PONG"
```

Auth today is **API-key only** (`google` type=api). Frontier models need OAuth Path B.

---

## Command 3 — G-1a Gemma again (same model as before)

1. Open https://aistudio.google.com/ → enable **billing / Tier 1** on the project that owns your OpenCode Google API key  
2. Confirm limits: https://aistudio.google.com/rate-limit  
3. Smoke:
```bash
opencode run -m google/gemma-4-31b-it "Reply PONG"
```
Must **not** show `free_tier_input_token_count, limit: 16000`.

---

## Command 4 — Interim free models (while 1–3 pending)

OpenCode built-in free (variable quality / daily caps):
```bash
opencode run -m opencode/mimo-v2.5-free "Reply PONG"
# or: opencode/deepseek-v4-flash-free, opencode/nemotron-3-ultra-free
```

Local (if LM Studio up):
```bash
opencode run -m lmstudio/qwen3-4b-thinking "Reply PONG"
```

---

## After W-1 is green

```bash
# Python health
.venv/bin/python -c "import anyio; from warp_proxy_pool import EphemeralWarpPool
async def m():
 p=EphemeralWarpPool(); print(await p.get_healthy_port())
anyio.run(m)"

# OCZ via OpenCode (model id may vary)
opencode models opencode | head
```

ModelGateway already injects WARP for provider name `opencode-zen` when pool is healthy.

---

## Do not

- Cap OpenCode context to 12k/16k to “fix” free Gemma  
- Re-add Google model whitelist (hides Antigravity)  
- Force `apiKey`/`baseURL` on shared `google` provider  
- Expect WARP to fix free Gemma quotas  

---

*⬡ OMEGA ⬡ ARCHITECT-RUNME ⬡ G-1/W-1 ⬡ 2026-07-22*
