import anyio
from pathlib import Path as LibPath
import yaml
import hashlib
import os
import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class FileMetadata:
    relative_path: str
    size_bytes: int
    language: str
    sha256: str
    purpose: str = "Not specified"

@dataclass
class PackProfile:
    name: str
    description: str
    max_slots: int
    include: List[str]
    exclude: List[str]
    themes: Dict[str, List[str]]

class ContextPacker:
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
        ext = os.path.splitext(path)[1]
        mapping = {
            ".py": "Python",
            ".md": "Markdown",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".json": "JSON",
            ".sh": "Shell",
            ".txt": "Text",
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

    async def _get_purpose(self, path: LibPath) -> str:
        # Simple purpose extraction from docstring for Python files
        if path.suffix == ".py":
            def _read_doc():
                try:
                    with open(str(path), "r") as f:
                        content = f.read()
                        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                        if match:
                            return match.group(1).strip().split('\n')[0]
                except Exception:
                    pass
                return "General implementation"
            return await anyio.to_thread.run_sync(_read_doc)
        return "General implementation"

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
            # Simple glob implementation using anyio.LibPath
            # Note: anyio.LibPath doesn't have a direct glob that returns relative paths easily
            # We'll use os.walk or LibPath.glob in a thread
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

        # Phase 2: Consolidation
        themed_bundles: Dict[str, List[str]] = {theme: [] for theme in profile.themes}
        themed_bundles["general"] = []

        for f in final_files:
            matched_theme = False
            for theme, patterns in profile.themes.items():
                for pattern in patterns:
                    if self._match_pattern(f, pattern):
                        themed_bundles[theme].append(f)
                        matched_theme = True
                        break
                if matched_theme: break
            if not matched_theme:
                themed_bundles["general"].append(f)

        # Phase 3: Pruning (Theme Merging)
        # If bundles > max_slots - 1 (leaving one for manifest), merge low-priority
        active_themes = [t for t, files in themed_bundles.items() if files]
        if len(active_themes) > profile.max_slots - 1:
            # Merge all but the most populated themes into 'general'
            sorted_themes = sorted(active_themes, key=lambda t: len(themed_bundles[t]), reverse=True)
            to_merge = sorted_themes[profile.max_slots - 2:]
            for t in to_merge:
                themed_bundles["general"].extend(themed_bundles[t])
                themed_bundles[t] = []

        # Phase 4: Packaging
        manifest_entries = []
        
        for theme, files in themed_bundles.items():
            if not files: continue
            
            bundle_content = []
            for f_rel in files:
                f_path = LibPath(f_rel)
                if not os.path.exists(f_rel):
                    continue
                
                stats = f_path.stat()
                sha = await self._calculate_sha256(f_path)
                lang = self._get_language(f_rel)
                purpose = await self._get_purpose(f_path)
                
                def _read_file():
                    with open(str(f_path), "r", errors="replace") as f:
                        return f.read()
                
                content = await anyio.to_thread.run_sync(_read_file)
                pruned_content = await self._prune_content(content)
                
                header = f"---\nFILE: {f_rel}\nSIZE: {stats.st_size}\nLANG: {lang}\nSHA256: {sha}\nPURPOSE: {purpose}\n---\n"
                bundle_content.append(header + pruned_content + "\n\n---\n")
                manifest_entries.append(f"- {f_rel} -> {theme}.md")

            bundle_file = output_dir / f"{theme}.md"
            await self._atomic_write(bundle_file, "\n".join(bundle_content))

        # Generate Manifest
        manifest_content = f"# Project Manifest: {profile_name}\n"
        manifest_content += f"Timestamp: {datetime.now().isoformat()}\n"
        manifest_content += f"Description: {profile.description}\n\n"
        manifest_content += "## Included Files\n"
        manifest_content += "\n".join(manifest_entries)
        
        await self._atomic_write(output_dir / "00_PROJECT_MANIFEST.md", manifest_content)

        return output_dir

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
        print("Usage: python packer.py <profile_name>")
        return

    profile_name = sys.argv[1]
    packer = ContextPacker()
    await packer.load_config()
    try:
        output_dir = await packer.pack(profile_name)
        print(f"Successfully packed {profile_name} to {output_dir}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    anyio.run(main)
