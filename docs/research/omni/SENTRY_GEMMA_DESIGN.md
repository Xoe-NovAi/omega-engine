# 🔱 Sentry-Gemma: Always-On Background Agent Design

**Part of the OmniHub Research Hub**
**AP Token**: `AP-SENTRY-V0.1.0`
**Status**: Implementation Spec

---

## Architecture

The Sentry-Gemma agent provides a low-latency, low-footprint "first contact" layer for the Omega Engine.

### Specifications
- **Model**: Gemma 3 270M (or Gemma 4 equivalent lightweight version)
- **Quantization**: 4-bit GGUF
- **RAM Budget**: $\approx 410\text{ MB}$ total
- **CPU Pinning**: Logical cores 14-15 (preventing interference with main Oracle)
- **Deployment**: Rootless Podman container managed by `systemd`

### Logic Flow
1. **Passive Listen**: Monitor audio/text stream for activation phrases ("Hey Omega").
2. **Triage**: Use a small intent-classifier to determine if the request is "Trivial" (handle locally) or "Complex" (escalate).
3. **Escalation**: Forward the request to `Oracle.talk()` via a local Unix socket.
4. **Response**: Deliver the response back to the user through the same channel.

### Integration with WADs
The Sentry-Gemma agent's activation phrases and basic persona are defined in the `_omega_default` WAD, allowing users to change the "Sentry" persona by updating their default WAD.
