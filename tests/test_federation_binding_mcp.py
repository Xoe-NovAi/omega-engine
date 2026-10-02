def test_mcp_boundary_keys_read_by_instance_not_entity(hub_runtime, tmp_path, monkeypatch):
    """The fix Ma'at shipped, exercised THROUGH THE REAL MCP BOUNDARY.

    Every earlier test drove federation_store directly and therefore never
    traversed the line that changed. This one calls the @mcp.tool coroutine.
    """
    import anyio, json
    from mcp_servers.omega_hub import state as hub_state
    from mcp_servers.omega_hub.hub_tools import tools as T

    root = tmp_path / "handoff"
    monkeypatch.setattr(hub_state, "HANDOFF_BASE", root)          # store root
    monkeypatch.setattr(T, "HANDOFF_PENDING", root / "pending")    # by-value name
    # KNOWN FOOTGUN, WORKED AROUND NOT FIXED: tools.py imports HANDOFF_PENDING BY
    # VALUE at line 64, so it is an ABSOLUTE path to the live queue computed at
    # import. It also bypasses store.ensure_layout(). Patching it + creating the
    # dir is what makes this hermetic. Reported, not silently repaired.
    for d in ("pending", "hot", "cold", "retired"):
        (root / d).mkdir(parents=True, exist_ok=True)

    def call(**kw):
        async def go():
            return await T.hivemind_handoff(**kw)
        r = anyio.run(go)
        return json.loads(r if isinstance(r, str)
                          else "".join(getattr(c, "text", "") for c in r.content))

    sub = call(action="submit", source_channel="opencode", source_entity="gaming-expert",
               target_channel="opencode", target_entity="ge-n1",
               task="BINDING TEST", context="", priority=0, source_instance="ge-n0/test")
    assert sub.get("status") == "submitted", sub
    pid = sub["packet_id"]

    call(action="read", source_channel="opencode", source_entity="gaming-expert",
         source_instance="ge-n0", packet_id=pid, result="ack")

    # Journal design: the envelope on disk is NEVER mutated by a read.
    # Read state lives in the `.receipts.jsonl` sidecar, keyed by instance.
    journal = root / "pending" / f"{pid}.receipts.jsonl"
    assert journal.is_file(), f"receipt journal missing: {journal}"
    lines = [json.loads(l) for l in journal.read_text().splitlines() if l.strip()]
    readers = {l["reader"] for l in lines}
    assert "ge-n0" in readers, f"read was NOT keyed by instance: {readers}"
    assert "ge-n1" not in readers, f"one agent's read leaked across instances: {readers}"
    # and the envelope itself must be untouched by the read
    stored = json.loads((root / "pending" / f"{pid}.json").read_text())
    assert stored.get("read_by", {}) == {}, (
        f"envelope read_by was mutated by a read: {stored.get('read_by')}"
    )
