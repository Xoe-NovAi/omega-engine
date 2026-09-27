#!/usr/bin/env python3
"""
Comprehensive diagnostic script for rpc.mountd registration failure.
Captures strace, system state, config, and registration attempts.
"""

import subprocess
import sys
import os
import time
import json
import signal
from datetime import datetime
from pathlib import Path

class NFSMountdDiagnostics:
    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "system_info": {},
            "config_files": {},
            "service_status": {},
            "rpcbind_state": {},
            "exports_state": {},
            "strace_output": "",
            "registration_test": {},
            "netconfig": {},
            "analysis": {}
        }

    def run_cmd(self, cmd, timeout=30, capture_stderr=True):
        """Run command and return (stdout, stderr, returncode)"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", f"TIMEOUT after {timeout}s", -1
        except OSError as e:
            return "", str(e), -1

    def collect_system_info(self):
        """Collect basic system information"""
        print("📋 Collecting system info...")
        self.results["system_info"] = {
            "kernel": self.run_cmd("uname -r")[0].strip(),
            "distro": self.run_cmd("cat /etc/os-release | grep PRETTY_NAME")[0].strip(),
            "nfs_utils_version": self.run_cmd("dpkg -l | grep nfs-utils | head -1")[0].strip(),
            "libtirpc_version": self.run_cmd("dpkg -l | grep libtirpc | head -1")[0].strip(),
            "rpcbind_version": self.run_cmd("rpcbind --version 2>&1 | head -1")[0].strip(),
        }

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
            stdout, _, _ = self.run_cmd(f"cat {config} 2>&1")
            self.results["config_files"][config] = stdout

    def collect_service_status(self):
        """Collect systemd service status"""
        print("📋 Collecting service status...")
        services = ["rpcbind", "nfs-server", "nfs-mountd", "nfsdcld", "rpc-statd", "rpc-idmapd"]
        for svc in services:
            stdout, _, _ = self.run_cmd(f"systemctl status {svc} 2>&1")
            self.results["service_status"][svc] = stdout

    def collect_rpcbind_state(self):
        """Collect rpcbind registration state"""
        print("📋 Collecting rpcbind state...")
        self.results["rpcbind_state"]["rpcinfo_p"] = self.run_cmd("rpcinfo -p localhost")[0]
        self.results["rpcbind_state"]["rpcinfo_s"] = self.run_cmd("rpcinfo -s localhost")[0]
        self.results["rpcbind_state"]["rpcinfo_t"] = self.run_cmd("rpcinfo -t localhost mountd")[0]
        self.results["rpcbind_state"]["rpcinfo_u"] = self.run_cmd("rpcinfo -u localhost mountd")[0]
        
        # Check rpcbind socket
        self.results["rpcbind_state"]["sockets"] = self.run_cmd("ss -lxp | grep rpcbind")[0]
        
        # Check rpcbind process
        self.results["rpcbind_state"]["process"] = self.run_cmd("ps aux | grep rpcbind | grep -v grep")[0]

    def collect_exports_state(self):
        """Collect export state"""
        print("📋 Collecting exports state...")
        self.results["exports_state"]["exportfs_v"] = self.run_cmd("exportfs -v")[0]
        self.results["exports_state"]["etab"] = self.run_cmd("cat /var/lib/nfs/etab")[0]
        self.results["exports_state"]["proc_exports"] = self.run_cmd("cat /proc/fs/nfs/exports")[0]
        self.results["exports_state"]["nfsd_exports"] = self.run_cmd("cat /proc/fs/nfsd/exports")[0]
        self.results["exports_state"]["portlist"] = self.run_cmd("cat /proc/fs/nfsd/portlist")[0]

    def collect_netconfig(self):
        """Collect netconfig and TI-RPC state"""
        print("📋 Collecting netconfig...")
        self.results["netconfig"]["netconfig"] = self.run_cmd("cat /etc/netconfig")[0]
        self.results["netconfig"]["getnetconfig"] = self.run_cmd("getnetconfig 2>&1")[0]

    def run_strace_registration(self):
        """Run strace on rpc.mountd registration attempt"""
        print("🔍 Running strace on rpc.mountd registration...")
        
        # Stop any existing mountd
        self.run_cmd("systemctl stop nfs-mountd 2>&1; pkill -9 rpc.mountd 2>&1; sleep 2")
        
        strace_cmd = (
            "strace -f -e trace=network,connect,bind,sendto,recvfrom,socket,"
            "openat,rt_sigaction,write,exit_group /usr/sbin/rpc.mountd "
            "--port 2050 -F 2>&1"
        )
        
        print("  Starting rpc.mountd with strace...")
        proc = subprocess.Popen(
            strace_cmd, shell=True, stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, text=True
        )
        
        # Give it time to attempt registration
        time.sleep(8)
        
        # Check registration
        rpcinfo_out, _, _ = self.run_cmd("rpcinfo -p localhost | grep -E '(mountd|100005|nfs)'")
        self.results["registration_test"]["rpcinfo_after"] = rpcinfo_out
        
        # Kill strace process
        self.run_cmd("pkill -9 -f 'strace.*rpc.mountd' 2>&1; pkill -9 rpc.mountd 2>&1")
        
        # Read strace output
        try:
            stdout, stderr = proc.communicate(timeout=5)
            self.results["strace_output"] = stdout
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            self.results["strace_output"] = stdout

    def analyze(self):
        """Analyze collected data and identify root cause"""
        print("🧠 Analyzing...")
        
        analysis = {
            "issues_found": [],
            "recommendations": [],
            "root_cause_hypothesis": ""
        }
        
        # Check rpcbind running
        if "rpcbind" not in self.results["service_status"].get("rpcbind", ""):
            analysis["issues_found"].append("rpcbind service not running")
        
        # Check if mountd appears in rpcinfo
        rpcinfo = self.results["rpcbind_state"].get("rpcinfo_p", "")
        if "100005" not in rpcinfo and "mountd" not in rpcinfo:
            analysis["issues_found"].append("mountd (program 100005) NOT registered with rpcbind")
        
        # Check netconfig ordering
        netconfig = self.results["netconfig"].get("netconfig", "")
        if "udp6" in netconfig and "tcp6" in netconfig:
            lines = netconfig.strip().split('\n')
            ipv6_first = False
            for line in lines:
                if line.strip().startswith(('udp6', 'tcp6')):
                    ipv6_first = True
                    break
                elif line.strip().startswith(('udp ', 'tcp ')) and not line.strip().startswith(('udp6', 'tcp6')):
                    break
            if ipv6_first:
                analysis["issues_found"].append("IPv6 transports (udp6/tcp6) listed BEFORE IPv4 in /etc/netconfig - causes svc_register failure")
        
        # Check nfsd running
        if "nfs-server" in self.results["service_status"]:
            status = self.results["service_status"]["nfs-server"]
            if "active (exited)" in status:
                analysis["issues_found"].append("nfs-server shows 'active (exited)' - oneshot service, nfsd kernel threads may not be persistent")
        
        # Check exportfs state
        proc_exports = self.results["exports_state"].get("proc_exports", "")
        if "Version 1.1" in proc_exports and "Client" in proc_exports and not proc_exports.strip().endswith("Client"):
            analysis["issues_found"].append("Kernel export table (/proc/fs/nfs/exports) is EMPTY - nfsd has no exports loaded")
        
        # Check strace for registration attempt
        strace = self.results.get("strace_output", "")
        if strace:
            if "svc_register" not in strace and "svc_create" not in strace:
                analysis["issues_found"].append("strace shows NO svc_create/svc_register calls - mountd not attempting RPC registration")
            if "ECONNREFUSED" in strace and "@/run/rpcbind.sock" in strace:
                analysis["issues_found"].append("mountd tries abstract socket @/run/rpcbind.sock first (ECONNREFUSED), then falls back to /run/rpcbind.sock")
            if "openat.*nfsd.export" in strace:
                analysis["recommendations"].append("mountd opens /proc/net/rpc/nfsd.export/channel - using netlink mode")
        
        # Determine root cause hypothesis
        if "mountd (program 100005) NOT registered with rpcbind" in analysis["issues_found"]:
            if any("IPv6 transports" in issue for issue in analysis["issues_found"]):
                analysis["root_cause_hypothesis"] = (
                    "IPv6 entries in /etc/netconfig appear before IPv4, causing libtirpc "
                    "svc_register() to fail when trying IPv6 first. Fix: reorder netconfig "
                    "to put IPv4 (udp/tcp) before IPv6 (udp6/tcp6)."
                )
            elif "Kernel export table (/proc/fs/nfs/exports) is EMPTY" in analysis["issues_found"]:
                analysis["root_cause_hypothesis"] = (
                    "nfsd kernel threads have no exports loaded. mountd cannot register "
                    "because there's nothing to serve. Need exportfs -r BEFORE mountd starts, "
                    "and nfsd must be running with exports."
                )
            elif "strace shows NO svc_create/svc_register calls" in analysis["issues_found"]:
                analysis["root_cause_hypothesis"] = (
                    "rpc.mountd starts but fails to create RPC listeners (svc_create). "
                    "Likely cause: TI-RPC netconfig issue, missing /etc/services mountd entry, "
                    "or netlink mode failure. Try no-netlink=y in /etc/nfs.conf [mountd] section."
                )
            else:
                analysis["root_cause_hypothesis"] = (
                    "rpc.mountd starts but doesn't complete RPC registration. Check strace "
                    "for svc_create/svc_register calls and netlink vs /proc mode issues."
                )
        
        # Add recommendations
        if analysis["issues_found"]:
            analysis["recommendations"].extend([
                "1. Fix /etc/netconfig: ensure IPv4 (udp/tcp) entries come BEFORE IPv6 (udp6/tcp6)",
                "2. Add 'no-netlink=y' to [mountd] section in /etc/nfs.conf to force /proc mode",
                "3. Ensure /etc/services has 'mountd 2050/tcp' and 'mountd 2050/udp' entries",
                "4. Restart order: rpcbind → nfs-server (exportfs -r) → nfs-mountd",
                "5. Verify nfsd kernel threads are running: 'ps aux | grep nfsd'",
                "6. Use 'exportfs -rv' to load exports into kernel BEFORE starting mountd",
            ])
        
        self.results["analysis"] = analysis

    def save_results(self, output_path=None):
        """Save results to JSON file"""
        if output_path is None:
            output_path = f"/home/xnai/Documents/Projects/omega-engine-alpha/nfs_mountd_diagnosis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
        return output_path

    def print_summary(self):
        """Print human-readable summary"""
        print("\n" + "="*80)
        print("DIAGNOSTIC SUMMARY")
        print("="*80)
        
        print("\n🔴 ISSUES FOUND:")
        for issue in self.results["analysis"].get("issues_found", []):
            print(f"  • {issue}")
        
        if not self.results["analysis"].get("issues_found"):
            print("  (none)")
        
        print("\n🎯 ROOT CAUSE HYPOTHESIS:")
        print(f"  {self.results['analysis'].get('root_cause_hypothesis', 'Unknown')}")
        
        print("\n💡 RECOMMENDATIONS:")
        for rec in self.results["analysis"].get("recommendations", []):
            print(f"  {rec}")

def main():
    diag = NFSMountdDiagnostics()
    
    print("="*80)
    print("NFS MOUNTD REGISTRATION DIAGNOSTIC")
    print("="*80)
    print()
    
    diag.collect_system_info()
    diag.collect_config_files()
    diag.collect_service_status()
    diag.collect_rpcbind_state()
    diag.collect_exports_state()
    diag.collect_netconfig()
    diag.run_strace_registration()
    diag.analyze()
    diag.save_results()
    diag.print_summary()

if __name__ == "__main__":
    main()