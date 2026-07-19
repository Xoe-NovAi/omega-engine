# 🔱 Omega Engine — TTY Agent Deployment Guide
**AP Token**: `AP-TTY-DEPLOYMENT-GUIDE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_tty_deployment ⬡ ACTIVE

**Date**: 2026-07-18
**Prerequisites**: Deep research complete (`R_TTY_VIRTUAL_CONSOLES_DEEP_RESEARCH.md`)

---

## 📋 OVERVIEW

This guide covers deploying Omega Engine agents on dedicated Linux Virtual Consoles (TTYs) accessed via **Ctrl+Alt+F3–F6**.

### TTY Assignment

| TTY | Device | Agent | Purpose |
|-----|--------|-------|---------|
| **tty1** | `/dev/tty1` | GUI (GDM/SDDM) | Graphical login |
| **tty2** | `/dev/tty2` | User shell | Primary admin access |
| **tty3** | `/dev/tty3` | **Researcher** | Deep research, web scraping, API calls |
| **tty4** | `/dev/tty4` | **Roc Racoon** | Legacy mining, pattern extraction |
| **tty5** | `/dev/tty5` | **Kali** | Oversight, fleet coordination |
| **tty6** | `/dev/tty6` | **Observability** | `dmesg -w`, `journalctl -f`, `htop` |

---

## 🚀 QUICK START

### 1. Install Service Template (One-time)

```bash
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh install
```

This:
- Creates `omega` user in `tty` group
- Installs `/etc/systemd/system/omega-tty-agent@.service`
- Reloads systemd

### 2. Enable Agents

```bash
# Enable all agents
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh enable researcher
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh enable roc_racoon
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh enable kali
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh enable observability
```

### 3. Start Agents

```bash
# Start all
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh start researcher
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh start roc_racoon
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh start kali
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh start observability
```

### 4. Access Agents

| Key Combo | TTY | Agent |
|-----------|-----|-------|
| **Ctrl+Alt+F3** | tty3 | Researcher |
| **Ctrl+Alt+F4** | tty4 | Roc Racoon |
| **Ctrl+Alt+F5** | tty5 | Kali |
| **Ctrl+Alt+F6** | tty6 | Observability |
| **Ctrl+Alt+F1** | tty1 | GUI Login |
| **Ctrl+Alt+F2** | tty2 | Your Shell |

---

## 🔧 SERVICE MANAGEMENT

### Status & Logs

```bash
# Check status
sudo manage_tty_agents.sh status researcher

# View logs (last 100 lines)
sudo manage_tty_agents.sh logs researcher

# Follow logs live
sudo manage_tty_agents.sh logs researcher -f
```

### Restart/Stop

```bash
sudo manage_tty_agents.sh restart researcher
sudo manage_tty_agents.sh stop researcher
```

### List All

```bash
manage_tty_agents.sh list
```

---

## 🛡️ SECURITY ARCHITECTURE

### Isolation Properties

| Property | TTY Agent | GUI Terminal |
|----------|-----------|--------------|
| **Compositor** | None | Wayland/X11 |
| **GPU Memory** | None | Shared (DMA-BUF) |
| **Clipboard** | None | Wayland/X11 |
| **Accessibility** | None | AT-SPI2 |
| **D-Bus** | None (unless connected) | Session + System |
| **Input Path** | Kernel → VT → App | libinput → Compositor → App |
| **Font Rendering** | Kernel fbcon/vgacon | FreeType + HarfBuzz + GPU |
| **Scrollback** | Kernel ring buffer (64KB default) | Terminal emulator (unlimited) |

### Systemd Hardening (in service template)

```ini
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=read-only
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictNamespaces=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
LockPersonality=yes
MemoryDenyWriteExecute=yes
SystemCallFilter=@system-service
CapabilityBoundingSet=CAP_DAC_OVERRIDE CAP_SYS_TTY_CONFIG
```

### VT-Level Security

- **`VT_PROCESS` mode**: Agent owns VT; kernel won't switch away
- **`VT_LOCKSWITCH`**: Prevents `Ctrl+Alt+Fn` and `chvt` (optional)
- **`vhangup()` on stop**: Revokes all FDs to VT (systemd `TTYVHangup=yes`)
- **`TTYVTDisallocate=yes`**: Frees kernel VT resources on stop

---

## 💻 AGENT IMPLEMENTATION

### Base Class: `src/omega/agents/tty_agent.py`

```python
from src.omega.agents.tty_agent import TTYAgent, TTYAgentConfig

config = TTYAgentConfig(
    entity_name="researcher",
    tty_path="/dev/tty3",
    data_dir=Path("data"),
    lock_switch=True  # Prevent accidental VT switches
)

agent = TTYAgent(config)
await agent.startup()
# ... agent runs on dedicated VT ...
await agent.shutdown()
```

### Key Features

1. **VTManager** — Handles `VT_PROCESS` acquisition, `VT_LOCKSWITCH`, `VT_ACTIVATE`
2. **Rich TUI** — Textual-based dashboard with live metrics
3. **Hivemind Integration** — File-based presence in `data/coordination/tty_hivemind/`
4. **Graceful Shutdown** — Releases VT, unlocks switch, deregisters from Hivemind

### Custom Agent Example

```python
class ResearcherTTYAgent(TTYAgent):
    async def run(self):
        self.console.print("[bold green]Researcher active on TTY3[/bold green]")
        while self.running:
            # Your research logic here
            await asyncio.sleep(1)
```

---

## 📊 OBSERVABILITY TTY (tty6)

The observability agent provides a **real-time system dashboard**:

```
┌─────────────────────────────────────────────────────────────┐
│ 🔱 Omega Engine — Sovereign Observatory                     │
├─────────────────────────────────────────────────────────────┤
│ [green]● SYSTEM STATUS[/green] | Global Error Rate: 0.0% | Active Breakers: 0 │
├─────────────────────────────────────────────────────────────┤
│ [bold cyan]Entity Focus: SYSTEM[/bold cyan]                       │
│ Cognitive Velocity: 1,247.3 tok/s                            │
│ Token Acceleration: [green]+0.12 tok/s²[/green]                         │
│ Session Cost: $0.0042 (local)                                │
│ Tokens (P/C): 1,234 / 567                                    │
│ Sovereignty Ratio: 1.00 (local/cloud)                        │
│ Avg Latency: 12.3ms | Max Latency: 45.1ms | Requests: 1,234 │
├─────────────────────────────────────────────────────────────┤
│ Time    Level  Entity        Message                    ID   │
│ 14:32:15 INFO  researcher   Deep research started      a1b2c3│
│ 14:32:10 WARN  roc_racoon   Legacy pattern found       d4e5f6│
│ 14:31:55 INFO  kali         Fleet coordination active  g7h8i9│
└─────────────────────────────────────────────────────────────┘
```

**Sources**: `dmesg -w`, `journalctl -f`, `htop`, Omega metrics DB

---

## 🔬 ADVANCED CONFIGURATION

### Increase Scrollback

```bash
# Temporary (until reboot)
echo 256000 > /sys/module/vt/parameters/default_utf8

# Permanent (kernel cmdline)
# Add to GRUB: vt.scrollback=256k
```

### Custom Font (fbcon)

```bash
# Load 16x32 font for 120x50 on 1920x1080
setfont /usr/share/consolefonts/Uni3-Terminus32x16.psf.gz

# Permanent: /etc/vconsole.conf
FONT=Uni3-Terminus32x16.psf.gz
```

### Disable VT Switching for Critical Agents

In agent code:
```python
agent.config.lock_switch = True  # Prevents Ctrl+Alt+Fn and chvt
```

Or in systemd:
```ini
ExecStartPre=/bin/bash -c 'echo 1 > /sys/class/tty/tty3/lock'
ExecStopPost=/bin/bash -c 'echo 0 > /sys/class/tty/tty3/lock'
```

---

## 🐛 TROUBLESHOOTING

| Issue | Cause | Fix |
|-------|-------|-----|
| `StandardInput=tty-force` fails | VT already in use | `systemctl stop getty@tty3.service` |
| Permission denied on `/dev/tty3` | User not in `tty` group | `usermod -aG tty omega` |
| Agent doesn't appear on TTY | VT not acquired | Check `VT_PROCESS` in logs |
| `chvt` doesn't work | VT locked | `VT_LOCKSWITCH=0` or unlock in agent |
| Scrollback too small | Default 64KB | Increase `vt.scrollback` kernel param |
| Font too small | Default 8x16 | Load larger font with `setfont` |

### Debug Commands

```bash
# Check VT state
cat /sys/class/tty/tty3/active
cat /sys/class/tty/tty3/vt_mode

# Current VT
fgconsole

# All VTs
ls /sys/class/tty/tty*/active

# Kernel VT params
cat /sys/module/vt/parameters/*

# systemd VT status
systemctl status systemd-vconsole-setup.service
```

---

## 📚 REFERENCES

| Document | Purpose |
|----------|---------|
| `R_TTY_VIRTUAL_CONSOLES_DEEP_RESEARCH.md` | Full technical research |
| `src/omega/agents/tty_agent.py` | Agent base class |
| `deploy/systemd/omega-tty-agent@.service` | Systemd template |
| `scripts/manage_tty_agents.sh` | Management CLI |
| `man 4 vt` | VT ioctl reference |
| `man 5 systemd.exec` | TTY directives |

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Run `install` (creates user, installs template)
- [ ] Enable desired agents (`enable researcher`, etc.)
- [ ] Start agents (`start researcher`)
- [ ] Verify with `Ctrl+Alt+F3` (researcher), `F4` (roc_racoon), etc.
- [ ] Check logs: `logs researcher -f`
- [ ] Configure observability TTY6 for monitoring
- [ ] Set up log rotation for journal
- [ ] Document agent-specific TTY keybindings

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_tty_deployment ⬡ GUIDE COMPLETE*