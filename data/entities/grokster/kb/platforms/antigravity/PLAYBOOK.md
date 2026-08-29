# Antigravity — House Operating Playbook

**KB Entry**: grokster/platforms/antigravity/PLAYBOOK
**last_verified**: 2026-08-26 · **rot_class**: slow (posture ages well; re-verify after any ban wave or fabric reorder)
**Sources**: `docs/research/R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` (web-primary deep mine), Ark §7 provider fabric, SOVEREIGN_MANDATES M7

---

## §1 Fabric Position — Burst Capacity, NEVER the Spine

Antigravity sits at **priority 3** in the provider fabric (native-gguf(0) → lmster(1) → Ollama(2) → **antigravity(3)** → google(4) → …) per Ark §7. That ordering IS the ToS defense:

- M7 local-first means Antigravity only sees traffic when local backends are saturated or the task needs a frontier model burst.
- **Never let Antigravity carry anything irreplaceable.** Google's Feb–Mar 2026 enforcement waves disabled accounts overnight (TOS_VIOLATION on `cloudcode-pa.googleapis.com`, simultaneous across Antigravity + Gemini CLI + Code Assist). Any workflow that cannot survive total pool loss by morning must not route through this backend.
- Corollary: no long-running unattended jobs pinned to Antigravity; no sole-source research pipelines; checkpoint work so a mid-task ban costs a retry, not a session.

## §2 Pool Posture Under Ban-Wave Reality

The terms (antigravity.google/terms §6) name third-party-client access as breach **per se** — there is no compliant configuration. Posture is containment, not compliance:

| Rule | Rationale |
|---|---|
| Burner accounts only | Enforcement hits the whole account (paid plans not spared — "Paid Pro Subscriber Banned Instantly" thread, 1.4k views). Never attach accounts holding paid plans or irreplaceable data. |
| Budget pool attrition | Assume periodic loss of most accounts per wave (CLIProxyAPI #1558: 5 of 6 gone). Pool size = headroom above steady-state need, not capacity plan. |
| Human-cadence request profiles | Automation/chaining cadence triggers abuse filters → 7-day lockouts even before TOS_VIOLATION disables. |
| Sticky-per-account selection (plugin default) | Preserves Anthropic prompt cache AND avoids round-robin volume spikes that look like automation. |
| No IP-evasion theater | VPN/IP rotation demonstrably does NOT clear account-level flags (#1015). Don't burn effort there. |

## §3 Plugin Wiring (Current House Setup)

- 📜 *(HISTORICAL — superseded by next bullet)* Mid-day 2026-08-26 disk audit found configs on `@latest` → npm install, byte-identical to checkout @7db338b; earlier KB `file:` claim was wrong at that time.
- **RESOLVED 2026-08-26 (Architect order)**: both configs switched from `@latest` to `file:///…/omega-engine/opencode-antigravity-auth` — the house-patched checkout @7db338b is now the SINGLE canonical load path (smoke-verified: opus-thinking routes through it). Stale copies removed (project + global node_modules); remaining cache copies under `~/.cache/opencode/packages/` are opencode-managed and inert under file: spec. The multi-copy drift problem is closed; any plugin change = a git commit in the checkout.

**Executing-copy verification (grokster M3, 2026-08-26)**: no direct runtime stack-trace names the checkout, so verification is by **elimination + smoke**: (a) project `.opencode/node_modules/opencode-antigravity-auth` and global `~/.config/opencode/node_modules/opencode-antigravity-auth` were `rm -rf`'d at 09:36:56Z BEFORE the post-switch smokes; (b) both `~/.cache/opencode/packages/opencode-antigravity-auth*` dirs have mtimes of Jul 06/Jul 21 — zero files written during smoke window (verified via `find -newermt`); (c) smokes at 09:36–09:37Z (`FILESPEC-OK`, `OPUS-MEDIUM-OK`, `OPUS-HIGH-OK`) streamed successfully through `modelID=antigravity-claude-opus-4-6-thinking`. With every alternative copy gone/inert, the checkout @7db338b is the only possible executing source. Re-verify after any OpenCode upgrade that changes plugin resolution.

- Accounts file: `~/.config/opencode/antigravity-accounts.json` (v3 schema, 7 accounts). Treat as credential vault — scopes include master `cloud-platform`. Plugin settings live in `~/.config/opencode/antigravity.json` (incl. `keep_thinking`, default false).

## §4 Model Selection & Thinking SKUs

Working set (verified through plugin + provenance audits):

| Model slug | Notes |
|---|---|
| `antigravity-gemini-3-pro` / `-3.1-pro` / `-3-flash` | Antigravity quota pool |
| `antigravity-claude-opus-4-6-thinking` | **FULL LADDER** (2026-08-26): minimal=4096 · low=8192 · medium=16384 · high=24576 · max=32768 — all tiers smoke-verified live; Sonnet 4.6 base + Opus confirmed working through OpenCode (Architect, 2026-08-26) |
| `antigravity-claude-sonnet-4-6` | Base preset |
| ~~`antigravity-claude-sonnet-4-6-thinking`~~ | ❌ **DEAD wire ID** — 404s at gateway across accounts (verified 2026-08-26, GOTCHAS G11); removed from configs in F6 revert |

Selection discipline:
- Thinking SKUs use **flat `thinkingBudget` keys** in variant config (plugin request.js reads them flat — nested schemas silently drop, see GOTCHAS G5).
- Opus ladder (2026-08-26, all tiers smoke-verified live): minimal=4096 · low=8192 · medium=16384 · high=24576 · max=32768. Pick the tier, don't hand-tune values. Legacy 3-tier family {low:8192, medium:16384, high:32768} remains the resolver's built-in default for SKUs without explicit variants.
- Upstream catalog also serves `gpt-oss-120b-medium` and gemini-3.5/3.6/3.7-flash effort slugs that house presets don't expose — candidates for future custom SKUs if a probe confirms availability on house accounts (RESEARCH_TARGETS #6).

## §5 Escalation & Review Triggers

Re-verify this playbook when ANY of: new ban wave reported (watch CLIProxyAPI issues/discussions), plugin runtime error after OpenCode upgrade, quota-API schema change observed in probe logs, **backend model-ID volatility** (any observed Google-side catalog change → re-smoke every house SKU; wire IDs rot independently of plugin pinning — sonnet-thinking worked Feb 2026, 404 by Aug 2026), or Architect orders pool restructuring.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
