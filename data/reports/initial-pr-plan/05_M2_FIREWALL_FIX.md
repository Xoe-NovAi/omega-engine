<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine Initial PR Plan — M2 Firewall Fix
## WAD → Stack Internal Rename: Complete Details

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Part**: 05 of 09  
**Date**: 2026-08-14  

---

## 🎯 THE MANDATE VIOLATION

### Mandate 2 (Engine-Stack Firewall):
> "Maintain absolute separation between the Omega Engine Core and Expansion Stacks (WADs).
> Core: `src/omega/`, `config/omega.yaml`, `opencode.json`.
> Stacks: `config/wads/<stack_name>/`.
> Constraint: Never add stack-specific logic to the Core Engine."

### The Violation:
**344 internal "WAD" references** in `src/omega/` — the engine core knows about "WAD" as its internal runtime concept. This IS the violation.

```bash
grep -rn "WAD" src/omega/ --include="*.py" | grep -v "__pycache__" | wc -l
# → 344 references
```

---

## 🔧 THE FIX: RENAME INTERNAL CONCEPT

### Principle:
- **Engine knows "Stack" interface** — the runtime concept
- **StackLoader knows "WAD" format** — the file format (heritage)
- **Heritage tags on StackLoader are CORRECT** — it loads Doom 1993 WAD format

### What Changes:
| Before | After | Reason |
|--------|-------|--------|
| `wad_loader.py` | `stack_loader.py` | Internal concept rename |
| `WADLoader` class | `StackLoader` class | Internal concept rename |
| `wad_loader` variable | `stack_loader` variable | Internal concept rename |
| `config/wads/` | `config/stacks/` | Directory rename |
| `active_iwad` config | `active_stack` config | Config rename |
| Heritage tags on loader | **PRESERVED** | Loader knows WAD format |

### What Does NOT Change:
- `[id-soft: doom-1993]` heritage tags on `StackLoader` class
- The WAD file format itself (`.wad` extension, lump structure)
- The Doom 1993 provenance of the WAD system

---

## 📝 EXACT COMMANDS

### Step 1: Rename Files
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1a. Rename wad_loader.py → stack_loader.py
mv src/omega/oracle/wad_loader.py src/omega/oracle/stack_loader.py

# 1b. Rename config/wads/ → config/stacks/
mv config/wads config/stacks

# 1c. Update config/omega.yaml
sed -i 's/active_iwad:/active_stack:/' config/omega.yaml
# Note: value "_omega_default" stays the same
```

### Step 2: Update oracle.py Imports
```bash
# 2a. Update import statement
sed -i 's/from \.wad_loader import/from .stack_loader import/' src/omega/oracle/oracle.py

# 2b. Rename WADLoader → StackLoader
sed -i 's/WADLoader/StackLoader/g' src/omega/oracle/oracle.py

# 2c. Replace wad_loader variable references
sed -i 's/wad_loader/stack_loader/g' src/omega/oracle/oracle.py
```

### Step 3: Update All Internal References (NOT Heritage Tags)
```bash
# 3a. Find all files with wad_loader/WADLoader references
# Exclude: __pycache__, [id-soft:] tags, doom-1993 heritage
grep -rn "wad_loader\|WADLoader" src/omega/ --include="*.py" | \
  grep -v "__pycache__" | \
  grep -v "\[id-soft:" | \
  grep -v "doom-1993" | \
  cut -d: -f1 | sort -u

# 3b. Apply rename to all found files
grep -rn "wad_loader\|WADLoader" src/omega/ --include="*.py" | \
  grep -v "__pycache__" | \
  grep -v "\[id-soft:" | \
  grep -v "doom-1993" | \
  cut -d: -f1 | sort -u | \
  xargs sed -i 's/wad_loader/stack_loader/g; s/WADLoader/StackLoader/g'
```

### Step 4: Verify Heritage Tags Preserved
```bash
# 4a. Check heritage tags on StackLoader class
grep -B 5 "class StackLoader" src/omega/oracle/stack_loader.py | head -15

# 4b. Verify [id-soft: doom-1993] tags exist
grep -A 10 "class StackLoader" src/omega/oracle/stack_loader.py | grep "id-soft"

# 4c. Verify NO WAD refs remain in engine core (except heritage)
grep -rn "WAD" src/omega/ --include="*.py" | \
  grep -v "__pycache__" | \
  grep -v "\[id-soft:" | \
  grep -v "doom-1993" | wc -l
# Must show: 0
```

---

## 📋 FILES THAT NEED UPDATING (Expected)

Based on the grep analysis, these files likely need updates:

### Core Engine Files:
- `src/omega/oracle/oracle.py` — imports WADLoader, uses wad_loader variable
- `src/omega/oracle/entity_registry.py` — likely references WAD concepts
- `src/omega/oracle/wad_loader.py` → `stack_loader.py` — the file itself
- `config/omega.yaml` — `active_iwad` config key

### Possible Other Files:
- Any file in `src/omega/` that references `wad_loader` or `WADLoader` as internal concept
- NOT files with `[id-soft: doom-1993]` heritage tags (those are correct)

---

## ✅ VERIFICATION CHECKLIST

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. No WAD refs in engine core (except heritage tags)
grep -rn "WAD" src/omega/ --include="*.py" | \
  grep -v "__pycache__" | \
  grep -v "\[id-soft:" | \
  grep -v "doom-1993" | wc -l
# Must show: 0

# 2. Heritage tags preserved on StackLoader
grep -A 10 "class StackLoader" src/omega/oracle/stack_loader.py | grep "id-soft"
# Must show: [id-soft: doom-1993] tags

# 3. StackLoader loads WAD format (correct)
grep -A 20 "class StackLoader" src/omega/oracle/stack_loader.py | grep -i "wad"
# Should show: references to WAD format loading

# 4. Config updated
grep "active_stack" config/omega.yaml
# Must show: active_stack: "_omega_default"

# 5. Directory renamed
ls config/stacks/
# Must show: stack directories (was config/wads/)

# 6. Core tests pass
.venv/bin/python -m pytest tests/test_stack_loader.py -q
# Must show: all passed

# 7. Temple-grade M2 gate passes
make temple-grade
# M2 must show: PASS
```

---

## 🎯 HERITAGE CORRECTNESS

### Why Heritage Tags on StackLoader Are CORRECT:

The `[id-soft: doom-1993]` heritage tag on `StackLoader` is **intentionally correct** because:

1. **StackLoader loads WAD-format files** — the Doom 1993 WAD lump structure
2. **The heritage is about the FILE FORMAT**, not the internal concept
3. **M2 Firewall requires**: Engine knows "Stack" interface; StackLoader knows "WAD" format
4. **This is the correct architectural boundary** — the loader is the translation layer

### What Would Be WRONG:
- Removing heritage tags from StackLoader (loses Doom provenance)
- Moving heritage tags to config/stacks/ directory (wrong level)
- Keeping "WAD" as internal engine concept (violates M2)

---

## 📋 OPEN DECISION FOR GROK CLI

**Decision**: Does Grok CLI agree the `[id-soft: doom-1993]` heritage tags should be preserved on `StackLoader` after the WAD→Stack rename?

**Options**:
- **A) Preserve heritage tags** — StackLoader keeps `[id-soft: doom-1993]`. Internal concept renamed from WAD to Stack, but loader's domain knowledge remains. **Recommended.**
- **B) Remove heritage tags** — Lose Doom provenance. Simplifies rename but loses historical context.
- **C) Move heritage tags** — Move `[id-soft: doom-1993]` from StackLoader to config/stacks/ directory-level or separate heritage file.

**Grok CLI Input Required**: Yes/No/Comment on preserving heritage tags on StackLoader.

---

## 📋 TIME ESTIMATE

| Step | Time |
|------|------|
| Rename files | 2 min |
| Update oracle.py | 2 min |
| Update all internal refs | 5 min |
| Verify heritage tags | 2 min |
| Run tests | 5 min |
| Temple-grade check | 5 min |
| **Total** | **~20 minutes** |

---

**Next**: See `06_COMMIT_PLAN.md` for the complete 4-commit plan with all commands.
