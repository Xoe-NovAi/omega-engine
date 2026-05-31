# Skill: blitz-validate

The "Sovereign Heartbeat" validator for the Omega Engine's integration chain.

## Purpose
To ensure that the entire path from ElevenLabs $\rightarrow$ Tunnel $\rightarrow$ Omega-Hub $\rightarrow$ Sovereign Plugin $\rightarrow$ Tool is unbroken before the 2-hour window closes.

## Validation Sequence
1. **Tunnel Check**: `curl -I [PUBLIC_URL]` $\rightarrow$ Must return 200 OK.
2. **Hub Heartbeat**: `curl [PUBLIC_URL]/health` $\rightarrow$ Must return `{"status": "healthy"}`.
3. **Plugin Interception**: Trigger a test tool call via the hub $\rightarrow$ Verify the `Sovereign Plugin` logs a "Boundary Check" event.
4. **End-to-End Response**: Verify the response returns to the caller in < 2 seconds.

## Success Criteria
A "Sovereign-Ready" status is only granted if all four steps pass. If any step fails, the `sovereign-expert` must immediately enter "Emergency Fix" mode.

## Implementation Note
This skill should be used after every single change to the `Sovereign Plugin` or the `omega-hub` configuration.
