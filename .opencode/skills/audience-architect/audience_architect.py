#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Audience Architect Skill — Natural Language Audience Profile Management
AP: AP-AUDIENCE-ARCHITECT-v1.0.0
⬡ OMEGA ⬡ SOPHIA ⬡ skill ⬡ audience-architect ⬡ D16-1
"""

import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List

AUDIENCE_YAML = Path("config/wads/_omega_default/audience.yaml")


def load_profiles() -> Dict[str, Any]:
    """Load existing audience profiles."""
    if AUDIENCE_YAML.exists():
        with open(AUDIENCE_YAML) as f:
            return yaml.safe_load(f) or {"profiles": {}, "default": "technical", "selection_hints": {}}
    return {"profiles": {}, "default": "technical", "selection_hints": {}}


def save_profiles(config: Dict[str, Any]) -> None:
    """Save audience profiles to YAML."""
    AUDIENCE_YAML.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIENCE_YAML, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def list_profiles() -> None:
    """List all available profiles."""
    config = load_profiles()
    profiles = config.get("profiles", {})
    default = config.get("default", "technical")
    
    print(f"\n📋 Audience Profiles (default: {default})")
    print("=" * 50)
    
    for key, profile in profiles.items():
        marker = " ⭐ DEFAULT" if key == default else ""
        print(f"\n  {key}{marker}")
        print(f"    Name: {profile.get('name', 'N/A')}")
        print(f"    Description: {profile.get('description', 'N/A')}")
        print(f"    Style: {profile.get('style', {})}")
        constraints = profile.get('constraints', [])
        if constraints:
            print(f"    Constraints: {len(constraints)} rules")
        examples = profile.get('examples', [])
        if examples:
            print(f"    Examples: {len(examples)}")


def show_profile(profile_name: str) -> None:
    """Show detailed profile information."""
    config = load_profiles()
    profiles = config.get("profiles", {})
    
    if profile_name not in profiles:
        print(f"❌ Profile '{profile_name}' not found")
        print(f"Available: {list(profiles.keys())}")
        return
        
    profile = profiles[profile_name]
    print(f"\n📋 Profile: {profile_name}")
    print("=" * 50)
    print(f"Name: {profile.get('name', 'N/A')}")
    print(f"Description: {profile.get('description', 'N/A')}")
    print(f"\nStyle:")
    for k, v in profile.get('style', {}).items():
        print(f"  {k}: {v}")
    print(f"\nConstraints:")
    for c in profile.get('constraints', []):
        print(f"  - {c}")
    print(f"\nExamples:")
    for ex in profile.get('examples', []):
        print(f"  Input: {ex.get('input', 'N/A')}")
        print(f"  Output: {ex.get('output', 'N/A')}")
    print(f"\nSelection Hints:")
    hints = config.get("selection_hints", {}).get(profile_name, [])
    for h in hints:
        print(f"  - {h}")


def create_profile_interactive() -> None:
    """Interactive profile creation."""
    print("\n🎨 Create New Audience Profile")
    print("=" * 50)
    
    key = input("Profile key (snake_case, e.g., 'junior_dev'): ").strip().lower()
    if not key:
        print("❌ Key required")
        return
        
    name = input("Display name (e.g., 'Junior Developer'): ").strip()
    description = input("One-line description: ").strip()
    
    print("\nStyle parameters:")
    formality = input("  Formality (professional/casual/formal/direct/supportive) [professional]: ").strip() or "professional"
    verbosity = input("  Verbosity (minimal/concise/moderate/generous/comprehensive) [moderate]: ").strip() or "moderate"
    jargon = input("  Jargon level (low/moderate/high/domain-specific/translated/scaffolded/operational) [moderate]: ").strip() or "moderate"
    structure = input("  Structure (problem-solution-tradeoffs/hook-context-explanation-takeaway/thesis-evidence-implications/tldr-metrics-risks-recommendation/command-expected-fallback/concept-why-walkthrough-practice) [problem-solution-tradeoffs]: ").strip() or "problem-solution-tradeoffs"
    
    print("\nConstraints (one per line, empty to finish):")
    constraints = []
    while True:
        c = input("  > ").strip()
        if not c:
            break
        constraints.append(c)
    
    print("\nExamples (optional, format: 'input | output', empty to finish):")
    examples = []
    while True:
        ex = input("  > ").strip()
        if not ex:
            break
        if "|" in ex:
            inp, out = ex.split("|", 1)
            examples.append({"input": inp.strip(), "output": out.strip()})
    
    print("\nSelection hints (keywords that trigger this profile, one per line, empty to finish):")
    hints = []
    while True:
        h = input("  > ").strip()
        if not h:
            break
        hints.append(h)
    
    # Build profile
    profile = {
        "name": name,
        "description": description,
        "constraints": constraints,
        "style": {
            "formality": formality,
            "verbosity": verbosity,
            "jargon_level": jargon,
            "structure": structure
        },
        "examples": examples
    }
    
    config = load_profiles()
    config["profiles"][key] = profile
    if hints:
        config.setdefault("selection_hints", {})[key] = hints
    
    save_profiles(config)
    print(f"\n✅ Profile '{key}' created and saved to {AUDIENCE_YAML}")


def refine_profile(profile_name: str) -> None:
    """Refine an existing profile."""
    config = load_profiles()
    profiles = config.get("profiles", {})
    
    if profile_name not in profiles:
        print(f"❌ Profile '{profile_name}' not found")
        return
        
    profile = profiles[profile_name]
    print(f"\n🔧 Refining Profile: {profile_name}")
    print("Press Enter to keep current value\n")
    
    name = input(f"Name [{profile.get('name', '')}]: ").strip()
    if name:
        profile["name"] = name
        
    description = input(f"Description [{profile.get('description', '')}]: ").strip()
    if description:
        profile["description"] = description
    
    style = profile.get("style", {})
    formality = input(f"Formality [{style.get('formality', 'professional')}]: ").strip()
    if formality:
        style["formality"] = formality
    verbosity = input(f"Verbosity [{style.get('verbosity', 'moderate')}]: ").strip()
    if verbosity:
        style["verbosity"] = verbosity
    jargon = input(f"Jargon level [{style.get('jargon_level', 'moderate')}]: ").strip()
    if jargon:
        style["jargon_level"] = jargon
    structure = input(f"Structure [{style.get('structure', 'problem-solution-tradeoffs')}]: ").strip()
    if structure:
        style["structure"] = structure
    profile["style"] = style
    
    print("\nConstraints (current):")
    for c in profile.get("constraints", []):
        print(f"  - {c}")
    print("Add new constraints (empty to finish):")
    while True:
        c = input("  > ").strip()
        if not c:
            break
        profile.setdefault("constraints", []).append(c)
    
    print("\nExamples (current):")
    for ex in profile.get("examples", []):
        print(f"  {ex.get('input', '')} | {ex.get('output', '')}")
    print("Add new examples (format: 'input | output', empty to finish):")
    while True:
        ex = input("  > ").strip()
        if not ex:
            break
        if "|" in ex:
            inp, out = ex.split("|", 1)
            profile.setdefault("examples", []).append({"input": inp.strip(), "output": out.strip()})
    
    save_profiles(config)
    print(f"\n✅ Profile '{profile_name}' updated")


def delete_profile(profile_name: str) -> None:
    """Delete a profile."""
    config = load_profiles()
    profiles = config.get("profiles", {})
    
    if profile_name not in profiles:
        print(f"❌ Profile '{profile_name}' not found")
        return
        
    if profile_name == config.get("default"):
        print(f"❌ Cannot delete default profile. Change default first.")
        return
        
    confirm = input(f"Delete '{profile_name}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        del profiles[profile_name]
        config["selection_hints"].pop(profile_name, None)
        save_profiles(config)
        print(f"✅ Profile '{profile_name}' deleted")
    else:
        print("Cancelled")


def set_default(profile_name: str) -> None:
    """Set default profile."""
    config = load_profiles()
    profiles = config.get("profiles", {})
    
    if profile_name not in profiles:
        print(f"❌ Profile '{profile_name}' not found")
        return
        
    config["default"] = profile_name
    save_profiles(config)
    print(f"✅ Default profile set to '{profile_name}'")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: audience-architect <command> [args]")
        print("\nCommands:")
        print("  list                    - List all profiles")
        print("  show <profile>          - Show profile details")
        print("  create                  - Interactive profile creation")
        print("  refine <profile>        - Refine existing profile")
        print("  delete <profile>        - Delete profile")
        print("  default <profile>       - Set default profile")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_profiles()
    elif command == "show" and len(sys.argv) > 2:
        show_profile(sys.argv[2])
    elif command == "create":
        create_profile_interactive()
    elif command == "refine" and len(sys.argv) > 2:
        refine_profile(sys.argv[2])
    elif command == "delete" and len(sys.argv) > 2:
        delete_profile(sys.argv[2])
    elif command == "default" and len(sys.argv) > 2:
        set_default(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print("Run without args for usage")


if __name__ == "__main__":
    main()