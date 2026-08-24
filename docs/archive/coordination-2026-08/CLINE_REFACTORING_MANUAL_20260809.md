# 🔱 Cline Refactoring Manual — Post Sovereign-Audit Remediation
**AP Token:** `AP-CLINE-REFACTOR-20260809-v1.0.0`
⬡ OMEGA ⬡ CLINE ⬡ refactoring-manual ⬡ 2026-08-09

**Context:** Carmack decisions from `CARMACK_REVIEW_KALI_INSIGHTS_20260809.md`. Three mechanical P1 tasks delegated to Cline CLI.

---

## 📋 Task Overview

| Task | Priority | Est. | Carmack Decision |
|------|----------|------|------------------|
| **1. Remove ICS-T Tags** | P1 | 20 min | Option B — Delete entirely, keep only ICS-S |
| **2. Provider Naming SSOT Doc** | P1 | 10 min | Lock `opencode-zen`, create `PROVIDER_NAMING_SSOT.md` |
| **3. ProviderRegistry Config Loading Test** | P1 | 20 min | Mock config with 3 providers, verify loaded count + `is_cloud` |

---

## 🎯 Task 1: Remove ICS-T Tags (40 Files)

### Background
ICS-T tags are static comments in source files like:
```python
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: DISCOVERY-PIPELINE]
# ICS: [NODE: KNOWLEDGE | ARCHETYPE: SOPHIA | CONTEXT: CURATION-PIPELINE]
```

**Carmack Decision:** These are dead weight — 40 files × ~80 chars = 3,200 bytes of noise. Zero runtime value. Conflate runtime entities with code modules. No tool consumes them. **Delete entirely. Keep only ICS-S (session headers).**

### Execution

**Step 1: Verify the pattern**
```bash
grep -rl '^# ICS: \[NODE:' src/omega/
```
Expected: ~40 files listed.

**Step 2: Dry run (preview changes)**
```bash
grep -rl '^# ICS: \[NODE:' src/omega/ | xargs sed -n '/^# ICS: \[NODE:/p'
```
Verify only ICS-T lines match (not ICS-S session headers).

**Step 3: Execute removal**
```bash
sed -i '/^# ICS: \[NODE:/d' $(grep -rl '^# ICS: \[NODE:' src/omega/)
```

**Step 4: Verify removal**
```bash
grep -r '^# ICS: \[NODE:' src/omega/ || echo "CLEAN - no ICS-T tags remain"
```

**Step 5: Verify ICS-S session headers preserved**
```bash
grep -r '^# ICS: \[SESSION:' src/omega/ | head -5
```
Should still show session headers (these are rendered at runtime, not static).

### Files Likely Affected (from grep)
```
src/omega/oracle/discovery.py
src/omega/oracle/indexer.py
src/omega/oracle/curator.py
src/omega/oracle/research_engine.py
src/omega/oracle/entity_registry.py
src/omega/oracle/model_gateway.py
src/omega/oracle/affinity_resolver.py
src/omega/oracle/budget_gate.py
src/omega/oracle/provider_selector.py
src/omega/oracle/gnosis_proxy.py
src/omega/oracle/entity_affinity.py
src/omega/oracle/retry_policy.py
src/omega/oracle/cascade_router.py
src/omega/oracle/health_monitor.py
src/omega/oracle/backends/*.py
src/omega/observability/*.py
src/omega/ingestion/*.py
src/omega/library/*.py
src/omega/workers/*.py
src/omega/search/*.py
```

### Acceptance Criteria
- [ ] `grep -r '^# ICS: \[NODE:' src/omega/` returns nothing
- [ ] `grep -r '^# ICS: \[SESSION:' src/omega/` still returns session headers
- [ ] `make test` passes (no syntax errors from removal)
- [ ] Git diff shows only ICS-T lines removed

---

## 🎯 Task 2: Provider Naming SSOT Document

### Background
`opencode-zen` (11 chars) is the canonical provider key used in:
- `provider_classification` table (SQLite)
- Historical `performance` table
- Cost attribution summaries
- `config/providers.yaml` inference providers list

**Carmack Decision:** Lock the name now. 11 chars is fine (Prometheus labels support 128). No migration path unless real constraint emerges. Create `docs/strategy/PROVIDER_NAMING_SSOT.md`.

### Execution

**Create file:** `docs/strategy/PROVIDER_NAMING_SSOT.md`

```markdown
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
```

### Acceptance Criteria
- [ ] `docs/strategy/PROVIDER_NAMING_SSOT.md` created with above content
- [ ] `opencode-zen` listed as canonical key
- [ ] No migration path designed (explicitly stated)
- [ ] File passes `make doc-llm-validate`

---

## 🎯 Task 3: ProviderRegistry Config Loading Test

### Background
`ProviderRegistry.from_config_path()` had **zero test coverage** on the config loading path. This allowed the "empty model map bug" where it read `config["providers"]` but YAML nests under `config["inference"]["providers"]`.

**Carmack Decision:** Add test with spec:
- Mock `config.yaml` with 3 known providers
- Call `ProviderRegistry.from_config_path()`
- Assert loaded count == 3, `is_cloud` matches mock

### Execution

**Create file:** `tests/contract/test_provider_registry_config.py`

```python
# AP: AP-TEST-PROVIDER-REGISTRY-CONFIG-20260809
# 🔱 ProviderRegistry Config Loading Test
# Verifies ProviderRegistry correctly loads providers from config/providers.yaml

import tempfile
import yaml
from pathlib import Path
from src.omega.oracle.provider_registry import ProviderRegistry


class TestProviderRegistryConfigLoading:
    """Test ProviderRegistry config loading path."""

    def test_loads_providers_from_yaml(self):
        """ProviderRegistry loads providers from config.yaml with correct is_cloud values."""
        # Arrange: Create mock config.yaml with 3 providers
        mock_config = {
            "inference": {
                "providers": [
                    {"provider": "test-local", "priority": 0, "enabled": True, "is_cloud": False},
                    {"provider": "test-cloud-1", "priority": 1, "enabled": True, "is_cloud": True},
                    {"provider": "test-cloud-2", "priority": 2, "enabled": True, "is_cloud": True},
                ]
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(yaml.dump(mock_config))

            # Act: Load registry from mock config
            registry = ProviderRegistry.from_config_path(str(config_path))

            # Assert: All 3 providers loaded
            assert len(registry._providers) == 3, f"Expected 3 providers, got {len(registry._providers)}"

            # Assert: Provider names match
            provider_names = {p.name for p in registry._providers}
            assert provider_names == {"test-local", "test-cloud-1", "test-cloud-2"}

            # Assert: is_cloud values match mock
            for provider in registry._providers:
                if provider.name == "test-local":
                    assert provider.is_cloud is False, f"{provider.name} should be local"
                else:
                    assert provider.is_cloud is True, f"{provider.name} should be cloud"

    def test_unknown_provider_defaults_to_cloud(self):
        """Unknown provider (not in config) defaults to cloud (pessimistic per M7)."""
        mock_config = {
            "inference": {
                "providers": [
                    {"provider": "known-local", "priority": 0, "enabled": True, "is_cloud": False},
                ]
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(yaml.dump(mock_config))

            registry = ProviderRegistry.from_config_path(str(config_path))

            # Unknown provider should default to cloud (pessimistic)
            assert registry.is_cloud("unknown-provider") is True
            # Known provider should match config
            assert registry.is_cloud("known-local") is False

    def test_synthetic_provider_exclusion(self):
        """Synthetic providers (mock, fallback) are excluded from sovereignty stats."""
        mock_config = {
            "inference": {
                "providers": [
                    {"provider": "real-local", "priority": 0, "enabled": True, "is_cloud": False},
                    {"provider": "mock", "priority": 99, "enabled": True, "is_cloud": False},
                    {"provider": "fallback", "priority": 100, "enabled": True, "is_cloud": False},
                ]
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(yaml.dump(mock_config))

            registry = ProviderRegistry.from_config_path(str(config_path))

            # Synthetic providers should be marked as such
            assert registry.is_synthetic("mock") is True
            assert registry.is_synthetic("fallback") is True
            assert registry.is_synthetic("real-local") is False
```

### Run Test
```bash
source .venv/bin/activate && python -m pytest tests/contract/test_provider_registry_config.py -v
```

### Acceptance Criteria
- [ ] `tests/contract/test_provider_registry_config.py` created
- [ ] All 3 tests pass
- [ ] Test covers: correct loading, unknown→cloud default, synthetic detection
- [ ] `make test` includes new test (no regressions)

---

## 📦 Submission Checklist

Before marking tasks complete:

| Task | Verification |
|------|--------------|
| **1. ICS-T Removal** | `grep -r '^# ICS: \[NODE:' src/omega/` returns nothing; `make test` passes |
| **2. Naming SSOT Doc** | `docs/strategy/PROVIDER_NAMING_SSOT.md` exists; `make doc-llm-validate` passes |
| **3. Config Loading Test** | `pytest tests/contract/test_provider_registry_config.py -v` → 3 passed |

---

## 🔗 Reference Documents

| Document | Purpose |
|----------|---------|
| `data/coordination/CARMACK_REVIEW_KALI_INSIGHTS_20260809.md` | Carmack decisions (source of truth) |
| `data/coordination/KALI_INSIGHTS_FOR_CARMACK_20260809.md` | Kali's analysis that prompted decisions |
| `src/omega/oracle/provider_registry.py` | SSOT implementation to test |
| `config/providers.yaml` | Authoritative provider config |

---

## 🚨 Important Notes

1. **Do not modify** `src/omega/ics.py` — ICS-S (session headers) are separate and must be preserved
2. **Do not create** migration scripts for provider naming — Carmack explicitly said "no migration unless real constraint"
3. **Use venv python** — `source .venv/bin/activate && python ...` for all test runs
4. **Commit separately** — Each task should be its own commit with clear message:
   - `chore(ics): remove ICS-T tags from 40 source files`
   - `docs(strategy): add PROVIDER_NAMING_SSOT.md locking opencode-zen`
   - `test(provider-registry): add config loading test with 3 providers`

---

*⬡ OMEGA ⬡ CLINE ⬡ REFACTORING-MANUAL ⬡ 2026-08-09*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: refactoring-manual | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
