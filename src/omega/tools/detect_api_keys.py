#!/usr/bin/env python3
"""
Omega Engine - API Key Detection Tool
Detects scattered os.environ.get / os.getenv calls for API keys in source code.
Part of the VaultCore unification effort - ensures all API keys go through VaultCore.
"""

import ast
import sys
import re
from pathlib import Path
from typing import List, Tuple

# Patterns that indicate API key access via environment variables
API_KEY_PATTERNS = [
    r'os\.environ\.get\(["\']([A-Z0-9_]+_API_KEY)["\']',
    r'os\.environ\.get\(["\']([A-Z0-9_]+_KEY)["\']',
    r'os\.getenv\(["\']([A-Z0-9_]+_API_KEY)["\']',
    r'os\.getenv\(["\']([A-Z0-9_]+_KEY)["\']',
    r'os\.environ\[["\']([A-Z0-9_]+_API_KEY)["\']\]',
    r'os\.environ\[["\']([A-Z0-9_]+_KEY)["\']\]',
]

# Known API key environment variable names (case-insensitive)
KNOWN_API_KEYS = {
    'openrouter_api_key', 'exa_api_key', 'firecrawl_api_key', 'google_api_key',
    'aa_api_key', 'perspective_api_key', 'openai_api_key', 'anthropic_api_key',
    'grok_api_key', 'deepseek_api_key', 'mistral_api_key', 'cohere_api_key',
    'huggingface_api_key', 'replicate_api_key', 'together_api_key', 'nvidia_api_key',
    'cerebras_api_key', 'groq_api_key', 'sambanova_api_key', 'xai_api_key',
    'opencode_zen_api_key', 'cline_api_key', 'copilot_api_key',
}

# Files to exclude from checking
EXCLUDE_PATTERNS = [
    'test_', 'tests/', '__pycache__', '.venv', 'venv/',
    'docs/', 'data/', 'scripts/', 'archive/', 'old/',
    'omega-vetala/', 'packages/omega-sieve/',
    'third-party/', 'third_party/',
]


def should_exclude(filepath: Path) -> bool:
    """Check if file should be excluded from scanning."""
    path_str = str(filepath)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def find_api_key_access(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Find API key access patterns in a Python file.
    Returns list of (line_number, matched_pattern, matched_key).
    """
    results = []
    try:
        content = filepath.read_text()
        # Parse with AST to identify comments and docstrings
        tree = ast.parse(content, filename=str(filepath))
        
        # Collect lines that are in docstrings or comments
        excluded_lines = set()
        
        # Find docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if hasattr(node, 'lineno'):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        start_line = node.lineno
                        docstring_lines = docstring.count('\n') + 1
                        for l in range(start_line, start_line + docstring_lines + 2):
                            excluded_lines.add(l)
            elif isinstance(node, ast.Module):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstring_lines = docstring.count('\n') + 1
                    for l in range(1, docstring_lines + 2):
                        excluded_lines.add(l)
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Skip excluded lines (docstrings)
            if i in excluded_lines:
                continue
            
            # Skip inline comments
            if '#' in line:
                line = line[:line.index('#')]
            
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            for pattern in API_KEY_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    key_name = match.group(1).lower()
                    if key_name in KNOWN_API_KEYS or any(k in key_name for k in ['api_key', '_key']):
                        results.append((i, pattern, key_name))
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
    
    return results


def check_file(filepath: Path, strict: bool = False) -> bool:
    """Check a single file for API key access violations."""
    if should_exclude(filepath):
        return True
    
    violations = find_api_key_access(filepath)
    if violations:
        print(f"\n{filepath}:")
        for line_num, pattern, key in violations:
            print(f"  Line {line_num}: Found API key access - {key}")
            print(f"    Pattern: {pattern}")
        
        if strict:
            print(f"  ERROR: Direct environment variable access for API keys is forbidden.")
            print(f"  Use VaultCore instead: from omega.vault import VaultCore")
            return False
    
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Detect API key access in source code")
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
        print("\n❌ API key access violations found!")
        print("Use VaultCore instead of os.environ.get / os.getenv for API keys.")
        print("Example:")
        print("  from omega.vault import VaultCore")
        print("  vault = VaultCore()")
        print("  cred = await vault.retrieve_credential('openrouter', 'api_key')")
        print("  api_key = cred.encrypted_blob")
        sys.exit(1)
    elif all_ok:
        print("✅ No API key access violations found")
    
    return 0


if __name__ == '__main__':
    main()