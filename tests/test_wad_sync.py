# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Tests for WAD dual-tree sync (config/wads/ == src/omega/config_data/wads/)."""

import hashlib
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[1]
CONFIG_WADS = REPO / "config" / "wads"
PACKAGED_WADS = REPO / "src" / "omega" / "config_data" / "wads"


def _file_hashes(directory: Path) -> dict:
    """Return {relative_path: sha256} for all files in directory."""
    hashes = {}
    for f in sorted(directory.rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(directory))
            hashes[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
    return hashes


def test_config_wads_exists():
    assert CONFIG_WADS.is_dir(), "config/wads/ missing"


def test_packaged_wads_exists():
    assert PACKAGED_WADS.is_dir(), "src/omega/config_data/wads/ missing"


def test_wad_trees_identical():
    """config/wads/ and src/omega/config_data/wads/ must be byte-identical."""
    config_hashes = _file_hashes(CONFIG_WADS)
    packaged_hashes = _file_hashes(PACKAGED_WADS)
    assert config_hashes == packaged_hashes, (
        f"WAD trees differ. "
        f"Only in config: {set(config_hashes) - set(packaged_hashes)}. "
        f"Only in packaged: {set(packaged_hashes) - set(config_hashes)}. "
        f"Changed: {[k for k in config_hashes if k in packaged_hashes and config_hashes[k] != packaged_hashes[k]]}"
    )


def test_same_wad_names():
    """Both trees must have the same WAD directories."""
    config_wads = {d.name for d in CONFIG_WADS.iterdir() if d.is_dir()}
    packaged_wads = {d.name for d in PACKAGED_WADS.iterdir() if d.is_dir()}
    assert config_wads == packaged_wads, f"WAD sets differ: config={config_wads}, packaged={packaged_wads}"