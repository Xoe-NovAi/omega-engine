# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Single source of truth for the MCP protocol version spoken by the Hub.

AP: AP-MCP-PROTOCOL-VERSION-v1.0.0
M2  Firewall — Hub-side constant; imports nothing from Core (src/omega)
M23 Failure Integrity — pure constants, no I/O, import-safe, no network

Why this module exists
----------------------
``mcp_client.py`` and ``hub_tools/federation.py`` both need to name the MCP
protocol version the Hub speaks. They previously carried independent copies:
the client documented 2026-07-28 in its docstrings while the federation probe
still POSTed ``"protocolVersion":"2024-11-05"`` at ``initialize``. A live health
probe asserting a two-year-old protocol string is precisely the M29 failure
class — the probe reported PASS because the endpoint answered HTTP 200, not
because the version was correct. Two copies of a protocol constant will drift;
one copy cannot.

SEP-2575 (MCP 2026-07-28) removed the ``initialize``/``initialized`` handshake
entirely and moved protocol identity into the ``_meta`` envelope. That
reshapes *where* a version may legally appear:

``_meta.protocolVersion``
    The SEP-2575 carrier. The Hub declares its identity here. Verified
    tolerated by the installed SDK: a probe sending ``_meta`` with this value
    returns HTTP 200 and a full tool list.

``MCP-Protocol-Version`` header (SEP-2243)
    Optional transport metadata. **Deliberately not sent with this value.**
    The installed ``mcp`` SDK (1.30.0) advertises exactly
    ``["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"]`` and answers
    a 2026-07-28 header with HTTP 400 / JSON-RPC ``-32600``. Asserting an
    unsupported version in the header is strictly worse than omitting it, so
    the Hub declares identity in ``_meta`` and leaves the transport header
    off rather than shipping a version claim the peer will reject.

See ``tests/mcp/test_hub_protocol_version.py`` for the regression guard that
keeps the literal out of every other file in this package.
"""

# The Hub's declared MCP protocol identity, carried in the SEP-2575 _meta
# envelope. Keep this the ONLY place in mcp_servers/omega_hub/ where a
# protocol version string is written as a literal.
PROTOCOL_VERSION = "2026-07-28"

# The Hub does not assert a protocol version in the SEP-2243 transport header.
# A peer running the currently installed mcp SDK rejects 2026-07-28 there with
# HTTP 400; omitting the header lets the peer advertise its own version and
# keeps the federation probe from manufacturing a version mismatch that the
# peer never claimed. Set to True to assert the header in probes.
SEND_PROTOCOL_VERSION_HEADER = False

__all__ = ["PROTOCOL_VERSION", "SEND_PROTOCOL_VERSION_HEADER"]