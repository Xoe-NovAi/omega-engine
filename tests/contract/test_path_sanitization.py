# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract Tests — P2-5 Path Traversal Sanitization.

Verifies entity_name/session_id can never escape the memory data dir via
path construction. The `sanitize_path_component()` canonical sanitizer is
applied at every path-construction site in the memory layer.

[P2-5 / §4 audit] Path traversal via `../`, absolute paths, null bytes and
OS path metacharacters is a denial-of-service/data-escape vector.
[T10: Integrity] Sanitized components resolve strictly inside the base dir.
"""

from pathlib import Path

import pytest

from omega.memory.providers import (
    FileStorageProvider,
    sanitize_path_component,
)


class TestSanitizer:
    """Direct unit tests for the canonical sanitizer."""

    @pytest.mark.parametrize(
        "evil",
        [
            "../evil",
            "../../etc/passwd",
            "..",
            "a/b\\c",
            "a\\b",
            "bad\x00name",
            "/etc/passwd",
            ".../x",
            "a/../b",
            "%2e%2e%2f",
        ],
    )
    def test_component_never_escapes_base_dir(self, tmp_path: Path, evil: str):
        safe = sanitize_path_component(evil)
        candidate = (tmp_path / safe).resolve()
        base = tmp_path.resolve()
        assert candidate == base or base in candidate.parents, (
            f"{evil!r} sanitized to {safe!r} which escapes base dir"
        )
        assert ".." not in safe
        assert "/" not in safe and "\\" not in safe
        assert "\x00" not in safe

    def test_normal_names_preserved(self):
        assert sanitize_path_component("john_carmack") == "john_carmack"
        assert sanitize_path_component("John Carmack") == "john_carmack"

    def test_empty_returns_placeholder(self):
        assert sanitize_path_component("") == "_unset"
        assert sanitize_path_component(None) == "_unset"

    def test_length_capped(self):
        assert len(sanitize_path_component("x" * 500)) == 128


class TestFileProviderPaths:
    """FileStorageProvider builds safe filesystem paths."""

    def test_entity_path_traversal_blocked(self, tmp_path: Path):
        provider = FileStorageProvider(tmp_path)
        path = provider._entity_path("../evil", "sess-001")
        # entity component sanitized; must be under data_dir/entities
        assert path.parts[-2] == "_evil"  # "../evil" -> "_evil"
        assert path.parts[-1] == "sess-001.json"
        assert str(path).startswith(str(tmp_path.resolve()))

    def test_archive_path_traversal_blocked(self, tmp_path: Path):
        provider = FileStorageProvider(tmp_path)
        path = provider._archive_path("normal-entity", "../../escape")
        assert path.parts[-1] == "_escape.json.gz"
        assert ".." not in str(path)
        assert str(path).startswith(str(tmp_path.resolve()))

    def test_session_id_traversal_blocked(self, tmp_path: Path):
        provider = FileStorageProvider(tmp_path)
        path = provider._entity_path("entity", "../../etc/passwd")
        assert path.parts[-1] == "_etc_passwd.json"
        assert ".." not in str(path)
        assert str(path).startswith(str(tmp_path.resolve()))
