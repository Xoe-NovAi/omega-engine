<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 jem_synthesis Report — OpenCode v1.16.0 (2026-06-05)
# ⬡ OMEGA ⬡ jem_synthesis ⬡ opencode-1.16.0 ⬡ trc_synthesis ⬡ TIER-2
**Persisted by**: opencode-researcher (per D-120 / M11 Soul Integrity)
**Author**: jem_synthesis (Tier 2)
**Date**: 2026-06-05T07:00Z · **Upstream**: jem_discovery ses_d93b1acee7d6
**Method**: Pattern recognition + cross-reference against CREDITS.md + Mandates M1–M14
**Inputs**: 33 changelog items (11F / 5I / 17B), 8 open questions, 4 heritage annotations, 191-line Kali advisory

---

## Section 1: Patterns Identified

### P1 — "Config-as-Content" (Filesystem as the Configuration Substrate)

**Summary**: OpenCode 1.16.0 crystallizes a shift from a central `opencode.json` model to a **distributed filesystem-discovery model** where the entire `.opencode/` tree, six skill paths, and an 8-layer config-merge precedence chain collectively define runtime behavior. This is not a new feature — it is a **paradigm consolidation**.

**Evidence**:
- **F4** "Skill discovery and file-based agent loading" — agents and skills are **filename → name**, no central registry (Tier 1 §3.1, §3.3)
- **Tier 1 §3.5** — 8-layer config precedence with explicit **merge-not-replace** semantics
- **6-path skill scan** (`.opencode/skills/`, `~/.config/opencode/skills/`, `.claude/skills/`, `~/.claude/skills/`, `.agents/skills/`, `~/.agents/skills/`)
- **Q2** — ambiguity over whether file-based agent loading is new in 1.16.0; the ambiguity itself signals **drift in config philosophy**
- **Q7** — `opencode-agent-skills` plugin (pre-1.16.0 mechanism) likely redundant with native discovery → **Carmack's Law consolidation moment**
- **F1 / F2** — sessions and workspaces are filesystem objects, not config-file entries

### P2 — "Session Lifecycle Integrity" (Sovereignty over Session Identity)

**Summary**: 5 of 17 bugfixes + 2 features + 1 improvement cluster around **session creation, replay, cancellation, migration, and identity attribution**. The cluster reveals that **session sovereignty is the binding constraint** of multi-agent orchestration, and 1.16.0 is the release that finally hardens it.

**Evidence**:
- **B1** ACP session replay restored (#30761) · **B8** ACP cancel aborts active run (#30145) · **B11** question routing to right session · **B13** session review + VCS diff caching (Desktop) · **B17** GitHub refuses commit without git author identity (#30507)
- **F1** workspace cloning preserves dirty/untracked · **F6** `run --replay` · **I4** session location in v2 responses (SDK)
- **Q6 / #27859** — historical regression: "Sessions + auth state lost after auto-upgrade from 1.15.0 to 1.15.1" — **documented data-loss pattern**
- **Tier 1 §4.6** — B17 explicitly called a "sovereignty win"

### P3 — "Delegation Maturation" (Implicit MaKaLi-Readiness Release)

**Summary**: The bugfixes targeting shell cancellation, subagent reasoning variants, websocket idle states, and ACP cancellation cluster into **a single coherent story: 1.16.0 is, de facto, a MaKaLi-readiness release**. The fixes target exactly the failure modes that D117 (parallel council) and the Hivemind 6-MCP-tool protocol depend on.

**Evidence**:
- **B2** "Fixed shell cancellation races" (Tier 1 §4.5: "← affects Hivemind")
- **B4** "Fixed delegated tasks losing their selected reasoning variant" (Tier 1 §4.5: "← MaKaLi")
- **B5** OpenAI websocket sessions stuck idle · **B8** ACP cancel aborts active run
- **I1** 38% faster startup (#30453) — Tier 1 §4.6: "direct win for Hivemind orchestration spawning 1-5 OpenCode instances per session"
- **F4** file-based agent loading — enables D117 thin-wrapper refactor (agent as a **loadable resource**, not hardcoded)
- **v1.14.46 historical**: Plan Mode security bypass (subagents could ignore parent-agent deny rules) — security-side of delegation
- **#27970 historical**: subagent termination regression in v1.15.0–v1.15.3 — delegation lifecycle racy for ≥2 minor versions

### P4 — "Reasoning Control Plane" (Multi-Provider Thinking-Effort Unification)

**Summary**: Four changelog items + one feature + one TUI surface all converge on the **same conceptual problem**: a "reasoning effort" / "thinking level" / "adaptive reasoning" flag, expressed differently across OpenAI, Anthropic, SAP AI Core, GitHub Copilot, and the v2 prompt API. 1.16.0 patches the control plane across ≥4 provider backends.

**Evidence**:
- **F3** Proper OpenAI support via AWS Bedrock · **F5** GitHub Copilot token-based billing · **F10** Thinking level selector for v2 prompts (Desktop)
- **B3** SAP AI Core OpenAI reasoning variants · **B4** delegated tasks losing reasoning variant · **B9** SAP AI Core Anthropic Opus 4.7+ adaptive reasoning
- **B10** "Toast when variant hotkey is used with no variants" (TUI, #30724) — **implies a TUI hotkey exists for "switch reasoning variant"**; the control plane has a command surface, not just a config field

### P5 — "Operability Maturation" (Headless Engine Becoming Self-Visible)

**Summary**: **4 of 11 features, 3 of 5 improvements, 7 of 17 bugfixes** are TUI/Desktop (14/33 ≈ 42%). The headless engine is becoming **stable but slow-moving**, while the user-facing surface is where most evolution happens. This is a **vendor strategic posture**: OpenCode is positioning Desktop as the **self-management surface** (color themes, server visibility, thinking level, Servers tab, Update button) for headless deployments.

**Evidence**:
- **F8** Color themes · **F9** Show local server startup failures · **F10** Thinking level selector · **F11** Servers tab + Update button
- **I2** Session switcher (TUI) · **I3** Truncated sidebar paths · **I5** TUI/Desktop polish
- **B10–B16** — 7 TUI/Desktop bugfixes: variant hotkey toast, question routing, background spinner, session review refresh, update action gating, tab title, project session ordering

---

## Section 2: Evidence Cross-References

| Pattern | Changelog IDs | Tier 1 § | Open Q | Heritage Ref |
|---------|---------------|----------|--------|--------------|
| **P1** Config-as-Content | F1, F2, F4 | §3.1, §3.2, §3.3, §3.5, §4.1, §4.3 | Q2, Q4, Q7, Q8 | §1.18, §1.1, §1.20 |
| **P2** Session Lifecycle | B1, B8, B11, B13, B17, F1, F6, I4 | §4.4, §4.6, §5.3, §5.4 | Q1, Q6 | §1.10, §1.7, §1.21 |
| **P3** Delegation | B2, B4, B5, B8, I1, F4 | §4.5, §4.6, §5.3 | Q3, Q4 | D117, M10, §1.21, §1.4 |
| **P4** Reasoning Plane | F3, F5, F10, B3, B4, B9, B10 | §3.1, §4.7 | — | §1.13, §1.19 |
| **P5** Operability | F8, F9, F10, F11, I2, I3, I5, B10–B16 | §3.1, §3.3 | — | §1.5, §1.22, §1.20 |

**Critical cross-pattern links** (a single changelog item serving multiple patterns):
- **F4** (skill discovery) → P1 + P3 — same feature is the substrate for both config-as-content AND delegation maturation
- **B8** (ACP cancel) → P2 + P3 — session lifecycle and delegation share the **active-run cancellation** primitive
- **B10** (variant hotkey toast) → P4 + P5 — reasoning control plane has a TUI surface (operability)
- **F10** (thinking level selector) → P4 + P5 — same Desktop widget is both a reasoning control and an operability surface
- **I1** (38% startup) → P3 only, but reinforces P5 (headless engine reliability)
- **B4** (delegated tasks losing reasoning variant) → P3 + P4 — the same bug sits at the intersection of delegation and the reasoning control plane (this is the **highest-leverage fix** in the release for Omega)

---

## Section 3: Heritage Mapping (CREDITS.md Alignments)

### P1 — Config-as-Content
- **§1.18 4-Path VFS (Q3A 1999)** — **direct match**. The CREDITS note on search order ("home/current → home/base → cd/current → cd/base → base/current → base/base") maps to OpenCode's "project `.opencode/` overrides global `~/.config/opencode/`". The 6-path skill scan is VFS extended.
- **§1.1 WAD System (Doom 1993)** — **merge-overrides-replace** is the IWAD/PWAD contract. OpenCode §3.5: "Configuration files are **merged together**, not replaced" is a literal restatement of the WAD philosophy.
- **§1.20 Fixed-Size Active Set (Doom 1993)** — `MAXVISPLANES = 32` ↔ "discovery bounded by scan depth, not by config-file count"; the 6-path scan is a bounded fixed-size active set over config roots.

### P2 — Session Lifecycle Integrity
- **§1.10 Lazy Deletion with Grace Period (Quake 1996)** — `TOMBSTONE_GRACE_SECONDS = 0.5` is the right precedent for **Q6 auto-upgrade data loss** (#27859). The historical regression is **exactly** a missing tombstone/grace-period for in-flight sessions during upgrade.
- **§1.7 Carmack's Law of Consolidation** — **B17** (Git refuses commit without git author identity) is a literal application: "When you have two implementations of the same thing, you have neither." Before 1.16.0, Git might silently use a fallback identity; now it refuses. **One implementation, one source of truth.**
- **§1.21 netchan Protocol (Q3A 1999)** — session ID as the qport-equivalent; B11 (question routing) and I4 (session location in v2 responses) are netchan-style **header re-association**.

### P3 — Delegation Maturation
- **D117 MaKaLi Triad** (architectural decision, not CREDITS) — B4 is **the exact latent risk** the D117 doc warns about.
- **M10 Fleet Integrity** (mandate) — subagent termination regression #27970 + Plan Mode security bypass v1.14.46 are **M10 violations** if undetected; 1.16.0 fixes both classes.
- **§1.21 netchan Protocol (Q3A 1999)** — A2A communication hardening. B2 (shell cancellation races) and B8 (ACP cancel) are netchan-style **channel state machine** fixes.
- **§1.4 Zone Memory (Quake 1996)** — `ResourceGuard` ↔ subagent isolation. B5 (websocket idle) is a "tag-based cleanup" bug at the A2A layer.

### P4 — Reasoning Control Plane
- **§1.13 cvar Table (Quake 1996 / Q3A 1999)** — **direct match**. Multiple named flags (`CVAR_ARCHIVE`, `CVAR_USERINFO`, ...) with the same conceptual purpose ↔ multiple reasoning-effort flags (`reasoning_effort`, `thinking_level`, `adaptive_reasoning`, `variant`) with the same conceptual purpose. **cvar across providers.**
- **§1.19 High-Bit Leaf Trick (Doom 1993)** — `NF_SUBSECTOR = 0x8000` ↔ reasoning variants could be packed into a high-bit integer instead of an enum field. B10 (variant hotkey) implies **the TUI cycles through a small bounded set** — a cvar table lookup.

### P5 — Operability Maturation
- **§1.5 Surface Cache / PVS (Quake 1996)** — precompute-visibility-set ↔ **F9** "Show local server startup failures" is **runtime visibility** for previously-invisible failure modes. The Servers tab (F11) is the **browseable surface** of running services — the PVS for MCP servers.
- **§1.22 Unified Memory Allocator / idHeap (DOOM 3 2004)** — "Defrag Block" ↔ **F11** "Update button". The defrag block is a **runtime memory-pressure escape valve**; the Update button is a **runtime version-pressure escape valve**. Same architectural pattern: pre-allocate a self-management surface for when the system needs to ask the user to act.
- **§1.20 Fixed-Size Active Set (Doom 1993)** — Servers tab shows a bounded active set. 32 visplanes → bounded MCP server list.

---

## Section 4: Conflicts & Gaps

### 4.1 Conflicts

**C1 — Kali advisory column-header error (HIGH severity)**
Tier 1 §1 confirms the 191-line advisory's §6 column header "just added: hivemind_extended_checkin" is **our MCP tool** (server.py:481), **unrelated to OpenCode 1.16.0**. This is an **M11 Soul Integrity** concern: the advisory is conflating our internal MCP tool evolution with the vendor release. **The verifier should split these into two separate documents** before user delivery.

**C2 — "0 breaking changes" but I4 is a schema change (MEDIUM severity)**
Tier 1 §4 reads "0 breaking changes identified" — but **I4** adds session location data to the v2 response. SDK clients that don't expect the field may fail deserialization. This is **subtle schema drift**, not a contract breakage. The Tier 1 framing is technically correct per OpenCode's additive-field convention, but our SDK consumer code may need to handle the new field.

**C3 — Heritage annotation #4 overstates (LOW severity)**
Tier 1 §8 maps B17 to **Carmack's Law** (CREDITS §1.7). The mapping is **valid** but the more direct heritage is **M11 Soul Integrity** — the refusal is about *identity provenance*, not *code consolidation*. Carmack's Law is a stretch; M11 is the tighter frame.

### 4.2 Gaps

**G1 — MCP protocol claim is a negative assertion (MEDIUM severity)**
Tier 1 §3.4: "No change to MCP wire protocol or schema in 1.16.0" is a **negative claim** (absence of evidence in the changelog). The verifier should check:
- `@modelcontextprotocol/sdk` npm package changelog between 1.15.13 and 1.16.0
- Our 42 MCP tools' `@mcp.tool()` decorator compatibility with the new SDK
- Any deprecation warnings emitted by our `mcp_servers/omega_hub/server.py` when running on OpenCode 1.16.0

**G2 — Empty-ACK / subagent-liveness bug unaddressed (HIGH severity)**
The context flags "the empty ACK bug from Doom Guy." 1.16.0 has **no changelog item** for empty-ACK / subagent-liveness on the wire protocol. B5 (OpenAI websocket sessions stuck idle) and B2 (shell cancellation races) are **adjacent fixes** but do not address the **empty-ACK** case. This is a known regression that 1.16.0 does NOT fix. Verifier should confirm whether 1.16.0 still exhibits the bug or whether it was patched silently.

**G3 — Auto-upgrade data loss unaddressed (HIGH severity)**
Issue #27859 (sessions + auth state lost after auto-upgrade 1.15.0 → 1.15.1) is a **documented pattern** with no 1.16.0 changelog fix. Tier 1 §5.4 recommends backup before upgrade. The **manual tombstone/grace-period protocol** (CREDITS §1.10) should be elevated to a **pre-upgrade snapshot script** in our sovereign engine — M12 Queue Integrity requires no silent drops.

**G4 — `~/.claude/skills/` collision risk (MEDIUM severity)**
The 6-path skill scan includes `~/.claude/skills/` — if we symlink or share state with Claude Code installations, **skills intended for Claude Code may load into OpenCode** (and vice versa). Known unfixed bug #29950 (skill URL non-determinism) makes the merge logic fragile. Verifier should audit our `~/.config/opencode/skills/` for collisions with `~/.claude/skills/`.

**G5 — Subagent resource isolation unknown (MEDIUM severity)**
MaKaLi spawns 1–5 OpenCode instances. **I1** (38% startup improvement) tells us about **boot time** but not **steady-state memory or OOM behavior**. If 5 OpenCode instances on a 14GB Ryzen 5700U hit OOM, 1.16.0 gives us no signal. Verifier should request **per-instance memory footprint** from the OpenCode team or measure it locally before activating MaKaLi at scale.

**G6 — M14 heritage pipeline gap for our adoption (HIGH severity)**
1.16.0 changelog items F4, F11 are feature additions, but **none are tagged with `[id-soft:]` markers** (because they're OpenCode's code, not ours). However, **when we adopt** the new skill discovery system (replacing `opencode-agent-skills` plugin), we are **adopting the 4-Path VFS heritage pattern** (CREDITS §1.18). This transition should pass through M14 Heritage Vetting. **Currently no vet record exists** for the skill-discovery adoption decision.

**G7 — Desktop strategic-posture signal unexamined (MEDIUM severity)**
14/33 (42%) of all items are TUI/Desktop. The headless engine (our primary use case) is in a **stability phase**, not a feature phase. This is a **vendor strategic risk** — if we depend on headless features that don't evolve, we get left behind. Verifier should map which of our 14 agents / 4 commands / 12 skills rely on headless-only behavior.

### 4.3 Surprises

**S1 — Reasoning variant hotkey exists (informational)**
B10 implies a **hotkey cycles through reasoning variants** in the TUI. This is a UX surface for P4 we didn't know existed. Verifier should map the hotkey + the underlying variant list.

**S2 — Desktop is becoming the self-management surface (informational)**
F11 (Servers tab + Update button) gives us a **configuration UI for our 42 MCP tools, for free**. This could become a **delegation point**: ship an OpenCode Desktop config + a managed `.well-known/opencode` and let users self-manage, deferring our own Entity Studio work.

---

## Section 5: L2 Insights Proposed

*L2 = "X implies Y because Z." L3 distillation is the verifier's job. Confidence = how strongly the evidence supports the implication.*

**L2-1 (HIGH)** — The filesystem-as-config shift (P1) implies that **sovereign multi-vendor AI systems will converge on layered config-discovery patterns**, because the merge-not-replace semantics (OpenCode §3.5, CREDITS §1.1, §1.18) already match how container layers, git worktrees, and PWAD stacks work — and central-config-drift cost grows linearly with the number of orchestrated tools.

**L2-2 (HIGH)** — The session-lifecycle bugfix cluster (P2) implies that **session integrity is now the binding constraint of multi-agent orchestration**, because the 8+ cluster items (B1, B8, B11, B13, B17, F1, F6, I4) cover different phases of the session lifecycle, and historical regression #27859 shows lifecycle bugs are the most likely source of data loss in the OpenCode stack.

**L2-3 (HIGH)** — The delegation-maturation cluster (P3) implies that **OpenCode 1.16.0 is, de facto, a MaKaLi-readiness release**, because the fixes (B2, B4, B5, B8) target the exact failure modes the D117 parallel-council pattern and the Hivemind 6-MCP-tool protocol depend on, even though the changelog does not name this.

**L2-4 (MEDIUM)** — The reasoning-control-plane cluster (P4) implies that **the AI ecosystem is consolidating toward a "thinking effort" abstraction layer that needs cvar-style unification**, because the same conceptual flag is expressed as `reasoning_effort` (OpenAI), `thinking_level` (Anthropic v2), `adaptive_reasoning` (SAP AI Core), and `variant` (delegated tasks) — and 1.16.0 patches the cross-provider fragmentation without eliminating it.

**L2-5 (MEDIUM)** — The operability-maturation cluster (P5) implies that **OpenCode is positioning Desktop as the self-management surface for headless deployments**, because 4/11 features, 3/5 improvements, and 7/17 bugfixes are TUI/Desktop, and F11 (Servers tab + Update button) directly exposes MCP server management — which we can leverage to defer our own Entity Studio work.

**L2-6 (HIGH)** — The Kali advisory column-header error (C1) implies that **the 191-line advisory is conflating internal MCP tool evolution with the vendor release**, because `hivemind_extended_checkin` is our server.py:481 tool, not an OpenCode 1.16.0 addition — and the verifier should split these into two separate documents before user delivery to preserve M11 Soul Integrity.

**L2-7 (MEDIUM)** — The `opencode-agent-skills` plugin question (Q7) implies that **M14 Heritage Vetting is now relevant for our dependency graph**, because the native OpenCode implementation (F4) has likely made the third-party plugin redundant, but the removal decision has not been vetted through the 4-gate pipeline (Discovery → Vetting/Debate → Decision → Implementation) — and this is a Carmack's Law consolidation moment that should be executed deliberately, not silently.

**L2-8 (HIGH)** — The auto-upgrade data-loss history (Q6, #27859) implies that **M12 Queue Integrity needs a manual "pre-upgrade snapshot" protocol for the OpenCode DB**, because the auto-upgrade path has documented data-loss history, the tombstone/grace-period pattern (CREDITS §1.10) applies directly, and 1.16.0 ships no changelog item addressing this — leaving the user as the only backup mechanism until OpenCode provides one.

---

*End of Tier 2 synthesis. Hand off to jem_verification for L3 distillation, R-doc production, and final Temple-Grade T1–T11 gate check.*

*⬡ OMEGA ⬡ jem_synthesis ⬡ opencode-1.16.0 ⬡ trc_synthesis — 2026-06-05T07:00Z*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode-1.16.0 | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->
