#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""G11 — Clean-environment artifact verification.

Verifies the built wheel from a CLEAN environment outside the repo checkout:
- Creates a fresh venv in a temp directory
- Installs the wheel into it
- Runs config resolution assertion from a non-repo directory
- Runs the smoke command (OMEGA_PROVIDER=mock omega talk ...)
- Asserts zero mutation of the checkout (git status unchanged)

This would have caught the first wheel bug (FileNotFoundError on
config/embedding_strategy.yaml) because the repo-relative config path
would not exist in the clean environment.

AP: AP-G11-CLEANVER-v1.0.0
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class CleanVerifyError(Exception):
    """Raised when clean verification fails (exit 1)."""
    pass


def run_cmd(cmd: list[str], cwd: Path, env: dict | None = None, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command with clean environment."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    # Ensure PYTHONPATH doesn't leak repo
    merged_env.pop("PYTHONPATH", None)
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=merged_env,
        capture_output=capture,
        text=True,
        timeout=120,
    )


def get_git_status(repo_root: Path) -> str:
    """Get git status --porcelain output."""
    result = run_cmd(["git", "status", "--porcelain"], repo_root, capture=True)
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(
        description="G11 — Clean-environment artifact verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  Clean verification passed
  1  Verification failed (config missing, smoke failed, repo mutated)
  2  Usage error or setup error
""",
    )
    parser.add_argument(
        "--wheel",
        required=True,
        help="Path to the built wheel (.whl file)",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--smoke-cmd",
        default="omega list-entities",
        help="Smoke command to run (default: 'omega list-entities')",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0 (AP-G11-CLEANVER-v1.0.0)",
    )

    args = parser.parse_args()

    wheel_path = Path(args.wheel).resolve()
    repo_root = Path(args.repo_root).resolve()

    if not wheel_path.is_file():
        print(f"G11 ERROR: Wheel not found at {wheel_path}", file=sys.stderr)
        return 2

    if not (repo_root / ".git").is_dir():
        print(f"G11 ERROR: Not a git repository: {repo_root}", file=sys.stderr)
        return 2

    # Capture git status BEFORE
    status_before = get_git_status(repo_root)

    # Create temp directory for clean environment
    with tempfile.TemporaryDirectory(prefix="omega-clean-verify-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        venv_dir = tmpdir_path / "venv"
        work_dir = tmpdir_path / "work"
        work_dir.mkdir(parents=True, exist_ok=True)

        print(f"G11: Creating clean venv at {venv_dir}")
        result = run_cmd([sys.executable, "-m", "venv", str(venv_dir)], tmpdir_path)
        if result.returncode != 0:
            raise CleanVerifyError(f"Failed to create venv: {result.stderr}")

        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"

        print(f"G11: Installing wheel {wheel_path.name}")
        result = run_cmd([str(venv_pip), "install", str(wheel_path)], tmpdir_path)
        if result.returncode != 0:
            raise CleanVerifyError(f"Failed to install wheel: {result.stderr}")

        # Verify the installed package is from site-packages, not the repo
        result = run_cmd(
            [str(venv_python), "-c", "import omega; print(omega.__file__)"],
            work_dir,
        )
        if result.returncode != 0:
            raise CleanVerifyError(f"Failed to import omega: {result.stderr}")
        omega_file = result.stdout.strip()
        if str(repo_root) in omega_file:
            raise CleanVerifyError(
                f"omega imported from repo ({omega_file}), not from site-packages. "
                f"Clean environment test invalid."
            )
        print(f"G11: omega imported from {omega_file}")

        # Assert config resolution finds packaged configs via CONFIG_DIR
        config_check_script = """
import sys
from pathlib import Path
from omega.governance.config_resolver import CONFIG_DIR, get_active_iwad

print(f"CONFIG_DIR = {CONFIG_DIR}")
print(f"CONFIG_DIR exists = {CONFIG_DIR.is_dir()}")

required = [
    "embedding_strategy.yaml",
    "models.yaml",
    "omega.yaml",
    "provider_capabilities.yaml",
    "providers.yaml",
]
missing = []
for f in required:
    p = CONFIG_DIR / f
    if not p.is_file():
        missing.append(f)
    else:
        print(f"  FOUND: {p}")

# Check IWAD
iw = get_active_iwad()
wad_path = CONFIG_DIR / "wads" / iw
print(f"Active IWAD = {iw}")
print(f"WAD path = {wad_path}")
print(f"WAD exists = {wad_path.is_dir()}")
if not wad_path.is_dir():
    missing.append(f"iwads/{iw}")

if missing:
    print("MISSING:", ", ".join(missing))
    sys.exit(1)
print("All packaged configs resolved via CONFIG_DIR")
"""

        print("G11: Verifying config resolution from clean environment...")
        result = run_cmd([str(venv_python), "-c", config_check_script], work_dir)
        if result.returncode != 0:
            raise CleanVerifyError(f"Config resolution failed:\n{result.stdout}\n{result.stderr}")
        print(result.stdout)

        # Run smoke command from non-repo directory
        print(f"G11: Running smoke command: {args.smoke_cmd}")
        # The installed console script is at venv/bin/omega
        omega_bin = venv_dir / "bin" / "omega"
        if not omega_bin.is_file():
            raise CleanVerifyError(f"Console script not found at {omega_bin}")

        # Parse the smoke command using shlex to handle quotes properly
        smoke_parts = shlex.split(args.smoke_cmd)
        # Replace 'omega' with the full path to the binary
        if smoke_parts and smoke_parts[0] == "omega":
            smoke_parts[0] = str(omega_bin)
        elif smoke_parts and smoke_parts[0] == "python" and len(smoke_parts) >= 3 and smoke_parts[1] == "-m" and smoke_parts[2] == "omega":
            # Handle 'python -m omega ...' form
            smoke_parts = [str(omega_bin)] + smoke_parts[3:]

        # Handle OMEGA_PROVIDER=mock prefix (env var assignment at start)
        env_extra = {}
        if smoke_parts and "=" in smoke_parts[0] and not smoke_parts[0].startswith("-"):
            k, v = smoke_parts[0].split("=", 1)
            env_extra[k] = v
            smoke_parts = smoke_parts[1:]

        result = run_cmd(smoke_parts, work_dir, env=env_extra)
        if result.returncode != 0:
            raise CleanVerifyError(f"Smoke command failed:\n{result.stdout}\n{result.stderr}")
        print(f"G11: Smoke command output: {result.stdout.strip()}")

    # Capture git status AFTER
    status_after = get_git_status(repo_root)

    if status_before != status_after:
        raise CleanVerifyError(
            f"Repository mutated during verification!\n"
            f"Before:\n{status_before or '(clean)'}\n"
            f"After:\n{status_after or '(clean)'}"
        )

    print("G11 PASS: Clean-environment verification successful")
    print("  - Config resolution via CONFIG_DIR works")
    print("  - Smoke command executes")
    print("  - Repository unchanged (git status clean)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CleanVerifyError as e:
        print(f"G11 FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as e:
        print(f"G11 ERROR: {e}", file=sys.stderr)
        sys.exit(2)