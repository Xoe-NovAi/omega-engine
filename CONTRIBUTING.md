# Contributing to Omega Engine Alpha

First: thank you for caring enough to read this. The Omega Engine exists
because a year and a half of "no tool does what I need" turned into "then
build your own." Every contribution that respects the invariants below is
welcome.

## The invariants (non-negotiable)

1. **NO PyTorch. Ever.** CPU-only, memory-bounded on 16GB single-channel.
2. **Absolute anyio async wiring.** Bare `asyncio`/`trio` only inside
   third-party vendored code, never in our scripts. See `docs/CODE_QUALITY.md`.
3. **The P-core pin TRAP.** Never narrow `AllowedCPUs` to physical P-cores
   only (`0,2,4,6,8,10`) — that collapses throughput to ~0.5 t/s.
   Correct: `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8`.
4. **Secrets never hit disk or git.** Use `{env:VAR}` placeholders. If you
   accidentally commit one, rotate it and amend history before merge.
5. **Truth over comfort.** We document shadows (failures, corrections) with the
   same rigor as wins. "I see it in my tool list" is NOT "I've verified it."

## Code-quality gates (pre-merge)

```bash
make lint-async          # rejects bare asyncio/trio in our scripts
make test                # runs the (growing) test suite
make docs                # validates README links + docs build (mkdocs)
```

## Contribution flow

1. Fork / branch from `main`.
2. One atomic change per branch; semantic commit message.
3. Run the gates locally.
4. Open a PR. Template covers: What / Why / Verification / Shadows.

## Commit message style

Concise subject, body explains the *why*:

```
docs: add GETTING_STARTED for first-run users

README links to the guide; keeps docs discoverable for new contributors.
Verified all anchor targets exist.
```

## Code-review checklist

- [ ] anyio-only async (no bare asyncio/trio)
- [ ] No torch imports / deps
- [ ] CPU pinning not regressed (HARDWARE.md consulted)
- [ ] Secrets stay `{env:...}`
- [ ] New behavior verified on real hardware, not assumed
- [ ] Session log / spec updated for behavioral changes
- [ ] `</dev/null` + hard timeout on any subprocess/network call

## Where to start

| Interest | Entry point |
|----------|-------------|
| Harness scripts | `scripts/`, `Makefile` |
| Documentation | `docs/*.md` (check README links) |
| Spatial knowledge | `~/WanderGround/` (separate repo) |
| Plugin dev | `docs/PLUGIN_DEVELOPMENT.md` + `~/.config/opencode/plugins/gnosis-leash.js` |
| Federation | `docs/omega-hub-exposure.md`, `docs/WANDERGROUND_SPEC.md` |

## Code of conduct

Be excellent. We build sovereign AI with curiosity and reverence for the
people who made the pieces — cite your sources, credit your borrowings,
speak truth in the temple.