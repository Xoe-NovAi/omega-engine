# Model Cards

This directory is Omega Engine Alpha's canonical registry for models we research,
trial, deploy, reject, or retire. A card is a decision record, not marketing
copy: every claim is dated, sourced, and labeled by evidence type.

## Lifecycle

| Status | Meaning |
|---|---|
| `candidate` | Researched or being evaluated; not adopted |
| `active` | Used in an Omega workflow |
| `rejected` | Evaluated and explicitly not adopted |
| `retired` | Previously active, now replaced or discontinued |

Deployment is separate from lifecycle. A hosted trial can be `candidate` while a
local model is `active`; record both states in the card.

## Evidence labels (standardized)

Use these exact labels when a claim could be mistaken for fact:

| Label | Definition |
|---|---|
| **Verified metadata** | Live provider/API/model-repository metadata (catalog fields, repo stats, API responses). |
| **Provider claim** | Benchmark, capability, or feature reported by the model publisher without independent replication. |
| **Independent report** | Third-party evaluation, academic paper, or user report with provenance. |
| **Local measurement** | Measured on Omega hardware with a reproducible command/script. |
| **Not yet measured locally** | Explicit marker for capabilities we plan to validate but have not yet tested. |

Never present provider benchmarks as independent validation. If no independent
or local evidence exists, say so explicitly and use **Not yet measured locally**.

## Card contract (v1)

Every card must contain these nine sections in order:

1. **Status & identity** — research status, deployment, card version, dates, confidence.
2. **Identity & access** — canonical IDs, provider, license, weights, context, modalities, pricing, caching.
3. **Architecture & capabilities** — base family, parameter counts, attention/tokenizer, reasoning, tools, local serving notes.
4. **Strengths** — intended workloads with provider-claimed benchmarks (labeled).
5. **Quirks & risks** — operational constraints, conflicts, capacity limits, privacy gaps.
6. **Evidence & benchmarks** — all scores with evidence labels; caveats on methodology.
7. **Omega fit & verdict** — workload fit table, clear go/no-go verdict, promotion criteria.
8. **Operating recipe** — minimal JSON snippet for the recommended route (OpenRouter, local, etc.).
9. **Open questions / next validation** — dated checklist for promotion.
10. **Sources** — primary URLs with access dates.

## File naming

`docs/models/<provider>-<model>-<variant>.md` (lowercase, hyphenated).

## Optional YAML frontmatter (machine-readable)

Cards may begin with a YAML block for tooling:

```yaml
---
card_version: "1.0"
model_id: "nex-agi/nex-n2.5-pro:free"
provider: "OpenRouter (Nex AGI)"
research_status: "candidate"
deployment: "hosted_trial"
last_verified: "2026-09-11"
confidence: "metadata:high,performance:low"
license: "Apache-2.0"
context_length: 262144
modalities_in: ["text", "image"]
modalities_out: ["text"]
---
```

The frontmatter is optional; the markdown tables remain the human contract.

## Updating a card

- Update `last_verified` whenever metadata or availability changes.
- Bump `card_version` if the template contract changes.
- Add local measurements under a dated subsection; do not overwrite provider claims.
- Keep rejected and retired cards so future evaluations can reuse the verdict.
- Link the card from `README.md`, `docs/ARCHITECTURE.md`, and the ROADMAP when it
  changes a decision or workload.
- Treat a new model as `candidate` until a real Omega task has been tested.

## Minimal template

```markdown
---
card_version: "1.0"
model_id: "<provider>/<model>:<variant>"
provider: "<provider>"
research_status: "candidate"
deployment: "hosted_trial / local / hybrid / not_deployed"
last_verified: "YYYY-MM-DD"
confidence: "high / medium / low (qualify if split)"
license: "<license>"
context_length: <int>
modalities_in: ["text", "image"]
modalities_out: ["text"]
---

# <Provider>: <Model> <Variant>

| Field | Value |
|---|---|
| Research status | candidate |
| Deployment | hosted trial / local / hybrid / not deployed |
| Last verified | YYYY-MM-DD |
| Confidence | high / medium / low |
| Card version | 1.0 |

## Identity and access
## Architecture and capabilities
## Strengths
## Quirks and risks
## Evidence and benchmarks
## Omega fit and verdict
## Operating recipe
## Open questions / next validation
## Sources
```
