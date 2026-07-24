# 🔱 Research Campaign Guide: Best Practices for Upstream Fix Contributions
**AP Token**: `AP-RESEARCH-GUIDE-FIX-CONTRIBUTIONS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_guide ⬡ 2026-07-24

---

## §0 Executive Summary

This guide provides a comprehensive framework for researching and implementing best practices when contributing fixes to upstream open source repositories, specifically for cases like the Antigravity OAuth plugin where a local fix was developed and prepared for upstream submission.

**Purpose**: Enable systematic research into contribution workflows, documentation standards, security practices, and community engagement for upstream fix contributions.

**Scope**: Applies to all research tasks in `docs/research/` and `docs/strategy/` requiring investigation of open source contribution best practices, fork maintenance strategies, and upstream collaboration patterns.

---

## §1 Core Principles — The Foundation

### 1.1 Contribution-First Mindset (Golchian 2026)
> "The most valuable open source contribution solves a real problem while making maintenance easier for upstream."

**Implementation**:
- Research contribution workflows that minimize upstream maintainer burden
- Study practices that increase PR acceptance rates
- Analyze successful fix contribution patterns from similar projects

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

**Decision Rule**:
- **High-friction contribution**: Requires significant upstream changes, breaking changes, or ongoing maintenance burden
- **Low-friction contribution**: Solves isolated problem, maintains backward compatibility, minimal ongoing burden
- **Target**: Aim for low-friction contributions that align with upstream roadmap

### 1.5 Fork-as-Bridge Model (Golchian 2026)
> "Treat your fork not as a permanent separation, but as a temporary bridge to upstream integration."

**Implementation**:
- Research strategies for keeping forks updatable
- Study rebase vs merge strategies for maintaining fork hygiene
- Analyze timing strategies for PR submission (release cycles, maintainer availability)

---

## §2 Execution Strategy (Sovereign Search Protocol)

Agents executing this guide MUST follow the T0-T6 search tier protocol:

1. **T0**: Check `.firecrawl/` cache first.
2. **T1 (`websearch`)**: Primary tool for general queries.
3. **T2 (`webfetch`)**: Deep extraction of specific documentation pages found in T1.
4. **T3 (`searxng_searxng_search`)**: Semantic/neural search refinement.
5. **T4 (`omega-hub_library_web_search`)**: For highly technical, academic, or GitHub-specific pattern hunting.
6. **T5 (`firecrawl_firecrawl_scrape`)**: Full-page scrape for complex docs.
7. **T6 (`sieve research`)**: Full research pipeline (T1→T2→T3), zero API keys needed.

**Hard-Stop Rule (M23)**: If all tools fail → `[TOOL-CHAIN-COLLAPSE]`. NO simulated rigor.

**Search Directives**:
- Use `site:` operators to restrict results to authoritative domains (e.g., `site:github.com`, `site:opensource.org`).
- Use exact match quotes `""` for specific error codes, headers, or library functions.
- **Temporal Mandate**: All queries MUST include "2026" or "latest".
- If primary queries yield SEO spam, immediately pivot to the provided Fallback Queries.

---

## §3 Research Domains & Search Directives:
- Use `site:` operators to restrict results to authoritative domains (e.g., `site:github.com`, `site:opensource.org`).
- Use exact match quotes `""` for specific error codes, headers, or library functions.
- **Temporal Mandate**: All queries MUST include "2026" or "latest".
- If primary queries yield SEO spam, immediately pivot to the provided Fallback Queries.

---

## §3 Research Domains & Search Vectors

### 📚 Domain 1: Contribution Workflow Best Practices
**Technical Context**: Understanding the optimal fork → PR → merge lifecycle for fix contributions.

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

### 🔐 Domain 2: Security Practices for Auth Plugins
**Technical Context**: Ensuring OAuth token handling follows security best practices to prevent credential leakage.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **OAuth Token Storage** | `site:owasp.org "OAuth Token Storage Cheat Sheet" 2026` | `site:oauth.net "security best practices" token handling` |
| **Credential Encryption** | `site:github.com "awesome-secret-management" 2026` | `csrc.nist.gov "publications" key management` |
| **Memory Safety** | `site:github.com "secure zero memory" nodejs typescript 2026` | `owasp "secrets management in memory" best practices` |
| **Logging Sanitization** | `site:stackoverflow.com "how to prevent logging passwords" 2026` | ` "sanitize logs" credentials tokens api keys` |
| **Dependency Scanning** | `site:snyk.io "blog" "typescript nodejs security" 2026` | ` "npm audit" "github dependabot" best practices` |

**Extraction Targets**:
- [ ] Recommended encryption algorithms for token at rest (Argon2id/scrypt/bcrypt parameters)
- [ ] Whether to encrypt tokens in memory or only at rest
- [ ] Standard patterns for redacting sensitive data from logs
- [ ] Frequency of dependency vulnerability scanning
- [ ] Responsible disclosure process for security findings in OSS

### 📖 Domain 3: Documentation Standards for Fix Contributions
**Technical Context**: Creating documentation that helps upstream maintainers understand, verify, and merge the fix.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **PR Description Templates** | `site:github.com "pull request template" bug fix example 2026` | ` "contributing.md" "reporting bugs" template` |
| **Changelog Entries** | `site:keepachangelog.com "en" "added" "changed" "deprecated" 2026` | ` "conventional commits" "fix:" prefix examples` |
| **README Updates** | `site:github.com "readme" "best practices" "contributing section" 2026` | ` "opensource guide" "documentation" tutorial` |
| **Issue Templates** | `site:github.com "issue template" "bug report" "feature request" 2026` | ` "github community" "best practices" issue templates` |
| **Testing Documentation** | `site:dev.to "how to document tests" "open source project" 2026` | ` "writing test documentation" "guide" examples` |

**Extraction Targets**:
- [ ] Essential elements of a good PR description (problem, solution, testing)
- [ ] Standard changelog format for patch/minor/major releases
- [ ] Whether to update README with fix details or keep in changelog only
- [ ] Recommended issue templates for bug reports vs feature requests
- [ ] How to document test procedures for verification

### 👥 Domain 4: Community & Maintainer Engagement
**Technical Context**: Building positive relationships with upstream maintainers to increase PR acceptance.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **First Contributor Guide** | `site:github.com "open source guide" "first contributions" 2026` | ` "first timers only" "up for grabs" labels` |
| **Maintainer Communication** | `site:opensource.com "how to communicate with maintainers" 2026` | ` "stackoverflow" "etiquette" "open source" questions` |
| **Handling Feedback** | `site:github.com "responding to code review" "best practices" 2026` | ` "software engineering" "code review" "tips" techniques` |
| **Building Reputation** | `site:dev.to "open source reputation" "contributor" "maintainer trust" 2026` | ` "how to become" "trusted contributor" "project" guide` |
| **License Compliance** | `site:choosealicense.com "licenses" "mit" "apache" "gpl" comparison 2026` | ` "fsf" "licensing" "compliance" checklist` |

**Extraction Targets**:
- [ ] Best practices for first-time contributor introductions
- [ ] Tone and timing for responding to review comments
- [ ] Strategies for addressing "won't fix" or "not a priority" feedback
- [ ] How to demonstrate ongoing commitment beyond single PR
- [ ] License compatibility considerations for forked projects

### ⚙️ Domain 5: Technical Implementation Best Practices
**Technical Context**: Ensuring the technical implementation follows standards that upstream will accept.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **TypeScript Best Practices** | `site:typescriptlang.org "docs" "handbook" "declaration files" 2026` | ` "eslint" "prettier" "config" "recommended" 2026` |
| **Node.js Package Publishing** | `site:docs.npmjs.com "cli" "commands" "npm publish" 2026` | ` "semantic versioning" "major minor patch" guide` |
| **CI/CD for OSS Projects** | `site:github.com "features" "actions" "guides" "continuous integration" 2026` | ` "gitlab ci" "circleci" "best practices" yaml` |
| **Semantic Versioning** | `site:semver.org "spec" "version" "2.0.0" 2026` | ` "github blog" "releasing software" "best practices" ` |
| **Backward Compatibility** | `site:martinfowler.com "articles" "backwardscompatibility" 2026` | ` "api evolution" "backward incompatible changes" guide` |

**Extraction Targets**:
- [ ] Recommended TypeScript strictness levels for libraries
- [ ] Version bump strategy for bug fixes (patch vs minor)
- [ ] Essential CI checks (lint, test, build, security scan)
- [ ] How to determine if a change is breaking vs non-breaking
- [ ] Best practices for maintaining backward compatibility

### 🏛️ Domain 6: Legal & Governance Considerations
**Technical Context**: Understanding the legal framework around forks, contributions, and licensing.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Fork Licensing** | `site:github.com "licensing" "forked repository" "same license" 2026` | ` "choosealicense.com" "faq" "forking" implications` |
| **Contributor Agreements** | `site:github.com "contributor license agreement" "cla" 2026` | ` "apache" "icl" "individual contributor license" explanation` |
| **Patent Clauses** | `site: apache.org "licenses" "license-faq.html" #patent-license 2026` | ` "gplv3" "patent retaliation" "clause" explanation` |
| **Trademark Considerations** | `site:uspto.gov "trademark" "basics" "what is" 2026` | ` "linux foundation" "trademark policy" "guidelines" ` |
| **Export Controls** | `site:bis.doc.gov "licensing" "encryption" "items" 2026` | ` " Wassenaar Arrangement" "cryptography" "notice" ` |

**Extraction Targets**:
- [ ] Whether forks must maintain same license as upstream
- [ ] Requirements for Contributor License Agreements (CLAs)
- [ ] Patent grant implications of different open source licenses
- [ ] Trademark usage rules for project names/logos
- [ ] Export control considerations for cryptographic software

---

## §4 Synthesis & Reporting Protocol

1. **Execute Sequentially**: Complete each domain before moving to the next to maintain focus.
2. **Log Verbatim**: Record exact URLs, code snippets, and standard references.
3. **Distill**: Translate raw findings into actionable technical decisions for contribution strategy.
4. **Update Tickets**: Inject verified patterns directly into contribution planning documents.
5. **Gate**: Proceed to implementation ONLY when all Extraction Targets for a domain are checked.
6. **Hivemind Post**: Post synthesis to Hivemind with `intent: decision` for team awareness.

---

## §5 Quick Reference — Essential Best Practices Checklist

### Before Forking
- [ ] Check if issue already has PR or is being worked on
- [ ] Verify you can reproduce the issue in latest upstream
- [ ] Review contribution guidelines (CONTRIBUTING.md, etc.)
- [ ] Check license compatibility for your intended use

### During Development
- [ ] Write tests for the fix before implementation
- [ ] Follow existing code style and patterns exactly
- [ ] Keep changes minimal and focused on the single issue
- [ ] Don't add unrelated "while I'm here" improvements
- [ ] Document assumptions and edge cases in code comments

### Before PR Submission
- [ ] Run full test suite locally
- [ ] Check for and fix any linting issues
- [ ] Update documentation (README, changelog, etc.) if needed
- [ ] Ensure commit messages follow conventional commits
- [ ] Verify no sensitive data is accidentally committed

### PR Submission
- [ ] Fill out PR template completely if provided
- [ ] Clearly state problem and solution in description
- [ ] Reference related issue if applicable
- [ ] List what testing was performed
- [ ] Mention any breaking changes (or confirm none)

### After PR Submission
- [ ] Respond promptly to review comments
- [ ] Be open to maintainer feedback and requested changes
- [ ] Keep branch updated with upstream changes
- [ ] Thank maintainers for their time regardless of outcome
- [ ] If closed, ask for specific feedback on how to improve

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ FIX-CONTRIBUTIONS-GUIDE ⬡ 2026*