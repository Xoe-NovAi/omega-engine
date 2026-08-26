# Cline — Research Targets (open probes & unknowns)

**KB Entry**: grokster/platforms/cline/RESEARCH_TARGETS
**last_verified**: 2026-08-26 · **rot_class**: fast
**Owner**: jem (standing Cline specialist session)
**Sources**: `docs/research/R_CLINE_DIRECT_API_DEEP_MINE_20260826.md` §J, `R_CLINE_COPILOT_PROVIDER_SETUP_20260826.md` residual unknowns

---

## Standing protocol

Run the 30-second gate re-probe BEFORE any posture change; escalate result to kali before any opencode.json edit:

```bash
curl -s -X POST https://api.cline.bot/api/v1/chat/completions \
  -H "Authorization: Bearer $CLINE_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"deepseek/deepseek-v4-flash","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```
200 = gate lifted (escalate immediately) · 403 = gate stands · 401 = rotate key first.

## Probe queue (P1–P10, carried from deep-mine §J)

**STATUS UPDATE 2026-08-26 (jem M3 — key extracted to `.env`, probes executed live):**

| # | Probe | Status | Finding |
|---|---|---|---|
| P1 | Gate re-check `deepseek/deepseek-v4-flash` | ✅ **RESOLVED 2026-08-26** | HTTP **403 stands**: *"only available via Cline product surfaces. If you are using an old version of Cline, please update to the latest version"* — note NEW version-hint suffix (feeds P5 hypothesis: gate may inspect client-version signals). |
| P2 | Free-model raw-API test (`minimax/minimax-m2.5`) | ✅ **RESOLVED 2026-08-26** | **NOT client-gated — credit-metered**: `insufficient_credits`, balance $0.01. The free-models page's blanket "not supported through the API" OVERGENERALIZES: per-id behavior varies (see GOTCHAS G15). Docs contradiction resolved: getting-started's curl example is plausible for non-gated ids. |
| P3 | Authenticated `/models` listing | ✅ **RESOLVED-NEGATIVE 2026-08-26** | **No public model-listing endpoint exists**: `/api/v1/models`, `/v1/models`, `/api/models`, `/api/v1/model` all → 404 `{"error":"Not Found","success":false}`. Docs' "model catalog" (supportsReasoning/supportsImages flags) is served to product clients via a private route only. Caps/entitlement discovery must use error-differentiation probes instead. |
| P7 | Namespace truth | ✅ **RESOLVED 2026-08-26** | **`cline-pass/` CONFIRMED LIVE**: POST with `cline-pass/deepseek-v4-flash` → clean `ENTITLEMENT_ERROR: "the user is not subscribed to required model plan"` (namespace valid, entitlement missing). Non-hyphenated `clinepass/…` → anomalous `"empty response content"` (see GOTCHAS G14). |
| P8 | 1M-context on cline-pass variant | ⏸ BLOCKED on ClinePass GO | Entitlement required before smoke possible. |
| P9 | `cline version` stamp | ⬜ open | |
| P10 | Dashboard quota magnitudes | ⏸ BLOCKED on ClinePass GO | |
| P4/P5/P6 | Gate mechanism / header matrix / wire-param capture | ⬜ open (lower priority — P1+P7 already establish gate is id-and-plan-keyed for practical purposes; P1's version-hint message keeps client-signal hypothesis alive) | |

**POSTURE CONSEQUENCE (M3)**: paid gate = **pure entitlement keyed to the SAME static key** — subscribing to ClinePass unlocks `cline-pass/*` through the already-extracted key and already-drafted OpenCode block with ZERO further config change. GO/NO-GO is now fully informed: the only remaining unknown post-subscribe is quota magnitude (P10) and context caps (P8).

## Additional open items (beyond deep-mine)

| ID | Unknown | Path |
|---|---|---|
| A1 | Whether Enterprise API key-management endpoints (`GET/DELETE /api/v1/api-keys`) work with plain-account tokens or require enterprise-admin tokens | one authenticated curl each |
| A2 | Whether ACP mode consumes gated free models legitimately (gate targets model access, not agent access — inference only) | run `cline --acp` from Zed/Neovim against a free model, observe billing/gate behavior |
| A3 | Cline SDK hub-spoke daemon as a third integration path (embed harness vs raw-API vs CLI-wrapper) — cost/latency profile | read docs.cline.bot/sdk/architecture/hub-spoke; smoke test if a use case appears |
| A4 | Does single-file `.clinerules` still get read alongside directory format? | empirical: place both, observe Rules panel |
| A5 | House `.clinerules` v7.2.0 migration design to directory format (Sovereign Proxy Identity as always-on file) | grokster-led task after A4 |
| A6 | Off-peak window definition for DeepSeek cline-pass pricing (hours? timezone?) | docs say "DeepSeek API pricing" footnote — chase api-docs.deepseek.com |
| A7 | X-Request-ID presence/reliability for forensic correlation in house observability | inspect headers on any live probe above |

## Explicitly closed (do not reopen)

- Header-spoofing / client-identity forgery to reach free models — ToS §2.2(10)/(11), M23/M8. PERMANENT.
- Waiting for free-gate removal as strategy — documented policy, not an outage.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
