# LFM2.5 Small Model Specialists — E0 Smoke Test

Date: 2026-10-08
Node: Node 1 (CPU-only i7-13620H, Ollama local)
Models:
- `lfm25-230m-q6k`
- `lfm25-350m-q6k`

Both created from local GGUFs:
- `/home/xnai/models/gguf/LFM2.5-230M-Q6_K.gguf`
- `/home/xnai/models/gguf/LFM2.5-350M.i1-Q6_K.gguf`

## Test setup

Ollama `/api/chat`, `format: "json"`, `num_thread: 6`, `temperature: 0.1`, `num_predict: 512`.
Five task shapes:
1. `extractor_jsonl`
2. `well_curator`
3. `tool_router`
4. `privacy_filter`
5. `empress_lens`

## Raw smoke results

| model | case | valid JSON | latency | tokens |
|---|---:|---:|---:|---:|
| lfm25-230m-q6k | extractor_jsonl | true | 1.22s | 89 |
| lfm25-230m-q6k | well_curator | true | 0.44s | 58 |
| lfm25-230m-q6k | tool_router | true | 0.38s | 44 |
| lfm25-230m-q6k | privacy_filter | true | 0.28s | 29 |
| lfm25-230m-q6k | empress_lens | true | 0.50s | 67 |
| lfm25-350m-q6k | extractor_jsonl | true | 1.80s | 118 |
| lfm25-350m-q6k | well_curator | true | 0.58s | 31 |
| lfm25-350m-q6k | tool_router | true | 0.68s | 54 |
| lfm25-350m-q6k | privacy_filter | true | 0.50s | 37 |
| lfm25-350m-q6k | empress_lens | true | 1.38s | 137 |

## Qualitative observations

- Both models can emit JSON when forced through Ollama `format: "json"`.
- The 230M variant is markedly faster and still usable for simple extraction/classification-shaped tasks.
- The 350M variant produces more verbose and detailed outputs but is slower and more likely to drift when not schema-constrained.
- Current output is promising but not yet semantically reliable. The extractor did not consistently preserve the expected exact schema without stronger prompting/fine-tuning.
- Privacy and tool routing are the most promising first specialties because the output contracts are narrow and easy to validate.

## Recommendation

Do not train yet. Move to a real `P7.1` benchmark with 50–100 held-out samples before LoRA. If JSON validity and schema compliance lag, fine-tune from base/safetensors with TRL/PEFT. The encoder model should be tested as a router/classifier alternative.
