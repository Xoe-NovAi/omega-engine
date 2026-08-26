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

- ⚠️ **CORRECTED 2026-08-26 (remediation-run disk audit)**: house configs reference the plugin as **`opencode-antigravity-auth@latest`** (project + subdir arrays), which resolves to the npm install at `~/.config/opencode/node_modules/` — v1.6.0, verified **byte-identical** to the local git checkout @7db338b (`diff -rq dist` = 0 differences). Earlier KB text claimed direct `file:` wiring — that was wrong; the checkout functions as a pinned source-of-truth mirror, not the load path.
- Per #30631, `@latest` pins to whatever npm snapshot was current at install time (Jul-21) and does NOT float — combined with upstream archive (G1), the effective plugin is frozen at 1.6.0 == 7db338b. Any future change requires explicit reinstall.
- Hash-pin or absolute path remains the recommended hardening (P2 follow-up): swap `@latest` → `file:` path to make the load path literally the checkout.
- Accounts file: `~/.config/opencode/antigravity-accounts.json` (v3 schema, 7 accounts). Treat as credential vault — scopes include master `cloud-platform`. Plugin settings live in `~/.config/opencode/antigravity.json` (incl. `keep_thinking`, default false).

## §4 Model Selection & Thinking SKUs

Working set (verified through plugin + provenance audits):

| Model slug | Notes |
|---|---|
| `antigravity-gemini-3-pro` / `-3.1-pro` / `-3-flash` | Antigravity quota pool |
| `antigravity-claude-opus-4-6-thinking` | Preset; thinking via budget family |
| `antigravity-claude-sonnet-4-6` | Base preset |
| `antigravity-claude-sonnet-4-6-thinking` | **Custom SKU** — omitted from presets (upstream issue #495) but works; resolver matches `claude`+`thinking` |

Selection discipline:
- Thinking SKUs use **flat `thinkingBudget` keys** in variant config (plugin request.js reads them flat — nested schemas silently drop, see GOTCHAS G5).
- Budget family is fixed: low=8192 / medium=16384 / high=32768. Pick the tier, don't hand-tune values.
- Upstream catalog also serves `gpt-oss-120b-medium` and gemini-3.5/3.6/3.7-flash effort slugs that house presets don't expose — candidates for future custom SKUs if a probe confirms availability on house accounts (RESEARCH_TARGETS #6).

## §5 Escalation & Review Triggers

Re-verify this playbook when ANY of: new ban wave reported (watch CLIProxyAPI issues/discussions), plugin runtime error after OpenCode upgrade, quota-API schema change observed in probe logs, or Architect orders pool restructuring.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
