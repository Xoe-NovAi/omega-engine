# Model Cards

This directory is Omega Engine Alpha's canonical registry for models we research,
trial, deploy, reject, or retire. A card is a decision record, not marketing
copy: every claim is dated, sourced, and labeled by evidence type. Cards are
**machine-validated** by the Omega Model Evaluation Registry (OMER) on every
`make lint` run.

## Lifecycle

| Status | Meaning |
|---|---|
| `candidate` | Researched or being evaluated; not adopted |
| `active` | Used in an Omega workflow |
| `rejected` | Evaluated and explicitly not adopted |
| `retired` | Previously active, now replaced or discontinued |

Deployment is separate from lifecycle. A hosted trial can be `candidate` while a
local model is `active`; record both states in the card.

## Rotating stealth aliases are not stable model identities

OpenCode stealth aliases such as `opencode/big-pickle` and
`opencode/space-bunny-free` may change underlying checkpoints, context windows,
output limits, modalities, or privacy terms in place. They can also behave
differently across nodes at the same time. Therefore:

- do not create a permanent OMER card that freezes a rotating alias's current
  context/output limits as model identity;
- do not hardcode those limits under `provider.opencode.models`;
- record dated node-specific observations as operational evidence, not a model
  specification;
- use exact alias IDs for routing and `opencode models <provider> --verbose
  --refresh` for current runtime metadata;
- use named, stable model IDs for OMER cards when evaluating the underlying
  model.

See `docs/OPENCODE_FOUNDATION.md` for the hosted-free policy and privacy tiers.

## Evidence labels (standardized — enforced by OMER)

Use these exact labels in every table's **Evidence** column. The validator
(`scripts/validate_model_cards.py`) rejects any other value:

| Label | Definition | Typical source |
|---|---|---|
| **Provider claim** | Benchmark/capability reported by the publisher, no independent replication | Model card, provider blog |
| **Community benchmark** | Third-party leaderboard score with public methodology | LMSYS, OpenLLM, HF leaderboards |
| **Independent eval** | Controlled third-party study or academic evaluation | Papers, external research teams |
| **Reproduced** | Independently reproduced by an external party on public materials | Replication studies |
| **Local measurement** | Measured on Omega hardware with a reproducible command/script | `make bench`, `scripts/bench.py` |

Never present provider benchmarks as independent validation. If no independent
or local evidence exists, say so explicitly. In prose you may additionally
qualify metadata as *verified* (live catalog/API observation), but table-level
evidence must use one of the five labels above.

## Reproduction status (evidence confidence — enforced by OMER)

For every **Local measurement**, also record a reproduction status in the
Evidence table or a `Reproduction status` row. The five levels:

| Level | Label | Meaning |
|---|---|---|
| 0 | **Indicative** | Informal, not gated; quick sanity check |
| 1 | **Reported** | Described in paper/blog; public materials exist |
| 2 | **Controlled** | Ran through the full validation methodology chain; public materials sufficient to re-run |
| 3 | **Verified** | Controlled + results replicated by an independent team |
| 4 | **Independent** | Verified + multiple independent reproductions |

Provider-declared scores default to **Indicative**. Only **Controlled** or higher
local measurements count toward promoting a card to `active`.

## Card contract (v1 — OMER-validated)

Every card must contain these sections. The first three are **required** by the
validator (their absence fails `make lint`); the rest are the human-readable
contract:

1. **YAML frontmatter** (required — see below).
2. **`## Provider Claims`** — all provider/community benchmark tables with evidence labels. *(required)*
3. **`## Local Measurement`** — dated local runs with reproduction status, hardware, config, command, trials. *(required — write "No local measurements available yet." if none)*
4. **`## Omega Verdict`** — workload-fit table + explicit go/no-go verdict. *(required)*
5. **Status & identity** — research status, deployment, card version, dates, confidence.
6. **Identity & access** — canonical IDs, provider, license, weights, context, modalities, pricing, caching.
7. **Architecture & capabilities** — base family, parameters, attention/tokenizer, reasoning, tools, local serving notes.
8. **Strengths** — intended workloads with provider-claimed benchmarks (labeled).
9. **Quirks & risks** — operational constraints, conflicts, capacity limits, privacy gaps.
10. **Operating recipe** — minimal JSON snippet for the recommended route (OpenRouter, local, etc.).
11. **Open questions / next validation** — dated checklist for promotion.
12. **Sources** — primary URLs with access dates; keep rejected/retired cards for future comparison.

## File naming

`docs/models/<provider>-<model>-<variant>.md` (lowercase, hyphenated).

## Required YAML frontmatter (v1.0 — OMER-enforced)

Every card **must** begin with a YAML block. The OMER validator (`make lint`)
rejects any card without it. Fields follow the OMER v1.0 schema — see
`docs/OMER_FOUNDATION.md` §2.1.

```yaml
---
card_version: "1.0"
model_id: "nex-agi/nex-n2-5-pro:free"
provider: "OpenRouter (Nex AGI)"
research_status: "candidate"        # candidate | active | rejected | retired
deployment: "hosted_trial"          # hosted_trial | local | hybrid | not_deployed
last_verified: "2026-09-11"
confidence: "metadata:high,performance:low"
license: "Apache-2.0"
context_length: 262144
modalities_in: ["text", "image"]
modalities_out: ["text"]
---

## YAML frontmatter (v1.0 — REQUIRED, enforced by OMER)

Every card begins with a YAML block. `make lint` validates it against the OMER
v1.0 schema (Pydantic in `scripts/validate_model_cards.py`):

```yaml
---
card_version: "1.0"
model_id: "nex-agi/nex-n2.5-pro:free"
provider: "OpenRouter (Nex AGI)"
research_status: "candidate"
deployment: "hosted_trial"             # hosted_trial | local | hybrid | not_deployed
last_verified: "2026-09-11"
confidence: "metadata:high,performance:low"
license: "Apache-2.0"
context_length: 262144
modalities_in: ["text", "image"]
modalities_out: ["text"]
---
```

Required keys: `card_version`, `model_id`, `provider`, `research_status`,
`deployment`, `last_verified`, `confidence`, `license`, `context_length`,
`modalities_in`, `modalities_out`.

If `deployment` is `local` or `hybrid`, a `local_hardware_profile` block is
**mandatory** (templated below). The validator hard-blocks the P-core trap:
`allowed_cpus: "0,2,4,6,8,10"` (physical-only) is rejected — use `0-11`.

```yaml
# Required for local/hybrid deployment only:
local_hardware_profile:
  cpu: "i7-13620H"
  cpu_cores: 10
  cpu_threads: 16
  allowed_cpus: "0-11"                 # P-cores + HT siblings — NEVER physical-only
  threads: 8
  ram_gb: 16
  ram_type: "DDR5"
  kv_cache_type: "q8_0"
  flash_attention: true
  max_loaded_models: 1
  quantization: "Q4_K_M"
```

## Adding or updating a card (new-card checklist)

1. Copy the minimal template below; fill frontmatter + every section.
2. Run `./scripts/omer validate docs/models/<card>.md` — fix until clean.
3. Run `make lint` (validates all cards), `make test`, `make docs`.
4. Link the card from `README.md` / `docs/ARCHITECTURE.md` / ROADMAP when it
   changes a decision or workload.
5. Treat a new model as `candidate` until a real Omega task has been tested.

On updates: bump `last_verified` whenever metadata/availability changes; bump
`card_version` if the template contract changes; add local measurements under a
dated subsection — never overwrite provider claims.

## Minimal template

```markdown
---
card_version: "1.0"
model_id: "<provider>/<model>:<variant>"
provider: "<provider>"
research_status: "candidate"
deployment: "hosted_trial"             # hosted_trial | local | hybrid | not_deployed
last_verified: "YYYY-MM-DD"
confidence: "metadata:high,performance:low"
license: "<license>"
context_length: 8192
modalities_in: ["text"]
modalities_out: ["text"]
# Optional for hosted_trial, required for local/hybrid:
# local_hardware_profile:
#   cpu: "i7-13620H"
#   cpu_cores: 10
#   cpu_threads: 16
#   allowed_cpus: "0-11"
#   threads: 8
#   ram_gb: 16
#   ram_type: "DDR5"
#   kv_cache_type: "q8_0"
#   flash_attention: true
#   max_loaded_models: 1
#   quantization: "Q4_K_M"
---

# <Provider>: <Model> <Variant>

| Field | Value |
|---|---|
| Research status | candidate |
| Deployment | hosted trial / local / hybrid / not deployed |
| Last verified | YYYY-MM-DD |
| Confidence | metadata:high,performance:low |
| Card version | 1.0 |

## Identity and access
## Architecture and capabilities
## Strengths
## Quirks and risks
## Provider Claims
| Benchmark | Score | Evidence |
|---|---|---|
| <benchmark> | <score> | **Provider claim** |

## Local Measurement
*No local measurements available yet.*

## Omega Verdict
**Verdict:** candidate

## Operating recipe
## Open questions / next validation
## Sources
```

## CLI Validation (OMER)

Validate any card or the whole registry with the OMER CLI. This runs inside
`make lint` and inside CI, so a card that fails validation blocks a merge.

```bash
./scripts/omer validate docs/models                # whole registry
./scripts/omer validate docs/models/nex-n2-5-pro.md # single card
make lint                                          # all gates incl. cards
```

`--strict` exits non-zero on any failure (default when run through `make lint`).
See `docs/OMER_FOUNDATION.md` for the full design (schema, evidence model,
promotion gates, adapters, roadmap to the `omer` PyPI package).
