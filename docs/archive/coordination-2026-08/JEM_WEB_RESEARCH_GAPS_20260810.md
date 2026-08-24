# 🔱 Jem Web Research — Knowledge Gaps for Next Tasks
**AP Token**: `AP-JEM-WEB-RESEARCH-20260810-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ opencode ⬡ trc_research ⬡ COMPLETE

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Status**: ✅ RESEARCH COMPLETE

---

## 1. W-1: WARP Proxy Pool — Web Research

### Root Cause Found
The **"Empty interface is likely to be undesired"** iptables error is caused by an **unquoted empty variable**. When `DEFAULT_IF` is empty:
- `iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o "$DEFAULT_IF" -j MASQUERADE`
- Becomes: `iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o -j MASQUERADE`
- iptables interprets `-j` as the interface name, MASQUERADE as a standalone argument

### Fix
1. **Quote all variables** in warp-ns-setup.sh
2. **Add fallback for DEFAULT_IF** (e.g., detect from `ip route show default` with fallback to first wireless/ethernet interface)
3. **Add `After=network-online.target`** to systemd unit to ensure network is ready
4. **Add `WantedBy=network-online.target`** for proper ordering

### systemd Best Practices
- Use `After=network-online.target` and `Wants=network-online.target` for network-dependent services
- `Type=oneshot` with `RemainAfterExit=yes` for setup scripts
- `PrivateMounts=no` required for systemd v254+ to allow ip netns bind mounts
- `NoNewPrivileges=true` with `CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN` for namespace operations

### Reference
- Superuser: "iptables Bad argument MASQUERADE" (https://superuser.com/questions/1376871)
- systemd-nspawn NAT: "How do systemd-nspawn and systemd-networkd implement NAT?" (https://unix.stackexchange.com/questions/794080)
- OneUpTime: "How to Provide Internet Access to a Network Namespace Using NAT" (https://oneuptime.com/blog/post/2026-03-20-internet-access-namespace-nat/view)

---

## 2. G-1: Workhorse Continuity — Web Research

### Critical Finding: 16K TPM Limit is NOT Just Free Tier
From Google AI Developers Forum (https://discuss.ai.google.dev/t/gemma-token-limits-change/174816):
- **"The new 16K TPM ceiling caps what a single request can send regardless of billing status"**
- **"I have confirmed in the Cloud Console quota panel that this ceiling remains the same even at Tier 3, the highest paid tier available"**
- **"Paying more buys no additional single-call headroom"**
- **"This differs from how TPM scales for Gemini-branded models, where the free-to-paid jump increases capacity substantially"**

### Implications for G-1 Paths
| Path | Viability | Notes |
|------|-----------|-------|
| G-1a Billing (Tier 1+) | ❌ WILL NOT WORK | 16K TPM ceiling applies even at Tier 3 |
| G-1b Antigravity OAuth | ✅ VIABLE | Different quota pool (Cloud Code / Antigravity) |
| G-1c OCZ+WARP | ✅ VIABLE | Different provider (OpenCode Zen) |
| G-1d Paid alt | ✅ VIABLE | OpenRouter, Cerebras, Groq, etc. |

### Google AI Studio Rate Limits (2026)
- Free tier: 5-15 RPM, 250K TPM (Gemini), 16K TPM (Gemma 4)
- Tier 1: $10 spend/10min, 20-300 RPM, 100K-1M TPM
- Tier 2: $200 spend/10min, 1000+ RPM, 2M TPM
- Tier 3: $200-1000+ spend/10min, highest paid tier

### Recommendation
**G-1a (billing) will NOT solve the problem.** The 16K TPM ceiling for Gemma 4 is hard-coded at all tiers. The viable paths are:
1. **G-1b**: Antigravity OAuth (fastest — `opencode auth login`)
2. **G-1c**: OCZ+WARP (requires W-1 fix first)
3. **G-1d**: Paid alternatives (OpenRouter, Cerebras, Groq, etc.)

---

## 3. QW-3: CI Guard for Token Counting — Web Research

### Tokenizer Drift is Real and Significant
From Tianpan.co (https://tianpan.co/blog/2026-04-28-tokenizer-drift-local-count-vs-billing):
- **"A team spent three weeks chasing a 'context truncation' bug that only fired in production for Japanese customers"**
- **"Their tiktoken count said the prompt fit in 8K with a 600-token margin. The provider's invoice said the request had been rejected"**
- **"The two numbers were off by 11%, the safety margin lived inside that 11%"**

### Provider vs Local Tokenizer Divergence
From `llm-tokens-atlas` (https://github.com/faraa2m/llm-tokens-atlas):
| Provider | Model | Median offline-vs-empirical delta |
|----------|-------|----------------------------------|
| Anthropic | claude-opus-4-7 | **+41.3%** (cl100k_base underestimates) |
| Google | gemini-2.5-pro | +4.5% (format-dependent) |
| OpenAI | gpt-4o | 0.0% (tiktoken is oracle) |
| Mistral | mistral-large | -0.1% |

### Key Insight
- **"The number that matters is not 'how many tokens does this string have' — that question has no single correct answer across providers, models, and release versions"**
- **"The number that matters is 'how many tokens will this provider charge me for this exact request envelope at this exact moment, against this model'"**

### CI Guard Best Practices
1. **Log provider returned usage alongside local estimate** on every call
2. **Alert on the ratio between the two**, not on absolute values
3. **Treat tokenizer pinning as a dependency contract** — pin, log, and eval on upgrade
4. **Use provider's `count_tokens` endpoint as pre-flight oracle** when available
5. **Schedule divergence audits** — sample recent calls, compute estimate/actual ratio, alert on drift

### Cache Read Tokens
- OpenAI reports via `prompt_tokens_details.cached_tokens`
- Anthropic reports via `cache_read_input_tokens`
- DeepSeek reports via `prompt_cache_hit_tokens`
- **All must be included in total token accounting**

---

## 4. QW-4: pool_tracker.py Wiring — Web Research

### Multi-Key Pool Patterns
From `mazori-ai/llm_gateway` (https://github.com/mazori-ai/llm_gateway):
- **Round-robin across N API keys per provider**
- **Billing-exhausted or auth-failed keys marked and skipped** for the rest of the run context
- **Per-tenant isolation** — one tenant's bad key shouldn't trip circuit for everyone
- **Cost tracking** — built-in pricing table; every response carries accurate `cost_usd`

### Key Rotation Patterns
From `AsiaOstrich/llm-key-router` (https://github.com/AsiaOstrich/llm-key-router):
- **Random selection** to avoid collision
- **Auto failover** — retry with next key on any failure, return 503 only when all exhausted
- **Cooldown** — configurable per error type (429: 5min, 5xx: 30s, timeout: 15s)
- **Weekly quota** — per-key budget with 90% warning, auto-reset every Monday
- **State persistence** — JSON file, survives restart

### Integration Recommendations
1. **Wire into ModelGateway.generate()** — after provider selection, before API call
2. **Track per-key usage** — tokens, cost, errors, cooldown status
3. **Implement drain-aware scoring** — prefer keys with remaining quota
4. **Add circuit breaker per key** — 5 consecutive failures → 30s cooldown
5. **Persist state to JSON** — survive restarts

---

## 5. QW-8: Context Gauge — Web Research

### Context Gauge Measures Absolute Working-Set Tokens
From `context-gauge` (https://pypi.org/project/context-gauge/):
- **Not a % of window** — absolute tokens, because degradation onset is window-independent
- **Color bands** (absolute working-set tokens):
  - 🟢 GREEN: <40K (full reasoning capacity)
  - 🟡 YELLOW: 40-90K (prefer delegating searches)
  - 🟠 ORANGE: 90-150K (split before reading)
  - 🔴 RED: 150-250K (handoff imminent)
  - ⚫ BLACK: ≥250K (STOP — hand off now)

### Floor Calibration
- **Every session is born tens of thousands of tokens deep** — harness system prompt, tool schemas, always-injected files
- **This floor is cached, position-privileged, and not what the model actively reasons over**
- **Banding raw fill would flag every fresh session as "degraded" on turn one (cry-wolf)**
- **Self-calibrate per project** so the band tracks the thing that actually degrades

### Data Sources
- **Claude Code statusLine JSON**: `context_window.total_input_tokens`, `context_window_size`
- **Transcript usage**: `input + cache_read + cache_creation`
- **Floor**: fill of the first genuine assistant turn

### Long-Context Degradation is Window-Independent
- **NoLiMa (2025)**: models advertised at 128K–1M drop below 50% of short-context baseline by ~32K task tokens
- **Chroma, "Context Rot" (2025)**: a 200K-context model measurably degrades around ~50K
- **Lost in the Middle (Liu et al., 2023)**: accuracy sags mid-context — a U-curve, not a cliff at the window edge

### Implementation Recommendations
1. **Measure absolute working-set tokens** (not % of window)
2. **Calibrate floor per project** (first genuine assistant turn)
3. **Use color bands**: GREEN <40K, YELLOW 40-90K, ORANGE 90-150K, RED 150-250K, BLACK ≥250K
4. **Integrate with ModelGateway** — emit context pressure events after each inference
5. **Add compaction trigger** at RED band (150-250K)

---

## 📊 Research Summary

| Task | Web Sources | Key Findings |
|------|-------------|--------------|
| W-1 WARP | 3 | iptables error = unquoted empty variable; systemd needs network-online.target |
| G-1 Workhorse | 4 | 16K TPM ceiling applies even at Tier 3 — billing won't fix it |
| QW-3 CI Guard | 3 | Tokenizer drift is 41% for Claude; provider usage is authoritative |
| QW-4 pool_tracker | 4 | Round-robin + drain-aware scoring + cooldown + state persistence |
| QW-8 Context Gauge | 3 | Absolute tokens (not %); floor calibration; color bands |

---
*⬡ OMEGA ⬡ JEM ⬡ trc_research ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
