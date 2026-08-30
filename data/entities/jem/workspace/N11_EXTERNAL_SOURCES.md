<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N11 External Sources — Offline Expertise Queue
**AP**: AP-N11-EXTERNAL-SOURCES-v1.0.0 · **last_verified: 2026-08-22** · **Curator**: Jem (N11 evaluator)
**Purpose**: Prioritized ingestion queue for future background curation worker. Each entry: title, source, priority, rationale, target format. Worker pulls, ingests, indexes into sovereign library.

---

## Priority Legend
- **P0**: Blocking N11 charter execution (must have offline before next session)
- **P1**: Needed for upcoming work (lm-eval integration, calibration pass, model registry)
- **P2**: Strategic depth (theoretical grounding, competitor tracking)
- **P3**: Archive/reference (historical context)

---

## Ingestion Queue

| # | Title | Source | Priority | Rationale | Target Format |
|---|-------|--------|----------|-----------|---------------|
| 1 | **lm-eval-harness v0.4.12 API Guide** | EleutherAI/lm-evaluation-harness/blob/main/docs/API_guide.md | P0 | Primary wiring doc for `local-completions` backend; TemplateAPI → LocalCompletionsAPI chain; completion vs chat endpoint distinction critical for D-585 | Markdown mirror in `data/library/domains/eval/lm-eval-api-guide.md` |
| 2 | **lm-eval-harness v0.4.12 Release Notes** | Zenodo 10.5281/zenodo.20122284 + GitHub releases | P0 | Exact feature set of ADOPT version; CLI refactor, lighter install, think_end_token, SGLang support | Markdown summary in `data/library/domains/eval/lm-eval-v0.4.12-release.md` |
| 3 | **promptfoo 0.122.0 Release Notes** | promptfoo/promptfoo/releases/tag/0.122.0 | P1 | Only breaking change: Node.js 20 drop (build-time); streaming stall fix relevant to M25; Shai-Hulud security fix | Markdown summary in `data/library/domains/eval/promptfoo-0.122.0-release.md` |
| 4 | **promptfoo Documentation (full)** | promptfoo.dev/docs | P1 | Red-team plugins (50+ vuln types), provider matrix (60+), CI/CD integration patterns, local execution model | Markdown mirror of key sections in `data/library/domains/eval/promptfoo-docs/` |
| 5 | **RAGAS Metrics Documentation** | docs.ragas.io/en/latest/concepts/metrics | P1 | Core RAG metrics (Faithfulness, Answer Relevancy, Context Precision/Recall) + Nvidia/Agent extensions; vocabulary stability confirmation | Markdown mirror in `data/library/domains/eval/ragas-metrics.md` |
| 6 | **RAGAS Foundational Papers** | arXiv:2309.15217 (RAGAS) + arXiv:2402.06416 (RAGAS v0.2) | P2 | Theoretical grounding for the four metrics Omega implements as vocabulary; faithfulness/answer_relevancy/context_precision/recall definitions | PDF → Markdown summary in `data/library/domains/eval/ragas-papers.md` |
| 7 | **llama.cpp Server README** | ggml-org/llama.cpp/blob/master/tools/server/README.md | P0 | Official server binary: endpoints (`/v1/completions`, `/v1/chat/completions`, `/health`), KV cache persistence, `--jinja` tool calling, `--ctx-size`, `--n-gpu-layers` | Markdown mirror in `data/library/domains/inference/llama-cpp-server.md` |
| 8 | **llama.cpp Server Deployment Guide** | unsloth.ai/docs/basics/inference-and-deployment/llama-server-and-openai-endpoint | P1 | Production wiring: `llama-server --model <gguf> --port 8001 --jinja` → OpenAI client at `http://localhost:8001/v1`; `--jinja` quirks for fine-tunes | Markdown mirror in `data/library/domains/inference/llama-server-deployment.md` |
| 9 | **Community llama-oai-server** | odellus/llama-oai-server (GitHub) | P2 | FastAPI wrapper: single-threaded, persistent KV cache, huge context (120K+), streaming SSE, function calling, env-var config | Markdown mirror in `data/library/domains/inference/llama-oai-server.md` |
| 10 | **Inspect AI Framework Docs** | inspect.aisi.org.uk + UKGovernmentBEIS/inspect_ai | P1 | Agentic eval framework competitor; built-in GAIA/SWE-Bench/GDM CTF/Cybench; sandboxed code execution; model-graded evals | Markdown mirror in `data/library/domains/eval/inspect-ai.md` |
| 11 | **Inspect AI v0.3.259 Release** | PyPI inspect-ai 0.3.259 (2026-08-16) | P2 | Weekly release cadence; 50+ contributors; UK AISI backing; MIT license | Markdown summary in `data/library/domains/eval/inspect-ai-v0.3.259.md` |
| 12 | **D-585 Canonical Model Matrix** | docs/decisions/PIVOT_LOG.md:252–260 | P0 | N11's constitutional matrix: Qwen3-4B planner / Qwen3-4B-Thinking executor / Qwen3-1.7B critic; nemotron correction mandated | YAML (models.yaml entry) + JSON (opencode.json alias) — NOT markdown |
| 13 | **C-0 Test Honesty Protocol** | PIVOT_LOG.md (search C-0) | P1 | False-count ban, honest badge, 95/95 Phase 2 hardening, quarantine protocol | Markdown in `data/library/domains/qa/test-honesty.md` |
| 14 | **C-10 Admission Control + OOMProtector** | PIVOT_LOG.md (search C-10) + src/omega/oracle/admission_controller.py | P1 | Semaphore(1) + 3-signal fusion (PSI/MemAvailable/zram); DENY_OOM_RISK hard floor; THROTTLE <4GB | Markdown in `data/library/domains/inference/admission-oom.md` |
| 15 | **LI Workstream Specs** | ACTIVE_SPRINT.json LI-2/LI-4 + docs/strategy/LOCAL_INFERENCE_OPT.md | P1 | SequentialModelLoader (one model at a time), Tier 0 matrix (Qwen3-4B/4B-Thinking/1.7B), q8_0 KV, zswap integration | Markdown in `data/library/domains/inference/local-inference-opt.md` |
| 16 | **Isotonic Regression for Calibration** | sklearn.isotonic.IsotonicRegression + "Calibration Curves 2026" heritage | P2 | Mathematical basis for JudgeCalibrator; ECE reduction 0.18→0.06 claim; 7-13B judge overconfidence band 0.8-0.95 | Markdown in `data/library/domains/eval/isotonic-calibration.md` |
| 17 | **CLEARScore/AMFO Paper Trail** | Internal: scorecard.py header + CLEAR-Pareto + AMFO tiers | P2 | Multi-fidelity evaluation (scout/validate/synthesize), cost inversion, early-stop heuristics, budget overrun break | Markdown in `data/library/domains/eval/clearscore-amfo.md` |
| 18 | **SEDA Pattern (LMAX Disruptor)** | [id-soft: vet-045] + sediment.py:12–16 | P3 | Ring-bus architecture for event streaming; NOT a sediment pipeline | Markdown in `data/library/domains/arch/seda-ringbus.md` |
| 19 | **Gemma 4 Thinking Config** | [heritage: pi-2026] Gemma 4 Thinking Config (binary MINIMAL/HIGH + regex) | P2 | Binary thinking levels, detection regex `gemma-?4`, thinking_mapping canonical→provider | Markdown in `data/library/domains/models/gemma4-thinking.md` |
| 20 | **OpenAI Evals / HELM / lmms-eval** | AISI directory related tools | P3 | Landscape awareness; OpenAI Evals community benchmarks, HELM holistic eval, lmms-eval multimodal fork | Markdown summaries in `data/library/domains/eval/landscape/` |

---

## Ingestion Instructions for Curation Worker

1. **Pull order**: P0 → P1 → P2 → P3. Within priority, by queue number.
2. **Fetch method**: Use `web_fetch` for GitHub/docs URLs; `firecrawl` for multi-page sites; local read for internal files.
3. **Transform**: Strip navigation/chrome; preserve code blocks, tables, API signatures, version numbers. Convert to Markdown with frontmatter: `title`, `source_url`, `fetched`, `priority`, `domain: eval|inference|qa|arch|models`.
4. **Index**: Write to `data/library/domains/<domain>/<slug>.md`. Update `data/library/domains/index.yaml` with entry.
5. **Verify**: Each ingestion must pass `make doc-llm-validate` (T2 gate).
6. **Signal completion**: Append to `data/coordination/CURATION_LOG.md` with timestamp, source, path, word count.

---

## N11-Specific Ingestion Triggers

| Trigger | Action |
|---------|--------|
| lm-eval v0.5.0 stable released | Re-ingest API guide + release notes; diff against v0.4.12 |
| promptfoo Node.js 22+ required in CI | Update promptfoo docs; verify build pipeline compatibility |
| RAGAS v0.3+ adds new core metrics | Ingest new metrics doc; evaluate vocabulary extension |
| llama.cpp server adds `/v1/completions` logprobs | Critical for lm-eval MCQ tasks; re-ingest server README |
| Inspect adds local model backend (Ollama/llama.cpp) | Re-evaluate ADOPT vs TRACK for agentic axis |
| D-585 matrix amended | Re-ingest decision log; propagate to models.yaml/opencode.json |

---

*End of External Sources. Worker: pull P0 #1–3, #7, #12 first. Curator: Jem (N11).*