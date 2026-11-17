// gnosis-leash.js — OpenCode plugin: automated Gnosis Lock leash for Node 1.
// V2 port: uses @opencode/plugin Plugin.define API.
//   - session.created / session.idle   → ctx.event.subscribe()
//   - experimental.session.compacting   → ctx.session.hook("compaction", …)
//   - experimental.chat.system.transform → ctx.session.hook("context", …)
// Pure JS, zero runtime deps, never throws. All events are fire-and-forget.
// Standards: async wiring uses Promises/$ (Bun); Python sibling code must use anyio.

import { Plugin } from "@opencode/plugin";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const HOME = os.homedir() || process.env.HOME || "/home/xnai";
// WELL_DIR_OVERRIDE mirrors the convention in scripts/well_storage.py: lets the
// regression suite point the reader at a fixture corpus instead of the live one.
const WELL_DIR =
  process.env.WELL_DIR_OVERRIDE ||
  path.join(HOME, "Documents/Projects/omega-engine-alpha/gnosis/well");
const STATE_DIR = path.join(HOME, ".config/opencode", "plugins", "state");
const TIMELINE = path.join(STATE_DIR, "gnosis-events.jsonl");
const ERRLOG = path.join(STATE_DIR, "gnosis-errors.jsonl");
const INDEX_MD = path.join(HOME, "WanderGround", "INDEX.md");
const WELL_JSONL = path.join(WELL_DIR, "well.jsonl");
const IDENTITY_JSON = path.join(
  HOME,
  "Documents/Projects/omega-engine-alpha/gnosis/identity/identity.json"
);
const SESSIONS_DIR = path.join(
  HOME,
  "Documents/Projects/omega-engine-alpha/gnosis/sessions"
);

function ts() {
  return new Date().toISOString();
}

function currentSessionOf() {
  try {
    if (!fs.existsSync(IDENTITY_JSON)) return "unknown";
    const id = JSON.parse(fs.readFileSync(IDENTITY_JSON, "utf8"));
    return id?.current_session || "unknown";
  } catch {
    return "unknown";
  }
}

function appendEvent(evt) {
  try {
    fs.mkdirSync(STATE_DIR, { recursive: true });
    fs.appendFileSync(TIMELINE, JSON.stringify({ ts: ts(), ...evt }) + "\n");
  } catch (err) {
    appendDiagnostic("appendEvent", err, { event: evt?.kind || "unknown" });
  }
}

function appendDiagnostic(where, err, ctx = {}) {
  try {
    fs.mkdirSync(STATE_DIR, { recursive: true });
    fs.appendFileSync(
      ERRLOG,
      JSON.stringify({
        ts: ts(),
        level: "error",
        event: "plugin.error",
        module: "gnosis-leash",
        where,
        message: err instanceof Error ? err.message : String(err),
        stack: err instanceof Error ? err.stack : undefined,
        ctx,
      }) + "\n"
    );
  } catch {
    try {
      console.error(`[gnosis-leash] ${where}: ${err instanceof Error ? err.message : err}`);
    } catch { /* no trace channels left */ }
  }
}

function readIndexRules() {
  try {
    const raw = fs.readFileSync(INDEX_MD, "utf8");
    const lines = raw.split("\n").filter((l) => l.trim().length > 0);
    return lines.slice(0, 24);
  } catch (err) {
    appendDiagnostic("readIndexRules", err, { file: INDEX_MD });
    return [];
  }
}

function isPopulatedNarrative(content) {
  return (
    !content.includes("TODO: Fill in") &&
    (content.includes("## Gnosis Gained") || content.includes("## Key Decisions"))
  );
}

function packStatus(sessionId) {
  try {
    if (!sessionId) return "captured";
    const manifestPath = path.join(SESSIONS_DIR, `${sessionId}_manifest.json`);
    if (!fs.existsSync(manifestPath)) return "captured";
    const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    return m.reflection_status || "captured";
  } catch (err) {
    appendDiagnostic("packStatus", err, { sessionId });
    return "captured";
  }
}

function readLatestNarrative() {
  const none = (reason) => ({ narrative: null, source: "none", reason, pack_state: "none" });
  try {
    if (!fs.existsSync(IDENTITY_JSON)) return none("identity.json missing");
    const identity = JSON.parse(fs.readFileSync(IDENTITY_JSON, "utf8"));
    const currentSession = identity?.current_session;

    if (currentSession) {
      const status = packStatus(currentSession);
      const narrativePath = path.join(SESSIONS_DIR, `${currentSession}_narrative.md`);
      if (fs.existsSync(narrativePath)) {
        const content = fs.readFileSync(narrativePath, "utf8");
        if (status === "reflected" && isPopulatedNarrative(content)) {
          return {
            narrative: content.trim(),
            source: "current",
            reason: `current_session ${currentSession} is REFLECTED`,
            pack_state: status,
          };
        }
        if (status !== "reflected") {
          return none(
            `current_session ${currentSession} status=${status} → reflection required`
          );
        }
        return none(
          `current_session ${currentSession} status=${status} → narrative still TODO (not ingested)`
        );
      }
      return none(`current_session ${currentSession} status=${status} → narrative file missing`);
    }
    return none("identity has no current_session");
  } catch (err) {
    appendDiagnostic("readLatestNarrative", err, { file: IDENTITY_JSON });
    return none("exception: " + (err instanceof Error ? err.message : String(err)));
  }
}

function findLatestReflectedNarrative() {
  try {
    if (!fs.existsSync(SESSIONS_DIR)) return null;
    const candidates = fs
      .readdirSync(SESSIONS_DIR)
      .filter((f) => f.endsWith("_narrative.md"))
      .map((f) => f.replace(/_narrative\.md$/, ""))
      .filter((sid) => packStatus(sid) === "reflected")
      .map((sid) => {
        const p = path.join(SESSIONS_DIR, `${sid}_narrative.md`);
        return { path: p, mtime: fs.statSync(p).mtimeMs };
      })
      .sort((a, b) => b.mtime - a.mtime);
    for (const c of candidates) {
      const content = fs.readFileSync(c.path, "utf8");
      if (isPopulatedNarrative(content)) {
        return { narrative: content.trim(), source: "fallback", session: path.basename(c.path) };
      }
    }
  } catch (err) {
    appendDiagnostic("findLatestReflectedNarrative", err, { dir: SESSIONS_DIR });
  }
  return null;
}

const WELL_INJECT_DOMAINS = ["harness", "local_ai"];

function normalizeTags(raw) {
  if (Array.isArray(raw)) return raw.map((t) => String(t).trim()).filter(Boolean);
  if (typeof raw === "string") return raw.split(",").map((t) => t.trim()).filter(Boolean);
  return [];
}

function projectWellRecord(rec) {
  return {
    rule: String(rec.rule ?? ""),
    domain: String(rec.domain ?? "unknown"),
    kind: String(rec.kind ?? "unknown"),
    tags: normalizeTags(rec.tags),
    id: String(rec.record_id ?? "????????").slice(0, 8),
    source_pack: String(rec.source_pack ?? "unknown"),
  };
}

const WELL_PINNED_KINDS = new Set(["correction", "anti_pattern"]);
const WELL_PERMANENCE_FLOOR = 2;

function rankWellRecords(active, limit) {
  const seen = new Set();
  const distinct = [];
  for (const r of active) {
    const key = String(r.rule ?? "").trim();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    distinct.push(r);
  }
  const pinned = distinct
    .filter((r) => WELL_PINNED_KINDS.has(r.kind))
    .slice(0, WELL_PERMANENCE_FLOOR);
  const pinnedIds = new Set(pinned.map((r) => r.record_id));
  const rest = distinct
    .filter((r) => !pinnedIds.has(r.record_id))
    .slice(0, Math.max(0, limit - pinned.length));
  const out = [...pinned, ...rest];
  out.sort((a, b) => (Date.parse(b?.ts ?? "") || 0) - (Date.parse(a?.ts ?? "") || 0));
  return out;
}

function readWellForInjection(limit = 8, domains = null) {
  const result = { records: [], scanned: 0, skipped: 0, errors: [] };
  try {
    if (!fs.existsSync(WELL_JSONL)) return result;
    const lines = fs.readFileSync(WELL_JSONL, "utf8").split("\n");
    const active = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      let rec;
      try {
        rec = JSON.parse(line);
      } catch (err) {
        result.skipped++;
        result.errors.push({ line: i + 1, reason: "invalid JSON" });
        appendDiagnostic("readWellForInjection.parse", err, { file: WELL_JSONL, line: i + 1 });
        continue;
      }
      if (!rec || typeof rec !== "object") {
        result.skipped++;
        result.errors.push({ line: i + 1, reason: "record is not an object" });
        continue;
      }
      result.scanned++;
      if (rec.status !== "active") continue;
      if (domains && !domains.includes(rec.domain)) continue;
      active.push(rec);
    }
    active.sort((a, b) => (Date.parse(b?.ts ?? "") || 0) - (Date.parse(a?.ts ?? "") || 0));
    result.records = rankWellRecords(active, limit).map(projectWellRecord);
  } catch (err) {
    result.skipped++;
    result.errors.push({ line: null, reason: String(err && err.message ? err.message : err) });
    appendDiagnostic("readWellForInjection", err, { file: WELL_JSONL });
  }
  return result;
}

function wellRecordsOrReport(res, where) {
  if (res.skipped > 0) {
    appendDiagnostic(
      where + ".degraded",
      new Error(`${res.skipped} Well record(s) skipped`),
      { scanned: res.scanned, records: res.records.length, errors: res.errors.slice(0, 5) }
    );
  }
  if (res.scanned > 0 && res.records.length === 0) {
    appendDiagnostic(
      where + ".silent_empty",
      new Error("Well contained records but none were injectable"),
      { scanned: res.scanned, skipped: res.skipped, errors: res.errors.slice(0, 5) }
    );
  }
  return res.records;
}

function formatWellBlock(records) {
  if (!records.length) return "";
  const lines = ["## ⬡ THE WELL — active corrections & insights (auto-injected)"];
  for (const r of records) {
    const tagStr = r.tags.length ? ` [${r.tags.join(",")}]` : "";
    lines.push(`- **${r.rule}**${tagStr}`);
    lines.push(`  (kind: ${r.kind} | domain: ${r.domain} | pack: ${r.source_pack} | id: ${r.id})`);
  }
  return lines.join("\n");
}

// ── V2 Plugin Entry ──────────────────────────────────────────────────────────

export default Plugin.define({
  id: "gnosis-leash",
  async setup(ctx) {
    const directory = ctx.location.directory;
    const project = ctx.location.project;

    // 1. Event subscription: session lifecycle logging.
    const controller = new AbortController();
    void (async () => {
      try {
        for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
          const type = event?.type || "";
          if (type === "session.created") {
            appendEvent({ kind: "session.created", session: event.sessionID, project });
          } else if (type === "session.idle") {
            appendEvent({ kind: "session.idle", session: event.sessionID });
          } else if (type === "session.compacted") {
            appendEvent({ kind: "session.compacted", session: event.sessionID });
          }
        }
      } catch (err) {
        appendDiagnostic("event.subscribe", err, {});
      }
    })();

    // 2. Compaction hook: inject temple context + human gnosis + Well.
    await ctx.session.hook("compaction", async (event) => {
      const rules = readIndexRules();
      const injected = [
        "## ⬡ GNOSIS LEASH — temple context (auto-injected)",
        "- Gnosis timeline: " + TIMELINE,
        "- WanderGround INDEX (domains, weights, operating rules):",
        ...rules,
        "- Compaction: preserve WanderGround invariants (NO local 8B+ synthesis;",
        "  deep synthesis via OpenCode Zen; sovereign capture in ~/WanderGround).",
      ];

      const current = readLatestNarrative();
      let narrative = current.narrative;
      let source = current.source;
      let reason = current.reason;
      let pack_state = current.pack_state;
      if (!narrative) {
        const fb = findLatestReflectedNarrative();
        if (fb) {
          narrative = fb.narrative;
          source = fb.source;
          pack_state = "reflected";
          reason = `fallback from current (${current.reason}) → ${fb.session}`;
        }
      }

      if (narrative) {
        injected.push(
          `## ⬡ HUMAN GNOSIS REFLECTION (captured before compaction; source: ${source}):`,
          narrative
        );
      } else {
        injected.push(
          "## ⚠️ GNOSIS-LOCK INCIDENT: NO HUMAN NARRATIVE AVAILABLE",
          `- reason: ${reason}`,
          "- This compaction is proceeding WITHOUT the human reflection channel.",
          "- The summary below is model-only synthesis; treat it as lower-fidelity.",
          "- To fix: run /gnosis-lock (skill) BEFORE the next /compact and answer",
          "  the reflection questions so a populated narrative exists.",
        );
        appendDiagnostic(
          "compaction_without_narrative",
          new Error("Compaction ran with no populated human narrative"),
          { current_session: currentSessionOf(), reason, source }
        );
      }

      const wellRes = readWellForInjection(8, WELL_INJECT_DOMAINS);
      const wellBlock = formatWellBlock(wellRecordsOrReport(wellRes, "compacting"));
      if (wellBlock) {
        injected.push(wellBlock);
      }

      if (Array.isArray(event.context)) {
        event.context.push(...injected);
      }

      appendEvent({
        kind: "session.compacting",
        session: event.sessionID,
        injected_count: injected.length,
        has_narrative: Boolean(narrative),
        narrative_source: source,
        narrative_reason: reason,
        pack_state: pack_state || "unknown",
      });
    });

    // 3. Context hook: append WanderGround operating rules + Well to system prompt.
    await ctx.session.hook("context", async (event) => {
      const rules = readIndexRules();
      const block =
        "## ⬡ GNOSIS LEASH — operating rules\n" +
        rules.map((l) => "  " + l).join("\n");

      const wellRes = readWellForInjection(6, WELL_INJECT_DOMAINS);
      const wellBlock = formatWellBlock(wellRecordsOrReport(wellRes, "system.transform"));

      const combined = wellBlock ? block + "\n\n" + wellBlock : block;

      if (Array.isArray(event.system) && event.system.length > 0) {
        event.system[0] = (event.system[0] ?? "") + "\n\n" + combined;
      } else if (Array.isArray(event.system)) {
        event.system.push(combined);
      } else {
        appendDiagnostic(
          "system.transform.no_system_array",
          new Error("event.system was not an array — injection skipped"),
          {}
        );
      }
    });

    // Cleanup: abort event subscription on unload.
    return () => controller.abort();
  },
});
