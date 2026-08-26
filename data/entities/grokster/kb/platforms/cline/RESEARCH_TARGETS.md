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

| # | Probe | Resolves |
|---|---|---|
| P1 | Gate re-check on `deepseek/deepseek-v4-flash` (protocol above) | Whether Aug-22 gate still stands |
| P2 | Same call with `minimax/minimax-m2.5` | Docs contradiction: getting-started shows free-model curl vs free-models page prohibition |
| P3 | Authenticated `GET /api/v1/models` listing | Real catalog + capability flags (`supportsReasoning`/`supportsImages`) + enforced context/output caps; whether anthropic/* is actually served |
| P4 | Repeat P1 using WorkOS accessToken from providers.json | Whether gate keys on token type vs client identity |
| P5 | Header matrix on free model (± X-Task-ID / HTTP-Referer / User-Agent) | What the gate inspects — DIAGNOSTIC ONLY; any bypass found must NOT be used (ToS §2.2(11)) |
| P6 | `cline --thinking xhigh "ping"` with CLINE_DEBUG=1 → grep `~/.cline/data/logs/cline.log` request body | Wire param for reasoning effort at gateway |
| P7 | Grep P3 listing for `cline-pass/` vs `clinepass/` | Namespace truth before any config write |
| P8 | Large-context smoke on `cline-pass/deepseek-v4-flash` (or read caps from P3) | Whether D-557's 1M figure carries to paid variant |
| P9 | `cline version` | Exact CLI stamp (house refs stuck at 3.0.52/3.0.56 era) |
| P10 | Manual app.cline.bot dashboard subscription check | Concrete ClinePass allowance magnitudes |

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
