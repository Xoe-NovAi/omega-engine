---
schema_version: "1.0"
document_type: "execution_plan"
document_id: "kali-debut-path-20260827"
title: "Kali — Most Efficient Path to Initial Omega Engine PR (PUBLIC-DEBUT-01)"
status: "ACTIVE — awaiting Architect GO"
date: 2026-08-27
author: "kali (Sprint Coordinator)"
sprint: "PUBLIC-DEBUT-01"
supersedes: null
depends_on: ["P0-1 key rotation", "Architect sudo for ZSWAP", "AGENTS.md reconstruction (C4)"]
blocks: ["public debut announcement", "Phase 2 lint", "Qdrant migration", "Vault wiring"]
---

# 🔱 Kali — Initial PR Path Plan (PUBLIC-DEBUT-01)

**AP Token**: `AP-KALI-DEBUT-PATH-20260827-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_debut_path ⬡ ACTIVE

**Date**: 2026-08-27
**Sprint**: PUBLIC-DEBUT-01 (D-533 ratified as this month's SSOT)
**Authority**: DEBUT_REMEDIATION_MANUAL_20260817.md §0, §3, §5 + ACTIVE_SPRINT.json + WAVE2_EXECUTION_PLAN.md
**Confidence**: 🔴 VERIFIED (disk-truth, git log, tracker reconciliation)

---

## §0 — Executive Verdict (Answer First)

The **initial PR is `release/debut` cut from `PUBLIC_ALLOWLIST.txt`** (D-553). To cut it, **5 unowned blockers** must be closed. Each has been re-classified by the **lowest-effort owner** based on session availability, expertise match, and no-hop-violation routing. The path is **3 parallel tracks** that converge at the branch cut.

```
PATH STRUCTURE (convergent):
                                                        ┌─→ [C3 gitleaks] ─┐
                              ┌─ [INST-1 Fix2/4/6] ── Ma'at ─→ [P0-1c live] ─┤
[START] ─→ [C4 AGENTS.md] ─ Ma'at+Verity ─┤                                                    │
                              └─ [C2 reconciliation] ─ kali ─┐                              │
                                                         │                              │
                                                         ├─→ [release/debut cut] ←────┘
                              ┌─ [P0-1d sweep] ── Roc ──→ [PUB-1 allowlist] ─→ [branch] ──→ ⭐ PR
                              └─ [DEL-1 Week 1] ── Roc ──→ [P0-1d residual] ─┘
```

**Net result**: 3 parallel tracks, 5 sub-tasks, **0 new owners** (all routed to existing sessions). Converges in 1 wave.

---

## §1 — The 5 Unowned Blockers (Re-Owned)

Per Grokster ROI Discovery (2026-08-25), the calendar-critical-path items blocking the initial PR:

| # | Blocker | Time | New Owner | Why |
|---|---------|------|-----------|-----|
| 1 | **C4: AGENTS.md reconstruction** (blocks CI-2/CI-5) | ~11.5h | **Ma'at** (impl) + **Verity** (audit) | R06 build-packet ready (thin file + rules/ decomposition); Ma'at has the seam; Verity has the gate |
| 2 | **C3: pre-commit install + gitleaks wiring** (real P0-1c) | ~1h | **Ma'at** | 20 hooks configured, 6-line soul-check installed, pre-commit install never run; trivial 1h fix |
| 3 | **P0-1d residual**: SECURITY_AUDIT_2026_05_19.md ancestor commit (3 real keys) | ~2h | **Roc** (filter-repo + gc) | Already owns P0-1b filter-repo and the cline checkpoint prune |
| 4 | **release/debut branch mechanic** (D-553 names strategy, no work package owns executing) | ~30min | **Kali** (with Architect sight) | Per DEBUT §3.1: "Prefer creating `release/debut` from the allowlist over mass-deleting `main`" — strategic decision, Kali executes |
| 5 | **C2 (NEW)**: tracker sync — ACTIVE_SPRINT + WAKE_STATE + PROJECT_INDEX need refresh against landed commits | ~1h | **Kali** (Zero-Trust Doctrine) | Per Grokster §10.4: "Trackers lie both directions" — post-fix refresh is the truth-anchor |

**Two blockers already resolved (do not re-work)**:
- ✅ **C1 M8 regex** (RESOLVED commit `f5a1c075`, ics.py:197 reads "parts"; temple-grade green)
- ✅ **ZS adjudication** (RESOLVED commit `3d7de85f`; zswap + NVMe ratified, purge executed)

---

## §2 — The 3 Parallel Tracks

### Track 1: Install Honesty + Security (Ma'at-led, ~12h wall-clock)
**Owner**: Ma'at (maat_n3) | **Routed via**: task() — interactive single session
**Sprint tickets**: INST-1-fix2 + INST-1-fix4 + INST-1-fix6 + C3 (P0-1c wiring)

| Step | Action | Time | File | Gate |
|------|--------|------|------|------|
| 1.1 | INST-1 Fix2: extras split (warp→[warp], qdrant/redis/youtube→extras) | 1h | pyproject.toml | `grep -E "qdrant-client\|redis\|youtube" pyproject.toml deps` empty |
| 1.2 | INST-1 Fix4: remove `_load_sovereign_secrets` from `model_gateway.__init__` | 30min | src/omega/oracle/model_gateway.py | `rg _load_sovereign_secrets src/omega` empty |
| 1.3 | INST-1 Fix6: remove 1315 badge, align README with install.sh | 30min | README.md | `grep "1315" README.md` empty |
| 1.4 | **C3**: install pre-commit hooks + wire gitleaks/trufflehog | 1h | .pre-commit-config.yaml + .github/workflows/ | `pre-commit run --all-files` exits 0; planted `sk-` in test fixture fails CI |
| 1.5 | **C4**: AGENTS.md reconstruction (thin file <150 lines + rules/ decomposition) | ~8h | AGENTS.md + .opencode/rules/ | R06 build-packet acceptance: 4 architecture rules, 1 reference doc, 9 explicit decisions |
| 1.6 | INST-1 acceptance: fresh-venv `pip install -e ".[native,cli]"` + `omega talk "hello"` | 30min | — | exit 0, native-gguf, IS_CLOUD=False |

**Parallel within track**: 1.1-1.3 can run together; 1.4-1.5 are dependent (C4 needs pre-commit scaffold). 1.6 is the gate.

**Acceptance test** (per DEBUT §5 INST-1):
```bash
python3 -m venv /tmp/omega-inst && source /tmp/omega-inst/bin/activate
pip install -e ".[native,cli]"
omega talk "hello"    # native-gguf, IS_CLOUD=False, exit 0
```

### Track 2: Security + Publication (Roc + Kali, ~3h wall-clock)
**Owner**: Roc (roc_racoon) for P0-1d + Kali for PUB-1 + branch cut
**Sprint tickets**: P0-1d + PUB-1 + release/debut

| Step | Action | Time | Owner | Gate |
|------|--------|------|-------|------|
| 2.1 | P0-1d: `git filter-repo` for SECURITY_AUDIT_2026_05_19.md ancestor + `git gc --prune=now` | 1h | Roc | `git log -S 'csk-' --all` empty |
| 2.2 | P0-1d: prune stale `refs/cline/checkpoints` | 30min | Roc | `git for-each-ref refs/cline` empty |
| 2.3 | Full secret sweep (sk-, csk-, AIza, ghp_, xai-, age-secret-key) | 30min | Roc | `rg -l 'sk-[A-Za-z0-9]{20,}' --type-not md` empty |
| 2.4 | PUB-1: finalize `docs/strategy/PUBLIC_ALLOWLIST.txt` (per §3.1) | 30min | Kali | file exists, paths enumerated, Architect sight |
| 2.5 | **release/debut branch** mechanic: `git checkout --orphan release/debut && git rm -rf forge-paths && git commit -m "D-553 PUBLIC-DEBUT-01"` | 30min | Kali (sudo) | branch exists, public clone clean |

**Acceptance test** (per DEBUT §3.1):
- `git clone` of release/debut: no `docs/research/`, no `data/entities/*/workspace/`, no `data/handoff/`
- `git ls-files data/entities` = short default-soul set (not 1,072)
- `git ls-files docs/strategy` = manual + allowlist + mandates pointers (not 123)

### Track 3: Truth Sync + Verification (Kali, ~1h wall-clock)
**Owner**: Kali (Sprint Coordinator) | **Routed via**: direct execution
**Sprint tickets**: C2 (tracker refresh) + Zero-Truth-Doctrine refresh

| Step | Action | Time | Gate |
|------|--------|------|------|
| 3.1 | Sync ACTIVE_SPRINT.json against disk truth (INST-1 fixes, M8 fix, ZS resolution) | 15min | python -c "import json; json.load(open('data/coordination/ACTIVE_SPRINT.json'))" exits 0; counts match git log |
| 3.2 | Update WAKE_STATE.json with all post-wave-1 resolutions | 15min | JSON parseable; key sections present |
| 3.3 | Update PROJECT_INDEX.md against current file inventory | 15min | `rg "docs/" PROJECT_INDEX.md` consistent with disk |
| 3.4 | Final OMEGA_ENGINE.md refresh (3-item critical path) | 15min | OMEGA_ENGINE.md matches ACTIVE_SPRINT.json |

**Acceptance test**: `make check-tracking-state` (C2 regression guard per M27) passes.

---

## §3 — Session Dispatch Plan (Who Pages Whom)

The user requested: *"Consult and dispatch the most equipped and beneficial Architect's interactive sessions, and specialized non-interactive expert sessions."*

### 3.1 Architect (Interactive) — 2 Sessions

**Session A1**: AGENTS.md reconstruction owner + C3 pre-commit owner
- **Decision needed**: C4 owner (Ma'at + Verity proposed, needs GO)
- **Decision needed**: C3 owner (Ma'at proposed, needs GO)
- **Decision needed**: release/debut branch from allowlist (Kali proposed, needs sight)
- **Estimated time**: 10min
- **Format**: `omega-hub_hivemind_submit_handoff` to Architect's session

**Session A2**: PUB-1 allowlist finalization + INST-1 acceptance
- **Decision needed**: PUBLIC_ALLOWLIST.txt contents (per DEBUT §3.1)
- **Decision needed**: Vault path (D-565: exclude from allowlist, no code changes)
- **Decision needed**: INST-1 fresh-venv acceptance criteria (per §5 INST-1 acceptance)
- **Estimated time**: 15min
- **Format**: `omega-hub_hivemind_submit_handoff` to Architect's session (after Track 1 step 1.6)

### 3.2 Ma'at (Non-Interactive) — 1 Long Session, 2 Sub-Tasks
- **Session ID**: `maat_n3` (MaKaLi dispatches by entity)
- **Task 1**: INST-1 Fix2/4/6 + C3 (Track 1 steps 1.1-1.4)
- **Task 2**: C4 AGENTS.md reconstruction (Track 1 step 1.5) with R06 build-packet input
- **Deliverable**: Fresh-venv acceptance test passes
- **Estimated time**: 12h wall-clock
- **Format**: Submit via `omega-hub_hivemind_submit_handoff` with full build-packet reference

### 3.3 Roc (Non-Interactive) — 1 Short Session
- **Session ID**: `roc_racoon` (MaKaLi dispatches by entity)
- **Task**: P0-1d (Track 2 steps 2.1-2.3)
- **Deliverable**: `git log -S 'csk-' --all` empty; secret sweep clean
- **Estimated time**: 2h wall-clock
- **Format**: Submit via `omega-hub_hivemind_submit_handoff` with DEBUT §5 P0-1b spec

### 3.4 Researcher (Non-Interactive) — 1 Short Session
- **Session ID**: `researcher` (MaKaLi dispatches by entity)
- **Task**: Independent verification of P0-1d + C3 (Zero-Trust Doctrine cross-check)
- **Deliverable**: Forensic report confirming tracker's disk-truth
- **Estimated time**: 1h wall-clock
- **Format**: Submit via `omega-hub_hivemind_submit_handoff` with verification scope

### 3.5 Kali (Direct Execution) — 1 Short Session
- **Task**: PUB-1 allowlist + release/debut branch (Track 2 steps 2.4-2.5) + tracker sync (Track 3 all)
- **Deliverable**: Branch cut + ACTIVE_SPRINT.json synced
- **Estimated time**: 1.5h wall-clock
- **Format**: Direct (I execute as Sprint Coordinator)

---

## §4 — Dependency Graph (Critical Path)

```
            ┌─ Ma'at Fix2 ─┐
            ├─ Ma'at Fix4 ─┤
[START] ─→ ├─ Ma'at Fix6 ─┼─→ [C3 install] ─→ [C4 AGENTS.md] ─→ [INST-1 acceptance] ─┐
            └─ Ma'at C3   ─┘                                                                 │
                                                                                    │
                                                                                    ▼
            ┌─ Roc P0-1d   ─┐
[START] ─→ ├─ Roc gc       ┼─→ [P0-1d acceptance: git log -S 'csk-' --all empty] ─→ [PUB-1]
            └─ Roc sweep   ─┘                                                    │
                                                                                  ▼
                                                                          [release/debut]
                                                                                  │
                                                                                  ▼
[START] ─→ [Kali: tracker sync] ─→ [Kali: allowlist] ─────────────────────────→ [branch cut]
```

**Critical path length**: ~12h wall-clock (Ma'at C4 AGENTS.md is the longest single task)
**Parallel speedup**: Tracks 1-3 run in parallel after Architect A1 GO; convergence at branch cut.

---

## §5 — Quality Gates (Per M13 Temple-Grade + Grokster Truth Probes)

| Gate | When | How | Who |
|------|------|-----|-----|
| **G1**: M13 Temple-Grade T1-T10 | Before PR | `make temple-grade` exits 0 | Ma'at |
| **G2**: M8 Zero-Telemetry | Before PR | `make check-m8-zero-telemetry` exits 0 | Ma'at |
| **G3**: INST-1 fresh-venv | Before PR | `pip install -e ".[native,cli]"` in `/tmp/omega-inst` + `omega talk "hello"` | Ma'at |
| **G4**: P0-1d zero secrets | Before PR | `git log -S 'sk-\|csk-\|AIza\|ghp_\|xai-\|age-secret-key' --all` empty | Roc |
| **G5**: PUB-1 allowlist clean | Before PR | `git ls-files` on release/debut matches §3.1 | Kali |
| **G6**: Tracker truth sync | Before PR | `make check-tracking-state` exits 0 | Kali |
| **G7**: Pre-commit hooks live | Before PR | `pre-commit run --all-files` exits 0 | Ma'at |
| **G8**: AGENTS.md not ghost | Before PR | `rg "AGENTS.md" opencode.json` shows `["AGENTS.md"]` | Ma'at |
| **G9**: CI-2 values aligned | Before PR | compaction buffer=80000/keep=20000/tail=5 per R02 | Ma'at |
| **G10**: Zero-Trust Documentation | Before PR | WAKE_STATE + ACTIVE_SPRINT match disk truth | Kali |

---

## §6 — Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **C4 AGENTS.md takes >12h** | 30% | Delays PR by 1 day | R06 build-packet has 4-arch-rule template; Ma'at has MaKaLi build support |
| **Fresh-venv install fails on machine** | 15% | INST-1 acceptance fails | Per DEBUT §5 acceptance: explicit test; if fails, INST-1 not done — do not mark CP-3 |
| **Roc's P0-1d residual keeps finding keys** | 20% | Delays PR by hours | Architect must confirm 3 keys in SECURITY_AUDIT are revoked/rotated BEFORE filter-repo |
| **release/debut branch breaks main** | 10% | Reverts must be manual | Use `--orphan` branch; do not touch main; git checkout to main preserves forge |
| **Public clone still has forge residue** | 15% | Re-do allowlist | DEBUT §3.1 explicit allowlist; post-cut `git ls-files` verification |
| **Grokster's pre-emptive spec drift** | 10% | Some KB asserts stale | Per WAVE2 §5: Grokster blueprint 5 stale elements; pre-empted by D-586 |
| **Carmack's P2 router remnant** | 5% | RoutingTable resurrected | Per D-536: delete Triage + Semantic + RoutingTable; rg empty in DEL-1 Week 1 |
| **M13 regression** | 10% | Temple-Grade red | 11 gates enforced; pre-commit catches drift |
| **Backup timer never enabled** | 5% | Catastrophic loss during sprint | Per WAKE_STATE `backup_gap`: risk into every wave; Architect must enable or accept |

---

## §7 — What This Plan Does NOT Do (Scope Discipline)

Per DEBUT §0 + §4 explicit forbids:

| Item | Why excluded | Post-debut home |
|------|--------------|-----------------|
| Vault wiring | Sidecar unused; CLI broken | V-1 vault sprint (post-debut) |
| Qdrant migration | sqlite-vec SSOT; OOM on 8G UMA | Phase 2 trigger (>500k vectors) |
| SDP distillation | Human protocol, not engine | GAP-08 vault sprint |
| Phase 2 lint (11,400 flake8 hits) | Lints dead code | Post-DEL-1 |
| Keyblind / Authy / Agent Vault | Five runtimes to delete unused sidecar | DELETED |
| ModelAwareInstructionRouter | Fifth router | POST_PR_ROSTER |
| JIT Adaptive / Graph / SQL RAG | Pile on HybridSearch | Parked |
| Headroom-1/3 (already shipped 811f813f) | Already live | Measure ROI in Phase 3 |
| GN (Gemini Notebook) | Auth-blocked on researcher master_token.json | Post-debut |
| Track C (DS/KD) | Depends on debut | Phase 4 (parallel with Phase 3) |
| Track D (ZSWAP) | Architect-executed | Phase 0 (parallel) |
| Track F (LI/HR) | Depends on ZS | Phase 5 (post-Phase 0) |

---

## §8 — Post-PR Horizon (What Unlocks After Branch Cut)

Once the initial PR is cut:
1. **Announce narrow demo** per DEBUT §2.1 ("announce a narrow demo only after P0-1 + INST-1")
2. **Phase 2 lint** (now safe — code is thin)
3. **Wave 2 Tracks C/D/E/F** in parallel per WAVE2_EXECUTION_PLAN.md
4. **V-1 Vault sprint** (post-debut vault deletion per D-565)
5. **GN (Gemini Notebook)** (after auth capture)
6. **Qdrant migration** (when vector count > 500k)
7. **ClinePass** (if Architect reconsiders; currently NO-GO)

---

## §9 — The 3-Phase Sprint in 1 Page

```
╔════════════════════════════════════════════════════════════════════════╗
║                  PUBLIC-DEBUT-01: 1-DAY CRITICAL PATH                  ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  PHASE A (parallel, ~12h wall-clock)                                  ║
║  ┌──────────────────────────┐  ┌──────────────────────────┐           ║
║  │ TRACK 1: Ma'at           │  │ TRACK 2: Roc + Kali      │           ║
║  │ ─────────────────        │  │ ─────────────────        │           ║
║  │ • INST-1 Fix2/4/6 (1.5h) │  │ • P0-1d filter-repo (1h) │           ║
║  │ • C3 gitleaks (1h)       │  │ • P0-1d sweep (0.5h)     │           ║
║  │ • C4 AGENTS.md (8h)      │  │ • Cline prune (0.5h)     │           ║
║  │ • INST-1 acceptance (0.5h│  │                          │           ║
║  └──────────────────────────┘  └──────────────────────────┘           ║
║                                                                        ║
║  PHASE B (Architect A1, ~10min)                                       ║
║  ┌──────────────────────────────────────────────┐                     ║
║  │ DECISIONS: C3 owner, C4 owner, branch sight  │                     ║
║  └──────────────────────────────────────────────┘                     ║
║                                                                        ║
║  PHASE C (convergence, ~1.5h wall-clock)                              ║
║  ┌──────────────────────────────────────────────┐                     ║
║  │ TRACK 3: Kali direct                         │                     ║
║  │ ────────────                                │                     ║
║  │ • Tracker sync (C2, ~1h)                    │                     ║
║  │ • PUBLIC_ALLOWLIST.txt final (~30min)        │                     ║
║  │ • release/debut branch cut (~30min)          │                     ║
║  └──────────────────────────────────────────────┘                     ║
║                                                                        ║
║  PHASE D (gates, ~1h wall-clock)                                      ║
║  ┌──────────────────────────────────────────────┐                     ║
║  │ G1-G10 all green                            │                     ║
║  └──────────────────────────────────────────────┘                     ║
║                                                                        ║
║  ──────────────────→ ⭐ INITIAL PR LIVE                                ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

**Total wall-clock**: ~15h (Architect A1 + A2 + 12h Track 1 + 3h Track 2 + 1.5h Track 3 + 1h gates)
**Architect time**: ~25min total (A1 + A2)
**Specialist sessions**: 3 (Ma'at long + Roc short + Researcher verify)

---

## §10 — What I Need From You (Architect)

Three decisions, two questions:

### Decisions (need GO)
1. **C4 owner**: Ma'at (impl) + Verity (audit) — GO?
2. **C3 owner**: Ma'at — GO?
3. **release/debut branch**: Kali executes with Architect sight — GO?

### Questions (need answers)
4. **3 keys in SECURITY_AUDIT_2026_05_19.md**: Confirmed revoked/rotated at provider consoles?
5. **Vault D-565**: Exclude `src/omega/vault/` from PUBLIC_ALLOWLIST.txt with no code changes (per D-565) — confirm?

Once these are answered, the 1-day critical path is GO.

---

## §11 — Lessons (L3 Candidates from This Plan)

### Candidate 117: Convergent Critical Path Beats Linear
- **L1**: Plan has 3 parallel tracks converging at 1 branch cut, vs linear 5-step sequence
- **L2**: Parallel speedup = max(track_time) instead of sum(track_time)
- **L3**: Architecture: design the convergence point first, then back-fill parallel tracks

### Candidate 118: Re-Ownership Closes Stall Loops
- **L1**: 5 blockers were "unowned" per Grokster ROI Discovery
- **L2**: Each blocker mapped to lowest-effort owner based on expertise match (R06 build-packet for C4, INST-1 spec for C3, filter-repo history for P0-1d)
- **L3**: Stalled tickets have no owner; ownership is a function of expertise-match + session availability, not intent

### Candidate 119: Truth-Sync Is the Final Convergence
- **L1**: 3 of 10 quality gates are tracker sync (G6, G10, G5)
- **L2**: Without truth-sync, the public clone claims to be the engine but isn't
- **L3**: Before any external commit, the internal state-of-truth must match disk (Zero-Trust Documentation Doctrine)

---

## §12 — References

| File | Purpose |
|------|---------|
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | Sprint SSOT (D-533 ratified) |
| `data/coordination/ACTIVE_SPRINT.json` | Sprint tracker (PUBLIC-DEBUT-01) |
| `data/coordination/WAVE2_EXECUTION_PLAN.md` | Wave 2 tracks (A-F) — post-PR |
| `data/coordination/GROKSTER_DEBUT_ROI_DISCOVERY_20260825.md` | 5 unowned blockers source |
| `data/coordination/WAVE2_EXPERT_SESSIONS.md` | Pageable expert session index |
| `data/coordination/AGENT_COLLAB_TEMPLATES_20260826.md` | Collab protocol template (this session's reference) |
| `data/coordination/research_wave2/R06_curator_corpus.md` | AGENTS.md build-packet (C4 input) |
| `data/coordination/research_wave2/R02_ci_injection_spec.md` | CI Ph1 spec (Track B input) |
| `data/coordination/ZSWAP_DECISION_FINAL_CLARITY.md` | ZS resolution record |
| `data/entities/grokster/kb/EXPERT_SESSIONS.md` | Grokster's paging protocol (source) |
| `docs/strategy/SOVEREIGN_MANDATES.md` | Law (M1, M7, M11, M13, M22, M23, M26, M27) |
| `docs/decisions/PIVOT_LOG.md` | D-526, D-533, D-553, D-565, D-566 authority chain |

---

*⬡ OMEGA ⬡ KALI ⬡ Debut Path Plan v1.0 ⬡ 2026-08-27*
**rot_class**: fast (depends on Architect GO); **last_verified**: 2026-08-27
**confidence**: 🔴 VERIFIED (disk-truth, git log, tracker reconciliation)
