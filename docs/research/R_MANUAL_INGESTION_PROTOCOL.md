<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R-doc: Sovereign Manual Ingestion Protocol
**Version**: 1.0.0
**Status**: FINAL
**Date**: 2026-06-09
**Author**: researcher

## Executive Summary
To ensure the Omega Engine remains sovereign and independent of cloud-based documentation availability, we must implement a systematic protocol for the local ingestion of technical manuals. This protocol defines the methods for acquisition, the structure for storage, and the priority for execution, transforming volatile web documentation into permanent, RAG-ready sovereign assets.

## 1. Ingestion Methodology
Different documentation sites require different acquisition strategies to maximize content integrity and minimize noise.

### 1.1 Acquisition Tiers
| Method | Tool | Use Case | Pros | Cons |
| :--- | :--- | :--- | :--- | :--- |
| **Full Mirror** | `firecrawl download` | Comprehensive documentation sites (e.g., Firecrawl, Qdrant) | Preserves structure, converts to clean markdown, local files. | Higher credit cost for very large sites. |
| **Targeted Crawl** | `firecrawl crawl` | Specific sections of a larger site or archives. | High precision, avoids irrelevant pages. | Requires manual path definition. |
| **Direct Fetch** | `curl` / `webfetch` | Single-page manuals, PDFs, or static `.txt` files. | Instant, zero-cost. | No structural discovery. |
| **Agentic Extraction** | `firecrawl agent` | Complex SPAs or gated docs requiring interaction. | Handles JS-heavy sites and auth. | Slowest, highest cost. |

## 2. Sovereign Storage Architecture
Manuals must be stored in a standardized format to ensure seamless integration with the Omega Engine's memory and RAG pipelines.

### 2.1 Directory Structure
All manuals are stored under `data/kb/manuals/`.

```
data/kb/manuals/
└── {tool_name}/
    ├── index.md             # Entry point: TOC, version, and ingestion date
    ├── manifest.json        # URL-to-file mapping and checksums
    ├── pages/               # Clean markdown files (one per original URL)
    │   └── {page_id}.md
    └── assets/              # Images, diagrams, and original PDFs
        └── {asset_id}.png
```

### 2.2 Metadata Requirements
Every ingested page must include a YAML frontmatter block:
```yaml
---
tool: {tool_name}
version: {version}
source_url: {url}
ingested_at: {timestamp}
checksum: {sha256}
tags: [category, feature]
---
```

## 3. Ingestion Pipeline (Workflow)
1. **Discovery**: Use `firecrawl map` to identify the full scope of the documentation.
2. **Acquisition**: Execute `firecrawl download` or `crawl` based on the site architecture.
3. **Normalization**: Convert all outputs to clean markdown using the `firecrawl` standard.
4. **Indexing**: Generate the `manifest.json` and `index.md`.
5. **Verification**: Run a sample query against the local files to ensure RAG-readiness.

## 4. Manuals Priority List (Phase 1)
The following tools are critical to the Omega Engine's core functionality and are prioritized for immediate ingestion.

| Priority | Tool | Target URL | Primary Method | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **P0** | **Firecrawl** | `https://docs.firecrawl.dev` | `firecrawl download` | Primary data acquisition tool; high volatility. |
| **P1** | **Qdrant** | `https://qdrant.tech/documentation` | `firecrawl download` | Core vector store; critical for memory management. |
| **P2** | **Podman** | `https://docs.podman.io` | `firecrawl download` | Infrastructure foundation; critical for sovereignty. |
| **P3** | **AnyIO** | `https://anyio.readthedocs.io` | `firecrawl download` | Runtime foundation; critical for async stability. |
| **P4** | **Llama-cpp-py**| `https://github.com/abetlen/llama-cpp-python` | `firecrawl crawl` | Primary local inference backend. |

## 5. Maintenance & Rotation
Documentation is not static. The following rotation policy is enforced:
- **High Volatility (P0)**: Re-index every 30 days.
- **Medium Volatility (P1-P2)**: Re-index every 90 days.
- **Low Volatility (P3-P4)**: Re-index every 180 days.
- **Triggered Update**: Re-index immediately upon a major version release (e.g., v2 $\rightarrow$ v3).
