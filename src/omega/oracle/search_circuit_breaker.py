"""Search Circuit Breaker — Resilience Pattern for Search Provider Tiers.
AP: AP-SEARCH-CIRCUIT-BREAKER-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_circuit_breaker ⬡ ACTIVE

⚠️ DEPRECATED — C-6' Unification (2026-07-22)
══════════════════════════════════════════════════════
This file is DEPRECATED. Use HealthMonitor.get_breaker() instead:
    
    from omega.oracle.health_monitor import get_health_monitor
    breaker = get_health_monitor().get_breaker("provider_name")
    
The SearchCircuitBreakerRegistry is kept for backward compatibility
during Phase C-6' migration. All new code MUST use HealthMonitor.
══════════════════════════════════════════════════════

Implements circuit breaker pattern per tier (T0-T3) to prevent cascade failures
and enable fast failover when search providers are degraded.
"""

import time
import logging
import threading
from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing recovery, one request allowed


@dataclass
class CircuitBreakerConfig:
    """Configuration for a single circuit breaker."""
    failure_threshold: int = 3          # Failures before opening
    success_threshold: int = 2          # Successes in half-open before closing
    recovery_timeout: float = 60.0      # Seconds before half-open
    timeout: float = 30.0               # Request timeout
    excluded_exceptions: tuple = ()     # Exceptions that don't count as failures


@dataclass
class CircuitBreakerStats:
    """Runtime statistics for a circuit breaker."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class SearchCircuitBreaker:
    """Circuit breaker for search provider tiers.
    
    Each tier (T0-T3) gets its own circuit breaker instance.
    Thread-safe for concurrent access.
    """
    
    def __init__(
        self,
        tier: int,
        config: Optional[CircuitBreakerConfig] = None,
        name: Optional[str] = None,
    ):
        self.tier = tier
        self.name = name or f"search_tier_{tier}"
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._stats = CircuitBreakerStats()
        self._lock = threading.RLock()
        self._last_state_change = time.time()
        
        # Tier name mapping for logging
        self._tier_names = {
            0: "T0_LOCAL",
            1: "T1_SEARXNG",
            2: "T2_EXA",
            3: "T3_FIRECRAWL",
        }
    
    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._check_state_transition()
            return self._state
    
    @property
    def tier_name(self) -> str:
        return self._tier_names.get(self.tier, f"T{self.tier}_UNKNOWN")
    
    def _check_state_transition(self) -> None:
        """Check and perform state transitions based on time and thresholds."""
        now = time.time()
        
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if now - self._last_state_change >= self.config.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
                logger.info(f"Circuit breaker {self.name} ({self.tier_name}) -> HALF_OPEN (recovery timeout)")
        
        elif self._state == CircuitState.HALF_OPEN:
            # Half-open state: if we have enough consecutive successes, close
            if self._stats.consecutive_successes >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
                logger.info(f"Circuit breaker {self.name} ({self.tier_name}) -> CLOSED (recovery confirmed)")
    
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        self._last_state_change = time.time()
        self._stats.state_changes += 1
        
        # Reset counters on state change
        if new_state == CircuitState.CLOSED:
            self._stats.consecutive_failures = 0
            self._stats.consecutive_successes = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._stats.consecutive_successes = 0
        elif new_state == CircuitState.OPEN:
            self._stats.consecutive_failures = 0
    
    def can_execute(self) -> bool:
        """Check if a request can be executed."""
        with self._lock:
            self._check_state_transition()
            
            if self._state == CircuitState.CLOSED:
                return True
            elif self._state == CircuitState.HALF_OPEN:
                return True  # Allow one test request
            else:  # OPEN
                self._stats.rejected_calls += 1
                logger.warning(f"Circuit breaker {self.name} ({self.tier_name}) REJECTED request (state=OPEN)")
                return False
    
    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            self._stats.total_calls += 1
            self._stats.successful_calls += 1
            self._stats.last_success_time = time.time()
            self._stats.consecutive_failures = 0
            self._stats.consecutive_successes += 1
            
            if self._state == CircuitState.HALF_OPEN:
                # Check if we should close
                if self._stats.consecutive_successes >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    logger.info(f"Circuit breaker {self.name} ({self.tier_name}) -> CLOSED (success threshold met)")
    
    def record_failure(self, exception: Optional[Exception] = None) -> None:
        """Record a failed call."""
        with self._lock:
            # Check if this exception should be excluded
            if exception and isinstance(exception, self.config.excluded_exceptions):
                logger.debug(f"Circuit breaker {self.name}: excluded exception {type(exception).__name__}")
                return
            
            self._stats.total_calls += 1
            self._stats.failed_calls += 1
            self._stats.last_failure_time = time.time()
            self._stats.consecutive_successes = 0
            self._stats.consecutive_failures += 1
            
            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open -> open
                self._transition_to(CircuitState.OPEN)
                logger.warning(f"Circuit breaker {self.name} ({self.tier_name}) -> OPEN (failure in half-open)")
            
            elif self._state == CircuitState.CLOSED:
                # Check if we should open
                if self._stats.consecutive_failures >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)
                    logger.warning(f"Circuit breaker {self.name} ({self.tier_name}) -> OPEN (failure threshold met)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        with self._lock:
            return {
                "name": self.name,
                "tier": self.tier,
                "tier_name": self.tier_name,
                "state": self._state.value,
                "total_calls": self._stats.total_calls,
                "successful_calls": self._stats.successful_calls,
                "failed_calls": self._stats.failed_calls,
                "rejected_calls": self._stats.rejected_calls,
                "success_rate": (
                    self._stats.successful_calls / self._stats.total_calls 
                    if self._stats.total_calls > 0 else 0.0
                ),
                "consecutive_failures": self._stats.consecutive_failures,
                "consecutive_successes": self._stats.consecutive_successes,
                "last_failure_time": self._stats.last_failure_time,
                "last_success_time": self._stats.last_success_time,
                "state_changes": self._stats.state_changes,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "success_threshold": self.config.success_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                },
            }
    
    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            self._stats = CircuitBreakerStats()
            logger.info(f"Circuit breaker {self.name} ({self.tier_name}) MANUALLY RESET")


class SearchCircuitBreakerRegistry:
    """Registry managing circuit breakers for all search tiers."""
    
    def __init__(self):
        self._breakers: Dict[int, SearchCircuitBreaker] = {}
        self._lock = threading.RLock()
        self._default_config = CircuitBreakerConfig()
    
    def get_breaker(self, tier: int, config: Optional[CircuitBreakerConfig] = None) -> SearchCircuitBreaker:
        """Get or create a circuit breaker for a tier."""
        with self._lock:
            if tier not in self._breakers:
                self._breakers[tier] = SearchCircuitBreaker(
                    tier=tier,
                    config=config or self._default_config,
                )
            return self._breakers[tier]
    
    def can_execute(self, tier: int) -> bool:
        """Check if a tier can execute."""
        return self.get_breaker(tier).can_execute()
    
    def record_success(self, tier: int) -> None:
        """Record success for a tier."""
        self.get_breaker(tier).record_success()
    
    def record_failure(self, tier: int, exception: Optional[Exception] = None) -> None:
        """Record failure for a tier."""
        self.get_breaker(tier).record_failure(exception)
    
    def get_all_stats(self) -> Dict[int, Dict[str, Any]]:
        """Get stats for all breakers."""
        with self._lock:
            return {tier: breaker.get_stats() for tier, breaker in self._breakers.items()}
    
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
    
    def reset_tier(self, tier: int) -> None:
        """Reset a specific tier's circuit breaker."""
        with self._lock:
            if tier in self._breakers:
                self._breakers[tier].reset()


# Global registry instance
_circuit_breaker_registry: Optional[SearchCircuitBreakerRegistry] = None
_registry_lock = threading.Lock()


def get_circuit_breaker_registry() -> SearchCircuitBreakerRegistry:
    """Get the global circuit breaker registry (singleton)."""
    global _circuit_breaker_registry
    if _circuit_breaker_registry is None:
        with _registry_lock:
            if _circuit_breaker_registry is None:
                _circuit_breaker_registry = SearchCircuitBreakerRegistry()
    return _circuit_breaker_registry


# Tier-specific default configurations
TIER_CONFIGS = {
    0: CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30.0),   # Local - more tolerant
    1: CircuitBreakerConfig(failure_threshold=3, recovery_timeout=60.0),   # SearXNG
    2: CircuitBreakerConfig(failure_threshold=3, recovery_timeout=60.0),   # Exa
    3: CircuitBreakerConfig(failure_threshold=2, recovery_timeout=120.0),  # Firecrawl - stricter (credits)
}


def initialize_circuit_breakers() -> SearchCircuitBreakerRegistry:
    """Initialize circuit breakers for all tiers with tier-specific configs."""
    registry = get_circuit_breaker_registry()
    for tier, config in TIER_CONFIGS.items():
        registry.get_breaker(tier, config)
    return registry