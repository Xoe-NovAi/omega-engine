# 📂 Cline Integration – Jem Custom Mode

## Purpose
Provide the Cline VS Code extension with the information it needs to load the **Jem Custom Mode** plugin and to use **DeepSeek V4 Flash** as the default inference backend for Jem‑mode sessions within the **MaKaLi governance hierarchy** (Kali→Ma'at→Lilith) and the **Dynamic Inference Protocol** (`docs/gnosis/Omega_Architectural_Sync.md`).

## MaKaLi Context
- Jem is a **research persona under the Light Oversoul (Ma'at)** — all output must be ethically sourced, citation‑verified, and fact‑checked.
- When the user passes the `--transgressive` flag, the Dark Oversoul (Lilith) governs the session instead, allowing unconstrained exploration.
- **Grand Oversoul (Kali)** provides the final synthesis pass for multi‑source research results.

## Dynamic Inference Protocol (DIP) for Cline
- **No hardcoded temperature or context_window** in `config/entities.yaml`. All values are **deleted**.
- Cline must use the `TriageRouter` in `src/omega/oracle/triage_router.py` for dynamic scaling:
  - `fast` tasks → temperature 0.3
  - `standard` → temperature 0.7
  - `deep` → temperature 0.5 (with possible creative offset for Dream/Art domains)
- Context window follows **model‑native limits** – do not clamp YAML constraints.

## Steps for Cline Developers
1. **Plugin Discovery**
   - Cline reads the `plugin_origins` array from `opencode.json`.
   - Ensure the extension includes the path `./plugins/jem_mode` in its plugin loader.
   - The loader should watch for the `/mode jem` command and, when received, activate the plugin.

2. **Backend Selection**
   - When Jem mode is active, Cline should prioritize the **kilo** provider entry that lists `kilo/deepseek/deepseek-v4-flash:free` (see `config/providers.yaml`).
   - If the DeepSeek V4 Flash server is not running locally, fall back to the **google** provider (Gemma 4‑31B) – this mirrors the existing priority chain.

3. **Compaction Settings**
   - Jem mode expects longer context windows. The OpenCode `compaction` settings already preserve 40 k recent tokens; Cline should **disable aggressive pruning** for Jem sessions (set `preserve_recent_tokens` to at least `80000` if the user opts‑in).

4. **Testing**
   - Open a terminal in VS Code, run `opencode start`.
   - In the OpenCode REPL, type `/mode jem`.
   - Ask a research‑heavy question, e.g.:
     ```text
     What are the latest free‑tier LLMs that support tool‑calling and have >1M context?
     ```
   - Verify:
     * The system prompt includes the Jem persona line.
     * The response cites the source (e.g. `> Source: exa (2026‑05‑18T12:34:56Z)`).
     * The model used is `deepseek-v4-flash` (check the trace header).

5. **Deployment**
   - Bundle the `plugins/jem_mode` directory with the Cline extension release.
   - Update the extension’s `README.md` with a **Jem Mode** section linking to this doc.

---
*Prepared by the Overseer – consolidating Jem’s research persona for seamless hand‑off to Cline and DeepSeek V4 Flash.*