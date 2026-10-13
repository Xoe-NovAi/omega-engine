# Exchange Duplex Deployment — Node 1

**Owner:** doom_guy (S1 Infrastructure) · **Executor:** Lilith-N1 (has N1 shell access)
**Origin:** `scripts/omega_exchange_server.py` @ `2aa3a7f7` — **one** implementation, no forks
**Law:** `https://n1.tail51f14a.ts.net:805/<path>` — **HTTPS ONLY**
**Date:** 2026-10-01

---

## 0. STATUS — READ THIS FIRST

**This is a HANDOFF PACKAGE. It has NOT been executed on Node 1.**

S1 (doom_guy) runs on Node 0 and has **no shell on Node 1**. Every command below
is written to be pasted verbatim by whoever does have N1 access. Nothing in this
document reports N1 output. Where this document shows output, it is **N0's real
output**, produced on 2026-10-01, and labelled as such.

### 0.1 The blocker, stated before the steps

> **Deploying on 805 — the port the Architect ruled — cannot work today.**
> Measured from N0 on 2026-10-01: `n0→n1:805` is **DENIED** by the tailnet
> packet filter. `n0→n1:8019` is **PERMITTED**. The gap is not a missing
> direction; it is a **port**. Evidence and method in §1.

The 805 deploy is still correct as written and the Architect still owns the ACL
change. But it must be understood as **blocked pending that ACL grant**, not as
a deploy that will start working when the unit starts. If the ACL is not
changed, the symptom is a **silent timeout with no error anywhere** — the worst
possible failure mode, because it looks like a slow network rather than a
policy denial. `scripts/exchange_verify_duplex.sh` was run against the live
`n1:805` and produced exactly that diagnosis (§7.3).

**Two ways forward. This is an Architect decision, not an S1 one:**

| Option | What it needs | What it costs |
|---|---|---|
| **A — keep 805** (Architect ruling, Lilith's proposal) | Architect adds an `n0→n1` grant on `tcp:805` | One ACL edit. Zero infra change. Port namespaces stay unambiguous. |
| **B — serve 8019 on N1** | **Nothing.** Works with today's ACL. | N1 also answers on 8019, so the port no longer identifies the node. You must read the manifest `root` field. |

Option B is one command away (`scripts/deploy/n1/omega-exchange.service.d/10-port-8019.conf`)
and requires no Tailnet change. It is documented, not recommended — Lilith's
namespace argument in §10 is correct, and the ACL is the only thing forcing
this trade. **The Architect picks. S1 does not silently resolve it.**

---

## 1. THE ACL REALITY (evidence, not assumption)

### 1.1 Method

No shell on N1, and the ACL itself is server-side (Tailnet console), so the
filter was measured **behaviourally**: probe each port from N0 and classify the
failure. Tailscale's packet filter **silently drops** non-permitted traffic, so
the failure mode distinguishes "denied" from "nothing listening".

| Outcome | Meaning |
|---|---|
| `Connection refused` (fast, RST) | The filter **allowed** the packet. The host answered. Nothing is listening. |
| `Connection timed out` (hangs to the deadline) | The filter **dropped** the packet. It never reached N1. |
| `SSH` / TLS banner | Something is listening. |

### 1.2 Measurement — N0, real output, 2026-10-01

Context first, so the numbers are interpretable:

```
$ tailscale status
100.123.51.67  n0  n0.tail51f14a.ts.net  linux  -
100.89.40.17   n1  tagged-devices        linux  active; direct 192.168.10.174:41641, tx 254152 rx 42480

# Health check:
#     - Tailscale SSH enabled, but access controls don't allow anyone to access
#       this device. Ask your admin to update your tailnet's ACLs to allow access.
```

Note `direct 192.168.10.174:41641` — **same physical LAN, WireGuard direct, no
relay.** A same-LAN RTT is single-digit milliseconds, which is what makes the
refusal below meaningful rather than a middlebox artifact.

```
$ tailscale status --json | jq '.Peer[].DNSName, .Peer[].Tags'
n1.tail51f14a.ts.net.
["tag:node1"]
```

Port matrix, N0 → N1 (`timeout 5 bash -c 'cat </dev/null >/dev/tcp/100.89.40.17/PORT'`):

```
port   22: TIMEOUT  (rc=124) -> packet DROPPED (filter)
port   80: TIMEOUT  (rc=124) -> packet DROPPED (filter)
port  443: TIMEOUT  (rc=124) -> packet DROPPED (filter)
port  805: TIMEOUT  (rc=124) -> packet DROPPED (filter)
port 8019: REFUSED  (rc=1)   -> reached host, no listener
port 8020: TIMEOUT  (rc=124) -> packet DROPPED (filter)
port 9999: TIMEOUT  (rc=124) -> packet DROPPED (filter)
```

Confirmed by `curl`, and stable across two rounds:

```
$ curl -sv http://100.89.40.17:8019/
*   Trying 100.89.40.17:8019...
* connect to 100.89.40.17 port 8019 from 100.123.51.67 port 57562 failed: Connection refused
* Failed to connect to 100.89.40.17 port 8019 after 4 ms: Could not connect to server

$ curl -sv http://100.89.40.17:805/
*   Trying 100.89.40.17:805...
* Connection timed out after 6002 milliseconds
```

**4 ms** for the 8019 refusal is a real host response over the LAN. A dropped
packet cannot produce an RST from the destination. So:

| Direction | Port | Verdict |
|---|---|---|
| n1 → n0 | 8019 | **PERMITTED** (given; working — 88/88 pulls recorded) |
| **n0 → n1** | **8019** | **PERMITTED — already exists. The brief's premise is wrong.** |
| **n0 → n1** | **805** | **DENIED** — the port the ruling selects |
| n0 → n1 | 22/80/443/8020/9999 | DENIED |

### 1.3 What this corrects

The brief stated: *"The REVERSE grant (n0→n1) does NOT exist yet."*
**It does — on 8019.** The existing rule is written in a way that covers both
directions for that port. The consequence is that §1.2 removes the stated
reason for needing an ACL change on 8019, and creates a new one on 805.

This is not a nitpick. Had the unit gone onto 805 and the ACL not been touched,
the deploy would have "succeeded" — the unit starts, binds loopback, answers
`curl http://127.0.0.1:805/` from N1 itself with a healthy manifest — and the
failure would only appear from N0, as a timeout, with the local health check
still green. **A deploy that is green locally and dead remotely is the exact
failure class M29 exists to prevent.** Do not accept a local-only health check
as evidence.

### 1.4 Verifying this yourself (from N1, after deploy)

The same classification, run from the other side. From N1 the permitted
direction is `n1→n0:8019` (known good), and after the ACL change `n1→n1:805`
is loopback so it is not a network test. The meaningful N1-side checks are the
local ones in §6, plus pulling from N0 in §7.2.

---

## 2. PREREQUISITES

On N1, as `xnai`:

- [ ] `tailnet` identity: `tailscale status` shows `n1` / `n1.tail51f14a.ts.net`
- [ ] `systemd --user` running **and lingering** — without linger the unit dies
      at logout and a reboot-surviving service is a fiction:
      `loginctl show-user xnai -p Linger` → must be `Linger=yes`
- [ ] A venv containing **`anyio`, `uvicorn`, `starlette`**. Two candidates
      exist (below). This is **unresolved** — see §3 Step 0.
- [ ] Free space on the NVMe backing `~/omega-exchange` (189 G free per
      Lilith-N1's survey; re-check, do not trust the number)
- [ ] **NOT** touching port 8016. That is a separate local MCP
      (`/home/xnai/mcp_server.py`) and is unrelated to the exchange.

---

## 3. DEPLOYMENT

Every command is run **on N1, as `xnai`**. Nothing here touches N0.

### Step 0 — Resolve the three unknowns (do not guess)

Lilith-N1's survey listed the venvs but **not the omega-engine checkout path on
N1**. The unit needs it. Find it, then confirm the venv actually has the
dependencies:

```bash
# 0a. locate the checkout — the one containing scripts/omega_exchange_server.py's repo
find /home/xnai -maxdepth 5 -type d -name .git 2>/dev/null | sed 's|/.git$||'

# 0b. pick the venv that actually satisfies the imports (authoritative, not guesswork)
for v in /home/xnai/Documents/Projects/omega-engine-alpha/.venv \
         /home/xnai/WanderGround/.venv; do
  printf '%s : ' "$v"
  "$v/bin/python" -c 'import anyio, uvicorn, starlette; print("OK", uvicorn.__version__)' \
    2>&1 | tail -1
done
```

Record the winner as `OMEGA_VENV` and the checkout as `OMEGA_REPO`, then
**edit the unit to match** (`ExecStart`, `ExecStartPre`, `WorkingDirectory`,
`Documentation`). The unit ships with `omega-engine-alpha` as the assumed path
because that venv sits inside an omega-engine checkout; that is an **inference,
not a verified fact**, and it is marked `# VERIFY` in the unit for that reason.

**M23 — if neither venv has the three packages, STOP.** Do not `pip install`
into an arbitrary venv and do not fall back to system python. Report the gap;
it is an M24 (venv sovereignty) decision, not a deploy-time improvisation.

### Step 1 — The publish-root symlink (Architect convention)

**Convention (Architect ruling, resolving Lilith's Q-A):** the served path is
always `~/exchange`, and `~/exchange` is always a **symlink** to whatever the
node's real store is. Never a copy. Never a second tree.

```bash
# N1: link the conventional name at the real store. Do not move the data.
ln -s /home/xnai/omega-exchange /home/xnai/exchange
ls -ld /home/xnai/exchange                      # expect: exchange -> /home/xnai/omega-exchange
readlink -f /home/xnai/exchange                 # expect: /home/xnai/omega-exchange
```

Why a symlink and not a copy — Lilith's argument, which is correct: a copy
forks the tree and creates a second source of truth that can drift. A symlink
cannot drift, because it has no content of its own.

> **N0 cannot follow this convention literally, and does not need to.**
> On N0, `$HOME` **is** `/home/arcana-novai`, so `~/exchange` and the real tree
> `/home/arcana-novai/exchange` are **the same path**. Making it a symlink to
> itself is not a thing you can do. N0 satisfies the convention *in substance*
> — the served path is `~/exchange` and it is the real store — while the form
> differs (real directory, not symlink). Recorded here so nobody later reads
> the asymmetry as drift and "fixes" N0 by converting the store.
> **Do not convert N0's store to a symlink.** The paths are identical; any such
> change is a no-op at best and a self-referential link at worst.

### Step 2 — Fetch the server from the canonical repo, pinned

**One implementation. Not a copy of N0's copy, not a hand-edited variant.**
Fetch the file *by blob* from git and verify it against N0's hash:

```bash
OMEGA_REPO=/home/xnai/Documents/Projects/omega-engine-alpha   # from Step 0
cd "$OMEGA_REPO"

# The file does not exist at N1's current pin (ddfa0d80, branch
# node1/all-5-mcp-green) and is not on main. It landed on
# debut-v1.6.0-alpha at 2aa3a7f7. Fetch that explicitly:
git fetch origin debut-v1.6.0-alpha
git cat-file -e 2aa3a7f7:scripts/omega_exchange_server.py && echo "blob present"

# Materialise it, then PROVE it is byte-identical to N0's.
git show 2aa3a7f7:scripts/omega_exchange_server.py > /tmp/omega_exchange_server.py
sha256sum /tmp/omega_exchange_server.py
```

**The pin — N0's actual value, measured 2026-10-01:**

```
sha256  9a9e0a09dbe160e00e8630510df0ddd44d9825b805b6194c930232bed6949da4
git blob df7c6d05b0ac3def68a33cd1fb3580a0859b15ec
path    scripts/omega_exchange_server.py   (17,386 bytes)
commit  2aa3a7f7  "fix(exchange): manifest cache key — max_mtime + entry_count"
branch  debut-v1.6.0-alpha
```

If the sha256 on N1 differs, **STOP.** That is either a different commit or a
modified file, and both mean a second implementation now exists. Do not
"reconcile" it — report the mismatch.

```bash
install -m 0755 /tmp/omega_exchange_server.py "$OMEGA_REPO/scripts/omega_exchange_server.py"
python3 -m py_compile "$OMEGA_REPO/scripts/omega_exchange_server.py" && echo "syntax OK"
```

**Do not modify this file.** It is AnyIO-native and must stay that way: no
`import asyncio` anywhere (M1). Known defects in it are listed in §9 and are
**documented, not patched** — patching is an Architect decision.

### Step 3 — Install the unit

```bash
mkdir -p ~/.config/systemd/user
cp /path/to/scripts/deploy/n1/omega-exchange.service ~/.config/systemd/user/
# adjust the paths you resolved in Step 0, then:
systemctl --user daemon-reload
systemctl --user enable --now omega-exchange.service
systemctl --user status omega-exchange.service --no-pager
journalctl --user -u omega-exchange.service -n 30 --no-pager
```

Expected in the journal — a startup line, then serving:

```json
{"ts":"...","service":"omega-exchange/2.0","method":"-","path":"-","status":0,"bytes":0,
 "client_ip":"-","user_agent":"-","note":"startup root=/home/xnai/exchange bind=127.0.0.1:805"}
```

`root=` must be `/home/xnai/exchange` — i.e. the symlink resolved. If it shows
`/home/arcana-novai/exchange` you are running the **N0 unit**; stop.

Local liveness, from N1 itself:

```bash
curl -s http://127.0.0.1:805/manifest.json | python3 -m json.tool | head -8
```

Hardening applied (modelled on `omega-research.service`, which was hardened on
2026-09-30 after a 62-day crash loop):

| Directive | Value | Why |
|---|---|---|
| `StartLimitIntervalSec` | `300` | With `RestartSec=10s`, five restarts take ~50 s — **inside** the window, so the limiter can actually fire. The research unit had `RestartSec=30s` under the 10 s default window: mathematically incapable of firing, for 62 days. |
| `StartLimitBurst` | `5` | Caps the loop at 5 attempts / 5 min. |
| `StandardOutput/Error` | `journal` | **Never** `append:` — that is what grew 81.5 MB of flat log. Journal retention is bounded. |
| `OOMScoreAdjust` | `200` | Prefer killing the exchange origin over the Hub. |
| `Restart` | `on-failure` | — |
| `RestartSec` | `10s` | — |
| `RestartPreventExitStatus` | `2` | The server exits **2** for a missing root or a non-loopback host. Both are operator-fixable; retrying only buries the FATAL line. |
| `OMEGA_EXCHANGE_HOST` | `127.0.0.1` | Loopback only. The server **refuses to start** otherwise (exit 2). |
| `ProtectSystem=strict` + `ReadOnlyPaths` | `%h/exchange %h/omega-exchange` | Read-only surface, enforced at the mount namespace. |
| `NoNewPrivileges`, `PrivateTmp` | yes | — |
| `ExecStartPre` ×3 | `test -d/-x/-r` | Fail loud and named, before uvicorn. |

`NoNewPrivileges` and `PrivateTmp` are the two directives carried over from N0's
unit unchanged. There is deliberately **no `ProtectHome`** — it would hide
`~/exchange` from the mount namespace and break the read path.

### Step 4 — Publish on the tailnet

Syntax verified against the live binary on N0 (`tailscale 1.102.4`):

```bash
tailscale serve --bg --yes --https=805 http://127.0.0.1:805
tailscale serve status
```

Expected shape (mirror of N0's working config):

```
https://n1.tail51f14a.ts.net:805 (tailnet only)
|-- / proxy http://127.0.0.1:805
```

The client URL is then:

```
https://n1.tail51f14a.ts.net:805/<path>      # HTTPS ONLY
```

**If the Architect takes Option B (8019)**, the serve command is:

```bash
tailscale serve --bg --yes --https=805 http://127.0.0.1:8019   # public 805 -> origin 8019
```

so the *public* port stays 805 — which preserves Lilith's namespace point at
the only layer a peer actually sees — while the *origin* binds 8019, where the
ACL already permits. **This is the cheapest reconciliation of the two
positions and the Architect should know it exists.**

---

## 4. THE ONLY SUPPORTED URL FORM

```
https://n1.tail51f14a.ts.net:805/<path>
```

**HTTPS only. Always `curl -f`.** Plain HTTP to the tailnet IP is answered by
tailscaled's TLS terminator with a **48-byte ASCII** body that `curl -o` writes
to disk exactly as though it were a successful download. That is the
false-success bug this origin exists to close — full analysis in
`EXCHANGE_PIPE_RUNBOOK.md` §"The Broken URL Form".

```bash
curl -sf -o /tmp/artifact.zip https://n1.tail51f14a.ts.net:805/<path>
```

---

## 5. HOW DO I KNOW IT IS READ-ONLY? (the check Lilith named)

**Expected: every write verb returns `405` with an `X-Omega-Error: 1` JSON
envelope — never a bare body, never a 200.**

```bash
BASE=https://n1.tail51f14a.ts.net:805
for M in PUT POST DELETE PATCH; do
  printf '%-6s -> ' "$M"
  curl -s -o /dev/null -w '%{http_code}\n' -X "$M" \
       --data-binary 'pwned' "$BASE/.__write_probe_do_not_create__"
done
```

```
PUT    -> 405
POST   -> 405
DELETE -> 405
PATCH  -> 405
```

Then prove nothing landed:

```bash
curl -s -o /dev/null -w 'GET after writes -> %{http_code}\n' \
     "$BASE/.__write_probe_do_not_create__"          # MUST be 404
```

N0's live equivalent, run on N0 2026-10-01, for comparison:

```
$ curl -s -o /dev/null -w "PUT  -> %{http_code}\n" -X PUT http://127.0.0.1:8019/evil.sh
PUT  -> 405
$ curl -s -o /dev/null -w "POST -> %{http_code}\n" -X POST http://127.0.0.1:8019/evil.sh
POST -> 405
```

Read-only is enforced in **three independent places**, which is why it holds:
(1) Starlette routes declare `methods=["GET","HEAD"]`; (2) a 405 exception
handler returns a JSON envelope; (3) `ProtectSystem=strict` +
`ReadOnlyPaths` make the store read-only **at the kernel**, so even a
hypothetical write handler could not persist anything.

> If any verb returns something other than 405, **roll back immediately** and
> report it. A writable origin on the tailnet is a remote-code-execution
> surface, and the manifest is the only thing standing between a corrupted file
> and a trusted one. A slower honest channel beats a writable one.

---

## 6. LOCAL CHECKS ON N1 (before anyone claims it works)

```bash
systemctl --user is-active omega-exchange.service        # active
systemctl --user show omega-exchange.service -p NRestarts # must not be climbing
ss -ltnp | grep 805                                      # 127.0.0.1:805 ONLY
```

**`ss` must show `127.0.0.1:805`, never `0.0.0.0:805` or `*:805`.** A wildcard
bind puts the store on the LAN — the exact defect class
`make check-lan-exposure` exists to catch. The server refuses a non-loopback
`HOST` at startup, so this is a belt-and-braces confirmation.

---

## 7. TWO-VANTAGE VERIFICATION

### THE LAW

> **A CHANNEL VERIFIED FROM ONE SIDE IS A HALF-CHANNEL.**

`scripts/exchange_verify_duplex.sh` verifies **one** leg. It is not a duplex
test. The duplex test is **both** legs, from the opposite nodes, both passing.
A one-sided green check is the same false success as a 48-byte download.

### 7.1 Leg 1 — N1 pulls from N0 (already proven, re-run to confirm still true)

```bash
# ON N1
./scripts/exchange_verify_duplex.sh \
    https://n0.tail51f14a.ts.net:8019 \
    /home/arcana-novai/exchange \
    /home/xnai/exchange 10
```

**Status: previously 88/88. N0's store has since grown — it is now 95
artifacts (measured 2026-10-01), so expect ~95 entries, not 88.** The count grew;
the transfer did not regress. Re-run rather than trusting the old number.

### 7.2 Leg 2 — N0 pulls from N1 (the new leg; this is what is unbuilt)

```bash
# ON N0   (repo: ~/Documents/Xoe-NovAi/omega-engine)
./scripts/exchange_verify_duplex.sh \
    https://n1.tail51f14a.ts.net:805 \
    /home/xnai/exchange \
    /home/arcana-novai/exchange 10
```

Both legs green ⇒ duplex. One leg green ⇒ half-channel, and the report must say
so in those words.

### 7.3 What the verifier checks, per leg

1. **Reachability** — HTTPS 200 on `/manifest.json`, with an ACL diagnosis if it
   times out vs. refuses.
2. **Origin identity** — the manifest's `root` equals the *expected remote*
   root, and does **not** equal this node's own root. This is the anti-self-fetch
   guard; see §9.1 for why it is not optional.
3. **Read-only** — PUT/POST/DELETE/PATCH all 405, and the probe file absent after.
4. **Path containment** — `../../../../etc/passwd` refused.
5. **Byte-exact** — N artifacts: size **and** sha256 against the manifest, with
   the `X-Omega-SHA256` / `X-Omega-Size` headers cross-checked against the
   manifest so a store mutating mid-read is caught rather than absorbed.

Exit `0` only if every check passed. No partial success, no "mostly fine"
(M23). **A verifier that exits 0 on a broken channel is worse than no
verifier** — it manufactures the confidence it was built to prevent.

### 7.4 Verifier test results (N0, 2026-10-01 — real runs)

The script was exercised before shipping, including against the live blocked port:

| Test | Invocation (abbreviated) | Result |
|---|---|---|
| A — happy path | `… 127.0.0.1:8019 /home/arcana-novai/exchange /home/xnai/exchange 3` | **12/12 PASS, exit 0** |
| B — self-fetch trap | `… 127.0.0.1:8019 /home/arcana-novai/exchange /home/arcana-novai/exchange 2` | **exit 1** — "ORIGIN IS THIS NODE'S OWN STORE" |
| C — live ACL drop | `… https://n1.tail51f14a.ts.net:805 …` | **exit 1** — `curl (28) Connection timed out`, diagnosed as ACL drop |

Test C is the finding from §1 reproduced through the tooling: pointed at the
port the Architect ruled, the verifier reports a timeout and names it as a
policy denial rather than a network fault.

---

## 8. ROLLBACK

Ordered fastest-first. Steps 1–2 restore N0 to exactly its pre-deploy state.

```bash
# 1. unpublish (immediate — the channel stops being visible at once)
tailscale serve --https=805 off          # or: tailscale serve clear

# 2. stop and disable
systemctl --user disable --now omega-exchange.service

# 3. remove the unit
rm ~/.config/systemd/user/omega-exchange.service
systemctl --user daemon-reload

# 4. optional — drop the symlink ONLY if you are certain nothing references it.
#    Do NOT delete /home/xnai/omega-exchange. That is the real store (M28:
#    no auto-deletion). The symlink carries no data; removing it loses nothing.
#    rm /home/xnai/exchange

# 5. optional — revert to the 8019 drop-in
rm ~/.config/systemd/user/omega-exchange.service.d/10-port-8019.conf
systemctl --user daemon-reload
```

**N0 is untouched by all of this** and needs no rollback. If Option B is in
force, the unit itself is unchanged; only the public port mapping moves.

---

## 9. KNOWN DEFECTS (documented, NOT patched — Architect rules on these)

### 9.1 `url_form` is hardcoded to N0 — a false-success vector

`omega_exchange_server.py` hardcodes, in **both** `/` and `/manifest.json`:

```python
"url_form": "https://n0.tail51f14a.ts.net:8019/<path>  (HTTPS ONLY)"
```

Confirmed live on N0, 2026-10-01:

```
url_form : https://n0.tail51f14a.ts.net:8019/<path>  (HTTPS ONLY)
root     : /home/arcana-novai/exchange
```

The string is **not** parameterised by the node serving it. So **N1's manifest
— served by N1, listing N1's files — instructs the client to download them
from N0.** A client that trusts `url_form` pulls N1's manifest, fetches every
path from N0, and receives N0's bytes. Where filenames differ, the sha256 check
catches it and reports a mismatch; where the two stores happen to share a
filename, it downloads **the wrong node's file** and only a size mismatch may
save you — and if sizes coincide too, it passes clean.

That is a false success on the precise channel whose only defence is the
manifest. It is the most consequential defect found in this exercise.

**Handled where it can be, without touching the server:** the verifier
**never reads `url_form`**. It builds every URL from the operator-supplied
`base_url` and proves identity from the manifest's `root` field. The trap is
caught by check 2, proven by test B in §7.4.

**Proposed server fix, for the Architect — NOT applied:**
derive `url_form` from the bound `HOST`/`PORT` (or an `OMEGA_EXCHANGE_PUBLIC_URL`
env var) instead of hardcoding. One line, removes the class of bug. Held back
because the Architect's instruction was *"do not modify it beyond nothing"*, and
silently patching a shared server during a deploy is how two implementations
start. **This needs an explicit ruling.**

### 9.2 The manifest truncates at 5000 entries

`_MANIFEST_MAX_ENTRIES = 5000`, and the walk `break`s at the limit. Beyond
5000 files, `/manifest.json` **silently reports a partial tree** — and the
`count` field reflects the truncation, not the tree. N0 has 95. N1's
`~/omega-exchange` is unknown. If it is large, a client can believe it has the
whole store. **Check `count` against a real file count before trusting a
manifest** (§7.3 prints it deliberately).

### 9.3 The exchange test suite exits 0 while running ZERO tests

`scripts/test_exchange_false_success.py` is a **pytest** file. Invoked as
documented in `EXCHANGE_PIPE_RUNBOOK.md` — as a plain script — it executes
**nothing** and still reports success:

```
$ .venv/bin/python scripts/test_exchange_false_success.py
$ echo $?
0                      # ← zero tests ran. This 0 means nothing.

$ .venv/bin/python -m pytest scripts/test_exchange_false_success.py -q
OK                    # ← real cases, real result
```

Both exit 0. Only one of them ran a test. The plain-script invocation has no
`unittest.main()`, no `pytest.main()`, and no `__main__` block, so the module
imports, defines classes, and exits — a green result for zero work.

This is the **exact false-success class this whole system was built to
eliminate**, sitting inside the system's own test suite: a check that reports
pass without having checked anything. It is the 48-byte-download bug wearing a
test harness.

**Rule: run this suite with `pytest`, never with `python`.** On N1, after
installing anything, the real signal is:

```bash
cd "$OMEGA_REPO" && .venv/bin/python -m pytest scripts/test_exchange_false_success.py -q
```

And when reading *any* green test result in this repo, confirm the case count
before believing it. A green run reporting `Ran 0 tests` is a failure wearing a
green shirt.

### 9.4 N1's checkout pin does not contain the server

N1 sits at `ddfa0d80` on `node1/all-5-mcp-green`; that commit is not even
present in N0's clone, and it does not contain the exchange server. The file
lives on `debut-v1.6.0-alpha` at `2aa3a7f7`. Step 2 fetches it explicitly. A
plain `git pull` on N1 will **not** bring the server along.

---

## 10. REVIEW OF LILITH-N1's PLAN

She was right about the things that were load-bearing, and one of her points is
the reason this document has a cheaper option than the one the ruling picked.

| Her claim | Verdict |
|---|---|
| Do not write a second implementation; deploy the same file | **Correct, and adopted.** The server is fetched by blob at a pinned commit and verified against N0's sha256 (§Step 2). |
| Alias the tree with a symlink, never a copy | **Correct, and adopted** — "a copy would fork the tree, a symlink cannot drift." |
| Read-only must hold at both ends | **Correct**, and verified in three layers (§5). |
| 805 rather than 8019 | **Sound reasoning, wrong constraint.** Her namespace argument is good and worth keeping. But the binding constraint is the ACL, and the ACL permits 8019 and denies 805 (§1). She reasoned about the namespace without checking the filter — the gap this whole exercise was commissioned to close. |
| — (missed) | **`url_form` is hardcoded to N0.** On a duplex pipe the remote manifest points clients back at the local node. This is the single most dangerous item found (§9.1). |
| — (missed) | **The venv that actually has `anyio`/`uvicorn`/`starlette` is unresolved.** Two venvs exist; she listed both and chose neither. Picking the wrong one is a failed deploy (§Step 0). |
| — (missed) | **The N1 checkout path is unknown.** Not in her survey, and the unit cannot be written without it (§Step 0). |
| — (missed) | **The reverse grant already exists on 8019.** The premise that n0→n1 "has never been built" is incorrect; it is built and permitted, on the other port (§1.3). |

The pattern worth naming: three of the four misses are **unverified local facts**
on the node she surveyed, and one is a **source-level defect** in the shared
server. None are reasoning errors. The plan is good; it needed the machine to
be asked.

---

## 11. SIGNOFF

| # | Check | Who | State |
|---|---|---|---|
| 1 | Step 0 resolved (repo path, venv with deps) | Lilith-N1 | ☐ |
| 2 | Step 1 symlink `~/exchange` → `~/omega-exchange` | Lilith-N1 | ☐ |
| 3 | Step 2 server fetched, sha256 `9a9e0a09…` matches | Lilith-N1 | ☐ |
| 4 | Step 3 unit active, `ss` shows `127.0.0.1:805` | Lilith-N1 | ☐ |
| 5 | Step 4 `tailscale serve status` shows n1:805 | Lilith-N1 | ☐ |
| 6 | §5 read-only: PUT/POST/DELETE/PATCH all 405 | Lilith-N1 | ☐ |
| 7 | §7.1 Leg 1 — N1 pulls N0 | Lilith-N1 | ☐ |
| 8 | §7.2 Leg 2 — N0 pulls N1 | doom_guy | ☐ |
| 9 | §9.1 ruling: patch `url_form`, or keep handled-in-verifier | Architect | ☐ |
| 10 | **§1.4 ruling: Option A (ACL on 805) or Option B (8019)** | Architect | ☐ |

> **Do not mark the pipe duplex until rows 7 AND 8 are both green.** One green
> leg is a half-channel, and saying otherwise is how a channel that only works
> in one direction gets reported as working in both.

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ SLOT-S1 ⬡ AP-DOOM_GUY-v3.0.0 ⬡ 2026-10-01 ⬡ model: space-bunny-free*
