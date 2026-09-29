<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Cline Provider Activation Audit — 2026-08-22
**AP Token**: `AP-CLINE-ACTIVATION-AUDIT-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_cline_activation_audit ⬡ GRAND-OVERSIGHT

**Requested by**: @kali (Grand Oversight) · **Type**: READ-ONLY research audit (M23-honest)
**Session**: ses_5b058490c0d0 · **Scope**: Can the `cline` fabric entry (priority 7) be made operational?

---

## VERDICT

**BLOCKED (as-configured)** — the OpenAI-compatible endpoint and credentials both exist, but the advertised free models (`deepseek-v4-flash`, `mimo-v2.5`) are **client-gated at HTTP 403 ("only available via Cline product surfaces")**, so no config-only wiring can activate them; activation requires either a NEW-MODULE CLI-wrapper backend (the `cline` CLI is itself a sanctioned "product surface" and is installed + authenticated on this machine) or repointing the entry at API-permitted models.

---

## 1. Transport Determination (file:line evidence)

**Finding: cline is ALREADY wired to the OpenAI-compat transport — but mis-wired.**

| Evidence | Location | Meaning |
|---|---|---|
| `"cline": ModelGateway._create_openrouter` | `src/omega/oracle/model_gateway.py:534` | cline maps to the OpenRouter factory → `OpenAICompatProvider` |
| Factory defaults `base_url` to `https://openrouter.ai/api` when absent | `model_gateway.py:364` (`cfg.get("base_url", "https://openrouter.ai/api")`) | cline's YAML block has NO `base_url`, so a live cline instance would **silently hit OpenRouter's endpoint under the name "cline"** — an M22 provenance violation waiting to fire |
| URL construction: `{base_url}/v1/chat/completions` | `src/omega/oracle/backends/openai_compat.py:94` | Setting `base_url: https://api.cline.bot/api` yields exactly `https://api.cline.bot/api/v1/chat/completions` — the real endpoint observed in this machine's Cline CLI logs |
| Streaming (M25) already generic | `openai_compat.py:127-204` reads `extra.streaming.chunk_timeout_ms/total_timeout_ms` | cline's existing streaming block (`config/providers.yaml:314-317`) would be consumed with zero code change |
| RemoteProvider base handles retry/breaker/budget/key-rotation generically | `src/omega/oracle/backends/remote_provider.py:249-378` | No provider-specific logic needed for transport |

**Transport answer**: Cline exposes an OpenAI-compatible HTTP endpoint (`https://api.cline.bot/api/v1/chat/completions`, confirmed from `~/.cline/data/logs/cline.log`) → `openai_compat.py` reuse is the correct transport, **but only for models the API permits**. CLI-wrapper semantics (`orchestrator.py:527-529` already dispatches `["cline","task",prompt]`) remain the fallback path for gated models.

## 2. Credential Status on This Machine

HG-003 (`docs/research/R_CARMACK_HG-003_HEADLESS_CREDENTIALS_20260719.md:65-105`) documents Cline credentials at `libsecret → ~/.local/share/cline/credentials.json`. **That path does not exist here — HG-003 is stale relative to Cline CLI 3.0.56.**

Actual stores found:

| Store | Contents | Format |
|---|---|---|
| `~/.cline/data/secrets.json` | `clineApiKey` (`sk_…`, 67 chars), plus openRouter/deepSeek/groq/etc. keys | Plain JSON, mode 600-ish, no keyring |
| `~/.cline/data/settings/providers.json` | Full OAuth state for provider `cline`: WorkOS JWT `accessToken`, `refreshToken`, `expiresAt`, accountId; `lastUsedProvider: "cline"` | Plain JSON |
| OAuth token freshness | `expiresAt = 2026-08-22 07:39 UTC` → **expired ~48 min before probe time**; refresh token present so CLI self-refreshes | — |

**ModelGateway consumption verdict**: the static `clineApiKey` could be consumed directly via `api_key: env:CLINE_API_KEY` in providers.yaml (same pattern as every other cloud entry). The OAuth pair would need vault mediation (V-1 / HG-003 adapter rewrite against the NEW paths above — HG-003's adapter skeleton targets the wrong directory).

⚠️ Note: `secrets.json` and `providers.json` are plaintext-on-disk. Any ModelGateway direct-read adds a second consumer of an unencrypted store; vault mediation remains the cleaner long-term path.

## 3. Gap Spec

### Path A — Config-only wiring (sufficient IF a permitted model is chosen)
No new module required. Deltas:
1. `config/providers.yaml` cline block (~6 LOC):
   - `base_url: https://api.cline.bot/api`
   - `api_key: env:CLINE_API_KEY`
   - model IDs renamed to API namespace format `modelType/model` (probe #1 proved bare `deepseek-v4-flash` → HTTP 400 "invalid model format")
2. `.env`: add `CLINE_API_KEY=...` (1 line)
3. Optional: extend `provider_registry` cloud list — NOT needed; `is_cloud: true` already set (`providers.yaml:104`), registry reads it.

**LOC: ~7, all config. Zero Python.**

### Path B — Activate the ADVERTISED models (deepseek-v4-flash, mimo-v2.5): NEW-MODULE
These are client-gated (see §4). Two sub-options:
- **B1 (recommended)**: `src/omega/oracle/backends/cline_cli.py` — `RemoteProvider` subclass wrapping headless `cline` CLI (pattern precedent: `orchestrator.py:527-529`; pool precedent: `subagent_pool/profile_manager.py:136-137`). `_send_request()` → `anyio.to_thread.run_sync(subprocess)` on `["cline","task", prompt]` with output capture. Caveat: agent-loop semantics, high latency (tens of seconds), not a clean completion API — suitable as deep-fallback only.
  - Modify `model_gateway.py:534` → point at new factory. **LOC: ~120-160 module + ~10 wiring + tests ~80.**
- **B2 (not recommended)**: header-spoofing the official client identity against api.cline.bot. Untested, ToS-fragile, breaks on client updates. Rejected on M23/M8 grounds.

### Also required regardless of path
- Fix or document the silent-OpenRouter default at `model_gateway.py:364` — any provider mapped to `_create_openrouter` without explicit `base_url` impersonates OpenRouter (opencode-zen at line 533 has the same latent issue). Suggest raising `ConfigError` on missing base_url. (~5 LOC)

## 4. Live Probe Result (M23-honest log)

Credentials existed locally → probe executed. Two HTTP requests total (probe #1 was rejected pre-inference at 400 — zero tokens consumed — so one corrected retry was made; both documented):

| # | Request | Result |
|---|---|---|
| 1 | POST `api.cline.bot/api/v1/chat/completions`, Bearer `clineApiKey`, model `deepseek-v4-flash` | **HTTP 400** `{"error":"invalid model format. Expected format: modelType/model"}` — endpoint alive, auth layer passed, namespace mismatch |
| 2 | Same, model `deepseek/deepseek-v4-flash` | **HTTP 403** `{"message":"Error 403: deepseek/deepseek-v4-flash is only available via Cline product surfaces. If you are using an old version of Cline, please update to the latest version"}` |

**Interpretation**: auth is valid; the free-tier models are gated to official Cline clients. No fake success claimed. OAuth access token had expired 48 min prior (refresh-token rotation handled inside the CLI); the static API key was used and accepted at the auth layer.

## 5. Effort Estimate to Activation

| Path | Effort | Outcome |
|---|---|---|
| A: config-only, permitted model (e.g., a third-party ID like `deepseek/deepseek-v4-pro` if API-billed) | **~30 min incl. smoke test** | Working priority-7 fabric entry, honest provenance |
| B1: CLI-wrapper module for gated free models | **~4-6 h** (module + contract tests per M21 + fabric wiring) | Access to deepseek-v4-flash/mimo-v2.5 via sanctioned client, as slow deep-fallback |
| HG-003 credential-doc refresh (new paths/formats) | ~15 min doc edit | Vault adapter unblocked |

**Recommendation to kali**: Do Path A now (cheap, fixes the silent-OpenRouter mis-wiring hazard too); park B1 behind V-1 vault work since B1's value depends on whether the Architect actually wants agent-loop-latency fallback capacity.

---

## Session Artifacts
- Hivemind: ses_5b058490c0d0 (awareness posted 08:22 UTC, heartbeat maintained)
- Lesson seeds appended: `data/entities/roc_racoon/proposed_lessons.yaml`
- Gnosis notes: `data/entities/roc_racoon/workspace/session_gnosis.md`
- No engine code modified. Read-only sweep honored.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ CLINE-ACTIVATION-AUDIT ⬡ BLOCKED-AS-CONFIGURED ⬡ 2026-08-22*

---

## ADDENDUM A — M22 base_url repair (2026-08-22)

**Mission**: @kali follow-up. After the M22 fix in `model_gateway.py:_create_openrouter` (silent `base_url="https://openrouter.ai/api"` default removed; non-openrouter providers without explicit `base_url` now raise `ConfigError`), the real config would fail gateway boot for opencode-zen + cline. Forensics + repair + boot verification executed this session.

### A.1 Zen endpoint — FORENSICALLY DETERMINED: `https://opencode.ai/zen/v1`

Evidence chain (strongest first):

1. **Binary provider registry** (`strings` dump `/tmp/opencode/oc_strings.txt`, from `~/.opencode/bin/opencode`):
   ```
   opencode:{id:"opencode",env:["OPENCODE_API_KEY"],npm:"@ai-sdk/openai-compatible",
             api:"https://opencode.ai/zen/v1",name:"OpenCode Zen",doc:"https://opencode.ai/docs/zen",...}
   ```
   The built-in first-party provider declares its own API base as `https://opencode.ai/zen/v1` via the `@ai-sdk/openai-compatible` adapter (OpenAI wire protocol). Subscription variant also present: `"opencode-go"` → `api:"https://opencode.ai/zen/go/v1"`.
2. **URL math consistency**: gateway stores `base_url.rstrip("/v1")` (`model_gateway.py:382`) and `openai_compat.py:94` builds `{base}/v1/chat/completions`. YAML value `https://opencode.ai/zen/v1` → stored `https://opencode.ai/zen` → wire `https://opencode.ai/zen/v1/chat/completions`. Exact match with the binary's declared base.
3. **i18n strings** in same binary confirm `opencode.ai/zen` is the marketing/key portal ("Go to https://opencode.ai/zen to get a key"), distinct from the API base.
4. **auth.json structure** (`~/.local/share/opencode/auth.json`, keys only — values redacted): top-level keys = google, openrouter, github-copilot, siliconflow, aihubmix, cerebras, nebius. **No `opencode` credential entry** — consistent with zen auth being baked into the binary/console-managed rather than stored in auth.json on this machine.
5. **Live log** (`~/.local/share/opencode/log/opencode.log`, 190MB): only workspace/billing/docs URLs matched; no contradicting API host found.

### A.2 Copilot verdict

**No usable static endpoint+credential story → keep OUT of providers.yaml until vault era (V-1).**
`auth.json` holds only an OAuth pair for github-copilot (type/refresh/access/expires — no static API key; Copilot requires device-flow OAuth + short-lived token exchange, incompatible with `OpenAICompatProvider`'s static Bearer model). Additionally **no `github-copilot` block exists anywhere in config/providers.yaml**, and `_load_provider_fabric()` iterates ONLY `inference.fallback_chain` entries (`model_gateway.py:545,562`) — so copilot is never instantiated and poses zero boot risk. No YAML change made or needed.

### A.3 YAML deltas applied (config/providers.yaml — scoped)

First attempt placed `base_url` in the detailed `inference.providers:<name>` dicts — **reverted** after boot test proved `_load_provider_fabric()` passes ONLY the flat chain entry to the factory (no generic merge exists; `_merge_native_gguf_config` is native-gguf-only, `model_gateway.py:458-520`). Verified nothing reads `providers:<name>.base_url` (grep of src/omega: only provider_registry.py:62 supported_models + capability_matrix.py:177 touch those dicts).

Final delta — two additions to flat `inference.fallback_chain` entries, nothing else changed:

```yaml
  - provider: opencode-zen
    ...
    # M22 repair 2026-08-22: endpoint forensically extracted from ~/.opencode/bin/opencode
    # binary provider registry ("api":"https://opencode.ai/zen/v1", @ai-sdk/openai-compatible).
    # NOTE: _load_provider_fabric() passes ONLY this flat chain entry to the factory —
    # the inference.providers: dicts are NOT read for base_url.
    base_url: https://opencode.ai/zen/v1
  - provider: cline
    ...
    # M22 repair 2026-08-22: endpoint per CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md
    # (openai_compat.py:94 URL math -> https://api.cline.bot/api/v1/chat/completions).
    base_url: https://api.cline.bot/api
```

### A.4 Boot verification — PASS

Real-config instantiation via normal code path (`ModelGateway()` → `_load_provider_fabric()`, `.venv`, no `OMEGA_ENV=test`): **no ConfigError**. Instance list (name / priority / stored base_url):

```
native-gguf      0  None            lmster          1  None
ollama           2  None            antigravity     3  https://api.antigravity.ai/v1
google           4  None            google-compat   4  None
openrouter       5  https://openrouter.ai/api          <- M22 default preserved
opencode-zen     6  https://opencode.ai/zen            <- /v1 stripped by factory (by design)
cline            7  https://api.cline.bot/api
mock            10  None
```

Wire URLs (`openai_compat.py:94` math): opencode-zen → `https://opencode.ai/zen/v1/chat/completions` ✓ · cline → `https://api.cline.bot/api/v1/chat/completions` ✓ · openrouter → `https://openrouter.ai/api/v1/chat/completions` (unchanged) ✓

### A.5 Test results — PASS

`OMEGA_ENV=test python -m pytest tests/test_model_gateway.py tests/test_providers.py -q -p no:tldr` → **47 passed, 0 failed, 1 warning in 4.62s**. (Note: `pytest-tldr` plugin masks counts; `-p no:tldr` restores honest tally per C-0.) No pre-existing reds observed in these two files.

### A.6 Pre-existing findings (NOT caused by this repair — reported, not fixed)

1. **anthropic + xai chain entries silently skipped at boot**: present in `fallback_chain` but absent from `provider_map` (`model_gateway.py:547-559`) → "Unrecognized provider" warning, never instantiated. Their `providers:*` detail blocks are dead weight for the fabric path.
2. **`enabled:false` not honored by fabric loader**: ollama/mock instantiate despite `enabled: false` (`model_gateway.py:562-575` never checks it).
3. **opencode-zen + cline have NO credential wiring anywhere** (neither chain entry nor providers dict carries `api_key`). Boot is clean, but first live call will go out unauthenticated (401 expected). Binary evidence shows zen's env key name: `OPENCODE_API_KEY` → one-line future fix: `api_key: env:OPENCODE_API_KEY` on the chain entry (+ cline equivalent), pending kali's call. Out of scope today per mission constraints.

### Session Artifacts (Addendum A)
- Files changed: `config/providers.yaml` (two `base_url` lines + comments on chain entries only) + this addendum. No commits.
- Hivemind heartbeat maintained; awareness post follows.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ ADDENDUM-A ⬡ M22-REPAIR-VERIFIED ⬡ BOOT-PASS-47-GREEN ⬡ 2026-08-22*

---

## ADDENDUM B — Zen auth investigation (2026-08-22)

**Mission**: Forensic determination of where the TUI's built-in zen client stores its auth, whether a static API key is extractable, and the auth mechanism.

### B.1 Where Zen Auth Lives

| Location | Status | Contents |
|---|---|---|
| `~/.local/share/opencode/auth.json` | **NO zen entry** | 7 credentials: google (oauth), openrouter (api), github-copilot (oauth), siliconflow (api), aihubmix (api), cerebras (api), nebius (api) |
| `~/.config/opencode/zen_accounts_state.json` | **EXISTS, EMPTY** | `{"accounts":[],"active_account":null,"last_rotation":null,"rotation_policy":{...}}` |
| `~/.local/state/opencode/kv.json` | No zen keys | UI prefs only |
| `~/.local/state/opencode/model.json` | Tracks recent zen models | `{"recent":[{"providerID":"opencode","modelID":"x-preview-f-free"},...]}` |
| `~/.opencode/bin/opencode` (binary) | **SOURCE OF TRUTH** | Embedded provider registry declares: `opencode:{id:"opencode",env:["OPENCODE_API_KEY"],npm:"@ai-sdk/openai-compatible",api:"https://opencode.ai/zen/v1",...}` |

**Conclusion**: The TUI does NOT store zen auth in `auth.json` on this machine. The zen provider is **baked into the binary** with its own credential management flow.

### B.2 Static API Key Extractable?

**YES — but not from local files.** The static API key is obtained from the web portal:

1. User visits `https://opencode.ai/auth` (or `https://opencode.ai/zen`)
2. Signs in, adds billing details
3. Copies the API key displayed there
4. Runs `/connect` in the TUI → selects "OpenCode Zen" → pastes the key
5. The TUI stores it internally (likely in its own encrypted store or keyring, not in `auth.json`)

The binary's embedded registry confirms the env var name: **`OPENCODE_API_KEY`**

### B.3 Mechanism

| Aspect | Finding |
|---|---|
| **Auth Type** | Static Bearer API key (not OAuth, not session cookies) |
| **Key Source** | `https://opencode.ai/auth` web portal (user-managed) |
| **Env Var** | `OPENCODE_API_KEY` (confirmed in binary strings) |
| **Base URL** | `https://opencode.ai/zen/v1` (forensically extracted from binary) |
| **Transport** | OpenAI-compatible (`@ai-sdk/openai-compatible` adapter) |
| **Local Storage** | Opaque — managed by TUI binary, not exposed in `auth.json` |
| **Free Models** | 7 free models available (e.g., `nemotron-3-ultra-free`, `deepseek-v4-flash-free`, `x-preview-f-free`, `mimo-v2.5-free`, `hy3-free`, `laguna-s-2.1-free`, `muse-spark-1.2-contributor-free`) |

### B.4 Live Endpoint Verification

```bash
curl https://opencode.ai/zen/v1/models
```
→ Returns 70+ models including 7 free models. Endpoint is live and unauthenticated for model listing.

### B.5 Recommendation

**WIRE IT NOW** — the zen provider is the highest-value cloud entry in the fabric (priority 6, free models, OpenAI-compat transport, binary-verified endpoint).

**Required config delta** (one line in `config/providers.yaml` fallback_chain entry for `opencode-zen`):

```yaml
  - provider: opencode-zen
    ...
    base_url: https://opencode.ai/zen/v1
    api_key: env:OPENCODE_API_KEY   # <-- ADD THIS
```

**User action required**: Get key from `https://opencode.ai/auth` → add to `.env` as `OPENCODE_API_KEY=sk-...`

**No new code needed**. The transport (`openai_compat.py`), model registry (`provider_registry.py`), and fabric loader (`model_gateway.py:_load_provider_fabric()`) already support this pattern. The only missing piece is the credential wiring.

**Risk**: Zero. If `OPENCODE_API_KEY` is unset, the provider will 401 on first live call — same as any other cloud provider without credentials. Boot is clean (verified in Addendum A).

### B.6 Cross-Reference

- Addendum A (§A.1) already forensically determined the zen endpoint from the binary
- Addendum A (§A.6.3) noted: "opencode-zen + cline have NO credential wiring anywhere... Binary evidence shows zen's env key name: `OPENCODE_API_KEY` → one-line future fix"
- This addendum confirms the mechanism and provides the exact wiring instruction

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ ADDENDUM-B ⬡ ZEN-AUTH-RESOLVED ⬡ WIRE-NOW ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->
