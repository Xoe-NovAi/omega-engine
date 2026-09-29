# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""R30 Circuit Breaker Benchmark — Live Performance Comparison.
AP: AP-R30-CB-BENCHMARK-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r30 ⬡ ACTIVE

Benchmarks 5 circuit breaker libraries under load:
- pybreaker 1.4.1
- tenacity 9.1.4
- stamina 26.1.0
- pyresilience 0.4.0
- interlock 2.6.0

Metrics: failure detection latency, recovery time, resource overhead, false positive rate.
"""

import time
import gc
import sys
import tracemalloc
import asyncio
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from enum import Enum

# ── Library Imports ──────────────────────────────────────────────
import pybreaker
import tenacity
import stamina
import pyresilience
import interlock


@dataclass
class BenchmarkResult:
    """Results for a single library benchmark."""
    name: str
    version: str
    sync_support: bool
    async_support: bool
    failure_detection_latency_ms: float  # Time from first failure to OPEN state
    recovery_time_ms: float  # Time from service recovery to CLOSED state
    memory_per_instance_kb: float  # Memory overhead per breaker instance
    false_positive_rate: float  # How often opens on transient success
    max_throughput_rps: float  # Requests/sec under load
    notes: str = ""


class FlakyService:
    """Simulates a service with configurable failure rate."""
    def __init__(self, failure_rate: float = 1.0, recover_after: int = None):
        self.failure_rate = failure_rate
        self.recover_after = recover_after
        self.call_count = 0
        self.recovered = False

    def call_sync(self) -> str:
        self.call_count += 1
        if self.recover_after and self.call_count >= self.recover_after:
            self.recovered = True
        if not self.recovered and self.failure_rate > 0:
            raise RuntimeError("Service unavailable")
        return "success"

    async def call_async(self) -> str:
        return self.call_sync()


def benchmark_pybreaker() -> BenchmarkResult:
    """Benchmark pybreaker 1.4.1."""
    # Failure detection latency
    service = FlakyService(failure_rate=1.0)
    breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=5)

    # Measure time to open
    start = time.perf_counter()
    failures = 0
    opened = False
    for _ in range(10):
        try:
            breaker.call(service.call_sync)
        except (pybreaker.CircuitBreakerError, RuntimeError):
            failures += 1
            if failures >= 3:
                opened = True
                break
    detection_latency = (time.perf_counter() - start) * 1000

    # Recovery time
    service2 = FlakyService(failure_rate=1.0, recover_after=5)
    breaker2 = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=1)
    # Open it
    for _ in range(3):
        try:
            breaker2.call(service2.call_sync)
        except:
            pass
    # Wait for reset
    time.sleep(1.1)
    # Now service should recover
    recovery_start = time.perf_counter()
    recovered = False
    for _ in range(10):
        try:
            result = breaker2.call(service2.call_sync)
            if result == "success":
                recovered = True
                break
        except:
            time.sleep(0.1)
    recovery_time = (time.perf_counter() - recovery_start) * 1000

    # Memory overhead
    tracemalloc.start()
    breakers = [pybreaker.CircuitBreaker() for _ in range(100)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mem_per = (peak / 100) / 1024

    # False positive rate: service that succeeds but breaker opens anyway
    service3 = FlakyService(failure_rate=0.0)  # Never fails
    breaker3 = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=5)
    fp_count = 0
    for _ in range(100):
        try:
            breaker3.call(service3.call_sync)
        except pybreaker.CircuitBreakerError:
            fp_count += 1
    fp_rate = fp_count / 100

    # Throughput
    service4 = FlakyService(failure_rate=0.0)
    breaker4 = pybreaker.CircuitBreaker(fail_max=1000, reset_timeout=5)
    start = time.perf_counter()
    for _ in range(10000):
        try:
            breaker4.call(service4.call_sync)
        except:
            pass
    elapsed = time.perf_counter() - start
    throughput = 10000 / elapsed

    return BenchmarkResult(
        name="pybreaker",
        version="1.4.1",
        sync_support=True,
        async_support=False,  # pybreaker is sync-only
        failure_detection_latency_ms=detection_latency,
        recovery_time_ms=recovery_time,
        memory_per_instance_kb=mem_per,
        false_positive_rate=fp_rate,
        max_throughput_rps=throughput,
        notes="Sync-only. M1 violation for async code. No built-in retry/bulkhead."
    )


def benchmark_tenacity() -> BenchmarkResult:
    """Benchmark tenacity 9.1.4 (retry library with circuit breaker pattern)."""
    # Tenacity is primarily a retry library; circuit breaker via stop_after_attempt
    # For CB pattern, we use retry with stop and a custom state
    service = FlakyService(failure_rate=1.0)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(RuntimeError),
        reraise=True
    )
    def protected_call():
        return service.call_sync()

    start = time.perf_counter()
    failures = 0
    for _ in range(10):
        try:
            protected_call()
        except RuntimeError:
            failures += 1
            if failures >= 3:
                break
    detection_latency = (time.perf_counter() - start) * 1000

    # Recovery: tenacity doesn't have native CB state; simulate with stop_after_attempt
    service2 = FlakyService(failure_rate=1.0, recover_after=5)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(10),
        retry=tenacity.retry_if_exception_type(RuntimeError),
        reraise=True
    )
    def protected_call2():
        return service2.call_sync()

    recovery_start = time.perf_counter()
    recovered = False
    try:
        result = protected_call2()
        if result == "success":
            recovered = True
    except RuntimeError:
        pass
    recovery_time = (time.perf_counter() - recovery_start) * 1000

    # Memory
    tracemalloc.start()
    # Tenacity doesn't have persistent breaker objects; use retry decorators
    breakers = [tenacity.retry(stop=tenacity.stop_after_attempt(3)) for _ in range(100)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mem_per = (peak / 100) / 1024

    # False positive
    service3 = FlakyService(failure_rate=0.0)

    @tenacity.retry(stop=tenacity.stop_after_attempt(3), reraise=True)
    def protected_call3():
        return service3.call_sync()

    fp_count = 0
    for _ in range(100):
        try:
            protected_call3()
        except RuntimeError:
            fp_count += 1
    fp_rate = fp_count / 100

    # Throughput
    service4 = FlakyService(failure_rate=0.0)

    @tenacity.retry(stop=tenacity.stop_after_attempt(1), reraise=True)
    def protected_call4():
        return service4.call_sync()

    start = time.perf_counter()
    for _ in range(10000):
        try:
            protected_call4()
        except:
            pass
    elapsed = time.perf_counter() - start
    throughput = 10000 / elapsed

    return BenchmarkResult(
        name="tenacity",
        version="9.1.4",
        sync_support=True,
        async_support=True,
        failure_detection_latency_ms=detection_latency,
        recovery_time_ms=recovery_time,
        memory_per_instance_kb=mem_per,
        false_positive_rate=fp_rate,
        max_throughput_rps=throughput,
        notes="Retry library, not native CB. CB pattern via stop_after_attempt. No sliding window."
    )


def benchmark_stamina() -> BenchmarkResult:
    """Benchmark stamina 26.1.0 (retry with structlog+prometheus)."""
    service = FlakyService(failure_rate=1.0)

    @stamina.retry(on=RuntimeError, attempts=3)
    def protected_call():
        return service.call_sync()

    start = time.perf_counter()
    failures = 0
    for _ in range(10):
        try:
            protected_call()
        except RuntimeError:
            failures += 1
            if failures >= 3:
                break
    detection_latency = (time.perf_counter() - start) * 1000

    # Recovery
    service2 = FlakyService(failure_rate=1.0, recover_after=5)

    @stamina.retry(on=RuntimeError, attempts=10)
    def protected_call2():
        return service2.call_sync()

    recovery_start = time.perf_counter()
    try:
        result = protected_call2()
        recovered = result == "success"
    except RuntimeError:
        recovered = False
    recovery_time = (time.perf_counter() - recovery_start) * 1000

    # Memory
    tracemalloc.start()
    breakers = [stamina.retry(on=RuntimeError, attempts=3) for _ in range(100)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mem_per = (peak / 100) / 1024

    # False positive
    service3 = FlakyService(failure_rate=0.0)

    @stamina.retry(on=RuntimeError, attempts=3)
    def protected_call3():
        return service3.call_sync()

    fp_count = 0
    for _ in range(100):
        try:
            protected_call3()
        except RuntimeError:
            fp_count += 1
    fp_rate = fp_count / 100

    # Throughput
    service4 = FlakyService(failure_rate=0.0)

    @stamina.retry(on=RuntimeError, attempts=1)
    def protected_call4():
        return service4.call_sync()

    start = time.perf_counter()
    for _ in range(10000):
        try:
            protected_call4()
        except:
            pass
    elapsed = time.perf_counter() - start
    throughput = 10000 / elapsed

    return BenchmarkResult(
        name="stamina",
        version="26.1.0",
        sync_support=True,
        async_support=True,
        failure_detection_latency_ms=detection_latency,
        recovery_time_ms=recovery_time,
        memory_per_instance_kb=mem_per,
        false_positive_rate=fp_rate,
        max_throughput_rps=throughput,
        notes="Retry library with free structlog+prometheus. No native CB state machine."
    )


def benchmark_pyresilience() -> BenchmarkResult:
    """Benchmark pyresilience 0.4.0."""
    # pyresilience is a manual state machine: record_failure()/record_success()
    config = pyresilience.CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=5.0,
        success_threshold=2
    )
    service = FlakyService(failure_rate=1.0)
    breaker = pyresilience.CircuitBreaker(config=config)

    # Measure time to open (3 failures → OPEN)
    start = time.perf_counter()
    for _ in range(3):
        try:
            service.call_sync()  # This raises RuntimeError
            breaker.record_success()
        except RuntimeError:
            breaker.record_failure()
    # Check state
    opened = str(breaker.state).upper() == "OPEN"
    detection_latency = (time.perf_counter() - start) * 1000

    # Recovery: after recovery_timeout, allow_request() returns True (HALF_OPEN)
    config2 = pyresilience.CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=1.0,
        success_threshold=2
    )
    service2 = FlakyService(failure_rate=1.0, recover_after=5)
    breaker2 = pyresilience.CircuitBreaker(config=config2)
    # Open it
    for _ in range(3):
        try:
            service2.call_sync()
            breaker2.record_success()
        except RuntimeError:
            breaker2.record_failure()
    # Wait for recovery
    time.sleep(1.1)
    # Now allow_request() should be True (HALF_OPEN)
    recovery_start = time.perf_counter()
    recovered = False
    for _ in range(10):
        if breaker2.allow_request():
            # Service should succeed now
            try:
                result = service2.call_sync()
                breaker2.record_success()
                if result == "success":
                    recovered = True
                    break
            except RuntimeError:
                breaker2.record_failure()
        else:
            time.sleep(0.1)
    recovery_time = (time.perf_counter() - recovery_start) * 1000

    # Memory
    tracemalloc.start()
    breakers = [pyresilience.CircuitBreaker(config=config) for _ in range(100)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mem_per = (peak / 100) / 1024

    # False positive: service never fails, breaker should never open
    service3 = FlakyService(failure_rate=0.0)
    breaker3 = pyresilience.CircuitBreaker(config=config)
    fp_count = 0
    for _ in range(100):
        try:
            service3.call_sync()
            breaker3.record_success()
        except RuntimeError:
            breaker3.record_failure()
        if str(breaker3.state).upper() == "OPEN":
            fp_count += 1
    fp_rate = fp_count / 100

    # Throughput
    service4 = FlakyService(failure_rate=0.0)
    config4 = pyresilience.CircuitBreakerConfig(failure_threshold=100000, recovery_timeout=5.0)
    breaker4 = pyresilience.CircuitBreaker(config=config4)
    start = time.perf_counter()
    for _ in range(10000):
        try:
            service4.call_sync()
            breaker4.record_success()
        except RuntimeError:
            breaker4.record_failure()
    elapsed = time.perf_counter() - start
    throughput = 10000 / elapsed

    return BenchmarkResult(
        name="pyresilience",
        version="0.4.0",
        sync_support=True,
        async_support=True,
        failure_detection_latency_ms=detection_latency,
        recovery_time_ms=recovery_time,
        memory_per_instance_kb=mem_per,
        false_positive_rate=fp_rate,
        max_throughput_rps=throughput,
        notes="Manual state machine API (record_failure/record_success). Native CB with sliding window. Young project (0.4.0)."
    )


def benchmark_interlock() -> BenchmarkResult:
    """Benchmark interlock 2.6.0."""
    service = FlakyService(failure_rate=1.0)

    config = interlock.config.Config(
        wait_duration_in_open=5.0,
        minimum_number_of_calls=3,
        failure_rate_threshold=1.0,  # 100% failures → open
        permitted_calls_in_half_open=1,
        window_type=interlock.window.WindowType.COUNT_BASED,
        window_size=10
    )
    breaker = interlock.CircuitBreaker(name="test", config=config)

    start = time.perf_counter()
    failures = 0
    for _ in range(10):
        try:
            breaker.call(service.call_sync)
        except (interlock.CircuitOpenError, RuntimeError):
            failures += 1
            if failures >= 3:
                break
    detection_latency = (time.perf_counter() - start) * 1000

    # Recovery
    service2 = FlakyService(failure_rate=1.0, recover_after=5)
    config2 = interlock.config.Config(
        wait_duration_in_open=1.0,
        minimum_number_of_calls=3,
        failure_rate_threshold=1.0,
        permitted_calls_in_half_open=1,
        window_type=interlock.window.WindowType.COUNT_BASED,
        window_size=10
    )
    breaker2 = interlock.CircuitBreaker(name="test2", config=config2)
    for _ in range(3):
        try:
            breaker2.call(service2.call_sync)
        except:
            pass
    time.sleep(1.1)
    recovery_start = time.perf_counter()
    recovered = False
    for _ in range(10):
        try:
            result = breaker2.call(service2.call_sync)
            if result == "success":
                recovered = True
                break
        except:
            time.sleep(0.1)
    recovery_time = (time.perf_counter() - recovery_start) * 1000

    # Memory
    tracemalloc.start()
    breakers = [interlock.CircuitBreaker(name=f"mem{i}", config=config) for i in range(100)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mem_per = (peak / 100) / 1024

    # False positive
    service3 = FlakyService(failure_rate=0.0)
    config3 = interlock.config.Config(
        wait_duration_in_open=5.0,
        minimum_number_of_calls=3,
        failure_rate_threshold=1.0,
        permitted_calls_in_half_open=1,
        window_type=interlock.window.WindowType.COUNT_BASED,
        window_size=10
    )
    breaker3 = interlock.CircuitBreaker(name="test3", config=config3)
    fp_count = 0
    for _ in range(100):
        try:
            breaker3.call(service3.call_sync)
        except interlock.CircuitOpenError:
            fp_count += 1
    fp_rate = fp_count / 100

    # Throughput
    service4 = FlakyService(failure_rate=0.0)
    config4 = interlock.config.Config(
        wait_duration_in_open=5.0,
        minimum_number_of_calls=1000,
        failure_rate_threshold=1.0,
        permitted_calls_in_half_open=1,
        window_type=interlock.window.WindowType.COUNT_BASED,
        window_size=10000
    )
    breaker4 = interlock.CircuitBreaker(name="test4", config=config4)
    start = time.perf_counter()
    for _ in range(10000):
        try:
            breaker4.call(service4.call_sync)
        except:
            pass
    elapsed = time.perf_counter() - start
    throughput = 10000 / elapsed

    return BenchmarkResult(
        name="interlock",
        version="2.6.0",
        sync_support=True,
        async_support=True,
        failure_detection_latency_ms=detection_latency,
        recovery_time_ms=recovery_time,
        memory_per_instance_kb=mem_per,
        false_positive_rate=fp_rate,
        max_throughput_rps=throughput,
        notes="Full pipeline: timeout, bulkhead, breaker, retry, fallback. Sync+async. Sliding window. Mature (2.6.0)."
    )


def main():
    """Run all benchmarks and print results."""
    print("=" * 80)
    print("R30 CIRCUIT BREAKER BENCHMARK — LIVE RESULTS")
    print("=" * 80)
    print(f"Python: {sys.version}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []
    benchmarks = [
        ("pybreaker", benchmark_pybreaker),
        ("tenacity", benchmark_tenacity),
        ("stamina", benchmark_stamina),
        ("pyresilience", benchmark_pyresilience),
        ("interlock", benchmark_interlock),
    ]

    for name, func in benchmarks:
        print(f"Running {name} benchmark...")
        try:
            result = func()
            results.append(result)
            print(f"  ✓ {name} complete")
        except Exception as e:
            print(f"  ✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
        gc.collect()

    # Print summary table
    print()
    print("=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Library':<15} {'Ver':<8} {'Sync':<5} {'Async':<6} {'Detect(ms)':<12} {'Recov(ms)':<11} {'Mem(KB)':<9} {'FP%':<6} {'RPS':<8}")
    print("-" * 80)
    for r in results:
        print(f"{r.name:<15} {r.version:<8} {str(r.sync_support):<5} {str(r.async_support):<6} "
              f"{r.failure_detection_latency_ms:<12.2f} {r.recovery_time_ms:<11.2f} "
              f"{r.memory_per_instance_kb:<9.2f} {r.false_positive_rate*100:<6.1f} {r.max_throughput_rps:<8.0f}")

    print()
    print("=" * 80)
    print("DETAILED NOTES")
    print("=" * 80)
    for r in results:
        print(f"\n{r.name} {r.version}:")
        print(f"  {r.notes}")

    # Save results to JSON
    import json
    output = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "python_version": sys.version,
        "results": [
            {
                "name": r.name,
                "version": r.version,
                "sync_support": r.sync_support,
                "async_support": r.async_support,
                "failure_detection_latency_ms": r.failure_detection_latency_ms,
                "recovery_time_ms": r.recovery_time_ms,
                "memory_per_instance_kb": r.memory_per_instance_kb,
                "false_positive_rate": r.false_positive_rate,
                "max_throughput_rps": r.max_throughput_rps,
                "notes": r.notes
            }
            for r in results
        ]
    }
    with open('/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/researcher/workspace/research_reports/R30_CB_BENCHMARK_RESULTS_20260813.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: R30_CB_BENCHMARK_RESULTS_20260813.json")


if __name__ == "__main__":
    main()
