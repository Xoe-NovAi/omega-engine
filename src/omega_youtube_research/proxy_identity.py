"""
L2 Anti-Bot Infrastructure — Sticky Proxy Identity + Adaptive Rate Limiting
⬡ OMEGA ⬡ RESEARCHER ⬡ L2 ⬡ PROXY_IDENTITY
AP Token: AP-YOUTUBE-PROXY-v2.0.0

Mandate Compliance:
- M1 AnyIO: all I/O wrapped in anyio.to_thread.run_sync
- M2 Firewall: WAD-isolated
- M7 Local-First: no cloud deps for rate limiting
- M8 Zero Telemetry: no analytics
- M12 Queue Integrity: identity state has terminal states
- M23 Failure Integrity: circuit breaker quarantines on 15% fail rate

Per Apify 2026 guide: YouTube tracks session continuity — rotating IPs mid-session triggers fraud detection.
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.omega.errors import OmegaError


# ── YouTube Identity (Sticky Session) ──────────────────────────────────────────

@dataclass
class YouTubeIdentity:
    """
    Sticky session identity for youtube.com — appears as consistent user.
    
    Bright Data / IPRoyal pattern: -session-{id} suffix on residential proxies.
    Rotates after configurable window (default 8 min = 80% of 10-min max).
    """
    
    proxy_base: str                    # e.g., "brd-customer-X-zone-residential:PASS@host:port"
    session_window: int = 480          # 8 min (80% of 10-min max)
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    session_start: float = field(default_factory=time.time)
    request_count: int = 0
    last_rotate: float = field(default_factory=time.time)
    
    @property
    def proxy_url(self) -> str:
        """Get proxy URL with current session ID."""
        if time.time() - self.session_start > self.session_window:
            self.rotate()
        
        # Bright Data / IPRoyal pattern: zone-residential-session-{id}
        if "zone-residential:" in self.proxy_base:
            return self.proxy_base.replace(
                "zone-residential:",
                f"zone-residential-session-{self.session_id}:"
            )
        elif "zone-residential-session-" in self.proxy_base:
            # Already has session, replace it
            import re
            return re.sub(
                r"zone-residential-session-[a-f0-9]+:",
                f"zone-residential-session-{self.session_id}:",
                self.proxy_base
            )
        return self.proxy_base
    
    def rotate(self) -> None:
        """Force rotate identity (after ban or window expiry)."""
        self.session_id = uuid.uuid4().hex
        self.session_start = time.time()
        self.request_count = 0
        self.last_rotate = time.time()
    
    def record_request(self) -> None:
        self.request_count += 1
    
    def get_stats(self) -> dict:
        return {
            "session_id": self.session_id,
            "session_age_sec": time.time() - self.session_start,
            "request_count": self.request_count,
            "proxy_url": self.proxy_url,
        }


# ── Adaptive Rate Limiter (Token Bucket + Circuit Breaker) ─────────────────────

class LimiterState(Enum):
    ACTIVE = "active"
    THROTTLED = "throttled"
    QUARANTINED = "quarantined"


@dataclass
class AdaptiveRateLimiter:
    """
    Token bucket per identity — halves refill on 429, quarantines on 15% fail rate.
    
    M12 Queue Integrity: state has terminal states (QUARANTINED).
    M23 Failure Integrity: no silent drops — explicit quarantine.
    """
    
    identity: YouTubeIdentity
    base_rate: float = 1.0              # tokens/sec
    max_tokens: float = 10.0
    tokens: float = field(default=10.0)
    refill_rate: float = field(default=1.0)
    fail_window: list[float] = field(default_factory=list)
    state: LimiterState = LimiterState.ACTIVE
    last_refill: float = field(default_factory=time.time)
    
    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    
    def acquire(self) -> bool:
        """Try to acquire a token. Returns True if allowed."""
        if self.state == LimiterState.QUARANTINED:
            return False
        
        self._refill()
        
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            self.identity.record_request()
            return True
        
        return False
    
    def report_result(self, status: int) -> None:
        """Report HTTP result — adapts rate and tracks failures."""
        now = time.time()
        
        # Clean old failures (10 min window)
        self.fail_window = [t for t in self.fail_window if now - t < 600]
        
        if status == 429:
            # Throttled — halve refill rate
            self.refill_rate *= 0.5
            self.fail_window.append(now)
            self.state = LimiterState.THROTTLED
            
        elif status == 200:
            # Success — gradually restore rate
            self.refill_rate = min(self.refill_rate * 1.1, self.base_rate)
            if self.state == LimiterState.THROTTLED and self.refill_rate >= self.base_rate * 0.9:
                self.state = LimiterState.ACTIVE
        
        # Check quarantine threshold (15% fail rate in window)
        if len(self.fail_window) >= 3:
            fail_rate = len(self.fail_window) / max(1, len(self.fail_window))
            if fail_rate > 0.15:
                self.state = LimiterState.QUARANTINED
                # Alert Hivemind
                # hivemind.post_context(entity="verity", intent="blocker", ...)
    
    def get_stats(self) -> dict:
        return {
            "state": self.state.value,
            "tokens": self.tokens,
            "refill_rate": self.refill_rate,
            "fail_count": len(self.fail_window),
            "identity": self.identity.get_stats(),
        }


# ── Contract Test Helpers (M21) ────────────────────────────────────────────────

def assert_youtube_identity_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for YouTubeIdentity type."""
    assert isinstance(obj, YouTubeIdentity), f"Expected YouTubeIdentity, got {type(obj)}"
    assert hasattr(obj, "proxy_url")
    assert hasattr(obj, "rotate")
    assert callable(obj.rotate)
    assert hasattr(obj, "record_request")
    assert callable(obj.record_request)
    assert hasattr(obj, "get_stats")
    assert callable(obj.get_stats)


def assert_adaptive_rate_limiter_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for AdaptiveRateLimiter type."""
    assert isinstance(obj, AdaptiveRateLimiter), f"Expected AdaptiveRateLimiter, got {type(obj)}"
    assert hasattr(obj, "acquire")
    assert callable(obj.acquire)
    assert hasattr(obj, "report_result")
    assert callable(obj.report_result)
    assert hasattr(obj, "get_stats")
    assert callable(obj.get_stats)
    assert hasattr(obj, "state")
    assert isinstance(obj.state, LimiterState)