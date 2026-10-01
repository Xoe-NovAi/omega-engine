Found it at `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/federation/DIALECTIC_ANTIGRAVITY_TO_MAKALI_20260920_2340.md`.

**Key forensic corrections from Antigravity's response:**

| Question | Original Claim | Corrected Finding |
|----------|---------------|-------------------|
| **Q1: `or-key.md`** | Unknown provenance | **Pre-existing** (mtime 2026-08-30), never committed, explicitly gitignored by name. **CONTAINMENT** — readable by all agents since Aug 30. |
| **Q2: `ACCOUNT_MAP.yaml`** | MaKaLi's git log showed no history | **Confirmed tracked** at HEAD (`b44b34be` ancestor). MaKaLi's `git log --all` missed it due to cline checkpoint commit chain. `git rm --cached` confirmed safe. |
| **Q3: `data/metrics/`** | "Potentially tracked" | **48 files definitively tracked** (3.6MB `free_model_probes.jsonl`, etc.). **Upgraded to P1 blocker**. |
| **Q4: `PUBLIC_ALLOWLIST.txt`** | "Too coarse" | **Counter-proposal accepted** — allowlist uses explicit file allows, not directory wildcards. Defer restructure to Phase 2. |
| **Q5: Node 1 `mcp-server`** | Unknown | **Same race confirmed** — Node 1 has `omega-hub` but not `n0` in `allowed_hosts`. Wildcard `*.tail51f14a.ts.net` covers it now, but explicit entries needed. |
| **Q6: `pyrage/argon2`** | Potential debut blocker | **Not a blocker** — graceful `try/except` in `crypto.py` allows import; crash only at `VaultCrypto()` instantiation. Audit call sites only. |

**Updated P0 Queue (corrected):**
```bash
# P0-1: Delete live key + revoke
rm or-key.md

# P0-2: De-track ACCOUNT_MAP.yaml
git rm --cached data/entities/antigravity/knowledge/ACCOUNT_MAP.yaml
echo 'data/entities/*/knowledge/ACCOUNT_MAP.yaml' >> .gitignore

# P0-3: De-track metrics (48 files) — NEW P0
git rm --cached data/metrics/*.jsonl data/metrics/*.json data/metrics/.key_health_cache 2>/dev/null || true
echo 'data/metrics/*.jsonl' >> .gitignore
echo 'data/metrics/*.json' >> .gitignore
echo 'data/metrics/.key_health_cache' >> .gitignore

# P0-4: Scan
make check-mandates
```

**Antigravity accepted all three MaKaLi counter-proposals** (defer allowlist restructure, `pyrage` audit only if `VaultCrypto()` called, Node 1 offline = validated dormancy).

The file is at `docs/federation/DIALECTIC_ANTIGRAVITY_TO_MAKALI_20260920_2340.md` (also mirrored at `data/coordination/`).
