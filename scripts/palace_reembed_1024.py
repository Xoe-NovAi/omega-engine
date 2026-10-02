#!/usr/bin/env python3
"""Re-embed the MemPalace palace from dim=384 to native 1024 (qwen3-embedding:0.6b).

Migrates in place, in batches, inside one transaction per batch so it is resumable
and safe against interruption. Records already at the target dim are skipped, so
re-running after a partial failure completes the job.

Usage:  python3 scripts/palace_reembed_1024.py [--batch 64] [--limit N] [--dry-run]
"""
import argparse, json, sqlite3, struct, sys, time, urllib.request, urllib.error

DB = "/home/xnai/WanderGround/mempalace/sqlite_exact.sqlite3"
MODEL = "qwen3-embedding:0.6b"
URL = "http://127.0.0.1:11434/api/embed"
TARGET_DIM = 1024


def embed(texts, retries=3):
    # No `dimensions` param => native 1024. `truncate_dim` is NOT an Ollama param.
    body = {"model": MODEL, "input": texts}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read())["embeddings"]
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0, help="cap rows (0 = all)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")  # crash-safe
    rows = con.execute(
        "SELECT id, document, dim FROM documents WHERE embedding IS NOT NULL AND dim != ?",
        (TARGET_DIM,),
    ).fetchall()
    if args.limit:
        rows = rows[: args.limit]
    print(f"to migrate: {len(rows)} rows (current dims != {TARGET_DIM})")
    if args.dry_run:
        for r in rows[:3]:
            print("  sample id:", r[0][:40], "dim=", r[2])
        return 0

    t0 = time.time()
    done = 0
    for i in range(0, len(rows), args.batch):
        chunk = rows[i : i + args.batch]
        ids = [r[0] for r in chunk]
        texts = [r[1] for r in chunk]
        vecs = embed(texts)
        assert len(vecs) == len(chunk), "embed count mismatch"
        upd = []
        for did, v in zip(ids, vecs):
            assert len(v) == TARGET_DIM, f"dim {len(v)} != {TARGET_DIM}"
            blob = struct.pack("<%df" % len(v), *v)
            upd.append((blob, TARGET_DIM, did))
        with con:
            con.executemany(
                "UPDATE documents SET embedding=?, dim=? WHERE id=?", upd
            )
        done += len(chunk)
        el = time.time() - t0
        rate = done / el if el else 0
        print(f"  {done}/{len(rows)}  {rate:.1f} rows/s  eta {(len(rows)-done)/rate:.0f}s")
    con.close()
    print(f"DONE {done} rows in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())