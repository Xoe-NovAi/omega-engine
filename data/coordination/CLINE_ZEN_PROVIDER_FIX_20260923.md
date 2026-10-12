---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "2.0"
document_type: "fix_report"
document_id: "cline-zen-provider-fix-20260923"
title: "Cline — OpenCode Zen 'invalid openai provider options' Root Cause + Fix"
status: "FIX APPLIED + VERIFIED (uncommitted)"
entity: "kali"
channel: "cline"
model: "deepseek-v4.1-flash"
date: "2026-09-23"
branch: "release/debut-v1.6.0"
---

# 🔱 OpenCode Zen — `invalid openai provider options` — Root Cause & Fix

> Every claim below carries a reproduction command. **The command wins over this
document** (M23). Model/agent/provider names are quoted verbatim from disk.

---

## §0 — 60-SECOND READ

1. **Symptom**: every `opencode/<zen-model>` whose catalog `npm` is `@ai-sdk/openai`
   (31 of 110 Zen models: all `gpt-*`, `grok-*`, `muse-spark-*`) died with
   `Error: invalid openai provider options`.
2. **Cause**: NOT the provider block. OpenCode forwards **unknown agent-config keys
directly to the provider as model options** (documented under *Agents → Additional*).
   Our `agent` blocks used `"instructions": ["…kali.md"]` — an **array**. `instructions`
   is a real OpenAI Responses option whose type is **`string`**. Zod rejected the array
   → `AI_InvalidArgumentError` before the request was ever sent.
3. **Blast radius**: all **12** agent blocks carried `instructions` (and the inert key
   `toolProfile`). Because `default_agent: kali`, this hit *every* session on the
   openai-npm Zen models. `@ai-sdk/anthropic` (Claude), `@ai-sdk/google` (Gemini) and
   the default `@ai-sdk/openai-compatible` models were unaffected.
4. **Fix**: delete `instructions` (and the inert `toolProfile`) from all agent blocks,
   and delete the redundant Zen `baseURL` override. Prompts are unaffected — the
   canonical `.opencode/agents/*.md` files already define them and win in the merge.
5. **Verified**: same call now reaches Zen (`Insufficient account funds` = request built
   and sent). Config layer is green.
6. **Second, non-config blocker**: the Zen account has **no funds** and the free models
   are currently **rate-limited**. Neither is fixable from a config file.

---

## §1 — VERIFIED FACT BASE

| Fact | Evidence (run it) |
|---|---|
| OpenCode `1.18.31`, binary `~/.opencode/bin/opencode` | `opencode --version` |
| Zen catalog is pristine (byte-identical to upstream) | diff `~/.cache/opencode/models.json` vs `https://models.dev/api.json` → 110/110 models, 0 npm/api diffs |
| Zen model → SDK package split | 49 `@ai-sdk/openai-compatible` · 22 `@ai-sdk/anthropic` · 8 `@ai-sdk/google` · **31 `@ai-sdk/openai`** |
| Credentials exist and match | `opencode auth list` → 8 providers incl. OpenCode Zen; `auth.json.opencode.key` == env `OPENCODE_API_KEY` |
| Config layers loaded, in order | `grep 'loading path' ~/.local/share/opencode/log/opencode.log` |
| Zen GPT models ARE reachable with zero config | `cd /tmp && HOME=/tmp/newhome opencode run -m opencode/gpt-5.3-codex 'ok'` → `Insufficient account funds` (not a config error) |

**Config sources actually in play** (merge order, later wins):

```
~/.config/opencode/opencode.json                      (global)
<repo>/opencode.json                                  (project)
<repo>/.opencode/opencode.json                        (project dir)
~/.opencode/opencode.json                             (home .opencode dir — LAST, wins)
```

---

## §2 — ROOT CAUSE (exact payload)

`opencode run --print-logs --log-level DEBUG -m opencode/gpt-5.3-codex 'ok'` produced:

```
AI_InvalidArgumentError: invalid openai provider options
(cause: AI_TypeValidationError: Type validation failed:
Value: {"store":false,"promptCacheKey":"ses_…","reasoningEffort":"medium",
        "reasoningSummary":"auto","include":["reasoning.encrypted_content"],
        "instructions":[".opencode/agents/kali.md"],   <-- ARRAY
        "toolProfile":"deploy","forceReasoning":true}.
Error message: [{"expected":"string","code":"invalid_type",
                 "path":["instructions"],
                 "message":"Invalid input: expected string, received array"}]
```

Mechanism:

1. OpenCode docs, *Agents → Additional*: “Any other options you specify in your agent
   configuration will be passed through directly to the provider as model options.”
2. `instructions` is not an OpenCode agent key — it was intended as a prompt-file
   pointer. It therefore fell into that pass-through path.
3. `instructions` **is** a legitimate OpenAI Responses option, typed `string`.
   An array failed zod validation inside `@ai-sdk/openai`.
4. `@ai-sdk/anthropic` / `@ai-sdk/google` / `@ai-sdk/openai-compatible` have no such
   option, so the same agent block was harmless there.

Isolation matrix (each run = a throwaway `HOME` + a reduced config copy; zero repo edits):

| Config under test | Zen `gpt-5.3-codex` |
|---|---|
| no config at all | ✅ reaches API |
| global config incl. Zen `baseURL` override | ✅ reaches API |
| repo config **without** the `provider` block | ❌ invalid openai provider options |
| Zen provider block only | ✅ reaches API |
| `lmstudio` provider block only | ✅ reaches API |
| `.opencode/opencode.json` (google) only | ✅ reaches API |
| full repo config + `--agent build` | ✅ reaches API |
| full repo config + `--agent kali` (default) | ❌ invalid openai provider options |
| agent `kali` **minus** `instructions` | ✅ reaches API |
| agent `kali` minus `toolProfile` / minus `model` / minus `temperature` | ❌ still fails |
| agent `kali` + Claude model (anthropic npm) | ✅ reaches API |
| agent `kali` + Gemini model (google npm) | ✅ reaches API |
| agent `kali` + `big-pickle` (openai-compatible) | ✅ no option error |

---

## §3 — THE FIX (applied 2026-09-23T18:46:45Z)

**`<repo>/opencode.json`** — 15 insertions / 59 deletions (`git diff --stat opencode.json`):

| Change | Count | Why |
|---|---|---|
| removed `"instructions": [...]` from agent blocks | 12 | the fatal pass-through key |
| removed `"toolProfile": "…"` from agent blocks | 12 | inert: **0 occurrences** in the opencode binary; only ever a pass-through hazard |
| removed `provider.opencode.options.baseURL = https://opencode.ai/zen/v1` | 1 | redundant — models.dev already ships `api: https://opencode.ai/zen/v1` for provider `opencode` |

**`~/.config/opencode/opencode.json`** — now just:

```json
{ "$schema": "https://opencode.ai/config.json", "plugin": [] }
```

Removed the `provider` block because:

* `provider.openrouter.baseURL/apiKey` were **mis-nested** (must live under `options`,
  per *Config → Providers → Base URL*) and were silently ignored; and
* the Zen `baseURL` entry was redundant (above).

> ⚠️ `auth.json`'s OpenRouter key and env `OPENROUTER_API_KEY` are **different keys**.
> Before the fix the env key was ignored (mis-nesting). After the fix the behaviour is
> **unchanged** (auth.json still wins). To deliberately prefer the env key, nest it:
> `"openrouter": { "options": { "apiKey": "{env:OPENROUTER_API_KEY}" } }`.

Backups: `opencode.json.bak.zenfix.20260923T184645Z` (repo + `~/.config/opencode/`).
Nothing was committed; the working tree holds the only copy (`git status --short opencode.json` → ` M`).

**Kept deliberately** (not redundancy — no md equivalent): `kali.model`,
`verity.model/hidden/permission`, `slot.steps`, `grok_cli.env`, `provider.lmstudio`.

---

## §4 — VERIFICATION (post-fix)

```bash
cd <repo>
opencode run -m opencode/gpt-5.3-codex 'ok'          # → "Insufficient account funds" (config OK)
opencode run --agent maat -m opencode/gpt-5.3-codex 'ok'   # same, any agent
opencode agent list                                   # 22 agents, unchanged
opencode debug agent kali                             # instructions=0 toolProfile=0, prompt = kali.md body
opencode debug config --pure                          # provider keys: [google, lmstudio]; 0 invalid agent keys
```

After-fix log (the config error is gone; only billing remains):

```
timestamp=… level=ERROR message="stream error" providerID=opencode modelID=gpt-5.3-codex
  agent=kali mode=all error.error="AI_APICallError: Upstream request failed: Insufficient account funds"
```

---

## §5 — REMAINING BLOCKERS (NOT config — do not re-edit configs for these)

| Symptom | Meaning | Action |
|---|---|---|
| `Insufficient account funds` (paid Zen) | account has no credits / payment method | add billing at the Zen console |
| `Rate limit exceeded. Please try again later.` (`big-pickle`, free) | Zen-side throttle on the free tier | retry later; funds lift free-tier limits |
| free `muse-spark-*` (openai npm) also hit the config bug since ≥ 2026-09-19 | historic evidence in the log | now fixed |

**Practical**: free Zen models are the only ones usable today; the config fix unblocks
all 31 `@ai-sdk/openai` models the moment credits exist.

---

## §6 — SECURITY FINDING (P0, unrelated to the bug)

The Zen API key is hardcoded in `~/.bashrc:177` (`export OPENCODE_API_KEY="sk-PVlr…"`),
and `~/.bashrc` is mode **`-rw-rw-r--`** (world-readable). The same key already lives in
`~/.local/share/opencode/auth.json` (identical SHA-256 prefix → the export is redundant).

Recommended: `chmod 600 ~/.bashrc`, delete the export line, **rotate the key** in the Zen
console, re-`/connect`. Also verify `~/.bashrc` never enters a git repo (it does not today).

---

## §7 — CLEANUP QUEUE (found while mapping configs; not touched)

1. **`.opencode/agent/` (singular) holds protocol docs that load as AGENTS** —
   `autonomous_meditation`, `CONVERSATIONAL_SUBAGENT_PROTOCOL`, `NODE_ONBOARDING_PROTOCOL`
   appear in `opencode agent list`. Move them out of any `agent(s)/` directory.
2. **Missing prompt files**: `agent.grok_cli.instructions` pointed at
   `.opencode/agents/grok_cli.md` (absent) and `agent.makali` at `…/plan.md` (absent).
   `grok_cli` therefore has **no prompt**; `makali` is covered by `makali.md`.
3. **Duplicate agent definitions**: `agent` blocks + `.opencode/agents/*.md`. The md wins
   for `description/mode/temperature` (e.g. `makali` resolves to mode `all`, not `primary`).
   Consider keeping definitions in md only, and leaving `opencode.json` for
   model/permission/env overrides.
4. **`~/.opencode/opencode.json` sets `model: opencode/big-pickle` and loads LAST** — it
   overrides the repo's `model: lmstudio/qwen3-4b-thinking` (`opencode debug config`).
   Either intentional (document it) or move it into the repo config.
5. **M23 tool-chain note**: the `exa` MCP returned `401 Invalid API key` and the firecrawl
   MCP tool failed with `No module named 'firecrawl'` during this session. Research was
   completed with the platform web tools instead — no result was synthesised.

---

## §8 — DO NOT

* Do **not** re-add `instructions` to agent blocks. Prompt files belong in
  `.opencode/agents/*.md` (frontmatter + body) or in the agent's `prompt` key.
* Do **not** add a `provider.opencode` block — Zen is built in; a custom `baseURL` buys nothing.
* Do **not** put unknown keys in agent blocks: they are forwarded to the provider and can
  collide with real provider options (the exact failure mode documented here).

---

## §9 — MINIMAL-CONFIG TARGET (what “let OpenCode manage it” looks like)

| Layer | Should contain |
|---|---|
| `~/.local/share/opencode/auth.json` | credentials (written by `/connect`) — the SSOT for keys |
| `~/.config/opencode/opencode.json` | only genuinely global prefs |
| `<repo>/opencode.json` | project: `instructions`, `mcp`, `permission`, `compaction`, `agent`, local `lmstudio` |
| agent prompts | `.opencode/agents/<name>.md` only |
| Zen/GPT/Claude/Gemini model metadata | leave to models.dev + `opencode models` — never hand-maintain |

---

## §10 — REPO-AUDIT CROSS-CHECK (why this was a known exposure class)

`scripts/infra_inventory.py` already carried this component, marked `expected="FIX"`:

```
"Agent-level instructions[] (opencode.json)"
  notes: "Audit FIX (WP-B2): agents carry instructions[], zero prompt:{file:} — GAP-4 exposure class."
  probe: opencode_json_agent_prompts  ->  with_instructions_array / with_prompt_file
```

Post-fix probe reading: `with_instructions_array: 0`, `with_prompt_file: 0`.

* The `instructions[]` half of GAP-4 is **resolved** (the collision risk is gone).
* The probe's `implemented` flag keys on `prompt:` keys and therefore still reads False.
  Prompts are now sourced the OpenCode-native way — `.opencode/agents/*.md` (verified:
  `opencode debug agent kali` shows the full kali.md body as `prompt`). **Follow-up**: teach
  the probe to accept md-defined prompts, and rename/retire the component.

Unrelated pre-existing CI red observed during this session
(`python3 scripts/infra_inventory.py --ci`, exit 1) — **not caused by this fix**:

```
[CI] REGRESSIONS DETECTED:
  - WAKE_STATE decision queue: verdict KEEP -> GHOST
  - WAKE_STATE decision queue: E True -> False
```

`data/coordination/WAKE_STATE.json` does not exist on disk (baseline expects it).

---

## §11 — READING THE GIT DIFF CORRECTLY

`git diff opencode.json` currently shows **more than this fix**. Isolate it with:

```bash
# my delta only (pre-edit working tree -> now)
diff -u opencode.json.bak.zenfix.20260923T184645Z opencode.json
# pre-existing, uncommitted churn (HEAD -> pre-edit working tree)
git show HEAD:opencode.json > /tmp/head.json
diff -u /tmp/head.json opencode.json.bak.zenfix.20260923T184645Z
```

* **This fix (69 lines removed, 14 added):** 1 Zen provider block, 12 `instructions`
  arrays, 12 `toolProfile` keys — every remaining change is comma relocation.
* **Pre-existing, NOT mine:** the working tree already differed from `HEAD` before this
  session (`HEAD` = 320 lines / 9,270 b, working tree = 275 lines / 8,170 b). That earlier
  edit had already dropped the `opencode-antigravity-auth` plugin entry and the hand-written
  `opencode` Zen model definitions with `variants` (`nemotron-3-ultra-free`, `mimo-v2.5-free`,
  `big-pickle`, …). Those deletions are **not** from this session.
* Verified: **no duplicate JSON keys** in the original (`object_pairs_hook` scan) — the
  catalog-like `opencode` block visible in `git diff` was HEAD-only.

---

## §12 — ROUND-2 RESEARCH ADDENDUM (deep dive, same day)

### §12.1 Upstream documentation confirms the mechanism

* **Agents** (opencode.ai/docs/agents) — *“Any other options you specify in your agent
  configuration will be passed through directly to the provider as model options.”* The
  documented agent fields are: `description`, `temperature`, max steps (`steps`),
  `disable`, `prompt`, `model`, `tools` (deprecated), `permission`, `mode`, `hidden`,
  `color`, `top_p` — **there is no `instructions` and no `toolProfile`.**
* **Models** (opencode.ai/docs/models) — model options belong in
  `provider.<id>.models.<model>.options` (and `.variants`), and: *“You can also configure
  these options for any agents that you are using. **The agent config overrides any global
  options here.**”* → agent-level values are the highest-precedence provider options.
* **Models** — *“OpenCode ships with built-in default variants”* (OpenAI:
  none/minimal/low/medium/high/xhigh). The Zen catalog already carries
  `reasoning_options: [{"type":"effort","values":["none","low","medium","high","xhigh"]}]`
  for `gpt-5.3-codex`, so **hand-writing variants/model defs is unnecessary** (user state
  `~/.local/state/opencode/model.json` already holds derived variants for Zen models).
* **Zen** (docs source `packages/web/src/content/docs/zen.mdx`) — GPT family →
  `https://opencode.ai/zen/v1/responses` + `@ai-sdk/openai`; Claude → `/zen/v1/messages` +
  `@ai-sdk/anthropic`. Sign-up step is *“add your billing details”*.

### §12.2 Three empirical probes (isolated `HOME`s, repo untouched)

| Probe | Config under test | Result |
|---|---|---|
| 1 | `agent.kali.options = {"instructions": ["…kali.md"]}` | ❌ `invalid openai provider options` → **agent `options` IS the `providerOptions` channel** |
| 2 | same + `agent.kali.env = {"GROK_CLI_PATH":"grok"}` | ❌ same error; payload = `…,"instructions":[…],"env":{"GROK_CLI_PATH":"grok"},"forceReasoning":true}` → **top-level unknown keys are merged into providerOptions too** |
| 3 | `agent.kali.prompt = "{file:.opencode/agents/kali.md}"` | ✅ no provider-options error; `opencode debug agent kali` resolves 3,657 chars of prompt from the file |

Consequences:

* `instructions` was doubly wrong: not a valid agent field **and** a real OpenAI option name
  (type `string`) — hence the hard failure instead of a silent no-op.
* `toolProfile` and `env` are the *same hazard class* but harmless only by luck (`env`/`toolProfile`
  are not real OpenAI Responses option names). `env` in `agent.grok_cli` is forwarded as a model
  option, so whether it ever set process env vars is **unverified** — do not rely on it.
* Safe ways to bind a prompt file: native `.opencode/agents/<name>.md` (recommended — already in
  place) or `"prompt": "{file:path}"`. Never `instructions`.
* Per-agent provider options are legitimate when namespaced correctly, e.g.
  `agent.<name>.options = {"reasoningEffort":"high"}` — valid keys only.

### §12.3 Zen billing / quota facts (why models still refuse to answer)

* Zen requires **billing details**; usage is charged per request against credits.
* **Free-model quota is separate from the prepaid balance.** Upstream issues:
  #14273 *“Free usage exceeded. Add credits (when using Zen free models)”*,
  #45324 *“Zen balance available but OpenCode says ‘Free usage exceeded, subscribe to Go’”* (open).
  Free Zen models are limited-time promos (Big Pickle, Kimi K2.5 Free, MiniMax M2.5 Free, …).
* **Auto-reload**: balance < $5 → auto-reload $20 (configurable/disable-able); monthly workspace
  and per-member limits are settable.
* Observed on this machine: `opencode/gpt-5.3-codex` → `Insufficient account funds`;
  `opencode/big-pickle` → `Rate limit exceeded. Please try again later.` Both are account/quota
  state, **not config**.
* **Bring your own key** is supported: your own OpenAI/Anthropic keys can be used through Zen
  (billed by the provider, not Zen).

### §12.4 `opencode-go` shares the same API key

Catalog entry: `opencode-go` — name “OpenCode Go”, `api: https://opencode.ai/zen/go/v1`,
`env: ["OPENCODE_API_KEY"]`, `@ai-sdk/openai-compatible`, 41 models. That is why
`opencode auth list` shows OpenCode Zen **and** OpenCode Go for one key. If a Go subscription
is active, `opencode-go/<model>` models are usable with the same credential — otherwise expect
subscription errors there (a Zen key alone grants the Zen catalog, not Go).

### §12.5 Documentation/KB that must be corrected (owner action — NOT edited here)

| Artifact | Why it is now wrong |
|---|---|
| `data/entities/grokster/kb/platforms/opencode/CONFIG_REFERENCE.md:41` | calls `instructions: ["…"]` the **“House pattern”** — this is the bug's origin; `toolProfile` also called a harmless stub |
| `data/entities/grokster/workspace/kb_staging_20260826/opencode/CONFIG_REFERENCE.md` | same staging copy |
| `docs/research/R_OPENCODE_FILEPATH_CONFIG_ARCHITECTURE_20260720.md:333` | instructs *“Keep `instructions: [".opencode/agents/kali.md"]` for frontmatter discovery”* |
| `docs/specs/team_infra/SPEC_B_P1_MECHANISM_HONESTY.md:99` | anchor asserts exactly 12 agents with `.value.instructions` → now 0. Verified **not** CI-enforced (no test/script/Make target references it) |
| `scripts/infra_inventory.py:237-245` | probe `opencode_json_agent_prompts` still keys on `prompt:` and calls the component “Agent-level instructions[]” |

`data/entities/grokster/` is grokster's soul domain — correction deferred to the owning entity
(per `.clinerules`).

### §12.6 Audits that came back clean

* **No generator writes `opencode.json`** — only `scripts/infra_inventory.py` (read),
  `scripts/permission_guard.sh` (read), `scripts/bootstrap_sprint.sh` (grep only),
  `scripts/hydrate_c2_errata.py` (markdown errata only). The fix will not be overwritten.
* **All four `opencode.json` on disk** are free of agent `instructions`/`toolProfile`.
* **No unknown keys in any `.opencode/agents/*.md` frontmatter** — every file uses only
  `description/mode/temperature/permission/steps`.
* **Nothing outside the repo reads `toolProfile`** (`~/.config/opencode`, `~/.opencode`, `~/bin` clean).
* Kilo (`~/.config/kilo/kilo.jsonc`) is a separate fork config with no agents — unaffected.

### §12.7 Safe-pattern cheat sheet (post-fix rulebook)

| Need | Correct field | Never |
|---|---|---|
| agent prompt body | `.opencode/agents/<name>.md` (or `agent.<n>.prompt: "{file:…}"`) | `agent.<n>.instructions` |
| model reasoning/variants | built-in variants from models.dev; `provider.<id>.models.<m>.variants` if overriding | hand-writing whole model defs |
| per-agent provider options | `agent.<n>.options` with **valid** provider keys (`reasoningEffort`, `textVerbosity`, …) | invented keys (`toolProfile`, `env`, `instructions`) |
| credentials | `/connect` → `auth.json` (or the provider's documented env var) | keys in `~/.bashrc` |
| Zen access | `/connect` once; leave `provider.opencode` undefined | custom `baseURL` for `opencode` |

---

## §13 — PASS-2 FIXES APPLIED (2026-09-23T19:45Z, Founder instruction: “just make the fixes”)

| # | File | Change | Verified by |
|---|---|---|---|
| 1 | `opencode.json` | `mcp.exa.headers["x-api-key"]`: `${EXA_API_KEY}` → **`{env:EXA_API_KEY}`** (the only documented interpolation form: *Config → Variables*) | `opencode mcp list` → exa still `✓ connected`; JSON parses |
| 2 | `opencode.json` | `agent.grok_cli`: removed the inert `env` block (proven forwarded as a model option, never applied), added `"prompt": "{file:.opencode/agents/archive/grok_cli.md}"` | `opencode debug agent grok_cli` → prompt **0 → 7,440 chars** |
| 3 | `data/entities/grokster/kb/platforms/opencode/CONFIG_REFERENCE.md:41` | “House pattern” corrected — it was the **source of the outage** and the re-introduction path | line re-read |
| 4 | `data/entities/grokster/workspace/kb_staging_20260826/opencode/CONFIG_REFERENCE.md:41` | same correction (staging copy could be promoted) | line re-read |
| 5 | `docs/research/R_OPENCODE_FILEPATH_CONFIG_ARCHITECTURE_20260720.md:333` | “Keep `instructions: [...]`” → CORRECTED 2026-09-23 | line re-read |
| 6 | `docs/specs/team_infra/SPEC_B_P1_MECHANISM_HONESTY.md` | inserted a **SUPERSEDED** note after the stale 12-agent anchor (verified not CI-enforced) | line re-read |
| 7 | `scripts/infra_inventory.py:244` | component `notes` now records the resolution + an explicit **HAZARD GUARD** (re-adding `instructions[]` re-breaks Zen GPT). Probe logic untouched → no verdict/baseline drift | `python3 -m py_compile` OK |
| 8 | `.env` (gitignored) | commented `EXA_API_KEY` placeholder + where it is consumed | `tail .env` |

Backup: `opencode.json.bak.zenfix2.20260923T194536Z` (plus the round-1 `…zenfix.20260923T184645Z`).

### §13.1 ⚠️ Gitignore finding — some of these fixes are LOCAL-ONLY

`git check-ignore` verdicts:

```
data/coordination/CLINE_ZEN_PROVIDER_FIX_20260923.md   TRACKABLE
docs/research/…R_OPENCODE_FILEPATH….md                 IGNORED   (blanket *.md)
docs/specs/team_infra/SPEC_B_P1_MECHANISM_HONESTY.md   IGNORED
data/entities/grokster/kb/…/CONFIG_REFERENCE.md        IGNORED
data/entities/grokster/workspace/kb_staging_…          IGNORED
.env                                                   IGNORED   (expected)
scripts/infra_inventory.py                             TRACKABLE
opencode.json                                          TRACKABLE
```

So the **durable, committable** guards are: `opencode.json`, `scripts/infra_inventory.py` and this
report. The KB/research/spec corrections fix what agents read **on this machine** but will not
propagate through git unless targeted `!` negations are added to `.gitignore` (a publish-surface
decision — do NOT negate whole trees, the repo is allowlist-driven: `docs/strategy/PUBLIC_ALLOWLIST.txt`).

### §13.2 Not changed (deliberately)

* `.opencode/agent/*.md` protocol docs still load as agents (`autonomous_meditation`,
  `CONVERSATIONAL_SUBAGENT_PROTOCOL`, `NODE_ONBOARDING_PROTOCOL`, `STALLED_SUBAGENT_RECOVERY`) —
  cosmetic `@`-mention noise; moving another entity's files was not warranted.
* `~/.opencode/opencode.json` (`model: opencode/big-pickle`) still wins over the repo default —
  a deliberate user preference, not a defect.
* Nothing committed. Staged-scope command if desired (never `git add -A`):
  `git add opencode.json scripts/infra_inventory.py data/coordination/CLINE_ZEN_PROVIDER_FIX_20260923.md`

### §13.3 Listing artifact (not a regression)

`opencode agent list` reported 22 agents in the baseline capture and 25 after pass 2. Diff:
**added** `slot (all)`, `verity (all)`, `STALLED_SUBAGENT_RECOVERY (all)`; **removed** none. All three
were already defined before pass 2 (two in the config, one as a protocol md) — the baseline capture
was simply cut short by its timeout. No agent was created or lost by this work.

