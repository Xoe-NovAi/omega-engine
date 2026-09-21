---
card_version: "1.0"
model_id: "z-ai/glm-5.3-flash"
provider: "Cline free tier (usage-billing provider)"
research_status: "candidate"
deployment: "hosted_trial"
last_verified: "2026-09-21"
confidence: "metadata:medium,performance:low"
license: "unconfirmed"
context_length: 1048576
modalities_in: ["text"]
modalities_out: ["text"]
---

# Cline: GLM-5.3-Flash (free tier)

| Field | Value |
|---|---|
| Cline model ID | `z-ai/glm-5.3-flash` |
| Base family | GLM-5.3-Flash (Zhipu) |
| Research status | **candidate** |
| Deployment | Hosted free tier via Cline Usage-Billing provider |
| Last verified | 2026-09-21 |
| Confidence | metadata:medium; performance:low (one indicative smoke test only) |
| Card version | 1.0 |

## Executive summary

GLM-5.3-Flash is the first free-tier model **verified working on Node 1 via the
Cline CLI** (smoke test 2026-09-21, `CLINE_SMOKE_OK`, $0 cost). It is a text-only
flash-class reasoning model advertised at 1,048,576-token context on the Cline
free list. The access pattern that matters for Omega: **after selecting the free
model once in the interactive selector, `cline --json -m z-ai/glm-5.3-flash`
works non-interactively at zero cost.** The free tier is a rotating, quota-gated
promotion — treat it as burst-credit, not a guarantee.

## Identity and access

| Item | Verified value |
|---|---|
| Cline catalog ID | `z-ai/glm-5.3-flash` |
| Provider | Cline (usage-billing provider, free promo) |
| Base model | GLM-5.3-Flash (Zhipu) |
| Context length | 1,048,576 (llm-stats.com compare page, secondary source) |
| Input modalities | Text |
| Output modality | Text |
| Pricing | **$0** on free list (community tracker 2026-09-20; $0.15/$0.50 per M reference tier per llm-stats.com) |
| Release | 2026-08-26 (llm-stats.com) |
| Known knowledge cutoff | Not specified |
| Prompt caching | Not established for the free route |

**Verified access (live, 2026-09-21):** `~/.cline/data/settings/providers.json`
records `provider=cline model=z-ai/glm-5.3-flash` after the operator selected the
model in `cline -i` → `/settings` → Cline provider. That interactive selection
grants the free-model entitlement; the identical `-m z-ai/glm-5.3-flash` form
succeeds afterwards.

## Architecture and capabilities

- Flash-class reasoning/text model (Zhipu GLM-5.3 family).
- Text in, text out; no image modality confirmed on this route.
- Advertised 1M-token context (secondary sources; **Cline may compact earlier —
  see quirks**).
- Cline CLI route supports ACT/plan modes and tool use through the Cline
  protocol.

## Strengths

- **Zero-cost frontier-quality access** on a machine that cannot run frontier
  weights locally (16 GB CPU-only host).
- **Non-interactive after one-time entitlement**: deterministic `-m` invocation
  is scriptable for smoke checks, reviews, and batch asks.
- Rotating free roster means multiple providers can be probed at $0.

## Quirks and risks

1. **Free tier is a quota, not a door.** Rotating promotions; "free today may be
   paid tomorrow". After quota exhaustion, switch to usage-billing/ClinePass —
   same drift-detect doctrine as Zen model rotation.
2. **Entitlement gating.** Before the interactive selection, `-m` runs can fail
   `model not found` even though the catalog resolves the model. The selector
   grants the entitlement; non-interactive agents inherit whatever was last
   selected.
3. **Effective context may be < 1M.** For DeepSeek V4 Flash, Cline auto-compacts
   at 128K regardless of the 1M marketing window (`cline/cline#10980`); a
   similar compact should be assumed until GLM's effective window is measured.
4. **License unconfirmed.** No authoritative license string confirmed for
   GLM-5.3-Flash on this route as of 2026-09-21; privacy/retention terms of the
   free Cline route not established — treat as non-private.

## Provider Claims

No provider benchmark table is available for this route yet. Metadata (context
window, pricing) is from secondary catalogs (llm-stats.com, free-token
community trackers) and is labeled accordingly in the tables above.

## Local Measurement

| Date | Measurement | Reproduction status | Evidence |
|---|---|---|---|
| 2026-09-21 | `timeout 120 cline --json -m z-ai/glm-5.3-flash "Reply with exactly: CLINE_SMOKE_OK"` | Indicative | **Local measurement** |

Details: returned `CLINE_SMOKE_OK`, `finishReason: completed`, 1 iteration,
**$0 cost**, usage 6602 in / 27 out tokens, 1622 cache read. Hardware: Node 1
(i7-13620H, CPU-only — irrelevant here: hosted route). Trials: 1. Command is
reproducible from `make`-less plain CLI; no repo script wrapper yet.

## Omega Verdict

| Workload | Fit | Reason |
|---|---|---|
| Frontier review / insight generation | **Candidate** | Zero-cost flash reasoning; smoke-verified route |
| Repository coding agent | **Untested** | No real Omega task run yet |
| Private work | **Conditional / no** | Free-tier retention not established |
| Node 1 local inference | **No** | Hosted only; CPU-only 16 GB host |
| High-volume swarms | **No/conditional** | Free quota is burst-credit, not capacity |

**Verdict:** keep `candidate`; do NOT promote to `active` until a real Omega
task (frontier review or a coding task) has run through this exact `-m` route
and the effective context window is measured.

## Operating recipe

```bash
timeout 120 cline --json -m z-ai/glm-5.3-flash "past your prompt here"
```

Precondition: model selected once in `cline -i` → `/settings` → Cline provider.

## Open questions / next validation

- [ ] Run one real Omega task (e.g. frontier review of a doc, or a small repo
  task) via `-m z-ai/glm-5.3-flash` and record factual accuracy vs. cost.
- [ ] Measure effective context window (does it compact below 1M?).
- [ ] Confirm free-list roster/rotation cadence and quota size over 2 weeks.
- [ ] File sibling cards for `cline-pass/deepseek-v4-flash` (1M/384K catalog
  verified, not yet entitlement-granted on Node 1) and `zai/glm-5.2` if probes
  succeed.
- [ ] Confirm privacy/retention terms of the Cline free route before any
  private work.

## Sources

- Cline free-models docs: https://docs.cline.bot/getting-started/free-models
- llm-stats.com GLM-5.3 vs Muse Spark compare page (context, release, pricing)
- Community free-token tracker listing GLM-5.3 Flash "Ox Alpha" free in Cline
  (accessed 2026-09-20)
- Live Node 1 probe: `~/.cline/data/settings/providers.json` (verified
  2026-09-21)
- `cline/cline#10980` (DeepSeek 128K compact; cited as the caveat pattern)