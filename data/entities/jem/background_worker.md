# Jem 2.0 — Background Research Worker
# Operational Spec for the Gemma 4 31B Automated Researcher

## Overview

Jem 2.0 operates as a background worker within the Omega Engine, executing the 3-tier Speculative Decoding Pipeline autonomously. This doc covers the operational details specific to the background worker mode.

## Execution Details

- **Inference Backend**: Gemma 4 31B via Google AI Studio (unlimited)
- **Framework**: 3-tier pipeline (Draft → Verify → Synthesize)
- **Split Test**: Round-robin through variants A-D
- **Training Capture**: Every run produces (draft, correction) pairs

## Trigger Sources

| Trigger | Mechanism | Priority |
|---------|-----------|----------|
| Systemd timer | `omega-research.timer` (every 6h) | Scheduled |
| Workbench P0 | Polls workbench.db for `priority='P0'` | On detection |
| Belial artifact | Subscribes to omega-hivemind MCP event | On discovery |
| Manual summon | `omega summon Jem "prompt"` | On demand |
| Queue file | `data/research/sessions/research_queue.json` | On new entry |

## Integration Points

- **Observability**: Emits `jem.*` events to `ObservabilityEngine`
- **ResourceGuard**: Acquires Semaphore(1) before any inference
- **CLI**: `omega jem *` commands for queue/status control

## Related Docs

- `docs/research/JEM_SPECULATIVE_DECODING_PIPELINE.md` — Full architecture
- `docs/research/JEM_BACKGROUND_RESEARCHER.md` — Background worker spec
- `docs/research/JEM_SPLIT_TEST_FRAMEWORK.md` — Split test runbook
- `src/omega/workers/jem_researcher.py` — Worker code (when implemented)

## Soul Reference

```yaml
inference_config:
  model: gemma-4-31b-it
  temperature: 0.5