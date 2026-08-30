# 🔱 Tri-Store Verification Suite
**⬡ OMEGA ⬡ VERITY ⬡ trc_verify_tri_store ⬡ VERIFICATION**

## 1. Functional Test Cases

### Test Case TC-S1: Hierarchical Descent (Semantic Zoom)
- **Input**: Query "Sovereign Mandate M1"
- **Expected Path**: 
    1. Gnosis Tree identifies L3: "Sovereign Law" $\rightarrow$ L2: "Async Runtime".
    2. Concept Graph activates "AnyIO", "Sovereign-Siloing", "ResourceGuard".
    3. Leaf Store returns specific paragraphs from `SOVEREIGN_MANDATES.md` regarding AnyIO.
- **Success Criterion**: All three tiers are hit in sequence; retrieval is more precise than pure vector search.

### Test Case TC-S2: Associative Leap (Cross-Domain Resonance)
- **Input**: Query "id Software memory management"
- **Expected Path**:
    1. Gnosis Tree anchors to "Legacy Engineering".
    2. Concept Graph activates "Zone Memory" $\rightarrow$ resonates with "AnyIO CapacityLimiter" (Sovereign resonance).
    3. Leaf Store returns both `CREDITS.md` (heritage) and `SovereignGateway` implementation.
- **Success Criterion**: Retrieval of "AnyIO" despite no direct keyword overlap with "id Software" in the query.

### Test Case TC-S3: Gnosis Gap Detection (Divergence)
- **Input**: A known contradiction (e.g., "M1 allows asyncio").
- **Expected Path**:
    1. Vector search finds a mention of asyncio in a legacy doc.
    2. Concept Graph finds a strong `CONTRADICTS` edge to "M1: AnyIO Absolute".
    3. System flags a **Gnosis Gap** and triggers a research task.
- **Success Criterion**: System identifies the contradiction rather than simply returning the most "similar" (but wrong) vector.

---

## 2. Performance Metrics

| Metric | Definition | Target | Baseline (Vector-Only) |
|--------|-------------|--------|-------------------------|
| **Retrieval Breadth** | Avg. number of distinct related concepts retrieved per query | $\ge 5$ | $\approx 1-2$ |
| **Sovereign Precision** | % of retrieved L1s that align with the anchor L3 principle | $> 90\%$ | $\approx 70\%$ |
| **Traversal Latency** | Total time for Gnosis $\rightarrow$ Graph $\rightarrow$ Leaf | $< 200\text{ms}$ | $50\text{ms}$ |
| **Activation Stability** | Variance of activation values after 5 iterations of SA | $\sigma < 0.1$ | N/A |

---

## 3. Edge Case Stress Tests

- **The Semantic Black Hole**: Create a node with 100+ high-weight edges. Verify that the Damping Factor ($\lambda$) prevents the activation from consuming the entire graph.
- **Coordinate Collapse**: Shift the L3 root of the Gnosis Tree. Verify that the system can re-calculate Poincaré coordinates without full re-indexing.
- **Zero-Resonance Query**: Input a query with no mapping in the Gnosis Tree. Verify a graceful fallback to standard vector search in the Leaf Store.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_verify_tri_store | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
