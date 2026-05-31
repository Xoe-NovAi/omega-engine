# 🔱 Phase C Preparation — Research Specification for Builder

**AP Token**: `AP-PHASE-C-RESEARCH-v1.0.0`
**Status**: ✅ COMPLETE
**Purpose**: Provide Builder with actionable specs for Phase C (Community-Ready Presentation)

---

## C1: README Rewrite — 60 Seconds to Understand Omega

### Current State
- Existing `README.md` (132 lines) is already well-structured with Quick Start, "What Makes Omega Different", and Default Council sections
- Already includes working code examples (pip install, omega talk, omega summon, omega repl)

### Research Findings (from 8 sources)

**The 10-Second Rule**: Visitors ask 3 questions in 10 seconds:
1. What is this? (One sentence)
2. Why should I care? (Why over 50 alternatives?)
3. How do I try it? (Copy-paste commands)

**Structure that works** (in order):
1. Title + one-line tagline
2. Badges (3-5 max)
3. Demo GIF/screenshot (10-second demo communicates faster than paragraphs)
4. One-paragraph pitch — what it is, who it's for, why different
5. Quick start — copy-paste install + minimal usage
6. Features — bulleted, scannable
7. Usage — common recipes with code

**Key Findings**:
- Readmes over 400 lines without TOC are punishing
- Write for tired developer at 4 PM — assume distracted
- Second-person, active voice: "Run `npm install`" > "The user should run `npm install`"
- Skip hype: "blazing fast", "revolutionary" — readers tune out
- Show, don't tell: "It's easy to use" vs a 3-line code example — example wins

### Recommendation for Omega
The current README is already 60% of the way there. Recommended updates:
1. Add a 1-line tagline at top (currently missing)
2. Add badges: License, Build status, Python version, Test count
3. Add demo GIF showing sovereign loop (from C2)
4. Trim the Pillar table (it's detailed but could be a link to docs)
5. Ensure the Quick Start works on clean machine (verify)
6. Add "Why Omega?" section comparing to alternatives (LLM APIs, local-first tools)

---

## C2: Terminal Demo (asciinema)

### Current State
- No existing demo recording

### Research Findings

**asciinema CLI**:
```bash
asciinema rec demo.cast      # Start recording
# ... do terminal things ...
exit                         # End recording
asciinema play demo.cast    # Replay locally
asciinema upload demo.cast  # Upload to asciinema.org
```

**Best Practices**:
- Use `--idle-time-limit 2` to compress idle moments (keeps viewers engaged)
- Record at 80x24 terminal size (standard)
- Use `agg` tool to convert to GIF for README embedding:
  ```bash
  agg --font-size 64 demo.cast demo.gif  # High quality
  ```

**Recommendations for Omega Demo**:
1. Sequence:
   - `omega status` — show provider detection
   - `omega talk "what is the omega engine?"` — fast response via Nova/Gemma
   - `omega summon sophia "explain gnosis"` — entity-specific response
   - `omega repl` → `/entity maat` → `exit` — interactive session
   - `omega health` — show provider status table

2. Technical: Use `--idle-time-limit 2` to keep demo engaging

3. Embedding: Use asciinema player (interactive) in docs, GIF in README

---

## C3: Changelog — Keep a Changelog Format

### Current State
- No existing CHANGELOG.md

### Research Findings

**Keep a Changelog Format** (adopted by 1000s of projects):
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Real-time notifications (in progress)

### Fixed
- Avatar not loading in dark mode
```

**Categories**: Added, Changed, Deprecated, Removed, Fixed, Security

**Key Principles**:
- Write for humans, not machines
- User-focused entries: "Fixed: sessions no longer expire unexpectedly" not "Refactored auth module"
- Include links to PRs/Issues
- Use ISO 8601 dates (YYYY-MM-DD)
- Keep Unreleased section at top, move to version on release

**Recommendation for Omega**:
Create `CHANGELOG.md` with:
- v0.1.0 (Unreleased): Phase A (Code-First Mandate), Phase B (Sovereign Loop) features
- First public release tagged

---

## C4: Documentation Pruning

### Current State
- `docs/research/` contains 63 items, many internal-only
- Research items marked with status indicators (🔲, 🔄, ✅, ⚠️)

### Research Findings

**Pruning Strategy**:
1. **Archive, don't delete**: Move stale content to `archives/`
2. **Criteria for pruning**:
   - Internal-only research (not user-facing)
   - Outdated specs replaced by implemented features
   - Duplicate content
   - Research for features not in current roadmap
3. **Keep**: User-facing docs (README, QUICKSTART, CONTRIBUTING, ARCHITECTURE)

**Omega Research Cleanup**:
| Category | Action |
|----------|--------|
| R-00 to R-19 | Keep (foundational) |
| R-20 to R-39 | Keep (Phase 1-2 roadmap) |
| R-40 to R-69 | Keep (Phase 3-4 roadmap) |
| R-70+ | Keep if tied to active stack |
| Internal discovery | Move to `docs/operations/internal-discovery/` |
| Legacy mining | Keep (reference) |
| OmniHub | Keep (cross-platform) |

**Recommendation**:
- Create `docs/archives/research_archive/` for deprecated research
- No major pruning needed — most research is still valuable
- Just organize with clear section headers

---

## C5: QUICKSTART.md — 5 Commands from Zero

### Current State
- Quick Start exists in README.md (lines 7-32)
- No separate QUICKSTART.md file

### Research Findings (from GitHub Docs, 6 sources)

**Definition**: Quickstarts get someone from zero to "it works!" in 5-15 minutes.

**Structure**:
1. **Introduction** (2-3 sentences): What you'll accomplish, prerequisites
2. **Prerequisites**: What's needed before starting
3. **Steps** (5-7 max): Opinionated, minimal, copy-pasteable
4. **Verify**: Show expected output
5. **Next Steps**: 2-3 actionable links

**Key Principles**:
- Test on clean machine — broken quickstart loses users forever
- Use project's default config so first experience matches production
- No more than 5 steps for minimal path to success
- Heavy use of code blocks for reassurance

**Recommendation for Omega**:
Create `QUICKSTART.md`:
```markdown
# Omega Engine Quickstart

Get from zero to your first AI council conversation in 5 minutes.

## What you'll build
A local AI runtime with entity memory, provider fallback, and sovereign loop.

## Prerequisites
- Python 3.12+
- 4GB RAM (8GB recommended)
- Linux/macOS (Windows via WSL)

## Step 1: Install
```bash
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
pip install -e ".[dev]"
```

## Step 2: Verify
```bash
omega --version
```

## Step 3: First conversation
```bash
omega talk "hello"
```

## Step 4: Summon an entity
```bash
omega summon sophia "what is gnosis?"
```

## Step 5: Interactive mode
```bash
omega repl
> /entity maat
> what is balance?
> /exit
```

## What's next?
- Read the full README
- Explore entity customization
- Configure cloud providers
```

---

## C6: CI/CD Pipeline Verification

### Current State
- `.github/workflows/ci.yml` exists (48 lines)
- Uses Python 3.12, 3.13 matrix
- Includes flake8 and pytest

### Research Findings

**Current Workflow Analysis**:
```yaml
# Current gaps identified:
- No dependency caching (slow builds)
- No coverage reporting
- No type checking (mypy/pyright)
- flake8 uses --exit-zero (doesn't fail on warnings)
- No security scanning
```

**Recommended Improvements**:
1. **Add pip caching** (fast builds):
   ```yaml
   - uses: actions/setup-python@v5
     with:
       python-version: "3.12"
       cache: 'pip'
   ```

2. **Add coverage** (py-cov-action or pytest-cov)

3. **Add type checking** (mypy):
   ```yaml
   - name: Type check
     run: mypy src/ --strict
   ```

4. **Fix flake8** (remove --exit-zero for critical errors):
   ```yaml
   # Keep for warnings, but fail on critical
   flake8 src tests --select=E9,F63,F7,F82 --show-source
   ```

5. **Add security** (dependabot or pip-audit)

**Recommendation**:
1. Keep current workflow functional as-is
2. Optional improvements in future releases:
   - Add pip caching (build speed)
   - Add coverage reporting (quality)
   - Add mypy type checking (reliability)

---

## Summary: Builder Action Items

| Task | Priority | Current State | Action |
|------|----------|----------------|--------|
| **C1: README** | 🔴 High | 60% done | Add tagline, badges, demo GIF, trim pillar table |
| **C2: Demo** | 🔴 High | Not started | Record asciinema, create GIF for README |
| **C3: Changelog** | 🟡 Medium | Not started | Create CHANGELOG.md with Keep a Changelog format |
| **C4: Pruning** | 🟢 Low | 90% done | Minor reorganization only |
| **C5: QUICKSTART** | 🟡 Medium | Exists in README | Extract to standalone QUICKSTART.md |
| **C6: CI/CD** | 🟢 Low | Working | Optional: add caching, coverage, mypy |

**Recommended Order**: C1 → C2 → C3 → C5 → C4 → C6

---

## Verification Checklist

After Phase C complete:
- [ ] `make test` passes (currently: 230 tests)
- [ ] `make lint` runs without errors (currently: --exit-zero, 479 warnings)
- [ ] `git clone` → `pip install -e ".[dev]"` → `make test` → `make demo` works
- [ ] README explains Omega in 60 seconds
- [ ] Demo GIF shows sovereign loop
- [ ] CHANGELOG.md follows Keep a Changelog format
- [ ] QUICKSTART.md gets users to first conversation in 5 minutes
- [ ] CI pipeline passes on GitHub Actions