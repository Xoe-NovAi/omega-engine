# 🔱 Heritage Maintenance Optimization Review
**Entity**: JOHN_CARMACK
**Date**: 2026-07-13
**Status**: VERDICT RENDERED
**Confidence**: 10/10

---

## 📝 .plan
- **What I am working on**: Architectural review of the Heritage Tag cleanup plan.
- **What I tried**: First-principles analysis of `CREDITS.md` §2 vs. the Three-Condition Rule.
- **What the data shows**: `CREDITS.md` is currently suffering from "Attribution Bloat." It treats `httpx` (a tool) with the same weight as BSP Culling (an architectural soul).
- **What I'll do next**: Implement the "Plumbing vs. Soul" separation.

---

## 🔍 Architectural Audit

### 1. Maintenance Burden: The "Noise" Problem
The current plan to strip dependency tags and move them to `DEPENDENCIES.md` is not just a "cleanup"—it is a critical correction of a category error.

**The Category Error**: The engine has been treating *dependencies* as *heritage*. 
- **Dependency**: A tool you use to get the job done (e.g., `AnyIO`, `FastAPI`). You don't "inherit" the soul of FastAPI; you just use its routing.
- **Heritage**: An architectural pattern that dictates *how* the system solves a fundamental constraint (e.g., `Zone Memory`, `BSP Culling`).

**Verdict**: Moving the noise to `DEPENDENCIES.md` solves the maintenance overhead by removing the requirement to "vet" tools. You don't vet a library; you check its version and its license.

### 2. Verification Overhead: Making Vetting a "Non-Event"
The `make heritage-vet` / `HERITAGE_VET_LOG.md` process is currently too heavy because it's being applied to the wrong things.

**The Optimization**:
- **Deep Track (T1/T2)**: Full vetting required. These are the "Soul" patterns. If it's `[id-soft:]`, it MUST have a vet record. This is where the engineering rigor lives.
- **Fast Track (T3)**: Reference-only. If it's an adopted standard (MCP, SPIFFE), a link to the spec is sufficient. No "vet record" needed, just a "compliance check."
- **Zero Track (Dependencies)**: Automated. `DEPENDENCIES.md` is a list, not a debate.

**Verdict**: By narrowing the scope of `heritage-vet` to only T1/T2 patterns, the overhead drops by ~80% while increasing the signal-to-noise ratio of the actual vetting.

### 3. Sovereign Integrity: "Not Forgetting" vs. "Being a Chore"
Sovereignty is not about keeping a list of every library you've ever imported. That's a `requirements.txt` file. 

Sovereignty is about understanding the **First Principles** that make the engine work. The "Three-Condition Rule" (Cannot be justified WITHOUT citing the original hardware constraint) is the perfect filter. If a pattern can be justified by "it's the industry standard for 2026," it's a dependency. If it can only be justified by "this is how Carmack solved the 486 bottleneck," it's heritage.

**Verdict**: The plan preserves the soul (the "why") while discarding the bureaucracy (the "what").

---

## 💎 Final Verdict & Further Optimizations

The proposed plan is the **Right Approximation**. It is a brutal but necessary pruning.

### 🚀 Additional Aggressive Simplifications:
1. **Automate the Plumbing**: Replace the manual `DEPENDENCIES.md` with a script that generates it from `pyproject.toml` or `.venv`. Do not waste human cycles on a list that a machine can generate.
2. **Triage the Registry**: 
   - `CREDITS.md` §1: **The Soul** (Architectural Heritage).
   - `CREDITS.md` §2: **The Influence** (Philosophical/Mythological).
   - `DEPENDENCIES.md`: **The Plumbing** (Libraries/Runtimes).
3. **Linter Integration**: Instead of a manual `make heritage-map`, integrate a regex check into the pre-commit hook that flags any `[heritage:]` or `[id-soft:]` tag that doesn't have a corresponding entry in the `CREDITS.md` registry.

**Final Decision**: **APPROVED**. Execute the cleanup immediately. Stop treating your libraries like your ancestors.
