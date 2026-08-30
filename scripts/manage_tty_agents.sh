#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# Omega Engine — TTY Agent Manager
# Manages systemd services for agents on dedicated Virtual Consoles

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_TEMPLATE="$PROJECT_ROOT/deploy/systemd/omega-tty-agent@.service"
SYSTEMD_DIR="/etc/systemd/system"

# Default TTY assignments
declare -A AGENT_TTY=(
    ["researcher"]="tty3"
    ["roc_racoon"]="tty4"
    ["kali"]="tty5"
    ["observability"]="tty6"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (sudo)"
        exit 1
    fi
}

check_tty_available() {
    local tty="$1"
    if [[ ! -e "/dev/$tty" ]]; then
        log_error "TTY device /dev/$tty does not exist"
        return 1
    fi
    if [[ ! -c "/dev/$tty" ]]; then
        log_error "/dev/$tty is not a character device"
        return 1
    fi
    return 0
}

check_user_exists() {
    local user="omega"
    if ! id "$user" &>/dev/null; then
        log_warn "User '$user' does not exist. Creating..."
        useradd -r -s /sbin/nologin -G tty "$user"
        log_success "Created user '$user' in group 'tty'"
    fi
}

install_service() {
    log_info "Installing systemd service template..."
    if [[ ! -f "$SERVICE_TEMPLATE" ]]; then
        log_error "Service template not found: $SERVICE_TEMPLATE"
        return 1
    fi
    cp "$SERVICE_TEMPLATE" "$SYSTEMD_DIR/omega-tty-agent@.service"
    systemctl daemon-reload
    log_success "Service template installed"
}

enable_agent() {
    local agent="$1"
    local tty="${AGENT_TTY[$agent]}"
    
    if [[ -z "$tty" ]]; then
        log_error "Unknown agent: $agent"
        return 1
    fi
    
    check_tty_available "$tty" || return 1
    
    local service_name="omega-tty-agent@${agent}-${tty}.service"
    
    log_info "Enabling $agent on $tty..."
    systemctl enable "$service_name"
    log_success "Enabled $service_name"
}

start_agent() {
    local agent="$1"
    local tty="${AGENT_TTY[$agent]}"
    
    if [[ -z "$tty" ]]; then
        log_error "Unknown agent: $agent"
        return 1
    fi
    
    local service_name="omega-tty-agent@${agent}-${tty}.service"
    
    log_info "Starting $agent on $tty..."
    systemctl start "$service_name"
    sleep 2
    systemctl status "$service_name" --no-pager
}

stop_agent() {
    local agent="$1"
    local tty="${AGENT_TTY[$agent]}"
    
    if [[ -z "$tty" ]]; then
        log_error "Unknown agent: $agent"
        return 1
    fi
    
    local service_name="omega-tty-agent@${agent}-${tty}.service"
    
    log_info "Stopping $agent on $tty..."
    systemctl stop "$service_name"
    log_success "Stopped $service_name"
}

restart_agent() {
    local agent="$1"
    local tty="${AGENT_TTY[$agent]}"
    
    if [[ -z "$tty" ]]; then
        log_error "Unknown agent: $agent"
        return 1
    fi
    
    local service_name="omega-tty-agent@${agent}-${tty}.service"
    
    log_info "Restarting $agent on $tty..."
    systemctl restart "$service_name"
    sleep 2
    systemctl status "$service_name" --no-pager
}

status_agent() {
    local agent="$1"
    local tty="${AGENT_TTY[$agent]}"
    
    if [[ -z "$tty" ]]; then
        log_error "Unknown agent: $agent"
        return 1
    fi
    
    local service_name="omega-tty-agent@${agent}-${tty}.service"
    systemctl status "$service_name" --no-pager
}

logs_agent() {
    local agent="$1"
    local tty="${AGENT_TTY[$agent]}"
    local follow="${2:-false}"
    
    if [[ -z "$tty" ]]; then
        log_error "Unknown agent: $agent"
        return 1
    fi
    
    local service_name="omega-tty-agent@${agent}-${tty}.service"
    
    if [[ "$follow" == "true" ]]; then
        journalctl -u "$service_name" -f
    else
        journalctl -u "$service_name" --no-pager -n 100
    fi
}

list_agents() {
    echo "Configured TTY Agents:"
    echo "======================"
    for agent in "${!AGENT_TTY[@]}"; do
        local tty="${AGENT_TTY[$agent]}"
        local service_name="omega-tty-agent@${agent}-${tty}.service"
        local status="$(systemctl is-enabled "$service_name" 2>/dev/null || echo "disabled")"
        local active="$(systemctl is-active "$service_name" 2>/dev/null || echo "inactive")"
        printf "  %-20s %-6s %-10s %s\n" "$agent" "$tty" "$status" "$active"
    done
}

switch_tty() {
    local tty="$1"
    if [[ ! "$tty" =~ ^tty[0-9]+$ ]]; then
        log_error "Invalid TTY format: $tty (expected tty3, tty4, etc.)"
        return 1
    fi
    log_info "Switching to $tty (Ctrl+Alt+F${tty#tty})..."
    chvt "${tty#tty}"
}

show_help() {
    cat <<EOF
Omega Engine — TTY Agent Manager

Usage: $0 <command> [agent] [options]

Commands:
    install                 Install systemd service template (run once)
    enable <agent>          Enable agent service (persistent)
    start <agent>           Start agent now
    stop <agent>            Stop agent
    restart <agent>         Restart agent
    status <agent>          Show agent status
    logs <agent> [-f]       Show logs (-f to follow)
    list                    List all configured agents
    switch <tty>            Switch to TTY (e.g., tty3)
    help                    Show this help

Agents:
    researcher      → tty3 (Deep research, web scraping)
    roc_racoon      → tty4 (Legacy mining, pattern extraction)
    kali            → tty5 (Oversight, fleet coordination)
    observability   → tty6 (dmesg -w, journalctl -f, htop)

Examples:
    sudo $0 install
    sudo $0 enable researcher
    sudo $0 start researcher
    sudo $0 logs researcher -f
    sudo $0 switch tty3
    sudo $0 list

TTY Access:
    Ctrl+Alt+F3  → researcher (tty3)
    Ctrl+Alt+F4  → roc_racoon (tty4)
    Ctrl+Alt+F5  → kali (tty5)
    Ctrl+Alt+F6  → observability (tty6)
    Ctrl+Alt+F1  → GUI login (tty1)
    Ctrl+Alt+F2  → User shell (tty2)

EOF
}

main() {
    local cmd="${1:-help}"
    local agent="${2:-}"
    local opt="${3:-}"
    
    case "$cmd" in
        install)
            check_root
            check_user_exists
            install_service
            ;;
        enable)
            check_root
            [[ -z "$agent" ]] && { log_error "Agent required"; show_help; exit 1; }
            enable_agent "$agent"
            ;;
        start)
            check_root
            [[ -z "$agent" ]] && { log_error "Agent required"; show_help; exit 1; }
            start_agent "$agent"
            ;;
        stop)
            check_root
            [[ -z "$agent" ]] && { log_error "Agent required"; show_help; exit 1; }
            stop_agent "$agent"
            ;;
        restart)
            check_root
            [[ -z "$agent" ]] && { log_error "Agent required"; show_help; exit 1; }
            restart_agent "$agent"
            ;;
        status)
            [[ -z "$agent" ]] && { log_error "Agent required"; show_help; exit 1; }
            status_agent "$agent"
            ;;
        logs)
            [[ -z "$agent" ]] && { log_error "Agent required"; show_help; exit 1; }
            logs_agent "$agent" "$opt"
            ;;
        list)
            list_agents
            ;;
        switch)
            [[ -z "$agent" ]] && { log_error "TTY required (e.g., tty3)"; show_help; exit 1; }
            switch_tty "$agent"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $cmd"
            show_help
            exit 1
            ;;
    esac
}

main "$@"