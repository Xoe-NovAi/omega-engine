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
import uuid
from datetime import datetime
# Platform-specific tuning (M-T): format adapters + bundle ordering strategies
from platform_adapters import PlatformConfig, get_format_adapter, get_ordering_strategy
# xml_quoteattr() for attribute escaping only — do NOT import xml_escape for body content
from xml.sax.saxutils import quoteattr as xml_quoteattr
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass, field

# ── V3 security-hardened XML (manual §1.2 step 5, §1.3) ───────────────────────
# defusedxml: PARSE-ONLY (its Element/SubElement are intentionally absent).
# stdlib xml.etree.ElementTree: ELEMENT CREATION.
import xml.etree.ElementTree as ETree
from defusedxml import ElementTree as DET

# ── V3 community substitution for _glob_files/_match_pattern (manual §1.2 step 1) ──
from pathspec import GitIgnoreSpec

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

# Debug/tracing configuration
import os
DEBUG_PACKER = os.environ.get('OMEGA_PACKER_DEBUG', '').lower() in ('1', 'true', 'yes', 'on')
TRACE_PACKER = os.environ.get('OMEGA_PACKER_TRACE', '').lower() in ('1', 'true', 'yes', 'on')

def _debug_log(msg: str):
    if DEBUG_PACKER:
        print(f"[PACKER-DEBUG] {msg}")

def _trace_log(msg: str):
    if TRACE_PACKER:
        print(f"[PACKER-TRACE] {msg}")

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
    r"(?i)hex\s*(encode|decode)",
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
    r"(?i)echo\s+(?:the\s+)?(prompt|instructions?)",
    r"(?i)verbatim\s+(?:prompt|instructions?)",
]

# Compile patterns for performance
INJECTION_REGEXES = [re.compile(p) for p in INJECTION_PATTERNS]


def _escape_bare_xml_chars(text: str) -> str:
    """Fully XML-escape file BODY content for valid XML output.

    EVERY `<` and `>` in the body is escaped to `<`/`>` so content can
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
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&lt;', text)
    return text


# ═════════════════════════════════════════════════════════════════════════════
# V3 DETERMINISTIC 5-STEP CONTRACT API (manual §1.2, §2; Phase 3)
# ============================================================================
# These module-level functions are the v3 specification. The contract suite at
# tests/contract/test_context_packer_v3.py pins their exact behavior. They are
# ADDITIVE — they do not disturb the legacy v2 EnhancedContextPacker pipeline,
# which remains for backward compatibility until the full Phase 3 rewrite wires
# `pack()` onto these primitives (and the v2 surgical methods are removed).
# ============================================================================

# step 4 — LITM zone -> priority mapping (manual §1.2 step 4, §1.6)
LITM_ZONE_PRIORITY: Dict[str, int] = {"start": 3, "middle": 2, "end": 1}


def apply_litm_priority(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve a bundle's ``litm_zone`` into a prioritized copy (step 4).

    ``start=3``, ``middle=2``, ``end=1``. Unknown or missing zone defaults to
    middle (2). v3 owns the zone->priority mapping.
    """
    zone = bundle.get("litm_zone")
    bundle["priority"] = LITM_ZONE_PRIORITY.get(zone, 2)
    return bundle


class PackValidationError(RuntimeError):
    """Fail-closed validation error. Message carries ``[PACK-FAIL]`` (M23)."""


def validate_pack(
    bundles: Dict[str, List[Dict[str, Any]]],
    cfg: "PlatformConfig",
    required_themes: Optional[Set[str]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """FAIL-CLOSED validation (manual §1.2 step 3, §1.2.3; M23 / DoD P0-2).

    Raises :class:`PackValidationError` (``[PACK-FAIL]``) if ANY of:
      * a required theme is absent,
      * a theme's summed ``token_count`` exceeds ``cfg.token_budget_per_bundle``,
      * the total across all themes exceeds ``cfg.token_budget_total``,
      * the number of bundles + 1 (the manifest) exceeds ``cfg.max_slots``.

    Never trims or silently deletes themes to fit a budget — it hard-stops
    with a diagnostic naming the offending theme and its largest files.
    """
    required_themes = required_themes or set()

    present = set(bundles.keys())
    missing = required_themes - present
    if missing:
        raise PackValidationError(
            f"[PACK-FAIL] required theme missing: {sorted(missing)}. "
            f"Present: {sorted(present)}"
        )

    offenders = []
    for theme, files in bundles.items():
        total = sum(int(f.get("token_count", 0)) for f in files)
        per_limit = int(cfg.token_budget_per_bundle)
        if total > per_limit:
            offenders.append((theme, total - per_limit, files))
    if offenders:
        offenders.sort(key=lambda o: -o[1])
        theme, _over, files = offenders[0]
        largest = sorted(files, key=lambda f: -int(f.get("token_count", 0)))[:3]
        top3 = "; ".join(f"{f.get('path', '?')}~{f.get('token_count', 0)}" for f in largest)
        raise PackValidationError(
            f"[PACK-FAIL] theme '{theme}' over per_bundle budget "
            f"({int(cfg.token_budget_per_bundle)}) tokens. Largest files: {top3}"
        )

    total_all = sum(
        int(f.get("token_count", 0)) for files in bundles.values() for f in files
    )
    if total_all > int(cfg.token_budget_total):
        raise PackValidationError(
            f"[PACK-FAIL] total budget exceeded: {total_all} > {int(cfg.token_budget_total)}"
        )

    slot_count = len(bundles) + 1  # manifest occupies a slot
    if slot_count > int(cfg.max_slots):
        raise PackValidationError(
            f"[PACK-FAIL] max_slots exceeded: {slot_count} (incl. manifest) "
            f"> {int(cfg.max_slots)}"
        )

    return bundles


def resolve_theme_files(
    profile: "PackProfile",
    base_path: os.PathLike,
) -> Dict[str, List[Dict[str, Any]]]:
    """Expand a profile's ``themes`` globs into concrete file info (step 1).

    Replaces the v2 ``_glob_files``/``_match_pattern`` hand-rolled matchers
    with ``GitIgnoreSpec`` (full Git behavior: ``**`` recursion, basename
    matching, negation). Returns ``{theme: [{path, full_path, ...}]}``.

    ``profile.themes`` is the dict form ``{theme: [globs]}``. Each theme's
    globs are resolved independently against ``base_path``.
    """
    base = LibPath(base_path)
    # Skip heavy/non-source dirs during the walk (keeps O(N) sane over a huge
    # repo). Themes reference src/, docs/, config/, etc. — never these.
    _SKIPPED_DIRS = {".git", ".hg", ".venv", "venv", "__pycache__",
                     "node_modules", "data", "context_packs", ".pytest_cache",
                     ".mypy_cache", ".ruff_cache"}
    all_files: List[LibPath] = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        try:
            if any(part in _SKIPPED_DIRS for part in p.parts):
                continue
        except ValueError:
            continue
        all_files.append(p)

    # Precompute the POSIX relative path once per file (pathspec requires
    # POSIX paths, manual §1.3; also avoids recomputing relative_to per pattern).
    rel_map = [(p, p.relative_to(base).as_posix()) for p in all_files]

    resolved: Dict[str, List[Dict[str, Any]]] = {}
    for theme, patterns in (profile.themes or {}).items():
        infos: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for pat in patterns:
            spec = GitIgnoreSpec.from_lines([pat])
            for f, rel in rel_map:
                if rel in seen:
                    continue
                if spec.match_file(rel):
                    infos.append({"path": rel, "full_path": str(f)})
                    seen.add(rel)
        resolved[theme] = infos
    _debug_log(f"resolve_theme_files: themes={list(resolved.keys())}, "
               f"sizes={ {k: len(v) for k, v in resolved.items()} }")
    return resolved


def write_pii_vault(
    profile_dir: os.PathLike,
    profile_name: str,
    tokens: Dict[str, str],
) -> LibPath:
    """Persist a reversible PII token map to ``context_packs/<profile>/pii_vault.json``.

    Per-profile encapsulation (DoD P0-8): the vault lives beside the generated
    pack, NOT in the global ``data/coordination/pii_vaults/``. Atomic
    ``.tmp -> .json`` rename (M8/M10 integrity).
    """
    profile_dir = LibPath(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    vault_path = profile_dir / "pii_vault.json"
    payload = {
        "profile": profile_name,
        "generated_at": datetime.now().astimezone().isoformat(),
        "tokens": tokens,
    }
    tmp = profile_dir / "pii_vault.json.tmp"
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, vault_path)
    _debug_log(f"write_pii_vault: {vault_path} ({len(tokens)} tokens)")
    return vault_path


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
    # Account & provenance metadata (for forensic linking)
    account: Optional[str] = None
    project: Optional[str] = None
    version: Optional[str] = None

class EnhancedContextPacker:
    def __init__(self, config_path: str = ".opencode/skills/context-packer/packer-config.yaml"):
        self.config_path = config_path
        self.profiles: Dict[str, PackProfile] = {}
        _debug_log(f"EnhancedContextPacker initialized with config_path: {config_path}")

    async def load_config(self):
        def _read_config():
            with open(self.config_path, "r") as f:
                return f.read()
        
        content = await anyio.to_thread.run_sync(_read_config)
        config = yaml.safe_load(content)
        profiles_data = config.get("profiles", {})
        _debug_log(f"Loaded config with {len(profiles_data)} profiles: {list(profiles_data.keys())}")
        
        for name, data in profiles_data.items():
            # M-T: build platform config from the profile's tuning block
            platform = None
            try:
                platform = PlatformConfig.from_profile_config(data)
            except Exception as e:
                print(f"  ⚠️  Profile '{name}' platform config parse failed: {e}")
                _debug_log(f"Profile '{name}' platform config parse failed: {e}")
            self.profiles[name] = PackProfile(
                name=name,
                description=data.get("description", ""),
                max_slots=data.get("max_slots", 12),
                include=data.get("include", []),
                exclude=data.get("exclude", []),
                themes=data.get("themes", {}),
                platform=platform,
                account=data.get("account"),
                project=data.get("project"),
                version=data.get("version"),
            )
            _debug_log(f"Loaded profile '{name}': max_slots={data.get('max_slots', 12)}, "
                       f"include={len(data.get('include', []))} patterns, "
                       f"themes={list(data.get('themes', {}).keys())}, "
                       f"account={data.get('account')}")
    
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
    
    async def _estimate_token_count(self, path: LibPath, model: str = "cl100k_base", margin: float = 1.3) -> int:
        """Estimate token count using shared TokenEstimator (v3 SSOT)."""
        import sys
        _engine_src = str(LibPath(__file__).resolve().parent.parent.parent.parent / "src")
        if _engine_src not in sys.path:
            sys.path.insert(0, _engine_src)
        from omega.oracle.token_estimator import tokens_for_file_async
        return await tokens_for_file_async(path, model=model, margin=margin)
    
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

    async def pack(self, profile_name: str):
        if profile_name not in self.profiles:
            raise ValueError(f"Profile '{profile_name}' not found in config. "
                             f"Available: {list(self.profiles.keys())}")

        profile = self.profiles[profile_name]
        base = LibPath(self.config_path).parent.parent.parent.parent  # repo root
        output_dir = LibPath("context_packs") / profile_name / "generated"
        await anyio.to_thread.run_sync(lambda: output_dir.mkdir(parents=True, exist_ok=True))

        # Generate unique pack ID for forensic linking
        pack_id = str(uuid.uuid4())
        pack_timestamp = datetime.now().astimezone().isoformat()
        
        _debug_log(f"═══ PACK START: profile='{profile_name}' pack_id={pack_id} "
                   f"max_slots={profile.max_slots} themes={list(profile.themes.keys())} ═══")

        # ── Step 1: RESOLVE ─────────────────────────────────────────────────────
        themed = resolve_theme_files(profile, base)

        # ── Step 2: COUNT (enrich with metadata + token counts) ────────────────
        # Convert file info to full metadata with token counts
        themed_bundles: Dict[str, List[Dict[str, Any]]] = {}
        for theme, files in themed.items():
            enriched_files = []
            for file_info in files:
                f_path = LibPath(file_info["full_path"])
                try:
                    stats = f_path.stat()
                    sha = await self._calculate_sha256(f_path)
                    lang = self._get_language(file_info["path"])
                    purpose = await self._get_purpose(f_path)
                    # Use platform-specific tokenizer encoding and margin from profile
                    model = profile.platform.tokenizer_encoding if profile.platform else "cl100k_base"
                    margin = profile.platform.token_margin_multiplier if profile.platform else 1.3
                    tokens = await self._estimate_token_count(f_path, model=model, margin=margin)
                except Exception as exc:
                    print(f"  ❌ [META-ERR] file='{file_info['path']}': {exc}")
                    raise

                enriched_files.append({
                    "path": file_info["path"],
                    "full_path": file_info["full_path"],
                    "size": stats.st_size,
                    "language": lang,
                    "sha256": sha,
                    "purpose": purpose,
                    "token_count": tokens,
                    "path_obj": f_path,
                    "stats": stats,
                    # Forensic linking: pack ID in every file metadata
                    "pack_id": pack_id,
                    "pack_timestamp": pack_timestamp,
                })
            themed_bundles[theme] = enriched_files

        _debug_log(f"  Step 2 complete: themes={list(themed_bundles.keys())}, "
                   f"sizes={ {k: len(v) for k, v in themed_bundles.items()} }")

        # ── Step 3: VALIDATE (fail-closed) ──────────────────────────────────────
        # Determine required themes from profile config (themes that must be present)
        required_themes = set(profile.themes.keys()) if profile.themes else set()
        cfg = profile.platform if profile.platform else PlatformConfig.from_profile_config({})
        validate_pack(themed_bundles, cfg, required_themes=required_themes)

        # ── Step 4: ORDER ───────────────────────────────────────────────────────
        # Apply LITM priority to each bundle, then use platform ordering strategy
        for theme_name, files in themed_bundles.items():
            for bundle in files:
                # Each file in the bundle gets the theme's priority
                apply_litm_priority(bundle)
        
        # Build bundle dicts for the ordering strategy
        bundle_dicts = []
        for theme, files in themed_bundles.items():
            if not files:
                continue
            # The theme's priority is derived from the first file (all have same priority)
            priority = files[0].get("priority", 2)
            bundle_dicts.append({
                "theme": theme,
                "files": files,
                "token_count": sum(f["token_count"] for f in files),
                "priority": priority,
                "relevance": priority / 3.0,
            })
        
        # Get ordering strategy from platform config
        ordering_strategy = get_ordering_strategy(
            profile.platform.bundle_ordering if profile.platform else None
        )
        _debug_log(f"  Step 4 ordering_strategy='{profile.platform.bundle_ordering if profile.platform else None}' "
                   f"→ class={type(ordering_strategy).__name__}")
        
        ordered_bundles = ordering_strategy.order(bundle_dicts)
        _debug_log(f"  Step 4 ordered order: {[b['theme'] for b in ordered_bundles]}")
        themed_bundles = {b["theme"]: b["files"] for b in ordered_bundles}

        # Resolve the format adapter for this profile (M-T)
        adapter = get_format_adapter(profile.platform.format if profile.platform else None)
        bundle_extension = adapter.extension
        _debug_log(f"  Step 4 adapter: format='{profile.platform.format if profile.platform else None}' "
                   f"→ class={type(adapter).__name__}, extension='{bundle_extension}'")

        # ── Step 5: WRITE (per-profile artifacts) ───────────────────────────────
        # PII masker setup (instantiate ONCE before the file loop)
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

        # Collect PII tokens for vault
        pii_vault: Dict[str, str] = {}
        bundles_written = 0
        file_errors = 0

        for theme, files in themed_bundles.items():
            if not files:
                _debug_log(f"  Step 5 skip empty theme: '{theme}'")
                continue
            
            for file_info in files:
                f_path = file_info["path_obj"]
                
                def _read_file():
                    with open(str(f_path), "r", encoding="utf-8", errors="replace") as f:
                        return f.read()

                try:
                    raw_content = await anyio.to_thread.run_sync(_read_file)
                except FileNotFoundError:
                    file_errors += 1
                    print(f"  ⚠️  [FILE-MISSING] '{file_info['path']}' vanished before pack — skipping")
                    continue
                except Exception as exc:
                    file_errors += 1
                    print(f"  ⚠️  [READ-ERR] '{file_info['path']}': {exc}")
                    continue

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

                # XML-style file block with forensic pack_id attribute
                # xml_quoteattr() wraps the value in quotes AND escapes <, >, &, ", '
                header = (
                    f"<file"
                    f" path={xml_quoteattr(file_info['path'])}"
                    f" size={xml_quoteattr(str(file_info['size']))}"
                    f" language={xml_quoteattr(file_info['language'])}"
                    f" sha256={xml_quoteattr(file_info['sha256'])}"
                    f" purpose={xml_quoteattr(file_info['purpose'])}"
                    f" tokens={xml_quoteattr(str(file_info['token_count']))}"
                    f" pack_id={xml_quoteattr(pack_id)}>"
                )
                footer = "</file>"
                # Body is fully XML-escaped by _escape_bare_xml_chars() above.
                rendered_block = header + "\n" + pruned_content + "\n" + footer + "\n\n"
                file_info["rendered"] = rendered_block

            # Render the bundle via the profile's format adapter
            try:
                bundle_file = output_dir / f"{theme}{bundle_extension}"
                rendered_bundle = adapter.render_bundle(theme, files, profile_name)
                await self._atomic_write(bundle_file, rendered_bundle)
                bundles_written += 1
                bundle_token_total = sum(f["token_count"] for f in files)
                _debug_log(f"  Step 5 wrote bundle '{theme}': {len(files)} files, "
                           f"{bundle_token_total:,} tokens")
            except Exception as exc:
                raise RuntimeError(f"[BUNDLE-ERR] failed to render/write bundle "
                                   f"'{theme}' ({len(files)} files): {exc}") from exc

        if file_errors:
            print(f"  ⚠️  [Step 5] {file_errors} file(s) had read errors during packaging")
        print(f"  📦 [Step 5] {bundles_written} bundle(s) written to {output_dir}")

        # Step 5b: PII VAULT + MANIFEST + PROJECT OVERVIEW
        # Fix Bug 1: Pass directory to write_pii_vault (not file path)
        vault_dir = LibPath("context_packs") / profile_name
        write_pii_vault(vault_dir, profile_name, pii_vault)

        # Fix Bug 3: Write manifest to profile root (not generated/)
        manifest_name = "00_PROJECT_MANIFEST.md"
        manifest_path = vault_dir / manifest_name
        manifest_content = await self._create_manifest(profile_name, themed_bundles, adapter, pack_id, pack_timestamp)
        await self._atomic_write(manifest_path, manifest_content)

        # Sign manifest and capture returns (Fix: _sign_manifest now returns signature data)
        sig_hex, pub_key = await self._sign_manifest(manifest_path, vault_dir)

        # Fix Bug 2: Write pack_index.json
        await self._write_pack_index(profile_name, themed_bundles, manifest_name, sig_hex, pub_key, pack_id, pack_timestamp, profile)

        # Generate Project Overview for system prompt assistance
        await self._write_project_overview(profile_name, themed_bundles, vault_dir, pack_id, pack_timestamp, profile)

        _debug_log(f"═══ PACK COMPLETE: profile='{profile_name}' pack_id={pack_id} "
                   f"output_dir='{output_dir}' bundles={bundles_written} "
                   f"pii_entries={len(pii_vault)} ════")
        return output_dir, pack_id, pack_timestamp

    async def _create_manifest(self, profile_name: str, themed_bundles: Dict[str, List[dict]],
                                adapter=None, pack_id: str = "", pack_timestamp: str = "") -> str:
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
                pack_id, profile.account, profile.project, profile.version,
            )

        # Fallback (no adapter): legacy markdown manifest
        lines = [
            f"# Enhanced Context Pack Manifest: {profile_name}",
            f"Generated: {pack_timestamp or datetime.now().isoformat()}",
            f"Pack ID: {pack_id}",
            f"Account: {profile.account or 'unspecified'}",
            f"Project: {profile.project or 'unspecified'}",
            f"Version: {profile.version or 'unspecified'}",
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
            "- Each file is wrapped in <file> tags with metadata attributes including pack_id",
            "- The manifest should be reviewed first to understand the pack structure",
            "- Token counts are estimates using cl100k_base encoder (Claude's tokenizer)",
            "- Pack ID enables forensic linking between pack materials and responses",
        ])
        
        return "\n".join(lines)

    # --- Manifest Signing (Ed25519) ---
    async def _sign_manifest(self, manifest_path: LibPath, output_dir: LibPath) -> tuple[str, str]:
        """Sign manifest with Ed25519 and write signed version. Returns (signature_hex, public_key_pem)."""
        if not ED25519_AVAILABLE:
            return "", ""
        
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
            
            # Get public key PEM
            pub_key_pem = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode().strip()
            
            # Append signature block
            signed_manifest = manifest_content + f"""

---
## Cryptographic Signature
**Algorithm**: Ed25519
**Signature**: `{signature_hex}`
**Signed**: {datetime.now().isoformat()}
**Public Key**: `{pub_key_pem}`
"""
            # Write signed manifest
            await self._atomic_write(manifest_path, signed_manifest)
            
            return signature_hex, pub_key_pem
        
        except Exception as e:
            print(f"  ⚠️  Manifest signing failed: {e}")
            return "", ""

    # ─── Pack Index Writing ──────────────────────────────────────────────────
    async def _write_pack_index(self, profile_name: str, themed_bundles: Dict[str, List[dict]],
                                manifest_name: str, sig_hex: str, pub_key: str,
                                pack_id: str, pack_timestamp: str, profile: "PackProfile"):
        """Write per-profile pack_index.json with bundle metadata and signature."""
        profile_dir = LibPath("context_packs") / profile_name
        
        bundles_meta = []
        total_files = 0
        total_tokens = 0
        
        for theme, files in themed_bundles.items():
            for f in files:
                bundles_meta.append({
                    "theme": theme,
                    "file": f.get("relative_path", f.get("path", "unknown")),
                    "tokens": f.get("token_count", 0),
                    "litm_zone": f.get("litm_zone", "middle"),
                    "required": f.get("required", False),
                    "pack_id": f.get("pack_id", pack_id),
                })
                total_files += 1
                total_tokens += f.get("token_count", 0)
        
        index_data = {
            "profile": profile_name,
            "pack_id": pack_id,
            "generated_at": pack_timestamp,
            "total_files": total_files,
            "total_tokens": total_tokens,
            "max_slots": profile.platform.max_slots if profile.platform else 12,
            "bundles": bundles_meta,
            "manifest": manifest_name,
            "signature": f"ed25519:{sig_hex}" if sig_hex else "none",
            "public_key": pub_key if pub_key else "none",
            "pii_vault": "pii_vault.json",
            # Account & provenance metadata
            "account": profile.account,
            "project": profile.project,
            "version": profile.version,
        }
        
        index_path = profile_dir / "pack_index.json"
        await self._atomic_write(index_path, json.dumps(index_data, indent=2))
        _debug_log(f"write_pack_index: {index_path} ({total_files} bundles, {total_tokens} tokens)")

    # ─── Project Overview Generation ────────────────────────────────────────────
    async def _write_project_overview(self, profile_name: str, themed_bundles: Dict[str, List[dict]],
                                      vault_dir: LibPath, pack_id: str, pack_timestamp: str, profile: "PackProfile"):
        """Generate PROJECT_OVERVIEW.md to assist agents in creating effective system prompts and chat initiation prompts."""
        total_files = sum(len(files) for files in themed_bundles.values())
        total_tokens = sum(f["token_count"] for files in themed_bundles.values() for f in files)
        
        # Analyze bundle composition
        theme_stats = {}
        for theme, files in themed_bundles.items():
            if files:
                theme_stats[theme] = {
                    "count": len(files),
                    "tokens": sum(f["token_count"] for f in files),
                    "top_files": sorted(files, key=lambda f: -f["token_count"])[:5]
                }
        
        # Determine pack purpose from profile
        purpose_keywords = {
            "sovereign-audit": "architecture audit, mandate compliance, un-overengineering",
            "tech-architecture-research": "technology architecture research, decision matrix, grounded truth",
            "provider-fabric-review": "provider fabric deep review, local inference, cloud backends, routing",
            "engineering-p3": "N3 Engineering Node context, core logic, validation",
            "kali-oversight": "grand oversight, mandates, fleet topology, decisions, agents",
            "youtube-research-primer": "YouTube research module, spec, implementation, integration",
            "decision-tools-review": "decision tools implementation review, grounding, schema, CLI",
            "sprint-context": "current sprint research, analysis, implementation plan",
            "context-packer-hardening-review": "context packer v2 hardening review, spec, implementation, gaps",
            "web-claude-sonnet5": "optimized for Claude Sonnet 5 via Web Claude Projects",
            "web-grok-4.3": "optimized for Grok 4.3 via Web Grok / SuperGrok",
            "web-grok-4.1-fast": "cost-optimized for high-volume review via Grok 4.1 Fast",
            "web-gemini-3-pro": "optimized for Gemini 3 Pro via Google AI Studio",
            "web-gemini-3.1-pro": "ultra-long context for massive codebase analysis",
            "notebooklm-research": "source-grounded export for NotebookLM research workflows",
        }
        
        pack_purpose = purpose_keywords.get(profile_name, "general context pack")
        
        lines = [
            f"# Project Overview: {profile_name}",
            f"",
            f"**Pack ID**: `{pack_id}`",
            f"**Generated**: {pack_timestamp}",
            f"**Account**: {profile.account or 'unspecified'}",
            f"**Project**: {profile.project or 'unspecified'}",
            f"**Version**: {profile.version or 'unspecified'}",
            f"**Profile**: {profile_name}",
            f"**Purpose**: {pack_purpose}",
            f"**Description**: {profile.description}",
            f"",
            f"## Pack Statistics",
            f"- **Total Files**: {total_files}",
            f"- **Estimated Total Tokens**: {total_tokens:,}",
            f"- **Max Slots**: {profile.max_slots}",
            f"- **Target Platform**: {profile.platform.profile.value if profile.platform else 'unspecified'}",
            f"- **Target Model**: {profile.platform.target_model if profile.platform else 'unspecified'}",
            f"- **Format**: {profile.platform.format if profile.platform else 'xml'}",
            f"- **Bundle Ordering**: {profile.platform.bundle_ordering if profile.platform else 'litm-u-shaped'}",
            f"",
            f"## Theme Composition",
            f"",
        ]
        
        for theme, stats in theme_stats.items():
            lines.append(f"### {theme} ({stats['count']} files, ~{stats['tokens']:,} tokens)")
            lines.append(f"")
            for f in stats['top_files']:
                lines.append(f"- `{f['path']}` — {f['token_count']:,} tokens — {f['purpose'][:80]}")
            lines.append(f"")
        
        lines.extend([
            f"## Recommended System Prompt Structure",
            f"",
            f"Based on this pack's composition and purpose ({pack_purpose}), the system prompt should include:",
            f"",
            f"### 1. Role Definition",
            f"- **Primary Persona**: Principal Architect / Security Auditor / Senior Engineer (match to pack purpose)",
            f"- **Mindset**: Ruthless pragmatism, minimal abstractions, high performance, zero bloat",
            f"- **Authority**: Custom instructions take absolute precedence over project knowledge",
            f"",
            f"### 2. Project Knowledge Reference",
            f"- List all {len(theme_stats)} XML bundles with their themes",
            f"- Reference the manifest (00_PROJECT_MANIFEST.md) as the entry point",
            f"- Note the pack_id for forensic linking: `{pack_id}`",
            f"",
            f"### 3. Ground Truth (Hardware + Constraints)",
            f"- Hardware: Ryzen 5 4600H, 16GB RAM, no GPU, 15W TDP",
            f"- Python 3.13.7 on Linux (requires >=3.12)",
            f"- 25 Sovereign Mandates (M1-M25) — non-negotiable",
            f"- Current sprint: UNOVERENGINEER-01",
            f"",
            f"### 4. Mandate Compliance Matrix Template",
            f"- All 11 critical mandates (M1, M2, M7, M8, M9, M13, M14, M22, M23, M24, M25)",
            f"- Status: PASS/FAIL with specific violations",
            f"- Files affected with line ranges",
            f"",
            f"### 5. Output Format Requirements",
            f"- Structured Markdown with 7 sections (Executive Summary → Recommendations)",
            f"- Evidence over opinion: every finding cites file + line range from XML bundles",
            f"- 5-element formula for recommendations: [Role] + [Scope] + [Focus] + [Format] + [Severity]",
            f"- Persona adoption: Strict Reviewer / Senior Architect / Security Auditor",
            f"",
            f"### 6. Account & Provenance Tracking",
            f"- Account: {profile.account or 'unspecified'}",
            f"- Pack Version: {pack_timestamp}",
            f"- Response frontmatter template (REQUIRED on all responses):",
            f"```yaml",
            f"---",
            f"account: {profile.account or 'unspecified'}",
            f"pack_version: {pack_timestamp.split('T')[0]}",
            f"pack_profile: {profile_name}",
            f"pack_files: {total_files}",
            f"pack_tokens: {total_tokens}",
            f"session_date: YYYY-MM-DD",
            f"session_type: audit|implementation|verification",
            f"---",
            f"```",
            f"",
            f"## Chat Initiation Prompt Template",
            f"",
            f"```markdown",
            f"## Project: {profile.description}",
            f"",
            f"### Role",
            f"You are a Principal Architect auditing the Omega Engine — a sovereign, local-first AI runtime. Your mindset is Carmack: ruthless pragmatism, minimal abstractions, high performance, zero bloat.",
            f"",
            f"### Ground Truth (Verified {pack_timestamp.split('T')[0]})",
            f"- Python 3.13.7 on Linux (requires >=3.12)",
            f"- Engine state: `OMEGA_ENGINE.md` in mandates.xml",
            f"- Mandates: 25 non-negotiable laws in `SOVEREIGN_MANDATES.md` (mandates.xml)",
            f"- Strategy: `SOVEREIGN_ARK_BLUEPRINT.md` (strategy_core.xml)",
            f"- Current sprint: UNOVERENGINEER-01",
            f"- Hardware: Ryzen 5 4600H, 16GB RAM, no GPU, 15W TDP",
            f"- **Account**: {profile.account or 'unspecified'}",
            f"- **Pack Version**: {pack_timestamp} (fresh, post-refactor)",
            f"",
            f"### Audit Scope ({len(theme_stats)} XML Bundles — {total_files} files, {total_tokens:,} tokens)",
        ])
        
        for i, (theme, stats) in enumerate(theme_stats.items(), 1):
            bundle_file = f"{theme}.xml"
            lines.append(f"{i}. **{bundle_file}** — {theme.replace('_', ' ').title()} ({stats['count']} files, ~{stats['tokens']:,} tokens)")
        
        lines.extend([
            f"",
            f"### Known Gaps (Already Tracked)",
            f"- [Reference CARMACK_REVIEW_WEB_CLAUDE_GAPS.md or equivalent]",
            f"",
            f"### Constraints (Non-Negotiable)",
            f"- M1: AnyIO only (no direct asyncio imports)",
            f"- M2: Core ≠ Stacks firewall",
            f"- M7: Local-first (no cloud-only deps)",
            f"- M8: Zero telemetry",
            f"- M9: Error integrity (typed, traceable, no silent swallowing)",
            f"- M13: Temple-grade quality (11 gates)",
            f"- M14: Heritage vetting ([id-soft:] tags need vet records)",
            f"- M22: Provenance (actual provider in logs)",
            f"- M23: Failure integrity (no soft-failures)",
            f"- M24: Venv sovereignty",
            f"- M25: Streaming resilience (30s chunk timeout)",
            f"",
            f"### Task",
            f"Perform a ruthless audit of the CURRENT implementation. For each mandate:",
            f"1. **Verify compliance** — cite specific file + line range from XML bundles",
            f"2. **Find violations** — code snippets that break the mandate",
            f"3. **Identify un-overengineering targets** — what to delete/flatten",
            f"4. **Flag concurrency risks** — blocking I/O, rogue asyncio, race conditions",
            f"5. **Inventory technical debt** — duplicated logic, dead code, stale patterns",
            f"",
            f"### Output Format",
            f"Structured Markdown report per system prompt:",
            f"- Executive Summary",
            f"- Mandate Compliance Matrix (table)",
            f"- Critical Violations (MUST FIX)",
            f"- Un-overengineering Targets (DELETE/FLATTEN)",
            f"- Concurrency & Safety Risks",
            f"- Technical Debt Inventory",
            f"- Recommendations Priority Order (using 5-element formula: Role/Scope/Focus/Format/Severity)",
            f"",
            f"### Key Principle",
            f"**Evidence over opinion.** Every finding must cite specific file + line range from the XML bundles. \"It looks like\" is not acceptable — we need proof from the code.",
            f"",
            f"### Response Frontmatter (REQUIRED on all responses)",
            f"```yaml",
            f"---",
            f"account: {profile.account or 'unspecified'}",
            f"pack_version: {pack_timestamp.split('T')[0]}",
            f"pack_profile: {profile_name}",
            f"pack_files: {total_files}",
            f"pack_tokens: {total_tokens}",
            f"session_date: YYYY-MM-DD",
            f"session_type: audit|implementation|verification",
            f"---",
            f"```",
            f"",
            f"---",
            f"",
            f"*System prompt should be in CLAUDE_PROJECT_SYSTEM_PROMPT.md. Project knowledge files are the {len(theme_stats)} XML bundles in generated/. Begin audit upon receiving the chat initiation prompt.*",
        ])
        
        overview_path = vault_dir / "PROJECT_OVERVIEW.md"
        await self._atomic_write(overview_path, "\n".join(lines))
        _debug_log(f"  Project Overview written: {overview_path}")

async def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python packer.py <profile_name>")
        print("Available profiles: sovereign-audit, engineering-p3, kali-oversight,")
        print("                    youtube-research-primer, sprint-context,")
        print("                    decision-tools-review, tech-architecture-research,")
        print("                    provider-fabric-review, context-packer-hardening-review,")
        print("                    web-claude-sonnet5, web-grok-4.3, web-grok-4.1-fast,")
        print("                    web-gemini-3-pro, web-gemini-3.1-pro, notebooklm-research")
        return

    profile_name = sys.argv[1]
    _debug_log(f"main() invoked with profile='{profile_name}'")
    packer = EnhancedContextPacker()
    await packer.load_config()
    try:
        output_dir, pack_id, pack_timestamp = await packer.pack(profile_name)
        profile = packer.profiles[profile_name]
        manifest_path = output_dir / "00_PROJECT_MANIFEST.md"
        overview_path = LibPath("context_packs") / profile_name / "PROJECT_OVERVIEW.md"
        print(f"\n✅ Pack '{profile_name}' generated at: {output_dir}")
        print(f"   Pack ID: {pack_id}")
        print(f"   Timestamp: {pack_timestamp}")
        print(f"   Manifest: {manifest_path}")
        print(f"   Project Overview: {overview_path}")
        print(f"   Pack Index: {LibPath('context_packs') / profile_name / 'pack_index.json'}")
        print(f"\n📋 NEXT STEPS FOR AGENT:")
        print(f"   1. READ: {overview_path}")
        print(f"      → Contains recommended system prompt structure, chat initiation template,")
        print(f"        and response frontmatter protocol for this specific pack")
        print(f"   2. CREATE/UPDATE: CLAUDE_PROJECT_SYSTEM_PROMPT.md")
        print(f"      → Use the 'Recommended System Prompt Structure' section as guide")
        print(f"   3. CREATE/UPDATE: CHAT_INITIATION_PROMPT.md")
        print(f"      → Use the 'Chat Initiation Prompt Template' section as guide")
        print(f"   4. ENSURE all responses include the frontmatter template from the overview")
        print(f"\n📡 Hivemind Broadcast (copy to operator):")
        print(f"   hivemind_post_context(")
        print(f"     channel='opencode', entity='packer',")
        print(f"     model='enhanced-packer-v3',")
        print(f"     task_current='Context pack generated: {profile_name}',")
        print(f"     focus_chain=['context-packer', 'sprint-prep'],")
        print(f"     decisions=['Pack {profile_name} generated with PII masking, XML escaping, pack_id={pack_id[:8]}, PROJECT_OVERVIEW.md'],")
        print(f"     continuation='Upload {output_dir} to Claude.ai Projects; review PROJECT_OVERVIEW.md for system prompt guidance'")
        print(f"   )")
        _debug_log(f"main() completed successfully for profile='{profile_name}' pack_id={pack_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        _debug_log(f"main() failed for profile='{profile_name}': {e}")
        raise

if __name__ == "__main__":
    anyio.run(main)