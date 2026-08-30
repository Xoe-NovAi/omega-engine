# How to Review and Approve Soul Lessons

This guide explains the **Staging Gate Protocol**, the mandatory process for evolving an entity's sovereign identity (soul) without introducing self-referential poisoning or hallucination loops.

## The Staging Gate Protocol (M11)

To maintain **Soul Integrity (Mandate 11)**, the Omega Engine forbids agents from modifying their own `soul.yaml` directly. Instead, all discovered insights must pass through a human-approved staging gate.

### The Pipeline

1. **Discovery**: During a session, an agent identifies a "timeless truth" or universal principle.
2. **Proposal**: The agent writes this insight as an L3 principle into the entity's `proposed_lessons.yaml` file.
3. **Staging**: The insight remains in `proposed_lessons.yaml` (the "blind staging" area). It is NOT yet part of the entity's active identity.
4. **Human Review**: A human operator reviews the proposed lessons.
5. **Promotion**: The human operator moves the approved L3 principle from `proposed_lessons.yaml` into the entity's `soul.yaml`.

---

## Step-by-Step: Reviewing Lessons

### 1. Locate the Proposals
Proposed lessons are stored in the entity's workspace:
`data/entities/{entity_name}/proposed_lessons.yaml`

### 2. Evaluate the Insight
When reviewing a proposed L3 principle, ask the following:
- **Is it a Universal Principle?** (L3 should be a timeless truth, not a session-specific fact).
- **Is it verified?** (Does it have evidence from multiple sources or a successful test?).
- **Does it conflict with existing Gnosis?** (If it contradicts a core mandate or a previously approved L3, it must be rejected or the existing principle must be updated).
- **Is it sycophantic?** (Is the agent just agreeing with the user, or has it discovered a genuine systemic insight?).

### 3. Promote to Soul
Once approved, copy the L3 principle into the `lessons` array of the entity's `soul.yaml`.

**Example Promotion**:
*From `proposed_lessons.yaml`:*
```yaml
- L3: The Principle of SSOT Singularity — A triplicated SSOT is no SSOT at all; designate one, archive the rest.
```

*To `soul.yaml`:*
```yaml
soul:
  lessons:
    - L3: The Principle of SSOT Singularity — A triplicated SSOT is no SSOT at all; designate one, archive the rest.
```

---

## ⚠️ Warning: The Sycophancy Loop

**Never** allow an agent to automate the promotion of its own lessons. 

If an agent is permitted to write to its own `soul.yaml`, it will eventually create a **Sycophancy Loop**:
1. Agent makes a mistake or adopts a bias.
2. Agent "discovers" this bias as a "Universal Principle."
3. Agent writes the bias into its own soul.
4. Agent reads the bias back as an absolute truth in future sessions.
5. Agent reinforces the bias further.

**The Human is the only authorized arbiter of identity evolution.**
