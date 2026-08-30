# 🔱 Omega Engine — R-04 Firecrawl Monitoring System
# ⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ R04

**AP Token**: `AP-RESEARCH-R04-v1.0.0`
**Author**: researcher (Sovereign Master Researcher)
**Date**: 2026-06-09
**Status**: READY

---

## Summary
This document analyzes Firecrawl's monitoring system, which enables recurring data acquisition and automated change detection. It details the "Meaningful Change" judging mechanism, the three modes of change tracking (Markdown, JSON, and Mixed), and the notification infrastructure.

## Findings

### 1. Monitor Architecture
A monitor is a scheduled job that performs a scrape or crawl and compares the result against the last retained snapshot.
- **Targets**:
    - `scrape`: Monitors specific URLs.
    - `crawl`: Monitors an entire domain or sub-section.
- **Schedules**: Supports Cron expressions or natural language (e.g., "every 30 minutes"). Minimum interval is 15 minutes.
- **Retention**: Snapshots are retained for up to 365 days.

### 2. Meaningful Change Judging
To reduce noise, Firecrawl implements an AI-driven judging system.
- **The Goal**: A plain-language description (e.g., "Alert when the price of the Pro plan drops below $50") that defines what constitutes a "meaningful" change.
- **The Process**:
    1. Scrape performs a check.
    2. If the page content has changed, the Judge LLM evaluates the diff against the `goal`.
    3. The judge returns a `judgment` object containing `meaningful` (boolean), `confidence`, and a `reason`.
- **Cost**: 1 additional credit per judged changed page.

### 3. Change Tracking Modes

| Mode | Mechanism | Output | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Markdown** (Default) | Unified Text Diff | `diff.text` (git-style) | General content monitoring, blog posts |
| **JSON** | Per-field Diff | `diff.json` (path-based) | Pricing tables, stock levels, specific specs |
| **Mixed** | Both | `diff.text` + `diff.json` | High-precision monitoring with context |

**JSON Mode Implementation**: Requires a JSON schema or prompt. The diff is keyed by the JSON path (e.g., `plans[0].price`), showing the `previous` and `current` values.

### 4. Notification Infrastructure
Monitors can trigger notifications via:
- **Webhooks**:
    - `monitor.page`: Sent for every page change.
    - `monitor.check.completed`: Sent after the full check is reconciled.
- **Email**: Summaries sent only when meaningful changes, new pages, removed pages, or errors occur.

## Recommendations

1. **Use JSON Mode for Quantitative Data**: For monitoring prices or metrics, avoid Markdown diffs and use JSON mode with a strict schema to enable programmatic reactions.
2. **Define Explicit Goals**: To avoid "alert fatigue," goals should include explicit exclusions (e.g., "Ignore changes to the footer or copyright date").
3. **Implement Webhook Listeners**: For the Omega Engine, a dedicated webhook listener should be implemented to feed monitor events directly into the `MemoryStore` or trigger specific agent tasks.

## Sources
- [Firecrawl Monitoring Docs](https://docs.firecrawl.dev/features/monitoring) — accessed 2026-06-09
- File: `.firecrawl/feature-monitoring.md`

## Implementation Note
_For: P8 Observability / WatchTower_
The `WatchTower` entity should utilize the `/monitor` endpoint to track the health and content of critical external dependencies. The `monitor.page` webhook should be integrated into the Omega Engine's event bus to trigger "Sovereign Alerts" when meaningful changes are detected in target domains.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
