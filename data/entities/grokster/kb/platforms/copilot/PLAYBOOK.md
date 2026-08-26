# GitHub Copilot — Canonical Operating Playbook (Omega Engine House Practices)

**KB Entry**: grokster/platforms/copilot/PLAYBOOK
**last_verified**: 2026-08-26 · **rot_class**: medium (doctrine stable; pricing/promo dates fast)
**Scope**: House operating doctrine for GitHub Copilot as provider + platform. Companion docs: ARCHITECTURE.md (wire-level), CONFIG_REFERENCE.md (config), GOTCHAS.md (traps), RESEARCH_TARGETS.md (open probes). Deep-mine evidence: `docs/research/R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md`.
**Sources**: R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md; github.blog changelog 2026-01-16 + 2026-06-01; github/copilot-cli issues #2591/#2881/#2969/#4308; docs.github.com billing references.

---

## §1 Sanctioned-Builtin-First Doctrine (NON-NEGOTIABLE)

- **Default path is the OpenCode builtin provider** (`github-copilot`), authenticated via official `/connect` device flow. GitHub **formally supports OpenCode as a Copilot surface** since changelog 2026-01-16 ("no additional AI license needed") — this path carries zero ToS ambiguity.
- **Raw internal-API impersonation is FORBIDDEN when ≤2 accounts are needed.** The builtin slots cover it; impersonating VS Code identity headers to reach undocumented endpoints buys nothing and adds ban-risk surface.
- **Community proxies (messense/copilot-api-proxy, whtsky/copilot2api, IT-BAER variant) are RESERVED for N>2 account fan-out** — the only pattern that escapes OpenCode's 2-slot isolation limit. Each proxy instance = one account credential = one localhost port = one custom OpenAI-compatible provider in OpenCode config.
- If proxy fan-out is ever activated: prefer implementations exposing **Copilot SDK semantics** over raw `/copilot_internal` impersonation where feasible; keep request volume low; never parallel-fanout in patterns that look abusive. No confirmed mass-ban incidents exist as of 2026-08-26 [UNVERIFIED absence-of-enforcement].

## §2 Plan-Type Requirements

- **Auto-only plans are dead ends** (anomalyco/opencode #34644): Copilot Free / Student expose models through auto model selection only — no explicit model picking via API. Any account intended for house use MUST be a paid plan (Pro minimum) or Pro+/Max for premium SKUs.
- Plan economics (post-Jun-1-2026 AI-Credits): Pro $10 → $15 credit value/mo; Pro+ $39 → $70; Max $100 → $200; Business/Enterprise pooled per-user 1,900/3,900 (promo pools thru Sep 1 2026). 1 credit = $0.01. No carryover; reset 00:00 UTC on calendar day 1.
- Flex allotment is explicitly variable — never model it as permanent income.

## §3 Burn-Control Hierarchy (ordered by leverage)

1. **Model choice** — GPT-5.4 nano ($0.20/$1.25) vs Opus 4.8 ($5/$25) is a ~20× input swing. Default cheap; escalate deliberately.
2. **Prompt caching** — cached input ≈10× cheaper than fresh (>93% cache-hit achievable per Microsoft). Preserve context-prefix stability across turns; avoid needless prompt reshuffling.
3. **Harness choice** — agentic loops run through **OpenCode's harness ONLY, NEVER Copilot CLI**. Documented CLI incidents: single user prompt → 87 billed requests (#2591); autopilot loops wiping weekly quotas overnight (#1540/#2881/#2969); post-task background consumption (#4308). OpenCode's context handling avoids re-sending growing tool-def/context payloads every turn.
4. **Session limits** — when Copilot CLI use is unavoidable (parity probes only): `--max-ai-credits=N`, soft cap, set ≥30 (most single model calls cost >20 credits); limit does NOT survive session resume — re-set it.

## §4 Multi-Account Posture

- House holds ~8 GitHub accounts; OpenCode exposes exactly **2 builtin isolation slots**: `github-copilot` + `github-copilot-enterprise`.
- Slot 1 = primary individual account (official flow). Slot 2 = enterprise slot — **likely accepts a plain github.com individual token** (pi implementation falls back to `api.individual.githubcopilot.com` without a domain) — UNVERIFIED until probe L4-a completes. Do not build dependencies on slot 2 before L4-a.
- N>2 accounts → proxy-per-account fan-out (§1), gated on an explicit Architect trade-off decision (ban-risk acceptance).
- Plan health-check: decode exchanged token's `sku=` field programmatically — no UI scraping needed.

## §5 What This Platform Is NOT Used For

- NOT a local-first component (M7 ordering: Copilot is priority-6 cloud backend — safety net, never crutch).
- NOT a replacement harness (Copilot CLI is reference/probe material only).
- NOT free capacity: every chat/agent/CLI turn is token-metered micro-billing. Completions/next-edit remain unmetered but irrelevant to house usage.

---
*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
