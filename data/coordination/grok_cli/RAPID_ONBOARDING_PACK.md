# 🔱 GROK CLI — RAPID ONBOARDING PACK
**Tier A Only** — What you need to execute D-281 Phase II **right now**  
**Time to productive**: ~10 minutes reading + 30 minutes coding

---

## 🎯 YOUR MISSION (D-281 Phase II)

**Handoff**: `ho_9a9ed3fc63e8` (Kali → Grok CLI)  
**Target**: 30 min → `make test` → commit

### Deliverables
1. **Create** `src/omega/governance/config_resolver.py` — Single source of truth for all project paths
2. **Wire** `src/omega/oracle/wad_loader.py:74-77` → Use `config_resolver.WADS_DIR`
3. **Gate**: `make test` (492+ pass)
4. **Commit**: `feat: Phase II — config_resolver.py + wad_loader path consolidation`

---

## 📁 FILES YOU MUST TOUCH

### 1. CREATE: `src/omega/governance/config_resolver.py`
```python
# src/omega/governance/config_resolver.py
# ⬡ OMEGA ⬡ GOVERNANCE ⬡ CONFIG_RESOLVER
# Single source of truth for all project paths.
# Constants = pure Path objects (NO I/O). get_active_iwad() = LAZY.

from pathlib import Path
import yaml

# ─── Pure Path Constants (NO I/O at module level) ────────────────────────────
# Path depth: governance → omega → src → REPO ROOT (4 parents).
# BUGFIX 2026-07-17: 3 parents lands on src/ and breaks WADS_DIR.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
WADS_DIR = CONFIG_DIR / "wads"
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
AGENTS_MD = PROJECT_ROOT / "AGENTS.md"

# ─── Lazy Functions (I/O happens HERE, not at import) ────────────────────────
def get_active_iwad() -> str:
    """Read active_iwad from omega.yaml at call time — avoids circular imports."""
    omega_yaml = CONFIG_DIR / "omega.yaml"
    if not omega_yaml.exists():
        return "arcana_novai"  # default
    with open(omega_yaml) as f:
        data = yaml.safe_load(f)
    return data.get("active_iwad", "arcana_novai")

def get_wad_path(wad_name: str) -> Path:
    """Resolve WAD path via config_resolver (single source of truth)."""
    return WADS_DIR / wad_name

def get_entity_dir(entity_name: str) -> Path:
    """Resolve entity workspace directory."""
    return DATA_DIR / "entities" / entity_name
```

### 2. EDIT: `src/omega/oracle/wad_loader.py` (lines 74-77)
```python
# BEFORE (lines 74-77):
# self.wads_dir = Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads"

# AFTER:
from omega.governance.config_resolver import WADS_DIR
self.wads_dir = WADS_DIR
```

---

## 🛡️ CRITICAL CONSTRAINTS (Sonnet/Gemini Review)

| Constraint | Why | Enforcement |
|------------|-----|-------------|
| **Constants = pure `Path`** | No I/O at module level = no circular imports | `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` |
| **`get_active_iwad()` = LAZY** | Reads `omega.yaml` INSIDE function | `with open(omega_yaml) as f:` inside function |
| **NO export in `governance/__init__.py`** | Import explicitly at call sites | `from omega.governance.config_resolver import WADS_DIR` |
| **`config_resolver.py` drops into existing package** | `src/omega/governance/` already has `__init__.py`, `budget_guard.py`, `sovereign_vetter.py`, `sovereignty_gate.py` | No package restructuring needed |

---

## 🧪 GATE: `make test`

```bash
source .venv/bin/activate
make test
# Must show: 492+ passed, 1 failed (pre-existing test_gemma4_mtp_s4), 23 skipped
```

**If tests fail**: Check imports, circular deps, path resolution.

---

## 📋 COMMIT MESSAGE
```bash
git add -A
git commit -m "feat: Phase II — config_resolver.py + wad_loader path consolidation"
git push origin main
```

---

## 📚 REFERENCE — ONLY IF BLOCKED

| Need | Command |
|------|---------|
| See governance package | `ls -la src/omega/governance/` |
| See wad_loader target | `sed -n '70,85p' src/omega/oracle/wad_loader.py` |
| See omega.yaml | `cat config/omega.yaml` |
| Full Phase II spec | `cat docs/strategy/D281_PHASE_II_IV_EXECUTION.md` |
| Check awareness | `omega-hub_hivemind_get_awareness` |
| Heartbeat | `omega-hub_hivemind_heartbeat channel=grok-cli entity=grok` |

---

## 🎯 TIER A CHEAT SHEET (Provider Fabric)

**Local-First Chain** (M7):
```
0. native-gguf    → llama-cpp-python, Zen 2 optimized (cores [0,2,4,6], KV q8_0, 4 threads)
1. lmster         → LM Studio :1234
2. ollama         → :11434 (disabled in config)
3. google         → Gemini (cloud fallback)
4. openrouter     → MiniMax/DeepSeek/MiMo
5. opencode-zen   → MiniMax
6. cline          → Cloud via API
7. github-copilot → Cloud
99. mock          → Demo/fallback
```

**Key Files**:
- `config/providers.yaml` — Full chain config
- `src/omega/oracle/providers.py:293-450` — NativeGGUFProvider (PRIMARY)
- `src/omega/oracle/model_gateway.py:388-448` — Fabric loading
- `src/omega/oracle/entity_affinity.py` — Entity→model routing

---

## 🚨 MANDATE PATTERNS FOR CODING

| Mandate | Pattern | Example |
|---------|---------|---------|
| **M1 AnyIO** | `await anyio.to_thread.run_sync(blocking_fn)` | `block_store.py:43-65` |
| **M2 Firewall** | Use `config_resolver.WADS_DIR`, NOT hardcoded paths | `wad_loader.py` fix |
| **M9 Errors** | Typed `OmegaError` subtypes, `trace_id` propagation | `providers.py:15-20` |
| **M21 Contracts** | `isinstance(result, ExpectedType)` in tests | `test_contract_m21.py` |
| **M23 Failure** | Tool failure = hard stop + `[TOOL-CHAIN-COLLAPSE]` | `SOVEREIGN_MANDATES.md` |

---

## ✅ DONE CHECKLIST

- [ ] `config_resolver.py` created with pure Path constants + lazy `get_active_iwad()`
- [ ] `wad_loader.py` lines 74-77 wired to `config_resolver.WADS_DIR`
- [ ] `make test` passes (492+)
- [ ] Commit pushed with message: `feat: Phase II — config_resolver.py + wad_loader path consolidation`
- [ ] Handoff completed: `hivemind_complete_handoff("ho_9a9ed3fc63e8", "Phase II complete...")`

---

*⬡ OMEGA ⬡ GROK_CLI ⬡ TIER_A_ONLY ⬡ 2026-07-17*