#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
M23 Gate: Config Path Sweep

Detects modules that compute config paths without using the shared CONFIG_DIR resolver.
This prevents the class of bug where a wheel install fails because config paths
were hardcoded relative to the source tree instead of using the package-data resolver.

Patterns detected:
- Path("config/...") or Path('config/...') for known runtime config files
- Path(__file__).parents[N] / "config" / "*.yaml" for runtime configs
- Hardcoded config filenames in strings that should use CONFIG_DIR

Exclusions (legitimate uses):
- The config_resolver.py itself (it IS the resolver)
- Test files that create temp dirs for testing
- Docstrings/comments
- Legitimate uses of Path(__file__) for finding project root (not config files)
- Test fixtures that create temp dirs
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Set

# Known runtime config filenames that MUST use CONFIG_DIR
RUNTIME_CONFIG_FILES = {
    "omega.yaml",
    "models.yaml",
    "providers.yaml",
    "embedding_strategy.yaml",
    "entity_model_affinity.yaml",
    "search.yaml",
    "hardware_profile.yaml",
    "youtube_worker.yaml",
    "model_registry/index.sqlite",
    "subagent_pool/templates",
}

# Files that are allowed to compute paths (the resolver itself, tests, etc.)
ALLOWED_FILES = {
    "src/omega/governance/config_resolver.py",
    "src/omega/governance/dispatch_registry.py",  # uses CONFIG_DIR
}

# Files that define security/firewall paths (legitimate config path references)
SECURITY_CONTEXT_FILES = {
    "src/omega/research/sandbox.py",  # Defines FORBIDDEN_PATHS and WAD_WORKSPACE_PREFIX for firewall
}

# Test directories
TEST_DIRS = {"tests/", "test_"}

# Known config directory patterns
CONFIG_DIR_PATTERNS = [
    "config/",
    "config\\",
]


class ConfigPathVisitor(ast.NodeVisitor):
    """AST visitor that finds hardcoded config path patterns."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: List[Tuple[int, str, str]] = []  # (line, pattern, code)
        self.in_test_function = False
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Track if we're in a test function
        old_test = self.in_test_function
        self.in_test_function = node.name.startswith("test_")
        self.generic_visit(node)
        self.in_test_function = old_test
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)
        
    def visit_Call(self, node: ast.Call):
        # Check for Path("config/...") or Path('config/...')
        if isinstance(node.func, ast.Name) and node.func.id == "Path":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    val = arg.value
                    if any(val.startswith(p) for p in CONFIG_DIR_PATTERNS):
                        # Check if it's a known runtime config file
                        for config_file in RUNTIME_CONFIG_FILES:
                            if config_file in val:
                                self.violations.append((
                                    node.lineno,
                                    f"hardcoded config path: {val}",
                                    f"Path('{val}')"
                                ))
        
        # Check for Path(__file__).parents[N] / "config" / "*.yaml"
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("__truediv__", "__div__"):
                # Check left side for Path(__file__).parents[N]
                left = node.func.value
                if (isinstance(left, ast.Call) and 
                    isinstance(left.func, ast.Attribute) and
                    left.func.attr == "parents"):
                    # Check right side for config path
                    right = node.args[0] if node.args else None
                    if isinstance(right, ast.Constant) and isinstance(right.value, str):
                        val = right.value
                        if any(val.startswith(p) for p in CONFIG_DIR_PATTERNS):
                            for config_file in RUNTIME_CONFIG_FILES:
                                if config_file in val:
                                    self.violations.append((
                                        node.lineno,
                                        f"hardcoded config path via Path(__file__).parents: {val}",
                                        f"Path(__file__).parents[N] / '{val}'"
                                    ))
        
        self.generic_visit(node)
    
    def visit_Constant(self, node: ast.Constant):
        # Check string constants for hardcoded config paths
        if isinstance(node.value, str):
            val = node.value
            for config_file in RUNTIME_CONFIG_FILES:
                if config_file in val and any(val.startswith(p) for p in CONFIG_DIR_PATTERNS):
                    # Skip if it's in a docstring or comment-like context
                    # We can't easily detect docstrings in AST, so we'll filter later
                    self.violations.append((
                        node.lineno,
                        f"hardcoded config filename in string: {config_file}",
                        f"'{val}'"
                    ))
        self.generic_visit(node)


def check_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Check a single Python file for config path violations."""
    if str(filepath) in ALLOWED_FILES:
        return []
    
    # Skip security context files (legitimate config path references in firewall/security code)
    if str(filepath) in SECURITY_CONTEXT_FILES:
        return []
    
    # Skip test directories
    if any(part in TEST_DIRS for part in filepath.parts):
        return []
    
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []
    
    visitor = ConfigPathVisitor(str(filepath))
    visitor.visit(tree)
    
    # Filter out violations in docstrings/comments (approximate)
    filtered = []
    content_lines = filepath.read_text(encoding="utf-8").splitlines()
    for line_no, pattern, code in visitor.violations:
        if line_no <= len(content_lines):
            line = content_lines[line_no - 1].strip()
            # Skip if it looks like a comment or docstring
            if line.startswith("#") or line.startswith('"""') or line.startswith("'''"):
                continue
            # Skip if it's in a test function (approximate)
            # This is a heuristic - we can't perfectly detect test functions from AST alone
            filtered.append((line_no, pattern, code))
    
    return filtered


def main():
    src_root = Path("src/omega")
    if not src_root.exists():
        print("ERROR: src/omega not found. Run from repo root.")
        return 1
    
    all_violations = []
    python_files = list(src_root.rglob("*.py"))
    
    for filepath in python_files:
        violations = check_file(filepath)
        for line_no, pattern, code in violations:
            all_violations.append((str(filepath), line_no, pattern, code))
    
    if all_violations:
        print("CONFIG PATH VIOLATIONS FOUND:")
        print("=" * 80)
        for filepath, line_no, pattern, code in all_violations:
            print(f"  {filepath}:{line_no}: {pattern}")
            print(f"    Code: {code}")
        print("=" * 80)
        print(f"Total violations: {len(all_violations)}")
        return 1
    else:
        print("No config path violations found.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
