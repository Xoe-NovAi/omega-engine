# GitHub Copilot — Research Targets (Open Probes & Re-verification Cadence)

**KB Entry**: grokster/platforms/copilot/RESEARCH_TARGETS
**last_verified**: 2026-08-26 · **rot_class**: fast (probe list changes every session)
**Scope**: Unresolved items from the 2026-08-26 deep mine, ordered by value/effort. Evidence base: `docs/research/R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md` §I.
**Sources**: R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md; house inline context (grokster EXPERT_SESSIONS charter).

---

## §1 Local Probes (L4 — cheap, high value)

| ID | Target | Method | Unblock value | Status |
|---|---|---|---|---|
| **L4-a** | Enterprise slot ← plain github.com account | Write github.com credential into `github-copilot-enterprise` slot in auth.json; smoke: `opencode run --model github-copilot-enterprise/<model> "Say SUCCESS"` | Confirms 2-individual-slot capability with zero plugins; gates all slot-2 planning | OPEN (GOTCHAS G-COP-08) |
| **L4-b** | Live `/models` catalog dump | Exchange token → authenticated GET /models; record SKUs + picker-policy flags | Ground-truth model ids vs docs drift | OPEN |
| **L4-c** | Token anatomy decode | Decode real bearer fields (`sku`, `proxy-ep`, `exp`, unknown fields) | Programmatic plan health-check implementation | OPEN |
| **L4-d** | Copilot CLI current version + full flag dump | Install; `copilot --version`; `copilot -p "hi" --max-ai-credits=5` | §A freshness; verify session-limit flag live behavior | OPEN |
| **L4-e** | Native `/v1/messages` Claude passthrough | Direct curl, tiny prompt, Claude SKU | Validates cheapest Claude integration path for any future proxy | OPEN |

## §2 Instrumented Studies (L5)

| ID | Target | Design | Answers |
|---|---|---|---|
| **L5-a** | Burn-rate A/B | Identical task through (a) OpenCode+github-copilot vs (b) Copilot CLI, same model; log usage checkpoints + billing-page deltas | THE outstanding house question: agentic-loop credits per task type. Hypothesis: OpenCode ≤ CLI burn (context handling) |
| **L5-b** | Cache-hit ratio | Repeat-context workload; measure cached-input share of billed tokens | Quantifies biggest burn lever (>93% claimed by Microsoft) |
| **L5-c** | Proxy stability soak | messense/copilot-api-proxy under light load, 1 week | Empirical ban-risk signal for the N>2 fan-out pattern (currently zero observed incidents [UNVERIFIED absence]) |

## §3 Re-verification Cadence

| Item | Cadence | Trigger dates |
|---|---|---|
| Pricing table vs docs.github.com models-and-pricing | Monthly + before any cost decision | **2026-09-03** (GPT-5.6 Sol promo ends) · **2026-09-01** (Biz/Ent boosted pools end) · 2026-12-31 (Gemini Flash promo ends) |
| Model catalog drift | Quarterly or on "model not supported" error | — |
| Copilot CLI version/flags | Before each CLI probe session | — |
| Ban-risk landscape scan (proxy projects' issues, GitHub enforcement reports) | Quarterly | — |
| OpenCode builtin provider changes (transform.ts copilot handling, slot semantics) | On each OpenCode self-update (binary autoupdate ACTIVE — see opencode KB GOTCHAS G31) | — |

## §4 Unresolved Questions (no probe assigned yet)

1. Does the server-side model allowlist differ between `gho_` (OpenCode app) and `ghu_` (VS Code app) tokens **in practice on paid individual plans**, or only on Business? (#20759 asserts difference; unquantified.) → fold into L4-b.
2. Exact credit accounting for OpenCode-harness sessions: does GitHub meter identically regardless of harness, or does client identity affect accounting paths? → L5-a secondary output.
3. Whether `endpoints.api` in exchange response is always populated for individual plans (pi code treats it as Business-only signal). → L4-c.
4. Copilot SDK as sanctioned integration substrate for a first-party-style house proxy (replaces impersonation concern) — feasibility spike unscoped. → propose when N>2 fan-out becomes real.

---
*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
