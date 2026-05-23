# 🔱 Omega Engine — Gemma Maintenance Worker Design
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ GEMMA-MAINTENANCE-WORKER

**AP Token**: `AP-GEMMA-MAINTENANCE-WORKER-v1.0.0`
**Status**: ✅ COMPLETE — Technical Design Ready
**Last Updated**: 2026-05-16
**Author**: OpenCode CLI (Sovereign Architect)

---

## §1 Executive Summary

This document specifies a background maintenance worker for Google Gemma 4-31b model via Google AI Studio. The worker operates as a companion to the `ModelGateway`, providing proactive health monitoring, quota tracking, failover coordination, and observability reporting.

**Key Design Decisions:**
- Worker runs as an async task group within the Omega Engine process
- Integrates with existing `ModelGateway` provider fabric
- Reports to existing `ObservabilityEngine` for metrics
- Stateless health checks against Google AI Studio API
- Failover triggers auto-reroute to configured backup providers

---

## §2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OMEGA ENGINE                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌────────────────────────┐ │
│  │    ORACLE       │    │  MODEL GATEWAY  │    │  OBSERVABILITY ENGINE  │ │
│  │                 │───▶│                 │───▶│                        │ │
│  │  .talk()        │    │  .generate()    │    │  .log_event()          │ │
│  │  .summon()      │    │  .providers[]   │    │  .record_training_()   │ │
│  └─────────────────┘    └────────┬────────┘    └────────────────────────┘ │
│                                  │                                          │
│                                  ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    GEMMA MAINTENANCE WORKER                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │HealthMonitor│  │QuotaTracker │  │WarmUpManager│  │FailoverCtrl │ │   │
│  │  │             │  │             │  │             │  │            │ │   │
│  │  │- API ping   │  │- RPM check │  │- Idle ping  │  │- Circuit   │ │   │
│  │  │- Latency    │  │- RPD track  │  │- Connection │  │- Fallback  │ │   │
│  │  │- Error rate │  │- TPM usage  │  │- Keep-alive │  │- Recovery  │ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘ │   │
│  │         │                │                │                │         │   │
│  │         └────────────────┴────────────────┴────────────────┘         │   │
│  │                                    │                                  │   │
│  │                                    ▼                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    TASK SCHEDULER (AnyIO)                     │ │   │
│  │  │  - Periodic health checks (every 60s)                          │ │   │
│  │  │  - Quota monitoring (every 300s)                               │ │   │
│  │  │  - Warm-up pings (every 180s)                                   │ │   │
│  │  │  - Metrics flush (every 60s)                                    │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                    │
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌────────────────┐  │
│  │   GOOGLE AI STUDIO   │    │    BACKUP PROVIDERS  │    │   ALERTING    │  │
│  │                      │    │                      │    │                │  │
│  │  gemma-4-31b-it      │    │  - DeepSeek V4 Flash │    │ - Omega logs  │  │
│  │  gemma-4-26b-a4b-it  │    │  - OpenCode Zen      │    │ - Optional    │  │
│  │                      │    │  - lmster (local)     │    │   Slack/PagerD│  │
│  │  /v1beta/models     │    │                      │    │                │  │
│  │  /v1beta/...:gen    │    │  (from providers.yaml)│    │                │  │
│  └──────────────────────┘    └──────────────────────┘    └────────────────┘  │
│                                                                              │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## §3 Component Breakdown

### 3.1 HealthMonitor

**Purpose**: Continuously verify Gemma availability and performance.

**Responsibilities:**
- Ping Google AI Studio API endpoint (`/v1beta/models`)
- Measure latency to first token (TTFT) via lightweight prompt
- Track error rates (429s, 500s, timeouts, network failures)
- Report health status to ModelGateway for routing decisions

**Implementation:**
```python
class HealthMonitor:
    """Monitors Google AI Studio Gemma model health."""
    
    def __init__(self, api_key: str, model: str = "gemma-4-31b-it"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._health_state = HealthState.HEALTHY
        self._consecutive_failures = 0
        self._latency_history: deque = deque(maxlen=100)
    
    async def check_health(self) -> HealthStatus:
        """Perform a health check against the API."""
        start = time.monotonic()
        try:
            # Lightweight test prompt
            payload = {
                "contents": [{"parts": [{"text": "OK"}]}],
                "generationConfig": {"maxOutputTokens": 2, "temperature": 0.0}
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/models/{self.model}:generateContent"
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": self.api_key},
                    json=payload
                )
                
                latency_ms = (time.monotonic() - start) * 1000
                self._latency_history.append(latency_ms)
                
                if response.status_code == 200:
                    self._consecutive_failures = 0
                    self._health_state = HealthState.HEALTHY
                    return HealthStatus(
                        available=True,
                        latency_ms=latency_ms,
                        error_rate=0.0
                    )
                elif response.status_code == 429:
                    self._consecutive_failures += 1
                    self._health_state = HealthState.RATE_LIMITED
                    return HealthStatus(
                        available=False,
                        latency_ms=latency_ms,
                        error_rate=1.0,
                        error_type="rate_limit"
                    )
                else:
                    self._consecutive_failures += 1
                    self._health_state = HealthState.UNHEALTHY
                    return HealthStatus(
                        available=False,
                        latency_ms=latency_ms,
                        error_rate=1.0,
                        error_type=f"http_{response.status_code}"
                    )
        except httpx.TimeoutException:
            self._consecutive_failures += 1
            self._health_state = HealthState.TIMEOUT
            return HealthStatus(
                available=False,
                latency_ms=10000,
                error_rate=1.0,
                error_type="timeout"
            )
        except Exception as e:
            self._consecutive_failures += 1
            return HealthStatus(
                available=False,
                latency_ms=0,
                error_rate=1.0,
                error_type=str(e)
            )
    
    @property
    def is_healthy(self) -> bool:
        """Return True if model is considered healthy."""
        return self._health_state == HealthState.HEALTHY
    
    @property
    def average_latency(self) -> float:
        """Return average latency over recent checks."""
        if not self._latency_history:
            return 0.0
        return sum(self._latency_history) / len(self._latency_history)
    
    @property
    def error_rate(self) -> float:
        """Return error rate over recent checks."""
        if not self._latency_history:
            return 0.0
        failures = sum(1 for lat in self._latency_history if lat > 5000)
        return failures / len(self._latency_history)


class HealthState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthStatus:
    available: bool
    latency_ms: float
    error_rate: float
    error_type: Optional[str] = None
```

### 3.2 QuotaTracker

**Purpose**: Monitor Google AI Studio quota usage and warn before exhaustion.

**Responsibilities:**
- Track RPM (requests per minute) via API response headers
- Estimate RPD (requests per day) from usage patterns
- Monitor TPM (tokens per minute) if available
- Emit warnings at configurable thresholds (75%, 90%)
- Track quota reset time (midnight Pacific)

**Implementation:**
```python
class QuotaTracker:
    """Tracks Google AI Studio quota usage."""
    
    # Current free tier limits (May 2026)
    DEFAULT_RPM_LIMIT = 30
    DEFAULT_RPD_LIMIT = 1500
    DEFAULT_TPM_LIMIT = 1_000_000
    
    def __init__(
        self,
        api_key: str,
        rpm_limit: int = DEFAULT_RPM_LIMIT,
        rpd_limit: int = DEFAULT_RPD_LIMIT,
        tpm_limit: int = DEFAULT_TPM_LIMIT,
    ):
        self.api_key = api_key
        self.rpm_limit = rpm_limit
        self.rpd_limit = rpd_limit
        self.tpm_limit = tpm_limit
        
        self._requests_this_minute = 0
        self._requests_today = 0
        self._minute_start = datetime.now()
        self._day_start = datetime.now()
        self._request_timestamps: deque = deque(maxlen=rpm_limit * 2)
    
    async def check_quota(self) -> QuotaStatus:
        """Check current quota status."""
        now = datetime.now()
        
        # Reset per-minute counter if needed
        if (now - self._minute_start).total_seconds() >= 60:
            self._requests_this_minute = 0
            self._minute_start = now
        
        # Reset per-day counter if needed (midnight Pacific)
        if now.date() > self._day_start.date():
            self._requests_today = 0
            self._day_start = now
        
        return QuotaStatus(
            rpm_used=self._requests_this_minute,
            rpm_remaining=max(0, self.rpm_limit - self._requests_this_minute),
            rpd_used=self._requests_today,
            rpd_remaining=max(0, self.rpd_limit - self._requests_today),
            rpm_percent=self._requests_this_minute / self.rpm_limit * 100,
            rpd_percent=self._requests_today / self.rpd_limit * 100,
        )
    
    async def record_request(self):
        """Record that a request was made."""
        self._requests_this_minute += 1
        self._requests_today += 1
        self._request_timestamps.append(time.time())
    
    def should_warn(self) -> bool:
        """Return True if quota usage warrants a warning."""
        status = asyncio.create_task(self.check_quota())
        # Would need sync version or cache for property access
        return False  # Placeholder


@dataclass
class QuotaStatus:
    rpm_used: int
    rpm_remaining: int
    rpd_used: int
    rpd_remaining: int
    rpm_percent: float
    rpd_percent: float
    
    @property
    def rpm_warning(self) -> bool:
        return self.rpm_percent >= 75.0
    
    @property
    def rpd_warning(self) -> bool:
        return self.rpd_percent >= 90.0
    
    @property
    def rpm_critical(self) -> bool:
        return self.rpm_percent >= 95.0
```

### 3.3 WarmUpManager

**Purpose**: Keep connection warm and reduce perceived latency for first requests.

**Note on Cloud API Warming**: Unlike self-hosted models where KV cache persistence matters, Google AI Studio models are always "warm" on Google's servers. The WarmUpManager instead focuses on:
- Maintaining connection readiness (HTTP keep-alive)
- Pre-validating API key still works
- Detecting early degradation before user-facing requests

**Implementation:**
```python
class WarmUpManager:
    """Manages warm-up pings for Gemma model."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemma-4-31b-it",
        ping_interval: int = 180,  # seconds
    ):
        self.api_key = api_key
        self.model = model
        self.ping_interval = ping_interval
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._last_ping_time: Optional[datetime] = None
        self._last_ping_success = False
    
    async def ping(self) -> bool:
        """Send a warm-up ping to keep connection ready."""
        try:
            # Minimal prompt - just validate the API works
            payload = {
                "contents": [{"parts": [{"text": "Ping"}]}],
                "generationConfig": {"maxOutputTokens": 1, "temperature": 0.0}
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"{self.base_url}/models/{self.model}:generateContent"
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": self.api_key},
                    json=payload
                )
                
                self._last_ping_time = datetime.now()
                self._last_ping_success = response.status_code == 200
                return self._last_ping_success
        except Exception:
            self._last_ping_success = False
            return False
    
    @property
    def needs_ping(self) -> bool:
        """Return True if a warm-up ping is due."""
        if self._last_ping_time is None:
            return True
        return (datetime.now() - self._last_ping_time).total_seconds() > self.ping_interval
    
    @property
    def was_recently_successful(self) -> bool:
        """Return True if last ping was successful."""
        return self._last_ping_success
```

### 3.4 FailoverController

**Purpose**: Coordinate automatic failover when Gemma becomes unavailable.

**Responsibilities:**
- Monitor health state from HealthMonitor
- Trigger failover when consecutive failures exceed threshold
- Coordinate with ModelGateway to update provider priority
- Attempt recovery after cooldown period
- Log all failover events for observability

**Implementation:**
```python
class FailoverController:
    """Manages failover to backup providers."""
    
    def __init__(
        self,
        model_gateway: "ModelGateway",
        max_consecutive_failures: int = 3,
        cooldown_seconds: int = 300,
    ):
        self.model_gateway = model_gateway
        self.max_consecutive_failures = max_consecutive_failures
        self.cooldown_seconds = cooldown_seconds
        
        self._is_failover_active = False
        self._failover_start_time: Optional[datetime] = None
        self._last_attempt_time: Optional[datetime] = None
        self._failure_count = 0
    
    async def on_request_failure(self, error: str) -> bool:
        """Process a request failure. Return True if failover was triggered."""
        self._failure_count += 1
        
        if self._failure_count >= self.max_consecutive_failures and not self._is_failover_active:
            await self._trigger_failover(error)
            return True
        
        return False
    
    async def _trigger_failover(self, reason: str):
        """Activate failover mode."""
        logger.warning(f"Activating failover to backup providers: {reason}")
        self._is_failover_active = True
        self._failover_start_time = datetime.now()
        self._failure_count = 0
        
        # Update ModelGateway provider order
        # Move backup providers to front
        await self.model_gateway.reorder_providers_for_failover()
        
        # Log to observability
        observability.get_engine().log_event(
            EventType.ERROR,
            f"trc_{uuid.uuid4().hex[:12]}",
            {"event": "failover.activated", "reason": reason}
        )
    
    async def attempt_recovery(self) -> bool:
        """Attempt to recover to primary provider."""
        if not self._is_failover_active:
            return True
        
        # Check cooldown
        if self._failover_start_time:
            elapsed = (datetime.now() - self._failover_start_time).total_seconds()
            if elapsed < self.cooldown_seconds:
                return False
        
        # Try to restore primary
        logger.info("Attempting to restore primary provider")
        await self.model_gateway.restore_primary_provider()
        self._is_failover_active = False
        self._failure_count = 0
        
        return True
    
    @property
    def is_failover_active(self) -> bool:
        return self._is_failover_active
```

---

## §4 Integration with ModelGateway

The worker integrates with the existing `ModelGateway` through the following interface:

### 4.1 Provider Reordering

```python
class ModelGateway:
    """Extended with failover support."""
    
    async def reorder_providers_for_failover(self):
        """Move backup providers to front of the chain."""
        # Reorder self.providers to put backups first
        # Current: [native-gguf, google, openrouter, lmster, ollama, mock]
        # After failover: [openrouter, lmster, ollama, mock, native-gguf, google]
        pass
    
    async def restore_primary_provider(self):
        """Restore original provider order."""
        # Restore self.providers to original order
        pass
```

### 4.2 Health State Access

```python
class ModelGateway:
    """Extended with health state query."""
    
    def get_provider_health(self, provider_name: str) -> Dict[str, Any]:
        """Return health status for a specific provider."""
        # Query the maintenance worker for current health
        pass
```

---

## §5 Metrics & Observability

### 5.1 Events to Track

| Event Type | When | Data |
|------------|------|------|
| `gemma.health_check` | Every health check | latency_ms, available, error_type |
| `gemma.quota_warning` | Quota usage > 75% | rpm_percent, rpd_percent |
| `gemma.quota_critical` | Quota usage > 95% | rpm_percent, rpd_percent |
| `gemma.warmup_ping` | Every warm-up ping | success, latency_ms |
| `gemma.failover_triggered` | Failover activated | reason, backup_provider |
| `gemma.recovery_success` | Primary restored | elapsed_seconds |
| `gemma.request_failure` | Inference request fails | error, provider |

### 5.2 Metrics Dashboard

| Metric | Source | Target |
|--------|--------|--------|
| `gemma.availability` | HealthMonitor | > 99% |
| `gemma.latency_p50` | HealthMonitor | < 2000ms |
| `gemma.latency_p95` | HealthMonitor | < 5000ms |
| `gemma.error_rate` | HealthMonitor | < 1% |
| `gemma.quota_rpm_percent` | QuotaTracker | < 75% sustained |
| `gemma.failover_count` | FailoverController | < 1/day |

---

## §6 Configuration Schema

Add to `config/omega.yaml`:

```yaml
omega:
  # ... existing config ...
  
  gemma_maintenance:
    enabled: true
    model: gemma-4-31b-it
    
    health_monitor:
      check_interval_seconds: 60
      timeout_seconds: 10
      failure_threshold: 3
    
    quota_tracker:
      warn_threshold_percent: 75
      critical_threshold_percent: 95
      check_interval_seconds: 300
    
    warmup_manager:
      enabled: true
      ping_interval_seconds: 180
    
    failover:
      enabled: true
      max_consecutive_failures: 3
      cooldown_seconds: 300
      backup_priority: openrouter,lmster,ollama
    
    observability:
      log_events: true
      metrics_interval_seconds: 60
```

---

## §7 Code Skeleton — Main Worker Class

```python
# src/omega/oracle/gemma_maintenance_worker.py

import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import deque

import anyio
import httpx
import yaml
from pathlib import Path

from ..observability import ObservabilityEngine, EventType, get_engine

logger = logging.getLogger(__name__)


class GemmaMaintenanceWorker:
    """Background maintenance worker for Google Gemma models."""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        model_gateway: Optional[Any] = None,
    ):
        # Load config
        if config_path is None:
            config_path = os.environ.get(
                "OMEGA_CONFIG",
                str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"),
            )
        
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f).get("omega", {})
        
        gemma_config = self.config.get("gemma_maintenance", {})
        self.enabled = gemma_config.get("enabled", True)
        
        # Components
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model = gemma_config.get("model", "gemma-4-31b-it")
        
        # Initialize sub-components
        self.health_monitor = HealthMonitor(
            api_key=self.api_key,
            model=self.model,
        )
        self.quota_tracker = QuotaTracker(
            api_key=self.api_key,
        )
        self.warmup_manager = WarmUpManager(
            api_key=self.api_key,
            model=self.model,
            ping_interval=gemma_config.get("warmup_manager", {}).get("ping_interval_seconds", 180),
        )
        self.failover_controller = FailoverController(
            model_gateway=model_gateway,
            max_consecutive_failures=gemma_config.get("failover", {}).get("max_consecutive_failures", 3),
            cooldown_seconds=gemma_config.get("failover", {}).get("cooldown_seconds", 300),
        )
        
        # Observability
        self.observability = get_engine()
        
        # Task tracking
        self._running = False
        self._tasks: List[anyio.TaskGroup] = []
    
    async def start(self):
        """Start the maintenance worker."""
        if not self.enabled:
            logger.info("Gemma maintenance worker disabled")
            return
        
        if not self.api_key:
            logger.warning("No GOOGLE_API_KEY found, worker will not start")
            return
        
        logger.info(f"Starting Gemma maintenance worker for {self.model}")
        self._running = True
        
        # Create task group for background tasks
        async with anyio.create_task_group() as tg:
            # Health check loop
            tg.start_soon(self._health_check_loop)
            
            # Quota check loop
            tg.start_soon(self._quota_check_loop)
            
            # Warmup ping loop
            tg.start_soon(self._warmup_loop)
            
            # Metrics flush loop
            tg.start_soon(self._metrics_loop)
    
    async def stop(self):
        """Stop the maintenance worker."""
        logger.info("Stopping Gemma maintenance worker")
        self._running = False
    
    async def _health_check_loop(self):
        """Periodic health checks."""
        interval = self.config.get("gemma_maintenance", {}).get("health_monitor", {}).get("check_interval_seconds", 60)
        while self._running:
            try:
                status = await self.health_monitor.check_health()
                self.observability.log_event(
                    EventType.ERROR,  # Reusing - could add new type
                    f"trc_{uuid.uuid4().hex[:12]}",
                    {
                        "event": "gemma.health_check",
                        "available": status.available,
                        "latency_ms": status.latency_ms,
                        "error_rate": status.error_rate,
                        "error_type": status.error_type,
                    }
                )
                
                # Update failover controller
                if not status.available:
                    await self.failover_controller.on_request_failure(status.error_type or "health_check_failed")
                else:
                    await self.failover_controller.attempt_recovery()
                    
            except Exception as e:
                logger.error(f"Health check failed: {e}")
            
            await anyio.sleep(interval)
    
    async def _quota_check_loop(self):
        """Periodic quota checks."""
        interval = self.config.get("gemma_maintenance", {}).get("quota_tracker", {}).get("check_interval_seconds", 300)
        while self._running:
            try:
                status = await self.quota_tracker.check_quota()
                
                if status.rpm_warning:
                    logger.warning(f"Gemma quota warning: {status.rpm_percent:.1f}% RPM")
                    self.observability.log_event(
                        EventType.ERROR,
                        f"trc_{uuid.uuid4().hex[:12]}",
                        {"event": "gemma.quota_warning", "rpm_percent": status.rpm_percent}
                    )
                
                if status.rpd_warning:
                    logger.warning(f"Gemma quota critical: {status.rpd_percent:.1f}% RPD")
                    self.observability.log_event(
                        EventType.ERROR,
                        f"trc_{uuid.uuid4().hex[:12]}",
                        {"event": "gemma.quota_critical", "rpd_percent": status.rpd_percent}
                    )
                    
            except Exception as e:
                logger.error(f"Quota check failed: {e}")
            
            await anyio.sleep(interval)
    
    async def _warmup_loop(self):
        """Periodic warmup pings."""
        while self._running:
            try:
                if self.warmup_manager.needs_ping:
                    success = await self.warmup_manager.ping()
                    self.observability.log_event(
                        EventType.ERROR,
                        f"trc_{uuid.uuid4().hex[:12]}",
                        {"event": "gemma.warmup_ping", "success": success}
                    )
            except Exception as e:
                logger.error(f"Warmup ping failed: {e}")
            
            await anyio.sleep(60)  # Check every minute
    
    async def _metrics_loop(self):
        """Periodic metrics flush."""
        interval = self.config.get("gemma_maintenance", {}).get("observability", {}).get("metrics_interval_seconds", 60)
        while self._running:
            try:
                # Log summary metrics
                logger.debug(
                    f"Gemma status: healthy={self.health_monitor.is_healthy}, "
                    f"latency={self.health_monitor.average_latency:.0f}ms, "
                    f"failover_active={self.failover_controller.is_failover_active}"
                )
            except Exception as e:
                logger.error(f"Metrics flush failed: {e}")
            
            await anyio.sleep(interval)
    
    async def on_request_start(self):
        """Called before a request is made to Gemma."""
        await self.quota_tracker.record_request()
    
    async def on_request_end(self, success: bool, error: Optional[str] = None):
        """Called after a request completes."""
        if not success and error:
            await self.failover_controller.on_request_failure(error)


# Singleton instance
_worker: Optional[GemmaMaintenanceWorker] = None


def get_maintenance_worker(
    config_path: Optional[str] = None,
    model_gateway: Optional[Any] = None,
) -> GemmaMaintenanceWorker:
    """Get or create the maintenance worker singleton."""
    global _worker
    if _worker is None:
        _worker = GemmaMaintenanceWorker(config_path, model_gateway)
    return _worker
```

---

## §8 Startup Integration

Add to `src/omega/oracle/oracle.py` or `model_gateway.py`:

```python
# At the end of ModelGateway.__init__ or in oracle startup
from .gemma_maintenance_worker import get_maintenance_worker

# After loading providers
if os.environ.get("OMEGA_ENV") != "test":
    maintenance_worker = get_maintenance_worker(model_gateway=self)
    self.background_worker = maintenance_worker
    
    # Start the worker
    anyio.create_task(maintenance_worker.start())
```

---

## §9 Test Plan

| Test | Description |
|------|-------------|
| `test_health_check_success` | Mock API returns 200 → health = healthy |
| `test_health_check_rate_limit` | Mock API returns 429 → health = rate_limited |
| `test_health_check_timeout` | Mock timeout → health = timeout |
| `test_quota_tracking` | Track 30 requests → rpm_percent = 100% |
| `test_quota_warning` | 75% usage → warning logged |
| `test_failover_trigger` | 3 consecutive failures → failover activated |
| `test_failover_recovery` | After cooldown → primary restored |
| `test_warmup_ping` | Ping succeeds → last_ping_success = True |

---

## §10 Configuration Summary

| Config Path | Default | Description |
|-------------|---------|-------------|
| `gemma_maintenance.enabled` | `true` | Enable/disable worker |
| `gemma_maintenance.model` | `gemma-4-31b-it` | Model to monitor |
| `health_monitor.check_interval_seconds` | `60` | Health check frequency |
| `health_monitor.timeout_seconds` | `10` | API call timeout |
| `health_monitor.failure_threshold` | `3` | Failures before failover |
| `quota_tracker.warn_threshold_percent` | `75` | Warning threshold |
| `quota_tracker.critical_threshold_percent` | `95` | Critical threshold |
| `warmup_manager.ping_interval_seconds` | `180` | Warmup ping frequency |
| `failover.max_consecutive_failures` | `3` | Failures to trigger failover |
| `failover.cooldown_seconds` | `300` | Recovery cooldown |

---

## §11 Related Documents

| Document | Purpose |
|----------|---------|
| `GOOGLE_GEMMA_MODEL_REFERENCE.md` | Gemma API reference, rate limits |
| `R04_fallback_chain_design.md` | Provider fallback strategy |
| `R06_circuit_breaker_policy.md` | Circuit breaker patterns |
| `src/omega/oracle/model_gateway.py` | Provider fabric implementation |
| `src/omega/oracle/providers.py` | GoogleAIProvider implementation |
| `src/omega/observability.py` | Event logging system |

---

## §12 Key URLs

| Resource | URL |
|----------|-----|
| Google AI Studio | https://aistudio.google.com |
| API Key Management | https://aistudio.google.com/app/apikey |
| Rate Limits Docs | https://ai.google.dev/gemini-api/docs/rate-limits |
| Gemma on Gemini API | https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api |
| API Reference | https://ai.google.dev/api |

---

*Maintained by: OpenCode CLI (Sovereign Architect)*
*Next update: Upon implementation completion*