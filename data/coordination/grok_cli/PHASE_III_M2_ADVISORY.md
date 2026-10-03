<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# D-281 Phase III — M2 Firewall Remediation (Advisory Spec)
**Packet**: `ho_a050ee6e2652`  
**Author**: `grok-cli/grok` · 2026-07-17  
**Role**: Advisory only — **do not** write `src/omega/` under this packet  
**Pre-req**: Phase II **COMPLETE** (`b661c49`) — `config_resolver` + `wad_loader` live

---

## Status correction for Kali

Kali’s knowledge-gap summary still says Phase II “ACCEPTED + IN PROGRESS.”  
**Truth**: Phase II is **completed** and committed. Phase III is the next *execution* slice for Triad (or a future Tier A handoff).

---

## Verified M2-LEAK inventory (live tree)

| File | Sites | Pattern | Severity |
|------|-------|---------|----------|
| `src/omega/oracle/hierarchy.py` | L39, L45, L46, L49, L50 | 4-parent `Path(__file__)` + `OMEGA_WADS_DIR` inline | **P0** — duplicated WAD root logic |
| `src/omega/oracle/entity_registry.py` | L303, L307, L310 | Same 4-parent for `omega.yaml` + `entities.yaml` | **P0** |
| `src/omega/oracle/oracle.py` | L251 | 4-parent → `AGENTS.md` | **P1** — config path, not WAD content, still bypasses resolver |
| `src/omega/ingestion/scraper.py` | L43 | `Path("config") / "wads" / "ingestion" / "domains.yaml"` | **P1** — CWD-relative (works only if cwd=repo root) |

**Scope correction confirmed**: do **not** treat `mandate_auditor.py` / `sovereign_vetter.py` as Phase III targets if they only use relative `Path("config")/...` without claiming Core ownership of WAD semantics (Sonnet/Kali note stands).

**Note on hierarchy “line 46”**: live file uses L46 for `self.config_path = wads_base / active_iwad / "hierarchy.yaml"` — still a direct WAD path construction (M2).

---

## Recommended fix patterns (for Triad implementers)

### Shared import rule
```python
from omega.governance.config_resolver import (
    PROJECT_ROOT,  # only if needed
    CONFIG_DIR,
    WADS_DIR,
    AGENTS_MD,
    get_active_iwad,
    get_wad_path,
)
```
- Do **not** re-export from `governance/__init__.py`.
- Prefer `get_active_iwad()` over re-parsing `omega.yaml` (DRY + single nested key path).

### 1. `hierarchy.py` (5 sites → 1 path)

**Before**: open `omega.yaml` manually + dual fallback with 4-parent + env.

**After (spec)**:
```python
def __init__(self, hierarchy_config: Optional[Path] = None):
    if hierarchy_config is None:
        active = get_active_iwad()
        wads_base = Path(os.environ.get("OMEGA_WADS_DIR", str(WADS_DIR)))
        self.config_path = wads_base / active / "hierarchy.yaml"
    else:
        self.config_path = hierarchy_config
```

**Optional upgrade**: inject `WadLoader` and resolve via loader API if public method exists; otherwise `WADS_DIR` + env is Phase II–consistent with `wad_loader`.

**Gate risk**: tests that mock 4-parent layout — prefer monkeypatching `WADS_DIR` / env.

### 2. `entity_registry.py` (3 sites)

```python
if config_path is None:
    try:
        active = get_active_iwad()
        config_path = str(get_wad_path(active) / "entities.yaml")
    except (OmegaError, RuntimeError, OSError) as e:
        logger.error(...)
        config_path = str(get_wad_path(DEFAULT_IWAD) / "entities.yaml")
```

Still opens files in Core — M2 is about **path construction**, not forbidding Core reads of WAD *content* via resolved paths.

### 3. `oracle.py` L251

```python
agents_md_path = AGENTS_MD  # config_resolver
# optional: Path(os.environ.get("OMEGA_AGENTS_MD", str(AGENTS_MD)))
```

### 4. `scraper.py` L43

```python
default_config = str(WADS_DIR / "ingestion" / "domains.yaml")
# or get_wad_path("ingestion") / "domains.yaml" if ingestion is a wad name
```

**Critical**: relative `Path("config")` breaks when CLI cwd ≠ repo root — replace with absolute resolver path.

---

## Anti-patterns (reject in review)

1. Re-introducing 3-parent `PROJECT_ROOT` (lands on `src/`).  
2. Module-level I/O in `config_resolver`.  
3. Expanding Phase III to “fix all path strings in repo.”  
4. Writing Phase III under an **advisory** handoff without a new Tier A packet.

---

## Execution order for Triad

1. Patch four files in one PR/commit.  
2. `make test` (expect pre-existing 4 fails unless fixed elsewhere).  
3. `make firewall-check` if available.  
4. Commit: `fix: Phase III — M2 Firewall remediation via config_resolver`

---

## Verdict

| Question | Answer |
|----------|--------|
| Is Kali’s file list correct? | **Yes** (with L46 as path site in hierarchy) |
| Is Phase II ready? | **Yes — already shipped** |
| Can Grok ship Phase III under this packet? | **No** — advisory only |
| Ready for Tier A dispatch? | **Yes** — patterns are low-risk copy of Phase II |

*Deliverable for `ho_a050ee6e2652`.*
