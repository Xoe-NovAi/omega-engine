# 🔱 Omega Engine — Persistent Permissions Resolution
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ jem-2.0 ⬡ researcher ⬡ trc_research_perm ⬡ PHASE-I

**AP Token**: `AP-RESEARCH-PERM-RESOLUTION-v1.0.0`
**Status**: 🔬 RESEARCH REQUEST
**Requested**: 2026-05-22
**Target**: Full root cause analysis + prevention protocol
**Researcher**: Jem 2.0 (Gemma 4-31B)

---

## §1 Problem Statement

The Omega Engine repo experienced a **P0 permission blocker** across 3 development sessions. Every file in the repository was owned by **UID 101000** (rootless Podman container user) instead of **UID 1000** (arcana-novai). This blocked `make test`, file writes, pytest caching, and all code development.

## §2 Root Cause Hypothesis

Rootless Podman subuid mapping (`arcana-novai:100000:65536`):
- Container UID 1001 → Host UID 100000 + 1001 = **101000**
- Container processes writing to volume-mounted host directories stamp files with UID 101000
- Multiple containers (iris, roc_racoon) mount the workspace

## §3 Resolution Achieved

**Command**: `sudo chown -R 1000:1000 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/`
**Verification**: `make test` → **236/236 passing** in 9.49s

## §4 Research Questions

### 4.1 Which containers leak UID 101000?
- [ ] Check all running podman containers for volume mounts
- [ ] Identify which container processes write to host filesystem
- [ ] Determine the exact UID mapping for each container

### 4.2 What paths were affected?
- [ ] `data/` (checkpoints, sessions)
- [ ] `tests/` (pytest cache)
- [ ] `config/` (iris read-only mount)
- [ ] `docs/` (handoffs, research)
- [ ] `src/` (runtime files)

### 4.3 Prevention mechanisms
- [ ] `:U` flag on all Podman volume mounts
- [ ] `--userns=keep-id` in container launch configs
- [ ] Post-start chown systemd oneshot
- [ ] Read-only volumes (`:ro`) where possible

### 4.4 The OpenCode Terminal Visibility Anomaly
During resolution, a strange symptom occurred:
- User's terminal showed `chown` succeeding (files owned by 1000)
- OpenCode agent (same machine, same path) consistently saw UID 101000
- Persisted across 3+ `sudo chown` attempts

## §5 Deliverables

1. **Root Cause Analysis** — Full chain: subuid mapping → container user → volume mount → host file ownership
2. **Prevention Protocol** — Canonical "Omega Engine Container Volume Mount Standard"
3. **Cleanup Checklist** — Any remaining 101000 files, `.venv` path drift, stale paths
4. **Anomaly Report** — Terminal-vs-OpenCode discrepancy documented

## §6 Research Method

```bash
# 1. Check all running container mounts
podman ps --format "{{.Names}}" | xargs -I {} podman inspect {} --format '{{.Name}}: {{range .Mounts}}{{.Source}} ({{.Options}}) {{end}}'

# 2. Scan for residual 101000 files
find /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/ -user 101000 -type f 2>/dev/null | wc -l

# 3. Check venv path drift
head -3 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/pyvenv.cfg

# 4. Check subuid mapping
cat /etc/subuid | grep arcana-novai
```

