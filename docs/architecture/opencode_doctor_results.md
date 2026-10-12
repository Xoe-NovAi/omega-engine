arcana-novai@Arcana-NovAi:~/Documents/Xoe-NovAi/omega-engine$ ./opencode_provider_doctor.sh --apply
=== opencode provider doctor — 2026-09-18T20:33:48Z ===
home=/home/arcana-novai project=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine apply=1
opencode: 1.18.23
[WARN] opencode < 1.18.30: OpenAI provider SDK compatibility fixes landed in .30 — consider 'opencode upgrade' for parity (not a diagnosis)
--- layers ---
present: /home/arcana-novai/.config/opencode/opencode.json
absent:  /home/arcana-novai/.config/opencode/opencode.jsonc
absent:  /nonexistent-openconfig
present: /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json
absent:  /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.jsonc
project plugins: awareness.ts error-capture.ts silent-stall-sensor.ts test-event.js.DISABLED test-event.js.DISABLED.license 
[WARN] project plugins load — a provider-hooking plugin (e.g. *-auth) can rewrite requests
[WARN] /home/arcana-novai/.config/opencode/opencode.json provider.google-standard enumerates 4 model(s): gemini-2.5-pro, gemini-2.5-flash, gemma-4-31b-it, gemma-4-26b-a4b-it — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
[PASS] /home/arcana-novai/.config/opencode/opencode.json ollama.baseURL resolves: 127.0.0.1
[WARN] /home/arcana-novai/.config/opencode/opencode.json provider.ollama enumerates 1 model(s): qwen3:4b — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
[WARN] /home/arcana-novai/.config/opencode/opencode.json provider.opencode enumerates 1 model(s): x-preview-f-free — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
[PASS] /home/arcana-novai/.config/opencode/opencode.json native-gguf-extractor.baseURL resolves: 127.0.0.1
[WARN] /home/arcana-novai/.config/opencode/opencode.json provider.native-gguf-extractor enumerates 1 model(s): qwen3-1.7b-extractor — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
[PASS] /home/arcana-novai/.config/opencode/opencode.json native-gguf-reasoner.baseURL resolves: 127.0.0.1
[WARN] /home/arcana-novai/.config/opencode/opencode.json provider.native-gguf-reasoner enumerates 1 model(s): qwen3-4b-thinking — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
[PASS] /home/arcana-novai/.config/opencode/opencode.json lmstudio.baseURL resolves: localhost
[WARN] /home/arcana-novai/.config/opencode/opencode.json provider.lmstudio enumerates 2 model(s): qwen3-1.7b-q6_k, qwen3-4b-thinking — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
[PASS] /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json lmstudio.baseURL resolves: localhost
[WARN] /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json provider.lmstudio enumerates 6 model(s): qwen3-4b-thinking, qwen3-1.7b, qwen3-1.7b-q6_k, phi-4-mini, krikri-8b, deepseek-r1-qwen3-8b — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
[WARN] /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json provider.opencode enumerates 3 model(s): nemotron-3-ultra-free, mimo-v2.5-free, big-pickle — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)
--- registry drift (custom limits vs live models.dev) ---
[WARN] google-standard/gemini-2.5-pro: absent from live registry (removed upstream?)
[WARN] google-standard/gemini-2.5-flash: absent from live registry (removed upstream?)
[WARN] google-standard/gemma-4-31b-it: absent from live registry (removed upstream?)
[WARN] google-standard/gemma-4-26b-a4b-it: absent from live registry (removed upstream?)
[WARN] ollama/qwen3:4b: absent from live registry (removed upstream?)
[WARN] native-gguf-extractor/qwen3-1.7b-extractor: absent from live registry (removed upstream?)
[WARN] native-gguf-reasoner/qwen3-4b-thinking: absent from live registry (removed upstream?)
[WARN] lmstudio/qwen3-1.7b-q6_k: absent from live registry (removed upstream?)
[WARN] lmstudio/qwen3-4b-thinking: absent from live registry (removed upstream?)
[WARN] lmstudio/qwen3-1.7b: absent from live registry (removed upstream?)
[WARN] lmstudio/phi-4-mini: absent from live registry (removed upstream?)
[WARN] lmstudio/krikri-8b: absent from live registry (removed upstream?)
[WARN] lmstudio/deepseek-r1-qwen3-8b: absent from live registry (removed upstream?)
[WARN] opencode/big-pickle: custom {"context": 1000000, "input": 950000, "output": 64000} != registry {"context": 200000, "input": 160000, "output": 32000} (Zen moved — drop or re-justify the override)
[WARN] drift: 1/3 custom limits disagree with registry
--- auth ---
auth providers (names only): google, openrouter, github-copilot, siliconflow, aihubmix, cerebras, nebius

┌  Credentials ~/.local/share/opencode/auth.json
│
●  Google api
│
●  OpenRouter api
│
●  GitHub Copilot oauth
--- env (names only, values never shown) ---
XDG_CONFIG_DIRS=<set>
XDG_MENU_PREFIX=<set>
XDG_SESSION_DESKTOP=<set>
XDG_SESSION_TYPE=<set>
XDG_CURRENT_DESKTOP=<set>
XDG_SESSION_CLASS=<set>
XDG_RUNTIME_DIR=<set>
XDG_DATA_DIRS=<set>
OPENCODE_DISABLE_AUTOUPDATE=<set>
OPENCODE_API_KEY=<set>
env API keys present: 8 (values never shown)
=== 5 pass, 25 warnings, 0 failures ===
Guidance: fix FAILs first; WARNs are hygiene/rot-risk. After ANY config change: quit TUI fully + fresh shell, then 'opencode models' to verify.
arcana-novai@Arcana-NovAi:~/Documents/Xoe-NovAi/omega-engine$ ./opencode_provider_doctor.sh --diagnose
unknown arg: --diagnose

