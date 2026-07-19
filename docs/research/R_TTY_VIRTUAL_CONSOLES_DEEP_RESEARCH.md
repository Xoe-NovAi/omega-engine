# 🔱 Deep Research: Linux Virtual Consoles (TTYs) for Omega Engine
**AP Token**: `AP-TTY-DEEP-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_tty_deep_research ⬡ ACTIVE

**Date**: 2026-07-18
**Scope**: Comprehensive technical analysis of Linux VT subsystem for sovereign agent deployment

---

## 📋 EXECUTIVE SUMMARY

Linux Virtual Consoles (VCs/TTYs) accessed via **Ctrl+Alt+F1–F6** are kernel-level text terminals managed by the **VT (Virtual Terminal) subsystem**. They provide:

- **True isolation**: No X11/Wayland, no compositor, no D-Bus, no GUI toolkit
- **Persistence**: Survive GPU driver crashes, X11/Wayland restarts, compositor failures
- **Direct kernel access**: `dmesg -w`, `kmsg`, `/proc/kmsg` real-time streams
- **Systemd integration**: `StandardInput=tty-force`, `TTYPath=`, `TTYReset=`, `TTYVHangup=`
- **Security boundary**: No clipboard, no accessibility bus, no GPU memory sharing

**For Omega Engine**: Dedicated TTYs per agent (researcher, roc_racoon, kali, etc.) enable **sovereign compute isolation** — agents run on bare metal text terminals with zero GUI attack surface.

---

## 🏗️ KERNEL ARCHITECTURE: THE VT SUBSYSTEM

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `vt.c` | `drivers/tty/vt/vt.c` | VT switching, allocation, ioctl handling |
| `vc_screen.c` | `drivers/tty/vt/vc_screen.c` | Screen buffer management, scrollback |
| `keyboard.c` | `drivers/tty/vt/keyboard.c` | Keyboard handling, keymaps, LED control |
| `vt_ioctl.c` | `drivers/tty/vt/vt_ioctl.c` | `VT_ACTIVATE`, `VT_WAITACTIVE`, `VT_GETSTATE`, `VT_SETMODE` |

### Key Data Structures

```c
// Per-VT state (simplified)
struct vc_data {
    struct tty_port port;        // TTY port operations
    unsigned int vc_num;         // VT number (1-63)
    unsigned char *vc_screenbuf; // Video memory buffer
    unsigned int vc_size_row;    // Columns
    unsigned int vc_rows;        // Rows
    unsigned int vc_top, vc_bottom; // Scroll region
    struct vc_state vc_state;    // Cursor, attributes, charset
    struct vt_mode vt_mode;      // VT_PROCESS, VT_AUTO, VT_ACKACQ
    struct pid *vt_pid;          // Process owning this VT
    unsigned long vc_flags;      // VC_REDRAW, VC_SCROLLED, etc.
};
```

### VT Modes (Critical for Agent Deployment)

| Mode | Constant | Behavior | Use Case |
|------|----------|----------|----------|
| **VT_AUTO** | `0` | Kernel handles switching | Default, GUI gets VT1 |
| **VT_PROCESS** | `1` | Process controls switching | **Agent owns VT exclusively** |
| **VT_ACKACQ** | `2` | Process acknowledges switch | Coordinated handoff |

**For Omega**: Agents should request `VT_PROCESS` mode via `ioctl(fd, VT_SETMODE, &mode)` to prevent accidental switches and own their VT completely.

---

## 🔧 SYSTEMD INTEGRATION: TTY-BASED SERVICES

### Unit File Directives

| Directive | Values | Purpose |
|-----------|--------|---------|
| `StandardInput=` | `tty`, `tty-force`, `tty-fail`, `null` | Connect stdin to VT |
| `StandardOutput=` | `tty`, `journal`, `kmsg`, `null` | Route stdout |
| `StandardError=` | `inherit`, `journal`, `kmsg`, `null` | Route stderr |
| `TTYPath=` | `/dev/tty3` | Explicit VT device |
| `TTYReset=` | `yes`, `no` | Reset VT on start/stop |
| `TTYVHangup=` | `yes`, `no` | `vhangup()` on stop |
| `TTYVTDisallocate=` | `yes`, `no` | Deallocate VT on stop |

### Critical: `StandardInput=tty-force`

```ini
# Forces allocation of a VT if none assigned
# Fails if VT already in use by another service
StandardInput=tty-force
TTYPath=/dev/tty3
TTYReset=yes
TTYVHangup=yes
```

### Example: Omega Agent on Dedicated TTY

```ini
# /etc/systemd/system/omega-researcher@tty3.service
[Unit]
Description=Omega Researcher Agent (TTY3)
Documentation=https://xoe-nov.ai/omega-engine
After=systemd-vconsole-setup.service
Wants=systemd-vconsole-setup.service
Conflicts=omega-researcher@tty4.service omega-roc_racoon@tty3.service

[Service]
Type=simple
User=arcana-novai
Group=arcana-novai
WorkingDirectory=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine
Environment=OMEGA_DATA_DIR=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data
Environment=OMEGA_ENTITY=researcher
Environment=OMEGA_TTY=/dev/tty3
# CRITICAL: Force VT allocation
StandardInput=tty-force
StandardOutput=journal
StandardError=journal
TTYPath=/dev/tty3
TTYReset=yes
TTYVHangup=yes
TTYVTDisallocate=yes
# Resource limits for sovereignty
MemoryMax=4G
CPUQuota=200%
IOWeight=100
# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data
CapabilityBoundingSet=CAP_DAC_OVERRIDE CAP_SYS_RESOURCE
ExecStartPre=/bin/chvt 3
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python -m src.omega.agents.researcher --tty=/dev/tty3
Restart=on-failure
RestartSec=10
StartLimitBurst=3
StartLimitIntervalSec=60

[Install]
WantedBy=multi-user.target
Alias=omega-researcher-tty3.service
```

### `chvt` Integration

```bash
# Switch to VT3 (Ctrl+Alt+F3 equivalent)
chvt 3

# Get current VT
fgconsole

# Wait for VT to become active
chvt 3 && sleep 1 && fgconsole
```

---

## 🔐 SECURITY ISOLATION PROPERTIES

### Attack Surface Comparison

| Surface | GUI Terminal (gnome-terminal, konsole) | Virtual Console (TTY) |
|---------|----------------------------------------|----------------------|
| **Compositor** | Wayland/X11 + compositor | None |
| **GPU Memory** | Shared via DMA-BUF | None (framebuffer only) |
| **Clipboard** | Wayland/X11 clipboard | None |
| **Accessibility** | AT-SPI2, a11y bus | None |
| **D-Bus** | Session + system bus | None (unless explicitly connected) |
| **Input** | libinput → compositor → app | Kernel → VT → app |
| **Font Rendering** | FreeType + HarfBuzz + GPU | Kernel built-in (VGA) or fbcon |
| **Scrollback** | Terminal emulator (unlimited) | Kernel buffer (default 64KB) |

### VT-Specific Security Features

1. **`vhangup()`** — Revokes all file descriptors to the VT on service stop
2. **`VT_LOCKSWITCH`** — `ioctl(fd, VT_LOCKSWITCH, 1)` prevents `chvt`/`Ctrl+Alt+Fn`
3. **`VT_PROCESS` mode** — Process owns VT; kernel won't switch away without permission
4. **No `$DISPLAY`/`$WAYLAND_DISPLAY`** — GUI toolkits fail to initialize
5. **No `$XDG_RUNTIME_DIR` access** — No socket activation, no portal access

---

## 📊 RESOURCE FOOTPRINT

### Memory Usage (Typical)

| Component | GUI Terminal | Virtual Console |
|-----------|--------------|-----------------|
| **Terminal Emulator** | 50-200 MB | 0 |
| **Compositor** | 100-500 MB | 0 |
| **X11/Wayland Server** | 50-200 MB | 0 |
| **Kernel VT** | 0 | ~2 MB (framebuffer + scrollback) |
| **Font Rendering** | GPU + CPU | CPU only (VGA 8x16 or fbcon) |
| **Total Baseline** | **250-900 MB** | **~2-5 MB** |

### CPU Overhead

- **VT switching**: ~50-200 µs (kernel context switch)
- **Scrollback**: Ring buffer in kernel — O(1) append, O(n) read
- **Rendering**: `fbcon` uses CPU blitting; `vgacon` uses VGA hardware

---

## 🛠️ ADVANCED VT OPERATIONS

### Programmatic VT Control (Python)

```python
import fcntl
import os
import struct
import termios

# VT ioctl constants
VT_OPENQRY = 0x5600
VT_GETMODE = 0x5601
VT_SETMODE = 0x5602
VT_GETSTATE = 0x5603
VT_SENDSIG = 0x5604
VT_RELDISP = 0x5605
VT_ACTIVATE = 0x5606
VT_WAITACTIVE = 0x5607
VT_DISALLOCATE = 0x5608

VT_AUTO = 0
VT_PROCESS = 1
VT_ACKACQ = 2

class VTManager:
    def __init__(self, tty_path: str = "/dev/tty3"):
        self.fd = os.open(tty_path, os.O_RDWR | os.O_NOCTTY)
        self.tty_path = tty_path
    
    def acquire_vt_process_mode(self) -> bool:
        """Request VT_PROCESS mode — we own this VT."""
        mode = struct.pack("h", VT_PROCESS)
        try:
            fcntl.ioctl(self.fd, VT_SETMODE, mode)
            return True
        except OSError:
            return False
    
    def release_vt(self) -> bool:
        """Release VT ownership."""
        mode = struct.pack("h", VT_AUTO)
        try:
            fcntl.ioctl(self.fd, VT_SETMODE, mode)
            return True
        except OSError:
            return False
    
    def activate_vt(self, vt_num: int) -> bool:
        """Switch to VT (like chvt)."""
        try:
            fcntl.ioctl(self.fd, VT_ACTIVATE, vt_num)
            fcntl.ioctl(self.fd, VT_WAITACTIVE, vt_num)
            return True
        except OSError:
            return False
    
    def lock_switch(self, lock: bool = True) -> bool:
        """Prevent/allow VT switching (VT_LOCKSWITCH)."""
        try:
            fcntl.ioctl(self.fd, 0x5609, 1 if lock else 0)  # VT_LOCKSWITCH
            return True
        except OSError:
            return False
    
    def get_state(self) -> dict:
        """Get VT state (active VT, open VTs, etc.)."""
        buf = bytearray(16)
        fcntl.ioctl(self.fd, VT_GETSTATE, buf)
        return {
            "active_vt": buf[0],
            "signal": buf[1],
            "open_vts": list(buf[2:])
        }
    
    def close(self):
        os.close(self.fd)
```

### Scrollback Management

```bash
# Increase scrollback (requires root, persistent via kernel param)
echo 256000 > /sys/module/vt/parameters/default_utf8
# Or at boot: vt.scrollback=256k

# Current scrollback size
cat /sys/module/vt/parameters/default_utf8

# Clear scrollback
echo -ne '\033[3J' > /dev/tty3
```

### Framebuffer Console (fbcon) vs VGA Console (vgacon)

| Feature | `vgacon` (legacy) | `fbcon` (modern) |
|---------|-------------------|------------------|
| **Resolution** | 80x25, 80x50 | Up to monitor native |
| **Fonts** | VGA ROM (8x8, 8x16) | Any loaded font (up to 32x64) |
| **Colors** | 16 | 16 (palette) or 256 |
| **Graphics** | None | Can show Tux logo, progress bars |
| **Driver** | VGA hardware | `drm_fb_helper` + GPU driver |
| **KMS** | No | Yes (requires DRM/KMS) |

**For Omega**: `fbcon` with a loaded 16x32 font gives 120x50 on 1920x1080 — much better for TUI apps.

---

## 🎯 OMEGA ENGINE: TTY DEPLOYMENT ARCHITECTURE

### Proposed TTY Allocation

| TTY | Agent | Purpose | Systemd Unit |
|-----|-------|---------|--------------|
| **tty1** | GUI (GDM) | Graphical login | `display-manager.service` |
| **tty2** | **User shell** | Primary admin access | `getty@tty2.service` |
| **tty3** | **Researcher** | Deep research, web scraping | `omega-researcher@tty3.service` |
| **tty4** | **Roc Racoon** | Legacy mining, pattern extraction | `omega-roc_racoon@tty4.service` |
| **tty5** | **Kali** | Oversight, fleet coordination | `omega-kali@tty5.service` |
| **tty6** | **Observability** | `dmesg -w`, `journalctl -f`, `htop` | `omega-observability@tty6.service` |

### Agent TTY Interface Contract

```python
# src/omega/agents/tty_agent.py
class TTYAgent:
    """Base class for agents running on dedicated VTs."""
    
    def __init__(self, entity_name: str, tty_path: str):
        self.entity_name = entity_name
        self.tty_path = tty_path
        self.vt_manager = VTManager(tty_path)
        self.running = False
    
    async def startup(self):
        # 1. Acquire VT_PROCESS mode
        if not self.vt_manager.acquire_vt_process_mode():
            raise RuntimeError(f"Failed to acquire {self.tty_path}")
        
        # 2. Lock switching (optional — for critical agents)
        self.vt_manager.lock_switch(True)
        
        # 3. Initialize TUI (Textual, rich, or raw)
        self.console = Console(file=open(self.tty_path, "w"))
        
        # 4. Register with Hivemind
        await self.register_with_hivemind()
    
    async def shutdown(self):
        # 1. Unlock switching
        self.vt_manager.lock_switch(False)
        
        # 2. Release VT ownership
        self.vt_manager.release_vt()
        
        # 3. vhangup() handled by systemd TTYVHangup=yes
        await self.deregister_from_hivemind()
    
    def write_status(self, msg: str):
        """Write to VT directly (bypasses logging)."""
        with open(self.tty_path, "w") as f:
            f.write(f"\033[2J\033[H{msg}")  # Clear screen, home cursor
```

### Hivemind Integration

```python
# TTY agents report presence via file-based Hivemind (no network needed)
TTY_HIVEMIND_DIR = Path("data/coordination/tty_hivemind")

def register_tty_agent(entity: str, tty: str, pid: int):
    (TTY_HIVEMIND_DIR / f"{entity}.json").write_text(json.dumps({
        "entity": entity,
        "tty": tty,
        "pid": pid,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "vt_mode": "VT_PROCESS",
        "status": "active"
    }))

def heartbeat_tty_agent(entity: str):
    path = TTY_HIVEMIND_DIR / f"{entity}.json"
    if path.exists():
        data = json.loads(path.read_text())
        data["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(data))
```

---

## 🔬 RESEARCH GAPS & OPEN QUESTIONS

| Gap | Priority | Investigation Needed |
|-----|----------|---------------------|
| **VT_PROCESS + systemd interaction** | P0 | Does `StandardInput=tty-force` set VT_PROCESS automatically? |
| **Scrollback persistence across restarts** | P1 | Can we preserve kernel scrollback via `VT_DISALLOCATE=0`? |
| **Multi-seat / logind integration** | P2 | How does `logind` manage VTs with `systemd-vconsole-setup`? |
| **GPU passthrough to fbcon** | P3 | Can we use `drm_fb_helper` for hardware-accelerated text? |
| **VT switching latency under load** | P2 | Measure `chvt` latency with 4-core inference running |
| **Kernel VT_MAX_NR limit** | P3 | Default 63 — can we increase for more agents? |
| **Secure boot / TPM integration** | P3 | Can VT ownership be attested? |

---

## 📚 AUTHORITATIVE SOURCES

| Source | Type | Relevance |
|--------|------|-----------|
| `man 4 vt` | Manual | VT ioctl reference |
| `man 5 systemd.exec` | Manual | TTY directives |
| `man 1 chvt` | Manual | VT switching |
| `man 1 openvt` | Manual | Run command on free VT |
| `man 1 vhangup` | Manual | Revoke VT access |
| `Documentation/admin-guide/vt.txt` | Kernel Doc | VT subsystem overview |
| `drivers/tty/vt/` | Kernel Source | Implementation |
| `systemd/src/core/vt.c` | Systemd Source | VT handling in systemd |
| `man 7 console_codes` | Manual | Escape sequences for VT |

---

## 🚀 NEXT STEPS FOR OMEGA

1. **Prototype**: Create `omega-researcher@tty3.service` with `StandardInput=tty-force`
2. **Test**: Verify `VT_PROCESS` mode acquisition in agent startup
3. **Benchmark**: Memory/CPU vs GUI terminal baseline
4. **Integrate**: Wire TTY agents into Hivemind (file-based)
5. **Hardening**: Add `VT_LOCKSWITCH`, `CapabilityBoundingSet`, `MemoryMax`
6. **Observability**: Deploy `omega-observability@tty6.service` with `dmesg -w` + `journalctl -f`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_tty_deep_research ⬡ RESEARCH COMPLETE*