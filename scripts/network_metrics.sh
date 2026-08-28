#!/usr/bin/env bash
# network_metrics.sh — Capture WiFi/network state + probe latency correlation
# Usage: run via cron every 5 min; logs to data/metrics/network_probes.jsonl
# Captures: SSID, BSSID, signal, channel, frequency, rate, IP, gateway, DNS, DHCP, latency
# Correlates: network state with provider probe success/failure for diagnostic analysis

set -uo pipefail

LOG_DIR="${HOME}/Documents/Xoe-NovAi/omega-engine/data/metrics"
LOG_FILE="${LOG_DIR}/network_probes.jsonl"
PROBE_LOG="${LOG_DIR}/free_model_probes.jsonl"
mkdir -p "$LOG_DIR"

# === NETWORK STATE ===
# Use iw dev (clean output, no colon-escaping issues)
WIFI_IFACE=$(iw dev 2>/dev/null | grep -oP 'Interface \K\w+' | head -1)
if [[ -n "$WIFI_IFACE" ]] && iw dev "$WIFI_IFACE" link 2>/dev/null | grep -q "SSID"; then
    SSID=$(iw dev "$WIFI_IFACE" link 2>/dev/null | grep 'SSID:' | sed 's/.*SSID: //' | head -1)
    BSSID=$(iw dev "$WIFI_IFACE" link 2>/dev/null | grep -oP 'Connected to \K[0-9a-f:]+' | head -1)
    FREQ=$(iw dev "$WIFI_IFACE" link 2>/dev/null | grep -oP 'freq: \K\d+' | head -1)
    SIGNAL=$(iw dev "$WIFI_IFACE" link 2>/dev/null | grep -oP 'signal: \K-?\d+' | head -1)
    RX_BITRATE=$(iw dev "$WIFI_IFACE" link 2>/dev/null | grep -oP 'rx bitrate: \K[0-9.]+ \w+' | head -1)
    TX_BITRATE=$(iw dev "$WIFI_IFACE" link 2>/dev/null | grep -oP 'tx bitrate: \K[0-9.]+ \w+' | head -1)
    RATE="${RX_BITRATE} / ${TX_BITRATE}"
    # Get security info
    SECURITY=$(iw dev "$WIFI_IFACE" info 2>/dev/null | grep -oP 'type \K\w+' | head -1)
else
    SSID="ethernet"
    BSSID="wired"
    SIGNAL="-"
    FREQ="-"
    RATE="-"
    SECURITY="-"
    WIFI_IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
fi

# Fallback: use nmcli for any missing fields
if [[ -z "$SSID" ]] || [[ "$SSID" == "ethernet" ]]; then
    ALT_SSID=$(nmcli -t -f ACTIVE,SSID dev wifi 2>/dev/null | grep '^yes:' | awk -F: '{print $2}' | head -1)
    [[ -n "$ALT_SSID" ]] && SSID="$ALT_SSID"
fi

# Interface state
IFACE="$WIFI_IFACE"
[[ -z "$IFACE" ]] && IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
IPV4=$(ip -4 addr show "$IFACE" 2>/dev/null | grep -oP 'inet \K[\d.]+' | head -1)
GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
DNS=$(cat /etc/resolv.conf 2>/dev/null | grep -oP 'nameserver \K[\d.]+' | head -1)

# DHCP lease time (from NetworkManager if available)
DHCP_LEASE=$(nmcli -t -f DHCP4.TIME-LEFT,IP4.ADDRESS device show "$IFACE" 2>/dev/null | head -1)

# === LATENCY PROBES ===
# Ping gateway (1 packet, 1s timeout)
GATEWAY_MS=$(ping -c1 -W1 "$GATEWAY" 2>/dev/null | grep -oP 'time=\K[\d.]+' | head -1)
GATEWAY_MS=${GATEWAY_MS:--1}

# Ping DNS (1 packet, 1s timeout)
DNS_MS=$(ping -c1 -W1 "$DNS" 2>/dev/null | grep -oP 'time=\K[\d.]+' | head -1)
DNS_MS=${DNS_MS:--1}

# DNS resolution test (resolve openrouter.ai)
DNS_RESOLVE_MS=$(dig +stats +tries=1 +time=1 openrouter.ai 2>/dev/null | grep -oP 'Query time: \K[\d]+' | head -1)
DNS_RESOLVE_MS=${DNS_RESOLVE_MS:--1}

# HTTPS handshake to openrouter.ai (TLS+HTTP, measures end-to-end)
OPENROUTER_MS=$(curl -o /dev/null -s -w "%{time_connect}" --max-time 5 https://openrouter.ai/ 2>/dev/null || echo "-1")

# Recent provider probe success rate (last 10 entries from cron probe log)
if [[ -f "$PROBE_LOG" ]]; then
    LAST_10=$(tail -10 "$PROBE_LOG" 2>/dev/null)
    if [[ -n "$LAST_10" ]]; then
        SUCCESS_COUNT=$(echo "$LAST_10" | python3 -c "import json,sys; print(sum(1 for l in sys.stdin if json.loads(l).get('success', False)))" 2>/dev/null || echo "0")
        FAILURE_COUNT=$(echo "$LAST_10" | python3 -c "import json,sys; print(sum(1 for l in sys.stdin if not json.loads(l).get('success', False)))" 2>/dev/null || echo "0")
        SUCCESS_RATE=$(python3 -c "s=int('${SUCCESS_COUNT}'); f=int('${FAILURE_COUNT}'); print(f'{(s/(s+f)*100):.0f}%' if (s+f) > 0 else 'N/A')" 2>/dev/null || echo "N/A")
    else
        SUCCESS_COUNT="0"
        FAILURE_COUNT="0"
        SUCCESS_RATE="N/A"
    fi
else
    SUCCESS_COUNT="0"
    FAILURE_COUNT="0"
    SUCCESS_RATE="N/A"
fi

# === WRITE JSONL ===
python3 -c "
import json, sys
from datetime import datetime, timezone
print(json.dumps({
    'ts': datetime.now(timezone.utc).isoformat(),
    'network': {
        'ssid': '$SSID',
        'bssid': '$BSSID',
        'signal_dbm': '$SIGNAL',
        'frequency_mhz': '$FREQ',
        'rate': '$RATE',
        'security': '$SECURITY',
        'iface': '$IFACE',
        'ipv4': '$IPV4',
        'gateway': '$GATEWAY',
        'dns': '$DNS',
        'dhcp_lease': '$DHCP_LEASE',
    },
    'latency_ms': {
        'gateway': float('$GATEWAY_MS'),
        'dns': float('$DNS_MS'),
        'dns_resolve': float('$DNS_RESOLVE_MS'),
        'openrouter_connect': float('$OPENROUTER_MS'),
    },
    'provider_recent': {
        'success_count': int('$SUCCESS_COUNT'),
        'failure_count': int('$FAILURE_COUNT'),
        'success_rate': '$SUCCESS_RATE',
        'sample_size': 10,
    }
}))
" >> "$LOG_FILE"

# === SUMMARY OUTPUT ===
echo "=== Network Metrics $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="
echo "Network: $SSID ($BSSID) @ ${SIGNAL}dBm, ${FREQ}MHz, ${RATE}, $SECURITY"
echo "Interface: $IFACE → $IPV4 → $GATEWAY (DNS: $DNS)"
echo "Latency: gateway=${GATEWAY_MS}ms, dns=${DNS_MS}ms, dns_resolve=${DNS_RESOLVE_MS}ms, openrouter=${OPENROUTER_MS}ms"
echo "Provider (last 10): ${SUCCESS_COUNT}/${SUCCESS_COUNT}+${FAILURE_COUNT} success ($SUCCESS_RATE)"
echo "Log: $LOG_FILE ($(wc -l < "$LOG_FILE") entries)"