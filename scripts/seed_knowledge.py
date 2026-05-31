import os
import shutil
from pathlib import Path

# Mapping of Entity (Pillar) to Research Doc Patterns
MAPPING = {
    "sysadmin": [
        "R_PODMAN", "R_CONTAINER", "R_ZEN2", "R_MEMORY_PRUNER", 
        "B8_NATIVE", "R13_zen2", "R42_zen2", "R15_podman"
    ],
    "datastore": [
        "R_QDRANT", "R_HOLOGRAPHIC", "R_LEGACY_XREF", "R33_holographic", 
        "R39_legacy", "R34_intake", "R14_legacy"
    ],
    "buildmaster": [
        "R99_PR_READINESS", "R-PHASE-C", "GITHUB_COPILOT", 
        "R99_DEEP_RESEARCH", "R60_SOVEREIGN_MODEL"
    ],
    "bridge": [
        "R_MCP_SPEC", "R-OPENCODE-MCP", "R-OPENCODE-CUSTOM-PROVIDER", 
        "A2A_PROTOCOL", "R29_mcp", "R28_omega"
    ],
    "sentinel": [
        "R-PERM", "R-OPENC-PERM", "R_SOVEREIGN_MAINTENANCE", 
        "R-PODMAN-SOV-V2", "R15_podman_permission", "R18_permission", 
        "R_OPENC_PERM", "R_OPENC_PERMISSIONS", "R_OPENC_PERMISSIONS_FIX"
    ],
    "modelgate": [
        "R01_GOOGLE", "R06_CIRCUIT_BREAKER", "R-KILO-COPILOT", "R-P001", 
        "R-P_VALIDATED", "R01_google", "R02_samba", "R03_cerebras", 
        "R04_fallback", "R05_model", "R07_escalation", "R08_token", 
        "R14_provider", "R16_core_provider", "R17_new_providers", 
        "R25_gemma", "R52a_openrouter", "R53_triangulation", 
        "R66_FREE_TIER", "R67_LOCAL", "R72_gemma", "R96_guard"
    ],
    "context": [
        "R50_SESSION_ID", "R51_CONTEXT_BUILDER", "R_HOLOGRAPHIC_MEMORY", 
        "R30_soul", "R19_soul", "R10_soul", "R11_context"
    ],
    "watchtower": [
        "R-BACKGR", "R14_PROVIDER_HEALTH", "R_MEMORY_PRUNER", 
        "B5_HEALTHMONITOR", "R14_provider_health", "R_BACKGROUND"
    ],
    "link": [
        "R-SUB-LESSONS", "R31_CROSS_POLLINATION", "R-SUB-REC", 
        "R31_cross_pollination", "R_SUBAGENT", "LATTICE_ORCHESTRATION", 
        "SUBAGENT_FLEET", "SUBAGENT_STATE"
    ],
    "verifier": [
        "R99_PR_READINESS", "R-PHASE-C", "R-SMOKE-TEST", "R71_knowledge"
    ],
}

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = REPO_ROOT / "docs" / "research"
ENTITIES_DIR = REPO_ROOT / "data" / "entities"

def seed():
    print(f"Seeding knowledge from {RESEARCH_DIR} to {ENTITIES_DIR}...")
    
    # Track statistics
    stats = {entity: 0 for entity in MAPPING}
    total_copied = 0

    # Ensure entity directories exist
    for entity in MAPPING:
        knowledge_dir = ENTITIES_DIR / entity / "knowledge"
        knowledge_dir.mkdir(parents=True, exist_ok=True)

    # Process each file in research directory
    for doc_path in RESEARCH_DIR.glob("*.md"):
        filename = doc_path.name
        
        for entity, patterns in MAPPING.items():
            matched = False
            for pattern in patterns:
                if filename.startswith(pattern):
                    matched = True
                    break
            
            if matched:
                target_path = ENTITIES_DIR / entity / "knowledge" / filename
                shutil.copy2(doc_path, target_path)
                stats[entity] += 1
                total_copied += 1
                print(f"  [{entity}] Copied {filename}")

    print("\nSeeding complete!")
    print(f"Total documents copied: {total_copied}")
    for entity, count in stats.items():
        print(f"  - {entity}: {count}")

    # Generate INDEX.md for each entity
    for entity in MAPPING:
        knowledge_dir = ENTITIES_DIR / entity / "knowledge"
        index_path = knowledge_dir / "INDEX.md"
        
        with open(index_path, "w") as f:
            f.write(f"# Knowledge Index — {entity.title()}\n\n")
            f.write(f"This is the primary knowledge repository for the {entity.title()} pillar.\n\n")
            f.write("## Documents\n\n")
            
            docs = sorted([d.name for d in knowledge_dir.glob("*.md") if d.name != "INDEX.md"])
            for doc in docs:
                f.write(f"- [{doc}]({doc})\n")
        
        print(f"Generated INDEX.md for {entity}")

if __name__ == "__main__":
    seed()
