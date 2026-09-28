# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""MCP server import-smoke gate (Tier A) [maat 2026-09-27].

THE DEFECT THIS GATE EXISTS TO CATCH
------------------------------------
`mcp_servers/omega_hub/server.py:85` imported three symbols from
`mcp_servers.omega_hub.state`:

    _extended_sessions, _extended_sessions_lock, EXTENDED_SESSIONS_FILE

The Hivemind consolidation (15 tools -> 4) deleted all three from `state.py`.
`state.__all__` (state.py:601-636) listed only HEARTBEAT_TTL and
EXTENDED_SAFETY_TTL_DEFAULT. The daemon crash-looped on boot.

Meanwhile `make temple-grade` reported 53/53 PASS.

WHY TAMPER-GRADE COULD NOT SEE IT — two independent blind spots
---------------------------------------------------------------
1. WRONG FLAKE8 CODES. CI runs `flake8 --select=E9,F63,F7,F82`. F401
   (undefined/unused import) is NOT in that set.

2. PYFLAKES CANNOT DETECT THIS DEFECT CLASS ANYWAY. For
   `from mod import name`, pyflakes assumes `name` may be a submodule
   and never checks membership in `mod.__all__`. `__all__` only governs
   `from mod import *`. So even with F401 enabled, a deleted module-level
   symbol referenced by an explicit `from ... import ...` is invisible
   to pyflakes. Only actually EXECUTING the import catches it.

Point 2 is the load-bearing one. Fixing the flake8 selection would not
have saved us. Only import execution does.

PRECEDENT
---------
`tests/test_cli_smoke.py` (N1/dc-cli-dead, 2026-08-24) caught the same
class of failure for the `omega` console script. That gate was proven,
scoped to the CLI, and never extended to the MCP servers. This file is
that gate, extended.

Note the two mechanisms differ but the gate catches both:
  - CLI defect: LAZY registration (typer validates at invocation).
  - Hub defect: EAGER import (fails at the `from` statement).
Both are caught by executing the real entry point.

WHY AN EXPLICIT MODULE LIST, NEVER A GLOB
------------------------------------------
A `**/server.py` glob would also match:
  - data/entities/roc_racoon/workspace/hlmc_ore/gap4_mcp_auth/hub_server.py
    (carries the SAME stale `_extended_sessions` import at its line 84)
  - docs/hardening/omega-hub/server_monolith_snapshot_20260613.py
  - docs/hardening/omega-hub/claude-project/outbox/server-snapshot.py

The latter two are deliberate archaeology snapshots that MUST keep their
historical code. A glob gate would either false-positive forever or force
a skip-list that silently rots. A small named list is auditable; a
skip-list is not.

THE SECOND FAILURE THIS GATE CAUGHT — github_bridge
---------------------------------------------------
2026-09-28. The Hivemind consolidation deleted `hivemind_post_context`, but
`mcp_servers/omega_hub/github_bridge.py` still imported it directly from
`hub_tools`. Result: the whole GitHub webhook bridge was dead at import and
`pytest tests/test_github_bridge.py` collected 0 tests.

This slipped past the original 5-module list for the same reason the first
defect did: nobody asked which modules were live consumers of a renamed
symbol. The list has to grow whenever a consolidation renames anything, and
it has to be derived from the rename set — not from "the modules that
looked like daemons".

That asymmetry is real and worth stating: `server.py` had a legacy-name
shim covering the MCP tool surface, so the hub booted clean. But
`github_bridge.py` does a DIRECT PYTHON IMPORT from `hub_tools`, bypassing
that shim entirely. Two different compatibility mechanisms, only one of
which applies to in-process callers. A shim on the MCP surface is invisible
to a direct import.

M1 AnyIO: this file contains no `import asyncio`.
M23 Failure Integrity: a hung import is a FAILURE, not a pass. Every
    non-zero exit is reported with the underlying traceback tail.
"""

from __future__ import annotations

import subprocess
import sys
import time

import pytest

# Explicit list. Order matters only for readable output.
# See module docstring for why this is NOT a glob.
#
# `github_bridge` was added 2026-09-28 after it was found importing a deleted
# Hivemind tool name. It is a live consumer of the hub, not a daemon, which is
# exactly why the daemon-only list missed it.
HUB_MODULES = (
    "mcp_servers.omega_hub.server",
    "mcp_servers.omega_hub.state",
    "mcp_servers.omega_hub.hub_tools",
    "mcp_servers.omega_hub.github_bridge",
    "mcp_servers.searxng.server",
    "mcp_servers.firecrawl.server",
)

# Per-module budget. Hub import pulls in mcp + starlette + the service
# singletons, so this is generous on a cold interpreter. It exists to
# convert a HANG (a real defect: e.g. blocking on a lock or a network
# call at import time) into a hard failure rather than a CI stall.
IMPORT_TIMEOUT_S = 60

_STDERR_TAIL = 800


def _probe(module: str) -> subprocess.CompletedProcess:
    """Import `module` in a clean subprocess. Never raises on failure."""
    return subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        capture_output=True,
        text=True,
        timeout=IMPORT_TIMEOUT_S,
    )


@pytest.mark.parametrize("module", HUB_MODULES)
def test_hub_module_imports_cleanly(module: str) -> None:
    """Each MCP server module must import without raising.

    Asserts BOTH:
      1. returncode == 0
      2. "Traceback" not in stderr   <- lifted from test_cli_smoke.py:37

    Clause 2 is not redundant. A module can exit 0 and still print a
    traceback it swallowed internally (M23 violation elsewhere), and a
    module whose import raises but is caught by a top-level handler can
    exit 0 while being functionally dead. Clause 2 catches both.
    """
    started = time.perf_counter()
    try:
        result = _probe(module)
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"[TIMEOUT] {module} did not import within {IMPORT_TIMEOUT_S}s.\n"
            f"A hung import is a FAILURE, not a pass. Probable causes: blocking\n"
            f"call at import time, lock held by another process, or network I/O\n"
            f"in a module-level statement."
        )

    elapsed = time.perf_counter() - started

    if result.returncode != 0:
        pytest.fail(
            f"[IMPORT-FAILURE] {module} failed to import "
            f"(exit {result.returncode}, {elapsed:.1f}s).\n"
            f"--- stderr tail (last {_STDERR_TAIL} chars) ---\n"
            f"{result.stderr[-_STDERR_TAIL:]}\n"
            f"--- end stderr ---\n"
            f"Check for a `from ... import <symbol>` naming a symbol that no\n"
            f"longer exists in the target module."
        )

    if "Traceback" in result.stderr:
        pytest.fail(
            f"[TRACEBACK-ON-IMPORT] {module} imported (exit 0) but printed a\n"
            f"traceback to stderr — a swallowed failure (M23).\n"
            f"--- stderr tail (last {_STDERR_TAIL} chars) ---\n"
            f"{result.stderr[-_STDERR_TAIL:]}\n"
            f"--- end stderr ---"
        )

    print(f"[PASS] {module} imported cleanly in {elapsed:.1f}s")


def test_hub_module_list_is_explicit() -> None:
    """Guard the guard: the module list must stay explicit, never a glob.

    If someone 'simplifies' this to a filesystem glob, the archaeology
    snapshots under docs/hardening/ and the roc_racoon workspace copy
    come back into scope and the gate false-positives forever.
    """
    assert len(HUB_MODULES) == 6, (
        f"Expected 6 explicit MCP/hub modules, found {len(HUB_MODULES)}. "
        f"If the entry points changed, update this list deliberately."
    )
    for module in HUB_MODULES:
        assert module.startswith("mcp_servers."), (
            f"{module} is not an mcp_servers module — the list is meant to "
            f"cover hub entry points only."
        )
        assert "*" not in module, f"Glob pattern leaked into module list: {module}"


def test_passthrough_tools_exist() -> None:
    """Every _PASSTHROUGH_TOOLS name must exist in tools.py.

    This is the guard against the exact defect found 2026-09-28. The
    Hivemind consolidation deleted 9 awareness + 3 lock tools from tools.py
    but left their names in _PASSTHROUGH_TOOLS. __getattr__ resolves the
    name and then calls `getattr(_tools, name)`, which raised AttributeError
    on first INVOCATION — not at import. The hub booted clean, temple-grade
    reported 53/53, and the failure only surfaced when a real caller used
    the name.

    A passthrough entry is a promise that the symbol exists. This test makes
    the promise checkable instead of aspirational.
    """
    import mcp_servers.omega_hub.hub_tools.tools as tools
    from mcp_servers.omega_hub.server import _PASSTHROUGH_TOOLS

    dead = [n for n in sorted(_PASSTHROUGH_TOOLS) if not hasattr(tools, n)]
    assert not dead, (
        f"_PASSTHROUGH_TOOLS names symbols that no longer exist in tools.py: {dead}\n"
        f"__getattr__ will resolve the name and then raise AttributeError on call.\n"
        f"Either restore the symbol, or move the name into _LEGACY_TOOL_ADAPTERS\n"
        f"with a bound action."
    )


def test_legacy_adapters_all_resolve() -> None:
    """Every _LEGACY_TOOL_ADAPTERS entry must resolve to a real target+action.

    Covers both halves of the adapter: the target tool must exist, and the
    bound action must be one the target accepts. A typo'd action name fails
    only when a caller invokes the legacy name.
    """
    import mcp_servers.omega_hub.hub_tools.tools as tools
    from mcp_servers.omega_hub.server import _LEGACY_TOOL_ADAPTERS

    problems = []
    for legacy, (target, bound) in sorted(_LEGACY_TOOL_ADAPTERS.items()):
        if not hasattr(tools, target):
            problems.append(f"{legacy} -> missing target tool '{target}'")
            continue
        action = bound.get("action")
        if action is not None:
            # Cheap static check: the action string must appear in the target's
            # docstring, which enumerates its valid actions.
            doc = getattr(tools, target).__doc__ or ""
            if action not in doc:
                problems.append(
                    f"{legacy} -> action '{action}' not listed in {target}.__doc__"
                )
    assert not problems, "legacy adapter problems:\n  " + "\n  ".join(problems)


def test_github_bridge_posts_via_unified_tool() -> None:
    """github_bridge must not reference any removed Hivemind tool name.

    Static source check. github_bridge was dead at import for a full day
    because it imported the deleted `hivemind_post_context` directly from
    hub_tools, bypassing the server.py legacy shim. The import-smoke entry
    above now catches that at import time; this catches a reintroduction
    even if the name were to exist again but be semantically wrong.
    """
    import inspect

    import mcp_servers.omega_hub.github_bridge as gb

    src = inspect.getsource(gb)
    removed = [
        "hivemind_post_context",
        "hivemind_heartbeat",
        "hivemind_get_awareness",
        "hivemind_get_continuation",
        "hivemind_workspace_lock_acquire",
        "hivemind_workspace_lock_release",
        "hivemind_workspace_lock_check",
    ]
    # Strip comment lines so the explanatory docstring is not a false positive.
    code_only = "\n".join(
        ln for ln in src.splitlines() if not ln.strip().startswith("#")
    )
    hits = [n for n in removed if n in code_only]
    assert not hits, (
        f"github_bridge references removed Hivemind tool name(s): {hits}. "
        f"Use hivemind_awareness(action=...) instead."
    )
