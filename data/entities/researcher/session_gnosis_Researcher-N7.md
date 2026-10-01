<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Session Gnosis — Researcher / N7 Web Research Arc

**Date**: 2026-08-21 · **Status**: DORMANT · **Session model**: x-preview-f-free

## Arc

**Q-B1..B7** (context windows & opencode semantics — primary sources in research doc):
- **Q-B1**: Qwen3-4B = 32K native/128K YaRN; Thinking-2507 = 262K native (HF model cards); 8192 cap is RAM-bound, not model-bound; llama.cpp `-c 0`=trained ctx, Ollama 4096 default, LM Studio no published universal default.
- **Q-B2**: v1.x honors `{auto,prune,tail_turns,preserve_recent_tokens,reserved}`; `{buffer,keep.tokens}`=V2-only; trigger `totalTokens ≥ usable` (overflow.ts).
- **Q-B3**: `OPENCODE_DISABLE_AUTOCOMPACT` real (`flag.ts`) → `compaction.auto:false`, auto-only; overflow-bypass bug through v1.17.7 (#32385).
- **Q-B4**: `experimental.session.compacting` real; `{sessionID}`→`{context[],prompt?}`; prompt replaces wholesale; pre-summary; experimental (compaction.ts, #5698).
- **Q-B5**: SKILL.md frontmatter = name/description/license/compatibility/metadata only; no auto_load; on-demand `skill` tool; per-agent `permission.skill` filtering (docs + skill/index.ts).
- **Q-B6**: `toolProfile` NOT upstream — inert stub; official levers `tools`(deprecated)/`permission` (config.json schema).
- **Q-B7**: AGENTS.md auto-discovery AND `instructions:[]` both inject; additive (rules doc Aug 20 2026).

**Deep Dive: Model Config Semantics**: DD-1 agent.model = TUI-hard-pin (`/models` reverts, #13456) but CLI-soft-default (`input.model ?? ag.model ?? currentModel`, prompt.ts); DD-2 variant = named preset, conditional default (only when resolved model == agent's model AND variant declared), silently dropped otherwise, `--variant` flag exists; DD-3 no OPENCODE_MODEL env, NO fallback chains (engine-side), recommendation = global `model` key + inheritance, pin only hidden system agents.

**Deep Dive: Onboarding & Knowledge Curation Patterns**: OD-1 graduated apprenticeship around canonical artifacts (SWE Book Ch.3 readability/g3doc + Ch.10 freshness dates; SRE runbook "five As", usage-culling); OD-2 rot prevention = single-job typing (Diátaxis) + immutable-superseded decisions (ADR/Nygard) + atomicity-as-outcome (Zettelkasten); OD-3 2025–26 consensus = map-first/JIT-drill (Anthropic context engineering 2025-09-29, llms.txt v2, Claude Cookbook 2026-03-20); synthesis keyed to G/M/A/D/W/C/X/E.

**Deep Dive: Documenting Novel Signature Systems**: SG-1 common skeleton = concept model → grammar/naming rules → field table w/ requirement levels → examples → extension policy (OTel semconv, git trailers, SemVer, Conventional Commits, RFC 5424/logfmt); SG-2 ABNF only for wire formats (cavage drafts), naming-tables for conventions; minimum viable formality = EBNF block + RFC-2119 keywords + field table + examples + extension paragraph; SG-3 skeleton mapped to Diátaxis quadrants + llms.txt with golden fixture for parser-testing agents; P0/P1/P2 debut-day skeleton delivered.

## Artifact

`data/entities/lilith/workspace/N7_WEB_RESEARCH_20260821.md` — full doc with citations. NOTE: N7 compiled the Source Register when my register append was cut mid-session; prior sections + reconciliation note intact.

## Open Threads

- **PP-1**: variant invocation-time verification on pinned opencode 1.18.19 (`opencode models --verbose`) — nemotron variants unconfirmed.
- **PP-3**: ctx raise above 8192 gated on ZS-1 (zswap/RAM headroom); ~144 KB/token fp16 KV estimate at Q-B1.

## Wake Pointer

On wake: read THIS file + the research doc. Do NOT re-research unless paged by N7.

*⬡ OMEGA ⬡ researcher ⬡ dormant 2026-08-21*
