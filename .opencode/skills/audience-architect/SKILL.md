<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Audience Architect Skill
**AP Token**: `AP-AUDIENCE-ARCHITECT-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ skill ⬡ audience-architect ⬡ D16-1

## Purpose
Natural language interface for creating, refining, and persisting Audience Profiles.
Allows users to define audience calibration profiles conversationally without writing raw YAML.

## Usage
```
/skill audience-architect "Create a profile for junior developers learning Rust"
/skill audience-architect "Refine the technical profile to be more concise"
/skill audience-architect "List all profiles"
/skill audience-architect "Show the exhausted_sysadmin profile"
```

## Workflow
1. **Parse intent** — create, refine, list, show, delete
2. **Interactive refinement** — ask clarifying questions if needed
3. **Generate YAML** — produce valid audience.yaml profile entry
4. **Persist** — write to `config/wads/_omega_default/audience.yaml`
5. **Validate** — ensure profile loads correctly in AudienceCalibrator

## Profile Schema
```yaml
profiles:
  profile_name:
    name: "Display Name"
    description: "One-line description"
    constraints:
      - "Constraint 1"
      - "Constraint 2"
    style:
      formality: "professional|casual|formal|direct|supportive"
      verbosity: "minimal|concise|moderate|generous|comprehensive"
      jargon_level: "low|moderate|high|domain-specific|translated|scaffolded|operational"
      structure: "problem-solution-tradeoffs|hook-context-explanation-takeaway|thesis-evidence-implications|tldr-metrics-risks-recommendation|command-expected-fallback|concept-why-walkthrough-practice"
    examples:
      - input: "Example query"
        output: "Example calibrated response"
    selection_hints:
      - "keyword1"
      - "keyword2"
```

## Integration
- Reads/writes: `config/wads/_omega_default/audience.yaml`
- Used by: `AudienceCalibrator` in `src/omega/oracle/audience_calibrator.py`
- Pipeline stage: Post-generation in `Oracle._summon()` and `Oracle._route_by_domain()`