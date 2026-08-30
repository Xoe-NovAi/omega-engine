#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# Setup Litestream sidecar for omega_memory.db
# AP: AP-LITESTREAM-BACKUP-v1.0.0
#
# Installs Litestream v0.5.x, writes the systemd unit, and starts the
# replication sidecar. Idempotent — safe to re-run.
set -euo pipefail

LITESTREAM_VERSION="${LITESTREAM_VERSION:-0.5.6}"
OMEGA_USER="${OMEGA_USER:-omega}"
OMEGA_DATA_DIR="${OMEGA_DATA_DIR:-/var/lib/omega}"
LITESTREAM_CONFIG="${LITESTREAM_CONFIG:-/etc/litestream.yml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Litestream v${LITESTREAM_VERSION}..."

# 1. Download & install binary
cd /tmp
if [[ ! -f /usr/local/bin/litestream ]]; then
    ARCH="$(uname -m)"
    case "${ARCH}" in
        x86_64) LITESTREAM_ARCH="amd64" ;;
        aarch64|arm64) LITESTREAM_ARCH="arm64" ;;
        *) echo "Unsupported architecture: ${ARCH}" >&2; exit 1 ;;
    esac
    curl -L "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-v${LITESTREAM_VERSION}-linux-${LITESTREAM_ARCH}.tar.gz" \
        -o /tmp/litestream.tar.gz
    tar -xzf /tmp/litestream.tar.gz -C /tmp/
    sudo mv /tmp/litestream /usr/local/bin/
    sudo chmod +x /usr/local/bin/litestream
    rm -f /tmp/litestream.tar.gz
    echo "    Binary installed at /usr/local/bin/litestream"
else
    echo "    Binary already present at /usr/local/bin/litestream — skipping"
fi

# 2. Create config from template (only if missing)
if [[ ! -f "${LITESTREAM_CONFIG}" ]]; then
    sudo install -m 0640 -o root -g "${OMEGA_USER}" \
        "${SCRIPT_DIR}/../config/litestream.yml" "${LITESTREAM_CONFIG}"
    echo "==> Created ${LITESTREAM_CONFIG} — please fill in bucket + credentials."
    echo "    Set LITESTREAM_BUCKET, LITESTREAM_ACCESS_KEY_ID, LITESTREAM_SECRET_ACCESS_KEY"
    echo "    in /etc/litestream.env (recommended) or systemd unit Environment=."
    exit 1
fi

# 3. Create systemd service (config-as-code: copy from repo, not heredoc)
SERVICE_SRC="${SCRIPT_DIR}/../config/systemd/omega-litestream.service"
if [[ ! -f "${SERVICE_SRC}" ]]; then
    echo "ERROR: ${SERVICE_SRC} not found. Repo layout broken." >&2
    exit 1
fi
sudo install -m 0644 -o root -g root \
    "${SERVICE_SRC}" /etc/systemd/system/litestream.service

# 4. Ensure data dir exists & is writable
if ! id "${OMEGA_USER}" &>/dev/null; then
    sudo useradd --system --no-create-home --shell /usr/sbin/nologin "${OMEGA_USER}"
fi
sudo mkdir -p "${OMEGA_DATA_DIR}"
sudo chown -R "${OMEGA_USER}:${OMEGA_USER}" "${OMEGA_DATA_DIR}"

# 5. Enable & start
sudo systemctl daemon-reload
sudo systemctl enable litestream
sudo systemctl restart litestream

echo "==> Litestream v${LITESTREAM_VERSION} installed and running."
echo "==> Verify with:  sudo systemctl status litestream"
echo "==> Verify replication: litestream snapshots -config ${LITESTREAM_CONFIG}"
echo "==> Test restore: sudo bash ${SCRIPT_DIR}/restore_litestream.sh /tmp/restored.db"
