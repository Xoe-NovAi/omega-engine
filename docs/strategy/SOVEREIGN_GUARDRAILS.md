# 🔱 The Sovereign Guardrails (The Steel Script v3)
**AP Token**: `AP-GUARDRAILS-v3.0.0`
⬡ OMEGA ⬡ OVERSEER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_overseer ⬡ GUARDRAILS

These rules are absolute. Any implementation that violates these guardrails is to be vetoed and refactored immediately.

## 🛡️ Rule 1: The AnyIO Absolute
**"If it touches the disk or the network, it must be Awaited."**
- No `pathlib` synchronous methods (`exists`, `read_text`, `write_text`, `mkdir`) in the runtime path.
- No `open()`, `os.mkdir()`, `os.replace()`, `os.remove()`.
- No `subprocess.run()` or `subprocess.Popen()` unless wrapped in `anyio.to_thread.run_sync`.
- No `time.sleep()`.

## 🛡️ Rule 2: The Engine-Stack Firewall
**"The Engine is the Fire; the WAD is the Tool."**
- The Engine core (`src/omega/`) must remain **Mythology-Agnostic**.
- No hardcoded entity names (except `Iris` as the default messenger).
- All domain-specific logic must be loaded dynamically from a WAD manifest.
- If a feature only serves a specific stack (e.g., Arcana-NovAi), it does not belong in the Engine.

## 🛡️ Rule 3: The zRAM Buffer Rule
**"Use the reserve for spikes, not for residency."**
- The 14GB-18GB "Yellow Zone" is for graceful degradation and temporary spikes.
- Permanent model residency must stay within the 14GB physical limit to avoid CPU thrashing during zRAM compression.

## 🛡️ Rule 4: The Sequentiality Mandate
**"One weight-set at a time."**
- All multi-model reasoning (Lattice/Council) must be implemented as a sequential pipeline.
- Parallel local inference is prohibited to prevent OOM and CPU starvation.

## 🛡️ Rule 5: The Iris Constant
**"Iris is the Anchor."**
- The always-on assistant is **Iris**.
- No changes may be proposed that require shutting down the Iris container.
