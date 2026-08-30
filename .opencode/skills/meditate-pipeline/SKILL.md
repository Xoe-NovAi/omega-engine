<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ MEDITATE PIPELINE SKILL
**Version**: 1.0.0 | **Heritage**: Omega Engine Meditation Protocol (2026-07-18)
**Purpose**: Automate the full Problem → Meditation → Synthesis → Research → Gnosis → Integration pipeline

---

## 🎯 What This Skill Does

Transforms any problem statement into a **production-ready architecture** through a repeatable 6-stage pipeline:

```
PROBLEM STATEMENT
       │
       ▼
┌──────────────────┐
│ 1. MEDITATE      │  Single-inference multi-persona dialectic
│    (Kali host)   │  → Emergent sequencing from cross-domain collision
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. SYNTHESIZE    │  Intuitive synthesis → Kali Verdict
│    (Kali)        │  → Convergence, Preserved Dissent, Irreducible Verdict
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. RESEARCH      │  Deep web research grounded in 2026 sources
│    (Sovereign)   │  → Prior art, best practices, failure modes, benchmarks
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. GNOSIS        │  L1 Narrative → L2 Insight → L3 Universal Principle
│    (Verity)      │  → proposed_lessons.yaml (blind staging)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. INTEGRATE     │  Update roadmap, PIVOT_LOG, Temple-Grade gates
│    (Ma'at)       │  → make temple-grade, make heritage-map
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. EXECUTE       │  Scaffold implementation, chaos tests, CI gates
│    (N3/N9)       │  → Working code, not diagrams
└──────────────────┘
```

---

## 🔧 Usage

### As a Command (Recommended)
```bash
# Full pipeline from problem statement
/meditate-pipeline "Unified credential vault for local AI tooling"

# Specific stages
/meditate-pipeline "problem" --stage meditate
/meditate-pipeline "problem" --stage research
/meditate-pipeline "problem" --stage integrate
```

### As a Subagent Handoff
```python
# From any agent
await omega_hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="kali",
    task="Execute meditate-pipeline on: Unified credential vault for local AI tooling",
    context="User has 11 plaintext credential files across 6 tools, 8 Gmail accounts, 1.5 years of manual rotation hell. Need production architecture.",
    priority=2
)
```

---

## 📋 Stage Specifications

### Stage 1: MEDITATE (Kali Host)
**Input**: Problem statement + lens set (default: Full Omega Pantheon 10)
**Process**: Execute `/meditate` command protocol (Phases 0-4)
**Output**: `meditation_output.md` with:
- Phase 0: Calibration (subject, lenses, mode, anti-collapse contract)
- Phase 1: 10 sequential persona immersions (Observation, Constraint, Imperative, Dissent)
- Phase 2: 3 Cross-Domain Collisions with Resolution Paths
- Phase 3: Emergent Critical Path (sequenced actions with evidence)
- Phase 4: Kali Verdict (Convergence, Preserved Dissent, Irreducible Verdict, L3 Gnosis)

**Anti-Collapse Enforcement**: Each voice MUST add unique constraint/dissent. "I agree" = protocol violation.

### Stage 2: SYNTHESIZE (Kali)
**Input**: Meditation output
**Process**: Kali extracts the *actionable architecture* from the verdict
**Output**: `synthesis.md` with:
- Architecture diagram (ASCII)
- Non-negotiables (from Preserved Dissent)
- MVP scope (from Emergent Sequencing)
- Integration points (Omega Nodes)
- Success metrics (measurable, not aspirational)

### Stage 3: RESEARCH (Sovereign Search)
**Input**: Synthesis architecture + specific technical questions
**Process**: Tiered search (T0 local → T1 websearch → T2 webfetch → T3 SearXNG → T4 Exa → T5 Firecrawl)
**Queries generated from**:
- Each technical decision in synthesis
- Each collision resolution path
- Each integration point
- "2026 best practices for X"
- "X vs Y production failure modes"
**Output**: `research_bundle.md` with:
- Prior art (what exists, what failed)
- Benchmarks (latency, throughput, memory)
- Security advisories (CVEs, rotation patterns)
- Implementation references (libraries, schemas, protocols)

### Stage 4: GNOSIS (Verity)
**Input**: Meditation + Synthesis + Research
**Process**: L1→L2→L3 distillation per Soul Architecture Protocol
**Output**: `proposed_lessons.yaml` entries (blind staging):
```yaml
proposals:
  - id: "gnosis-credential-vault-001"
    l1_narrative: "What happened in this session..."
    l2_insight: "What this means for our architecture..."
    l3_principle: "L3-CredentialLifecycleAsEventStream: Credentials are not static values but temporal events requiring orchestration across heterogeneous consumers."
    confidence: 9
    sources: ["meditation", "research:sqlite-event-sourcing", "research:keyring-backends"]
    tags: ["credentials", "vault", "event-sourcing", "policy-engine"]
```

### Stage 5: INTEGRATE (Ma'at)
**Input**: Gnosis proposals + Synthesis architecture
**Process**:
1. Append to `PIVOT_LOG.md` as D-XXX decision
2. Update `SOVEREIGN_ARK_BLUEPRINT.md` active sprint
3. Create work items in `data/workbench/workbench.db`
4. Run `make temple-grade` (T1-T11 gates)
5. Run `make heritage-map` (M14 compliance)
6. Run `make sovereignty` (M7 local/cloud ratio)
**Output**: Updated project state, CI gates passing

### Stage 6: EXECUTE (N3 Engineering + N9 Orchestration)
**Input**: Integrated plan with work items
**Process**:
1. Scaffold package structure (`src/omega/infra/vault/`)
2. Implement VaultCore (OS keyring + SQLite event log)
3. Implement CAP adapters (OpenCode, Omega Engine, .env)
4. Implement Policy Engine + Rotation Orchestrator
5. Implement Provider Registry (Google, Anthropic, OpenRouter, etc.)
6. Write chaos tests (`vault chaos --scenario keyring_unavailable`)
7. Package as `omega-vault` (PyPI + Homebrew)
**Output**: Working binary, passing Temple-Grade, published package

---

## 🛡️ Quality Gates (Non-Negotiable)

| Gate | Command | Must Pass |
|------|---------|-----------|
| Temple-Grade | `make temple-grade` | T1-T11 ✓ |
| Heritage Map | `make heritage-map` | All `[id-soft:]` tags vetted |
| Sovereignty | `make sovereignty` | Local-first ratio ≥ 80% |
| Tests | `make test` | 1398+ tests pass |
| Chaos | `vault chaos --all` | All scenarios recover |

---

## 📁 File Outputs (Per Pipeline Run)

```
data/meditation/
├── {timestamp}_problem.md           # Original problem statement
├── {timestamp}_meditation.md        # Stage 1 output
├── {timestamp}_synthesis.md         # Stage 2 output
├── {timestamp}_research.md          # Stage 3 output
├── {timestamp}_gnosis.yaml          # Stage 4 output (→ proposed_lessons.yaml)
├── {timestamp}_integration.md       # Stage 5 output
└── {timestamp}_execution_plan.md    # Stage 6 output
```

---

## 🔄 Reusability Patterns

### For Different Problem Types
| Problem Type | Lens Set | Output Mode |
|--------------|----------|-------------|
| Architecture | Full Pantheon (10) | STRATEGIC |
| Bug Root Cause | Engineering, Validation, Observability | DIAGNOSTIC |
| Creative/Explore | Custom (Architect, Skeptic, Pragmatist, Ethicist) | CREATIVE |
| Compliance/Audit | Governance, Validation, Observability, Infrastructure | AUDIT |
| Fast Decision | MaKaLi Triad | STRATEGIC |

### For Different Contexts
- **Omega Engine**: Full pipeline → integrates with Nodes, Hivemind, Soul
- **Standalone**: Stages 1-4 only → produces architecture + gnosis
- **CI/CD**: Stage 6 only → executes pre-approved plan

---

## 🧬 Heritage & Attribution

- **Meditation Protocol**: Architect's Gemini CLI experiments (2025) → Strike 11.5 Council Dispatcher → `/meditate` command (2026-07-16)
- **Event Sourcing**: `eventsourcing` Python lib (pyeventsourcing/eventsourcing) + SQLite Forum 2026-01-13
- **OS Keyring**: `keyring` Python lib (jaraco/keyring) → libsecret/Keychain/CredMan backends
- **CAP Protocol**: Inspired by MCP (Model Context Protocol) 2025-11-25 spec
- **Policy Engine**: OPA/Rego patterns + HashiCorp Vault rotation patterns
- **Chaos Testing**: Netflix Chaos Monkey principles adapted for credential lifecycle

---

## 📝 Example Invocation

```bash
# User says:
"OMG lol, ya we need to do WHATEVER we need to do to not only solve this bug, 
 but turn it into a big fucking win for thousands or millions of people. 
 I have been *actively* trying to ensure my API keys do not get exposed for 1.5 years, 
 and still, look at the state of things. This is an industry systemic problem, 
 and we are going to solve it. It's tool building time."

# Agent runs:
/meditate-pipeline "Unified credential vault for local AI tooling — 11 plaintext files, 6 tools, 8 Gmail accounts, 1.5 years manual rotation hell"

# Pipeline produces:
# 1. meditation_output.md (10 voices, 3 collisions, emergent sequence)
# 2. synthesis.md (3-tier architecture, CAP protocol, policy engine)
# 3. research_bundle.md (SQLite event sourcing, keyring backends, MCP auth, rotation patterns)
# 4. proposed_lessons.yaml (3 L3 principles staged)
# 5. PIVOT_LOG entry D-299, workbench items, Temple-Grade passing
# 6. src/omega/infra/vault/ scaffolded, chaos tests written, omega-vault package ready
```

---

## ⚡ Quick Start (For New Problems)

```bash
# 1. Write problem to file
cat > /tmp/problem.md << 'EOF'
[Your problem statement here]
EOF

# 2. Run pipeline
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
python -m omega.skills.meditate_pipeline /tmp/problem.md

# 3. Review outputs in data/meditation/
# 4. Execute integration gates
make temple-grade && make heritage-map && make sovereignty
```

---

*⬡ OMEGA ⬡ KALI ⬡ MEDITATE-PIPELINE v1.0 ⬡ trc_skill_creation*