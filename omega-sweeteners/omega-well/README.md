# The Well — Structured Corrections Corpus

**Version**: 1.0 | **Status**: Production-ready | **License**: Apache-2.0

The Well is a structured, queryable, self-aging corpus of corrections, coding tips, preferences, anti-patterns, and insights. It provides institutional memory that survives context compactions and agent handoffs.

## Features

- **Append-only truth**: `well.jsonl` — immutable, line-delimited JSON records
- **Human view**: `WISDOM.md` — auto-rendered, grouped by kind (Correction/Preference/Tip/Anti-pattern/Insight/Dream)
- **Lifecycle**: `CAPTURED → ACTIVE → SUPERSEDED` (mirrors gnosis pack lifecycle)
- **Zero external deps**: Pure Python stdlib
- **Secret-safe**: Built-in secret pattern rejection (API keys, passwords, tokens)
- **Tested**: 7 unit tests covering validation, supersession, rendering, stats, Make targets

## Quick Start

```bash
# Install (optional - just copy the gnosis/well/ dir and scripts/well_storage.py)
./install.sh

# Add a record
python3 scripts/well_storage.py add correction harness "trigger" "rule" "rationale" --tags "tag1,tag2" --pack "session-xyz"

# List records
python3 scripts/well_storage.py list --kind correction --status active

# Render human view
python3 scripts/well_storage.py render-md

# Stats
python3 scripts/well_storage.py stats

# Supersede a record
python3 scripts/well_storage.py supersede <old_uuid> <new_uuid>
```

## Make Targets (if integrated into Makefile)

```bash
make well-add KIND=correction DOMAIN=harness TRIGGER="..." RULE="..." RATIONALE="..." [TAGS="..."] [PACK=...]
make well-list [KIND=...] [DOMAIN=...] [STATUS=active|all]
make well-stats
make well-supersede OLD=<uuid> NEW=<uuid>
make well-export   # renders WISDOM.md
```

## Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| record_id | UUIDv4 | Yes | Auto-generated |
| ts | ISO-8601 UTC | Yes | Auto-generated |
| kind | enum | Yes | correction\|preference\|tip\|anti_pattern\|insight\|dream |
| source_pack | string | Yes | Gnosis session ID |
| domain | enum | Yes | local_ai\|consciousness\|psychology\|classical\|games\|harness\|other |
| trigger | string | Yes | What prompted the rule |
| rule | string | Yes | The actionable rule (single sentence preferred) |
| rationale | string | Yes | Why it matters |
| tags | string | No | Comma-separated |
| status | enum | Yes | active\|superseded (default: active) |
| superseded_by | UUID | Conditional | Required if status=superseded |

## Integration

1. Copy `gnosis/well/` and `scripts/well_storage.py` into your project
2. Add `scripts/test_well.py` to your test suite
3. Optionally add Make targets (see `WELL_INTEGRATION.md`)
4. Hook into your agent's context injection to inject top-N active records at session start

## Testing

```bash
python3 -m pytest tests/test_well.py -v
# or
python3 tests/test_well.py
```

## License

Apache-2.0 — see LICENSE in parent repo.