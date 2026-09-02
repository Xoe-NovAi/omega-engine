<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# ❓ Omega Engine — Frequently Asked Questions

> Common questions about the Omega Engine sovereign AI runtime.

---

## General

### What is the Omega Engine?

The Omega Engine is a **sovereign AI runtime** — software that runs AI models entirely on your hardware, with zero cloud dependency. It includes an agent orchestration layer, persistent memory, document processing, and a sovereign WAD protocol for data management.

### Who is the Omega Engine for?

- **Privacy-conscious users** who want AI without sending data to the cloud
- **Developers** building local-first AI applications
- **Researchers** who need reproducible, auditable AI infrastructure
- **Organizations** with data sovereignty requirements
- **Hobbyists** who want to run models on their own hardware

### Is the Omega Engine free?

Yes. The Omega Engine is released under the **Apache 2.0** license. You can use it, modify it, and distribute it freely, including for commercial purposes. See [LICENSE](LICENSE) for details.

### How is this different from ChatGPT, Claude, or other cloud AI?

| Feature | Cloud AI | Omega Engine |
|---------|----------|--------------|
| Data location | Vendor's servers | Your hardware |
| Internet required | Yes | No |
| Source code | Proprietary | Open source |
| Cost | Subscription | Free (you own the hardware) |
| Customization | Limited | Full |
| Telemetry | Yes | Zero |
| Vendor lock-in | High | None |

---

## Installation

### What are the system requirements?

**Minimum**:
- Python 3.12 or 3.13
- 8 GB RAM (for 1.7B-4B models)
- 10 GB disk space

**Recommended**:
- 16 GB RAM (for 7B-13B models)
- 32 GB RAM (for 30B+ models)
- GPU with 8+ GB VRAM (for faster inference)

See [README.md](README.md#quick-start--3-commands-no-cloud-key-needed) for the quickstart guide.

### Does it work on Windows / macOS / Linux?

Yes. The Omega Engine is cross-platform:
- **Linux**: Full support (primary platform)
- **macOS**: Full support (Intel and Apple Silicon)
- **Windows**: Full support (via WSL2 recommended)

### Can I run it without a GPU?

Yes. The native GGUF backend runs on CPU only. Performance will be slower, but functional. For 1.7B-4B models, expect 5-20 tokens/second on a modern CPU.

---

## Models

### What models are supported?

Any model in **GGUF format** (llama.cpp compatible). The Omega Engine has been tested with:
- Qwen 1.7B, 4B, 7B
- Llama 3 8B, 70B
- Mistral 7B, Mixtral 8x7B
- Phi-3, Phi-4
- Gemma 2 9B, 27B
- And many more

See [config/models.yaml](config/models.yaml) for the default model registry.

### Where do I get models?

1. **Hugging Face**: Download GGUF files from [huggingface.co](https://huggingface.co)
2. **Ollama**: Use `ollama pull` to download, then import
3. **Custom**: Convert any model to GGUF using [llama.cpp's convert script](https://github.com/ggerganov/llama.cpp)

### Can I use cloud models as a fallback?

Yes. The Omega Engine supports OpenRouter and any OpenAI-compatible API as a fallback. Configure your API keys in `config/providers.yaml`.

---

## Architecture

### What is the "agent fleet"?

The Omega Engine includes 14 specialized agents that collaborate via the Hivemind P2P layer. Each agent has a distinct role (e.g., research, code review, compliance). See [ARCHITECTURE.md](ARCHITECTURE.md#agent-fleet) for details.

### What is the Hivemind?

Hivemind is the peer-to-peer coordination layer that allows agents to communicate and share context. It runs locally — no external server required.

### What is a "Sovereign WAD"?

Sovereign WAD (SWP) is a Doom-inspired data lump system for packaging and routing knowledge artifacts. It enables hierarchical, efficient data access patterns.

---

## Privacy & Security

### Does the Omega Engine phone home?

No. The Omega Engine has **zero telemetry**. No analytics, no tracking, no remote calls (except when you explicitly configure a cloud provider).

### Where is my data stored?

All data is stored locally on your machine:
- **Conversations**: `data/sessions/`
- **Vector embeddings**: `data/embeddings/`
- **Credentials**: `data/vault/` (encrypted)
- **Models**: Wherever you choose to store them

### Can I encrypt my data?

Yes. The Sovereign Vault uses SQLCipher for database encryption and `age` for file encryption. See [SECURITY.md](SECURITY.md) for details.

### How do I report a security vulnerability?

Please report security issues via [GitHub Security Advisories](https://github.com/Xoe-NovAi/omega-engine/security/advisories/new) — do NOT use public issues. See [SECURITY.md](SECURITY.md) for the full policy.

---

## Development

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We welcome:
- Bug reports and feature requests
- Documentation improvements
- Code contributions (PRs)
- Translations
- Heritage vetting reviews

### How do I add a new model backend?

Implement the `InferenceBackend` protocol in `src/omega/inference/`. See the existing native-gguf and Ollama backends for reference.

### How do I add a new agent?

1. Create an agent definition in `.opencode/agents/your_agent.md`
2. Add the agent to the Hivemind registry
3. Add tests in `tests/`
4. Submit a PR

See [ARCHITECTURE.md](ARCHITECTURE.md#agent-fleet) for the canonical agent list.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'omega.library'"

This is a known issue from the v1.6.0 debut (D-565 cleanup). Fix coming in v1.7.0. Workaround:
```bash
# Reinstall in development mode
pip install -e .
```

### "pip install fails with 'externally-managed-environment'"

Use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### "Model runs but responses are slow"

- Use a smaller model (1.7B instead of 7B)
- Enable GPU acceleration if available
- Reduce context length
- Use quantized models (Q4_K_M instead of Q8_0)

### "I can't connect to the Hivemind"

Check that:
- Port 8016 is not blocked by a firewall
- No other process is using port 8016
- The MCP server is running (`omega-hub` service)

---

## Community

### Where can I get help?

- **GitHub Issues**: [github.com/Xoe-NovAi/omega-engine/issues](https://github.com/Xoe-NovAi/omega-engine/issues)
- **GitHub Discussions**: [github.com/Xoe-NovAi/omega-engine/discussions](https://github.com/Xoe-NovAi/omega-engine/discussions)
- **Documentation**: [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md)

### How can I support the project?

- ⭐ Star the repo
- 🐛 Report bugs
- 📝 Improve documentation
- 💻 Submit PRs
- 💰 Sponsor development (coming soon)

### Is there a Discord or Slack?

Not yet. We're focused on shipping stable releases first. Community chat will come post-debut.

---

## Licensing

### What license is the Omega Engine under?

**Apache 2.0**. You can use it commercially, modify it, and distribute it. See [LICENSE](LICENSE) for the full text.

### What about third-party code?

The Omega Engine includes vetted third-party code under various open-source licenses. See [CREDITS.md](CREDITS.md) for the complete list and license information.

### Can I use the Omega Engine in a commercial product?

Yes. Apache 2.0 explicitly allows commercial use. You must include the license and copyright notice, but there are no royalties or fees.

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ community ⬡ FAQ*
