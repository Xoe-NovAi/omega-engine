# 🔱 R_CONFIG_REMEDIATION_PREEXEC_REVIEW_20260826
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_preexec_review ⬡ ADVERSARIAL PRE-FLIGHT

**Mission**: Adversarial "what did we miss" pass on the ratified-pending OpenCode config
remediation plan (`R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826.md`). Zero config changes made.
**Method**: Local repo/config forensics + installed-plugin source inspection + web research
(GitHub issues, official docs) + reasoning from verified facts. Every claim confidence-tagged.
**Confidence tags**: 🟢 HIGH (primary source / directly verified) · 🟡 MEDIUM (corroborated) · 🔴 LOW / UNVERIFIED (M23-flagged)

---

## §0 EXECUTIVE VERDICT

> ## ⚠️ CONDITIONAL GO — **DO NOT EXECUTE AS WRITTEN**
>
> The plan's *direction* is sound (de-pollution + catalog reversion are correct), but
> pre-flight found **2 plan-invalidating defects and 3 execution hazards** that must be
> fixed before Phase 1 runs. One defect changes a Phase-3 deliverable; one invalidates a
> stated "verified fact."

### Blocking conditions (must fix before GO)

| # | Condition | Severity |
|---|-----------|----------|
| C1 | **Phase 3b schema defect**: plan specifies `thinkingConfig.thinkingBudget` variants for `antigravity-claude-sonnet-4-6-thinking`. Installed plugin 1.6.0 source reads **flat** `variantConfig.thinkingBudget` (`dist/src/plugin/request.js:663`, `model-resolver.js:311`). Nested form will be **silently dropped** (the exact failure mode this remediation exists to fix). Use flat `"thinkingBudget": 8192/32768` — matching the working sibling Opus entry. | 🔴 BLOCKER |
| C2 | **Version-drift premise stale**: plan assumes running binary = 1.18.18. Actual: `~/.opencode/bin/opencode` = **1.18.23**, mtime 2026-08-25 03:11 — it updated **yesterday**, unattended. Auto-update is demonstrably active. A freeze strategy (§4) is mandatory BEFORE phase work starts, or verification results are non-reproducible. | 🔴 BLOCKER |
| C3 | **Runtime dependents not inventoried in plan**: `.opencode/plugins/error-capture.ts:109` hardcodes `opencode/nemotron-3-ultra-free`; `config/providers.yaml`, `config/entity_model_affinity.yaml`, `configs/token_budgets.yaml`, subagent_pool code, and tests reference the Zen ids. Full checklist in §2. None break if ids are KEPT (plan keeps nemotron/deepseek ids) — but any future id change without this list breaks engine code silently. | 🟡 MUST-PATCH PLAN DOC |
| C4 | **Rollback bundle incomplete**: global config not in git AND plugin is a **local `file:` git checkout inside the repo** (`~/.config/opencode/package.json` → `omega-engine/opencode-antigravity-auth`, currently at commit `7db338b`, version field still 1.6.0). Plugin drift via `git pull`/rebuild is invisible to config backups. Bundle spec in §5. | 🟡 MUST-DO PRE-PHASE-0 |

### Non-blocking recommendations
- R1: Reorder phases (§3) — variants re-schema BEFORE override deletions; MiMo re-key LAST within its phase.
- R2: Add post-phase `opencode --version` + plugin-commit-hash pin check to every verification step (plan only pins binary).
- R3: Do NOT flip `keep_thinking:true` in the same window as model changes (changes two variables at once; violates single-variable verification).

---

## §1 VERIFIED LOCAL GROUND TRUTH (inspected 2026-08-26)

All items below verified by direct inspection on this machine. 🟢 HIGH each.

| Item | Value | Evidence |
|---|---|---|
| Binary | `~/.opencode/bin/opencode` **v1.18.23**, mtime 2026-08-25 03:11 | `opencode --version` |
| Plan's stated binary | 1.18.18 — **STALE**; auto-update fired between plan writing and now | mtime vs mission brief |
| Global config | `~/.config/opencode/opencode.json` (15.7 KB, mtime Aug 22); 9 polluted provider blocks confirmed; `"plugin": []` (empty); `model`/`small_model` = `opencode/nemotron-3-ultra-free` | read |
| Project config | `opencode.json`: plugin array uses `@latest`; Zen variants use INVALID nested `reasoning.effort`; custom openrouter id `llama-3.3-70b-free` → `meta-llama/llama-3.3-70b-instruct:free` | read |
| Subdir config | `.opencode/opencode.json`: antigravity models; Opus-thinking uses **FLAT** `"thinkingBudget": 8192/32768` (working) | read |
| Plugin install mode | `~/.config/opencode/package.json` → `"opencode-antigravity-auth": "file:../../…/omega-engine/opencode-antigravity-auth"` — LOCAL checkout, NOT npm | read |
| Plugin version | package.json says 1.6.0; git HEAD = `7db338b` "fix(token): persist refreshed OAuth tokens to disk" (recent fix commits present) | inspected |
| Plugin variant-key reading | `request.js:663` reads `variantConfig?.thinkingLevel` and `?.thinkingBudget` — FLAT; `model-resolver.js:311` `if (!variantConfig.thinkingBudget)` — FLAT | source inspection |
| Auth state | `~/.local/share/opencode/auth.json` exists (1285 B, touched 2026-08-25 22:08) | stat |
| Zen account state | `zen_accounts_state.json`: accounts EMPTY, rotation policy all zeros | read |
| Antigravity state | `antigravity-accounts.json` (8.3 KB, active); `antigravity.json`: `keep_thinking:false`, `account_selection_strategy:"sticky"`, `switch_on_first_rate_limit:true` | read |
| tui.json | Does NOT exist on this machine (neither location) | ls |

---

## §2 Q2 — REFERENCE INTEGRITY: COMPLETE DEPENDENT INVENTORY

Repo-wide grep for the five at-risk ids (`nemotron-3-ultra-free`, `mimo-v2.5`,
`deepseek-v4-flash-free`, `llama-3.3-70b-free`, `x-preview-f-free`) across src/, config/,
configs/, scripts/, tests/, .opencode/, .github/. ~250 hits total; **runtime dependents**
isolated below (docs/gnosis/session files excluded — historical record, not breakage).

### 2.1 Config-level dependents

| File | Reference | Breaks if id changes? |
|---|---|---|
| `opencode.json` project+global | `model` + `small_model` = `opencode/nemotron-3-ultra-free` | 🔴 YES — orphaned default at startup. Plan KEEPS this id → safe today; but a future catalog-side rename orphans BOTH configs simultaneously (single point of failure ×2). |
| `config/providers.yaml:308,332` | opencode-zen `supported_models`: `deepseek-v4-flash-free`; cline: `mimo-v2.5` | 🟡 Engine provider fabric routing mismatch = model unroutable via engine (not TUI). Ids kept → safe. |
| `config/entity_model_affinity.yaml:443` | roc_racoon cloud tier = `nemotron-3-ultra-free` @ opencode-zen | 🟡 Affinity routing only. |
| `configs/token_budgets.yaml:71,82` | `nemotron-3-ultra-free: 128000` output budget | 🟡 Budget math; value already stale vs live catalog. |
| `config/model_registry/providers/opencode-zen.yaml:19`, `cline.yaml:13` | model lists incl. both Zen ids | 🟡 Registry metadata. |

### 2.2 Code-level dependents

| File | Reference | Note |
|---|---|---|
| `.opencode/plugins/error-capture.ts:109` | hardcodes `model: "opencode/nemotron-3-ultra-free"` in hivemind notify payload | 🟡 Metadata field only; cosmetic if id changes. |
| `src/omega/infra/subagent_pool/models.py:373` | slot assignment `"deepseek-v4-flash"` / `"mimo-v2.5"` | 🟡 CLINE-family ids — unaffected by OpenCode config edits. |
| `src/omega/infra/subagent_pool/profile_manager.py:143` | `"mimo-v2.5": 512_000` context map | 🟡 Stale limit (pre-existing debt, not remediation-caused). |
| `scripts/bulk_update_model_cards.py:41,44` | maps `deepseek-v4-flash-free`, `llama-3.3-70b-free` → categories | 🟡 ONLY repo reference to the project-config custom openrouter id. Deleting that override orphans this mapping silently. |
| `scripts/correct_ics_provenance.py:204`, `tests/test_provenance_worker_w14.py`, `tests/test_ics.py`, `scripts/extract_dpo_pairs.py:75` | `x-preview-f-free` / `nemotron-3-ultra-free` fixtures & defaults | 🟢 Safe under plan (ids kept); would break provenance tests if ids ever change. |

### 2.3 Non-file dependents (the ones plans usually miss)

1. **Session history resumption** 🟡: OpenCode stores per-message model refs in
   `~/.local/share/opencode/opencode.db`. Resuming an old session pinned to a deleted id
   (`openrouter/llama-3.3-70b-free`, custom `mimo-v2.5`) will fail model resolution.
   Mitigation: expect "model not found" on old sessions; re-select model manually. Do NOT
   treat as regression. 🟢 HIGH (mechanism), 🔴 LOW (exact error string unverified).
2. **CI spec pins** 🟡: `docs/specs/context_injection/*` references 1.18.x versions and
   planned model pins — any CI harness written against `opencode/nemotron-3-ultra-free`
   stays valid only while that catalog id survives upstream. Add a catalog-watch note.
3. **`default_agent: kali`** — unaffected by provider changes. 🟢

### 2.4 Verdict for Q2

Under the plan AS WRITTEN (ids kept, only display names changed): **no runtime dependent
breaks**. The inventory above becomes mandatory the moment anyone re-keys an id — which
Phase 3a does for MiMo. `mimo-v2.5` repo references (providers.yaml cline block,
subagent_pool, model_registry) are all CLINE-provider scoped, so the OpenCode-side re-key
does not touch them. 🟢 HIGH.

---

## §3 Q1 — DELETION REGRESSIONS (override removal → builtin catalog)

### 3.1 Credential continuity: SAFE by architecture 🟢 HIGH
Provider resolution order (documented in a third-party auth-plugin README citing
`provider/provider.ts:1001`, corroborated by official docs): config `provider` keys are
snapshotted → merged over the models.dev catalog → plugin hooks fire → auth loaders run.
Credentials live in `~/.local/share/opencode/auth.json` **keyed by provider id**, NOT by
npm package or model list. Deleting the `npm:@ai-sdk/openai-compatible` override and hand
model lists does not touch `auth.json`; builtin catalog pickup re-attaches the same stored
auth for openrouter/cerebras/groq/etc. Env-var credentials (`{env:…}`) likewise unaffected.
Sources: https://github.com/coleleavitt/opencode-openwebui-auth (README resolution-order
section); https://opencode.ai/docs/config (disabled_providers/env semantics).

### 3.2 Known regression vectors when reverting to catalog 🟡 MEDIUM

| Vector | Evidence | Impact on us |
|---|---|---|
| **Deprecation-status silent removal**: models marked `"status":"deprecated"` in models.dev are dropped from the picker EVEN IF config declares them under the catalog id | anomalyco/opencode #22644 + #22146 (maintainer workaround: override with `"status":"beta"`) | 🔴 DIRECT HIT on Phase 3d: `deepseek-v4-flash-free` is officially dead (see §6). Also a standing risk for ANY catalog-keyed entry we keep — a future upstream deprecation silently removes it while our config still names it. |
| **Stale cached model state after provider changes**: old bug where removed providers/models lingered or lists went empty until cache cleared (`rm ~/.local/state/opencode/model.json`) | #6251 (fix commit de28fafb) | 🟡 If post-deletion picker looks wrong, clear state cache before diagnosing. Check `~/.local/state/opencode/` during verification. |
| **v2 regression class**: config-declared custom-provider models with non-catalog ids silently dropped (0 models, no error) | #41360 (labeled v2) | 🟢 Likely N/A on 1.18.x (our custom `mimo-v2.5` works today), but confirms the fragility of non-catalog ids across version boundaries. |
| **System fallback overrides selection / built-in providers resist removal** | #26353 | 🟡 After Phase 2, expect builtin behaviors (fallbacks, environment-injected providers like Google [env]) to appear. This is WHY google-standard is kept — plan already accounts for it. |

### 3.3 Verdict Q1
No known 1.18.x issue where plain override-removal broke auth or emptied a provider's list
**when credentials were already stored**. The real deletion risks are (a) catalog-side
deprecation filtering (#22644 class) and (b) stale client caches (#6251 class). Both are
detectable in Phase-5 verification if you know to look. 🟡 MEDIUM confidence on absence
(absence-of-evidence); 🟢 HIGH on the two named vectors.

---

## §4 Q3 — VERSION DRIFT DURING EXECUTION + FREEZE STRATEGY

### 4.1 Findings
1. **Binary auto-update is ON and already fired** 🟢 HIGH: binary = 1.18.23, mtime
   2026-08-25 03:11 — one day before this review. The plan's "1.18.18" premise is dead.
   Official docs: OpenCode auto-downloads updates at startup; disable via
   `"autoupdate": false` in **GLOBAL config (project-level values are IGNORED)** or env
   `OPENCODE_DISABLE_AUTOUPDATE=true`. Sources: https://opencode.ai/docs/config;
   https://opencode.ai/v2/docs/config ("Project-level values are ignored");
   anomalyco/opencode #1793 (env var added by thdxr).
   Caveat 🟡: #3412 reported `autoupdate:false` being ignored for some local-config paths
   (fixed PR #3408) — use BOTH the global-config key AND the env var.
2. **Plugin `@latest` does NOT float** 🟢 HIGH: #30631/#25293 — `@latest` resolves ONCE at
   install time into a wrapper under `~/.cache/opencode/packages/<pkg>@latest/package.json`
   and is never re-resolved. So the drift risk from `@latest` is not "updates mid-plan";
   it's "silently stale forever". HOWEVER our install is stranger: `~/.config/opencode/
   package.json` maps the plugin to a LOCAL `file:` checkout inside the repo (git HEAD
   `7db338b`). Which resolution wins is unresolved (§9 U3) — meaning the effective plugin
   code can change via a plain `git pull` + rebuild in the repo, invisible to config backups.
3. **models.dev catalog is live remote data** 🟢 HIGH: catalog contents (ids, limits,
   deprecation status) can change between phases independent of any local action — this is
   exactly how `mimo-v2.5`→`mimo-v2.5-free` and the DeepSeek free kill happened.

### 4.2 Freeze strategy (execute BEFORE Phase 0)
```bash
export OPENCODE_DISABLE_AUTOUPDATE=true        # shell profile + execution session
# AND add to GLOBAL config only:
#   "autoupdate": false
```
Plus:
- Record `opencode --version` (expect 1.18.23) and plugin provenance
  (`git -C omega-engine/opencode-antigravity-auth rev-parse HEAD`) in the run log before each phase.
- No `git pull` / rebuild inside `omega-engine/opencode-antigravity-auth` during the window.
- Pin plugin spec `opencode-antigravity-auth@<exact>` OR leave as-is but snapshot
  `~/.cache/opencode/packages/` wrapper state (see §8).
- Time-box the whole remediation to a single session; catalog drift between days is the
  residual risk no local freeze fully removes.

---

## §5 Q4 — ANTIGRAVITY SONNET-4-6-THINKING RISKS

1. **Schema defect in plan (BLOCKER C1)** 🟢 HIGH: issue #495's own snippet uses nested
   `"thinkingConfig":{"thinkingBudget":…}`, and the npm README shows the same — BUT the
   installed plugin source reads variant keys FLAT: `request.js:663`
   (`variantConfig?.thinkingBudget`), `model-resolver.js:311`. The working sibling Opus
   entry in `.opencode/opencode.json` uses flat `"thinkingBudget": 8192` and works.
   Resolution: **use flat keys** (empirically validated locally); the docs/issue snippets
   reflect either an older/newer plugin or doc simplification. Verify once with a single
   smoke call at `--variant=low`.
   Sources: local dist inspection; https://github.com/NoeFabris/opencode-antigravity-auth/issues/495; npm README.
2. **Signature-error history on Claude thinking** 🟡 MEDIUM: #245 ("Unknown name
   thinking/signature/type", fixed v1.3.1-beta via `isOurCachedSignature`) and #126
   ("Invalid signature in thinking block" with keep_thinking, root-caused, fixed). Our
   local checkout (7db338b ≥1.6.0) postdates both fixes, but the failure class exists and
   resurfaces whenever signature cache misses meet multi-turn tool use. Smoke-test must
   include at least one tool call, not just chat.
3. **keep_thinking:true costs** 🟢 HIGH: README warns enabling "may degrade model
   stability"; mechanically it re-sends thinking blocks each turn → higher input-token
   burn against Antigravity quota and exposure to the #126 signature-cache-miss failure
   mode. Recommendation: keep `false` for the remediation window; flip later as an
   isolated change.
4. **Quota routing & rotation** 🟡 MEDIUM: `-thinking` SKUs route via Antigravity quota
   (QUOTA_PREFIX_REGEX strips prefix; `supportsThinkingTiers()` gates on id containing
   claude+thinking — verified in local resolver source). Per-model-family rate limits +
   sticky account selection preserve prompt cache; Google actively throttles 3rd-party
   usage patterns (#245 comment thread). A NEW thinking SKU adds a new family entry —
   expect first-use quota surprises; `switch_on_first_rate_limit:true` is already set,
   which mitigates.
5. **Sonnet-thinking is NOT in plugin default presets** 🟢 HIGH (issue #495 open since
   Feb): means zero upstream test coverage for this exact SKU; treat as custom-model
   territory — if it errors, it's ours to debug, not the plugin's.

---

## §6 Q5 — ZEN FREE-TIER QUIRKS (mimo / deepseek / nemotron)

1. **`deepseek-v4-flash-free` IS DEAD — plan Phase 3d targets a corpse** 🔴 CRITICAL:
   Maintainer-confirmed (#43829, ~2026-08-21): "The limited-time DeepSeek V4 Flash Free
   promotion has ended… no longer available in the model picker." Live completions fail
   400 "Model is unavailable" for everyone; catalog marks it deprecated (picker hides it,
   per #22644 mechanism). Duplicates: #43805, #41708. Earlier 429 storms (#42977, #42385,
   #42128) were the wind-down.
   → **Phase 3d must be re-scoped**: do NOT "refresh limits to live values" (that adopts
   the 200K cap on a dead SKU). Either DELETE the deepseek entry + `config/providers.yaml`
   reference, or keep as tombstone with a comment. Engine-side dependents listed in §2.
2. **`mimo-v2.5-free`**: alive post-restructure 🟡 MEDIUM — listed among working free
   models in #43829 triage; intermittent 429 `FreeUsageLimitError` reports exist
   (#42977: mimo 429 while nemotron 200; daily window w/ ~19h Retry-After) but no
   hard-failure reports after the id change.
3. **Old id `mimo-v2.5` still resolves server-side** 🟢 HIGH (empirical: our working
   entry proves it) — but the DeepSeek precedent shows Zen kills/renames free SKUs with
   zero notice and NO deprecation grace on non-catalog ids. Relying on the ghost id even
   briefly carries unquantifiable deprecation risk; the re-key to `mimo-v2.5-free` is the
   right call. Note the trade: catalog-keyed ids inherit deprecation filtering (#22644) —
   if upstream ever flips `mimo-v2.5-free` to deprecated, our override keyed to that id
   may be hidden too; a `"status":"beta"` override is the documented escape hatch.
4. **`nemotron-3-ultra-free`**: healthy 🟢 HIGH — consistently the 200-OK control in
   every rate-limit triage thread (#42977 etc.). Keeping it as `model`/`small_model` is safe.
5. **General Zen free-tier instability** 🟡 MEDIUM: #41236 documents frequent upstream
   failures/timeouts across `-free` models (gateway-level, ongoing); #44300 reports
   `x-preview-f-free` failing with "Endpoint is unavailable" for tool-containing requests.
   → Verification smoke calls may fail for reasons UNRELATED to our config edits. Any
   Phase-5 verification must distinguish gateway flake from config regression (retry +
   cross-check a second free model before declaring failure).

---

## §7 Q6 — ORDERING HAZARDS + REVISED EXECUTION ORDER

### 7.1 Hazards in the proposed order
1. **Phase 1 (rename) then Phase 2 (delete) touches the same blocks twice** 🟡: renaming
   display names inside provider blocks that Phase 2 then deletes outright is wasted,
   review-noise-generating work, and doubles the diff surface. Merge into one edit pass:
   delete the 9 blocks; only rename inside blocks that SURVIVE.
2. **Override deletion vs variants re-schema order** 🟡 MEDIUM: deleting the openrouter
   override while `small_model` fallback chains reference its models would orphan the
   reference at startup. Verified: nothing references `openrouter/*` in either config's
   `model`/`small_model` (both = nemotron), so THIS plan is safe — but the general rule
   stands: never delete a provider block whose ids are referenced by `model`,
   `small_model`, agent definitions, or CI pins in the same commit that deletes them.
3. **MiMo re-key should come AFTER variant re-schema** 🟢: re-keying to `mimo-v2.5-free`
   with the old nested schema would recreate the exact "no thinking levels" bug on the new
   id. Re-schema first, then re-key, then verify variants render.
4. **keep_thinking flip isolated** (R3): separate session/change.

### 7.2 REVISED EXECUTION ORDER
```
Phase F0  FREEZE: OPENCODE_DISABLE_AUTOUPDATE=true + global "autoupdate": false;
          record binary version + plugin HEAD; full rollback bundle (§8)
Phase F1  BACKUP: timestamped copies of global/project/subdir configs + auth.json +
          antigravity state files + plugin wrapper cache manifest
Phase F2  SINGLE-PASS DEPOLLUTION (merges old P1+P2):
          - DELETE the 9 redundant provider blocks (global + project openrouter block)
          - In SURVIVING blocks only: strip "(Free)" names/prefixes
          - KEEP google-standard, lmstudio, ollama, native-gguf-*, opencode
          Verify: picker clean, builtin catalogs present, auth intact (one smoke call
          per previously-overridden provider you actually use)
Phase F3  ZEN VARIANTS RE-SCHEMA (flat reasoningEffort) on kept entries
          Verify: variant options render for nemotron/deepseek*
Phase F4  MIMO RE-KEY mimo-v2.5 → mimo-v2.5-free (+ live limits 200000/32000)
          Verify: single MiMo entry, no erroring ghost, variants render
Phase F5  DEEPSEEK DECISION (re-scoped 3d): delete entry or tombstone;
          update config/providers.yaml + token_budgets to match
Phase F6  SUBDIR: add antigravity-claude-sonnet-4-6-thinking with FLAT
          thinkingBudget variants (8192/32768)
          Verify: picker shows SKU; smoke call --variant=low INCLUDING one tool call
Phase F7  FINAL: opencode --version unchanged; plugin HEAD unchanged; session-resume
          spot-check on an old session (expect benign model-not-found on deleted ids)
```
(*deepseek variants moot if F5 deletes it.)

---

## §8 Q7 — ROLLBACK BUNDLE CHECKLIST

Global config is NOT in git; plugin is a repo-local git checkout; several state stores are
live-mutated by the TUI. Guaranteed rollback requires ALL of:

| # | Item | Path | Why |
|---|---|---|---|
| 1 | Global config | `~/.config/opencode/opencode.json` (+ existing `.backup*` files left untouched) | primary target |
| 2 | Project config | `opencode.json` | git-tracked BUT commit the pre-change state or stash — working-tree loss ≠ git loss |
| 3 | Subdir config | `.opencode/opencode.json` | same |
| 4 | **auth.json** | `~/.local/share/opencode/auth.json` | credentials for all providers; NOT regenerated from configs |
| 5 | **antigravity-accounts.json** | `~/.config/opencode/antigravity-accounts.json` | Google OAuth accounts/tokens for plugin rotation |
| 6 | antigravity.json | `~/.config/opencode/antigravity.json` | plugin behavior flags |
| 7 | zen_accounts_state.json | `~/.config/opencode/zen_accounts_state.json` | currently empty but part of the auth surface |
| 8 | **Plugin provenance** | `git -C omega-engine/opencode-antigravity-auth rev-parse HEAD` recorded + `git stash list` clean; note dirty files | file: dependency can drift via pull/rebuild |
| 9 | **Plugin wrapper cache manifest** | `ls ~/.cache/opencode/packages/` + contents of any `opencode-antigravity-auth@latest/package.json` wrapper | @latest pins silently (#30631); needed to prove which code actually loaded |
| 10 | `~/.config/opencode/package.json` + `bun.lock` + `node_modules/` manifest | global plugin install dir | defines the file: resolution |
| 11 | Binary version stamp | `opencode --version` output in run log | autoupdate may swap binary mid-window otherwise |
| 12 | tui.json | DOES NOT EXIST here (verified §1) — drop from bundle; note in run log | mission listed it speculatively |

Rollback procedure: restore 1–3 + 4–7 from timestamps; `git -C … checkout <recorded-HEAD>`
for 8; rebuild plugin dist if dist/ changed (`bun run build` per repo docs — record the
command used); relaunch with autoupdate still disabled.

---

## §9 RESIDUAL UNKNOWNS (M23 honesty manifest)

| ID | Unknown | Why unresolved | Mitigation |
|---|---|---|---|
| U1 | Exact 1.18.23 behavior deltas vs 1.18.18/1.18.19 relevant to provider loading | release notes not enumerated in this pass | read changelog before F0; freeze makes it constant regardless |
| U2 | Whether nested `thinkingConfig.thinkingBudget` ALSO works on 1.18.x via OpenCode-level variant normalization (docs show nested; source shows flat) | conflicting doc-vs-source evidence | use FLAT (empirically working sibling); single smoke test settles it |
| U3 | Which resolution wins for the plugin: local `file:` checkout vs `@latest` npm wrapper | both present; no local log checked | inspect startup log (~/.local/share/opencode/log/) at F0; record which path loads |
| U4 | Server-side lifetime of ghost id `mimo-v2.5` | Zen gives no deprecation notices | minimize exposure — re-key in F4, don't linger |
| U5 | Whether any of the 9 deleted providers' hand-listed models are ABSENT from current builtin catalog (would silently shrink options) | live catalog diff not run per-provider | during F2 verification, spot-check each retained provider's picker count |
| U6 | x-preview-f-free tools-endpoint instability (#44300) impact on this very session's verification calls | upstream, open issue | cross-check failures against a second model before diagnosing |

## §10 SOURCES

Local (🟢 direct inspection, 2026-08-26): all paths in §1; plugin dist files
`dist/src/plugin/request.js`, `dist/src/plugin/transform/model-resolver.js`;
repo grep inventory §2.

Web:
- https://github.com/anomalyco/opencode/issues/22644 (deprecation status silent removal + workaround)
- https://github.com/anomalyco/opencode/issues/22146 (config entry ignored for deprecated catalog model)
- https://github.com/anomalyco/opencode/issues/43829 (DeepSeek V4 Flash Free promo ended — maintainer confirmed)
- https://github.com/anomalyco/opencode/issues/43805, /issues/41708 (same, duplicates)
- https://github.com/anomalyco/opencode/issues/42977, /issues/42385, /issues/42128 (Zen free-tier 429 storms)
- https://github.com/anomalyco/opencode/issues/41236 (free-tier upstream instability)
- https://github.com/anomalyco/opencode/issues/44300 (x-preview-f-free tools endpoint unavailable)
- https://github.com/anomalyco/opencode/issues/40958 (deepseek-free 200K metadata cap)
- https://github.com/anomalyco/opencode/issues/6251 (stale model cache; rm ~/.local/state/opencode/model.json)
- https://github.com/anomalyco/opencode/issues/26353 (builtin provider removal resistance; system fallback)
- https://github.com/anomalyco/opencode/issues/41360 (v2: custom non-catalog models dropped)
- https://github.com/anomalyco/opencode/issues/30631 + /issues/25293 (@latest resolves once, pins stale)
- https://github.com/anomalyco/opencode/issues/1793 (OPENCODE_DISABLE_AUTOUPDATE added)
- https://github.com/anomalyco/opencode/issues/3412 (autoupdate:false ignored — fixed PR #3408)
- https://opencode.ai/docs/config ; https://opencode.ai/v2/docs/config (autoupdate semantics; project ignored)
- https://github.com/NoeFabris/opencode-antigravity-auth/issues/495 (sonnet-thinking missing; maintainer response)
- https://github.com/NoeFabris/opencode-antigravity-auth/issues/245 (Claude thinking signature errors; fix v1.3.1-beta)
- https://github.com/NoeFabris/opencode-antigravity-auth/issues/126 (keep_thinking signature validation bug)
- https://www.npmjs.com/package/opencode-antigravity-auth (README: variant formats, keep_thinking warning, rotation)
- https://github.com/coleleavitt/opencode-openwebui-auth (provider resolution order citation)

Tool-failure note (M23): Exa search returned HTTP 401 (invalid API key) during this
session; research completed via parallel-search + websearch instead. No findings were
synthesized without a live source.

---
*⬡ OMEGA ⬡ JEM ⬡ PREEXEC-REVIEW ⬡ CONDITIONAL-GO ⬡ 2026-08-26*
