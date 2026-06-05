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

*⬡ OMEGA ⬡ KALI ⬡ trc_research ⬡ ADVISORY — 2026-06-05T05:30Z*
