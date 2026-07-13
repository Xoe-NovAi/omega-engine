#!/usr/bin/env python3
"""
Enhanced Context Packer for Omega Engine
Improvements over original:
1. XML-based output format for better Claude comprehension
2. Enhanced purpose extraction for multiple file types
3. Token-aware packing strategy (basic implementation)
4. Manifest-first approach
"""

import anyio
from pathlib import Path as LibPath
import yaml
import hashlib
import os
import re
import json
# xml_quoteattr() for attribute escaping only — do NOT import xml_escape for body content
from xml.sax.saxutils import quoteattr as xml_quoteattr
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime

try:
    import tiktoken
    ENCODER = tiktoken.get_encoding("cl100k_base")  # Claude's tokenizer
except ImportError:
    ENCODER = None
    print("Warning: tiktoken not installed. Token counting will be approximate.")

def _escape_bare_xml_chars(text: str) -> str:
    """Fully XML-escape file BODY content for valid XML output.

    EVERY `<` and `>` in the body is escaped to `&lt;`/`&gt;` so content can
    never be mistaken for an XML tag or cause Claude truncation (Issue #59787).
    Bare `&` is escaped unless already part of a valid entity. The `<file>`
    wrapper tags are emitted by the packer separately (NOT part of content),
    so they are never touched by this function.

    M9/M23: deterministic transform — no silent corruption, no fake tags.
    """
    # Escape < and > ALWAYS — no exceptions. This prevents docstrings/comments
    # that mention `<file>` or `<tag>` from creating fake XML boundaries.
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # Escape & only when not already part of a valid XML entity.
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', text)
    return text


@dataclass
class FileMetadata:
    relative_path: str
    size_bytes: int
    language: str
    sha256: str
    purpose: str = "Not specified"
    token_count: int = 0

@dataclass
class PackProfile:
    name: str
    description: str
    max_slots: int
    include: List[str]
    exclude: List[str]
    themes: Dict[str, List[str]]

class EnhancedContextPacker:
    def __init__(self, config_path: str = ".opencode/skills/context-packer/packer-config.yaml"):
        self.config_path = config_path
        self.profiles: Dict[str, PackProfile] = {}
        
    async def load_config(self):
        def _read_config():
            with open(self.config_path, "r") as f:
                return f.read()
        
        content = await anyio.to_thread.run_sync(_read_config)
        config = yaml.safe_load(content)
        for name, data in config.get("profiles", {}).items():
            self.profiles[name] = PackProfile(
                name=name,
                description=data.get("description", ""),
                max_slots=data.get("max_slots", 12),
                include=data.get("include", []),
                exclude=data.get("exclude", []),
                themes=data.get("themes", {})
            )
    
    def _get_language(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        mapping = {
            ".py": "Python",
            ".md": "Markdown",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".json": "JSON",
            ".txt": "Text",
            ".html": "HTML",
            ".css": "CSS",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".sql": "SQL"
        }
        return mapping.get(ext, "Unknown")
    
    async def _calculate_sha256(self, path: LibPath) -> str:
        def _hash():
            sha256_hash = hashlib.sha256()
            with open(str(path), "rb") as f:
                while chunk := f.read(8192):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        return await anyio.to_thread.run_sync(_hash)
    
    async def _estimate_token_count(self, path: LibPath) -> int:
        """Estimate token count with 30% safety margin.

        tiktoken undercounts by 10-30% compared to Claude's actual tokenizer
        (per researcher findings). We add a 30% margin to prevent exceeding
        Claude's context window during Projects upload.
        """
        if ENCODER is None:
            # Rough approximation: 4 characters per token, plus 30% margin
            return int(os.path.getsize(path) // 4 * 1.3)
        
        def _count_tokens():
            with open(str(path), "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            return len(ENCODER.encode(text))
        
        raw_count = await anyio.to_thread.run_sync(_count_tokens)
        # Apply 30% safety margin (researcher finding: tiktoken undercounts 10-30%)
        return int(raw_count * 1.3)
    
    async def _get_purpose(self, path: LibPath) -> str:
        ext = os.path.splitext(path)[1].lower()
        
        def _extract_purpose():
            try:
                with open(str(path), "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                if ext == ".py":
                    # Try to extract docstring
                    match = re.search(r'"""(.*?)"""', content, re.DOTALL | re.IGNORECASE)
                    if match:
                        return match.group(1).strip().split('\n')[0][:100]
                    # Fallback to first non-empty line that looks like a comment
                    lines = content.split('\n')
                    for line in lines[:10]:
                        stripped = line.strip()
                        if stripped.startswith('#') and len(stripped) > 10:
                            return stripped[1:].strip()[:100]
                
                elif ext == ".md":
                    # First H1 or first substantial paragraph
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('# '):
                            return line[2:].strip()[:100]
                    # Look for first paragraph with substantial content
                    for line in lines:
                        if len(line.strip()) > 20 and not line.startswith('#'):
                            return line.strip()[:100]
                
                elif ext in [".yaml", ".yml"]:
                    # Try to get a descriptive comment or first key
                    lines = content.split('\n')
                    for line in lines[:15]:
                        stripped = line.strip()
                        if stripped.startswith('#') and len(stripped) > 10:
                            return stripped[1:].strip()[:100]
                        if ':' in stripped and not stripped.startswith('{') and len(stripped) < 50:
                            return f"Config: {stripped}"[:100]
                
                elif ext == ".json":
                    # Try to get a description from top-level keys
                    try:
                        data = json.loads(content)
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]
                            if keys:
                                return f"JSON object with keys: {', '.join(keys)}"[:100]
                    except (json.JSONDecodeError, ValueError):
                        pass
                
                # Generic fallback: first non-empty line with substance
                lines = content.split('\n')
                for line in lines[:20]:
                    stripped = line.strip()
                    if len(stripped) > 15 and not stripped.startswith(('/*', '//', '<!--', '{', '[')):
                        return stripped[:100]
                        
                return "Configuration or data file"
                
            except Exception as e:
                return f"Error extracting purpose: {str(e)}"
        
        return await anyio.to_thread.run_sync(_extract_purpose)
    
    async def _prune_content(self, content: str) -> str:
        # Collapse triple+ newlines to double
        content = re.sub(r'\n{3,}', '\n\n', content)
        # Remove trailing whitespace on each line
        lines = [line.rstrip() for line in content.splitlines()]
        return '\n'.join(lines)
    
    async def _atomic_write(self, path: LibPath, content: str):
        def _write():
            path_str = str(path)
            tmp_path = path_str + ".tmp"
            with open(tmp_path, "w") as f:
                f.write(content)
            os.replace(tmp_path, path_str)
        await anyio.to_thread.run_sync(_write)
    
    async def pack(self, profile_name: str):
        if profile_name not in self.profiles:
            raise ValueError(f"Profile {profile_name} not found in config.")
        
        profile = self.profiles[profile_name]
        output_dir = LibPath(f"context_packs/{profile_name}")
        await anyio.to_thread.run_sync(lambda: output_dir.mkdir(parents=True, exist_ok=True))
        
        # Phase 1: Selection
        selected_files: Set[str] = set()
        for pattern in profile.include:
            files = await anyio.to_thread.run_sync(self._glob_files, pattern)
            selected_files.update(files)
        
        # Apply excludes
        final_files = []
        for f in selected_files:
            excluded = False
            for pattern in profile.exclude:
                if self._match_pattern(f, pattern):
                    excluded = True
                    break
            if not excluded:
                final_files.append(f)
        
        # Phase 2: Enhance metadata with token counts and purposes
        file_data = []
        for f_rel in final_files:
            f_path = LibPath(f_rel)
            if not os.path.exists(f_rel):
                continue
            
            stats = f_path.stat()
            sha = await self._calculate_sha256(f_path)
            lang = self._get_language(f_rel)
            purpose = await self._get_purpose(f_path)
            tokens = await self._estimate_token_count(f_path)
            
            file_data.append({
                "path": f_rel,
                "size": stats.st_size,
                "language": lang,
                "sha256": sha,
                "purpose": purpose,
                "token_count": tokens,
                "path_obj": f_path,
                "stats": stats
            })
        
        # Phase 3: Sort by token count (descending) for priority-based packing
        file_data.sort(key=lambda x: x["token_count"], reverse=True)
        
        # Phase 4: Distribute files across themes (simple round-robin for now)
        # More sophisticated algorithms could be implemented here
        themed_bundles: Dict[str, List[dict]] = {theme: [] for theme in profile.themes}
        themed_bundles["general"] = []
        
        # Assign files to themes based on path matching
        for file_info in file_data:
            matched = False
            for theme, patterns in profile.themes.items():
                for pattern in patterns:
                    if self._match_pattern(file_info["path"], pattern):
                        themed_bundles[theme].append(file_info)
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                themed_bundles["general"].append(file_info)
        
        # Phase 5: If we have too many themes, merge smallest ones into general
        active_themes = [t for t, files in themed_bundles.items() if files]
        if len(active_themes) > profile.max_slots - 1:  # -1 for manifest
            # Sort by total token count in each theme
            theme_totals = [(t, sum(f["token_count"] for f in files)) for t, files in themed_bundles.items() if files]
            theme_totals.sort(key=lambda x: x[1])  # Ascending by token count
            
            # Merge the smallest themes into general
            num_to_merge = len(active_themes) - (profile.max_slots - 1)
            for i in range(num_to_merge):
                theme_to_merge = theme_totals[i][0]
                themed_bundles["general"].extend(themed_bundles[theme_to_merge])
                themed_bundles[theme_to_merge] = []
        
        # Phase 6: Packaging
        manifest_entries = []
        
        # Create manifest first
        manifest_content = await self._create_manifest(profile_name, themed_bundles)
        manifest_path = output_dir / "00_PROJECT_MANIFEST.md"
        await self._atomic_write(manifest_path, manifest_content)
        manifest_entries.append("- 00_PROJECT_MANIFEST.md (manifest)")
        
        # ── PII masker setup (instantiate ONCE before the file loop) ──────────────
        # [heritage: anyio 2024] detect() is async; tokenize() is sync
        # Lazy import keeps the skill decoupled from the engine at module load time.
        # M8/M23: PII masking is MANDATORY for external packs. Import failure is a
        # hard stop — never emit an unmasked pack (sovereignty breach).
        _masker = None
        try:
            import sys as _sys
            _engine_src = str(LibPath(__file__).resolve().parent.parent.parent.parent / "src")
            if _engine_src not in _sys.path:
                _sys.path.insert(0, _engine_src)
            from omega.oracle.pii_masker import PIIMasker, PIIRedactionStyle
            # TOKENIZE mode: replaces PII with reversible [EMAIL_1] placeholders.
            # Use MASK_FULL (mask_full()) if you want non-reversible **** masking instead.
            _masker = PIIMasker(redaction_style=PIIRedactionStyle.TOKENIZE)
        except ImportError as e:
            # M23 Failure Integrity: do NOT silently continue. Halt pack generation.
            try:
                from omega.errors import OmegaError
            except ImportError:
                raise RuntimeError(
                    "[SEC-BLOCKER] PIIMasker unavailable — refusing to generate "
                    f"unmasked pack for external upload. ImportError: {e}"
                ) from e
            raise OmegaError(
                "[SEC-BLOCKER] PIIMasker unavailable — refusing to generate "
                f"unmasked pack for external upload. ImportError: {e}"
            ) from e

        # Pack each theme
        for theme, files in themed_bundles.items():
            if not files:
                continue
            
            bundle_content = []
            for file_info in files:
                f_path = file_info["path_obj"]
                
                def _read_file():
                    with open(str(f_path), "r", encoding="utf-8", errors="replace") as f:
                        return f.read()

                raw_content = await anyio.to_thread.run_sync(_read_file)

                # PII masking before external upload (M8 Zero Telemetry / M7 Local-First)
                # API: detect() is async (runs in thread), tokenize() is sync.
                # The masker instance was created once before this loop — do NOT re-instantiate here.
                if _masker is not None:
                    detections = await _masker.detect(raw_content)
                    if detections:
                        masked_content, _token_map = _masker.tokenize(raw_content, detections)
                        content = masked_content
                    else:
                        content = raw_content  # No PII found — pass through unchanged
                else:
                    content = raw_content

                pruned_content = await self._prune_content(content)

                # B5 fix: escape bare & and stray < in the file BODY before wrapping
                # in <file>. Preserves <file>/</file> and tag-like sequences; only
                # escapes stray characters that would break XML parsing.
                pruned_content = _escape_bare_xml_chars(pruned_content)

                # XML-style file block. Attributes are escaped via xml_quoteattr();
                # the BODY is fully XML-escaped by _escape_bare_xml_chars() (see B5 fix
                # above) so the content is valid XML and cannot trigger Claude truncation
                # (Issue #59787). The <file> wrapper tags are emitted by the packer, not
                # part of content, so they remain real XML boundaries.
                # xml_quoteattr() wraps the value in quotes AND escapes <, >, &, ", '
                header = (
                    f"<file"
                    f" path={xml_quoteattr(file_info['path'])}"
                    f" size={xml_quoteattr(str(file_info['size']))}"
                    f" language={xml_quoteattr(file_info['language'])}"
                    f" sha256={xml_quoteattr(file_info['sha256'])}"
                    f" purpose={xml_quoteattr(file_info['purpose'])}"
                    f" tokens={xml_quoteattr(str(file_info['token_count']))}>"
                )
                footer = "</file>"
                # Body is fully XML-escaped by _escape_bare_xml_chars() above.
                bundle_content.append(header + "\n" + pruned_content + "\n" + footer + "\n\n")

                manifest_entries.append(f"- {file_info['path']} -> {theme}.xml ({file_info['token_count']} tokens)")

            # B5 fix: wrap all <file> blocks in a single root element so the
            # file is a valid XML document (ElementTree requires exactly one root).
            root_open = f'<pack profile={xml_quoteattr(profile_name)} theme={xml_quoteattr(theme)}>\n'
            root_close = "</pack>\n"
            bundle_file = output_dir / f"{theme}.xml"
            await self._atomic_write(bundle_file, root_open + "".join(bundle_content) + root_close)
        
        # Generate Manifest
        await self._atomic_write(manifest_path, manifest_content)
        
        return output_dir
    
    async def _create_manifest(self, profile_name: str, themed_bundles: Dict[str, List[dict]]) -> str:
        total_files = sum(len(files) for files in themed_bundles.values())
        total_tokens = sum(f["token_count"] for files in themed_bundles.values() for f in files)
        
        lines = [
            f"# Enhanced Context Pack Manifest: {profile_name}",
            f"Generated: {datetime.now().isoformat()}",
            f"Description: {self.profiles[profile_name].description}",
            f"Total Files: {total_files}",
            f"Estimated Total Tokens: {total_tokens}",
            f"Max Slots: {self.profiles[profile_name].max_slots}",
            "",
            "## Theme Breakdown",
        ]
        
        for theme, files in themed_bundles.items():
            if files:
                file_count = len(files)
                theme_tokens = sum(f["token_count"] for f in files)
                lines.append(f"- {theme}: {file_count} files, ~{theme_tokens} tokens")
                for f in files[:3]:  # Show first 3 files as examples
                    lines.append(f"  - {f['path']} ({f['token_count']} tokens)")
                if len(files) > 3:
                    lines.append(f"  - ... and {len(files) - 3} more")
        
        lines.extend([
            "",
            "## Usage Notes",
            "- This pack uses XML format for optimal Claude comprehension",
            "- Each file is wrapped in <file> tags with metadata attributes",
            "- The manifest should be reviewed first to understand the pack structure",
            "- Token counts are estimates using cl100k_base encoder (Claude's tokenizer)",
        ])
        
        return "\n".join(lines)
    
    def _glob_files(self, pattern: str) -> List[str]:
        import glob
        return glob.glob(pattern, recursive=True)
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Match path against glob pattern, supporting ** recursive globs.

        [heritage: id-soft 1993] BSP-style path culling — O(1) pattern gate.
        fnmatch treats `*` as non-recursive (stops at `/`); `**` maps to zero or
        more directory segments so theme patterns like `src/omega/**/*.py` match
        correctly instead of falling through to `general`.

        NOTE: The originally-specified snippet (`(.+/)?` substitution) is broken —
        it requires a trailing `/` inside the recursive group, so `a/**/b` can
        never match `a/b` (zero directories). This implementation uses the correct
        glob `**` semantics: `**/` → `(?:[^/]+/)*` (zero-or-more dir segments),
        bare `**` → `.*` (rest of path), single `*` → `[^/]*` (one segment).
        """
        import fnmatch, re
        if '**' not in pattern:
            return fnmatch.fnmatch(path, pattern)

        out = ['^']
        i, n = 0, len(pattern)
        while i < n:
            c = pattern[i]
            if c == '*':
                if i + 1 < n and pattern[i + 1] == '*':
                    i += 2
                    if i < n and pattern[i] == '/':
                        out.append('(?:[^/]+/)*')  # **/ → zero-or-more directory segments
                        i += 1
                    else:
                        out.append('.*')  # trailing ** → rest of path (any depth)
                    continue
                out.append('[^/]*')  # single * → one path segment (no slash)
                i += 1
                continue
            if c == '?':
                out.append('[^/]')
                i += 1
                continue
            if c == '.':
                out.append(r'\.')
                i += 1
                continue
            if c in '()[]{}|+^$\\':
                out.append('\\' + c)
                i += 1
                continue
            out.append(c)
            i += 1
        out.append('$')
        return bool(re.match(''.join(out), path))

async def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python enhanced_packer.py <profile_name>")
        print("Available profiles: sovereign-audit, engineering-p3, kali-oversight,")
        print("                    youtube-research-primer, sprint-context")
        return

    profile_name = sys.argv[1]
    packer = EnhancedContextPacker()
    await packer.load_config()
    try:
        output_dir = await packer.pack(profile_name)
        profile = packer.profiles[profile_name]
        # Compute total tokens from manifest
        manifest_path = output_dir / "00_PROJECT_MANIFEST.md"
        print(f"\n✅ Pack '{profile_name}' generated at: {output_dir}")
        print(f"   Manifest: {manifest_path}")
        print(f"\n📡 Hivemind Broadcast (copy to operator):")
        print(f"   hivemind_post_context(")
        print(f"     channel='opencode', entity='packer',")
        print(f"     model='enhanced-packer-v2',")
        print(f"     task_current='Context pack generated: {profile_name}',")
        print(f"     focus_chain=['context-packer', 'sprint-prep'],")
        print(f"     decisions=['Pack {profile_name} generated with PII masking and XML escaping'],")
        print(f"     continuation='Upload {output_dir} to Claude.ai Projects'")
        print(f"   )")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    anyio.run(main)