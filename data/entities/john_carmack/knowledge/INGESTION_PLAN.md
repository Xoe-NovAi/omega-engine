# 📚 Carmack Gnosis Ingestion Plan
**Objective**: Transform the lifework of John Carmack into a structured, queryable knowledge base for the Omega Engine.

## ⬡ The Ingestion Pipeline
$\text{Source} \rightarrow \text{Parse} \rightarrow \text{Axiomatize} \rightarrow \text{Sovereign Inscription}$

### 1. Primary Source Streams
| Source | Format | Priority | Target Directory | Key Value |
|---|---|---|---|---|
| **.plan files** | Text/Log | P0 | `knowledge/plans/` | Daily technical struggles, breakthroughs, and "failed" paths. |
| **GDC Talks** | Audio/Transcript | P1 | `knowledge/gdc/` | High-level architectural philosophy and retrospective analysis. |
| **id Tech Source** | C/C++ | P1 | `knowledge/source/` | Direct implementation of BSP, Z-Zones, and Fast-Inverse-Sqrt. |
| **Interviews/Podcasts**| Transcript | P2 | `knowledge/interviews/` | Nuanced views on AI, aerospace, and first-principles thinking. |

### 2. The "Continuous Study" Loop
The entity is not static. He must evolve as new archival data is recovered.

**Loop Sequence**:
1. **Discovery**: `@roc_racoon` mines legacy partitions for newly discovered `.plan` files or technical notes.
2. **Parsing**: `@jem_discovery` extracts key technical claims and implementation details.
3. **Axiomatization**: `@scribe` transforms these claims into **Soul Axioms** (L1 $\rightarrow$ L2 $\rightarrow$ L3).
4. **Inscription**: The axioms are written to `soul.yaml`, updating the entity's intuition.

### 3. Metrics of Success
The ingestion is complete when the entity can:
- Predict the performance bottleneck of a new Omega module based on a `.plan` file pattern.
- Critique a heritage implementation by citing the original id Tech constraint.
- Provide a "Right Approximation" for any provided technical trade-off.
