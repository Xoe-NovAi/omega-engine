#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Validate LLM-friendly documentation against standards.
Checks: frontmatter schema, answer-first sections, self-contained code blocks, dependency graphs.
"""

import sys
import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from jsonschema import validate, ValidationError

class LLMDocValidator:
    def __init__(self, schema_path: Path, budget_path: Path):
        with open(schema_path) as f:
            self.schema = json.load(f)
        with open(budget_path) as f:
            self.budgets = yaml.safe_load(f)
        
        self.errors = []
        self.warnings = []
    
    def validate_frontmatter(self, content: str, filepath: Path) -> bool:
        """Validate YAML frontmatter against schema."""
        if not content.startswith("---"):
            self.errors.append(f"{filepath}: Missing YAML frontmatter (must start with ---)")
            return False
        
        parts = content.split("---", 2)
        if len(parts) < 3:
            self.errors.append(f"{filepath}: Malformed frontmatter")
            return False
        
        try:
            frontmatter = yaml.safe_load(parts[1])
            validate(instance=frontmatter, schema=self.schema)
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"{filepath}: Invalid YAML in frontmatter: {e}")
            return False
        except ValidationError as e:
            self.errors.append(f"{filepath}: Frontmatter schema violation: {e.message}")
            return False
    
    def validate_answer_first(self, content: str, filepath: Path) -> bool:
        """Check that each ## section starts with answer-first format."""
        # Remove frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Find all ## sections
        sections = re.split(r'\n(## .+)', content)
        
        ok = True
        for i in range(1, len(sections), 2):
            heading = sections[i].strip()
            section_content = sections[i + 1] if i + 1 < len(sections) else ""
            
            # Skip if no content
            if not section_content.strip():
                continue
            
            # Get first non-empty, non-heading line
            lines = section_content.strip().split('\n')
            first_content = ""
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    first_content = line
                    break
            
            if not first_content:
                continue
            
            # Check for answer-first patterns
            answer_patterns = [
                r'^\*\*What\*\*:',
                r'^\*\*Why\*\*:',
                r'^\*\*Acceptance\*\*',
                r'^\*\*Dependencies\*\*',
                r'^\*\*Owner\*\*',
                r'^\*\*Estimated\*\*',
                r'^## What',
                r'^## Why',
            ]
            
            is_answer_first = any(re.match(p, first_content) for p in answer_patterns)
            
            if not is_answer_first:
                self.warnings.append(f"{filepath}: Section '{heading}' may not be answer-first (starts with: {first_content[:80]}...)")
        
        return ok
    
    def validate_code_blocks(self, content: str, filepath: Path) -> bool:
        """Check that code blocks are self-contained."""
        code_blocks = re.findall(r'```(\w+)\n(.*?)\n```', content, re.DOTALL)
        
        ok = True
        for lang, code in code_blocks:
            if lang in ['python', 'bash', 'yaml', 'json']:
                if lang == 'python':
                    # Check for imports or function/class definitions
                    has_import = 'import ' in code or 'from ' in code
                    has_def = 'def ' in code or 'class ' in code
                    has_file_comment = code.strip().startswith('# File:')
                    
                    if not (has_import or has_def or has_file_comment):
                        self.warnings.append(f"{filepath}: Python code block may lack imports/context")
                
                elif lang == 'bash':
                    # Check for shebang or file comment
                    has_shebang = code.strip().startswith('#!')
                    has_file_comment = code.strip().startswith('# File:')
                    
                    if not (has_shebang or has_file_comment):
                        self.warnings.append(f"{filepath}: Bash code block missing shebang or file comment")
                
                elif lang in ['yaml', 'json']:
                    # These are usually config snippets, OK if they look complete
                    pass
        
        return ok
    
    def validate_dependency_graph(self, content: str, filepath: Path) -> bool:
        """Check for Mermaid + YAML dependency graph."""
        has_mermaid = '```mermaid' in content
        has_yaml_deps = 'dependencies:' in content
        
        if not has_mermaid:
            self.warnings.append(f"{filepath}: Missing Mermaid dependency diagram")
        if not has_yaml_deps:
            self.warnings.append(f"{filepath}: Missing machine-readable YAML dependencies")
        
        # These are style recommendations, not hard requirements
        return True
    
    def validate_token_budget(self, content: str, filepath: Path) -> bool:
        """Check token count against budget."""
        # Remove frontmatter for counting
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]
        
        tokens = len(content) // 4  # Rough estimate
        
        # Determine doc type from path
        doc_type = "reference_doc"
        if "sprints" in str(filepath) and "index.md" in str(filepath):
            doc_type = "sprint_plan"
        elif "sprints" in str(filepath) and "tickets" in str(filepath):
            doc_type = "ticket_page"
        elif "research-index" in str(filepath):
            doc_type = "research_index"
        
        budget = self.budgets.get("token_budgets", {}).get(doc_type, {})
        hard_limit = budget.get("hard_limit", 16000)
        soft_limit = budget.get("soft_limit", 12800)
        target = budget.get("target", 8000)
        
        ok = True
        if tokens > hard_limit:
            self.errors.append(f"{filepath}: Token count {tokens} exceeds hard limit {hard_limit} for {doc_type}")
            ok = False
        elif tokens > soft_limit:
            self.warnings.append(f"{filepath}: Token count {tokens} exceeds soft limit {soft_limit} for {doc_type}")
        elif tokens > target:
            self.warnings.append(f"{filepath}: Token count {tokens} exceeds target {target} for {doc_type}")
        
        return ok
    
    def validate_file(self, filepath: Path) -> bool:
        """Validate a single markdown file."""
        content = filepath.read_text()
        
        all_ok = True
        all_ok &= self.validate_frontmatter(content, filepath)
        all_ok &= self.validate_answer_first(content, filepath)
        all_ok &= self.validate_code_blocks(content, filepath)
        all_ok &= self.validate_dependency_graph(content, filepath)
        all_ok &= self.validate_token_budget(content, filepath)
        
        return all_ok
    
    def validate_directory(self, dirpath: Path) -> bool:
        """Validate all .md files in directory."""
        all_ok = True
        for md_file in dirpath.rglob("*.md"):
            if md_file.name in ["llms.txt", "llms-full.txt"]:
                continue
            print(f"Validating {md_file}...")
            if not self.validate_file(md_file):
                all_ok = False
        return all_ok


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate LLM-friendly documentation")
    parser.add_argument("--frontmatter-schema", required=True, help="Path to frontmatter JSON schema")
    parser.add_argument("--token-budget", required=True, help="Path to token budgets YAML")
    parser.add_argument("--answer-first-check", action="store_true", help="Enable answer-first validation")
    parser.add_argument("--code-block-check", action="store_true", help="Enable code block validation")
    parser.add_argument("--dependency-graph-check", action="store_true", help="Enable dependency graph validation")
    parser.add_argument("paths", nargs="+", help="Files or directories to validate")
    
    args = parser.parse_args()
    
    validator = LLMDocValidator(Path(args.frontmatter_schema), Path(args.token_budget))
    
    all_ok = True
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_dir():
            all_ok &= validator.validate_directory(path)
        else:
            all_ok &= validator.validate_file(path)
    
    # Report
    if validator.warnings:
        print("\n⚠️  WARNINGS:")
        for w in validator.warnings:
            print(f"  {w}")
    
    if validator.errors:
        print("\n❌ ERRORS:")
        for e in validator.errors:
            print(f"  {e}")
        all_ok = False
    
    if all_ok:
        print("\n✅ All validations passed!")
        return 0
    else:
        print("\n❌ Validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())