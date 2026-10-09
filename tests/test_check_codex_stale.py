# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
import tempfile
import json
import subprocess
import sys
import shutil

class TestCheckCodexStale:
    def setup_method(self):
        # Copy the scripts directory to a temp location for testing
        self.repo_root = Path(__file__).parent.parent
        self.scripts_dir = self.repo_root / "scripts"

    def _setup_test_env(self, tmp_path):
        """Copy scripts and create test files in tmp_path."""
        # Copy scripts directory
        test_scripts = tmp_path / "scripts"
        shutil.copytree(self.scripts_dir, test_scripts)
        
        # Create test files
        (tmp_path / "FILE1.md").write_text("# File 1\nContent 1")
        (tmp_path / "FILE2.md").write_text("# File 2\nContent 2")
        
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        groups = {"test": ["FILE1.md", "FILE2.md"]}
        (scripts_dir / "groups.json").write_text(json.dumps(groups))
        (scripts_dir / "hydration_header.md").write_text("# Header\n{{TIMESTAMP}}")
        
        return tmp_path

    def test_fresh_codex_passes(self, tmp_path):
        """Test that a fresh codex passes the check."""
        test_root = self._setup_test_env(tmp_path)
        
        # Generate codex
        out_file = tmp_path / "OMEGA_CODEX.md"
        subprocess.run([
            sys.executable, "scripts/codex_cat.py"
        ], cwd=tmp_path, check=True, capture_output=True)
        
        # Check passes
        result = subprocess.run([
            sys.executable, "scripts/check_codex_stale.py"
        ], cwd=tmp_path, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Codex is fresh" in result.stdout

    def test_stale_codex_fails(self, tmp_path):
        """Test that a stale codex fails the check."""
        test_root = self._setup_test_env(tmp_path)
        
        # Generate codex
        subprocess.run([
            sys.executable, "scripts/codex_cat.py"
        ], cwd=tmp_path, check=True, capture_output=True)
        
        # Modify a source file
        (tmp_path / "FILE1.md").write_text("# File 1\nModified Content")
        
        # Check should fail
        result = subprocess.run([
            sys.executable, "scripts/check_codex_stale.py"
        ], cwd=tmp_path, capture_output=True, text=True)
        
        assert result.returncode == 1
        assert "Codex is stale" in result.stdout

    def test_fix_regenerates(self, tmp_path):
        """Test that --fix regenerates the codex."""
        test_root = self._setup_test_env(tmp_path)
        
        # Generate codex
        subprocess.run([
            sys.executable, "scripts/codex_cat.py"
        ], cwd=tmp_path, check=True, capture_output=True)
        
        # Modify a source file
        (tmp_path / "FILE1.md").write_text("# File 1\nModified Content")
        
        # Run with --fix
        result = subprocess.run([
            sys.executable, "scripts/check_codex_stale.py", "--fix"
        ], cwd=tmp_path, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "regenerated" in result.stdout.lower() or "fresh" in result.stdout.lower()

    def test_force_regenerates(self, tmp_path):
        """Test that --force always regenerates."""
        test_root = self._setup_test_env(tmp_path)
        
        # Generate codex
        subprocess.run([
            sys.executable, "scripts/codex_cat.py"
        ], cwd=tmp_path, check=True, capture_output=True)
        
        # Run with --force
        result = subprocess.run([
            sys.executable, "scripts/check_codex_stale.py", "--force"
        ], cwd=tmp_path, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "regenerat" in result.stdout.lower() or "fresh" in result.stdout.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])