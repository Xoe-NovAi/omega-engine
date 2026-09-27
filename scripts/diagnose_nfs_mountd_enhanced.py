#!/usr/bin/env python3
"""
Enhanced NFS mountd diagnostic with proper subprocess handling, signal management,
and comprehensive error capture. Runs strace in background with proper cleanup.

Sync by design (CODE_QUALITY §1): every collection step is sequential and the
only background process is strace — subprocess.Popen covers it. No asyncio/trio.
"""

import subprocess
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class DiagnosticResult:
    """Container for all diagnostic results"""
    timestamp: str
    system_info: Dict[str, str]
    config_files: Dict[str, str]
    service_status: Dict[str, str]
    rpcbind_state: Dict[str, str]
    exports_state: Dict[str, str]
    netconfig: Dict[str, str]
    strace_output: str
    registration_test: Dict[str, str]
    analysis: Dict[str, Any]
    errors: list

class MountdDiagnostics:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path.cwd()
        self.results = DiagnosticResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            system_info={},
            config_files={},
            service_status={},
            rpcbind_state={},
            exports_state={},
            netconfig={},
            strace_output="",
            registration_test={},
            analysis={},
            errors=[]
        )
        self.strace_proc: Optional[subprocess.Popen] = None
        self.mountd_proc: Optional[subprocess.Popen] = None
        self._cleanup_done = False

    def run_cmd(self, cmd: str, timeout: int = 30) -> Tuple[str, str, int]:
        """Run command synchronously with timeout"""
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired:
            return "", f"TIMEOUT after {timeout}s", -1
        except OSError as e:
            return "", str(e), -1

    def run_cmd_capture(self, cmd: str, timeout: int = 30) -> str:
        """Run command and return combined output"""
        stdout, stderr, _ = self.run_cmd(cmd, timeout)
        return stdout + stderr

    def add_error(self, msg: str):
        """Add error to results"""
        self.results.errors.append(f"{datetime.now(timezone.utc).isoformat()}: {msg}")

    def collect_system_info(self):
        """Collect basic system information"""
        print("📋 Collecting system info...")
        cmds = {
            "kernel": "uname -r",
            "distro": "cat /etc/os-release | grep PRETTY_NAME",
            "nfs_utils": "dpkg -l | grep nfs-utils | head -1",
            "libtirpc": "dpkg -l | grep libtirpc | head -1",
            "rpcbind_ver": "rpcbind --version 2>&1 | head -1",
        }
        for key, cmd in cmds.items():
            self.results.system_info[key] = self.run_cmd_capture(cmd).strip()

    def collect_config_files(self):
        """Collect all relevant config files"""
        print("📋 Collecting config files...")
        configs = [
            "/etc/nfs.conf",
            "/etc/exports",
            "/etc/exports.d/node-drive.exports",
            "/etc/netconfig",
            "/etc/services",
            "/etc/hosts.allow",
            "/etc/hosts.deny",
        ]
        for config in configs:
            self.results.config_files[config] = self.run_cmd_capture(f"cat {config} 2>&1")

    def collect_service_status(self):
        """Collect systemd service status"""
        print("📋 Collecting service status...")
        services = ["rpcbind", "nfs-server", "nfs-mountd", "nfsdcld", "rpc-statd", "rpc-idmapd"]
        for svc in services:
            self.results.service_status[svc] = self.run_cmd_capture(f"systemctl status {svc} 2>&1")

    def collect_rpcbind_state(self):
        """Collect rpcbind registration state"""
        print("📋 Collecting rpcbind state...")
        self.results.rpcbind_state["rpcinfo_p"] = self.run_cmd_capture("rpcinfo -p localhost")
        self.results.rpcbind_state["rpcinfo_s"] = self.run_cmd_capture("rpcinfo -s localhost")
        self.results.rpcbind_state["rpcinfo_t"] = self.run_cmd_capture("rpcinfo -t localhost mountd")
        self.results.rpcbind_state["rpcinfo_u"] = self.run_cmd_capture("rpcinfo -u localhost mountd")
        self.results.rpcbind_state["sockets"] = self.run_cmd_capture("ss -lxp | grep rpcbind")
        self.results.rpcbind_state["process"] = self.run_cmd_capture("ps aux | grep rpcbind | grep -v grep")

    def collect_exports_state(self):
        """Collect export state"""
        print("📋 Collecting exports state...")
        self.results.exports_state["exportfs_v"] = self.run_cmd_capture("exportfs -v")
        self.results.exports_state["etab"] = self.run_cmd_capture("cat /var/lib/nfs/etab")
        self.results.exports_state["proc_exports"] = self.run_cmd_capture("cat /proc/fs/nfs/exports")
        self.results.exports_state["nfsd_exports"] = self.run_cmd_capture("cat /proc/fs/nfsd/exports")
        self.results.exports_state["portlist"] = self.run_cmd_capture("cat /proc/fs/nfsd/portlist")

    def collect_netconfig(self):
        """Collect netconfig and TI-RPC state"""
        print("📋 Collecting netconfig...")
        self.results.netconfig["netconfig"] = self.run_cmd_capture("cat /etc/netconfig")
        self.results.netconfig["getnetconfig"] = self.run_cmd_capture("getnetconfig 2>&1")

    def run_strace_registration(self, duration: int = 15) -> str:
        """Run strace on rpc.mountd registration attempt with proper cleanup"""
        print(f"🔍 Running strace on rpc.mountd registration (duration: {duration}s)...")

        # Stop any existing mountd
        self.run_cmd("systemctl stop nfs-mountd 2>&1; pkill -9 rpc.mountd 2>&1; sleep 2")

        strace_cmd = (
            "strace -f -e trace=network,connect,bind,sendto,recvfrom,socket,"
            "openat,rt_sigaction,write,exit_group,clone,fork /usr/sbin/rpc.mountd "
            "--port 2050 -F 2>&1"
        )

        print("  Starting rpc.mountd with strace...")
        self.strace_proc = subprocess.Popen(
            strace_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Give it time to attempt registration
        time.sleep(duration)

        # Check registration
        rpcinfo_out = self.run_cmd_capture("rpcinfo -p localhost | grep -E '(mountd|100005|nfs)'")
        self.results.registration_test["rpcinfo_after"] = rpcinfo_out

        # Proper cleanup
        self._cleanup_processes()

        # Read strace output (drain the pipe after cleanup)
        if self.strace_proc and self.strace_proc.stdout:
            try:
                stdout_text, _ = self.strace_proc.communicate(timeout=5)
                return stdout_text or "[no strace output captured]"
            except subprocess.TimeoutExpired:
                self.strace_proc.kill()
                self.strace_proc.communicate()
                return "[strace read timeout]"

        return "[no strace output captured]"

    def _cleanup_processes(self):
        """Clean up any running processes"""
        if self.strace_proc and self.strace_proc.poll() is None:
            self.strace_proc.terminate()
            try:
                self.strace_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.strace_proc.kill()
                self.strace_proc.wait()

        if self.mountd_proc and self.mountd_proc.poll() is None:
            self.mountd_proc.terminate()
            try:
                self.mountd_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.mountd_proc.kill()
                self.mountd_proc.wait()

        # Fallback cleanup
        self.run_cmd("pkill -9 -f 'strace.*rpc.mountd' 2>&1; pkill -9 rpc.mountd 2>&1")

    def analyze(self):
        """Analyze collected data and identify root cause"""
        print("🧠 Analyzing...")

        issues = []
        recommendations = []

        # Check mountd registration
        rpcinfo = self.results.rpcbind_state.get("rpcinfo_p", "")
        if "100005" not in rpcinfo and "mountd" not in rpcinfo:
            issues.append("mountd (program 100005) NOT registered with rpcbind")

        # Check netconfig ordering
        netconfig = self.results.netconfig.get("netconfig", "")
        lines = netconfig.strip().split('\n')
        ipv6_first = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('udp6', 'tcp6')):
                ipv6_first = True
                break
            elif stripped.startswith(('udp ', 'tcp ')) and not stripped.startswith(('udp6', 'tcp6')):
                break
        if ipv6_first:
            issues.append("IPv6 transports (udp6/tcp6) listed BEFORE IPv4 in /etc/netconfig - causes svc_register failure")

        # Check kernel export table
        proc_exports = self.results.exports_state.get("proc_exports", "")
        if "Version 1.1" in proc_exports and proc_exports.strip().endswith("Client"):
            issues.append("Kernel export table (/proc/fs/nfs/exports) is EMPTY - nfsd has no exports loaded")

        # Check strace for registration attempt
        strace = self.results.strace_output
        if strace:
            if "svc_register" not in strace and "svc_create" not in strace:
                issues.append("strace shows NO svc_create/svc_register calls - mountd not attempting RPC registration")
            if "openat.*nfsd.export" in strace:
                issues.append("mountd opens /proc/net/rpc/nfsd.export/channel - using netlink mode")
            if "ECONNREFUSED" in strace and "@/run/rpcbind.sock" in strace:
                issues.append("mountd tries abstract socket @/run/rpcbind.sock first (ECONNREFUSED), then falls back to /run/rpcbind.sock")
            if "Permission denied" in strace and "/proc/net/rpc" in strace:
                issues.append("mountd cannot access /proc/net/rpc channels (Permission denied) - needs CAP_SYS_ADMIN or root")
            if "exit_group(1)" in strace:
                issues.append("mountd exited with code 1 after permission errors on netlink channels")

        # Determine root cause
        root_cause = ""
        if "mountd (program 100005) NOT registered with rpcbind" in issues:
            if any("IPv6 transports" in i for i in issues):
                root_cause = (
                    "IPv6 entries in /etc/netconfig appear before IPv4, causing libtirpc "
                    "svc_register() to fail when trying IPv6 first. Fix: reorder netconfig "
                    "to put IPv4 (udp/tcp) before IPv6 (udp6/tcp6)."
                )
            elif "Kernel export table (/proc/fs/nfs/exports) is EMPTY" in issues:
                root_cause = (
                    "nfsd kernel threads have no exports loaded. mountd cannot register "
                    "because there's nothing to serve. Need exportfs -r BEFORE mountd starts."
                )
            elif any("Permission denied" in i and "/proc/net/rpc" in i for i in issues):
                root_cause = (
                    "rpc.mountd lacks permissions to access netlink channels "
                    "(/proc/net/rpc/nfsd.export/channel). Running as root via sudo should work, "
                    "but AppArmor or capability bounding set may be restricting it. "
                    "Try: 1) Run with full sudo (not user), 2) Disable AppArmor for rpc.mountd, "
                    "3) Use no-netlink=y in /etc/nfs.conf to force /proc mode."
                )
            elif "strace shows NO svc_create/svc_register calls" in issues:
                root_cause = (
                    "rpc.mountd starts but fails to create RPC listeners (svc_create). "
                    "Likely cause: TI-RPC netconfig issue, missing /etc/services mountd entry, "
                    "or netlink mode failure. Try no-netlink=y in /etc/nfs.conf [mountd] section."
                )
            else:
                root_cause = (
                    "rpc.mountd starts but doesn't complete RPC registration. Check strace "
                    "for svc_create/svc_register calls and netlink vs /proc mode issues."
                )

        # Recommendations
        if "Kernel export table" in str(issues):
            recommendations = [
                "1. Run 'exportfs -rv' to load exports into kernel BEFORE starting mountd",
                "2. Ensure nfs-server runs exportfs -r in ExecStartPre",
            ]
        else:
            recommendations = [
                "1. Fix /etc/netconfig: ensure IPv4 (udp/tcp) entries come BEFORE IPv6 (udp6/tcp6)",
                "2. Add 'no-netlink=y' to [mountd] section in /etc/nfs.conf to force /proc mode",
                "3. Ensure /etc/services has 'mountd 2050/tcp' and 'mountd 2050/udp' entries",
                "4. Restart order: rpcbind → nfs-server (exportfs -r) → nfs-mountd",
                "5. Verify nfsd kernel threads are running: 'ps aux | grep nfsd'",
                "6. Run mountd with full root privileges (sudo -E) to access netlink channels",
            ]

        self.results.analysis = {
            "issues_found": issues,
            "recommendations": recommendations,
            "root_cause_hypothesis": root_cause
        }

    def run_full_diagnostic(self) -> Path:
        """Run complete diagnostic suite"""
        print("=" * 80)
        print("ENHANCED NFS MOUNTD REGISTRATION DIAGNOSTIC")
        print("=" * 80)
        print()

        # Collect all data
        self.collect_system_info()
        self.collect_config_files()
        self.collect_service_status()
        self.collect_rpcbind_state()
        self.collect_exports_state()
        self.collect_netconfig()

        # Run strace registration test
        self.results.strace_output = self.run_strace_registration(duration=15)

        # Analyze
        self.analyze()

        # Save results
        output_path = self.output_dir / f"nfs_mountd_diagnosis_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, 'w') as f:
            json.dump(asdict(self.results), f, indent=2, default=str)

        print(f"\n💾 Results saved to: {output_path}")

        # Print summary
        self._print_summary()

        return output_path

    def _print_summary(self):
        """Print human-readable summary"""
        print("\n" + "=" * 80)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 80)

        print("\n🔴 ISSUES FOUND:")
        for issue in self.results.analysis.get("issues_found", []):
            print(f"  • {issue}")
        if not self.results.analysis.get("issues_found"):
            print("  (none)")

        print("\n🎯 ROOT CAUSE HYPOTHESIS:")
        print(f"  {self.results.analysis.get('root_cause_hypothesis', 'Unknown')}")

        print("\n💡 RECOMMENDATIONS:")
        for rec in self.results.analysis.get("recommendations", []):
            print(f"  {rec}")

        if self.results.errors:
            print("\n⚠️  ERRORS DURING DIAGNOSTIC:")
            for err in self.results.errors:
                print(f"  • {err}")

def main():
    diag = MountdDiagnostics()
    diag.run_full_diagnostic()

if __name__ == "__main__":
    main()
