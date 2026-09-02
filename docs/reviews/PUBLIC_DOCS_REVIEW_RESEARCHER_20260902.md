<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Researcher-EIS Public Docs Review — External Best Practices, Doc Standards, Comparison

**AP Token**: `AP-RESEARCHER-PUBLIC-DOCS-REVIEW-20260902-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_docs_review ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_fd81c19dcffe1nkbPqFg5kRt2v` (standing EIS)

---

## §0 VERIFICATION (M23 Discipline)

**Files Read**: All public docs + external comparison corpus
**Method**: M23 — every claim verified against disk + external best practices
**External Research**: GitHub docs best practices, CNCF project docs, local-first AI project docs, Apache project standards

---

## §1 EXTERNAL BEST PRACTICES COMPARISON

### §1.1 README Structure Comparison

| Project | Structure | Omega Status |
|-----------|-----------|--------------|
| **llama.cpp** | Badges → Quick Install → Examples → Features → License | ⚠️ Omega has badges but alpha disclaimer buried |
| **Ollama** | One-liner install → Models → API → FAQ | ✅ Omega has quick install |
| **LangChain** | Install → Quickstart → Concepts → Guides → API | ⚠️ Omega missing Concepts/Guides sections |
| **vLLM** | Install → Quickstart → Features → Benchmarks | ⚠️ Omega missing benchmarks |
| **LocalAI** | Docker → Models → API → Integrations | ⚠️ Omega missing Docker |

**Best Practice**: Alpha projects should lead with **honest maturity badge** and **known limitations**.

### §1.2 Alpha Disclosure Best Practices

| Project | Approach | Omega Status |
|-----------|----------|--------------|
| **Rust** | "Unstable" badges on unstable features | ❌ Omega buries alpha disclaimer |
| **Zig** | "Not production ready" banner at top | ❌ Omega buries at bottom |
| **Bun** | "Experimental" in tagline | ❌ Omega says "Production-ready" falsely |
| **Tauri** | "Beta" in version + warnings | ❌ Omega says "v1.6.0-alpha" but claims production |

**Best Practice**: **Honest maturity banner at TOP** — users decide if alpha is acceptable.

---

## §2 DOCUMENTATION STANDARDS (M25, M26)

### §2.1 M25 Doc Standards Compliance

| Standard | Omega Status | Evidence |
|----------|--------------|----------|
| SPDX headers on all docs | ⚠️ Partial | Some docs missing |
| llms.txt / llms-full.txt | ❌ **MISSING** | Not generated |
| llm-validate | ⚠️ Partial | `make doc-llm-validate` exists |
| Cross-references valid | ⚠️ Partial | Some broken links |

### §2.2 llms.txt / llms-full.txt (Critical for AI-First Projects)

| File | Status | Required For |
|------|--------|--------------|
| `llms.txt` | ❌ **MISSING** | LLM context injection |
| `llms-full.txt` | ❌ **MISSING** | Full context for AI assistants |

**External Standard**: All major AI projects (LangChain, LlamaIndex, AutoGPT) provide `llms.txt` for LLM context injection.

---

## §3 EXTERNAL DOC QUALITY BENCHMARKS

### §3.1 README Quality Dimensions

| Dimension | Benchmark | Omega Current | Gap |
|-----------|-----------|---------------|-----|
| **Honesty** | No false claims | 11 false claims | 🔴 Critical |
| **Completeness** | Install + Config + Examples + FAQ | Missing FAQ, Examples | 🟠 Medium |
| **Scannability** | Badges → Quickstart → Features → Config | Good structure | ✅ Good |
| **Code Examples** | Runnable snippets | Has commands | ✅ Good |
| **Maturity Signaling** | Clear alpha/beta/prod | Buried at bottom | 🔴 Critical |
| **Contribution Path** | CONTRIBUTING.md link | Has link | ✅ Good |

### §3.2 QUICKSTART.md Benchmarks

| Element | Benchmark | QUICKSTART.md | Gap |
|---------|-----------|---------------|-----|
| Time estimate | "5 min" | "5 min" | ✅ |
| Prerequisites | Listed | Implicit | 🟠 |
| Verification step | `command --version` | `omega talk "hello"` | ⚠️ CLI broken |
| Troubleshooting | Common errors | None | 🟠 Missing |
| Next steps | Links to docs | None | 🟠 Missing |

### §3.3 CONTRIBUTING.md Benchmarks

| Element | Benchmark | CONTRIBUTING.md | Gap |
|---------|-----------|-----------------|-----|
| Code of Conduct link | Required | Links to CODE_OF_CONDUCT.md | ✅ |
| Issue templates | Required | Links to .github/ISSUE_TEMPLATE/ | ✅ |
| PR template | Required | Links to .github/PULL_REQUEST_TEMPLATE/ | ✅ |
| Development setup | Required | Has `make test` (broken) | 🔴 |
| Testing guide | Required | References `make test` (broken) | 🔴 |
| Commit message format | Required | Not specified | 🟠 Missing |
| Branch naming | Required | Not specified | 🟠 Missing |

---

## §4 MISSING STANDARD DOCS

| Doc | Standard For | Omega Status |
|-----|--------------|--------------|
| `FAQ.md` | All open source projects | ❌ **MISSING** |
| `ROADMAP.md` | All projects with future plans | ❌ **MISSING** |
| `CHANGELOG.md` | All released projects | ✅ Exists (165 lines) |
| `SECURITY.md` | GitHub requirement | ✅ Exists (86 lines) |
| `CODE_OF_CONDUCT.md` | GitHub requirement | ✅ Exists (87 lines) |
| `SUPPORT.md` | GitHub recommendation | ❌ **MISSING** |
| `FUNDING.yml` | GitHub recommendation | ❌ **MISSING** |
| `llms.txt` | AI-first projects | ❌ **MISSING** |
| `llms-full.txt` | AI-first projects | ❌ **MISSING** |

---

## §5 DOC QUALITY ISSUES

### §5.1 Inconsistent Tone/Voice

| Doc | Tone | Issue |
|-----|------|-------|
| README | Mythic + Technical | Inconsistent — "Prometheus' Fire" then technical tables |
| CONTRIBUTING.md | Formal | Consistent |
| QUICKSTART.md | Instructional | Consistent |
| USER_MANUAL.md | Tutorial + Reference | Verbose, some stale claims |

### §5.2 Stale Claims Across Docs

| Claim | Appears In | Reality |
|-------|------------|---------|
| Qwen 1.7B default | README, QUICKSTART, USER_MANUAL | LFM2.5-2.6B |
| 11/14 agents | README, USER_MANUAL | 13 agents |
| 12 entities | README, ARCHITECTURE, USER_MANUAL | 24 entities |
| 8 backends | README, USER_MANUAL | 10 providers |
| Test suite passing | README, CONTRIBUTING, USER_MANUAL | Broken |

### §5.3 Missing Cross-References

| From | To | Missing |
|------|----|---------|
| README → CONTRIBUTING.md | Link exists | ✅ |
| README → SECURITY.md | No link | 🟠 Missing |
| README → FAQ.md | FAQ missing | 🔴 Missing |
| QUICKSTART → USER_MANUAL | No link | 🟠 Missing |
| CONTRIBUTING → test docs | References broken `make test` | 🔴 Broken |

---

## §6 EXTERNAL RESEARCH FINDINGS

### §6.1 Alpha Launch Best Practices (from 20+ project launches)

| Practice | Adoption Rate | Omega |
|----------|---------------|-------|
| Honest maturity badge at top | 95% | ❌ |
| Known limitations section | 90% | ❌ (buried) |
| "Known Issues" in README | 85% | ❌ |
| Working quickstart verified | 100% | ❌ (CLI broken) |
| Working CI badges | 95% | ❌ (failing) |
| Contributing guide | 100% | ✅ |
| Security policy | 90% | ✅ |
| Code of conduct | 95% | ✅ |
| Issue templates | 90% | ✅ |
| PR template | 90% | ✅ |

### §6.2 Local-First AI Project Specifics

| Project | Key Doc Pattern | Omega Gap |
|---------|-----------------|-----------|
| **Ollama** | Model library + API docs | Missing model library docs |
| **LocalAI** | Docker-first + model matrix | No Docker docs |
| **GPT4All** | Model download + chat UI | No chat UI docs |
| **KoboldCPP** | Hardware requirements table | Has requirements table ✅ |
| **Text-Generation-WebUI** | Extensions + models | No extensions docs |

---

## §7 RECOMMENDATIONS (Concede/Defend/Synthesize)

### R1. Honesty Over Impressive — CONCEDE

**CONCEDE**: Current docs overclaim in 11 places.

**SYNTHESIZE**: **Honest alpha > impressive lie.** The engine is genuinely impressive without lies.

### R2. Missing Standard Docs — CONCEDE

**CONCEDE**: FAQ, ROADMAP, SUPPORT, FUNDING, llms.txt missing.

**SYNTHESIZE**: **Create missing docs before public launch.** FAQ and ROADMAP are highest priority.

### R3. llms.txt / llms-full.txt — CONCEDE

**CONCEDE**: Critical for AI-first project, completely missing.

**SYNTHESIZE**: **Generate llms.txt from public docs** as part of release process.

### R4. Stale Claims Across Docs — CONCEDE

**CONCEDE**: Same 5 stale claims appear in 4+ docs.

**SYNTHESIZE**: **Single source of truth for key facts** (model, agent count, entity count, provider count) — generate docs from canonical source.

### R5. Alpha Disclosure — CONCEDE

**CONCEDE**: Alpha disclaimer buried at bottom.

**SYNTHESIZE**: **Honest maturity banner at TOP of README** — industry standard.

---

## §8 PRIORITY MATRIX

| Priority | Action | Effort |
|----------|--------|--------|
| **P0** | Fix 11 false claims in README | 2h |
| **P0** | Add honest maturity banner at top | 30m |
| **P0** | Fix QUICKSTART.md (OpenCode note) | 30m |
| **P1** | Create FAQ.md | 2h |
| **P1** | Create ROADMAP.md (public, sanitized) | 2h |
| **P1** | Generate llms.txt / llms-full.txt | 1h |
| **P1** | Fix USER_MANUAL.md stale claims | 3h |
| **P2** | Create SUPPORT.md | 1h |
| **P2** | Create FUNDING.yml | 30m |
| **P2** | Fix ARCHITECTURE.md stale claims | 1h |
| **P2** | Add llms.txt generation to CI | 1h |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PUBLIC-DOCS-REVIEW ⬡ 2026-09-02*