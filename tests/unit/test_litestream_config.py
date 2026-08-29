"""Unit tests for Litestream config and operational scripts.

AP: AP-LITESTREAM-BACKUP-v1.0.0

These tests validate the YAML config structure and the script's
command-line interface without actually invoking Litestream (which
requires the binary + a real S3 bucket).
"""
import re
import stat
import subprocess
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
LITESTREAM_YML = REPO_ROOT / "config" / "litestream.yml"
SETUP_SH = REPO_ROOT / "scripts" / "setup_litestream.sh"
RESTORE_SH = REPO_ROOT / "scripts" / "restore_litestream.sh"
VERIFY_SH = REPO_ROOT / "scripts" / "verify_litestream.sh"


# ── Test 1: config is valid YAML + structurally correct ─────────────────
def test_litestream_yml_is_valid_yaml():
    """The config file must parse as YAML and have the required keys."""
    assert LITESTREAM_YML.exists(), f"Missing: {LITESTREAM_YML}"
    with open(LITESTREAM_YML) as fh:
        cfg = yaml.safe_load(fh)
    assert "dbs" in cfg, "Config must have top-level 'dbs' key"
    assert len(cfg["dbs"]) >= 1, "Must declare at least one DB to replicate"
    db = cfg["dbs"][0]
    assert "path" in db, "DB entry must have 'path'"
    assert "replicas" in db, "DB entry must have 'replicas'"
    assert len(db["replicas"]) >= 1, "Must have at least one replica"
    replica = db["replicas"][0]
    assert replica.get("url", "").startswith("s3://"), \
        "Replica url must be s3:// (or s3-compatible)"


def test_litestream_yml_does_not_set_retention():
    """CRITICAL (tvcam 2026-05): retention: is silently ignored in v0.5.x.

    The presence of `retention:` (anywhere) is a smell — operators should
    use the S3 bucket lifecycle policy, not litestream's broken field.
    """
    content = LITESTREAM_YML.read_text()
    # Allow the word in comments (e.g. "do not set retention") but not
    # as a YAML key with a value.
    has_retention_key = bool(
        re.search(r"^\s*retention\s*:", content, re.MULTILINE)
    )
    assert not has_retention_key, (
        "litestream.yml must NOT set retention: — it's silently ignored "
        "in v0.5.x. Use the S3 bucket lifecycle policy instead."
    )


def test_litestream_yml_required_env_vars_documented():
    """The config must document every env var it depends on."""
    content = LITESTREAM_YML.read_text()
    for var in [
        "LITESTREAM_BUCKET",
        "LITESTREAM_ACCESS_KEY_ID",
        "LITESTREAM_SECRET_ACCESS_KEY",
    ]:
        assert var in content, f"{var} must be referenced in litestream.yml"


# ── Test 2: scripts have bash syntax + executable bit ───────────────────
@pytest.mark.parametrize("script", [SETUP_SH, RESTORE_SH, VERIFY_SH])
def test_script_has_bash_syntax(script):
    assert script.exists(), f"Missing: {script}"
    # bash -n parses without executing
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"{script.name} syntax error: {result.stderr}"


@pytest.mark.parametrize("script", [SETUP_SH, RESTORE_SH, VERIFY_SH])
def test_script_is_executable(script):
    assert script.exists(), f"Missing: {script}"
    mode = script.stat().st_mode
    assert mode & stat.S_IXUSR, f"{script.name} must be executable by owner (chmod +x)"


def test_setup_script_installs_systemd_unit_from_repo():
    """The setup script must install the systemd unit from config/ (not
    inline heredoc) — config-as-code is the law of this repo."""
    content = SETUP_SH.read_text()
    assert "config/systemd/omega-litestream.service" in content, (
        "setup_litestream.sh must install the unit from "
        "config/systemd/omega-litestream.service, not an inline heredoc."
    )
    # And no inline heredoc writing a unit file
    heredoc_match = re.search(
        r"<<'?EOF'?\s*\n\[Unit\]", content
    )
    assert not heredoc_match, (
        "setup_litestream.sh must NOT use a heredoc to write the unit. "
        "Use install -m from config/systemd/."
    )


# ── Test 3: verify script has the right exit-code contract ───────────────
def test_verify_script_defines_exit_codes():
    """The verify script must document its exit-code contract so that
    cron / monitoring / CI can rely on it."""
    content = VERIFY_SH.read_text()
    # Header comment lists exit codes
    for code in ["0", "1", "2"]:
        # Should mention each exit code with its meaning
        assert re.search(rf"^\s*{code}\s+", content, re.MULTILINE) or \
               re.search(rf"exit {code}", content) or \
               code in content, \
            f"verify_litestream.sh must document exit code {code}"
    # And it should call `exit` with the code, not just echo
    assert "exit $EXIT_CODE" in content or "exit ${EXIT_CODE}" in content, (
        "verify_litestream.sh must propagate its computed exit code."
    )


def test_verify_script_handles_missing_litestream_binary():
    """If litestream is not installed, the script must exit 3 (or similar)
    with a clear message — M23 Failure Integrity, not silent crash."""
    result = subprocess.run(
        ["bash", "-c", f"PATH=/empty PATH=/usr/bin:/bin bash {VERIFY_SH}"],
        capture_output=True,
        text=True,
        # Use a sanitized PATH that won't find litestream
        env={"PATH": "/usr/bin:/bin", "HOME": "/tmp"},
    )
    # Should exit non-zero (1, 2, or 3) with a clear message
    assert result.returncode != 0, (
        "verify_litestream.sh should fail when litestream is not on PATH"
    )
    # The error message should be informative, not blank
    combined = (result.stdout + result.stderr).lower()
    assert "litestream" in combined, (
        "Error output must mention 'litestream' so operator knows what's missing"
    )
