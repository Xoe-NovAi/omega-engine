# Gap R56: Lazy Loading

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** UO-6 Phase 1 (startup performance / optional-dep deferral)
**Status:** ✅ RESOLVED (re-research — prior R56 report was LOST during 2026-08-14 reconciliation)

## Summary
Lazy loading defers a module's import until first use. The engine currently runs **Python 3.12** (per AGENTS.md), so the new `lazy import` keyword (PEP 810, Python 3.15, stable Oct 2026) is **not yet available**. Today use **function-level imports** or `importlib.util.LazyLoader`. This unblocks UO-6 Phase 1 by keeping heavy optional deps (prometheus_client, structlog, pybreaker, qdrant-client, gradio) out of the import-time path.

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| PEP 810 (lazy imports) | https://pydevtools.com/handbook/explanation/what-is-pep-810/ | 2026-05-08 | Accepted Nov 2025, 3.15 beta1 May 2026, stable Oct 2026 |
| Python 3.15 lazy imports | https://modernpython.io/python-3-15-lazy-imports-faster-startup-times-and-the-design-behind-pep-810/ | 2026-06-16 | `lazy import`, `-X lazy_imports=all`, `__lazy_modules__` |
| PEP 810 benchmarked | https://www.danilchenko.dev/posts/python-lazy-imports/ | 2026-07-24 | 8× startup win on boto3; LazyLoader today |
| importlib docs | https://docs.python.org/3/library/importlib.html | 2026 | `importlib.util.LazyLoader` |

## Findings
- **PEP 810 (3.15)**: `lazy import pandas as pd` defers real import until first attribute access; soft keyword; module scope only; `sys.set_lazy_imports("all"|"normal"|"none")` for process-wide modes; `__lazy_modules__` list as a 3.14-compatible shim. Steering Council accepted 2025-11-03; 3.15.0b1 shipped 2026-05-07; stable targeted 2026-10.
- **Today (3.12) option A — function-level import**: move `import prometheus_client` inside the function that uses it. Downside: scatters imports (Ruff `E402`/`PLC0415`); PEP 810 exists to fix exactly this.
- **Today (3.12) option B — `importlib.util.LazyLoader`**:
  ```python
  import importlib.util, sys
  def lazy(name):
      spec = importlib.util.find_spec(name)
      spec.loader = importlib.util.LazyLoader(spec.loader)
      mod = importlib.util.module_from_spec(spec)
      sys.modules[name] = mod
      spec.loader.exec_module(mod)   # returns immediately; work deferred
      return mod
  prometheus_client = lazy("prometheus_client")
  ```
  Keeps a top-level name, defers the heavy work. (Benchmark: ~51ms vs ~394ms for eager boto3 on the common path.)
- **Avoid**: global `-X lazy_imports=all` in production — it changes import-time side effects (logging setup, registration) fleet-wide.

## Recommendation
For UO-6 Phase 1, apply lazy loading to **heavy optional dependencies** so they don't load at engine startup:
1. On Python 3.12: prefer `importlib.util.LazyLoader` for top-level names (cleaner than scattered function imports), or function-level imports where the dep is used in one place.
2. When the engine moves to Python 3.15 (Oct 2026): switch to `lazy import` declarations — one-line, IDE/type-checker aware.
3. Do **not** enable global lazy-imports mode in production.
4. Audit which deps are truly optional/heavy (prometheus_client, structlog, pybreaker, qdrant-client, gradio) before wrapping — verify none rely on import-time side effects (logging config, decorator registration) that would break under deferral.

## Confidence
**HIGH** — PEP 810 status and the `importlib.util.LazyLoader` pattern are verified against official docs; the engine's Python version (3.12) is confirmed from AGENTS.md.

## Remaining Unknowns
- Which specific modules in the engine import heavy deps at top level (grep audit at impl time).
- Timeline for the engine's own Python 3.15 upgrade (gates the `lazy import` switch).
