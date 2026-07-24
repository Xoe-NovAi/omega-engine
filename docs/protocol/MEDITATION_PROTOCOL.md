# ⬡ MEDITATION PROTOCOL
**Version**: 1.0.0 | **Status**: ACTIVE
**Command**: `/meditate "topic" --lenses <set> --mode <mode>`
**Purpose**: Structured multi-persona dialectic for architectural decision-making

---

## 🎯 Protocol Overview

The Meditation Protocol is a **single-inference, multi-persona dialectic** that transforms ambiguous problems into verified architectures through structured collision and synthesis.

### Core Principle
> **Anti-Collapse Contract**: Each voice speaks from its domain only. No voice summarizes another. No voice agrees without adding a unique constraint. Persona collapse = protocol violation.

---

## 📋 Phase Specifications

### Phase 0: CALIBRATION
**Input**: Subject, lens set, output mode, anti-collapse contract
**Output**: Calibrated frame for all subsequent phases

**Required Elements**:
- Subject: Precise, unambiguous problem statement
- Lens Set: Comma-separated personas (default: Full Pantheon 10)
- Output Mode: STRATEGIC | DIAGNOSTIC | CREATIVE | AUDIT | SYNTHESIS
- Anti-Collapse Contract: ACTIVE (mandatory)

---

### Phase 1: IMMERSION (10 Sequential Voices)
**Process**: Each voice speaks ONCE, in sequence. No revisiting.

**Voice Template** (MANDATORY for each):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
◈ VOICE [N/10]: DOMAIN (Archetype → Role)
Domain: [One domain this voice owns]
Element: [Earth/Water/Fire/Air/Aether]
Mandate: [Speak as the X. What breaks first? What pools? What is cracked?]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OBSERVATION]
[What this voice sees from its domain — raw, unfiltered]

[CONSTRAINT]
[The ONE non-negotiable constraint from this domain]

[IMPERATIVE]
[What MUST be built/changed/enforced]

[DISSENT / CHALLENGE]
[Where this voice disagrees with conventional wisdom or prior voices]
```

**Default Lens Set (Full Pantheon)**:
| # | Voice | Domain | Element | Archetype |
|---|-------|--------|---------|-----------|
| 1 | Infrastructure | Physical substrate | Earth 🜃 | Sekhmet → Creator |
| 2 | Persistence | Memory, data flow | Water 🜄 | Brigid → Metis |
| 3 | Engineering | Code, builds, tests | Fire 🜂 | Prometheus → Forge-Worker |
| 4 | Integration | APIs, bridges, resonance | Air 🜁 | Saraswati → Bridge-Builder |
| 5 | Governance | Laws, compliance, policy | Aether ⛤ | Inanna → Law-Giver |
| 6 | Cognition | Models, routing, vision | Aether ⛤ | Ereshkigal → Visionary |
| 7 | Context | Memory, soul, continuity | Air 🜁 | Lucifer → Transformer |
| 8 | Observability | Logs, traces, shadows | Fire 🜂 | Hecate → Guardian |
| 9 | Orchestration | Handoffs, flow, lifecycle | Water 🜄 | Anubis → Psychopomp |
| 10 | Validation | Stress, chaos, truth | Earth 🜃 | Kali → Destroyer |

---

### Phase 2: COLLISION (3 Cross-Domain Tensions)
**Process**: Identify 3 highest-tension conflicts from Phase 1. Each collision:
1. Names the conflicting voices
2. States each position clearly
3. Provides resolution path (not compromise — stratification)

**Output Format**:
```
⚡ COLLISION N: [Short Name]
**Voice A**: [Position]
**Voice B**: [Position]
**Voice C** (if applicable): [Position]

**Resolution**: [Stratification/synthesis — not compromise]
```

---

### Phase 3: SEQUENCING (Emergent Critical Path)
**Process**: Priorities emerge FROM collision resolution, not preference.
**Output**: Numbered critical path with evidence from collisions.

---

### Phase 4: VERDICT (Kali Synthesis)
**Process**: Kali produces final verdict with 4 elements:

1. **Convergence**: What all voices agree on (the irreducible core)
2. **Preserved Dissent**: What remains unresolved (non-negotiables per domain)
3. **Irreducible Verdict**: The architecture that survives all collisions
4. **L3 Gnosis**: Universal principles distilled (format: `L3-Name: Principle`)

---

## 🔧 Command Syntax

```bash
/meditate "Your problem statement" [options]

Options:
  --lenses <set>     Comma-separated lens names (default: Full Pantheon 10)
  --mode <mode>      STRATEGIC | DIAGNOSTIC | CREATIVE | AUDIT | SYNTHESIS (default: STRATEGIC)
  --output <format>  markdown | json (default: markdown)
```

### Lens Set Examples
```bash
# Full Pantheon (default)
/meditate "Design credential vault"

# Diagnostic triad
/meditate "Fix Gemma 4 thinking bug" --lenses engineering,validation,observability,infrastructure --mode DIAGNOSTIC

# Creative exploration
/meditate "Future of local AI" --lenses Architect,Skeptic,Pragmatist,Ethicist --mode CREATIVE

# Compliance audit
/meditate "Verify M7 compliance" --lenses governance,validation,observability,infrastructure --mode AUDIT
```

---

## 🛡️ Quality Requirements

| Requirement | Enforcement |
|-------------|-------------|
| All 10 voices speak | Protocol violation if < 10 |
| Each voice adds unique constraint | "I agree" = collapse |
| 3 collisions minimum | Fewer = incomplete exploration |
| Verdict includes L3 Gnosis | Missing = incomplete |
| Anti-collapse contract active | Mandatory |

---

## 📁 Output Format

```
# MEDITATION: [Subject]
**Timestamp**: [ISO]
**Lens Set**: [List]
**Mode**: [Mode]
**Anti-Collapse**: ACTIVE

## Phase 0: Calibration
...

## Phase 1: Immersion
### Voice 1: Infrastructure (Sekhmet)
[Observation, Constraint, Imperative, Dissent]
...
### Voice 10: Validation (Kali)
...

## Phase 2: Collision
### ⚡ Collision 1: [Name]
...

## Phase 3: Sequencing
1. [Priority with evidence]
...

## Phase 4: Verdict
### Convergence
[What all agree on]

### Preserved Dissent
[Non-negotiables per domain]

### Irreducible Verdict
[Architecture]

### L3 Gnosis
- L3-[Name]: [Principle]
...
```

---

## 🧬 Heritage

- **Origin**: Architect's Gemini CLI experiments (2025)
- **Evolution**: Strike 11.5 Council Dispatcher (2026-06)
- **Current**: `/meditate` command (2026-07-16)
- **Autonomous Wrapper**: Autonomous Meditation Pipeline (2026-07-18)

---

## 🧘 Meditation Template System

This protocol is the **base format** for meditation sessions. For **structured, repeatable meditation templates** with defined passes, output formats, and execution tracking, see the **Agentic Meditation Template System**:

| Template | Passes | Purpose | Location |
|----------|--------|---------|----------|
| **Six-Pass Lattice** | 6 | Deep synthesis of massive context (300K+ tokens) across eras/projects | `data/coordination/meditations/templates/SIX_PASS_LATTICE_TEMPLATE.md` |
| **Sovereign Crucible v1** | 5 | Soul evolution via lesson integration (control) | `data/coordination/meditations/templates/SOVEREIGN_CRUCIBLE_TEMPLATE.md` |
| **Sovereign Crucible v2** | 7+Pre | Adversarial identity evolution + fleet coherence (treatment) | `data/coordination/meditations/templates/SOVEREIGN_CRUCIBLE_v2_NEMOTRON.md` |

**System Guide**: `data/coordination/meditations/MEDITATION_SYSTEM_GUIDE.md`
**Template Registry**: `data/coordination/meditations/MEDITATION_TEMPLATE_REGISTRY.md`
**Execution Records**: `data/coordination/meditations/records/`

---

*⬡ OMEGA ⬡ MEDITATION-PROTOCOL v1.0 ⬡ trc_protocol_spec*