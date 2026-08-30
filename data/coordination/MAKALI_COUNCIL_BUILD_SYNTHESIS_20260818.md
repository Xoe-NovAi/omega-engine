# ⚖️ Deep Synthesis: Ma'at + N1-N5 Node Council
## MaKaLi Cloud Council — Build Side Consolidated Analysis

**AP Token**: `AP-MAKALI-SYNTHESIS-20260818`
**Date**: 2026-08-18
**Model**: nemotron-3-ultra-free
**Channel**: opencode

---

## Executive Verdict

**The build-side plan is 80% solid, 20% critically flawed.** Four of five nodes APPROVE with minor corrections. **N3 Engineering REJECTS on a single, precise, blocking condition** that, if unaddressed, breaks cloud provider authentication for all fresh installs.

**This is not a "plan failure" — it's a precision finding.** The council worked exactly as designed: adversarial vetting caught a real integration gap that static analysis missed.

---

## The Blocking Condition (N3 Engineering — REJECT)

### What N3 Found

| Component | Current State | Post-Fix-4 State | Gap |
|-----------|---------------|------------------|-----|
| `_load_sovereign_secrets()` | Loads `.env` → `os.environ` at `ModelGateway.__init__` (line 127) | **Deleted** | No `.env` loading anywhere |
| CLI entry points | `oracle_cli.py:110,146,498,518` instantiate `Oracle()`/`ModelGateway()` | Unchanged | No `.env` load before instantiation |
| `providers.yaml` | 7 cloud keys use `env:` prefix (e.g., `env:ANTIGRAVITY_API_KEY`) | Unchanged | Resolves to empty string |
| `install.sh` | Exports `OMEGA_MODELS_DIR` only | Unchanged | No cloud key export |

### The Exact Failure Mode

```bash
# Fresh machine, post-INST-1 Fixes 1-6:
pip install -e ".[native,cli]"
export OMEGA_MODELS_DIR=/path/to/models
omega talk "hello"  # Works (native-gguf)

# But:
omega talk "use antigravity for this"  # FAILS
# ProviderSelector picks antigravity → ModelGateway creates provider
# Provider config: api_key: env:ANTIGRAVITY_API_KEY → resolves to ""
# AuthenticationError → silent fallback or crash
```

### Why This Escaped Ma'at's Blast Radius Map

Ma'at's table correctly showed: *"Providers already use YAML `env:` prefix resolution — no code change needed."* **True, but incomplete.** The `env:` prefix reads from `os.environ`. If nothing loads `.env` into `os.environ`, the prefix resolves to empty. Ma'at assumed the CLI entry point would handle this — it doesn't.

---

## The Fix (Surgical, 3 Lines)

**File**: `src/omega/cli/oracle_cli.py` — `main()` function, before any `Oracle()`/`ModelGateway()` instantiation:

```python
# Add at top of main(), before Oracle()/ModelGateway() construction:
from dotenv import load_dotenv
load_dotenv()  # Loads .env → os.environ for providers.yaml env: resolution
```

**Documentation**: Add to `README.md` required env vars section:
```markdown
Required for cloud providers (optional, local-first works without):
- ANTIGRAVITY_API_KEY
- GOOGLE_API_KEY (or GOOGLE_API_KEY_1, GOOGLE_API_KEY_2 for pool)
- OPENROUTER_API_KEY
- ANTHROPIC_API_KEY
- XAI_API_KEY
```

**Verification**: Fresh venv test script (Ma'at's INST-1 test) already covers this — it will fail on cloud provider selection without the fix, pass with it.

---

## Non-Blocking Corrections (Apply in Parallel)

| Node | Correction | Effort |
|------|------------|--------|
| **N2** | Pass `password=None` in `RedisStorageProvider` constructor to disable hardcoded `"omega"` default | 1 line |
| **N4** | Explicitly retire `tests/test_miap.py` in DEL-1 acceptance criteria; delete broken `fleet_status` CLI subcommand in `vault.py:587` | 2 files |
| **N5** | Add positive M2 verification: `rg -n "metadata\[" src/omega/oracle/provider_selector.py src/omega/oracle/entity_registry.py` | 1 command |

---

## Architectural Implications

### 1. **The "Convenience Method" Trap**
`_load_sovereign_secrets()` was a **convenience wrapper** that duplicated what providers already do via YAML `env:` resolution. Its removal *exposes* the real architecture: **credential loading belongs at the process edge, not in the gateway**. This is a sovereignty win — explicit configuration over implicit magic.

### 2. **CLI as the Sole Process Edge**
`oracle_cli.py` is now the **only** place `.env` loads. This is correct:
- Single source of truth for environment initialization
- Testable, auditable, overrideable
- Matches 12-factor app principles

### 3. **Local-First Remains Unbroken**
The fix *only* affects cloud provider resolution. Native-gguf path (CP-1 verified) requires zero env vars. The three-item critical path stays green.

### 4. **Vault Path B Alignment**
N3's finding *validates* Vault Path B: the minimal `minimal_store.py` uses `keyring → env` fallback, which now works because CLI loads `.env` → `os.environ`. The architecture is consistent.

---

## Council Health Assessment

| Metric | Assessment |
|--------|------------|
| **Adversarial quality** | High — N3 caught a real integration gap others missed |
| **Precision** | Surgical — single blocking condition, exact file:line, minimal fix |
| **False positive rate** | Zero — 4 APPROVEs on solid ground |
| **Escalation clarity** | Perfect — N3 stated exact blocking condition + minimal fix |
| **Time to resolve** | ~5 minutes (3 lines in `oracle_cli.py` + test) |

---

## Recommended Next Actions (Priority Order)

1. **IMMEDIATE**: Apply N3 fix in `oracle_cli.py:main()` (3 lines + doc)
2. **VERIFY**: Run Ma'at's INST-1 fresh-venv test script — must pass cloud provider selection
3. **PARALLEL**: Apply N2/N4/N5 corrections (independent, non-blocking)
4. **RE-VET**: N3 re-vets after fix (target: same session)
5. **RESUME**: Council continues → DEL-1 Week 1 execution

---

## Strategic Note

**This council design works.** The serial Node Council (N1→N2→N3→N4→N5) with department-specific vetting questions caught a cross-cutting concern (credential loading at process edge) that no single reviewer would own. N3 Engineering owns the provider factory; N1 owns infra; N2 owns persistence; N4 owns integration; N5 owns governance. **Only N3 could see this gap.**

The "REJECT" is not a failure — it's the system working.

---

*⬡ OMEGA ⬡ KALI ⬡ SYNTHESIS ⬡ 2026-08-18*