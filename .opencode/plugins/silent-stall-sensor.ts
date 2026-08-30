// SPDX-FileCopyrightText: 2026 Arcana Novai
//
// SPDX-License-Identifier: Apache-2.0

import type { Plugin } from "@opencode-ai/plugin";

// Silent-Stall Sensor — detects protocol-clean degradations that never raise
// session.error/tool.error: empty completions, empty subagent returns,
// truncated tool-call arguments, slow-dribble streams.
// Companion to error-capture.ts (which catches EXPLICIT failures only).
// Local-only observability (M8): JSONL + hourly JSON snapshot under data/coordination/errors/.

interface AssistantTrack {
  sessionID: string;
  modelID: string;
  providerID: string;
  agent?: string;
  firstTs: number;
  lastTs: number;
  outputTokens: number;
  inputTokens: number;
  textLen: number;
  classified: boolean;
}

interface StallRecord {
  kind: "SILENT_STALL_EMPTY" | "SILENT_STALL_TASK" | "TRUNCATED_ARGS" | "SLOW_DRIBBLE";
  timestamp: string;
  sessionID: string;
  modelID: string;
  providerID: string;
  detail: string;
  metrics: Record<string, number | string>;
}

const config = {
  logDir: "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/errors",
  trackAllSessions: true, // primary sessions INCLUDED (blind spot #3 fix)
  dribbleMinMs: 60_000, // assistant turn longer than this...
  dribbleMaxOutputTokens: 60, // ...with fewer output tokens than this => SLOW_DRIBBLE
  emptyMinInputTokens: 500, // guard: trivial inputs legitimately yield tiny outputs
  // --- recovery (the better-opencode-retries lineage, retargeted at silent stalls) ---
  autoRecoverPrimary: true, // inject continuation prompt on primary-session stalls
  notifyParentOnTaskStall: true, // inject recovery notice into parent on empty task results
  maxRecoveriesPerSessionPerHour: 3, // dead-provider loop guard
};

const recoveryLog = new Map<string, number[]>(); // sessionID -> recovery timestamps
const subagentSessions = new Set<string>(); // sessionIDs spawned with a parent

const tracked = new Map<string, AssistantTrack>(); // key: messageID
const hourly = new Map<string, Record<string, number>>(); // "YYYY-MM-DDTHH" -> counts

function bump(hourKey: string, kind: string) {
  const bucket = hourly.get(hourKey) ?? {};
  bucket[kind] = (bucket[kind] ?? 0) + 1;
  hourly.set(hourKey, bucket);
}

async function record(kind: StallRecord["kind"], r: Omit<StallRecord, "kind" | "timestamp">) {
  const rec: StallRecord = { kind, timestamp: new Date().toISOString(), ...r };
  try {
    const { $ } = await import("bun");
    await $`mkdir -p ${config.logDir}`.quiet();
    const day = rec.timestamp.slice(0, 10);
    const line = JSON.stringify(rec) + "\n";
    await Bun.write(`${config.logDir}/silent-stalls-${day}.jsonl`, line, { append: true });
    bump(rec.timestamp.slice(0, 13), kind);
    console.warn(`[stall-sensor] ${kind} ${rec.modelID} :: ${rec.detail.slice(0, 100)}`);
  } catch (e) {
    console.error("[stall-sensor] record failed:", e);
  }
}

async function flushHealthSnapshot() {
  try {
    const day = new Date().toISOString().slice(0, 10);
    const obj: Record<string, unknown> = { updated: new Date().toISOString(), hourly: Object.fromEntries(hourly) };
    await Bun.write(`${config.logDir}/provider-health-${day}.json`, JSON.stringify(obj, null, 2));
  } catch {}
}

function classify(t: AssistantTrack): StallRecord["kind"] | null {
  if (t.outputTokens === 0 && t.textLen === 0 && t.inputTokens >= config.emptyMinInputTokens)
    return "SILENT_STALL_EMPTY";
  const dur = t.lastTs - t.firstTs;
  if (dur >= config.dribbleMinMs && t.outputTokens <= config.dribbleMaxOutputTokens) return "SLOW_DRIBBLE";
  return null;
}

// --- recovery (better-opencode-retries lineage) ---
function allowRecovery(sessionID: string): boolean {
  const now = Date.now();
  const stamps = (recoveryLog.get(sessionID) ?? []).filter((ts) => now - ts < 3_600_000);
  if (stamps.length >= config.maxRecoveriesPerSessionPerHour) return false;
  stamps.push(now);
  recoveryLog.set(sessionID, stamps);
  return true;
}

const CONTINUATION_PROMPT =
  "[stall-sensor] Your previous response was lost to a provider stream failure (silent stall — clean completion, no content). Your context is fully intact. Continue your current task from where it stands.";

async function injectPrompt(client: any, sessionID: string, text: string, expectReply: boolean) {
  try {
    await client.session.prompt({
      path: { id: sessionID },
      body: {
        parts: [{ type: "text", text, synthetic: true }],
        noReply: !expectReply,
      },
    });
    await appendEventLog({
      kind: "RECOVERY_ISSUED",
      timestamp: new Date().toISOString(),
      sessionID,
      detail: expectReply ? "continuation prompt injected" : "parent notice injected",
      metrics: {},
    });
  } catch (e) {
    console.error("[stall-sensor] recovery injection failed:", e);
  }
}

async function recoverPrimary(client: any, sessionID: string) {
  if (!config.autoRecoverPrimary) return;
  if (!allowRecovery(sessionID)) {
    console.warn("[stall-sensor] recovery rate-limited for", sessionID.slice(0, 12));
    return;
  }
  // "." in honor of the original better-opencode-retries ritual; descriptive for silent stalls
  await injectPrompt(client, sessionID, CONTINUATION_PROMPT, true);
}

async function notifyParentToResume(client: any, parentSessionID: string, childSessionID: string) {
  if (!config.notifyParentOnTaskStall) return;
  if (!allowRecovery(parentSessionID)) return;
  const notice = `<silent-stall>
SUBAGENT RETURNED EMPTY (provider silent stall — no error was raised).
Child session: ${childSessionID}
Its context is PRESERVED in the DB — resume it via task(task_id=<child-session-id>) with a short "finish the job" prompt rather than respawning fresh.
</silent-stall>`;
  await injectPrompt(client, parentSessionID, notice, false);
}

async function appendEventLog(evt: Record<string, unknown>) {
  try {
    const day = new Date().toISOString().slice(0, 10);
    const line = JSON.stringify(evt) + "\n";
    await Bun.write(`${config.logDir}/silent-stalls-${day}.jsonl`, line, { append: true });
  } catch {}
}

export const SilentStallSensorPlugin: Plugin = async ({ client }) => {
  console.log("[stall-sensor] initialized — silent-degradation detection ACTIVE");

  // periodic health snapshot
  const snapTimer = setInterval(flushHealthSnapshot, 10 * 60 * 1000);
  // avoid keeping process alive purely for the timer
  (snapTimer as any)?.unref?.();

  return {
    event: async ({ event }) => {
      try {
        if (!event) return;
        if (event.type === "session.created") {
          const info = (event.properties as any)?.info;
          if (info?.parentID && info?.id) subagentSessions.add(info.id);
          return;
        }
        if (event.type !== "message.updated") return;
        const info = (event.properties as any)?.info;
        if (!info || info.role !== "assistant") return;

        const msgID: string = info.id;
        if (!msgID) return;

        let textLen = 0;
        for (const p of info.parts ?? []) {
          if (typeof p?.text === "string") textLen += p.text.length;
        }

        const prev = tracked.get(msgID);
        const now = Date.now();
        const t: AssistantTrack = {
          sessionID: (event.properties as any)?.sessionID ?? info.sessionID ?? "unknown",
          modelID: info.modelID ?? prev?.modelID ?? "unknown",
          providerID: info.providerID ?? prev?.providerID ?? "unknown",
          agent: info.agent ?? prev?.agent,
          firstTs: prev?.firstTs ?? now,
          lastTs: now,
          outputTokens: info.tokens?.output ?? prev?.outputTokens ?? 0,
          inputTokens: info.tokens?.input ?? prev?.inputTokens ?? 0,
          textLen: Math.max(textLen, prev?.textLen ?? 0),
          classified: false,
        };
        tracked.set(msgID, t);

        // Flush classification when a NEW user message lands in the same session
        // (i.e., the assistant turn is definitively over).
        if ((event.properties as any)?.synthetic !== true) {
          // cheap heuristic: classify previous assistant msgs of this session not yet classified
          for (const [id, tr] of tracked) {
            if (tr.classified || tr.sessionID !== t.sessionID) continue;
            if (id === msgID) continue;
            const kind = classify(tr);
            tr.classified = true;
            if (kind) {
              await record(kind, {
                sessionID: tr.sessionID,
                modelID: tr.modelID,
                providerID: tr.providerID,
                detail: `msg=${id} out=${tr.outputTokens}tok text=${tr.textLen}ch in=${tr.inputTokens}tok dur=${Math.round((tr.lastTs - tr.firstTs) / 1000)}s`,
                metrics: {
                  outputTokens: tr.outputTokens,
                  inputTokens: tr.inputTokens,
                  textLen: tr.textLen,
                  durationMs: tr.lastTs - tr.firstTs,
                },
              });
              // Recovery: primary-session empty completions get the continuation kick
              // (the better-opencode-retries lineage — context survives, generation died).
              if (kind === "SILENT_STALL_EMPTY" && !subagentSessions.has(tr.sessionID)) {
                await recoverPrimary(client, tr.sessionID);
              }
            }
          }
          if (tracked.size > 500) {
            for (const [id, tr] of tracked) if (tr.classified) tracked.delete(id);
          }
        }
      } catch (e) {
        console.error("[stall-sensor] event handler failed:", e);
      }
    },

    "tool.execute.after": async (input) => {
      try {
        const result = input as unknown as {
          sessionID?: string;
          tool: string;
          args?: Record<string, unknown>;
          result?: unknown;
          error?: string;
          durationMs?: number;
        };

        // TRUNCATED_ARGS: malformed tool-call JSON = stream died mid-invoke
        if (result.error && /SchemaError|Missing key|Unexpected end|Failed to parse|invalid argument/i.test(result.error)) {
          await record("TRUNCATED_ARGS", {
            sessionID: result.sessionID ?? "unknown",
            modelID: "unknown-at-tool-layer",
            providerID: "unknown-at-tool-layer",
            detail: `tool=${result.tool} err=${result.error}`,
            metrics: { durationMs: result.durationMs ?? 0 },
          });
          // The invoke never executed — prompt the model to re-issue it.
          if (result.sessionID && !subagentSessions.has(result.sessionID)) {
            await recoverPrimary(client, result.sessionID);
          }
          return;
        }

        // SILENT_STALL_TASK: subagent completed cleanly but produced nothing
        if (result.tool === "task" && !result.error) {
          const out =
            typeof result.result === "string"
              ? result.result
              : result.result == null
                ? ""
                : JSON.stringify(result.result);
          if (out.trim().length === 0) {
            await record("SILENT_STALL_TASK", {
              sessionID: result.sessionID ?? "unknown",
              modelID: "unknown-at-tool-layer",
              providerID: "unknown-at-tool-layer",
              detail: `task returned empty result after ${result.durationMs ?? 0}ms`,
              metrics: { durationMs: result.durationMs ?? 0 },
            });
            const child = out.match(/ses_[A-Za-z0-9]+/)?.[0];
            if (child && result.sessionID) {
              await notifyParentToResume(client, result.sessionID, child);
            }
          }
        }
      } catch (e) {
        console.error("[stall-sensor] tool handler failed:", e);
      }
    },
  };
};

export default SilentStallSensorPlugin;
