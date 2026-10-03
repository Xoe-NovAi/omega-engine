# Quick Start — Omega Engine

Get running in under 5 minutes. No cloud keys needed.

---

## Prerequisites

- **Linux** (Ubuntu 24.04+ or equivalent)
- **Python 3.12+**
- **4GB RAM** minimum (14GB recommended)
- **~2GB disk** (engine + model)
- **x86-64 CPU with AVX2** (most modern CPUs)

---

## Install

```bash
# Clone the repo
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine

# Run the one-click installer
./scripts/install.sh
```

The installer will:
1. Create a virtual environment
2. Install dependencies (llama-cpp-python, etc.)
3. Download Qwen3-1.7B (~1.67GB) for local inference
4. Verify the install with `omega talk "hello"`

---

## Use

```bash
# Activate the environment
source .venv/bin/activate

# Talk to your local AI
omega talk "hello"

# List available entities
omega list-entities

# Summon a specific entity
omega summon ma'at "check the system"

# Check available backends
omega backends
```

---

## Optional: Second Local Backend (Ollama)

```bash
# Install Ollama and pull a model (no cloud account needed)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3:1.7b

# Ollama is enabled by default in config/providers.yaml
```

---

## Optional: Cloud Fallbacks

Local inference works out of the box. If you want cloud fallbacks:

```bash
# Add to .env
echo "GOOGLE_API_KEY=your_key_here" >> .env
echo "OPENROUTER_API_KEY=your_key_here" >> .env
```

Cloud providers are **never called unless local inference fails**.

---

## What Just Happened?

You now have a sovereign AI runtime running entirely on your machine:

- **No data leaves your computer** (unless you opt in to cloud)
- **No API keys required** for basic operation
- **No telemetry** — zero phone-home

The engine uses a local Qwen3-1.7B model via llama-cpp-python. It's smaller than frontier cloud models, but it's **yours**.

---

## Troubleshooting

**Install fails on `pip install`**: Make sure you have `python3-dev` and a C compiler:
```bash
sudo apt install python3-dev build-essential
```

**Model download is slow**: The model is ~1.67GB. On slow connections, you can download it manually:
```bash
# Using HuggingFace CLI
pip install huggingface_hub
hf download lmstudio-community/Qwen3-1.7B-GGUF Qwen3-1.7B-Q6_K.gguf --local-dir models/
```

**`omega` command not found**: Make sure the venv is activated:
```bash
source .venv/bin/activate
```

---

## Next Steps

- Read the [README](README.md) for architecture details
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Review [SECURITY.md](SECURITY.md) for vulnerability reporting

---

*⬡ OMEGA ⬡ QUICKSTART ⬡ v1.6.0-alpha ⬡ 2026-10-03*