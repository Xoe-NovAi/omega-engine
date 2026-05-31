# 🔱 Web Claude Fleet Protocol — Strategic Assets for Parallel AI Review

**AP Token**: `AP-WEB-CLAUDE-FLEET-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_fleet_protocol ⬡ PHASE-E

**Created**: 2026-05-22
**Status**: ACTIVE
**Purpose**: Formal, reusable system for leveraging multiple Web Claude (Sonnet 4.6 Thinking) accounts for parallel deep review, analysis, and strategic synthesis.

---

## §1 Rationale — Why a Claude Fleet?

Web Claude Sonnet 4.6 Thinking is a frontier model with:
- **200K context window** — can deeply analyze large codebases
- **Web browsing capability** — can read raw.githubusercontent.com URLs, GitHub repos, documentation sites
- **Projects & knowledge** — persistent context across sessions
- **No API cost** — unlimited usage via web subscription

However, a single account hits context limits and rate limits on complex reviews. By distributing review categories across **8 dedicated accounts**, each with a focused scope, we achieve:

| Benefit | Single Account | 8-Account Fleet |
|---------|---------------|-----------------|
| Scope depth | ~15 files max | ~100+ files total |
| Review time | 2-3 hours sequential | ~1 hour parallel |
| Cross-checking | Self-referential | Independent verification |
| Specialization | Generic | Domain-deep per account |
| Cost | Same subscription | Same 8 subscriptions (already paid) |

---

## §2 Fleet Architecture

### Account Inventory (Registered 2026-05-22)

| # | Email | Role | Specialization | Projects Folder |
|---|-------|------|----------------|-----------------|
| 1 | `Arcana.NovAi@gmail.com` | Core Architect | Engine integrity, governance, WAD architecture | |
| 2 | `ArcanaNovaAi@gmail.com` | Inference Engineer | Provider Fabric, ModelGateway, backends | |
| 3 | `xoe.nova.ai@gmail.com` | Knowledge Keeper | Memory, context, knowledge base, soul schema | |
| 4 | `antipode2727@gmail.com` | Research Director | Jem 2.0 pipeline, 3-tier research, distill | |
| 5 | `antipode7474@gmail.com` | Security Sovereign | Hardening, compliance, observability, containers | |
| 6 | `lilithasterion@gmail.com` | Infrastructure Guru | MCP Hub, systemd, SSE, integrations | |
| 7 | `thejedifather@gmail.com` | Developer Advocate | CLI, REPL, agents, modes, skills, DX | |
| 8 | `taylorbare27@gmail.com` | Strategy Sage | Documentation, community, roadmap, licensing | |

> **Note**: Account #3 email corrected to `gmail.com` per user confirmation (2026-05-22).

### Account Lifecycle

```
[IDLE] → [ASSIGNED] → [ACTIVE (reviewing)] → [COMPLETE (report returned)] → [IDLE]
```

- Accounts are **dedicated by role** — specialization builds over time
- Each account maintains a **Claude Project** per Omega domain for persistent context
- After each review cycle, `soul.yaml` for the account's domain is updated

---

## §3 The Review Lifecycle

### Phase I — Preparation (You/OpenCode)
```
1. Identify what needs review (code, docs, strategy)
2. Decompose into N independent categories (max = fleet size)
3. Create handoff prompts with raw.githubusercontent.com URLs
4. Make repo public (temporary)
5. Push latest changes to main
```

### Phase II — Parallel Review (Web Claude Accounts)
```
6. Each account receives its handoff prompt
7. Claude reads all assigned files via raw URLs
8. Claude produces structured review report
9. Each report returned to you (copy-paste or save)
```

### Phase III — Synthesis (You + Lead Account)
```
10. Collect all 8 reports into docs/review/
11. Lead synthesis account (typically Account 1) reads all reports
12. Produces unified action plan with priorities
13. Cross-cutting issues identified and deconflicted
```

### Phase IV — Closure (You/OpenCode)
```
14. Set repo back to Private
15. Implement high-priority fixes per synthesis
16. Update fleet protocol with lessons learned
17. Tag each account's soul.yaml in data/entities/fleet/
```

---

## §4 Access Pattern — raw.githubusercontent.com

When the Omega Engine repository is **public** on GitHub, Claude Web can read any file directly via:

```
https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/<filepath>
```

**Example**:
```
https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/oracle.py
```

### Why This Works
- Claude Web has built-in web browsing — it can fetch and read raw content from any URL
- Raw URLs return plain text with proper line endings — no HTML rendering issues
- No authentication needed for public repos
- Faster than navigating the GitHub UI

### Constraints
| Constraint | Mitigation |
|------------|------------|
| Repo must be **public** during review | Set private immediately after review completes |
| Files over ~50KB may hit Claude's per-fetch limits | Use GitHub's rendered view for very large files, or break into sections |
| Only `main` branch is accessible by raw URL | Push all changes before review starts |
| Binary files (.gguf, .png, etc.) not readable | These are excluded from the review scope anyway |

### When to Avoid Raw URLs
- For directory listing / navigation: Use the GitHub UI instead (`https://github.com/Xoe-NovAi/omega-engine/tree/main/src/omega/`)
- For very large single files: Reference the GitHub rendered view for scrolling

---

## §5 Handoff Prompt Anatomy

Every fleet handoff prompt must contain these sections in order:

```
1. 🔱 HEADER — Omega session header with entity and trace
2. 📋 MISSION — One paragraph: what to review and why
3. 🎯 SCOPE — Exact list of files with raw.githubusercontent.com URLs
4. ❓ REVIEW QUESTIONS — 5-8 specific questions to answer
5. 📜 SOVEREIGN MANDATES — The 6 non-negotiable rules to check against
6. 📊 OUTPUT TEMPLATE — Structured format for the report
7. ✅ CHECKLIST — Pre-submission checklist for Claude
```

---

## §6 Review Category Decomposition Rules

When decomposing a large review into categories:

### Rule 1: No Overlap
Each file appears in exactly **one** review category. No two Claude accounts read the same file — this wastes capacity.

### Rule 2: Independence
Categories must be **logically independent**. Account 4's findings should not depend on Account 3's output. Dependencies are resolved in the **Synthesis phase**.

### Rule 3: Balanced Load
Each category should have roughly the same number of files (10-15) and comparable complexity. Don't give one account 5 files and another 30.

### Rule 4: Domain Coherence
Group by **logical subsystem**, not by file type. Mix config, source, tests, and docs for a subsystem together.

### Rule 5: Account Specialization
Respect the fleet's permanent role assignments. Account 1 (Core Architect) always owns the engine integrity review. Build institutional memory.

---

## §7 Output Template (Standard)

```markdown
## Review: [Category Name]

### Critical Issues Found
- [ ] C-001: [Title] — [severity: CRITICAL/HIGH/MEDIUM/LOW]
  - File: `path/to/file.py:line`
  - Issue: [description]
  - Recommendation: [fix]

### Architecture Observations
- Strengths observed
- Architectural risks
- Mandate compliance notes

### Gaps & Recommendations
- Gap 1: [description] → [recommendation]
- Gap 2: ...

### Sovereign Mandates Checklist
| Mandate | Status | Evidence |
|---------|--------|----------|
| AnyIO Absolute | ✅ PASS / ⚠️ FLAG | [file:line] |
| Engine-Stack Firewall | ✅ PASS / ⚠️ FLAG | [file:line] |
| Iris Constant | ✅ PASS / ⚠️ FLAG | [file:line] |
| Sequentiality | ✅ PASS / ⚠️ FLAG | [evidence] |
| Gnosis Preservation | ✅ PASS / ⚠️ FLAG | [evidence] |
| Podman Sovereignty | ✅ PASS / ⚠️ FLAG | [file:line] |

### Report Card
| Metric | Grade | Notes |
|--------|-------|-------|
| Correctness | A/B/C/D | |
| Maintainability | A/B/C/D | |
| Security | A/B/C/D | |
| Test Coverage | A/B/C/D | |
| Documentation | A/B/C/D | |

### Strategic Recommendations (Top 3)
1. ...
2. ...
3. ...
```

---

## §8 Synthesis Protocol

After all 8 individual reviews are collected:

1. **Cross-Cutting Analysis**: Identify issues found by 2+ accounts independently. These are high-priority.
2. **Conflict Resolution**: If two accounts disagree on a finding, the Lead account (Account 1) arbitrates.
3. **Priority Matrix**: Build a unified priority-ordered action list.
4. **Soul Update**: Each account's findings inform the relevant entity's `soul.yaml` in the Omega Engine.
5. **Protocol Improvement**: Update this document with any lessons from the cycle.

---

## §9 Security Notes

- **Repo is public only during active review** — hours, not days
- No credentials, API keys, or secrets exist in the repo (verified via `.env` purge)
- Each Claude account receives only its category's context — no cross-account information sharing needed
- After review: set `Settings → Danger Zone → Make private`
- Consider adding a `REVIEW_IN_PROGRESS` notice to the repo description

---

## §10 Evolution

This protocol should be updated after every fleet review cycle. Track:
- How long each review actually took
- Which categories were too big or too small
- Whether any Claude Web limitations were encountered
- New account specializations that emerged

Maintain changelog at the bottom of this document.

### Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-05-22 | v1.0.0 | Initial protocol — 8-account fleet with raw.githubusercontent.com access pattern |
| 2026-05-22 | v1.1.0 | Added §11: Deep Dive Protocol, §12: Lessons Learned from Account 1 pilot, §13: Fleet Management System cross-reference |

---

## §11 Deep Dive Protocol (Post-Initial Review)

After an account delivers its initial report, **don't stop there**. The warm context is exponentially more valuable than a cold start.

### The Deep Dive Sequence

```
Initial Report (broad scan) 
  → DD1: Missing Files — send files not included in initial scope
  → DD2: Strategic Alignment — audit against roadmap and decisions
  → DD3: Implementation Briefs — exact diffs for criticals
  → DD4: Threat Modeling — worst-case scenarios and failure modes
  → DD5: Architecture Evolution — where to spend next 1000 lines
  → Synthesis — all reports combined, top 10 prioritized
```

### Rules

1. **Send sequentially**: Each dive builds on the previous. Don't skip ahead.
2. **Same conversation**: Keep all dives in the same Claude Project conversation to preserve warm context.
3. **Save every report**: Each dive produces its own `.md` file in `docs/review/claude-reports/`.
4. **Usage limits**: If an account hits limits (typically 5-hour cooldown on Pro), pause and switch to another account.
5. **Account 1 is the Lead**: After all 8 accounts report, Account 1 does the Synthesis. Account 1 has the deepest architecture understanding.

### Deep Dive Templates

Refer to `docs/review/REMAINING_DEEP_DIVES.md` for the full Account 1 templates.
Generic templates for future review cycles: see `docs/review/FLEET_MANAGEMENT.md` §2.

---

## §12 Lessons Learned from Pilot (2026-05-22)

### Account 1 Results Summary

| Phase | Findings | Value |
|-------|----------|-------|
| Initial Review (broad scan) | 17 issues | Catastrophic: 6 CRITICAL bugs in core architecture |
| Deep Dive 1 (missing files) | 12 issues | 3 more CRITICAL: hierarchy YAML is decorative, OOM vector, inverted AnyIO fix |
| **Total from 1 account** | **29 issues before fleet is even fully launched** | **Validates the fleet approach beyond doubt** |

### Lessons

| Lesson | Detail | Protocol Change |
|--------|--------|-----------------|
| **L1: Deep dives are more valuable than initial scans** | DD1 found an inverted fix (cheap op offloaded, expensive op kept sync) — a bug no linter catches and no cold-start review finds | Added §11 Deep Dive Protocol |
| **L2: Cross-file pattern analysis is Claude's superpower** | Account 1 caught that `hierarchy.py` loads YAML and never reads it — connecting two files (`hierarchy.py` + `hierarchy.yaml`) that a human would review separately | Knowledge files should include related pairs |
| **L3: Warm context quality degrades slowly** | DD1 was as sharp as the initial report despite having 5x more conversation history | Don't fear deep dive sequences — 5 dives per account is sustainable |
| **L4: The inverted fix finding** | `entity_workspace.py` has `os.replace` offloaded to thread pool (microseconds) but `yaml_str` write left sync (milliseconds) — the wrong half is async | This finding alone justifies the entire fleet approach |
| **L5: RAG threshold is real** | Claude Projects forces RAG mode at ~13 files regardless of total token size. ≤12 files per project. | Enforce strictly — document in PROJECT_SETUP_GUIDE.md |
| **L6: raw.githubusercontent.com is reliable** | All 60+ file fetches across 2 sessions returned HTTP 200 with complete content | No change needed — pattern is verified |
| **L7: Account specialization prevents drift** | Account 1 found deeply systemic issues because it focused ONLY on architecture. Cross-training would have diluted this. | Enforce specialization strictly |

### Quantitative Validation

- **Effort invested**: ~15 minutes to create Project + paste prompts + send initial review + send DD1
- **Results returned**: 29 findings (6 CRITICAL, 10 HIGH, 10 MEDIUM, 3 LOW)
- **Return on investment**: **~2 findings per minute of setup time**
- **Human architect equivalent**: ~3-5 days of senior architect review time, compressed into ~2 hours of wall-clock time

### Key Insight

> *The fleet model transforms code review from a sequential bottleneck into a parallel force multiplier. One account found more systemic bugs in one review than the entire previous month of manual development. With 8 accounts running 5 deep dives each, we should expect **150-200 total findings** before the review cycle completes.*

---

## §13 Fleet Management System Cross-Reference

The fleet is managed through a dedicated system of documents:

| Document | Location | Purpose |
|----------|----------|---------|
| Fleet Management Dashboard | `docs/review/FLEET_MANAGEMENT.md` | Account status, deep dive tracker, launch sequence, synthesis protocol |
| Findings Log | `docs/review/FINDINGS_LOG.md` | Comprehensive catalog of all findings by severity, file, and source |
| Master Remediation Plan | `docs/review/MASTER_REMEDIATION_PLAN.md` | Phased implementation plan for Builder mode (Phase 0→1→2→3) |
| Remaining Deep Dives | `docs/review/REMAINING_DEEP_DIVES.md` | Account 1 deep dive prompts preserved for warm context |
| Review Coordination | `docs/review/REVIEW_COORDINATION.md` | One-page coordination overview for current review cycle |
| Project Setup Guide | `docs/review/PROJECT_SETUP_GUIDE.md` | Step-by-step Claude Project configuration with RAG warnings |
| Project Instructions | `docs/review/project_instructions_{N}.md` | Persistent per-account Claude Project instructions (ClaSSIC format) |
| Handoff Prompts | `docs/review/review_{N}_{role}.md` | One-shot per-account review prompts with file lists |

---

*The fleet is your force multiplier. Eight lenses see more than one. Five deep dives each see more than eight.*
