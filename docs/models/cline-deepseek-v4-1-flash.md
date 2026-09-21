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
2. **Effective context — REBALANCED 2026-09-21**: `cline/cline#10980` (filed
   2026-05-21, an *earlier* DeepSeek-Flash-family model) reported Cline
   auto-compacting DeepSeek context at 128K regardless of the 1M marketing
   window. **On V4.1, Node 1's own probe contradicts that**: a 151,604-char
   (~43.5K-token) file was read **in full** with needle + all questions correct
   at $0, and the operator reports Cline 1M-window models stay usable at 700K
   tokens. Do NOT assume 128K compact on V4.1; a 100K+ probe remains open.
3. **Text-loop collapse in long ACT sessions** — `cline/cline#13041` (filed
   2026-08-07, also pre-V4.1-dated): can stop emitting `tool_use` and stream
   unbounded near-identical text (worst observed turn 137K chars, 0 tools).
   Mitigation: avoid `xhigh` reasoning on long sessions, prefer plan mode,
   abort on repeated no-tool turns. Reviews run through this card have not
   observed the loop (see Local Measurement).
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
| 2026-09-21 | Frontier review of P3.7 docs (15 iterations, 825,136 in / 771,072 cache-read / 33,249 out, $0, 220,755 ms; ran live machine checks) | Controlled | **Local measurement** |
| 2026-09-21 | Long-context probe: 151,604-char / ~43.5K-token docs read in full (459,904 cache-read), needle + 4/4 questions correct, $0, 65,243 ms | Controlled | **Local measurement** |
| 2026-09-21 | **100K probe**: 7,315-line / ~404,476-char (~100K-token) corpus of 13 docs read page-by-page — no grep/search; 11 truncation gaps self-patched; needles A (mid-sentence @51.1%) + B (standalone @84.9%) quoted verbatim; 4/4 comprehension; $0, 145,127 ms, 29 iterations, 2,610,044 in / 2,450,176 cache-read / 13,837 out | **Verified** | **Local measurement** |

Details (smoke): returned `DS41_SMOKE_OK`, `finishReason: completed`, 1 iteration,
**$0 cost**, usage 6854 in / 8 out tokens, duration 1695 ms. Hardware: Node 1
(i7-13620H, CPU-only — hosted route, so irrelevant to throughput).
Details (review/probe): executed via the same `-m` route at $0; the review's
findings are committed to `docs/ROADMAP.md`, `docs/ANTIGRAVITY_GUIDE.md`, and
`KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md` §14. Operator observation (2026-09-21):
1M-window Cline models reach 700K tokens and remain usable in speed and accuracy —
consistent with the 771K cache-read review session. The **100K probe** (2026-09-21)
is the first fully-verified single-file window on this route: 404,476-char /
7,315-line corpus read in full with both needles verbatim and correct recall at
$0 — effective context on V4.1 is at least ~100K single-file, and the session
stayed coherent through 2.6M cumulative ACT tokens (29 iterations). Command is
reproducible from the plain CLI (no repo wrapper yet).

## Omega Verdict

| Workload | Fit | Reason |
|---|---|---|
| Frontier review / insight generation | **Active** | Ran the P3.7 doc review end-to-end at $0; live checks + 15 iterations; findings committed |
| Long-context ingestion | **Active** | 43.5K + **100K probes both passed** (full read, needles verbatim, 4/4 correct); operator confirms ~700K usable |
| Image/UI verification | **Untested (capable)** | First free Cline model with image input on Node 1; catalog capability confirmed |
| Repository coding agent | **Candidate** | Frontier review = real Omega task; repo edit quality unproven |
| Private work | **Conditional / no** | Free-tier retention not established |
| High-volume swarms | **No/conditional** | Free quota is burst-credit, not capacity |

**Verdict:** promote to `active` for frontier-review and long-context-ingestion
scope (both verified at $0); keep the card `candidate` overall until an
image-input run and repo-edit task confirm the remaining open questions.

## Operating recipe

```bash
timeout 150 cline --json -m cline-free/deepseek-v4.1-flash "past your prompt here"
```

Precondition: model selected once in `cline -i` → `/settings` → Cline provider.

## Open questions / next validation

- [x] Run one real Omega task (frontier review of P3.7 docs) via
  `-m cline-free/deepseek-v4.1-flash` at $0 — DONE 2026-09-21, findings applied.
- [x] Measure effective context window on a long input — DONE 2026-09-21:
  43.5K-token full read passed; 128K compact from cline#10980 NOT observed on V4.1.
- [x] Probe 100K+ token input — **DONE 2026-09-21: 100K probe PASSED** (7,315
  lines / ~404KB read in full, needles verbatim, $0). Operator reports usable
  at 700K; a 250K–500K probe is the next open stretch.
- [ ] Probe 250K–500K token input (operator observation says 700K usable).
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