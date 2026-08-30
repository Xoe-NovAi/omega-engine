<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N3 Vetting — Ma'at T1 Diff Plan (INST-1 fix2 completion)
**AP Token**: AP-N3-T1-VET-v1.0.0
⬡ OMEGA ⬡ MAAT ⬡ [N3] ⬡ big-pickle ⬡ opencode ⬡ trc_n3_t1_vet ⬡ 2026-08-23
**Page source**: Ma'at overseer (BUILD VETTING 2026-08-23) · **Deliverable vetted**: MAAT_DEBUT_BUILD_VETTING_20260823.md §T1

---

## Probe Evidence (all verified 2026-08-23)

| # | Probe | Result |
|---|-------|--------|
| P1 | `pip download llama-cpp-python==0.3.32 --only-binary :all:` | **FAILS** — "No matching distribution". No cp313 wheel on PyPI for 0.3.32 → fresh installs build from source (cmake/C++, est. 5–20 min on 5700U). |
| P2 | llama-cpp-python in current `.venv` | 0.3.32 installed and working (talk gate verified 2026-08-22 per ACTIVE_SPRINT gates.one_click_install). |
| P3 | youtube dep import sites | ALL lazy/function-level: `cli/youtube_cli.py:48`, `workers/youtube_worker.py:307`. Extras move safe; no guard needed beyond a helpful ImportError message. |
| P4 | redis module-level import sites | UNGUARDED at `memory/providers.py:22`, `ingestion/worker.py:7`, `workers/youtube_worker.py:47`. ALREADY GUARDED (canonical pattern): `governance/budget_guard.py:23-28` (`try/except ImportError` + `REDIS_AVAILABLE` flag). |
| P5 | CLI import chain reachability | `oracle_cli.py`, `oracle.py`, `omega/__init__.py` do NOT import ingestion.worker or workers.youtube_worker → unguarded sites there cannot break `omega talk`; they WILL break full pytest if redis leaves core deps and CI installs `.[cli,dev]` without `[redis]`. |
| P6 | qdrant-client consumer | Only `memory/vector_adapters.py` via `_lazy_qdrant()` (lazy, :16-25) — dep deletion safe pre-DEL-1; class deletion lands in T2 #5. |
| P7 | console_scripts | `[project.scripts] omega` (:98-99) untouched by extras moves — no entrypoint hazard. |
| P8 | cli extra duplication | `typer/rich/shellingham` pinned in CORE (:57,:69,:51) AND re-listed in `[cli]` extra (:79). Harmless today; post-debut cleanup candidate. |
| P9 | `src/omega/__init__.py` | importlib.metadata.version("omega") + hardcoded fallback "1.2.0" confirmed. |

## Verdicts

### Item 1 — pyproject deps move → **AMEND (minor)**
- youtube→[youtube]: APPROVE. All call sites already lazy (P3).
- redis→[redis]: APPROVE **conditional on item 2 amendment** (guard all three module-level sites, not just providers.py).
- qdrant-client delete: APPROVE. Sole consumer lazy-imported (P6); removing its grpc/pydantic pin pressure REDUCES resolver risk on 3.13.
- Hazards checked: console_scripts unaffected (P7); native/cli interplay clean (P8 duplication cosmetic); core-set shrink strictly reduces conflict surface.
- **AMEND**: add `redis` + `youtube` to `dev` extra (or CI workflow installs them) or full pytest goes red post-move (P5).

### Item 2 — HAS_REDIS module-level guard vs lazy import → **APPROVE pattern / AMEND scope**
Module-level try/except + OmegaError raise in `__init__` is correct: RedisStorageProvider must be importable (MemoryStore factory references it) while failing typed at construction (M9). Lazy-in-method would scatter the guard across get_history/save/check_health and break type annotations. Canonical reference already exists in-tree: budget_guard.py:23-28 — mirror it verbatim for consistency.
**AMEND**: plan names only providers.py; same guard required at `ingestion/worker.py:7` + `workers/youtube_worker.py:47` (P4/P5). Also delete `password="omega"` default as planned — confirmed still present at providers.py:119.

### Item 3 — verify_debut_install.sh → **AMEND**
Gaps:
1. **llama-cpp-python source build**: no cp313 wheel (P1) → pip step alone can exceed the 300s budget; needs gcc/cmake present. Add `command -v gcc && command -v cmake || fail-fast`; measure & record actual install seconds in T6 table before trusting "<300s".
2. **Model availability**: script bypasses install.sh, so nothing sets OMEGA_MODELS_DIR/downloads Qwen3 GGUF → step [6/6] can fail for environment reasons. Export OMEGA_MODELS_DIR to host model dir or add download step.
3. **Not a true fresh-clone gate**: editable install runs against working tree. Acceptable for warp-absence check (warp already out of core), but document the limitation or `git clone` to temp for full fidelity.
4. Minor: step [4] hardcodes "1.2.0" (3rd copy of literal) — acceptable for a pinning gate; note it.
Answer to direct question: install works on this host (0.3.32 proven), but NOT quickly/cleanly-by-wheel — it compiles.

### Item 4 — version fallback raise vs silent → **APPROVE as-is**
Fallback literal acceptable; PackageNotFoundError only occurs running from bare source tree. Raising at import time would break sphinx/docs/source-tree introspection AND make acceptance step [3/6] fail confusingly before [4/6] can diagnose. Optional hardening consistent with ICS B1/F5 precedent: emit `warnings.warn(...RuntimeWarning)` instead of silent pass. Do not raise.

## Lessons [N_3]
- l1: No cp313 wheel exists for llama-cpp-python 0.3.32; fresh venv installs compile from source (5-20 min).
- l2: Any dep moved to an extra requires auditing EVERY module-level import site, not just the one named in the ticket — redis had 3 unguarded sites; the ticket named 1.
- l3: An existing in-tree guard (budget_guard.py REDIS_AVAILABLE) should be mirrored, not reinvented — pattern consistency beats local cleverness.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: [N3] | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
