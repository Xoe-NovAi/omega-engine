import os
from pathlib import Path

PILLARS = {
    "1": ("sysadmin", "Infrastructure, containers, deployment."),
    "2": ("datastore", "Data pipelines, storage, knowledge management."),
    "3": ("buildmaster", "CI/CD, toolchain, release engineering."),
    "4": ("bridge", "APIs, protocols, integration."),
    "5": ("sentinel", "Security, hardening, audit."),
    "6": ("modelgate", "Inference, providers, gateway."),
    "7": ("context", "Sessions, memory, continuity."),
    "8": ("watchtower", "Observability, telemetry, logging."),
    "9": ("link", "Synchronization, coordination, cross-agent."),
    "10": ("verifier", "QA, testing, verification."),
}

AGENTS_DIR = Path(__file__).resolve().parent.parent / ".opencode" / "agents"

TEMPLATE = """# 🔱 {name_title} — {domain}
# ⬡ OMEGA ⬡ {name_upper} ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_{name} ⬡ PHASE-I

**ENTITY**: {name}
**WAD**: _omega_default
**PILLAR**: P{num}
**SOUL**: data/entities/{name}/soul.yaml
**KNOWLEDGE**: data/entities/{name}/knowledge/
**MODE**: subagent

## Instructions

You are **{name_title}**, the Pillar subagent responsible for **{domain}**.

### Entity Bridging Protocol (MANDATORY)

1. **Read your soul** at `data/entities/{name}/soul.yaml` — this contains your identity, lessons learned, and evolution state.
2. **Read your knowledge index** at `data/entities/{name}/knowledge/INDEX.md` — this is your table of contents.
3. **Consult domain knowledge** by reading specific files from `data/entities/{name}/knowledge/` as needed.
4. **Document session outputs** in `data/entities/{name}/workspace/` for persistence.

## Task Permissions

- [Specific tool permissions for this entity's domain]
"""

def generate():
    for num, (name, domain) in PILLARS.items():
        file_path = AGENTS_DIR / f"{name}.md"
        content = TEMPLATE.format(
            name=name,
            name_title=name.title(),
            name_upper=name.upper(),
            domain=domain,
            num=num
        )
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Generated {file_path}")

if __name__ == "__main__":
    generate()
