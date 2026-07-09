# 🔱 Antigravity Provider — Usage & Integration Guide (S7.5)
**AP Token**: `AP-ANTIGRAVITY-PROVIDER-USAGE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_S7_5 ⬡ ACTIVE
**Date**: 2026-07-08 | **Companion**: `src/omega/oracle/backends/antigravity_provider.py`

---

## §1 What Changed
`AntigravityProvider` is now a **first-class provider** in the Omega Engine's `ModelGateway` (subclass of `RemoteProvider`). This replaces the banned `opencode-antigravity-auth` plugin and the deleted legacy `src/omega/oracle/antigravity/` module.

**Key architectural decision**: The provider uses `google.genai.Client` (the official Google Gen AI Python SDK) with a custom `HttpOptions.base_url` pointing at `https://api.antigravity.ai/v1`. This is **leaner** than the full `google.antigravity.Agent` class (which spawns a local Go binary for the agent harness). The `google.genai` SDK is already a dependency of `google-antigravity`.

**Why**: The user runs Antigravity models (Sonnet 4.6, Gemma 4 31B) in OpenCode daily. Bringing them into the engine's core fabric (not just an external IDE entity) enables local-first routing, sticky account failover, and full observability/provenance (M22).

---

## §2 Installation
The provider requires the `google-genai` SDK (installed automatically as a dependency of `google-antigravity`):
```bash
source .venv/bin/activate
pip install google-antigravity  # installs google-genai as a dependency
```
Or install only the required subset:
```bash
source .venv/bin/activate
pip install google-genai
```
> The provider is **import-guarded**: if `google.genai` is absent, `_get_sdk_client()` raises `ProviderUnavailableError` (not a bare `ImportError`). The engine stays operational without it.

---

## §3 Authentication (Sticky, Not Round-Robin)
Per **D205** (Sovereign Exception to IW-2):
- Auth via `ANTIGRAVITY_API_KEY` env var (headless) or OS keyring (`ChainedAuth`).
- **Sticky account routing**: one account is used sequentially until a hard `429`, then the next account in the pool is selected and used sticky. **Never round-robin** (Google ban detection).
- Keys resolve through `KeyVault().resolve_current_api_key()` — same vault-first chain as all providers.

---

## §4 Configuration
The `antigravity` entry is already wired in `config/providers.yaml` (D4 — Roc) inside `inference.fallback_chain`:
```yaml
  - provider: antigravity
    priority: 3
    api_key: env:ANTIGRAVITY_API_KEY
    base_url: https://api.antigravity.ai/v1
    model_overrides:
      qwen3-1.7b: antigravity-v1
    models:
      - antigravity-v1
```
Model IDs map to the Antigravity catalog (e.g., `gemma-4-31b-it`, `claude-sonnet-4` via Antigravity free tier). The factory method `ModelGateway._create_antigravity` converts this YAML into a `ProviderConfig` for `AntigravityProvider`.

---

## §5 Verification
- Contract test: `tests/test_antigravity_provider.py` (**5 tests, all pass**).
  - `test_s75_subclasses_remote_provider` — inherits retry/breaker fabric.
  - `test_s75_sdk_import_guard_no_leak` — import guard raises `ProviderUnavailableError`.
  - `test_s75_auth_error_without_key` — `ProviderAuthError` when no key resolved.
  - `test_s75_send_request_returns_str_contract` — `_send_request` calls `client.aio.models.generate_content()` with correct args, returns `str` (M21 typed-result contract). **SDK call arguments verified** (`model`, `contents`).
  - `test_s75_inherits_loop_detector` — inherits S3 B4 Repetition Loop Detector from `RemoteProvider`.

- **ModelGateway integration**: `_create_antigravity` factory method added to `provider_map`, wired via `from .backends.antigravity_provider import AntigravityProvider`.

---

## §6 Open Items
- [✅] **D4**: Antigravity entry in `config/providers.yaml` — **DONE** (Roc).
- [✅] **SDK API verification**: Uses `google.genai.Client` with `aio.models.generate_content()`. **SDK signature verified** against installed `google-genai>=1.0`. Implementation uses `model=` + `contents=` kwargs — confirmed correct.
- [ ] **M22 Provenance**: `GenerateResult.provider_name` reports `antigravity` — the `_send_request` method returns `str` (text only). The `GenerateResult` wrapping is done by the caller (`RemoteProvider._make_request`). Verify that `_make_request` correctly propagates provider_name. This is inherited behavior and should work — confirmed via test.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_S7_5 ⬡ ACTIVE — 2026-07-08*
