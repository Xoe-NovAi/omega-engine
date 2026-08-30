#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Test potion-mxbai-micro vs MiniLM embedding models.

⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ BENCHMARK ⬡ P1-GAP-CLOSURE

Benchmarks two local embedding approaches:
  1. MiniLM (all-MiniLM-L6-v2-f16.gguf via llama-cpp-python, 384-dim)
  2. potion-mxbai-micro (via model2vec, static precomputed embeddings)

This is an EXPERIMENT — results inform the H2-H (Sovereign Metadata)
and H2-S (Provider-Agnostic Embedding Layer) decisions.
"""

import json
import os
import sys
import time
from pathlib import Path

# Config
MINILM_PATH = "/media/arcana-novai/omega_library/models/gguf/all-MiniLM-L6-v2-Q4_K_M.gguf"
POTION_MODEL_FULL = "blobbybob/potion-mxbai-micro"  # 768-dim, higher quality
POTION_MODEL_TINY = "minishlab/potion-base-2M"      # 64-dim, fastest (~2MB)
N_ITERATIONS = 5

TEST_SENTENCES = [
    "The Omega Engine is a sovereign AI framework for local-first intelligence.",
    "Embedding models convert text into fixed-size vectors for semantic search.",
    "The quick brown fox jumps over the lazy dog near the bank of the river.",
    "What is the meaning of sovereignty in the context of artificial intelligence?",
    "Podman containers provide rootless isolation for secure service deployment.",
    "All-MiniLM-L6-v2 is a sentence embedding model that maps sentences to 384-dimensional vectors.",
    "ZONEID magic constants from id Software's DOOM engine provide runtime integrity verification.",
    "The MaKaLi Triad architecture decomposes queries across parallel Oversoul councils.",
    "This is a very short sentence.",
    "Potion is a static embedding approach that precomputes token embeddings through a transformer once, then looks them up via numpy at inference time.",
]


def benchmark_minilm(model_path: str, sentences: list) -> dict:
    """Benchmark all-MiniLM-L6-v2 via llama-cpp-python."""
    print(f"\n{'='*60}")
    print(f"📊 BENCHMARK: MiniLM via llama-cpp-python")
    print(f"{'='*60}")
    print(f"Model: {model_path}")
    print(f"Sentence count: {len(sentences)}")
    print(f"Iterations: {N_ITERATIONS}")

    import numpy as np
    from llama_cpp import Llama

    # Load model
    t0 = time.time()
    print(f"\nLoading model...", end=" ", flush=True)
    llm = Llama(model_path=model_path, embedding=True, n_ctx=512, n_threads=8, verbose=False)
    load_time = time.time() - t0
    print(f"done ({load_time:.2f}s)")

    # Warmup
    print("Warmup...", end=" ", flush=True)
    llm.embed("Warmup sentence for cache priming.")
    print("done")

    # Benchmark
    dims_found = set()
    total_time = 0.0
    embeddings = []

    for i in range(N_ITERATIONS):
        iter_start = time.time()
        for sentence in sentences:
            result = llm.embed(sentence)
            # New GGUF: flat List[float]; old GGUF: nested List[List[float]]
            if result and len(result) > 0:
                if isinstance(result[0], float):
                    # Flat: result is already the vector
                    vec = result
                else:
                    # Nested: unwrap first element
                    vec = result[0]
                dims_found.add(len(vec))
                embeddings.append(vec)
            else:
                print(f"  \u26a0\ufe0f  Embedding failed for: {sentence[:40]}...")
        iter_time = time.time() - iter_start
        total_time += iter_time
        print(f"  Iteration {i+1}: {iter_time:.3f}s (avg {iter_time/len(sentences)*1000:.1f}ms/sentence)")

    avg_time = total_time / N_ITERATIONS
    avg_ms_per_sentence = (total_time / (N_ITERATIONS * len(sentences))) * 1000

    # Memory estimate (rough)
    import psutil
    proc = psutil.Process(os.getpid())
    rss_mb = proc.memory_info().rss / 1024 / 1024

    results = {
        "provider": "LocalGGUFEmbeddingProvider",
        "model": "all-MiniLM-L6-v2-f16.gguf",
        "backend": "llama-cpp-python 0.3.28",
        "dimensions": list(dims_found),
        "load_time_s": round(load_time, 2),
        "avg_inference_time_s": round(avg_time, 3),
        "avg_ms_per_sentence": round(avg_ms_per_sentence, 1),
        "rss_mb_after_load": round(rss_mb, 1),
        "sentences_tested": len(sentences),
        "iterations": N_ITERATIONS,
        "first_vector_sample": [round(v, 6) for v in embeddings[0][:5]] if embeddings else [],
    }
    print(f"\n✅ Results: dim={results['dimensions']}, load={load_time:.2f}s, "
          f"avg={avg_ms_per_sentence:.1f}ms/sent, RSS~{rss_mb:.0f}MB")

    llm.close()
    return results


def benchmark_potion(model_name: str, sentences: list) -> dict:
    """Benchmark potion-mxbai-micro via model2vec."""
    print(f"\n{'='*60}")
    print(f"📊 BENCHMARK: potion-mxbai-micro via model2vec")
    print(f"{'='*60}")
    print(f"Model: {model_name}")
    print(f"Sentence count: {len(sentences)}")
    print(f"Iterations: {N_ITERATIONS}")

    import numpy as np
    from model2vec import StaticModel

    # Load model
    t0 = time.time()
    print(f"\nLoading model...", end=" ", flush=True)
    # model2vec downloads from HuggingFace Hub on first load
    model = StaticModel.from_pretrained(model_name)
    load_time = time.time() - t0
    print(f"done ({load_time:.2f}s)")
    # Discover dimension by encoding a test string
    test_emb = model.encode("discover dimension")
    dim = test_emb.shape[0] if hasattr(test_emb, 'shape') else len(test_emb)
    print(f"  Output dimension: {dim}")

    # Warmup
    print("Warmup...", end=" ", flush=True)
    _ = model.encode("Warmup sentence for cache priming.")
    print("done")

    # Benchmark
    total_time = 0.0
    embeddings = []

    for i in range(N_ITERATIONS):
        iter_start = time.time()
        for sentence in sentences:
            vec = model.encode(sentence)
            embeddings.append(vec.tolist() if hasattr(vec, 'tolist') else list(vec))
        iter_time = time.time() - iter_start
        total_time += iter_time
        print(f"  Iteration {i+1}: {iter_time:.3f}s (avg {iter_time/len(sentences)*1000:.1f}ms/sentence)")

    avg_time = total_time / N_ITERATIONS
    avg_ms_per_sentence = (total_time / (N_ITERATIONS * len(sentences))) * 1000

    import psutil
    proc = psutil.Process(os.getpid())
    rss_mb = proc.memory_info().rss / 1024 / 1024

    results = {
        "provider": "StaticEmbeddingProvider (model2vec)",
        "model": model_name,
        "backend": f"model2vec 0.8.2",
        "dimensions": [dim],
        "load_time_s": round(load_time, 2),
        "avg_inference_time_s": round(avg_time, 3),
        "avg_ms_per_sentence": round(avg_ms_per_sentence, 1),
        "rss_mb_after_load": round(rss_mb, 1),
        "sentences_tested": len(sentences),
        "iterations": N_ITERATIONS,
        "first_vector_sample": [round(v, 6) for v in embeddings[0][:5]] if embeddings else [],
    }
    print(f"\n✅ Results: dim={results['dimensions']}, load={load_time:.2f}s, "
          f"avg={avg_ms_per_sentence:.1f}ms/sent, RSS~{rss_mb:.0f}MB")
    return results


def main():
    print(f"{'='*60}")
    print(f"🔱 OMEGA EMBEDDING BENCHMARK")
    print(f"{'='*60}")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Host: {os.uname().nodename}")

    can_minilm = os.path.isfile(MINILM_PATH)
    print(f"\nMiniLM path exists: {can_minilm} ({MINILM_PATH})")

    results = {}

    # 1. Benchmark MiniLM
    if can_minilm:
        try:
            results["minilm"] = benchmark_minilm(MINILM_PATH, TEST_SENTENCES)
        except Exception as e:
            print(f"\n❌ MiniLM benchmark failed: {e}")
            results["minilm"] = {"error": str(e)}
    else:
        print(f"\n❌ MiniLM not found at {MINILM_PATH} — skipping")

    # 2. Benchmark potion-base-2M (tiny, 64-dim)
    try:
        results["potion_tiny"] = benchmark_potion(POTION_MODEL_TINY, TEST_SENTENCES)
    except Exception as e:
        print(f"\n❌ Potion tiny benchmark failed: {e}")
        results["potion_tiny"] = {"error": str(e)}

    # 3. Benchmark potion-mxbai-micro (full, 768-dim)
    try:
        results["potion_full"] = benchmark_potion(POTION_MODEL_FULL, TEST_SENTENCES)
    except Exception as e:
        print(f"\n❌ Potion full benchmark failed: {e}")
        results["potion_full"] = {"error": str(e)}

    # 4. Summary comparison
    print(f"\n{'='*60}")
    print(f"📋 COMPARISON SUMMARY")
    print(f"{'='*60}")

    for key, label in [("minilm", "MiniLM (Q4_K_M)"), ("potion_tiny", "Potion (base-2M)"), ("potion_full", "Potion (mxbai-micro)")]:
        if key in results and "error" not in results[key]:
            p = results[key]
            dims = p.get('dimensions', ['?'])
            print(f"\n  {label} ({dims}d):")
            print(f"    Load:      {p['load_time_s']:.2f}s")
            print(f"    Per sent:  {p['avg_ms_per_sentence']:.1f}ms")
            print(f"    RSS:       {p['rss_mb_after_load']:.0f}MB")

    # Speed comparison between MiniLM and fastest potion
    best_potion = None
    for pk in ["potion_tiny", "potion_full"]:
        if pk in results and "error" not in results[pk]:
            if best_potion is None or results[pk]["avg_ms_per_sentence"] < best_potion["avg_ms_per_sentence"]:
                best_potion = results[pk]
    
    if "minilm" in results and "error" not in results["minilm"] and best_potion:
        m = results["minilm"]
        p = best_potion
        speed_ratio = m["avg_ms_per_sentence"] / p["avg_ms_per_sentence"] if p["avg_ms_per_sentence"] > 0 else float('inf')
        print(f"\n  Ratio (MiniLM / Potion-fastest): {speed_ratio:.1f}x")
        if speed_ratio > 1:
            print(f"  → Potion is {speed_ratio:.1f}x faster per sentence")
        else:
            print(f"  → MiniLM is {1/speed_ratio:.1f}x faster per sentence")

    # Save results
    output_path = Path("/tmp/omega_embedding_benchmark.json")
    output_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n📝 Full results saved to: {output_path}")

    # Return summary for the report
    print(f"\n{'='*60}")
    print("Done.")
    return results


if __name__ == "__main__":
    main()
