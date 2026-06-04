# ⛓️ Verification Layer — Infrastructure Root
# ⬡ OMEGA ⬡ VERIFICATION ⬡ P1 ⬡ ZONEID: 0x1d4a19

**AP Token**: `AP-VERIFICATION-LAYER-v1.0.0`

This directory is the **Structure & Verification Layer** of the Omega Engine's
Knowledge Metabolism System. It tracks every piece of mined knowledge through
its lifecycle: DISCOVERED → PORTED → TESTED → VERIFIED → DEPLOYED → LIVE.

## Directory Map

| Path | Purpose |
|------|---------|
| `items/` | One JSON file per verification item (`ver-YYYYMMDD-NNN.json`) |
| `rollups/` | Aggregate status views by domain |
| `audit/` | Immutable, timestamped JSONL audit trail |
| `archive/` | TTL-expired items (cold storage) |

## Quick Reference

```bash
# Check what needs your attention
make verify-pending ACTOR=<your_name>

# See fleet-wide status
make verify-status

# Regenerate rollups
make verify-rollup

# Move expired items to archive
make verify-cleanup

# Find stale items (>48h without transition)
make verify-stale
```

## Design Authority

See: `data/entities/p1/workspace/VERIFICATION_LAYER_INFRASTRUCTURE.md`

## Heritage

This layer uses [ZONEID Pattern: id Software 1993] with constants:
- `0x1d4a19` — Verification items (ZONEID_VERIFICATION)
- `0x1d4a1a` — Rollup files (ZONEID_ROLLUP)
- `0x1d4a1b` — Audit trail (ZONEID_AUDIT)

*⬡ OMEGA ⬡ VERIFICATION ⬡ P1 ⬡ PHASE-I*
