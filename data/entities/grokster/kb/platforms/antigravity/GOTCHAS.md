# Antigravity Gotchas — Trap → Evidence → Defense

**KB Entry**: grokster/platforms/antigravity/GOTCHAS
**last_verified**: 2026-08-26 · **rot_class**: slow (traps age well; re-check enforcement climate quarterly)
**Sources**: `R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` §G/§B.3/§H, antigravity.google/terms, CLIProxyAPI #1015/#1558/#1823, house findings #30631/#495
**Format**: each entry = trap → evidence → defense, with confidence tag.

---

## G1. Dead-upstream plugin trap — 🔴 VERIFIED
**Trap**: House runs NoeFabris/opencode-antigravity-auth @7db338b as file: dependency. Upstream repo is **ARCHIVED (read-only)** since ~2026-06-25 (GitHub API: `archived: true`, last release v1.6.5-beta.0 Feb 2026). Any drift — new model slugs, quota-API schema change, header requirement — will never get an upstream fix.
**Evidence**: GitHub API check 2026-08-26; 11k stars, 43 open issues frozen.
**Defense**: treat the local checkout as the de-facto fork; every plugin change is a house commit; watch live forks (shekohex lineage, 374★ active) for protocol fixes worth cherry-picking.

## G2. ToS/enforcement trap — 🔴 VERIFIED
**Trap**: Third-party-client access is a named ToS breach, not a gray area. Terms §6: "Using third party software, tools, or services to access the Service … is a breach of this Agreement … grounds for suspension or termination." Enforcement is automated and account-wide.
**Evidence**: Ban error `reason: TOS_VIOLATION`, `domain: cloudcode-pa.googleapis.com`, official appeal form (CLIProxyAPI #1823); Feb–Mar 2026 waves hit pooled AND paid accounts ("Paid Pro Subscriber Banned Instantly", 1.4k views); 7-day lockouts from automation/chaining cadence (Google forum).
**Defense**: burner accounts only; nothing irreplaceable on this backend; human-cadence request profiles; Antigravity stays priority-3 burst capacity per M7. There is NO compliant config — plan attrition, don't litigate it.

## G3. Hidden-throttle trap (quota lies) — 🟡 HIGH CONFIDENCE
**Trap**: `fetchAvailableModels` can report 100% remaining while EVERY generation call returns 429. Trusting the quota API for scheduling produces false "pool healthy" verdicts.
**Evidence**: CLIProxyAPI #1015 — 17 accounts, quota API all green, all generation 429 across models and both base URLs; VPN/IP change no effect → second limiting layer (short-window rate + abuse flags) invisible to quota API. Conflicting partial evidence of IP-based component (#54 simultaneous multi-account 429s).
**Defense**: health-check with a real minimal generation call, not the quota endpoint; exponential backoff; don't interpret green quota as "Google owes you capacity."

## G4. @latest stale-pin trap — 🟡 HOUSE-VERIFIED
**Trap**: `"plugin": ["opencode-antigravity-auth@latest"]` pins to a STALE npm snapshot, not float (#30631). Combined with G1, the npm artifact is doubly dead.
**Defense**: file: path to pinned checkout (house standard) or explicit version tag. Never @latest.

## G5. Nested-schema silent-drop trap — 🟡 HOUSE-VERIFIED
**Trap**: Variant config keys must be FLAT (`variantConfig?.thinkingBudget`, request.js :591/:669). Nested-schema variants drop their thinking values silently — model runs without requested thinking, no error anywhere.
**Defense**: flat keys only in variant definitions; verify thinking actually appears in responses (`thoughtSignature` parts present) after any variant edit. Cross-ref: opencode GOTCHAS G29 (same silent-drop class).

## G6. Ban-wave attrition trap (pool sizing) — 🟡 HIGH CONFIDENCE
**Trap**: Sizing the pool for current need instead of post-wave survivorship. Waves take most of a pool at once (#1558: 5 of 6 accounts gone simultaneously).
**Defense**: pool = steady-state need ÷ expected survival fraction; automate ban detection (403 TOS_VIOLATION / persistent 429 patterns) so dead accounts are pruned before they poison rotation; keep re-auth runbook ready (rm accounts.json → auth login).

## G7. Dual-pool fallback surprise — 🟢 DOCUMENTED
**Trap**: When all Antigravity pools exhaust, Gemini requests silently fall back to the Gemini-CLI pool with transformed model names (`gemini-3-flash` → `gemini-3-flash-preview`) and DIFFERENT requirements (needs real GCP projectId + cloudaicompanion API enabled). Fallback can fail confusingly if projectId missing — error surfaces as `rising-fact-p41fc` permission denied.
**Defense**: add `projectId` to each account if Gemini-CLI fallback is wanted; otherwise expect hard-stop after Antigravity pool exhaustion.

## G8. Credential-vault exposure — 🟡 STRUCTURAL
**Trap**: `antigravity-accounts.json` holds refresh tokens under master `cloud-platform` scope — far more powerful than Antigravity itself. Leak = full GCP exposure per account.
**Defense**: treat as password file (never commit, never log); it lives OUTSIDE the repo today — keep it that way; rotate by re-auth after any machine compromise.

## G9. Parallel-process account collision — 🟢 DOCUMENTED
**Trap**: Multiple OpenCode processes/subagents select the SAME account concurrently → self-inflicted 429s that look like Google throttling.
**Evidence**: NoeFabris MULTI-ACCOUNT.md (oh-my-opencode case).
**Defense**: `"pid_offset_enabled": true` in antigravity.json, or more accounts.

## G10. Thinking-budget overflow — 🟢 SPEC-VERIFIED
**Trap**: Gateway 400s when `maxOutputTokens ≤ thinkingBudget`. Easy to trigger with low max-tokens configs on thinking SKUs.
**Defense**: budget family floors are safe (8192+); enforce `maxOutputTokens > thinkingBudget` wherever house code builds generationConfig directly.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*

## G11. Sonnet-thinking backend-ID DEAD — 🔴 VERIFIED-BLOCKED (live probe 2026-08-26)
**Trap**: `claude-sonnet-4-6-thinking` wire ID returns **404 NOT_FOUND at the gateway** — confirmed live across multiple pool accounts (debug-log evidence, remediation run F7). Issue #1942 (Feb 2026) was never fixed server-side. Official antigravity.google/docs listing "Claude Sonnet 4.6 (thinking)" describes an IDE UI MODE — the backend serves only `claude-sonnet-4-6` (base verified working) and `claude-opus-4-6-thinking`. Custom SKU configs for sonnet-thinking are dead on arrival; plugin swallows the 404s during account rotation and returns an EMPTY response.
**Defense**: do NOT define antigravity-claude-sonnet-4-6-thinking SKUs. For Sonnet thinking needs: probe base-model + providerOptions thinkingConfig (untested path), use opus-thinking, or wait for backend fix. Related: some pool accounts return 403 "#3501 valid license" for Claude entirely — account provisioning varies.
**Trap**: `antigravity-claude-sonnet-4-6-thinking` may 404 at the gateway (backend ID mismatch reported Feb 2026, oh-my-openagent #1942). Official antigravity.google/docs lists "Claude Sonnet 4.6 (thinking)" ✅, but active fork (dragon-Elec) quota-row mapping has NO sonnet-thinking entry — conflicting signals on whether the backend exposes the thinking ID or folds thinking into the base Sonnet row.
**Defense**: live smoke before relying on the SKU; if 404 persists, fall back to base `antigravity-claude-sonnet-4-6` + agent-level thinking config, or keep Opus for thinking workloads.

## G12. Server-side thinking-budget cap (Claude) — 🟡 HIGH CONFIDENCE (community)
**Trap**: Requested `thinkingBudget` may be aspirational — community documentation (Mar 2026, agentpedia) reports Antigravity caps ACTUAL Claude thinking at ~1,024 tokens regardless of declared budget (cost control; Google unacknowledged). Verified for Opus in AG IDE v1.20.5; plugin/gateway path + Sonnet UNVERIFIED.
**Defense**: don't assume declared budget = delivered depth; compare output quality vs Gemini 3.x for deep-reasoning tasks; measure `usageMetadata` thinking tokens in responses when precision matters. Declared budgets still correct for config (they're what the API contract asks for).

## G13. Silent-empty total-failure mode — 🔴 VERIFIED (live probe 2026-08-26)
**Trap**: When ALL accounts fail for a family (404/403/429 rotation exhausted), the plugin returns an **EMPTY response with no error surfaced** to OpenCode — looks identical to a model that simply said nothing. Debug log showed full rotation then quiet surrender.
**Defense**: never diagnose empty responses from output alone — enable `"debug": true` in antigravity.json temporarily and read `~/.config/opencode/antigravity-logs/` (NOTE: debug logs contain FULL prompts incl. system souls — disable after use). Cross-check quota via check-quota.mjs but remember G3: quota API can lie while generation is throttled.

## G14. License-provisioning variance across pool accounts — 🟡 VERIFIED (2026-08-26)
**Trap**: Pool accounts are NOT uniformly provisioned. Some return 403 PERMISSION_DENIED "#3501 You do not have a valid license of this product" for Claude models regardless of quota. A healthy-looking pool may have only partial Claude capability.
**Defense**: per-account capability probe before relying on pool-wide Claude capacity; treat fetchAvailableModels as necessary-but-insufficient (see G3).
