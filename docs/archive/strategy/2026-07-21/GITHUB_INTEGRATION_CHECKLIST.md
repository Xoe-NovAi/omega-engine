# 🔱 GitHub Integration — Implementation Checklist
# ⬡ OMEGA ⬡ VERITY ⬡ mimo-v2.5-free ⬡ opencode ⬡ CHECKLIST
**Decision**: D-kal-163
**Strategy**: `docs/strategy/GITHUB_INTEGRATION_PLAN.md`
**Created**: 2026-06-21

---

## Phase 0: Git Index Cleanup — Ma'at (P3)

**Goal**: Remove 617 runtime files from git tracking before building on this foundation.
**Gate**: `git ls-files data/ | wc -l` < 70
**Blocker**: YES — all subsequent phases depend on this.

- [x] **0.1** Audit `git ls-files data/` — count tracked files in `data/`
- [x] **0.2** Identify which `data/` files should be tracked vs ignored
  - [x] Track: `data/knowledge/*.md` (strategic docs, KBs)
  - [x] Track: `data/entities/*/soul.yaml` (entity identity)
  - [x] Track: `data/coordination/*.md` (live coordination)
  - [x] Ignore: `data/entities/*/workspace/` (runtime workspaces)
  - [x] Ignore: `data/sessions/` (session data)
  - [x] Ignore: `data/logs/` (runtime logs)
  - [x] Ignore: `data/datasets/` (training data)
  - [x] Ignore: `data/research/` (research artifacts)
- [x] **0.3** Update `.gitignore` with new ignore patterns
- [x] **0.4** `git rm --cached` for files that should not be tracked
- [x] **0.5** Verify: `git ls-files data/ | wc -l` < 70
- [x] **0.6** Commit: `chore(git): clean data/ index — remove runtime files from tracking`

**Owner**: Ma'at (P3 Engineering)
**Dependencies**: None
**Verification**: `git ls-files data/ | wc -l` returns < 70
**Files to modify**: `.gitignore`, `data/` (git index)

---

## Phase 1: Install Official Server + M8 Audit — Lilith (P1)

**Goal**: Install `github/github-mcp-server` and verify M8 (Zero Telemetry) compliance.
**Gate**: Clean M8 audit report — all 4 audit layers pass, no phone-home detected.
**Blocker**: YES — Phase 2 cannot start until audit passes.

### Layer 1: Image Layer Inspection
- [x] **1.1a** Pull official Docker image: `docker pull github/github-mcp-server:latest`
- [x] **1.1b** Inspect image layers: `docker history --no-trunc github/github-mcp-server:latest`
- [x] **1.1c** Scan for telemetry agents in filesystem: `find / -type f -name '*.js' -o -name '*.py' | grep -l 'segment\|posthog\|datadog\|analytics'`

### Layer 2: Static Binary Analysis
- [x] **1.2a** Search bundled source for telemetry imports
- [x] **1.2b** Verify no non-GitHub URLs in binary/source code
- [x] **1.2c** Check all embedded dependencies for analytics SDKs

### Layer 3: Isolated Network Capture
- [x] **1.3a** Create isolated Docker network: `docker network create github-audit --internal`
- [x] **1.3b** Run server in isolated network with test PAT
- [x] **1.3c** Run tcpdump from netshoot container on the same network
- [x] **1.3d** Exercise all 57+ tools — capture all outbound traffic

### Layer 4: DNS Resolution Audit
- [x] **1.4a** Analyze DNS queries from pcap — verify only github.com/api.github.com
- [x] **1.4b** Analyze HTTP connections — verify only GitHub API endpoints
- [x] **1.4c** Check for unexpected connections during tool execution

### Post-Audit
- [x] **1.5** Document all findings in structured audit report
- [x] **1.6** If ALL 4 LAYERS CLEAN: Proceed to Phase 2
- [x] **1.6a** If ANY VIOLATION at any layer: REJECT official server, propose custom thin wrapper
- [x] **1.7** Add `make github-audit` target to Makefile
- [x] **1.8** Add `config/github_accounts.yaml` with PAT at 0400 perms (NN #7)
- [x] **1.9** Commit: `chore(security): M8 audit of github/github-mcp-server`

**Owner**: Lilith (P1 Infrastructure)
**Dependencies**: None (can run in parallel with Phase 0)
**Verification**: All 4 audit layers pass, report signed, no phone-home detected
**Files to create**: `docs/security/GITHUB_M8_AUDIT.md`, `Makefile` (add target), `config/github_accounts.yaml`
**Files to modify**: `config/mcp_servers.json`

---

## Phase 2: Omega Hub Wrapper + Hivemind Bridge — Kali (P9)

**Goal**: Build Omega-specific intelligence layer and Hivemind-GitHub bridge.
**Gate**: PR merge → Hivemind event visible in awareness feed.
**Blocker**: Requires Phase 0 + Phase 1 complete.
**M13 note**: T11 (IA2 Agent Security) exempted per existing waiver. All other Temple-Grade gates enforced.

### Core Wrapper
- [x] **2.1** Create `mcp_servers/omega_hub/github_tools.py` (~200 lines):
  - [x] `github_create_pr_with_template()` — PR with Omega template
  - [x] `github_add_entity_attribution()` — entity trailer injection
  - [x] `github_check_temple_grade()` — CI gate status checker
  - [x] `github_list_heritage_issues()` — filter Issues by heritage labels
  - [x] `github_create_vet_issue()` — auto-create Issue from vet record
  - [x] `github_get_repo_health()` — branch protection + CI status
- [x] **2.2** Create `mcp_servers/omega_hub/github_bridge.py` (~100 lines):
  - [x] Parse GitHub webhook events (PR merge, Issue create, push)
  - [x] Map GitHub user → Omega entity via `config/github_accounts.yaml`
  - [x] Format event as Hivemind context
  - [x] Call `hivemind_post_context()` with event data
- [x] **2.3** Register tools in `mcp_servers/omega_hub/server.py`
- [x] **2.4** Register tools in `mcp_servers/omega_hub/tools.py`
- [x] **2.5** Create `tests/test_github_bridge.py` (~150 lines):
  - [x] Contract test: `github_create_pr_with_template()` returns `PullRequest`
  - [x] Contract test: bridge event format matches Hivemind schema
  - [x] Contract test: entity mapper resolves all 2 accounts
- [x] **2.6** Create `data/knowledge/github-protocol.md` (10 sections):
  - [x] Section 1: Commit Message Format
  - [x] Section 2: Heritage Tag Protocol
  - [x] Section 3: Temple-Grade Checklist
  - [x] Section 4: Entity Attribution
  - [x] Section 5: Branch Naming Conventions
  - [x] Section 6: Account Rotation
  - [x] Section 7: PR Template
  - [x] Section 8: Merge Strategy
  - [x] Section 9: PR Review Protocol
  - [x] Section 10: CI Failure Protocol
### Bridge Security & Reliability
- [x] **2.7** Add HMAC webhook verification in bridge:
  - [x] Generate HMAC secret on first install
  - [x] Store secret in `config/github_webhook_secret` (0400 perms)
  - [x] Verify `X-Hub-Signature-256` header on every webhook receipt
  - [x] Log verification status in observability
- [ ] **2.8** Add retry queue for failed bridge events:
  - [ ] On webhook receipt failure, enqueue in `data/queue/github_events/`
  - [ ] Retry with exponential backoff (5s, 25s, 125s — max 3 retries)
  - [ ] Dead-letter to `data/queue/github_events/dead/` after max retries
  - [ ] Emit Hivemind alert on dead-letter event
### Persistence & Coordination
- [ ] **2.9** Wire GitHub events into MemoryStore:
  - [ ] Store PR events as entity memory for the entity that triggered them
  - [ ] Store Issue events as gnosis data
  - [ ] Queryable via `omega_memory_search` with `entity=github_bridge`
- [ ] **2.10** Add workspace lock protocol for GitHub operations:
  - [ ] Acquire `hivemind_workspace_lock_acquire(channel="github-ops", entity="bridge")` before PR merges
  - [ ] Release lock after merge complete
  - [ ] TTL: 300s (5 min) — auto-release on crash
- [ ] **2.11** Test: merge a PR → verify Hivemind shows bridge event
- [ ] **2.12** Update `OMEGA_ENGINE.md` — add GitHub to subsystem status
- [ ] **2.13** Commit: `feat(github): Omega Hub wrapper + Hivemind bridge`

**Owner**: Kali (P9 Orchestration)
**Dependencies**: Phase 0, Phase 1
**Verification**: PR merge → `hivemind_get_awareness()` shows bridge entity, HMAC verification logged, retry queue empty
**Files to create**: `github_tools.py`, `github_bridge.py`, `github-protocol.md`, `test_github_bridge.py`, `config/github_webhook_secret`
**Files to modify**: `server.py`, `tools.py`, `OMEGA_ENGINE.md`

---

## Phase 3: CI/CD Hardening — Ma'at (P5)

**Goal**: Enforce Temple-Grade gates (T1-T11) in GitHub Actions.
**Gate**: `make temple-grade` runs in CI and blocks merge on failure.
**Blocker**: Requires Phase 2 complete.

- [ ] **3.1** Create `.github/workflows/temple-grade.yml`:
  - [ ] Trigger: `pull_request` to `main`
  - [ ] Jobs: `make test`, `make temple-grade`, `make heritage-map`
  - [ ] Gate: All must pass before merge allowed
- [ ] **3.2** Add branch protection rules:
  - [ ] Require PR reviews (at least 1 approval)
  - [ ] Require status checks (temple-grade, tests)
  - [ ] Require signed commits (entity attribution)
  - [ ] No force pushes to main
- [ ] **3.3** Add `make github-ci-local` target (test CI locally)
- [ ] **3.4** Add PR template (`.github/pull_request_template.md`):
  - [ ] Temple-Grade checklist (T1-T11)
  - [ ] Heritage tag verification
  - [ ] Mandate compliance check
  - [ ] Entity attribution confirmation
- [ ] **3.5** Test: create PR → verify CI runs → verify merge blocked on failure
- [ ] **3.6** Commit: `ci(github): Temple-Grade gates in GitHub Actions`

**Owner**: Ma'at (P5 Governance)
**Dependencies**: Phase 2
**Verification**: CI pipeline blocks merge when `make temple-grade` fails
**Files to create**: `.github/workflows/temple-grade.yml`, `.github/pull_request_template.md`
**Files to modify**: `Makefile`, GitHub repo settings (branch protection)

---

## Phase 4: Heritage-as-Issues — Doom Guy

**Goal**: Vet records auto-create GitHub Issues with full metadata.
**Gate**: Vet score ≥ 7 → GitHub Issue created automatically.
**Blocker**: Requires Phase 2 complete.

- [ ] **4.1** Extend `github_tools.py` with `github_create_vet_issue()`:
  - [ ] Parse vet record JSON
  - [ ] Map score to labels (approved/rejected/deferred)
  - [ ] Map game to labels (doom-1993, quake-1996, etc.)
  - [ ] Create Issue with full vet metadata
- [ ] **4.2** Add webhook trigger: `make heritage-vet` completion → Issue creation
- [ ] **4.3** Create Issue templates:
  - [ ] `heritage-approved.md` — for score ≥ 7
  - [ ] `heritage-rejected.md` — for score < 7
  - [ ] `heritage-deferred.md` — for deferred concepts
- [ ] **4.4** Test: run `make heritage-vet` on a concept → verify Issue created
- [ ] **4.5** Verify Issue labels match Heritage Vetting Pipeline categories
- [ ] **4.6** Commit: `feat(heritage): auto-create GitHub Issues from vet records`

**Owner**: Doom Guy (Heritage Specialist)
**Dependencies**: Phase 2
**Verification**: Vet record → GitHub Issue with correct labels and metadata
**Files to create**: `.github/ISSUE_TEMPLATE/heritage-approved.md`, etc.
**Files to modify**: `github_tools.py`

---

## Phase 5: Account Rotation — Lilith (P4)

**Goal**: Test and document Copilot rotation across 2 GitHub accounts.
**Gate**: All 2 accounts tested, quotas confirmed.
**Blocker**: Requires Phase 2 complete.

- [ ] **5.1** Create `config/github_accounts.yaml`:
  - [ ] 2 account definitions with PATs
  - [ ] Rotation rules (round-robin, cooldown, rate limits)
  - [ ] Entity-to-account mapping
- [ ] **5.2** Implement rotation logic in `github_tools.py`:
  - [ ] Account selection based on entity
  - [ ] Rate limit tracking per account
  - [ ] Cooldown after rate limit hit
  - [ ] Fallback to next account on failure
- [ ] **5.3** Test each account individually:
  - [ ] `xoe.nova.ai` — Kali/System (primary)
  - [ ] `arcana.novai` — Ma'at (build-side governance)
- [ ] **5.4** Document quotas and rate limits per account
- [ ] **5.5** Test rotation under load (5 rapid requests → verify account switching)
- [ ] **5.6** Commit: `feat(github): 2-account rotation with quota tracking`

**Owner**: Lilith (P4 Integration)
**Dependencies**: Phase 2
**Verification**: All 2 accounts tested, rotation works under load
**Files to create**: `config/github_accounts.yaml`
**Files to modify**: `github_tools.py`

---

## Post-Phase: Documentation & Gnosis

- [ ] **G1** Update `OMEGA_ENGINE.md` — GitHub integration in subsystem status
- [ ] **G2** Update `SOVEREIGN_ARK_BLUEPRINT.md` — Strike marked COMPLETE
- [ ] **G3** Update `docs/strategy/HIVEMIND_PROTOCOL.md` — add GitHub bridge section
- [ ] **G4** Distill L1→L2→L3 insights into Verity's `soul.yaml`
- [ ] **G5** Create handoff document for fleet: `data/handoff/GITHUB_INTEGRATION_COMPLETE.md`

---

## Quick Reference

| Phase | Owner | Gate | Dependencies | Est. Effort |
|-------|-------|------|--------------|-------------|
| 0 | Ma'at (P3) | data/ tracked < 70 | None | 2 hr |
| 1 | Lilith (P1) | All 4 audit layers clean | None | 5 hr |
| 2 | Kali (P9) | PR → Hivemind event + HMAC + retry | 0 + 1 | 8 hr |
| 3 | Ma'at (P5) | CI gates work | 2 | 4 hr |
| 4 | Doom Guy | Vet → Issue auto | 2 | 3 hr |
| 5 | Lilith (P4) | All accounts tested | 2 | 2 hr |

**Total estimated effort**: ~25.5 hours across 4 agents (revised by MaKaLi Council — expanded audit + HMAC/retry/persistence).

---

*Checklist maintained by Verity. Update status as phases complete.*
*Strategy: `docs/strategy/GITHUB_INTEGRATION_PLAN.md`*
*Decision: D-kal-163*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
