#!/bin/bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Workstation Hardening Baseline
# AP Token: AP-HARDEN-v1.0.0
# 
# Purpose: Eliminate the bottom 90% of attack surface on the development workstation.
# Threat model: Supply chain compromise (Shai-Hulud 2.0, malicious npm/PyPI, IDE extensions).
# One compromised dev laptop = poisoned WAD releases.
#
# Usage:
#   chmod +x scripts/omega-harden-workstation.sh
#   ./scripts/omega-harden-workstation.sh [--check-only]
#
# Based on: PROP-RP04-001 (Carmack Briefing 2026-07-30)

set -uo pipefail
# Note: -e (exit on error) intentionally omitted — we handle errors per-check.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD='\033[1m'

CHECK_ONLY=false
[[ "${1:-}" == "--check-only" ]] && CHECK_ONLY=true

PASS=0
WARN=0
FAIL=0

check() {
    local desc="$1"
    local result="$2"  # pass, warn, fail
    local detail="${3:-}"
    
    case "$result" in
        pass) echo -e "  ${GREEN}✓${NC} $desc"; PASS=$((PASS + 1)) ;;
        warn) echo -e "  ${YELLOW}⚠${NC} $desc — $detail"; WARN=$((WARN + 1)) ;;
        fail) echo -e "  ${RED}✗${NC} $desc — $detail"; FAIL=$((FAIL + 1)) ;;
    esac
}

echo -e "${BOLD}🔱 Omega Workstation Hardening Check${NC}"
echo "   $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ── 1. Full Disk Encryption ──────────────────────────────────────────────────
echo -e "${BOLD}[1/7] Full Disk Encryption${NC}"
if lsblk -f 2>/dev/null | grep -q "crypto_LUKS"; then
    check "FDE active (LUKS)" pass
elif command -v diskutil &>/dev/null && diskutil apfs list 2>/dev/null | grep -q "FileVault"; then
    check "FileVault active (macOS)" pass
else
    check "FDE status" fail "No LUKS/FileVault detected — CRITICAL"
fi

# ── 2. Firewall ──────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[2/7] Firewall${NC}"
if command -v ufw &>/dev/null; then
    if ufw status 2>/dev/null | grep -q "Status: active"; then
        check "UFW active" pass
    else
        check "UFW status" warn "UFW installed but not active"
        if [[ "$CHECK_ONLY" == "false" ]]; then
            echo "    → Run: sudo ufw --force reset && sudo ufw default deny incoming && sudo ufw default allow outgoing && sudo ufw enable"
        fi
    fi
elif command -v firewall-cmd &>/dev/null; then
    if firewall-cmd --state 2>/dev/null | grep -q "running"; then
        check "firewalld active" pass
    else
        check "firewalld status" warn "Installed but not running"
    fi
else
    check "Firewall" warn "No firewall detected (ufw/firewalld)"
fi

# ── 3. DNS Security (DoH) ────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[3/7] DNS Security${NC}"
RESOLVED_CONF="/etc/systemd/resolved.conf"
if [[ -f "$RESOLVED_CONF" ]] || [[ -d "/etc/systemd/resolved.conf.d" ]]; then
    if grep -rq "DNSOverTLS=yes\|DNSSEC=yes" /etc/systemd/resolved.conf /etc/systemd/resolved.conf.d/ 2>/dev/null; then
        check "DNS-over-TLS enabled" pass
    else
        check "DNS-over-TLS" warn "systemd-resolved installed but DoH not configured"
    fi
else
    check "systemd-resolved" warn "Not found — DNS may be unencrypted"
fi

# ── 4. Non-Root Daily User ───────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[4/7] User Privileges${NC}"
if id -nG 2>/dev/null | grep -qw "sudo\|wheel"; then
    check "Daily user has sudo/wheel" warn "Consider removing from sudo group for daily use"
else
    check "Daily user is non-root" pass
fi

# ── 5. SSH Configuration ─────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[5/7] SSH Hardening${NC}"
if [[ -f ~/.ssh/config ]]; then
    if grep -q "IdentityFile.*ed25519" ~/.ssh/config 2>/dev/null; then
        check "SSH uses Ed25519" pass
    else
        check "SSH key type" warn "Consider Ed25519 keys"
    fi
    if grep -q "PasswordAuthentication no" ~/.ssh/config 2>/dev/null; then
        check "SSH password auth disabled" pass
    else
        check "SSH password auth" warn "Consider disabling password authentication"
    fi
else
    check "SSH config" warn "~/.ssh/config not found"
fi

# Check sshd_config if we have access
if [[ -r /etc/ssh/sshd_config ]]; then
    if grep -q "^PermitRootLogin no" /etc/ssh/sshd_config 2>/dev/null; then
        check "SSH root login disabled" pass
    else
        check "SSH root login" warn "Consider disabling root login"
    fi
fi

# ── 6. VS Code / IDE Extension Audit ─────────────────────────────────────────
echo ""
echo -e "${BOLD}[6/7] IDE Extension Audit${NC}"
if [[ -d "$HOME/.vscode/extensions" ]]; then
    EXT_COUNT=$(ls -1 "$HOME/.vscode/extensions" 2>/dev/null | wc -l)
    check "VS Code extensions installed: $EXT_COUNT" warn "Review extensions for supply chain risk"
elif [[ -d "$HOME/.vscode-server/extensions" ]]; then
    EXT_COUNT=$(ls -1 "$HOME/.vscode-server/extensions" 2>/dev/null | wc -l)
    check "VS Code Server extensions: $EXT_COUNT" warn "Review extensions for supply chain risk"
else
    check "VS Code extensions" pass "No VS Code extensions directory found"
fi

# ── 7. System Updates ────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[7/7] System Updates${NC}"
if command -v apt &>/dev/null; then
    if [[ -f /var/cache/apt/pkgcache.gz ]]; then
        LAST_UPDATE=$(stat -c %Y /var/cache/apt/pkgcache.gz 2>/dev/null || echo 0)
        AGE_DAYS=$(( ($(date +%s) - LAST_UPDATE) / 86400 ))
        if [[ $AGE_DAYS -lt 7 ]]; then
            check "Package cache fresh ($AGE_DAYS days old)" pass
        else
            check "Package cache stale ($AGE_DAYS days old)" warn "Run: sudo apt update && sudo apt upgrade"
        fi
    fi
elif command -v dnf &>/dev/null; then
    check "Package manager (dnf)" warn "Run: sudo dnf check-update"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}PASS: $PASS${NC}  ${YELLOW}WARN: $WARN${NC}  ${RED}FAIL: $FAIL${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $FAIL -gt 0 ]]; then
    echo ""
    echo -e "${RED}${BOLD}⚠ $FAIL critical issues found. Review above.${NC}"
    exit 1
elif [[ $WARN -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}${BOLD}⚠ $WARN warnings. Address when convenient.${NC}"
    exit 0
else
    echo ""
    echo -e "${GREEN}${BOLD}✓ Workstation is hardened. All checks passed.${NC}"
    exit 0
fi
