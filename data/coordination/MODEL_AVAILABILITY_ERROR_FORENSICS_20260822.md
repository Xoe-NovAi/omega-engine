<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Model Availability Error Forensics — 2026-08-22
**AP Token**: `AP-MODEL-AVAIL-FORENSICS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_model_avail_forensics ⬡ COMPLETE

**Requested by**: @kali · **Type**: READ-ONLY forensic research (sole write: this file)
**Session**: ses_320708d3da00 · **Timebox**: ~75 min · **M23**: no tool-chain failures encountered

---

## VERDICT (Mission 5, stated first)

**The fixed base_url bug does NOT explain the Architect's observed errors — verdict: NO (bug real, but it never fired in recorded telemetry).** The bug was a genuine M22 provenance violation (confirmed by working-tree diff on `src/omega/oracle/model_gateway.py`), and engine-fabric requests for zen/cline/copilot models would indeed have been rejected by OpenRouter with model-not-found-class errors. However, an exhaustive sweep of three independent evidence stores (`opencode.log` 190 MB / 7,842 AI_APIcallErrors; `opencode.db` historical tool-error parts; `data/observability/metrics.db` performance table) found **zero** events carrying the misroute signature (zen/cline-style model IDs receiving OpenRouter-style rejections). The dominant real error classes are TUI-path: Google quota exhaustion, the known G-1 Gemma workhorse collapse, OpenCode Zen upstream instability, and OpenRouter free-tier rate limits. Full classification below.

---

## Mission 1 — Error Classification

### 1.1 Signature census — `~/.local/share/opencode/log/opencode.log` (190,667,860 bytes)

| Signature | Hits | Assessment |
|---|---|---|
| `AI_APICallError` | **7,842** | Master class; broken down below |
| `model_not_found` | 0 | — |
| `no such model` | 0 | — |
| `No endpoints found` | 14 | All `providerID=openrouter`, legitimate routing rejections (tool_choice/tool-use capability gaps), Jun 14–Jul 10. NOT misroute |
| `does not exist` | 105 | Model-related subset = Google `"Requested entity was not found"` (`cloudcode-pa.googleapis.com`), Jun 22–Jul 1 era. Google-side, not OpenRouter |
| `is not available` | 1 | False positive (INFO heredoc content) |
| `unknown model` | 2 | False positives (INFO permission-eval lines containing doc text) |

### 1.2 Provider census across ERROR lines

```
google          5,251     opencode (zen)  3,364     openrouter      1,144
cerebras            6     siliconflow         5     lmstudio            5
github-copilot      2     cline               0     opencode-zen        0
```

### 1.3 Top error classes (provider × model × message)

| Count | Provider | Model | Class |
|---|---|---|---|
| 3,306 | google | gemini-3.5-flash | Quota exceeded (plan/billing) |
| 1,334 | google | gemma-4-31b-it | "Internal error encountered" — **known G-1 free-tier workhorse collapse** |
| ~550 | openrouter | nemotron/dolphin/north-mini :free | Free-models-per-day rate limits |
| ~470 | opencode | mimo-v2.5-free | Internal server error / socket closed |
| ~270 | opencode | deepseek-v4-flash-free | Socket closed / rate limit / **"Free promotion has ended" (Aug 21 00:38Z)** |
| ~100+ | opencode | nemotron-3-ultra-free | `[502] Upstream error from Nvidia: Service temporarily overloaded` |
| ~15 | opencode | x-preview-f-free | "Service Unavailable" / "Endpoint is unavailable" (Aug 21–22, **incl. post-fix**) |

### 1.4 Misroute-signature check (the decisive question)

**Signature sought**: requests intended for zen/cline/copilot models receiving OpenRouter-style rejections.
**Result**: **NOT FOUND** in any store.
- Log: every `No endpoints found` line carries `providerID=openrouter` with genuinely-OpenRouter model IDs (`nvidia/...:free`, `google/gemma-3-4b-it`) — legitimate calls with capability mismatches, e.g. lines 63025/133261/198877/391761.
- DB historical scan (tool-error parts before 08:00 UTC today, both live sessions excluded, signatures `not foun|does not exist|not available|no such model|model_not_found|unknown model|base_url|No endpoints|is not supported` × model context): **0 hits** (3.4 s bounded scan).
- Engine observability `metrics.db.performance` (3,315 rows): dominated by test-synthetic traffic (mock providers, uniform per-provider counts, placeholder model name `"model"`, newest ≈ Aug 19). **Zero** rows with zen/cline IDs under `provider=openrouter`.
- Hub journal (`journalctl --user -u 'omega-hub*'` since Aug 21): zero model/provider error lines.
- Oracle MCP tool errors in DB exist but are a **distinct failure class**: `"Service registry is not a lazy-loadable service or is not initialized"` (`oracle_list_entities`, parts `prt_0174b6a37001ZAjSUSUvTnZaJ8`, `prt_016eee514001Nclhl59orx24xj`, Aug 18) — hub infra, not model availability.

### 1.5 github-copilot hits (both genuine)

- `2026-06-21T15:08:10Z` — `mai-code-1-flash-picker`: *"not accessible via the /chat/completions endpoint"* (Copilot API policy).
- `2026-07-03T19:58:23Z` — `claude-haiku-4.5`: *"The requested model is not supported."*
Both TUI-path Copilot rejections; unrelated to the gateway bug.

---

## Mission 2 — Timeline Correlation

**Fix anchor**: uncommitted working-tree change to `src/omega/oracle/model_gateway.py`; file mtime `2026-08-22 05:42:01 -0300` = **08:42 UTC** (brief said ~08:20 UTC; same-morning window confirmed). Last committed touch of this file: `e2c16d3c` 2026-08-17.

| Window | Errors observed | Consistent with bug? |
|---|---|---|
| Pre-fix (all history → 08:42 UTC today) | Classes in §1.3 | **No** — none carry misroute signature |
| Post-fix (only 2 log errors: 08:43:55Z, 08:44:01Z) | Both TUI `x-preview-f-free` "Service Unavailable" | **No** — identical class to pre-fix zen instability; different root cause |
| Post-fix ConfigError (`requires an explicit base_url`) | 0 occurrences anywhere | Expected: string exists in new code path; fires only when engine instantiates an unconfigured multi-provider entry |

**Parallel remediation discovered mid-mission** (concurrent kali session `ses_fd74cc98dffe…` + roc_racoon audit `CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md`): `config/providers.yaml` now carries explicit `base_url` entries — `opencode-zen: https://opencode.ai/zen/v1` (line 103, endpoint forensically pinned from binary strings `/tmp/opencode/oc_strings.txt`) and `cline: https://api.cline.bot/api` (line 111); loader reads flat `inference.fallback_chain` entries, NOT the detailed `inference.providers:` dicts (yaml comment line 102). Boot verification passed post-edit. **Consequence: the loud-failure gap I identified mid-mission (ConfigError for unconfigured zen/cline) has already been closed in the working tree.** Note: my initial yaml read predated these edits — timeline reconciled.

---

## Mission 3 — Pattern Sweep (other hardcoded URLs / cross-provider defaults)

| # | Location | Finding | Risk |
|---|---|---|---|
| P1 | `src/omega/oracle/backends/openai_compat.py:231` | `create_openrouter_provider()`: `config.base_url = config.base_url or "https://openrouter.ai/api"` — **identical bug shape** to the fixed one | LOW today: dead code, zero callers repo-wide (grep verified). Recommend deletion (D-kal-164 spirit) or alignment with `_KNOWN_BASE_URLS` pattern |
| P2 | `src/omega/oracle/model_gateway.py:382` | `.rstrip("/v1")` uses **character-set** semantics (strips any trailing `/`,`v`,`1`), not suffix removal. Intentional normalization — `openai_compat.py:94` appends `/v1/chat/completions` — but corrupts URLs ending in those chars otherwise (e.g. `https://proxy.internal:8081` → `:808`) | LATENT: now that explicit `base_url` entries are mandatory, recommend `removesuffix("/v1")` |
| P3 | `src/omega/oracle/model_gateway.py:412` | `_create_antigravity` silent default `https://api.antigravity.ai/v1` — same *shape* | ACCEPTABLE: single-provider factory; cross-provider misroute impossible. Consistency note only |
| P4 | `ingestion/guards.py:23`, `ingestion/extractors.py:107` | Hardcoded Google endpoints | Informational: ingestion subsystem, not inference routing |
| P5 | `teachers/nemotron_pipeline.py:305`, `workers/model_updater.py:36-47`, `integrations/quota_pollers.py:292` | Hardcoded OpenRouter/Google/Zen URLs | By design (explicitly OpenRouter-targeted teacher / catalog polling) |
| P6 | `oracle/providers.py:282,304,384,406` | Local LM Studio/Ollama endpoint defaults | Single-provider factories; fine |

**Nothing else shaped like the fixed bug remains live in the inference path.**

---

## Mission 4 — TUI ↔ Engine Coverage Gap

Sources: `~/.config/opencode/opencode.json` (15 TUI providers) vs `config/providers.yaml` (engine fabric, 12 entries).

| Category | Providers | Consequence |
|---|---|---|
| **TUI-only** (unreachable from engine) | cerebras (3 models), cloudflare (7), groq (6), mistral (4), nvidia-nim (3), sambanova (4), siliconflow (6), together (4), native-gguf-extractor/reasoner (dedicated LM Studio ports 1234/1235) | ~37 models invisible to omega CLI / MCP oracle tools |
| **Engine-only** (absent from TUI config) | antigravity (gemini-3.5-flash, gemini-3.1-pro, claude-sonnet-4.6, claude-opus-4.6, gpt-oss-120b), google-compat (gemma-4 thinking variants), anthropic (claude-opus-4.8 etc.), xai (grok-4.3-web), engine-local aliases (13 `-local` names) | Invisible to TUI chat without config additions |
| **Both-but-divergent** | openrouter: TUI IDs (`qwen3-coder-480b:free`, `deepseek-r1:free`) ≠ engine IDs (`qwen/qwen3-coder:free`, `deepseek/deepseek-v4-flash:free`); google ≈ google-standard; lmstudio ≈ lmster; ollama enabled-TUI/disabled-engine | Same backends, different ID conventions → cross-path model handoffs risk not-found errors even when wired correctly |
| **Zen access asymmetry** | TUI reaches zen via built-in `opencode` provider (observed: mimo-v2.5-free, deepseek-v4-flash-free, nemotron-3-ultra-free, x-preview-f-free); engine reaches it via `opencode-zen` entry (catalog: big-pickle, ring-2.6-1t-free, kimi-k2.6, glm-5.1 …) | Partial overlap only; catalog-level models differ per side |
| **cline** | Engine-only entry; now correctly wired (`api.cline.bot/api`) BUT advertised free models are **client-gated at HTTP 403** ("only available via Cline product surfaces") per `CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` | Config-complete yet operationally blocked without CLI-wrapper backend or API-permitted models |

---

## Mission 5 — Verdict & Residual Causes

**Verdict: NO — the fixed bug does not explain the Architect's observed errors.** It was a real, live M22 violation whose failure mode (OpenRouter rejecting foreign model IDs) matches the *reported symptom class*, but zero such events exist in any telemetry store. The observable error mass decomposes as:

1. **Google quota exhaustion** — 3,306 hits (gemini-3.5-flash et al.). Largest single class.
2. **G-1 workhorse collapse** — 1,334 gemma-4-31b-it internal errors; already a tracked P0.
3. **OpenCode Zen upstream instability** — x-preview-f-free Service Unavailable (continues *post-fix*: 08:43/08:44 UTC today), Nvidia 502 overload on nemotron-3-ultra-free, DeepSeek V4 Flash free-promo termination (Aug 21 00:38Z). This is most likely what the Architect experienced as "models that should be available" failing.
4. **OpenRouter free-tier daily rate limits** — ~550 hits.
5. **Hub service-registry init failures** — intermittent total breakage of `oracle_*` MCP tools (distinct bug, needs its own ticket).

**Caveat (honest uncertainty)**: the engine fabric's observability trail is nearly empty of real production traffic (test-synthetic dominance in `performance`). If pre-fix engine dispatches occurred before observability wiring, their rejections would have vanished unrecorded. The claim "never fired" is therefore scoped to *recorded* telemetry — which is itself a finding: **M22 provenance capture for engine-path inference is too sparse to adjudicate past behavior**, and should be treated as a gap.

**Recommended follow-ups** (for kali triage; no work performed by this mission):
1. Delete dead `create_openrouter_provider` (P1) and swap `.rstrip("/v1")` → `.removesuffix("/v1")` (P2).
2. Ticket the hub service-registry lazy-load failure (oracle tools).
3. Add request-level wire-URL logging to `openai_compat._send_request` so future misroutes are directly observable (strengthens M22 enforcement).
4. Zen upstream instability → fold into G-1 workhorse strategy rather than chasing as a bug.

---

## Evidence Index

| Artifact | Reference |
|---|---|
| Fix diff | `git diff src/omega/oracle/model_gateway.py` (uncommitted; mtime 08:42 UTC) |
| Factory map | `src/omega/oracle/model_gateway.py:559-563` (openrouter/opencode-zen/cline/github-copilot → `_create_openrouter`) |
| Wire URL build | `src/omega/oracle/backends/openai_compat.py:94` |
| Log samples | opencode.log lines 63025, 133261, 198877, 391761 (No-endpoints); 2026-08-21T00:38:25Z (promo ended); 2026-08-22T08:43:55Z (post-fix S.U.) |
| DB parts | `prt_0174b6a37001ZAjSUSUvTnZaJ8`, `prt_016eee514001Nclhl59orx24xj` (service-registry errors) |
| Observability | `data/observability/metrics.db` table `performance` (3,315 rows, test-synthetic) |
| Parallel remediation | `config/providers.yaml:102-111`; `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` |
| Zen endpoint proof | `/tmp/opencode/oc_strings.txt` (binary provider registry), per concurrent kali session |

**Redaction note**: no secrets/tokens were encountered in cited excerpts; credential references appear as env-var names only.

---

## M15 Gnosis (embedded — read-only constraint)

L1: Swept 190MB log + 17.7GB DB + observability DB for misroute signatures after kali's base_url fix; found zero misroute events; error mass is TUI-side quota/outage classes; discovered parallel kali remediation closing the ConfigError gap mid-mission.
L2: Absence of evidence here is meaningful but bounded — engine-path telemetry sparsity means "never fired" holds only for recorded data; two inference paths with divergent model-ID conventions remain a standing confusion source.
L3: A fix that removes a silent failure mode must simultaneously add positive observability of the corrected behavior, or forensics can never distinguish "fixed" from "never exercised".

## M11 Lesson Seeds (proposed, staged for Scribe)

- L3 candidate: Silent cross-provider URL defaults violate provenance twice — once at misroute time, once retroactively, because the absence of wire-URL logging makes the bug's history unauditable.
- L3 candidate: When a factory serves multiple providers, per-provider endpoint constants belong in config validation (fail-fast), never in factory defaults.
- Process note: parallel sessions editing the same config during a forensic run require re-verification of file state immediately before citing it (my yaml read was stale within minutes).

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->
