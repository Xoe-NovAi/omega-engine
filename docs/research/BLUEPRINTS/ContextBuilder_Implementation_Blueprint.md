# 🔱 Implementation Blueprint: ContextBuilder Wiring

**Goal**: Integrate `ContextBuilder` and `MemoryStore` into the `Oracle` to enable persistent multi-turn conversations.

**Target Files**:
- `src/omega/oracle/constants.py` (New)
- `src/omega/memory_store.py`
- `src/omega/oracle/session_manager.py` (New)
- `src/omega/oracle/oracle.py`
- `tests/conftest.py` (New)
- `tests/test_memory_store.py` (New)
- `tests/test_context_builder.py` (New)
- `tests/test_oracle.py`

**Step-by-Step Instructions**:

### Step 1: Establish Shared Constants
Create `src/omega/oracle/constants.py` to de-duplicate context limits.
- Define `DEFAULT_CONTEXT_LIMIT = 6`
- Define `MAX_HISTORY_EXCHANGES = 20`
- Update `memory_store.py` and `context_builder.py` to import these.

### Step 2: Harden MemoryStore Infrastructure
Modify `src/omega/memory_store.py`:
- **Path Standardization**: Update `DATA_DIR` to use a relative path from the file location: `Path(__file__).resolve().parent.parent.parent.parent / "data"`.
- **Test Guard**: Wrap the `mkdir` loop for memory directories in an `if os.environ.get("OMEGA_ENV") != "test":` block.
- **Reset Mechanism**: Add `reset_memory_store()` function to reset the `_memory_store` singleton to `None`.

### Step 3: Implement SessionManager
Create `src/omega/oracle/session_manager.py`:
- Implement `SessionManager` class.
- `get_session_id(entity_name)`: 
    - Resolve `entity_slug`.
    - Check `data/sessions/{entity_slug}.active`.
    - If current date matches, increment counter. Otherwise, reset counter to 1.
    - Write updated session metadata to `.active` file.
    - Return `ses_{YYYYMMDD}_{entity_slug}_{counter:03d}`.
- `get_session_id_transient(trace_id)`: Return `trace_id`.

### Step 4: Wire into Oracle Core
Modify `src/omega/oracle/oracle.py`:
- **Dependency Injection**: Update `__init__` to accept `SessionManager` and `ContextBuilder`. Initialize `self.memory_store = get_memory_store()`.
- **Response Dataclass**: Add `session_id: Optional[str] = None` to `OracleResponse`.
- **Method Integration**: In `_summon`, `_route_by_domain`, and `_respond_as_iris`:
    1. Resolve `session_id` using `SessionManager` (or `trace_id` if `transient`).
    2. Call `await self.context_builder.build_context(entity_name, session_id)`.
    3. Use `ContextBuilder.prepend_to_prompt(context_block, entity.personality)` to generate the system prompt.
    4. After receiving the model response, call `await self.memory_store.add_exchange(...)` (skip if `transient`).
- **Forwarding**: Update `talk()` to ensure the `transient` flag is passed to internal methods.

### Step 5: Verification
1. **Unit Tests**: 
    - Implement `tests/conftest.py` with `temp_data_dir` and `mock_memory_store` fixtures.
    - Run `tests/test_memory_store.py` (12 tests).
    - Run `tests/test_context_builder.py` (22 tests).
2. **Integration Tests**:
    - Run `tests/test_oracle.py` (3 new memory integration tests).
3. **Manual Validation**:
    - `omega talk "hello"` $\rightarrow$ Verify `data/sessions/sophia.active` is created.
    - `omega talk "what did I just say?"` $\rightarrow$ Verify response references "hello".
    - `omega talk "test" --transient` $\rightarrow$ Verify no session file is created.
    - Run `make test` and `make lint`.
