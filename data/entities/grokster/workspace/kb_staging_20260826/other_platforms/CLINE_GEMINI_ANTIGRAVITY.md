# Cline / Gemini CLI / Antigravity — Durable Expertise Extract

**KB Entry**: grokster/platforms/other/CLINE_GEMINI_ANTIGRAVITY
**last_verified**: 2026-08-26 · **rot_class**: medium (Cline active), fast (Gemini ref stale-flagged)
**Sources**: `.clinerules` (v7.2.0, Cline 3.0.52), `docs/briefings/CLINE_CLI_BRIEFING_20260815.md`, `docs/research/R_CLINE_CATCHUP_REVIEW_FOR_KALI_20260822.md`, `ACTIVE_SPRINT.json` D-557/D-563, `docs/research/GEMINI_CLI_QUICK_REF.md` (STALE-flagged), provider fabric docs

---

## Cline (secondary dev platform — ACTIVE)

**House posture (rulings)**:
- D-557: Cline + DeepSeek V4 Flash = 1M context → "primary surgical tool" for large-context passes.
- D-563: **1 active Cline instance max**; the 8-account pool exists for rate-limit resilience, NOT parallelism.
- Model pairing: DeepSeek V4 Flash (1M) + MiMo V2.5 (512K) via Cline CLI 3.0.52.

**Config surface**: `.clinerules` at repo root = HOW-to-work rules; OMEGA_ENGINE.md = WHAT the engine is. Entry point pattern: a briefing doc (`docs/briefings/CLINE_CLI_BRIEFING_*.md`) read first every session (~1% of 1M context), tiered document index Tier-1 SSOTs → Tier-4 deprecated.
**Durable practice**: Sovereign Proxy Identity framing — platform instructed to prioritize local files/mandates over training weights; local-first bias; Cloud-Drift violation concept; M23 hard-stop on tool outages written directly into .clinerules.
**Cross-platform handoff**: `docs/research/opencode_custom_handoff_to_cline.md`; Cline sessions produce full session-export markdown dumps (see `data/coordination/fle_study_20260825/`) — good forensic artifacts.
**Cline as auditor**: R_CLINE_CATCHUP_REVIEW_FOR_KALI_20260822 demonstrates the fresh-eyes independent-review pattern — Cline re-derived measured facts instead of trusting the manual, and found NEW criticals (B5 23MB tracked binary, B6 M1 enforced by whitelisting violator, B7 truthiness drift). Value: use Cline for adversarial cross-platform audits where OpenCode fleet has blind spots.

## Gemini CLI (dormant / stale)

Repo reference is STALE-flagged (pre-June 2026). Durable nuggets only:
- Config hierarchy: `/etc/gemini-cli/system-defaults.json` → `~/.gemini/settings.json` → `.gemini/settings.json` (+ overrides); project context via GEMINI.md/CONTEXT.md.
- Key settings: context.fileName, context.includeDirectories, model.maxSessionTurns, general.plan.enabled (read-only plan mode), general.checkpointing.enabled (session recovery).
- Flags: `--yolo`/`--approval-mode=yolo` (auto-approve all — dangerous), `--headless`.
- Memory flow: auto-distillation back into GEMINI.md.
**Verdict**: keep as shallow reference; no active mileage. Research targets: settings.json current schema, MCP support, quota model.

## Antigravity (cloud OAuth pool)

- Position: **primary cloud backend** in provider fabric ordering (priority 3, after local) per Ark §7; accessed from OpenCode via `opencode-antigravity-auth@latest` plugin (npm, in live plugin array).
- Durable pattern: OAuth-pool auth via OpenCode plugin rather than API keys; Antigravity Claude Sonnet 4.6 appears in provenance audits as an actual response generator.
- Not deep-mined: `docs/research/antigravity/` dir exists, unexamined this pass. Research target: pool rotation mechanics, rate-limit profile, session attribution.

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB-STAGING ⬡ 2026-08-26*
