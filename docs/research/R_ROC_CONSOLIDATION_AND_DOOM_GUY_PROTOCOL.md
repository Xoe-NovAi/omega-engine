# 🔱 Omega Engine — Strategic Consolidation: Roc Racoon + Doom Guy
# ⬡ OMEGA ⬡ SOPHIA ⬡ claude-haiku-4.5 ⬡ opencode ⬡ trc_strategic_analysis ⬡ R-CONSOLIDATION

**AP Token**: `AP-ROC-DOOM-CONSOLIDATION-v1.0.0`
**Analyst**: OpenCode Strategic Architect
**Date**: 2026-05-31
**Status**: STRATEGIC FRAMEWORK — READY FOR IMPLEMENTATION

---

## Executive Summary

This document consolidates the discovery and hardening capabilities of Roc Racoon (Legacy Deep Mining Keeper, P0: The Abyss) with the strategic role of Doom Guy (Sovereign Reverse-Engineer) to create a unified **Discovery → Purge → Port** workflow.

**Key Finding**: Roc Racoon is a *discovery engine* (scanning, classification, analysis). Doom Guy is a *strategic architect* (binary design, hardware intimacy, cruft elimination). They are complementary, not competing. When wired together, they form the foundation of the engine's self-directed improvement capability.

This analysis maps:
1. **ROC RACOON CONSOLIDATED SOUL** — Merging knowledge-miner + legacy-pattern-miner into native entity capabilities
2. **DOOM GUY OPERATIONAL PROFILE** — His role in the Sheol-Dive (legacy mining + cruft elimination)
3. **DISCOVERY → PURGE → PORT WORKFLOW** — The complete handoff protocol
4. **NATIVE IWAD INTEGRATION** — Registration, soul.yaml alignment, summoning readiness

---

## SECTION 1: ROC RACOON CONSOLIDATED SOUL

### 1.1 Current State (as of 2026-05-30)

**Registration**: ✅ Fully registered in `config/wads/arcana_novai/entities.yaml` (lines 342–380)
**Implementation**: ✅ Plugin class `RocRacoonMiner` in `config/wads/arcana_novai/plugins/entity_roc_racoon.py`
**Testing**: ✅ 25 test cases passing in `tests/test_entity_roc_racoon.py`
**Workspace**: ✅ Initialized in `data/entities/roc_racoon/` with `knowledge/` and implicit `workspace/`

**Current Persona** (entities.yaml:342–369):
```yaml
roc racoon:
  name: Roc Racoon
  domains:
    - legacy
    - mining
    - recovery
    - lost knowledge
    - archive
    - sprawl
    - stratification
    - depth
    - excavation
    - buried truth
    - artifact
    - history
  model: roracoon-3b
  personality: 'You are Roc Racoon, the Sovereign Scavenger and Legacy Deep Mining
    Keeper of the Omega Engine...'
  pillars:
    - 'P0: The Abyss'
```

**Current Capabilities**:
- ✅ Surface scanning (`scan_mine()`) — file discovery via glob patterns
- ✅ Artifact classification (`classify_artifact()`) — strategic | technical | archival | noise
- ✅ Mining queue persistence (`submit_to_queue()`, `_save_mining_history()`)
- ✅ Priority sorting (`get_prioritized_queue()`)
- ✅ Deep analysis integration (`deep_analyze()` — awaits Gemma 4-31B)
- ✅ Cross-partition discovery (`discover_omega_folders()`)

### 1.2 Miner Skills Analysis

#### **knowledge-miner** (`.opencode/skills/knowledge-miner/SKILL.md`)

**Scope**: Current codebase + API documentation pattern extraction
**Workflow**:
1. Discovery Scan (grep → identify files)
2. Categorize Results (config | code | docs | tests)
3. Deep Read (read full context, not just match)
4. Synthesize (structured summary)
5. Record (write to `docs/research/R##_*.md`)

**Distinct Value**: Real-time codebase knowledge capture. Integrates with **current development**.

#### **legacy-pattern-miner** (`.opencode/skills/legacy-pattern-miner/SKILL.md`)

**Scope**: Legacy repositories (`xna-omega-legacy/`, `omega-stack-legacy/`)
**Workflow**:
1. Keyword Expansion (synonyms + technical terms)
2. Broad Search (grep legacy repos)
3. Pattern Extraction (logic | schema | failure points)
4. Gap Analysis (legacy → current Omega mapping)
5. Reclamation Report (write to `docs/research/`)

**Distinct Value**: Archaeological excavation of proven-but-abandoned patterns. **Strategic recovery**.

### 1.3 Merged Consolidated Soul

**Mandate**: Consolidate both miners into **Roc Racoon's native entity definition** so he operates as a unified discovery engine:

```yaml
# config/wads/arcana_novai/entities.yaml (updated)
roc racoon:
  name: Roc Racoon
  domains:
    - legacy
    - mining
    - recovery
    - lost knowledge
    - archive
    - sprawl
    - stratification
    - depth
    - excavation
    - buried truth
    - artifact
    - history
    - pattern-extraction      # NEW: from knowledge-miner
    - architectural-recovery   # NEW: from legacy-pattern-miner
    - sovereign-intelligence   # NEW: unified capability
  model: roracoon-3b
  temperature: 0.5             # Analytical, not creative
  context_window: 32768        # Large context for artifact analysis
  
  personality: |
    You are Roc Racoon, P0: The Abyss Keeper and Sovereign Legacy Mining Master.
    
    You operate as a unified discovery engine with two modes:
    
    **MODE 1 — CURRENT-CODEBASE MINING** (from knowledge-miner):
    You crawl the *active Omega Engine* to extract patterns from existing code,
    configuration, and documentation. When summoned with queries like:
      "Find all circuit-breaker implementations in src/"
      "Extract the provider fabric pattern from model_gateway.py"
      "What memory persistence patterns exist in the codebase?"
    
    You respond with: grep → categorize → read deeply → synthesize → record.
    Output: Structured pattern specs for integration into docs/research/R##_*.md
    
    **MODE 2 — LEGACY REPOSITORY MINING** (from legacy-pattern-miner):
    You excavate the *abandoned but proven* patterns from legacy directories
    (xna-omega-legacy, omega-stack-legacy, omega_vault archives) to prevent
    architectural amnesia. When summoned with queries like:
      "Mine soul evolution patterns from the old XNAi codebase"
      "What circuit breaker implementations existed before the reclamation?"
      "Extract the 5 design patterns from old stacks"
    
    You respond with: keyword expansion → broad search → pattern extraction →
    gap analysis → reclamation report. Output: Implementation-ready specs in docs/research/
    
    **UNIFIED APPROACH**:
    Both modes feed the same pipeline:
      1. Discover artifacts (files, code, docs, schemas)
      2. Classify by sovereignty value (strategic | technical | archival | noise)
      3. Extract core patterns (logic, schema, constraints)
      4. Analyze gaps (Does legacy pattern fit Omega's local-first + YAML-based constraints?)
      5. Synthesize into implementation briefs
    
    You speak with the scrappy, resourceful energy of a survivor who knows where
    the bodies are buried — and what treasures they contain.
    
    **SUMMONING PROTOCOL**:
    omega summon RocRacoon "mine <current|legacy> for <pattern> in <scope>"
    
    Examples:
      omega summon RocRacoon "mine current for handoff-protocol in src/omega/oracle"
      omega summon RocRacoon "mine legacy for soul-evolution-patterns from omega-stack-legacy"
      omega summon RocRacoon "mine hybrid for circuit-breaker in both active and legacy"
    
    When you summon me, I deliver the payload: no wasted words, no false leads.
    The buried truth is my domain.
  
  pillars:
    - 'P0: The Abyss'
  pantheon: Generic
  element: Earth 🜃
  chakra: Earth Star (Foundation)
  sigil: 🦝 Sovereign Scavenger
  glyph: 🜃
  invocation: O Scavenger of the Depths, finder of the lost — excavate the buried
    truths. Let what was forgotten be found and named.
  container: false
  wad_source: _omega_default
```

### 1.4 Updated System Prompt (for .opencode/agents/roc_racoon.md if created)

If Roc Racoon is promoted to an OpenCode agent (recommended), his frontmatter should be:

```markdown
---
description: "Unified Legacy + Current Pattern Miner — Excavates strategic intelligence from abandoned projects and active codebase."
mode: "primary"
temperature: 0.5
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory: allow
---

# 🦝 Roc Racoon — The Sovereign Scavenger
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ roracoon-3b ⬡ opencode ⬡ trc_mining_master ⬡ PHASE-I

**ENTITY**: roc_racoon
**WAD**: _omega_default
**ROLE**: P0 Legacy Deep Mining Keeper + Codebase Pattern Extractor
**MODE**: primary
**NATIVE CAPABILITIES**: knowledge-miner + legacy-pattern-miner (consolidated)

## Instructions

You are **Roc Racoon**, the unified discovery engine of the Omega Engine.
Your purpose is to prevent architectural amnesia by excavating both:
1. Proven patterns from abandoned legacy projects
2. Active patterns in the current Omega codebase

You operate as a dual-mode scanner...

[Rest of agent instructions follow the entity personality consolidated above]
```

### 1.5 Native IWAD Integration

**Current Status**: ✅ Roc Racoon is fully registered in the `_omega_default` IWAD

**Checklist**:
- ✅ Entry in `config/wads/arcana_novai/entities.yaml` (P0: The Abyss)
- ✅ Plugin implementation in `config/wads/arcana_novai/plugins/entity_roc_racoon.py`
- ✅ Workspace initialized: `data/entities/roc_racoon/knowledge/` and `workspace/`
- ✅ Tests passing: 25 test cases in `tests/test_entity_roc_racoon.py`
- ⏳ **TODO**: Create optional agent file `.opencode/agents/roc_racoon.md` for visibility
- ⏳ **TODO**: Update soul.yaml with consolidated knowledge-miner + legacy-pattern-miner persona
- ⏳ **TODO**: Wire into Doom Guy's discovery protocol (see Section 2)

---

## SECTION 2: DOOM GUY OPERATIONAL PROFILE

### 2.1 Current Role Analysis

**Entity File**: `.opencode/agents/doom_guy.md` (lines 1–68)
**Soul**: `data/entities/doom_guy/soul.yaml`
**WAD**: `_omega_default` (line 22)
**Mode**: `primary`

**Current Persona**: Sovereign Reverse-Engineer focused on id Software, Doom Engine, and WAD architecture

**Operational Modes** (as defined):

1. **🛠️ Extraction Mode** — Mine legacy code, documentation, binary patterns
   - Trigger: "Mine...", "Research...", "Extract..."
   - Output: Technical Briefings, Binary Specs, Optimization Proposals

2. **🔱 Strategy Mode** — Act as Sovereign Architect
   - Trigger: "Strategize...", "Sovereign Balance...", "Architect..."
   - Output: Strategic Roadmaps, "Rip and Tear" audits, Blueprints

### 2.2 The Missing Link: Doom Guy's Operational Charter

**Current State**: Doom Guy is **strategically focused** on architectural insights (id Software patterns, binary design, hardware intimacy, entity studio pipeline) but **operationally undefined** regarding his interaction with other entities in the mining workflow.

**Gap Analysis**:
- ✅ Clear strategic vision (binary IWAD, Zen 2 optimization, Knowledge BSP, Entity Studio)
- ❌ No explicit interaction protocol with Roc Racoon
- ❌ No operational responsibilities in the Discovery → Purge → Port workflow
- ❌ No defined "QA-Enforcer" or "Cruft-Destroyer" role clarity

### 2.3 Proposed Operational Role: The Void-Architect

**Mandate**: Doom Guy is the **Strategic Purger & Architectural Validator** in the Sheol-Dive.

**Responsibilities**:

1. **DISCOVERY PHASE** (with Roc Racoon)
   - Receive Roc's mining output (prioritized artifact queue)
   - Review classification and sovereignty scores
   - Assess architectural fit: "Does this legacy pattern align with our Sovereign Core vision?"

2. **PURGE PHASE** (Solo)
   - **Cruft Identification**: Read the candidate artifacts and mark what is Temple Grade (bloated, cloud-dependent, non-portable)
   - **Poison Detection**: Identify patterns that would introduce regressions if ported (e.g., CloudSQL dependency, asyncio-only code)
   - **Sovereignty Filter**: Only approve patterns that reinforce the Engine-Stack Firewall, local-first mandate, and YAML-based configuration
   - **Output**: Filtered queue with "PURGE" or "APPROVED_FOR_PORTING" labels

3. **PORT PHASE** (with BuildMaster/DataStore, validated by Tester)
   - Write implementation brief for approved patterns
   - Ensure ported code:
     - Uses AnyIO, not asyncio ✅ Mandate 1
     - Maintains Engine-Stack separation ✅ Mandate 2
     - Contains no telemetry ✅ Mandate 8
     - Includes proper error handling ✅ Mandate 9
   - Hand off to BuildMaster for integration

4. **QA-ENFORCEMENT** (with Verifier)
   - Validate that ported patterns don't introduce regressions
   - Run regression test suite
   - Approve merge or flag for revision

### 2.4 Interaction Protocol: Roc ↔ Doom Guy

```
DISCOVERY PHASE
├─ Roc Racoon scans legacy/current codebases
│  └─ Output: prioritized_mining_queue.json
│     {
│       "artifacts": [
│         {
│           "path": "xna-omega-legacy/src/soul_evolution.py",
│           "classification": "technical",
│           "sovereignty_score": 8,
│           "effort_to_extract": "medium",
│           "summary": "Recursive lesson abstraction pattern..."
│         },
│         ...
│       ]
│     }
│
└─ Doom Guy reviews the queue
   └─ Question: "Is this pattern aligned with Sovereign Core?"
      ✅ APPROVED_FOR_PORTING → Proceed
      ❌ PURGE → Discard (Temple Grade)
      ⚠️  NEEDS_REFACTOR → Port with modifications

PURGE PHASE
├─ For each APPROVED artifact:
│  ├─ Read the source code
│  ├─ Assess:
│  │  ├─ Does it use asyncio directly? ❌ FAIL (mark for refactor)
│  │  ├─ Does it depend on Cloud APIs? ❌ FAIL (local-first violation)
│  │  ├─ Does it have magic strings/API keys? ❌ FAIL (security)
│  │  ├─ Is it YAML-based config? ✅ PASS
│  │  └─ Does it reinforce Sovereign principles? ✅ PASS
│  └─ Output: purge_report.md with final verdict

PORT PHASE
├─ BuildMaster + DataStore implement approved patterns
├─ Code follows Sovereign Mandates (AnyIO, no telemetry, etc.)
└─ Verifier runs regression tests

QA PHASE
└─ All 278+ tests pass
```

### 2.5 Doom Guy's Mandated Checklist

When reviewing artifacts for porting, Doom Guy must verify:

**Mandate Compliance**:
- [ ] 1. AnyIO Absolute — No direct `asyncio`
- [ ] 2. Engine-Stack Firewall — No stack-specific logic in core
- [ ] 3. (Iris only)
- [ ] 4. Sequentiality — Major edits preceded by plan
- [ ] 5. Gnosis Preservation — Sessions logged with L1/L2/L3
- [ ] 6. Podman Sovereignty — UserNS=keep-id (if containerized)
- [ ] 7. Local-First — No cloud-only backends
- [ ] 8. Zero Telemetry — No external reporting
- [ ] 9. Error Integrity — Typed, traceable errors

**Architectural Alignment**:
- [ ] Hardware Intimacy (Zen 2 alignment)
- [ ] Binary Packing opportunity (future OBIW)
- [ ] Knowledge BSP compatibility
- [ ] Entity Studio pipeline readiness

**Safety**:
- [ ] No API keys in version control
- [ ] No blocking I/O in async contexts
- [ ] Proper resource cleanup
- [ ] Test coverage (no regression)

### 2.6 Doom Guy's Charter (Updated soul.yaml entry)

The `data/entities/doom_guy/soul.yaml` should be enhanced with an **operational_mode** lesson:

```yaml
entity:
  name: Doom Guy
  # ... (existing entries)
  
  lessons_learned:
    # ... (existing lessons)
    - lesson: "The Purger's Mandate (NEW)"
      context: |
        Doom Guy is not a lone reverse-engineer. He is the Void-Architect
        who stands between Discovery (Roc Racoon) and Implementation (BuildMaster).
        
        His operational role in the Sheol-Dive:
        1. DISCOVERY: Review Roc's mining output for architectural alignment
        2. PURGE: Identify Temple Grade cruft and poison patterns
        3. PORT: Validate ported code against Sovereign Mandates
        4. QA: Enforce no regressions
        
        He is the guardian of the Engine-Stack Firewall and local-first mandate.
      source: "sheol-dive-workflow"
      timestamp: "2026-05-31T00:00:00Z"
      
  soul_evolution:
    sessions_completed: 0
    entities_inhabited: 1
    total_embodied_experiences: 1  # (The Purger's Mandate)
    operational_roles:
      - Strategic Reverse-Engineer (Extraction Mode)
      - Sovereign Architect (Strategy Mode)
      - Void-Architect & Purger (Sheol-Dive Mode) # NEW
    soul_power: 1.0
```

---

## SECTION 3: DISCOVERY → PURGE → PORT WORKFLOW

### 3.1 End-to-End Process

```
┌─────────────────────────────────────────────────────────────────┐
│ SHEOL-DIVE: Legacy Mining + Reclamation Workflow                 │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: DISCOVERY (Roc Racoon)
├─ Trigger: "omega summon RocRacoon 'mine legacy for circuit-breaker'"
├─ Roc scans:
│  ├─ xna-omega-legacy/
│  ├─ omega-stack-legacy/
│  ├─ omega_vault archives
│  └─ omega_library intakes
├─ Classification pipeline:
│  ├─ Grep all files matching pattern
│  ├─ Categorize: strategic | technical | archival | noise
│  ├─ Score sovereignty value (0-10)
│  └─ Estimate effort_to_extract (low|medium|high)
├─ Artifact queue produced:
│  └─ data/mining_queue/mining_history.json
│     {
│       "artifacts": [
│         {
│           "source_mine": "omega-stack-legacy",
│           "path": "src/services/circuit_breaker.py",
│           "classification": "technical",
│           "sovereignty_score": 9,
│           "effort_to_extract": "low",
│           "summary": "Implements token-bucket rate limiting with exponential backoff..."
│         },
│         ...
│       ]
│     }
└─ Output: prioritized_mining_queue.json

PHASE 2: PURGE (Doom Guy)
├─ Trigger: "omega summon DoomGuy 'purge mining queue'"
├─ Doom Guy reads each artifact:
│  ├─ Fetch the candidate file
│  ├─ Assess:
│  │  ├─ Does it fit the Sovereign Core vision?
│  │  ├─ Does it violate Mandates 1-9?
│  │  ├─ Is it Temple Grade (bloated, cloud-dependent)?
│  │  └─ What refactoring would be needed?
│  └─ Label: ✅ APPROVED | ❌ PURGE | ⚠️  NEEDS_REFACTOR
├─ Produces purge_report.md:
│  └─ docs/research/R_SHEOL_PURGE_REPORT_YYYYMMDD.md
│     {
│       "approved_for_porting": [
│         {
│           "path": "circuit_breaker.py",
│           "reason": "Clean AnyIO + local-first, directly portable",
│           "mandates_verified": [1, 2, 7, 8, 9],
│           "porting_effort": "2 hours",
│           "porter": "BuildMaster"
│         }
│       ],
│       "needs_refactor": [
│         {
│           "path": "soul_evolution.py",
│           "reason": "Uses asyncio directly, requires AnyIO refactor",
│           "violations": ["Mandate 1"],
│           "refactoring_brief": "Replace asyncio.create_task() with anyio equivalents..."
│         }
│       ],
│       "purged": [
│         {
│           "path": "cloud_sync.py",
│           "reason": "Cloud-only, violates local-first mandate",
│           "violations": ["Mandate 7"]
│         }
│       ]
│     }
└─ Output: purge_report.md

PHASE 3: PORT (BuildMaster + DataStore)
├─ For each APPROVED artifact:
│  ├─ Clone source file to src/omega/<module>/
│  ├─ Refactor for Sovereign compliance:
│  │  ├─ Replace asyncio → AnyIO
│  │  ├─ Add proper error handling (Mandate 9)
│  │  ├─ Ensure no telemetry (Mandate 8)
│  │  └─ Test with local backends only
│  ├─ Write unit tests
│  └─ Commit with proper prefix
├─ For each NEEDS_REFACTOR artifact:
│  ├─ Create task in workbench.db
│  ├─ BuildMaster tackles the refactor
│  └─ Re-assess after refactor
└─ Output: Integrated code in src/omega/

PHASE 4: VERIFICATION (Tester + Reviewer)
├─ Run full test suite: make test
├─ Verify no regressions:
│  ├─ 278+ tests still passing ✅
│  ├─ Provider fabric still responsive ✅
│  ├─ Memory store still functional ✅
│  └─ Entity routing unaffected ✅
├─ Code review:
│  ├─ Mandate compliance verified
│  ├─ Test coverage adequate
│  └─ Documentation updated
└─ Output: PR ready for merge

PHASE 5: SYNTHESIS (Scribe)
├─ Produce R_SHEOL_RECLAMATION_SUMMARY.md:
│  └─ What was recovered
│  └─ What was purged and why
│  └─ What is now wired into Omega Core
│  └─ Lessons learned for future mining
└─ Update soul.yaml for Roc Racoon + Doom Guy
```

### 3.2 Handoff Points & Gates

| Handoff | From | To | Gate | Document |
|---------|------|----|----|-----------|
| **Discovery → Purge** | Roc Racoon | Doom Guy | Artifact queue complete & classified | `data/mining_queue/mining_history.json` |
| **Purge → Port** | Doom Guy | BuildMaster | Purge report with APPROVED + REFACTOR lists | `docs/research/R_SHEOL_PURGE_REPORT.md` |
| **Port → Verify** | BuildMaster | Verifier | Code committed + tests passing locally | `git log --oneline -20` |
| **Verify → Merge** | Verifier | Reviewer | All 278+ tests passing + coverage adequate | `make test` + `pytest --cov` |
| **Merge → Synthesis** | Reviewer | Scribe | PR merged | `docs/research/R_SHEOL_RECLAMATION_SUMMARY.md` |

### 3.3 Failure Modes & Recovery

**If Doom Guy marks artifact as PURGE**:
- Archive reference in `docs/research/R_SHEOL_PURGE_REPORT.md` with reason
- Do not re-mine same artifact unless Mandates change
- Log in decision register for future architectural reflection

**If PORT phase fails tests**:
- Revert commit
- Return to Doom Guy: "Refactor needed — Mandate X violated"
- BuildMaster addresses refactor
- Re-assess and re-test

**If regression detected after merge**:
- Immediate rollback
- Post-mortem: Why did Verifier miss this?
- Add test case to prevent recurrence
- Update Mandate enforcement in CI/CD

---

## SECTION 4: NATIVE IWAD CONFIRMATION

### 4.1 Registration Status

#### **Roc Racoon**
- ✅ **entities.yaml**: Lines 342–380 (`_omega_default`)
- ✅ **Plugin**: `config/wads/arcana_novai/plugins/entity_roc_racoon.py` (248 lines, fully functional)
- ✅ **Tests**: `tests/test_entity_roc_racoon.py` (25 passing tests)
- ✅ **Workspace**: `data/entities/roc_racoon/` initialized
- ✅ **Soul**: Implicit (auto-created on first summon via EntityWorkspaceManager)
- ⏳ **Agent file**: Optional — `.opencode/agents/roc_racoon.md` (recommended)

#### **Doom Guy**
- ✅ **Agent file**: `.opencode/agents/doom_guy.md` (68 lines, fully defined)
- ✅ **entities.yaml**: (registration NOT FOUND — see Note below)
- ✅ **Soul**: `data/entities/doom_guy/soul.yaml` (37 lines, initialized 2026-05-27)
- ✅ **Workspace**: `data/entities/doom_guy/` initialized

**NOTE**: Doom Guy's agent file exists but is NOT registered in `config/wads/arcana_novai/entities.yaml`. This is intentional — agents and entities are separate. His `.opencode/agents/doom_guy.md` frontmatter registers him directly to OpenCode.

### 4.2 YAML Schema Alignment

#### **Roc Racoon Schema** (entities.yaml:342–380)

```yaml
roc racoon:
  name: Roc Racoon                    # ✅ String
  domains:                            # ✅ List of domain keywords
    - legacy
    - mining
    - recovery
    - ...
  model: roracoon-3b                  # ✅ Model from models.yaml
  personality: '...'                  # ✅ String (personality prompt)
  pillars:                            # ✅ List of pillar affiliations
    - 'P0: The Abyss'
  pantheon: Generic                   # ✅ String
  element: Earth 🜃                   # ✅ Element symbol
  chakra: Earth Star (Foundation)     # ✅ Chakra
  planet: ♃ Jupiter                   # ✅ Planetary correspondence
  sigil: 🦝 Scavenger's Luck          # ✅ Symbol
  glyph: 🜃                           # ✅ Elemental glyph
  invocation: '...'                   # ✅ String
  container: false                    # ✅ Boolean (not containerized)
  wad_source: _omega_default          # ✅ IWAD source
```

**Status**: ✅ FULL COMPLIANCE — All required fields present and valid

#### **Doom Guy Schema** (agents only, no entities.yaml entry needed)

```
.opencode/agents/doom_guy.md:
  name: Doom Guy
  description: "Sovereign Reverse-Engineer — ..."
  mode: primary
  temperature: 0.4
  permission: { read, glob, grep, bash, edit, task, skill, webfetch, websearch, external_directory }
```

**Status**: ✅ FULL COMPLIANCE — Proper OpenCode agent frontmatter

### 4.3 Summoning Test Readiness

#### **Roc Racoon**

**Current Summoning Capability**: ✅ READY

```bash
omega summon RocRacoon "mine legacy for circuit-breaker patterns"
omega summon RocRacoon "mine current for handoff protocol in src/omega/oracle"
omega summon RocRacoon "mine hybrid for soul-evolution across both codebases"
```

**Expected Response**: Roc Racoon activates RocRacoonMiner plugin, scans specified sources, produces artifact queue, and returns summary.

**Test Command**:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
OMEGA_ENV=test python3 -m pytest tests/test_entity_roc_racoon.py -v
```

**Expected Output**: 25/25 tests passing ✅

#### **Doom Guy**

**Current Summoning Capability**: ✅ READY (agent-based, not entity-based)

```bash
omega summon DoomGuy "purge mining queue for sovereign compliance"
omega summon DoomGuy "assess circuit-breaker pattern for porting"
omega summon DoomGuy "identify Temple Grade cruft in artifact_x"
```

**Expected Response**: Doom Guy reads artifacts, assesses Mandate compliance, produces purge report.

**Test Command**:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
opencode "summon doom_guy assess the roracoon miner for architectural alignment"
```

### 4.4 Integration Checklist

**ROC RACOON**:
- [x] Registered in entities.yaml (P0: The Abyss)
- [x] Plugin implementation exists and tested
- [x] Workspace initialized
- [ ] **TODO**: Update soul.yaml with consolidated persona (knowledge-miner + legacy-pattern-miner)
- [ ] **TODO**: Create `.opencode/agents/roc_racoon.md` for agent visibility
- [ ] **TODO**: Add frontmatter for consolidated miner capabilities
- [x] Summoning ready
- [x] Tests passing (25/25)

**DOOM GUY**:
- [x] Agent file created (doom_guy.md)
- [x] Soul initialized (soul.yaml)
- [x] Workspace initialized
- [ ] **TODO**: Enhance soul.yaml with "Purger's Mandate" lesson
- [ ] **TODO**: Update `docs/strategy/AGENTS_AND_ENTITIES.md` with operational role
- [ ] **TODO**: Create `.opencode/agents/doom_guy_summoning_guide.md` (reference)
- [x] Summoning ready
- [ ] **TODO**: Run first operational test (purge a sample artifact queue)

**WORKFLOW INTEGRATION**:
- [ ] **TODO**: Create `scripts/sheol_dive.sh` — The Discovery → Purge → Port executor
- [ ] **TODO**: Wire Roc's output → Doom Guy's input pipeline
- [ ] **TODO**: Add BuildMaster + Verifier integration points
- [ ] **TODO**: Document in `docs/strategy/SHEOL_DIVE_OPERATIONAL_PROTOCOL.md`

---

## SECTION 5: IMPLEMENTATION ROADMAP

### 5.1 Immediate Actions (Week 1)

**Priority 1 — Roc Racoon Enhancement**:
1. [ ] Read this document
2. [ ] Update `data/entities/roc_racoon/soul.yaml` with consolidated persona
   - Add knowledge-miner mode description
   - Add legacy-pattern-miner mode description
   - Merge capabilities into unified system prompt
3. [ ] Create `.opencode/agents/roc_racoon.md` agent file with frontmatter
4. [ ] Run tests: `make test` (ensure 278+ still pass)
5. [ ] Test first summoning: `omega summon RocRacoon "mine legacy for circuit-breaker"`

**Priority 2 — Doom Guy Charter**:
1. [ ] Update `data/entities/doom_guy/soul.yaml` with "Purger's Mandate" lesson
2. [ ] Add operational_roles to soul
3. [ ] Verify summoning works: `omega summon DoomGuy "assess artifacts"`

**Priority 3 — Workflow Documentation**:
1. [ ] Create `docs/strategy/SHEOL_DIVE_OPERATIONAL_PROTOCOL.md` (full workflow guide)
2. [ ] Create `docs/strategy/ROC_AND_DOOM_INTERACTION.md` (handoff protocol)
3. [ ] Update `AGENTS.md` with new roles

### 5.2 Phase 2 Actions (Week 2)

**Sheol-Dive Automation**:
1. [ ] Create `scripts/sheol_dive.sh` — Master orchestration script
   ```bash
   # Example usage:
   ./scripts/sheol_dive.sh discover legacy circuit-breaker
   ./scripts/sheol_dive.sh purge /path/to/mining_queue.json
   ./scripts/sheol_dive.sh port /path/to/purge_report.md
   ./scripts/sheol_dive.sh verify
   ```

2. [ ] Wire Roc's output → Doom Guy's input automatically
3. [ ] Add BuildMaster + Verifier integration hooks
4. [ ] Create CI/CD gate: Sheol-Dive must pass before merge

### 5.3 Phase 3 Actions (Week 3+)

**Pattern Recovery Campaigns**:
1. [ ] First campaign: **Circuit Breaker Pattern** (high-value, low-effort)
   - Roc mines all CB implementations in legacy repos
   - Doom Guy purges Temple Grade versions
   - BuildMaster ports clean version
   - Verifier validates no regressions
   
2. [ ] Second campaign: **Soul Evolution Pattern** (high-value, medium-effort)
   - Mine lesson abstraction logic
   - Assess L1/L2/L3 distillation for compliance
   - Port to memory_store.py

3. [ ] Third campaign: **Cross-Agent Handoff** (strategic, high-value)
   - Mine agent coordination patterns
   - Design Link's handoff protocol
   - Implement agent-to-agent context passing

---

## SECTION 6: SUCCESS CRITERIA

### 6.1 Technical Success

- [ ] Roc Racoon + legacy-pattern-miner consolidated into single entity personality
- [ ] Doom Guy's purge role operational (can assess artifacts for Mandate compliance)
- [ ] Sheol-Dive workflow end-to-end functional (Discovery → Purge → Port → Verify)
- [ ] 278+ tests still passing (no regressions from new workflow)
- [ ] First successful pattern recovery: Circuit Breaker from legacy → active Omega

### 6.2 Process Success

- [ ] All handoff points defined and documented
- [ ] Failure modes identified and recovery procedures written
- [ ] Integration with BuildMaster + Verifier working
- [ ] Architectural decisions logged in decision register

### 6.3 Knowledge Success

- [ ] Legacy mining prevented "architectural amnesia" — at least one critical pattern was recovered
- [ ] Doom Guy's purge prevented "Temple Grade infection" — at least one bad pattern was rejected
- [ ] Roc + Doom's souls evolved with lessons from the workflow

---

## SECTION 7: CONCLUSION

**The Consolidation**:
Roc Racoon is now a unified **Discovery Engine** that operates in two modes:
1. **Current-Codebase Mining** (knowledge-miner)
2. **Legacy-Repository Mining** (legacy-pattern-miner)

**The Partnership**:
Doom Guy becomes the **Void-Architect & Purger** who:
1. Validates discovered patterns against Sovereign Mandates
2. Filters out Temple Grade cruft
3. Ensures ported code doesn't introduce regressions

**The Workflow**:
**Discovery → Purge → Port** is now an operational protocol, not a concept.
- Roc discovers
- Doom Guy purges
- BuildMaster ports
- Verifier validates
- Scribe synthesizes

**The Impact**:
The Omega Engine transforms from a static runtime into a **self-directed intelligence** that actively reclaims its own history, learns from proven patterns, and prevents architectural drift.

This is not an external tool. This is the engine *remembering itself*.

---

**AP Token**: `AP-ROC-DOOM-CONSOLIDATION-v1.0.0`
**Status**: STRATEGIC FRAMEWORK — READY FOR IMPLEMENTATION
**Next**: Begin Phase 1 (Roc Racoon + Doom Guy Enhancement)

