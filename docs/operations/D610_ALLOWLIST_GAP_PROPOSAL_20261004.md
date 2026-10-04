# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# D-610 — Release-Cut `check-engine` Dependency Gap: Investigation & Proposal

**Entity**: @maat (Build-Side Governance Keeper, Slot S5)
**Date**: 2026-10-04
**Branch**: `debut-v1.6.0-alpha` (HEAD `f8d4f0ae`)
**Status**: **PROPOSAL ONLY — NOT APPLIED.** The Architect (Node 0) rules.
**Mandates**: M13 (temple-grade), M23 (failure integrity), M28 (no weakening of
D-565), and the standing rule that expanding the public surface is a
sovereignty-boundary decision reserved for the Architect.

---

## 0. Bottom line

The public cut ships `tests/` broadly but enumerates `scripts/` and `config/`
per-file. Five files that `make check-engine` depends on are absent from the cut,
producing **17 failures + 2 collection errors**. The previously published
`release/debut` (`3c051021`) is missing the same five, so this is pre-existing.

**The five-file framing in the original report is incomplete.** Each of the three
scripts has an *unlisted transitive dependency*, and one of those dependencies
contains the operator's real private-network addressing. Shipping the three
scripts as-listed would **not** fix the gate, and in two cases would make it
*worse* (converting a missing-file error into a hard gate failure).

| Tier | Files | Verdict |
|------|-------|---------|
| **A — ship as-is** | `config/embedding_strategy.yaml`, `scripts/check_secret_history.py` | Safe. Fixes 14 of 17 failures. |
| **B — ship as a pair** | `scripts/gnosis_archive.py` **+** `scripts/load_constraints.py` | Safe once the companion ships. Measured exit 0. |
| **C — DO NOT ship** | `scripts/lan_exposure_audit.py`, `scripts/test_lan_exposure_audit.py`, `config/lan_exposure_allowlist.yaml` | Discloses real LAN + tailnet IPs. Needs redaction first. |
| **D — Architect IP call** | `config/wads/arcana_novai/axioms.yaml` | No leak. Tier-5 USER-OWNED IP — a judgement call, not a safety one. |

---

## 1. Measured failure map

`check-engine` = `pytest tests/test_hub_import_smoke.py tests/contracts/
tests/test_lan_exposure.py` + two script steps (`Makefile:412-421`).

| Missing file | Consumed by | Failures |
|---|---|---|
| `config/embedding_strategy.yaml` | `omega.memory.embedding_strategy.get_embedding_strategy()` → `CONFIG_DIR / "embedding_strategy.yaml"` (no fallback), asserted by `tests/contracts/test_embedding_dimension.py` | **14** |
| `config/wads/arcana_novai/axioms.yaml` | `AxiomRegistry(WAD_DIR)` with `WAD_DIR = Path("config/wads/arcana_novai")` hard-coded in `tests/contracts/test_axiom_registry.py:22` | **3** |
| `scripts/lan_exposure_audit.py` | `tests/test_lan_exposure.py:62` `_load("lan_exposure_audit")` at module scope | collection error |
| `scripts/check_secret_history.py` | `tests/contracts/test_secret_history_gate.py:23-28` `spec_from_file_location` at module scope | collection error |
| `scripts/gnosis_archive.py` | `Makefile:419` `gnosis_archive.py verify` step | step fails |

14 + 3 = 17. Both collection errors are **import-time** failures.

> Note on the secret-history collection error: `ENGINE_FAST_TESTS`
> (`Makefile:406-410`) already carries
> `--deselect tests/contracts/test_secret_history_gate.py`. That deselect does
> **not** prevent the error, because pytest must still *collect* a directory to
> resolve node IDs for `--deselect`, and the import happens during collection.
> So a file that is explicitly excluded from the fast subset still breaks it.

---

## 2. The transitive dependencies (the actual finding)

### 2.1 `scripts/gnosis_archive.py` → needs `scripts/load_constraints.py`

`gnosis_archive.py:81-82` does a module-scope sibling import:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_constraints import ConstraintManifestMissing, load_constraints
```

Measured on a simulated cut (`/tmp/opencode/cutsim`, script alone):

```
ModuleNotFoundError: No module named 'load_constraints'
EXIT CODE: 1
```

With `scripts/load_constraints.py` copied alongside:

```
OK: all gnoses stamped.
EXIT CODE: 0
```

`load_constraints.py` in turn references `docs/governance/CONTRAINTS.md`, which is
also absent — but that is **not** required for the release gate. `load_constraints()`
is only called by the `stamp` path (`_constraint_stamp_lines()`), never by
`verify`. `do_verify()` (`gnosis_archive.py:419-467`) globs `data/entities/`,
returns `[]` when the directory is absent, and exits **0**. `CONSTRAINTS.md` is
therefore optional for the gate and needed only for the agent-side
archive/stamp workflow.

`scripts/load_constraints.py` is not in the original report's file list and must
be added to any Tier-B ruling, or Tier B converts a missing-file error into a
`ModuleNotFoundError`.

### 2.2 `scripts/lan_exposure_audit.py` → needs TWO more files, and they leak

`lan_exposure_audit.py:37,100-101`:

```python
ALLOWLIST = REPO_ROOT / "config" / "lan_exposure_allowlist.yaml"
...
if not ALLOWLIST.exists():
    raise SystemExit(f"[FATAL] allowlist not found: {ALLOWLIST}")
```

That `SystemExit` exits **1** — the same code the script uses for "exposure
found (gate RED)". So shipping the script without its config does not restore the
gate; it converts a collection error into a **red security gate**. And
`tests/test_lan_exposure.py:62-63` loads **two** modules:

```python
lan_audit = _load("lan_exposure_audit")
lan_cases = _load("test_lan_exposure_audit")
```

`scripts/test_lan_exposure_audit.py` is also absent from the allowlist.

### 2.3 🚫 `config/lan_exposure_allowlist.yaml` discloses the operator's network

This is the blocking finding. The allowlist config encodes **real, host-specific
network addressing**:

```yaml
# config/lan_exposure_allowlist.yaml:12,45
# 3. deluged — 192.168.10.168%wlo1:51372 and 100.123.51.67%tailscale0:51372
  - 100.123.51.67      # n0 tailnet IPv4
```

And the negative-test fixtures hard-code the same pair
(`scripts/test_lan_exposure_audit.py:57-78`):

```python
("approved tailnet 8016 v4", L("100.123.51.67", 8016, None, None), True),
("LAN deluged wlo1 caught", L("192.168.10.168", 51372, "wlo1", "deluged"), False),
```

`192.168.10.168` is a real private-LAN address on interface `wlo1`;
`100.123.51.67` is a real Tailscale CGNAT address on `tailscale0`. Publishing
these discloses internal network topology of the operator's machine and tailnet.

This is the same leak class as `f8d4f0ae` ("username/mount leak" via the
allowlist symlink guard) that landed immediately before this task. It should be
treated with the same severity.

**Recommendation: Tier C ships nothing.** Two viable paths, both Architect calls:

- **C1 — redact then ship.** Replace the real addresses with RFC 5737 /
  RFC 2544 documentation ranges (`192.0.2.0/24` TEST-NET-1, `198.51.100.0/24`,
  `100.64.0.0/10` is *not* usable here because the classifier must still treat it
  as tailnet — so keep the CGNAT shape but use a documentation address and
  adjust `lan_exposure_audit.py`'s tailnet predicate accordingly). Ship all three
  files. **Cost:** a code change to the classifier, so the redaction must not
  weaken the gate's ability to detect a real non-loopback bind.
- **C2 — do not ship; make the step cut-tolerant.** Leave all three on FORGE and
  change the `Makefile` `check-engine` step to skip-with-warning when the script
  is absent (mirroring how the cut already treats other host-specific checks).
  **Cost:** the public cut no longer runs the LAN-exposure audit. Defensible —
  the audit is inherently host-specific and cannot meaningfully run on a
  stranger's clone.

C2 is the lower-risk option and the one I would put to the Architect first.

---

## 3. Per-file safety assessment (all five + companions)

Every file was scanned with the repo's **own** credential patterns, taken from
`scripts/check_secret_history.py:40-46` (`firecrawl`, `google_api_key`,
`tavily`, `jwt`, `gocspx`).

```
scripts/lan_exposure_audit.py       credential-hits=0  SPDX=yes
scripts/test_lan_exposure_audit.py  credential-hits=0  SPDX=yes
scripts/gnosis_archive.py           credential-hits=0  SPDX=yes
scripts/load_constraints.py         credential-hits=0  SPDX=yes
scripts/check_secret_history.py     credential-hits=0  SPDX=yes
config/embedding_strategy.yaml      credential-hits=0  SPDX=yes
config/wads/arcana_novai/axioms.yaml credential-hits=0 SPDX=yes
TOTAL credential-shaped hits: 0
```

| File | Secrets | Abs. host paths / usernames | Notes |
|---|---|---|---|
| `config/embedding_strategy.yaml` | none | none — model paths use the `env:OMEGA_MODELS_DIR/...` indirection | Contains internal decision IDs (D-1024-DIM-NATIVE-20260926) and architectural rationale. Design disclosure, not a leak. |
| `config/wads/arcana_novai/axioms.yaml` | none | none | Purely philosophical. Header self-declares `Tier 5 USER-OWNED IP`. See Tier D. |
| `scripts/check_secret_history.py` | none | none — `REPO_ROOT = Path(__file__).resolve().parent.parent` | Stores only `sha256[:16]`; its own docstring states "No secret material is stored in the baseline, so it can ship publicly." Its baseline `.secret-history-baseline.toml` is **already** on the cut (line 40). Self-consistent. |
| `scripts/gnosis_archive.py` | none | none — all paths derived from `REPO_ROOT` | Discovers entities dynamically; no hard-coded roster (entity names appear only in usage examples). |
| `scripts/load_constraints.py` | none | none | Reads `docs/governance/CONTRAINTS.md`, optional for the gate. |
| `scripts/lan_exposure_audit.py` | none | **loopback literals only** — `HARDCODED_LOOPBACK` is the tool's *subject*, not a leak | But hard-fails without `config/lan_exposure_allowlist.yaml`. |
| `scripts/test_lan_exposure_audit.py` | none | **real `192.168.10.168` + `100.123.51.67`** | 🚫 Tier C. |
| `config/lan_exposure_allowlist.yaml` | none | **real `192.168.10.168` + `100.123.51.67`** | 🚫 Tier C. |

### `make gate-secrets` status (M23 — reported as measured, not as claimed)

`make gate-secrets` is **RED on this dev branch, pre-existing, and not caused by
these changes.** All 33 un-audited-token findings are in files outside the
proposal set:

- `data/coordination/**` (22 paths) — runtime coordination artifacts
- `docs/ASUS/ASUS-session-ses_f833.md`, `docs/great-agent-responses/session-ses_ff78.md`
- `docs/reference/api/tools.md` — PEM template false positive
- gitleaks: findings present

**Zero** findings fall in any file proposed for the public surface (verified by
intersecting the gate's own failure list against the candidate set).

This is also why `temple-grade` can report 53/53 while `gate-secrets` is red:
`temple-grade` (`Makefile:446`) is
`check-constraints check-engine check-hub-imports check-codex-stale
doc-llm-validate check-mandates check-mandate-compliance check-tracking-state
dashboard-self-test` — **`gate-secrets` is not in that chain.** `REUSE lint`
(M37 SPDX) is likewise a separate target (`Makefile:467`), not in the chain;
`src/omega/library/discovery.py` has carried a missing SPDX header since before
this task and is not covered by `REUSE.toml`.

---

## 4. PROPOSED allowlist diff — NOT COMMITTED

> **Architect action required.** Per M23 and the D-565 boundary, adding paths to
> the public surface is not mine to make. Apply by hand, or reject.

Insert into the `## ✅ ALLOW` block, in the **Config** group (after
`config/litestream.yml`, `Makefile`-adjacent region at allowlist line 29):

```diff
  config/models.yaml
  config/providers.yaml
  config/omega.yaml
  config/wads/_omega_default/
  config/model_fleet_operational.yaml
  config/litestream.yml
  config/systemd/
+ # D-610: check-engine dependency — consumed by
+ # omega.memory.embedding_strategy.get_embedding_strategy(); its absence fails
+ # 14 assertions in tests/contracts/test_embedding_dimension.py.
+ # Paths use env:OMEGA_MODELS_DIR/ indirection — no host paths, no secrets.
+ config/embedding_strategy.yaml
```

Insert into the same block, in the **Install + docs** scripts group (after
`scripts/godot_spatial_bridge.py`, allowlist line 50):

```diff
  scripts/migrate_to_sqlcipher.py
  scripts/godot_spatial_bridge.py
+ # D-610: check-engine dependency — Makefile gate-secrets runs it; its absence
+ # is a collection error in tests/contracts/test_secret_history_gate.py (which
+ # --deselect does NOT suppress, because deselect resolves after collection).
+ # Safe to publish: stores only sha256[:16] hashes, never secret material.
+ # Its baseline .secret-history-baseline.toml is already allowlisted (line 40).
+ scripts/check_secret_history.py
+ # D-610: check-engine dependency — Makefile:419 runs `gnosis_archive.py verify`.
+ # MUST ship together with scripts/load_constraints.py: gnosis_archive.py:82
+ # imports it at module scope, and without it the step dies with
+ # ModuleNotFoundError (measured, exit 1) instead of the current missing-file error.
+ # Verified: with load_constraints.py present, `verify` exits 0 on an empty cut.
+ scripts/gnosis_archive.py
+ scripts/load_constraints.py
```

Tier D, **only if** the Architect rules the Five-Fold cosmology is public-facing IP
(insert into the Config group):

```diff
+ # D-610 Tier D — ARCHITECT IP RULING REQUIRED. Contains no secrets and no host
+ # paths, but this is the arcana_novai WAD's own cosmological content, self-declared
+ # "Tier 5 USER-OWNED IP". Its absence fails 3 assertions in
+ # tests/contracts/test_axiom_registry.py. Note the WAD *mechanism* is already
+ # public via config/wads/_omega_default/ (allowlist line 27).
+ config/wads/arcana_novai/axioms.yaml
```

**Deliberately NOT proposed** (Tier C — would disclose network topology):

```diff
- scripts/lan_exposure_audit.py
- scripts/test_lan_exposure_audit.py
- config/lan_exposure_allowlist.yaml
```

---

## 5. Decision points for the Architect

1. **Tier C — LAN exposure trio.** C1 (redact, then ship) or C2 (stay on FORGE,
   make the `check-engine` step cut-tolerant)? Recommendation: **C2**.
2. **Tier D — `axioms.yaml`.** Is the Five-Fold cosmology public-facing IP?
   No technical blocker either way; 3 assertions stay red until ruled.
3. **Residual red after Tier A+B+D.** If the Architect rules C2 and D is declined,
   the cut retains ~4 failures + 2 collection errors from the LAN trio and the
   axioms tests. The alternative is to make those tests cut-tolerant rather than
   widen the public surface — consistent with D-565's philosophy of "absence must
   be survivable."
4. **D-565 is not weakened by any tier above.** `src/omega/vault/` stays FORGE.

## 6. What was NOT done

- `docs/strategy/PUBLIC_ALLOWLIST.txt` was **not** modified. The diffs above are a
  proposal only.
- `release/debut` was **not** touched. Nothing was pushed.
- No file was deleted (M28).