# 🔱 First Wad
**AP Token**: `AP-FIRST_WAD-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Tutorial documentation for first wad.

---

# Tutorial: Your First WAD

> Build a custom WAD stack with entities that use the ingestion pipeline.
>
> **WAD** stands for **"Where's All the Data?"** — a name coined by Tom Hall in the Doom Bible (id Software, 1993). It was a joke about modders asking where game data was stored. The name stuck for 30+ years.

## What You'll Learn

- How to create a WAD ("Where's All the Data?")
- How to define entities with ingestion capabilities
- How to configure domain allowlists for web scraping
- How to run your first ingestion

## Prerequisites

- Omega Engine installed and running (`make test` passes)
- At least one local model available (`ollama pull qwen3:1.7b`)

## Step 1: Create Your WAD Directory

```bash
mkdir -p config/wads/my_stack
```

## Step 2: Define Your Entity

Create `config/wads/my_stack/entities.yaml`:

```yaml
entities:
  my_researcher:
    role: "researcher"
    description: "A research assistant that ingests and verifies web content"
    domains:
      - research
      - analysis
      - verification
    model: "qwen3:1.7b"
    metadata:
      pantheon: "custom"
      sigil: "R"
```

## Step 3: Configure Domain Allowlist

Create `config/wads/my_stack/ingestion/domains.yaml`:

```yaml
# Domains this WAD is allowed to scrape
# sovereignty: all domains are optional, none are required
allowed_domains:
  - arxiv.org
  - docs.python.org
  - github.com
  - stackoverflow.com

# Domains that require extra verification
high_trust_domains:
  - arxiv.org
  - github.com

# Blocked domains (never scrape)
blocked_domains:
  - facebook.com
  - twitter.com
  - instagram.com
```

## Step 4: Load Your WAD

```bash
# Start the engine with your WAD
source .venv/bin/activate
python3 -m omega.cli.oracle_cli talk \
  --iwad my_stack \
  --msg "hello, I'm testing my custom WAD"
```

Or in Python:

```python
from omega.oracle.wad_loader import WadLoader

loader = WadLoader()
loader.load("my_stack")
print(f"Loaded WAD: my_stack")
print(f"Entities: {list(loader.get_entities().keys())}")
```

## Step 5: Run Your First Ingestion

```python
import anyio
from omega.ingestion.pipeline import IngestionPipeline
from omega.ingestion.ingestion_types import IngestionConfig
from omega.ingestion.extractors import GoogleExtractor

async def main():
    config = IngestionConfig(
        entity_name="my_researcher",
        model_name="qwen3:1.7b",
    )
    
    extractor = GoogleExtractor(config)
    pipeline = IngestionPipeline(config, extractor)
    
    # Ingest a URL
    result = await pipeline.run_source("https://arxiv.org/abs/2301.00001")
    
    if result:
        print(f"Ingested: {result.source}")
        print(f"CAS CID: {result.cas_cid}")
        print(f"Confidence: {result.confidence:.2f}")
    else:
        print("Ingestion failed (pre-flight check or verification failed)")

anyio.run(main)
```

## Step 6: Verify the Ingestion

```python
import anyio
from omega.archive.cas import CASArchiver

async def verify():
    archiver = CASArchiver()
    
    # Check if content was archived
    exists = await archiver.exists(result.cas_cid)
    print(f"Archived: {exists}")
    
    # Retrieve the raw content
    content = await archiver.retrieve(result.cas_cid)
    if content:
        print(f"Content length: {len(content)} bytes")

anyio.run(verify)
```

## What Just Happened

1. **Sentry Probe**: Checked provider health before scraping
2. **T1 Fast Scrape**: Quick extraction of the URL content
3. **T3 Deep Scrape**: Full extraction with enriched metadata
4. **Triangulation**: Cross-checked T1 vs T3 for factual consistency
5. **CAS Store**: Archived raw content with SHA-256 address
6. **LLM Extraction**: Extracted technical facts, gnosis principles, DPO pairs
7. **Persistence**: Stored results in MemoryStore + Qdrant

## Next Steps

- [Configure more domains](../how-to/configure-ingestion.md)
- [Add custom payload fields to Qdrant](../how-to/add-qdrant-payload.md)
- [Read the full ingestion architecture](../explanation/ingestion-architecture.md)
- [API Reference: Ingestion](../reference/api/ingestion.md)
- [API Reference: CAS](../reference/api/cas.md)

## Troubleshooting

**"Sentry probe failed"**
The provider is unhealthy. Check `make health` to see provider status.

**"Budget exceeded"**
Set `max_tokens` higher in `IngestionConfig` or use a local model (zero cost).

**"Triangulation confidence < 0.7"**
The T1 and T3 extractions contradicted each other. This is working as designed — the Sovereign-Sieve rejected low-quality content.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
