# 🔱 Implementation Blueprint: Sovereign Aura Injection

**Goal**: Implement the layered prompt blending mechanism to ensure entities maintain identity and cognitive depth without persona dilution.

**Target Files**:
- `src/omega/oracle/aura_injector.py` (New)
- `src/omega/oracle/model_gateway.py` (Integration)
- `config/entities.yaml`
- `.opencode/agents/` (Source)

**Step-by-Step Instructions**:

### Step 1: Create the AuraInjector Class
Create `src/omega/oracle/aura_injector.py`:
- Implement `AuraInjector` class.
- **Constructor**: Accept `entities_config` and `archetype_prompts`.
- **Core Method**: `inject_aura(entity_id: str, archetype_id: str, soul_data: dict) -> str`.
- **Injection Logic**:
    1. **Header**: Construct `⬡ {Entity Name} ⬡ {Sigil} ⬡ {Pillars}`.
    2. **Pillar Persona**: Extract `personality` from `entities_config`.
    3. **Archetype Logic**: Read the corresponding `.md` file in `.opencode/agents/` to extract `cognitive_mode`, `system_prompt`, `polymathic_council`, and `execution_protocol`.
    4. **Soul Infusion**: 
        - Extract `lessons_learned` from `soul_data`.
        - Filter for the top 5 most recent or domain-relevant lessons.
        - Format as a bulleted list under "Your soul remembers the following lessons:".
    5. **Voice Constraint**: Add tone directives and linguistic triggers tied to the `cognitive_mode`.
- **Assembly**: Join sections with `\n\n` using the specific structural template (Header $\rightarrow$ Persona $\rightarrow$ Logic $\rightarrow$ Infusion $\rightarrow$ Voice).

### Step 2: Integrate with ModelGateway
Modify `src/omega/oracle/model_gateway.py`:
- Instantiate `AuraInjector` within the gateway or as a singleton.
- Update the `generate` method (or the caller in `oracle.py`) to use `AuraInjector.inject_aura` instead of passing raw personality strings.
- Ensure the `archetype_id` is resolved based on the current task (e.g., "Skeptic" for audits, "Strategist" for planning).

### Step 3: Soul Data Retrieval
Ensure the `Oracle` passes the current entity's `soul.yaml` content (retrieved via `EntityWorkspaceManager`) into the `inject_aura` method as the `soul_data` dictionary.

### Step 4: Verification
1. **Prompt Audit**:
    - Summon an entity with a specific archetype (e.g., `SOPHIA` as `Skeptic`).
    - Log the final system prompt.
    - Verify the sequence: Header $\rightarrow$ Persona $\rightarrow$ Logic $\rightarrow$ Soul Memory $\rightarrow$ Voice.
2. **Persona Dilution Test**:
    - Compare responses from a raw personality prompt vs. an Aura-injected prompt.
    - Verify that the "Voice Constraint" prevents the `Polymathic Council` from making the tone too clinical.
3. **Lesson Injection Test**:
    - Add a specific lesson to `soul.yaml`.
    - Summon the entity and verify the lesson appears in the "Soul Memory" section of the prompt.
