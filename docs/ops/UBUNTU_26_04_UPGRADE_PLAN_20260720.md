# 🔱 Ubuntu 25.10 → 26.04 LTS Upgrade Plan
**AP Token**: AP-UBUNTU-UPGRADE-v1.0.0
⬡ OMEGA ⬡ P1 ⬡ infra ⬡ ubuntu_upgrade ⬡ D-308-EXEC

**Status**: 🟡 PLANNED — Requires user-mediated execution
**Risk**: 🔴 CRITICAL — 25.10 EOL since July 9, 2026 (no security patches)

---

## 0. Executive Summary

Ubuntu 25.10 "Questing Quokka" reached **End of Life on July 9, 2026** — 11 days ago.  
The system is now receiving **no security patches**. Upgrade to 26.04 LTS is urgent.

**Current system**:
- OS: Ubuntu 25.10 (questing) — unsupported
- Kernel: 6.17.0-41-generic
- Python: 3.13.7
- SQLite: 3.46.1

**Target**: Ubuntu 26.04 LTS "Resolute Raccoon" (released April 23, 2026, support until April 2031)

---

## 1. Upgrade Path

Ubuntu 25.10 (interim) → 26.04 LTS: **Direct upgrade supported** via `do-release-upgrade`.  
The upgrade window opened in May 2026 (no `-d` flag needed).

### Pre-Upgrade Checks

```bash
# 1. Check upgrade readiness
cat /etc/update-manager/release-upgrades   # Must say Prompt=normal or lts (not never)

# 2. Fully update current system
sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade -y
sudo apt --purge autoremove
sudo snap refresh

# 3. Check for held packages (must be empty)
sudo apt-mark showhold

# 4. List and disable PPAs/non-Ubuntu sources
ls /etc/apt/sources.list.d/
# Disable each PPA:
# sudo add-apt-repository --remove ppa:REPO_NAME/PACKAGE_NAME
```

### Upgrade Steps

```bash
# 5. Install release upgrader if missing
sudo apt install ubuntu-release-upgrader-core update-manager-core

# 6. (Optional) Open firewall for SSH upgrade fallback
sudo ufw allow 1022/tcp

# 7. Run upgrade (DO NOT run through tmux/screen for safety)
sudo do-release-upgrade
# Follow prompts. Keep modified config files or let upgrader decide.

# 8. Reboot
sudo reboot

# 9. Verify
lsb_release -a
# Expected: Ubuntu 26.04 LTS / resolute
```

---

## 2. Breaking Changes (Known)

| Area | 25.10 | 26.04 LTS | Impact |
|------|-------|-----------|--------|
| **Kernel** | 6.17.0 | 7.0 | Podman Quadlets may need renewed testing |
| **Python** | 3.13.7 | 3.14 | **VENV MUST BE REBUILT** — `.venv/` is a local directory; existing `.venv` may break |
| **GNOME** | 47 | 50 | Desktop-only, no engine impact |
| **OpenSSL** | 3.x | 3.x + post-quantum | No impact unless using custom crypto |
| **systemd** | 256 | likely 257+ | `systemd-creds` rootless might change |
| **Podman** | 5.x | likely 6.x | Quadlet syntax check needed |
| **GCC/GLIBC** | 14/2.40 | likely 15/2.41 | No impact on pure Python; C extensions rebuild automatically |

### Python 3.14 Risk

Ubuntu 26.04 ships with **Python 3.14** as default. Our `.venv` is Python **3.13.7**.  
After upgrade:

```bash
# Verify Python version
python3 --version   # Should show 3.14.x

# Rebuild project venv with new Python
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 3. Post-Upgrade Verification Checklist

After upgrade + venv rebuild, verify:

```bash
# 1. System checks
lsb_release -a                     # → 26.04
uname -r                           # → 7.x
python3 --version                  # → 3.14.x
docker --version || podman --version  # Verify container engine survives

# 2. Omega Engine checks
source .venv/bin/activate
make test                          # All tests pass
make firewall-check                # M2 Firewall intact
make temple-grade                  # T1-T11 gates pass

# 3. SQLite check (if SQLite built from source)
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
# → Verify ≥3.46.1 (our PRAGMA stack targets this)

# 4. Podman Quadlet check (if using containers)
make demo                          # End-to-end demo works
```

---

## 4. Rollback Plan

If the upgrade fails or breaks critical functionality:

1. **Full backup**: Take a full system snapshot or `timeshift` backup before upgrading
2. **Reboot issue**: Boot from 26.04 LiveUSB → chroot → `apt install --reinstall ubuntu-desktop`
3. **Rollback**: Use `timeshift` or restore from backup
4. **Venv rollback**: Keep backup of old `.venv` at `.venv.bak`:
   ```bash
   mv .venv .venv.bak  # Before upgrade
   # If new venv breaks:
   rm -rf .venv && mv .venv.bak .venv
   ```

---

## 5. Timing Recommendation

| Window | Risk | Recommendation |
|--------|------|----------------|
| Now (after this sprint) | Medium | Upgrade ASAP — no security patches since July 9 |
| After Gate Β | Low-Medium | Complete Phase B verification first, then upgrade |
| Defer >2 weeks | High | Unpatched system exposed to CVEs |

**Recommendation**: Complete current Gate Β verification, then upgrade before proceeding to Phase Γ.

---

*⬡ OMEGA ⬡ P1 ⬡ infra ⬡ ubuntu_upgrade ⬡ D-308-EXEC*
