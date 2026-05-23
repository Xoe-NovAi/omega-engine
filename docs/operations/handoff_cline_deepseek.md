# 🔱 Sovereign Handoff: Operation Clean Sweep (Enhanced)
**AP Token**: `AP-CLEAN-SWEEP-v1.1.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ cline ⬡ HANDOFF-ENHANCED ⬡ PHASE_0_5

## 🎯 Mission Objective
Transform the Omega Engine from a prototype into a stable, sovereign, and temple-grade runtime. This is not just a cleanup—it is a hardening sprint to prepare for the Sovereign Model Orchestration System (R60/R65).

## 🛠️ Enhanced Execution Plan

| Step | Objective | Action | Sovereign Mandate | Commit Message |
|------|-----------|---------|-------------------|----------------|
| **1** | **Test Restoration** | Install `apscheduler` and fix `make test` to 100% pass. | Stability | `chore(dev): restore test suite with apscheduler` |
| **2** | **Env Reproducibility** | Create `dev_setup.sh` and a strict lockfile for all dependencies. | Consistency | `chore(env): add reproducible dev setup and lockfile` |
| **3** | **Sovereign Scrub** | 1. Sanitize secrets/`.env`/`.gitignore`. <br> 2. **AnyIO Absolute Purge**: Remove all `asyncio` and blocking I/O in `src/`. | **AnyIO Absolute** | `security(core): sanitize secrets and AnyIO hardening` |
| **4** | **Arsenal Alignment** | 1. Align Iris extras and model paths. <br> 2. Wire `CURRENT_MODELS.md` as the source of truth for `ModelGateway`. | **Engine-Stack Firewall** | `chore(deps): align arsenal and pin dev versions` |
| **5** | **Sovereign Seal** | 1. Archive legacy repos. <br> 2. Scaffold `config/wads/` for `.xoe` transition. <br> 3. Implement `SovereignLock` for `soul.yaml`. | **Gnosis Preservation** | `refactor(org): archive legacy and scaffold WADs` |
| **6** | **Orchestration Activation** | Update Workbench DB to prioritize the **Triage Router** and **Health Monitor** (R60). | **Sovereign Logic** | (Database Update) |

## 🛡️ Verification Protocol (Temple-Grade)

A task is only "Done" when the following are verified:
1.  **AnyIO Audit**: `grep -r "asyncio" src/` returns zero results.
2.  **Test Integrity**: `make test` passes in both `mock` and `live` modes.
3.  **Security Seal**: No plain-text keys in any committed file; `.env` is strictly ignored.
4.  **WAD Readiness**: `config/wads/` structure exists and matches the R60 spec.
5.  **Lattice Update**: All changes are distilled into `session_gnosis.md` and the `Sovereign_Lattice.md`.

**Toggled to ACT MODE: Execute immediately.**
