# 🔱 Implementation Blueprint: Lattice Dispatch

**Goal**: Implement dynamic multi-agent topology (Linear Chaining vs. Triad Spawning) to handle varying cognitive complexities.

**Target Files**:
- `src/omega/oracle/orchestrator.py`
- `src/omega/oracle/oracle.py`
- `src/omega/oracle/resonance_map.py` (New)

**Step-by-Step Instructions**:

### Step 1: Define the Resonance Map
Create `src/omega/oracle/resonance_map.py`:
- Implement a mapping of `QueryType` to `ResonanceTriad`.
- **Triad Definitions**:
    - `Architectural Review`: [Auditor, Skeptic, Optimizer]
    - `Gnosis Extraction`: [Archaeologist, Critic, Synthesizer]
    - `Security Hardening`: [Guardian, Red-Teamer, Verifier]
    - `Strategic Planning`: [Tactician, Risk-Analyst, Visionary]
    - `Code Refactor`: [Purist, Pragmatist, Architect]

### Step 2: Implement Dispatch Logic in Orchestrator
Modify `src/omega/oracle/orchestrator.py`:
- **Topology Selector**: Create a method `determine_topology(query: str) -> TopologyMode`.
    - **Linear**: Default for simple requests or sequential dependencies.
    - **Triad**: Triggered by keywords like "review", "audit", "strategize", "synthesize", or high-complexity markers.
- **Triad Spawning Logic**:
    1. Resolve the `ResonanceTriad` from `resonance_map.py` based on the query type.
    2. Launch three concurrent headless agents using `anyio.create_task_group()`.
    3. Inject a unique Archetype Soul into each agent's system prompt (e.g., Agent A = Anchor, Agent B = Friction, Agent C = Catalyst).
    4. Collect responses from all three agents.
    - **Synthesis Step**: 
        - Pass the three divergent responses to a final `Synthesizer` projection.
        - Use the following **MaKaLi Synthesis Prompt**:
          \"You are the MaKaLi Synthesis Projection. Your goal is to reconcile the three divergent perspectives provided by the Resonance Triad into a single, hardened conclusion.
          1. **SIFT**: Identify the core truth and eliminate noise/redundancy from all three responses.
          2. **EMBRACE**: Integrate the critical friction from the 'Skeptic' and the creative leverage from the 'Catalyst'.
          3. **BALANCE**: Resolve the contradictions into a final, authoritative answer that is both rigorous and visionary.
          Final output must be structured as: [Sifted Truth] $\rightarrow$ [Integrated Synthesis] $\rightarrow$ [Final Verdict].\"

### Step 3: Wire into Oracle
Modify `src/omega/oracle/oracle.py`:
- Update the routing logic to check if a task requires `Lattice Dispatch`.
- If `Triad` mode is selected, delegate the execution to `Orchestrator.dispatch_triad(...)` instead of a single `_summon()`.

### Step 4: Verification
1. **Topology Trigger Test**:
    - Query "Review this architecture" $\rightarrow$ Verify `Triad Spawning` is triggered.
    - Query "What is the time?" $\rightarrow$ Verify `Linear Chaining` (single agent) is used.
2. **Diversity Audit**:
    - For a Triad task, inspect the intermediate logs.
    - Verify that the "Skeptic/Friction" agent provided conflicting/critical feedback compared to the "Anchor" agent.
3. **Synthesis Quality**:
    - Verify that the final response integrates the critiques of the Friction agent and the improvements of the Catalyst agent.
