# ZRAM Control Series — LFM2.5-2.6B-Q4_K_M (2026-10-13)

Companion to `BENCHMARK_STUDY_20260926.md` §"Open items / defects", item 6
("zRAM-off vs zRAM-on is untested for LFM"). This closes that item.

## Conditions

- Same blob both series: `sha256-79fdf00351...` (verified via `ollama show --modelfile`)
- Same machine, same harness (`scripts/bench_threads.py`), 512 fixed tokens
- OFF series: `docs/research/bench-data/lfm25_512.json` (2026-09-26, n=2 reps, zRAM swapped off)
- ON series: `docs/research/bench-data/lfm25_512_zram_on.json` (2026-10-13, n=3 reps)
- ON-state zRAM: 7.4 GB zstd device, 840 MB payload @ 0.27 compression ratio
  (3.7x), 11.1% utilisation, 0.91 GB swap in use. AC on, profile=performance,
  EPP=performance, battery 99%.

## Head-to-head (mean t/s)

| Threads | zRAM OFF (n=2) | zRAM ON (n=3) | Delta ON−OFF |
|---|---|---|---|
| 4 | 19.57 ± 0.64 | 19.44 ± 0.29 | −0.13 (−0.7%) |
| 6 | 21.19 ± 1.02 | 20.49 ± 0.20 | −0.70 (−3.3%) |
| 8 | 19.82 ± 0.58 | 20.54 ± 0.00 | **+0.72 (+3.6%)** |
| 12 | 20.99 ± 0.21 | 20.63 ± 0.04 | −0.36 (−1.7%) |

All gates passed on the ON series (runner `-t` verified 4/4, CV ≤ 1.3%).

## Verdict

**zRAM-on at 11% utilisation has no consistent throughput effect on
LFM2.5-2.6B.** Deltas span −3.3% … +3.6% with mixed sign; the OFF series'
own CIs (±0.21 … ±1.02, n=2) overlap every ON point. The apparent ranking
flip (OFF winner t6 @ 21.19, ON winner t12 @ 20.63) is within run-to-run
variation, not a zRAM effect — the OFF t6 CI alone (±1.02) covers the
entire ON range.

Practical read: production (zRAM on, ~11% util) ≈ clean-lab (zRAM off)
for this model. The 6-thread recommendation stands; quote LFM numbers as
a range (20–21 t/s), never a point. Revisit only if zRAM utilisation
exceeds ~50% (compression-CPU cost regime untested).

## Harness fixes landed with this series (scripts/bench_threads.py)

1. `restart_ollama()` rewritten: unload-via-API + warm-load instead of
   `systemctl restart` (restart dropped the script's own connection mid-run
   and killed CONFIG 1). The old v1 file is preserved as
   `lfm25_512_zram_on_v1_buggy.json` (configs 4/6 failed gate: runner held
   `-t 8`; zram fields read 0.0 — wrong sysfs path).
2. `ensure_variant()` strips a pre-existing `bench-t` prefix + `-N` suffix
   so re-runs never create `bench-tbench-t…` doubles; Modelfile `FROM`
   uses the canonical base (was: variant-chaining).
3. `memory_state()` reads zRAM from `/sys/block/zram0/mm_stat` (this
   kernel has no `mem_used_total`/`orig_data_size` files) and reports
   `zram_compr_ratio` (low = good, ~0.27) separately from `zram_util_pct`
   (capacity pressure). The old `zram_pct` key is kept as compression-ratio
   % for backward compat; the >25% warning now keys on utilisation.
4. `ollama rm` flag fixed (`-f` unsupported on this version).
