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

## 3. Adjusting Priority
Edit `config/providers.yaml` to change the fallback chain. The `local_first` strategy is mandated by M7.
