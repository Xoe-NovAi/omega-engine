# 🔱 Omega Engine — Partition Merge Plan
# AP: AP-MERGE-PLAN-v1.0.0

**Objective**: Merge nvme0n1p3 (omega_library) and nvme0n1p4 (omega_vault) into nvme0n1p2 (root) to eliminate disk space shortages.

## Current Layout
- nvme0n1p2 (110G) = / (ROOT — 99% full)
- nvme0n1p3 (112G) = /media/arcana-novai/omega_library
- nvme0n1p4 ( 16G) = /media/arcana-novai/omega_vault

## Post-Merge Target
- nvme0n1p2 (238G) = / (Unified root)
- omega_library and omega_vault become directories on the root partition.

## Prerequisites
1. **Full Backup**: Must be completed using `scripts/backup_to_8tb.sh` to the 8TB external drive.
2. **Live USB**: Boot from a Live Ubuntu 24.04 LTS USB.
3. **Tools**: `gparted` must be installed on the Live USB.

## Execution Steps (GParted)
1. **Boot**: Boot from Live USB.
2. **Select Disk**: Open GParted and select `/dev/nvme0n1`.
3. **Unmount**: Right-click and unmount `nvme0n1p3` and `nvme0n1p4`.
4. **Delete p4**: Delete the `nvme0n1p4` partition.
5. **Delete p3**: Delete the `nvme0n1p3` partition.
6. **Resize p2**: Right-click `nvme0n1p2` → Resize/Move → Drag the right edge to fill all available unallocated space.
7. **Apply**: Click the checkmark icon to apply all changes.
8. **Reboot**: Reboot into the installed system.

## Post-Reboot Recovery
1. **Mount External**: `sudo mount /dev/sda1 /media/arcana-novai/ffb6feb0-b742-478c-8463-09542edccb42`
2. **Restore Data**: Restore the backed-up `omega_library` and `omega_vault` folders to the root partition (or as desired).
3. **Update fstab**: Remove the old mount entries for p3 and p4 from `/etc/fstab`.
4. **Verify**: Check `df -h /` to confirm ~238G total size.
