"""
Scribe Hub Master — File Locking with Stale Lock Recovery
Cross-platform atomic file locking for HMC_COLLABORATION_HUB.md
"""
import os
import json
import time
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


class HubLockError(Exception):
    """Raised when lock acquisition fails."""
    pass


class HubLock:
    """
    File-based lock with TTL-based stale lock detection and recovery.
    Uses atomic file creation (O_CREAT | O_EXCL) for lock acquisition.
    """
    
    def __init__(self, target_file: str, ttl_seconds: int = 60):
        self.target_file = target_file
        self.lock_file = f"{target_file}.lock"
        self.ttl_seconds = ttl_seconds
        self._acquired = False

    def _is_stale(self) -> bool:
        """Check if existing lock is stale (older than TTL)."""
        try:
            with open(self.lock_file, 'r') as f:
                lock_data = json.load(f)
                return (time.time() - lock_data.get('timestamp', 0)) > self.ttl_seconds
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return True  # If unreadable or missing, treat as stale/acquirable

    def acquire(self, agent_id: str, timeout: int = 10) -> bool:
        """
        Acquire lock with stale lock recovery.
        
        Args:
            agent_id: Identifier of the agent acquiring the lock (e.g., "scribe-hub-master")
            timeout: Maximum seconds to wait for lock
            
        Returns:
            True if lock acquired
            
        Raises:
            HubLockError: If lock cannot be acquired within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Atomic file creation - fails if file exists
                fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, 'w') as f:
                    json.dump({
                        "agent": agent_id,
                        "timestamp": time.time(),
                        "pid": os.getpid()
                    }, f)
                self._acquired = True
                return True
            except FileExistsError:
                if self._is_stale():
                    self.release()  # Clear stale lock
                else:
                    time.sleep(0.5)  # Wait and retry
            except OSError as e:
                raise HubLockError(f"Lock acquisition failed: {e}")
        
        raise HubLockError(f"Failed to acquire lock on {self.target_file} after {timeout}s")

    def release(self):
        """Release the lock if we own it."""
        if self._acquired:
            try:
                os.remove(self.lock_file)
            except FileNotFoundError:
                pass
            self._acquired = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


@contextmanager
def managed_hub_lock(target_file: str, agent_id: str, ttl_seconds: int = 60):
    """
    Context manager for safe lock acquisition and release.
    
    Usage:
        with managed_hub_lock("HUB.md", "scribe") as lock:
            # Write to HUB.md
            pass
    """
    lock = HubLock(target_file, ttl_seconds)
    lock.acquire(agent_id)
    try:
        yield lock
    finally:
        lock.release()


def atomic_write(target_file: str, content: str) -> None:
    """
    Atomically write content to target file using temp file + rename.
    Ensures no partial writes are visible to readers.
    """
    dir_name = os.path.dirname(target_file) or "."
    prefix = f".{os.path.basename(target_file)}-"
    
    fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix=prefix, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
        os.rename(temp_path, target_file)  # Atomic on POSIX
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise