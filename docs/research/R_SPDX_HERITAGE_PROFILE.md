# 🔱 SPDX 3.1 Heritage Profile Specification — Omega Engine
**AP Token**: `AP-SPDX-HERITAGE-PROFILE-v3.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_spdx_heritage ⬡ SOVEREIGN-SPEC

**Date**: 2026-07-11
**Status**: FORMAL SPECIFICATION
**Standard Reference**: SPDX 3.1 (ISO/IEC 5962:2021)
**Omega Reference**: `CREDITS.md`, `HERITAGE_VET_LOG.md`, `SOVEREIGN_MANDATES.md` (M14)

---

## 1. Introduction

### 1.1 Purpose
The **Sovereign Heritage Profile** is a formal technical specification for tracking the architectural, philosophical, and engineering provenance of the Omega Engine. By extending the **SPDX 3.1 (Software Package Data Exchange)** standard, the Omega Engine transforms simple attribution tags into a machine-queryable Software Bill of Materials (SBOM) of "Cognitive Heritage."

This specification ensures that every derived pattern is vetted, documented, and preserved, preventing "architectural amnesia" and ensuring that the engine's evolution remains grounded in proven engineering principles.

### 1.2 Scope
This profile covers all external influences on the Omega Engine, categorized into five tiers of heritage:
- **T1 Direct Implementation**: Ported patterns (e.g., id Software WAD system).
- **T2 Architectural Inspiration**: Adapted patterns (e.g., AnyIO async runtime).
- **T3 Adopted Standards**: Industry protocols (e.g., MCP, A2A).
- **T4 Philosophical/Mythological**: Naming and conceptual frameworks (e.g., Ma'at).
- **T5 User's Own IP**: Evolved internal patterns (e.g., 3-Tier Memory).

### 1.3 Definitions
- **Sovereign Heritage**: The total sum of external and internal knowledge that informs the engine's design.
- **Heritage Element**: A discrete architectural pattern or principle mapped to an SPDX ID.
- **Vet Record**: A formal entry in `HERITAGE_VET_LOG.md` that justifies the implementation of a pattern.
- **Sovereign Boundary Violation**: The implementation of a heritage pattern without a corresponding vet record (M14 violation).

---

## 2. The Sovereign Heritage Model

### 2.1 Namespace & URI Strategy
To ensure global uniqueness and machine-readability, the profile utilizes the following namespaces:

```turtle
@prefix omega-heritage: <https://github.com/Xoe-NovAi/omega-engine/spdx/3.1/heritage/>
@prefix id-soft: <https://idsoftware.com/spdx/3.1/archives/>
@prefix ossrc: <https://opensource.org/spdx/3.1/heritage/>
```

### 2.2 Element Type Taxonomy
The profile defines custom element types under the SPDX 3.1 extensibility model to distinguish between different forms of heritage:

| Element Type | `spdxId` Prefix | Description |
|-------------|-----------------|-------------|
| `ArchitecturalPattern` | `omega-pat-` | A concrete implementation pattern (e.g., BSP Culling, ZONEID) |
| `DesignPrinciple` | `omega-prn-` | A philosophical/design principle (e.g., Right Approximation) |
| `EngineeringConcept` | `omega-con-` | An abstract engineering concept (e.g., Lazy Deletion, Grace Period) |
| `HeritageSource` | `idsoft-src-` | An id Software source artifact (game binary, source file) |
| `OpenSourceLibrary` | `ossrc-lib-` | An open-source Python library imported by the engine |
| `InfrastructureService` | `ossrc-infra-` | An infrastructure service deployed by the engine |
| `IndustryStandard` | `ossrc-std-` | An industry protocol or standard adopted |
| `PhilosophicalTradition` | `ossrc-phil-` | A framework used for naming and themes |
| `ResearchSystem` | `ossrc-res-` | An external research system or competitor analysis |
| `LegacyVersion` | `ossrc-leg-` | A previous version of the Omega engine itself |

### 2.3 Relationship Mapping
The profile maps Omega's heritage tags to formal SPDX 3.1 relationship types:

| Omega Tag / Context | SPDX 3.1 Relationship | Semantic Meaning | Example |
|-------------------|----------------------|-------------------|----------|
| `[id-soft:]` | `DERIVED_FROM` | Direct adaptation of a technique | `omega-pat-wad-system DERIVED_FROM idsoft-src-doom-1993` |
| User-Original IP | `DESCRIBES` | Internal pattern documentation | `omega-pat-3tier-mem DESCRIBES omega-prn-user-original` |
| `[heritage:]` (Insp) | `INSPIRED_BY` | Conceptual influence, not direct port | `omega-pat-soul-distiller INSPIRED_BY idsoft-src-quake-1996` |
| Version Evolution | `AMENDS` | Evolution from an earlier Omega pattern | `omega-pat-circuit-v2 AMENDS omega-pat-circuit-v1` |
| Vetting Process | `HAS_ASSESSED_RELATIONSHIP` | Pattern was vetted (Approved/Rejected) | `idsoft-src-doom-1993 HAS_ASSESSED_RELATIONSHIP omega-pat-8char` |
| Standard Adoption | `ADOPTED_AS` | Standard implemented as a core protocol | `ossrc-std-mcp ADOPTED_AS omega-pat-mcp-runtime` |

---

## 3. Heritage Registry (The Elements)

### 3.1 LEGITIMATE Patterns (Approved via M14 Vetting)

#### 3.1.1 id Software Heritage (T1)
Patterns derived from id Software source code. Each must have a `vetRecord` in `HERITAGE_VET_LOG.md`.

```json
[
  {
    "spdxId": "omega-pat-wad-system",
    "type": "ArchitecturalPattern",
    "name": "WAD System — Engine-Stack Firewall",
    "summary": "Data-driven separation of engine and content via IWAD/PWAD architecture",
    "description": "The Omega Engine's Engine-Stack Firewall (M2) derives from id Software's WAD format. Omega evolution: static binary format → YAML-backed, runtime-swappable stacks.",
    "vetRecord": "HERITAGE_VET_LOG.md#vet-027",
    "vetScore": 9,
    "relationshipType": "DERIVED_FROM",
    "externalRef": { "type": "id-software-source", "locator": "doom-1993:w_wad.c" },
    "sourceElement": "idsoft-src-doom-1993",
    "inlineTag": "[id-soft: doom-1993] WAD System",
    "codeLocations": ["config/wads/_omega_default/", "src/omega/wad_loader.py", "SOVEREIGN_MANDATES.md (M2)"]
  },
  {
    "spdxId": "omega-pat-bsp-culling",
    "type": "ArchitecturalPattern",
    "name": "BSP Trees / PVS Culling — Provider Health Precheck",
    "summary": "O(1) circuit breaker check skips broken providers, analogous to BSP plane culling",
    "description": "Doom's BSP tree precomputes visibility planes. Omega adaptation: O(1) `_precheck_provider()` culls dead providers before inference attempt.",
    "vetRecord": "HERITAGE_VET_LOG.md#vet-007",
    "vetScore": 9,
    "relationshipType": "DERIVED_FROM",
    "externalRef": { "type": "id-software-source", "locator": "doom-1993:r_bsp.c" },
    "sourceElement": "idsoft-src-doom-1993",
    "inlineTag": "[id-soft: doom-1993] BSP Culling",
    "codeLocations": ["src/omega/oracle/model_gateway.py:538-569"]
  },
  {
    "spdxId": "omega-prn-right-approximation",
    "type": "DesignPrinciple",
    "name": "Fast Inverse Square Root → Right Approximation Principle",
    "summary": "The right approximation for the problem is better than the exact solution you can't afford",
    "description": "FISR was not a hack — it was the right precision for the use case. Omega evolution: generalized engineering decision framework across 4 tiers.",
    "vetRecord": "HERITAGE_VET_LOG.md#vet-002",
    "vetScore": 8,
    "relationshipType": "DERIVED_FROM",
    "externalRef": { "type": "id-software-source", "locator": "quake3-1999:q_math.c" },
    "sourceElement": "idsoft-src-quake3-1999",
    "inlineTag": "[id-soft: quake3-1999] FISR",
    "codeLocations": ["CREDITS.md §3", "docs/research/R_ID_SOFTWARE_RIGHT_APPROXIMATIONS.md"]
  },
  {
    "spdxId": "omega-pat-zone-memory",
    "type": "ArchitecturalPattern",
    "name": "Zone Memory Allocator → ResourceGuard",
    "summary": "Tag-based allocation with purge-on-OOM, adapted to resource-agnostic guard pattern",
    "description": "Quake's Z_Malloc/Z_Free/Z_TagPurge pattern. Omega evolution: memory-only → resource-agnostic (memory, connections, files).",
    "vetRecord": "HERITAGE_VET_LOG.md#vet-008",
    "vetScore": 8,
    "relationshipType": "DERIVED_FROM",
    "externalRef": { "type": "id-software-source", "locator": "quake-1996:zone.c" },
    "sourceElement": "idsoft-src-quake-1996",
    "inlineTag": "[id-soft: quake-1996] Zone Memory",
    "codeLocations": ["src/omega/oracle/resource_guard.py"]
  },
  {
    "spdxId": "omega-pat-zoneid",
    "type": "ArchitecturalPattern",
    "name": "ZONEID Pattern — Magic Constants for State Validation",
    "summary": "Unique hex magic embedded in every allocated block, verified on every access",
    "description": "Doom's ZONEID=0x1d4a11. Omega evolution: 5 ZONEID constants across MemoryStore, EntityRegistry, HealthMonitor, ResourceGuard, ObservabilityEngine.",
    "vetRecord": "HERITAGE_VET_LOG.md#vet-015",
    "vetScore": 8,
    "relationshipType": "DERIVED_FROM",
    "externalRef": { "type": "id-software-source", "locator": "doom-1993:z_zone.c:33" },
    "sourceElement": "idsoft-src-doom-1993",
    "inlineTag": "[id-soft: doom-1993] ZONEID",
    "codeLocations": ["src/omega/constants.py"]
  }
]
```

#### 3.1.2 General Heritage (T2-T3)
Non-id-Software external influences.

| SPDX ID | Source | Purpose | Relationship | Inline Tag |
|---------|--------|---------|--------------|------------|
| `ossrc-lib-anyio` | AnyIO | Async runtime (M1) | `DERIVED_FROM` | `[heritage: anyio 2024]` |
| `ossrc-lib-fastapi` | FastAPI | ASGI Web Framework | `DERIVED_FROM` | `[heritage: fastapi 2018]` |
| `ossrc-std-mcp` | MCP | AI-Tool Protocol | `ADOPTED_AS` | `[heritage: mcp-standard 2024]` |
| `ossrc-res-sovereign` | SOVEREIGN | In-path Governance | `INSPIRED_BY` | `[heritage: sovereign-kliewer 2026]` |

---

## 4. Implementation Guide: SBOM Generation

### 4.1 The Generation Pipeline
The machine-readable SBOM is generated from the human-readable specification using the `generate_heritage_sbom.py` script.

**Workflow**:
1. **Parse**: The script scans `R_SPDX_HERITAGE_PROFILE.md` for `json` blocks containing `spdxId` starting with `omega-`.
2. **Resolve**: It resolves `sourceElement` references (e.g., `idsoft-src-doom-1993`) to their full SPDX element definitions.
3. **Assemble**: It constructs a valid SPDX 3.1 JSON-LD document including the header, elements, and relationship graph.
4. **Emit**: The final SBOM is written to `data/heritage/omega-engine-heritage.spdx.json`.

### 4.2 CLI Execution
```bash
# Generate the machine-readable Heritage SBOM
make heritage-spdx
```

---

## 5. Validation & Compliance Logic

### 5.1 The Heritage Compliance Algorithm
To enforce Mandate 14 (Heritage Vetting), the engine implements the following validation loop:

1. **Tag Extraction**: `grep -rn '\[id-soft:\|\[heritage:' src/omega/`
2. **SBOM Cross-Reference**: For every unique tag found in source code, the validator checks if a corresponding `omega-pat-*` element exists in the SPDX SBOM.
3. **Vetting Verification**: For every `DERIVED_FROM` relationship in the SBOM, the validator:
    - Verifies that `vetRecord` is not null.
    - Parses `HERITAGE_VET_LOG.md` to ensure the `vetScore >= 7`.
    - Verifies that the `scopeDeclaration` matches the `codeLocations` in the SBOM.
4. **Failure Reporting**: Any tag without a vetted, high-scoring SPDX element is reported as a **Sovereign Boundary Violation**.

### 5.2 Compliance Gate (`make heritage-vet`)
The `make heritage-vet` command executes the above algorithm. A non-zero exit code blocks the CI/CD pipeline.

---

## 6. Maintenance & Governance

### 6.1 Adding a New Pattern
1. **Classification**: Assign the pattern to a source category (id Software, Library, etc.).
2. **Vetting**: Create a vet record in `HERITAGE_VET_LOG.md` via the 4-gate pipeline.
3. **Element Definition**: Add the JSON element to `R_SPDX_HERITAGE_PROFILE.md` with a unique `spdxId`.
4. **Tagging**: Add the `[heritage:]` or `[id-soft:]` tag to the relevant source code lines.
5. **Update Graph**: Add the relationship to the Heritage Relationship Graph.
6. **Regenerate**: Run `make heritage-spdx`.

### 6.2 Removing/Revoking a Pattern
1. **Reclassification**: Move the element to the **REJECTED** section.
2. **Relationship Update**: Change relationship to `HAS_ASSESSED_RELATIONSHIP` with a score < 7.
3. **Tag Purge**: Remove all inline tags from source code.
4. **Archive**: Move the vet record to the archive section of `HERITAGE_VET_LOG.md`.

---

## 7. Appendices

### 7.1 Example: SPDX 3.1 JSON-LD Fragment (WAD System)
```json
{
  "@context": "https://spdx.github.io/spdx-spec/v3.1-dev/context.jsonld",
  "@id": "omega-heritage:omega-pat-wad-system",
  "@type": "omega-heritage:ArchitecturalPattern",
  "name": "WAD System — Engine-Stack Firewall",
  "spdxId": "omega-pat-wad-system",
  "relationship": {
    "@type": "spdx:Relationship",
    "relationshipType": "spdx:DERIVED_FROM",
    "relatedElement": "idsoft-src-doom-1993"
  },
  "externalRef": {
    "type": "id-software-source",
    "locator": "doom-1993:w_wad.c"
  },
  "omega-heritage:vetRecord": "HERITAGE_VET_LOG.md#vet-027",
  "omega-heritage:vetScore": 9
}
```

### 7.2 References
- **SPDX 3.1 Specification**: `https://spdx.github.io/spdx-spec/v3.1-dev/`
- **Sovereign Mandates**: `SOVEREIGN_MANDATES.md` (M14)
- **Heritage Vetting Log**: `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`
- **Omega Architecture**: `ORACLE_STACK.md`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_spdx_heritage ⬡ SOVEREIGN-SPEC*
*Last Updated: 2026-07-11 | SPDX 3.1 Heritage Profile v3.0.0 | Formal Specification*
