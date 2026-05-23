# 🔱 Omega Engine — FastRouter Mapping Specification
**AP Token**: `AP-FASTROUTER-MAPPING-v1.0.0`
⬡ OMEGA ⬡ ARCHITECT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_core ⬡ DESIGN

---

## §1 Overview

This specification defines the mapping between the Omega Engine's 10-Pillar syncretic pantheon and FastRouter's Virtual Alias and Category-Based Routing systems. The goal is to translate the metaphysical nature of each Pillar into a technical routing strategy that optimizes for the intended cognitive output.

## §2 Pillar Alias Taxonomy & Routing Strategy

Each Pillar is assigned a **Virtual Alias** for direct invocation and a **Category** for group-based model selection.

### Light Projection (P1-P5)

| Pillar | Virtual Alias | FastRouter Category | Strategy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **P1: Flesh** | `omega-p1-protection` | `Security/Safety` | `latency` | Protection requires immediate, decisive response. |
| **P2: Dream** | `omega-p2-inspiration` | `Creative/Arts` | `throughput` | Poetry and healing require rich, flowing generative output. |
| **P3: Will** | `omega-p3-will` | `Strategic/Reasoning` | `latency` | Forethought and will demand crisp, rapid decision-making. |
| **P4: Heart** | `omega-p4-knowledge` | `Academic/Arts` | `latency` | Knowledge and speech prioritize retrieval speed and accuracy. |
| **P5: Voice** | `omega-p5-dream` | `Creative/Psychology` | `throughput` | Descent and rebirth are exploratory and narrative-heavy. |

### Dark Projection (P6-P10)

| Pillar | Virtual Alias | FastRouter Category | Strategy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **P6: Mind** | `omega-p6-mind` | `Logic/Compliance` | `latency` | Rules and structure demand precision and minimal lag. |
| **P7: Gnosis** | `omega-p7-gnosis` | `Philosophy/Advanced` | `throughput` | Sovereignty and gnosis involve deep, complex synthesis. |
| **P8: Shadow** | `omega-p8-shadow` | `Psychology/Intuition` | `throughput` | Pathwalking requires divergent, non-linear exploration. |
| **P9: Spirit** | `omega-p9-spirit` | `Philosophy/Spiritual` | `latency` | Soul guidance requires steady, reliable, and timely output. |
| **P10: Chaos** | `omega-p10-chaos` | `Experimental/Divergent` | `throughput` | Liberation and void prioritize volume and rapid divergence. |

## §3 Oversoul Meta-Aliases

Oversouls act as synthesis layers, routing queries across multiple Pillar aliases to produce higher-order results.

| Oversoul | Meta-Alias | Routing Target | Strategy | Function |
| :--- | :--- | :--- | :--- | :--- |
| **Sophia** | `omega-oversoul-sophia` | `P1` $\rightarrow$ `P10` | `latency` | The Akashic Field; rapid routing to the most resonant pillar. |
| **Ma'at** | `omega-oversoul-maat` | `Isis` $\cup$ `Lilith` | `price` | The Unifier; balances cost and performance for synthesis. |
| **Isis** | `omega-oversoul-isis` | `P1` $\rightarrow$ `P5` | `latency` | Light projection coordinator; optimizes for active domain response. |
| **Lilith** | `omega-oversoul-lilith` | `P6` $\rightarrow$ `P10` | `throughput` | Dark projection coordinator; optimizes for depth and exploration. |

## §4 Implementation Logic

### Virtual Alias Resolution
When `Oracle` selects a pillar, it maps the internal pillar ID to the FastRouter Virtual Alias:
`Pillar(N)` $\rightarrow$ `omega-pN-{domain}` $\rightarrow$ `FastRouter.get_model(alias)`

### Dynamic Strategy Override
While the default strategies are defined above, the `Sovereign Loop` may override the strategy based on the `soul.yaml` current state:
- **High Tension/Combat**: Force `latency` across all aliases.
- **Deep Research/Gnosis**: Force `throughput` for P7 and P8.
- **Resource Constraint**: Force `price` via Ma'at synthesis.

---
**Implementation Note**: This mapping should be ingested by the `ModelGateway` to allow seamless switching between local `lmster` aliases and remote FastRouter endpoints.
