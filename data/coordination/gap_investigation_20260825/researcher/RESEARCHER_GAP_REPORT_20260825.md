<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 RESEARCHER GAP REPORT — Deep Gap Investigation (Web Research & Empirical Portfolio)
**AP Token**: `AP-RESEARCHER-GAPINV-20260825`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_gap_research ⬡ 2026-08-25
**Dispatched by**: Kali (ses_fdef2be4effe4pAaLXCTUx62GO) | **Method**: Sovereign Search T0-T6; 3 expert leaves (ses_fc4a5c456ffe5hc5SL0HNYruGp, ses_fc4a5a3caffeF3uLUEPwQ5cwj9, ses_fc4a571a5ffe5I2FxkzQYKnJbH); every claim traces to a retrieved URL.
**Vision test applied**: every verdict answers "does this serve M7 local-first sovereignty + the one-install community-tool horizon?"

---

## VERDICT SUMMARY TABLE

| Gap | Verdict | One-line |
|-----|---------|----------|
| R35 Model degradation | **ACTIONABLE-NOW** | Silent provider swaps are documented 2026 reality; canary-hash tripwire is the standard detection pattern |
| R36 Baseline calibration | **FILLED-STALE→ACTIONABLE-NOW** | Methodology canon exists (Miller error bars, n≥30 floor, power analysis); engine lacks implementation |
| R33 Cold session context | **ACTIONABLE-NOW** | Industry consensus = hybrid preload+JIT, lean memory files <100 lines, compaction at ~70% window |
| R34 Provider bands | **ACTIONABLE-NOW (empirical-only)** | Google killed static quota tables; bands must be measured, never hardcoded |
| DP-2 Context Window Registry | **ACTIONABLE-NOW (CRITICAL freshness)** | Major spec corrections: Qwen3-2507=262K native; Nemotron3-Ultra=262K native (1M=extended+warning); Gemma4-31B=256K; Gemini output default 8K trap |
| DP-3 Planner/Executor Router | **RESEARCH-NEEDED→DESIGN FILLED** | 2026 consensus: static tier map v1 → learned router only at volume; cascade-with-verifier for quality floors |
| GN-1..4 NotebookLM | **ACTIONABLE-NOW + CORRECTIONS** | Product renamed "Gemini Notebook" Jul 16 2026; free Deep Research = **10/mo NOT 30**; real account-ban case exists; no consumer API |
| H1-H5 kill-conditions | **DRAFTED** (separate file) | Grounded in τ-bench/PAE/LCFO/power-analysis literature; see `H1_H5_KILL_CONDITIONS_DRAFT.md` |
| R31 Plugin scope reduction | **RESEARCH-NEEDED→CONSENSUS FOUND** | Minimal core (loop+state+tool registry) + MCP surface; three documented monolith regrets validate our architecture |

---

## R35 — MODEL DEGRADATION · Verdict: ACTIONABLE-NOW

### Findings (sourced)
- **Silent updates are systemic, not paranoia**: arXiv 2608.11803 audited 9 providers — only 2/9 flag safety-relevant changes; 0/9 expose verifiable API-to-eval round-trip; documents alias re-pointing (Google Vertex auto-updated aliases; DeepSeek `deepseek-chat` resolving to successive versions over 19 months). https://arxiv.org/html/2608.11803v1
- **Precedent cases**: GPT-4 code-execution rate dropped 52%→10% over 3 months with no version change; Claude Sonnet 4 routing bugs hit up to 16% of requests (Anthropic Aug-2025 postmortem); Mistral `mistral-ocr-latest` silently moved OCR-2512→OCR-4 between Jun 18–Jul 3, 2026. https://arxiv.org/html/2604.27789v1 , https://inferbase.ai/blog/silent-llm-model-swaps
- **Silent quantization confirmed on aggregators**: OpenRouter observed same-model/same-nominal-quant producing different outputs per host; shipped FP16-guaranteed "Exacto" tier; Together AI is the only gpt-oss-120b host disclosing quant level. https://tianpan.co/blog/2026-05-02-silent-quantization-model-you-paid-for-last-quarter
- **Gemini free-tier quantization**: community suspicion documented (unanswered transparency request), structural free/paid divergence confirmed in official docs (free tier Flash-family only; free-tier data used for training; Pro free tier removed Apr 2026). Hard evidence of free-tier weight degradation: **UNVERIFIED** — treat as suspicion. https://discuss.ai.google.dev/t/how-can-we-verify-that-the-trial-and-paid-versions-of-gemini-use-the-exact-same-non-quantized-model-request-for-more-transparency/95691/1 , https://ai.google.dev/gemini-api/docs/pricing
- **Counterweight**: pinned Claude snapshots showed NO sustained regression Feb–Apr 2026 on public trackers — drift reports often correlate with user-side prompt/context drift. Honest baselines matter. https://callsphere.ai/blog/claude-sonnet-opus-haiku-silent-downgrade-theory

### Detection methods (the actionable core)
1. **Behavioral fingerprinting beats golden-output matching**: fingerprinting achieved ~86% detection power vs ~0% for single-output diff (non-determinism makes byte-diff noise-vs-noise). Probe suite of 30–100 frozen prompts covering format compliance, refusal boundaries, length distributions. https://tianpan.co/blog/2026-04-19-invisible-model-drift-silent-provider-updates
2. **Canary-hash tripwire (3 layers)**: pin dated snapshot → run 15–40 frozen prompts at temp 0 on schedule → hash outputs → alarm on step-changes in refusal-rate/length/tool-call-shape. Establish k≈10-run noise floor BEFORE alerting. https://dreaming.press/posts/how-to-catch-a-silent-model-upgrade-hosted-endpoint-drift.html
3. **Log served-model identity**: OpenTelemetry GenAI `gen_ai.response.model` ≠ `gen_ai.request.model`; OpenAI `system_fingerprint` as weak hint. https://multigrid.ai/learn/silent-model-updates
4. **External drift canary**: LiveBench (contamination-resistant, monthly refresh) binds to whatever is actually served. https://github.com/livebench/livebench

### Recommended GAP_REGISTRY change (R35)
Close as FILLED-METHOD; open implementation ticket: "Provider drift canary" — extend existing M22 provenance capture (`GenerateResult.provider_name`) with `served_model_id` + scheduled 30-prompt fingerprint run per cloud provider, noise-floored alerting to observability (local-only, M8-compliant).

---

## R36 — BASELINE CALIBRATION · Verdict: ACTIONABLE-NOW (methodology filled; implementation absent)

### Findings
- **Canonical stats**: Evan Miller "Adding Error Bars to Evals" — paired-difference SEs, clustered SEs for repeated decodes, explicit sample-size/power formula. https://arxiv.org/pdf/2411.00640
- **Tooling**: `evalci` — CI + paired permutation/McNemar from per-item tables; re-analysis showed 3/8 adjacent leaderboard gaps insignificant after multiplicity correction. https://arxiv.org/html/2607.04429v1
- **Sample-size law**: detecting a 1pp delta at 80% power needs 3,800–9,600 examples (ρ∈[0.4,0.7]); n=1,000 detects only ~2–3pp; N<15 → report no statistics; N≥30 minimum for reliable CIs; Tango interval preferred for paired binary. https://clawrxiv.io/abs/2604.01974 , https://statsforevals.com/which-method.html
- **Agent-specific**: Procedure-Aware Evaluation found 27–78% of reported agent "successes" are corrupt successes hiding policy violations; pass^k gating collapses fast. https://arxiv.org/html/2603.03116 ; τ-bench family https://taubench.com/
- **Workflow standard**: freeze prompt → golden set → version-tagged baseline → same-dataset comparison → merge gates. Pin snapshots (`-latest` pins are how providers masquerade as your regressions). https://vadimall.com/posts/promptfoo-ai-eval-suite-prompt-regression-testing

### Recommended GAP_REGISTRY change (R36)
Split: methodology research CLOSED (this report); open P2 ticket "Golden-set calibration harness" — ≥30-item frozen golden set per core oracle path, paired-difference reporting, snapshot pinning. Directly serves FLE study M1/M2 metrics (tokens-per-finding and ceremony index both need honest baselines).

---

## R33 — COLD SESSION CONTEXT · Verdict: ACTIONABLE-NOW

### Findings
- **Canonical pattern (Anthropic)**: hybrid — static memory files preloaded + just-in-time retrieval via lightweight identifiers (paths/grep); compaction; structured note-taking (NOTES.md); sub-agent isolation. Principle: "smallest set of high-signal tokens." https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Write/Select/Compress/Isolate framework** (LangChain): external scratchpads, selective retrieval, summarization, sub-agent quarantining; context-failure taxonomy (poisoning/distraction/confusion/clash). https://rlancemartin.github.io/2025/06/23/context_engineering/
- **Memory-file conventions**: lean always-loaded files (<100 lines / <500 words) holding non-obvious decisions; MEMORY.md append-only decision log written BY the agent; skills loaded JIT. https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/
- **Overstuffed context backfires**: maximalist context files prime over-action; ETH Zurich manual-vs-automated memory findings cited. https://dev.to/max_quimby/ai-agent-memory-in-2026-auto-dream-context-files-and-what-actually-works-39m8
- **Budget guidance (single practitioner source — UNVERIFIED as standard)**: system 10–15%, tools 15–20%, retrieved knowledge 30–40%, history 20–30%; compact at ~70% of effective window, not exhaustion; fewer tools beat more. https://tianpan.co/blog/2026-02-26-context-engineering-memory-compaction-tool-clearing
- **Letta memory blocks**: labeled blocks always visible (no retrieval); archival via explicit tool calls; git-backed memory versioning (Feb 2026). https://docs.letta.com/v1-sdk/memory/memory-blocks

### Engine fit (vision test)
Our OMEGA_CODEX hydration sequence + `.opencode/anchored-summary.md` already implement the hybrid pattern. Gap: Codex size discipline (currently ~424 lines concatenated — exceeds the <100-line lean-file consensus by 4×) and no ~70%-window compaction trigger tied to effective (not advertised) windows. This validates M15 and suggests a "Codex slimming" candidate ticket — but note M18 sane-boundary: do NOT compress to semantic loss; trim duplication, not doctrine.

---

## R34 — PROVIDER BAND ADJUSTMENTS · Verdict: ACTIONABLE-NOW (empirical measurement required)

### Findings (fresh Aug 2026)
- **Gemini API free tier**: mechanics stable (RPM+TPM(input)+RPD, per-project, reset midnight Pacific) BUT Google removed the static per-model table — quotas now live behind AI Studio dashboard; third-party snapshots CONFLICT (2.5 Pro RPD: 25 vs 50 vs 100 post-Dec-2025 cuts). **Any hardcoded band number will rot.** https://ai.google.dev/gemini-api/docs/rate-limits (updated 2026-08-18)
- **Key policy change**: from June 19, 2026 Gemini API rejects unrestricted API keys — keys must be restricted. https://discuss.ai.google.dev/t/bug-quota-ai-pro-subscription-fails-to-sync-in-antigravity-ide-stuck-on-free-tier/134635
- **Antigravity**: Dec 2025 cuts (RPD 250→20, RPM 10→5); Mar 2026 AI Credits ($25/2,500 credits); Free/AI Pro $20/Ultra $100/Ultra Max $200 plans; legacy Gemini CLI retired Jun 18 2026 into shared credit pool. Widely-reported reliability failures: 4–10 day lockouts instead of 5h refresh, subscription-sync bugs, MODEL_CAPACITY_EXHAUSTED. https://vibecoding.app/blog/google-antigravity-pricing-2026 , https://discuss.ai.google.dev/t/bug-antigravity-ide-critical-quota-error-7-day-lockout-for-google-ai-pro-subscriber/114724
- **OpenCode Zen**: free roster (MiMo-V2.5 Free, Hy3 Free, Nemotron 3 Ultra Free, Big Pickle, Ox Alpha Free, Muse Spark 1.2…) with **no published numeric limits** — maintainer: "free usage is dynamic… shifting based off capacity vs demand." User reports: opaque "Free usage exceeded" errors, ~24h cooldowns, sustained 429s. Nemotron Ultra Free rides NVIDIA trial endpoints ("logged for security purposes"). https://opencode.ai/docs/zen/ , https://github.com/anomalyco/opencode/issues/28055 , https://github.com/anomalyco/opencode/issues/43786
- **OpenRouter free**: 20 req/min + 50 req/day; ≥$10 lifetime credits → 1,000/day shared pool; lowest-priority serving; data-policy gating can 404 `:free`. https://openrouter.ai/docs/faq

### Recommended GAP_REGISTRY change (R34)
Reframe gap: bands cannot be a registry — they must be **observed telemetry**. Ticket: "Quota telemetry module" — record 429/quota-error events per provider with timestamps into local observability; derive empirical bands (matches C-10.5 quota-aware routing, extends it with historical windows). Never hardcode Google's moving numbers.

---

## DP-2 — CONTEXT WINDOW REGISTRY · Verdict: ACTIONABLE-NOW (CRITICAL corrections)

### The Registry (vendor-advertised, Aug 2026)

| Model | Advertised window | Critical caveats | Source |
|-------|------------------|------------------|--------|
| Qwen3 original line (incl. 1.7B/4B/32B) | 32,768 native; 131,072 w/ YaRN | Static YaRN implementations degrade SHORT texts; vendor: don't enable YaRN if avg ctx ≤32K; default max_position_embeddings=40,960 | https://huggingface.co/Qwen/Qwen3-4B-GGUF |
| Qwen3-4B-Thinking-2507 (+Instruct-2507) | **262,144 NATIVE** (no YaRN) | Vendor recommends ≥131K due to long reasoning chains | https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507 |
| Nemotron 3 Ultra (550B-A55B, released Jun 4 2026) | **262,144 native**; 1M ONLY via `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` | NVIDIA explicit warning: beyond 262K "validate output quality"; RULER@1M=94.7% is VENDOR-CLAIMED, no independent replication | https://docs.nvidia.com/nim/large-language-models/2.0.6/day-0/get-started-nemotron-3-ultra.html |
| Gemma 4 (E2B/E4B) | 128K | Hybrid sliding-window+global attention, p-RoPE | https://ai.google.dev/gemma/docs/core/model_card_4 |
| Gemma 4 12B / 26B-A4B / **31B Dense** | **256K** | KV-cache cost heavy: 128K adds ~8–16GB over weights — relevant to our 8GB UMA ceiling | https://huggingface.co/google/gemma-4-31B , https://www.compute-market.com/blog/gemma-4-local-hardware-guide-2026 |
| Gemini 3.x family (3 Flash/3.1 Pro/3.5 Flash/3.7 Flash GA) | 1M input | Output caps 64K, but some models DEFAULT to 8,192 output unless raised; pricing jumps >200K input | https://ai.google.dev/gemini-api/docs/latest-model , https://www.aifreeapi.com/en/posts/gemini-3-1-pro-output-limit |

### Effective-window truth (third-party)
- STRING (ICLR 2025) reproduction: small open 7B-class models deliver effective ~6K–18K vs 32K+ claims. https://github.com/psychofict/llm-effective-context-length
- arXiv 2601.15300: first systematic intelligence-degradation thresholds for open Qwen under long contexts. https://arxiv.org/abs/2601.15300
- Lost-in-the-middle U-curve persists industry-wide 2026; directional survey claim "most models break 30–40% earlier than claimed". RULER remains reference suite. https://github.com/NVIDIA/RULER
- **UNVERIFIED**: no independent effective-window number exists yet for Nemotron 3 Ultra, Gemma 4, or Gemini 3.x specifically.

### Recommended GAP_REGISTRY change (DP-2)
Registry schema: `{model, advertised_window, native_vs_extended, effective_confidence: vendor_claim|independent|none, output_default_cap, kv_cost_note}`. Route conservatively: treat 262K-native models as trustworthy to ~131K until independently benched; NEVER route Gemma 4 256K claims to our 8GB-UMA hardware without KV math. This is exactly the M7-honesty move: don't let marketing windows write checks local RAM can't cash.

---

## DP-3 — PLANNER/EXECUTOR MODEL ROUTER · Verdict: DESIGN FILLED (research complete)

### Findings
- **2026 production consensus stack**: rule-based/static tier mapping as baseline → classifier routers (RouteLLM lineage) for strong/weak binary → cascade-with-verifier escalation (FrugalGPT lineage) → semantic/capability routing for multi-route dispatch. Hybrid "rules pre-filter + embeddings + rules post-filter" is the recommended shape. Purely-learned routing is NOT the norm.
- **RouteLLM** (LMSYS): canonical learned router, Apache-2.0, stable/research-grade. https://github.com/lm-sys/RouteLLM
- **FrugalGPT** (Stanford): canonical cascade, maintained as reference. https://github.com/stanford-futuredata/FrugalGPT
- **LLMRouter** (ulab-uiuc): 2026 successor — 16+ routing methods, xRouteBench, actively maintained through Aug 2026; learned routers beat strongest fixed baseline by 14.6% relative. https://github.com/ulab-uiuc/LLMRouter
- **Unified theory**: routing+cascading unified (Dekoninck et al.). https://arxiv.org/abs/2410.10347
- **Productionization signal**: vLLM Semantic Router v0.1 (Jan 2026) — programmable MoM routing layer, capability/policy/cost-aware. https://github.com/vllm-project/semantic-router
- **Practical numbers**: 40–70% of production queries servable by cheap tier without detectable loss; router must be cheaper/faster than the routed delta; worst-case cascade latency = sum of hops. https://shuji-bonji.github.io/ai-agent-architecture/strategy/routing-vs-cascading
- **Capability-routing finding**: good routers make a weak-model POOL outperform its best single member (IRT-Router). https://tianpan.co/blog/2025-10-19-llm-routing-production

### Engine fit (vision test)
This VALIDATES our existing architecture rather than demanding new machinery: C-10.5 quota-aware routing IS the static tier map (correct v1 per consensus). Recommendation: keep static capability/quota mapping as the deterministic spine; add cascade-with-verifier only where quality floors matter (entity synthesis); consider LLMRouter-style learned routing ONLY if local/cloud volume grows enough that misrouting cost exceeds router cost. Local-first alignment: the router itself must be cheap/local (embedding classifier or rules) — never a cloud call.

---

## GN-1..4 — NOTEBOOKLM · Verdict: ACTIONABLE-NOW + MAJOR CORRECTIONS

### Corrections to current workstream assumptions
1. **PRODUCT RENAMED**: NotebookLM → **Gemini Notebook**, July 16, 2026 (links redirect). All docs/tickets should adopt new name. https://workspaceupdates.googleblog.com/2026/07/notebooklm-is-now-gemini-notebook.html
2. **FREE DEEP RESEARCH = 10/MONTH, NOT 30**. Multiple independent 2026 trackers converge: Free = 10 DR/month, 100 notebooks, 50 sources/notebook (500k words each), 50 chat/day, 3 Audio Overviews/day. Plus ($4.99)=3/day; Pro ($19.99)=20/day. High-confidence secondary-source convergence; no live primary Google page retrieved. **GN workstream quota math must be corrected.** https://glasp.co/articles/notebooklm-2026 , https://felloai.com/is-notebooklm-free/
3. **NO official consumer API** as of Aug 2026; Enterprise REST API EXISTS (Gemini Notebook Enterprise, Discovery Engine endpoints, notebook/source CRUD + batch upload + audio generation; min ~15 licenses per forum report). https://notebooktoolkit.com/blog/notebooklm-api-status , https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks
4. **Real account-ban risk**: notebooklm-py Issue #228 — user account DISABLED after one library use (Mar 2026); maintainer acknowledged timing, explored TLS-fingerprint mitigation. Library uses undocumented RPC APIs; README warns breakage. https://github.com/teng-lin/notebooklm-py/issues/228
5. **Library state**: notebooklm-py v0.8.1 (Aug 14, 2026), MIT, ~18.9K stars, very active (~30 releases since Jan 2026), embedded MCP server, CLI, bulk source import, audio overviews. Chrome 127+ App-Bound Encryption blocks cookie extraction on Windows (we're Linux — lower risk). https://github.com/teng-lin/notebooklm-py
6. **Auth-isolation**: dominant pattern = browser session cookies (no OAuth exists); PleasePrompto/notebooklm-mcp offers native multi-account via isolated Chrome profiles (`--account work`). Rotation-to-evade-limits projects exist and are risky. Google ToS (Jul 30, 2026) prohibits automated access violating machine-readable instructions — automation sits gray-to-violating. https://github.com/PleasePrompto/notebooklm-mcp , https://policies.google.com/terms?hl=en-US

### Vision-test verdict
GN workstream survives the sovereignty test ONLY as: (a) ingestion target for OUR OWN docs (legitimate use), (b) with ban-risk acknowledged and isolated accounts (never the Architect's primary Google identity), (c) quota plan rebased to 10 DR/mo. The Enterprise API path is the clean long-term answer if budget ever allows; otherwise notebooklm-py with conservative pacing. Recommend GAP_REGISTRY: correct GN-3 quota figure, add ban-risk mitigation requirement (dedicated account + Chrome profile isolation + rate pacing), rename references.

---

## R31 — PLUGIN SCOPE REDUCTION · Verdict: CONSENSUS FOUND (validates current architecture)

### Findings
- **Minimal-core consensus (2026)**: loop + typed state + tool registry in core; everything else extension. OpenAI Agents SDK = Agent/Runner/Handoffs/Guardrails/Sessions/Tracing built-in, rest pluggable. smolagents = ~1,000 lines total. https://openai.github.io/openai-agents-python/ , https://the-agent-report.com/2026/07/ai-agent-frameworks-comparison-2026-langgraph-crewai-autogen/
- **Documented monolith regrets**: (1) LangChain→LangGraph ("honest reckoning with its own complexity"); (2) AutoGen v0.4 event-driven rewrite, then maintenance-mode merger into Microsoft Agent Framework; (3) **OpenAI Assistants API deprecated Aug 26, 2026** in favor of leaner Agents SDK — heavyweight hosted-state core retired for thin client primitives; (4) Letta rebuilt memory internals as git-backed Context Repositories (Feb 2026). https://agentmarketcap.ai/blog/2026/04/06/smolagents-langgraph-crewai-code-first-orchestration , https://developers.openai.com/api/docs/guides/agents
- **MCP as universal extension surface**: MCP spec moved to stateless core (Jul 28, 2026) — strengthens plugin-via-MCP as THE pattern. https://blog.modelcontextprotocol.io/posts/2026-07-28/
- **Memory placement splits the field**: Letta makes memory THE core; most others keep it pluggable. Observability universally pluggable tracing processors. Evals trend toward trace-replay.

### Engine fit
Omega's shape (oracle loop + gateway + memory core; skills/hooks/MCP as extension; zero-telemetry local observability) matches the winning pattern. R31 recommendation: keep core minimal; resist adding evals/routing/guardrails machinery INTO core — expose as MCP/skills. The Assistants-API deprecation is a cautionary tale against hosted-state fat cores that maps directly onto our Hub-split plans (Phase Γ).

---

## CROSS-CUTTING SYNTHESIS (Triangulation)

**Convergence (The Truth)**:
1. Silent provider drift is real, measurable, and detectable with cheap local probes — a perfect M7 fit (local verification of cloud teachers).
2. Statistical honesty floors exist: n≥30 for any claim, paired tests, snapshot pinning. Our FLE scorecard M2 ceremony-index fix aligns with this literature.
3. Minimal core + MCP surface won the framework wars; three major vendors/frameworks paid the monolith tax publicly.
4. Every "advertised" number (context windows, quotas) needs an effective-confidence field. Marketing writes checks hardware can't cash.

**Divergence (The Uncertainty)**:
- Exact Gemini free-tier RPD: UNVERIFIED (dynamic dashboard, conflicting snapshots).
- Effective long-context quality for Nemotron 3 Ultra / Gemma 4 / Gemini 3.x: no independent benchmarks yet.
- NotebookLM exact quotas: strong secondary convergence, no primary source.
- H3 (Ambiguity Attractor) has analogical grounding only — requires novel measurement design.

**Raw Signal (L3)**: *Advertised capability is a vendor claim; effective capability is an engineering measurement. A sovereign runtime measures its own teachers.* This is M22 (provenance) generalized from responses to capabilities — and it is the connective tissue across R35/R36/R34/DP-2.

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ GAP-INVESTIGATION-PORTFOLIO ⬡ 2026-08-25*
