---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

id: kb-0005
type: knowledge
domain: operations
tags: [system-maintenance, disk-space, journalctl, cache, snap, flatpak, opencode, pkexec, runbook]
sensitivity: internal
maintainer: roc_racoon
created: 2026-09-01
reviewed: 2026-09-01
modified: 2026-09-01
supersedes: null
superseded_by: null
status: ACTIVE
research_source: null
reinforcement_count: 0
---

# 🔱 Omega Engine — Routine System Maintenance KB

**Domain**: Routine Linux system maintenance — disk-space recovery, cache hygiene, and log management for the Omega Engine host.
**Version**: 1.0.0
**Last Updated**: 2026-09-01
**Maintainer**: roc_racoon
**Status**: ACTIVE

---

## Changelog

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-09-01 | 1.0.0 | roc_racoon | Initial creation — distilled from the 2026-09-01 disk emergency session (109G partition at 100%, recovered ~5GB) |

---

## Domain Overview

**What**: This KB is the canonical runbook for keeping the Omega Engine host's main partition healthy. It captures the verified disk-analysis workflow, the safe-to-clear cache inventory, and the operational lessons learned from the 2026-09-01 emergency (partition at 100%, 129MB free).

**Why**: The Omega Engine runs heavy AI tooling (OpenCode DB ~27GB, container images, snap packages, model caches). These accumulate silently and drive the partition to 100%, which breaks writes, crashes services, and stalls the fleet. A repeatable maintenance procedure prevents emergencies.

**Who needs this**: Any agent performing host maintenance, the Architect before a debut/release, and any entity that observes disk-pressure warnings.

---

## Core Knowledge

### 1. The Disk Analysis Workflow (5-Tier)

**What**: A deterministic procedure to find reclaimable space before touching anything.
**Why**: Blind deletion is dangerous. The workflow maps the partition, then drills into each consumer.

```bash
# Tier 1 — Partition state
df -h / /home

# Tier 2 — Home top-level consumers
du -h --max-depth=1 /home/arcana-novai/ | sort -rh | head -20

# Tier 3 — The big three AI data dirs
du -h --max-depth=1 /home/arcana-novai/.local/share/ | sort -rh | head -20
du -h --max-depth=1 /home/arcana-novai/.cache/ | sort -rh | head -30
du -h --max-depth=1 /home/arcana-novai/.config/ | sort -rh | head -20

# Tier 4 — System-level consumers (needs pkexec)
pkexec du -sh /var/log/journal/
journalctl --disk-usage
du -h /var/cache/apt/archives/

# Tier 5 — Containers + snap
podman images --format "{{.Repository}}:{{.Tag}} {{.Size}}"
docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}"
du -h --max-depth=1 /home/arcana-novai/snap/ | sort -rh | head -10
```

### 2. Verified Safe-to-Clear Inventory (2026-09-01)

**What**: Items cleared without data loss, with measured sizes from the 2026-09-01 session.
**Why**: These are the first-line reclaim targets. All rebuild automatically or are pure cache.

| Item | Size | Command | Rebuilds? |
|------|------|---------|-----------|
| Sessions Explorer search cache | ~778M | `rm -rf ~/.local/share/opencode-sessions-explorer/*` | Yes — rebuilds from opencode.db on next search |
| Systemd journal (rotate + vacuum) | ~3.6G | `pkexec journalctl --rotate && pkexec journalctl --vacuum-size=200M` | No — logs are disposable |
| APT package cache | ~97M | `pkexec apt clean` | Yes — re-downloads on demand |
| Podman dangling images | ~136M | `podman image prune -f` | No — dangling layers only |
| OpenCode package cache | ~193M | `rm -rf ~/.cache/opencode/` | Yes — re-fetches on demand |

### 3. The Journal Rotate-Then-Vacuum Lesson (CRITICAL)

**What**: `journalctl --vacuum-time=2w` and `--vacuum-size=200M` **silently free 0B** when the journal is large and unrotated.
**Why**: Vacuum only touches *archived* journals. Active journals are excluded. On a busy host the active journal can be gigabytes.
**Fix**: Always rotate first, then vacuum:

```bash
pkexec journalctl --rotate
pkexec journalctl --vacuum-size=200M
```

**Measured result**: Bare vacuum → 0B freed. Rotate-then-vacuum → 3.6G freed.

### 4. pkexec vs sudo in Non-Interactive Sessions

**What**: `sudo` fails with "a terminal is required to read the password" in agent sessions. `pkexec` works (pops the polkit GUI).
**Why**: Agents run without a TTY. sudo's password prompt cannot be answered; pkexec delegates to the desktop polkit agent.
**Pattern**:

```bash
# ❌ Fails in agent sessions
sudo apt clean

# ✅ Works (polkit GUI prompt)
pkexec apt clean
```

### 5. The OpenCode DB Exclusion Rule

**What**: `~/.local/share/opencode/opencode.db` is ~27GB and is the session history store. **Do not touch it without explicit Architect instruction.**
**Why**: It is the fleet's memory. Deleting or vacuuming it destroys session provenance, compaction history, and the sessions-explorer index source.
**Related**: `opencode.db-wal` (write-ahead log) is transient and small (~150M); the sessions-explorer cache (item 2) is the *derived* index and is safe to clear because it rebuilds from the DB.

### 6. Second-Line Targets (Require Verification)

**What**: Larger consumers that may be reclaimable but need a human go/no-go.
**Why**: These are tool installs and caches for tools that may still be in use.

| Item | Size | Question to Ask |
|------|------|-----------------|
| snap copilot-cli | 2.4G | Still using the copilot snap? |
| snap chromium | 847M | Using snap chromium or native browser? |
| `~/.copilot/pkg` | 1.4G | Still using Copilot extension? |
| `~/.cline/data` | 1.0G | Still using Cline? |
| `~/.grok/downloads` + `sessions` | 634M | Need Grok local data? |
| `~/.codex/packages` + `.tmp` | 371M | Still using Codex? |
| Flatpak Freedesktop SDK | ~1.8G | Anything depend on it? |
| `~/.lmstudio/extensions` | 1.7G | Still using LM Studio? |
| `~/.antigravity/extensions` | 537M | Still using Antigravity? |
| `~/archive/foundation-legacy` | 861M | Legacy code — keep? |
| `~/Downloads/thunderbird.tmp` | 705M | Temporary file? |

### 7. Recurring Maintenance Cadence

**What**: A suggested schedule to prevent the 100% emergency from recurring.
**Why**: The 2026-09-01 session recovered ~5GB but the partition sits at 96%. Proactive cadence is cheaper than emergency surgery.

| Frequency | Action | Est. Reclaim |
|-----------|--------|--------------|
| Weekly | Journal rotate + vacuum to 200M | 1–4G |
| Weekly | `podman image prune -f` + `docker image prune -f` | 100–500M |
| Monthly | Sessions Explorer cache clear | 500M–1G |
| Monthly | `pkexec apt clean` | 50–150M |
| Monthly | Review second-line targets with Architect | 2–10G |
| Quarterly | Full 5-tier analysis + report | 5–15G |

---

## Known Antipatterns

| Antipattern | Symptom | Correct Approach |
|-------------|---------|-----------------|
| Vacuuming without rotating | `journalctl --vacuum-*` reports "freed 0B" | Always `--rotate` first |
| Using `sudo` in agent sessions | "a terminal is required to read the password" | Use `pkexec` |
| Deleting `opencode.db` for space | Fleet memory loss, provenance corruption | Clear the sessions-explorer *cache* instead |
| `rm -rf` on tool dirs without asking | Broken tooling, lost sessions | Verify tool usage with Architect first (second-line table) |
| Only checking `df -h` | Misses the actual consumers | Run the full 5-tier analysis |
| `apt clean` without pkexec | Permission denied, no reclaim | `pkexec apt clean` |

---

## References

- `docs/kb/MEMORY_MANAGEMENT_KB.md` — memory/swap maintenance (zswap, zRAM, cgroups)
- `docs/operations/SOVEREIGN_HEALTH_CHECK.md` — 5-tier engine health validation
- `docs/ops/UBUNTU_26_04_UPGRADE_PLAN_20260720.md` — OS upgrade plan
- `data/entities/roc_racoon/workspace/ZRAM_ZSWAP_DEEPENED_ANALYSIS.md` — swap subsystem deep-dive
- `data/entities/roc_racoon/workspace/zram_integrated_plan.md` — integrated memory plan
- `data/coordination/ROC_RACOON_WORKSPACE_LOCK_20260901.md` — session coordination record

## Evolution Notes

- **Known gap**: No automated disk-pressure alerting. A `df -h` threshold check (e.g., warn at 90%) could be added to the health check protocol.
- **Known gap**: The second-line inventory (item 6) is a snapshot from 2026-09-01. Sizes drift as tools update; re-measure before acting.
- **Known gap**: Flatpak SDK removal (1.8G) was identified but not executed — needs a dependency check before it becomes safe-to-clear.
- **To investigate**: Whether a systemd timer could automate the weekly journal rotate+vacuum without root (user-level journal rotation).
- **To investigate**: Whether `opencode.db` can be safely VACUUM'd (SQLite) to reclaim pages without losing history — do NOT attempt without Architect approval.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_kb ⬡ 2026-09-01*