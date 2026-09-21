---
card_version: "1.0"
model_id: "cline-free/deepseek-v4.1-flash"
provider: "Cline free tier (usage-billing provider)"
research_status: "candidate"
deployment: "hosted_trial"
last_verified: "2026-09-21"
confidence: "metadata:high,performance:low"
license: "unconfirmed"
context_length: 1048576
modalities_in: ["text", "image"]
modalities_out: ["text"]
---

# Cline: DeepSeek V4.1 Flash (free)

| Field | Value |
|---|---|
| Cline registry ID | `cline-free/deepseek-v4.1-flash` |
| Display name | DeepSeek V4.1 Flash (free) |
| Base family | `deepseek-flash` (DeepSeek) |
| Research status | **candidate** |
| Deployment | Hosted free tier via Cline Usage-Billing provider |
| Last verified | 2026-09-21 |
| Confidence | metadata:high (live catalog); performance:low (one indicative smoke test only) |
| Card version | 1.0 |

## Executive summary

DeepSeek V4.1 Flash (free) is the **second free-tier model verified working on
Node 1 via the Cline CLI** (smoke test 2026-09-21, `DS41_SMOKE_OK`, $0 cost).
The live Cline catalog reports: context window 1,048,576, max output 384,000,
capabilities `images, tools, reasoning, structured_output, temperature,
prompt-cache`, release date 2026-09-10, all pricing $0.

**⚠️ Name correction (operator, 2026-09-21)**: the model is **DeepSeek V4.1
Flash** — NOT "V4". `cline-free/deepseek-v4.1-flash` is the free variant;
`cline-pass/deepseek-v4-flash` is a **paid** model tied to ClinePass and was
removed from `~/.cline/data/settings/providers.json` (probe artifact created
2026-09-21 18:42Z, deleted per operator).

## Identity and access

| Item | Verified value |
|---|---|
| Cline registry ID | `cline-free/deepseek-v4.1-flash` |
| Provider | Cline (usage-billing provider, free promo) |
| Display name | DeepSeek V4.1 Flash (free) |
| Context window | 1,048,576 (live catalog) |
| Max output tokens | 384,000 (live catalog) |
| Capabilities | images, tools, reasoning, structured_output, temperature, prompt-cache |
| Reasoning options | toggle + effort (low / high / max) |
| Release date | 2026-09-10 (live catalog) |
| Family | `deepseek-flash` |
| Pricing (live catalog) | input 0, output 0, cacheRead 0, cacheWrite 0 |
| License / retention | Not established for the free route — treat as non-private |

**Verified access (live, 2026-09-21):** `~/.cline/data/settings/providers.json`
records `provider=cline model=cline-free/deepseek-v4.1-flash` (same `cline`
provider, `tokenSource: oauth`) after the operator selected the model in the
interactive selector.

## Architecture and capabilities

- Flash-class family `deepseek-flash`, 1M context / 384K max output (live
  catalog, not marketing copy).
- Multimodal input: **images** + text; text output.
- Tool calling, structured output, temperature control, prompt caching (live
  catalog capabilities).
- Reasoning: optional toggle with effort levels low / high / max.

## Strengths

- **Zero-cost frontier-class access** on a CPU-only 16 GB host — the same
  practical benefit as GLM-5.3-Flash, plus image input.
- **Non-interactive after one-time entitlement**: the `-m` invocation is
  scriptable.
- Multimodal input makes it the first free Cline model on Node 1 that can read
  screenshots — relevant for UI verification (USB display / OWUI checks).

## Quirks and risks

1. **Free tier is a quota, not a door** — rotating promotions; after quota
   exhaustion, switch to usage-billing. Same drift-detect doctrine as Zen.
2. **Effective context may be < 1M in Cline** — `cline/cline#10980`: Cline
   auto-compacts DeepSeek context at 128K regardless of the 1M marketing window;
   `settings` 400000 cannot raise it. Verify effective window with a real long
   input before relying on 1M.
3. **Text-loop collapse in long ACT sessions** — `cline/cline#13041`: can stop
   emitting `tool_use` and stream unbounded near-identical text (worst observed
   turn 137K chars, 0 tools). Mitigation: avoid `xhigh` reasoning on long
   sessions, prefer plan mode, abort on repeated no-tool turns.
4. **License/privacy unconfirmed** — free-route retention terms not established;
   treat as non-private.
5. **Name/ID churn risk** — "V4.1" vs "V4" confusion (this card documents the
   correction); verify registry IDs at runtime, don't hardcode.

## Provider Claims

No independent benchmark table is available. The live Cline catalog metadata
(sizes, capabilities, pricing, release date) is **verified** (observed in the
`run_result` `model.info` on 2026-09-21), not provider marketing.

## Local Measurement

| Date | Measurement | Reproduction status | Evidence |
|---|---|---|---|
| 2026-09-21 | `timeout 150 cline --json -m cline-free/deepseek-v4.1-flash "Reply with exactly: DS41_SMOKE_OK"` | Indicative | **Local measurement** |

Details: returned `DS41_SMOKE_OK`, `finishReason: completed`, 1 iteration,
**$0 cost**, usage 6854 in / 8 out tokens, duration 1695 ms. Hardware: Node 1
(i7-13620H, CPU-only — hosted route, so irrelevant to throughput). Trials: 1.
Command is reproducible from the plain CLI (no repo wrapper yet).

## Omega Verdict

| Workload | Fit | Reason |
|---|---|---|
| Frontier review / insight generation | **Candidate** | Zero-cost reasoning with 1M ctx; smoke-verified route |
| Image/UI verification | **Candidate** | First free Cline model with image input on Node 1 |
| Repository coding agent | **Untested** | No real Omega task run yet |
| Private work | **Conditional / no** | Free-tier retention not established |
| High-volume swarms | **No/conditional** | Free quota is burst-credit, not capacity |

**Verdict:** keep `candidate`; do NOT promote to `active` until a real Omega
task runs through this `-m` route and effective context is measured.

## Operating recipe

```bash
timeout 150 cline --json -m cline-free/deepseek-v4.1-flash "past your prompt here"
```

Precondition: model selected once in `cline -i` → `/settings` → Cline provider.

## Open questions / next validation

- [ ] Run one real Omega task (frontier review or UI screenshot check) via
  `-m cline-free/deepseek-v4.1-flash` and record factual accuracy vs. cost.
- [ ] Measure effective context window on a long input (does it compact at 128K
  per cline#10980?).
- [ ] Test image input (screenshot) through the `-m` route.
- [ ] Confirm free-list roster/rotation cadence and quota size over 2 weeks.
- [ ] Confirm privacy/retention terms of the Cline free route before private
  work.

## Sources

- Live Node 1 probe: `~/.cline/data/settings/providers.json` (verified
  2026-09-21); `run_result.model.info` from the smoke test
- docs.cline.bot free-models: https://docs.cline.bot/getting-started/free-models
- `cline/cline#10980` (128K compact), `cline/cline#13041` (text-loop collapse)
- llm-stats.com / devtools.sh context-window compare pages (secondary)