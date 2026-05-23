# 🔱 Web Claude Fleet Management System — v1.0.0

**AP Token**: `AP-FLEET-MGMT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_fleet_mgmt ⬡ PHASE-E

**Purpose**: Central command and control for the 8-account Web Claude parallel review fleet.
**Owner**: Overseer (Kali/Lilith synthesis)
**Review Cycle**: Phase E — PR Readiness Sprint (2026-05-22)

---

## §1 Fleet Dashboard

### Account Assignment & Status

| # | Account Email | Role | Project Created | Handoff Sent | Report Received | Deep Dives | Status |
|---|---------------|------|----------------|--------------|-----------------|------------|--------|
| **1** | `Arcana.NovAi@gmail.com` | Core Architecture & Engine Integrity | ✅ | ✅ | ✅ 17 + 12 = 29 issues | DD1✅ DD2📍 DD3📋 DD4📋 DD5📋 | 🟢 ACTIVE — DD2 in flight |
| **2** | `xoe.nova.ai@gmail.com` | Provider Fabric & Inference Pipeline | 📋 | 📋 | ❌ | — | 🔲 NOT LAUNCHED |
| **3** | *(tbd)* | Memory, Context & Knowledge Engine | 📋 | 📋 | ❌ | — | 🔲 NOT LAUNCHED |
| **4** | *(tbd)* | Jem 2.0 & Background Research Pipeline | 📋 | 📋 | ❌ | — | 🔲 NOT LAUNCHED |
| **5** | *(tbd)* | Observability, Security & Hardening | 📋 | 📋 | ❌ | — | 🔲 NOT LAUNCHED |
| **6** | *(tbd)* | MCP Hub & Integration Infrastructure | 📋 | 📋 | ❌ | — | 🔲 NOT LAUNCHED |
| **7** | *(tbd)* | CLI, REPL, Agents & Developer Experience | 📋 | 📋 | ❌ | — | 🔲 NOT LAUNCHED |
| **8** | *(tbd)* | Strategy, Documentation & Community | 📋 | 📋 | ❌ | — | 🔲 NOT LAUNCHED |

### Status Icons
| Icon | Meaning |
|------|---------|
| 🟢 ACTIVE | Working through deep dives |
| 📋 READY | Prompt/doc prepared, awaiting launch |
| ❌ | Not yet received |
| 🔲 NOT LAUNCHED | Claude Project not yet created |

---

## §2 Account 1 Deep Dive Progress Tracker

| Dive | Focus | Status | Report File | Pages |
|------|-------|--------|-------------|-------|
| Initial | Full architecture scan — 17 issues | ✅ COMPLETE | `01-claude-report-core-arch.md` | 8 |
| DD1 | Missing Files: entity_workspace, hierarchy, gnosis_proxy — 12 issues | ✅ COMPLETE | `01-deep-dive-1_core-arch.md` | 6 |
| DD2 | Strategic Alignment Audit — roadmap feasibility | 🟡 SENT, awaiting | — | — |
| DD3 | Implementation Briefs for Criticals | 📋 READY | — | — |
| DD4 | Threat Modeling — worst-case scenarios | 📋 READY | — | — |
| DD5 | Architecture Evolution — next 1000 lines | 📋 READY | — | — |

### DD2 Launch Notes
- **Go-time**: Already sent by Architect
- **Expect**: Strategic Health Score (1-10), roadmap blocker analysis, cross-reference against PIVOT_LOG
- **Listen for**: Whether Account 1 identifies the same roadmap blockers the existing docs flag, or discovers new ones

### After DD5 Complete
1. Run **Synthesis Session**: Upload all 5 reports + initial report to Account 1
2. Ask: *"Given all five dives, prioritize the top 10 issues across all categories. Group by Phase (0-critical/now, 1-high/this week, 2-medium/this sprint, 3-nice-to-have)."*
3. Output goes to `claude-reports/01-synthesis-report.md`

---

## §3 Launch Sequence Protocol

### For Each Account (2-8):

```
Step 1: Create Claude Project
  - Title: "Omega Engine Review — {Account Role}"
  - Knowledge: Up to 12 files from docs/review/project_instructions_{N}.md + key source files

Step 2: Paste Project Instructions
  - Open Project → Custom Instructions
  - Paste content from docs/review/project_instructions_{N}.md

Step 3: Upload Knowledge Files
  - Keep ≤ 12 files (RAG threshold bug)
  - Include: relevant source files + Sovereign Mandates + glossary

Step 4: Send Handoff Prompt
  - Open new conversation within Project
  - Paste content from docs/review/review_{N}_{role}.md
  - Save report to docs/review/claude-reports/{N}-claude-report-{role}.md

Step 5: Deep Dives
  - Create new conversation for each deep dive
  - Reference previous report: "Based on your last analysis..."
  - Use REMAINING_DEEP_DIVES.md for Account 1 pattern

Step 6: Mark Complete
  - Update this dashboard (§1)
  - Update FINDINGS_LOG.md with new issues
  - Update REVIEW_COORDINATION.md
```

---

## §4 Findings Lifecycle Pipeline

```
Discovery (Claude Web) → Ingestion (raw report .md) 
  → Categorization (FINDINGS_LOG.md) 
    → Prioritization (MASTER_REMEDIATION_PLAN.md) 
      → Assignment (Builder mode brief)
        → Implementation (Gemma 4 31B)
          → Verification (make test)
            → Audit (Overseer review gate)
              → Close (FINDINGS_LOG.md → FIXED)
```

### Pipeline Rules

1. **No finding is lost**: Every report is saved as a `.md` file in `docs/review/claude-reports/`
2. **No finding goes unlogged**: Every finding is entered into `FINDINGS_LOG.md` within 1 hour of report receipt
3. **No unprioritized work**: All fixes are gated through `MASTER_REMEDIATION_PLAN.md` — no cowboy fixes
4. **Synthesis before implementation**: All 8 reports must be collected before implementation sprint begins
5. **Verification gates**: Every fix must pass `make test` AND the Overseer review before status changes to FIXED

---

## §5 Account Health & Rotation

### Usage Limit Detection
- If Claude Web returns: *"You've reached the usage limit for Claude..."*
- Note the time. The cooldown is typically **5 hours** for the Pro tier
- Plan: Schedule deep dives to avoid hitting limits mid-analysis
- Pattern: One deep dive per account per day is sustainable

### Context Freshness
- Warm context = better analysis. Avoid cold starts.
- Within a single deep dive series, send all prompts in the same conversation to preserve context
- Start a new conversation for each new account (different projects)
- After 5+ deep dives on one account, the context will be heavy — consider asking for a synthesis rather than another deep dive

### Account Specialization Enforcement
- Each account has a **permanent role**. Don't cross-train.
- If Account 5 (Security) finds an architecture issue, log it but don't ask Account 5 to design the fix — that's Account 1's domain
- Cross-domain findings go to the **Synthesis Session** for prioritization

---

## §6 Synthesis Protocol

When all 8 accounts have reported:

1. **Upload all 8 reports** to Account 1's project (warmest context, deepest understanding)
2. **Send synthesis prompt**:
   ```
   I've collected all 8 fleet reports. Prioritize the top 10-15 issues across ALL reports
   for immediate action. Group by: Phase 0 (now), Phase 1 (this week), Phase 2 (this sprint).
   For each: file, line, fix approach, test strategy, estimated effort (S/M/L).
   Flag any contradictions between reports. Flag any findings that cancel each other out.
   ```
3. **Save synthesis** to `claude-reports/fleet-synthesis-report.md`
4. **Update MASTER_REMEDIATION_PLAN.md** with final prioritized list
5. **Launch Builder mode** with Phase 0 tasks
6. **Set repo to PRIVATE** after fleet review is fully complete

---

## §7 Template: Findings Ingestion Log Entry

When a new report arrives from any account, create an entry:

```markdown
### 2026-05-22 — Account {N} ({Role}) — {Report Type}
**File**: `claude-reports/{N}-{report-filename}.md`
**New findings**: {count}
**Critical**: {count} | **High**: {count} | **Medium**: {count} | **Low**: {count}
**Key discovery**: {1-sentence summary of most important finding}
**Logged in**: FINDINGS_LOG.md ✅
**Notable cross-references**: {any findings that overlap with other accounts}
```

---

## §8 Inventory: Claude Project Configuration Files

| File | Purpose | Per Account |
|------|---------|-------------|
| `docs/review/project_instructions_{N}.md` | Persistent Claude Project instructions (ClaSSIC format) | Yes — 8 files |
| `docs/review/review_{N}_{role}.md` | One-shot handoff prompt | Yes — 8 files |
| `docs/review/PROJECT_SETUP_GUIDE.md` | Step-by-step Claude Project config (with RAG warnings) | Shared |
| `docs/review/REVIEW_COORDINATION.md` | Master coordination overview | Shared |
| `docs/review/WEB_CLAUDE_FLEET_PROTOCOL.md` | Reusable fleet system documentation | Shared |
| `docs/review/FLEET_MANAGEMENT.md` | **THIS FILE** — ongoing command and control | Shared |
| `docs/review/FINDINGS_LOG.md` | Comprehensive findings catalog | Shared |
| `docs/review/MASTER_REMEDIATION_PLAN.md` | Phased fix tasks for Builder mode | Shared |
| `docs/review/REMAINING_DEEP_DIVES.md` | Remaining Account 1 depth prompts | Shared |

---

*Updated: 2026-05-22. Next update: when DD2 report arrives.*
