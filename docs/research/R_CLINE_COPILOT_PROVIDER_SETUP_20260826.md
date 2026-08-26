# 🔱 R_CLINE_COPILOT_PROVIDER_SETUP_20260826
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_provider_setup ⬡ CLINE+COPILOT→OPENCODE

**Mission**: Determine how to make Cline-served and Copilot-served models selectable in
OpenCode's model picker, honoring house rules from the config remediation (clean names,
flat variant schemas, no npm downgrades of builtins). Research only — zero config writes.
**Confidence tags**: 🟢 HIGH · 🟡 MEDIUM · 🔴 LOW/UNVERIFIED (M23-flagged)

---

## EXECUTIVE SUMMARY

| Provider | Verdict | Path |
|---|---|---|
| **GitHub Copilot** | ✅ **SUPPORTED — ALREADY BUILT IN, ALREADY AUTHED HERE** | Zero-config: builtin `github-copilot` provider ships in anomalyco/opencode 1.18.x with OAuth device flow; `auth.json` on this machine already holds a valid `github-copilot` oauth credential. Add NOTHING to config (house rule: no overrides of builtin providers). |
| **Cline** | ⚠️ **SUPPORTED TRANSPORT / GATED MODELS** | Official OpenAI-compatible gateway exists (`https://api.cline.bot/api/v1`) and accepts static API keys — but our own live probe (2026-08-22) proved the advertised free models incl. **DeepSeek V4 Flash are client-gated (HTTP 403)**. Config-only wiring works ONLY for API-permitted models; D-557's DeepSeek-through-Cline needs the CLI-wrapper path or stays blocked. |

**Key strategic finding**: The Architect's two asks sit at opposite ends of the effort
spectrum. Copilot is a *zero-delta* activation (auth exists; picker populates itself).
Cline is a *one-block* config addition whose headline model (deepseek-v4-flash, D-557)
is exactly the one Cline gates hardest. Plan accordingly.

---

## §1 GITHUB COPILOT → OPENCODE

### 1.1 Support status: FIRST-CLASS BUILTIN 🟢 HIGH

Copilot is not a community-plugin affair — it ships inside anomalyco/opencode core:

- Provider id `github-copilot`, auth plugin at
  `packages/opencode/src/plugin/github-copilot/copilot.ts` (verified on dev branch):
  registers an OAuth device-flow method, dynamically fetches the model list from the
  Copilot API on auth, rewrites model API URLs to `https://api.githubcopilot.com`, and
  pins `npm: "@ai-sdk/github-copilot"` internally.
- A second builtin provider id `github-copilot-enterprise` exists with identical
  transport and its own auth slot — usable as a **second account / isolation slot**
  without any plugin (exploited by cavanaug/opencode-copilot-vscode).
- Sources: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/plugin/github-copilot/copilot.ts ;
  https://gist.github.com/dymoo/54fb6cf021dedc254613946ec9527c46 (source-level walkthrough);
  https://github.com/cavanaug/opencode-copilot-vscode (README architecture section).

**Local state** 🟢 HIGH: `~/.local/share/opencode/auth.json` already contains a
`github-copilot` entry (`type: oauth`, refresh+access+expires). Credentials exist; the
provider should already appear in `/models` once auth is valid. If it doesn't:
`opencode auth login` → "Login with GitHub Copilot" → device flow at
`github.com/login/device`.

### 1.2 Underlying API & auth mechanics 🟢 HIGH

| Aspect | Value |
|---|---|
| OAuth | GitHub device flow (RFC 8628), client_id `Ov23li8tweQw6odWQebz` (opencode's own OAuth App) |
| Token | `gho_…` bearer stored in auth.json (`refresh` field); no separate refresh flow — re-login on expiry |
| Inference endpoint | `https://api.githubcopilot.com` (enterprise variant: `copilot-api.<ghe-domain>`) |
| SDK | `@ai-sdk/github-copilot`; GPT-5.x routed to `/v1/responses`, older to `/chat/completions` |
| Model list | Fetched LIVE from Copilot API per auth — picker self-populates; no hand-listing needed or wanted |
| Utility models | Plugin silently routes small_model/title-gen to Copilot utility models not shown in picker |

Caveat 🔴→🟡: #19338 reported preview models failing because the raw OAuth token was sent
instead of exchanging for a Copilot session token via `/copilot_internal/v2/token`
(closed/fixed Apr 2026). If a premium/preview model 400s with `model_not_supported`,
update binary before debugging config.

### 1.3 Rate limits & ToS reality check 🟢 HIGH (limits) / 🟡 MEDIUM (ToS text)

- Since **June 1 2026**, premium-request units were replaced by **GitHub AI Credits**
  ($0.01/credit), metered per input/output/cached tokens. Agentic CLI use burns credits
  fast — opencode's own issue tracker documents "premium request burning" as a chronic
  complaint (#8030, #8067 — synthetic messages misclassified as paid tier; partially fixed).
- Per-model limits are **intentionally undisclosed**; errors cite ToS. Community consensus:
  third-party clients draw from the SAME quota pool as VS Code — no separate allocation.
- Known breakage class: **Auto-only plans (Copilot Free/Student since Jun 24 2026) yield
  "Provider not found"** because the API returns no model list (#34644). Any of our ~8
  accounts on Auto-only plans are USELESS through this path.
- ToS posture 🟡: using Copilot through opencode is widespread and tolerated (GitHub
  staff respond to related discussions with tuning advice, not bans), but it remains a
  reverse-engineered internal API — no entitlement guarantee. 8-account rotation to
  aggregate quota is the pattern most likely to trip abuse detection; see 1.4.
- Sources: https://rottenwifi.com/github-copilots-new-limits-and-premium-ai-charges-explained-2025-2026/ ;
  https://github.com/orgs/community/discussions/189990 ; #15243 (architecture critique of
  rate-limit pain); #34644.

### 1.4 Multi-account feasibility (~8 accounts) 🟡 MEDIUM

Mechanics: auth.json is keyed by provider id → builtin gives exactly **2 slots**
(`github-copilot`, `github-copilot-enterprise`). Beyond that:

| Approach | Verdict |
|---|---|
| 2 accounts via the two builtin ids | ✅ Works today, zero plugins, complete isolation (cavanaug pattern) |
| N>2 via custom auth plugins each registering a distinct provider id (copy of copilot.ts with renamed id) | 🟡 Feasible (JosXa gist demonstrates custom-id Copilot plugin) but each is bespoke code we'd maintain against a moving internal API |
| N instances with separate `OPENCODE_CONFIG_DIR` + separate data dirs | 🟡 Heavyweight; multiplies sessions/plugins/auth stores |
| Automatic rotation on 429 | ❌ Nothing builtin; would be custom tooling touching auth.json mid-flight — fragile, and the highest ban-risk pattern |

**Recommendation**: activate 2 accounts now (builtin slots); treat 8-account rotation as
a V-1-vault-era project requiring its own design review. Aligns with D-563's spirit
(accounts = resilience, not parallelism).

### 1.5 Config block: NONE (deliberately)

House rule "no npm downgrades of builtin providers" applies maximally here: the builtin
plugin fetches models live, handles Responses-API routing, utility-model offload, and
zero-cost accounting. Any `provider.github-copilot` block in our configs would override
and degrade it. **The correct config delta for Copilot is the empty set** — activation is
purely `opencode auth login`. Optional non-degrading touches only (see §3.1).

---

## §2 CLINE → OPENCODE

### 2.1 VERDICT FIRST 🟢 HIGH

**Supported — with a critical asterisk.** Cline operates an official, documented,
OpenAI-compatible API gateway (`https://api.cline.bot/api/v1`, Bearer-key auth, keys from
app.cline.bot → Settings → API Keys). Any OpenCode config can consume it as a custom
provider — this is a GENUINE custom endpoint (same class as lmstudio/ollama), so the
house "no npm downgrades" rule is not violated; `@ai-sdk/openai-compatible` is the
correct and only adapter here.

**The asterisk**: our own live probe (CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md, §4)
proved that Cline's advertised free models — **including D-557's
`deepseek/deepseek-v4-flash`** — are **client-gated**: raw API calls return
`HTTP 403: only available via Cline product surfaces`. The endpoint, auth, and model-id
namespace all worked (probe #1 got a 400 format error = auth layer passed); the gate is
per-model.

Sources:
- https://docs.cline.bot/api/overview (gateway exists, OpenAI-compatible) 🟢
- https://docs.cline.bot/api/authentication (API keys vs account tokens; curl/OpenAI-SDK examples) 🟢
- https://docs.cline.bot/api/sdk-examples ("any tool that works with OpenAI also works with the Cline API") 🟢
- Local: `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` (live 403 probe) 🟢

### 2.2 What this means per model class

| Model | Via api.cline.bot from OpenCode | Evidence |
|---|---|---|
| `deepseek/deepseek-v4-flash` (D-557 primary) | 🔴 **BLOCKED (403 client-gate)** as of 2026-08-22 probe | house audit §4 |
| `mimo-v2.5` family | 🔴 Same gate expected (advertised-free models are the gated class) 🟡 inference | audit verdict |
| API-billed third-party models (e.g. `anthropic/claude-sonnet-4-6`, `deepseek/deepseek-v4-pro`) | 🟡 Likely permitted (usage-billed via ClinePass/credits) — NOT yet probed live; docs show them as canonical examples | docs.cline.bot examples use `anthropic/claude-sonnet-4-6`; cline.bot/models/deepseek-v4-flash markets "Cline (usage-billing) or ClinePass" |
| Anything, via `cline` CLI wrapper | ✅ Sanctioned product surface — but agent-loop semantics, tens-of-seconds latency; deep-fallback only | audit Path B1 |

**D-557 impact**: "Cline DeepSeek V4 Flash = 1M ctx primary surgical tool" is achievable
today ONLY through the `cline` CLI (installed + authenticated on this machine), not
through OpenCode's picker. The 1M context figure itself is confirmed for DeepSeek V4
Flash generally (https://github.com/cline/cline/discussions/10387 — requests 1M ctx +
reasoning_effort high/max for v4 endpoints). Whether the gate has lifted since Aug 22 is
a 30-second re-probe — listed in §5 unknowns.

### 2.3 No existing OpenCode↔Cline integration plugin 🟢 HIGH (absence)

No OpenCode provider plugin for Cline exists in the anomalyco/opencode ecosystem or npm
(searches across plugin registries, GitHub, npm returned none). None is needed: the
gateway is plain OpenAI-compatible, which is exactly what OpenCode's custom-provider
mechanism consumes natively. LiteLLM-style bridges are unnecessary indirection here.

### 2.4 Endpoint shape & config math 🟢 HIGH

- Wire endpoint: `POST https://api.cline.bot/api/v1/chat/completions`
- Model id namespace: **`modelType/model`** (e.g. `deepseek/deepseek-v4-flash`,
  `anthropic/claude-sonnet-4-6`) — bare ids rejected with HTTP 400 (house probe #1).
- Auth: `Authorization: Bearer $CLINE_API_KEY`. Static key exists on this machine at
  `~/.cline/data/secrets.json` (`clineApiKey`) per house audit §2 — extract to `.env`
  rather than letting two tools read the plaintext store directly.
- Optional headers: `HTTP-Referer`, `X-Title` for usage tracking (docs).

---

## §3 READY-TO-PASTE CONFIG BLOCKS

### 3.1 Copilot — nothing to paste (activation is auth-only)

```bash
# ONLY step needed (credential already present on this machine; run only if picker lacks copilot):
opencode auth login          # → "Login with GitHub Copilot" → device flow
opencode models github-copilot   # verify picker population
```

Optional second account via the second builtin slot (no plugin, complete isolation):

```bash
# cavanaug pattern without their plugin: authenticate github-copilot-enterprise directly.
# NOTE 🟡: builtin enterprise-slot login UI may expect a GHE URL; if the TUI forces
# enterprise deployment selection, choose "GitHub.com". If the builtin path refuses,
# fall back to the cavanaug file-plugin for slot 2.
```

House-rule compliance: no provider block added → builtin live model list, native SDK,
clean names guaranteed by upstream catalog. ✅

### 3.2 Cline — one custom provider block (project `opencode.json`)

> ⚠️ **CORRECTED 2026-08-26 (later same-day research — see R_GAP_CLOSURE_SWEEP D2 + R_CLINE_DIRECT_API_DEEP_MINE §C/§D.3):**
> 1. **DROP the `anthropic/claude-sonnet-4-6` entry below** — third-party validation found anthropic/* NOT actually served despite docs listing them.
> 2. **deepseek output cap corrected**: validated table says **1M ctx / 384K output**, not the 131072 estimate below.
> 3. **Free-tier gate is OFFICIAL POLICY** (free-models page + ToS) — deepseek-v4-flash free id stays blocked; the sanctioned direct-API path is ClinePass `cline-pass/deepseek-v4-flash` ($9.99/mo, hyphenated namespace).
> The block below is preserved as originally researched; apply corrections before any paste.

```jsonc
// ADD to project opencode.json → "provider" (merge-safe: "cline" id unused in TUI configs)
// House rules: clean names ✓ · flat variants ✓ · genuine custom endpoint (not a builtin downgrade) ✓
"cline": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Cline",
  "options": {
    "baseURL": "https://api.cline.bot/api/v1",
    "apiKey": "{env:CLINE_API_KEY}"
  },
  "models": {
    "deepseek/deepseek-v4-flash": {
      "name": "DeepSeek V4 Flash",
      "limit": { "context": 1048576, "output": 131072 },
      "reasoning": true,
      "variants": {
        "high": { "reasoningEffort": "high" },
        "max":  { "reasoningEffort": "max" }
      }
    },
    "anthropic/claude-sonnet-4-6": {
      "name": "Claude Sonnet 4.6",
      "limit": { "context": 200000, "output": 64000 }
    }
  }
}
```

Plus `.env`: `CLINE_API_KEY=sk_…` (extract from `~/.cline/data/secrets.json` once; do not
point tools at the plaintext store).

**Confidence annotations**:
- Block shape / baseURL / key handling: 🟢 HIGH (docs.cline.bot/api/* + house probe).
- deepseek limits (1M ctx): 🟡 MEDIUM — 1M confirmed as DeepSeek-native and requested for
  Cline's v4 endpoints (#10387); Cline-side enforced cap unverified. Output 131072 is an
  estimate 🔴 — verify against `/api/v1/models` listing before trusting.
- `variants` with flat `reasoningEffort` through `@ai-sdk/openai-compatible`: 🟡 MEDIUM —
  adapter maps it to OpenAI-style `reasoning_effort`; whether api.cline.bot honors the
  param for deepseek is UNVERIFIED (#10387 shows raw-API usage of reasoning_effort, so
  plausible). If variants render but have no effect, drop them rather than ship dead knobs.
- **deepseek-v4-flash entry will 403 if the Aug-22 gate still stands** — RE-PROBE FIRST
  (§5 U1); if gated, ship the block WITHOUT that model and keep D-557 on the CLI-wrapper
  track.

---

## §4 SEQUENCING vs REMEDIATION PLAN (F0–F7)

**Recommendation: BOTH additions go AFTER F7**, as a separate session ("Phase P1").

Rationale:
1. The remediation window's verification protocol depends on single-variable changes;
   adding two new providers mid-window contaminates every "did the picker change because
   of my edit?" check. 🟢
2. Copilot needs ZERO config change — nothing to sequence. Its activation (auth refresh)
   can happen any time without touching the remediation surface. 🟢
3. Cline's block touches project `opencode.json`, which F2/F3/F4 also edit. Adding it
   after F7 means its first diff review isn't tangled with depollution diffs, and the
   dependent-inventory rule from R_CONFIG_REMEDIATION_PREEXEC_REVIEW §2 applies cleanly
   (new ids → add to inventory at introduction time). 🟢
4. Exception: the **CLINE_API_KEY extraction to `.env`** and the **gate re-probe** are
   read-only/external and may run in parallel with F0–F7 safely. 🟢

Post-F7 checklist for Phase P1: re-probe gate → paste block → picker inspect (clean
names?) → one smoke call per model → record binary+plugin stamps per freeze protocol.

---

## §5 SOURCE INDEX & RESIDUAL UNKNOWNS

### Sources
- https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/plugin/github-copilot/copilot.ts — builtin Copilot provider source 🟢
- https://gist.github.com/dymoo/54fb6cf021dedc254613946ec9527c46 — Copilot/Codex auth internals walkthrough 🟢
- https://github.com/cavanaug/opencode-copilot-vscode — VSCode-client-id variant + auth isolation pattern 🟢
- https://www.npmjs.com/package/opencode-copilot-auth — community npm auth plugin (thdxr), v0.0.12, ~7mo old 🟢 (exists; not needed given builtin)
- https://gist.github.com/JosXa/ab2224a6134917e0dbf31bd08ce92104 — custom-id Copilot plugin (GHE + GPT-5.3) 🟢
- https://github.com/anomalyco/opencode/issues/19338 — preview-model token-exchange bug (fixed) 🟢
- https://github.com/anomalyco/opencode/issues/34644 — Auto-only plans → provider absent 🟢
- https://github.com/anomalyco/opencode/issues/8030 , /issues/8067 , /issues/15243 — agentic quota burn saga 🟢
- https://github.com/orgs/community/discussions/189990 — undisclosed limits, ToS-citing errors 🟢
- https://rottenwifi.com/github-copilots-new-limits-and-premium-ai-charges-explained-2025-2026/ — AI Credits (Jun 2026) system 🟡
- https://docs.cline.bot/api/overview , /api/authentication , /api/sdk-examples — Cline gateway docs 🟢
- https://github.com/cline/cline/discussions/10387 — DeepSeek V4 endpoints, 1M ctx, reasoning_effort 🟢
- https://cline.bot/models/deepseek-v4-flash — availability via usage-billing/ClinePass 🟢
- Local: `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` (live 403 probe,
  credential paths, endpoint math) 🟢; `auth.json` key inventory 🟢; `config/providers.yaml`
  fabric entries 🟢.

### Residual unknowns (M23)

| ID | Unknown | Resolution path |
|---|---|---|
| U1 | Has the Cline client-gate on `deepseek/deepseek-v4-flash` lifted since 2026-08-22? | 30-second curl re-probe with existing key (pre-P1) |
| U2 | Cline-enforced output cap for deepseek-v4-flash (block guesses 131072) | `GET api.cline.bot/api/v1/models` authenticated listing |
| U3 | Whether api.cline.bot honors `reasoning_effort` (flat variant) for deepseek | one smoke call per variant post-P1 |
| U4 | Whether builtin `github-copilot-enterprise` slot accepts github.com (non-GHE) device login on 1.18.x without the cavanaug plugin | try `opencode auth login`; fallback = file-plugin |
| U5 | Health/plan-type of our ~8 Copilot accounts (Auto-only plans are dead ends per #34644) | manual check per account at github.com/settings/copilot |
| U6 | Current Copilot AI-Credit burn rate for opencode-style agentic loops post-June-2026 billing change | empirical: instrument one session, read usage dashboard |

---
*⬡ OMEGA ⬡ JEM ⬡ PROVIDER-SETUP ⬡ COPILOT-ZERO-DELTA / CLINE-GATED ⬡ 2026-08-26*
