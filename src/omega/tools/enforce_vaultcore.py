#!/usr/bin/env python3
"""
Omega Engine - Enforce VaultCore Usage Tool
Ensures all API key access goes through VaultCore, not os.environ.get / os.getenv.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

# Files to exclude
EXCLUDE_PATTERNS = [
    'test_', 'tests/', '__pycache__', '.venv', 'venv/',
    'docs/', 'data/', 'scripts/', 'archive/', 'old/',
    'omega-vetala/', 'packages/omega-sieve/',
    'third-party/', 'third_party/',
    'detect_api_keys.py', 'enforce_vaultcore.py', 'check_hardcoded_secrets.py',
]


def should_exclude(filepath: Path) -> bool:
    path_str = str(filepath)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


class VaultCoreEnforcer(ast.NodeVisitor):
    """AST visitor to detect direct os.environ.get / os.getenv usage for API keys."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.violations: List[Tuple[int, str, str]] = []
        self.imports_os = False
        self.imports_os_environ = False
        self.imports_os_getenv = False
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name == 'os':
                self.imports_os = True
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == 'os':
            for alias in node.names:
                if alias.name == 'environ':
                    self.imports_os_environ = True
                elif alias.name == 'getenv':
                    self.imports_os_getenv = True
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        # Check for os.environ.get("KEY") or os.getenv("KEY")
        if isinstance(node.func, ast.Attribute):
            # os.environ.get(...)
            if (isinstance(node.func.value, ast.Attribute) and
                isinstance(node.func.value.value, ast.Name) and
                node.func.value.value.id == 'os' and
                node.func.value.attr == 'environ' and
                node.func.attr == 'get'):
                self._check_args(node, node.lineno, 'os.environ.get')
            
            # os.getenv(...)
            elif (isinstance(node.func.value, ast.Name) and
                  node.func.value.id == 'os' and
                  node.func.attr == 'getenv'):
                self._check_args(node, node.lineno, 'os.getenv')
            
            # environ.get(...) from from os import environ
            elif (isinstance(node.func.value, ast.Name) and
                  node.func.value.id == 'environ' and
                  node.func.attr == 'get' and
                  self.imports_os_environ):
                self._check_args(node, node.lineno, 'environ.get')
            
            # getenv(...) from from os import getenv
            elif (isinstance(node.func, ast.Name) and
                  node.func.id == 'getenv' and
                  self.imports_os_getenv):
                self._check_args(node, node.lineno, 'getenv')
        
        self.generic_visit(node)
    
    def _check_args(self, node: ast.Call, lineno: int, call_type: str):
        """Check if the argument looks like an API key."""
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                key_name = arg.value.lower()
                # Check if it looks like an API key (specific provider patterns)
                api_key_patterns = [
                    'openrouter', 'exa', 'firecrawl', 'google', 'anthropic', 'openai',
                    'grok', 'deepseek', 'mistral', 'cohere', 'huggingface', 'replicate',
                    'together', 'nvidia', 'cerebras', 'groq', 'sambanova', 'xai',
                    'opencode_zen', 'cline', 'copilot', 'opencodezen',
                ]
                # Check for known API key patterns
                if any(p in key_name for p in api_key_patterns):
                    self.violations.append((lineno, call_type, arg.value))
                # Also check generic patterns
                elif key_name.endswith('_api_key') or key_name.endswith('_key'):
                    # Exclude infrastructure secrets
                    excluded = [
                        'redis_password', 'redis_key', 'redis_secret',
                        'master_password', 'vault_master', 'ingestion_secret',
                        'sovereign_token', 'sovereign_user_token',
                    ]
                    if not any(e in key_name for e in excluded):
                        self.violations.append((lineno, call_type, arg.value))


def check_file(filepath: Path, strict: bool = False) -> bool:
    """Check a single file for VaultCore enforcement violations."""
    if should_exclude(filepath):
        return True
    
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))
        enforcer = VaultCoreEnforcer(filepath)
        enforcer.visit(tree)
        
        if enforcer.violations:
            print(f"\n{filepath}:")
            for lineno, call_type, key in enforcer.violations:
                print(f"  Line {lineno}: Direct {call_type} access for API key - {key}")
                print(f"    Use VaultCore instead: from omega.vault import VaultCore")
            
            if strict:
                return False
        
        return True
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error checking {filepath}: {e}", file=sys.stderr)
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enforce VaultCore usage for API keys")
    parser.add_argument('files', nargs='*', type=Path, help="Files to check")
    parser.add_argument('--strict', action='store_true', help="Exit with error on violations")
    parser.add_argument('--all', action='store_true', help="Check all Python files in project")
    args = parser.parse_args()
    
    if args.all:
        files = list(Path('.').rglob('*.py'))
    else:
        files = args.files if args.files else list(Path('.').rglob('*.py'))
    
    all_ok = True
    for filepath in files:
        if not check_file(filepath, args.strict):
            all_ok = False
    
    if not all_ok and args.strict:
        print("\n❌ Direct environment variable access for API keys detected!")
        print("All API keys must go through VaultCore.")
        print("Example:")
        print("  from omega.vault import VaultCore")
        print("  vault = VaultCore()")
        print("  cred = await vault.retrieve_credential('openrouter', 'api_key')")
        print("  api_key = cred.encrypted_blob")
        sys.exit(1)
    elif all_ok:
        print("✅ All API key access goes through VaultCore")
    
    return 0


if __name__ == '__main__':
    main()