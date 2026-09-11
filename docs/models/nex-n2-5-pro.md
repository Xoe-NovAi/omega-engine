# Nex AGI: Nex-N2.5-Pro (free)

| Field | Value |
|---|---|
| Canonical OpenRouter ID | `nex-agi/nex-n2.5-pro:free` |
| Research status | **candidate** |
| Deployment | Hosted trial via OpenRouter; not locally deployed |
| Last verified | 2026-09-11 |
| Confidence | **High** for metadata; **low** for independent performance |
| License | Apache-2.0 |
| Weight status | Released on Hugging Face |
| Omega verdict | Promising agentic candidate; validate before replacing current models |

## Executive summary

Nex-N2.5-Pro is a very new multimodal Mixture-of-Experts model aimed at
long-horizon agent work: coding, tool use, browser/computer interaction, visual
feedback, and self-verification. Its provider-published results are strong, but
the model was released only days before this review and independent evaluations
are essentially absent.

For Omega, it is worth a controlled OpenRouter trial for repository agents and
visual/tool workflows. It is not a local-inference candidate on the current
CPU-only 16 GB Node 1.

## Identity and access

| Item | Verified value |
|---|---|
| OpenRouter catalog ID | `nex-agi/nex-n2.5-pro:free` |
| OpenRouter display name | Nex AGI: Nex-N2.5-Pro (free) |
| Canonical dated slug | `nex-agi/nex-n2.5-pro-20260907` |
| Hugging Face repository | `nex-agi/Nex-N2.5-Pro` |
| Created | 2026-09-08 (OpenRouter catalog) |
| Context length | 262,144 tokens |
| Input modalities | Text and image |
| Output modality | Text |
| Pricing | Prompt `0`, completion `0` in the live catalog |
| Knowledge cutoff | Not specified |
| Voice support | Not advertised |
| Prompt caching | No model-specific cache capability or pricing listed |

**Verified metadata:** the live OpenRouter catalog currently contains the free
variant, but its endpoint-detail response reports `endpoints: []`. Provider
identity, latency, throughput, and capacity are therefore not visible through
the catalog API. A 429 or 502 should be treated as an expected retryable route
failure, not as a model-quality result.

## Architecture and capabilities

- **Base family:** Qwen3.5-based MoE; the publisher identifies Pro as
  `Qwen3.5-397B-A17B` (397B total parameters, approximately 17B active).
- **OpenRouter architecture metadata:** `Qwen3_5MoeForConditionalGeneration`,
  Qwen3 tokenizer, 60 text layers, 512 experts, 10 experts per token.
- **Attention mix:** hybrid full and linear attention; full-attention layers
  occur every fourth layer in the published configuration.
- **Context:** 262,144 maximum positions.
- **Vision:** text + image input with a 27-layer vision encoder; hosted output is
  text only.
- **Reasoning:** optional `none`, `medium`, or `high` effort.
- **Agent features:** tools, tool choice, structured outputs, response formats,
  log probabilities, top-k/top-p/temperature control.
- **Local serving:** publisher recommends the patched SGLang image
  `nexagi/sglang:v0.5.18-nex-patch`, `--tool-call-parser qwen3_coder`, and
  `--reasoning-parser qwen3`. The Pro reference deployment uses 8 × H100 GPUs.

The Hugging Face repository reports approximately 407 GB of stored weights
(122 safetensors shards). This confirms that the model is not a fit for Node 1's
CPU-only memory envelope.

## Strengths

### Agentic coding and verification

The model is explicitly trained and positioned for codebase exploration,
multi-file implementation, program execution, test generation, and verified
outcomes. Provider-reported Pro scores include:

| Benchmark | Provider-reported score | Evidence |
|---|---:|---|
| Terminal-Bench 2.1 | 82.7 | Provider claim |
| SWE-Bench Pro | 61.2 | Provider claim |
| DeepSWE v1.1 | 55.8 | Provider claim |
| Toolathlon Verified | 68.5 | Provider claim |
| Job Bench | 41.4 | Provider claim |

### Visual feedback and computer use

Nex-AGI emphasizes screenshots and environment state as a feedback loop for
computer and browser operation. Provider-reported multimodal scores include:

| Benchmark | Provider-reported score | Evidence |
|---|---:|---|
| OSWorld-Verified | 82.2 | Provider claim |
| OSWorld-2 | 56.4 | Provider claim |
| WebArena-Verified | 67.6 | Provider claim |
| OSWorld-G | 87.4 | Provider claim |
| Vision2Web | 68.2 | Provider claim |
| OmniDoc | 92.2 | Provider claim |

### Long-horizon agent work

The combination of a 262K context, optional reasoning, tool calling, and visual
feedback is well aligned with Omega's multi-step coding and federation tasks.
One public GitHub issue reports a user running many hours of multi-agent
mathematical research through the OpenRouter free route, with externally
machine-verified intermediate results. This is an **independent user report**,
not a controlled benchmark, but it is a useful signal for long-horizon behavior.

## Quirks and risks

1. **Very new release.** The model, weights, OpenRouter route, and publisher
   repository all appeared around 2026-09-08. Independent replication is sparse.
2. **Provider-authored benchmarks.** The model card says some results come from
   Nex-AGI's own evaluations. NexCUA was described as not yet open-sourced, and
   WebTest results use oracle mode with a ground-truth checklist.
3. **Reasoning-default conflict.** OpenRouter metadata lists `high` as the
   default reasoning effort; the publisher card lists `medium` as default.
   Set `reasoning_effort` explicitly.
4. **Free-route capacity is uncertain.** The catalog shows zero pricing but no
   provider endpoints. A user reported an account-wide free-tier ceiling near
   1,000 requests/day; treat this as anecdotal until confirmed by OpenRouter.
5. **No paid catalog entry found.** The current snapshot exposes the free route;
   do not assume a paid fallback exists.
6. **Tool parsing is gateway-sensitive.** Self-hosting requires the publisher's
   parser and SGLang flags; a generic OpenAI-compatible server may not preserve
   reasoning/tool semantics correctly.
7. **Multimodal input is not multimodal output.** It accepts images but returns
   text. GUI actions still require an external execution/verification loop.
8. **No known knowledge cutoff.** Time-sensitive answers need retrieval or web
   verification.

## Evidence and benchmark caveats

The publisher's sampling settings are `temperature=0.7`, `top_p=0.95`, and
`top_k=40`. Its tables compare against other very new provider models and use a
mix of public leaderboards and internal evaluations. The scores are useful for
forming hypotheses, not for declaring a production ranking.

No independent benchmark suite or Omega-local measurement was available at the
time of this card. The next evidence step is a controlled A/B against the current
OpenRouter model on the same repository, tool, long-context, and visual tasks.

## Omega fit and verdict

| Workload | Fit | Reason |
|---|---|---|
| Repository coding agent | **High candidate** | Strong provider coding claims; tool/verification focus |
| Browser/computer use | **High candidate** | Explicit visual-feedback training and GUI benchmarks |
| Long-horizon planning | **Medium/high candidate** | 262K context + reasoning + tools; needs local validation |
| Private work | **Conditional** | Use only a zero-retention paid route if privacy matters; free-tier retention is not established here |
| Node 1 local inference | **No** | 397B/407 GB weights; CPU-only 16 GB host |
| High-volume swarms | **No/conditional** | Free-route capacity and rate limits are unverified |

**Verdict:** keep as a `candidate`; do not promote to `active` until the A/B
validation below is complete.

## Operating recipe

```json
{
  "model": "nex-agi/nex-n2.5-pro:free",
  "reasoning_effort": "medium",
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 40,
  "stream": true,
  "session_id": "omega-engine-alpha-nex-n2-5-pro-001"
}
```

For difficult tasks, test `reasoning_effort: "high"` separately. For cheap
instruction following, test `"none"`. Retry HTTP 429/502 with exponential
backoff and verify all tool actions externally.

## Open questions / next validation

- [ ] Run the same 4-task A/B against the current model: bug fix, multi-file
  refactor, tool orchestration, and screenshot/UI interpretation.
- [ ] Record latency, token usage, failure rate, and human correction time.
- [ ] Confirm free-tier rate limits and provider stability over at least 100
  requests.
- [ ] Test structured output and tool-call fidelity with a deterministic schema.
- [ ] Re-check the model card and OpenRouter catalog after 30 days.

## Sources

All sources accessed 2026-09-11:

- [OpenRouter live model catalog](https://openrouter.ai/api/v1/models)
- [OpenRouter Nex-N2.5-Pro API guide](https://openrouter.ai/nex-agi/nex-n2.5-pro:free/llms.txt)
- [OpenRouter endpoint metadata](https://openrouter.ai/api/v1/models/nex-agi/nex-n2.5-pro-20260907/endpoints)
- [Hugging Face model card and weights](https://huggingface.co/nex-agi/Nex-N2.5-Pro)
- [Nex-N2.5 publisher repository](https://github.com/nex-agi/Nex-N2.5)
- [Nex-AGI model site](https://nex-agi.com/)
- [Independent user report: GitHub issue #2](https://github.com/nex-agi/Nex-N2.5/issues/2)
- [OpenRouter provider-sticky routing documentation](https://openrouter.ai/docs/guides/best-practices/prompt-caching#provider-sticky-routing)
