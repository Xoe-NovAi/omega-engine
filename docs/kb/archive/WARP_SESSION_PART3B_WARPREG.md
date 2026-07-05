# 🔱 WARP Proxy Pool — Session Knowledge Capture (Part 3b: warp-reg@.service)
# ⬡ OMEGA ⬡ KALI ⬡ WARP-KB ⬡ 2026-07-05

---

## §1 warp-reg@.service (Complete Unit File)

This unit file handles the first-boot WARP registration for each instance. It uses a global flock lock to ensure strict sequential execution across all 3 instances, preventing IPC socket conflicts on the host's single warp-svc daemon.

```ini
[Unit]
Description=First-boot WARP Registration for Instance %i
Documentation=file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md
After=warp-ns-prep@%i.service
Before=warp-node@%i.service
DefaultDependencies=no

[Service]
Type=oneshot
RemainAfterExit=yes
# Runs on HOST — uses HOST warp-svc for registration (single daemon), copies config to custom path
# Strict sequential execution via flock on global lock file
ExecStart=/usr/bin/flock -x /run/warp-reg-global.lock -c '\
  set -e; \
  NS="warp_node_%i"; \
  CONF="/var/lib/cloudflare-warp-%i"; \
  DEFAULT="/var/lib/cloudflare-warp"; \
  \
  # 1. Stop host warp-svc if running; \
  /usr/bin/systemctl stop warp-svc 2>/dev/null || true; \
  \
  # 2. Kill ALL warp-svc processes; \
  /usr/bin/pkill -9 warp-svc 2>/dev/null || true; \
  \
  # 3. Wait for process cleanup and socket release; \
  sleep 2; \
  \
  # 4. Clean up stale IPC socket; \
  rm -f /run/cloudflare-warp/warp_service 2>/dev/null || true; \
  \
  # 5. AGGRESSIVE: Remove immutable flag, then nuke ALL stale registration files + SQLite WAL; \
  /usr/bin/chattr -i "$${DEFAULT}/reg.json" "$${DEFAULT}/conf.json" "$${DEFAULT}/warp.db" \
    "$${DEFAULT}/settings.json" "$${DEFAULT}/final-overrides-settings.json" \
    "$${DEFAULT}/warp.db-wal" "$${DEFAULT}/warp.db-shm" 2>/dev/null || true; \
  /usr/bin/chattr -i "$${CONF}/reg.json" "$${CONF}/conf.json" "$${CONF}/warp.db" \
    "$${CONF}/warp.db-wal" "$${CONF}/warp.db-shm" 2>/dev/null || true; \
  rm -rf "$${DEFAULT}/reg.json" "$${DEFAULT}/conf.json" "$${DEFAULT}/warp.db" \
         "$${DEFAULT}/settings.json" "$${DEFAULT}/final-overrides-settings.json" \
         "$${DEFAULT}/warp.db-wal" "$${DEFAULT}/warp.db-shm" \
         "$${CONF}/reg.json" "$${CONF}/conf.json" "$${CONF}/warp.db" \
         "$${CONF}/warp.db-wal" "$${CONF}/warp.db-shm"; \
  \
  # 6. Ensure custom config dir exists; \
  mkdir -p "$${CONF}"; \
  \
  # 7. Set up warp-svc directories (StateDirectory, RuntimeDirectory, LogsDirectory); \
  mkdir -p /var/lib/cloudflare-warp /run/cloudflare-warp /var/log/cloudflare-warp; \
  chmod 755 /var/log/cloudflare-warp; \
  \
  # 8. Start host warp-svc (on HOST, not in namespace) for registration; \
  LOGS_DIRECTORY=/var/log/cloudflare-warp /usr/bin/warp-svc & \
  WARP_PID=$!; \
  \
  # Cleanup background warp-svc on script exit; \
  trap "kill $${WARP_PID} 2>/dev/null || true; wait $${WARP_PID} 2>/dev/null || true" EXIT; \
  \
  # 9. Wait for IPC readiness (poll warp-cli status up to 30s); \
  for i in $(seq 1 60); do \
    if /usr/bin/warp-cli --accept-tos status &>/dev/null 2>&1; then \
      break; \
    fi; \
    sleep 0.5; \
  done; \
  \
  # 10. RESET daemon internal state (clears "old registration" memory); \
  /usr/bin/warp-cli --accept-tos settings reset; \
  \
  # 11. Register new WARP license on HOST (creates reg.json in DEFAULT); \
  /usr/bin/warp-cli --accept-tos registration new && \
  \
  # 12. Copy ALL config from DEFAULT to custom path for warp-node --config-dir; \
  cp -r "$${DEFAULT}"/* "$${CONF}"/'

# SECURITY: CAP_NET_ADMIN for ip netns, CAP_SYS_ADMIN for setns + pkill + chattr
NoNewPrivileges=true
RestrictAddressFamilies=AF_INET AF_UNIX AF_NETLINK
CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN

# Allow up to 180s for registration (warp-svc start ~5s + DNS + tunnel connect ~60s + registration ~5s)
TimeoutStartSec=180

[Install]
WantedBy=multi-user.target
```

---

*Part 3b of 4 — warp-reg@.service*
*Next: Part 3c — warp-node@.service & socat-bridge@.service*