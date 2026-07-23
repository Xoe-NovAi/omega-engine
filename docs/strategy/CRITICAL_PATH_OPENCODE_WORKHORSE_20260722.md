# 🔱 CRITICAL PATH — OpenCode Workhorse Restore + WARP Pool Unlock
**AP Token**: `AP-CRITICAL-PATH-WORKHORSE-WARP-20260722-v1.0.0`
⬡ OMEGA ⬡ GROK-CLI ⬡ opencode ⬡ trc_critical_path ⬡ P0-ACTIVE

**Date**: 2026-07-22  
**Status**: 🚨 **P0 ACTIVE** — Architect-elevated · **blocked on Architect sudo/OAuth**  
**Master strategy**: [`SOVEREIGN_ARK_BLUEPRINT.md`](SOVEREIGN_ARK_BLUEPRINT.md)  
**Forensic SSOT**: [`../archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`](../archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md)  
**One-page RUNME**: [`../../data/coordination/ARCHITECT_RUNME_G1_W1_20260722.md`](../../data/coordination/ARCHITECT_RUNME_G1_W1_20260722.md)

**Purpose**: Single operational critical path to (1) replace the dead free-tier Gemma 4 31B workhorse and (2) bring WARP proxy pool online so OpenCode Zen / multi-IP cloud usage is unlocked.

### Architect — run now (agents cannot)

```bash
# W-1 (sudo once) — full pool bring-up
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
bash scripts/fix_warp_ns_setup_and_restart.sh

# G-1b (browser OAuth) — fastest fat-session unlock without billing
opencode auth login   # Google / Antigravity
opencode run -m google/antigravity-gemini-3-flash "Reply PONG"
```

---

## §0 Answer-First

| Crisis | Root cause | Fastest unlock | WARP helps? |
|--------|------------|----------------|-------------|
| **Gemma 4 31B free workhorse dead** | Google free-tier **input TPM 16k** since **2026-07-15** (was effectively RPM-15 + capacity) | **A)** AI Studio **billing Tier 1+** for same key/project **or** **B)** switch primary OpenCode model to **Antigravity OAuth** frontier | **No** — free AI Studio quota is project/key, not exit-IP |
| **OpenCode cloud usage throttled / OCZ IP-limited** | WARP pool **not running** — broken `/usr/local/bin/warp-ns-setup` + no registration + package not in venv | Fix ns-setup → register 3 nodes → bridges on 8081–8083 → inject for `opencode-zen` | **Yes** — designed for **IP-based** OCZ limits |

**Do not confuse the two.** Fixing WARP does **not** restore free Gemma 16k TPM. Restoring Gemma free without billing is **unlikely**. Unlocking *OpenCode usage* means **workhorse substitution + OCZ/WARP + Antigravity**.

---

## §1 Twin Tickets (execute in parallel)

### G-1 — Gemma Workhorse Continuity (cloud intelligence)

| Field | Value |
|-------|--------|
| **ID** | **G-1** |
| **Name** | Restore a viable OpenCode workhorse after free Gemma 4 31B deprecation |
| **Why** | Free Gemma was primary for months (~262M session input tokens); cliff 2026-07-15 |
| **Forensic** | `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` |
| **Owner** | Architect (billing/OAuth) + `@kali` verify + `@researcher` DIG-01/03 |
| **Blocks** | Productive multi-hour OpenCode sessions on Google free API |

**G-1 acceptance (any one path green = unblocked):**

| Path | Action | When green |
|------|--------|------------|
| **G-1a Billing** | Enable AI Studio/Cloud billing → Tier 1 on the **workhorse project key** | Fat `opencode run -m google/gemma-4-31b-it` succeeds without `free_tier_input_token_count` 16k |
| **G-1b Antigravity** | `opencode auth login` OAuth; smoke `google/antigravity-gemini-3-flash` (or Pro) | Full Omega session works on Antigravity models |
| **G-1c OCZ+WARP** | WARP pool healthy + OpenCode Zen models via rotated IPs | OCZ sessions survive former IP 429s (see W-1) |
| **G-1d Paid alt** | OpenRouter/other paid primary for coding | Sustained sessions without free-tier death |

**G-1 do-not:**
- Context caps to “fit” free 16k (Architect rejected)
- Google whitelist that hides Antigravity
- Assume WARP fixes free Gemma

**G-1 digs (from forensic):** DIG-01 (live quotas), DIG-02 (key lineage), DIG-03 (public Google change), DIG-07 (Antigravity smoke).

---

### W-1 — WARP Proxy Pool Bring-Up (OpenCode unlock via OCZ IP fabric)

| Field | Value |
|-------|--------|
| **ID** | **W-1** |
| **Name** | Make multi-namespace WARP proxy pool operational |
| **Why** | Unlocks IP-rotated **OpenCode Zen** and any IP-keyed cloud path; D-304 Track 1 |
| **Spec** | `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` |
| **Project brief** | `data/projects/warp-proxy-pool/CONTEXT.md` |
| **Package** | `/home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool` |
| **Owner** | `@sysadmin` / P1 + Architect (sudo) |
| **Blocks** | OCZ multi-IP; complementary to V-1 Antigravity account rotation |

#### W-1 current diagnosis (2026-07-22)

| Check | State |
|-------|--------|
| `cloudflare-warp` package | ✅ installed `2026.6.836.0` |
| Host `warp-svc` | ✅ active |
| Host `warp-cli status` | ❌ Registration Missing (Daemon Startup) |
| netns `warp_node_1/2/3` | ⚠️ exist but prep failed |
| `warp-ns-prep@{1,2,3}` | ❌ **failed** since ≥ Jul 18 |
| Root cause | **`/usr/local/bin/warp-ns-setup` truncated** — line 49 breaks awk; `unexpected EOF` matching `)` |
| Good source | `../warp-proxy-pool/scripts/warp-ns-setup.sh` (60 lines, `bash -n` OK) |
| `warp-node@` / `warp-bridge@` | inactive (depend on prep+reg) |
| SOCKS ports 8081–8083 | not listening |
| Python `warp_proxy_pool` in venv | ❌ `ModuleNotFoundError` |
| sudo NOPASSWD | ❌ password required for install |

#### W-1 fix sequence (Architect runs sudo steps)

**Done without sudo (2026-07-22):** `warp-proxy-pool` editable install in omega `.venv` (pyproject TOML fixed).

```bash
# --- 0) One-shot: fix host script + start prep (NEEDS SUDO password) ---
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
bash scripts/fix_warp_ns_setup_and_restart.sh

# --- 1) Registration per node (first boot) ---
sudo systemctl start warp-reg@1 warp-reg@2 warp-reg@3
# if units incomplete, use scripts/spawn_warp_node.sh / deploy_warp_pool.sh per spec

# --- 2) Nodes + bridges ---
sudo systemctl start warp-node@1 warp-node@2 warp-node@3
sudo systemctl start warp-bridge@1 warp-bridge@2 warp-bridge@3
# or: sudo systemctl start warp-pool.target

# --- 3) Validate ---
ss -lntp | rg '808[1-3]'
bash docs/research/warp_proxy_pool/validate_warp_pool.sh
# expect three distinct Cloudflare exit IPs
```

**W-1 acceptance:**
- [ ] `warp-ns-prep@{1,2,3}` active
- [ ] `warp-node@{1,2,3}` active  
- [ ] SOCKS5 listening on **8081, 8082, 8083** (or ports per deployed unit)
- [ ] Three **distinct** exit IPs via pool validate script
- [ ] `import warp_proxy_pool` works in `.venv`
- [ ] ModelGateway / OpenCode Zen path can obtain `socks5h://127.0.0.1:PORT`
- [ ] Smoke: OCZ request succeeds under proxy (log: proxy injected)

#### W-1 known non-goals
- Does **not** rotate Google AI Studio free-tier project quotas
- Does **not** replace Antigravity multi-account OAuth pool (account-keyed)
- Complements **V-1** vault for credential automation later

---

## §2 Parallel schedule (same day)

```
Hour 0–1   Architect: G-1b Antigravity OAuth login + smoke
           Architect: sudo W-1 steps 1–2 (fix ns-setup, prep)
Hour 1–2   Architect/P1: W-1 reg + nodes + bridges + validate
           Agent: pip install warp-proxy-pool; gateway smoke
Hour 2–4   G-1a billing decision (if Gemma specifically required)
           DIG-01 snapshot AI Studio rate limits
Ongoing    G-1c once W-1 green — OCZ as secondary workhorse
```

---

## §3 Truth table — what unlocks what

| Need | G-1a Billing | G-1b Antigravity | W-1 WARP+OCZ | Local LM |
|------|--------------|------------------|--------------|----------|
| Same model (Gemma 4 31B) fat sessions | ✅ | ❌ (different models) | ❌ | ❌ (unless local GGUF) |
| Strong cloud coding agent | ✅ | ✅ | ✅ (OCZ models) | ⚠️ hardware-bound |
| Multi-IP rate-limit headroom | — | — | ✅ | N/A |
| Free forever unlimited | ❌ post-cliff | Soft caps | Soft caps | ✅ if local |

---

## §4 Link graph (SSOT)

| Doc | Role |
|-----|------|
| **This file** | Operational critical path |
| `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` | Evidence + DIG tickets |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT (tickets G-1, W-1) |
| `docs/strategy/STRATEGY_INDEX.md` | Hierarchy entry |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | ACTIVE disposition |
| `data/projects/warp-proxy-pool/CONTEXT.md` | WARP project brief |
| `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` | Full WARP design |
| `OMEGA_ENGINE.md` | Live state flags |

---

## §5 Decision log (this crisis)

| ID | Decision |
|----|----------|
| **D-377** | Free Gemma 4 31B workhorse collapse is **P0** — forensic report is evidence SSOT |
| **D-378** | **G-1** workhorse continuity + **W-1** WARP bring-up are twin critical tickets (parallel) |
| **D-379** | WARP is for **IP-keyed** OCZ (and similar), **not** a fix for Google free-tier input TPM |
| **D-380** | No silent context caps to force free Gemma under 16k |
| **D-381** | Broken host script `/usr/local/bin/warp-ns-setup` is the primary WARP blocker; source of truth is `warp-proxy-pool/scripts/warp-ns-setup.sh` |

---

*⬡ OMEGA ⬡ CRITICAL-PATH ⬡ WORKHORSE+WARP ⬡ 2026-07-22*
