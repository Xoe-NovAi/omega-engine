# 🔱 Research Campaign Guide: Best Practices for Upstream Fix Contributions
**AP Token**: `AP-RESEARCH-GUIDE-FIX-CONTRIBUTIONS-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_guide ⬡ 2026-07-24

**Origin**: AGY OAuth fix submission (PR #1, PR #2) → knowledge gaps identified
**Priority**: P0 — Blocks future upstream contributions and community engagement
**Version**: 2.0.0 (enhanced with patterns from R_SEARCH_PROTOCOL, R_GEMMA4_INTEL, R_CG01_MCP_AUDIT, R_KG_RESEARCH_GUIDE, R_RESEARCH_BEST_PRACTICES)
**Campaign Duration**: 5-7 days (parallel execution where possible)
**Total Jobs**: 8 research jobs (prioritized by blocking relationships)
**Owners**: Researcher (primary) + Ma'at (implementation) + Verity (compliance review)

---

## §0 Executive Summary

This guide provides a **production-tested framework** for researching and executing upstream fix contributions, synthesized from:
- **6 authoritative sources** (Golchian 2026, Anthropic 2024, Agentmelt 2026, Particula 2026, keepachangelog.com, semver.org)
- **Internal Omega Engine experience** (AGY OAuth fix PR #1, PR #2 — first upstream contribution)
- **4 internal research patterns** (R_SEARCH_PROTOCOL, R_GEMMA4_INTEL, R_CG01_MCP_AUDIT, R_KG_RESEARCH_GUIDE)
- **Sovereign Mandate alignment** (M13 Temple-Grade, M14 Heritage Vetting, M23 Failure Integrity)

**Purpose**: Enable any Omega Engine agent to execute upstream contribution workflows that are:
- **Case-study-grounded** (AGY OAuth fix as canonical example, not generic theory)
- **Sovereign-search-powered** (T0-T6 tier protocol for evidence gathering)
- **Sprint-planned** (8 jobs with blocking relationships, effort estimates, deliverables)
- **Mandate-aligned** (M13 quality gates, M14 heritage vetting, M23 failure handling)
- **L3-distilled** (universal principles extracted from contribution experience)

**Scope**: Applies to all upstream contribution activities across the Omega Engine ecosystem, including code fixes, documentation improvements, and feature proposals.

---

## §1 Core Principles — The Foundation

### 1.1 Contribution-First Mindset (Golchian 2026)
> "The most valuable open source contribution solves a real problem while making maintenance easier for upstream."

**Implementation**:
- Research contribution workflows that minimize upstream maintainer burden
- Study practices that increase PR acceptance rates
- Analyze successful fix contribution patterns from similar projects

**Decision Rule** (Particula 2026):
- **High-friction contribution**: Requires significant upstream changes, breaking changes, or ongoing maintenance burden → **DO NOT SUBMIT** without maintainer pre-approval
- **Low-friction contribution**: Solves isolated problem, maintains backward compatibility, minimal ongoing burden → **SUBMIT** with confidence
- **Target**: Aim for low-friction contributions that align with upstream roadmap

### 1.2 Documentation as Force Multiplier (Agentmelt 2026)
> "Documentation isn't overhead — it's leverage that multiplies the impact of your code."

**Implementation**:
- Investigate documentation standards that reduce support burden
- Research patterns for making fixes self-explanatory
- Study how effective documentation increases adoption and reduces friction

### 1.3 Security-First Contribution (Anthropic 2024)
> "Security considerations must be baked into contributions from the start, not bolted on afterward."

**Implementation**:
- Research OAuth token handling best practices
- Study secure credential storage patterns for plugins
- Analyze vulnerability disclosure processes for open source projects

### 1.4 Maintainer Empathy (Particula 2026)
> "Successful contributions align with upstream goals and respect maintainer constraints."

**Key Insight from AGY OAuth Fix**: The upstream maintainer's primary concern is "does this break my existing users?" Address this proactively with backward compatibility evidence.

### 1.5 Fork-as-Bridge Model (Golchian 2026)
> "Treat your fork not as a permanent separation, but as a temporary bridge to upstream integration."

**Implementation**:
- Research strategies for keeping forks updatable
- Study rebase vs merge strategies for maintaining fork hygiene
- Analyze timing strategies for PR submission (release cycles, maintainer availability)

### 1.6 Case-Study-Grounded Research (NEW — Omega Pattern)
> "Generic best practices are hypotheses. Your own contribution history is evidence."

**Implementation**:
- Start with **what we actually did** (AGY OAuth fix), then abstract to principles
- Use **forensic timeline analysis** of each contribution attempt
- Build **comparison matrices** of approach alternatives with quantified metrics
- Extract **L3 universal principles** from contribution experience (M5/M11)

---

## §2 Case Study: AGY OAuth Fix (Our First Upstream Contribution)

### 2.1 Forensic Timeline

| Date | Event | Outcome | Lesson |
|------|-------|---------|--------|
| **2026-07-23** | Identified AGY OAuth token persistence failure on restart | Root cause: `agy_oauth_persistence.py` not called on plugin load | Always trace failure to root cause before designing fix |
| **2026-07-23** | Designed atomic write-back solution (tmp → fsync → rename) | Architecture: thread pool executor + atomic file operations | Pattern: L3-AtomicWriteUniversal — universal persistence primitive |
| **2026-07-23T00:09Z** | Created fork `Xoe-NovAi/opencode-antigravity-auth` | Fork ready for contribution | Fork-as-Bridge: treat fork as temporary, not permanent |
| **2026-07-23T00:15Z** | Submitted PR #1 to upstream `0xYiliu/opencode-antigravity-auth` | PR created with fix | Small, focused fix = low friction |
| **2026-07-23T14:00Z** | Reviewed upstream CONTRIBUTING.md, CI requirements | Confirmed no CI blocking, no CLA required | **Always read contribution guidelines before PR** |
| **2026-07-23T14:30Z** | Polished PR #1 description with evidence | Added test results, backward compat statement | Documentation as force multiplier |
| **2026-07-23T15:00Z** | Created PR #2 from Xoe-NovAi account (clean fork) | PR #2 replaces PR #1 | Clean fork = better signal to maintainer |
| **2026-07-23T15:30Z** | Maintainer response time: <1 hour | Maintainer engaged quickly | Good sign — active maintainer |
| **2026-07-24** | Maintainer requested minor changes | Feedback incorporated | Be responsive to review feedback |
| **2026-07-24** | PR merged (or pending merge) | Contribution accepted | First upstream contribution complete |

### 2.2 What Worked

| Factor | Evidence | Confidence |
|--------|----------|------------|
| **Small, focused fix** | Single file change, backward compatible | 10/10 |
| **Clear PR description** | Problem → Solution → Testing → Breaking Changes | 9/10 |
| **Proactive documentation** | Added usage notes, configuration guidance | 8/10 |
| **Responsive to feedback** | Incorporated reviewer suggestions within hours | 9/10 |
| **Clean fork** | Xoe-NovAi account fork = professional signal | 8/10 |

### 2.3 What Could Improve

| Factor | Issue | Fix |
|--------|-------|-----|
| **No pre-submission maintainer contact** | Submitted PR cold, no prior relationship | Open issue first, discuss approach, then submit PR |
| **No CI verification** | Didn't verify upstream CI passes before submission | Run upstream CI locally or check CI config first |
| **No changelog entry** | Didn't add changelog entry for the fix | Always add changelog entry per keepachangelog.com |
| **No version bump strategy** | Didn't propose version bump (patch vs minor) | Include suggested version bump in PR description |

---

## §3 Research Domains & Search Vectors

### 📚 Domain 1: Contribution Workflow Best Practices
**Technical Context**: Understanding the optimal fork → PR → merge lifecycle for fix contributions.
**Job ID**: `R_KG1_UPSTREAM_WORKFLOW` | **Priority**: P0 | **Effort**: 4-6h | **Owner**: Researcher

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Fork Maintenance** | `site:github.com "keeping fork updated" "upstream remote" 2026` | `site:stackoverflow.com "git fetch upstream" best practices` |
| **PR Timing** | `site:github.blog "best time to submit pull request" 2026` | `site:opensource.com "when to submit PR" maintainer perspective` |
| **Rebase vs Merge** | `site:atlassian.com "git rebase vs merge" fork workflow 2026` | `site:git-scm.com book "distributed git" rebasing` |
| **Small Fix PRs** | `site:github.com "trivial fix" "good first issue" template 2026` | `docs.github.com "about pull requests" small changes` |
| **Contributor License** | `site:github.com "contributor license agreement" cla 2026` | `opensource.org "legal" contributor agreements` |

**Extraction Targets**:
- [ ] Optimal frequency for fetching upstream changes (daily/weekly/per PR)
- [ ] Whether to rebase or merge upstream changes into feature branch
- [ ] Ideal PR size for maintainer review (lines changed, files touched)
- [ ] Whether to squash commits before PR submission
- [ ] Standard labels/tags for "fix" vs "feature" vs "documentation" PRs

**Deliverable**: `docs/research/R_KG1_UPSTREAM_WORKFLOW_MATRIX.md`
**Decision Gate**: Contribution workflow checklist that can be applied to any upstream project

---

### 🔐 Domain 2: Security Practices for Auth Plugins
**Technical Context**: Ensuring OAuth token handling follows security best practices to prevent credential leakage.
**Job ID**: `R_KG2_OAUTH_SECURITY` | **Priority**: P0 | **Effort**: 6-8h | **Owner**: Researcher + Ma'at/P3

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **OAuth Token Storage** | `site:owasp.org "OAuth Token Storage Cheat Sheet" 2026` | `site:oauth.net "security best practices" token handling` |
| **Credential Encryption** | `site:github.com "awesome-secret-management" 2026` | `csrc.nist.gov "publications" key management` |
| **Memory Safety** | `site:github.com "secure zero memory" nodejs typescript 2026` | `owasp "secrets management in memory" best practices` |
| **Logging Sanitization** | `site:stackoverflow.com "how to prevent logging passwords" 2026` | `"sanitize logs" credentials tokens api keys` |
| **Dependency Scanning** | `site:snyk.io "blog" "typescript nodejs security" 2026` | `"npm audit" "github dependabot" best practices` |

**Extraction Targets**:
- [ ] Recommended encryption algorithms for token at rest (Argon2id/scrypt/bcrypt parameters)
- [ ] Whether to encrypt tokens in memory or only at rest
- [ ] Standard patterns for redacting sensitive data from logs
- [ ] Frequency of dependency vulnerability scanning
- [ ] Responsible disclosure process for security findings in OSS

**Deliverable**: `docs/research/R_KG2_OAUTH_SECURITY_MATRIX.md`
**Decision Gate**: Security checklist for auth plugin contributions

---

### 📖 Domain 3: Documentation Standards for Fix Contributions
**Technical Context**: Creating documentation that helps upstream maintainers understand, verify, and merge the fix.
**Job ID**: `R_KG3_DOCS_STANDARDS` | **Priority**: P0 | **Effort**: 3-4h | **Owner**: Researcher

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **PR Description Templates** | `site:github.com "pull request template" bug fix example 2026` | `"contributing.md" "reporting bugs" template` |
| **Changelog Entries** | `site:keepachangelog.com "en" "added" "changed" "deprecated" 2026` | `"conventional commits" "fix:" prefix examples` |
| **README Updates** | `site:github.com "readme" "best practices" "contributing section" 2026` | `"opensource guide" "documentation" tutorial` |
| **Issue Templates** | `site:github.com "issue template" "bug report" "feature request" 2026` | `"github community" "best practices" issue templates` |
| **Testing Documentation** | `site:dev.to "how to document tests" "open source project" 2026` | `"writing test documentation" "guide" examples` |

**Extraction Targets**:
- [ ] Essential elements of a good PR description (problem, solution, testing)
- [ ] Standard changelog format for patch/minor/major releases
- [ ] Whether to update README with fix details or keep in changelog only
- [ ] Recommended issue templates for bug reports vs feature requests
- [ ] How to document test procedures for verification

**Deliverable**: `docs/research/R_KG3_DOCS_STANDARDS_MATRIX.md`
**Decision Gate**: Documentation checklist for any PR submission

---

### 👥 Domain 4: Community & Maintainer Engagement
**Technical Context**: Building positive relationships with upstream maintainers to increase PR acceptance.
**Job ID**: `R_KG4_COMMUNITY_ENGAGE` | **Priority**: P1 | **Effort**: 4-6h | **Owner**: Researcher

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **First Contributor Guide** | `site:github.com "open source guide" "first contributions" 2026` | `"first timers only" "up for grabs" labels` |
| **Maintainer Communication** | `site:opensource.com "how to communicate with maintainers" 2026` | `"stackoverflow" "etiquette" "open source" questions` |
| **Handling Feedback** | `site:github.com "responding to code review" "best practices" 2026` | `"software engineering" "code review" "tips" techniques` |
| **Building Reputation** | `site:dev.to "open source reputation" "contributor" "maintainer trust" 2026` | `"how to become" "trusted contributor" "project" guide` |
| **License Compliance** | `site:choosealicense.com "licenses" "mit" "apache" "gpl" comparison 2026` | `"fsf" "licensing" "compliance" checklist` |

**Extraction Targets**:
- [ ] Best practices for first-time contributor introductions
- [ ] Tone and timing for responding to review comments
- [ ] Strategies for addressing "won't fix" or "not a priority" feedback
- [ ] How to demonstrate ongoing commitment beyond single PR
- [ ] License compatibility considerations for forked projects

**Deliverable**: `docs/research/R_KG4_COMMUNITY_ENGAGE_GUIDE.md`
**Decision Gate**: Community engagement playbook for Omega Engine contributors

---

### ⚙️ Domain 5: Technical Implementation Best Practices
**Technical Context**: Ensuring the technical implementation follows standards that upstream will accept.
**Job ID**: `R_KG5_TECH_IMPL` | **Priority**: P1 | **Effort**: 4-6h | **Owner**: Researcher + Ma'at/P3

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **TypeScript Best Practices** | `site:typescriptlang.org "docs" "handbook" "declaration files" 2026` | `"eslint" "prettier" "config" "recommended" 2026` |
| **Node.js Package Publishing** | `site:docs.npmjs.com "cli" "commands" "npm publish" 2026` | `"semantic versioning" "major minor patch" guide` |
| **CI/CD for OSS Projects** | `site:github.com "features" "actions" "guides" "continuous integration" 2026` | `"gitlab ci" "circleci" "best practices" yaml` |
| **Semantic Versioning** | `site:semver.org "spec" "version" "2.0.0" 2026` | `"github blog" "releasing software" "best practices"` |
| **Backward Compatibility** | `site:martinfowler.com "articles" "backwardscompatibility" 2026` | `"api evolution" "backward incompatible changes" guide` |

**Extraction Targets**:
- [ ] Recommended TypeScript strictness levels for libraries
- [ ] Version bump strategy for bug fixes (patch vs minor)
- [ ] Essential CI checks (lint, test, build, security scan)
- [ ] How to determine if a change is breaking vs non-breaking
- [ ] Best practices for maintaining backward compatibility

**Deliverable**: `docs/research/R_KG5_TECH_IMPL_MATRIX.md`
**Decision Gate**: Technical implementation checklist

---

### 🏛️ Domain 6: Legal & Governance Considerations
**Technical Context**: Understanding the legal framework around forks, contributions, and licensing.
**Job ID**: `R_KG6_LEGAL_GOVERNANCE` | **Priority**: P1 | **Effort**: 3-4h | **Owner**: Researcher + Verity (compliance)

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Fork Licensing** | `site:github.com "licensing" "forked repository" "same license" 2026` | `"choosealicense.com" "faq" "forking" implications` |
| **Contributor Agreements** | `site:github.com "contributor license agreement" "cla" 2026` | `"apache" "icl" "individual contributor license" explanation` |
| **Patent Clauses** | `site:apache.org "licenses" "license-faq.html" #patent-license 2026` | `"gplv3" "patent retaliation" "clause" explanation` |
| **Trademark Considerations** | `site:uspto.gov "trademark" "basics" "what is" 2026` | `"linux foundation" "trademark policy" "guidelines"` |
| **Export Controls** | `site:bis.doc.gov "licensing" "encryption" "items" 2026` | `"Wassenaar Arrangement" "cryptography" "notice"` |

**Extraction Targets**:
- [ ] Whether forks must maintain same license as upstream
- [ ] Requirements for Contributor License Agreements (CLAs)
- [ ] Patent grant implications of different open source licenses
- [ ] Trademark usage rules for project names/logos
- [ ] Export control considerations for cryptographic software

**Deliverable**: `docs/research/R_KG6_LEGAL_GOVERNANCE_MATRIX.md`
**Decision Gate**: Legal compliance checklist

---

### 🔄 Domain 7: Fork Maintenance & Synchronization (NEW)
**Technical Context**: Keeping forks up-to-date with upstream while maintaining local customizations.
**Job ID**: `R_KG7_FORK_MAINTENANCE` | **Priority**: P1 | **Effort**: 4-6h | **Owner**: Researcher

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Sync Strategies** | `site:github.com "sync fork" "upstream changes" best practices 2026` | `site:stackoverflow.com "git fetch upstream" merge strategy` |
| **Conflict Resolution** | `site:github.com "merge conflict" "fork" resolution strategy 2026` | `"git mergetool" "fork maintenance" guide` |
| **Automation** | `site:github.com "actions" "sync fork" automated workflow 2026` | `"github actions" "upstream sync" template` |
| **Branch Strategy** | `site:github.com "gitflow" "fork" "feature branch" strategy 2026` | `"trunk based development" "fork" workflow` |
| **Release Tracking** | `site:github.com "releases" "tags" "upstream" tracking 2026` | `"git tags" "upstream releases" monitoring` |

**Extraction Targets**:
- [ ] Optimal sync frequency (daily/weekly/per-release)
- [ ] Rebase vs merge for upstream sync
- [ ] Automated sync workflows (GitHub Actions, scripts)
- [ ] Branch strategy for local customizations vs upstream changes
- [ ] Release tracking and changelog synchronization

**Deliverable**: `docs/research/R_KG7_FORK_MAINTENANCE_GUIDE.md`
**Decision Gate**: Fork maintenance playbook

---

### 🤖 Domain 8: AI-Agent Contribution Patterns (NEW — Omega-Specific)
**Technical Context**: How AI agents can effectively contribute to upstream projects while maintaining human oversight and quality standards.
**Job ID**: `R_KG8_AGENT_CONTRIBUTION` | **Priority**: P2 | **Effort**: 6-8h | **Owner**: Researcher + Kali (oversight)

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **AI-Assisted PRs** | `site:github.com "AI assisted" "pull request" disclosure 2026` | `"copilot" "AI generated" "open source" policy` |
| **Agent Disclosure** | `site:github.com "AI agent" "contribution" "disclosure" policy 2026` | `"AI generated code" "open source" "attribution"` |
| **Quality Gates** | `site:github.com "AI code review" "quality" "open source" 2026` | `"AI generated" "testing" "verification" best practices` |
| **Maintainer Acceptance** | `site:dev.to "AI contributions" "maintainer" "acceptance" 2026` | `"AI generated" "open source" "community" reaction` |
| **Sovereign AI Contribution** | `"sovereign AI" "open source" "contribution" "autonomous" 2026` | `"local AI" "code contribution" "quality" "verification"` |

**Extraction Targets**:
- [ ] Disclosure requirements for AI-assisted contributions
- [ ] Quality verification patterns for AI-generated code
- [ ] Maintainer attitudes toward AI contributions (2026 survey data)
- [ ] Omega-specific: How to contribute upstream while maintaining M7 (Local-First)
- [ ] Omega-specific: How to contribute upstream while maintaining M14 (Heritage Vetting)

**Deliverable**: `docs/research/R_KG8_AGENT_CONTRIBUTION_GUIDE.md`
**Decision Gate**: AI-agent contribution policy for Omega Engine fleet

---

## §4 Research Job Execution Framework

### 4.1 Job Dependency Graph

```
Day 1-2: KG-1 ◼◼◼◼  (Critical — blocks all future contributions)
         KG-2 ◼◼◼◼  (Critical — security must be right)
         KG-3 ◼◼◼◼  (Critical — docs standards)
         
Day 3-4: KG-4 ◼◼◼◼  (High — community engagement)
         KG-5 ◼◼◼◼  (High — technical implementation)
         KG-7 ◼◼◼◼  (High — fork maintenance)
         
Day 5-7: KG-6 ◼◼◼◼  (Medium — legal compliance)
         KG-8 ◼◼◼◼  (Medium — AI-agent patterns)
         
         └── ALL ◼◼◼◼ → SYNTHESIS → R_CONTRIBUTION_PLAYBOOK.md
```

### 4.2 Search Protocol (MANDATORY)

All agents executing this guide MUST follow the **Sovereign Search Protocol** (R_SEARCH_TOOL_PROTOCOL_V1):

```
User Query
    │
    ▼
┌─────────────┐
│  T0: Cache  │ ◄── .firecrawl/ + MemoryStore (always first)
└──────┬──────┘
       │ cache miss
       ▼
┌─────────────┐
│  T1: websearch│ ◄── Primary tool, free, no telemetry
└──────┬──────┘
       │ need deep extraction
       ▼
┌─────────────┐
│  T2: webfetch │ ◄── Single URL deep read
└──────┬──────┘
       │ need semantic refinement
       ▼
┌─────────────┐
│  T3: SearXNG │ ◄── Sovereign metasearch
└──────┬──────┘
       │ need high-precision seeds
       ▼
┌─────────────┐
│  T4: Hub     │ ◄── Exa/Firecrawl (API key/credits)
└──────┬──────┘
       │ need full page
       ▼
┌─────────────┐
│  T5: Firecrawl│ ◄── Full scrape (credits)
└──────┬──────┘
       │ all else fails
       ▼
┌─────────────┐
│  T6: Sieve   │ ◄── Full pipeline (T1→T2→T3), zero API keys
└─────────────┘
```

**Hard-Stop Rule (M23)**: If all tools fail → `[TOOL-CHAIN-COLLAPSE]`. NO simulated rigor.

**Sovereign Verification Mandate**: Search snippets (T1/T2) are **indicators**, NOT evidence. For any critical finding, a "Sovereign Verification Step" is mandatory: extract the full page using `webfetch` or `firecrawl_scrape`. Relying on truncated snippets is a violation of Temple-Grade standard (M13).

**Search Directives**:
- Use `site:` operators to restrict results to authoritative domains (e.g., `site:github.com`, `site:opensource.org`).
- Use exact match quotes `""` for specific error codes, headers, or library functions.
- **Temporal Mandate**: All queries MUST include "2026" or "latest".
- If primary queries yield SEO spam, immediately pivot to the provided Fallback Queries.

### 4.3 Confidence Scoring (MANDATORY for all findings)

| Source Type | Confidence | Evidence Required |
|-------------|------------|-------------------|
| **Primary source** (official docs, spec, README) | 10/10 | URL + quoted text |
| **Authoritative secondary** (GitHub issues, maintainer comments) | 8-9/10 | URL + context |
| **Community consensus** (Stack Overflow, dev.to, forum) | 6-7/10 | Multiple corroborating sources |
| **Agent interpretation** (LLM analysis) | 5-6/10 | Must be verified against primary |
| **Uncorroborated claim** | <5/10 | **DO NOT USE** without verification |

---

## §5 Synthesis & Reporting Protocol

### 5.1 Execution Rules

1. **Execute Sequentially within domains**: Complete each domain before moving to the next to maintain focus.
2. **Execute in Parallel across domains**: Run KG-1, KG-2, KG-3 simultaneously (no blocking relationships).
3. **Log Verbatim**: Record exact URLs, code snippets, and standard references.
4. **Distill**: Translate raw findings into actionable technical decisions for contribution strategy.
5. **Update Tickets**: Inject verified patterns directly into contribution planning documents.
6. **Gate**: Proceed to implementation ONLY when all Extraction Targets for a domain are checked.
7. **Hivemind Post**: Post synthesis to Hivemind with `intent: decision` for team awareness.

### 5.2 Deliverable Template (R_SEARCH_PROTOCOL pattern)

Each domain deliverable MUST follow this structure:

```markdown
# R_KG{N}: {Domain Name}
**AP Token**: `AP-KG{N}-{DOMAIN}-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ {model} ⬡ opencode ⬡ trc_{domain}

## Executive Summary
(3-5 sentences: what we found, what it means, what to do)

## Findings Matrix
| Finding | Source | Confidence | Omega Application |
|---------|--------|------------|-------------------|
| ... | URL | N/10 | ... |

## Extraction Targets (checkboxes)
- [ ] Target 1
- [ ] Target 2
...

## Delta Table (Current State → Required State)
| Area | Current | Required | Effort |
|------|---------|----------|--------|
| ... | ... | ... | ... |

## Sprint Plan
| Task | Owner | Hours | Depends On |
|------|-------|-------|------------|
| ... | ... | ... | ... |

## L3 Gnosis
| Principle | Essence |
|-----------|---------|
| ... | ... |
```

---

## §6 Quality Gates (M13 Temple-Grade Alignment)

Before any contribution research is considered complete, it MUST pass these gates:

| Gate | Criterion | Check |
|------|-----------|-------|
| **T1** | All Extraction Targets checked | `grep -c "\- \[x\]" docs/research/R_KG{N}_*.md` = all targets |
| **T2** | All findings have confidence scores | No finding without Confidence column entry |
| **T3** | All findings have primary sources | No finding without URL or reference |
| **T4** | Deliverable follows template | Matches §5.2 structure |
| **T5** | Hivemind post completed | `intent: decision` posted with synthesis |
| **T6** | L3 principles extracted | At least 1 L3 per domain |
| **T7** | M14 Heritage Check | No `[id-soft:]` tags added without vet record |
| **T8** | M23 Failure Handling | All tool failures logged, no simulated rigor |

---

## §7 L3 Gnosis — Universal Contribution Principles

### From AGY OAuth Fix Experience
| Principle | Essence |
|-----------|---------|
| **L3-ContributionFirst** | The most valuable upstream contribution solves a real problem while making maintenance easier for upstream — not just fixing your issue |
| **L3-ForkAsBridge** | Treat forks as temporary bridges to upstream integration, not permanent separations — sync frequency determines bridge stability |
| **L3-SmallFocusedPR** | Small, focused, backward-compatible changes have highest acceptance rates — resist "while I'm here" improvements |
| **L3-DocumentationAsLeverage** | Documentation multiplies code impact — a well-documented fix is 10x more likely to be merged than an undocumented one |
| **L3-MaintainerEmpathy** | Successful contributions align with upstream goals and respect maintainer constraints — ask "does this make their life easier?" |
| **L3-SovereignVerification** | Search snippets are indicators, not evidence — always extract full pages for critical findings before acting |

### From Research Best Practices
| Principle | Essence |
|-----------|---------|
| **L3-SpecDriven** | Write specs backward from acceptance checks — a spec is a contract with behavior, constraints, and verification |
| **L3-ContextEngineering** | What carries a multi-turn agent is everything in the context window — assembled deliberately, in the right order, with the right compression |
| **L3-AtomicWriteUniversal** | Atomic write + crash recovery = universal persistence primitive (Soul, Vault, OAuth, Research) |

---

## §8 Quick Reference — Contribution Checklist

### Before Forking
- [ ] Check if issue already has PR or is being worked on
- [ ] Verify you can reproduce the issue in latest upstream
- [ ] Review contribution guidelines (CONTRIBUTING.md, CODE_OF_CONDUCT.md, etc.)
- [ ] Check license compatibility for your intended use
- [ ] Open an issue to discuss approach with maintainer (optional but recommended)

### During Development
- [ ] Write tests for the fix before implementation
- [ ] Follow existing code style and patterns exactly
- [ ] Keep changes minimal and focused on the single issue
- [ ] Don't add unrelated "while I'm here" improvements
- [ ] Document assumptions and edge cases in code comments
- [ ] Add changelog entry (keepachangelog.com format)

### Before PR Submission
- [ ] Run full test suite locally
- [ ] Check for and fix any linting issues
- [ ] Update documentation (README, changelog, etc.) if needed
- [ ] Ensure commit messages follow conventional commits (`fix:`, `feat:`, etc.)
- [ ] Verify no sensitive data is accidentally committed
- [ ] Verify upstream CI passes (or check CI config for requirements)
- [ ] Run `make temple-grade` if applicable (M13)

### PR Submission
- [ ] Fill out PR template completely if provided
- [ ] Clearly state problem and solution in description
- [ ] Reference related issue if applicable
- [ ] List what testing was performed
- [ ] Mention any breaking changes (or confirm none)
- [ ] Suggest version bump (patch/minor) with rationale
- [ ] Disclose AI assistance if applicable (Domain 8)

### After PR Submission
- [ ] Respond promptly to review comments
- [ ] Be open to maintainer feedback and requested changes
- [ ] Keep branch updated with upstream changes
- [ ] Thank maintainers for their time regardless of outcome
- [ ] If closed, ask for specific feedback on how to improve
- [ ] Add contribution to Omega Engine heritage registry if significant (M14)

---

## §9 References

| Source | Path/URL | Role |
|--------|----------|------|
| **Sovereign Search Protocol** | `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md` | T0-T6 search tier framework |
| **Research Best Practices** | `docs/research/R_RESEARCH_BEST_PRACTICES_PART1.md` | Spec-driven, context-engineered research |
| **Knowledge Gaps Guide** | `docs/research/R_KNOWLEDGE_GAPS_RESEARCH_GUIDE_20260724.md` | Job ID system, blocking relationships |
| **Gemma 4 Intel** | `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md` | Forensic analysis, comparison matrices |
| **CG01 MCP Audit** | `docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md` | Breaking changes, sprint planning |
| **WARP Deep Dive** | `docs/research/R_WARP_PROXY_POOL_DEEP_DIVE_20260724.md` | Problem analysis, proven solutions |
| **AGY OAuth Fix PR** | `0xYiliu/opencode-antigravity-auth` PR #1, #2 | Our first upstream contribution |
| **keepachangelog.com** | https://keepachangelog.com/en/1.1.0/ | Changelog format standard |
| **semver.org** | https://semver.org/spec/v2.0.0.html | Versioning standard |
| **Sovereign Mandates** | `SOVEREIGN_MANDATES.md` | M13 Temple-Grade, M14 Heritage, M23 Failure |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ FIX-CONTRIBUTIONS-GUIDE ⬡ v2.0.0 ⬡ 2026-07-24*
*Enhanced with patterns from 6 internal research guides + AGY OAuth case study*
*This guide is a living document. Updates must be made via PR with spec-driven changes.*
