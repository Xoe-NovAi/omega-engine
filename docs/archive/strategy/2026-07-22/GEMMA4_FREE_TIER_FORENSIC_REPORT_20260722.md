# 🔱 Gemma 4 Free-Tier Forensic Report — Workhorse Collapse & OpenCode Provider Incident
**AP Token**: `AP-GEMMA4-FREE-TIER-FORENSIC-20260722-v1.0.0`
⬡ OMEGA ⬡ GROK-CLI ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_forensic ⬡ INVESTIGATION-HANDOFF

**Date**: 2026-07-22  
**OpenCode Version (at write)**: 1.18.4  
**Status**: FORENSIC COMPLETE (local evidence) — GOOGLE-SIDE CHANGE NOT PROVEN FROM PUBLIC CHANGELOG; BEHAVIORAL CLIFF DATED  
**Audience**: Architect + fleet agents (`@kali`, `@researcher`, `@roc_racoon`, `@verity`, `@makali`, `@grok_cli`)  
**Purpose**: Single dossier of all findings on free-tier Gemma 4 31B history, the 16k input-token cliff, OpenCode “way too hot” retry storms, provider config damage, and **open dig tickets** for deeper agent work.

**Tags**: gemma-4, free-tier, quota, opencode, antigravity, forensic, provider, 429, TPM, RPM  

**Cross-references**:
- **Ops critical path (G-1 + W-1)**: `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`
- **Ark tickets**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` §4 G-1/W-1 · D-377…D-381
- **Strategy index**: `docs/strategy/STRATEGY_INDEX.md` (v5.2 P0 overlay)
- **Corpus map**: `docs/strategy/STRATEGY_CORPUS_MAP.md`
- `docs/archive/strategy/2026-07-21/GEMMA4_OPENCODE_DEBUG_REPORT_20260718.md`
- `docs/archive/strategy/2026-07-21/GEMMA4_COMPREHENSIVE_REPORT_20260719.md`
- `docs/archive/strategy/2026-07-21/GEMMA4_HARDENED_STRATEGY_20260719.md`
- `docs/archive/strategy/2026-07-21/GEMMA4_BUG_TO_FEATURE_STRATEGY.md`
- `docs/archive/strategy/2026-07-21/GEMMA4_PROVIDER_FEATURE_STRATEGY_20260719.md`
- `data/projects/antigravity-multi-account/CONTEXT.md`
- `data/projects/warp-proxy-pool/CONTEXT.md` (WARP is **not** a free-Gemma fix)
- Google rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
- AI Studio live limits: https://aistudio.google.com/rate-limit

---

## 0. Answer-First (for agents)

| Claim | Verdict | Evidence grade |
|-------|---------|----------------|
| User **did** live on free-tier Gemma 4 31B as workhorse for weeks/months | **TRUE** | DB + log (May 27 → ~Jul 13) |
| Free tier was “unlimited tokens forever” by contract | **FALSE** — felt unlimited operationally | Pre-cliff free metric was **15 RPM**, rarely hit |
| **16k** is OpenCode context cap in config | **FALSE** | Google 429 body; config advertises 262144 context |
| **16k** is free-tier **input token** quota for `gemma-4-31b` | **TRUE** (post-cliff) | First log hit **2026-07-15T16:28:37Z** |
| Pre-cliff free metric for Gemma | **`generate_content_free_tier_requests` limit 15** | Only 4 hits (Jun 15, Jul 10) |
| Cliff date for input-token free tier | **2026-07-15 ~16:28 UTC** | First `free_tier_input_token_count` / 16000 |
| Titles use Gemma’s 16k | **FALSE** | Titles = `gemini-3.6-flash` (`small=true`) |
| Direct tiny Gemma API still works | **TRUE** (2026-07-22) | HTTP 200, ~6 input tokens |
| Fat OpenCode + free Gemma = structural fail post-cliff | **TRUE** | Omega instructions alone ~14k tokens est. |
| Roc/config mess caused the 16k quota | **FALSE** | 16k is Google; config caused separate 400/path bugs |
| History is gone | **FALSE** | Lives in `opencode.db` + `opencode.log` |

---

## 1. Executive Summary

For roughly **late May through mid-July 2026**, OpenCode on this machine ran **Google AI Studio API free-tier `gemma-4-31b-it`** as the primary coding workhorse—multi-hour days, high `variant=high` usage, tens of millions of input tokens on peak days.

That era ended in practice on **2026-07-15**, when Google began returning (for this project/key) a free-tier error that **had never appeared** in a month of heavy Gemma traffic:

```text
Quota exceeded for metric:
  generativelanguage.googleapis.com/generate_content_free_tier_input_token_count
limit: 16000
model: gemma-4-31b
status: RESOURCE_EXHAUSTED (HTTP 429)
```

OpenCode surfaces this as **“Gemini is way too hot right now”** and **retries aggressively**, which makes the failure feel permanent.

Separately, mid-July **OpenCode provider config damage** (forced `apiKey`/`baseURL` on shared `google`, invalid plugin `"list"`, uppercase thinking levels, Gemma whitelist hiding Antigravity) created a **second failure mode**. Config was cleaned during 2026-07-22 recovery; **the free-tier 16k cliff remains**.

This report freezes local forensic evidence and lists **deeper dig tickets** for agents.

---

## 2. Evidence Corpus (where history lives)

### 2.1 Primary (machine-local, authoritative)

| Path | Role | Scale (2026-07-22 snapshot) |
|------|------|-----------------------------|
| `~/.local/share/opencode/opencode.db` | Session/message store | ~**13 GB**; **2206** sessions; **88385** messages; **376849** parts |
| `~/.local/share/opencode/log/opencode.log` | Stream/error timeline | ~**138 MB+**; Gemma stream starts **~11721** across 36 days |
| `~/.local/share/opencode/auth.json` | Provider auth | `google` type **`api`** only; `openrouter` type `api` (2026-07-22) |
| `~/.config/opencode/opencode.json` | Global OpenCode config | Gemma variants + Antigravity model cards; compaction settings |
| `omega-engine/opencode.json` | Project config | Fat `instructions[]`; no google models block at root |
| `omega-engine/.opencode/opencode.json` | Project google provider | Antigravity + Gemma model definitions |
| `~/.config/opencode/antigravity.json` | Antigravity plugin opts | rotation strategy flags; **not** account store |

### 2.2 Secondary (repo strategy archive)

| Path | Role |
|------|------|
| `docs/archive/strategy/2026-07-21/GEMMA4_OPENCODE_DEBUG_REPORT_20260718.md` | Thinking/config bugs + first 16k diagnosis |
| `docs/archive/strategy/2026-07-21/GEMMA4_*` | Provider/feature strategies |
| `data/projects/antigravity-multi-account/CONTEXT.md` | 8-account OAuth rotation research (2026-07-19) |

### 2.3 Not the history store

- Omega git tree does **not** hold full chat transcripts.
- `storage/session_diff/` is diffs, not the conversational SSOT.
- Google AI Studio UI rate-limit page is **live** truth for current project quotas (not snapshotted here).

### 2.4 DB aggregate (Gemma 4 31B sessions)

Query basis: `session.model` JSON contains `gemma-4-31b`.

| Metric | Value |
|--------|-------|
| Sessions | **830** |
| Sum `tokens_input` | **~262,391,477** |
| Sum `tokens_output` | **~4,755,376** |
| First session `time_created` | **2026-05-27T19:25:51Z** |
| Last session `time_created` | **2026-07-22T20:38:44Z** |
| Dominant model JSON | `{"id":"gemma-4-31b-it","providerID":"google","variant":"high"}` (**596** sessions) |
| Other variants | `default` (232), bare model (1), OpenRouter free (1), 26B high (12) |

**Note**: Session token fields are OpenCode’s accounting. They prove scale of historical use; they are not Google’s official billing export.

---

## 3. Timeline (forensic)

### 3.1 Workhorse era (healthy enough to live on)

| Date (UTC) | Signal |
|------------|--------|
| **2026-05-27** | First Gemma 31B sessions in DB |
| **2026-05-27 → 2026-06-09** | Heavy DB token days before continuous log focus (e.g. Jun 5 ~17.3M input session-agg) |
| **2026-06-10** | Continuous `opencode.log` Gemma streams begin in analyzed window; OpenCode **1.17.3** |
| **2026-06-11–12** | Peak log volume (1000–1450 streams/day); multi-hour spans (14–16 UTC hours) |
| **2026-06-15** | First explicit free-tier metric on Gemma: **`free_tier_requests` limit 15** (RPM-class) |
| **2026-06–07-13** | Sustained workhorse; errors mostly **Internal error** / **high demand** |
| **2026-07-07** | Example healthy day: **1161** streams, **~3.4%** error rate |
| **2026-07-10** | Again `free_tier_requests` limit **15** (still not 16k input tokens) |
| **2026-07-13** | Last substantial pre-cliff day (~129 streams); ends with Internal errors |
| **2026-07-14** | **Zero** Gemma streams in log (gap day) |

### 3.2 Cliff and after

| Date (UTC) | Signal |
|------------|--------|
| **2026-07-15T16:28:37.167Z** | **FIRST** `free_tier_input_token_count` **limit: 16000** for `gemma-4-31b` |
| **2026-07-15–18** | Error rate ~90–100%; usage collapses (~8–57 streams/day) |
| **2026-07-16** | Same 16k metric on **`gemma-4-26b`** |
| **2026-07-18** | Debug report written; config + quota both in play |
| **2026-07-19** | Antigravity multi-account research project filed |
| **2026-07-20–21** | Near-dead Gemma usage in log |
| **2026-07-22** | Provider cleanup (remove forced google options, fix variants, drop plugin `list`); **16k free-tier still blocks fat sessions**; direct tiny API OK |

### 3.3 OpenCode version trail (Gemma session creates)

| Day | Version (from log `message=created` + gemma model) |
|-----|------------------------------------------------------|
| 2026-06-10–11 | 1.17.3 |
| 2026-06-12–13 | 1.17.4 |
| … | progressive 1.17.x |
| 2026-07-11 | 1.17.18 |
| 2026-07-13 | 1.17.19 |
| 2026-07-22 | 1.18.4 |

**Conclusion**: Version churn correlates with calendar, **not** with inventing the 16k metric. The 429 text is Google’s.

---

## 4. Free-tier metrics — the actual rule change (behavioral)

### 4.1 All free-tier / quota metrics observed for Gemma in `opencode.log`

| Metric | Limit | Model | Count | First | Last | Days |
|--------|-------|-------|-------|-------|------|------|
| `generate_content_free_tier_requests` | **15** | gemma-4-31b | **4** | 2026-06-15 | 2026-07-10 | Jun 15, Jul 10 |
| `generate_content_free_tier_input_token_count` | **16000** | gemma-4-31b | **88** | **2026-07-15** | 2026-07-22 | Jul 15–18, 22 |
| `generate_content_free_tier_input_token_count` | **16000** | gemma-4-26b | **1** | 2026-07-16 | 2026-07-16 | Jul 16 |

### 4.2 Pre-cliff vs post-cliff error character

**Pre-cliff (Jun 10 – Jul 13) dominant Gemma errors:**

| Message | Approx count (pre-Jul-15 sample window) | Meaning |
|---------|------------------------------------------|---------|
| Internal error encountered | ~1050 | Backend flakiness |
| high demand / try again later | ~91 | Capacity |
| Resource has been exhausted (generic) | ~41 | Soft quota/capacity |
| free_tier_requests limit 15 | 4 | True free RPM |
| free_tier_input_token_count 16000 | **0** | Did not exist in this traffic |

**Post-cliff (Jul 15+):** almost exclusively **free_tier_input_token_count / 16000**.

### 4.3 Comparison: Gemini Flash free tier (same machine, earlier)

From same log family (Gemini, not Gemma):

```text
generate_content_free_tier_input_token_count, limit: 250000, model: gemini-3.5-flash
```

So free-tier **input TPM is model-specific**. Flash free was ~**250k**; Gemma free post-cliff is **16k**. That alone does not explain pre-cliff Gemma success—pre-cliff Gemma traffic simply **never received** the 16k input metric.

### 4.4 Why “15 RPM free” felt unlimited

Operational model pre-cliff:

```text
Free gate ≈ 15 requests per minute (rarely hit)
Context window  ≈ large (config 262144)
Fat Omega prompts allowed
Pain = capacity/internal + occasional RPM
Daily multi-hour use viable
```

Post-cliff:

```text
Free gate ≈ 16000 input tokens per time window (TPM-class)
One fat OpenCode turn (instructions + tools + history) can exhaust window
OpenCode retries 429 → "way too hot" storm
Workhorse dead for Omega-sized sessions
Tiny direct API still works
```

### 4.5 What “16k” is NOT

| Not this | Why |
|----------|-----|
| Model context window | Config/model still ~256k |
| OpenCode `limit.context` free-tier diet | Never applied (Architect rejected caps 2026-07-22) |
| Title-generation budget on Gemma | Titles use `gemini-3.6-flash` |
| A number invented by Omega `configs/token_budgets.yaml` | Unrelated local budget file exists; Google 429 is independent |

### 4.6 “12k” mention

**12k was only a rejected workaround idea** (artificial OpenCode context diet to stay under free TPM). **Not a Google limit. Not applied.**

---

## 5. Volume evidence (workhorse scale)

### 5.1 Log: stream starts per day (`message=stream` + `modelID=gemma-4-31b-it`)

Selected:

| Day | Streams | Uniq sessions | Errors | Err rate |
|-----|---------|---------------|--------|----------|
| 2026-06-12 | 1451 | 102 | 127 | 8.8% |
| 2026-07-05 | 1130 | 13 | 101 | 8.9% |
| 2026-07-07 | 1161 | 6 | 40 | **3.4%** |
| 2026-07-13 | 129 | 14 | 26 | 20.2% |
| 2026-07-15 | 8 | 2 | 8 | **100%** |
| 2026-07-22 | 27 | 8 | 22 | 81.5% |

**Totals:** ~**11607** streams pre-cliff (≤ Jul 13); ~**114** post-cliff (≥ Jul 15).

### 5.2 Log: active UTC hours (span of workhorse days)

Examples: Jun 11 **14h**, Jun 12 **16h**, Jun 21 **16h**, Jul 1 **14h**, Jul 7 **14h**.  
Matches user report of long continuous use.

### 5.3 DB: peak session-aggregate input token days (illustrative)

| Day | Gemma sessions | tokens_input (sum) |
|-----|----------------|--------------------|
| 2026-06-12 | 100 | ~29.99M |
| 2026-06-29 | 35 | ~21.01M |
| 2026-06-11 | 46 | ~19.08M |
| 2026-06-28 | 17 | ~18.60M |
| 2026-06-05 | 93 | ~17.34M |

---

## 6. OpenCode UX: “Gemini is way too hot right now”

### 6.1 Mapping

| Layer | Behavior |
|-------|----------|
| Google API | HTTP **429** `RESOURCE_EXHAUSTED` + free-tier metric text |
| AI SDK / OpenCode | `isRetryable: true` on many 429s |
| UI | Friendly string **“gemini is way too hot right now… retrying…”** |
| Effect | Retry storm keeps window hot; feels permanently broken |

### 6.2 Title vs main model (2026-07-22 log)

| Role | Flags | Model |
|------|-------|--------|
| Title | `agent=title`, `small=true` | `google/gemini-3.6-flash` |
| Main | `agent=build` (etc.), `small=false` | `google/gemma-4-31b-it` |

Titles burn **Flash free-tier** (separate model metrics), not “Gemma’s 16k.” Both share the Google API key **project** free-tier universe.

### 6.3 Direct API control (2026-07-22)

Stored Google API key: tiny `gemma-4-31b-it` generateContent with `thinkingLevel: MINIMAL` → **HTTP 200**, ~6 prompt tokens.  
**Key alive; model alive; free-tier budget / payload size is the blocker for fat sessions.**

---

## 7. Provider / config incident (orthogonal but co-timed)

### 7.1 Footguns introduced during Gemma recovery attempts (Roc et al.)

| Footgun | Symptom | Status 2026-07-22 |
|---------|---------|-------------------|
| `provider.google.options.apiKey` + `baseURL` on shared google | Forces AI Studio path; breaks Antigravity OAuth routing (“model not found” on v1beta for antigravity IDs) | **Removed** from project configs |
| Plugin entry `"list"` | `failed to load plugin path=list` | **Removed** |
| `thinkingLevel: "HIGH"` / invalid levels | SDK rejects; Gemma only MINIMAL/HIGH (API) with OpenCode variant mapping | Variants restored **lowercase** `minimal`/`high` |
| Gemma-only **whitelist** on google | Hides Antigravity models | **Do not re-add** (prior Kali incident) |
| Auth | `google` type **api** only; no live antigravity account JSON observed | Antigravity OAuth re-login still needed for that path |

### 7.2 Dual Google paths (architecture)

```text
Path A — AI Studio API key
  auth.json google type=api
  models: gemma-4-*, gemini-*-preview (API)
  free-tier metrics: free_tier_* on generativelanguage.googleapis.com

Path B — Antigravity OAuth plugin
  opencode-antigravity-auth
  models: antigravity-gemini-*, antigravity-claude-*
  quota pool: Cloud Code / Antigravity (NOT the same as free AI Studio Gemma TPM)
```

**Never** put API key/baseURL on the shared `google` provider if Path B must work.

### 7.3 Fat context contributors (project)

Root `opencode.json` `instructions` (approx size by bytes/4):

| File | ~tokens |
|------|---------|
| SOVEREIGN_MANDATES.md | ~5311 |
| ORACLE_STACK.md | ~109 |
| MASTER_SYNTHESIS… | ~5895 |
| SOVEREIGN_ARK_BLUEPRINT.md | ~2685 |
| CREDITS.md | ~353 |
| **Sum instructions only** | **~14.3k** |

Plus system/agent prompts, tools, MCP schemas, chat history → routinely **>16k free input** post-cliff.

Architect directive **2026-07-22**: **do not add artificial context caps** to “fix” free tier.

---

## 8. Related systems / red herrings

| Item | Relevance |
|------|-----------|
| OpenRouter `google/gemma-4-31b-it:free` | Separate free pool; previously hit daily free-model caps (see Jul 18 report) |
| Antigravity multi-account (8 Gmail) | Mitigation research for OAuth frontier quota; not the historical workhorse path in DB |
| Local LM Studio models | Different provider; small context limits are VRAM, not Google free tier |
| `configs/token_budgets.yaml` hard_limit 16000 | Local Omega budget artifact — **do not confuse** with Google metric |
| Gemini “no longer available to new users” / invalid key on some Flash IDs | Separate Google product/API availability issues |

---

## 9. Working theory (for agents to stress-test)

### Theory T1 — Google free-tier policy/enforcement change for Gemma (~2026-07-15)

**Claim**: Google began enforcing (or newly published) **free-tier input TPM = 16000** for `gemma-4-31b` (and 26B), replacing an operational regime where free traffic was gated mainly by **RPM (15)** + capacity.

**Support**: Metric never appears pre-Jul-15 despite huge volume; appears suddenly and dominates after.

**Falsifiers**:
- Same 16k always existed but errors were suppressed/mis-logged (unlikely—other free_tier strings logged fine).
- Project tier demotion on that exact day (check AI Studio project history).
- API key / project swap on Jul 15 (check key creation dates, project IDs).

### Theory T2 — Project/key tier demotion or quota reclassification

**Claim**: This Cloud/AI Studio project fell to free tier or lost a higher experimental allowance.

**Support**: Direct calls return free_tier metric names.

**Falsifiers**: Billing already Tier 1+ on that project; rate-limit UI shows paid TPM.

### Theory T3 — OpenCode started sending larger prompts around Jul 15

**Claim**: Payload growth alone triggered a latent 16k limit.

**Weak**: Pre-cliff days already show multi-million token session aggregates; limit-15 RPM was the free metric then. A latent 16k TPM would have fired constantly during Jun peaks.

### Theory T4 — Config bugs only

**Claim**: Thinking/prefix bugs explain “dead Gemma.”

**Partial**: Explain 400s/empty/wrong path; **do not** explain free_tier_input_token_count 16000 body.

---

## 10. Open dig tickets (for agents)

Assign freely. Each ticket is **self-contained**.

### DIG-01 — AI Studio live quota snapshot
**Owner**: human + `@researcher`  
**Do**:
1. Open https://aistudio.google.com/rate-limit for **every** Google project/key used with OpenCode.
2. Record table: model → RPM/TPM/RPD free vs paid for `gemma-4-31b-it`, `gemma-4-26b-a4b-it`, Flash family.
3. Note usage tier (Free / Tier 1+).
4. Screenshot or export dated **YYYY-MM-DD**.  
**Done when**: Numbers frozen in an appendix to this report or sibling file.

### DIG-02 — API key / project archaeology
**Owner**: `@roc_racoon` / human  
**Do**:
1. List all Google API keys ever used (AI Studio, env `GOOGLE_GENERATIVE_AI_API_KEY`, shell history carefully, password manager).
2. Map key → project → create date → whether rotated near **2026-07-15**.
3. Check if workhorse era used a **different project** with looser free or experimental quotas.  
**Done when**: Key lineage timeline exists.

### DIG-03 — Google public changelog / community reports
**Owner**: `@researcher` (web T1–T6, date-bound **2026**)  
**Do**:
1. Search for Gemma 4 free tier TPM changes, 16k input free tier, mid-July 2026 rate limit posts.
2. Collect discuss.ai.google.dev / release notes / AI Studio announcements.  
**Done when**: “Public confirmation yes/no” with links; if no public note, mark **unconfirmed vendor-side change**.

### DIG-04 — Export day-by-day Gemma token CSV from DB
**Owner**: `@pillar` P8 / any  
**Do**: SQL/Python over `session` + `message` → CSV: date, sessions, tokens_input, tokens_output, error proxy from log join if possible.  
**Done when**: `docs/archive/strategy/2026-07-22/data/gemma4_daily_usage.csv` (or under `data/`).

### DIG-05 — Message-level success vs failure reconstruction
**Owner**: `@verity`  
**Do**: Parse `message.data` JSON for assistant roles with `modelID=gemma-4-31b-it`; classify finish vs error; sample pre/post cliff prompt sizes if stored.  
**Done when**: Statistical confirmation of success rate cliff independent of log stream counts.

### DIG-06 — OpenCode retry policy hard-stop
**Owner**: `@doom_guy` / OpenCode config research  
**Do**: Find whether `maxRetries` / provider options can **stop 429 retry storms** without context caps. Document config key + recommended value for free-tier death.  
**Done when**: Working config snippet or “not configurable; file upstream issue.”

### DIG-07 — Antigravity path restore smoke
**Owner**: human (OAuth interactive) + `@kali` verify  
**Do**:
1. `opencode auth login` (Google / Antigravity OAuth).
2. Confirm account artifact appears.
3. Smoke: `opencode run -m google/antigravity-gemini-3-flash "ping"`.  
**Done when**: Path B green without touching free Gemma.

### DIG-08 — Multi-account free AI Studio vs Antigravity pools
**Owner**: `@researcher` + `data/projects/antigravity-multi-account`  
**Do**: Clarify legally/technically: rotating **AI Studio API keys** vs rotating **Antigravity OAuth**. Risk of ban. Whether free Gemma 16k is per-project or per-billing-account.  
**Done when**: Decision memo: allowed / forbidden / grey + recommended architecture.

### DIG-09 — Instruction set cost audit (no caps)
**Owner**: `@maat`  
**Do**: Measure actual tokenized size of full OpenCode system+instructions+tools for a cold Gemma turn (instrumented request dump if possible). Compare to 16k. Propose **optional** gemma-lite *profile* (separate config file), **not** silent global caps.  
**Done when**: Measured prompt budget table + optional profile proposal.

### DIG-10 — Thinking config correctness re-verify on 1.18.4
**Owner**: `@roc_racoon`  
**Do**: After free tier cool / paid tier: confirm OpenCode sends Gemma-legal thinking (`minimal`/`high`, not `LOW`). Diff against Jul 18 debug report.  
**Done when**: One green fat-session or captured request body.

### DIG-11 — Correlate Jul 14 gap
**Owner**: `@researcher`  
**Do**: Why zero Gemma streams on Jul 14? Machine off, model switch, outage, travel? Check other providers’ volume that day.  
**Done when**: One-paragraph explanation.

### DIG-12 — Preserve forensic snapshot
**Owner**: `@sysadmin` / human  
**Do**: Copy or hardlink dated snapshot of:
- first/last 16k error lines
- `opencode models google` output
- auth types (redact keys)
- this report  
**Done when**: Immutable snapshot under `docs/archive/strategy/2026-07-22/snapshots/` (keys redacted).

---

## 11. Do-not-chase list (save agent time)

| Trap | Why not |
|------|---------|
| Re-adding google `whitelist` for Gemma only | Hides Antigravity; prior Kali incident |
| Forcing `apiKey`/`baseURL` on shared google | Breaks Path B |
| Lowering `limit.context` to 12k/16k as “fix” | Architect rejected; doesn’t raise Google free quota; damages paid/OAuth use |
| Assuming titles caused Gemma 16k | Wrong model |
| Blaming only thinkingLevel for post-Jul-15 death | Dominant error is free_tier **input** 16k |
| Expecting free Gemma + full Omega instructions to work post-cliff without billing | Arithmetic fails |

---

## 12. Immediate operational guidance (non-agent)

1. **Cancel** OpenCode retry storms (Esc) when “too hot” appears—retries worsen free windows.  
2. **Do not** use free Gemma as Omega OpenCode workhorse until Tier 1+ billing **or** Google restores usable free TPM.  
3. Use **Antigravity OAuth**, OpenRouter paid, or local for heavy sessions.  
4. Keep free Gemma for **tiny** direct/Cline-slim experiments only.  
5. Preserve `opencode.db` / logs — they are the historical record (~262M session input tokens of Gemma 31B work).

---

## 13. Reproduction commands (forensic)

```bash
# First 16k cliff line
rg -n "free_tier_input_token_count, limit: 16000, model: gemma-4-31b" \
  ~/.local/share/opencode/log/opencode.log | head

# Pre-cliff free RPM metric
rg -n "free_tier_requests, limit: 15, model: gemma-4-31b" \
  ~/.local/share/opencode/log/opencode.log

# Gemma session inventory (redact before sharing)
python3 - <<'PY'
import sqlite3, json
con = sqlite3.connect("file:/home/arcana-novai/.local/share/opencode/opencode.db?mode=ro", uri=True)
print(con.execute(
  "SELECT COUNT(*), SUM(tokens_input), SUM(tokens_output) FROM session WHERE model LIKE '%gemma-4-31b%'"
).fetchone())
PY

# Tiny direct API health (uses auth.json key — do not log key)
# See prior session: generateContent gemma-4-31b-it thinkingLevel MINIMAL → expect 200
```

---

## 14. Config state snapshot (2026-07-22 recovery intent)

| Item | Intended state |
|------|----------------|
| Root `opencode.json` google provider block | Absent / no forced options |
| `.opencode/opencode.json` plugin | `opencode-antigravity-auth@latest` only (no `list`) |
| Gemma variants | `low` → thinkingLevel `minimal`; `high` → `high` (lowercase) |
| Google whitelist | **None** |
| Context caps for free tier | **None** (by Architect order) |
| Auth | API key present; Antigravity OAuth may still need re-login |

*(If drift reappears, re-run `opencode models` and diff configs against this section.)*

---

## 15. Relationship to prior Gemma reports

| Report | Focus | This report adds |
|--------|-------|------------------|
| GEMMA4_OPENCODE_DEBUG_REPORT_20260718 | Thinking/ID/config + 16k as blocker | Full **pre-cliff workhorse proof**, metric evolution RPM→TPM, dated cliff |
| GEMMA4_COMPREHENSIVE / HARDENED / BUG-TO-FEATURE | Product strategy | Forensic **what changed when** + dig tickets |
| Antigravity multi-account CONTEXT | OAuth pool tooling | Separation of Path A free API vs Path B OAuth |

---

## 16. Verdict

**You were not wrong.** Free-tier Gemma 4 31B **was** the workhorse for weeks, with enormous local history still on disk.

**What changed:** On **2026-07-15 ~16:28 UTC**, this environment started receiving Google free-tier **`generate_content_free_tier_input_token_count` limit 16000** for `gemma-4-31b`—a metric **absent** from a month of heavy prior use, when free-tier hits (rare) were **`free_tier_requests` limit 15**. Combined with fat OpenCode Omega context and retry storms, free Gemma ceased to be a viable workhorse.

**Config chaos made recovery harder but did not invent the 16k free input metric.**

**Next value is agent digs DIG-01…DIG-12**, especially live AI Studio quotas, key/project lineage, and public confirmation of Google’s mid-July free-tier change.

---

## 17. Document control

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Author | Grok CLI forensic pass 2026-07-22 |
| Classification | Archive strategy / investigation handoff |
| Next review | After DIG-01 + DIG-03 complete |
| Secrets | **Do not** commit API keys; redact auth dumps |

---

*⬡ OMEGA ⬡ GROK-CLI ⬡ GEMMA4_FREE_TIER_FORENSIC ⬡ 2026-07-22*
