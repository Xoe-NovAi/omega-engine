# The Well — Integration Guide for Omega Engine

## Overview

This guide documents how to integrate The Well (structured corrections corpus) into the Omega Engine codebase.

## Files to Copy

```
omega-well/
├── gnosis/well/
│   ├── well.jsonl          # Append-only JSONL corpus
│   └── WISDOM.md           # Rendered human view (auto-generated)
├── scripts/
│   └── well_storage.py     # Core storage + CLI + Make targets
└── tests/
    └── test_well.py        # 7 unit tests
```

## Integration Steps

### 1. Copy Files

```bash
# From omega-well/ extraction package:
cp -r gnosis/well/ $OMEGA_ENGINE_ROOT/gnosis/well/
cp scripts/well_storage.py $OMEGA_ENGINE_ROOT/scripts/well_storage.py
cp tests/test_well.py $OMEGA_ENGINE_ROOT/tests/test_well.py
chmod +x $OMEGA_ENGINE_ROOT/scripts/well_storage.py
```

### 2. Add Make Targets

Add these targets to your `Makefile`:

```makefile
# The Well — structured corrections corpus
well-add: ## Add a Well record
	python3 scripts/well_storage.py add $(KIND) $(DOMAIN) "$(TRIGGER)" "$(RULE)" "$(RATIONALE)" $(if $(TAGS),--tags $(TAGS)) $(if $(PACK),--pack $(PACK))

well-list: ## List Well records
	python3 scripts/well_storage.py list $(if $(KIND),--kind $(KIND)) $(if $(DOMAIN),--domain $(DOMAIN)) $(if $(STATUS),--status $(STATUS))

well-stats: ## Show Well corpus stats
	python3 scripts/well_storage.py stats

well-supersede: ## Supersede a record
	python3 scripts/well_storage.py supersede $(OLD) $(NEW)

well-export: ## Render WISDOM.md + JSONL bundle
	python3 scripts/well_storage.py render-md

well-search: ## Semantic search (stub — see ROADMAP)
	python3 scripts/well_storage.py search $(QUERY)
```

### 3. Environment Variable (Optional)

```bash
# Override default well location (default: gnosis/well relative to script)
export WELL_DIR_OVERRIDE=/path/to/your/gnosis/well
```

### 4. Hook Into Agent Context Injection

At session start, inject top-N active Well records:

```python
# In your agent's session initialization:
from scripts.well_storage import get_active, render_wisdom_md

def get_well_injection(limit=8, domains=None):
    """Get top-N active Well records for context injection."""
    records = get_active()
    if domains:
        records = [r for r in records if r.domain in domains]
    # Sort by recency
    records.sort(key=lambda r: r.ts, reverse=True)
    return records[:limit]

# Inject at session start:
well_records = get_well_injection(limit=8, domains=["harness", "local_ai"])
# Format for injection...
```

### 5. Run Tests

```bash
python3 tests/test_well.py
# or
python3 -m pytest tests/test_well.py -v
```

Expected: 7 tests pass (validation, supersession, rendering, stats, Make targets, UTF-8, secret rejection)

## Well Schema Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| record_id | UUIDv4 | Auto | Unique identifier |
| ts | ISO-8601 UTC | Auto | Timestamp |
| kind | enum | Yes | correction\|preference\|tip\|anti_pattern\|insight\|dream |
| source_pack | string | Yes | Gnosis session ID |
| domain | enum | Yes | local_ai\|consciousness\|psychology\|classical\|games\|harness\|other |
| trigger | string | Yes | What prompted the rule |
| rule | string | Yes | The actionable rule (single sentence) |
| rationale | string | Yes | Why it matters |
| tags | string | No | Comma-separated |
| status | enum | Auto | active\|superseded (default: active) |
| superseded_by | UUID | Conditional | Required if status=superseded |

## Secret Rejection

The Well automatically rejects records containing:
- API keys (`api_key=...`, `sk-...`, `ghp_...`)
- Passwords (`password=...`)
- Secrets (`secret=...`)
- Tokens (`token=...`)

Rejection happens at validation time — record is not written.

## Lifecycle

```
CAPTURED (new record added) 
    → ACTIVE (default status)
    → SUPERSEDED (via `supersede` command, points to replacement)
```

## Integration with Gnosis-Lock

The Well is designed to work with the Gnosis-Lock protocol:
- `make gnosis-lock` → Step 4c sweeps narrative for corrections → `make well-add`
- `make well-export` renders `WISDOM.md` for human review
- `gnosis-leash` injects top-N active records at session start + compaction

## Testing

```bash
# Run all tests
python3 tests/test_well.py

# Or with pytest
python3 -m pytest tests/test_well.py -v
```

All 7 tests should pass:
1. `test_well_add_basic` - basic record creation
2. `test_well_no_secrets` - secret rejection
3. `test_well_supersession_resolves` - supersession chain
4. `test_well_index_matches_jsonl` - WISDOM.md matches JSONL
5. `test_well_jsonl_valid_utf8_and_newlines` - UTF-8 validity
6. `test_well_stats_counts_match` - stats accuracy
7. `test_make_targets_work` - Make targets execute

## Corpus Size

Current corpus: **19 active records** across 6 kinds:
- Correction: 9
- Preference: 3
- Insight: 5
- Dream: 2

The Well is designed for **static injection** (top-N recency + domain filter) at current size (~19 records). Semantic search is deliberately stubbed — becomes relevant at ~30-50 records or with federated Well sharing (see ROADMAP).

## License

Apache-2.0 — see parent repo LICENSE.