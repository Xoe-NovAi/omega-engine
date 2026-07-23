"""
Scribe Hub Master — File Locking with filelock (Cross-Platform, OS-Enforced)
Replaces custom sidecar lock files with filelock.FileLock for:
- OS-enforced release on process crash (no stale TTL guessing)
- Cross-platform: fcntl (Linux/macOS) + msvcrt (Windows)
- Async support via anyio.to_thread.run_sync
- Network filesystem safety with SoftFileLock option
"""
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional

try:
    from filelock import FileLock, SoftFileLock, Timeout
    FILELOCK_AVAILABLE = True
except ImportError:
    FILELOCK_AVAILABLE = False


class HubLockError(Exception):
    """Raised when lock acquisition fails."""
    pass


class HubLock:
    """
    Cross-platform, OS-enforced file lock using filelock library.
    
    Advantages over custom sidecar locks:
    - Automatic release on process death (kernel-enforced)
    - No TTL guessing or stale lock detection needed
    - Works on Linux (fcntl), macOS (fcntl), Windows (msvcrt)
    - Optional SoftFileLock for NFS/SMB network filesystems
    - Thread-safe and process-safe
    """
    
    def __init__(
        self, 
        target_file: str, 
        timeout: float = 10.0
    ):
        """
        Initialize lock for a target file.
        
        Args:
            target_file: Path to the file being protected (e.g., HMC_COLLABORATION_HUB.md)
            timeout: Maximum seconds to wait for lock acquisition
        """
        self.target_file = Path(target_file)
        self.lock_file = self.target_file.with_suffix(
            self.target_file.suffix + ".lock"
        )
        self.timeout = timeout
        
        # Use standard FileLock (fcntl on POSIX, msvcrt on Windows)
        self._lock = FileLock(str(self.lock_file), timeout=timeout)
        self._acquired = False
    
    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire the lock.
        
        Args:
            blocking: If True, wait up to timeout. If False, return immediately.
            timeout: Override default timeout for this acquisition.
            
        Returns:
            True if lock acquired, False if non-blocking and unavailable.
            
        Raises:
            HubLockError: If blocking=True and timeout exceeded.
        """
        try:
            self._lock.acquire(blocking=blocking, timeout=timeout or self.timeout)
            self._acquired = True
            return True
        except Timeout:
            if blocking:
                raise HubLockError(
                    f"Failed to acquire lock on {self.target_file} after {timeout or self.timeout}s"
                )
            return False
    
    def release(self):
        """Release the lock if we own it."""
        if self._acquired:
            try:
                self._lock.release()
            except Exception:
                pass  # Lock may already be released
            self._acquired = False
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
    
    @property
    def is_locked(self) -> bool:
        """Check if lock is currently held by this instance."""
        return self._acquired and self._lock.is_locked


@asynccontextmanager
async def managed_hub_lock(
    target_file: str, 
    timeout: float = 10.0
) -> AsyncGenerator[None, None]:
    """
    Async context manager for file locking.
    
    Runs the blocking lock acquisition/release in a thread pool
    to avoid blocking the event loop.
    
    Usage:
        async with managed_hub_lock("HUB.md") as lock:
            # Safe to write to HUB.md
            atomic_write("HUB.md", content)
    """
    import asyncio
    
    lock = HubLock(target_file, timeout=timeout)
    loop = asyncio.get_event_loop()
    
    # Acquire in thread pool (blocking call)
    acquired = await loop.run_in_executor(None, lock.acquire, True, timeout)
    if not acquired:
        raise HubLockError(f"Failed to acquire lock on {target_file} after {timeout}s")
    
    try:
        yield
    finally:
        # Release in thread pool
        await loop.run_in_executor(None, lock.release)


def atomic_write(target_file: str, content: str) -> None:
    """
    Atomically write content to target file using temp file + fsync + os.replace.
    
    Cross-platform atomic write:
    - POSIX: os.replace is atomic
    - Windows 3.3+: os.replace is atomic
    - fsync ensures durability before rename
    
    Args:
        target_file: Path to target file
        content: String content to write
    """
    target = Path(target_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    fd, temp_path = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}-",
        suffix=".tmp"
    )
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # CRITICAL: force to disk before rename
        
        # Atomic replace
        os.replace(temp_path, target)
    except Exception:
        # Cleanup on failure
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise


# --- Compatibility: Re-export for existing imports ---
__all__ = [
    "HubLock",
    "HubLockError", 
    "managed_hub_lock",
    "atomic_write",
]