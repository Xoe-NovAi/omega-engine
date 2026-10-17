# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Canonical embedder for the corpus index, pinned to PHYSICAL cores.

Why this exists: `Qwen3GGUFEmbeddingProvider` hard-codes its parent's
defaults (n_threads=6, n_ctx=512) and exposes no override. For a
long-running bulk indexing job that is the wrong shape on an SMT laptop:

  * Thread oversubscription. The 5700U exposes 16 logical / 8 physical
    cores. llama.cpp CPU inference does not benefit from running two
    hyperthreads on one core — they contend for the same FP units and the
    extra runnable threads mostly buy scheduler churn. Measured on this
    host, an unpinned run pushed load average to ~17 while making
    progress no faster (2026-10-17).
  * Starvation. The hub, the OpenCode process, and a dozen MCP servers
    share this box. A bulk embedder that takes every core starves them
    and inflates latency for every other agent in the fleet.

So the corpus embedder derives its width from PHYSICAL cores, leaves one
core free for the rest of the fleet, and honours explicit env overrides
(OMEGA_CORPUS_THREADS / OMEGA_CORPUS_CTX).

[D-1024-DIM-NATIVE-20260926] The model and width are unchanged: native
Qwen3-Embedding-0.6B at 1024. This module tunes SCHEDULING only. It does
not alter the embedding space, so vectors written here remain comparable
with any other canonical-space vector.

M23: if the canonical model or its llama.cpp build is missing, this
raises. It never falls back to feature hashing — a hashed corpus answers
"where is the Ark vision?" with confident nonsense.
"""

from __future__ import annotations

import os
import logging
from typing import List, Optional

import anyio

from omega.memory.embeddings import Qwen3GGUFEmbeddingProvider

from .store import CANONICAL_DIM

logger = logging.getLogger(__name__)


def physical_cores(default: int = 4) -> int:
    """Best-effort physical core count (not hyperthreads).

    Parses `lscpu` rather than trusting `os.cpu_count()`, which reports
    logical CPUs. Falls back conservatively (half the logical count, or
    `default`) when the parse fails.
    """
    logical = os.cpu_count() or default
    try:
        import subprocess

        out = subprocess.run(
            ["lscpu"], capture_output=True, text=True, timeout=5, check=True
        ).stdout
        cores = None
        threads_per_core = 1
        for line in out.splitlines():
            if line.startswith("Core(s) per socket"):
                cores = int(line.split(":")[1].strip())
            elif line.startswith("Thread(s) per core"):
                threads_per_core = int(line.split(":")[1].strip())
        if cores:
            sockets = 1
            for line in out.splitlines():
                if line.startswith("Socket(s)"):
                    sockets = int(line.split(":")[1].strip())
                    break
            physical = cores * sockets
            if threads_per_core > 1:
                # cores-per-socket is already physical; don't divide again.
                return max(1, physical)
            return max(1, physical)
    except (subprocess.SubprocessError, ValueError, IndexError, OSError) as exc:
        logger.debug("Failed to detect physical cores via lscpu: %s", exc)
    return max(1, min(logical // 2 if logical > 2 else logical, default * 2))


def physical_core_ids() -> List[int]:
    """One representative logical CPU per physical core, ascending.

    Thread count is NOT core count. On SMT (this host: Ryzen 7 5700U,
    8 physical / 16 logical, adjacent-pair topology — cpu0+cpu1 share a
    core) the scheduler may place N threads on N logical CPUs that map to
    only ceil(N/2) physical cores, so two runnable threads contend for
    one core's FP units. That contention is what "thrashing" looks like.

    Reading `thread_siblings_list` gives the true mapping; taking the
    lowest sibling of each group yields the canonical one-CPU-per-core
    representative set (here: 0,2,4,6,8,10,12,14).
    """
    groups = set()
    try:
        import glob as _glob

        for path in _glob.glob("/sys/devices/system/cpu/cpu[0-9]*/topology/thread_siblings_list"):
            try:
                raw = open(path).read().strip()
            except OSError as err:
                logger.debug("Cannot read thread_siblings_list at %s: %s", path, err)
                continue
            # Expand forms like "0-1", "0,8", "0-1,4-5"
            members: List[int] = []
            for part in raw.split(","):
                part = part.strip()
                if not part:
                    continue
                if "-" in part:
                    a, _, b = part.partition("-")
                    try:
                        members.extend(range(int(a), int(b) + 1))
                    except ValueError as err:
                        logger.debug("Failed parsing cpu range %s: %s", part, err)
                        continue
                else:
                    try:
                        members.append(int(part))
                    except ValueError as err:
                        logger.debug("Failed parsing cpu part %s: %s", part, err)
                        continue
            if members:
                groups.add(tuple(sorted(members)))
    except (OSError, RuntimeError) as exc:
        logger.debug("Failed traversing thread_siblings_list: %s", exc)
        groups = set()

    if not groups:
        # No sysfs topology (non-Linux/container). Fall back to even CPUs,
        # which is the adjacent-pair layout, and let affinity sort it out.
        return list(range(0, (os.cpu_count() or 8), 2))

    reps = sorted(min(g) for g in groups)
    # Sanity: only keep representatives that actually exist.
    online = os.cpu_count() or len(reps)
    return [c for c in reps if c < online]


def _cgroup_cpuset_path() -> Optional[Path]:
    """Return the cpuset.cpus.effective path for the current cgroup v2, or None."""
    try:
        # Find the cgroup v2 mount
        with open('/proc/self/cgroup', 'r') as f:
            for line in f:
                if line.startswith('0::'):
                    path = line.strip().split('::')[-1].strip()
                    return Path('/sys/fs/cgroup') / path / 'cpuset.cpus.effective'
    except (OSError, IndexError) as exc:
        logger.debug("Failed checking cgroup cpuset path: %s", exc)
    return None


def _apply_cgroup_cpuset(cpus: List[int]) -> bool:
    """Write CPU list to cgroup v2 cpuset.cpus (kernel-enforced, cannot be overridden)."""
    try:
        # Try to write to the current cgroup's cpuset.cpus
        with open('/proc/self/cgroup', 'r') as f:
            for line in f:
                if line.startswith('0::'):
                    path = line.strip().split('::')[-1].strip()
                    cpuset_path = Path('/sys/fs/cgroup') / path / 'cpuset.cpus'
                    if cpuset_path.exists():
                        cpu_str = ','.join(str(c) for c in cpus)
                        cpuset_path.write_text(cpu_str)
                        # Verify
                        effective = (Path('/sys/fs/cgroup') / line.strip().split('::')[-1].strip() / 'cpuset.cpus.effective').read_text().strip()
                        return True
    except (OSError, IndexError) as exc:
        logger.debug("Failed applying cgroup cpuset: %s", exc)
    return False


def pin_to_physical_cores(n_threads: Optional[int] = None) -> Optional[List[int]]:
    """Restrict this process to distinct physical cores using cgroup v2 cpuset.

    This is KERNEL-ENFORCED and cannot be overridden by llama.cpp's internal
    pthread_setaffinity_np calls. Returns the CPU list actually applied,
    or None if unsupported. OMEGA_CORPUS_NO_AFFINITY=1 disables.
    """
    if os.environ.get("OMEGA_CORPUS_NO_AFFINITY"):
        return None
    cores = physical_core_ids()
    n = int(n_threads or default_threads())
    chosen = cores[:n]
    if not chosen:
        return None

    # Try cgroup v2 cpuset first (kernel-enforced, survives pthread_setaffinity_np)
    if _apply_cgroup_cpuset(chosen):
        return chosen

    # Fallback: process-level affinity (can be overridden by llama.cpp)
    try:
        os.sched_setaffinity(0, set(chosen))
        return chosen
    except (AttributeError, OSError):
        return None


def default_threads() -> int:
    """One fewer than physical cores — leave a core for the rest of the fleet."""
    env = os.environ.get("OMEGA_CORPUS_THREADS")
    if env and env.isdigit():
        return max(1, int(env))
    return max(1, physical_cores() - 1)


def default_ctx() -> int:
    env = os.environ.get("OMEGA_CORPUS_CTX")
    if env and env.isdigit():
        return max(256, int(env))
    # 512 is the engine default and holds a 1500-char chunk (~357 tokens)
    # with ~43% headroom. Raise only deliberately.
    return 512


class CorpusEmbedder(Qwen3GGUFEmbeddingProvider):
    """Qwen3-Embedding-0.6B, physical-core-pinned, canonical 1024-dim."""

    def __init__(
        self,
        n_threads: Optional[int] = None,
        n_ctx: Optional[int] = None,
        target_dim: Optional[int] = None,
    ):
        super().__init__(target_dim=target_dim)
        # Overwrite the parent's hard-coded defaults AFTER super().__init__
        # but BEFORE first load, since _ensure_loaded reads these lazily.
        self._n_threads = int(n_threads or default_threads())
        self._n_ctx = int(n_ctx or default_ctx())
        self._affinity = pin_to_physical_cores(self._n_threads)
        self._assert_ready()

    async def _ensure_loaded(self) -> None:
        """Load the GGUF with BOTH thread caps pinned.

        The parent implementation builds the model as:

            llama_cpp.Llama(model_path=..., embedding=True,
                            n_ctx=..., n_threads=..., verbose=False)

        It never passes `n_threads_batch`, and llama-cpp-python defaults that
        to `multiprocessing.cpu_count()`. Because EMBEDDING runs on llama.cpp's
        batch/prompt path, the batch cap — not `n_threads` — governs actual
        parallelism. Measured on the 5700U (16 logical / 8 physical):
        n_threads=7 still produced 32 OS threads, because the batch path
        picked up 16. Setting only n_threads was therefore a no-op.

        This override pins n_threads_batch to the same physical-core budget.
        """
        if self._loaded and self._llama is not None:
            return

        import os as _os

        if not _os.path.isfile(self._model_path):
            raise FileNotFoundError(f"Embedding model not found: {self._model_path}")

        try:
            import llama_cpp
        except ImportError as e:
            raise FileNotFoundError(
                "llama-cpp-python not installed — the corpus indexer requires "
                "the native extra (pip install the-omega-engine[native])."
            ) from e

        def _load():
            return llama_cpp.Llama(
                model_path=self._model_path,
                embedding=True,
                n_ctx=self._n_ctx,
                n_threads=self._n_threads,
                n_threads_batch=self._n_threads,  # <-- the cap that matters
                verbose=False,
            )

        self._llama = await anyio.to_thread.run_sync(_load)
        self._loaded = True
        logger.info(
            "CorpusEmbedder: loaded %s (native=%d, n_ctx=%d, threads=%d, threads_batch=%d)",
            _os.path.basename(self._model_path),
            self._native_dimension, self._n_ctx, self._n_threads, self._n_threads,
        )

    def os_thread_count(self) -> int:
        """Live OS thread count for this process — used to VERIFY the cap."""
        import os as _os

        try:
            return len(_os.listdir("/proc/self/task"))
        except OSError as exc:
            logger.debug("Cannot list /proc/self/task: %s", exc)
            return -1

    def _assert_ready(self) -> None:
        if self._native_dimension != CANONICAL_DIM:
            raise RuntimeError(
                f"non-canonical model width {self._native_dimension} != {CANONICAL_DIM} "
                "[D-1024-DIM-NATIVE-20260926]"
            )

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed document chunks (no instruction prefix — Qwen3 convention)."""
        out: List[List[float]] = []
        for t in texts:
            v = await self.get_embedding(t, is_query=False)
            if v is None or len(v) != CANONICAL_DIM:
                raise RuntimeError(
                    "canonical width violation during document embedding "
                    "[D-1024-DIM-NATIVE-20260926]"
                )
            out.append(list(v))
        return out

    async def embed_query(self, text: str) -> List[float]:
        """Embed a search query (instruction-prefixed, per Qwen3-Embedding)."""
        v = await self.get_embedding(text, is_query=True)
        if v is None or len(v) != CANONICAL_DIM:
            raise RuntimeError(
                "canonical width violation during query embedding "
                "[D-1024-DIM-NATIVE-20260926]"
            )
        return list(v)
