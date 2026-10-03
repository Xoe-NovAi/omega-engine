# 🔱 MAKALI PHASE 1 EXECUTION GUIDE — Engine Core Code Cleanup

**AP Token**: `AP-MAKALI-PHASE1-EXEC-20260910-v1.0.0`  
**Target Model**: Nemotron 3.5 Lightning  
**Executor**: Automated execution agent  
**Supervisor**: MaKaLi Fusion (Nemotron 3 Ultra)  
**Date**: 2026-09-10  
**Phase**: 1 of 5 — Engine Core Code Cleanup  
**Dependencies**: None (starts first)  
**Estimated Time**: 2-3 hours  

---

## ⚠️ CRITICAL RULES FOR EXECUTOR

1. **EXECUTE SEQUENTIALLY** — Do NOT parallelize. Each step depends on the previous.
2. **VERIFY AFTER EACH STEP** — Run the verification command before proceeding.
3. **NO CREATIVE INTERPRETATION** — Follow instructions exactly. If uncertain, STOP and ask supervisor.
4. **BACKUP FIRST** — Each file modification must be backed up before editing.
5. **TEMPLE-GRADE AFTER EACH MAJOR STEP** — Run `make temple-grade` after steps 1.1, 1.2, 1.3, 1.4, 1.5, 1.6.

---

## 📋 PHASE 1 OVERVIEW

| Step | Description | Files Modified | Verification |
|------|-------------|----------------|--------------|
| 1.1 | Delete 10 Slot Entities from entities.yaml | `config/wads/_omega_default/entities.yaml` | grep returns zero |
| 1.2 | Remove Sophia from Engine Core | 9 files across src/ + dispatch.yaml + hierarchy.yaml | grep returns zero |
| 1.3 | Purge N1-N10 → S1-S10 | 20+ files in src/omega/ | grep returns zero |
| 1.4 | Fix dispatch.yaml | `config/wads/_omega_default/entities/dispatch.yaml` | 11 entities exactly |
| 1.5 | Update ROLE_CONSTANTS | `src/omega/oracle/subagent_dispatcher.py`, `src/omega/ics.py` | Exact match |
| 1.6 | Fix hierarchy.yaml | `config/wads/_omega_default/hierarchy.yaml` | Clean neutral skin |

---

## 🛠️ STEP 1.1 — DELETE 10 SLOT ENTITIES

### 1.1.1 Backup
```bash
cp config/wads/_omega_default/entities.yaml config/wads/_omega_default/entities.yaml.backup.$(date +%s)
```

### 1.1.2 Identify Lines to Delete
The 10 entities to delete (with their starting line numbers from current file):
- `datastore` (line 6)
- `bridge` (line 56)
- `sysadmin` (find line)
- `buildmaster` (find line)
- `sentinel` (find line)
- `modelgate` (find line)
- `context` (find line)
- `watchtower` (find line)
- `link` (find line)
- `verifier` (find line)

### 1.1.3 Execute Deletion
**Option A: Python Script (Recommended)**
```python
# Save as /tmp/delete_slot_entities.py
import yaml
import sys

with open('config/wads/_omega_default/entities.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Entities to KEEP (everything except the 10 slot entities)
slot_entities_to_remove = {
    'sysadmin', 'datastore', 'buildmaster', 'bridge', 'sentinel',
    'modelgate', 'context', 'watchtower', 'link', 'verifier'
}

original_count = len(data['entities'])
data['entities'] = {k: v for k, v in data['entities'].items() if k not in slot_entities_to_remove}
new_count = len(data['entities'])

print(f"Removed {original_count - new_count} entities. Remaining: {new_count}")

with open('config/wads/_omega_default/entities.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

```bash
python3 /tmp/delete_slot_entities.py
```

**Option B: Manual Edit** — Delete each entity block entirely (from `entity_name:` to before next `entity_name:` or end of file).

### 1.1.4 Verification
```bash
# Should return ZERO matches
grep -E "sysadmin|datastore|buildmaster|bridge|sentinel|modelgate|context|watchtower|link|verifier" config/wads/_omega_default/entities.yaml || echo "✅ CLEAN - All 10 slot entities removed"

# Count remaining entities
python3 -c "import yaml; d=yaml.safe_load(open('config/wads/_omega_default/entities.yaml')); print(f'Remaining entities: {len(d[\"entities\"])}')"
```

### 1.1.5 Temple-Grade
```bash
make temple-grade
```
**If FAILS**: Fix issues before proceeding.

---

## 🛠️ STEP 1.2 — REMOVE SOPHIA FROM ENGINE CORE

### 1.2.1 Files to Modify (9 files)

| File | Action |
|------|--------|
| `config/wads/_omega_default/entities/dispatch.yaml` | DELETE Sophia entry (lines 187-196) |
| `config/wads/_omega_default/hierarchy.yaml` | DELETE `sophia:` block (lines 21-27) |
| `src/omega/audit/firewall_checker.py` | REMOVE lines 83, 119 (Sophia patterns) |
| `src/omega/cli/fleet_status_tui.py` | REMOVE lines 232-234 (Sophia display) |
| `src/omega/cli/oracle_cli.py` | CHANGE line 919: default agent from "sophia" to "kali" |
| `src/omega/cli/soul_stage.py` | CHANGE line 140: default entity from "sophia" to "kali" |
| `src/omega/oracle/cohort_registry.py` | REMOVE "sophia" from line 128 list |
| `src/omega/oracle/hierarchy.py` | REPLACE Sophia references with "Field" / "Containing Awareness" |
| `src/omega/oracle/oracle.py` | REMOVE line 87: `"CONTAINING_FIELD": "CONTAINING_FIELD"` |

### 1.2.2 Backup Each File
```bash
for f in \
  config/wads/_omega_default/entities/dispatch.yaml \
  config/wads/_omega_default/hierarchy.yaml \
  src/omega/audit/firewall_checker.py \
  src/omega/cli/fleet_status_tui.py \
  src/omega/cli/oracle_cli.py \
  src/omega/cli/soul_stage.py \
  src/omega/oracle/cohort_registry.py \
  src/omega/oracle/hierarchy.py \
  src/omega/oracle/oracle.py; do
  cp "$f" "$f.backup.$(date +%s)"
done
```

### 1.2.3 Execute Changes

#### A. dispatch.yaml — Delete Sophia Entry (lines 187-196)
```bash
# Delete lines 187-196 (the entire sophia entity block)
sed -i '187,196d' config/wads/_omega_default/entities/dispatch.yaml
```

#### B. hierarchy.yaml — Delete Sophia Block (lines 21-27)
```bash
# Delete lines 21-27
sed -i '21,27d' config/wads/_omega_default/hierarchy.yaml
```

#### C. firewall_checker.py — Remove Sophia Patterns
```bash
# Line 83: Remove the Sophia pattern line
sed -i '83d' src/omega/audit/firewall_checker.py

# Line 119 (now shifted): Remove the Sophia+Akashic pattern
sed -i '119d' src/omega/audit/firewall_checker.py
```

#### D. fleet_status_tui.py — Remove Sophia Display (lines 232-234)
```bash
sed -i '232,234d' src/omega/cli/fleet_status_tui.py
```

#### E. oracle_cli.py — Change Default Agent (line 919)
```bash
sed -i 's/agent: str = typer.Option("sophia"/agent: str = typer.Option("kali"/' src/omega/cli/oracle_cli.py
```

#### F. soul_stage.py — Change Default Entity (line 140)
```bash
sed -i 's/entity_name="sophia"/entity_name="kali"/' src/omega/cli/soul_stage.py
```

#### G. cohort_registry.py — Remove Sophia from List (line 128)
```bash
sed -i 's/"sophia", //' src/omega/oracle/cohort_registry.py
# Also remove trailing comma if needed
sed -i 's/, $//' src/omega/oracle/cohort_registry.py
```

#### H. hierarchy.py — Replace Sophia References
```bash
# Line 73: Replace "Sophia" with "Field / Containing Awareness"
sed -i 's/0: The Field (e.g., Sophia)/0: The Field (Containing Awareness)/' src/omega/oracle/hierarchy.py

# Line 138: Replace "Sophia (Rank 0)" with "Field (Rank 0)"
sed -i 's/Sophia (Rank 0)/Field (Rank 0)/' src/omega/oracle/hierarchy.py
```

#### I. oracle.py — Remove CONTAINING_FIELD Role (line 87)
```bash
sed -i '87d' src/omega/oracle/oracle.py
```

### 1.2.4 Verification
```bash
# Should return ZERO matches
grep -r "Sophia\|CONTAINING_FIELD" src/omega/ --include="*.py" || echo "✅ CLEAN - No Sophia in engine core"

# Check dispatch.yaml
grep -c "sophia" config/wads/_omega_default/entities/dispatch.yaml || echo "✅ CLEAN - No Sophia in dispatch.yaml"

# Check hierarchy.yaml
grep -c "sophia" config/wads/_omega_default/hierarchy.yaml || echo "✅ CLEAN - No Sophia in hierarchy.yaml"
```

### 1.2.5 Temple-Grade
```bash
make temple-grade
```

---

## 🛠️ STEP 1.3 — PURGE N1-N10 → S1-S10

### 1.3.1 Files to Modify (20+ files)

**CRITICAL**: Replace `N1`→`S1`, `N2`→`S2`, ..., `N10`→`S10` in ALL contexts EXCEPT:
- `ZEN2_*`, `ZEN3_*` constants (CPU cache/core/thread constants)
- Variable names like `node_count`, `node_id` (if they refer to physical nodes)
- Comments referencing hardware topology

### 1.3.2 Backup All Files
```bash
FILES=(
  "src/omega/audit/firewall_checker.py"
  "src/omega/audit/mandate_auditor.py"
  "src/omega/cvar_table.py"
  "src/omega/research/sandboxes/ml_training.py"
  "src/omega/research/sandbox.py"
  "src/omega/research/types.py"
  "src/omega/governance/budget_guard.py"
  "src/omega/governance/sovereignty_gate.py"
  "src/omega/governance/__init__.py"
  "src/omega/coordination/__init__.py"
  "src/omega/integrations/__init__.py"
  "src/omega/soul/lessons.py"
  "src/omega/cli/fleet_status_tui.py"
  "src/omega/oracle/entity_registry.py"
  "src/omega/oracle/feed_utils.py"
  "src/omega/oracle/model_gateway.py"
  "src/omega/oracle/capability_matrix.py"
  "src/omega/oracle/sentinel.py"
  "src/omega/oracle/link_p9_runtime.py"
  "src/omega/oracle/backends/google_compat.py"
)

for f in "${FILES[@]}"; do
  cp "$f" "$f.backup.$(date +%s)"
done
```

### 1.3.3 Execute Replacements

#### A. Header Comments (First 10 lines of each file)
```bash
for f in "${FILES[@]}"; do
  # Replace N1-N10 in headers only (first 15 lines)
  sed -i '1,15s/\bN\([1-9]\|10\)\b/S\1/g' "$f"
done
```

#### B. Specific File Fixes

**cvar_table.py** — LinkN9Runtime → LinkS9Runtime, N5→S5, N7→S7, N9→S9
```bash
sed -i 's/LinkN9Runtime/LinkS9Runtime/g' src/omega/cvar_table.py
sed -i 's/\bN5\b/S5/g' src/omega/cvar_table.py
sed -i 's/\bN7\b/S7/g' src/omega/cvar_table.py
sed -i 's/\bN9\b/S9/g' src/omega/cvar_table.py
```

**entity_registry.py** — Migration comment line 417-418
```bash
sed -i "s/nodes: \['N1: Flesh'\]/slots: ['S1']/g" src/omega/oracle/entity_registry.py
sed -i "s/nodes: \['1'\]/slots: ['S1']/g" src/omega/oracle/entity_registry.py
```

**feed_utils.py** — Header N9:LINK → S9:LINK
```bash
sed -i 's/N9:LINK/S9:LINK/' src/omega/oracle/feed_utils.py
```

**model_gateway.py** — N3→S3, N6→S6
```bash
sed -i 's/\bN3\b/S3/g' src/omega/oracle/model_gateway.py
sed -i 's/\bN6\b/S6/g' src/omega/oracle/model_gateway.py
```

**sentinel.py** — N5→S5
```bash
sed -i 's/\bN5\b/S5/g' src/omega/oracle/sentinel.py
```

**link_p9_runtime.py** — RENAME CLASS and all references
```bash
# This is the big one - class name and all references
sed -i 's/LinkN9Runtime/LinkS9Runtime/g' src/omega/oracle/link_p9_runtime.py
sed -i 's/Link N9/Link S9/g' src/omega/oracle/link_p9_runtime.py
sed -i 's/link_n9/link_s9/g' src/omega/oracle/link_p9_runtime.py
sed -i 's/LINK_N9/LINK_S9/g' src/omega/oracle/link_p9_runtime.py
```

**coordination/__init__.py** — N4→S4
```bash
sed -i 's/\bN4\b/S4/g' src/omega/coordination/__init__.py
```

**integrations/__init__.py** — N4→S4, N5→S5
```bash
sed -i 's/\bN4\b/S4/g' src/omega/integrations/__init__.py
sed -i 's/\bN5\b/S5/g' src/omega/integrations/__init__.py
```

**fleet_status_tui.py** — N1→S1 (specialist terminology)
```bash
sed -i 's/\bN1\b/S1/g' src/omega/cli/fleet_status_tui.py
```

### 1.3.4 Verification
```bash
# Should return ZERO engine-relevant matches (ZEN2/3 constants allowed)
grep -r "\bN\([1-9]\|10\)\b" src/omega/ --include="*.py" | grep -v "ZEN2\|ZEN3\|cache\|core\|thread\|core_" || echo "✅ CLEAN - No N1-N10 in engine core"

# Verify LinkS9Runtime exists
grep -r "LinkS9Runtime" src/omega/ --include="*.py" | head -5

# Verify S1-S10 present
grep -r "\bS\([1-9]\|10\)\b" src/omega/ --include="*.py" | head -10
```

### 1.3.5 Temple-Grade
```bash
make temple-grade
```

---

## 🛠️ STEP 1.4 — FIX DISPATCH.YAML

### 1.4.1 Backup
```bash
cp config/wads/_omega_default/entities/dispatch.yaml config/wads/_omega_default/entities/dispatch.yaml.backup.$(date +%s)
```

### 1.4.2 Write Clean dispatch.yaml
```bash
cat > config/wads/_omega_default/entities/dispatch.yaml << 'EOF'
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Subagent Dispatch Configuration (WAD-Loaded)
# ⬡ OMEGA ⬡ DISPATCH ⬡ M2-COMPLIANT
#
# Defines agent capability registry loaded at runtime by
# src/omega/oracle/subagent_dispatcher.py. Entity names live HERE (WAD content),
# not in engine core. M2 Firewall Phase B.
#
# Schema:
#   entities:
#     - name:          lowercase agent key (used as CAPABILITY_REGISTRY key)
#       role:          ROLE_CONSTANT (GRAND_OVERSIGHT | BUILD_OVERSOUL | RUNTIME_OVERSOUL | S1-S10)
#       mode:          "primary" | "subagent"
#       purpose:       human-readable description
#       capabilities:  list of capability strings
#       domains:       list of domain strings
#       slot:          "SX" for slot-based agent, null otherwise
#       task_tool_type: general | buildmaster | verity | node | explore
#       owned_files:   list of file paths
#       model:         default model for this agent

entities:
  # Engine Core Triad + M3 (4) — ALWAYS
  - name: "kali"
    role: "GRAND_OVERSIGHT"
    mode: "primary"
    purpose: "Grand Oversight — Sees all, delegates, destroys drift"
    capabilities: ["oversight", "delegation", "strategy", "drift_destruction"]
    domains: ["strategy", "fleet_management", "architecture"]
    slot: null
    task_tool_type: "general"
    owned_files: []
    model: "qwen3-4b-think-q4_k_m"

  - name: "maat"
    role: "BUILD_OVERSOUL"
    mode: "subagent"
    purpose: "Build Oversoul — Governs S1-S5 on the build side"
    capabilities: ["oversight_build", "build_governance", "hardening"]
    domains: ["build_side", "S1", "S2", "S3", "S4", "S5"]
    slot: null
    task_tool_type: "buildmaster"
    owned_files: []
    model: "qwen3-4b-think-q4_k_m"

  - name: "lilith"
    role: "RUNTIME_OVERSOUL"
    mode: "subagent"
    purpose: "Runtime Oversoul — Governs S6-S10 (Cognition through Validation) on the run side"
    capabilities: ["oversight_runtime", "run_governance", "operations", "vision_oversight", "knowledge_metabolism"]
    domains: ["run_side", "S6", "S7", "S8", "S9", "S10"]
    slot: null
    task_tool_type: "general"
    owned_files: []
    model: "qwen3-4b-think-q4_k_m"

  - name: "iris"
    role: "MESSENGER_BRIDGE"
    mode: "subagent"
    purpose: "Messenger Bridge — Speculative decoder, fast-path query resolution"
    capabilities: ["speculative_decode", "intent_matching", "fast_path_routing"]
    domains: ["routing", "intent_detection", "fast_path"]
    slot: null
    task_tool_type: "general"
    owned_files:
      - "src/omega/iris/"
    model: "qwen3-1.7b-q4_k_m"

  # Proven Dedicated Slot Keeper (1)
  - name: "carmack"
    role: "S3_DEDICATED_KEEPER"
    mode: "primary"
    purpose: "Sovereign S3 Consultant — Architectural review & performance optimization (S3 Engineering)"
    capabilities: ["architectural_review", "performance_audit", "code_optimization", "right_approximation"]
    domains: ["architecture", "performance", "code_quality", "heritage_engineering"]
    slot: "S3"
    task_tool_type: "general"
    owned_files: []
    model: "qwen3-4b-think-q4_k_m"

  # Dispatched Capabilities (6)
  - name: "roc_racoon"
    role: "LEGACY_MINER"
    mode: "primary"
    purpose: "Sovereign Miner — Legacy archaeology & pattern extraction"
    capabilities: ["legacy_mining", "pattern_extraction", "archaeology"]
    domains: ["legacy_repos", "grok_exports", "old_stacks", "document_analysis"]
    slot: null
    task_tool_type: "explore"
    owned_files:
      - "data/entities/roc_racoon/"
    model: "qwen3-4b-think-q4_k_m"

  - name: "jem"
    role: "RESEARCH_ORCHESTRATOR"
    mode: "primary"
    purpose: "Research Orchestrator — 3-phase pipeline (Discovery → Synthesis → Verification) with self-dispatch"
    capabilities: ["research_orchestration", "discovery", "synthesis", "verification", "knowledge_synthesis"]
    domains: ["research", "knowledge_pipeline", "source_verification"]
    slot: null
    task_tool_type: "general"
    owned_files:
      - "data/entities/jem/"
      - "data/coordination/JEM_*"
    model: "qwen3-4b-think-q4_k_m"

  - name: "makali"
    role: "COUNCIL_ORCHESTRATOR"
    mode: "primary"
    purpose: "Triad Council Orchestrator — Parallel dispatch with synthesis"
    capabilities: ["parallel_decomposition", "council_dispatch", "maat_lilith_synthesis"]
    domains: ["fleet_coordination", "parallel_execution", "cross_node_synthesis"]
    slot: null
    task_tool_type: "general"
    owned_files: []
    model: "qwen3-4b-think-q4_k_m"

  - name: "verity"
    role: "COMPLIANCE_GNOSIS"
    mode: "subagent"
    purpose: "Sovereign Verity — Unified Sentry (compliance/audit) + Scribe (gnosis distillation/soul evolution)"
    capabilities:
      - "gnosis_distillation"
      - "soul_update"
      - "abstraction"
      - "code_review"
      - "stress_testing"
      - "mandate_enforcement"
      - "temple_grade_audit"
      - "skeptical_verification"
      - "knowledge_compaction"
    domains: ["soul_yaml", "session_gnosis", "verification", "qa", "compliance", "verity"]
    slot: null
    task_tool_type: "verity"
    owned_files:
      - "data/entities/*/soul.yaml"
    model: "qwen3-4b-think-q4_k_m"

  - name: "doom_guy"
    role: "HERITAGE_ATTRIBUTION"
    mode: "primary"
    purpose: "Sovereign id Software Architect — WAD translation & performance"
    capabilities: ["heritage_design", "wad_translation", "performance_tuning", "c_const_propagation"]
    domains: ["id_software_patterns", "architecture", "constants", "heritage_attribution"]
    slot: null
    task_tool_type: "general"
    owned_files:
      - "src/omega/cvar_table.py"
      - "src/omega/constants.py"
      - "CREDITS.md"
      - "docs/strategy/HERITAGE_SOURCE_MAP.md"
    model: "qwen3-4b-think-q4_k_m"

  - name: "researcher"
    role: "DEEP_RESEARCH"
    mode: "primary"
    purpose: "Sovereign Master Researcher — deep research, lattice reasoning"
    capabilities: ["deep_research", "lattice_reasoning", "web_search", "source_verification"]
    domains: ["research", "web_intelligence", "documentation"]
    slot: null
    task_tool_type: "general"
    owned_files: []
    model: "qwen3-4b-think-q4_k_m"

  # Template (1)
  - name: "slot"
    role: "S1"
    mode: "subagent"
    purpose: "Slot-based domain agent — parameterized by --slot SX"
    capabilities: ["domain_execution", "slot_dispatch"]
    domains: ["slot_domain"]
    slot: "SX"
    task_tool_type: "slot"
    owned_files: []
    model: "qwen3-4b-think-q4_k_m"
EOF
```

### 1.4.3 Verification
```bash
# Count entities - should be 11
python3 -c "
import yaml
d = yaml.safe_load(open('config/wads/_omega_default/entities/dispatch.yaml'))
print(f'Entity count: {len(d[\"entities\"])}')
for e in d['entities']:
    print(f'  {e[\"name\"]}: role={e[\"role\"]} slot={e.get(\"slot\")}')
"

# Verify no S1 role collisions (except slot template)
python3 -c "
import yaml
d = yaml.safe_load(open('config/wads/_omega_default/entities/dispatch.yaml'))
s1_count = sum(1 for e in d['entities'] if e['role'] == 'S1')
print(f'Entities with role=S1: {s1_count} (should be 1: slot template)')
"
```

### 1.4.4 Temple-Grade
```bash
make temple-grade
```

---

## 🛠️ STEP 1.5 — UPDATE ROLE_CONSTANTS

### 1.5.1 Files to Modify
1. `src/omega/oracle/subagent_dispatcher.py` (lines ~251-265)
2. `src/omega/ics.py` (lines ~71-88)

### 1.5.2 Backup
```bash
cp src/omega/oracle/subagent_dispatcher.py src/omega/oracle/subagent_dispatcher.py.backup.$(date +%s)
cp src/omega/ics.py src/omega/ics.py.backup.$(date +%s)
```

### 1.5.3 Update subagent_dispatcher.py
```bash
# Find the ROLE_CONSTANTS dict and replace entirely
# First, locate the exact line range
grep -n "ROLE_CONSTANTS" src/omega/oracle/subagent_dispatcher.py | head -5
```

**Then replace the entire dict** (use Python for precision):
```python
# Save as /tmp/update_role_constants.py
import re

with open('src/omega/oracle/subagent_dispatcher.py', 'r') as f:
    content = f.read()

new_constants = '''ROLE_CONSTANTS: Dict[str, str] = {
    # Engine Core Governance
    "GRAND_OVERSIGHT": "grand_oversight",      # Kali
    "BUILD_OVERSOUL": "build_oversoul",        # Ma'at → S1-S5
    "RUNTIME_OVERSOUL": "runtime_oversoul",    # Lilith → S6-S10
    "MESSENGER_BRIDGE": "messenger_bridge",    # Iris (M3)
    
    # Proven Slot Keeper
    "S3_DEDICATED_KEEPER": "s3_dedicated_keeper",  # Carmack
    
    # Dispatched Capabilities
    "LEGACY_MINER": "legacy_miner",
    "RESEARCH_ORCHESTRATOR": "research_orchestrator",
    "COUNCIL_ORCHESTRATOR": "council_orchestrator",
    "COMPLIANCE_GNOSIS": "compliance_gnosis",
    "HERITAGE_ATTRIBUTION": "heritage_attribution",
    "DEEP_RESEARCH": "deep_research",
    
    # Slot Semantics (Neutral Engineering Terms)
    "S1": "infrastructure",
    "S2": "persistence",
    "S3": "engineering",
    "S4": "integration",
    "S5": "governance",
    "S6": "cognition",
    "S7": "context",
    "S8": "observability",
    "S9": "orchestration",
    "S10": "validation",
}'''

# Replace the entire ROLE_CONSTANTS dict
pattern = r'ROLE_CONSTANTS: Dict\[str, str\] = \{[^}]+\}'
content = re.sub(pattern, new_constants, content, flags=re.DOTALL)

with open('src/omega/oracle/subagent_dispatcher.py', 'w') as f:
    f.write(content)

print("✅ Updated subagent_dispatcher.py")
```

```bash
python3 /tmp/update_role_constants.py
```

### 1.5.4 Update ics.py
```bash
# Find ROLE_CONSTANTS in ics.py
grep -n "ROLE_CONSTANTS" src/omega/ics.py
```

```python
# Save as /tmp/update_ics_constants.py
import re

with open('src/omega/ics.py', 'r') as f:
    content = f.read()

new_constants = '''ROLE_CONSTANTS = {
    "GRAND_OVERSIGHT": "grand_oversight",
    "BUILD_OVERSOUL": "build_oversoul",
    "RUNTIME_OVERSOUL": "runtime_oversoul",
    "MESSENGER_BRIDGE": "messenger_bridge",
    "S3_DEDICATED_KEEPER": "s3_dedicated_keeper",
    "LEGACY_MINER": "legacy_miner",
    "RESEARCH_ORCHESTRATOR": "research_orchestrator",
    "COUNCIL_ORCHESTRATOR": "council_orchestrator",
    "COMPLIANCE_GNOSIS": "compliance_gnosis",
    "HERITAGE_ATTRIBUTION": "heritage_attribution",
    "DEEP_RESEARCH": "deep_research",
    "S1": "infrastructure",
    "S2": "persistence",
    "S3": "engineering",
    "S4": "integration",
    "S5": "governance",
    "S6": "cognition",
    "S7": "context",
    "S8": "observability",
    "S9": "orchestration",
    "S10": "validation",
}'''

pattern = r'ROLE_CONSTANTS = \{[^}]+\}'
content = re.sub(pattern, new_constants, content, flags=re.DOTALL)

with open('src/omega/ics.py', 'w') as f:
    f.write(content)

print("✅ Updated ics.py")
```

```bash
python3 /tmp/update_ics_constants.py
```

### 1.5.5 Verification
```bash
# Check both files match exactly
echo "=== subagent_dispatcher.py ==="
grep -A 25 "ROLE_CONSTANTS" src/omega/oracle/subagent_dispatcher.py | head -30

echo "=== ics.py ==="
grep -A 25 "ROLE_CONSTANTS" src/omega/ics.py | head -30

# Verify no old roles remain
grep -r "CONTAINING_FIELD\|S1_DEDICATED_KEEPER\|LATTICE_" src/omega/oracle/subagent_dispatcher.py src/omega/ics.py || echo "✅ No old roles"
```

### 1.5.6 Temple-Grade
```bash
make temple-grade
```

---

## 🛠️ STEP 1.6 — FIX _OMEGA_DEFAULT HIERARCHY.YAML

### 1.6.1 Backup
```bash
cp config/wads/_omega_default/hierarchy.yaml config/wads/_omega_default/hierarchy.yaml.backup.$(date +%s)
```

### 1.6.2 Verify Current State
```bash
cat config/wads/_omega_default/hierarchy.yaml
```

### 1.6.3 Ensure Clean Neutral Skin
The file should already be mostly correct (software company metaphor). Verify:
- No `sophia` block (deleted in 1.2)
- No `P1-P10` references (should be `N1-N10` or `S1-S10`)
- `kali_founder`, `maat_cto`, `lilith_ciso` present
- `governs_nodes: [N1, N2, N3, N4, N5]` → change to `[S1, S2, S3, S4, S5]`
- `governs_nodes: [N6, N7, N8, N9, N10]` → change to `[S6, S7, S8, S9, S10]`
- `keepers:` section uses `N1:` → change to `S1:`

### 1.6.4 Execute Fixes
```bash
# Replace N1-N10 with S1-S10 in hierarchy.yaml
sed -i 's/\bN\([1-9]\|10\)\b/S\1/g' config/wads/_omega_default/hierarchy.yaml

# Verify sophia is gone
grep -c "sophia" config/wads/_omega_default/hierarchy.yaml || echo "✅ No Sophia"
```

### 1.6.5 Verification
```bash
cat config/wads/_omega_default/hierarchy.yaml
# Should show clean neutral skin with S1-S10
```

### 1.6.6 Temple-Grade
```bash
make temple-grade
```

---

## ✅ PHASE 1 COMPLETION CHECKLIST

Run ALL verification commands. All must pass.

```bash
echo "=== PHASE 1 VERIFICATION ==="

echo "1.1 Slot entities removed:"
grep -E "sysadmin|datastore|buildmaster|bridge|sentinel|modelgate|context|watchtower|link|verifier" config/wads/_omega_default/entities.yaml || echo "✅ PASS"

echo "1.2 Sophia removed from engine core:"
grep -r "Sophia\|CONTAINING_FIELD" src/omega/ --include="*.py" || echo "✅ PASS"
grep -c "sophia" config/wads/_omega_default/entities/dispatch.yaml || echo "✅ PASS"
grep -c "sophia" config/wads/_omega_default/hierarchy.yaml || echo "✅ PASS"

echo "1.3 N1-N10 purged:"
grep -r "\bN\([1-9]\|10\)\b" src/omega/ --include="*.py" | grep -v "ZEN2\|ZEN3\|cache\|core\|thread\|core_" || echo "✅ PASS"

echo "1.4 dispatch.yaml clean (11 entities):"
python3 -c "
import yaml
d = yaml.safe_load(open('config/wads/_omega_default/entities/dispatch.yaml'))
print(f'Count: {len(d[\"entities\"])} (expected 11)')
"

echo "1.5 ROLE_CONSTANTS updated:"
grep -c "S3_DEDICATED_KEEPER" src/omega/oracle/subagent_dispatcher.py && echo "✅ PASS"
grep -c "LEGACY_MINER" src/omega/oracle/subagent_dispatcher.py && echo "✅ PASS"

echo "1.6 hierarchy.yaml clean:"
grep -c "S1\|S2\|S3\|S4\|S5\|S6\|S7\|S8\|S9\|S10" config/wads/_omega_default/hierarchy.yaml && echo "✅ PASS"

echo "=== TEMPLE-GRADE ==="
make temple-grade && echo "✅ TEMPLE-GRADE PASSES"

echo "=== MANDATE COMPLIANCE ==="
make check-mandate-compliance
```

---

## 🚨 IF ANY VERIFICATION FAILS

1. **STOP** — Do not proceed to next step
2. **CHECK BACKUPS** — Restore from `.backup.*` if needed
3. **RE-RUN** the failed step
4. **ASK SUPERVISOR** if uncertain

---

## 📝 EXECUTION LOG

Executor must log each step completion:

```bash
# After each step, append to execution log
echo "$(date -Iseconds) | STEP 1.X | STATUS=PASS" >> /tmp/phase1_execution.log
```

---

**END OF PHASE 1 EXECUTION GUIDE**

*Next: Phase 2 — Transfer ANAi WAD to USB (after Phase 1 complete and verified)*

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ nemotron-3-ultra-free ⬡ trc_phase1_exec_guide ⬡ 2026-09-10*