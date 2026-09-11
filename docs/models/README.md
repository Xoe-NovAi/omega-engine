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

## Evidence labels

Use these labels when a claim could otherwise be mistaken for fact:

- **Verified metadata** — live provider/API/model-repository metadata.
- **Provider claim** — benchmark or capability reported by the model publisher.
- **Independent report** — third-party evaluation or user report; include provenance.
- **Local measurement** — measured on Omega hardware with a reproducible command.

Never present provider benchmarks as independent validation. If no independent
or local evidence exists, say so explicitly.

## Card contract

Every card must contain:

1. Status, deployment, research date, and confidence.
2. Identity, provider, license, weights, context, modalities, and pricing.
3. Architecture and supported capabilities.
4. Strengths and intended workloads.
5. Quirks, risks, and operational constraints.
6. Benchmarks with evidence labels and caveats.
7. Omega fit, verdict, and next validation step.
8. A minimal invocation or deployment recipe when applicable.
9. Primary sources and access date.

Use lowercase hyphenated filenames:
`docs/models/<provider>-<model>-<variant>.md`.

## Updating a card

- Update the `Last verified` date whenever metadata or availability changes.
- Add local measurements under a dated section; do not overwrite provider claims.
- Keep rejected and retired cards so future evaluations can reuse the verdict.
- Link the card from `README.md`, `docs/ARCHITECTURE.md`, and the ROADMAP when it
  changes a decision or workload.
- Treat a new model as `candidate` until a real Omega task has been tested.

## Minimal template

```markdown
# <Provider>: <Model> <Variant>

| Field | Value |
|---|---|
| Research status | candidate |
| Deployment | hosted trial / local / hybrid / not deployed |
| Last verified | YYYY-MM-DD |
| Confidence | high / medium / low |

## Identity and access
## Architecture and capabilities
## Strengths
## Quirks and risks
## Evidence and benchmarks
## Omega fit and verdict
## Operating recipe
## Open questions
## Sources
```
