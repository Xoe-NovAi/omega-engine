<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 05 — Two Tiers: VNR in Front of a VL Model

## The division

VNR answers counting questions. A vision-language model answers meaning
questions. Never ask the expensive one what the cheap one can answer, and
never trust the cheap one about semantics.

| | Tier 1 — VNR | Tier 2 — VL model |
|---|---|---|
| Cost | microseconds | seconds |
| Determinism | total | none |
| Good at | "is anything changing", "how much", "where" | "is this a menu or gameplay" |
| Fails at | semantics | precise geometry, counting, reproducibility |

The working pattern: VNR cheaply rejects frames the VL model would waste
seconds on (a frozen frame, a 0.3% change), and the semantic call is reserved
for frames that survive the gate — plus every frame that ends up in results,
so each classification carries its reason.

## The hard rule

Tier 2 **always reads the same buffer the human sees** — the final composited
frame, never an intermediate render target. A semantic verdict on a different
buffer than the one under dispute is not a verdict on the dispute.

## Server wiring (llama.cpp, verified)

A vision model needs two files: the language weights and the multimodal
projector (`--mmproj`). Pair each model strictly with its own projector —
projectors are architecture-specific and a mismatched one fails silently or
loudly, never usefully.

```bash
llama-server -m model-Q4_K_M.gguf --mmproj mmproj-model.gguf --port 8081 --ctx-size 4096
```

| Flag | Purpose |
|---|---|
| `--mmproj FILE` | path to the multimodal projector (required for vision) |
| `--no-mmproj-offload` | keep the projector on CPU (stability fallback) |
| `--mmproj-offload` | offload projector to GPU (default; measure before trusting) |
| `--ctx-size 4096` | context size; vision consumes tokens per image, size accordingly |
| `--image-min-tokens N` / `--image-max-tokens N` | bound dynamic-resolution token cost per image |

The server speaks OpenAI-compatible `/v1/chat/completions`. Send images as
base64 data URIs or `image_url`. Multiple images per message are supported —
required for golden-vs-candidate comparison in a single call:

```json
{
  "model": "argus-vlm",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "Compare these two screenshots."},
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
    ]
  }]
}
```

Prefer HTTP to the server over in-process bindings for multimodal work; the
bindings historically lag the server's vision support.

## Structured output

Free-form prose from a VL model cannot feed a decision log. Constrain it to a
fixed schema and parse defensively (strip markdown fences, retry on failure).
Shape the schema to the question:

```json
{
  "sprite": "graham",
  "body_parts_visible": {"head": false, "cap": false, "body": true, "legs": true},
  "occluded_by": "unknown",
  "confidence": 0.9,
  "notes": "Crown region shows background wall texture; no cap-colored pixels detected."
}
```

Log every Tier-2 verdict **with the Tier-1 statistics that accompanied it**.
The first time they disagree, the paired numbers say which one lied — and
that disagreement is the most informative event the system produces.

## Version note

Upstream multimodal support in llama.cpp is explicitly under heavy
development with breaking changes expected. Pin the build you validate
against. Commands above are known-good for the current tree, not guaranteed
for the next.
