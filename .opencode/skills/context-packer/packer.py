#!/usr/bin/env python3
"""
Enhanced Context Packer for Omega Engine
Improvements over original:
1. XML-based output format for better Claude comprehension
2. Enhanced purpose extraction for multiple file types
3. Token-aware packing strategy (basic implementation)
4. Manifest-first approach
5. Ed25519 manifest signing for integrity verification
6. Injection pattern scanning for security
7. Per-bundle token limit enforcement
8. Lost-in-the-middle mitigation via bundle reordering
"""

import anyio
from pathlib import Path as LibPath
import yaml
import hashlib
import os
import re
import json
# Platform-specific tuning (M-T): format adapters + bundle ordering strategies
from platform_adapters import PlatformConfig, get_format_adapter, get_ordering_strategy
# xml_quoteattr() for attribute escaping only — do NOT import xml_escape for body content
from xml.sax.saxutils import quoteattr as xml_quoteattr
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    import tiktoken
    ENCODER = tiktoken.get_encoding("cl100k_base")  # Claude's tokenizer
except ImportError:
    ENCODER = None
    print("Warning: tiktoken not installed. Token counting will be approximate.")

# Ed25519 for manifest signing
try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    ED25519_AVAILABLE = True
except ImportError:
    ED25519_AVAILABLE = False
    print("Warning: cryptography not installed. Manifest signing disabled.")

# ─── Injection Pattern Scanner ──────────────────────────────────────────────
# OWASP LLM Top 10 2026 + Microsoft/Google research patterns
INJECTION_PATTERNS = [
    # Direct instruction override
    r"(?i)ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions?",
    r"(?i)forget\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions?|prompts?)",
    r"(?i)disregard\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions?|prompts?)",
    r"(?i)override\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions?|prompts?)",
    
    # Role manipulation
    r"(?i)act\s+as\s+(?:DAN|developer|admin|root|system)",
    r"(?i)you\s+are\s+now\s+(?:DAN|developer|admin|root|system)",
    r"(?i)switch\s+to\s+(?:developer|admin|root|system)\s+mode",
    r"(?i)enable\s+(?:developer|admin|root|system)\s+mode",
    
    # System prompt extraction
    r"(?i)reveal\s+(?:your\s+)?system\s+prompt",
    r"(?i)show\s+(?:me\s+)?(?:your\s+)?system\s+prompt",
    r"(?i)output\s+(?:your\s+)?system\s+prompt",
    r"(?i)print\s+(?:your\s+)?system\s+prompt",
    r"(?i)what\s+is\s+(?:your\s+)?system\s+prompt",
    
    # Data exfiltration
    r"(?i)send\s+(?:all\s+)?(?:data|files|secrets|keys|tokens)\s+to",
    r"(?i)exfiltrate\s+(?:data|files|secrets)",
    r"(?i)upload\s+(?:data|files|secrets)\s+to",
    r"(?i)email\s+(?:data|files|secrets)\s+to",
    
    # Tool/agent manipulation
    r"(?i)call\s+(?:the\s+)?(?:function|tool|api)\s+",
    r"(?i)execute\s+(?:code|command|script)",
    r"(?i)run\s+(?:code|command|script)",
    r"(?i)invoke\s+(?:function|tool|api)",
    
    # Jailbreak variants
    r"(?i)DAN\s+(?:mode|prompt)",
    r"(?i)Do\s+Anything\s+Now",
    r"(?i)STAN\s+(?:mode|prompt)",
    r"(?i)STRIVE\s+(?:mode|prompt)",
    r"(?i)MANGO\s+(?:mode|prompt)",
    
    # Encoding/obfuscation attempts
    r"(?i)base64\s*(?:encode|decode)",
    r"(?i)rot13\s*(?:encode|decode)",
    r"(?i)hex\s*(?:encode|decode)",
    r"(?i)unicode\s*(?:encode|decode)",
    
    # Hypothetical framing
    r"(?i)hypothetically\s+(?:speaking|,)",
    r"(?i)in\s+a\s+hypothetical\s+(?:scenario|situation)",
    r"(?i)imagine\s+(?:you\s+are|that\s+you)",
    r"(?i)pretend\s+(?:you\s+are|that\s+you)",
    
    # Authority impersonation
    r"(?i)I\s+am\s+(?:the\s+)?(?:developer|admin|creator|owner)",
    r"(?i)as\s+(?:the\s+)?(?:developer|admin|creator|owner)",
    r"(?i)authorized\s+(?:by|access)",
    
    # Continuation attacks
    r"(?i)continue\s+(?:from|where\s+you\s+left\s+off)",
    r"(?i)pick\s+up\s+where\s+you\s+left\s+off",
    
    # Prompt leaking
    r"(?i)repeat\s+(?:the\s+)?(?:prompt|instructions?)",
    r"(?i)echo\s+(?:the\s+)?(?:prompt|instructions?)",
    r"(?i)verbatim\s+(?:prompt|instructions?)",
]

# Compile patterns for performance
INJECTION_REGEXES = [re.compile(p) for p in INJECTION_PATTERNS]

# ─── Token Limits ────────────────────────────────────────────────────────────
# Per-bundle token limits (with safety margin for Claude Projects)
MAX_BUNDLE_TOKENS = 15000  # Conservative limit per bundle
MAX_TOTAL_TOKENS = 150000  # Total pack limit (well under 1M context)

# ─── Lost-in-the-Middle Bundle Ordering ──────────────────────────────────────
# Bundles that should be at START (positions 1-3) - critical for reviewer
CRITICAL_START_BUNDLES = {
    "grounding", "decisions", "decree", "verdict", "summary", "overview"
}

# Bundles that should be at END (last 2-3) - action items, next steps
CRITICAL_END_BUNDLES = {
    "handoff", "exit_protocol", "next_steps", "action_items", "verdict", "recommendations"
}

# Bundles that go in MIDDLE - reference material, evidence, logs
MIDDLE_BUNDLES = {
    "implementation", "engine_state", "mandates", "session_log", "research", 
    "pivot_log", "evidence", "logs", "history", "appendix"
}

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
    platform: Optional["PlatformConfig"] = None  # platform-specific tuning (M7/M18)

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
            # M-T: build platform config from the profile's tuning block
            platform = None
            try:
                platform = PlatformConfig.from_profile_config(data)
            except Exception as e:
                print(f"  ⚠️  Profile '{name}' platform config parse failed: {e}")
            self.profiles[name] = PackProfile(
                name=name,
                description=data.get("description", ""),
                max_slots=data.get("max_slots", 12),
                include=data.get("include", []),
                exclude=data.get("exclude", []),
                themes=data.get("themes", {}),
                platform=platform,
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

    # ─── Security: Injection Pattern Scanner ───────────────────────────────────
    async def _scan_for_injection(self, content: str, file_path: str) -> List[str]:
        """Scan content for prompt injection patterns.
        
        Returns a list of detected pattern names, or empty list if clean.
        """
        # Use simple regex scanning for now - can be enhanced with LLM-based detection
        detections = []
        for pattern in INJECTION_REGEXES:
            if pattern.search(content):
                detections.append(pattern.pattern[:50])
        return detections

    # ─── Token Limit Enforcement ───────────────────────────────────────────────
    def _enforce_token_limits(self, themed_bundles: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
        """Enforce per-bundle and total token limits by splitting oversized bundles."""
        result = {}
        total_tokens = 0
        
        for theme, files in themed_bundles.items():
            if not files:
                continue
                
            bundle_tokens = sum(f["token_count"] for f in files)
            
            if bundle_tokens <= MAX_BUNDLE_TOKENS:
                result[theme] = files
                total_tokens += bundle_tokens
                continue
            
            # Split oversized bundle - REPLACE original with split parts
            split_bundles = self._split_bundle_by_tokens(theme, files)
            for split_theme, split_files in split_bundles.items():
                result[split_theme] = split_files
                total_tokens += sum(f["token_count"] for f in split_files)
        
        # Check total limit
        if total_tokens > MAX_TOTAL_TOKENS:
            # Trim lowest-priority bundles (middle bundles first)
            result = self._trim_to_token_limit(result, MAX_TOTAL_TOKENS)
        
        return result

    def _split_bundle_by_tokens(self, theme: str, files: List[dict]) -> Dict[str, List[dict]]:
        """Split a bundle into multiple sub-bundles by token count."""
        split_bundles = {}
        current_bundle = []
        current_tokens = 0
        split_num = 1
        
        # Sort files by token count descending for better packing
        sorted_files = sorted(files, key=lambda x: x["token_count"], reverse=True)
        
        for file_info in sorted_files:
            if current_tokens + file_info["token_count"] > MAX_BUNDLE_TOKENS and current_bundle:
                split_bundles[f"{theme}_part{split_num}"] = current_bundle
                split_num += 1
                current_bundle = []
                current_tokens = 0
            
            current_bundle.append(file_info)
            current_tokens += file_info["token_count"]
        
        if current_bundle:
            split_bundles[f"{theme}_part{split_num}"] = current_bundle
        
        return split_bundles

    def _trim_to_token_limit(self, themed_bundles: Dict[str, List[dict]], limit: int) -> Dict[str, List[dict]]:
        """Trim bundles to fit within total token limit, removing lowest priority first."""
        # Priority order: start bundles > end bundles > middle bundles
        all_bundles = []
        for theme, files in themed_bundles.items():
            priority = 0
            if any(kw in theme.lower() for kw in CRITICAL_START_BUNDLES):
                priority = 3
            elif any(kw in theme.lower() for kw in CRITICAL_END_BUNDLES):
                priority = 2
            else:
                priority = 1
            
            bundle_tokens = sum(f["token_count"] for f in files)
            all_bundles.append((priority, theme, files, bundle_tokens))
        
        # Sort by priority (lowest first for removal)
        all_bundles.sort(key=lambda x: x[0])
        
        total_tokens = sum(b[3] for b in all_bundles)
        result = {b[1]: b[2] for b in all_bundles}
        
        # Remove lowest priority bundles until under limit
        for priority, theme, files, bundle_tokens in all_bundles:
            if total_tokens <= limit:
                break
            if priority == 1:  # Only remove middle bundles
                del result[theme]
                total_tokens -= bundle_tokens
        
        return result

    # ─── Lost-in-the-Middle Mitigation ─────────────────────────────────────────
    def _reorder_bundles_for_litm(self, themed_bundles: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
        """Reorder bundles to place critical content at start and end (U-shaped attention)."""
        start_bundles = {}
        middle_bundles = {}
        end_bundles = {}
        
        for theme, files in themed_bundles.items():
            theme_lower = theme.lower()
            
            if any(kw in theme_lower for kw in CRITICAL_START_BUNDLES):
                start_bundles[theme] = files
            elif any(kw in theme_lower for kw in CRITICAL_END_BUNDLES):
                end_bundles[theme] = files
            else:
                middle_bundles[theme] = files
        
        # Sort each group by token count (larger first for better context)
        def sort_by_tokens(bundles):
            return dict(sorted(bundles.items(), 
                             key=lambda x: sum(f["token_count"] for f in x[1]), 
                             reverse=True))
        
        start_bundles = sort_by_tokens(start_bundles)
        middle_bundles = sort_by_tokens(middle_bundles)
        end_bundles = sort_by_tokens(end_bundles)
        
        # Combine: start + middle + end
        result = {}
        result.update(start_bundles)
        result.update(middle_bundles)
        result.update(end_bundles)
        
        return result

    # ─── Bundle Consolidation (≤12 files) ──────────────────────────────────────
    def _consolidate_bundles(self, themed_bundles: Dict[str, List[dict]], max_slots: int) -> Dict[str, List[dict]]:
        """Consolidate bundles to stay within max_slots limit (minus 1 for manifest)."""
        max_bundles = max_slots - 1  # Reserve 1 slot for manifest
        active_bundles = {k: v for k, v in themed_bundles.items() if v}
        
        if len(active_bundles) <= max_bundles:
            return active_bundles
        
        # Sort by priority (start/end bundles kept, middle merged)
        bundle_priorities = []
        for theme, files in active_bundles.items():
            theme_lower = theme.lower()
            if any(kw in theme_lower for kw in CRITICAL_START_BUNDLES):
                priority = 3
            elif any(kw in theme_lower for kw in CRITICAL_END_BUNDLES):
                priority = 2
            else:
                priority = 1
            bundle_priorities.append((priority, theme, files))
        
        # Sort by priority (highest first)
        bundle_priorities.sort(key=lambda x: x[0], reverse=True)
        
        # Keep high-priority bundles, merge rest into "general"
        result = {}
        general_files = []
        
        for priority, theme, files in bundle_priorities:
            if len(result) < max_bundles:
                result[theme] = files
            else:
                general_files.extend(files)
        
        if general_files:
            result["general"] = general_files
        
        return result

    # ─── Manifest Signing (Ed25519) ────────────────────────────────────────────
    async def _sign_manifest(self, manifest_path: LibPath, output_dir: LibPath):
        """Sign manifest with Ed25519 and write signed version."""
        if not ED25519_AVAILABLE:
            return
        
        try:
            # Read current manifest
            def _read():
                with open(manifest_path, "r") as f:
                    return f.read()
            manifest_content = await anyio.to_thread.run_sync(_read)
            
            # Load or generate signing key
            key_path = LibPath("data/coordination/packer_signing_key.pem")
            key_path.parent.mkdir(parents=True, exist_ok=True)
            
            if key_path.exists():
                def _load_key():
                    with open(key_path, "rb") as f:
                        return serialization.load_pem_private_key(f.read(), password=None)
                private_key = await anyio.to_thread.run_sync(_load_key)
            else:
                def _gen_key():
                    key = ed25519.Ed25519PrivateKey.generate()
                    pem = key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                    with open(key_path, "wb") as f:
                        f.write(pem)
                    return key
                private_key = await anyio.to_thread.run_sync(_gen_key)
            
            # Sign manifest
            def _sign():
                signature = private_key.sign(manifest_content.encode("utf-8"))
                return signature.hex()
            
            signature_hex = await anyio.to_thread.run_sync(_sign)
            
            # Append signature block
            signed_manifest = manifest_content + f"""

---
## Cryptographic Signature
**Algorithm**: Ed25519
**Signature**: `{signature_hex}`
**Signed**: {datetime.now().isoformat()}
**Public Key**: `{private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode().strip()}`
"""
            # Write signed manifest
            await self._atomic_write(manifest_path, signed_manifest)
            
        except Exception as e:
            print(f"  ⚠️  Manifest signing failed: {e}")

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
        
        # Phase 4: Distribute files across themes
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
        
        # Phase 5: Consolidate bundles to stay within max_slots (≤12 files including manifest)
        themed_bundles = self._consolidate_bundles(themed_bundles, profile.max_slots)
        
        # Phase 6: Enforce per-bundle token limits (split oversized bundles)
        themed_bundles = self._enforce_token_limits(themed_bundles)
        
        # Phase 6b: Re-consolidate after token limit enforcement to stay within max_slots
        themed_bundles = self._consolidate_bundles(themed_bundles, profile.max_slots)
        
        # Phase 7: Reorder bundles for lost-in-the-middle mitigation
        # M-T: use the profile's platform-specific ordering strategy (default LITM-U)
        ordering_strategy = get_ordering_strategy(
            profile.platform.bundle_ordering if profile.platform else None
        )
        # Build bundle dicts with priority/relevance metadata for the strategy
        bundle_dicts = []
        for theme, files in themed_bundles.items():
            if not files:
                continue
            theme_lower = theme.lower()
            priority = 1
            if any(kw in theme_lower for kw in CRITICAL_START_BUNDLES):
                priority = 3
            elif any(kw in theme_lower for kw in CRITICAL_END_BUNDLES):
                priority = 2
            bundle_dicts.append({
                "theme": theme,
                "files": files,
                "token_count": sum(f["token_count"] for f in files),
                "priority": priority,
                "relevance": priority / 3.0,
            })
        ordered_bundles = ordering_strategy.order(bundle_dicts)
        themed_bundles = {b["theme"]: b["files"] for b in ordered_bundles}

        # Resolve the format adapter for this profile (M-T)
        adapter = get_format_adapter(profile.platform.format if profile.platform else None)
        bundle_extension = adapter.extension
        
        # Phase 8: Packaging
        manifest_entries = []
        
        # Create manifest first
        manifest_content = await self._create_manifest(profile_name, themed_bundles, adapter)
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
        # M8/M23: collect PII token maps for reversible vault persistence (OPF schema).
        # The vault is written at data/coordination/pii_vaults/{profile}.json so the
        # masked pack can be detokenized later (GDPR Recital 26 / EU AI Act Art. 10 lineage).
        pii_vault: Dict[str, str] = {}
        for theme, files in themed_bundles.items():
            if not files:
                continue
            
            bundle_content = []
            bundle_token_total = 0
            
            for file_info in files:
                f_path = file_info["path_obj"]
                
                def _read_file():
                    with open(str(f_path), "r", encoding="utf-8", errors="replace") as f:
                        return f.read()

                raw_content = await anyio.to_thread.run_sync(_read_file)

                # Security: Scan for injection patterns before PII masking
                injection_matches = await self._scan_for_injection(raw_content, file_info["path"])
                if injection_matches:
                    print(f"  ⚠️  Injection pattern detected in {file_info['path']}: {injection_matches}")
                    # Log but continue - the content will be XML-escaped anyway
                
                # PII masking before external upload (M8 Zero Telemetry / M7 Local-First)
                # API: detect() is async (runs in thread), tokenize() is sync.
                # The masker instance was created once before this loop — do NOT re-instantiate here.
                if _masker is not None:
                    detections = await _masker.detect(raw_content)
                    if detections:
                        masked_content, token_map = _masker.tokenize(raw_content, detections)
                        content = masked_content
                        # Persist this file's reversible token map into the vault
                        for placeholder, original in token_map.tokens.items():
                            pii_vault[placeholder] = original
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
                rendered_block = header + "\n" + pruned_content + "\n" + footer + "\n\n"
                bundle_content.append(rendered_block)
                bundle_token_total += file_info["token_count"]

                # Store rendered block for the format adapter + PII vault
                file_info["rendered"] = rendered_block

                manifest_entries.append(f"- {file_info['path']} -> {theme}{bundle_extension} ({file_info['token_count']} tokens)")

            # Check bundle token limit
            if bundle_token_total > MAX_BUNDLE_TOKENS:
                print(f"  ⚠️  Bundle {theme} exceeds token limit: {bundle_token_total} > {MAX_BUNDLE_TOKENS}")

            # M-T: render the bundle via the profile's format adapter
            bundle_file = output_dir / f"{theme}{bundle_extension}"
            rendered_bundle = adapter.render_bundle(theme, files, profile_name)
            await self._atomic_write(bundle_file, rendered_bundle)
        
        # Phase 8b: Persist reversible PII vault (OPF schema) — M8/M23.
        # The vault lives at data/coordination/pii_vaults/{profile}.json (gitignored,
        # local-only) so the masked pack can be detokenized later for lineage/audit.
        if pii_vault:
            vault_path = LibPath("data/coordination/pii_vaults") / f"{profile_name}.json"
            await anyio.to_thread.run_sync(lambda: vault_path.parent.mkdir(parents=True, exist_ok=True))
            vault_payload = {
                "schema": "opf.reversible.v1",
                "profile": profile_name,
                "generated": datetime.now().isoformat(),
                "token_count": len(pii_vault),
                "tokens": pii_vault,
            }
            await self._atomic_write(vault_path, json.dumps(vault_payload, indent=2))
            print(f"  🔐 PII vault persisted: {vault_path} ({len(pii_vault)} tokens)")
        else:
            print("  🔓 No PII detected in pack — no vault written.")
        
        # Phase 9: Sign manifest with Ed25519 for integrity verification
        await self._sign_manifest(manifest_path, output_dir)
        
        return output_dir
    
    async def _create_manifest(self, profile_name: str, themed_bundles: Dict[str, List[dict]],
                               adapter=None) -> str:
        total_files = sum(len(files) for files in themed_bundles.values())
        total_tokens = sum(f["token_count"] for files in themed_bundles.values() for f in files)
        profile = self.profiles[profile_name]

        # M-T: if a format adapter is provided, delegate manifest rendering to it
        # (carries target_model + prompt_caching metadata).
        if adapter is not None:
            bundles = []
            for theme, files in themed_bundles.items():
                if not files:
                    continue
                bundles.append({
                    "theme": theme,
                    "files": files,
                    "token_count": sum(f["token_count"] for f in files),
                })
            platform = profile.platform
            return adapter.render_manifest(
                profile_name, bundles, total_files, total_tokens,
                profile.description, profile.max_slots,
                platform.target_model if platform else None,
                platform.prompt_caching if platform else False,
            )

        # Fallback (no adapter): legacy markdown manifest
        lines = [
            f"# Enhanced Context Pack Manifest: {profile_name}",
            f"Generated: {datetime.now().isoformat()}",
            f"Description: {profile.description}",
            f"Total Files: {total_files}",
            f"Estimated Total Tokens: {total_tokens}",
            f"Max Slots: {profile.max_slots}",
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
        print("                    youtube-research-primer, sprint-context,")
        print("                    decision-tools-review")
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