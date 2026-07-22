# 🔱 Omega Engine — Coordinated Failure Layer
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ SCAFFOLD
#
# 4-layer failure handling for MaKaLi Parallel Council:
# 1. Jitter retry (exponential backoff with random jitter)
# 2. Fallback chain (degrade gracefully)
# 3. Quality-aware circuit breaker (>30% error/10min opens)
# 4. WAL checkpointing (crash recovery)

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
import math
import random
import time

from .models import RetryPolicy, FallbackChain, CircuitBreakerState


class CoordinatedRecovery:
    """Manages recovery across all 4 failure layers."""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.wal = WriteAheadLog()
    
    def should_retry(self, attempt: int, policy: Optional[RetryPolicy] = None) -> bool:
        """Check if retry should be attempted with jitter."""
        policy = policy or RetryPolicy()
        if attempt >= policy.max_retries:
            return False
        if self.circuit_breaker.state != CircuitBreakerState.CLOSED:
            return False
        return True
    
    def wait_time(self, attempt: int, policy: Optional[RetryPolicy] = None) -> float:
        """Calculate exponential backoff with jitter."""
        policy = policy or RetryPolicy()
        delay = min(
            policy.base_delay_ms * (2 ** attempt),
            policy.max_delay_ms
        )
        jitter = delay * random.uniform(-policy.jitter_factor, policy.jitter_factor)
        return max(0.001, (delay + jitter) / 1000.0)  # Return seconds


class CircuitBreaker:
    """Quality-aware circuit breaker for council operations.
    
    ⚠️ C-6' NOTE: This breaker is domain-specific (schema quality).
    For provider-level circuit breaking, use HealthMonitor.get_breaker().
    
    Opens when >30% error rate over 10 minutes, or
    >15% schema validation failure over 60 seconds.
    """
    
    def __init__(self):
        self.state = CircuitBreakerState.CLOSED
        self.error_window: list[tuple[datetime, bool]] = []
        self.window_minutes = 10
        self.error_threshold = 0.30
        self.half_open_timeout_seconds = 30
    
    @property
    def error_rate(self) -> float:
        """Current error rate over the sliding window."""
        self._prune_window()
        if not self.error_window:
            return 0.0
        errors = sum(1 for _, is_error in self.error_window if is_error)
        return errors / len(self.error_window)
    
    def record_attempt(self, success: bool):
        """Record a success or failure in the sliding window."""
        now = datetime.now(timezone.utc)
        self.error_window.append((now, not success))
        self._prune_window()
        
        if self.error_rate > self.error_threshold:
            self.state = CircuitBreakerState.OPEN
    
    def _prune_window(self):
        """Remove entries outside the sliding window."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.window_minutes)
        self.error_window = [(ts, e) for ts, e in self.error_window if ts > cutoff]


class WriteAheadLog:
    """Write-Ahead Log for crash recovery during council operations.
    
    Records each stage's progress with:
    - session_id
    - stage name
    - state (pending/started/completed/failed)
    - timestamp
    - artifact paths
    """
    
    def __init__(self, log_dir: str = "data/council/wal/"):
        self.log_dir = log_dir
    
    def checkpoint(self, session_id: str, stage: str, state: str, **metadata):
        """Write a WAL checkpoint entry.
        
        TODO: Implement atomic write with .tmp → .json rename.
        """
        pass
