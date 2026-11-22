# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 WAD Loader — Universal Runtime Container Loader
# AP: AP-WAD-LOADER-v1.1.0
#
# Implements the WAD (Where's All Data) architecture.
# Loads self-contained stacks from config/wads/ and registers them into the
# EntityRegistry and Voice system.
#
# Respects the Engine-Stack Firewall: only modifies runtime state.
#
# [id-soft: vet-043] WAD System — IWAD/PWAD separation with backward scan
#   DOOM's WAD format (w_wad.c:376) scans backwards so PWAD patch files
#   take precedence over IWAD base entries. Omega mirrors this: later WAD
#   entity definitions override earlier ones.
# [id-soft: vet-044] 4-Path VFS — search order: active stack → _omega_default
#   Q3A's files.c:39-75 defines base + cd + home + current game search order.
#   Omega's wad_loader follows the same override chain pattern.

# S1.5a Hardening: Schema validation, file size limits, adapter whitelist.


# DocRef: docs/architecture/TRAINING_PIPELINE.md
import logging
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import anyio
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .entity_registry import DEFAULT_ENTITY_MODEL, EntityRegistry, Entity
from .world_state import world_state, WorldLump
from omega.errors import OmegaError
from omega.governance.config_resolver import WADS_DIR

# ── S1.5a Hardening Constants ────────────────────────────────────────
# [id-soft: vet-015] ZONEID — size sentinel for file validation
MAX_YAML_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB — prevents loading huge YAML files
MAX_ENTITY_NAME_LENGTH = 128  # Entity name length cap
MAX_DOMAINS_PER_ENTITY = 20  # Max domains per entity

# Adapter module whitelist — loaded from config/adapter_whitelist.yaml (Phase 4.2).
# Falls back to hardcoded defaults if config file is missing.
def _load_adapter_whitelist() -> Set[str]:
    """Load adapter module whitelist from config/adapter_whitelist.yaml."""
    try:
        from omega.governance.config_resolver import _get_config_dir
        config_dir = _get_config_dir()
        whitelist_path = config_dir / "adapter_whitelist.yaml"
        if whitelist_path.exists():
            with open(whitelist_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            modules = data.get("adapter_modules", [])
            if isinstance(modules, list):
                return set(str(m) for m in modules)
    except (OSError, yaml.YAMLError, ImportError):
        pass
    # Hardcoded fallback
    return {
        "omega.memory.adapters",
        "omega.memory.adapters.mnemosyne_adapter",
    }

ADAPTER_MODULE_WHITELIST: Set[str] = _load_adapter_whitelist()

# Required/core manifest field types (WadManifest V1)
MANIFEST_FIELD_TYPES = {
    "name": str,
    "version": str,
    "entities": (list, dict),
    "adapters": (list, dict),
}

# WadManifest V2 — optional heritage / IWAD metadata fields (explicit allow-list).
# Still extra=forbid: unknown keys reject. V2 fields are typed when present.
# [D-281 sidecar / ho_881bae336522] arcana_novai + _omega_default use these.
MANIFEST_V2_OPTIONAL_FIELD_TYPES = {
    "author": str,
    "description": str,
    "license": str,
    "type": str,  # iwad | pwad
    "mode": str,
    "requires_engine": str,
    "startup": dict,
    "voices": (list, dict),
    "vr_scenes": (list, dict),
    "dependencies": (list, dict),
    "hierarchy": str,  # relative path override for hierarchy.yaml
    "priority": int,
}

# Required entity field types (kept for backward compatibility)
ENTITY_FIELD_TYPES = {
    "name": str,
    "domains": list,
    "model": str,
    "personality": str,
    "temperature": (int, float),
    "context_window": int,
    "slots": list,
}

# Core fields extracted directly into Entity; everything else goes to metadata.
CORE_ENTITY_FIELDS: Set[str] = {
    "name",
    "domains",
    "model",
    "personality",
    "temperature",
    "context_window",
    "slots",
    "role",
    "container",
    "port",
    "wad_source",
    "priority",
}


class WADEntitySchema(BaseModel):
    """Canonical schema for WAD entity YAML `entity:` blocks (2.7 consolidation).

    Strict on core types (no silent str->float or bool->int coercion) while
    allowing WAD-specific extra fields (archetype, element, sigil, etc.) to
    pass through into Entity.metadata per D-282 / M2 Engine-Stack Firewall.
    """

    model_config = ConfigDict(extra="allow", strict=True)

    name: Optional[str] = Field(default=None, max_length=MAX_ENTITY_NAME_LENGTH)
    domains: List[Any] = Field(default_factory=list, max_length=MAX_DOMAINS_PER_ENTITY)
    model: str = Field(default=DEFAULT_ENTITY_MODEL)
    personality: str = Field(default="")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    context_window: int = Field(default=8192, ge=1, le=131072)
    slots: List[Any] = Field(default_factory=list)
    role: Optional[str] = Field(default=None)
    container: bool = Field(default=False)
    port: Optional[int] = Field(default=None, ge=1, le=65535)
    wad_source: Optional[str] = Field(default=None)
    priority: Optional[int] = Field(default=None)
    nodes: Optional[List[Any]] = Field(default=None)
    sovereignty: Optional[Any] = Field(default=None)

    @field_validator("temperature", mode="before")
    @classmethod
    def _validate_temperature_numeric(cls, v: Any) -> float:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f"expected int or float, got {type(v).__name__}")
        return float(v)

    @field_validator("context_window", "port", "priority", mode="before")
    @classmethod
    def _validate_strict_int(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError(f"expected int, got {type(v).__name__}")
        return v


def validate_wad_entity(
    ent_data: Dict[str, Any], default_name: str = ""
) -> Tuple[WADEntitySchema, Dict[str, Any]]:
    """Validate a raw `entity:` dict against WADEntitySchema.

    Returns (validated_model, metadata_dict_for_extra_and_noncore_fields).
    Raises ValueError on validation error.
    """
    if not isinstance(ent_data, dict):
        raise ValueError(f"'entity' must be a mapping, got {type(ent_data).__name__}")
    try:
        validated = WADEntitySchema.model_validate(ent_data)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc

    if not validated.name and default_name:
        if len(default_name) > MAX_ENTITY_NAME_LENGTH:
            raise ValueError(
                f"Entity name too long ({len(default_name)} chars, max {MAX_ENTITY_NAME_LENGTH})"
            )
        validated.name = default_name

    wad_metadata = {
        k: v
        for k, v in ent_data.items()
        if k not in CORE_ENTITY_FIELDS and v is not None
    }
    return validated, wad_metadata


def _get_engine_version_str() -> str:
    """Return the running engine version string (SSOT: pyproject.toml)."""
    try:
        from omega import __version__ as _v
    except ImportError:
        return "0.0.0+unknown"
    if isinstance(_v, str) and _v:
        return _v
    return "0.0.0+unknown"


def enforce_engine_compatibility(stack_name: str, requires_engine: Any | None) -> None:
    """Enforce WAD `requires_engine` semver against the running engine (M23).

    Contract: WAD_LOADER_CONTRACT.md §6.2 (`packaging.SpecifierSet`).

    - Missing (`None`) or empty/whitespace `requires_engine` → no constraint
      (equivalent to the contract's `manifest.get("requires_engine", ">=0.0.0")`
      default: any engine version passes).
    - Otherwise the running engine version MUST satisfy the specifier.
      Incompatible or malformed specifiers FAIL LOUD via `ValueError`
      carrying the exact required vs running versions (no soft-skip).

    Note on prereleases: enforced via
    `spec.contains(engine_version, prereleases=True)` rather than the
    contract pseudo-code's bare `engine_version not in required`, so that
    prerelease engine builds (e.g. `1.6.0-alpha.1`) satisfy stable lower
    bounds (e.g. `>=0.4.0`). Verified equivalent for the shipped IWADs
    under `packaging==26.2`; the explicit flag is the PEP 440-correct
    hardening.

    Raises:
        ValueError: If the specifier is invalid or not satisfied.
    """
    if requires_engine is None:
        return
    if isinstance(requires_engine, str) and not requires_engine.strip():
        return
    engine_version_str = _get_engine_version_str()
    try:
        spec = SpecifierSet(requires_engine)
    except InvalidSpecifier as e:
        raise ValueError(
            f"WAD {stack_name} has invalid requires_engine "
            f"'{requires_engine}' (running engine {engine_version_str}): {e}"
        ) from e
    try:
        engine_version = Version(engine_version_str)
    except InvalidVersion as e:
        raise ValueError(
            f"Running engine version '{engine_version_str}' is not valid "
            f"PEP 440 (required by WAD {stack_name} requires_engine "
            f"'{requires_engine}'): {e}"
        ) from e
    if not spec.contains(engine_version, prereleases=True):
        raise ValueError(
            f"WAD {stack_name} requires_engine '{requires_engine}' "
            f"not satisfied by running engine {engine_version_str}"
        )


logger = logging.getLogger(__name__)


class WADVersion:
    """Semantic version parser and comparator for WAD versioning (Phase 4.5).

    Supports major.minor.patch with pre-release suffixes (e.g., "1.0.0-rc1").
    """

    def __init__(self, version_str: str):
        self.raw = version_str.strip()
        parts = self.raw.split("-", 1)
        self.pre = parts[1] if len(parts) > 1 else ""
        num_parts = parts[0].split(".")
        self.major = int(num_parts[0]) if len(num_parts) > 0 and num_parts[0].isdigit() else 0
        self.minor = int(num_parts[1]) if len(num_parts) > 1 and num_parts[1].isdigit() else 0
        self.patch = int(num_parts[2]) if len(num_parts) > 2 and num_parts[2].isdigit() else 0

    def __lt__(self, other: "WADVersion") -> bool:
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        # Pre-release versions are lower than release versions
        if self.pre and not other.pre:
            return True
        if not self.pre and other.pre:
            return False
        return self.pre < other.pre

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WADVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch, self.pre) == (other.major, other.minor, other.patch, other.pre)

    def __le__(self, other: "WADVersion") -> bool:
        return self < other or self == other

    def __gt__(self, other: "WADVersion") -> bool:
        return not (self <= other)

    def __ge__(self, other: "WADVersion") -> bool:
        return not (self < other)

    def __str__(self) -> str:
        return self.raw

    def __repr__(self) -> str:
        return f"WADVersion({self.raw!r})"


class WADLoader:
    """Loads Omega Engine stacks (WADs) from the filesystem."""

    def __init__(
        self,
        registry: EntityRegistry,
        wads_dir: Optional[Path] = None,
        adapter_registry: Optional[Any] = None,
    ):
        self.registry = registry
        # OMEGA_WADS_DIR env override preserved; default from config_resolver (D-281 Phase II)
        self.wads_dir = wads_dir or Path(os.environ.get("OMEGA_WADS_DIR", str(WADS_DIR)))
        self._startup_messages: Dict[str, str] = {}  # stack_name -> startup message
        self._loaded_wads: Dict[str, Dict[str, Any]] = {}  # stack_name -> metadata
        self.active_hierarchy_path: Optional[Path] = None
        self._adapter_registry = adapter_registry  # MemoryAdapterRegistry (optional)

        if os.environ.get("OMEGA_ENV") != "test":
            try:
                self.wads_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                logger.warning(f"WADs directory read-only: {self.wads_dir}")

    @property
    def loaded_wads(self) -> Dict[str, Dict[str, Any]]:
        """Return a shallow copy of currently loaded WAD metadata."""
        return dict(self._loaded_wads)

    async def _discover_wads(self) -> List[Dict[str, Any]]:
        """Discover all WAD directories and read their manifest metadata.

        Scans the wads directory for subdirectories containing a manifest.yaml.
        For each valid WAD, extracts metadata: name, type (iwad/pwad),
        dependencies, priority, and version.

        Returns:
            List of WAD metadata dicts, sorted by discovery order.
            Each dict has keys: name, type, dependencies, priority, version,
            path, manifest_path.
        """
        discovered: List[Dict[str, Any]] = []

        try:
            async for entry in anyio.Path(self.wads_dir).iterdir():
                if not await entry.is_dir():
                    continue

                stack_name = entry.name
                wad_path = self.wads_dir / stack_name
                manifest_path = wad_path / "manifest.yaml"

                if not await anyio.Path(manifest_path).exists():
                    logger.debug(f"WAD {stack_name} has no manifest.yaml. Skipping discovery.")
                    continue

                # Read manifest for metadata
                try:
                    async with await anyio.open_file(str(manifest_path), "r") as f:
                        manifest = yaml.safe_load(await f.read())

                    if manifest is None:
                        logger.warning(f"WAD {stack_name} manifest is empty. Skipping discovery.")
                        continue

                    # Support both flat and wad:-wrapped manifests
                    if "wad" in manifest:
                        manifest = manifest["wad"]

                    wad_type = manifest.get("type", "pwad")
                    dependencies = manifest.get("dependencies", [])
                    if isinstance(dependencies, str):
                        dependencies = [dependencies]
                    elif not isinstance(dependencies, list):
                        dependencies = []

                    discovered.append(
                        {
                            "name": stack_name,
                            "type": wad_type,
                            "dependencies": dependencies,
                            "priority": manifest.get("priority", 0),
                            "version": manifest.get("version", "unknown"),
                            "path": wad_path,
                            "manifest_path": manifest_path,
                        }
                    )
                except (OSError, yaml.YAMLError) as e:
                    logger.warning(f"Failed to read manifest for WAD {stack_name}: {e}")
                    continue

        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to iterate WADs directory for discovery: {e}")

        return discovered

    async def _resolve_load_order(self, discovered: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve the load order for discovered WADs.

        Ordering rules:
        1. IWADs load before PWADs (IWAD = base, PWAD = patch/overlay).
        2. Dependencies load before dependents (topological sort).
        3. Circular dependencies are detected and reported.

        Args:
            discovered: List of WAD metadata dicts from _discover_wads().

        Returns:
            WAD metadata dicts in resolved load order.

        Raises:
            OmegaError: If a circular dependency is detected.
        """
        # Build name -> metadata lookup
        name_to_wad: Dict[str, Dict[str, Any]] = {w["name"]: w for w in discovered}

        # Assign base priority: IWAD = 100, PWAD = 0, plus manifest priority
        def effective_priority(wad: Dict[str, Any]) -> int:
            base = 100 if wad["type"] == "iwad" else 0
            return base + wad.get("priority", 0)

        # Topological sort with cycle detection
        # We use a modified Kahn's algorithm that also respects type-based priority
        # for tie-breaking among independent nodes.

        # Build adjacency: dependency -> [dependents]
        # and in-degree: wad_name -> count of unmet dependencies
        in_degree: Dict[str, int] = {}
        dependents: Dict[str, List[str]] = {w["name"]: [] for w in discovered}

        for wad in discovered:
            name = wad["name"]
            in_degree[name] = 0
            for dep in wad["dependencies"]:
                if dep in name_to_wad:
                    dependents[dep].append(name)
                    in_degree[name] += 1
                else:
                    logger.warning(
                        f"WAD {name} depends on unknown WAD '{dep}'. Dependency will be ignored."
                    )

        # Kahn's algorithm with priority queue (sorted by effective priority)
        # Use a list as a priority queue (sorted each iteration — small N)
        ready = sorted(
            [name for name, deg in in_degree.items() if deg == 0],
            key=lambda n: effective_priority(name_to_wad[n]),
            reverse=True,  # Higher priority first
        )

        resolved: List[Dict[str, Any]] = []
        processed: Set[str] = set()

        while ready:
            # Pick highest-priority ready node
            current_name = ready.pop(0)
            current_wad = name_to_wad[current_name]
            resolved.append(current_wad)
            processed.add(current_name)

            # Reduce in-degree of dependents
            new_ready: List[str] = []
            for dep_name in dependents[current_name]:
                in_degree[dep_name] -= 1
                if in_degree[dep_name] == 0:
                    new_ready.append(dep_name)

            # Merge new ready nodes into the ready list, maintaining priority order
            ready.extend(new_ready)
            ready.sort(
                key=lambda n: effective_priority(name_to_wad[n]),
                reverse=True,
            )

        # Detect circular dependencies
        if len(resolved) < len(discovered):
            unresolved = [w["name"] for w in discovered if w["name"] not in processed]
            raise OmegaError(
                f"Circular dependency detected among WADs: {unresolved}. "
                f"Load order resolution failed."
            )

        return resolved

    async def load_all_wads(self) -> Dict[str, bool]:
        """Discover and load WADs based on config/omega.yaml composition.

        Phase 4.1 Multi-PWAD Composition:
        - If ``omega.entity.active_pwads`` is configured, loads the IWAD
          (``omega.entity.active_iwad``) + each listed PWAD in order.
        - Otherwise falls back to auto-discovery of all WADs in the directory.

        Returns a map of stack_name -> success_status.
        """
        results: Dict[str, bool] = {}

        try:
            from omega.governance.config_resolver import get_active_iwad, get_active_pwads

            active_iwad = get_active_iwad()
            active_pwads = get_active_pwads()

            wads_to_load = []

            if active_pwads:
                wads_to_load.append((active_iwad, "iwad", 10))
                for pwad_name in active_pwads:
                    wads_to_load.append((pwad_name, "pwad", 100))
                logger.info(
                    f"Multi-PWAD composition: IWAD={active_iwad}, PWADs={active_pwads}"
                )
            else:
                discovered = await self._discover_wads()
                if not discovered:
                    logger.info("No WADs discovered in wads directory.")
                    return results
                ordered_wads = await self._resolve_load_order(discovered)
                for w in ordered_wads:
                    wads_to_load.append((w["name"], w["type"], None))

            for stack_name, wad_type, base_priority in wads_to_load:
                if base_priority is None:
                    try:
                        manifest_path = self.wads_dir / stack_name / "manifest.yaml"
                        if manifest_path.exists():
                            with open(manifest_path, encoding="utf-8") as f:
                                raw = yaml.safe_load(f) or {}
                            manifest = raw.get("wad", raw) if isinstance(raw, dict) else {}
                            wad_type = manifest.get("type", wad_type)
                            manifest_prio = manifest.get("priority", 0)
                            if not isinstance(manifest_prio, int) or isinstance(manifest_prio, bool):
                                manifest_prio = 0
                        else:
                            manifest_prio = 0
                    except (OSError, yaml.YAMLError):
                        manifest_prio = 0
                    bp = 10 if wad_type == "iwad" else 100
                    priority = bp + manifest_prio
                else:
                    try:
                        manifest_path = self.wads_dir / stack_name / "manifest.yaml"
                        if manifest_path.exists():
                            with open(manifest_path, encoding="utf-8") as f:
                                raw = yaml.safe_load(f) or {}
                            manifest = raw.get("wad", raw) if isinstance(raw, dict) else {}
                            manifest_prio = manifest.get("priority", 0)
                            if not isinstance(manifest_prio, int) or isinstance(manifest_prio, bool):
                                manifest_prio = 0
                        else:
                            manifest_prio = 0
                    except (OSError, yaml.YAMLError):
                        manifest_prio = 0
                    priority = base_priority + manifest_prio

                logger.info(f"Loading WAD: {stack_name} (type={wad_type}, priority={priority})")
                success, _ = await self.load_wad(stack_name, priority=priority)
                results[stack_name] = success

        except OmegaError as e:
            logger.error(f"WAD auto-loading failed: {e}")
            if "discovered" in locals():
                for wad_meta in discovered:
                    if wad_meta["name"] not in results:
                        results[wad_meta["name"]] = False

        return results


    async def load_single_wad(self, stack_name: str, priority: int = 10) -> bool:
        """Load only a single named WAD.

        Unlike load_all_wads(), this loads exactly one IWAD and skips the rest.
        The selected IWAD gets higher priority so its entities override entities.yaml.

        Args:
            stack_name: Name of the WAD directory to load
            priority: Override priority (default 10 — overrides entities.yaml baseline)
        """
        logger.info(f"Loading single WAD: {stack_name} (priority {priority})")
        success, _ = await self.load_wad(stack_name, priority=priority)
        return success

    def get_loaded_version(self, stack_name: str) -> Optional[str]:
        """Return the version of a currently loaded WAD, or None."""
        meta = self._loaded_wads.get(stack_name)
        if meta:
            return meta.get("version")
        return None

    def check_version_update(self, stack_name: str, new_version: str) -> dict:
        """Check if a new WAD version is an upgrade over the currently loaded one.

        Returns:
            dict with: is_update (bool), current (str), new (str), direction (str)
        """
        current = self.get_loaded_version(stack_name)
        if current is None:
            return {"is_update": False, "current": None, "new": new_version, "direction": "not_loaded"}
        try:
            cur_ver = WADVersion(current)
            new_ver = WADVersion(new_version)
        except (ValueError, AttributeError):
            return {"is_update": False, "current": current, "new": new_version, "direction": "unparseable"}
        if new_ver > cur_ver:
            return {"is_update": True, "current": current, "new": new_version, "direction": "upgrade"}
        elif new_ver < cur_ver:
            return {"is_update": False, "current": current, "new": new_version, "direction": "downgrade"}
        else:
            return {"is_update": False, "current": current, "new": new_version, "direction": "same"}

    async def wad_upgrade(self, stack_name: str, *, force: bool = False) -> dict:
        """Upgrade a WAD to a new version, preserving runtime state.

        Unloads the current WAD, loads the new one, and reports what changed.
        Runtime souls are preserved (not overwritten) during upgrade.

        Args:
            stack_name: WAD to upgrade.
            force: Force upgrade even if version is not newer.

        Returns:
            dict with: success, previous_version, new_version, direction, entities_loaded
        """
        previous_version = self.get_loaded_version(stack_name)

        # Read new manifest version
        manifest_path = self.wads_dir / stack_name / "manifest.yaml"
        if not manifest_path.exists():
            return {"success": False, "error": f"WAD '{stack_name}' not found"}

        try:
            with open(manifest_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            manifest = raw.get("wad", raw) if isinstance(raw, dict) else {}
            new_version = manifest.get("version", "unknown")
        except (OSError, yaml.YAMLError) as e:
            return {"success": False, "error": f"Invalid manifest: {e}"}

        check = self.check_version_update(stack_name, new_version)
        if not force and not check["is_update"] and check["direction"] not in ("not_loaded",):
            return {
                "success": False,
                "error": f"Not an upgrade: {check['direction']} ({check['current']} -> {check['new']})",
                "previous_version": previous_version,
                "new_version": new_version,
            }

        # Unload current (preserving runtime state)
        if stack_name in self._loaded_wads:
            await self.unload_wad(stack_name)

        # Load new version
        success, hierarchy_path = await self.load_wad(stack_name)

        return {
            "success": success,
            "previous_version": previous_version,
            "new_version": new_version,
            "direction": check["direction"],
            "entities_loaded": len(self.registry.list()) if success else 0,
            "hierarchy_path": str(hierarchy_path) if hierarchy_path else None,
        }

    async def unload_wad(self, stack_name: str) -> bool:
        """Unload a specific WAD and remove its entities from the registry.

        Removes all entities whose wad_source matches stack_name,
        resets hierarchy if it was from this WAD, and clears startup message.
        Returns True on success.
        """
        try:
            # Remove entities from this WAD
            to_remove = []
            for key, layers in self.registry._entities.items():
                active = [l for l in layers if getattr(l, "wad_source", None) == stack_name]
                if active:
                    to_remove.append(key)

            for key in to_remove:
                # Remove only layers from this WAD, keep others
                layers = self.registry._entities.get(key, [])
                remaining = [l for l in layers if getattr(l, "wad_source", None) != stack_name]
                if remaining:
                    self.registry._entities[key] = remaining
                    self.registry._entities[key].sort(key=lambda e: e.priority, reverse=True)
                else:
                    del self.registry._entities[key]
                    if key in self.registry._wad_sources:
                        self.registry._wad_sources[key] = [
                            w for w in self.registry._wad_sources[key] if w != stack_name
                        ]
                        if not self.registry._wad_sources[key]:
                            del self.registry._wad_sources[key]

            # Clear startup message
            if stack_name in self._startup_messages:
                del self._startup_messages[stack_name]

            # Reset hierarchy if it was from this WAD
            if self.active_hierarchy_path and stack_name in str(self.active_hierarchy_path):
                self.active_hierarchy_path = None

            self._loaded_wads.pop(stack_name, None)

            # Invalidate dispatch_registry cache so stale WAD dispatch is not served
            try:
                from omega.governance.dispatch_registry import invalidate_cache
                invalidate_cache()
            except ImportError:
                pass

            logger.info(f"Unloaded WAD: {stack_name} (removed {len(to_remove)} entity keys)")
            return True
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to unload WAD {stack_name}: {e}")
            return False

    async def wad_switch(
        self,
        stack_name: str,
        *,
        unload_existing_pwads: bool = True,
        unload_all_others: bool = False,
        priority: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Switch active WAD at runtime without restarting the engine (Phase 3.5).

        Validates the target WAD exists before unloading anything (fail-safe).
        - If target is a PWAD and ``unload_existing_pwads`` is True, unloads
          previously loaded PWADs while keeping the base IWAD intact.
        - If ``unload_all_others`` is True (or target is an IWAD), unloads
          conflicting WADs of the same/all types cleanly before loading target.
        """
        resolved_target = (self.wads_dir / stack_name).resolve()
        if not str(resolved_target).startswith(str(self.wads_dir.resolve())):
            return {
                "success": False,
                "switched_to": stack_name,
                "error": f"Path traversal attempt detected: {stack_name}",
                "unloaded": [],
                "loaded_wads": list(self._loaded_wads.keys()),
            }

        manifest_path = resolved_target / "manifest.yaml"
        if not await anyio.Path(manifest_path).exists():
            return {
                "success": False,
                "switched_to": stack_name,
                "error": f"WAD '{stack_name}' missing manifest.yaml at {manifest_path}",
                "unloaded": [],
                "loaded_wads": list(self._loaded_wads.keys()),
            }

        try:
            async with await anyio.open_file(str(manifest_path), "r") as f:
                raw_manifest = yaml.safe_load(await f.read()) or {}
            manifest = raw_manifest.get("wad", raw_manifest)
            if not isinstance(manifest, dict):
                raise ValueError("Manifest root must be a mapping")
        except (OSError, ValueError, yaml.YAMLError) as exc:
            return {
                "success": False,
                "switched_to": stack_name,
                "error": f"Invalid manifest for '{stack_name}': {exc}",
                "unloaded": [],
                "loaded_wads": list(self._loaded_wads.keys()),
            }

        wad_type = manifest.get("type", "pwad")
        manifest_prio = manifest.get("priority", 0)
        if not isinstance(manifest_prio, int) or isinstance(manifest_prio, bool):
            manifest_prio = 0
        effective_priority = (
            priority if priority is not None else ((10 if wad_type == "iwad" else 100) + manifest_prio)
        )

        # Determine which loaded WADs to unload
        to_unload: List[str] = []
        for loaded_name, meta in list(self._loaded_wads.items()):
            if loaded_name == stack_name:
                to_unload.append(loaded_name)
            elif unload_all_others:
                to_unload.append(loaded_name)
            elif wad_type == "pwad" and unload_existing_pwads and meta.get("type") == "pwad":
                to_unload.append(loaded_name)
            elif wad_type == "iwad" and meta.get("type") == "iwad":
                to_unload.append(loaded_name)

        unloaded: List[str] = []
        for name in to_unload:
            if await self.unload_wad(name):
                unloaded.append(name)

        try:
            from omega.governance.dispatch_registry import invalidate_cache
            invalidate_cache()
        except ImportError:
            pass

        success, hierarchy_path = await self.load_wad(stack_name, priority=effective_priority)
        return {
            "success": success,
            "switched_to": stack_name,
            "wad_type": wad_type,
            "priority": effective_priority,
            "unloaded": unloaded,
            "loaded_wads": list(self._loaded_wads.keys()),
            "entity_count": len(self.registry.list()),
            "startup_message": self.get_startup_message(stack_name),
            "hierarchy_path": str(hierarchy_path) if hierarchy_path else None,
        }

    def get_startup_message(self, stack_name: Optional[str] = None) -> Optional[str]:
        """Return the startup personality message for a given WAD stack.

        If no stack_name is specified, returns the message from the last-loaded WAD
        that defined one (useful for --iwad mode where a specific IWAD is active).
        """
        if stack_name:
            return self._startup_messages.get(stack_name)
        # Return most recently added startup message (active IWAD)
        if self._startup_messages:
            return list(self._startup_messages.values())[-1]
        return None

    async def load_wad(self, stack_name: str, priority: int = 0) -> Tuple[bool, Optional[Path]]:
        """Load a specific WAD stack.

        Returns:
            Tuple of (success_status, hierarchy_path)
        """
        # Path traversal guard
        resolved_wad_path = (self.wads_dir / stack_name).resolve()
        if not str(resolved_wad_path).startswith(str(self.wads_dir.resolve())):
            logger.warning(f"Path traversal attempt detected: {stack_name}")
            return False, None

        wad_path = resolved_wad_path
        manifest_path = wad_path / "manifest.yaml"

        if not await anyio.Path(manifest_path).exists():
            logger.warning(f"WAD {stack_name} missing manifest.yaml. Skipping.")
            return False, None

        # S1.5a: File size guard — reject manifests over 1 MB
        try:
            manifest_stat = await anyio.Path(manifest_path).stat()
            if manifest_stat.st_size > MAX_YAML_SIZE_BYTES:
                logger.error(
                    f"WAD {stack_name} manifest too large: {manifest_stat.st_size} bytes "
                    f"(max {MAX_YAML_SIZE_BYTES}). Possible DoS attempt."
                )
                return False, None
        except OSError:
            pass  # stat() failure is non-fatal; yaml.safe_load will catch truncation

        try:
            async with await anyio.open_file(str(manifest_path), "r") as f:
                manifest = yaml.safe_load(await f.read())

            if manifest is None:
                raise ValueError(f"WAD {stack_name} manifest is empty")

            # Support both flat (name/version/entities) and wad:-wrapped manifests
            if "wad" in manifest:
                manifest = manifest["wad"]

            # Validate required fields
            required_fields = ["name", "version", "entities"]
            missing = [f for f in required_fields if f not in manifest]
            if missing:
                raise ValueError(
                    f"WAD {stack_name} manifest missing required fields: {', '.join(missing)}"
                )

            # S1.5a: Validate field types (V1 core + V2 heritage optional)
            field_types = {**MANIFEST_FIELD_TYPES, **MANIFEST_V2_OPTIONAL_FIELD_TYPES}
            for field, expected_type in field_types.items():
                if field in manifest and not isinstance(manifest[field], expected_type):
                    raise TypeError(
                        f"WAD {stack_name} manifest field '{field}' has wrong type: "
                        f"expected {expected_type}, got {type(manifest[field]).__name__}"
                    )

            # extra="forbid" — reject unknown manifest fields (V1 core ∪ V2 heritage)
            # Do NOT loosen to extra=allow; only versioned explicit fields pass.
            known_manifest_fields = set(field_types.keys())
            unknown_manifest_fields = set(manifest.keys()) - known_manifest_fields
            if unknown_manifest_fields:
                raise ValueError(
                    f"WAD {stack_name} manifest has unknown fields: {sorted(unknown_manifest_fields)}. "
                    f"Known fields: {sorted(known_manifest_fields)}"
                )

            # S1.5a: Validate name and version are non-empty strings
            if not manifest.get("name", "").strip():
                raise ValueError(f"WAD {stack_name} manifest 'name' is empty")
            if not manifest.get("version", "").strip():
                raise ValueError(f"WAD {stack_name} manifest 'version' is empty")

            # §6.2 Engine-version enforcement — FAIL LOUD (M23, no soft-skip).
            # Raises ValueError with exact required vs running versions;
            # the outer except logs it and returns (False, None).
            enforce_engine_compatibility(stack_name, manifest.get("requires_engine"))

            # Capture startup personality if defined
            if manifest.get("startup") and manifest["startup"].get("message"):
                self._startup_messages[stack_name] = manifest["startup"]["message"]

            logger.info(
                f"Loading stack {stack_name} (version {manifest.get('version', 'unknown')})"
            )

            # 1. Load Entities
            entities_dir = wad_path / "entities"
            if await anyio.Path(entities_dir).exists():
                await self._load_entities(entities_dir, wad_source=stack_name, priority=priority)

            # 2. Load Voices (currently mapped to entities in this simple version)
            voices_dir = wad_path / "voices"
            if await anyio.Path(voices_dir).exists():
                await self._load_voices(voices_dir, wad_source=stack_name)

            # 3. Resolve Hierarchy Path (if specified in manifest or exists in WAD root)
            hierarchy_path = None
            if "hierarchy" in manifest:
                h_path = (wad_path / manifest["hierarchy"]).resolve()
                if not str(h_path).startswith(str(wad_path.resolve())):
                    raise ValueError(
                        f"WAD {stack_name} hierarchy path escapes WAD root: {manifest['hierarchy']}"
                    )
                if await anyio.Path(h_path).exists():
                    hierarchy_path = h_path
            else:
                default_h_path = wad_path / "hierarchy.yaml"
                if await anyio.Path(default_h_path).exists():
                    hierarchy_path = default_h_path

            if hierarchy_path:
                self.active_hierarchy_path = hierarchy_path

            # 4. Load World State (First Breath)
            world_dir = wad_path / "world"
            if await anyio.Path(world_dir).exists():
                await self._load_world_state(world_dir, wad_source=stack_name)

            # 5. Register Memory Adapter (if specified in manifest)
            if self._adapter_registry and "adapters" in manifest:
                await self._register_adapters(manifest["adapters"], stack_name)

            wad_ver = manifest.get("version", "unknown")
            self._loaded_wads[stack_name] = {
                "name": stack_name,
                "type": manifest.get("type", "pwad"),
                "version": wad_ver,
                "version_parsed": WADVersion(wad_ver) if wad_ver != "unknown" else None,
                "priority": priority,
                "hierarchy_path": str(hierarchy_path) if hierarchy_path else None,
            }

            return True, hierarchy_path

        except (OmegaError, RuntimeError, OSError, ValueError, TypeError, yaml.YAMLError) as e:
            logger.error(f"Failed to load WAD {stack_name}: {e}")
            return False, None

    async def _register_adapters(self, adapters_config: Dict[str, Any], stack_name: str) -> None:
        """Register memory adapters from WAD manifest.

        Supports:
          adapters:
            memory:
              module: "config.wads.arcana_novai.adapters.mnemosyne_adapter"
              class: "MnemosyneAdapter"

        Dynamically imports the module, instantiates the class, and
        registers the instance with the MemoryAdapterRegistry.
        All entities in this WAD are then mapped to this adapter.
        """
        memory_adapter_cfg = adapters_config.get("memory")
        if not memory_adapter_cfg:
            return

        module_path = memory_adapter_cfg.get("module")
        class_name = memory_adapter_cfg.get("class")
        if not module_path or not class_name:
            logger.warning(
                f"WAD {stack_name} has incomplete memory adapter config: {memory_adapter_cfg}"
            )
            return

        try:
            # S1.5a: Adapter module whitelist enforcement
            # [M2] Engine-Stack Firewall: WADs cannot import arbitrary engine internals.
            if module_path not in ADAPTER_MODULE_WHITELIST:
                logger.error(
                    f"WAD {stack_name} adapter module '{module_path}' not in whitelist. "
                    f"Allowed: {sorted(ADAPTER_MODULE_WHITELIST)}"
                )
                return

            # Dynamic import
            import importlib

            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)

            if self._adapter_registry is None:
                logger.warning(
                    f"Cannot register adapter for WAD {stack_name}: no adapter registry set"
                )
                return

            # Import IMemoryAdapter for type check
            from omega.memory.adapters import IMemoryAdapter

            instance = adapter_class()

            # P0: Must call initialize() after construction
            # Adapters load sphere/qliphoth data and create vault directories here
            await instance.initialize()

            if not isinstance(instance, IMemoryAdapter):
                logger.error(
                    f"WAD {stack_name} adapter class {class_name} does not implement IMemoryAdapter"
                )
                return

            self._adapter_registry.register(stack_name, instance)
            logger.info(f"Registered memory adapter {class_name} for WAD '{stack_name}'")

            # Map all entities loaded from this WAD to the adapter
            for entity_key, entity in self.registry.list().items():
                if hasattr(entity, "wad_source") and entity.wad_source == stack_name:
                    # S2: Conflict detection — warn if entity already mapped to different WAD
                    existing_wad = self._adapter_registry._entity_to_adapter.get(entity.name)
                    if existing_wad and existing_wad != stack_name:
                        logger.warning(
                            f"Entity '{entity.name}' already mapped to WAD '{existing_wad}', "
                            f"overwriting with WAD '{stack_name}'"
                        )
                    self._adapter_registry.register_entity_to_wad(entity.name, stack_name)

        except ImportError as e:
            logger.error(
                f"Failed to import adapter module '{module_path}' for WAD {stack_name}: {e}"
            )
        except AttributeError as e:
            logger.error(
                f"Adapter class '{class_name}' not found in '{module_path}' for WAD {stack_name}: {e}"
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to register adapter for WAD {stack_name}: {e}", exc_info=True)

    async def _load_entities(
        self, entities_dir: Path, wad_source: str = "", priority: int = 0
    ) -> None:
        """Load all .yaml files from the entities directory.

        Uses batch_add() for efficiency (single disk write per WAD).

        Args:
            entities_dir: Path to the entities directory
            wad_source: WAD name to tag entities with (for IWAD tracking)
            priority: Override priority — higher priority can replace lower priority
        """
        collected: list = []
        async for path in anyio.Path(entities_dir).glob("**/*.yaml"):
            # Accept any .yaml file. Extract name from parent dir (if soul.yaml) or filename stem.
            if path.name == "soul.yaml":
                entity_name = path.parent.name
            elif path.suffix == ".yaml":
                entity_name = path.stem  # e.g., "maat.yaml" → "maat"
            else:
                continue

            if not entity_name:
                continue

            # Collision detection with priority resolution
            existing = self.registry.get(entity_name)
            if existing:
                existing_priority = getattr(existing, "priority", 0)
                if existing.wad_source and existing.wad_source == wad_source:
                    logger.warning(
                        f"Entity {entity_name} already registered from WAD {wad_source}. Skipping duplicate."
                    )
                    continue
                if priority <= existing_priority:
                    logger.info(
                        f"Entity {entity_name} already registered (priority {existing_priority} >= {priority}). Skipping from WAD {wad_source}."
                    )
                    continue
                logger.info(
                    f"Entity {entity_name} already registered (priority {existing_priority} < {priority}). Overriding from WAD {wad_source}."
                )

            try:
                # S1.5a: File size guard for entity files
                try:
                    file_stat = await anyio.Path(path).stat()
                    if file_stat.st_size > MAX_YAML_SIZE_BYTES:
                        logger.warning(
                            f"Entity file {path.name} too large: {file_stat.st_size} bytes. Skipping."
                        )
                        continue
                except OSError:
                    pass  # Non-fatal; yaml.safe_load will handle truncation

                async with await anyio.open_file(str(path), "r") as f:
                    data = yaml.safe_load(await f.read())

                    if data is None:
                        logger.warning(f"Entity file {path.name} is empty. Skipping.")
                        continue

                    # Create Entity object via unified WADEntitySchema (2.7)
                    ent_data = data.get("entity", {})

                    if not ent_data:
                        logger.warning(f"Entity file {path.name} missing 'entity' key. Skipping.")
                        continue

                    try:
                        validated, wad_metadata = validate_wad_entity(
                            ent_data, default_name=entity_name
                        )
                    except ValueError as val_err:
                        logger.warning(
                            f"Entity {entity_name} failed schema validation: {val_err}. Skipping."
                        )
                        continue

                    if wad_metadata:
                        logger.debug(
                            f"Entity {entity_name} has WAD-specific fields: {sorted(wad_metadata.keys())} (captured as metadata)"
                        )

                    entity = Entity(
                        name=validated.name or entity_name,
                        domains=validated.domains,
                        model=validated.model,
                        personality=validated.personality,
                        temperature=validated.temperature,
                        context_window=validated.context_window,
                        slots=validated.slots,
                        metadata=wad_metadata,
                        role=validated.role,
                        container=validated.container,
                        port=validated.port,
                        wad_source=wad_source,
                        priority=priority,
                    )
                    # WAD-to-runtime soul seeding: copy WAD soul.yaml to runtime if not exists
                    # or if WAD version is newer (upgrade path). Never overwrite
                    # operator-modified runtime souls with older WAD content.
                    wad_soul = Path(path).parent / "soul.yaml"
                    if wad_soul.exists():
                        import shutil as _shutil
                        from omega.oracle.entity_workspace import _get_entities_data_dir
                        runtime_dir = _get_entities_data_dir() / entity.name.lower().replace(" ", "_").replace("'", "")
                        runtime_soul = runtime_dir / "soul.yaml"
                        should_seed = False
                        if not runtime_soul.exists():
                            should_seed = True
                        else:
                            # Check if WAD soul is newer (compare file mtimes as proxy)
                            try:
                                wad_mtime = wad_soul.stat().st_mtime
                                runtime_mtime = runtime_soul.stat().st_mtime
                                if wad_mtime > runtime_mtime:
                                    # WAD is newer — but preserve approved_lessons.yaml
                                    should_seed = True
                                    logger.info(
                                        f"WAD soul newer than runtime for {entity.name} — upgrading (preserving approved_lessons)"
                                    )
                            except OSError:
                                pass
                        if should_seed:
                            runtime_dir.mkdir(parents=True, exist_ok=True)
                            # Preserve approved_lessons.yaml before overwriting
                            approved_backup = None
                            approved_path = runtime_dir / "memory" / "approved_lessons.yaml"
                            if approved_path.exists():
                                approved_backup = approved_path.read_text(encoding="utf-8")
                            _shutil.copy2(wad_soul, runtime_soul)
                            # Restore approved_lessons.yaml if it was overwritten
                            if approved_backup is not None and not approved_path.exists():
                                approved_path.parent.mkdir(parents=True, exist_ok=True)
                                approved_path.write_text(approved_backup, encoding="utf-8")
                            logger.info(f"Seeded/upgraded soul.yaml from WAD for {entity.name}")

                    collected.append(entity)
                    logger.info(f"Collected entity {entity.name} from WAD {wad_source}")
            except (OmegaError, RuntimeError, OSError, yaml.YAMLError) as e:
                logger.warning(f"Failed to load entity from {path}: {e}")

        # Batch add all collected entities (single disk write)
        if collected:
            await self.registry.batch_add(collected)
            logger.info(f"Batch-registered {len(collected)} entities from WAD {wad_source}")

    async def _load_voices(self, voices_dir: Path, wad_source: str = "") -> None:
        """Load voice configurations from the voices directory."""
        # In the current architecture, voices are essentially entities with
        # specific activation phrases and roles.
        async for path in anyio.Path(voices_dir).glob("*.yaml"):
            try:
                async with await anyio.open_file(str(path), "r") as f:
                    data = yaml.safe_load(await f.read())

                voice_name = path.stem
                existing = self.registry.get(voice_name)
                if existing:
                    existing_priority = 0
                    if existing.wad_source and existing.wad_source == wad_source:
                        logger.warning(
                            f"Voice {voice_name} already registered from WAD {wad_source}. Skipping."
                        )
                        continue
                    if wad_source and existing.wad_source != wad_source:
                        logger.info(
                            f"Voice {voice_name} already registered from WAD {existing.wad_source}. Skipping voice from WAD {wad_source}."
                        )
                        continue

                # Create a voice entity
                entity = Entity(
                    name=voice_name,
                    domains=data.get("domains", []),
                    model=data.get("model", "opencode/big-pickle"),
                    personality=data.get("personality", ""),
                    role=data.get("role", "Voice Interface"),
                    container=True,
                    port=data.get("port", 8080),
                    wad_source=wad_source,
                )
                await self.registry.add(entity)
                logger.info(f"Registered voice {voice_name} from WAD")
            except (OmegaError, RuntimeError, OSError, yaml.YAMLError) as e:
                logger.warning(f"Failed to load voice from {path}: {e}")

    async def _load_world_state(self, world_dir: Path, wad_source: str = "") -> None:
        """Load world-lumps for VR Omegaverse. [id-soft: doom-1993]

        Structure: world/<sector_id>/<lump_id>.yaml
        """
        async for sector_path in anyio.Path(world_dir).iterdir():
            if await sector_path.is_dir():
                sector_id = sector_path.name
                async for lump_path in anyio.Path(sector_path).glob("*.yaml"):
                    try:
                        async with await anyio.open_file(str(lump_path), "r") as f:
                            data = yaml.safe_load(await f.read())

                        lump_id = lump_path.stem
                        lump = WorldLump(
                            lump_id=lump_id,
                            data=data.get("world_data", {}),
                            metadata={"wad_source": wad_source, "path": str(lump_path)},
                        )
                        await world_state.load_lump(sector_id, lump)
                        logger.info(
                            f"World State: Loaded lump {lump_id} in sector {sector_id} from {wad_source}"
                        )
                    except (OmegaError, RuntimeError, OSError) as e:
                        logger.warning(f"Failed to load world lump {lump_path}: {e}")
