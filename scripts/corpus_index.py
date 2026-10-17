#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""CLI for the Sovereign Ark corpus index.

Usage:
  python scripts/corpus_index.py build  [--source ID ...] [--limit N] [--force] [--cgroup]
  python scripts/corpus_index.py search "query" [-k N] [--lexical-only]
  python scripts/corpus_index.py stats

M1: AnyIO throughout. Never imports asyncio.
"""

from __future__ import annotations

import argparse
import sys
import subprocess
import shlex
from typing import List
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import anyio  # noqa: E402

from omega.corpus import CorpusIndexer, CorpusSearch, CorpusStore, resolve_sources  # noqa: E402

DB = REPO / "data" / "corpus" / "corpus.db"


def _store() -> CorpusStore:
    return CorpusStore(DB)


def _launch_with_cgroup(cpus: List[int], args: List[str]) -> int:
    """Launch the corpus indexer under systemd-run with AllowedCPUs.

    This creates a systemd user scope with CPU restriction enforced at the
    kernel level via cgroup v2 cpuset, which llama.cpp's pthread_setaffinity_np
    CANNOT override. Requires systemd user session (standard on modern Linux).
    """
    cpu_list = ','.join(str(c) for c in cpus)
    # Preserve working directory for systemd-run
    cwd = Path.cwd()
    # Launch via systemd-run with AllowedCPUs - use the current command but re-exec
    # We need to preserve the full command line including the script path
    # args[0] is the script path, args[1:] are the remaining args
    # Use sh -c with proper quoting for args
    # Build the command string with proper shell escaping
    # Strip --cgroup to avoid infinite recursion
    child_args = [a for a in args if a != '--cgroup']
    module_cmd = ' '.join([sys.executable, '-m', 'scripts.corpus_index'] + [shlex.quote(a) for a in child_args])
    cmd = [
        'systemd-run', '--user', '--scope',
        f'--property=AllowedCPUs={cpu_list}',
        '--property=MemoryAccounting=yes',
        '--property=MemoryMax=4G',
        'sh', '-c', f'cd {REPO} && exec {module_cmd}'
    ]
    print(f"Launching under systemd-run with AllowedCPUs={cpu_list}...", file=sys.stderr)
    return subprocess.run(cmd).returncode


def _store() -> CorpusStore:
    return CorpusStore(DB)


def cmd_build(args) -> int:
    store = _store()
    idx = CorpusIndexer(store)

    def progress(rep):
        print(
            f"  ... seen={rep.files_seen} indexed={rep.files_indexed} "
            f"skipped={rep.files_skipped_unchanged} chunks={rep.chunks_written}",
            flush=True,
        )

    async def go():
        return await idx.run(
            source_ids=args.source or None,
            limit=args.limit,
            force=args.force,
            progress=progress,
            path_glob=args.glob,
            max_chunks_per_doc=args.max_chunks,
        )

    print("Corpus sources:", flush=True)
    for s in resolve_sources(args.source or None):
        print("  -", s.describe(), flush=True)
    print("Indexing (embedding via canonical Qwen3-Embedding-0.6B, 1024-dim)...", flush=True)
    if args.cgroup:
        from omega.corpus.embedder import physical_core_ids, default_threads
        cores = physical_core_ids()[:int(default_threads())]
        return _launch_with_cgroup(cores, sys.argv[1:])
    rep = anyio.run(go)
    print("\n== Index report ==")
    for k, v in rep.as_dict().items():
        print(f"  {k}: {v}")
    print("\n== Store stats ==")
    for k, v in store.stats().items():
        print(f"  {k}: {v}")
    store.close()
    return 0 if rep.files_failed == 0 else 1


def cmd_search(args) -> int:
    store = _store()
    search = CorpusSearch(store)
    hits = anyio.run(search.search, args.query, args.k, args.lexical_only)
    if not hits:
        print("(no hits)")
    for i, h in enumerate(hits, 1):
        arms = ("S" if h.semantic else "-") + ("L" if h.lexical else "-")
        dist = f" d={h.distance:.4f}" if h.distance is not None else ""
        print(f"{i:2}. [{arms} rrf={h.rrf:.5f}{dist}] {h.title or '(untitled)'}")
        print(f"    {h.uri}")
        snippet = " ".join(h.text.split())[:220]
        print(f"    {snippet}...")
    store.close()
    return 0


def cmd_stats(args) -> int:
    store = _store()
    for k, v in store.stats().items():
        print(f"{k}: {v}")
    store.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="ingest + embed corpus sources")
    b.add_argument("--source", action="append", help="restrict to a source_id")
    b.add_argument("--limit", type=int, default=None)
    b.add_argument("--force", action="store_true", help="re-embed even if unchanged")
    b.add_argument("--glob", default=None, help="only files whose name matches this glob")
    b.add_argument(
        "--max-chunks", type=int, default=None,
        help="cap chunks per document (protects bulk runs from huge files)",
    )
    b.add_argument("--cgroup", action="store_true", help="launch under systemd-run with AllowedCPUs (kernel-enforced affinity)")
    b.set_defaults(func=cmd_build)

    s = sub.add_parser("search", help="hybrid search the corpus")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=10)
    s.add_argument("--lexical-only", action="store_true")
    s.set_defaults(func=cmd_search)

    t = sub.add_parser("stats", help="index statistics")
    t.set_defaults(func=cmd_stats)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())