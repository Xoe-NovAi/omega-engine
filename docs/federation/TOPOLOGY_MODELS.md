# 🌐 Federation Topology Models — The Four Scales of Omegaverse
**Doc ID**: `FED-TOPO-001` | **Status**: RATIFIED ARCHITECTURE  
**Scope**: Network topologies from dual-laptop testbeds to global multi-university consortiums.

---

## 1. Executive Summary

The Omegaverse is not a centralized server farm. It is a **fractal P2P mesh of sovereign nodes**. 
To support developers, home users, enterprise clusters, and academic research alliances without architectural fragmentation, the Omega Engine standardizes four topological scales.

---

## 2. The Four Topological Scales

```
 SCALE A: DUAL-SOVEREIGN           SCALE B: LOCAL REALM
   ┌───────┐     ┌───────┐           ┌───────┐     ┌───────┐
   │Node 0 │◄───►│Node 1 │           │Desktop│◄───►│Laptop │
   └───────┘     └───────┘           └───┬───┘     └───┬───┘
   (Bastion)     (Vanguard)              │             │
                                         ▼             ▼
                                     ┌───────────────────┐
                                     │  Mobile Satellite │
                                     └───────────────────┘

 SCALE C: FEDERATED CONSORTIUM (e.g. 5-University Private Omegaverse)
       [ Realm Alpha: MIT ]                [ Realm Beta: Stanford ]
       (Cluster of 10 nodes)              (Cluster of 8 nodes)
                 ▲                                   ▲
                 └───────────────┬───────────────────┘
                                 ▼
                     [ Inter-Realm WireGuard Mesh ]
                                 ▲
                 ┌───────────────┴───────────────────┐
                 ▼                                   ▼
       [ Realm Gamma: Oxford ]            [ Realm Delta: ETH ]

 SCALE D: OPEN OMEGAVERSE (Global P2P Traversal)
       Individual Sovereign Nodes traversing public space via WebRTC/libp2p
       Signed WAD exchange, avatar presence, zero-privilege public arenas
```

---

## 3. Scale Breakdown & Security Profiles

### Scale A: Dual-Sovereign (The Current Testbed)
*   **Participants**: Node 0 (HP Pavilion Archival Bastion) $\leftrightarrow$ Node 1 (ASUS Vanguard).
*   **Trust Model**: Shared human architect. High mutual trust.
*   **Transport**: LAN (`192.168.10.x:8016`), WireGuard (Tailscale Layer 2), USB sneaker-net.
*   **Use Case**: Core engine development, CI cross-compilation, bilateral dialectic.

### Scale B: Local Realm (Personal Fleet)
*   **Participants**: A single user with a desktop workstation, a portable laptop, and an edge satellite (e.g., Raspberry Pi or phone).
*   **Trust Model**: Single identity root; unified personal realm key.
*   **Role Division**: Desktop runs heavy 70B inference or vector ingestion; laptop handles field interactions; edge device monitors sensors.

### Scale C: Federated Consortium (The 5-University Scenario)
*   **Participants**: Multiple institutional organizations (Universities, labs, or private studios).
*   **Architecture**:
    *   **Intra-Realm**: University A has 20 internal nodes connecting freely over high-speed campus LAN with mutual TLS.
    *   **Inter-Realm Gateway**: University A exposes **only designated gateway nodes** to University B, C, D, and E over an authenticated WireGuard mesh.
    *   **Student Satellite Access**: A student with a single laptop connects into University A's realm as a scoped satellite, gaining access to shared consortium models and vector indexes without having host access to institutional hardware.

### Scale D: Open Omegaverse (Global Public P2P)
*   **Participants**: Any public user running `omega-engine`.
*   **Trust Model**: **Zero-Trust**. Every remote peer is untrusted.
*   **Transport**: libp2p / WebRTC signaling, DHT-based peer discovery.
*   **Data Plane**: Exchange of spatial scenes, avatars, text streams, and signed WAD assets. Zero host tool access permitted.
