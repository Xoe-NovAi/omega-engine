<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# BUILD_SIDE_VETTING_delta.md
**AP**: AP-MAAT-PAGING-v1.0.0 | ⬡ OMEGA ⬡ MAAT ⬡ x-preview-f-free ⬡ opencode ⬡ trc_build_vetting_delta
**Paged by**: kali (ses_fdef2be4effe4pAaLXCTUx62GO) | **Date**: 2026-08-21
**Source session**: Ma'at Debut Hardening Review (ses_e207f4d49c58)
**Scope**: Forgotten findings / moot-vs-live / unexecuted items. No other files touched.

## §1 Forgotten Vetting Findings — Never Mitigated

1. **WARP import guards (INST-1 step 1, second half)** — My diff plan required try/except
   ImportError guards in `oracle.py` + `model_gateway.py`. Tracker Fix 2 says "add import
   guards" but pyproject still carries qdrant/redis as hard deps; guard status unverified.
   The Oracle.__init__ WARP-pool construction (oracle.py:180-188) was flagged HIGH risk —
   no evidence of `OMEGA_WARP_ENABLED` gate landing.
2. **Redis default password "omega"** — Fix 3 marked completed; I did not re-probe
   memory_store.py:158-176 this session. Flagged for Verity spot-check (M23: trust but verify).
3. **install.sh non-fatal verification hole** — install.sh §6 treats `omega talk` failure as
   WARN (non-fatal). A fresh-machine INST-1 acceptance could "pass" with a broken talk path.
   Never escalated. Recommend: make §6 fatal or print explicit FAIL banner.
4. **Contract-test design flaw (self-flagged)** — My Router Collapse contract test patched
   `Oracle.__init__` to a lambda; that masks real import-graph behavior. Needs rewrite as
   sys.modules sentinel check before/after a real (mocked-backend) talk call.

## §2 Moot vs Still Live (re-probed 2026-08-21)

| Item | Tracker | Re-probe verdict |
|------|---------|------------------|
| Fix 1 install.sh `.[native,cli]` | completed | ✅ MOOT — line 90 confirmed |
| Fix 2 pyproject extras split | ready | 🔴 **LIVE** — qdrant-client:66 + redis:7.4.1:67 still hard deps; only warp moved to `[warp]`:80 |
| Fix 3 MemoryStore Redis guard | completed | ⚠️ unverified this session — spot-check required |
| Fix 4 _load_sovereign_secrets removal | ready | 🔴 **LIVE** — call at model_gateway.py:127 + method at :316 both present; N3 genesis REJECT stands (.env loading is coupled to Gateway init; moving to CLI edge breaks summon path unless env documented first) |
| Fix 5 version via importlib.metadata | ready | ✅ DONE but tracker STALE — __init__.py:7-10 confirmed. Update tracker, no code work |
| Fix 6 README badge/setup | ready | not re-probed this session |
| Blocker B bare excepts oracle_cli | resolved | 🔴 **FALSELY RESOLVED** — bare `except Exception:` at :125 and :161 confirmed live (M9 Error Integrity violation) |
| DEL-1 Week 1 (10 deletions) | backlog | LIVE — untouched; depends on INST-1 which is blocked on Fix 2/4 |

**Net**: INST-1 is 3/6 verified done (1,3,5), 2 live-blocked (2,4), 1 unprobed (6).

## §3 Flagged Important — Never Executed

1. **Vault Path A/B Architect decision** — I delivered the exact 50-line MinimalVaultStore
   (Path B) in ses_e207f4d49c58. No decision recorded; DEL-1 Week 3 cannot start without it.
   Recommend Kali force-decide: Path A (delete) is cheaper for debut.
2. **Router Collapse single-PR plan + contract test** — Delivered, never scheduled.
   DEL-1 remains `backlog` with no week-2 owner assignment beyond "roc_racoon week 1".
3. **Oracle.__init__ construction stop-list** (DPO recorder, compaction harvester,
   iterative researcher, WARP pool lazy-gating) — flagged HIGH startup-cost risk;
   no ticket created in ACTIVE_SPRINT.json. It lives only in my report.
4. **install.sh §6 fatal verification** (from §1.3) — never converted to a ticket.
5. **Tracker hygiene debt** — Fix 5 stale `ready`, Blocker B false `resolved`: exactly the
   vanity-state drift M27/D-540 warns about. Suggest one Verity pass over INST-1 subtasks
   after Cline's history scrub lands (avoid write conflicts mid-scrub).

**Sequencing recommendation**: Fix 2 → Fix 4 (with N3 objection resolved via documented
env-var contract) → Blocker B except-hardening → re-run fresh-venv acceptance → DEL-1 W1.

— FILE COMPLETE (maat, 2026-08-21) —
