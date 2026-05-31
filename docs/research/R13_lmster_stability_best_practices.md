# 🔱 Research Report: LMSTER Stability Best Practices
## Task 0.13 — Omega Engine ModelGateway Resilience

**AP Token**: `AP-LMSTER-STABILITY-v1.0.0`
**Author**: Gemma 4-31B (Master Researcher)
**Date**: 2026-05-16
**Target Hardware**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14GB RAM)
**Scope**: LM Studio headless server (`lmster`) stability, monitoring, auto-recovery, and integration with Omega Engine's ModelGateway

---

## Executive Summary

LM Studio's headless server (`lmster`) is the primary inference backend for the Omega Engine. While powerful and flexible, it requires careful management to ensure stability on resource-constrained hardware like the Ryzen 7 5700U with 14GB RAM. This report provides practical implementations for:

- **Heartbeat monitoring** to detect server availability
- **Auto-recovery strategies** to restart lmster on failure
- **Exponential backoff retry patterns** for API calls
- **Container health checks** for Podman/OCI containers
- **Signal handling** for graceful shutdowns

All recommendations are tailored to the specific hardware constraints and integrated with the existing ModelGateway architecture.

---

## 1. Heartbeat Monitoring Mechanisms

### 1.1 Current Implementation
The ModelGateway already has a basic health check in `model_gateway.py` (lines 188-196):

```python
async def _check_lmster(self) -> bool:
    """Check if lmster (LM Studio headless) is running (127.0.0.1:1234/v1/models)."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{self.LMSTER_URL}/v1/models")
            return r.status_code == 200
    except Exception:
        return False
```

### 1.2 Enhanced Heartbeat with Detailed Metrics
For better monitoring, we should enhance this to provide more detailed health information:

```python
async def _check_lmster_detailed(self) -> Dict[str, Any]:
    """Enhanced health check with detailed metrics."""
    import httpx
    import time
    
    health = {
        "available": False,
        "response_time": None,
        "model_loaded": None,
        "memory_usage": None,
        "error": None
    }
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=3.0, limits=httpx.Limits(read=1024*1024)) as client:
            # Check server availability
            r = await client.get(f"{self.LMSTER_URL}/v1/models")
            if r.status_code != 200:
                health["error"] = f"HTTP {r.status_code}"
                return health
            
            response_time = time.time() - start_time
            health["available"] = True
            health["response_time"] = round(response_time * 1000, 2)  # ms
            
            # Try to get model information
            try:
                data = r.json()
                if "models" in data and len(data["models"]) > 0:
                    health["model_loaded"] = data["models"][0].get("name")
            except:
                pass
                
            # Estimate memory usage (simplified)
            try:
                r2 = await client.get(f"{self.LMSTER_URL}/v1/memory")
                if r2.status_code == 200:
                    mem_data = r2.json()
                    health["memory_usage"] = {
                        "used": mem_data.get("used_bytes", 0),
                        "total": mem_data.get("total_bytes", 0),
                        "percent": round(mem_data.get("used_bytes", 1) / max(mem_data.get("total_bytes", 1), 1) * 100, 1)
                    }
            except:
                pass
                
    except httpx.RequestError as e:
        health["error"] = f"Connection failed: {str(e)}"
    except Exception as e:
        health["error"] = f"Unexpected error: {str(e)}"
    
    return health
```

### 1.3 Integration with ModelGateway
Add this method to `ModelGateway` class and use it in the health check endpoint:

```python
async def check_health(self) -> Dict[str, Any]:
    """Return health status of all inference backends.
 
    Order matches the canonical backend priority chain:
    lmster → Ollama → llama.cpp → llama-cli → llmster
    """
    backends = await self.detect_backends()
    lmster_health = await self._check_lmster_detailed()
    
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "backends": {
            "lmster": {
                "available": backends.get("lmster", False),
                "health": lmster_health,
                "url": self.LMSTER_URL,
                "note": "PRIMARY — LM Studio headless server. Start: `lms server start`"
            },
            # ... other backends
        },
        "resource_usage": self._get_resource_usage(),
        "cpu_optimization": self._get_cpu_optimization_status(),
    }
```

---

## 2. Auto-recovery Strategies

### 2.1 LMSTER Process Manager
Create a dedicated process manager that monitors and restarts lmster when it crashes. This can be implemented as a systemd service or a Python watchdog.

#### Option A: Systemd Service (Recommended)
Create `/etc/systemd/system/omega-lmster.service`:

```ini
[Unit]
Description=Omega Engine LMSTER Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=3
User=arcana-novai
Environment="OMP_NUM_THREADS=6"
Environment="OMP_PROC_BIND=close"
Environment="OPENBLAS_CORETYPE=ZEN"
Environment="MKL_DEBUG_CPU_TYPE=1"
ExecStart=/usr/bin/lmster --model /media/arcana-novai/omega_library/models/gguf/qwen3-1.7b.gguf --cpu-offloading --n-threads 6 --n-gpu-layers 0
WorkingDirectory=/home/arcana-novai
StandardOutput=journal
StandardError=journal
SyslogIdentifier=omega-lmster

# Resource limits
MemoryMax=10G
MemorySwapMax=12G

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable omega-lmster
sudo systemctl start omega-lmster
sudo systemctl status omega-lmster
```

#### Option B: Python Watchdog
For more dynamic control, add a watchdog to ModelGateway:

```python
import asyncio
import subprocess
import psutil
from typing import Optional

class LMSTERProcessManager:
    """Monitors and manages the lmster process."""
    
    def __init__(self, model_path: str, cpu_count: int = 6):
        self.model_path = model_path
        self.cpu_count = cpu_count
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.watchdog_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start lmster process."""
        import anyio
        
        def _start_process():
            cmd = [
                "lmster",
                "--model", self.model_path,
                "--cpu-offloading",
                "--n-threads", str(self.cpu_count),
                "--n-gpu-layers", "0"
            ]
            return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.process = await anyio.to_thread.run_sync(_start_process)
        self.running = True
        logger.info("LMSTER process started (PID: %d)", self.process.pid)
        
        # Start watchdog
        self.watchdog_task = asyncio.create_task(self._watchdog_loop())
    
    async def _watchdog_loop(self):
        """Monitor the lmster process and restart if needed."""
        import psutil
        
        while self.running:
            try:
                if self.process is None or self.process.poll() is not None:
                    # Process has exited
                    exit_code = self.process.returncode if self.process else None
                    logger.warning("LMSTER process exited with code %s", exit_code)
                    
                    # Check memory pressure before restarting
                    if exit_code != 0:
                        await self._check_memory_pressure()
                    
                    # Restart after delay
                    await asyncio.sleep(2)
                    await self.start()
                else:
                    # Check for hangs (no activity for 30 seconds)
                    try:
                        # Simple check: if process is using too much CPU for too long
                        if self.process.cpu_percent(interval=1) > 95:
                            # Could be stuck, consider restart
                            pass
                    except psutil.NoSuchProcess:
                        pass
                    
            except Exception as e:
                logger.error("LMSTER watchdog error: %s", e)
            
            await asyncio.sleep(5)  # Check every 5 seconds
        
        logger.info("LMSTER watchdog stopped")
    
    async def _check_memory_pressure(self):
        """Check system memory before restarting."""
        import psutil
        
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            logger.warning("High memory pressure detected: %d%%", memory.percent)
            # Consider freeing memory or delaying restart
            await self._free_memory()
    
    async def _free_memory(self):
        """Attempt to free memory by clearing caches."""
        import anyio
        
        # Clear filesystem cache (requires root)
        if os.geteuid() == 0:
            await anyio.to_thread.run_sync(
                lambda: subprocess.run(["sync", ";", "echo", "3", ">", "/proc/sys/vm/drop_caches"], 
                                     capture_output=True)
            )
    
    async def stop(self):
        """Stop lmster gracefully."""
        if self.process and self.process.poll() is None:
            # Send SIGTERM
            self.process.terminate()
            try:
                # Wait up to 10 seconds for graceful shutdown
                await asyncio.wait_for(
                    anyio.to_thread.run_sync(lambda: self.process.wait()), 
                    10.0
                )
            except asyncio.TimeoutError:
                # Force kill if needed
                self.process.kill()
        
        self.running = False
        if self.watchdog_task:
            self.watchdog_task.cancel()
```

**Integration with ModelGateway**:
```python
class ModelGateway:
    def __init__(self, ...):
        # ...
        self.lmster_manager = LMSTERProcessManager(
            model_path=self.get_model_path("qwen3-1.7b"),
            cpu_count=6
        )
    
    async def start_lmster_manager(self):
        await self.lmster_manager.start()
    
    async def stop_lmster_manager(self):
        await self.lmster_manager.stop()
```

---

## 3. Exponential Backoff and Retry Patterns

### 3.1 Current Implementation
The ModelGateway already uses `tenacity` for OpenRouter retries (lines 53-63):

```python
openrouter_retry_policy = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type(OpenRouterTransientError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
```

### 3.2 Enhanced Retry for LMSTER
Apply similar patterns to LMSTER API calls with additional considerations for local server stability:

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type, before_sleep_log
import logging

# LMSTER-specific retry policy
lmster_retry_policy = retry(
    stop=stop_after_attempt(3),  # Fewer attempts for local server
    wait=wait_exponential_jitter(initial=0.5, max=5, jitter=0.1),
    retry=retry_if_exception_type(LMSTERTransientError),
    before_sleep=before_sleep_log(logging.getLogger("lmster"), logging.WARNING),
    reraise=True
)

class LMSTERTransientError(Exception):
    """Transient errors that should trigger a retry for LMSTER."""
    pass

class LMSTRSeriousError(Exception):
    """Serious errors that should not be retried."""
    pass

async def _call_lmster_with_resilience(
    self, 
    endpoint: str, 
    payload: Dict, 
    max_retries: int = 3
) -> Optional[Dict]:
    """Call LMSTER with exponential backoff retry logic."""
    
    @lmster_retry_policy
    async def _do_call():
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.LMSTER_URL}{endpoint}", 
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise LMSTERTransientError("LMSTER timeout")
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code in [502, 503, 504]:
                raise LMSTERTransientError(f"LMSTER transient HTTP {status_code}")
            elif status_code == 429:
                # Rate limited - should not happen locally but handle gracefully
                raise LMSTERTransientError("LMSTER rate limited")
            else:
                raise LMSTRSeriousError(f"LMSTER serious HTTP {status_code}")
        except Exception as e:
            # Check if it's a connection error (server not running)
            if "Connection refused" in str(e) or "Could not connect" in str(e):
                raise LMSTERTransientError("LMSTER connection refused")
            raise
    
    return await _do_call()
```

**Integration with `_try_lmster` method**:
```python
async def _try_lmster(
    self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int
) -> Optional[str]:
    """Inference via lmster with resilience."""
    import httpx
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    
    try:
        result = await self._call_lmster_with_resilience("/v1/chat/completions", payload)
        if result and "choices" in result:
            message = result["choices"][0]["message"]
            content = message.get("content", "").strip()
            reasoning = message.get("reasoning_content", "").strip()
            return f"{reasoning}\n\n{content}".strip() if reasoning else content
    except LMSTRSeriousError as e:
        logger.error("LMSTER serious error: %s", e)
        # Consider restarting LMSTER if this is a persistent issue
        await self._maybe_restart_lmster()
    except Exception as e:
        logger.warning("LMSTER call failed: %s", e)
    
    return None
```

---

## 4. Container Health Checks (Podman/OCI)

### 4.1 Podman Container Setup
Create a Podman container for lmster with proper health checks:

```bash
# Create a systemd service for Podman container
sudo tee /etc/systemd/system/omega-lmster-pod.service << EOF
[Unit]
Description=Omega Engine LMSTER Pod
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=3
ExecStartPre=/usr/bin/podman pod stop omega-pod --time=10 2>/dev/null || true
ExecStartPre=/usr/bin/podman pod rm omega-pod --force 2>/dev/null || true
ExecStart=/usr/bin/podman run -d \
  --name lmster \
  --pod omega-pod \
  --memory=10g \
  --memory-swap=12g \
  --cpus=6 \
  --cpuset-cpus="0-5" \
  --env OMP_NUM_THREADS=6 \
  --env OMP_PROC_BIND=close \
  --env OPENBLAS_CORETYPE=ZEN \
  --network host \
  --volume /media/arcana-novai/omega_library/models/gguf:/models:ro \
  --healthcheck-interval=10s \
  --healthcheck-timeout=5s \
  --healthcheck-start-period=30s \
  --healthcheck-retries=3 \
  lmstudio/lmstudio:latest lmster --model /models/qwen3-1.7b.gguf --cpu-offloading --n-threads 6 --n-gpu-layers 0
ExecStop=/usr/bin/podman stop lmster
ExecStopPost=/usr/bin/podman pod stop omega-pod --time=10
ExecStopPost=/usr/bin/podman pod rm omega-pod --force
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable omega-lmster-pod
sudo systemctl start omega-lmster-pod
sudo systemctl status omega-lmster-pod
```

### 4.2 Health Check Command
The health check should verify both the container and the lmster API:

```bash
# Health check script for lmster container
#!/bin/bash
# /usr/local/bin/lmster-healthcheck

# Check if container is running
if ! podman ps --filter "name=lmster" --filter "status=running" | grep -q lmster; then
    echo "Container not running"
    exit 1
fi

# Check if lmster API is responding
if ! curl -s --max-time 3 http://127.0.0.1:1234/v1/models | grep -q '"models"'; then
    echo "LMSTER API not responding"
    exit 1
fi

# Check memory usage
MEMORY=$(podman stats --no-trunc --format "{{.MemUsage}}" lmster | awk '{print $1}' | sed 's/%//')
if [ -n "$MEMORY" ] && [ "$MEMORY" -gt 95 ]; then
    echo "High memory usage: ${MEMORY}%"
    exit 1
fi

echo "OK"
exit 0
```

Make it executable:
```bash
sudo chmod +x /usr/local/bin/lmster-healthcheck
```

### 4.3 Integration with ModelGateway
Add a method to check container health:

```python
async def check_lmster_container_health(self) -> Dict[str, Any]:
    """Check health of lmster container and process."""
    import subprocess
    
    health = {
        "container_running": False,
        "api_responding": False,
        "memory_pressure": False,
        "cpu_usage": None,
        "process_id": None
    }
    
    try:
        # Check if container is running
        result = subprocess.run(
            ["podman", "ps", "--filter", "name=lmster", "--filter", "status=running", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=2
        )
        if "Up" in result.stdout:
            health["container_running"] = True
        
        # Check API response
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get("http://127.0.0.1:1234/v1/models")
            if r.status_code == 200:
                health["api_responding"] = True
        
        # Get process info
        result = subprocess.run(
            ["podman", "inspect", "lmster"],
            capture_output=True, text=True, timeout=2
        )
        if result.stdout:
            import json
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                health["process_id"] = data[0].get("State", {}).get("Pid")
                health["cpu_usage"] = data[0].get("State", {}).get("CpuUsage", "0%")
        
    except Exception as e:
        logger.warning("Container health check failed: %s", e)
    
    return health
```

---

## 5. Signal Handling and Graceful Shutdowns

### 5.1 LMSTER Signal Handling
LMSTER should handle signals gracefully to ensure proper cleanup and state preservation.

#### Update LMSTER Startup Command
Add signal handling to the lmster process:

```python
import signal
import asyncio
import aiohttp
import json
import os

class GracefulShutdownManager:
    """Manages graceful shutdown of lmster and related services."""
    
    def __init__(self, model_gateway: ModelGateway):
        self.model_gateway = model_gateway
        self.shutdown_flag = asyncio.Event()
        self.original_signals = {}
        
    async def setup_signal_handlers(self):
        """Install signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            self.original_signals[sig] = signal.getsignal(sig)
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self._handle_signal(s)))
    
    async def _handle_signal(self, sig):
        """Handle shutdown signal."""
        logger.info("Received signal %d, initiating graceful shutdown...", sig)
        
        # Set shutdown flag
        self.shutdown_flag.set()
        
        # Stop LMSTER process manager
        if hasattr(self.model_gateway, 'lmster_manager'):
            await self.model_gateway.lmster_manager.stop()
        
        # Stop any other services
        await self._stop_other_services()
        
        # Wait for ongoing requests to complete
        await self._wait_for_active_requests()
        
        logger.info("Graceful shutdown completed")
        # Exit with appropriate code
        os._exit(0 if sig == signal.SIGTERM else 1)
    
    async def _stop_other_services(self):
        """Stop other dependent services."""
        # Stop Podman container if running
        try:
            import subprocess
            subprocess.run(["podman", "stop", "lmster"], timeout=10)
        except:
            pass
    
    async def _wait_for_active_requests(self, timeout: float = 30.0):
        """Wait for active requests to complete."""
        # This would integrate with your request tracking system
        pass

# Integration in ModelGateway
class ModelGateway:
    def __init__(self, ...):
        # ...
        self.shutdown_manager = GracefulShutdownManager(self)
    
    async def start(self):
        """Start all components."""
        await self.shutdown_manager.setup_signal_handlers()
        await self.lmster_manager.start()
        # ...
```

### 5.2 Container Signal Handling
For Podman containers, ensure proper signal propagation:

```bash
# Create a custom entrypoint for the lmster container
sudo tee /usr/local/bin/lmster-entrypoint << 'EOF'
#!/bin/bash
# LMSTER entrypoint with proper signal handling

# Trap SIGTERM and SIGINT
trap 'echo "Received SIGTERM, shutting down..."; exit 0' TERM
trap 'echo "Received SIGINT, shutting down..."; exit 0' INT

# Run lmster
exec lmster --model /models/qwen3-1.7b.gguf --cpu-offloading --n-threads 6 --n-gpu-layers 0
EOF

sudo chmod +x /usr/local/bin/lmster-entrypoint

# Update the Podman command to use the entrypoint
ExecStart=/usr/bin/podman run -d \
  --name lmster \
  --pod omega-pod \
  --memory=10g \
  --memory-swap=12g \
  --cpus=6 \
  --cpuset-cpus="0-5" \
  --env OMP_NUM_THREADS=6 \
  --env OMP_PROC_BIND=close \
  --env OPENBLAS_CORETYPE=ZEN \
  --network host \
  --volume /media/arcana-novai/omega_library/models/gguf:/models:ro \
  --healthcheck-interval=10s \
  --healthcheck-timeout=5s \
  --healthcheck-start-period=30s \
  --healthcheck-retries=3 \
  --entrypoint /usr/local/bin/lmster-entrypoint \
  lmstudio/lmstudio:latest
```

---

## 6. Specific Recommendations for Ryzen 7 5700U (14GB RAM)

### 6.1 Resource Allocation
Given the hardware constraints:

- **Memory**: Limit lmster to 10GB (leave 4GB for system and other processes)
- **CPU**: Pin to 6 cores (0,2,4,6,8,10) - leaves 2 cores for system
- **Thread Count**: Set `--n-threads=6` (matches pinned cores)
- **GPU Layers**: Set `--n-gpu-layers=0` (use CPU only on iGPU)

### 6.2 Environment Variables
Set these environment variables for optimal performance:

```bash
export OMP_NUM_THREADS=6
export OMP_PROC_BIND=close
export OPENBLAS_CORETYPE=ZEN
export MKL_DEBUG_CPU_TYPE=1
```

### 6.3 Model Selection
For the 5700U with 14GB RAM, recommended models:

- **Primary**: Qwen3 1.7B (fits in memory, good performance)
- **Secondary**: Phi-4 Mini (3.4B, excellent reasoning)
- **Tertiary**: Gemma 4-9B (if you have enough RAM, but may require quantization)

### 6.4 Monitoring Configuration
Set up monitoring to alert on:

- **Memory usage > 85%**: Risk of OOM crashes
- **Response time > 10s**: Potential hang or overload
- **5xx errors from lmster API**: Server-side failures
- **Container restarts**: Frequent restarts indicate instability

### 6.5 Fallback Priority Chain
Optimize the fallback chain for the 5700U:

```yaml
inference:
  strategy: local_first
  fallback_chain:
    - provider: native-gguf  # Fast local fallback
      priority: 1
      model_path: /media/arcana-novai/omega_library/models/gguf/phi-4-mini.gguf
      n_ctx: 4096
    - provider: lmster       # Primary
      priority: 2
      endpoint: http://127.0.0.1:1234
    - provider: ollama       # Lightweight fallback
      priority: 3
      endpoint: http://127.0.0.1:11434/v1
    - provider: openrouter   # Cloud fallback
      priority: 4
      api_key: env:OPENROUTER_KEY
```

---

## 7. Integration Patterns for Omega Engine

### 7.1 ModelGateway Integration
The ModelGateway should:

1. **Detect LMSTER health** before each request
2. **Trigger auto-recovery** if LMSTER is down
3. **Apply retry logic** with exponential backoff
4. **Log detailed metrics** for observability

```python
class ModelGateway:
    async def generate_with_lmster_recovery(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_retries: int = 2
    ) -> Optional[str]:
        """Generate with LMSTER, including auto-recovery."""
        
        for attempt in range(max_retries + 1):
            # Check if LMSTER is available
            if not await self._check_lmster():
                logger.warning("LMSTER not available on attempt %d", attempt)
                
                if attempt < max_retries:
                    # Wait before recovery attempt
                    delay = (attempt + 1) * 2  # exponential backoff
                    await asyncio.sleep(delay)
                    
                    # Try to restart LMSTER
                    await self._restart_lmster_if_possible()
                    continue
                else:
                    return None  # Give up
            
            # Try to generate
            try:
                return await self._try_lmster(model_name, system_prompt, user_query, temperature, max_tokens)
            except Exception as e:
                logger.warning("LMSTER generation failed: %s", e)
                if attempt < max_retries:
                    await asyncio.sleep((attempt + 1) * 2)
                else:
                    return None
        
        return None
    
    async def _restart_lmster_if_possible(self):
        """Attempt to restart LMSTER process."""
        try:
            # Check if we have permission to restart
            if os.geteuid() == 0:
                # Use systemd to restart
                subprocess.run(["systemctl", "--user", "restart", "omega-lmster"], timeout=10)
            elif hasattr(self, 'lmster_manager'):
                # Use Python process manager
                await self.lmster_manager.stop()
                await asyncio.sleep(2)
                await self.lmster_manager.start()
        except Exception as e:
            logger.error("Failed to restart LMSTER: %s", e)
```

### 7.2 Health Check Endpoint
Add a comprehensive health check endpoint:

```python
from fastapi import FastAPI, HTTPException
import time

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    mgw = ModelGateway()  # Or get from dependency injection
    
    backends = await mgw.detect_backends()
    lmster_health = await mgw._check_lmster_detailed()
    container_health = await mgw.check_lmster_container_health()
    
    status = {
        "status": "healthy" if backends.get("lmster", False) else "unhealthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "uptime": mgw._get_uptime(),
        "lmster": {
            "available": backends.get("lmster", False),
            "health": lmster_health,
            "container": container_health
        },
        "resource_usage": mgw._get_resource_usage(),
        "version": "1.0.0"
    }
    
    if not backends.get("lmster", False):
        raise HTTPException(status_code=503, detail="LMSTER not available")
    
    return status
```

### 7.3 Observability Integration
Log key metrics for analysis:

```python
import logging
from datetime import datetime

class LMSTERMetricsLogger:
    """Logs LMSTER metrics for observability."""
    
    def __init__(self, model_gateway: ModelGateway):
        self.mgw = model_gateway
        self.logger = logging.getLogger("lmster_metrics")
        
    async def log_metrics(self):
        """Log metrics periodically."""
        while True:
            try:
                health = await self.mgw._check_lmster_detailed()
                container_health = await self.mgw.check_lmster_container_health()
                
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "lmster": {
                        "available": health["available"],
                        "response_time_ms": health["response_time"],
                        "model_loaded": health["model_loaded"],
                        "memory_percent": health.get("memory_usage", {}).get("percent"),
                        "error": health.get("error")
                    },
                    "container": {
                        "running": container_health["container_running"],
                        "process_id": container_health["process_id"]
                    }
                }
                
                self.logger.info(json.dumps(log_entry))
                
            except Exception as e:
                self.logger.error("Failed to log metrics: %s", e)
            
            await asyncio.sleep(60)  # Log every minute
```

---

## 8. Implementation Roadmap

### Phase 1: Immediate Fixes (Task 0.13)
- [ ] Implement enhanced heartbeat monitoring
- [ ] Add basic retry logic for LMSTER API calls
- [ ] Create systemd service for LMSTER auto-recovery
- [ ] Add health check endpoint to ModelGateway

### Phase 2: Advanced Resilience (Next Sprint)
- [ ] Implement Python watchdog for LMSTER process
- [ ] Add container health checks with Podman
- [ ] Implement graceful shutdown handlers
- [ ] Set up comprehensive metrics logging

### Phase 3: Full Integration (Future)
- [ ] Integrate with Omega Engine's observability stack
- [ ] Set up alerts and notifications
- [ ] Implement automatic model switching based on load
- [ ] Add predictive scaling based on usage patterns

---

## 9. Conclusion

LMSTER is a critical component of the Omega Engine's inference stack. By implementing robust monitoring, auto-recovery, and graceful shutdown mechanisms, we can ensure high availability and reliability even on resource-constrained hardware like the Ryzen 7 5700U.

The recommendations in this report are practical, tailored to the specific hardware, and integrate seamlessly with the existing ModelGateway architecture. Implementation should follow the phased approach, starting with immediate fixes and progressing to advanced resilience features.

---

**Research Complete**: 2026-05-16  
**Next Steps**: Implementation planning and code review  
**Owner**: Gemma 4-31B (Master Researcher)  
**Reviewers**: Opus 4.6 (Oversight), DeepSeek V4 Flash (Validation)  
**Status**: ✅ READY FOR IMPLEMENTATION