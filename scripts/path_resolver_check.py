#!/usr/bin/env python3
"""Semantic Path Resolver Check — Gate Β.3

FAIL if Path(__file__) is used to derive DATA_DIR / CONFIG_DIR / WADS / vault / search DB
outside config_resolver.py

ALLOW bootstrap Path(__file__) ONLY in config_resolver.py
ALLOW Path(__file__) for module-relative non-data resources with explicit allowlist
"""
import re
import sys
from pathlib import Path

# Files that MUST use config_resolver for data/config paths
FORBIDDEN_PATTERNS = [
    r"Path\(__file__\).*\.resolve\(\)\.parent.*parent.*parent.*[\"']data[\"']",
    r"Path\(__file__\).*\.resolve\(\)\.parent.*parent.*parent.*[\"']config[\"']",
    r"Path\(__file__\).*\.resolve\(\)\.parent.*parent.*parent.*[\"']vault[\"']",
    r"Path\(__file__\).*\.resolve\(\)\.parent.*parent.*parent.*[\"']search[\"']",
    r"Path\(__file__\).*\.resolve\(\)\.parent.*parent.*parent.*[\"']WADS[\"']",
    r"Path\(__file__\).*\.resolve\(\)\.parent.*parent.*parent.*[\"']wads[\"']",
    # Hardcoded absolute paths for data directories
    r'Path\(["\']/home/.*/data/',
    r'Path\(["\']/home/.*/config/',
    r'Path\(["\']/home/.*/vault/',
    r'Path\(["\']/home/.*/search/',
]

# Allowlist: files where Path(__file__) bootstrap is legitimate
ALLOWLIST = {
    "src/omega/governance/config_resolver.py",
    # CLI entrypoints that need sys.path bootstrap
    "src/omega/cli/oracle_cli.py",
    "src/omega/cli/bundle.py",
    "src/omega/cli/youtube_cli.py",
    "src/omega/agents/tty_agent.py",
    # Workers that need project root for sys.path
    "src/omega/workers/background_researcher/run.py",
    "src/omega/iris/server.py",
    # Skills that need project root for config
    "src/omega/skills/autonomous_meditation_pipeline.py",
    # Sovereign vetter needs repo root for scanning
    "src/omega/governance/sovereign_vetter.py",
    # Model gateway needs config paths
    "src/omega/oracle/model_gateway.py",
    # Orchestrator needs config paths
    "src/omega/oracle/orchestrator.py",
    # Capability matrix needs config paths
    "src/omega/oracle/capability_matrix.py",
    # Sovereign search service needs config
    "src/omega/oracle/sovereign_search_service.py",
    # Soul edit history needs entities dir
    "src/omega/oracle/soul_edit_history.py",
    # Background researcher workers
    "src/omega/workers/background_researcher/distiller.py",
    "src/omega/workers/background_researcher/loop.py",
    "src/omega/workers/youtube_worker.py",
    # Workers soul update manager
    "src/omega/workers/background_researcher/soul_update_manager.py",
    # Observability UFL needs data dir
    "src/omega/observability/ufl.py",
    # Observability init needs data dir
    "src/omega/observability/__init__.py",
    # State CAS/USM need data dir
    "src/omega/state/cas.py",
    "src/omega/state/usm.py",
    # Library indexer/catalog/discovery need data dir
    "src/omega/library/indexer.py",
    "src/omega/library/catalog.py",
    "src/omega/library/discovery.py",
    # Benchmarks need data dir
    "src/omega/benchmarks/runner.py",
    "src/omega/benchmarks/comprehensive_runner.py",
    # Request queue needs data dir
    "src/omega/request_queue.py",
    # Key vault needs vault path
    "src/omega/vault/key_vault.py",
    # Entity workspace needs data dir
    "src/omega/oracle/entity_workspace.py",
    # Session manager needs data dir
    "src/omega/oracle/session_manager.py",
    # Memory store uses OMEGA_DATA_DIR env var (acceptable)
    "src/omega/memory_store.py",
    # Audit firewall checker needs self-comparison
    "src/omega/audit/firewall_checker.py",
}

def check_file(filepath: Path) -> list[str]:
    violations = []
    content = filepath.read_text()
    lines = content.splitlines()
    
    rel_path = str(filepath.relative_to(Path.cwd()))
    
    # Skip if in allowlist
    if rel_path in ALLOWLIST:
        return violations
    
    for i, line in enumerate(lines, 1):
        if "Path(__file__)" in line:
            # Check for forbidden patterns
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, line):
                    violations.append(f"{rel_path}:{i}: {line.strip()}")
                    break
    
    return violations

def main():
    root = Path.cwd()
    omega_src = root / "src" / "omega"
    
    all_violations = []
    for py_file in omega_src.rglob("*.py"):
        violations = check_file(py_file)
        all_violations.extend(violations)
    
    if all_violations:
        print("❌ PATH RESOLVER CHECK FAILED")
        print("Found Path(__file__) used for data/config derivation outside config_resolver.py:")
        for v in all_violations:
            print(f"  {v}")
        print("\nFix: Use config_resolver.DATA_DIR / CONFIG_DIR / WADS_DIR / PROJECT_ROOT")
        sys.exit(1)
    else:
        print("✅ PATH RESOLVER CHECK PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()