# MAAT LIVE FEED — 2026-10-04

**Entity**: maat (Build Oversoul, Slot S5)
**Channel**: opencode
**Model**: space-bunny-free (opencode/space-bunny-free)
**Task**: D-611 — fix D-610 release blockers (vault import + symlink leak)
**Branch**: `debut-v1.6.0-alpha` · HEAD `f8d4f0ae`

---

## STATUS: COMPLETE (both assigned defects) — with 3 items ESCALATED, not actioned

### Delivered

| # | Defect | Fix | Commit |
|---|--------|-----|--------|
| 1 | `temple-grade` failed on EVERY allowlist cut (`ModuleNotFoundError: No module named 'omega.vault'` at `src/omega/library/discovery.py:32`) | Every `omega.vault` import in cut-retained code is ImportError-guarded; absent vault degrades to no credentials | `3234d066` |
| 2 | Cut script skipped symlinks → `data/library` + `data/memory` shipped pointing at `/media/arcana-novai/omega_library/...` | `[[ ! -f "$f" ]]` → `[[ ! -e "$f" && ! -L "$f" ]]`; plus a new SYMLINK LEAK AUDIT | `f8d4f0ae` |

**D-565 NOT weakened.** Vault is still cut, still absent, still the single source of
truth for credentials when present, still NOT allowlisted.

### Evidence

Both defects proven **read-only on the already-published `release/debut` (3c051021)**:

- `git ls-tree -r 3c051021 -- src/omega/vault/` → **0 files**
- `3c051021:src/omega/library/discovery.py:32` → `from omega.vault import VaultCore`
- `3c051021:mcp_servers/omega_hub/state.py:50` → imports `DiscoveryOrchestrator`
- ⇒ the published release **has been failing M13 since it was cut**
- `git ls-tree -r 3c051021` mode `120000` → `data/library`, `data/memory` → `/media/arcana-novai/...`
  ⇒ username + mount layout **live in the public repo**

### Gates

- `make temple-grade` (dev, `f8d4f0ae`): **exit 0 · TOTAL 53 PASS 53 FAIL 0**
  · `check-engine` 175/175 · `check-hub-imports PASSED (6 modules, clean venv)`
- DRY-RUN CUT in a throwaway worktree (removed; real branch untouched):
  **799 kept / 9568 removed** · 7 symlinks removed · 2 symlinks kept
- On the cut tree: all 6 hub modules import; the 25 new regression tests ship and pass
- Before/after on the *identical* cut: pre-fix → `ModuleNotFoundError` at line 32;
  post-fix → chain imports

### Escalated — NOT actioned (M23: boundary changes need a human)

1. **BLOCKER — third, independent, pre-existing cut defect.** The allowlist ships
   `tests/` broadly but enumerates `scripts/` + `config/` per-file, so `check-engine`
   fails on the cut: **17 failed + 2 collection errors**. Missing:
   `scripts/lan_exposure_audit.py` and `scripts/gnosis_archive.py` (both are also
   `check-engine` *steps*), `scripts/check_secret_history.py`,
   `config/embedding_strategy.yaml` (14 fails),
   `config/wads/arcana_novai/axioms.yaml` (3 fails — sits outside the
   `config/wads/_omega_default/` ALLOW pattern). All absent from `3c051021` too.
   **The cut still fails M13 after this fix.** Repairing it means ADDING paths to
   the public allowlist = sovereignty boundary = Architect ruling.
2. `data/entities/cline_kqv/{session_gnosis.md,soul.yaml}` still ship as symlinks →
   `../../experiments/kq5-godot/gnosis/` (not shipped ⇒ broken in a public clone).
   They survive via the `data/entities/*/…` Explicit-Exclusion globs. The new audit
   reports them every run; `--strict` blocks on them.
3. `DiscoveryOrchestrator._phase_discovery` **does not exist** — its body is
   unreachable dead code after a `return` in `_try_generate`, and
   `_research_subtopic` calls it ⇒ `discover()` raises `AttributeError` **with or
   without vault**. Present at `3c051021` and `17a940dd`. Real P0,
   vault-independent. Filed for its own ticket rather than smuggled in here.

### Also reported, not applied

`--confirm` is impractically slow: the dry run alone took **16m13s**
(~200 regex compiles per file in bash; ~9,000 individual `git rm` index rewrites).
Recommend `git rm --cached --pathspec-from-file=- --pathspec-file-nul`.

### Tool-chain note (M23)

`omega-hub_hivemind_awareness` is **BROKEN** — pydantic
`kwargs Field required` on every call shape, including `heartbeat`.
`omega-hub_hivemind_handoff` works; coordination was posted there instead.
Packets: `ho_a9ce1982f678` (kali, delivered) · `ho_79a120549948` (architect, target
unresolved — no live `architect` entity).

### M28 compliance

Nothing deleted from the working tree. `data/library` + `data/memory` remain on disk
and in the dev index; the fix lives in the *cut script*. `src/omega/vault/` untouched
(5 modules). Throwaway worktrees removed; two pre-existing worktrees
(`/tmp/opencode/debut-cut`, `/tmp/opencode/hubwt`) left untouched — not mine.

---

*⬡ OMEGA ⬡ MAAT ⬡ D-611 ⬡ 2026-10-04*