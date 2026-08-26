# Antigravity — Config Reference (OpenCode via Plugin)

**KB Entry**: grokster/platforms/antigravity/CONFIG_REFERENCE
**last_verified**: 2026-08-26 · **rot_class**: medium (config keys stable while plugin is pinned; dead upstream means keys only change when WE change them)
**Sources**: house source verification of plugin @7db338b (request.js :591/:669, model-resolver.js, config/models.js), NoeFabris docs/MULTI-ACCOUNT.md + CONFIGURATION.md refs, `R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` §B

---

## §1 Wiring in opencode.json

```jsonc
{
  "plugin": ["/abs/path/to/opencode-antigravity-auth"]   // house: file: checkout @7db338b
}
```

- Key is **`plugin` SINGULAR** — `"plugins"` → "Unrecognized key" error.
- TUI-side commands (`/ag`, `/ag-accounts`) need a second entry: `"opencode-antigravity-auth/tui"` spec. House runs the server plugin via file: path; TUI entry optional.
- Hash-pin or absolute path only. `@latest` resolves to a STALE npm snapshot (#30631) — and upstream is archived anyway.
- Auth-store quirk: OpenCode only invokes the plugin loader if a google credential stub exists in `~/.local/share/opencode/auth.json`. Bootstrap pattern exists (lobehub skill doc) for cases where refresh tokens already sit in antigravity-accounts.json.

## §2 Model Variant Schema — FLAT Keys Only

The plugin reads variant config at **flat keys** (`variantConfig?.thinkingBudget`, request.js :591/:669). Nested-schema variants silently drop their values (cross-ref: opencode GOTCHAS G29 nested-schema silent-drop).

| Key | Applies to | Values |
|---|---|---|
| `thinkingBudget` | Claude thinking SKUs | resolved through budget family — set tier, not raw number |
| `thinkingLevel` | Gemini 3 models | low / medium / high |
| reasoningEffort (Zen-style) | ❌ n/a here | Antigravity path does not consume Zen-style effort keys |

Budget family (model-resolver.js): `{low: 8192, medium: 16384, high: 32768}`. Constraint from gateway: `maxOutputTokens > thinkingBudget` always.

## §3 Custom SKU Pattern

Presets live in plugin `config/models.js`. When a model+thinking combo is missing from presets (e.g. `claude-sonnet-4-6-thinking`, omitted per upstream issue #495):

1. Define model entry with slug `antigravity-claude-sonnet-4-6-thinking` (resolver strips the `antigravity-` prefix before the wire name).
2. Resolver's `supportsThinkingTiers()` matches on `claude` + `thinking` substring → budget family applies automatically.
3. Write model definitions into `opencode.json` via `/ag-accounts` manager, or by hand.

Verified working custom SKU: `antigravity-claude-sonnet-4-6-thinking` ✅.

## §4 Model Slugs (house working set + upstream extras)

House-verified: `antigravity-gemini-3-pro` · `antigravity-gemini-3.1-pro` · `antigravity-gemini-3-flash` · `antigravity-claude-opus-4-6-thinking` · `antigravity-claude-sonnet-4-6` (+custom `-thinking`).

Upstream catalog extras NOT in house presets ⚠️(availability on house accounts unprobed): `gpt-oss-120b-medium`; gemini-3.5/3.6/3.7-flash with `-high/-medium` effort suffixes; `gemini-3-pro-high/-low`.

## §5 Account & Plugin State Files

| File | Role |
|---|---|
| `~/.config/opencode/antigravity-accounts.json` | Pool: v3 schema — accounts[] (`email`, `refreshToken`, `projectId?`, `enabled?`), `activeIndex`, `activeIndexByFamily{claude,gemini}`. CREDENTIAL VAULT (master cloud-platform scope). |
| `~/.config/opencode/antigravity.json` | Plugin settings: `account_selection_strategy` (sticky/round-robin/hybrid), `pid_offset_enabled` |
| `~/.local/share/opencode/auth.json` | OpenCode auth store — needs google stub for plugin loader to fire |
| `zen_accounts_state.json` | Separate account-state file (house-known; role vs accounts.json not fully mapped ❓) |

## §6 Operational Commands

- Add/manage accounts: `opencode auth login` → Google → "OAuth with Google (Antigravity)" (callback port 51121).
- Quota check outside harness: NoeFabris standalone `node scripts/check-quota.mjs [--account N]` (hits `fetchAvailableModels`; works without OpenCode running).
- Token revocation symptoms: `invalid_grant` errors → plugin auto-prunes account → re-auth required.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*

## §7 Format Note — Flat vs Nested (upstream docs divergence)
Upstream MODEL-VARIANTS.md documents Claude variants as NESTED `{"thinkingConfig": {"thinkingBudget": N}}`; installed source (`extractVariantThinkingConfig`, request.js) normalizes BOTH nested and FLAT `{"thinkingBudget": N}` forms. House standard = **FLAT** (production-verified via opus-thinking block). Custom budgets officially sanctioned — docs example ships a 5-tier spread (4096/8192/16384/24576/32768); variant names are free-form labels. A no-variant call = dynamic budget (model decides).
