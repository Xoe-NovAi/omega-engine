# 🔱 FALLBACK SLUG RUNBOOK — Fleet Substrate Continuity (D1-b)
**AP Token**: `AP-RESEARCHER-FALLBACK-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_fallback_runbook ⬡ ARCHITECT-DECISION-READY

**Date**: 2026-08-24
**Purpose**: Make the Architect's fallback-slug decision a one-liner. Cliff context: `x-preview-f-free` (Ox Alpha/GLM) dies ~Aug 28 on weights drop; broader risk = free-slug deprecation without notice (proven pattern).
**Method**: Tier-A candidates live-probed RIGHT NOW with minimal inference calls; Tier-B verified by historical liveness from `messages.modelID` stamps (opencode.db, Tier-0 provenance).

---

## §1 SCOPE CLARIFICATION (read first)

The Aug-28 GLM weights drop kills **only the GLM-family slug** (`x-preview-f-free`). Other OC Zen free slugs (nemotron/hy3/big-pickle/mimo families) are different model families and survive *that* event — but remain exposed to the general free-slug-deprecation pattern. The fallback decision therefore covers both: immediate post-cliff default + general deprecation insurance.

## §2 CANDIDATE TABLE

### Tier A — LIVE-VERIFIED THIS HOUR (real inference calls, HTTP 200)
| Slug | Provider | Response | Notes |
|---|---|---|---|
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | openrouter | "STATUS: CONFIRMED 🟢" | **Frontier-class (550B), $0, key already in auth store** |
| `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | openrouter | "fully operational" | Mid-tier, $0, fast |
| `deepseek/deepseek-v4-flash-0731` | openrouter | "ALIVE" | ⚠️ PAID (non-`:free`) — needs billing authorization |

### Tier B — HISTORICALLY ALIVE ≤31h (Tier-0 stamp evidence, not re-probed: no standalone key path)
| Slug | Provider | Last alive | Notes |
|---|---|---|---|
| `google/gemini-3.1-pro-preview-customtools` | google | 15.8h | The Architect's own Gemini pass ran on this |
| `google/antigravity-claude-opus-4-6-thinking` | google | 27.3h | Frontier reasoning; used via manual switch |
| `google/antigravity-claude-sonnet-4-6` | google | 27.3h | Same |
| `google/gemini-3.7-flash` | google | 29.6h | Fast tier |
| `opencode/big-pickle` | opencode | 30.5h | Frontier per jem-2.0 docs; free slug (deprecation-exposed) |
| `opencode/hy3-free` | opencode | 30.3h | Free slug |

### Tier C — CURRENT SUBSTRATE (cliff-exposed)
| Slug | Status |
|---|---|
| `opencode/x-preview-f-free` | Dies ~Aug 28 (GLM weights drop) |
| `opencode/nemotron-3-ultra-free` | **Current configured default** (opencode.json:321-322); last alive 2.2h ago; different family → survives GLM cliff; free-slug risk remains |

## §3 THE SWITCH PROCEDURE (exact edit)

**Primary config**: `opencode.json` lines 321–322:
```json
"model": "opencode/nemotron-3-ultra-free",
"small_model": "opencode/nemotron-3-ultra-free",
```
**To switch, replace BOTH values** with the chosen slug verbatim (e.g. `"google/gemini-3.7-flash"`). Then restart OpenCode sessions (config read at session start). Per-session alternative without editing config: `/models` command inside a session.

**Provider prerequisites**: google/openrouter credentials already present in `~/.local/share/opencode/auth.json` — no new auth needed for any candidate above.

## §4 RECOMMENDATION (for Architect one-liner)

**Option 1 (zero-action default)**: Do nothing pre-cliff. `nemotron-3-ultra-free` is already the configured default and survives the GLM cliff specifically. Fleet continuity is automatic unless OC Zen deprecates it independently.
**Option 2 (capability fallback)**: Switch to `google/gemini-3.7-flash` (fast) or `gemini-3.1-pro-preview-customtools` (deep) — strongest models with proven recent function via your own hot-swap usage; Google quota economics apply.
**Option 3 (frontier free)**: Switch to `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` — live-verified frontier-class at $0 today; OpenRouter free-tier rate limits apply (20 RPM class).
**Suggested posture**: Option 1 through Aug 28; if x-preview dies and nemotron-default holds, stay; if quality regresses, escalate to Option 2/3 via the same two-line edit.

## §5 VERIFICATION CAVEATS
- Tier-B entries NOT live-probed (no standalone key path for google/opencode providers from script); evidence = successful assistant stamps within 31h. Re-verify by running any session on the chosen slug before fleet-wide reliance.
- All probes used the OpenRouter key from the auth store; that key was rotated-clean as of tonight (env var copy remains revoked — separate cosmetic item).

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ FALLBACK-SLUG-RUNBOOK v1.0 ⬡ DECISION-READY ⬡ 2026-08-24*
<!-- PROVENANCE-CORRECTED 2026-08-25T03:09:58Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

