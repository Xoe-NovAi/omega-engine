#!/usr/bin/env python3
# ⬡ OMEGA ⬡ CARMACK PROFILER ⬡ BENCHMARK RUNNER ⬡ 2026-07-01
# Loadable benchmark harness for profiling engine subsystems without live inference.
# Invoked by: make profile-context-builder, make profile-model-gateway
# Requires PYTHONPATH=src or appropriate sys.path setup.

import sys
import anyio


async def benchmark_context_builder():
    """Profile ContextBuilder memory assembly without live inference."""
    from omega.memory_store import get_memory_store
    from omega.oracle.context_builder import ContextBuilder

    store = get_memory_store()
    builder = ContextBuilder()

    entity = "profile-entity"
    session = "profile-bench"
    for i in range(20):
        await store.add_exchange(
            entity_name=entity,
            session_id=session,
            user_message=f"User message {i}",
            response=f"Assistant response {i}",
        )

    for i in range(5):
        ctx = await builder.build_context(
            entity_name=entity,
            session_id=session,
        )
    print(f"ContextBuilder: 5 assemblies on {entity}/{session}")


async def benchmark_model_gateway():
    """Profile HealthMonitor circuit breaker culling (BSP-style)."""
    from omega.oracle.health_monitor import get_health_monitor

    health = get_health_monitor()
    models = ["qwen3-1.7b", "qwen3-4b-think", "deepseek-r1-8b", "phi-2", "krikri-8b"]

    # Set model-provider mappings
    for model in models:
        health.set_model_provider(model, "mock-provider")

    # Record probe results (simulate 200 probe cycles per model)
    for model in models:
        for i in range(200):
            if i < 180:
                health.record_success(model)
                health.record_latency(model, 50.0)
            else:
                health.record_failure(model)
                health.record_latency(model, 5000.0)

    # Run availability checks (the hot path culling)
    for model in models:
        for _ in range(100):
            _ = health.is_available(model)

    # Run success rate checks
    for model in models:
        _ = health.get_success_rate(model)

    print(f"ModelGateway: 5 models × 200 probes + 500 checks + 5 success rates")


BENCHMARKS = {
    "context-builder": benchmark_context_builder,
    "model-gateway": benchmark_model_gateway,
}


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <{'|'.join(BENCHMARKS.keys())}>")
        sys.exit(1)

    mode = sys.argv[1]
    if mode not in BENCHMARKS:
        print(f"Unknown benchmark: {mode}")
        print(f"Available: {', '.join(BENCHMARKS.keys())}")
        sys.exit(1)

    print(f"CARMACK PROFILER BENCHMARK: {mode}")
    anyio.run(BENCHMARKS[mode])
    print("BENCHMARK COMPLETE")


if __name__ == "__main__":
    main()
