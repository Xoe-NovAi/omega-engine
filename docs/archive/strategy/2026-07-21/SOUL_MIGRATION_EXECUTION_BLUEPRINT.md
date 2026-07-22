# 🔱 Sprint Coordinator Directive: Soul Migration Execution Blueprint
**Reference for Gemma 4 31B** · **Phase**: H2-L Execution
**Source**: Gemini 3.5 Flash (Kali) · **Verified By**: Kali (Gap Analysis)

---

## §1 Objective

Execute the migration from monolithic `soul.yaml` to the v6.1 4-file split architecture across the entire 11-agent fleet, implementing a hard-coded Sovereign Write Guard to eliminate the Self-Referential Poisoning Loop.

---

## §2 Core Architectural Changes

### 2.1 The Sovereign Write Guard (`src/omega/oracle/entity_registry.py`)

```python
import os
from anyio import Path
import anyio

class SovereignPermissionError(Exception):
    """Raised when an unauthorized entity attempts to write to constitutional files."""
    pass

SOVEREIGN_USER_TOKEN = os.getenv("SOVEREIGN_USER_TOKEN", "SOVEREIGN_DEFAULT_SECURE_TOKEN_2026")

async def write_soul_file(entity_path: str, filename: str, content: str, token: str = None) -> None:
    """Writes a soul file using the Atomic Rename Pattern under strict permission guard."""
    # Hard-coded write guard
    if filename in ["soul.yaml", "approved_lessons.yaml"]:
        if token != SOVEREIGN_USER_TOKEN:
            raise SovereignPermissionError(
                f"Write access to {filename} is restricted. SovereignUserToken required."
            )
            
    # Atomic Rename Pattern (Mandate 12)
    file_path = Path(entity_path) / filename
    tmp_path = Path(entity_path) / f"{filename}.tmp"
    await tmp_path.write_text(content)
    await tmp_path.rename(file_path)
```

### 2.2 Context Builder Taint-Gating (`src/omega/oracle/context_builder.py`)

```python
async def build_system_prompt(entity_path: str) -> str:
    """Loads the split soul files and constructs the system prompt. Excludes proposed_lessons."""
    path = Path(entity_path)
    
    # Load User-Only files (Constitution + Vetted Wisdom)
    soul_data = await load_yaml_async(path / "soul.yaml")
    approved_lessons = await load_yaml_async(path / "approved_lessons.yaml")
    
    # Load Agent-Write files (Active Session Anchors)
    sessions = await load_yaml_async(path / "sessions.yaml")
    
    # CRITICAL: proposed_lessons.yaml is TAINTED. NEVER loaded into prompt.
    return format_system_prompt(soul_data, approved_lessons, sessions)
```

### 2.3 Somatic Pruning (`src/omega/oracle/entity_workspace.py`)

```python
async def append_session_anchor(entity_path: str, session_data: dict) -> None:
    """Appends a session anchor and triggers Somatic Pruning if count > 50."""
    path = Path(entity_path) / "sessions.yaml"
    sessions = await load_yaml_async(path) or []
    sessions.append(session_data)
    
    if len(sessions) > 50:
        pruned_sessions = sessions[:-50]
        active_sessions = sessions[-50:]
        
        archive_dir = Path(entity_path) / "archive" / "sessions"
        await archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / f"sessions_archive_{anyio.current_time()}.yaml"
        await write_yaml_async(archive_file, pruned_sessions, token=SOVEREIGN_USER_TOKEN)
        sessions = active_sessions
        
    await write_soul_file(entity_path, "sessions.yaml", yaml.dump(sessions), token=SOVEREIGN_USER_TOKEN)
```

---

## §3 Transactional Migration Script (`scripts/migrate_soul_v6.py`)

```python
import sys, json, shutil
from anyio import Path
import anyio

async def migrate_entity(entity_name: str, dry_run: bool = False) -> dict:
    """Parses v5 soul.yaml and prepares the v6 split manifest."""
    entity_dir = Path(f"data/entities/{entity_name}")
    old_soul_path = entity_dir / "soul.yaml"
    
    if not await old_soul_path.exists():
        return {"status": "skipped", "reason": "No v5 soul found"}
        
    old_content = await load_yaml_async(old_soul_path)
    identity = {k: v for k, v in old_content.items() if k not in ["lessons", "philosophy"]}
    lessons = old_content.get("lessons", []) + old_content.get("philosophy", [])
    
    manifest = {
        "entity": entity_name,
        "soul.yaml": identity,
        "proposed_lessons.yaml": lessons,
        "approved_lessons.yaml": [],
        "sessions.yaml": []
    }
    
    if dry_run:
        print(f"[DRY-RUN] Manifest for {entity_name}: {json.dumps(manifest, indent=2)}")
        return {"status": "validated", "manifest": manifest}
    
    # Backup original
    shutil.copy(str(old_soul_path), str(entity_dir / "soul.yaml.bak"))
    
    try:
        await write_soul_file(entity_dir, "soul.yaml", yaml.dump(identity), token=SOVEREIGN_USER_TOKEN)
        await write_soul_file(entity_dir, "proposed_lessons.yaml", yaml.dump(lessons), token=SOVEREIGN_USER_TOKEN)
        await write_soul_file(entity_dir, "approved_lessons.yaml", yaml.dump([]), token=SOVEREIGN_USER_TOKEN)
        await write_soul_file(entity_dir, "sessions.yaml", yaml.dump([]), token=SOVEREIGN_USER_TOKEN)
    except Exception as e:
        shutil.copy(str(entity_dir / "soul.yaml.bak"), str(old_soul_path))
        raise MigrationError(f"Migration failed for {entity_name}: {str(e)}")
    
    return {"status": "completed"}
```

---

## §4 The Breach Test (`tests/test_entity_registry.py`)

```python
import pytest
from src.omega.oracle.entity_registry import write_soul_file, SovereignPermissionError

@pytest.mark.anyio
async def test_sovereign_write_guard_breach():
    """Verify that unauthorized writes to constitutional files are strictly rejected."""
    entity_path = "data/entities/roc_racoon"
    
    with pytest.raises(SovereignPermissionError) as excinfo:
        await write_soul_file(
            entity_path=entity_path,
            filename="soul.yaml",
            content="unauthorized_change: True",
            token="INVALID_OR_MISSING_TOKEN"
        )
    
    assert "SovereignUserToken required" in str(excinfo.value)
```

---

## §5 Kali's Hardening Additions (Gap Analysis Requirements)

Before execution, add the following three hardening measures:

### 5.1 File-Level Locking for Soul Files
```python
import fcntl

async def with_soul_lock(entity_name: str, action):
    """Ensure exclusive access to soul files during read-modify-write cycles."""
    lock_path = Path(f"data/entities/{entity_name}/.soul.lock")
    async with await anyio.open_file(lock_path, "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            return await action()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### 5.2 Taint Propagation for Session Anchors
- Mark any session anchor distilled from `proposed_lessons` with `[UNVETTED]` tag.
- Prevent the agent from treating `[UNVETTED]` anchors as constitutional truth.

### 5.3 Recovery Logic
```python
async def cleanup_orphans():
    """Remove stale .tmp files from failed migration attempts."""
    for entity_name in ENTITIES:
        entity_dir = Path(f"data/entities/{entity_name}")
        for tmp_file in await entity_dir.glob("*.tmp"):
            await tmp_file.unlink()
```

---

## §6 Execution Sequence

1. **Preparation**: Read `entity_registry.py`, `context_builder.py`, `entity_workspace.py`
2. **Implement Guardian**: Add `SovereignWriteGuard`, `FileLocking`, `TaintPropagation`
3. **Write Migration Script**: Create `scripts/migrate_soul_v6.py`
4. **Dry Run**: `python scripts/migrate_soul_v6.py --dry-run` across 11 entities
5. **Validate**: Inspect the generated manifest
6. **Commit Migration**: Run the actual migration
7. **Write Breach Test**: Add `test_sovereign_write_guard_breach`
8. **Verify**: `make test` (must stay 444/444), `make verify-souls`

---

*Blueprint recorded by Kali · 2026-06-22 · Ratified by MaKaLi Triad*
*Cross-reference: SOUL_ARCHITECTURE_PROTOCOL.md, SOVEREIGN_ARK_BLUEPRINT.md*
