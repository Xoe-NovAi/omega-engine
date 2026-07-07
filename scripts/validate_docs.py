#!/usr/bin/env python3
"""
Documentation Validation Script
Validates all Markdown documentation files against the Omega Engine style guide.

AP Token: AP-DOC-VALIDATE-v1.0.0
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    file_path: str
    passed: bool
    errors: List[str]
    warnings: List[str]

class DocValidator:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.docs_dir = root_dir / "docs"
        self.results: List[ValidationResult] = []
        
        # Valid values from style guide
        self.valid_entities = {
            "NEMOTRON-3-SUPER", "GEMMA-4-31B", "DEEPSEEK-V4-FLASH", 
            "MIMO-V2.5", "KALI", "MAAT", "LILITH", "DOOM_GUY", 
            "ROC_RACOON", "JEM", "RESEARCHER", "MAKALI", 
            "JOHN_CARMACK", "VERITY", "SOPHIA", "IRIS",
            "SEKHMET", "BRIGID", "PROMETHEUS", "SARASWATI", 
            "INANNA", "ERESHKIGAL", "LUCIFER", "HECATE", 
            "ANUBIS", "KALI_PILLAR", "PILLAR"
        }
        
        self.valid_models = {
            "gemma-4-31b-it", "nemotron-3-super", "deepseek-v4-flash",
            "mimo-v2.5", "qwen3-1.7b", "qwen3-4b-thinking", 
            "phi-4-mini", "krikri-8b", "deepseek-r1-qwen3-8b",
            "rocracoon-3b-instruct", "qwen3-0.6b",
            "opencode", "researcher"
        }
        
        self.valid_trc = {
            "trc_doc_inventory", "trc_doc_style", "trc_doc_user", 
            "trc_doc_ref", "trc_doc_deep", "trc_doc_strat", 
            "trc_doc_proc", "trc_doc_agent", "trc_doc_skill",
            "trc_ark_blueprint", "trc_master_synthesis", "trc_horizon1",
            "trc_provider_fix", "trc_maat", "trc_lilith", "trc_kali",
            "trc_research", "trc_heritage", "trc_integration",
            "trc_sovereign", "trc_continuity", "trc_hardening",
            "trc_pillar", "trc_verity", "trc_audit", "trc_mining",
            "trc_synthesis", "trc_oversight", "trc_build", "trc_run",
            "trc_council", "trc_makali", "trc_doc_sprint"
        }
        
        self.valid_status = {"DRAFT", "REVIEW", "STANDARD", "DEPRECATED", "ARCHIVED", "ACTIVE"}
        
        # AP Token pattern
        self.ap_token_pattern = re.compile(r'AP-[A-Z0-9_-]+-v\d+\.\d+\.\d+')
        
        # Date pattern
        self.date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        
        # Header pattern
        self.header_pattern = re.compile(
            r'^#\s[🔱⚠️]\s.+\n'
            r'\*\*AP Token\*\*:\s`[^`]+`\n'
            r'⬡\sOMEGA\s⬡\s[A-Z0-9_-]+\s⬡\s[a-z0-9.-]+\s⬡\sopencode\s⬡\strc_[a-z_]+\s⬡\s[A-Z]+\n\n'
            r'\*\*Date\*\*:\s\d{4}-\d{2}-\d{2}\n'
            r'\*\*Purpose\*\*:\s.+'
        )

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single documentation file."""
        errors = []
        warnings = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return ValidationResult(str(file_path), False, [f"Cannot read file: {e}"], [])
        
        lines = content.split('\n')
        
        # Check header
        header_end = self._find_header_end(lines)
        if header_end == -1:
            errors.append("Missing or malformed header")
        else:
            header_lines = lines[:header_end]
            header_text = '\n'.join(header_lines)
            self._validate_header(header_text, header_lines, errors, warnings)
        
        # Check for common issues
        self._check_common_issues(content, lines, errors, warnings)
        
        # Check links
        self._check_links(content, file_path, errors, warnings)
        
        # Check version consistency
        self._check_version_consistency(content, errors, warnings)
        
        passed = len(errors) == 0
        return ValidationResult(str(file_path), passed, errors, warnings)
    
    def _find_header_end(self, lines: List[str]) -> int:
        """Find the end of the header section, skipping YAML frontmatter."""
        if not lines:
            return -1

        # If the file starts with YAML frontmatter (---), skip past it
        search_start = 0
        if lines[0].strip() == '---':
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    search_start = i + 1
                    break

        # Find the next --- which separates header from body
        for i in range(search_start, len(lines)):
            if lines[i].strip() == '---':
                return i + 1

        return -1
    
    def _validate_header(self, header_text: str, header_lines: List[str], errors: List[str], warnings: List[str]):
        """Validate header fields."""
        # Check AP Token
        ap_match = re.search(r'\*\*AP Token\*\*:\s`([^`]+)`', header_text)
        if not ap_match:
            errors.append("Missing AP Token")
        else:
            token = ap_match.group(1)
            if not self.ap_token_pattern.match(token):
                errors.append(f"Invalid AP Token format: {token}")
        
        # Check entity line
        entity_match = re.search(r'⬡\sOMEGA\s⬡\s([A-Z0-9_-]+)\s⬡', header_text)
        if not entity_match:
            errors.append("Missing or malformed entity line")
        else:
            entity = entity_match.group(1)
            if entity not in self.valid_entities:
                warnings.append(f"Unknown entity: {entity}")
        
        # Check model
        model_match = re.search(r'⬡\s[A-Z0-9_-]+\s⬡\s([a-z0-9.-]+)\s⬡', header_text)
        if not model_match:
            errors.append("Missing model in header")
        else:
            model = model_match.group(1)
            if model not in self.valid_models:
                warnings.append(f"Unknown model: {model}")
        
        # Check trc code
        trc_match = re.search(r'⬡\sopencode\s⬡\s(trc_[a-z_]+)\s⬡', header_text)
        if not trc_match:
            errors.append("Missing trc code")
        else:
            trc = trc_match.group(1)
            if trc not in self.valid_trc:
                warnings.append(f"Unknown trc code: {trc}")
        
        # Check status
        status_match = re.search(r'⬡\s([A-Z]+)$', header_text, re.MULTILINE)
        if not status_match:
            errors.append("Missing status")
        else:
            status = status_match.group(1)
            if status not in self.valid_status:
                warnings.append(f"Unknown status: {status}")
        
        # Check date
        date_match = re.search(r'\*\*Date\*\*:\s(\d{4}-\d{2}-\d{2})', header_text)
        if not date_match:
            errors.append("Missing or invalid date")
        else:
            date_str = date_match.group(1)
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format: {date_str}")
        
        # Check purpose
        purpose_match = re.search(r'\*\*Purpose\*\*:\s(.+)', header_text)
        if not purpose_match:
            errors.append("Missing Purpose statement")
        elif len(purpose_match.group(1)) < 10:
            warnings.append("Purpose statement very short")
    
    def _check_common_issues(self, content: str, lines: List[str], errors: List[str], warnings: List[str]):
        """Check for common documentation issues."""
        # Identify YAML frontmatter boundaries
        yaml_start = -1
        yaml_end = -1
        if lines and lines[0].strip() == '---':
            yaml_start = 0
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    yaml_end = i
                    break

        def in_yaml(line_num: int) -> bool:
            return yaml_start >= 0 and yaml_end >= 0 and yaml_start <= line_num <= yaml_end

        # Check for TODO/FIXME markers
        todo_count = content.count('TODO') + content.count('FIXME') + content.count('XXX')
        if todo_count > 0:
            warnings.append(f"Found {todo_count} TODO/FIXME/XXX markers")
        
        # Check for very long lines (skip YAML frontmatter)
        for i, line in enumerate(lines):
            if len(line) > 120 and not in_yaml(i):
                warnings.append(f"Line {i+1} exceeds 120 characters ({len(line)} chars)")
        
        # Check for trailing whitespace (skip YAML frontmatter)
        for i, line in enumerate(lines):
            if line.rstrip() != line and not in_yaml(i):
                warnings.append(f"Line {i+1} has trailing whitespace")
        
        # Check for multiple blank lines
        blank_count = 0
        for i, line in enumerate(lines):
            if line.strip() == '':
                blank_count += 1
                if blank_count > 2:
                    warnings.append(f"More than 2 consecutive blank lines at line {i+1}")
            else:
                blank_count = 0
    
    def _check_links(self, content: str, file_path: Path, errors: List[str], warnings: List[str]):
        """Check internal and external links."""
        # Find markdown links
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        links = link_pattern.findall(content)
        
        for text, url in links:
            # Check internal links
            if url.startswith('./') or url.startswith('../') or (url.startswith('/') and not url.startswith('http')):
                # Resolve relative path
                if url.startswith('./') or url.startswith('../'):
                    target = (file_path.parent / url).resolve()
                else:
                    target = (self.root_dir / url.lstrip('/')).resolve()
                
                if not target.exists():
                    errors.append(f"Broken internal link: {url} (from {text})")
                elif target.suffix == '.md':
                    # Check anchor links
                    if '#' in url:
                        anchor = url.split('#')[1]
                        self._check_anchor(target, anchor, errors)
            
            # Check external links (basic format)
            elif url.startswith('http'):
                if not re.match(r'https?://[^\s/$.?#].[^\s]*', url):
                    warnings.append(f"Suspicious external URL format: {url}")
    
    def _check_anchor(self, target_file: Path, anchor: str, errors: List[str]):
        """Check if anchor exists in target file."""
        try:
            content = target_file.read_text(encoding='utf-8')
            # Convert anchor to header format
            anchor_pattern = re.compile(r'^#+\s+' + re.escape(anchor.replace('-', ' ')) + r'\s*$', re.MULTILINE | re.IGNORECASE)
            if not anchor_pattern.search(content):
                # Try exact match
                if f'#{anchor}' not in content and f'##{anchor}' not in content:
                    errors.append(f"Anchor not found: #{anchor} in {target_file}")
        except Exception:
            pass
    
    def _check_version_consistency(self, content: str, errors: List[str], warnings: List[str]):
        """Check version consistency within document."""
        # Find all version-like patterns
        versions = re.findall(r'v?(\d+\.\d+\.\d+)', content)
        if versions:
            unique_versions = set(versions)
            if len(unique_versions) > 1:
                warnings.append(f"Multiple versions found: {unique_versions}")

    def validate_all(self) -> List[ValidationResult]:
        """Validate all documentation files."""
        md_files = list(self.docs_dir.rglob("*.md"))
        # Also check root level docs
        md_files.extend(self.root_dir.glob("*.md"))
        # Check agent files
        md_files.extend((self.root_dir / ".opencode" / "agents").glob("*.md"))
        # Check skill files
        md_files.extend((self.root_dir / ".opencode" / "skills").glob("*.md"))
        
        for file_path in md_files:
            # Skip archive directories
            if 'archive' in file_path.parts:
                continue
            result = self.validate_file(file_path)
            self.results.append(result)
        
        return self.results

    def print_summary(self):
        """Print validation summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        total_errors = sum(len(r.errors) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)
        
        print(f"\n{'='*60}")
        print(f"DOCUMENTATION VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total files checked: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total errors: {total_errors}")
        print(f"Total warnings: {total_warnings}")
        print(f"{'='*60}")
        
        if failed > 0:
            print("\nFAILED FILES:")
            for result in self.results:
                if not result.passed:
                    print(f"\n  ❌ {result.file_path}")
                    for error in result.errors:
                        print(f"    ERROR: {error}")
                    for warning in result.warnings:
                        print(f"    WARN:  {warning}")
        
        if total_warnings > 0:
            print("\nWARNINGS:")
            for result in self.results:
                if result.warnings:
                    print(f"\n  ⚠️  {result.file_path}")
                    for warning in result.warnings:
                        print(f"    WARN:  {warning}")
        
        return failed == 0

def main():
    root_dir = Path(__file__).parent.parent
    validator = DocValidator(root_dir)
    validator.validate_all()
    success = validator.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()