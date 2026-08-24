# Build Observability & RAM Guard — Fleet Guide
**AP: AP-BUILD-OBS-GUIDE-v1.0.1**
⬡ OMEGA ⬡ P8 ⬡ build ⬡ install ⬡ 2026-08-22
**RATIFIED as fleet policy by kali 2026-08-22 (D-K4); Sovereign Mandate amendment deferred post-debut.**

## The rule (short version)
> **Any native or long build runs under `observe-build.sh`. No exceptions.**
> Any sdist rebuild uses `fetch-sdist.sh`. Never `pip download --no-binary`.

This exists because of a real incident: an unpinned llama-cpp-python compile hit
~13GiB RSS **plus ~1.9GiB compressed zRAM overflow** (true demand ~17-19GiB on a
14GiB box) and OOM'd the machine; later, a `pip download` wedged for 52+ minutes
inside scikit-build-core's metadata configure with zero visibility.
Both failure modes are now covered by tooling below.

---

## 1. Wrapping a build (`scripts/observe-build.sh`)

```bash
scripts/observe-build.sh <run-name> <command> [args...]
# or via make:
make observe CMD='bash scripts/install.sh'
make install-guarded          # install.sh under the observer, pre-named
```

Artifacts land in `/tmp/opencode/obs/<run-name>/`:
| File | What |
|------|------|
| `metrics.csv` | 1 Hz samples: mem used/avail, load, top-PID RAM attribution |
| `console.log` | full command output (pass `-v` to pip to expose cmake/ninja lines) |
| `STALL` | appears when console output freezes ≥5 min (configurable) — your tripwire |
| `summary.txt` | auto-postmortem: exit code, duration, peak RAM, top-5 offenders, stalls |

Env knobs:
- `BUILD_TIMEOUT_SECS=1800` — hard-kill guard (off by default)
- `STALL_SAMPLES=300` — samples of zero log growth before STALL fires (~5 min @1Hz)

**UX contract**: you never need to watch btop again. Poll for `summary.txt`
appearance (build done) or `STALL` file (wedged). Both are machine-readable,
so agents can check them in one command.

## 2. Rebuilding sdists safely (`scripts/fetch-sdist.sh`)

```bash
source .venv/bin/activate
scripts/fetch-sdist.sh llama-cpp-python==0.3.35
```

- Fetches the sdist ONCE via PyPI JSON API → cached at `~/.cache/omega-sdists`
- Installs from the local tarball: always compiles fresh, zero network
  re-resolution, no other wheels re-downloaded
- **Never use `pip download --no-binary :all:`** — it triggers a FULL wheel
  build inside metadata extraction (PEP 517 fallback) = silent double compile
  and the 52-minute wedge we hit
- Also never pass `--no-cache-dir` habitually: it wipes the HTTP cache too and
  is why every retry re-downloaded everything during the incident session

## 3. RAM facts on this box (measured, do not re-derive)

Host: Ryzen 7 5700U, 8C/16T, ~14GiB usable RAM. `/tmp` is tmpfs (RAM-backed).

| Build parallelism | Peak total RSS | Notes |
|---|---|---|
| unpinned (16 jobs) | ~13 GiB + ~1.9 GiB zRAM overflow (compressed) | OOM territory |
| 6 jobs | <10 GiB incl. both IDEs resident | validated empirically |
| **8 jobs (default)** | expected ≲11-12 GiB | `install.sh` default; validate next natural rebuild |

- The ONLY honored knob on scikit-build-core builds is **`CMAKE_BUILD_PARALLEL_LEVEL`**
  (verified against skbuild-core 1.0.3 source). `_JOBS`/`MAKEFLAGS` are dead vars.
- `/tmp` artifacts consume RAM. Clean build workspaces after use;
  big caches go to `~/.cache`, not tmpfs.

## 4. Secret-gate hygiene for build/report docs

PRIMARY gate (format-regex, prose-safe by construction):
```bash
for R in 'GOCSPX-[A-Za-z0-9]{12,}' 'csk-[A-Za-z0-9]{16,}' \
         'fc-[a-f0-9]{20,}' 'AIzaSy[A-Za-z0-9_-]{20,}'; do
  printf -- '-G %s: ' "$R"; git log -G "$R" --all --oneline | wc -l
done
```
Bare `-S '<prefix>'` scans are ADVISORY only (prose trips them).
When writing incident reports, mask literals as `PREFIX-<REDACTED>` and mangle
bare prefixes (`G0CPX`, `c-sk`) so docs stay gate-clean forever.

## 5. Incident references

- Full execution record: `docs/research/R_CLINE_SESSION_REPORT_FOR_KALI_20260822.md`
- Raw evidence: `docs/research/evidence_20260822/` (gitleaks report, sampler logs)
- OPS NOTE: `data/coordination/HMC_COLLABORATION_HUB.md` (2026-08-22 entry)

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: build | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
