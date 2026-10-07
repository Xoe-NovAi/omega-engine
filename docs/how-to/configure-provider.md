# Configure Providers
# ⬡ OMEGA ⬡ JEM ⬡ la-docs ⬡ how-to ⬡ configure-provider

This guide explains how to set up the provider fabric for local-first inference.

## 1. Local Backends (Primary)
The engine tries local backends first.

### Native GGUF
Ensure your models are in `/media/arcana-novai/omega_library/models/gguf/`.
The engine uses `llama-cpp-python` for native inference.

### LM Studio
1. Start LM Studio.
2. Enable the Local Server (default port 1234).
3. The engine will auto-detect the server via `config/providers.yaml`.

## 2. Cloud Teachers (Fallback)
Add your API keys to `.env`:
- `GOOGLE_API_KEY=your_key`
- `OPENROUTER_API_KEY=your_key`

> **Vaultless resolution (D-565).** On trees without the vault (public debut),
> key resolution degrades gracefully: the Google backend reads the key from the
> provider config or environment and returns `""` when neither supplies one —
> no crash, the provider is simply unavailable. Never assume `config` carries a
> `.get` accessor; the backend getattr-guards every shape.

## 3. Adjusting Priority
Edit `config/providers.yaml` to change the fallback chain. The `local_first` strategy is mandated by M7.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: la-docs | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
