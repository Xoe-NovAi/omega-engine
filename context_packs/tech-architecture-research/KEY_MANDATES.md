# Key Sovereign Mandates (M1-M25 Excerpt)

## M1 — AnyIO Absolute
All asynchronous code MUST use AnyIO. Never use `asyncio` directly. Wrap blocking I/O in `anyio.to_thread.run_sync()`.

## M7 — Local-First (Non-Negotiable)
Local inference is PRIMARY. Cloud is FALLBACK. Always. Provider fabric must try local backends before cloud backends.

## M8 — Zero Telemetry
No telemetry. Zero. None. Ever. No analytics, no usage tracking, no phone-home. Local observability OK.

## M13 — Temple-Grade Compliance
All engine code MUST comply with Temple-Grade standards (T1-T11). Run `make temple-grade` after non-trivial changes.

## M23 — Failure Integrity
No "soft-failures" or simulated rigor. If a mandatory tool is missing or broken → `[TOOL-CHAIN-COLLAPSE]` hard stop.

## M24 — Venv Sovereignty
All Python operations MUST run within the project virtual environment. Never `--break-system-packages`.

## M22 — Response Provenance
All observability logs MUST record the actual provider that generated a response, not the configured intent.

## M14 — Heritage Vetting
No id Software concept may be implemented without passing through the Heritage Vetting Pipeline. Every `[id-soft:]` tag must have a vet record.
