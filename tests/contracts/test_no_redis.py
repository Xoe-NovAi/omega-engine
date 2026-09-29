# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M29 / D-redis-20260928 — the engine must import and run with NO redis present.

Why this test exists
--------------------
Redis was `*:6379` on this box for a month and no gate saw it. Then the
Architect ruled it deprecated entirely. The removal could silently regress in
two ways:

  1. someone re-adds `import redis` behind a try/except, and the engine again
     depends on an external service that nothing gates;
  2. someone re-creates the env-var gate (OMEGA_REDIS_HOST) that made the hot
     storage tier switchable — the live re-creation vector, because ONE env var
     was sufficient to bring a non-loopback `*:6379` connection back.

Both are invisible to a suite that only runs on a machine where redis already
happens to be absent. That is why this file has TWO halves:

  * `test_redis_package_is_absent` — the environment precondition, asserted so
    a machine WITH redis installed fails loudly here instead of silently
    passing the import checks.
  * `test_no_reachable_code_imports_redis` — a source-level sweep. This half
    runs REGARDLESS of whether the package is installed, which is what makes
    it a real gate rather than a property of one machine.

Falsification standard (the same one I imposed on TestCriticalTools):
a gate that has only ever passed is untested. See the module docstring of
`tests/test_hub_health.py` for the 20-skip defect this standard exists to
prevent.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Modules that were redis-dependent and must import cleanly without it.
# This list is itself the regression record — if you add a module here, you are
# adding a redis dependency, and the Architect's ruling says you may not.
REDIS_FREE_MODULES = [
    "omega.memory.providers",
    "omega.memory",
    "omega.memory_store",
    "omega.governance.budget_guard",
    "omega.research.hivemind_bridge",
    "omega.coordination.watchdog",
    "omega.workers.youtube_worker",
    "omega.ingestion.pipeline",
    "omega.ingestion.cli",
]

# The env vars that used to switch the redis tier on. None may be read by
# reachable code. Names are matched as substrings so `OMEGA_REDIS_HOST`,
# `OMEGA_REDIS_PORT` and `OMEGA_REDIS_PASSWORD` are all caught.
FORBIDDEN_ENV_TOKENS = ("OMEGA_REDIS",)


def _live_python_files():
    """Every .py under src/ that is live code (excludes backups and caches)."""
    for path in (REPO_ROOT / "src").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        # `.backup.<ts>` files are pre-refactor snapshots. They are not live
        # code and are deliberately not swept — see the Architect's ruling.
        if ".backup." in path.name:
            continue
        yield path


def test_redis_package_is_absent():
    """PRECONDITION: the redis package must not be importable in this venv.

    Fails loudly if someone `pip install`s redis into the working venv. That is
    a legitimate action, but it silently disables every other check in this
    file, so it must be visible rather than absorbed.
    """
    spec = importlib.util.find_spec("redis")
    assert spec is None, (
        "the `redis` package IS importable in this venv — every import check in "
        "this file becomes vacuous. M29 requires redis to be absent. If you just "
        "installed it deliberately, uninstall it or run this file in a clean env."
    )


def test_redis_is_not_declared_as_a_dependency():
    """pyproject must not offer a redis extra, and must not depend on redis."""
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    # Allow the historical note, forbid an actual dependency/extra.
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        lowered = stripped.lower()
        assert not (("redis" in lowered) and (
            "dependencies" in lowered
            or "optional-dependencies" in lowered
            or lowered.startswith("redis")
            or '"redis' in lowered
            or "'redis" in lowered
        )), f"pyproject declares a live redis dependency/extra: {stripped!r}"


@pytest.mark.parametrize("module_name", REDIS_FREE_MODULES)
def test_module_imports_without_redis(module_name):
    """Each formerly-redis module must import on a core-only install.

    M1-adjacent: this is the check that would have caught a hoisted
    `import redis` breaking the module at import time.
    """
    # Guard: if redis somehow became importable, the import below would succeed
    # for the wrong reason and this test would prove nothing.
    assert importlib.util.find_spec("redis") is None, (
        f"{module_name}: redis is importable — this assertion is vacuous"
    )
    __import__(module_name)


def test_no_reachable_code_imports_redis():
    """SOURCE SWEEP — the load-bearing gate.

    Runs whether or not the package is installed. Scans every live .py under
    src/ for the import forms that the removal was supposed to eliminate.
    """
    import_forms = (
        "import redis",
        "from redis",
        "redis.asyncio",
        "StrictRedis",
        "aioredis",
    )
    offenders = []
    for path in _live_python_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue  # a removal note is provenance, not a dependency
            for form in import_forms:
                if form in line:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {stripped}")
    assert not offenders, (
        "live src/ code still references a redis import form:\n  "
        + "\n  ".join(offenders)
    )


def test_no_reachable_code_reads_redis_env_vars():
    """The env-var re-creation vector must be closed.

    This is the check for TASK 5 of the removal dispatch: a single
    OMEGA_REDIS_HOST was enough to re-create a non-loopback redis connection.
    Reading the variable is how that switch came back.
    """
    offenders = []
    for path in _live_python_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for token in FORBIDDEN_ENV_TOKENS:
                if token in line:
                    offenders.append(
                        f"{path.relative_to(REPO_ROOT)}:{lineno}: {stripped}"
                    )
    assert not offenders, (
        "live src/ code still reads a redis env var — the re-creation vector "
        "is open:\n  " + "\n  ".join(offenders)
    )


# `src/omega/tools/check_hardcoded_secrets.py` is a SECRET SCANNER: it holds
# `redis://` as a *regex pattern* so it can flag one in someone else's code.
# That is the opposite of a dependency, and a gate that flagged it would
# pressure someone into deleting a security check. Excluded by module path,
# with the reason recorded so the exclusion is auditable rather than a blanket
# hole in the sweep.
DETECTOR_MODULES = {
    Path("src") / "omega" / "tools" / "check_hardcoded_secrets.py",
}


def test_no_redis_url_literals_in_live_code():
    """No `redis://` connection string may survive in live src/ code."""
    offenders = []
    for path in _live_python_files():
        if path.relative_to(REPO_ROOT) in DETECTOR_MODULES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "redis://" in line:
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {stripped}")
    assert not offenders, (
        "live src/ code still contains a redis:// URL:\n  "
        + "\n  ".join(offenders)
    )


def test_storage_chain_has_no_redis_tier():
    """`MemoryStore` must not reference a redis provider or the env gate.

    Specific to the group-A removal: the chain is USM -> File -> InMemory, and
    the OMEGA_REDIS_* switch is gone. This is the assertion that fails if
    someone reintroduces the branch "just for a hot tier".
    """
    text = (REPO_ROOT / "src" / "omega" / "memory_store.py").read_text(encoding="utf-8")
    live = [
        ln.strip()
        for ln in text.splitlines()
        if not ln.strip().startswith("#")
    ]
    joined = "\n".join(live)
    assert "RedisStorageProvider" not in joined, (
        "memory_store.py still references RedisStorageProvider in live code"
    )
    assert "OMEGA_REDIS" not in joined, (
        "memory_store.py still reads an OMEGA_REDIS_* env var in live code — "
        "the re-creation vector is open"
    )


def test_ingestion_worker_module_is_gone():
    """`omega.ingestion.worker` (SovereignWorker) was deleted with Redis.

    The class was architecturally redis-dependent: its constructor hard-raised
    without the package, and nothing referenced it.
    """
    spec = importlib.util.find_spec("omega.ingestion.worker")
    assert spec is None, (
        "omega.ingestion.worker still exists — it was a Redis-only background "
        "worker and was removed under the Architect's ruling"
    )


def test_engine_imports_in_a_fresh_interpreter_with_redis_hidden():
    """Subprocess proof: a clean interpreter with `redis` blocked imports the engine.

    Stronger than the in-process import checks because it rules out a module
    that only works because something else already imported it. `redis` is
    blocked via a meta_path finder that raises ImportError on sight, which
    simulates an install where the package is genuinely unavailable — not one
    where it merely hasn't been imported yet.
    """
    script = (
        "import sys\n"
        "class _Block:\n"
        "    def find_module(self, name, path=None):\n"
        "        return self.find_spec(name, path)\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'redis' or name.startswith('redis.'):\n"
        "            raise ImportError('redis is blocked by M29 test')\n"
        "        return None\n"
        "sys.meta_path.insert(0, _Block())\n"
        "import omega.memory_store, omega.memory.providers\n"
        "import omega.research.hivemind_bridge\n"
        "import omega.governance.budget_guard\n"
        "s = omega.memory.providers\n"
        "assert not hasattr(s, 'RedisStorageProvider'), 'RedisStorageProvider still exported'\n"
        "print('ENGINE_IMPORTS_CLEAN')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(Path.home()),
            "PYTHONPATH": str(REPO_ROOT / "src"),
        },
    )
    assert result.returncode == 0, (
        "engine failed to import with redis blocked:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "ENGINE_IMPORTS_CLEAN" in result.stdout, result.stdout
