<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Cline — Gotchas (trap → evidence → defense)

**KB Entry**: grokster/platforms/cline/GOTCHAS
**last_verified**: 2026-08-26 · **rot_class**: fast
**Confidence tags**: VERIFIED = house first-hand evidence · REPORTED = single credible source · UNVERIFIED = flagged per M23
**Sources**: `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md`, `docs/research/R_CLINE_DIRECT_API_DEEP_MINE_20260826.md`, docs.cline.bot, cline.bot/tos

---

## G1. Free-model gate trap — "it'll work from raw API eventually"

- **Trap**: treating the HTTP 403 on free models as a transient bug to wait out.
- **Evidence**: VERIFIED ×2. House live probes 2026-08-22 AND 2026-08-26 (`403 …only available via Cline product surfaces`) + official docs: *"Free model usage is not supported through the Cline API"* + ToS §2.2(10)/(11). The Aug-26 response adds a version-hint suffix ("update to the latest version") — gate may inspect client-version signals, but bypass remains forbidden.
- **Defense**: gate is policy. Route around it: ClinePass for paid direct-API (entitlement unlocks the SAME key server-side), CLI wrapper for $0. Never spoof.

## G2. Header-spoofing ToS hazard

- **Trap**: faking client identity (User-Agent/X-Task-ID) to pass the gate.
- **Evidence**: ToS §2.2(10) "no access through means other than provided or authorized" + §2.2(11) "no bypassing measures used to prevent or restrict access". VERIFIED text.
- **Defense**: PERMANENTLY REJECTED (audit Path B2). Diagnostic header probes are fine; using any success is not.

## G3. Namespace hyphen trap — `clinepass/` vs `cline-pass/`

- **Trap**: wiring paid model ids with the wrong namespace → silent 404/400.
- **Evidence**: old KB said `clinepass/claude-sonnet-4-6`; official ClinePass docs say `cline-pass/glm-5.3` etc. CORRECTED 2026-08-26.
- **Defense**: use `cline-pass/*`; confirm against live `/api/v1/models` before any config write (probe P7).

## G4. anthropic/claude-* listed but not served

- **Trap**: shipping `anthropic/claude-sonnet-4-6` in a config block because docs use it as the canonical example.
- **Evidence**: REPORTED — third-party marketplace author validated every model ID directly against the gateway; anthropic/* absent. Consistent with observed docs-lag.
- **Defense**: never ship an unverified id; validate via `/api/v1/models` (probe P3) first.

## G5. reasoning_effort wire-param unknown

- **Trap**: assuming OpenCode `reasoningEffort` variants reach DeepSeek through this gateway.
- **Evidence**: gateway docs document only model/messages/stream/tools/temperature — no reasoning_effort. CLI has `--thinking none|low|medium|high|xhigh` so effort control exists in sanctioned clients, but the wire param for non-OpenAI models is UNVERIFIED.
- **Defense**: capture what the CLI sends (probe P6, CLINE_DEBUG=1 + cline.log); drop dead variants rather than ship them.

## G6. Quota windows undisclosed

- **Trap**: planning agentic loops against imagined ClinePass allowances.
- **Evidence**: VERIFIED that limits are NOT published — only structure: 5-hour rolling + weekly + monthly windows; "2-5x usage vs standard API rate" multiplier semantics.
- **Defense**: check dashboard before heavy runs; instrument one session empirically (probe P10).

## G7. Mid-stream errors inside HTTP 200

- **Trap**: streaming handlers that only check HTTP status will swallow failures.
- **Evidence**: api/errors doc — errors arrive as chunks with `finish_reason:"error"` after 200 OK. REPORTED (official doc, not house-reproduced).
- **Defense**: always inspect finish_reason; engine's M25 streaming block already reads chunk timeouts — extend with finish_reason checks if wiring cline into fabric.

## G8. Legacy credential paths (HG-003 stale)

- **Trap**: vault adapters targeting `libsecret` / `~/.local/share/cline/credentials.json`.
- **Evidence**: VERIFIED Aug-22 — actual stores are `~/.cline/data/secrets.json` (static key) and `~/.cline/data/settings/providers.json` (WorkOS OAuth pair).
- **Defense**: use current paths; extract static key to `.env`; vault-mediate OAuth (V-1).

## G9. Headless auto-approve default

- **Trap**: `cline "prompt"` runs act mode with auto-approve TRUE by default — tools execute without prompts.
- **Evidence**: cli-reference (`--auto-approve <boolean>` default true; FALSE only in ACP mode). REPORTED (official doc).
- **Defense**: pass `--auto-approve false` on untrusted trees or audits; or scope `CLINE_COMMAND_PERMISSIONS`.

## G10. `.clinerules` format drift

- **Trap**: editing house's single-file v7.2.0 as if it were current spec.
- **Evidence**: current spec is directory-of-files with optional YAML `paths:` frontmatter; MCP moved to `.cline/mcp.json`. VERIFIED vs docs.
- **Defense**: see CONFIG_REFERENCE §1–§2; migrate on next touch, don't re-litigate.

## G11. Free-tier training exposure

- **Trap**: sending sensitive code through free models assuming privacy.
- **Evidence**: free-models page ("may be used to help improve model performance") + ToS §3.2(2)/§3.5. VERIFIED text.
- **Defense**: sensitive work → BYOK/local models, or paid Subscription (contractual carve-out), and telemetry off regardless.

## G12. MiMo V2.5 512K cap claim

- **Trap**: citing "MiMo V2.5 = 512K context" as validated.
- **Evidence**: UNVERIFIED — no primary source captured in deep-mine.
- **Defense**: do not cite until probed; treat as folklore.

## G13. No public /models endpoint exists

- **Trap**: assuming `GET /api/v1/models` works because docs reference a "model catalog" with capability flags.
- **Evidence**: VERIFIED 2026-08-26 — `/api/v1/models`, `/v1/models`, `/api/models`, `/api/v1/model` all return 404 `{"error":"Not Found","success":false}` with a valid Bearer key. Catalog is served privately to product clients.
- **Defense**: discover models/caps via error-differentiation POSTs (see RESEARCH_TARGETS P-probes) or the app.cline.bot dashboard; never promise a live listing in tooling.

## G14. Invalid namespace doesn't fail cleanly

- **Trap**: expecting a typo'd model id (`clinepass/…` without hyphen) to return 404 model-not-found.
- **Evidence**: VERIFIED 2026-08-26 — non-hyphenated id returned anomalous `"empty response content"` / `success:false` instead of a diagnostic error. Silent-failure shape.
- **Defense**: treat `"empty response content"` as "check your model id first"; always copy ids verbatim from official ClinePass table (CONFIG_REFERENCE/ARCHITECTURE).

## G15. Free-models page overgeneralizes — per-id behavior varies

- **Trap**: applying the blanket rule "free models are blocked via API" to ALL free-tagged ids.
- **Evidence**: VERIFIED 2026-08-26 — same key, same minute: `deepseek/deepseek-v4-flash` → 403 product-surface gate, but `minimax/minimax-m2.5` → `insufficient_credits` (balance $0.01) i.e. **credit-metered and API-reachable**. Gate taxonomy is per-id: client-gated vs credit-metered vs plan-entitled (`cline-pass/*`). Promotions rotate, so an id's class can change over time.
- **Defense**: probe each id before relying on it; read the error class (`ENTITLEMENT_ERROR` vs `insufficient_credits` vs 403 product-surface) as the authoritative tier signal.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
