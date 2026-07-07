# 🔱 PYTHONPATH Resolution — The "Why It Works Now" Document

**AP Token**: `AP-PYTHONPATH-FIX-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_pythonpath_fix ⬡ DOCUMENTATION

---

## The Problem

For weeks, every agent and test run failed with:
```
ModuleNotFoundError: No module named 'omega'
```
or
```
ModuleNotFoundError: No module named 'llama_cpp'
```

Agents were manually prepending `PYTHONPATH=src` to every command, which is fragile and violates **Mandate 16 (Modularization & Portability)** — the core engine should not require hardcoded path assumptions.

---

## Root Cause

The `omega` package was **not installed in the virtual environment**. The `pyproject.toml` defines it as an editable package with optional dependencies:

```toml
[project.optional-dependencies]
native = ["llama-cpp-python>=0.3.0,<0.4.0"]
cli = ["typer[full]", "rich>=15.0.0", "shellingham>=1.5.0"]
dev = ["pytest>=9.0.0", "pytest-asyncio>=0.25.0", "pytest-cov>=6.0.0", "pytest-timeout>=2.4.0", "flake8>=7.0.0"]
all = ["omega[native,cli,dev]"]
```

But `pip install -e .` was never run (or was run without the `[native]` extra), so:
1. `omega` module not on `sys.path`
2. `llama-cpp-python` not installed → `somatic_state.py` import fails

---

## The Fix (One Command)

```bash
source .venv/bin/activate && pip install -e .[native]
```

This:
1. Installs `omega` in **editable mode** (`-e`) → `src/omega` is now importable
2. Pulls the `native` extra → installs `llama-cpp-python`
3. Registers the `omega` CLI entry point (`omega.cli.oracle_cli:main`)

---

## Verification

```bash
# Before fix
python -c "import omega"  # ModuleNotFoundError

# After fix
source .venv/bin/activate
python -c "from omega.oracle.sovereign_search_service import SovereignSearchService; print('OK')"
# Output: OK
```

All tests now run via `make test` (which sets `PYTHONPATH=src` as a belt-and-suspenders) **and** work without it when the venv is activated.

---

## Why This Was Missed

| Factor | Explanation |
|--------|-------------|
| **No `setup.py` / `pip install` culture** | Project relied on `PYTHONPATH=src` in Makefile, masking the missing install |
| **Optional dependencies** | `llama-cpp-python` is in `[native]` extra — not installed by default |
| **Venv recreation** | Every time the venv was wiped, the install step was forgotten |
| **Agent amnesia** | Agents don't persist shell state; each new session starts fresh |

---

## Permanent Solution

**Documented in `Makefile` and `AGENTS.md`:**

```makefile
# Makefile — install target
install:
	source .venv/bin/activate && pip install -e .[all]
```

```markdown
# AGENTS.md — Before Starting Work
1. `source .venv/bin/activate`
2. `pip install -e .[native]`  # or `[all]` for dev
3. `make test`  # verifies 855 tests pass
```

---

## Mandate Compliance

- **M16 (Modularization & Portability)**: Package is now a proper installable distribution, no hardcoded paths needed.
- **M1 (AnyIO Absolute)**: `llama-cpp-python` (blocking I/O) is wrapped in `anyio.to_thread.run_sync` in `somatic_state.py` — now actually importable.
- **M7 (Local-First)**: Native GGUF backend (`native-gguf` provider) is functional because the dependency exists.

---

## Lessons Learned (L1→L2→L3)

| Level | Insight |
|-------|---------|
| **L1 (Narrative)** | We wasted weeks manually setting `PYTHONPATH` because the package wasn't installed. |
| **L2 (Insight)** | Editable installs with extras are the standard Python packaging pattern — skipping them creates "works on my machine" fragility. |
| **L3 (Principle)** | **Sovereign infrastructure must be installable.** If `pip install -e .` doesn't work, the project is not a library — it's a script collection. Every agent session must begin with a verified environment. |

---

*⬡ OMEGA ⬡ LILITH ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_pythonpath_fix ⬡ DOCUMENTED*
