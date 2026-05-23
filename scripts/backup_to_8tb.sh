#!/bin/bash
# 🔱 Omega Engine — Full System Backup to 8TB External Drive
# AP: AP-BACKUP-v1.0.0
#
# Backs up critical partitions to the 8TB external drive.
# Excludes virtual filesystems, caches, and rebuildable artifacts.

set -euo pipefail

BACKUP_ROOT="/media/arcana-novai/ffb6feb0-b742-478c-8463-09542edccb42/omega_backup/$(date +%Y%m%d_%H%M%S)"
EXCLUDE_FILE="/tmp/rsync_exclude.txt"

# Verify mount
if [ ! -d "/media/arcana-novai/ffb6feb0-b742-478c-8463-09542edccb42" ]; then
    echo "ERROR: 8TB drive not mounted"
    exit 1
fi

# Verify space
AVAILABLE=$(df --output=avail /media/arcana-novai/ffb6feb0-b742-478c-8463-09542edccb42 | tail -1)
echo "8TB drive has $(numfmt --to=iec $AVAILABLE) available"

# Excludes
cat > "$EXCLUDE_FILE" << 'EOF'
/proc/*
/sys/*
/dev/*
/tmp/*
/run/*
/mnt/*
/media/*
/lost+found
/swapfile
/var/cache/apt/archives/*.deb
/var/lib/apt/lists/*
/home/*/.cache/*
/home/*/.local/share/Trash/*
/home/*/snap/*
EOF

# Backup root partition (p2)
echo "Backing up / (nvme0n1p2)..."
mkdir -p "$BACKUP_ROOT/root"
sudo rsync -aAXv --delete --exclude-from="$EXCLUDE_FILE" / "$BACKUP_ROOT/root/"

# Backup omega_library (p3)
echo "Backing up omega_library (nvme0n1p3)..."
mkdir -p "$BACKUP_ROOT/omega_library"
sudo rsync -aAXv --delete /media/arcana-novai/omega_library/ "$BACKUP_ROOT/omega_library/"

# Backup omega_vault (p4)
echo "Backing up omega_vault (nvme0n1p4)..."
mkdir -p "$BACKUP_ROOT/omega_vault"
sudo rsync -aAXv --delete /media/arcana-novai/omega_vault/ "$BACKUP_ROOT/omega_vault/"

# Summary
echo "=== Backup Complete ==="
echo "Location: $BACKUP_ROOT"
du -sh "$BACKUP_ROOT"/* | sort -rh
df -h /media/arcana-novai/ffb6feb0-b742-478c-8463-09542edccb42
