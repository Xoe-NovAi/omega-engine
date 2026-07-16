import pytest
from pathlib import Path
import tempfile
import json
import os
from scripts.codex_cat import generate_codex

class TestCodexCat:
    def test_generate_codex(self, tmp_path):
        # Create test files in tmp_path
        (tmp_path / "FILE1.md").write_text("# File 1\nContent 1")
        (tmp_path / "FILE2.md").write_text("# File 2\nContent 2")
        
        # Create scripts directory and groups.json
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        groups = {"test": ["FILE1.md", "FILE2.md"]}
        (scripts_dir / "groups.json").write_text(json.dumps(groups))
        
        # Run generation with tmp_path as root
        out_file = tmp_path / "OMEGA_CODEX.md"
        generate_codex(root=tmp_path, out_file=out_file)
        
        assert out_file.exists()
        content = out_file.read_text()
        assert "FILE1.md" in content
        assert "FILE2.md" in content
        assert "Type" in content
        assert "Size" in content
        assert "Lines" in content

    def test_header_injection(self, tmp_path):
        (tmp_path / "TEST.md").write_text("# Test\nContent")
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        groups = {"test": ["TEST.md"]}
        (scripts_dir / "groups.json").write_text(json.dumps(groups))
        
        out_file = tmp_path / "OMEGA_CODEX.md"
        generate_codex(root=tmp_path, out_file=out_file)
        
        content = out_file.read_text()
        assert "### TEST.md" in content
        assert "**Type**: markdown" in content
        assert "**Size**:" in content
        assert "**Lines**:" in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
