# 🔱 Provider Naming SSOT
**AP Token:** `AP-PROVIDER-NAMING-SSOT-20260809`
⬡ OMEGA ⬡ STRATEGY ⬡ NAMING-SSOT

**Date:** 2026-08-09
**Status:** LOCKED
**Decision Authority:** Carmack (AP-CARMACK-REVIEW-20260809-v1.0.0)

---

## 📋 Canonical Provider Keys

| Provider | Canonical Key | Source |
|----------|---------------|--------|
| Native GGUF | `native-gguf` | `config/providers.yaml` |
| LM Studio | `lmster` | `config/providers.yaml` |
| Ollama | `ollama` | `config/providers.yaml` |
| Google AI Studio | `google` | `config/providers.yaml` |
| **OpenCode Zen** | **`opencode-zen`** | **`config/providers.yaml`** |
| Antigravity | `antigravity` | `config/providers.yaml` |
| OpenRouter | `openrouter` | `config/providers.yaml` |
| Cline | `cline` | `config/providers.yaml` |
| GitHub Copilot | `copilot` | `config/providers.yaml` |
| xAI (Grok) | `xai` | `config/providers.yaml` |

---

## 🔒 Locked Keys

### `opencode-zen` — **CANONICAL**
- **Length:** 11 characters
- **Used in:** `provider_classification` table, `performance` table, cost attribution, `ProviderRegistry`
- **Rationale:** Single source of truth for all provider references. No aliasing, no shortening.
- **Migration:** None planned. If a real constraint emerges (e.g., Prometheus label limit), add migration *then*.

### Other Keys
All other keys in the table above are similarly locked. Do not introduce aliases or alternate spellings.

---

## 🛡️ Enforcement

1. **CI Gate:** `make check-provider-naming` (to be added) — verifies no alternate keys in codebase
2. **Code Review:** Any new provider reference must use canonical key from this document
3. **Config Source:** `config/providers.yaml` is the *only* authoritative source for provider keys

---

## 📝 Change Process

To add a new provider:
1. Add to `config/providers.yaml` with canonical key
2. Update this document
3. Run `make check-provider-naming` to verify

To rename a provider (requires real constraint):
1. Document the constraint
2. Create migration plan (SQL + code)
3. Execute in single atomic commit
4. Update this document

---

*⬡ OMEGA ⬡ PROVIDER-NAMING-SSOT ⬡ LOCKED ⬡ 2026-08-09*