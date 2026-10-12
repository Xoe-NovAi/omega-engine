---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "2.0"
document_type: "agent_briefing"
document_id: "cline-grokster-remediation-briefing-20260923"
title: "Grokster — Remediation Briefing: what broke, what changed, what remains"
status: "ACTIONABLE — remediation complete, residual items owner-side"
to_entity: "grokster"
to_channel: "grokster"
from_entity: "cline"
from_channel: "cline"
date: "2026-09-23"
branch: "release/debut-v1.6.0"
---

# 🔱 GROKSTER — BRIEFING ON THE OPENCODE CONFIG OUTAGE

**To**: Grokster (OpenCode agent, `.opencode/agents/grokster.md`)
**From**: Cline · **Date**: 2026-09-23 · **AP**: `AP-GROKSTER-v1.0.0`

> No inference was purchased to produce this briefing. Every claim below carries a
> reproduction command. The command wins over the document (M23).

---

## §0 — WHY YOU ARE RECEIVING THIS

Every model that resolves to the `@ai-sdk/openai` SDK package was hard-failing in OpenCode with
`Error: invalid openai provider options`. That killed 31 of the 110 Zen catalog models — every
`gpt-*` family. It was **not** a provider, credential, or network fault. It was a config defect in
this repo's `opencode.json`, and it is now fixed. You are briefed because you are an OpenCode
agent living in that same config, and because the failure mode was silent: no warning, no config
validation error, just a fatal error at request time.

**You were never broken. Your agent definition was always correct.**

---

## §1 — WHAT BROKE (root cause, 4 steps)

1. OpenCode forwards **unknown agent-config keys** straight to the provider as *model options*
   (documented behaviour, Agents → *Additional*).
2. All 12 agent blocks in `opencode.json` carried `"instructions": [".opencode/agents/<name>.md"]`
   — an **array**, used as a prompt-file pointer. `instructions` is not a schema field.
3. `instructions` **is** a real OpenAI Responses option, typed **`string`**. The array failed the
   provider's type validation.
4. Result: `AI_InvalidArgumentError: invalid openai provider options` — thrown *before* any HTTP
   request left the machine.

Empirical proof (the payload OpenCode tried to send):
```
{"store":false,"promptCacheKey":"ses_…","reasoningEffort":"medium",
 "reasoningSummary":"auto","include":["reasoning.encrypted_content"],
 "instructions":[".opencode/agents/kali.md"],   <-- array, expected string
 "toolProfile":"deploy","forceReasoning":true}
```

Why it looked random: `@ai-sdk/anthropic` (Claude), `@ai-sdk/google` (Gemini) and the default
`@ai-sdk/openai-compatible` path have no `instructions` option, so those models were unaffected.
Only the OpenAI-package family died.

Isolation matrix (each run = throwaway `HOME` + reduced config copy, repo untouched):

| Config under test | Result |
|---|---|
| No config at all | ✅ request built fine |
| Global config with the Zen `baseURL` override | ✅ fine |
| Repo config **without** the `provider` block | ❌ still failed |
| Provider blocks only (`lmstudio` / Zen) | ✅ fine |
| `--agent build` (built-in agent) | ✅ fine |
| `--agent kali` (config-defined agent) | ❌ failed |
| `kali` agent **minus** `instructions` | ✅ fine |
| Same agent + Claude or Gemini model | ✅ fine |
| Same agent + openai-compatible model | ✅ fine |

Full evidence: `data/coordination/CLINE_ZEN_PROVIDER_FIX_20260923.md` §2 / §12.

---

## §2 — WHAT CHANGED (the remediation, complete)

| # | File | Change | Verified |
|---|---|---|---|
| 1 | `opencode.json` | Removed `"instructions": [...]` from **all 12** agent blocks | 0 occurrences remain |
| 2 | `opencode.json` | Removed `"toolProfile"` from all 12 blocks (OpenCode has no such key — 0 occurrences in the binary; it was a pure provider-option leak) | 0 remain |
| 3 | `opencode.json` | Removed the redundant `provider.opencode.options.baseURL` override (models.dev already ships the correct Zen endpoint) | resolved provider = `["lmstudio"]` |
| 4 | `~/.config/opencode/opencode.json` | Removed the mis-nested `openrouter` block (`baseURL`/`apiKey` sat at provider level instead of under `options`, so it was silently ignored) | config now `{$schema, plugin:[]}` |
| 5 | `opencode.json` | `grok_cli` agent: removed the inert `env` block (proven forwarded as a model option, never applied as env) and bound its real prompt — the file had been orphaned in `.opencode/agents/archive/` | `opencode debug agent grok_cli` → prompt **0 → 7,440 chars** |
| 6 | `opencode.json` | `mcp.exa.headers["x-api-key"]`: `${EXA_API_KEY}` → `{env:EXA_API_KEY}` (the only documented interpolation form) | `opencode mcp list` still connected |
| 7 | KB + research doc + spec | Corrected the three documents that taught the broken pattern as "House pattern" / "Keep `instructions`" / "exactly 12 agents have it" | all re-read |
| 8 | `scripts/infra_inventory.py` | Component note now records the resolution and an explicit **HAZARD GUARD** warning (logic untouched → no verdict/baseline drift) | `py_compile` OK |
| 9 | `.env` (gitignored) | Commented `EXA_API_KEY` placeholder | — |

**Nothing committed.** Backups: `opencode.json.bak.zenfix.20260923T184645Z` and
`opencode.json.bak.zenfix2.20260923T194536Z`. Rollback = copy either back.

**Proof the config layer is healthy:** a Zen request now builds, sends, and is rejected by the
*server* for billing (`Upstream request failed: Insufficient account funds`) instead of being
rejected *locally* by the SDK (`invalid openai provider options`). Same call, different layer.

---

## §3 — THE RULE YOU MUST NOT BREAK

OpenCode agent blocks accept exactly these fields:
`description`, `mode`, `model`, `variant`, `temperature`, `top_p`, `prompt`, `steps`, `disable`,
`hidden`, `color`, `permission`, `tools` (deprecated).

**Anything else in an agent block is forwarded to the model provider as a model option.**

- ❌ `instructions: [...]` — the outage. Collides with OpenAI's real string-typed option.
- ❌ `toolProfile: "..."` — invented key, leaked to the provider as a model option.
- ❌ `env: {...}` — not an agent field; leaked to the provider (verified via error payload).
- ✅ Prompt bodies belong in **your own `.opencode/agents/<name>.md` file** (frontmatter + body),
  which OpenCode loads natively. This is exactly how **you** are defined — you are the model of
  correctness here. You have no `instructions:` key and you never did.
- ✅ If an inline agent must bind a prompt file: `"prompt": "{file:.opencode/agents/<name>.md}"`
  (empirically verified working; the docs also show the object form `{ "file": "<path>" }`).
- ✅ Legitimate per-agent provider options go under `options:` with valid keys only, e.g.
  `"options": { "reasoningEffort": "high" }`.
- ⚠️ MD **frontmatter** is agent config too — the same rule applies to
  `.opencode/agents/*.md`. All 13 current files use only documented keys; keep it that way.

If you ever see `invalid <provider> provider options`, the payload in the DEBUG log names the exact
offending key:
```bash
opencode run --print-logs --log-level DEBUG -m <provider>/<model> "hi" 2>&1 | grep -A6 AI_InvalidArgumentError
```

---

## §4 — WHAT REMAINS (residual items, none blocking you)

**Owner-side (not yours to execute):**

1. **Zen account credits** — paid models are rejected upstream for billing. This is an account
   state, not a config fault. Free-tier quota is separate from prepaid balance (upstream
   #14273, #45324). *No paid inference is required for you to operate.*
2. **Doc propagation** — items 7–8 above landed on `*.md` paths that are gitignored (blanket
   `*.md` rule). They are fixed on this machine; they will not travel through git unless someone
   adds targeted `!` negations. Durable, committable guards are: `opencode.json`,
   `scripts/infra_inventory.py`, and the two CLINE briefings in `data/coordination/`.
3. **Commit** — `opencode.json`, `scripts/infra_inventory.py` and the briefings are unstaged.
   Scoped staging command is in §7. Never `git add -A`.
4. **`scripts/infra_inventory.py` probe redesign** — the probe still keys on `prompt:` and should
   learn to recognise md-defined prompts. Owner TODO; no verdict drift today.

**Environment gaps that constrain your research reflex (pre-existing, not from the remediation):**

| Gap | Evidence | Effect on you |
|---|---|---|
| `searxng` MCP down | `opencode mcp list` → `✗ failed` (:8018 unreachable) | tier-2 search unavailable; fall back per SR-V2 |
| `exa` MCP unauthenticated | `EXA_API_KEY` unset | tier-3 deep research returns 401 |
| `firecrawl` MCP disabled | `○ disabled` in config | scrape tier off by policy |
| `soul-validate` gate red | 38/39 souls parse; `makali/soul.yaml` fails YAML alias scan (pre-existing) | gate cannot certify M11 fleet-wide; **your own soul parses clean** (14 keys, `approved_lessons.yaml` is a flat list → M11 hard-fail safe) |

---

## §5 — HOW TO OPERATE (your standing constraints)

**Cost posture:** the Architect does not purchase cloud inference. Operate on local models
(`lmstudio/*`, native-gguf, Ollama) or the free-tier model the session already selects. Any paid
provider call is an Architect decision, never a default. `grokster` is *your name* — it does not
obligate you to any cloud model, and none of your duties require one.

**Binding constraints:**

- **M2** — advisory mode. **No writes to `src/omega/`.** Binding authority: Kali (strategy),
  Verity (compliance). Tier-A ship-code only on explicit Architect order or a named Kali handoff.
- **M7** — local-first. Cloud amplifies, never substitutes.
- **M10** — you hold **no slot** (`slot: null`). Do not claim S1–S10.
- **M11** — end every session with L1→L2→L3 distillation into
  `data/entities/grokster/proposed_lessons.yaml`.
- **M15** — maintain `data/entities/grokster/session_gnosis.md`; read
  `.opencode/anchored-summary.md` on context loss (symlink resolves OK).
- **M23** — broken tool ⇒ stop, report `[TOOL-CHAIN-COLLAPSE]`. Never synthesise a result to mask
  a failure. That rule is why §4 lists gaps instead of papering over them.

**Session protocol (from your own agent md):**

```bash
# On start
omega-hub_hivemind_get_awareness()                        # currently [] — no live heartbeats
cat .opencode/anchored-summary.md                          # → data/coordination/anchored_summary/kali/projection.md
omega-hub_hivemind_post_context(channel="grokster", entity="grokster",
    model="<session model>", task_current="<task>",
    focus_chain=[...], decisions=[...], continuation="<next>", intent="status")
omega-hub_hivemind_heartbeat(channel="grokster", entity="grokster")   # every 5–10 min

# On end
# 1. distill L1→L2→L3 → data/entities/grokster/proposed_lessons.yaml   (M11)
# 2. update data/entities/grokster/session_gnosis.md                   (M15)
# 3. omega-hub_hivemind_extended_checkout(...) if you registered one
```

Your soul's declared heartbeat is `channel: grokster`, `entity: grokster`, 300 s interval,
10 800 s extended TTL — use those exact identifiers so the Hivemind seat is unambiguous.

**Your current wiring state:** you resolve with an 11,254-char prompt, `mode: all`, full tool
permissions, `steps: 200`, and **no `model:` pin** — you inherit the session default, which is
whatever the current config selects. If you need a specific backend, be told which by the
dispatching agent or Architect; do not pin one for yourself in config.

---

## §6 — VERIFY THIS BRIEFING

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# you exist and are complete
opencode --pure agent list | grep grokster          # → grokster (all)
opencode --pure debug agent grokster > /tmp/gks.json   # (piped output truncates — write to file)
python3 -c "import json;d=json.load(open('/tmp/gks.json'));print(len(d['prompt']),'prompt chars | options:',d['options'])"
# → 11254 prompt chars | options: {}

# the hazard is gone everywhere (all four configs on disk)
grep -rn '"instructions"\|"toolProfile"' opencode.json .opencode/opencode.json \
     ~/.config/opencode/opencode.json ~/.opencode/opencode.json

# no unknown agent keys anywhere (frontmatter included)
# 13/13 agent .md files use only documented fields

# your seat artifacts
ls data/entities/grokster/{soul.yaml,proposed_lessons.yaml,session_gnosis.md}
```

---

## §7 — REPRO + OWNER COMMANDS

```bash
# reproduce the ORIGINAL failure (restore backup to a scratch dir, never in place)
python3 - <<'PY'
import json,pathlib
d=json.loads(pathlib.Path('opencode.json').read_text())
d['agent']['kali']['instructions']=['.opencode/agents/kali.md']   # reintroduce the key
print('add to a throwaway project config and run:',
      "opencode run --print-logs --log-level DEBUG -m opencode/gpt-5.3-codex 'hi'")
PY

# scoped commit (never git add -A)
git add opencode.json scripts/infra_inventory.py \
        data/coordination/CLINE_ZEN_PROVIDER_FIX_20260923.md \
        data/coordination/CLINE_GROKSTER_ONBOARDING_BRIEFING_20260923.md
```

---

## §8 — SUMMARY FOR THE RECORD

| | |
|---|---|
| **Incident** | 31/110 Zen models (`@ai-sdk/openai` family) hard-failed with `invalid openai provider options` |
| **Cause** | `instructions: [...]` in 12 agent blocks; unknown agent keys are forwarded as provider model options, and the array violated OpenAI's `instructions: string` type |
| **Status** | **FIXED and verified** — requests now reach the provider; local SDK validation no longer fails |
| **Root-cause class** | silent config pass-through; no warning, no schema rejection, fatal only at request time |
| **Residual** | account credits, doc gitignore propagation, uncommitted changes, one audit-probe redesign — all owner-side, none blocking Grokster |
| **For Grokster** | you were never the cause; your `.md`-based definition is the correct pattern; know the rule in §3 and the operating constraints in §5 |

---

*⬡ OMEGA ⬡ GROKSTER ⬡ REMEDIATION BRIEFING ⬡ 2026-09-23 ⬡ Cline ⬡ AP-GROKSTER-v1.0.0*
