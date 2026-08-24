# Run Data Ingestion
# ⬡ OMEGA ⬡ JEM ⬡ la-docs ⬡ how-to ⬡ run-ingestion

This guide explains how to use the Sovereign-Sieve pipeline to ingest knowledge into an entity.

## 1. Prepare the Source
Your data can be:
- A local directory of markdown/text files.
- A list of URLs for the `SovereignScraper`.
- A structured JSONL dataset.

## 2. Execute Ingestion
Use the `omega ingest` command (or the `SovereignScholar` agent):
```bash
omega ingest --entity "MyEntity" --source "./my_docs/" --mode "deep"
```

## 3. The Ingestion Pipeline
The engine performs the following steps:
1. **Sieve**: Filter out noise and PII (via `PIIMasker`).
2. **Chunk**: Break data into semantic pieces.
3. **Embed**: Generate vectors using the local embedding model.
4. **Store**: Save to Qdrant and the entity's `knowledge/` folder.

## 4. Verify Ingestion
Check the entity's knowledge base:
```bash
omega entity-info MyEntity --show-knowledge
```

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: la-docs | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
