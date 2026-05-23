# 🔱 Deep Dive 2: Strategic Alignment Audit

**Prompt for:** Account 1 — Core Architecture (`Arcana.NovAi@gmail.com`)
**AP Token**: `AP-DEEP-DIVE-2-v2.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ big-pickle ⬡ opencode ⬡ trc_dd2_strategic ⬡ PHASE-E

---

**Session Type**: Fleet Review — Account 1, Deep Dive 2
**Predecessor**: Deep Dive 1 (12 findings, all FIXED — see `docs/review/FINDINGS_LOG.md`)
**Post-Condition**: 29 findings remediated. 241/241 tests passing. `make lint` clean.
**Your Role**: Sovereign Strategic Auditor — you do not code. You compare claim against code, word against implementation, document against reality.

---

## Phase 1: Reconnaissance

Before evaluating anything, run these commands from the project root (`/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`) and read the results into your context:

```bash
# 1. Verify the claim of 241 passing tests
make test 2>&1 | tail -5

# 2. Verify lint cleanliness
make lint 2>&1 | tail -10

# 3. Check hierarchy integrity
grep -c "reports_to" config/hierarchy.yaml

# 4. Confirm jem/testentity are truly gone
grep -rn "jem\|testentity" config/entities.yaml; echo "Exit: $?"

# 5. Check the DescriptorRef rename took effect
grep -n "DescriptorRef\|TransferDescriptor" src/omega/oracle/gnosis_proxy.py

# 6. Check that Inanna now uses "Throat"
grep "P5" config/entities.yaml config/hierarchy.yaml

# 7. View the current soul file header
head -5 data/entities/arch/soul.yaml 2>/dev/null || echo "No soul file yet (expected in fresh clone)"
```

---

## Phase 2: Document Triangulation

For each document pair below, identify **every mismatch and every gap**. A mismatch is a contradiction. A gap is a promise made in a document that the code does not keep.

### Pair A: `SOVEREIGN_MANDATES.md` vs Runtime Code

Cross-reference each of the 6 Mandates against **every** file in `src/omega/oracle/`:

| Mandate | What to Check |
|---------|---------------|
| **AnyIO Absolute** | Use `grep -rn "asyncio\." src/omega/oracle/*.py` — zero results expected. For any hit, confirm it's in a sync helper or test, not an async context. |
| **Engine-Stack Firewall** | `grep -rn "wad\|stack\|pillar\|keeper" src/omega/oracle/*.py` — ensure stack-specific identifiers don't appear in core engine logic. |
| **Iris Constant** | Confirm `oracle.py` references Iris only as messenger/voice, never as a Pillar Keeper. |
| **Sequentiality** | Spot-check 3 recent edits in `PIVOT_LOG.md`. Do they follow Plan → Verify → Execute? |
| **Gnosis Preservation (L1→L2→L3)** | Read `oracle.py` method `_track_soul_evolution`. Does it produce L3 abstractions, or just L1 logs? |
| **Podman Sovereignty** | Read `docs/research/R_PODMAN_SOVEREIGN_V2.md`. Verify the `keep-id` protocol is documented, even if not in the Python layer. |

### Pair B: `ORACLE_STACK.md` vs Actual Architecture

Compare every claim in §3 Core Architecture against the actual code:

- **Claim**: "Oracle.talk() uses Nova speculative decode". Read `oracle.py:208` — confirm the flow matches the description (confidence check → escalate → fallback).
- **Claim**: "ModelGateway has 7-provider fallback chain". Read `model_gateway.py` — count the backends. Which are missing?
- **Claim**: "Hardware target: Ryzen 7 5700U, 14Gi RAM". Read `config/models.yaml` — do any model specs exceed 12Gi available?

**List every discrepancy you find, even minor wording differences.**

### Pair C: `PIVOT_LOG.md` Decisions vs Code

| Decision | Code Must Show | Check |
|----------|----------------|-------|
| **Decision 50** (Podman keep-id) | Quadlets at `~/.config/containers/systemd/` use `UserNS=keep-id` | `grep -rn "keep-id\|:U\|:Z" ~/.config/containers/systemd/*.container` |
| **Decision 52** (Jem-2.0 Oversoul) | Sub-facet soul files at `data/entities/jem/souls/` | `ls data/entities/jem/souls/ 2>/dev/null` |
| **Decision 53** (Belial local model) | Belial's model is `qwen3-4b-thinking-q4_k_m` | `grep "belial" config/entities.yaml -A 5` |
| **Decision 54** (Remediation complete) | 241 tests pass, all findings FIXED | Verify `docs/review/FINDINGS_LOG.md` shows 🟢 FIXED for all 29 entries |

### Pair D: `AGENTS.md` vs Agent Readiness

The document describes a fleet of CLI agents (Opus 4.6, OpenCode CLI, Cline, Gemini CLI) with specific roles. Check:

- Do the `.opencode/agents/` files exist for all mentioned agents? (`ls .opencode/agents/*.md`)
- Do the listed "Quick Start" commands actually work? Run `omega version`, `omega backends`, `omega list-entities` (in test mode).
- Does the Provider Fabric description match `config/providers.yaml`?

---

## Phase 3: Gap Analysis & Severity Assessment

### Gap Severity Rubric

| Severity | Definition | Example |
|----------|------------|---------|
| **🔴 CRITICAL** | Security vulnerability, data loss risk, or mandate violation that would cause incorrect behavior in production | `asyncio` used in async path; entity overwrite without warning |
| **🟡 HIGH** | Architectural inconsistency that would cause a bug under specific conditions (edge case) | Config load that fails silently; missing env var fallback |
| **🔵 MEDIUM** | Doc-code mismatch that does not cause a bug but misleads developers or operators | Stale doc describing old flow |
| **🟢 LOW** | Cosmetic, naming, or formatting inconsistency | Variable naming vs doc terminology |
| **⚪ INFO** | Not a bug, but a suggestion for improvement | A doc that could be clearer |

### Requirements for Each New Finding

Each finding must include:
1. **Evidence**: The exact file, line number, and surrounding code or document text
2. **Sovereign Mandate Violated** (if applicable): Which of the 6 pillars
3. **Fix Suggestion**: One sentence actionable description
4. **Estimated Fix Time**: In hours/minutes

---

## Phase 4: Strategic Recommendations

### Phase C Readiness Scoring

Rate each dimension 0-10:

| Dimension | Description |
|-----------|-------------|
| **Architecture** | Does the code structure match the documented architecture? |
| **Security** | Are there obvious security holes (path traversal, async race conditions)? |
| **Test Coverage** | Is `make test` sufficient for community trust? |
| **Documentation** | Would a new developer understand the project from the docs? |
| **Onboarding** | Could someone set up Omega from scratch using only the docs? |
| **Mandate Compliance** | How well do the 6 Sovereign Mandates hold in code? |

**Total Score**: /60

### Top 3 Recommendations

For each:
- **What**: The actionable item
- **Why**: The strategic rationale
- **When**: Pre-Phase C, Phase C, or Post-Phase C
- **Owner**: Which agent role (Builder, Researcher, Scribe, etc.)

---

## Phase 5: Output Requirements

Your output must include ALL of the following sections:

1. **[SUMMARY]** — One-paragraph executive summary of the strategic health
2. **[TRIANGULATION RESULTS]** — Mismatches found in each Pair (A, B, C, D)
3. **[NEW FINDINGS TABLE]** — Any issues found, using the rubric format
4. **[SOVEREIGN MANDATE COMPLIANCE]** — Per-mandate GREEN/YELLOW/RED rating with evidence
5. **[PHASE C READINESS]** — Dimensional scores /60 + top 3 recommendations
6. **[REGRESSION PREVENTION ASSESSMENT]** — Are the §4 prevention measures adequate?
7. **[EDGE CASES CHECKED]** — List the edge cases you manually verified

### Edge Cases You Must Check

- **Empty config**: What happens if `omega.yaml` is missing? (Run `PYTHONPATH=src python3 -c "from omega.oracle.oracle import Oracle; o=Oracle(); import asyncio; asyncio.run(o.bootstrap())"`)
- **Malformed soul file**: What if `soul.yaml` has invalid YAML?
- **Duplicate entity registration**: What if a WAD and an entity with the same name are loaded?
- **Concurrent soul writes**: Are there still race conditions in `_track_soul_evolution`?
- **Transient session with memory disabled**: Does `/transient` truly skip soul writes?

---

## Closure Criteria

Deep Dive 2 is complete when you have delivered:

1. ✅ Document triangulation for all 4 pairs (A, B, C, D)
2. ✅ Zero CRITICAL findings (if any found, escalate immediately)
3. ✅ Phase C Readiness score with supporting evidence
4. ✅ At least 3 edge cases manually verified (empty config, duplicate entity, transient session)
5. ✅ All claims cross-referenced against 2+ sources (triangulation rule)

**Account 1 has already produced 29 findings from 2 reports. If you find 0 new issues, that is a success — it means the remediation was thorough. If you find 1-3 new medium/low issues, that is expected — no remediation is perfect. If you find more than 5, the remediation was incomplete and Builder mode must revisit.**

Begin.
