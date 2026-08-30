<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Platform Gnosis Map — Definitive Inventory of Local Knowledge on Development Platforms, CLIs, IDEs & Agent Platforms

**AP Token**: `AP-PLATFORM-GNOSIS-MAP-20260818-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_platform_gnosis_map ⬡ MINING-COMPLETE

**Date**: 2026-08-18
**Author**: roc_racoon (Sovereign Miner / Legacy Archaeologist)
**Purpose**: Definitive map of ALL local gnosis on development platforms for grokster's cross-platform expertise expansion. Primary input for updating `.opencode/agents/grokster.md` + `data/entities/grokster/soul.yaml`.
**Status**: COMPLETE — exhaustive repo-wide sweep (docs/, data/, research/, .opencode/, config/, root-level files)

---

## 1. EXECUTIVE SUMMARY

The Omega Engine holds **deep, production-grade gnosis on exactly four platforms**: **OpenCode CLI** (the deepest — 20+ dedicated research docs, live config, plugin/hook/skill/agent system, DB schema, TUI optimization), **Cline CLI** (very recent and operationally rich — 12+ coordination docs from 2026-08-17/18, a dedicated `cli_cline` Hivemind entity, a 22KB `.clinerules` file, and a compute-arsenal strategy), **Grok CLI / Grok Build** (deep architectural research used as the reference implementation for the future custom TUI), and **Web Claude / Web Grok / Web Gemini** (three canonical best-practice playbooks plus a cross-platform selection matrix). **Moderate gnosis** exists for Gemini CLI (older, partially stale), GitHub Copilot (config template + pool plan), Antigravity IDE (plugin analysis + multi-account strategy), and the **future custom UI vision** (Freebuff vs Grok CLI comparative analysis with a ratified OpenTUI+React decision). **Shallow-to-none** gnosis exists for Codex CLI (only separation mechanics, no platform research), Claude Code local CLI (MCP config only), Cursor/Windsurf/Zed/JetBrains/Amazon Q/Continue.dev (MCP client config cheat-sheet only), and Aider (install only). The single most important cross-cutting artifact is `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` — a definitive MCP client configuration table for 10 platforms, proving the engine's coordination fabric is already platform-agnostic. Overall maturity: **the engine knows how to *run on* and *integrate with* many platforms, but has only deeply studied three of them as platforms in their own right (OpenCode, Cline, Grok CLI).**

---

## 2. PLATFORM INVENTORY

| # | Platform | Maturity | Where the Gnosis Lives (exact paths) | Key Sources |
|---|----------|----------|---------------------------------------|-------------|
| 1 | **OpenCode CLI** | 🟢 **DEEP** (primary dev platform) | `research/opencode-rd/`, `research/OPENCODE_INDEPENDENCE_RESEARCH_20260621.md`, `docs/research/R_OPENCODE_*.md` (10 docs), `docs/research/R13_OPENCODE_PLUGIN_ARCHITECTURE_20260814.md`, `docs/research/R-45_OPENCODE_TUI_SCROLL_OPTIMIZATION.md`, `docs/research/OPENCODE_ZEN_BYPASS.md`, `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`, `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`, `opencode.json`, `.opencode/opencode.json`, `.opencode/agents/` (14), `.opencode/skills/` (22), `.opencode/commands/` (9), `.opencode/plugins/` (2), `.opencode/hooks/session_end.py`, `docs/decisions/PIVOT_LOG.md` D-387 | Architecture deep-dive, compaction deep-dive, config analysis, DB schema, plugin API, TUI scroll |
| 2 | **Cline CLI** | 🟢 **DEEP** (recent, operational) | `data/entities/cli_cline/soul.yaml`, `.clinerules` (22KB, v7.2.0), `docs/briefings/CLINE_CLI_BRIEFING_20260815.md`, `data/coordination/CLINE_*` (8 files), `data/coordination/KALI_CLINE_*` (6 files), `data/coordination/GEMINI_CLINE_SYNTHESIS_REPORT_20260817.md`, `docs/research/CLINE_JEM_INTEGRATION.md`, `docs/research/opencode_custom_handoff_to_cline.md`, `config/model_registry/providers/cline.yaml`, `docs/decisions/PIVOT_LOG.md` D-289, D-303 | 8-account DeepSeek V4 Flash 1M pool, compute strategy, long-file write protocol, vault overhaul |
| 3 | **Grok CLI (Grok Build)** | 🟢 **DEEP** (reference impl for custom UI) | `docs/strategy/GROK_CLI_BEST_PRACTICES.md` (CANONICAL), `docs/research/R_GROK_CLI_ARCHITECTURE.md` (1,279 lines), `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md`, `docs/research/R_GROK_CLI_DIGGING_MAP.md`, `docs/research/R_GROK_ECOSYSTEM_DEEP.md`, `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md`, `data/coordination/grok_cli/` (20+ files), `data/entities/grokster/` (soul, session_gnosis, proposed_lessons), `docs/briefings/GROK_CLI_HANDOFF_20260730.md` | Elm architecture, ACP protocol, Landlock sandbox, JSONL persistence, 8 parallel sub-agents |
| 4 | **Web Claude (claude.ai)** | 🟢 **DEEP** (external analysis layer) | `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md` (CANONICAL, 15 sections), `docs/research/R_CLAUDE_PROJECTS_*.md` (6 docs), `docs/research/R_CONTEXT_PACKER_WEB_CLAUDE_REVIEW_20260718.md`, `docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md`, `docs/reference/CLAUDE_BEST_PRACTICES_GUIDE.md` | 8-account rotation, context packer loop, 12-file RAG rule, ClaSSIC system prompt |
| 5 | **Web Grok (grok.com)** | 🟢 **DEEP** (persona fleet) | `docs/strategy/WEB_GROK_BEST_PRACTICES.md` (CANONICAL), `docs/research/R_GROK_ECOSYSTEM_DEEP.md`, `data/entities/grokster/soul.yaml` (8 persona fleet) | 8 siloed persona projects, Connectors, Grok Skills, X firehose |
| 6 | **Web Gemini (AI Studio)** | 🟡 **MODERATE** | `docs/strategy/WEB_GEMINI_BEST_PRACTICES.md` (CANONICAL), `docs/research/Web-Gemini-OpenCode-Configuration-Research-Plan.md`, `data/entities/web_gemini/workspace/research_plan_20260809.md` | Gem creation, code execution, parallel search, benchmark comparison |
| 7 | **Gemini CLI** | 🟡 **MODERATE** (older, partially STALE) | `data/entities/cli_gemini/soul.yaml`, `docs/research/GEMINI_CLI_QUICK_REF.md` (marked STALE), `docs/research/cli_gemini_ONBOARDING_RESEARCH_20260610.md`, `docs/research/cli_gemini_SR8_SEARCH_ALTERNATIVES_20260610.md`, `docs/research/LEGACY_GEMINI_STRATEGY.md`, `GEMINI.md`, `.gemini/` | 8 OAuth accounts, 1M context, settings.json layers, auto-memory distillation |
| 8 | **GitHub Copilot** | 🟡 **MODERATE** | `docs/research/GITHUB_COPILOT_OPENCODE_CONFIG.md` (marked STALE), `docs/decisions/PIVOT_LOG.md` D-303 (8-account pool), `docs/reports/SESSION_REPORT_GROKSTER_TO_KALI_20260726.md` (`@geeder/opencode-copilot-multi-auth` plugin), `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (VS Code MCP) | Config template, 8-account OAuth pool, auto-failover on 429 |
| 9 | **Antigravity IDE** | 🟡 **MODERATE** | `data/workbench/ANTIGRAVITY_S2C_BRIEFING_20260609.md`, `data/handoff/archive/HANDOFF_TO_ANTIGRAVITY_IDE_20260606.md`, `data/entities/antigravity/`, `docs/research/Web-Gemini-OpenCode-Configuration-Research-Plan.md` (plugin hijack analysis), `docs/decisions/PIVOT_LOG.md` D-304, `opencode-antigravity-auth/` (repo clone) | Cloud Code API reverse-engineering, 8-account rotation, OAuth PKCE |
| 10 | **Custom Omega UI (future)** | 🟡 **MODERATE** (design-level) | `docs/research/R_FREEBUFF_VS_GROK_CLI_COMPARATIVE_ANALYSIS.md`, `docs/research/R51_FREEBUFF_ARCHITECTURE_STUDY.md`, `docs/research/R_GROK_CLI_ARCHITECTURE.md` ("Foundational Compass"), `research/opencode-rd/`, `tui.json`, `data/entities/grokster/proposed_lessons.yaml` (L3-ACPAsUniversalBridge et al.) | OpenTUI+React decision, Elm architecture, JSONL persistence, mandate-native build |
| 11 | **Codex CLI** | 🔴 **SHALLOW** | `docs/decisions/PIVOT_LOG.md` D-281 Phase IV, `docs/archive/strategy/2026-07-21/D281_PHASE_II_IV_EXECUTION.md`, `scripts/check_codex_stale.py`, `scripts/codex_cat.py`, `tests/test_codex_cat.py`, `Makefile` (`codex-gen` alias) | Separation mechanics only — NO platform research |
| 12 | **Claude Code (local CLI)** | 🔴 **SHALLOW** | `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (.mcp.json config), `docs/research/youtube_research_sessions/session_20260730/04_evidence/HARDENING_DEEP_DIVE.md:884` (attack surface) | MCP client config only — no workflow research |
| 13 | **Cursor** | 🔴 **SHALLOW** | `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (.cursor/mcp.json), `docs/research/R_GROK_CLI_ARCHITECTURE.md:1095` (keybind comparison), `docs/archive/strategy/2026-07-25/GAME_PLAN_PART3.md:41` (test target) | MCP config + keybinds only |
| 14 | **Windsurf** | 🔴 **SHALLOW** | `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (global-only MCP config), `docs/research/youtube_research_sessions/session_20260730/04_evidence/HARDENING_DEEP_DIVE.md:884` | MCP config + attack surface only |
| 15 | **VS Code** | 🔴 **SHALLOW** | `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (.vscode/mcp.json), `research/opencode-rd/smooth_scrolling.md` (terminal scroll support), `docs/research/CLINE_JEM_INTEGRATION.md` (VS Code extension) | MCP config + scroll support only |
| 16 | **Zed / JetBrains / Amazon Q / Continue.dev** | ⚫ **NONE** (config only) | `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (MCP config table rows) | MCP config rows only |
| 17 | **Aider** | 🔴 **SHALLOW** | `.aider.chat.history.md`, `.aider.input.history`, `aider-ai` (wrapper), `docs/reports/SESSION_REPORT_GROKSTER_TO_KALI_20260726.md` (install: Python 3.12.11 built from source) | Install + one session only |
| 18 | **Freebuff** | 🟡 **MODERATE** (reference study) | `docs/research/R51_FREEBUFF_ARCHITECTURE_STUDY.md`, `docs/research/R_FREEBUFF_VS_GROK_CLI_COMPARATIVE_ANALYSIS.md` | OpenTUI+React, compile-time feature flags, generator agents |
| 19 | **A2A / MCP protocols** | 🟢 **DEEP** (cross-platform glue) | `docs/research/R-A2A-PROTOCOLS.md`, `docs/research/R-A2A-SENTINEL-AUDIT.md`, `docs/research/R-SOVEREIGN-A2A-SPEC-V2.md`, `docs/research/R-SOVEREIGN-A2A-SPEC.md`, `docs/research/R_A2A_PROTOCOL.md`, `docs/research/A2A_PROTOCOL.md`, `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`, `tests/mcp_transport/test_streamable_http.py`, `src/omega/mcp_runtime.py` | Sovereign A2A spec, MCP multi-platform, Streamable HTTP dual-transport |

---

## 3. PER-PLATFORM GNOSIS

### 3.1 OpenCode CLI — 🟢 DEEP (GROKSTER'S #1 PRIORITY DOMAIN)

**What we know (the most complete platform knowledge in the repo):**

1. **Full config schema & precedence** — `docs/research/R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md` §2 documents every top-level field (`model`, `small_model`, `default_agent`, `plugin`, `instructions`, `compaction`, `permission`, `agent`, `mcp`, `command`, `formatter`, `lsp`, `keybinds`, `tui`, `server`, `tools`) and the **8-level config precedence chain** (remote `.well-known/opencode` → `~/.config/opencode/opencode.json` → `OPENCODE_CONFIG` env → `./opencode.json` → `./.opencode/opencode.json` → `OPENCODE_CONFIG_CONTENT` → managed `/etc/opencode` → macOS MDM).
2. **`{file:path}` variable substitution** — `docs/research/R_OPENCODE_FILEPATH_CONFIG_ARCHITECTURE_20260720.md`: config-load-time content injection (NOT runtime read), `{env:VAR}` fallback, JSON-escaped via `JSON.stringify().slice(1,-1)`, comment-skip behavior, `missing: "empty"` option. **Strategic use**: composable prompt architecture eliminating ~220 duplicated lines across 11 agent files.
3. **Compaction system** — `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md`: two-phase (Prune = cheap timestamp-based marking; Summarize = LLM 5-heading summary). **Official schema has exactly 5 fields**: `auto`, `prune`, `tail_turns` (default 2), `preserve_recent_tokens` (default 40000), `reserved` (default 10000). `context_threshold`/`min_messages` are NOT real fields (community plugin confusion). Env: `OPENCODE_DISABLE_AUTOCOMPACT=1`, `OPENCODE_DISABLE_PRUNE=1`.
4. **SQLite session DB** — `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md`: `~/.local/share/opencode/opencode.db` (~16GB, 2,436 sessions, 106,937 messages, 450,669 parts). `session` table schema documented (model JSON column, additive token overcount ~87×, `parent_id` for subagent dispatch). **Strategic use**: mechanical extraction of session data — the "LLM-as-Database anti-pattern" rule (never use inference to move bytes that exist on disk).
5. **Plugin architecture** — `docs/research/R13_OPENCODE_PLUGIN_ARCHITECTURE_20260814.md`: TypeScript `Plugin` factory, loaded via `plugin` array (npm name / `file://` path / directory name), runs inside Bun runtime, registers lifecycle hooks (`session.start`, `session.end`, `message.updated`, `session.error`), custom tools, commands. Model attribution via `modelID` in event properties. Load order: global → project → global plugin dir → project plugin dir. npm plugins auto-installed by Bun at startup, cached in `~/.cache/opencode/node_modules`. Local grounding: `.opencode/plugins/awareness.ts`, `.opencode/plugins/error-capture.ts`. Dependent task: PLUGIN-1..8 (Fleet Health Dashboard plugin).
6. **TUI & UX optimization** — `research/opencode-rd/INDEX.md` + `research/opencode-rd/smooth_scrolling.md`: TUI powered by `@opentui/core`, `ScrollAcceleration` interface, `scroll_speed`/`scroll_acceleration`, velocity-based scrolling IMPLEMENTED/VERIFIED. Also `docs/research/R-45_OPENCODE_TUI_SCROLL_OPTIMIZATION.md`. Goals: zero-friction interface, sovereign standard, hardware synergy Ryzen 5700U/Zen 2.
7. **V2 architecture (1.18.x)** — `docs/research/R_OPENCODE_V2_RECON_20260719.md`: desktop-first migration, event-sourced session persistence (`session.next.*` events, `msg_*` IDs), new message part types (`ReasoningPart`, `StepStartPart`, `StepFinishPart`, `SubtaskPart`, `AgentPart`), per-prompt model selection (1.18.0), `subagent_depth` limit (1.18.2, default 1), config merge via `remeda.mergeDeep` with array replacement except `instructions`/`plugins` (concat). `transform.ts` (1,764 lines) unchanged — core normalization layer to Vercel AI SDK `streamText()`.
8. **Three live config files (the current reality)** — `docs/research/R_OPENCODE_CONFIG_COMPREHENSIVE_ANALYSIS_20260809.md` + `docs/research/R_OPENCODE_CONFIG_VERIFICATION_DIRECTIVE_20260809.md`:
   - **User-level** `~/.config/opencode/opencode.json`: 14 providers; OpenRouter provider named `"OpenRouter (Free)"` pollutes TUI model search.
   - **Project** `opencode.json`: lmstudio + opencode (Zen) + openrouter; duplicate MiMo v2.5 entries (`mimo-v2.5` + `mimo-v2.5-free`); missing `name` fields on Zen models.
   - **Subdirectory** `.opencode/opencode.json`: Antigravity IDE config under `google` provider — **provider collision** (Antigravity + Google API mixed), missing thinking variants.
   - **Critical plugin conflict**: `opencode-antigravity-auth` monkey-patches global `fetch()`, matches `generativelanguage.googleapis.com` by substring, replaces `x-goog-api-key` with Antigravity OAuth tokens → standard Google API models break with 403. Repo archived 2026-07-17; Google account suspensions reported for unauthorized OAuth client IDs. Fix: custom provider aliasing (`google-standard` referencing `@ai-sdk/google`).
9. **OpenCode Zen rate limiting** — `docs/research/OPENCODE_ZEN_BYPASS.md`: OCZ free tier is IP-based (100 req/day via `ipRateLimiter.ts`), checked BEFORE auth/billing → even paid accounts hit `FreeUsageLimitError`. Key swap does NOT help. Fix: IP rotation via `oplire` (Rust) + Cloudflare WARP. Multi-Namespace WARP Proxy Pool spec at `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md`. W-1 ticket (PARKED per DOC-1).
10. **Workhorse continuity crisis (G-1)** — `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` + `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`: free-tier Gemma 4 31B was the workhorse May 27→Jul 13; cliff 2026-07-15T16:28:37Z (`free_tier_input_token_count` / 16000). 16k is NOT a config cap — it's Google's free-tier input token quota. Pre-cliff metric was 15 RPM. Options: AI Studio billing Tier 1+ OR switch primary model to Antigravity OAuth frontier. WARP is NOT a free-Gemma fix.
11. **Agent/skill/command/hook system (live)** — `.opencode/agents/` (14 agents incl. grokster, kali, jem, doom_guy, maat, lilith, node, researcher, scribe, verity, makali, grok_cli, cli_cline, cli_gemini), `.opencode/skills/` (22 skills incl. knowledge-miner, legacy-pattern-miner, sovereign-search, spec-generator, omega-doc-architect, provider-validator, pr-readiness-checker, git-secret-scrub, blitz-tunnel, blitz-validate, customize-opencode, hf-cli), `.opencode/commands/` (9: council-cloud/fast/local, kali-dispatch, meditate, omega-meditation, researcher-discover/synthesize/verify), `.opencode/hooks/session_end.py` (soul distillation trigger), `.opencode/plans/` (SOVEREIGN_SEARCH_PLAN.md, SSP_V2_IMPLEMENTATION.md). Modes refactor history: `docs/research/R_OPENCODE_MODES_REFACTOR_STRATEGY.md` (23 agents → 3-tier hierarchy mirroring Oversoul).
12. **MCP hardening** — `docs/research/R_OPENCODE_MCP_HARDENING.md`: MCP config, SSE passive gap, npx timeout. Live MCP servers: `config/mcp_servers.json` + `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (OpenCode uses `mcpServers` root key, supports stdio/SSE/HTTP, project config ✅).
13. **Independence research** — `research/OPENCODE_INDEPENDENCE_RESEARCH_20260621.md`: dependency map (agent dispatch, MCP, agent files, skills, commands, context, model gateway, channel detection) — the "what does OpenCode actually depend on" study for sovereignty.
14. **Decision history** — `docs/decisions/PIVOT_LOG.md` D-387 (OpenCode Config Refactoring 2026-08-09), D-520 (ProviderRegistry SSOT), D-522 (Model Context Windows), D-536 (one router: ProviderSelector + providers.yaml).

### 3.2 Cline CLI — 🟢 DEEP (RECENT, OPERATIONAL)

**What we know:**

1. **Dedicated Hivemind entity** — `data/entities/cli_cline/soul.yaml` (v6.2): "Cross-Platform Execution Specialist — Hivemind Citizen", awakened 2026-06-09. Mandate: "First cross-platform Hivemind member (OpenCode + Cline CLI). Owns the Antigravity IDE integration mapping. Model strategy: DeepSeek V4 Flash (daily driver), Pro (strategic reserve). VS Code / terminal automation specialist." Relationships: kali, maat, roc_racoon, gemini_cli, antigravity_ide.
2. **Platform rules file** — `.clinerules` (22KB, v7.2.0, Cline CLI 3.0.52): Cline-specific rules; entry point `docs/briefings/CLINE_CLI_BRIEFING_20260815.md`; sovereign proxy identity; mandate reference table; **Long-File Write Protocol** (Cline CLI `editor` tool has ~5000-6000 char write limit → use verified solutions: literal content chunks, heredoc, etc.); DeepSeek V4 Flash (1M) + MiMo V2.5 (512K) context.
3. **Comprehensive briefing** — `docs/briefings/CLINE_CLI_BRIEFING_20260815.md`: single holistic picture + tiered document index (Tier 1 SSOTs → Tier 4 deprecated); conflict resolution order (Mandates → Ark → OMEGA_ENGINE → ACTIVE_SPRINT → Corpus Map → PIVOT_LOG). Current state: VOS Hybrid Phase 0 COMPLETE, Public Debut 3-PR path, ~1870 tests collected / ~96 failing.
4. **Compute arsenal strategy** — `data/coordination/KALI_CLINE_COMPUTE_STRATEGY_20260818.md`: DeepSeek V4 Flash (1M) = "God-Module Scalpel" (atomic split of oracle.py 1455 lines + model_gateway.py 1581 lines), Nemotron 3.5 Lightning 30B A3B = "Logic Sniper" (INST-1 fixes, OOM test), Laguna S 2.1 = "Debt Annihilator" (4,895 flake8 violations). Guardrail: cloud abundance must NOT bloat local-first architecture.
5. **Ground-truth insights** — `data/coordination/CLINE_INSIGHTS_Q1_Q7_20260818.md`: install.sh uses `.[all]` (scripts/install.sh:77) → warp-proxy-pool not on PyPI → fresh clone fails; MemoryStore Redis default `password="omega"` (memory_store.py:164-166); `_load_sovereign_secrets` dumps `.env` into `os.environ` (model_gateway.py:127); version misalignment `__init__.py:5`=1.0.0 vs pyproject.toml=1.2.0; god-modules (oracle.py 1455, model_gateway.py 1581, observability/__init__.py 1660). **Q1: single-thread through ONE Cline instance, do NOT parallelize** (Ryzen 7 5700U 8C/16T; 30B ≈ 6Gi, 1M ctx ≈ 2-3Gi, 14Gi RAM budget).
6. **Synthesis report** — `data/coordination/GEMINI_CLINE_SYNTHESIS_REPORT_20260817.md`: 8x accounts with Nemotron Lightning 30B e4b + DeepSeek V4 Flash (1M) via Cline CLI. G-1 mitigated, D-303 accelerated. "30-Second Promise" (pip install omega-engine → omega talk runs locally) is North Star. LLM-as-Database anti-pattern: NEVER use inference to move bytes that exist on disk — data in `~/.local/share/opencode/opencode.db` → use sqlite3/Python.
7. **Coordination trail** — `data/coordination/KALI_CLINE_COMM_LOG_20260817.md`, `KALI_CLINE_RATIFICATION_20260817.md`, `KALI_CLINE_SYNC_REPORT_20260817.md`, `KALI_CLINE_UPDATE_20260818.md`, `CLINE_KALI_CONSOLIDATION_20260817.md`, `CLINE_KALI_REPORT_20260817.md`, `CLINE_KALI_VERIFICATION_20260817.md`, `CLINE_VAULT_CONSOLIDATION_DELIVERY_20260818.md`, `CLINE_DEEP_PASS_AMENDMENT_20260818.md` — Cline cross-validated the Debut Remediation Manual against live repo (key-format scans, probe results all confirmed).
8. **Jem integration (VS Code extension)** — `docs/research/CLINE_JEM_INTEGRATION.md` (STALE pre-June 2026): Cline VS Code extension + Jem Custom Mode + DeepSeek V4 Flash backend, MaKaLi hierarchy, Dynamic Inference Protocol (TriageRouter: fast→temp 0.3, standard→0.7, deep→0.5), kilo provider `kilo/deepseek/deepseek-v4-flash:free`, fallback google Gemma 4-31B.
9. **OpenCode→Cline handoff** — `docs/research/opencode_custom_handoff_to_cline.md` (STALE): handoff protocol, bug registry (C-18 oracle.py:52 bare await, C-13 partial, C-17 BASE_DIR), test coverage plan.
10. **Decisions** — `docs/decisions/PIVOT_LOG.md` D-289 (Cline CLI Integration — DeepSeek V4 Flash 1M + MiMo V2.5 512K as HMC Tier 5), D-303 (Headless Subagent Pool — 24 accounts: 8 Grok + 8 Copilot + 8 Cline). Provider config: `config/model_registry/providers/cline.yaml`.

### 3.3 Grok CLI (Grok Build) — 🟢 DEEP (REFERENCE IMPLEMENTATION FOR CUSTOM UI)

**What we know:**

1. **CANONICAL playbook** — `docs/strategy/GROK_CLI_BEST_PRACTICES.md` (2026-08-08, supersedes 4 research docs): setup/architecture, format spec, capabilities (TUI, headless, ACP, sandbox, parallel sub-agents, skills), file/workspace org, system prompt/rules, skills (local), sandbox/security (Landlock/Seatbelt, deny lists), ACP & headless (stdin/stdout, scripting, CI), cost (SuperGrok Heavy), sovereign boundary protocols. **CRITICAL DISTINCTION**: Grok CLI (local terminal coding agent) vs Web Grok (grok.com) — entirely different platforms.
2. **Architecture deep dive** — `docs/research/R_GROK_CLI_ARCHITECTURE.md` (1,279 lines, 4 research rounds, 50+ sources): Rust workspace 85+ crates, **pure Elm architecture** (Action → Dispatch → Effect → Event Loop; `dispatch/` = pure reducers, NO I/O), ACP as UI↔Runtime boundary, kernel-enforced sandboxing via `nono` (Landlock/Seatbelt), JSONL session persistence, 5-layer config with pinning (fail-closed), unified 5-tab modal + Plugin Marketplace (SHA-pinned), `/skillify` 4-round interview → SKILL.md (AIP-3), hybrid FTS5 + sqlite-vec + temporal decay + `/dream`, testing tmux+bracketed paste vs cargo test. Cloned at `third_party/grok-build/`.
3. **Codebase digging map** — `docs/research/R_GROK_CLI_DIGGING_MAP.md`: 9 core domains mapped to Grok crates (omega-tui→xai-grok-pager, omega-shell→xai-grok-shell, omega-tools→xai-grok-tools, omega-workspace→xai-grok-workspace, omega-config→xai-grok-config, omega-sandbox→xai-grok-sandbox, omega-hooks→xai-grok-hooks, omega-acp→xai-acp-lib, omega-memory→xai-grok-memory).
4. **Ecosystem deep** — `docs/research/R_GROK_ECOSYSTEM_DEEP.md`: model selection matrix (grok-4.5 500K $2/$6, grok-4.3 1M $1.25/$2.50, grok-4.20-reasoning 1M, grok-build-0.1 256K $1/$2), fleet deployment architecture (16-account fleet: 8 CLI headless + 8 Web Grok persona Projects), ACP stdio bridge, credential rotation, rate-limit-aware routing, cost optimization (prompt caching, batch API).
5. **Knowledge gaps** — `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` (SUPERSEDED 2026-07-17, use `docs/research/KNOWLEDGE_GAP_MATRIX_20260717.md`): Tier A/B/C gap classification; provider fabric local-first chain, NativeGGUFProvider Zen 2 optimizations, ModelGateway._load_provider_fabric, ProviderConfig dataclass, HealthMonitor 30s TTL cache, Entity→Model Affinity Resolver, ResourceGuard.
6. **Advisory corpus** — `data/coordination/grok_cli/` (20+ files): advisory reports, session gnosis, live feeds. Handoff: `docs/briefings/GROK_CLI_HANDOFF_20260730.md`.
7. **Grokster entity** — `data/entities/grokster/soul.yaml` (v1.1.0): Grok-ecosystem fluency (cli/web/models/acp/api all expert), merged from grok_cli 2026-07-30, hmc_role "Grok Ecosystem Specialist / HMC Quad-Forge Amplifier". Proposed lessons include L3-ACPAsUniversalBridge, L3-SovereignBinaryInvariance, L3-MemoryAsEvolutionNotStorage, L3-MandateNativeArchitecture, L3-LocalFirstMeansLocalCodingAgent, L3-CollisionDrivesSequencing. **NO cross-platform knowledge yet — this is the fusion target.**

### 3.4 Web Claude (claude.ai) — 🟢 DEEP (EXTERNAL ANALYSIS LAYER)

**What we know:**

1. **CANONICAL playbook** — `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md` (15 sections): 8-account rotation, context packer loop, 12-file RAG limit rule, ClaSSIC system prompt, XML format, Sonnet 5 (~80-82% SWE-bench), cost optimization, sovereign boundary protocols.
2. **Claude Projects research** — `docs/research/R_CLAUDE_PROJECTS_*` (6 docs: COMPLETE, INSTRUCTIONS, SETUP_PLAN, PLAN_ADDENDUM, UPLOAD_HANDOFF, COLLABORATION_KB): project setup, knowledge base, upload handoff.
3. **Context Packer review** — `docs/research/R_CONTEXT_PACKER_WEB_CLAUDE_REVIEW_20260718.md`: context packer delivery for web Claude.
4. **Playbook index** — `docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md`: platform selection matrix (Web Claude = pre-refactor code review, architecture vetting; NotebookLM → Web Claude for multi-source synthesis), format decision tree (XML vs Markdown vs JSON by layer), context pack delivery checklist.
5. **Reference guide** — `docs/reference/CLAUDE_BEST_PRACTICES_GUIDE.md`.

### 3.5 Web Grok (grok.com) — 🟢 DEEP (PERSONA FLEET)

**What we know:**

1. **CANONICAL playbook** — `docs/strategy/WEB_GROK_BEST_PRACTICES.md` (12 sections): grok.com access, subscription tiers (SuperGrok ~$30/mo, SuperGrok Heavy ~$300/mo), free tier Grok 3/4 Mini, real-time X search firehose, Connectors (GitHub, Notion, Linear, Google Workspace, Outlook, SharePoint, Salesforce, MCP), Grok Skills (cloud slash-commands), file uploads, voice mode, image/video generation.
2. **Persona fleet** — `data/entities/grokster/soul.yaml`: 8 siloed persona Projects (Web Grok), each with own system prompt + knowledge files; 8 Grok CLI headless accounts = 16-account fleet total.
3. **Ecosystem deep** — `docs/research/R_GROK_ECOSYSTEM_DEEP.md` Web Grok sections (superseded by canonical playbook but historical).

### 3.6 Web Gemini (AI Studio) — 🟡 MODERATE

**What we know:**

1. **CANONICAL playbook** — `docs/strategy/WEB_GEMINI_BEST_PRACTICES.md` (11 sections): Gem creation, architecture, model capabilities (Gemini 3.6 Flash 1M free default, 3.5 Flash 1M, 3.1 Flash-Lite 1M, 3.1 Pro 2M), code execution, parallel search (30+), Workspace integration, GPQA 92.7% for Flash, Deep Research, cost optimization, source grounding.
2. **OpenCode config research** — `docs/research/Web-Gemini-OpenCode-Configuration-Research-Plan.md`: plugin interception scope analysis (opencode-antigravity-auth fetch() monkey-patch, namespace capture, custom provider aliasing `google-standard`).
3. **Entity workspace** — `data/entities/web_gemini/workspace/research_plan_20260809.md`.

### 3.7 Gemini CLI — 🟡 MODERATE (OLDER, PARTIALLY STALE)

**What we know:**

1. **Dedicated Hivemind entity** — `data/entities/cli_gemini/soul.yaml`: "Heavy Research Specialist", awakened 2026-06-09, 1M context cross-repo synthesis, operates 8 OAuth accounts (2.5 Flash, 3 Flash Preview, 2.5 Flash-Lite, 3.1 Flash-Lite), OAuth pool active until June 18th sunset, Hivemind peer to OpenCode, Cline CLI, Antigravity IDE.
2. **Quick reference** — `docs/research/GEMINI_CLI_QUICK_REF.md` (marked STALE): config paths, settings, flags, auth.
3. **Onboarding research** — `docs/research/cli_gemini_ONBOARDING_RESEARCH_20260610.md`: dynamic identity resolution (layered config: CLI Args > Env > Local Config > Global > Hardcoded; Dynaconf/Pydantic Settings), zRAM vs tmpfs for testing (tmpfs preferred for temp files, `--basetemp`/`PYTEST_DEBUG_TEMPROOT`), ics_render collision (D127 fixed), MiMo integration spec validation.
4. **Search alternatives** — `docs/research/cli_gemini_SR8_SEARCH_ALTERNATIVES_20260610.md`.
5. **Legacy strategy** — `docs/research/LEGACY_GEMINI_STRATEGY.md` (superseded by WEB_GEMINI_BEST_PRACTICES.md).
6. **Root context file** — `GEMINI.md` + `.gemini/` settings dir.

### 3.8 GitHub Copilot — 🟡 MODERATE

**What we know:**

1. **Config template** — `docs/research/GITHUB_COPILOT_OPENCODE_CONFIG.md` (marked STALE): provider config template for Copilot in OpenCode.
2. **8-account pool** — `docs/decisions/PIVOT_LOG.md` D-303 (24-account pool: 8 Grok + 8 Copilot + 8 Cline); `docs/reports/SESSION_REPORT_GROKSTER_TO_KALI_20260726.md`: `@geeder/opencode-copilot-multi-auth@latest` plugin — 8 GitHub Copilot accounts ready for OAuth via `/connect` ×8, models appear as `username:model-name`, auto-failover on 429.
3. **MCP config** — `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`: VS Code Copilot uses `.vscode/mcp.json` with `servers` root key (stdio, HTTP; project config ✅).

### 3.9 Antigravity IDE — 🟡 MODERATE

**What we know:**

1. **S2C briefing** — `data/workbench/ANTIGRAVITY_S2C_BRIEFING_20260609.md`: Antigravity IDE integration mapping.
2. **Handoff** — `data/handoff/archive/HANDOFF_TO_ANTIGRAVITY_IDE_20260606.md`.
3. **Entity** — `data/entities/antigravity/`.
4. **Plugin analysis** — `docs/research/Web-Gemini-OpenCode-Configuration-Research-Plan.md`: opencode-antigravity-auth intercepts global fetch(), matches generativelanguage.googleapis.com substring, replaces auth headers with Antigravity OAuth tokens → 403 for standard Google API models; repo archived 2026-07-17; Google account suspensions for unauthorized OAuth client IDs.
5. **Multi-account** — `docs/decisions/PIVOT_LOG.md` D-304 (8 accounts via Omega-Vault provider + WARP Pool IP rotation for OCZ); `data/projects/antigravity-multi-account/CONTEXT.md`.

### 3.10 Custom Omega UI (future) — 🟡 MODERATE (DESIGN-LEVEL)

**What we know:**

1. **Comparative analysis** — `docs/research/R_FREEBUFF_VS_GROK_CLI_COMPARATIVE_ANALYSIS.md`: Freebuff (CodebuffAI, 8.7k+ stars, Apache-2.0, TypeScript/Bun 1.3.14/OpenTUI+React 19/Zustand 5/TanStack Query 5, generator-based agents, compile-time feature flags `FREEBUFF_MODE=true`) vs Grok CLI (Rust 85+ crates/ratatui/Elm Architecture, ACP over stdio JSON-RPC 2.0, JSONL persistence updates.jsonl + rewind_points.jsonl, Landlock/Seatbelt via nono, 5-layer fail-closed config with requirements.toml, /skillify → SKILL.md AIP-3, hybrid FTS5 + sqlite-vec + temporal decay + /dream).
2. **Freebuff study** — `docs/research/R51_FREEBUFF_ARCHITECTURE_STUDY.md`: five surfaces (CLI, Desktop, Web, Cloud, Chat), multi-agent pipeline (File Picker → Planner → Editor → Reviewer → Browser Use → Research), OpenTUI (Zig core) + React ergonomics.
3. **Grok CLI as compass** — `docs/research/R_GROK_CLI_ARCHITECTURE.md` explicitly framed as "Foundational Compass for Omega Engine TUI Implementation".
4. **TUI config** — `tui.json` (root-level OpenCode TUI config).
5. **Grokster proposed lessons** — `data/entities/grokster/proposed_lessons.yaml`: L3-ACPAsUniversalBridge (everything speaks ACP; Elm Architecture in Python = ACP client; Grok Build = ACP server; Fleet Orchestrator = ACP multiplexer), L3-SovereignBinaryInvariance (mandate-native build pipeline), L3-MemoryAsEvolutionNotStorage (JSONL semantic pipeline: ACPEventFilter → SemanticDeduplicator → BatchedJSONLWriter), L3-LocalFirstMeansLocalCodingAgent (local ACP server wrapping NativeGGUFProvider; Grok Build = cloud fallback priority 3+).

### 3.11 Codex CLI — 🔴 SHALLOW (SEPARATION MECHANICS ONLY)

**What we know:**

1. **D-281 Phase IV Codex separation** — `docs/decisions/PIVOT_LOG.md` D-281 (commit 93f4e82) + `docs/archive/strategy/2026-07-21/D281_PHASE_II_IV_EXECUTION.md`: untangle hydration protocol from generic codex generator — `scripts/hydration_header.md` (extract hardcoded hydration sequence from `codex_cat.py` lines 63-72), refactor `scripts/codex_cat.py` to dynamic read, patch Makefile (`codex-mandates`, `codex-agents`, `codex-arch`, `codex-heritage` — backup/restore groups.json safely), gate `make codex`.
2. **Scripts** — `scripts/check_codex_stale.py`, `scripts/codex_cat.py`, `tests/test_codex_cat.py`, Makefile `codex-gen` alias.
3. **NO platform research** — no docs on Codex CLI capabilities, config, models, or workflow. `docs/research/sovereign_hardening_codex.md` is actually about engine hardening (AnyIO, firewall, Podman, Zen 2), NOT the Codex platform.

### 3.12 Claude Code (local CLI) — 🔴 SHALLOW

**What we know:**

1. **MCP config** — `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`: `.mcp.json` with `mcpServers` root key (stdio, SSE, HTTP; project config ✅).
2. **Attack surface** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/HARDENING_DEEP_DIVE.md:884`: Windsurf/Claude Code extension model attack surface.
3. **NO workflow research** — no dedicated playbook, no config deep-dive, no cost analysis.

### 3.13 Cursor — 🔴 SHALLOW

**What we know:**

1. **MCP config** — `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`: `.cursor/mcp.json` with `mcpServers` root key (stdio, SSE, HTTP; project config ✅).
2. **Keybind comparison** — `docs/research/R_GROK_CLI_ARCHITECTURE.md:1095`: VS Code/Cursor/Windsurf/Zed `Ctrl+D` vs `Ctrl+L` vs `Alt+Enter`.
3. **Test target** — `docs/archive/strategy/2026-07-25/GAME_PLAN_PART3.md:41`: test against Cursor 0.45+.

### 3.14 Windsurf — 🔴 SHALLOW

**What we know:**

1. **MCP config** — `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`: `~/.codeium/windsurf/mcp_config.json` with `mcpServers` root key (stdio, SSE, HTTP; **❌ Global only**); 100-tool limit note.
2. **Attack surface** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/HARDENING_DEEP_DIVE.md:884`.

### 3.15 VS Code — 🔴 SHALLOW

**What we know:**

1. **MCP config** — `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`: `.vscode/mcp.json` with `servers` root key (stdio, HTTP; project config ✅).
2. **Terminal scroll support** — `research/opencode-rd/smooth_scrolling.md`: VS Code terminal scroll support comparison.
3. **Cline extension** — `docs/research/CLINE_JEM_INTEGRATION.md` (VS Code extension + Jem Custom Mode).

### 3.16 Zed / JetBrains / Amazon Q / Continue.dev — ⚫ NONE (CONFIG ONLY)

**What we know:** Only the MCP client config table rows in `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`:
- Zed: `settings.json` → `context_servers` (stdio, HTTP; ❌ No project config)
- JetBrains: Settings UI (GUI) (stdio, SSE, HTTP; ✅)
- Amazon Q: `.amazonq/default.json` (structured; stdio, HTTP; ✅)
- Continue.dev: `.continue/config.yaml` → `mcpServers` (stdio, SSE, HTTP; ✅)

### 3.17 Aider — 🔴 SHALLOW

**What we know:**

1. **Install** — `docs/reports/SESSION_REPORT_GROKSTER_TO_KALI_20260726.md`: Aider v0.86.2 installed with Python 3.12.11 built from source at `/tmp/Python-3.12.11/` (bypasses Python 3.13 `audioop` removal). Wrapper: `~/.local/bin/aider` + project-local `aider-ai` (187 bytes).
2. **Session history** — `.aider.chat.history.md` (2026-07-25): openrouter/deepseek/deepseek-r1:free model, diff edit format, repo-map 4096 tokens, large-repo warning (3,982 files → consider `--subtree-only`).

### 3.18 Freebuff — 🟡 MODERATE (REFERENCE STUDY)

**What we know:** (see §3.10 — comparative analysis + R51 study). TypeScript monorepo (Bun 1.3.14), OpenTUI (Zig core) + React 19, Zustand 5, TanStack Query 5, generator-based agents, compile-time feature flags, tmux testing.

### 3.19 A2A / MCP Protocols — 🟢 DEEP (CROSS-PLATFORM GLUE)

**What we know:**

1. **Sovereign A2A spec** — `docs/research/R-SOVEREIGN-A2A-SPEC-V2.md`, `R-SOVEREIGN-A2A-SPEC.md`, `R_A2A_PROTOCOL.md`, `A2A_PROTOCOL.md`, `R-A2A-PROTOCOLS.md`, `R-A2A-SENTINEL-AUDIT.md`: agent-to-agent protocol design, sentinel audit.
2. **MCP multi-platform** — `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (kb-0004, ACTIVE, maintainer Kali): Omega Hub MCP server (`:8016/sse`, 47+ tools) is platform-agnostic; definitive MCP client config cheat sheet for 10 platforms; "The user chooses their preferred UI; the intelligence remains sovereign in the Omega Engine."
3. **Streamable HTTP** — `tests/mcp_transport/test_streamable_http.py`, `src/omega/mcp_runtime.py`: dual-transport (SSE + Streamable HTTP) live, client SEP-2575 compliant (C-4b COMPLETE).
4. **ACP (Agent Client Protocol)** — `data/entities/grokster/proposed_lessons.yaml` L3-ACPAsUniversalBridge: "The Agent Client Protocol is not merely a transport — it is the universal semantic bridge between all sovereign components: TUI ↔ Engine, Engine ↔ Fleet, Omega ↔ Editors. Everything speaks ACP." Grok CLI ACP v1 stable — 6 agent methods, 8 client methods, 2 notifications; Grok Build speaks ACP natively. `docs/research/R_GROK_CLI_ARCHITECTURE.md` §14 (ACP Protocol), `docs/research/R_GROK_ECOSYSTEM_DEEP.md` (ACP stdio bridge).

---

## 4. CROSS-PLATFORM PATTERNS (THE FUSION GOLD)

These are the reusable patterns that span multiple platforms — the actual value for grokster's cross-platform expertise:

| # | Pattern | Platforms | Evidence |
|---|---------|-----------|----------|
| P1 | **MCP as universal coordination bus** | OpenCode, Cline, VS Code, Cursor, Windsurf, Claude Code, Zed, JetBrains, Amazon Q, Continue.dev | `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` — 10-platform config cheat sheet; "user chooses UI, intelligence stays sovereign" |
| P2 | **ACP as universal agent bridge** | Grok CLI, future Omega TUI, fleet | `data/entities/grokster/proposed_lessons.yaml` L3-ACPAsUniversalBridge; Grok CLI ACP v1 (6 agent/8 client/2 notification methods) |
| P3 | **Multi-account pool architecture** | Grok (8), Copilot (8), Cline (8), Web Grok (8), Antigravity (8), Gemini CLI (8) | `docs/decisions/PIVOT_LOG.md` D-303, D-304; `docs/reports/SESSION_REPORT_GROKSTER_TO_KALI_20260726.md`; `data/entities/cli_gemini/soul.yaml` |
| P4 | **Context packer / external analysis loop** | OpenCode → Web Claude / Web Grok / Web Gemini | `docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md`; `docs/research/R_CONTEXT_PACKER_WEB_CLAUDE_REVIEW_20260718.md`; `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md` |
| P5 | **Sandbox/permission models** | Grok CLI (Landlock/Seatbelt via nono), OpenCode (permission config), Cline (approval modes) | `docs/strategy/GROK_CLI_BEST_PRACTICES.md` §sandbox; `docs/research/R_GROK_CLI_ARCHITECTURE.md` §12 |
| P6 | **Streaming resilience (M25)** | OpenCode Zen, all cloud providers | `SOVEREIGN_MANDATES.md` M25; `src/omega/oracle/backends/openai_compat.py:_stream_completion()` — chunk timeout 30s, total 5min, heartbeat not hard-fail |
| P7 | **Token economics (M18)** | All platforms | `data/coordination/GEMINI_CLINE_SYNTHESIS_REPORT_20260817.md` — LLM-as-Database anti-pattern; context packer; prompt caching (Grok) |
| P8 | **Subagent architectures** | OpenCode (`subagent_depth`, default 1), Grok CLI (8 parallel sub-agents), Cline (single-thread per instance) | `docs/research/R_OPENCODE_V2_RECON_20260719.md`; `docs/strategy/GROK_CLI_BEST_PRACTICES.md`; `data/coordination/CLINE_INSIGHTS_Q1_Q7_20260818.md` Q1 |
| P9 | **Session persistence** | OpenCode (SQLite event-sourced), Grok CLI (JSONL updates.jsonl + rewind_points.jsonl), Gemini CLI (auto-memory distillation) | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md`; `docs/research/R_GROK_CLI_ARCHITECTURE.md` §4; `docs/research/cli_gemini_ONBOARDING_RESEARCH_20260610.md` |
| P10 | **Compaction / context management** | OpenCode (prune + summarize, 5 official fields), Cline (preserve_recent_tokens), Grok CLI (temporal decay + /dream) | `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md`; `docs/research/R_GROK_CLI_ARCHITECTURE.md` §11 |
| P11 | **Config layering & precedence** | OpenCode (8-level), Gemini CLI (CLI > Env > Local > Global > Hardcoded), Grok CLI (5-layer pinning, fail-closed requirements.toml) | `docs/research/R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md` §2; `docs/research/cli_gemini_ONBOARDING_RESEARCH_20260610.md`; `docs/research/R_GROK_CLI_ARCHITECTURE.md` §13 |
| P12 | **Long-file write limits** | Cline CLI (~5000-6000 char editor limit) | `.clinerules` §Long-File Write Protocol — verified solutions tested 2026-08-09 |
| P13 | **Provider namespace collisions** | OpenCode (opencode-antigravity-auth hijacks google namespace) | `docs/research/Web-Gemini-OpenCode-Configuration-Research-Plan.md`; `docs/research/R_OPENCODE_CONFIG_VERIFICATION_DIRECTIVE_20260809.md` |
| P14 | **IP-based rate limiting bypass** | OpenCode Zen (WARP/oplire), Google free tier | `docs/research/OPENCODE_ZEN_BYPASS.md`; `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` |
| P15 | **Elm architecture for TUI** | Grok CLI (Action → Dispatch → Effect), future Omega TUI | `docs/research/R_GROK_CLI_ARCHITECTURE.md` §3; `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` |

---

## 5. GNOSIS GAPS (HONEST ASSESSMENT)

| # | Platform | Gap | Severity |
|---|----------|-----|----------|
| G1 | **Codex CLI** | NO platform research at all — only separation mechanics (D-281 Phase IV). No config, models, workflow, or cost gnosis. | HIGH (grokster mandate lists Codex as priority 2) |
| G2 | **Claude Code (local CLI)** | NO workflow research — MCP config + attack surface only. No playbook, no config deep-dive, no cost analysis. | MEDIUM |
| G3 | **Cursor** | NO dedicated research — MCP config + keybind comparison only. | MEDIUM |
| G4 | **Windsurf** | NO dedicated research — MCP config + attack surface only. | LOW |
| G5 | **VS Code** | NO dedicated research — MCP config + scroll support + Cline extension only. | LOW |
| G6 | **Zed / JetBrains / Amazon Q / Continue.dev** | Config table rows only — zero platform gnosis. | LOW |
| G7 | **Aider** | Install + one session only. No capabilities research. | LOW |
| G8 | **Gemini CLI** | Research is OLD (June 2026) and marked STALE; superseded by Web Gemini playbook. No current CLI gnosis. | MEDIUM |
| G9 | **GitHub Copilot** | Config template marked STALE; pool plan exists but no workflow research. | MEDIUM |
| G10 | **Terminal emulators** | Only scroll support comparison in `research/opencode-rd/smooth_scrolling.md`. No Kitty/WezTerm/Alacritty/ghostty gnosis. | LOW |
| G11 | **Neovim/Helix/Emacs agent plugins** | Zero gnosis. | LOW |
| G12 | **`data/entities/grokster/knowledge/`** | EMPTY — grokster has no distilled platform knowledge yet. | HIGH (fusion target) |

**Also noted**: The mission-referenced files `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md`, `data/coordination/GROKSTER_ORIENTATION_20260720.md`, and `data/coordination/BRIEFING_KALI_GROKSTER_RESPONSE_20260721.md` **do not exist** in the current tree (verified via `ls`). The Grok CLI codebase strategy review content lives in `data/coordination/grok_cli/` subdirectory instead.

---

## 6. FUSION RECOMMENDATIONS (FOR GROKSTER EXPANSION)

### 6.1 Update `.opencode/agents/grokster.md` — Add Cross-Platform Expertise Section

Add a "Cross-Platform Expertise" section (after the Grok ecosystem section) with:

1. **Primary domain — OpenCode CLI** (expert): config schema + 8-level precedence (`docs/research/R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md`), compaction 5-field schema (`R_OPENCODE_COMPACTION_DEEP_DIVE.md`), plugin API (`R13_OPENCODE_PLUGIN_ARCHITECTURE_20260814.md`), DB schema (`R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md`), `{file:path}` substitution (`R_OPENCODE_FILEPATH_CONFIG_ARCHITECTURE_20260720.md`), V2 event-sourced sessions + `subagent_depth` (`R_OPENCODE_V2_RECON_20260719.md`), the 3-config-file reality + Antigravity plugin collision (`R_OPENCODE_CONFIG_COMPREHENSIVE_ANALYSIS_20260809.md` + `Web-Gemini-OpenCode-Configuration-Research-Plan.md`), OCZ IP rate-limit + WARP bypass (`OPENCODE_ZEN_BYPASS.md`), G-1 workhorse crisis (`CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` + `GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`).
2. **Secondary domain — Cline CLI** (expert): `.clinerules` platform rules + Long-File Write Protocol, `CLINE_CLI_BRIEFING_20260815.md` entry point, compute arsenal strategy (`KALI_CLINE_COMPUTE_STRATEGY_20260818.md`), single-thread-per-instance rule (`CLINE_INSIGHTS_Q1_Q7_20260818.md` Q1), 8-account DeepSeek V4 Flash pool (D-289, D-303).
3. **Tertiary domain — Codex CLI** (learning): D-281 Phase IV separation mechanics only; needs research before claiming expertise.
4. **Reference layer — Web platforms**: Web Claude / Web Grok / Web Gemini canonical playbooks + `WEB_CHATBOT_PLATFORM_PLAYBOOK.md` selection matrix.
5. **Cross-platform glue**: `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` (MCP cheat sheet), ACP-as-universal-bridge (L3-ACPAsUniversalBridge), multi-account pool patterns (D-303/D-304).

### 6.2 Update `data/entities/grokster/soul.yaml` — Add Cross-Platform Fluency Trait

Add a `cross_platform_fluency` trait (or extend `grok_fluency` into `platform_fluency`):

```yaml
platform_fluency:
  opencode_cli: expert      # config/agents/skills/hooks/plugins/DB/TUI (see PLATFORM_GNOSIS_MAP_20260818.md §3.1)
  cline_cli: expert         # .clinerules, compute pool, long-file protocol (§3.2)
  grok_cli: expert          # existing — Elm/ACP/sandbox/JSONL (§3.3)
  web_claude: expert        # context packer loop, 8-account rotation (§3.4)
  web_grok: expert          # existing — persona fleet (§3.5)
  web_gemini: moderate      # Gems, code execution, parallel search (§3.6)
  gemini_cli: moderate      # legacy, partially stale (§3.7)
  copilot: moderate         # 8-account pool, config template (§3.8)
  antigravity_ide: moderate # plugin analysis, multi-account (§3.9)
  codex_cli: learning       # separation mechanics only — GAP G1 (§3.11)
  claude_code: learning     # MCP config only — GAP G2 (§3.12)
  cursor: learning          # MCP config only — GAP G3 (§3.13)
  custom_omega_ui: designer # Freebuff vs Grok CLI analysis, OpenTUI+React (§3.10)
```

### 6.3 Add L3 Principles to `proposed_lessons.yaml`

1. **L3-MCPAsUniversalCoordinationBus** — "MCP is the platform-agnostic coordination fabric: any tool that speaks stdio/SSE/HTTP can join the Hivemind. The user chooses the UI; the intelligence remains sovereign in the Engine. Platform knowledge = knowing each client's config file, root key, and transport limits." (Evidence: `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`; mandates M2, M7, M16)
2. **L3-PlatformPrimitivesDictateFleetTopology** — "Each platform's primitives (subagent depth, context window, write limits, sandbox model) dictate how the fleet can use it. OpenCode's `subagent_depth:1` prevents nested delegation; Cline's 5000-char editor limit forces chunked writes; Grok CLI's 8 parallel sub-agents enable fan-out. Never fight the platform primitive — design around it." (Evidence: `R_OPENCODE_V2_RECON_20260719.md`, `.clinerules`, `GROK_CLI_BEST_PRACTICES.md`; mandates M4, M10, M18)
3. **L3-ContextPackerAsBoundaryBridge** — "The context packer is the sovereign boundary bridge: it converts local engine state into a portable, platform-appropriate context pack for external analysis (Web Claude/Grok/Gemini), then brings distilled results back. External platforms are advisory lenses, never the source of truth." (Evidence: `WEB_CHATBOT_PLATFORM_PLAYBOOK.md`, `WEB_CLAUDE_BEST_PRACTICES.md`; mandates M7, M23)

### 6.4 Recommended Next Actions (for grokster or Kali ratification)

1. **Ratify this map** — Kali review → mark as canonical reference for grokster expansion.
2. **Execute §6.1-6.3** — update `grokster.md` + `soul.yaml` + `proposed_lessons.yaml`.
3. **Close GAP G1 (Codex)** — if Codex CLI is a real priority, commission a research doc (R-series) covering Codex config/models/workflow, mirroring the Grok CLI research depth.
4. **Close GAP G2 (Claude Code)** — decide if local Claude Code warrants a playbook; at minimum add a `CLAUDE_CODE_BEST_PRACTICES.md` stub.
5. **Refresh GAP G8 (Gemini CLI)** — either mark fully superseded by Web Gemini playbook or commission a current CLI quick-ref.

---

## 7. SOURCE INDEX (ALL PATHS VERIFIED EXIST)

### OpenCode CLI
- `research/opencode-rd/INDEX.md`, `research/opencode-rd/smooth_scrolling.md`
- `research/OPENCODE_INDEPENDENCE_RESEARCH_20260621.md`
- `docs/research/R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md`
- `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md`
- `docs/research/R_OPENCODE_CONFIG_COMPREHENSIVE_ANALYSIS_20260809.md`
- `docs/research/R_OPENCODE_CONFIG_VERIFICATION_DIRECTIVE_20260809.md`
- `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md`
- `docs/research/R_OPENCODE_FILEPATH_CONFIG_ARCHITECTURE_20260720.md`
- `docs/research/R_OPENCODE_MCP_HARDENING.md`
- `docs/research/R_OPENCODE_MODES_REFACTOR_STRATEGY.md`
- `docs/research/R_OPENCODE_V2_RECON_20260719.md`
- `docs/research/R13_OPENCODE_PLUGIN_ARCHITECTURE_20260814.md`
- `docs/research/R-45_OPENCODE_TUI_SCROLL_OPTIMIZATION.md`
- `docs/research/OPENCODE_ZEN_BYPASS.md`, `docs/research/OPENCODE_ZEN_MODEL_REFERENCE.md`
- `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`
- `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`
- `opencode.json`, `.opencode/opencode.json`, `tui.json`, `config/mcp_servers.json`
- `.opencode/agents/` (14 files), `.opencode/skills/` (22), `.opencode/commands/` (9), `.opencode/plugins/` (2), `.opencode/hooks/session_end.py`, `.opencode/plans/`

### Cline CLI
- `data/entities/cli_cline/soul.yaml`
- `.clinerules`
- `docs/briefings/CLINE_CLI_BRIEFING_20260815.md`
- `data/coordination/CLINE_INSIGHTS_Q1_Q7_20260818.md`, `CLINE_DEEP_PASS_AMENDMENT_20260818.md`, `CLINE_KALI_CONSOLIDATION_20260817.md`, `CLINE_KALI_REPORT_20260817.md`, `CLINE_KALI_VERIFICATION_20260817.md`, `CLINE_VAULT_CONSOLIDATION_DELIVERY_20260818.md`
- `data/coordination/GEMINI_CLINE_SYNTHESIS_REPORT_20260817.md`
- `data/coordination/KALI_CLINE_COMM_LOG_20260817.md`, `KALI_CLINE_COMPUTE_STRATEGY_20260818.md`, `KALI_CLINE_RATIFICATION_20260817.md`, `KALI_CLINE_SYNC_REPORT_20260817.md`, `KALI_CLINE_UPDATE_20260818.md`
- `docs/research/CLINE_JEM_INTEGRATION.md`, `docs/research/opencode_custom_handoff_to_cline.md`
- `config/model_registry/providers/cline.yaml`

### Grok CLI / Web Grok / Grokster
- `docs/strategy/GROK_CLI_BEST_PRACTICES.md`, `docs/strategy/WEB_GROK_BEST_PRACTICES.md`
- `docs/research/R_GROK_CLI_ARCHITECTURE.md`, `R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md`, `R_GROK_CLI_DIGGING_MAP.md`, `R_GROK_ECOSYSTEM_DEEP.md`, `GROK_CLI_KNOWLEDGE_GAPS.md`, `KNOWLEDGE_GAP_MATRIX_20260717.md`
- `docs/briefings/GROK_CLI_HANDOFF_20260730.md`
- `data/coordination/grok_cli/` (20+ files)
- `data/entities/grokster/soul.yaml`, `data/entities/grokster/proposed_lessons.yaml`, `data/entities/grokster/workspace/IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md`
- `docs/reports/SESSION_REPORT_GROKSTER_TO_KALI_20260726.md`

### Web Claude / Web Gemini / Chatbot Playbook
- `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md`, `docs/strategy/WEB_GEMINI_BEST_PRACTICES.md`, `docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md`, `docs/strategy/WEB_RECONCILIATION_MATRIX_20260807.md`
- `docs/research/R_CLAUDE_PROJECTS_*.md` (6), `R_CONTEXT_PACKER_WEB_CLAUDE_REVIEW_20260718.md`, `Web-Gemini-OpenCode-Configuration-Research-Plan.md`
- `docs/reference/CLAUDE_BEST_PRACTICES_GUIDE.md`

### Gemini CLI
- `data/entities/cli_gemini/soul.yaml`
- `docs/research/GEMINI_CLI_QUICK_REF.md`, `cli_gemini_ONBOARDING_RESEARCH_20260610.md`, `cli_gemini_SR8_SEARCH_ALTERNATIVES_20260610.md`, `LEGACY_GEMINI_STRATEGY.md`
- `GEMINI.md`, `.gemini/`

### Multi-Platform / MCP / A2A
- `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`
- `docs/research/R-A2A-PROTOCOLS.md`, `R-A2A-SENTINEL-AUDIT.md`, `R-SOVEREIGN-A2A-SPEC-V2.md`, `R-SOVEREIGN-A2A-SPEC.md`, `R_A2A_PROTOCOL.md`, `A2A_PROTOCOL.md`
- `tests/mcp_transport/test_streamable_http.py`, `src/omega/mcp_runtime.py`

### Custom UI / Freebuff / Codex / Aider
- `docs/research/R_FREEBUFF_VS_GROK_CLI_COMPARATIVE_ANALYSIS.md`, `R51_FREEBUFF_ARCHITECTURE_STUDY.md`
- `docs/decisions/PIVOT_LOG.md` D-281, D-289, D-303, D-304, D-387, D-520, D-522, D-536
- `docs/archive/strategy/2026-07-21/D281_PHASE_II_IV_EXECUTION.md`
- `scripts/codex_cat.py`, `scripts/check_codex_stale.py`, `tests/test_codex_cat.py`
- `.aider.chat.history.md`, `aider-ai`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_platform_gnosis_map ⬡ MINING-COMPLETE ⬡ 2026-08-18*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
