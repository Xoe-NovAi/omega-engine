# GRUB Secure Boot Diagnosis — ASUS ExpertBook P1503CVA / Ubuntu 26.04.1

## 0. Bottom line

`search --label` succeeding and `linux /casper/vmlinuz` failing right after is a
**path-resolution failure, not a signing/shim/lockdown failure.** Shim/GRUB's
signature verifier only fires once a file is actually opened for the kernel or
a dynamically-loaded module — it never gets that far here. Fix the lookup first;
signature issues (if any) will surface as a *different* error afterward.

Highest-leverage fix: **stop re-deriving the boot stanza by hand.** Section 5 of
the briefing shows the ISO's own `/boot/grub/grub.cfg` already boots
`/casper/vmlinuz` successfully with a much simpler command line than the
custom entries use (no `boot=casper`, no `iso-scan/filename`, no
`layerfs-path`, no `lockdown=off`). Chainloading into that file via
`configfile` reuses Canonical's tested path instead of a hand-rolled copy of
it. See `grub.cfg` (attached) for a chainload-first rewrite.

---

## 1. Root-cause ranking for "found ISO9660 / casper/vmlinuz not found"

| # | Hypothesis | Confidence | Why | Confirm/deny with |
|---|---|---|---|---|
| 1 | `search --file` vs `search --label` take different code paths, and the label match is a shallower probe than the directory-tree walk `linux` performs | Medium | `search --label` only needs the Primary Volume Descriptor; opening `/casper/vmlinuz` requires a full directory traversal (Joliet vs Rock Ridge tree selection, `CE` continuation records, etc.) | Run `search --no-floppy --set=root --file /casper/vmlinuz` directly — if *this* also fails to set root, the bug is in directory traversal, not label matching |
| 2 | Rock Ridge vs Joliet tree mismatch: GRUB's iso9660 driver picks one naming tree, and the specific record is malformed/absent in that tree for this xorriso build | Medium | Known GRUB iso9660 driver quirk class (see Launchpad #1169492 for a related symlink-in-Rock-Ridge case) | `ls -l (hd0,gpt1)/casper/` — if `vmlinuz` is listed but `ls -l (hd0,gpt1)/casper/vmlinuz` errors, this is it |
| 3 | Nested/duplicated partition metadata: this GPT partition 1 begins exactly at the byte offset where the raw ISO9660 Volume Descriptor Set normally lives (both land at 32 KiB), which can confuse offset math in some iso9660 driver builds when the fs is read as a *partition object* instead of a *whole-disk object* | Low–Medium | Consistent with "label found, file not found" but unconfirmed without live testing | `linux (hd0,gpt1)/casper/vmlinuz` with an **explicit** device prefix instead of relying on `$root` — if this succeeds, `$root` scoping/offset is the culprit |
| 4 | `rmmod tpm` at top level (outside any menuentry) throws a parse-time error if `tpm` was never loaded, which can silently disrupt subsequent parsing | Low | Speculative, but zero-cost to remove | Removed in the rewritten `grub.cfg` — retest without it |
| 5 | Curly/smart quotes (`" "` instead of `" "`) around the label string, introduced by a copy/paste through a rich-text tool | Low for the vmlinuz error, **higher for the missing menu entry** (see §2) | Smart quotes silently break GRUB string tokenizing | `hexdump -C grub.cfg \| grep -A2 -B2 e2` on the HP — non-ASCII bytes near the quotes confirm it |

**Do not spend more time guessing — hypothesis 1's command is a 10-second test
that tells you whether this is a label-matching issue or a genuine
directory-lookup issue.** That single result should eliminate 2 of the 5 rows.

---

## 2. Missing "Chainload ISO GRUB" menu entry

GRUB has no menu-entry count limit and `--class` doesn't hide entries — rule
those out. The realistic causes are:

- **A syntax error inside that specific block** (unbalanced quote/brace) that
  makes GRUB's parser silently absorb it into the neighboring entry, rather
  than erroring visibly.
- **Non-ASCII characters** (smart quotes, non-breaking spaces) introduced when
  the config was copied through a document/chat tool at some point in the
  pipeline. Entry 1 uses the identical quoted label string and *does* render,
  which argues against this — but it doesn't rule out corruption specific to
  that one instance if the two entries were pasted from different sources.

**Action**: on the HP, run `hexdump -C /path/to/grub.cfg | less` and check the
bytes around both `search --label` occurrences are `22` (`"`) rather than
`e2 80 9c` / `e2 80 9d` (smart quotes). Then rebuild from the attached
`grub.cfg`, which is plain ASCII, and retest with only that one entry present
(comment out the others) to isolate whether it renders alone.

---

## 3. Shim lockdown & kernel loading (Q3)

- Shim's PE-signature verifier is invoked by GRUB for exactly two file
  classes: `GRUB_FILE_TYPE_LINUX_KERNEL` (whatever `linux` opens) and
  `GRUB_FILE_TYPE_GRUB_MODULE` (a `.mod` loaded from disk that wasn't already
  compiled into `core.img`). **`initrd` is never signature-checked** — it's
  loaded as opaque data.
- The current error occurs at file *lookup*, before GRUB ever gets to hand
  the file to shim's verifier. So nothing you're seeing right now is a
  lockdown/signature symptom. Once the lookup is fixed, a *new* error
  mentioning "bad shim signature," "invalid signature," or similar would be
  the real lockdown signal — and given the firmware DB already contains the
  Canonical key (confirmed in your research), that chain should validate
  without needing the Microsoft path at all.
- Separately: **`lockdown=off` is not a valid kernel parameter.** The Linux
  kernel's lockdown LSM only accepts `lockdown=none`, `lockdown=integrity`, or
  `lockdown=confidentiality`. `off` is silently ignored, so this flag is
  currently a no-op either way. It's not your blocker, but correct it to
  `lockdown=none` if you specifically need lockdown disabled — most live-boot
  sessions don't need it at all, since lockdown mainly restricts unsigned
  module loading, raw `/dev/mem` access, and unsigned `kexec`.

---

## 4. ISO9660 module timing (Q4)

`insmod iso9660` before `search` is correct ordering — this is not the issue.
GRUB's `search` command already tries every loaded/available filesystem
driver against every visible device, so as long as `iso9660` is loaded before
the *first* `search` call in the file (which it is), later `search`/`linux`
calls in other menuentries don't need to re-`insmod` it — though the rewritten
config does so defensively per-entry anyway, since it's a zero-cost safeguard
against entries being reordered later.

---

## 5. `iso-scan/filename` (Q6) — drop it

This parameter tells casper's initramfs scripts to **search attached devices
for a literal `.iso` file** and loopback-mount it — the mechanism used when an
ISO sits as a file inside another filesystem (Ventoy-style). You dd'd the ISO
directly onto the block device; there is no `.iso` file anywhere on the USB,
only the extracted ISO9660 filesystem itself. With `iso-scan/filename` set,
casper's initramfs will search for a file that doesn't exist and can fail to
find rootfs even after GRUB successfully loads the kernel and initrd. Boot
with plain `boot=casper` only, as the rewritten `grub.cfg` does.

## 6. `layerfs-path` (Q7)

Correct mechanism for the "minimal" squashfs layering used by newer Ubuntu
desktop ISOs — but verify the **exact filename** for 26.04.1 before trusting
it, since it can change between point releases. At the grub prompt:
`ls (hd0,gpt1)/casper/` and confirm the squashfs name matches
`minimal.standard.live.squashfs` exactly. If casper still can't assemble the
rootfs after the file-lookup issue is fixed, that's the next thing to check.

---

## 7. ASUS ExpertBook / firmware notes (Q5)

- Esc = one-time boot menu, F2 = setup — already confirmed correct, not a
  factor here.
- Firmware DB has the Canonical key directly (not just the Microsoft chain),
  which is the normal arrangement on Ubuntu-certified OEM hardware and means
  shim can validate GRUB without ever touching the Microsoft UEFI CA path —
  the *absence* of Microsoft UEFI CA in your DB is very likely a non-issue
  for this specific chain.
- Timely but probably tangential: Microsoft's 2011 UEFI CA and KEK CA
  expired June 2026, with a 2023 CA generation replacing them industry-wide.
  Existing boot assets keep working, but future Canonical shim updates will
  ship signed against the new 2023 certificates. Worth knowing given today's
  date, but since your db path doesn't rely on the Microsoft chain at all,
  it shouldn't be what's blocking you right now.
- If you hit an *actual* signature-verification error later (distinct from
  today's file-not-found error), check the BIOS for a CSM
  (Compatibility Support Module) toggle — leaving CSM enabled alongside
  Secure Boot causes inconsistent boot-path behavior on some ASUS boards and
  is worth ruling out.

---

## 8. Alternative approach (Q4 in "requested deliverables")

**Yes — restructure around `configfile` chainload as the primary entry**, per
the attached `grub.cfg`. Keep exactly one manual fallback entry with
corrected, minimal kernel params (§5–6 above) for cases where chainloading
itself has a problem, and one raw-device-path control entry to isolate
`search` vs `linux` behavior if needed. Don't maintain three parallel
hand-written reimplementations of the same boot stanza — every one of Q1,
Q4, Q6, and Q7 above evaporates if the primary path just reuses Canonical's
already-working config instead of re-deriving it.

---

## 9. Diagnostic commands — run these live at the ASUS `grub>` prompt

Press `c` at the boot menu to get a shell, then run in order:

```
ls
ls (hd0,gpt1)/
ls -l (hd0,gpt1)/casper/
search --no-floppy --set=root --file /casper/vmlinuz
echo $root
linux (hd0,gpt1)/casper/vmlinuz boot=casper
```

What each answers:
- `ls` — confirms disk/partition enumeration (is the USB really `hd0`, or is
  the internal NVMe `hd0` and the USB `hd1`?)
- `ls (hd0,gpt1)/` — confirms `casper/`, `.disk/`, `pool/` are visible at all
- `ls -l (hd0,gpt1)/casper/` — confirms `vmlinuz` is listed with a real size
  (not zero, not missing)
- `search --file` — the single most informative test; see §1 row 1
- `echo $root` — confirms what `search` actually set, verbatim
- explicit-device `linux` — isolates whether the failure is about `$root`
  scoping/offset vs. the file genuinely being unreachable by any path

Report back what each of these actually prints — that will pin the exact
failure point far faster than further hypothesis-ranking from a transcribed
config.
