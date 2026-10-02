// gnosis-leash.js — OpenCode plugin: automated Gnosis Lock leash for Node 1.
// Uses the plugin event + compaction-hook surface (verified in 1.18.30 SDK types):
//   - session.created                      → log SESSION_START to the gnosis timeline
//   - session.idle                         → log SESSION_IDLE (end-of-session marker)
//   - experimental.session.compacting      → inject "the temple remembers" context
//   - experimental.chat.system.transform   → append WanderGround operating rules
// Pure JS, zero runtime deps, never throws. All events are fire-and-forget.
// Standards: async wiring uses Promises/$ (Bun); Python sibling code must use anyio.

import fs from "node:fs";
import path from "node:path";

const HOME = process.env.HOME || "/home/xnai";
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
    // Traceability: never swallow — write a structured diagnostic instead.
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
    // Last-resort floor: the diagnostics sink itself is broken. Never throw
    // out of a plugin hook; stderr is the only remaining trace channel.
    try {
      console.error(`[gnosis-leash] ${where}: ${err instanceof Error ? err.message : err}`);
    } catch { /* no trace channels left — exit silently */ }
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
  // Substantive reflection content, not an unedited template (TODO placeholders).
  return (
    !content.includes("TODO: Fill in") &&
    (content.includes("## Gnosis Gained") || content.includes("## Key Decisions"))
  );
}

// Missing manifest/status defaults to captured (conservative). Only a
// reflected manifest may satisfy narrative injection; content alone cannot
// override the lifecycle state machine.
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

// Structured narrative lookup. Returns { narrative, source, reason, pack_state }.
function readLatestNarrative() {
  const none = (reason) => ({ narrative: null, source: "none", reason, pack_state: "none" });
  try {
    if (!fs.existsSync(IDENTITY_JSON)) return none("identity.json missing");
    const identity = JSON.parse(fs.readFileSync(IDENTITY_JSON, "utf8"));
    const currentSession = identity?.current_session;

    // 1. Preference: the current session's narrative, if REFLECTED + populated.
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

// 2. Fallback: most recent REFLECTED pack on disk (narrative populated AND
//    manifest says reflected). The ritual creates a fresh CAPTURED pack moments
//    before /compact; a second lock mid-session leaves it TODO. The previous
//    REFLECTED pack still holds the human reflection and must survive — but
//    only packs that were intentionally ingested qualify.
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

// Domains injected at session start and compaction. Single source of truth:
// both call sites read this, so the two filters cannot drift apart.
const WELL_INJECT_DOMAINS = ["harness", "local_ai"];

// Coerce a record's `tags` into string[] regardless of how it was written.
// The corpus is append-only and hand-written: historical records store tags as
// a comma-string, newer ones as a JSON array. `truncate_dim`-class schema drift
// must degrade a single record, never abort the read. (An earlier version
// called .split() unguarded — one array-tagged record threw, the outer catch
// returned [], and the Well silently injected nothing at all.)
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

// Kinds that must never age out of the top-N. The permanence floor guarantees at
// least this many of the newest records of these kinds are always injected,
// however many newer records of other kinds land afterwards.
const WELL_PINNED_KINDS = new Set(["correction", "anti_pattern"]);
const WELL_PERMANENCE_FLOOR = 2;

// Rank active records for injection. Pure — no I/O. Input must already be
// sorted newest-first.
//
//   Dedup: identical rule text collapses to its newest record, so two copies of
//          one rule cannot occupy two injection slots.
//   Permanence floor: the newest WELL_PERMANENCE_FLOOR records of a pinned kind
//          are guaranteed a slot. This is a floor, NOT a monopoly — with more
//          corrections than slots it cannot resurface every high-severity rule;
//          it guarantees the class is always represented, and it rescues a
//          correction that has been pushed below the recency line by newer
//          non-correction records. Full old-rule reachability would need a
//          rotation or relevance term, which is deferred (see ROADMAP P1.5).
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

// Read top-N active Well records for injection (session start + compaction).
// Filters to relevant domains if provided; ranks via rankWellRecords (dedup +
// permanence floor over recency).
//
// Returns { records, scanned, skipped, errors } — deliberately NOT a bare array.
// `scanned > 0 && records.length === 0` means "there was data and none of it was
// readable", which is an incident, not an empty Well. Callers must be able to
// tell those apart; a bare [] cannot.
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
    // Unparseable ts sorts as epoch rather than poisoning the comparator with NaN.
    active.sort((a, b) => (Date.parse(b?.ts ?? "") || 0) - (Date.parse(a?.ts ?? "") || 0));
    result.records = rankWellRecords(active, limit).map(projectWellRecord);
  } catch (err) {
    // Last-resort: still return whatever survived, and make the loss explicit.
    result.skipped++;
    result.errors.push({ line: null, reason: String(err && err.message ? err.message : err) });
    appendDiagnostic("readWellForInjection", err, { file: WELL_JSONL });
  }
  return result;
}

// Make read failures visible. A Well that silently injects nothing is worse than
// one that reports why: the first is indistinguishable from "no rules exist".
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

export const GnosisLeash = async ({ project, client, $, directory }) => {
  return {
    event: async ({ event }) => {
      const type = event?.type || "";
      // SESSION lifecycle — the "hooks on open/close" the user asked about.
      if (type === "session.created") {
        appendEvent({ kind: "session.created", session: event.sessionID, project });
      } else if (type === "session.idle") {
        appendEvent({ kind: "session.idle", session: event.sessionID });
      } else if (type === "session.compacted") {
        appendEvent({ kind: "session.compacted", session: event.sessionID });
      }
    },

    // Fire before the LLM generates the compaction continuation summary.
    "experimental.session.compacting": async (input, output) => {
      const rules = readIndexRules();
      const injected = [
        "## ⬡ GNOSIS LEASH — temple context (auto-injected)",
        "- Gnosis timeline: " + TIMELINE,
        "- WanderGround INDEX (domains, weights, operating rules):",
        ...rules,
        "- Compaction: preserve WanderGround invariants (NO local 8B+ synthesis;",
        "  deep synthesis via OpenCode Zen; sovereign capture in ~/WanderGround).",
      ];

      // Human gnosis first: current session, then fallback to the most recent
      // REFLECTED pack on disk. NEVER silent — a compaction without human
      // reflection is a first-class incident, injected loudly and logged.
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
        // LOUD FAILURE: inject a warning INTO the compaction prompt so the
        // model cannot unknowingly summarize a context with no human gnosis.
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

      // The Well: inject top active corrections/insights into the compaction
      // summary so the condensed context carries the rules forward.
      const wellRes = readWellForInjection(8, WELL_INJECT_DOMAINS);
      const wellBlock = formatWellBlock(wellRecordsOrReport(wellRes, "compacting"));
      if (wellBlock) {
        injected.push(wellBlock);
      }

      // output.context is a string[]; mutate it in place. Reassigning the
      // property was a silent no-op (upstream reads its own local array).
      output.context.push(...injected);
      appendEvent({
        kind: "session.compacting",
        session: input?.sessionID,
        injected_count: injected.length,
        has_narrative: Boolean(narrative),
        narrative_source: source,
        narrative_reason: reason,
        pack_state: pack_state || "unknown",
      });
      return output;
    },

    // Append WanderGround operating rules + The Well to the system prompt of every session.
    "experimental.chat.system.transform": async (input, output) => {
      const rules = readIndexRules();
      const block =
        "## ⬡ GNOSIS LEASH — operating rules\n" +
        rules.map((l) => "  " + l).join("\n");

      // The Well: inject top active corrections/insights at session start.
      // Filter to harness/local_ai (core domains) to keep context focused.
      const wellRes = readWellForInjection(6, WELL_INJECT_DOMAINS);
      const wellBlock = formatWellBlock(wellRecordsOrReport(wellRes, "system.transform"));

      const combined = wellBlock ? block + "\n\n" + wellBlock : block;

      // output.system is a string[]. Append to element 0 IN PLACE rather than
      // push(): a push leaves the array at length 2, which upstream's collapse
      // guard (`system.length > 2`) does not fire on — it then emits two
      // {role:"system"} messages, rejected outright by OpenAI-compatible
      // providers (anomalyco/opencode#34243, unmerged upstream).
      // Reassigning output.system would be a silent no-op: upstream reads its
      // own local array, not the wrapper property.
      if (Array.isArray(output.system) && output.system.length > 0) {
        output.system[0] = (output.system[0] ?? "") + "\n\n" + combined;
      } else if (Array.isArray(output.system)) {
        output.system.push(combined);
      } else {
        appendDiagnostic(
          "system.transform.no_system_array",
          new Error("output.system was not an array — injection skipped"),
          {}
        );
      }
      return output;
    },
  };
};