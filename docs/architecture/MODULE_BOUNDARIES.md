# 🔱 Omega Engine — Module Boundaries & Engine-Stack Firewall (M2)
**AP Token**: `AP-MODULE-BOUNDARIES-v1.0.0` · **Status**: ACTIVE · **Last Updated**: 2026-08-28
**Mandate**: M2 — Engine-Stack Firewall
**Companion**: `ORACLE_STACK_CANONICAL.md` · `docs/architecture/ARCHITECTURE_CANONICAL.md`

---

## §1 M2 MANDATE — THE LAW

> **M2 Engine-Stack Firewall**: Absolute separation of engine logic (machine) from content/personas (mission).
> The WAD system made this explicit in 1993; the Engine-Stack Firewall enforces it today.
>
> **Rule**: `src/omega/` (Core) **never** imports from `config/wads/` (Stacks).
> Stacks may import from Core. Core never imports from Stacks.

**Enforcement**: `scripts/check_mandate_compliance.py` — scans 268 files, 0 violations.

---

## §2 CORE vs STACK — DEFINITIONS

### Core (`src/omega/`) — The Machine
**Immutable engine logic** — same for every user, every pantheon, every deployment.

| Category | Modules | Examples |
|----------|---------|----------|
| Inference | `oracle/`, `model_gateway.py`, `provider_selector.py` | Routing, provider fabric, speculative decode |
| Memory | `memory/`, `memory_store.py`, `soul_store.py` | Vector, FTS, hybrid search, soul persistence |
| Entity | `oracle/entity_registry.py`, `oracle/entity_workspace.py` | YAML CRUD, workspace scaffolding |
| CLI | `cli/oracle_cli.py`, `cli/youtube_cli.py`, etc. | Typer commands, vault injection |
| Observability | `observability.py`, `ics.py` | Trace IDs, session headers |
| Config | `config/loader.py`, `cvar_table.py` | Config loading, runtime tunables |
| Audit | `audit/mandate_auditor.py`, `audit/firewall_checker.py` | Mandate compliance, M2 enforcement |
| Infrastructure | `hub.py`, `mcp_runtime.py`, `monitoring/` | Hivemind, MCP, hardware monitoring |
| Security | `security/`, `privacy/` | Taint tracking, PII masking |

**Core Invariants**:
- Zero telemetry (M8)
- AnyIO only (M1)
- No bare `except:` (M9)
- Local-first provider chain (M7)
- 27 mandates enforced (v3.8.0)

### Stacks (`config/wads/`) — The Mission
**User-customizable content** — pantheons, personas, domain configs, prompts.

| Stack | Path | Purpose |
|-------|------|---------|
| `_omega_default` | `config/wads/_omega_default/` | Default engine config (models, providers) |
| `arcana_novai` | `config/wads/arcana_novai/` | Arcana-NovAi pantheon (10 Pillars + Oversouls) |
| `ingestion` | `config/wads/ingestion/` | Ingestion pipeline config |
| `omega_research` | `config/wads/omega_research/` | Research stack config |

**Stack Contents**:
```
config/wads/<stack>/
├── entities.yaml          # Entity definitions (personas, slots, domains)
├── providers.yaml         # Provider overrides (optional)
├── models.yaml            # Model overrides (optional)
├── hierarchy.yaml         # Oversoul hierarchy (optional)
└── prompts/               # System prompts, invocations
```

---

## §3 FIREWALL ENFORCEMENT

### 3.1 Static Check (CI Gate)
```bash
# In scripts/check_mandate_compliance.py
def check_engine_stack_firewall():
    violations = []
    for py_file in Path("src/omega").rglob("*.py"):
        content = py_file.read_text()
        if "from config.wads" in content or "import config.wads" in content:
            violations.append(f"{py_file}: imports config.wads")
    return violations
```

**Current Status**: 268 files scanned, **0 violations**.

### 3.2 Runtime Enforcement
- `ProviderSelector` reads `config/providers.yaml` (Core SSOT) — NOT from Stack
- `EntityRegistry` reads active IWAD's `entities.yaml` via explicit path resolution
- `WadLoader` (`src/omega/oracle/wad_loader.py`) loads Stack config into Core data structures — **one-way data flow**

### 3.3 WadLoader — The Only Bridge
```python
# src/omega/oracle/wad_loader.py
class WadLoader:
    """Loads Stack config into Core data structures. One-way: Stack → Core."""
    
    def load_active_iwad(self) -> dict:
        """Returns merged config: Core defaults + Stack overrides."""
        core = self._load_core_defaults()      # config/providers.yaml, config/models.yaml
        stack = self._load_stack_config()      # config/wads/<active>/entities.yaml
        return self._merge(core, stack)        # Stack overrides Core
```

**Critical**: `WadLoader` is in Core (`src/omega/oracle/`). It **reads** Stack files but Stack files **never import** Core modules.

---

## §4 INTERFACE CONTRACTS

### 4.1 Core → Stack (Data Flow)
| Interface | Core Module | Stack Data | Direction |
|-----------|-------------|------------|-----------|
| Entity Definitions | `EntityRegistry` | `entities.yaml` | Stack → Core |
| Provider Overrides | `ProviderSelector` | `providers.yaml` | Stack → Core |
| Model Overrides | `ModelGateway` | `models.yaml` | Stack → Core |
| Hierarchy | `Oracle` | `hierarchy.yaml` | Stack → Core |
| Prompts | `ContextBuilder` | `prompts/*.md` | Stack → Core |

### 4.2 Stack → Core (Forbidden)
| Forbidden Pattern | Example | Mandate |
|-------------------|---------|---------|
| `from config.wads import ...` | `from config.wads.arcana_novai import entities` | M2 |
| `import config.wads` | `import config.wads.ingestion` | M2 |
| `sys.path` manipulation to reach Stacks | `sys.path.append("config/wads")` | M2 |

---

## §5 VERIFICATION CHECKLIST

### 5.1 Pre-Commit (Local)
```bash
# Run before commit
python3 scripts/check_mandate_compliance.py --json
# Must show: "engine_stack_firewall": {"violations": 0}
```

### 5.2 CI Gate (GitHub Actions)
```yaml
# .github/workflows/ci.yml
- name: M2 Engine-Stack Firewall
  run: python3 scripts/check_mandate_compliance.py --json | jq -e '.engine_stack_firewall.violations == 0'
```

### 5.3 Manual Verification
```bash
# Quick grep — should return NOTHING
rg "from config\.wads|import config\.wads" src/omega/ --type py

# Verify WadLoader is the only bridge
rg "config/wads" src/omega/ --type py
# Should only match in wad_loader.py
```

---

## §6 COMMON VIOLATIONS & FIXES

| Violation | Fix |
|-----------|-----|
| Stack imports Core utility | Move utility to Core, or duplicate in Stack |
| Core reads Stack file directly | Use `WadLoader.load_active_iwad()` |
| Shared constants in Stack | Move to `src/omega/constants.py` |
| Stack defines base classes | Define in Core, Stack provides config only |

---

## §6 HISTORICAL CONTEXT

**1993 — Doom WAD System**: The original Engine-Stack separation. Engine (`doom.exe`) loads WAD files (`doom.wad`, `doom2.wad`, user PWADs). Engine never imports WAD code; WADs are pure data.

**2026 — Omega Engine**: Same principle. Core (`src/omega/`) is the engine. Stacks (`config/wads/`) are the WADs. `WadLoader` is the WAD directory scanner.

**Why it matters**: 
- Users swap Stacks without touching Core
- Core updates don't break user Stacks
- Multiple pantheons coexist (Arcana-NovAi, Torment, Pokemon, custom)
- Engine is truly universal — the runtime for any vision

---

## §7 AUDIT TRAIL

| Date | Auditor | Finding | Resolution |
|------|---------|---------|------------|
| 2026-08-28 | John Carmack | 0 violations in 268 files | Clean |
| 2026-07-15 | Ma'at | 1 violation in `oracle.py` (imported `config.wads`) | Fixed — moved to `WadLoader` |
| 2026-06-20 | Verity | 3 violations in `ingestion/` | Fixed — Stack config moved to `WadLoader` |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ MODULE-BOUNDARIES-v1.0.0*