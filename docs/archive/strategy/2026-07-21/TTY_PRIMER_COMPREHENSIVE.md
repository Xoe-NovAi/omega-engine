# 🔱 Omega Engine — TTY Primer: The Missing Manual
**AP Token**: `AP-TTY-PRIMER-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_tty_primer ⬡ COMPLETE

**Date**: 2026-07-18
**Audience**: Anyone who uses Linux but doesn't know what Ctrl+Alt+F3 actually does
**Goal**: Transform "mystery keys" into "sovereign infrastructure"

---

## 🎯 PART 1: WHAT YOU ALREADY KNOW (But Didn't Realize)

### The Secret You've Been Using Since Day 1

Every Linux boot gives you **7 virtual terminals** by default:

| Key Combo | Device | What You See | Who Owns It |
|-----------|--------|--------------|-------------|
| **Ctrl+Alt+F1** | `/dev/tty1` | Graphical login screen | GDM/SDDM (display manager) |
| **Ctrl+Alt+F2** | `/dev/tty2` | Text login prompt | `getty` (your fallback shell) |
| **Ctrl+Alt+F3** | `/dev/tty3` | Text login prompt | **UNUSED** ← **Omega puts Researcher here** |
| **Ctrl+Alt+F4** | `/dev/tty4` | Text login prompt | **UNUSED** ← **Omega puts Roc Racoon here** |
| **Ctrl+Alt+F5** | `/dev/tty5` | Text login prompt | **UNUSED** ← **Omega puts Kali here** |
| **Ctrl+Alt+F6** | `/dev/tty6` | Text login prompt | **UNUSED** ← **Omega puts Observability here** |
| **Ctrl+Alt+F7** | `/dev/tty7` | Usually back to GUI | X11/Wayland |

**You've probably used F1 and F2. F3-F6 have been sitting empty for years.**

---

## 🧠 PART 2: THE MENTAL MODEL SHIFT

### Old Mental Model (Wrong)
```
"TTYs are old-school text terminals from the 1970s. 
 Terminal emulators (gnome-terminal, konsole) replaced them.
 They're obsolete."
```

### New Mental Model (Correct)
```
"TTYs are KERNEL-LEVEL VIRTUAL DISPLAYS.
 
 Terminal emulators RUN ON TOP OF a graphical compositor (Wayland/X11).
 TTYs ARE THE COMPOSITOR — they exist BELOW the graphics stack.
 
 When your GPU driver crashes:
   • Terminal emulator → DIES (compositor died)
   • TTY3 → STILL WORKS (kernel VT subsystem survived)
 
 When your GUI freezes:
   • You can't click anything
   • Ctrl+Alt+F3 → INSTANT ESCAPE HATCH (kernel handles the switch)
 
 TTYs aren't obsolete — they're the FOUNDATION everything else sits on."
```

---

## 🏗️ PART 3: ARCHITECTURE — WHY TTYs ARE DIFFERENT

### The Stack Comparison

```
┌────────────────────────────────────────────────────────────────────┐
│                        GUI TERMINAL (gnome-terminal)               │
├────────────────────────────────────────────────────────────────────┤
│  Your Shell (bash)                                                 │
│       │                                                            │
│       ▼                                                            │
│  Terminal Emulator (GTK/Qt app)  ← 200 MB RAM                     │
│       │                                                            │
│       ▼                                                            │
│  Wayland/X11 Compositor (KWin, Mutter)  ← 300 MB RAM             │
│       │                                                            │
│       ▼                                                            │
│  GPU Driver (nvidia/amdgpu/i915)  ← Kernel module                 │
│       │                                                            │
│       ▼                                                            │
│  Linux Kernel                                                      │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                        VIRTUAL CONSOLE (TTY3)                      │
├────────────────────────────────────────────────────────────────────┤
│  Your Shell (bash)  OR  Omega Agent (Python)                      │
│       │                                                            │
│       ▼                                                            │
│  Kernel VT Subsystem (drivers/tty/vt/)  ← 2-5 MB RAM             │
│       │                                                            │
│       ▼                                                            │
│  Framebuffer (fbcon) or VGA (vgacon)  ← Kernel                    │
│       │                                                            │
│       ▼                                                            │
│  Linux Kernel                                                      │
└────────────────────────────────────────────────────────────────────┘
```

### Key Differences That Matter

| Property | GUI Terminal | **Virtual Console (TTY)** |
|----------|--------------|---------------------------|
| **Process tree depth** | 5+ layers | **1 layer** (kernel → app) |
| **RAM baseline** | 500 MB+ | **2-5 MB** |
| **GPU dependency** | Required | **None** (fbcon uses CPU) |
| **Compositor dependency** | Required | **None** |
| **Survives GPU crash** | ❌ | ✅ |
| **Survives compositor crash** | ❌ | ✅ |
| **Survives OOM killer** | First to die | **Last to die** |
| **Switch latency** | ~100ms (compositor) | **~50µs** (kernel VT switch) |
| **Security boundary** | User namespace | **Kernel VT isolation** |

---

## 🔐 PART 4: THE SECURITY SUPERPOWER

### What "Kernel VT Isolation" Actually Means

```
┌─────────────────────────────────────────────────────────────────┐
│                     GUI TERMINAL ATTACK SURFACE                 │
├─────────────────────────────────────────────────────────────────┤
│  • Wayland/X11 socket (/tmp/.X11-unix, $WAYLAND_DISPLAY)       │
│  • Clipboard (copy/paste between apps)                          │
│  • Accessibility bus (AT-SPI2 — screen readers, automation)    │
│  • D-Bus session bus (IPC with all GUI apps)                   │
│  • GPU memory (DMA-BUF — shared with browser, games, etc.)     │
│  • Screenshot/recording APIs (any app can capture)             │
│  • Input injection (xdotool, ydotool — any app can type)       │
│  • Font rendering (FreeType + HarfBuzz — complex parsers)      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     VIRTUAL CONSOLE ATTACK SURFACE              │
├─────────────────────────────────────────────────────────────────┤
│  • /dev/tty3 (character device — standard Unix permissions)    │
│  • That's it.                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**No clipboard. No accessibility. No D-Bus. No GPU sharing. No screenshots. No input injection. No complex font parsers.**

---

## ⚡ PART 5: VT_PROCESS MODE — THE AGENT SUPERPOWER

### Normal VT Behavior (VT_AUTO)
```
Kernel owns the VT.
User presses Ctrl+Alt+F4 → Kernel switches to TTY4.
User presses Ctrl+Alt+F3 → Kernel switches back to TTY3.
Agent has NO control over switching.
```

### VT_PROCESS Mode (What Omega Uses)
```
Agent calls: ioctl(fd, VT_SETMODE, {mode: VT_PROCESS})
Kernel: "OK, YOU own this VT now. I won't switch away without your permission."

Agent can now:
  • Lock switching: ioctl(fd, VT_LOCKSWITCH, 1)  // Ctrl+Alt+Fn BLOCKED
  • Unlock switching: ioctl(fd, VT_LOCKSWITCH, 0) // Allow switching again
  • Force switch: ioctl(fd, VT_ACTIVATE, 4)       // Programmatically chvt
  • Get notified: Kernel sends SIGUSR1 when someone tries to switch
```

### Why This Matters for Agents

```python
# Researcher on TTY3 doing critical work:
agent.vt.lock_switch(True)  # Ctrl+Alt+F4 now DOES NOTHING
# User at keyboard: "Why can't I switch?" → They CAN'T
# Agent is SOVEREIGN over its display

# Later, when safe:
agent.vt.lock_switch(False)  # User can switch again
```

---

## � PART 6: REAL-WORLD OMEGA USE CASES

### Use Case 1: The "GPU Driver Crashed" Scenario

**Before TTY Agents:**
```
1. nvidia driver crashes → screen freezes → compositor dies
2. All terminal emulators die (they ran on compositor)
3. You can't see logs, can't restart agent, can't debug
4. Hard reboot → lose all agent state → restart research from scratch
```

**With TTY Agents:**
```
1. nvidia driver crashes → GUI freezes
2. Press Ctrl+Alt+F6 (Observability TTY) → WORKS INSTANTLY
3. See: dmesg -w shows "nvidia: GPU has fallen off the bus"
4. journalctl -f shows agent heartbeats still running on TTY3/4/5
5. sudo systemctl restart nvidia-persistenced
6. GUI comes back → agents never stopped → zero data loss
```

### Use Case 2: The "OOM Killer" Scenario

**Before:**
```
1. Researcher loads 70B model → RAM hits 95%
2. OOM killer picks gnome-terminal (big process) → KILLS IT
3. Researcher agent dies mid-task → partial results lost
```

**With TTY Agents:**
```
1. Researcher on TTY3 uses 5 MB baseline + model RAM
2. gnome-terminal on GUI uses 300 MB → OOM killer picks THAT
3. TTY3 agent survives (small, low oom_score_adj)
4. Research completes → results saved
```

### Use Case 3: The "Secure API Key Entry" Scenario

**Problem:** You need to enter `HF_TOKEN`, `AA_API_KEY`, `GH_TOKEN` for agents. Don't want them in shell history, logs, or clipboard.

**TTY Solution:**
```bash
# On TTY3 (Researcher), agent prompts:
┌─────────────────────────────────────────────────────────────┐
│ 🔐 SECURE API KEY ENTRY                                     │
├─────────────────────────────────────────────────────────────┤
│ Enter HF_TOKEN (input hidden, not logged, not in history):  │
│ ****************************************                    │
│                                                             │
│ [Enter] to confirm  |  [Esc] to cancel                      │
└─────────────────────────────────────────────────────────────┘

# Implementation:
with open("/dev/tty3", "r") as tty_in:
    token = getpass.getpass(stream=tty_in)  # Reads DIRECTLY from TTY
    # Never touches shell stdin, never in history, never in logs
```

### Use Case 4: The "24/7 Unattended Research" Scenario

**Before:**
```
tmux session + terminal emulator → fragile
• Terminal emulator updates → restart
• Compositor crashes → session dies
• GUI update → reboot → session dies
• "Where was I?" → scrollback lost
```

**With TTY Agents:**
```
systemd service + VT_PROCESS → bulletproof
• Survives GUI updates, compositor crashes, GPU driver updates
• systemd restarts on failure (Restart=on-failure)
• Kernel scrollback persists (64KB default, configurable to 256KB)
• Journal logs via systemd (journalctl -u omega-tty-agent@...)
• Hivemind heartbeat every 30s → fleet knows it's alive
```

### Use Case 5: The "Instant Context Switch" Workflow

**User Workflow:**
```
08:00  Ctrl+Alt+F3  → Researcher dashboard (deep research running)
08:05  Ctrl+Alt+F4  → Roc Racoon (mining legacy patterns)
08:10  Ctrl+Alt+F5  → Kali (fleet oversight, mandate enforcement)
08:15  Ctrl+Alt+F6  → Observability (kernel logs, CPU, memory, sovereignty)
08:20  Ctrl+Alt+F1  → GUI (browser, email, docs)
08:25  Ctrl+Alt+F3  → Back to Researcher (exact same state)
```

**No Alt+Tab hunting. No window management. Muscle memory. Instant.**

---

## 🛠️ PART 7: PRACTICAL TTY COMMANDS CHEAT SHEET

### Navigation
```bash
# Switch VTs (from anywhere)
Ctrl+Alt+F1   # GUI login
Ctrl+Alt+F2   # Your shell
Ctrl+Alt+F3   # Researcher
Ctrl+Alt+F4   # Roc Racoon
Ctrl+Alt+F5   # Kali
Ctrl+Alt+F6   # Observability

# From command line
chvt 3        # Switch to TTY3 (like Ctrl+Alt+F3)
fgconsole     # Print current VT number (1-63)
```

### Inspection
```bash
# See all VTs and their state
ls /sys/class/tty/tty*/active
# /sys/class/tty/tty1/active:1  (active)
# /sys/class/tty/tty2/active:1  (active)
# /sys/class/tty/tty3/active:1  (active = agent owns it)

# Current VT mode
cat /sys/class/tty/tty3/vt_mode
# 0 = VT_AUTO, 1 = VT_PROCESS, 2 = VT_ACKACQ

# Kernel VT parameters
cat /sys/module/vt/parameters/*
# default_utf8, scrollback, etc.
```

### Scrollback
```bash
# Increase scrollback (temporary)
echo 256000 > /sys/module/vt/parameters/default_utf8

# Permanent: add to kernel cmdline (GRUB)
vt.scrollback=256k

# Clear scrollback
echo -ne '\033[3J' > /dev/tty3
```

### Fonts (fbcon)
```bash
# List available fonts
ls /usr/share/consolefonts/

# Load larger font (16x32 = 120x50 on 1920x1080)
setfont /usr/share/consolefonts/Uni3-Terminus32x16.psf.gz

# Permanent: /etc/vconsole.conf
FONT=Uni3-Terminus32x16.psf.gz
```

### Debugging
```bash
# Watch kernel logs LIVE (on Observability TTY6)
dmesg -w
dmesg -T -w  # Human-readable timestamps

# Watch systemd journal LIVE
journalctl -f
journalctl -u omega-tty-agent@researcher-tty3.service -f

# Watch specific agent logs
tail -f data/coordination/tty_hivemind/researcher.json
```

---

## 🚀 PART 8: DEPLOYMENT QUICKSTART

### One-Time Setup (5 minutes)

```bash
# 1. Install service template + create omega user
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/manage_tty_agents.sh install

# 2. Enable all agents (persistent across reboots)
sudo manage_tty_agents.sh enable researcher
sudo manage_tty_agents.sh enable roc_racoon
sudo manage_tty_agents.sh enable kali
sudo manage_tty_agents.sh enable observability

# 3. Start them now
sudo manage_tty_agents.sh start researcher
sudo manage_tty_agents.sh start roc_racoon
sudo manage_tty_agents.sh start kali
sudo manage_tty_agents.sh start observability
```

### Verify It Works

```bash
# Check status
manage_tty_agents.sh list
# researcher           tty3   enabled active
# roc_racoon           tty4   enabled active
# kali                 tty5   enabled active
# observability        tty6   enabled active

# Follow logs
sudo manage_tty_agents.sh logs researcher -f

# Switch to Researcher
# Press Ctrl+Alt+F3
```

### What You'll See on Each TTY

| TTY | Agent | Dashboard Shows |
|-----|-------|-----------------|
| **F3** | Researcher | Research sessions, cache hits, API calls, current task, uptime |
| **F4** | Roc Racoon | Mining status, patterns found, partitions scanned, uptime |
| **F5** | Kali | Fleet oversight, mandate enforcement, agent delegation, uptime |
| **F6** | Observability | **Live kernel logs (dmesg -w)** + CPU/memory/sovereignty metrics |

---

## 🎓 PART 9: ADVANCED PATTERNS

### Pattern 1: TTY as Secure Enclave

```python
# Agent reads sensitive config DIRECTLY from TTY (bypasses stdin/stdout)
async def read_secret(self, prompt: str) -> str:
    """Read password/API key directly from controlling TTY."""
    tty_path = f"/dev/tty{self.vt_num}"
    with open(tty_path, "r") as tty_in:
        # This NEVER touches shell history, logs, or pipes
        return getpass.getpass(prompt, stream=tty_in)
```

### Pattern 2: TTY as Crash Forensics Console

```ini
# In systemd service: TTYVTDisallocate=no
# On crash, VT persists with last screen content
# User switches to TTY: sees exact crash state
# No "where was I?" — the screen IS the state
```

### Pattern 3: TTY as Hivemind Bridge

```python
# File-based Hivemind on TTY agents (no network needed)
TTY_HIVEMIND_DIR = Path("data/coordination/tty_hivemind")

# Researcher writes:
{"entity": "researcher", "tty": "tty3", "task": "deep_research", "status": "running"}

# Kali reads (on TTY5) and coordinates:
# "Researcher busy on deep_research, delegating roc_racoon to mining"
```

### Pattern 4: TTY as Secure Boot Attestation

```bash
# Kernel command line: vt.cur_default=3 vt.default_utf8=1
# systemd: TTYPath=/dev/tty3 TTYReset=yes TTYVHangup=yes
# On boot: Researcher starts BEFORE graphical.target
# Proves: Agent ran from cold boot, no GUI interference
```

---

## 🧭 PART 10: WHEN TO USE WHAT

| Situation | Use GUI Terminal | Use Omega TTY Agent |
|-----------|------------------|---------------------|
| Quick command, interactive | ✅ | Overkill |
| Long-running research (hours) | ❌ Fragile | ✅ Bulletproof |
| GPU-intensive work | ✅ (needs GPU) | ❌ No GPU access |
| Need clipboard/copy-paste | ✅ | ❌ None |
| Security-sensitive (keys, secrets) | ❌ Leaks | ✅ Air-gapped |
| 24/7 unattended | ❌ Dies on GUI crash | ✅ Survives everything |
| Kernel debugging | ❌ Hard to see | ✅ dmesg -w native |
| Multiple simultaneous agents | ❌ Window chaos | ✅ Ctrl+Alt+F3-F6 |
| Low memory (embedded/edge) | ❌ 500 MB+ | ✅ 5 MB |

---

## 📚 PART 11: AUTHORITATIVE REFERENCES

| Command/File | Purpose |
|--------------|---------|
| `man 4 vt` | VT ioctl reference (VT_PROCESS, VT_LOCKSWITCH, etc.) |
| `man 5 systemd.exec` | `StandardInput=tty-force`, `TTYPath=`, `TTYVHangup=` |
| `man 1 chvt` | Switch VT from command line |
| `man 1 openvt` | Run command on free VT |
| `man 1 vhangup` | Revoke access to VT |
| `man 7 console_codes` | Escape sequences (colors, cursor, scrollback) |
| `man 4 fbcon` | Framebuffer console |
| `Documentation/admin-guide/vt.txt` | Kernel VT subsystem docs |
| `drivers/tty/vt/vt.c` | Kernel source — VT implementation |
| `systemd/src/core/vt.c` | systemd VT handling |

---

## 💡 PART 11: THE PHILOSOPHY

> **"The TTY is not a legacy terminal. It is the kernel's native display device.**
> 
> **Everything else — X11, Wayland, terminal emulators — is a userspace abstraction layered on top.**
> 
> **When you put an agent on a TTY, you're not 'running in a terminal.'**
> 
> **You're giving the agent DIRECT KERNEL-LEVEL DISPLAY OWNERSHIP.**
> 
> **No compositor. No window manager. No GPU driver. No clipboard. No D-Bus.**
> 
> **Just: Agent ↔ Kernel VT ↔ Framebuffer.**
> 
> **That is sovereignty."**

---

## 🎯 QUICK REFERENCE CARD

```
┌────────────────────────────────────────────────────────────────────┐
│                    OMEGA TTY QUICK REFERENCE                       │
├────────────────────────────────────────────────────────────────────┤
│  Ctrl+Alt+F1  → GUI Login          │  chvt 1                       │
│  Ctrl+Alt+F2  → Your Shell         │  chvt 2                       │
│  Ctrl+Alt+F3  → 🔱 RESEARCHER      │  chvt 3  (deep research)      │
│  Ctrl+Alt+F4  → 🦝 ROC RACOON      │  chvt 4  (legacy mining)      │
│  Ctrl+Alt+F5  → ⚖️ KALI            │  chvt 5  (oversight)          │
│  Ctrl+Alt+F6  → 📊 OBSERVABILITY   │  chvt 6  (dmesg -w, htop)     │
│  Ctrl+Alt+F7  → Back to GUI        │  chvt 7                       │
├────────────────────────────────────────────────────────────────────┤
│  fgconsole              → Current VT number                        │
│  ls /sys/class/tty/tty*/active  → All VT states                   │
│  cat /sys/class/tty/tty3/vt_mode  → VT mode (0=AUTO, 1=PROCESS)   │
│  dmesg -w               → Live kernel logs (on TTY6)              │
│  journalctl -f          → Live systemd logs                       │
│  setfont Uni3-Terminus32x16.psf.gz  → Large font (120x50)        │
│  echo 256000 > /sys/module/vt/parameters/default_utf8  → Scrollback│
├────────────────────────────────────────────────────────────────────┤
│  sudo manage_tty_agents.sh install      → One-time setup          │
│  sudo manage_tty_agents.sh enable X     → Persistent enable       │
│  sudo manage_tty_agents.sh start X      → Start now               │
│  sudo manage_tty_agents.sh logs X -f    → Follow logs             │
│  sudo manage_tty_agents.sh status X     → Check status            │
│  sudo manage_tty_agents.sh list         → List all                │
└────────────────────────────────────────────────────────────────────┘
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_tty_primer ⬡ COMPLETE*

**This primer transforms "Ctrl+Alt+F3 is a weird text mode" into "Ctrl+Alt+F3 is my sovereign research terminal."**
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
