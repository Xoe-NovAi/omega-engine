# Skill: blitz-tunnel

A high-speed utility for establishing a secure, public tunnel to the Omega Engine's internal services.

## Purpose
The ElevenLabs Conversational AI platform requires a public HTTPS URL to communicate with the `omega-hub` for tool execution. `blitz-tunnel` automates the process of exposing the local hub to the internet.

## Workflow
1. **Service Identification**: Identify the local port for `omega-hub` (default: 8016).
2. **Tunnel Initiation**: Launch `ngrok` or `Cloudflare Tunnel` (cloudflared).
3. **URL Extraction**: Parse the generated public HTTPS URL.
4. **Config Update**: Provide the URL to the `sovereign-expert` for injection into the ElevenLabs dashboard.

## Command Reference
- `ngrok http 8016`: Quick start tunnel.
- `cloudflared tunnel --url http://localhost:8016`: More stable, long-term tunnel.

## Implementation Note
Ensure the tunnel is launched in a separate terminal or as a background process so it doesn't block the OpenCode CLI.
