# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""D-565 regression: the public cut has no `src/omega/vault/`.

`src/omega/vault/` is FORGE on the public allowlist cut (D-565). Retained core
code used to hard-import it at MODULE scope:

    src/omega/library/discovery.py
        from omega.vault import VaultCore          # line 32

`mcp_servers/omega_hub/state.py` imports `DiscoveryOrchestrator` at module
scope, and `make temple-grade` -> `check-hub-imports` imports
`mcp_servers.omega_hub.state` inside a CLEAN worktree. The hard import
therefore made `make temple-grade` fail with

    ModuleNotFoundError: No module named 'omega.vault'

on every allowlist cut — including the already-published `release/debut`
(3c051021), which has been failing M13 since it was cut.

These tests simulate the cut by making `omega.vault` genuinely unimportable
inside a child interpreter, then assert:

  1. `omega.library.discovery` imports cleanly,
  2. it reports the degradation (`VAULT_AVAILABLE is False`, `VaultCore is None`),
  3. `DiscoveryOrchestrator` constructs and resolves NO credentials,
  4. the non-vault discovery surface returns correct results,
  5. `omega.cli.vault` also imports cleanly and fails fast with a D-565 message,
  6. structurally: NO module anywhere under `src/omega/` may import
     `omega.vault` at module scope without an ImportError guard.

Assertion 6 is the durable one — it fails the moment someone re-introduces an
unguarded import, regardless of whether the rest of the suite runs.

D-565 IS NOT WEAKENED: vault is still cut, still absent, still the single
source of truth for credentials whenever it is present. These tests only
require that its ABSENCE be survivable.
"""

import ast
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Child-interpreter preamble: block `omega.vault` at the import-system level.
# This is a faithful simulation of the public cut — not a monkeypatch of a
# symbol — because on a real cut the module genuinely does not exist.
_VAULT_BLOCKER = """
import sys

class _VaultAbsent:
    \"\"\"Meta-path finder that makes `omega.vault` unimportable.\"\"\"

    def find_spec(self, name, path=None, target=None):
        if name == "omega.vault" or name.startswith("omega.vault."):
            raise ModuleNotFoundError(
                "No module named " + repr(name), name=name
            )
        return None

sys.meta_path.insert(0, _VaultAbsent())
sys.path.insert(0, __SRC__)
"""


def _run_without_vault(body: str) -> dict:
    """Execute `body` in a child interpreter where omega.vault cannot import.

    Returns the JSON the child printed on its last stdout line. Raises
    AssertionError with the child's stderr if it died before printing.
    """
    src = str(REPO_ROOT / "src")
    script = _VAULT_BLOCKER.replace("__SRC__", repr(src)) + textwrap.dedent(body)
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=180,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert lines, (
        f"child interpreter produced no result\n"
        f"--- returncode: {proc.returncode}\n"
        f"--- stdout:\n{proc.stdout}\n"
        f"--- stderr:\n{proc.stderr}"
    )
    return json.loads(lines[-1])


# ── 1. import surface ───────────────────────────────────────────────────────


def test_discovery_imports_cleanly_without_vault():
    """The gate-breaker: `import omega.library.discovery` must not raise."""
    out = _run_without_vault(
        """
        import json
        import omega.library.discovery as d
        print(json.dumps({"ok": d.__name__}))
        """
    )
    assert out["ok"] == "omega.library.discovery"


def test_vault_symbols_degrade_to_none():
    """No half-bound vault symbols — absence is explicit and inspectable."""
    out = _run_without_vault(
        """
        import json
        import omega.library.discovery as d
        print(json.dumps({
            "vault_available": d.VAULT_AVAILABLE,
            "vault_core": d.VaultCore,
        }))
        """
    )
    assert out["vault_available"] is False, "VAULT_AVAILABLE must be False without vault"
    assert out["vault_core"] is None, "VaultCore must be None without vault"


# ── 2. orchestrator construction ───────────────────────────────────────────


def test_orchestrator_constructs_and_resolves_no_credentials():
    """__init__ must degrade to no-keys, not raise.

    Before the fix the vault block caught only (OmegaError, KeyError), so a
    missing module propagated ModuleNotFoundError out of __init__.
    """
    out = _run_without_vault(
        """
        import json, tempfile
        import os
        os.environ["OMEGA_DATA_DIR"] = tempfile.mkdtemp()
        from unittest.mock import MagicMock
        import omega.library.discovery as d
        o = d.DiscoveryOrchestrator(model_gateway=MagicMock())
        print(json.dumps({
            "exa_key": o.exa_key,
            "firecrawl_key": o.firecrawl_key,
            "jobs": o._jobs,
        }))
        """
    )
    assert out["exa_key"] is None, "no vault => no exa key"
    assert out["firecrawl_key"] is None, "no vault => no firecrawl key"
    assert out["jobs"] == {}, "job store must be usable and start empty"


# ── 3. non-vault discovery results are still correct ───────────────────────


def test_non_vault_discovery_returns_correct_results():
    """The non-vault path must produce a well-formed, persisted result.

    Covers the vault-independent surface that a public user can actually
    reach: start a job, read its status back, and confirm it was persisted
    with a correct status mapping.
    """
    out = _run_without_vault(
        """
        import anyio, json, tempfile, os
        os.environ["OMEGA_DATA_DIR"] = tempfile.mkdtemp()
        from unittest.mock import MagicMock
        import omega.library.discovery as d

        async def main():
            o = d.DiscoveryOrchestrator(model_gateway=MagicMock())
            job_id = await o.start_discovery("what is sovereign inference")
            status = o.get_job_status(job_id)
            path = o._job_path(job_id, status["status"])
            return {
                "job_id": job_id,
                "query": status["query"],
                "status": status["status"],
                "keys": sorted(status.keys()),
                "persisted": path.is_file(),
                "persisted_query": json.loads(path.read_text())["query"],
                "path_matches_run_dir": path.parent.name == "running",
                "unknown_job": o.get_job_status("does-not-exist"),
            }

        print(json.dumps(anyio.run(main)))
        """
    )
    assert out["query"] == "what is sovereign inference"
    assert out["status"] == "running"
    assert out["persisted"] is True, "job must be persisted to disk"
    assert out["persisted_query"] == "what is sovereign inference"
    assert out["path_matches_run_dir"] is True, "running jobs live in JOBS_RUNNING_DIR"
    assert out["unknown_job"] == {"status": "not_found"}
    for key in ("created_at", "final_synthesis", "sources", "subtopics"):
        assert key in out["keys"], f"DiscoveryReport.to_dict() must expose {key}"


def test_report_round_trips_through_disk():
    """A non-vault DiscoveryReport survives a write/read cycle unchanged."""
    out = _run_without_vault(
        """
        import json, tempfile, os
        os.environ["OMEGA_DATA_DIR"] = tempfile.mkdtemp()
        import omega.library.discovery as d
        r = d.DiscoveryReport(query="q", status="pending", recon_summary="rs")
        p = d.DATA_DIR / "jobs" / "pending" / "rt.json"
        p.write_text(json.dumps(r.to_dict()))
        back = json.loads(p.read_text())
        print(json.dumps({"query": back["query"], "status": back["status"],
                          "recon": back["recon_summary"]}))
        """
    )
    assert out == {"query": "q", "status": "pending", "recon": "rs"}


# ── 4. the vault CLI must also survive the cut ──────────────────────────────


def test_vault_cli_imports_cleanly_without_vault():
    out = _run_without_vault(
        """
        import json
        import omega.cli.vault as v
        print(json.dumps({
            "vault_available": v.VAULT_AVAILABLE,
            "commands": sorted(v.vault.commands.keys()),
        }))
        """
    )
    assert out["vault_available"] is False
    # The click group must still be constructible — decorators evaluate
    # click.Choice([x.value for x in ProviderName]) at import time, so a
    # missing enum would have raised here.
    assert "init" in out["commands"], "vault CLI surface must still be registered"


def test_vault_cli_fails_fast_with_d565_message():
    """Commands refuse loudly instead of half-running without a vault."""
    out = _run_without_vault(
        """
        import json, os
        os.environ["OMEGA_VAULT_PASSPHRASE"] = "x"   # skip the interactive prompt
        from click.testing import CliRunner
        import omega.cli.vault as v

        runner = CliRunner()
        res = runner.invoke(v.vault, ["init", "--vault-dir", "/tmp/maat-no-vault-xyz"])
        print(json.dumps({
            "exit_code": res.exit_code,
            "output": res.output,
            "mentions_d565": "D-565" in (res.output or ""),
        }))
        """
    )
    assert out["exit_code"] != 0, "vault command must not succeed without vault"
    assert out["mentions_d565"] is True, "error must name D-565 so the cause is obvious"


# ── 5. structural guard against re-introduction ─────────────────────────────


def _module_scope_vault_imports(path: Path) -> list[str]:
    """Return `omega.vault` imports at MODULE scope (not inside a try)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    guarded: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type is None:
                    continue  # bare `except:` — not ImportError-specific
                exc = handler.type
                names = (
                    [exc.id] if isinstance(exc, ast.Name)
                    else [e.id for e in exc.elts if isinstance(e, ast.Name)]
                    if isinstance(exc, ast.Tuple) else []
                )
                if "ImportError" in names or "ModuleNotFoundError" in names:
                    guarded.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))

    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        mod = node.module or ""
        if not (mod == "omega.vault" or mod.startswith("omega.vault.")):
            continue
        if node.lineno not in guarded:
            offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}: from {mod} import ...")
    return offenders


@pytest.mark.parametrize(
    "relpath",
    [
        "src/omega/library/discovery.py",
        "src/omega/cli/vault.py",
        "src/omega/cli/oracle_cli.py",
        "src/omega/oracle/orchestrator.py",
        "src/omega/oracle/search_providers.py",
    ],
)
def test_no_unguarded_module_scope_vault_import(relpath: str):
    """No unguarded `from omega.vault...` at module scope in cut-retained code."""
    offenders = _module_scope_vault_imports(REPO_ROOT / relpath)
    assert offenders == [], (
        "unguarded module-scope omega.vault import — ModuleNotFoundError on "
        "every public cut (D-565):\n  " + "\n  ".join(offenders)
    )


def test_call_site_vault_imports_all_guard_import_error():
    """EVERY `from omega.vault...` in cut-retained code must be ImportError-guarded.

    Covers both scopes, because both break on a cut:

      * module scope  -> `import omega.library.discovery` raises
                          ModuleNotFoundError, which fails the clean-worktree
                          `check-hub-imports` temple-grade gate;
      * call scope    -> ImportError escapes a handler that catches only
                          (OmegaError, RuntimeError, OSError), crashing the
                          caller at RUNTIME instead of degrading.

    "Guarded" means lexically inside a `try` whose handler names ImportError,
    ModuleNotFoundError, Exception, or BaseException. Nothing else counts.
    """
    offenders = []
    for path in sorted((REPO_ROOT / "src" / "omega").rglob("*.py")):
        if "vault" in path.parts:
            continue  # src/omega/vault/** is itself FORGE (D-565)
        rel = path.relative_to(REPO_ROOT)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        # Line ranges covered by a try whose handlers tolerate ImportError.
        guarded: set[int] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            catches = any(
                isinstance(h, ast.ExceptHandler)
                and h.type is not None
                and any(
                    getattr(t, "id", getattr(t, "attr", None))
                    in ("ImportError", "ModuleNotFoundError", "Exception", "BaseException")
                    for t in (h.type.elts if isinstance(h.type, ast.Tuple) else [h.type])
                )
                for h in node.handlers
            )
            if catches:
                guarded.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            mod = node.module or ""
            if not (mod == "omega.vault" or mod.startswith("omega.vault.")):
                continue
            if node.lineno in guarded:
                continue
            scope = "module scope" if any(node is s for s in tree.body) else "call scope"
            offenders.append(f"{rel}:{node.lineno}: {scope}: from {mod} import ...")

    assert offenders == [], (
        "omega.vault import that can raise ModuleNotFoundError on a public cut "
        "(D-565):\n  " + "\n  ".join(offenders)
    )