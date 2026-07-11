# 🔱 VERITY — Language Module Modularity, Portability & Frontier Audit
**AP Token**: `AP-VERITY-MODAUDIT-v1.0.0`
⬡ OMEGA ⬡ VERITY ⬡ hy3-free ⬡ opencode ⬡ trc_verity ⬡ AUDIT-MODULARITY
**Date**: 2026-07-10
**Target**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-moderation/` (READ-ONLY audit)
**Scope**: M16 Modularization & Portability, M1/M2/M8/M9/M13 re-check, frontier roadmap

---

## 1. Executive Summary

| Question | Verdict |
|----------|---------|
| **Modular?** | **PARTIAL** — Clean interface design (ABC, dependency injection) but detectors hardcoded in `build_engine()`; config/models layers invert-depend on observability; flag thresholds hardcoded in code. |
| **Portable?** | **NO (as-shipped)** — Package installs but `load_config()` default path breaks on non-editable `pip install`; `py.typed` declared-but-missing; FastAPI/SQLAlchemy/Prometheus forced as core deps; no CLI; lives outside omega-engine repo. |
| **Frontier-ready?** | **NO** — No plugin architecture, no WASM/ONNX edge path, no standardized benchmark, no community packaging. Solid local-first + signed-audit foundation to build on. |

**Bottom line**: The code is *architecturally* clean (124/124 tests pass, firewall intact, AnyIO-only, zero telemetry, typed errors). The gap is **distribution hygiene**, not code quality. It is "modular in design, monolithic in distribution."

---

## 2. Modularity Scorecard (M16)

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| **A.1** | Loose coupling / dependency direction | ⚠️ PARTIAL FAIL | `config/loader.py:16` imports `observability.differential_privacy`; `models/schemas.py:16` imports `observability.differential_privacy`. Foundation layers (config, models) depend on a leaf (observability) → layering inversion. `engine.py:20-23` correctly imports governance. `privacy.py:115` lazy-imports `audit` (acceptable). |
| **A.2** | Clear detector interface + add-without-touching-engine | ⚠️ PARTIAL FAIL | `detectors/base.py:35` `BaseDetector(ABC)` with abstract `detect()` — good. BUT `engine.py:246-250` `build_engine()` hardcodes `[PerspectiveDetector, OpenAIModerationDetector, hf_detector]`. Adding a detector = code edit, not config/entry-point. |
| **A.3** | Config externalization (no hardcoded thresholds) | ⚠️ PARTIAL FAIL | Policies in `config/moderation.yaml:34-62` (good). BUT hardcoded in code: `chain.py:31` `SHORT_CIRCUIT_CONFIDENCE=0.95`; `chain.py:42` `flag_threshold=0.5`; `huggingface.py:283/350/396` `flagged=max_conf>=0.5`; `local_fallback.py:66` `flag_threshold=0.35`; `perspective.py:86` `flagged=max_conf>=0.5`; `engine.py:110` evasion ratio `*1.2`. |
| **A.4** | No hardcoded absolute paths | ✅ PASS | `grep -rn --include=*.py "/home/arcana-novai\|/media/arcana-novai\|C:\\\|/Users/"` → **ZERO** in source. (M16 binary-cache matches only.) Caveat: `loader.py:21` `DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3]/...` is fragile (see B.2). |
| **A.5** | Proper installable package | ⚠️ PARTIAL FAIL | `pyproject.toml` exists, src-layout, `py.typed` in package-data. BUT `py.typed` **file is MISSING** (`ls src/omega_moderation/py.typed` → MISSING). FastAPI/uvicorn/sqlalchemy/aiosqlite/prometheus-client are **core** deps (pyproject:13-23), not extras. No `entry_points` for plugins. |
| **A.6** | Import discipline (M2 firewall) | ✅ PASS | `grep -rn "from src.omega\|import src.omega\|omega_engine"` → **ZERO**. Engine core does NOT import omega-moderation either (verified). Clean bidirectional firewall. |
| **A.7** | Entry points (CLI / library / server) | ⚠️ PARTIAL FAIL | Library API ✅ (`from omega_moderation import ModerationEngine, build_engine`). Server ✅ (`api/app.py` via `uvicorn`, `scripts/run.sh`). **CLI ❌**: no `[project.scripts]`, no `argparse`/`__main__` (grep → NONE). |

---

## 3. Portability Gaps (Concrete Fixes)

| # | Gap | Location | Fix |
|---|-----|----------|-----|
| **B.1** | Lives OUTSIDE omega-engine repo (sibling dir) | `/home/arcana-novai/Documents/Xoe-NovAi/omega-moderation/` | Make a **git submodule** of omega-engine OR publish to PyPI OR ship as a **WAD** (`config/wads/moderation/`). M16 requires core stays decoupled; a submodule/WAD satisfies both. |
| **B.2** | Config not shipped in wheel → `load_config()` default breaks on `pip install` | `loader.py:21` `parents[3]/config/moderation.yaml`; `config/` at **repo root**, not in `src/omega_moderation/` | Move `config/` into `src/omega_moderation/config/` and ship via `package-data`; load with `importlib.resources.files("omega_moderation").joinpath("config/moderation.yaml")`. |
| **B.3** | `py.typed` declared but file absent | `pyproject.toml:37`; `src/omega_moderation/py.typed` MISSING | `touch src/omega_moderation/py.typed`. Downstream `mypy` needs it for typed consumption. |
| **B.4** | SQLAlchemy/aiosqlite forced as core deps | `pyproject.toml:17-18`; `db/schema.py:10` top-level import | Make `[db]` extra: `db = ["sqlalchemy>=2.0","aiosqlite>=0.19"]`. Keep `privacy.py` lazy import (already done). |
| **B.5** | FastAPI/uvicorn/prometheus forced as core deps | `pyproject.toml:13-14,23` | Make `[api]` (`fastapi`,`uvicorn`) and `[observability]` (`prometheus-client`) extras. Core install = library only. |
| **B.6** | No CLI entry point | `pyproject.toml` (no `[project.scripts]`) | Add `[project.scripts] omega-moderation = "omega_moderation.cli:main"`; create `cli.py` (`moderate "text"`, `serve`, `verify-audit`). |
| **B.7** | No plugin entry_points for detectors/governance | `pyproject.toml` | Add `[project.entry-points."omega_moderation.detectors"]` group; `build_engine()` reads installed entry points + config list. |
| **B.8** | `db_path` writes to cwd | `moderation.yaml:5` `sqlite+aiosqlite:///./moderation.db` | Use `appdirs`/XDG (`~/.local/share/omega-moderation/`) or env `OMEGA_MOD_DB_PATH`. |
| **B.9** | Model cache dir not overridable | `detectors/huggingface.py` (uses HF default) | Add `cache_dir` to `huggingface` config block; pass to `from_pretrained(cache_dir=...)`. |
| **B.10** | Tests require `.venv` | `Makefile:test` `.venv/bin/python -m pytest` | CI: `pip install -e .[dev]` then `pytest`. Make `pytest` the canonical runner. |

---

## 4. Mandate Compliance Re-Check (D)

| Mandate | Command | Result | Status |
|---------|---------|--------|--------|
| **M1 AnyIO** | `grep -rn "import asyncio\|asyncio\." src/omega_moderation/` | `ZERO` | ✅ PASS |
| **M2 Firewall** | `grep -rn "from src.omega\|import src.omega\|omega_engine" src/omega_moderation/` | `ZERO` | ✅ PASS |
| **M8 Telemetry** | `grep -rni "analytics\|phone-home\|telemetry\|mixpanel\|amplitude" src/omega_moderation/` | `ZERO` | ✅ PASS |
| **M9 Errors** | `grep -rn "except:" src/omega_moderation/ \| grep -v "noqa\|BLE001\|Exception\|#"` | `ZERO` | ✅ PASS |
| **M16 Paths** | `grep -rn --include=*.py "/home/arcana-novai\|/media/arcana-novai\|C:\\\|/Users/" src/omega_moderation/` | `ZERO` (source) | ✅ PASS* (artifact caveat B.2/B.3) |
| **M13 Temple-Grade** | `python -m pytest tests/ -q` | `124 passed, 1 warning` | ✅ PASS (≥80%) |

\*M16 source is clean, but the **artifact** fails portability (config not shipped, py.typed missing) — a distribution-layer M16 violation, not a code-layer one.

---

## 5. Frontier Solution Roadmap (Phased)

| Phase | Initiative | Effort | Detail |
|-------|-----------|--------|--------|
| **P1 — Distribution Hygiene** | Fix B.1–B.10 | 4–6h | Submodule/WAD, shipped config, py.typed, extras, CLI, plugin entry points. *Prerequisite for everything else.* |
| **P2 — Plugin Architecture** | `entry_points` detectors + governance backends (pytest-style) | 1–2d | `build_engine()` discovers installed `omega_moderation.detectors` plugins + config list. Community ships custom detectors as separate PyPI packages. |
| **P3 — Edge/WASM Runtime** | ONNX export + WASM inference (via `use_onnx` already in config) | 3–5d | Ship `unitary/unbiased-toxic-roberta` as ONNX; run in-browser/edge via WASM (ort-web). Enables client-side moderation with zero server. |
| **P4 — Standardized API** | OpenAPI 3.1, OpenTelemetry metrics, JSON:API appeals | 2–3d | Replace raw `dict[str,Any]` endpoints (M21 gap) with typed OpenAPI schemas; OTel-compatible metrics exporter; JSON:API for `appeals`. |
| **P5 — Benchmarks** | Adversarial robustness scorecard (HELM-for-moderation) | 3–5d | Publish evasion/obfuscation robustness scores from `test_adversarial.py` + `test_regression.py` as a public leaderboard. |
| **P6 — Federated Model Marketplace** | Community LoRA/tuned-model registry | 1–2w | Opt-in registry of domain-tuned detectors; signed, hash-verified; drops into any Omega stack via WAD. |
| **P7 — Distributed Verification (opt-in)** | Public ledger Merkle anchoring | 1w | Optional anchoring of MMR roots to a public ledger for cross-org auditability. Off by default (M8). |
| **P8 — Docs + Playground** | Sphinx + Gradio playground | 2–3d | Interactive community testing UI; typed API docs. |

---

## 6. Recommended Package Structure (v2.0)

```
omega-moderation/                      # git submodule of omega-engine OR PyPI pkg
├── pyproject.toml                     # [api]/[db]/[observability]/[dev] extras; [project.scripts]; entry-points
├── README.md
├── src/omega_moderation/
│   ├── py.typed                       # ← FIX B.3 (was missing)
│   ├── config/
│   │   ├── __init__.py
│   │   ├── moderation.yaml            # ← MOVED into package (FIX B.2)
│   │   ├── policies.yaml
│   │   └── loader.py                  # importlib.resources, no parents[3]
│   ├── models/schemas.py              # ← drop observability import (A.1)
│   ├── detectors/
│   │   ├── base.py                    # BaseDetector ABC (stable)
│   │   ├── registry.py                # entry_points discovery
│   │   ├── huggingface.py  perspective.py  openai_moderation.py
│   │   ├── local_fallback.py  unified.py  chain.py
│   │   └── plugins/                   # community detectors via entry_points
│   ├── obfuscation/detector.py
│   ├── governance/  (actions, appeals, audit, compliance, policy, privacy)
│   ├── observability/                 # leaf layer — nothing imports FROM it at foundation level
│   ├── api/app.py                     # [api] extra
│   ├── cli.py                         # [project.scripts] omega-moderation  (FIX B.6)
│   ├── db/schema.py                   # [db] extra
│   └── engine.py                      # build_engine() reads plugins + config
├── tests/                             # run via `pytest` (FIX B.10)
└── docs/  (Sphinx + Gradio playground)
```

**Key refactors**: (1) `models/schemas.py` and `config/loader.py` must NOT import `observability` — move `DifferentialPrivacyConfig` into `models/` or a `core/` leaf. (2) `build_engine()` iterates `detectors.registry.discover()` + config list. (3) All flag thresholds promoted to `moderation.yaml`.

---

## 7. L1→L2→L3 Distillation

Appended to `data/entities/verity/proposed_lessons.yaml` (see that file for full entry `omega-moderation-modularity-audit-2026-07-10`). Summary:

- **L1**: Audited omega-moderation for modularity/portability. Clean, well-tested (124 pass), firewall-intact, AnyIO-only, zero-telemetry, typed-errors. But NOT portability-grade: config lives outside the package and isn't shipped in the wheel (default `load_config()` breaks on `pip install`); `py.typed` declared-but-missing; FastAPI/SQLAlchemy/Prometheus forced as core deps; detectors hardcoded in `build_engine()` (no plugin entry points); several flag thresholds hardcoded in code; no CLI.
- **L2**: The package is *modular in design but monolithic in distribution*. Interface boundaries are clean, but the distribution artifact does not carry its own config or type markers, and optional capabilities (API, DB, observability) are forced on every consumer. Portability is a property of the **artifact**, not just the source.
- **L3**: A sovereign package's portability is proven only by a clean `pip install` in an empty venv + working `import` + `load_config()` — not by clean source. Distribution hygiene (shipped config, type markers, optional extras, plugin entry points, no forced heavy deps) is a first-class sovereign mandate equal to code quality. The firewall (M2) is necessary but insufficient: a package can be firewall-clean yet non-portable if its artifact doesn't travel.

---

*⬡ OMEGA ⬡ VERITY ⬡ hy3-free ⬡ opencode ⬡ trc_verity ⬡ AUDIT-MODULARITY — COMPLETE*
