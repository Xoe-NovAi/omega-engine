# Session Gnosis — roc_racoon — Cline Provider Activation Audit
**Date**: 2026-08-22 · **Session**: ses_5b058490c0d0 · **Trigger**: @kali Grand Oversight audit request

## What happened (L1)
Read-only audit of whether the `cline` fabric entry (priority 7) can be activated.
Determined transport (openai_compat reuse), located real credentials (NOT where HG-003 says),
ran 2 live probes (400 → corrected → 403 client-gate), wrote deliverable report.

## Key facts for hydration
- `model_gateway.py:534` maps cline → `_create_openrouter`; line 364 silently defaults base_url to openrouter.ai when absent → latent M22 provenance bug (opencode-zen at :533 shares it).
- Real Cline endpoint: `https://api.cline.bot/api/v1/chat/completions` (from `~/.cline/data/logs/cline.log`). With openai_compat.py:94 URL math, `base_url: https://api.cline.bot/api` works code-free.
- Credentials: `~/.cline/data/secrets.json` (`clineApiKey`, static) + `~/.cline/data/settings/providers.json` (WorkOS OAuth, refresh token present). HG-003's path (~/.local/share/cline/credentials.json) DOES NOT EXIST — stale.
- Probe: bare model ID → 400 (needs `modelType/model`); namespaced → **403 "only available via Cline product surfaces"** = free models are client-gated. Direct HTTP activation of deepseek-v4-flash/mimo-v2.5 impossible without impersonating official client (rejected).
- VERDICT: BLOCKED as-configured. Path A (config-only, permitted model, ~30 min) vs Path B1 (CLI-wrapper RemoteProvider subclass, ~4-6h).

## Continuation notes
- Deliverable: `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md`
- If Architect approves Path B1: create `src/omega/oracle/backends/cline_cli.py` following orchestrator.py:527-529 subprocess pattern; add contract tests per M21.
- Fix candidate filed implicitly: raise ConfigError on missing base_url in `_create_openrouter`.
- Stall-echo observed mid-session (truncated own-draft message); handled per ORACLE_STACK.md advisory — treated as continuation, verified nothing against it.
