# 🔱 Omega Engine — GitHub Integration Strategy
# ⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ STRATEGY
**AP Token**: `AP-GITHUB-INTEGRATION-v1.0.0`
**Date**: 2026-06-21
**Decision**: D-kal-163 — GitHub as Sovereign Memory Layer
**Status**: RATIFIED — Awaiting Phase 0 execution
**Baseline**: 440 tests passing · 104 source files · 22 Sovereign Mandates

---

## §0 Decision Record — D-kal-163

### The Verdict

GitHub is NOT a new agent behavior. It is a **tool** — a sovereign memory layer that
the existing 11-agent fleet uses via a shared Knowledge Base and the official
`github/github-mcp-server` (31K stars, 57+ tools, Docker container).

### What We Rejected

| Option | Rejected By | Reason |
|--------|-------------|--------|
| `@github` subagent | Kali (D-kal-163) | "GitHub is a tool, not a behavior. A KB is the right abstraction." |
| Custom MCP server | Doom Guy | "The official server has 31K stars. Don't rewrite what works." |
| No GitHub integration | Lilith | "We need version control intelligence, not just git commands." |

### What We Adopted

1. **Official `github/github-mcp-server`** — Docker container, 57+ tools, M8-audited
2. **Omega Hub wrapper** — `mcp_servers/omega_hub/github_tools.py` (~200 lines) with Omega-specific intelligence
3. **Shared Knowledge Base** — `data/knowledge/github-protocol.md` (10 sections, fleet-wide)
4. **Hivemind-GitHub bridge** — PR merges trigger Hivemind events
5. **Heritage-as-Issues** — vet records auto-create GitHub Issues

---

## §1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  11-Agent Fleet (Kali, Ma'at, Lilith, Doom Guy, ...)           │
│  loads KB → uses Hub wrapper → delegates to official MCP server │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Omega Hub   │
                    │  github_tools│  (~200 lines, Omega intelligence)
                    │  .py         │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Official    │
                    │  github/     │  (Docker container, 57+ tools)
                    │  github-mcp  │
                    │  -server     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  GitHub API  │  (via PAT, entity-attributed)
                    └─────────────┘
```

### Component Responsibilities

| Component | Location | Lines | Purpose |
|-----------|----------|-------|---------|
| **Knowledge Base** | `data/knowledge/github-protocol.md` | ~300 | Fleet-wide protocol reference (10 sections) |
| **Hub Wrapper** | `mcp_servers/omega_hub/github_tools.py` | ~200 | Omega-specific intelligence on top of official server |
| **Official Server** | `github/github-mcp-server` (Docker) | N/A | 57+ raw GitHub API tools |
| **Account Config** | `config/github_accounts.yaml` | ~50 | 2 GitHub account PATs + rotation rules |
| **Hivemind Bridge** | `mcp_servers/omega_hub/github_bridge.py` | ~100 | PR merge → Hivemind event propagation |

---

## §2 The 5-Phase Execution Plan

| Phase | Owner | What | Gate | Effort |
|-------|-------|------|------|--------|
| **0** | Ma'at (P3) | Git index cleanup — remove 617 runtime files from tracking | `data/` tracked < 70 | 2 hr |
| **1** | Lilith (P1) | Install official server + M8 audit (does it phone home?) | Clean audit report | 4 hr |
| **2** | Kali (P9) | Omega Hub wrapper + Hivemind-GitHub bridge | PR merge → Hivemind fires | 6 hr |
| **3** | Ma'at (P5) | CI/CD hardening — Temple-Grade gates in GitHub Actions | `make temple-grade` in CI | 4 hr |
| **4** | Doom Guy | Heritage-as-Issues — vet records auto-create GitHub Issues | Vet → Issue automated | 3 hr |
| **5** | Lilith (P4) | Copilot rotation across 2 GitHub accounts | Quota tested | 2 hr |

### Phase Dependencies

```
Phase 0 (cleanup) → Phase 1 (install) → Phase 2 (wrapper + bridge)
                                              ↓
                                         Phase 3 (CI/CD)
                                              ↓
                                         Phase 4 (heritage)
                                              ↓
                                         Phase 5 (accounts)
```

**Phase 0 is the blocker.** 617 runtime files tracked in git must be removed before
building on this foundation. Every subsequent phase depends on a clean git index.
Gate threshold: < 70 tracked files in `data/` (revised from < 50 per council finding B1).

---

## §3 The 7 Non-Negotiables

| # | Rule | Enforcement | Owner |
|---|------|-------------|-------|
| 1 | **M8 audit first** — verify official server doesn't phone home | Network capture + strace before install | Lilith (Phase 1) |
| 2 | **M7 compliance** — local Docker only, no cloud relays | Docker compose with `network_mode: host` or bridge, no external endpoints | Lilith (Phase 1) |
| 3 | **Git cleanup is Phase 0** — 617 runtime files must be removed | `git rm --cached` + .gitignore update, verify `data/` tracked < 70 | Ma'at (Phase 0) |
| 4 | **Entity-attributed commits** — `[entity: kali]` trailers | `git commit --author` or `Signed-off-by:` trailer convention | All agents (Phase 2) |
| 5 | **Hivemind-GitHub bridge** — PR merges must trigger Hivemind events | GitHub webhook → local listener → `hivemind_post_context()` | Kali (Phase 2) |
| 6 | **Heritage-as-Issues** — vet records auto-create GitHub Issues | Vet pipeline → GitHub API → Issue creation with vet metadata | Doom Guy (Phase 4) |
| 7 | **PAT secret management** — tokens stored in encrypted file, not plaintext | 0400 perms on `config/github_accounts.yaml`, tokens never logged, excluded from git | Lilith (Phase 1) |

---

## §4 The GitHub KB Structure (10 Sections)

The shared Knowledge Base at `data/knowledge/github-protocol.md` contains:

| # | Section | Purpose | Key Content |
|---|---------|---------|-------------|
| 1 | **Commit Message Format** | Standardize all commits | Prefix convention (`feat:`, `fix:`, `docs:`, etc.) + entity trailer |
| 2 | **Heritage Tag Protocol** | `[id-soft:]` inline tags | Game codes, format spec, enforcement via `make heritage-map` |
| 3 | **Temple-Grade Checklist** | T1-T11 gates for PRs | Must-pass gates before merge |
| 4 | **Entity Attribution** | Per-agent identity in commits | `git commit --author="Entity <entity@omega.engine>"` |
| 5 | **Branch Naming Conventions** | Structured branch names | `feat/{entity}/{task}`, `fix/{entity}/{bug}`, `docs/{entity}/{topic}` |
| 6 | **Account Rotation** | 2 GitHub accounts | Account purposes, rate limits, rotation rules |
| 7 | **PR Template** | Standardized pull requests | Checklist: tests, mandates, heritage tags, temple-grade |
| 8 | **Merge Strategy** | How PRs get merged | Squash merge default, no fast-forward on main |
| 9 | **PR Review Protocol** | Who reviews what | Kali reviews all, domain experts review domain PRs |
| 10 | **CI Failure Protocol** | What happens when CI fails | Block merge, notify Hivemind, auto-retry once |

---

## §5 Entity Attribution Protocol

### The Problem
One GitHub PAT, 11 agents. How do we preserve per-agent identity?

### The Solution: Git Trailers

Every commit includes an entity trailer in the commit message:

```
feat(memory): add tiered eviction policy

Implement hardware-adaptive eviction for MemoryStore hot tier
based on available RAM signals.

Signed-off-by: Kali <kali@omega.engine>
[entity: kali]
[mandate: M7, M8]
[temple-grade: T1-T10 PASS]
```

### Implementation

| Method | When | Example |
|--------|------|---------|
| `git commit --author` | CLI commits | `git commit --author="Kali <kali@omega.engine>"` |
| `Signed-off-by:` trailer | PR merges | Standard DCO format |
| `[entity: name]` custom trailer | All commits | Machine-readable entity attribution |
| `Co-authored-by:` | Multi-agent work | `Co-authored-by: Doom Guy <doom_guy@omega.engine>` |

### Account Mapping

**Model**: 2 accounts for the entire 11-agent fleet (not one per entity).
All agents share both accounts; the primary assignment determines which account
is used for routine operations and which is the fallback.

| Account | Primary Entity | Purpose | Fallback For |
|---------|---------------|---------|-------------|
| `xoe.nova.ai` | Kali / System | Primary development, releases, CI/CD | All agents |
| `arcana.novai` | Ma'at | Build-side governance, heritage vetting | All agents |

---

## §6 M8 Audit Requirements (Phase 1 Gate)

Before installing `github/github-mcp-server`, Lilith MUST complete:

### 6.1 Systematic Audit Methodology

The M8 audit follows a multi-layer verification protocol. Each layer targets a different
attack surface — network, binary, filesystem, and runtime.

**Layer 1: Image Layer Inspection** (before any code execution)
```bash
# Inspect Docker image layers for embedded telemetry agents
docker pull github/github-mcp-server:latest
docker history --no-trunc github/github-mcp-server:latest
# Check for: datadog, segment, posthog, newrelic, telemetry, analytics in layer history

# Inspect filesystem for telemetry artifacts
docker run --rm -it --entrypoint sh github/github-mcp-server:latest \
  -c "find / -type f -name '*.js' -o -name '*.py' -o -name '*.json' | head -100"
```

**Layer 2: Static Binary Analysis** (before runtime)
```bash
# Check for telemetry imports in bundled source
docker run --rm -it --entrypoint /bin/bash github/github-mcp-server:latest \
  -c "grep -rn 'segment\|posthog\|datadog\|newrelic\|amplitude\|analytics' /app/ || echo 'CLEAN'"
```

**Layer 3: Network Capture** (during isolated runtime)
```bash
# Run official server in isolated Docker network with packet capture
docker network create github-audit --internal
docker run --rm -d --name github-mcp-audit \
  --network github-audit \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<test-token> \
  github/github-mcp-server:latest

# Capture all traffic from the isolated network
docker run --rm -it --network github-audit \
  nicolaka/netshoot tcpdump -i any -w /tmp/github-mcp-traffic.pcap &
```

**Layer 4: DNS Resolution Audit** (verify all resolved hosts)
```bash
# After test run, analyze DNS queries
tcpdump -r /tmp/github-mcp-traffic.pcap -n 'udp port 53' 2>/dev/null \
  | grep -oP 'A\?\s+\K[^\s]+' | sort -u
# Expected: only github.com, api.github.com, *.githubusercontent.com
```

### 6.2 Telemetry Checklist

| Check | Pass Criteria | Fail Action | Methodology |
|-------|--------------|-------------|-------------|
| **Image layers** | No telemetry agents in layer history | REJECT — do not install | `docker history` + layer inspection |
| **Static imports** | No segment/posthog/datadog/analytics in source | REJECT — do not install | `grep -rn` in container filesystem |
| **Outbound DNS** | Only github.com/api.github.com | BLOCK — add to firewall | tcpdump DNS analysis |
| **Outbound HTTP** | Only to GitHub API endpoints | BLOCK — add to firewall | tcpdump HTTP/HTTPS analysis |
| **Analytics imports** | No telemetry SDK calls in bundled JS/Python | REJECT — do not install | Layer 2 static binary analysis |
| **Phone-home endpoints** | No non-GitHub URLs in binary/source | REJECT — do not install | Layer 1 + Layer 2 combined |
| **Data exfiltration** | No user data sent anywhere except GitHub API | REJECT — do not install | All 4 layers combined |
| **Docker image layers** | No pre-installed telemetry agents | REJECT — do not install | Layer 1 inspection |
| **Runtime behavior** | No unexpected connections during tool execution | INVESTIGATE — document | Layer 3 network capture |

### 6.3 M8 Compliance Decision

| Outcome | Action |
|---------|--------|
| **CLEAN** — No phone-home detected | Proceed to Phase 2 |
| **SUSPECT** — Unexplained outbound traffic | Investigate, document, re-audit |
| **VIOLATION** — Telemetry detected | REJECT official server, build custom thin wrapper |

---

## §7 Hivemind-GitHub Bridge (Phase 2)

### The Flow

```
GitHub PR Merged
       │
       ▼
GitHub Webhook (local listener)
       │
       ▼
bridge.py parses event
       │
       ▼
hivemind_post_context(
    channel="github",
    entity="bridge",
    model="system",
    task_current="PR #{number} merged: {title}",
    focus_chain=[...],
    decisions=[{pr: number, author: entity, merged_by: actor}],
    continuation="CI pipeline triggered"
)
       │
       ▼
All active agents see PR merge in awareness feed
```

### Bridge Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `github_bridge.py` | Parse GitHub webhook events | `mcp_servers/omega_hub/github_bridge.py` |
| `/github/webhook` | Receive webhook POST | Omega Hub route |
| Event formatter | Convert webhook JSON to Hivemind context | Inline in bridge |
| Entity mapper | Map GitHub user → Omega entity | `config/github_accounts.yaml` |

---

## §8 Heritage-as-Issues Automation (Phase 4)

### The Flow

```
Doom Guy runs make heritage-vet
       │
       ▼
Vet pipeline produces vet record
       │
       ▼
bridge.py checks vet score
       │
       ├── score >= 7 → Auto-create GitHub Issue
       │                 Title: "[HERITAGE] {concept} — APPROVED (score/10)"
       │                 Labels: heritage, approved, {game-code}
       │                 Body: Full vet record + source citations
       │
       └── score < 7 → Auto-create GitHub Issue
                        Title: "[HERITAGE] {concept} — REJECTED (score/10)"
                        Labels: heritage, rejected, {game-code}
                        Body: Rejection rationale + lessons learned
```

### Issue Template

```markdown
## Heritage Vetting Record — {concept_name}

**Game**: {game} ({year})
**Score**: {score}/10
**Decision**: {APPROVED|REJECTED|DEFERRED}
**Vetted by**: Doom Guy + {reviewer}
**Date**: {date}

### Original Pattern
{id Software original description}

### Omega Adaptation
{how we evolved it}

### Source Citations
{links to actual source code verified}

### Mandate Compliance
- M7: {pass/fail}
- M8: {pass/fail}
- M14: {pass/fail — Heritage Vetting}

---
Auto-created by Heritage-as-Issues pipeline (D-kal-163, Phase 4)
```

---

## §9 Mandate Compliance Matrix

| Mandate | GitHub Integration Compliance | Status |
|---------|------------------------------|--------|
| **M1** AnyIO | Bridge uses `anyio.to_thread.run_sync` for blocking I/O | ✅ Required |
| **M2** Engine-Stack Firewall | GitHub KB in `data/knowledge/` (stack), not in `src/omega/` (core) | ✅ Compliant |
| **M3** Iris Constant | GitHub integration bypasses Iris entirely | ✅ Compliant |
| **M4** Sequentiality | 5-phase plan with gates: Plan → Verify → Execute | ✅ Enforced |
| **M5** Gnosis Preservation | PR merges → Hivemind context → session knowledge | ✅ Enhanced |
| **M6** Podman Sovereignty | Official server runs in Docker with `UserNS=keep-id` | ✅ Required |
| **M7** Local-First | Docker container runs locally, no cloud relays | ✅ Gate: Phase 1 |
| **M8** Zero Telemetry | M8 audit required before install (Phase 1 gate) | ✅ Gate: Phase 1 |
| **M9** Error Integrity | Bridge errors typed and traced, no bare except | ✅ Required |
| **M10** Fleet Integrity | No new agents — GitHub is a tool, not a behavior | ✅ Compliant |
| **M11** Soul Integrity | PR context feeds into Hivemind → soul distillation | ✅ Enhanced |
| **M12** Queue Integrity | Webhook events result in terminal states (processed/failed) | ✅ Required |
| **M13** Temple-Grade | Phase 3: CI/CD gates enforce T1-T11 in GitHub Actions | ✅ Phase 3 |
| **M14** Heritage Vetting | Phase 4: Heritage-as-Issues auto-creates vet records | ✅ Phase 4 |
| **M15** Sovereign Continuity | GitHub as backup memory layer (PRs, issues, discussions) | ✅ Enhanced |
| **M16** Modularization | Hub wrapper is thin (~200 lines), delegates to official server | ✅ Compliant |
| **M17** Cognitive Integrity | PR reviews include mandate compliance checks | ✅ Enhanced |
| **M18** Token Efficiency | KB is concise (10 sections, ~300 lines), not bloated | ✅ Compliant |
| **M19** Adversarial Alchemy | 617-file mess becomes clean foundation (weakness → strength) | ✅ Applied |
| **M20** SomaticState | Not applicable to GitHub integration | N/A |
| **M21** Gate Integrity | Phase 2: Contract tests for bridge API boundaries before live deployment | ✅ Phase 2 |
| **M22** Response Provenance | PR merge events carry full provenance (actor, time, SHA) | ✅ Compliant |

---

## §10 Files to Create/Modify

### New Files

| File | Purpose | Phase | Est. Lines |
|------|---------|-------|-----------|
| `docs/strategy/GITHUB_INTEGRATION_PLAN.md` | This document | 0 | ~400 |
| `data/knowledge/github-protocol.md` | Fleet-wide GitHub KB (10 sections) | 2 | ~300 |
| `mcp_servers/omega_hub/github_tools.py` | Omega Hub wrapper for GitHub | 2 | ~200 |
| `mcp_servers/omega_hub/github_bridge.py` | Hivemind-GitHub bridge | 2 | ~100 |
| `config/github_accounts.yaml` | 2 GitHub account PATs + rotation | 5 | ~50 |
| `tests/test_github_bridge.py` | Bridge contract tests | 2 | ~150 |
| `.github/workflows/temple-grade.yml` | CI/CD with Temple-Grade gates | 3 | ~100 |

### Modified Files

| File | Change | Phase |
|------|--------|-------|
| `.gitignore` | Add `data/` runtime files to ignore list | 0 |
| `mcp_servers/omega_hub/server.py` | Register github_tools + github_bridge | 2 |
| `mcp_servers/omega_hub/tools.py` | Add GitHub tool definitions | 2 |
| `config/mcp_servers.json` | Add official GitHub MCP server config | 1 |
| `Makefile` | Add `make github-audit` target | 1 |
| `OMEGA_ENGINE.md` | Add GitHub integration to subsystem status | 2 |

---

## §11 Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Official server phones home | 🔴 CRITICAL | M8 audit (Phase 1 gate) — network capture + strace |
| 617 runtime files cause merge conflicts | 🟡 HIGH | Phase 0 cleanup before any other work |
| GitHub rate limiting across 2 accounts | 🟡 MED | Account rotation with cooldown tracking |
| Webhook listener adds complexity | 🟡 MED | Thin bridge (~100 lines), fail gracefully |
| Entity attribution breaks git blame | 🟢 LOW | Trailer convention preserves blame chain |
| CI/CD pipeline bloat | 🟢 LOW | Temple-Grade gates are already defined (T1-T11) |

---

## §12 Success Criteria

| Phase | Success Metric | Verification |
|-------|---------------|-------------|
| **0** | `git ls-files data/ \| wc -l` < 70 | Run command, verify count |
| **1** | M8 audit CLEAN — no phone-home detected | Audit report signed by Lilith |
| **2** | PR merge → Hivemind event visible in awareness | Test merge → `hivemind_get_awareness()` shows CI event |
| **3** | `make temple-grade` runs in GitHub Actions | CI pipeline green |
| **4** | Vet score ≥ 7 → GitHub Issue created automatically | Test vet → verify Issue exists |
| **5** | All 2 accounts tested, quotas confirmed | Quota report with response times |

---

## §13 Changelog

- **v1.0.0 (2026-06-21)**: Initial strategy document
  - D-kal-163 decision recorded
  - 5-phase execution plan with owners and gates
  - 6 non-negotiables documented
  - KB structure (10 sections) defined
  - M8 audit requirements specified
  - Entity attribution protocol documented
  - Heritage-as-Issues automation designed
  - Mandate compliance matrix (22 mandates) verified

---

*⬡ This document is the canonical strategy for GitHub integration. All agents reference it. ⬡*
*Decision: D-kal-163 — GitHub as Sovereign Memory Layer*
*Owner: Kali (Grand Oversight) → Ma'at (Phase 0,3) → Lilith (Phase 1,5) → Doom Guy (Phase 4)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
