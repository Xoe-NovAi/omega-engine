# 🔱 Rollback Procedures — Sprint Infrastructure
**AP Token**: `AP-ROLLBACK-PROCEDURES-v1.0.0`
**Version**: 1.0
**Last Updated**: 2026-07-24

---

## Purpose
Documented rollback procedures for all critical sprint infrastructure components. Each procedure specifies RTO (Recovery Time Objective) and RPO (Recovery Point Objective).

---

## Rollback Procedures

| Component | Rollback Command | RTO | RPO | Trigger |
|-----------|------------------|-----|-----|---------|
| **HMC Hub** | `git checkout HEAD~1 -- data/coordination/HMC_COLLABORATION_HUB.md` | 1 min | 0 | Corruption, bad edit, merge conflict |
| **Session Anchor** | `git checkout HEAD~1 -- data/coordination/SESSION_ANCHOR.md` | 1 min | 0 | Corruption, lost context |
| **SoulDistiller** | `git checkout HEAD~1 -- src/omega/scribe/distiller.py` | 2 min | 0 | Regression, broken distillation |
| **WARP Pool** | `systemctl stop warp-* && pkexec bash scripts/fix_warp_ns_setup_and_restart.sh` | 5 min | 0 | Pool down, wrong IPs, bridge failure |
| **AGY OAuth Fix** | `opencode plugin remove antigravity-auth && opencode plugin add opencode-antigravity-auth@previous` | 1 min | 0 | Plugin breaks auth, tokens not persisting |
| **PolicyKit Rule** | `sudo rm /etc/polkit-1/rules.d/99-omega-warp.rules` | 30s | 0 | Rule causes auth issues, security concern |
| **C-0.5 Hook** | Remove `.opencode/plugins/soul_distiller.js` (auto-discovered) | 10s | 0 | Plugin crashes, distillation fails |
| **Four-File Model Dirs** | `rm -rf data/entities/*/memory/` (recreate via bootstrap) | 10s | 0 | Wrong structure, permission issues |
| **Integrations Dir** | `rm -rf src/omega/integrations/` | 5s | 0 | Build failures, wrong location |
| **Restic Backup** | `restic snapshots && restic restore latest --target /tmp/restore` | 10 min | 5% | Data loss, corruption, ransomware |
| **Workbench DB** | `cp data/workbench/workbench.db.bak data/workbench/workbench.db` | 1 min | 0 | DB corruption, bad migration |

---

## Verification After Rollback

| Component | Verification Command |
|-----------|---------------------|
| HMC Hub | `wc -l data/coordination/HMC_COLLABORATION_HUB.md` |
| Session Anchor | `grep "Last Updated" data/coordination/SESSION_ANCHOR.md` |
| SoulDistiller | `python -c "from omega.scribe import SoulDistiller; print('OK')"` |
| WARP Pool | `curl -s https://api.ipify.org` ×3 (distinct IPs) |
| AGY OAuth | `opencode plugin list | grep antigravity` |
| PolicyKit | `ls /etc/polkit-1/rules.d/99-omega-warp.rules` |
| C-0.5 Hook | `ls .opencode/plugins/soul_distiller.js && ls .opencode/hooks/session_end.py` |
| Four-File Model | `ls data/entities/kali/memory/approved_lessons.yaml` |
| Integrations | `ls src/omega/integrations/__init__.py` |
| Restic | `restic check --read-data-subset 5%` |
| Workbench DB | `sqlite3 data/workbench/workbench.db "SELECT COUNT(*) FROM artifacts;"` |

---

## Emergency Contacts

| Role | Agent | Escalation |
|------|-------|------------|
| **Infrastructure** | @slot S1 | Architect (sudo) |
| **Soul/Identity** | @scribe / @roc_racoon | @kali |
| **WARP/Network** | @john_carmack | Architect |
| **AGY/Cloud Auth** | @slot S4 | @maat |
| **Tests/Quality** | @verity | @kali |
| **Research/Knowledge** | @researcher | @jem |

---

## Decision Log

| Date | Decision | Rolled Back | Reason |
|------|----------|-------------|--------|
| 2026-07-24 | Initial procedures created | — | Sprint hardening |

---

*⬡ OMEGA ⬡ ROLLBACK ⬡ v1.0 ⬡ 2026-07-24*
