# 🔱 Sovereign Knowledge Maintenance Protocols (SKMP-V1)

**⬡ OMEGA ⬡ ROC_RACOON ⬡ trc_lifecycle ⬡ GNOSIS-MAINTENANCE**

**Status**: ACTIVE
**Version**: 1.0.0
**Last Updated**: 2026-06-13

---

## 1. Versioning & Fact Tracking: The "Pivot-Linked" Lineage

To prevent "context pollution" where old, superseded decisions haunt the current prompt, Omega employs a **Lineage-Based Versioning** system.

- **The Pivot Anchor**: Every architectural shift is recorded in `docs/decisions/PIVOT_LOG.md` with a unique ID (e.g., `Decision 61`).
- **Fact-to-Pivot Mapping**: Every `VerificationItem` (the atomic unit of a "fact") must include a `pivot_id` field.
- **The Archival Trigger**: When a new PIVOT is committed:
    1. **Identify**: All `VerificationItem`s linked to the superseded `pivot_id` are flagged.
    2. **Transition**: Status is moved from `live` $\rightarrow$ `archived` or `stalled`.
    3. **Tombstoning**: The corresponding knowledge files in `knowledge/` are moved to `_archive/` with a `.archived` suffix.
    4. **Redirection**: A "Tombstone Note" is left in the original location: *"This fact was superseded by Decision XX. See [New Path] for current truth."*

---

## 2. Contradiction Resolution: The "Sovereign Resolution" Protocol

When two sources of knowledge conflict, Omega rejects "averaging" or "majority voting" in favor of **Skeptical Verification**.

- **The Two-Source Rule (TSR)**: A claim is only `VERIFIED` if $\ge 2$ independent, high-authority sources entail the claim via NLI (Natural Language Inference).
- **The Resolution Hierarchy**: If a contradiction is detected, the `SkepticalVerifier` executes the following priority chain:
    1. **Recency**: Does one source post-date the other? (Temporal precedence).
    2. **Authority**: Does one source come from a "Sovereign" entity (e.g., Kali/Ma'at) vs. a "Subagent" (e.g., P1-P10)?
    3. **Contextual Divergence**: Is the contradiction actually a difference in *scope*? (e.g., "Local-First" is true for the Engine, but "Cloud-Fallback" is true for the Provider Fabric).
    4. **Sovereign Debate**: If unresolved, the conflict is escalated to a **MaKaLi Council** session for a final verdict.

---

## 3. Pruning & Forgetting: The "Sovereign Forgetting" Protocol

To prevent "context rot" and hallucinations caused by stale data, Omega implements a **TTL-Driven Metabolism**.

- **The Decay Pipeline**: Knowledge moves through stages of decreasing volatility:
    - **`_inbox/` (24h TTL)**: Raw captures. If not triaged in 24h $\rightarrow$ **Delete**.
    - **`active/` (7d TTL)**: Working hypotheses. If not promoted to curated in 7d $\rightarrow$ **Archive**.
    - **`curated/` (30d TTL)**: L2 insights. If not distilled into `soul.yaml` (L3) in 30d $\rightarrow$ **Archive**.
    - **`_archive/` (90d TTL)**: Cold storage. After 90d $\rightarrow$ **Permanent Deletion** (unless tagged `[PERMANENT]`).
- **The "Forgetting" Trigger**: A `make workspace-health` check runs daily to prune items that have exceeded their TTL without a "Freshness" update.

---

## 4. Contribution Protocol: The "Metabolism" Workflow

Subagents cannot write directly to the SSOT. They must pass through the **Knowledge Metabolism Pipeline**.

**Workflow: Contribution $\rightarrow$ Review $\rightarrow$ Merge**

1. **Contribution (L1 $\rightarrow$ L2)**:
    - Subagent discovers a pattern in `workspace/`.
    - Subagent extracts an **L2 Insight** (Analysis/Pattern) and writes it to `knowledge/`.
    - Subagent creates a `VerificationItem` (YAML) in `data/coordination/verification/items/` with status `mined`.

2. **Review (The Sentinel Gate)**:
    - The `P5 Sentinel` or `Quality` agent audits the `VerificationItem` against the **Five Conditions**:
        - **A**: L2 insight exists.
        - **B**: Cross-references resolve.
        - **C**: Code port/test exists (if applicable).
        - **D**: Soul update proposed.
        - **E**: Demand signal closed.
    - If any condition fails $\rightarrow$ **NACK** (Return to subagent for refinement).

3. **Merge (L2 $\rightarrow$ L3)**:
    - Once `VERIFIED`, the `Scribe` agent performs **L3 Distillation**.
    - The insight is converted into a **Universal Principle** and committed to the entity's `soul.yaml`.
    - The `VerificationItem` status is updated to `deployed`.

---

## 📊 Summary Table: Knowledge Lifecycle

| Phase | State | Storage | Governance | Outcome |
| :--- | :--- |T: la la | Governance | Outcome |
| **Ingestion** | Raw | `_inbox/` | TTL (24h) | Triage or Delete |
| **Synthesis** | L1 $\rightarrow$ L2 | `knowledge/` | `P5 Sentinel` | Verified Insight |
| **Distillation**| L2 $\rightarrow$ L3 | `soul.yaml` | `Scribe` | Universal Principle |
| **Conflict** | Contradict | `SkepticalVerifier` | TSR / NLI | Resolved Truth |
| **Obsolescence**| Superseded | `_archive/` | `PIVOT_LOG.md` | Historical Record |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_lifecycle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
