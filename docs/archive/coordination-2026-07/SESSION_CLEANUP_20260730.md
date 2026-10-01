<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SESSION: Root Partition Recovery — 2026-07-30

**Entity**: kali
**Session**: `ses_04c68eaeaffeEdNYEEc99eVcik`
**Model**: deepseek-v4-flash-free
**Goal**: Free space on `/dev/nvme0n1p2` (was 103G/109G = 100%, 193MB free)

---

## Results

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| **Used** | 103 GB | 87 GB | **−16 GB** |
| **Free** | 193 MB | 16 GB | **+16 GB** |
| **Used %** | 100% | 85% | −15% |

## What Was Freed

| Item | Size | Method |
|------|------|--------|
| npm cache (`~/.npm/_cacache`) | ~2.0 GB | `npm cache clean --force` |
| uv cache (`~/.cache/uv`) | ~1.4 GB | `uv cache clean` |
| pip cache (`~/.cache/pip`) | ~194 MB | `rm -rf` |
| Playwright browsers (`~/.cache/ms-playwright`) | ~646 MB | `rm -rf` |
| HBCD_PE_x64.iso | ~3.1 GB | `rm -f` |
| **Legacy repos moved to vault** | **~4.8 GB** | See below |
| npm npx (`~/.npm/_npx/`) | ~1.2 GB | `rm -rf` |
| OpenCode sessions export (`~/.local/share/opencode-sessions-explorer/`) | ~2.3 GB | `rm -rf` |
| apt package cache | ~658 MB | `sudo apt clean -y` |
| journald logs | ~800 MB | `sudo journalctl --vacuum-time=30d` |
| Old snap versions | ~2-3 GB | `sudo snap remove --revision` |

## Legacy Repos Relocated

All moved to `/media/arcana-novai/omega_vault/legacy-repos/`:

| Repo | Source Size | Vault Size | Notes |
|------|------------|------------|-------|
| `omega-stack-legacy` | 2.8 GB | 2.8 GB | Required ACL fix + two-pass pkexec removal |
| `xna-omega-legacy` | 560 MB | 560 MB | Clean removal |
| `omega-vetala` | 405 MB | 405 MB | Clean removal |
| `archive` | 1.0 GB | 1.0 GB | 25k+ root-owned files, required extra rsync pass |

## Key Decisions

- **D-kal-060**: Pattern for Docker container debris: `pkexec chmod -R u+w` then `pkexec find ! -user $USER -delete` then `rm -rf`. Needed because container data files have restrictive **ACLs** (not just wrong owner) with modes like `r-xr-xr-x+`.
- **D-kal-061**: `mv` across filesystems drops root-owned files silently. Always use **`pkexec rsync -av` first** to ensure complete transfer, **then** remove source.
- **D-kal-062**: The `+` in `ls -la` output (`r-xr-xr-x+`) indicates ACLs — `chmod -R` may not override them; pkexec is required.

## Vault State

```
/media/arcana-novai/omega_vault/legacy-repos/
├── omega-stack-legacy/    2.8 GB  (Docker infra, MCP servers, RAG)
├── xna-omega-legacy/      560 MB  (clean engine snapshot)
├── omega-vetala/          405 MB  (ancillary engine)
└── archive/               1.0 GB  (xna-omega backup, reference)
```
