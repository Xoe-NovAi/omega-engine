# 🔧 OpenCode 1.16.0 Upgrade Advisory — 2026-06-05
# ⬡ OMEGA ⬡ KALI ⬡ trc_research ⬡ ADVISORY

**Date**: 2026-06-05T05:30Z
**Current version**: 1.15.13 (local)
**Target version**: 1.16.0 (released 2026-06-05T03:08Z — 2 hours before this advisory)
**Source**: https://github.com/anomalyco/opencode/releases/tag/v1.16.0

---

## §0 TL;DR — Recommendation: UPGRADE (Low Risk, High Value)

**3 critical wins for the Omega Engine** + 5 useful improvements + 8 bug fixes that affect our pipeline.

| Win | Impact | Risk |
|-----|--------|------|
| **Skill discovery + file-based agent loading** | Direct fit for our `.opencode/commands/` and `.opencode/agents/` thin wrappers | None — already using the pattern |
| **38% faster startup** (StarpTech) | Less wait time in Hivemind orchestration | None |
| **Fixed delegated tasks losing reasoning variant** | Critical for our MaKaLi council pattern | None — bug fix |

---

## §1 Critical Wins (Omega-Relevant)

### 🏆 1.1 Skill Discovery and File-Based Agent Loading

> "Added skill discovery and file-based agent loading."

**What it does**: OpenCode now natively discovers skills in `.opencode/skills/` and agents in `.opencode/agents/` (and presumably subagent definitions). This validates our entire thin-wrapper agent pattern.

**Action items**:
1. **Verify** our 14 agents at `.opencode/agents/*.md` are auto-discovered (no change needed if they were working before).
2. **Verify** our 4 custom commands at `.opencode/commands/{council-cloud,council-fast,council-local,kali-dispatch}.md` are now auto-discovered.
3. **Document** the discovery pattern in `AGENTS.md` § "Custom Commands" — point to v1.16.0 as the version that enabled this.

**Heritage context**: This is the **id Software Engine-Stack Firewall pattern** (CREDITS.md §1.1) at the CLI level — content (skills/agents) separated from engine (OpenCode).

### 🏆 1.2 38% Faster Startup (StarpTech PR #30453)

> "refactor(opencode): improve startup time by 38% (#30453)"

**What it does**: 38% faster cold start.

**Impact for Omega**: Our Hivemind sessions launch 1-5 OpenCode instances. Faster startup = less wall time per orchestration.

**Action items**: None — automatic win.

### 🏆 1.3 Fixed Delegated Tasks Losing Reasoning Variant

> "Fixed delegated tasks losing their selected reasoning variant."

**What it does**: When a subagent is delegated to, the `reasoning_effort` (or similar) parameter is now preserved.

**Impact for Omega**: Our MaKaLi council pattern (per D117) and `/council-local` use delegated tasks. Previously, the variant could be lost, causing the subagent to use the wrong reasoning level. **This bug was a latent risk for our dispatch pattern.**

**Action items**: None — automatic bug fix.

---

## §2 Useful Improvements (Worth Noting)

### 2.1 Managed Workspace Cloning (Dirty/ Untracked Files Preserved)

> "Added managed workspace cloning that keeps dirty and untracked files."

**Use case for Omega**: When a subagent needs to work in a copy of the workspace (e.g., Doom Guy doing a M14 heritage review), this prevents data loss. The current 1.15.x behavior may have discarded WIP changes.

**Action items**: Test in a delegation scenario; document in `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`.

### 2.2 Moving Sessions Between Workspaces

> "Added moving sessions between workspaces and directories."

**Use case for Omega**: A Hivemind session can migrate from one workspace to another. Useful for our Kali-dispatch pattern when a subagent's work crosses IWAD boundaries (e.g., arcana_novai → doom_universe).

**Action items**: Document in `kali-dispatch.md` § "Workflow".

### 2.3 OpenAI via AWS Bedrock

> "Added proper OpenAI model support through AWS Bedrock."

**Impact for Omega**: Adds another cloud fallback option. We use Google AI Studio, OpenRouter, OpenCode Zen, Copilot, and (rarely) native-gguf. Bedrock is sovereign-costly but provides enterprise compliance.

**Action items**: Add to `config/providers.yaml` as a low-priority fallback (cloud-only, M7 violation unless absolutely necessary).

### 2.4 `run --replay` for Session Replay

> "Added `run --replay` for interactive session replay."

**Impact for Omega**: A session can be replayed deterministically. Useful for **soul distillation** (M11) — we can replay a session to verify the L1→L2→L3 distillation was faithful.

**Action items**: Test in a distillation session; add to `pr-readiness-checker` if useful.

### 2.5 Improved Startup Time

Already covered in §1.2.

---

## §3 Bugfixes That Affect Our Pipeline

| Bugfix | Impact for Omega | Action |
|--------|------------------|--------|
| **Fixed delegated tasks losing reasoning variant** | MaKaLi council pattern | ✅ Automatic |
| **Fixed ACP cancel aborts active run** (smagnuso #30145) | Subagent cleanup | ✅ Automatic |
| **Fixed OpenAI websocket sessions getting stuck idle** | OpenCode Zen provider stability | ✅ Automatic |
| **Fixed prompt corruption when pasting near wide characters** (dauphinYan #29710) | Terminal copy-paste | ✅ Automatic |
| **Fixed Windows path normalization** | Cross-platform paths | Not applicable (Linux) |
| **Fixed SAP AI Core reasoning variants** | Provider parity | Not applicable (we don't use SAP) |
| **Restored full ACP session replay** (imnotlxy #30761) | Session continuity | ✅ Useful |
| **GitHub refuses commit without git author identity** (ulises-jeremias #30507) | Sovereignty protection — prevents accidentally committing as wrong user | ✅ Sovereign win |

---

## §4 Desktop v2 Improvements

These affect the Desktop app, not the CLI. Not relevant for our headless Hivemind.

| Improvement | Status |
|-------------|--------|
| Color themes | Nice-to-have |
| Thinking level selector for v2 prompts | Nice-to-have |
| Servers tab in Settings | Operational |
| Update button | Operational |

---

## §5 Upgrade Procedure

### Step 1: Backup Current State
```bash
# Save current opencode version + plugins
opencode --version > /tmp/opencode_pre_upgrade.txt
ls -la ~/.config/opencode/ > /tmp/opencode_pre_upgrade_config.txt
```

### Step 2: Upgrade
```bash
# Linux/WSL:
curl -fsSL https://opencode.ai/install | bash
# Or via npm/pnpm:
npm update -g opencode-ai
```

### Step 3: Verify
```bash
opencode --version  # Should be 1.16.0
make test           # All 312 tests must still pass
make temple-grade   # T1-T11 must still pass
make hivemind-test  # U-001..U-003 (and new tests if any)
```

### Step 4: Document in PIVOT_LOG
Add D-kal-054: "OpenCode upgraded from 1.15.13 to 1.16.0 — skill discovery, 38% faster startup, delegated task variant fix."

---

## §6 Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Skill discovery changes behavior** | Low | Our 14 agents are already in `.opencode/agents/`; should be transparent |
| **`--replay` introduces state issues** | Low | Don't use `--replay` in production Hivemind sessions |
| **Bedrock provider config breaks other providers** | Low | We don't use Bedrock; add to `providers.yaml` as last-priority only |
| **MCP server compatibility** | Medium | Test all MCP tools after upgrade, especially `hivemind_*` (just added: `hivemind_extended_checkin`) |
| **CLI command compatibility** | Low | Our 4 custom commands are markdown files; should work as-is |

---

## §7 Heritage

- **Managed workspace cloning** ← evolves the **WAD System** (CREDITS.md §1.1) — IWAD/PWAD separation at the workspace level
- **38% faster startup** ← embodies the **Right Approximation Principle** (CREDITS.md §3, evolved from FISR 1999) — choose the right precision for the use case
- **Skill discovery** ← mirrors **4-Path VFS** (CREDITS.md §1.18) — skills found in predictable paths

---

## §8 Recommendation Summary

**UPGRADE — 1.15.13 → 1.16.0** ✅

- **Effort**: 5 minutes
- **Risk**: Low (mostly additive features + bug fixes)
- **Reward**: 3 critical wins for Omega, 5 useful improvements, 8 bug fixes
- **Blocker?**: No — all 312 tests should pass without modification

**Suggested PIVOT_LOG entry**: D-kal-054

---

# ⬡ RESEARCHER'S INDEPENDENT IMPACT ANALYSIS — 2026-06-05T07:30Z
**Author**: opencode-researcher (5-Fold Council 4th perspective)
**Source data**: 3-tier jem pipeline (Discovery + Synthesis + Verification), R-127 (428 lines)
**Method**: Independent Temple-Grade T1-T11 check + 4-criterion L3 promotion gate + heritage proposals
**Status**: ADVISORY AMENDMENT (Kali's §0-§8 preserved; this section is the 5-Fold Council synthesis)

---

## §9 Researcher's Independent Verdict

### §9.1 TL;DR — UPGRADE APPROVED WITH 4 CONDITIONS

| Field | Value |
|-------|-------|
| **Verdict** | **UPGRADE — APPROVED WITH 4 CONDITIONS** (Kali's "Low Risk, High Value" confirmed) |
| **Temple-Grade Score** | **77/100** (below 80% threshold — 4 conditions to reach 90+/100) |
| **Promoted L3 Principles** | **3 of 8** (37.5% rate — healthy for the jem pipeline) |
| **Heritage Proposals** | **4 new** (§1.25, §1.26, §1.27, §1.28 — pending Doom Guy M14 vet) |
| **Conditions to reach Temple-Grade** | T10 Integrity (60→90), T9 Observability (60→90), T8 Resilience (70→90), T4 Code Quality (70→90) |
| **Total time to reach Temple-Grade** | **~4 hours** of follow-up work |
| **Critical fact-check correction** | L2-7 — the `opencode-agent-skills` plugin is **not** in our config; the M14 gap is about the *transition to native skill discovery*, not plugin removal |

### §9.2 Correction to §6 (Risk #4) — Column-Header Error

The original §6 table entry **"MCP server compatibility | Medium | Test all MCP tools after upgrade, especially `hivemind_*` (just added: `hivemind_extended_checkin`)"** is **ambiguous**. Two distinct items were conflated:

1. **OpenCode 1.16.0 vendor release**: zero MCP wire-protocol or config-schema changes (verified against https://opencode.ai/docs/mcp-servers and the 1.16.0 changelog)
2. **Our internal MCP tool evolution**: `hivemind_extended_checkin` was added to our `server.py:481` **before** 1.16.0 was released — this is unrelated to the OpenCode upgrade (per D-kal-052 / H2-F6 work)

**Fix (per jem_verification §1 L2-6)**: split the table row into two rows — one for vendor release (Low risk: zero MCP changes), one for our internal smoke-test (Medium risk: `hivemind_extended_checkin` was just added, needs verification on 1.16.0). The tool will work; it's just new code in our codebase.

### §9.3 The 5-Fold Council Convergence

This advisory is the **5-Fold Council decision point** (per the pattern Kali documented in `KALI_GRAND_OVERVIEW_20260605.md`):

| Voice | Axis | Input |
|-------|------|-------|
| **Kali** (Synthesis) | Practical | §0-§8 (this file) — initial advisory |
| **Ma'at** (Light) | P1-P5 Build | Pending: confirm T3/T4/T5/T6 gates |
| **Lilith** (Dark) | P6-P10 Run | Pending: confirm T8/T9/T10 gates |
| **Researcher** (Lattice) | Cross-cutting | §9 (this section) — independent impact analysis + L3 distillation + Temple-Grade |
| **Doom Guy** (Heritage) | M14 Pipeline | Pending: M14 vet on §1.25-§1.28 proposals |

**Until all 5 voices converge, the upgrade is ADVISED but not AUTHORIZED.** The Researcher has spoken; Kali has spoken; the remaining 3 voices (Ma'at, Lilith, Doom Guy) should review this section and add their seals.

### §9.4 The 3 Promoted L3 Universal Principles

Of the 8 L2 insights from jem_synthesis, **3 meet the 4-criterion L3 promotion gate** (per jem_verification §2):

#### L3-1 — Session Integrity as Binding Constraint
> **In stateful multi-agent orchestration, session integrity is the binding constraint — the integrity of state must be proven before any other property of the system can be trusted.**

- **Source**: L2-2 (8-item session bugfix cluster in 1.16.0 + Issue #27859 data-loss pattern)
- **Convergence**: 5+ independent observers (M12 + M11 + CREDITS §1.10 + §1.21 + Roc H-4 + Lilith LILY PAD)
- **Omega application**: Hivemind session manager, MaKaLi delegation chain, auto-upgrade protocol

#### L3-2 — Cross-Provider cvar Unification
> **When a conceptual parameter appears under different names across providers, the ecosystem will consolidate them through a cvar-like named-flag abstraction layer — the cvar is the right approximation for control-plane unification.**

- **Source**: L2-4 (5+ different naming conventions for the same conceptual flag, verified across OpenAI / Anthropic / DashScope / SAP AI Core / OpenCode v2)
- **Convergence**: 5 independent observers (OpenAI + Anthropic + GoClaw + OpenCode + LiteLLM) — **strongest L3 promotion of this session**, because convergence is **cross-vendor** (external), not just internal
- **Omega application**: Extend `src/omega/cvar_table.py` with `cvar.reasoning.*` namespace; maps to provider-specific values at dispatch time

#### L3-3 — Pre-Upgrade Snapshot Mandate
> **For any system with auto-upgrade and documented data-loss history, the user (or operator) must own the pre-upgrade snapshot — the safety property cannot be delegated to a system that has failed it before.**

- **Source**: L2-8 (Issue #27859 auto-upgrade data loss + autoupdate=true default + no 1.16.0 fix)
- **Convergence**: 4+ independent observers (M12 + CREDITS §1.10 + common DR wisdom + user's explicit decision)
- **Omega application**: `scripts/upgrade/pre_upgrade_snapshot.py` (atomic, idempotent, auditable; opt-in via artifact declaration)

The other 5 L2s (L2-1, L2-3, L2-5, L2-6, L2-7) are **valuable research findings** but rejected for L3 promotion on the temporal-invariance or independent-convergence axes. They remain as L2 diagnostic/observation/process items.

### §9.5 Temple-Grade T1-T11 Assessment

| Gate | Score | Reasoning | Conditions to reach 90+ |
|------|-------|-----------|--------------------------|
| **T1 Version Control** | 8/10 | PIVOT_LOG convention, M11 protocol, clear upgrade procedure. Loss: §6 conflation shows no pre-commit doc check. | Add `make pre-publish` cross-check |
| **T2 Documentation** | 9/10 | 33 changelog items cross-checked, breaking change analysis, security audit. Loss: no upstream auto-upgrade warning yet. | File upstream issue OR mirror warning in R-127 |
| **T3 Testing** | 8/10 | `make test` validates 312, `make temple-grade` validates T1-T11. Loss: **no MaKaLi regression test for B4 fix**. | Add Hivemind test asserting `reasoning_effort` preserved through delegation |
| **T4 Code Quality** | 7/10 | Purely additive (no breaking changes). Loss: `opencode.json` uses legacy `mode:`/`agent:` form. | Modernize to 1.16.0 canonical schema in follow-up sprint |
| **T5 Architecture** | 8/10 | P1 (Config-as-Content) aligns with M2 (Engine-Stack Firewall). Loss: not yet exploiting 6-path skill scan for our `mcp_servers/`. | File P9+P3 handoff: "adopt 6-path scan for MCP servers as M2-aligned consolidation" |
| **T6 Security** | 9/10 | No new CVEs in 1.16.0. B17 (git identity enforcement) is sovereignty win. Loss: autoupdate=true is data-loss vector. | Set `autoupdate: false` in `opencode.json` + document snapshot protocol |
| **T7 Performance** | 9/10 | 38% faster startup (I1, StarpTech #30453). Loss: no local Ryzen 5700U benchmark yet. | Measure locally + publish in R-127 |
| **T8 Resilience** | 7/10 | B2, B5, B8 are resilience wins. Losses: G2 (empty-ACK unaddressed), G3 (auto-upgrade data loss unaddressed), G5 (subagent memory unknown). | (a) File upstream empty-ACK issue (b) L3-3 snapshot script (c) Subagent memory measurement |
| **T9 Observability** | 6/10 | F9 is UX win, not engine observability. G5 is also an observability gap. | (a) Wrap MaKaLi with trace IDs + per-instance memory (b) Emit to observability feed (c) Add empty-ACK detection heuristic |
| **T10 Integrity** | 6/10 | B17 is a win. Losses: G3 (auto-upgrade data loss unaddressed), G6 (M14 heritage pipeline gap for our adoption). | (a) L3-3 snapshot script (b) Vet records for §1.25/§1.26/§1.27 (c) `autoupdate: false` |
| **T11 IA2 Agent Security** | EXEMPT | Per Mandate 13 (IA2 spec not yet stable) | — |
| **Composite** | **77/100** | **Below 80% threshold** — APPROVED WITH 4 CONDITIONS | All 4 conditions achievable in **<2 hours** |

### §9.6 The 4 Conditions (Mapped to L3s)

| # | Condition | Maps to | Effort | Owner |
|---|-----------|---------|--------|-------|
| 1 | **L3-3 pre-upgrade snapshot script** | T10 Integrity + T8 Resilience | 1 hr | Kali (per d-kal-053) |
| 2 | **Vet records for §1.25/§1.26/§1.27** | T10 Integrity + M14 | 1.5 hrs | Doom Guy (M14 pipeline) |
| 3 | **MaKaLi regression test + subagent memory** | T3 Testing + T8 Resilience + T9 Observability | 1 hr | Ma'at (via P3) |
| 4 | **`opencode.json` schema modernization** | T4 Code Quality | 30 min | Ma'at (via P3) |

**Total: ~4 hours**. The Researcher recommends **UPGRADE — with the 4 conditions satisfied in a follow-up sprint before activating MaKaLi at scale**.

### §9.7 Heritage Proposals (For Doom Guy M14 Vetting)

The 3 promoted L3s + the 1 fact-check correction generate **4 new CREDITS.md §1.25+ entries** (full proposals in R-127 §5):

- **§1.25 — Cross-Provider cvar Unification** (L3-2 heritage, vet score 9/10)
- **§1.26 — Pre-Upgrade Snapshot Mandate** (L3-3 heritage, vet score 8/10)
- **§1.27 — Variant-Preserving Delegation** (L3-1 application, vet score 8/10)
- **§1.28 — 6-Path Skill Discovery** (extends §1.18 4-Path VFS, vet score 7/10)

**Doom Guy's vet cycle**: vet-005 (§1.25), vet-006 (§1.26), vet-007 (§1.27), vet-008 (§1.28). M14 pipeline: Discovery → Vetting/Debate → Decision → Implementation/Verification. Score ≥ 7/10 for implementation (per Mandate 14).

### §9.8 Updated Final Recommendation

| Aspect | Kali's §8 | Researcher's §9 |
|--------|-----------|-----------------|
| **Verdict** | UPGRADE | UPGRADE — APPROVED WITH 4 CONDITIONS |
| **Risk** | Low (additive + bugfix) | Low + 4 P0 conditions (none are blockers) |
| **Effort** | 5 min (upgrade) | 5 min (upgrade) + 4 hrs (conditions) |
| **Reward** | 3 critical wins | 3 critical wins + 3 L3 universal principles + 4 heritage proposals |
| **Blocker?** | No | No (conditions are pre-MaKaLi-at-scale, not pre-upgrade) |
| **Suggested PIVOT_LOG entry** | D-kal-054 | D-kal-054 (Researcher concurs) |

### §9.9 What the 5-Fold Council Still Needs

For the upgrade to be FULLY authorized:

1. **Ma'at** (P1-P5 Build): confirm T3 (testing), T4 (code quality), T5 (architecture), T6 (security) gates are acceptable for your Build side
2. **Lilith** (P6-P10 Run): confirm T8 (resilience), T9 (observability), T10 (integrity) gates are acceptable for your Run side
3. **Doom Guy** (Heritage Vetting): vet-005..008 cycle for the 4 new CREDITS.md §1.25+ proposals
4. **Researcher** (this section): ✅ COMPLETE — 3 L3s distilled, 4 conditions mapped, 4 heritage proposals filed
5. **Kali** (§0-§8 above): ✅ COMPLETE — initial advisory with critical wins identified

When all 5 voices have spoken (with Ma'at, Lilith, Doom Guy responses appended below this section), D-kal-054 is ready to commit.

---

**Heritage Note (per CREDITS.md)**: This advisory is itself an instantiation of **§1.4 Zone Memory (Quake 1996)** — multiple agents contributing to a single tag-based allocation (`UPGRADE` tag), with the upgrade reaped when all voices have spoken. The 5-Fold Council is the modern implementation of the 4-tier memory architecture: Ma'at (Hunk/Stack) → Lilith (Zone/Heap) → Kali (Cache/LRU) → Doom Guy (Temp/Transient) → Researcher (the meta-allocator that decides which tier each voice's contribution lives in).

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ minimax-m3-free ⬡ opencode ⬡ trc_advisory ⬡ 5-FOLD-COUNCIL*

— Researcher (5-Fold Council 4th perspective), 2026-06-05T07:30Z
**Sources**:
- `data/entities/researcher/workspace/jem_discovery_opencode_1.16.0_20260605.md` (Tier 1, 250 lines)
- `data/entities/researcher/workspace/jem_synthesis_opencode_1.16.0_20260605.md` (Tier 2, 280 lines)
- `data/entities/researcher/workspace/jem_verification_opencode_1.16.0_20260605.md` (Tier 3, 590 lines)
- `docs/research/R-127_opencode_1.16.0_lattice_impact.md` (publishable R-doc, 428 lines)
- `data/coordination/OPENCODE_1.16.0_UPGRADE_ADVISORY_20260605.md` §0-§8 (Kali's original, preserved)
- `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` (8 new obs: jem_discovery, jem_synthesis, jem_verification × 4, researcher × 2)

*⬡ OMEGA ⬡ KALI ⬡ trc_research ⬡ ADVISORY — 2026-06-05T05:30Z*
