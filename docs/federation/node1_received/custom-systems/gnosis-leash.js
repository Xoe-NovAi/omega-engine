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
const STATE_DIR = path.join(HOME, ".config/opencode", "plugins", "state");
const TIMELINE = path.join(STATE_DIR, "gnosis-events.jsonl");
const ERRLOG = path.join(STATE_DIR, "gnosis-errors.jsonl");
const INDEX_MD = path.join(HOME, "WanderGround", "INDEX.md");
const WELL_JSONL = path.join(
  HOME,
  "Documents/Projects/omega-engine-alpha/gnosis/well/well.jsonl"
);
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

// Authoritative lifecycle state: read the pack's manifest reflection_status.
// "captured" = ritual ran, still on the leash, narrative TODO by intent.
// "reflected" = skill ran, narrative ingested.
// Missing manifest / status defaults to captured (be conservative; content check
// still applies downstream as a second gate).
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
        if (isPopulatedNarrative(content)) {
          return {
            narrative: content.trim(),
            source: "current",
            reason: status === "reflected"
              ? `current_session ${currentSession} is REFLECTED`
              : `current_session ${currentSession} status=${status} but narrative is populated (content gate)`,
            pack_state: status,
          };
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

// Read top-N active Well records for injection (session start + compaction).
// Ranks by recency; filters to relevant domains if provided.
function readWellForInjection(limit = 8, domains = null) {
  try {
    if (!fs.existsSync(WELL_JSONL)) return [];
    const lines = fs.readFileSync(WELL_JSONL, "utf8").trim().split("\n").filter(Boolean);
    const active = [];
    for (const line of lines) {
      try {
        const rec = JSON.parse(line);
        if (rec.status !== "active") continue;
        if (domains && !domains.includes(rec.domain)) continue;
        active.push(rec);
      } catch {
        // skip malformed
      }
    }
    active.sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime());
    return active.slice(0, limit).map((r) => ({
      rule: r.rule,
      domain: r.domain,
      kind: r.kind,
      tags: r.tags ? r.tags.split(",").map((t) => t.trim()) : [],
      id: r.record_id.slice(0, 8),
      source_pack: r.source_pack,
    }));
  } catch (err) {
    appendDiagnostic("readWellForInjection", err, { file: WELL_JSONL });
    return [];
  }
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
      const wellRecs = readWellForInjection(8, ["harness", "local_ai"]);
      const wellBlock = formatWellBlock(wellRecs);
      if (wellBlock) {
        injected.push(wellBlock);
      }

      if (Array.isArray(output.context)) {
        output.context.push(...injected);
      } else {
        output.context = (output.context || []).concat(injected);
      }
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
      const wellRecs = readWellForInjection(6, ["harness", "local_ai"]);
      const wellBlock = formatWellBlock(wellRecs);

      const combined = wellBlock
        ? block + "\n\n" + wellBlock
        : block;

      if (Array.isArray(output.system)) {
        output.system.push(combined);
      } else {
        output.system = (output.system || "") + "\n\n" + combined;
      }
      return output;
    },
  };
};