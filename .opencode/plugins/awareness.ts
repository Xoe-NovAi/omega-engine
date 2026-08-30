import type { Plugin } from "@opencode-ai/plugin";

interface AwarenessEvent {
  type: string;
  timestamp: number;
  sessionId?: string;
  parentSessionId?: string;
  error?: string;
  providerId?: string;
  modelId?: string;
  agent?: string;
  summary: string;
}

const eventBuffer: AwarenessEvent[] = [];
const MAX_BUFFER = 200;
const CRITICAL_EVENT_TYPES = new Set([
  "session.error",
  "message.updated",
  "session.compacted",
  "session.created",
  "session.deleted",
]);

function addEvent(event: AwarenessEvent) {
  eventBuffer.push(event);
  if (eventBuffer.length > MAX_BUFFER) eventBuffer.shift();
}

function getRecentEvents(count: number = 20): AwarenessEvent[] {
  return eventBuffer.slice(-count);
}

function formatAwarenessContext(event: AwarenessEvent, recent: AwarenessEvent[]): string {
  const ts = new Date(event.timestamp).toISOString();
  let context = `<system-awareness timestamp="${ts}">\n`;
  
  switch (event.type) {
    case "session.error":
      context += `🔴 STREAMING ERROR DETECTED\n`;
      context += `Session: ${event.sessionId}\n`;
      context += `Provider: ${event.providerId}\n`;
      context += `Model: ${event.modelId}\n`;
      context += `Error: ${event.error}\n`;
      context += `⚠️ If you next see a "." prompt, YOU WERE RESTARTED by retry plugin.\n`;
      context += `Your context was preserved. Continue seamlessly.\n`;
      break;
    case "message.updated":
      context += `🔴 ASSISTANT MESSAGE ERROR\n`;
      context += `Session: ${event.sessionId}\n`;
      context += `Error: ${event.error}\n`;
      break;
    case "session.compacted":
      context += `🟡 SESSION COMPACTED - Context compressed\n`;
      context += `Previous turns summarized. Full history in DB.\n`;
      break;
    case "session.created":
      if (event.parentSessionId) {
        context += `🟢 SUBAGENT SPAWNED\n`;
        context += `Child: ${event.sessionId}\n`;
        context += `Parent: ${event.parentSessionId}\n`;
        context += `Agent: ${event.agent}\n`;
      } else {
        context += `🟢 NEW MAIN SESSION\n`;
        context += `Session: ${event.sessionId}\n`;
        context += `Agent: ${event.agent}\n`;
      }
      break;
    case "session.deleted":
      context += `🔴 SESSION ENDED\n`;
      context += `Session: ${event.sessionId}\n`;
      break;
  }
  
  context += `\nRecent event stream (last ${recent.length}):\n`;
  for (const e of recent) {
    const t = new Date(e.timestamp).toISOString().split("T")[1].split(".")[0];
    context += `  [${t}] ${e.type}${e.sessionId ? ` ${e.sessionId.slice(0,8)}` : ""}${e.error ? ` → ${e.error.slice(0,60)}` : ""}\n`;
  }
  
  context += `</system-awareness>`;
  return context;
}

async function injectAwareness(client: any, sessionId: string, context: string) {
  try {
    await client.session.prompt({
      path: { id: sessionId },
      body: {
        parts: [{ type: "text", text: context, synthetic: true }],
        noReply: true,
      }
    });
  } catch (e) {
    console.error("[awareness] Injection failed:", e);
  }
}

async function getMySessionId(client: any): Promise<string | null> {
  try {
    const sessions = await client.session.list();
    // Find the most recent kali session that's not archived
    const mySessions = sessions.filter((s: any) => s.agent === "kali" && !s.archived);
    if (mySessions.length > 0) {
      return mySessions[0].id;
    }
    return sessions[0]?.id || null;
  } catch {
    return null;
  }
}

export const AwarenessPlugin: Plugin = async ({ client, $, directory }) => {
  console.log("[awareness] Plugin initialized", { directory });

  return {
    // Capture ALL events for awareness buffer
    event: async ({ event }) => {
      if (!event) return;
      
      const sessionId = event.sessionID || event.properties?.sessionID || event.properties?.info?.id;
      const parentSessionId = event.properties?.info?.parentID;
      const providerId = event.providerID || event.properties?.providerID || event.properties?.info?.providerID;
      const modelId = event.modelID || event.properties?.modelID || event.properties?.info?.modelID;
      const agent = event.properties?.info?.agent;
      
      let error: string | undefined;
      let summary = event.type;
      
      if (event.type === "session.error") {
        error = event.error || event.properties?.error;
        summary = `session.error: ${error?.slice(0,80)}`;
      } else if (event.type === "message.updated") {
        const info = event.properties?.info;
        if (info?.error) {
          error = typeof info.error === "string" ? info.error : JSON.stringify(info.error);
          summary = `message.error: ${error?.slice(0,80)}`;
        }
      } else if (event.type === "session.compacted") {
        summary = "session.compacted";
      } else if (event.type === "session.created") {
        summary = parentSessionId ? `subagent.created (parent: ${parentSessionId?.slice(0,8)})` : "session.created";
      } else if (event.type === "session.deleted") {
        summary = "session.deleted";
      }
      
      const awarenessEvent: AwarenessEvent = {
        type: event.type,
        timestamp: Date.now(),
        sessionId,
        parentSessionId,
        error,
        providerId,
        modelId,
        agent,
        summary,
      };
      
      addEvent(awarenessEvent);
      
      // Inject awareness for critical events into the launching agent's context
      if (CRITICAL_EVENT_TYPES.has(event.type) && sessionId) {
        const mySessionId = await getMySessionId(client);
        if (mySessionId && mySessionId !== sessionId) {
          const recent = getRecentEvents(15);
          const context = formatAwarenessContext(awarenessEvent, recent);
          await injectAwareness(client, mySessionId, context);
        }
      }
    },
    
    // Also track tool errors
    "tool.execute.after": async (input) => {
      const result = input as unknown as {
        sessionID?: string;
        tool: string;
        args: Record<string, unknown>;
        result?: unknown;
        error?: string;
        durationMs?: number;
      };
      
      if (result.error) {
        const awarenessEvent: AwarenessEvent = {
          type: "tool.error",
          timestamp: Date.now(),
          sessionId: result.sessionID,
          error: `Tool ${result.tool} failed: ${result.error}`,
          summary: `tool.error: ${result.tool}`,
        };
        addEvent(awarenessEvent);
        
        const mySessionId = await getMySessionId(client);
        if (mySessionId && mySessionId !== result.sessionID) {
          const recent = getRecentEvents(15);
          const context = formatAwarenessContext(awarenessEvent, recent);
          await injectAwareness(client, mySessionId, context);
        }
      }
    },
  };
};

export default AwarenessPlugin;