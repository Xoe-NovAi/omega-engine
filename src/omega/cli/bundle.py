# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Sovereign Export Bundle — `.omega` Entity Portability
# AP: AP-BUNDLE-v1.0.0
#
# Creates portable .omega ZIP bundles that fully capture an entity's state:
# soul.yaml, sessions, knowledge base, proposed lessons, and integrity checksums.
#
# [heritage: zip-json 2026] ZIP+JSON bundle format per Soul Protocol v0.4.0
#   Jem S1 validation: Parquet is for ML weights, not entity state.
#   The .omega bundle is the universal sovereign portability baseline.

import hashlib
import json
import logging
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import anyio
import typer
import yaml
from rich.console import Console
from rich.table import Table

from omega.oracle.entity_registry import EntityRegistry
from omega.errors import OmegaError

logger = logging.getLogger(__name__)
console = Console()

# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

BUNDLE_SCHEMA_VERSION = "1.0.0"
BUNDLE_VERSION = "1.0.0"
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def _get_data_dir() -> Path:
    """Resolve data directory at call time, respecting OMEGA_DATA_DIR env var.

    This allows tests using monkeypatch.setenv("OMEGA_DATA_DIR", tmp_path)
    to properly isolate without leaking into production.
    """
    return BASE_DIR / os.getenv("OMEGA_DATA_DIR", "data")


def _get_entities_dir() -> Path:
    """Resolve entities data directory at call time (env-aware)."""
    return _get_data_dir() / "entities"


def _get_bundles_dir() -> Path:
    """Resolve bundles directory at call time (env-aware)."""
    return _get_data_dir() / "bundles"


app = typer.Typer(
    help="🔱 Sovereign Bundle — export/import entity state as portable .omega bundles"
)


# ═══════════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════════


@app.command()
def export(
    entity_name: str = typer.Argument(..., help="Entity name to export"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output path for the .omega.zip bundle"
    ),
):
    """Export an entity's state to a portable .omega ZIP bundle.

    Packages soul.yaml, sessions, knowledge base, proposed lessons,
    and integrity checksums into a single ZIP file.
    """

    async def _run():
        try:
            result = await _export_entity(entity_name, output)
            console.print(f"[green]✅ Exported {entity_name} → {result}[/green]")

            # Show bundle contents
            _display_bundle_contents(result)
        except (ValueError, FileNotFoundError, RuntimeError) as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    anyio.run(_run)


async def _export_entity(entity_name: str, output_path: Optional[str] = None) -> str:
    """Core export logic. Returns the path to the created .omega.zip bundle."""
    safe_name = entity_name.lower().strip()
    entity_dir = _get_entities_dir() / safe_name

    if not entity_dir.exists():
        raise FileNotFoundError(f"Entity directory not found: {entity_dir}")

    # Verify entity exists in registry (soft warning — entity directory takes precedence)
    try:
        registry = EntityRegistry()
        entity_obj = registry.get(safe_name)
        if not entity_obj:
            logger.warning(
                f"Entity '{entity_name}' not found in entity registry — exporting from directory only"
            )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.warning(f"Entity registry unavailable ({e}) — exporting from directory only")

    # Determine output path
    if output_path:
        bundle_path = Path(output_path)
        if bundle_path.is_dir():
            bundle_path = bundle_path / f"{safe_name}.omega.zip"
    else:
        bundle_path = _get_bundles_dir() / f"{safe_name}.omega.zip"
        bundle_path.parent.mkdir(parents=True, exist_ok=True)

    # Collect all files to bundle
    files_to_bundle: Dict[str, bytes] = {}

    # 1. soul.yaml
    soul_file = entity_dir / "soul.yaml"
    if soul_file.exists():
        files_to_bundle["soul.yaml"] = await anyio.to_thread.run_sync(
            lambda: soul_file.read_bytes()
        )
    else:
        logger.warning(f"No soul.yaml found for {entity_name} — creating minimal placeholder")
        minimal_soul = {"entity": {"name": entity_name, "sovereignty_level": 1}}
        files_to_bundle["soul.yaml"] = yaml.dump(
            minimal_soul, default_flow_style=False, sort_keys=False
        ).encode("utf-8")

    # 2. Sessions
    memory_dir = entity_dir / "memory"
    session_files = {}
    if memory_dir.exists():
        for fname in ["sessions.yaml"]:
            fpath = memory_dir / fname
            if fpath.exists():
                session_files[fname] = await anyio.to_thread.run_sync(
                    lambda p=fpath: p.read_bytes()
                )

    if session_files:
        # Parse session metadata
        session_meta = _extract_session_metadata(session_files)
        files_to_bundle["sessions/session_metadata.json"] = json.dumps(
            session_meta, indent=2, default=str
        ).encode("utf-8")

        # Extract recent exchanges
        exchanges = _extract_recent_exchanges(session_files)
        if exchanges:
            files_to_bundle["sessions/recent_exchanges.jsonl"] = (
                "\n".join(json.dumps(e, default=str) for e in exchanges)
            ).encode("utf-8")
    else:
        # Empty but properly structured
        files_to_bundle["sessions/session_metadata.json"] = json.dumps(
            {"entity": entity_name, "total_sessions": 0, "sessions": []},
            indent=2,
        ).encode("utf-8")

    # 3. Knowledge base
    knowledge_dir = entity_dir / "knowledge"
    if knowledge_dir.exists():
        # Build knowledge index
        knowledge_files_list = sorted(knowledge_dir.iterdir())
        knowledge_index = []
        for kf in knowledge_files_list:
            if kf.is_file() and not kf.name.startswith("."):
                rel_name = kf.name
                kf_data = await anyio.to_thread.run_sync(lambda p=kf: p.read_bytes())
                files_to_bundle[f"knowledge/{rel_name}"] = kf_data
                knowledge_index.append(
                    {
                        "filename": rel_name,
                        "size_bytes": len(kf_data),
                        "extension": kf.suffix,
                    }
                )

        files_to_bundle["knowledge/index.json"] = json.dumps(
            knowledge_index, indent=2, default=str
        ).encode("utf-8")
    else:
        files_to_bundle["knowledge/index.json"] = json.dumps([], indent=2).encode("utf-8")

    # 4. Proposed lessons (check memory/ first, then entity root, then root level)
    proposed_found = None
    if memory_dir.exists():
        p = memory_dir / "proposed_lessons.yaml"
        if p.exists():
            proposed_found = p
    if not proposed_found:
        p = entity_dir / "proposed_lessons.yaml"
        if p.exists():
            proposed_found = p
    if proposed_found:
        files_to_bundle["proposed_lessons.yaml"] = await anyio.to_thread.run_sync(
            lambda: proposed_found.read_bytes()
        )

    # 5. Workspace files (optional — include non-temp files)
    workspace_dir = entity_dir / "workspace"
    workspace_files = []
    if workspace_dir.exists():
        for wf in sorted(workspace_dir.iterdir()):
            if wf.is_file() and not wf.name.startswith(".") and wf.suffix == ".md":
                rel_path = f"workspace/{wf.name}"
                data = await anyio.to_thread.run_sync(lambda p=wf: p.read_bytes())
                files_to_bundle[rel_path] = data
                workspace_files.append(wf.name)

    # 6. Compute manifest
    file_count = len(files_to_bundle)
    total_size = sum(len(v) for v in files_to_bundle.values())
    created_at = datetime.now(timezone.utc).isoformat()

    manifest = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_version": BUNDLE_VERSION,
        "created_at": created_at,
        "entity_name": entity_name,
        "file_count": file_count,
        "total_size_bytes": total_size,
    }
    files_to_bundle["manifest.json"] = json.dumps(manifest, indent=2).encode("utf-8")

    # 7. Compute checksums (excluding checksums.sha256 itself)
    checksums: List[str] = []
    for fname in sorted(files_to_bundle.keys()):
        if fname == "checksums.sha256":
            continue
        sha256 = hashlib.sha256(files_to_bundle[fname]).hexdigest()
        checksums.append(f"{sha256}  {fname}")

    files_to_bundle["checksums.sha256"] = "\n".join(checksums).encode("utf-8")

    # Build the ZIP
    def _build_zip():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".omega.zip") as tmp:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, data in sorted(files_to_bundle.items()):
                    zf.writestr(fname, data)
            tmp_path = tmp.name

        # Atomic rename to target
        os.makedirs(bundle_path.parent, exist_ok=True)
        os.replace(tmp_path, str(bundle_path))
        return str(bundle_path)

    return await anyio.to_thread.run_sync(_build_zip)


def _extract_session_metadata(session_files: Dict[str, bytes]) -> dict:
    """Extract session count, timestamps, and IDs from session YAML data."""
    sessions_data = session_files.get("sessions.yaml", b"")
    if not sessions_data:
        return {"total_sessions": 0, "sessions": []}

    try:
        parsed = yaml.safe_load(sessions_data)
    except yaml.YAMLError:
        return {"total_sessions": 0, "sessions": []}

    if not isinstance(parsed, list):
        return {"total_sessions": 0, "sessions": []}

    sessions = []
    for s in parsed:
        if isinstance(s, dict):
            sessions.append(
                {
                    "session_id": s.get("session_id", s.get("id", "unknown")),
                    "created_at": str(s.get("created_at", s.get("timestamp", "unknown"))),
                    "summary": str(s.get("summary", s.get("continuation", "")))[:200],
                }
            )
        elif isinstance(s, str):
            sessions.append({"session_id": s})

    return {
        "total_sessions": len(sessions),
        "sessions": sessions,
    }


def _extract_recent_exchanges(session_files: Dict[str, bytes]) -> List[dict]:
    """Extract recent exchanges from session data."""
    # sessions.yaml may contain session summaries — extract what we can
    sessions_data = session_files.get("sessions.yaml", b"")
    if not sessions_data:
        return []

    try:
        parsed = yaml.safe_load(sessions_data)
    except yaml.YAMLError:
        return []

    if not isinstance(parsed, list):
        return []

    exchanges = []
    for s in parsed:
        if isinstance(s, dict):
            summary = s.get("summary", s.get("continuation", ""))
            if summary:
                exchanges.append(
                    {
                        "session_id": s.get("session_id", s.get("id", "unknown")),
                        "summary": str(summary)[:500],
                        "timestamp": str(s.get("created_at", s.get("timestamp", ""))),
                    }
                )

    return exchanges[-20:]  # Last 20 only


def _display_bundle_contents(bundle_path: str):
    """Display the contents of a .omega bundle in a table."""

    def _read_manifest():
        with zipfile.ZipFile(bundle_path, "r") as zf:
            if "manifest.json" in zf.namelist():
                return json.loads(zf.read("manifest.json"))
        return {}

    manifest = _read_manifest()

    table = Table(title=f"📦 Bundle: {manifest.get('entity_name', '?')}", border_style="cyan")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Path", bundle_path)
    table.add_row("Schema Version", manifest.get("schema_version", "?"))
    table.add_row("Created At", manifest.get("created_at", "?"))
    table.add_row("File Count", str(manifest.get("file_count", 0)))
    table.add_row("Total Size", f"{manifest.get('total_size_bytes', 0):,} bytes")

    console.print(table)

    # Show file listing
    file_table = Table(title="Bundle Contents", border_style="dim")
    file_table.add_column("File", style="cyan")
    file_table.add_column("Size", style="yellow")

    with zipfile.ZipFile(bundle_path, "r") as zf:
        for info in sorted(zf.infolist(), key=lambda x: x.filename):
            if not info.filename.endswith("/"):
                file_table.add_row(
                    info.filename,
                    f"{info.file_size:,} bytes",
                )

    console.print(file_table)


# ═══════════════════════════════════════════════════════════════════
# Import
# ═══════════════════════════════════════════════════════════════════


@app.command()
def import_bundle(
    bundle_path: str = typer.Argument(..., help="Path to the .omega.zip bundle to import"),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-f", help="Overwrite existing entity data"
    ),
):
    """Import an entity from a .omega ZIP bundle.

    Extracts soul.yaml, knowledge base, and proposed lessons into the
    entity's workspace. Validates checksums for integrity.
    """

    async def _run():
        try:
            entity_name = await _import_entity(bundle_path, overwrite)
            console.print(f"[green]✅ Successfully imported entity: {entity_name}[/green]")

            # Show imported entity info
            registry = EntityRegistry()
            entity_obj = registry.get(entity_name)
            if entity_obj:
                table = Table(title=f"🔱 Imported Entity: {entity_name}", border_style="green")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="white")
                table.add_row("Name", entity_obj.name)
                table.add_row("Model", entity_obj.model or "—")
                table.add_row(
                    "Domains", ", ".join(entity_obj.domains) if entity_obj.domains else "—"
                )
                if entity_obj.slots:
                    table.add_row("Slots", ", ".join(entity_obj.slots))
                console.print(table)
        except (ValueError, FileNotFoundError, RuntimeError, zipfile.BadZipFile) as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    anyio.run(_run)


async def _import_entity(bundle_path: str, overwrite: bool = False) -> str:
    """Core import logic. Returns the entity name."""
    bundle = Path(bundle_path)

    if not bundle.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle}")
    if bundle.suffix not in (".zip",):
        # Also accept .omega.zip
        if not bundle.name.endswith(".omega.zip"):
            raise ValueError(f"Not a valid .omega bundle (expected .zip or .omega.zip): {bundle}")

    # Read ZIP into memory for validation
    def _read_zip():
        with zipfile.ZipFile(str(bundle), "r") as zf:
            contents = {}
            for name in zf.namelist():
                contents[name] = zf.read(name)
        return contents

    contents = await anyio.to_thread.run_sync(_read_zip)

    # Validate manifest
    if "manifest.json" not in contents:
        raise ValueError("Bundle missing manifest.json — invalid .omega bundle")

    manifest = json.loads(contents["manifest.json"])
    entity_name = manifest.get("entity_name", "")
    if not entity_name:
        raise ValueError("manifest.json missing entity_name")

    safe_name = entity_name.lower().strip()

    # Validate checksums
    if "checksums.sha256" in contents:
        checksum_errors = _validate_checksums(contents)
        if checksum_errors:
            error_msg = "\n".join(checksum_errors)
            console.print(
                f"[yellow]⚠ Checksum validation had {len(checksum_errors)} issue(s):[/yellow]"
            )
            for err in checksum_errors:
                console.print(f"  [red]{err}[/red]")
            if not overwrite:
                console.print(
                    "[yellow]Use --overwrite/-f to import despite checksum issues[/yellow]"
                )
                raise ValueError(f"Checksum validation failed ({len(checksum_errors)} errors)")
    else:
        console.print(
            "[yellow]⚠ Bundle missing checksums.sha256 — integrity not verifiable[/yellow]"
        )

    # Check for existing entity
    entity_dir = _get_entities_dir() / safe_name
    if entity_dir.exists() and not overwrite:
        raise ValueError(
            f"Entity '{entity_name}' already exists at {entity_dir}. "
            f"Use --overwrite/-f to replace existing data."
        )

    # Extract files
    def _extract():
        if entity_dir.exists():
            shutil.rmtree(str(entity_dir))
        entity_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        sessions_dir = entity_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)

        knowledge_dir = entity_dir / "knowledge"
        knowledge_dir.mkdir(exist_ok=True)

        memory_dir = entity_dir / "memory"
        memory_dir.mkdir(exist_ok=True)

        for fname, data in contents.items():
            if fname in ("manifest.json", "checksums.sha256"):
                continue  # Metadata files — not extracted to entity dir

            # Map bundle paths to entity directory paths
            if fname.startswith("sessions/"):
                target = sessions_dir / Path(fname).name
            elif fname.startswith("knowledge/"):
                target = knowledge_dir / Path(fname).name
            elif fname.startswith("workspace/"):
                target = entity_dir / "workspace" / Path(fname).name
                target.parent.mkdir(exist_ok=True)
            elif fname == "proposed_lessons.yaml":
                target = memory_dir / fname
            elif fname == "soul.yaml":
                target = entity_dir / fname
            else:
                target = entity_dir / fname

            target.write_bytes(data)

        # Reconstruct sessions.yaml from metadata if needed
        sessions_meta_file = sessions_dir / "session_metadata.json"
        if sessions_meta_file.exists() and not (memory_dir / "sessions.yaml").exists():
            try:
                sessions_meta = json.loads(sessions_meta_file.read_text())
                if sessions_meta.get("sessions"):
                    sessions_yaml_path = memory_dir / "sessions.yaml"
                    with open(sessions_yaml_path, "w") as f:
                        yaml.dump(
                            sessions_meta["sessions"], f, default_flow_style=False, sort_keys=False
                        )
            except (json.JSONDecodeError, OSError):
                pass

        # Clean up sessions dir (metadata already extracted)
        shutil.rmtree(str(sessions_dir))

        return entity_name

    return await anyio.to_thread.run_sync(_extract)


def _validate_checksums(contents: Dict[str, bytes]) -> List[str]:
    """Validate checksums.sha256 against file contents.

    Returns a list of error messages (empty = all valid).
    """
    if "checksums.sha256" not in contents:
        return ["Missing checksums.sha256"]

    checksum_content = contents["checksums.sha256"].decode("utf-8")
    errors = []

    for line in checksum_content.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            errors.append(f"Malformed checksum line: {line}")
            continue

        expected_hash, fname = parts
        actual_data = contents.get(fname)

        if actual_data is None:
            errors.append(f"Missing file for checksum: {fname}")
            continue

        actual_hash = hashlib.sha256(actual_data).hexdigest()
        if actual_hash != expected_hash:
            errors.append(
                f"Checksum mismatch for {fname}: expected {expected_hash}, got {actual_hash}"
            )

    return errors


# ═══════════════════════════════════════════════════════════════════
# List / Info commands
# ═══════════════════════════════════════════════════════════════════


@app.command()
def list_bundles():
    """List all .omega bundles in the data/bundles directory."""
    bundles_dir = _get_bundles_dir()
    if not bundles_dir.exists():
        console.print("[dim]No bundles directory found at data/bundles/[/dim]")
        return

    bundle_files = sorted(bundles_dir.glob("*.omega.zip"))
    if not bundle_files:
        console.print("[dim]No .omega bundles found in data/bundles/[/dim]")
        return

    table = Table(title="📦 Available Bundles", border_style="cyan")
    table.add_column("Bundle", style="cyan")
    table.add_column("Size", style="yellow")
    table.add_column("Modified", style="green")

    for bf in bundle_files:
        stat = bf.stat()
        table.add_row(
            bf.name,
            f"{stat.st_size:,} bytes",
            datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


@app.command()
def info(
    bundle_path: str = typer.Argument(..., help="Path to the .omega.zip bundle to inspect"),
):
    """Show detailed information about a .omega bundle without importing it."""

    async def _run():
        try:
            _display_bundle_contents(bundle_path)
        except (FileNotFoundError, zipfile.BadZipFile, RuntimeError) as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    anyio.run(_run)


# ═══════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app()
