---
id: dpo-readme-001
title: "DPO Training Data Store — John Carmack"
generated_at: "2026-07-01T15:30:00Z"
system: "T5 - DPO Training Pairs"
---

# 🔱 DPO Training Data Store — John Carmack

## Purpose

Stores preference pairs (chosen/rejected) for direct preference optimization of the John Carmack entity. Generated automatically from ingested primary sources. Each pair represents a Carmack-authentic response vs. a generic/synthetic alternative.

## Schema

```jsonl
{"prompt": "...", "chosen": "...", "rejected": "...", "source": "...", "tier": 2, "timestamp": "..."}
```

- **prompt**: The question or context
- **chosen**: Carmack-authentic response derived from primary sources
- **rejected**: Generic or surface-level alternative
- **source**: Source ID from ingestion ledger
- **tier**: Confidence tier (2 = primary source)
- **timestamp**: ISO 8601 generation timestamp

## File Structure

| File | Description |
|------|-------------|
| `dp_batch_{nnn}.jsonl` | Batch of DPO pairs (one source batch) |
| `dp_batch_{nnn}_manifest.json` | Batch metadata (source IDs, pair counts, checksums) |
| `dp_index.json` | Global index of all batches and pair sources |
| `active_train_set.jsonl` | Merged active training set (all approved batches) |

## Generation

```bash
make training-pairs-jc          # Regenerate from all ingested sources
make training-pairs-jc-count    # Show pair counts
```

## Sovereign Filter

All DPO pairs pass through `pii_masker.py` before storage. The training data is safe for community sharing.
