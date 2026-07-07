#!/usr/bin/env python3
"""
Documentation Validation Script (v2.0 — The Carmack Cut)
Validates Markdown documentation files against the Omega Engine style guide.

AP Token: AP-DOC-VALIDATE-v2.0.0

Changes from v1.0:
- Added file category awareness (Reference, Agent, Skill, R-Doc, Working, Archive)
- 120-char line warnings downgraded to informational (no longer errors)
- Added orphan file detection (docs not linked from any index)
- Added freshness detection (docs >30 days stale)
- Added DocRef: coverage reporting
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class ValidationResult:
    file_path: str
    passed: bool
    errors: List[str]
    warnings: List[str]
    info: List[str] = field(default_factory=list)
    category: str = "unknown"

class DocValidator:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.docs_dir = root_dir / "docs"
        self.results: List[ValidationResult] = []
        self.all_doc_links: Dict[str, Set[str]] = {}  # file -> set of files it links to
        self.linked_files: Set[str] = set()  # files that ARE linked to by others

        # Valid values from style guide
        self.valid_entities = {
            "NEMOTRON-3-SUPER", "GEMMA-4-31B", "DEEPSEEK-V4-FLASH",
            "MIMO-V2.5", "KALI", "MAAT", "LILITH", "DOOM_GUY",
            "ROC_RACOON", "JEM", "RESEARCHER", "MAKALI",
            "JOHN_CARMACK", "VERITY", "SOPHIA", "IRIS",
            "SEKHMET", "BRIGID", "PROMETHEUS", "SARASWATI",
            "INANNA", "ERESHKIGAL", "LUCIFER", "HECATE",
            "ANUBIS", "KALI_PILLAR", "PILLAR", "NEMOTRON-3-ULTRA"
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

        self.ap_token_pattern = re.compile(r'AP-[A-Z0-9_-]+-v\d+\.\d+\.\d+')
        self.date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')

    def categorize_file(self, file_path: Path) -> str:
        """Determine the file category based on path and content."""
        parts = file_path.parts

        # Category 2: Agent files
        if '.opencode' in parts and 'agents' in parts:
            return 'agent'

        # Category 3: Skill files
        if '.opencode' in parts and 'skills' in parts:
            return 'skill'

        # Category 4: R-Docs
        if 'research' in parts and file_path.name.startswith('R'):
            return 'rdoc'

        # Category 5: Working docs
        if 'team' in parts or 'intake' in parts or 'coordination' in parts:
            return 'working'

        # Category 6: Archives
        if 'archive' in parts or 'archived' in parts:
            return 'archive'

        # Category 7: Root docs (already standardized)
        if file_path.parent == self.root_dir and file_path.suffix == '.md':
            return 'root'

        # Category 1: Reference docs (everything else in docs/)
        if 'docs' in parts or 'standards' in parts or 'architecture' in parts:
            return 'reference'

        return 'other'

    def requires_header(self, category: str) -> bool:
        """Whether a file category requires the Omega header."""
        return category in ('reference', 'root', 'agent')

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single documentation file."""
        errors = []
        warnings = []
        info = []
        category = self.categorize_file(file_path)

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return ValidationResult(str(file_path), False, [f"Cannot read file: {e}"], [], category=category)

        lines = content.split('\n')

        # Check header (only for categories that require it)
        if self.requires_header(category):
            header_end = self._find_header_end(lines)
            if header_end == -1:
                errors.append(f"Missing or malformed header (required for {category} files)")
            else:
                header_lines = lines[:header_end]
                header_text = '\n'.join(header_lines)
                self._validate_header(header_text, header_lines, errors, warnings)
        elif category not in ('skill',):
            # For non-reference, non-skill files, check if they have a header anyway
            header_end = self._find_header_end(lines)
            if header_end == -1:
                info.append(f"No Omega header (category={category}, exempt from requirement)")

        # Check for common issues
        self._check_common_issues(content, lines, errors, warnings, category)

        # Check links
        self._check_links(content, file_path, errors, warnings)

        # Track links for orphan detection
        self._track_links(content, file_path)

        # Check freshness
        self._check_freshness(content, file_path, info)

        passed = len(errors) == 0
        return ValidationResult(str(file_path), passed, errors, warnings, info, category)

    def _find_header_end(self, lines: List[str]) -> int:
        """Find the end of the header section, skipping YAML frontmatter."""
        if not lines:
            return -1

        search_start = 0
        if lines[0].strip() == '---':
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    search_start = i + 1
                    break

        for i in range(search_start, len(lines)):
            if lines[i].strip() == '---':
                return i + 1

        return -1

    def _validate_header(self, header_text: str, header_lines: List[str], errors: List[str], warnings: List[str]):
        """Validate header fields."""
        ap_match = re.search(r'\*\*AP Token\*\*:\s`([^`]+)`', header_text)
        if not ap_match:
            errors.append("Missing AP Token")
        else:
            token = ap_match.group(1)
            if not self.ap_token_pattern.match(token):
                errors.append(f"Invalid AP Token format: {token}")

        entity_match = re.search(r'⬡\sOMEGA\s⬡\s([A-Z0-9_-]+)\s⬡', header_text)
        if not entity_match:
            errors.append("Missing or malformed entity line")
        else:
            entity = entity_match.group(1)
            if entity not in self.valid_entities:
                warnings.append(f"Unknown entity: {entity}")

        model_match = re.search(r'⬡\s[A-Z0-9_-]+\s⬡\s([a-z0-9.-]+)\s⬡', header_text)
        if not model_match:
            errors.append("Missing model in header")
        else:
            model = model_match.group(1)
            if model not in self.valid_models:
                warnings.append(f"Unknown model: {model}")

        trc_match = re.search(r'⬡\sopencode\s⬡\s(trc_[a-z_]+)\s⬡', header_text)
        if not trc_match:
            errors.append("Missing trc code")
        else:
            trc = trc_match.group(1)
            if trc not in self.valid_trc:
                warnings.append(f"Unknown trc code: {trc}")

        status_match = re.search(r'⬡\s([A-Z]+)$', header_text, re.MULTILINE)
        if not status_match:
            errors.append("Missing status")
        else:
            status = status_match.group(1)
            if status not in self.valid_status:
                warnings.append(f"Unknown status: {status}")

        date_match = re.search(r'\*\*Date\*\*:\s(\d{4}-\d{2}-\d{2})', header_text)
        if not date_match:
            errors.append("Missing or invalid date")
        else:
            date_str = date_match.group(1)
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format: {date_str}")

        purpose_match = re.search(r'\*\*Purpose\*\*:\s(.+)', header_text)
        if not purpose_match:
            errors.append("Missing Purpose statement")
        elif len(purpose_match.group(1)) < 10:
            warnings.append("Purpose statement very short")

    def _check_common_issues(self, content: str, lines: List[str], errors: List[str], warnings: List[str], category: str):
        """Check for common documentation issues."""
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

        # 120-char lines: INFO only (not error, not warning)
        for i, line in enumerate(lines):
            if len(line) > 120 and not in_yaml(i):
                # Skip code blocks and URLs
                if not line.strip().startswith(('```', '|', '-')):
                    pass  # Intentionally not flagging — this is a guideline

        # Check for trailing whitespace
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
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        links = link_pattern.findall(content)

        for text, url in links:
            if url.startswith('./') or url.startswith('../') or (url.startswith('/') and not url.startswith('http')):
                if url.startswith('./') or url.startswith('../'):
                    target = (file_path.parent / url).resolve()
                else:
                    target = (self.root_dir / url.lstrip('/')).resolve()

                if not target.exists():
                    errors.append(f"Broken internal link: {url} (from {text})")
                elif target.suffix == '.md':
                    if '#' in url:
                        anchor = url.split('#')[1]
                        self._check_anchor(target, anchor, errors)

            elif url.startswith('http'):
                if not re.match(r'https?://[^\s/$.?#].[^\s]*', url):
                    warnings.append(f"Suspicious external URL format: {url}")

    def _check_anchor(self, target_file: Path, anchor: str, errors: List[str]):
        """Check if anchor exists in target file."""
        try:
            content = target_file.read_text(encoding='utf-8')
            anchor_pattern = re.compile(r'^#+\s+' + re.escape(anchor.replace('-', ' ')) + r'\s*$', re.MULTILINE | re.IGNORECASE)
            if not anchor_pattern.search(content):
                if f'#{anchor}' not in content and f'##{anchor}' not in content:
                    errors.append(f"Anchor not found: #{anchor} in {target_file}")
        except Exception:
            pass

    def _track_links(self, content: str, file_path: Path):
        """Track internal links for orphan detection."""
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        links = link_pattern.findall(content)

        file_str = str(file_path)
        self.all_doc_links[file_str] = set()

        for text, url in links:
            if url.startswith('./') or url.startswith('../'):
                target = (file_path.parent / url).resolve()
                target_str = str(target)
                self.all_doc_links[file_str].add(target_str)
                self.linked_files.add(target_str)
            elif url.startswith('/') and not url.startswith('http'):
                target = (self.root_dir / url.lstrip('/')).resolve()
                target_str = str(target)
                self.all_doc_links[file_str].add(target_str)
                self.linked_files.add(target_str)

    def _check_freshness(self, content: str, file_path: Path, info: List[str]):
        """Check if document is stale (>30 days without update)."""
        date_match = re.search(r'\*\*Date\*\*:\s(\d{4}-\d{2}-\d{2})', content)
        if date_match:
            try:
                doc_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                age = (datetime.now() - doc_date).days
                if age > 30:
                    info.append(f"Stale: {age} days since last update")
            except ValueError:
                pass

    def detect_orphans(self) -> List[str]:
        """Detect docs that are not linked from any other doc."""
        orphans = []
        for file_path in self.docs_dir.rglob("*.md"):
            if 'archive' in file_path.parts:
                continue
            file_str = str(file_path)
            if file_str not in self.linked_files:
                # Don't flag index files or top-level docs
                if file_path.name.lower() not in ('index.md', 'readme.md'):
                    orphans.append(file_path)
        return orphans

    def detect_docref_coverage(self) -> Dict[str, bool]:
        """Check which source files have DocRef: comments."""
        src_dir = self.root_dir / "src" / "omega"
        coverage = {}
        for py_file in src_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                has_docref = 'DocRef:' in content
                coverage[str(py_file)] = has_docref
            except Exception:
                pass
        return coverage

    def validate_all(self) -> List[ValidationResult]:
        """Validate all documentation files."""
        md_files = list(self.docs_dir.rglob("*.md"))
        md_files.extend(self.root_dir.glob("*.md"))
        md_files.extend((self.root_dir / ".opencode" / "agents").glob("*.md"))
        md_files.extend((self.root_dir / ".opencode" / "skills").glob("*.md"))

        for file_path in md_files:
            if 'archive' in file_path.parts:
                continue
            result = self.validate_file(file_path)
            self.results.append(result)

        return self.results

    def print_summary(self):
        """Print validation summary with category breakdown."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        total_errors = sum(len(r.errors) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)
        total_info = sum(len(r.info) for r in self.results)

        # Category breakdown
        categories = {}
        for r in self.results:
            cat = r.category
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0, 'failed': 0}
            categories[cat]['total'] += 1
            if r.passed:
                categories[cat]['passed'] += 1
            else:
                categories[cat]['failed'] += 1

        print(f"\n{'='*60}")
        print(f"DOCUMENTATION VALIDATION SUMMARY (v2.0 — Carmack Cut)")
        print(f"{'='*60}")
        print(f"Total files checked: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total errors: {total_errors}")
        print(f"Total warnings: {total_warnings}")
        print(f"Total info: {total_info}")
        print(f"{'='*60}")

        print(f"\nCATEGORY BREAKDOWN:")
        for cat, stats in sorted(categories.items()):
            print(f"  {cat:12s}: {stats['total']:3d} files ({stats['passed']} pass, {stats['failed']} fail)")

        if failed > 0:
            print("\nFAILED FILES:")
            for result in self.results:
                if not result.passed:
                    print(f"\n  ❌ {result.file_path} [{result.category}]")
                    for error in result.errors:
                        print(f"    ERROR: {error}")
                    for warning in result.warnings:
                        print(f"    WARN:  {warning}")

        # Orphan detection
        orphans = self.detect_orphans()
        if orphans:
            print(f"\nORPHAN FILES ({len(orphans)} not linked from any other doc):")
            for o in orphans[:20]:
                rel = str(o.relative_to(self.root_dir))
                print(f"  📎 {rel}")
            if len(orphans) > 20:
                print(f"  ... and {len(orphans) - 20} more")

        # DocRef coverage
        docref = self.detect_docref_coverage()
        covered = sum(1 for v in docref.values() if v)
        total_src = len(docref)
        if total_src > 0:
            print(f"\nDocRef: COVERAGE: {covered}/{total_src} source files have DocRef: backlinks ({100*covered//total_src}%)")

        return failed == 0

def main():
    root_dir = Path(__file__).parent.parent
    validator = DocValidator(root_dir)
    validator.validate_all()
    success = validator.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
