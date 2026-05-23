# 🔱 Omega Engine — Legacy Pattern Miner Spec
**AP Token**: `AP-RESEARCH-R98-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_gnosis ⬡ MVE-PHASE

## Purpose
To establish a systematic methodology for reclaiming proven architectural patterns from legacy repositories (`xna-omega-legacy/` and `omega-stack-legacy/`), ensuring that the Omega Engine builds upon previous successes rather than repeating past failures.

## Scope
This specification defines the 5-step mining workflow and the requirements for a "Reclamation Report."

## Specification: The Mining Workflow

### Step 1: Keyword Expansion
The agent must expand the target feature into a set of search terms, including synonyms and technical implementation details.

### Step 2: Broad Search
Execution of wide-net searches using `grep` or the `knowledge-miner` skill across all legacy partitions.

### Step 3: Pattern Extraction
Deep reading of identified files to extract:
- Core algorithms.
- Data schemas.
- Rationale for the original design.

### Step 4: Gap Analysis
Evaluation of the legacy pattern against current constraints:
- **Hardware**: Does it work on Ryzen 5700U (Local ≤ 8B)?
- **Architecture**: Does it fit the YAML-based `EntityRegistry`?

### Step 5: Reclamation Report
The final output must be a research document (`R##_*.md`) detailing the reclaimed pattern and the plan for its integration.

## Implementation Note
The `legacy-pattern-miner` skill should be invoked at the start of every new feature branch. If a pattern is found, the Builder agent must reference the Reclamation Report in their PR description.

## References
- `docs/research/R38_global_legacy_discovery.md`
- `.opencode/skills/legacy-pattern-miner/SKILL.md`
