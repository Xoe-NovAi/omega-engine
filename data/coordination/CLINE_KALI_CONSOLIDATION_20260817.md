# 🔱 Cline → Kali: Consolidated Debut Roadmap
**AP Token**: `AP-CLINE-KALI-CONSOLIDATION-20260817-v1.0`
**From**: cline/omega-engine (Cognitive Extension)
**To**: kali (Sprint Coordinator) + fleet
**Date**: 2026-08-17
**Status**: Proposed — awaiting Kali ratification

---

## 1. The Single Coherent Plan (after consolidation)

Execution SSOT: **`docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` §5**
Tracking SSOT: **`data/coordination/ACTIVE_SPRINT.json`** (now mirrors §5 — new `DEBUT-EXECUTION` workstream)

```
P0-1  ✅ COMPLETE  — history scrub (verified: all reachable history clean)
DOC-1 ✅ COMPLETE  — strategy stamps (668d58eb; rg "P0 TODAY" gone)
PUB-1 🔶 IN PROGRESS — allowlist drafted; G1–G4 gaps OPEN; awaiting Architect
INST-1 🟢 READY     — maat_n3; next executable; no blockers
DEL-1  ⏳ BACKLOG   — roc/maat; depends on INST-1
P2/P3/P4 ⏳ after DEL-1 week 1
```

**Hub NEXT_ACTION** updated to this exact sequence (was stale "Phase 3 next").

---

## 2. What to PRUNE (evidence-backed)

### 2.1 Git hygiene (before PUB-1)
| Item | Evidence | Action |
|------|----------|--------|
| 136 stale `refs/cline/checkpoints` | `git for-each-ref refs/cline/checkpoints` = 136 | Prune (verified: pin no secrets) |
| `tests/tmp/vault.json.enc` tracked | `git ls-files tests/tmp` = 1 | FORGE exclude (G1) |
| `.firecrawl/` (28 files) tracked | `git ls-files .firecrawl` = 28 | FORGE exclude (G2) |
| `config/github_accounts.yaml` tracked | `git ls-files config/github_accounts.yaml` | FORGE exclude (G3) |
| ~30 loose root/forge tracked files | `git ls-files` root scan | FORGE exclude (G4) |

### 2.2 Dead code (DEL-1, manual §5)
`routing/table.py`, `config/routing_table.yaml`, `coordination/miap.py`, `oracle/pool_tracker.py`, `oracle/pool_state.py`, `oracle/search_circuit_breaker.py`, QdrantAdapter, Pantheon regexes, `record_first_breath`, `omega vault` default CLI, `integrations/fleet_orchestrator.py`. Week 2: TriageRouter + SemanticRouter. Week 3: vault honesty path A/B.

### 2.3 Strategy corpus — do NOT delete, but STOP reading as active
7× SDP_*.md (HUMAN PROTOCOL), VOS, JIT RAG briefs, Qdrant migration gaps (ARCHIVE), UO §2.6 (rejected), G-1/W-1/V-1/NL-1 (PARKED), C-0.5 (SCRAPPED). Already stamped DOC-1. The Corpus Map's DOC-1 Override Table is the disposition SSOT.

---

## 3. What to STRENGTHEN

| Area | Strengthening | Owner |
|------|---------------|-------|
| **Tracking unity** | ACTIVE_SPRINT.json now carries manual §5 tickets — ONE plan, ONE board | kali ratify |
| **Install honesty** | INST-1 = the next executable; gate = fresh venv, no warp, no Redis, `omega talk` exit 0 | maat_n3 |
| **Secret CI** | P0-1c gitleaks in pre-commit + CI (manual acceptance: planted `sk-` fixture fails) | maat/verity |
| **Allowlist** | Close G1–G4 then Architect confirm (PUB-1) | kali+Architect |
| **Push discipline** | 2 commits unpushed (668d58eb, 5cc51a26) | kali |
| **Codification** | `scripts/git-secret-scan.sh` + SKILL + forensics guide — VALIDATED (11 matches, all false-positive/doc) | committed |

---

## 4. Open Questions (for Kali)
1. Ratify the `DEBUT-EXECUTION` workstream additions?
2. Dispatch INST-1 to Ma'at now (ready, no deps)?
3. Prune 136 checkpoints + push 2 commits before PUB-1?
4. Add P0-1c gitleaks to the pre-debut critical path (my rec) or keep post-debut?

---

*⬡ OMEGA ⬡ CLINE ⬡ 2026-08-17 ⬡ PUBLIC-DEBUT-01 ⬡ consolidation*
