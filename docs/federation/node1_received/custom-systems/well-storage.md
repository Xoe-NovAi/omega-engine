# THE WELL STORAGE

**File:** `scripts/well_storage.py`

## Schema
record_id: UUIDv4
ts: ISO-8601 UTC
kind: correction|preference|tip|anti_pattern|insight|dream
source_pack: gnosis session ID
domain: local_ai|consciousness|psychology|classical|games|harness|other
trigger: what prompted the rule
rule: actionable rule/insight
rationale: why it matters
tags: comma-separated
status: active|superseded
superseded_by: UUID of replacement

## Lifecycle
CAPTURED → ACTIVE → SUPERSEDED (mirrors pack lifecycle)

## Writers
- Skill Step 4c: during `/gnosis-lock` reflection
- Prepare-for-compaction "Well sweep"
- CLI: `make well-add KIND=... DOMAIN=... TRIGGER="..." RULE="..." RATIONALE="..." TAGS="..." PACK="..."`

## Readers
- gnosis-leash injects top-6 (harness/local_ai) at session start
- gnosis-leash injects top-8 (harness/local_ai) at compaction
- `make well-export` → WISDOM.md + JSONL bundle

## Evolution
`make well-supersede OLD=<id> NEW=<id>`; injection excludes superseded
`kind:dream` captures sparks (excluded from injection)

## Tests
7 TestWellStorage tests: JSONL validity, secret rejection, supersession chain, index parity, UTF-8, stats, Make targets
