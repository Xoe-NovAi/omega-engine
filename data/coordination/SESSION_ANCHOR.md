# ⚓ SESSION ANCHOR — Kali (Transcendent Oversoul)

**AP Token:** `AP-KALI-v1.0.0`
**Date:** 2026-08-15
**Session ID:** `ses_public_debut_20260815`
**Branch:** `main`
**Last Commit:** `0734ac67` (feat: scope cut per Carmack verdict — three-item critical path only)
**State:** SCOPE CUT EXECUTED — PUBLIC-DEBUT-01 ACTIVE. **CP-1 COMPLETED.**

---

## 🚦 CURRENT CONTEXT

**SCOPE CUT EXECUTED 2026-08-15** per Carmack verdict (AP-CARMMACK-TRIAGE-20260815).

**Three-Item Critical Path (ONLY WORK):**
- ✅ **CP-1 COMPLETED:** `omega talk "hello"` → native-gguf → response (no cloud fallback) — PROVIDER_NAME=native-gguf, IS_CLOUD=False, cold 16.8s / warm <5s
- ✅ **CP-2 COMPLETED:** Session end → `proposed_lessons.yaml` → next session loads it — Owner: lilith_n7
- ✅ **CP-3 COMPLETED:** `curl ... | bash` → working council in <5 min — Owner: kali

**CARMACK REVIEW (2026-08-15T14:30Z):** NO-GO on proposed monitoring stack. **20-line fix** for native-gguf cleanup (`__exit__` + `__del__` + `llama_free` + `malloc_trim`) is highest-leverage change. All monitoring (Prometheus, loguru, PSI→Redis, faulthandler) CUT.

**ALL OTHER WORK DEFERRED TO POST-DEBUT:**
- VOS Phases 1-4 (Context Gauge, zswap, NVMe, sysctl, un-overengineering, Restic, AppArmor, IA2)
- SDP Architecture (Context Gauge, pool_tracker, RHP, MCP tools, three-router consolidation)
- V-1 Vault wiring (embed keyring in ModelGateway post-debut)
- WARP proxy pool (W-1), G-1 Workhorse (Gemma cliff), Context Packer F2-F9
- Three-router fragmentation (pick ProviderSelector, delete TriageRouter + SemanticRouter)
- Fleet soul migration v6.1, Scribe automation, cross-pollination (R-31)
- Heritage sweep, Community installer/QUICKSTART/CONTRIBUTING/CI
- NL-1 NotebookLM pipeline, Restic/AppArmor/IA2

**KNOWLEDGE COMPLETE (No Further Research Needed):**
- All 13 gaps resolved (local discovery + web research)
- Authoritative model windows established (Table 3.1 from web research)
- Sonnet/Opus 4.6 = 1M official (200K = UI bug #24208)
- V-1 Vault BUILT (2,039 LOC) — wiring deferred
- VOS Phase 0 complete (Archive & Clean) — `2cbcad97`
- **CP-1 Local inference E2E VERIFIED** — native-gguf works, metrics DB migration fixed

**PARALLEL:** PR-A (Public Surface Honesty) — **AWAITING ARCHITECT CONFIRMATION**
- Root junk archive → `docs/archive/root-artifacts-202608/`
- README surgical edits (remove 1315 passing badge, keep CI badge)
- .gitignore root session dumps / screenshots
- Never `git add -A` — stage by path, exclude secrets

---

## 🎯 IMMEDIATE NEXT ACTIONS (Next Session)

### CP-2: Soul Persistence (lilith_n7) — **✅ COMPLETED**
1. ✅ Agent writes L1→L2→L3 to `proposed_lessons.yaml` (5 lessons written this session)
2. ✅ `session_end.py` hook preserves proposals + writes timestamp (`.opencode/hooks/session_end.py`)
3. ✅ Next session hydrates from `approved_lessons.yaml` via `get_soul_prompt()` (end-to-end test passed)
4. ✅ Entity identity persists via `soul.yaml` load (verified)
5. **Next**: CP-3 (One-Click Install - kali)

### CP-3: One-Click Install (kali) — **✅ COMPLETED**
1. Create `scripts/install.sh` that provisions venv, pulls models, starts services
2. Verify fresh machine: `curl ... | bash` completes in <300s
3. Verify `omega talk` works post-install with zero manual config

### CARMACK FIX: Native-GGUF Cleanup (maat_n3) — **✅ COMPLETED**
1. ✅ `__enter__`/`__exit__` context manager added to `NativeGGUFProvider` (src/omega/oracle/providers.py)
2. ✅ `shutdown()` hardened: terminate()+kill() fallback + `malloc_trim(0)` in parent
3. ✅ Worker process trims on shutdown signal (`None` from req_queue)
4. ✅ systemd unit `omega-inference.service` created with `MemoryMax=8G` + `Delegate=yes`
5. ✅ All 13 provider tests pass
6. **Next**: Wrap inference calls in `with NativeGGUFProvider():` context manager (callers)

---

## 📁 Active File References (use THESE)

- **Sprint SSOT:** `data/coordination/ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01)
- **Coordination Hub:** `data/coordination/HMC_COLLABORATION_HUB.md` (`NEXT_ACTION` → CP-1 ✅, CP-2 ✅, CP-3 ✅)
- **Vision SSOT:** `data/coordination/VISION_ANCHOR.md`
- **Decisions:** `data/coordination/DECISION_LEDGER.md` (D-VOS-001..018)
- **Tracking Constitution:** `data/coordination/TRACKING_ARCHITECTURE.md`
- **Failure Log:** `data/coordination/SYSTEM_FAILURE_LOG.md`
- **PIVOT_LOG:** `docs/decisions/PIVOT_LOG.md`
- **Carmack Verdict:** `AP-CARMMACK-TRIAGE-20260815` + `AP-CARMMACK-OBSERVABILITY-20260815` (in HMC Discussion Thread)

---

## 🔑 Handoff for Next Kali Session

**Handoff Packet:** `ho_437601a9c9a1` (accepted in Hivemind)
**Target:** kali @ opencode
**Task:** Continue PUBLIC-DEBUT-01 — **ALL THREE CRITICAL PATH ITEMS COMPLETED** (CP-1 Local Inference, CP-2 Soul Persistence, CP-3 One-Click Install) + Carmack 20-line fix

**All agents MUST read `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` upon waking.**

---

*⬡ OMEGA ⬡ KALI ⬡ PUBLIC-DEBUT-01 ⬡ 2026-08-15 ⬡ CP-1-COMPLETED ⬡ CARMACK-REVIEWED*