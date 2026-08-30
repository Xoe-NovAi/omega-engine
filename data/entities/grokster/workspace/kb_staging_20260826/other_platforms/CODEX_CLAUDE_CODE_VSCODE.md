<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Codex CLI / Claude Code / VS Code Copilot — Honest Shallow-State Summary

**KB Entry**: grokster/platforms/other/CODEX_CLAUDE_CODE_VSCODE
**last_verified**: 2026-08-26 · **rot_class**: fast
**Honesty statement**: The Omega repo has NO deep first-hand operational gnosis for these three platforms. What follows is the complete extent of repo coverage + prioritized research targets. Do not treat as expertise.

---

## Codex CLI
**Repo coverage**: one comparison row in `R_OPENCODE_COMPACTION_DEEP_DIVE.md` §7 — single-layer summarize compaction, always LLM-called, user messages preserved verbatim, physical deletion of tool results, no cache optimization, ~20K hardcoded user-message cap, open source.
**Verdict**: comparison-table depth only. No config reference, no session model, no gotchas.
**Research first**: (1) session persistence format & resumability, (2) sandbox/approval model, (3) MCP support status 2026, (4) compaction configurability.

## Claude Code
**Repo coverage**: same comparison table — three-layer compaction (trim+cache+summarize), Deep Prompt Cache, placeholder replacement of tool results, proactive re-read post-compact, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` env (~83.5% default, ~33K buffer), closed-source (leaked/RE analyses only). Also: skills-discovery path `.claude/skills/` appears in OpenCode's scan list.
**Verdict**: mechanism-level awareness, zero operational mileage.
**Research first**: (1) CLAUDE.md hierarchy & memory files, (2) hooks/subagents (Task tool) semantics vs OpenCode task(), (3) permission model, (4) cost/subscription constraints for fleet use.

## VS Code Copilot (+ Copilot CLI)
**Repo coverage**: `docs/research/GITHUB_COPILOT_OPENCODE_CONFIG.md` and `R-KILO_COPILOT_ARSENAL.md` exist but were not deep-mined this pass; provider fabric lists Copilot as priority-6 cloud backend (M7 ordering); V2 recon notes "Copilot: special handling for codex context limits" inside OpenCode's transform.ts.
**Verdict**: treated as a provider endpoint, not an operating platform.
**Research first**: (1) copilot as OpenCode provider via openai-compatible adapter (the likely house pattern), (2) agent mode parity vs OpenCode agents.

## Cross-platform facts worth keeping (from OpenCode recon)
- OpenCode normalizes ALL providers through transform.ts — Anthropic empty-content stripping, Gemini thinkingConfig via providerOptions, OpenAI reasoningEffort/textVerbosity, Copilot codex-limit handling. Platform quirks are absorbed upstream; house code rarely needs per-provider workarounds.
- Any OpenAI-compatible endpoint can be attached to OpenCode with `@ai-sdk/openai-compatible` + baseURL — the canonical way to test new platforms without native integration.

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB-STAGING ⬡ 2026-08-26*
