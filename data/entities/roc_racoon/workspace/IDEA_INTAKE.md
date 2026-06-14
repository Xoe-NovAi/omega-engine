# 🦝 ROC_RACOON IDEA INTAKE

This file serves as the raw receptacle for all mind-dumps, experiments, and strategic sparks.

## 🗃️ CORRECTION LOG
- `[2026-06-14]` **Headroom miscategorization**: I classified Headroom as a `[EXP]` Utility Tool / resource monitor (ISS-18, P2). This was WRONG. Headroom is a Rust-core compression proxy achieving 60-95% token reduction with reversible CCR (Compress-Cache-Retrieve) — a direct reference implementation of the Sovereign Compression Layer. Corrected to `[EXP][ARCH]` with ISS-42/P0. 
- `[2026-06-14]` **last30days miscategorization**: I called this "Engagement-Weighted Research" and "compression/time-based synthesis." It is neither. It's a multi-source social research engine (Reddit/X/YT/TikTok/HN/GitHub scoring by engagement). The "30 days" is a recency filter, not a compression window. Corrected to `[EXP]` with ISS-23/P1.
- `[2026-06-14]` **agent-skills reduction**: I reduced this to "Anti-Rationalization tables." It is a full 24-skill production-grade engineering workflow system (Define→Plan→Build→Verify→Review→Ship) with 4 personas, 7 commands, multi-CLI support, and 58.9K stars. Corrected to `[ARCH]` with ISS-40/P0.
- `[2026-06-14]` **open-notebook under-description**: I called it "Grounded Corpus Synthesis" which was vague. It is a self-hosted NotebookLM alternative (PDF/YouTube/web/audio ingestion, RAG chat, multi-speaker podcast gen, 18+ providers, SurrealDB). The Esperanto library is the key pattern for provider abstraction. Corrected with ISS-33/P1.

**Lesson**: The Sovereign Miner must dig deeper than truncated scrapes and repo names. Every mis-categorization was caused by guessing from names instead of reading actual docs.

## 🗃️ RAW INTAKE LOG

### [2026-06-13]
- `[ARCH]` **agent-skills** (ISS-40/P0): https://github.com/addyosmani/agent-skills — 24 production-grade engineering skills for AI coding agents. SKILL.md anatomy with anti-rationalization + verification gates. 58.9K stars. Multi-CLI. Omega adaptation: template for evolving `.opencode/skills/` system.
- `[ARCH]` **open-notebook** (ISS-33/P1): https://github.com/lfnovo/open-notebook — Self-hosted NotebookLM alternative. Multi-modal ingestion, RAG chat, multi-speaker podcast gen. 18+ providers via Esperanto library. SurrealDB backend. Omega adaptation: Esperanto provider patterns, content ingestion pipeline.
- `[EXP]` **last30days-skill** (ISS-23/P1): https://github.com/mvanhorn/last30days-skill — Multi-source social research engine for AI agents. Aggregates Reddit/X/YT/TikTok/HN/GitHub by engagement. 41K stars, #1 trending. Omega adaptation: Agent Skills distribution model case study, --competitors parallel fan-out pattern.
- `[EXP]` `[ARCH]` **headroom** (ISS-42/P0): https://github.com/chopratejas/headroom — Reversible compression proxy. Rust core, SmartCrusher, CCR (Compress-Cache-Retrieve), CacheAligner. 60-95% token reduction with zero accuracy loss. 25K stars. Omega adaptation: reference implementation for Sovereign Compression Layer.
- `[ARCH]` **The Teammate Stack** (ISS-43/P0): Jeremy Utley's 8-file system for AI onboarding. Shift from "prompting" to "onboarding" via a Meta-Prompt interview. Qr code at `docs/intake/8-file-agent-system`. Video: https://www.youtube.com/watch?v=IdOr6WNKLVw

### [2026-06-14]
- `[GNOSIS]` **Correction Lesson**: Never mine from truncated scrapes. Always fetch raw README or delegate research to a task agent when scrape truncates. The name is not the thing — read the docs.
