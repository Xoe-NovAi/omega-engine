import type { Plugin } from "@opencode-ai/plugin";

interface SubagentSession {
  sessionId: string;
  parentSessionId: string;
  launchedBy: string;
  taskId: string;
  taskDescription: string;
  createdAt: number;
}

interface SubagentError {
  sessionId: string;
  parentSessionId: string;
  launchedBy: string;
  taskId: string;
  taskDescription: string;
  error: string;
  errorType: "session.error" | "tool.error";
  timestamp: string;
  sessionSnapshot: {
    lastThinking: string;
    lastToolCall: string;
    errorContext: string;
    messageCount: number;
    tokenUsage: { input: number; output: number };
  };
}

const subagentSessions = new Map<string, SubagentSession>();

const config = {
  logDir: "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/errors",
  retentionDays: 30,
  enableHivemindNotify: true,
  trackSubagentsOnly: true,
  captureSnapshots: true,
};

async function ensureLogDir() {
  const { $ } = await import("bun");
  await $`mkdir -p ${config.logDir}`.quiet();
}

async function appendErrorLog(error: SubagentError) {
  await ensureLogDir();
  const date = new Date().toISOString().split("T")[0];
  const filePath = `${config.logDir}/subagent-errors-${date}.jsonl`;
  const line = JSON.stringify(error) + "\n";
  await Bun.write(filePath, line, { append: true });
}

async function captureSessionSnapshot(client: any, sessionId: string) {
  if (!config.captureSnapshots) {
    return { lastThinking: "", lastToolCall: "", errorContext: "", messageCount: 0, tokenUsage: { input: 0, output: 0 } };
  }

  try {
    const session = await client.session.get({ path: { id: sessionId } });
    if (!session) return { lastThinking: "", lastToolCall: "", errorContext: "", messageCount: 0, tokenUsage: { input: 0, output: 0 } };

    const messages = session.messages || [];
    const recentMessages = messages.slice(-10);
    
    let lastThinking = "";
    let lastToolCall = "";
    let inputTokens = 0;
    let outputTokens = 0;

    for (const msg of recentMessages) {
      if (msg.role === "assistant") {
        for (const part of msg.parts || []) {
          if (part.type === "reasoning" && part.text) {
            lastThinking = part.text.slice(-2000);
          }
          if (part.type === "tool" && part.state?.input) {
            lastToolCall = JSON.stringify(part.state.input).slice(-2000);
          }
        }
      }
      inputTokens += msg.tokens?.input || 0;
      outputTokens += msg.tokens?.output || 0;
    }

    const errorContext = recentMessages
      .map(m => `${m.role}: ${m.parts?.map((p: any) => p.text || p.type).join(" ") || ""}`)
      .join("\n")
      .slice(-3000);

    return {
      lastThinking,
      lastToolCall,
      errorContext,
      messageCount: messages.length,
      tokenUsage: { input: inputTokens, output: outputTokens },
    };
  } catch (e) {
    return { lastThinking: "", lastToolCall: "", errorContext: `Snapshot failed: ${e}`, messageCount: 0, tokenUsage: { input: 0, output: 0 } };
  }
}

async function notifyParentAgent(client: any, errorRecord: SubagentError) {
  if (!config.enableHivemindNotify) return;

  try {
    await client.hivemind?.post_context?.({
      channel: "opencode",
      entity: errorRecord.launchedBy,
      model: "opencode/nemotron-3-ultra-free",
      task_current: `SUBAGENT FAILED: ${errorRecord.taskDescription}`,
      focus_chain: [errorRecord.taskId],
      decisions: [
        `Subagent session ${errorRecord.sessionId} (child of ${errorRecord.parentSessionId}) FAILED`,
        `Error type: ${errorRecord.errorType}`,
        `Error: ${errorRecord.error}`,
      ],
      continuation: `SUBAGENT STALLED - AWAITING DECISION. Subagent session preserved. Options: 1) Resume with custom prompt 2) Query subagent 3) Abandon and spawn new. Parent agent MUST decide.`,
      intent: "subagent_failed",
    });
  } catch (e) {
    console.error("[error-capture] Hivemind notify failed:", e);
  }
}

async function injectIntoParentSession(client: any, errorRecord: SubagentError) {
  const parentSessionId = errorRecord.parentSessionId;
  if (!parentSessionId || parentSessionId === "unknown") return;

  try {
    const context = `<subagent-failure>
SUBAGENT FAILED - PARENT AGENT NOTIFIED
Subagent: ${errorRecord.sessionId}
Parent: ${parentSessionId}
Task: ${errorRecord.taskDescription} (${errorRecord.taskId})
Error Type: ${errorRecord.errorType}
Error: ${errorRecord.error}
Timestamp: ${errorRecord.timestamp}

SUBAGENT SESSION PRESERVED - CAN BE RESUMED
Snapshot: ${errorRecord.sessionSnapshot.messageCount} messages, ${errorRecord.sessionSnapshot.tokenUsage.input} in / ${errorRecord.sessionSnapshot.tokenUsage.output} out tokens
Last Thinking: ${errorRecord.sessionSnapshot.lastThinking.slice(0,200)}...
Last Tool Call: ${errorRecord.sessionSnapshot.lastToolCall.slice(0,200)}...
Error Context: ${errorRecord.sessionSnapshot.errorContext.slice(0,300)}...

PARENT AGENT MUST DECIDE:
1. Resume subagent with custom prompt
2. Query subagent for more info
3. Abandon and spawn new subagent
</subagent-failure>`;

    await client.session.prompt({
      path: { id: parentSessionId },
      body: {
        parts: [{ type: "text", text: context, synthetic: true }],
        noReply: true,
      }
    });
  } catch (e) {
    console.error("[error-capture] Parent injection failed:", e);
  }
}

export const ErrorCapturePlugin: Plugin = async ({ client, $, directory }) => {
  console.log("[error-capture] Plugin initialized - SUBAGENT FAILURE DETECTION ACTIVE", { directory });

  return {
    "session.created": async ({ sessionID, parentID, agent, model }) => {
      if (!parentID) return;

      let taskId = "unknown";
      let taskDescription = "subagent";
      let launchedBy = "unknown";

      // Parent detection: use agent name from session metadata if available
      // Task registry lookup deferred to Phase 2 (M24: no broken imports)
      try {
        const sessions = await client.session.list();
        const parentSession = sessions.find((s: any) => s.id === parentID);
        if (parentSession) {
          launchedBy = parentSession.agent || "unknown";
          taskDescription = parentSession.title || "subagent task";
        }
      } catch {}

      subagentSessions.set(sessionID, {
        sessionId: sessionID,
        parentSessionId: parentID,
        launchedBy,
        taskId,
        taskDescription,
        createdAt: Date.now(),
      });
      console.log("[error-capture] Tracking subagent", { sessionID, parentID, taskId });
    },

    "session.error": async ({ sessionID, error, providerID, modelID, properties }) => {
      const sessionId = sessionID || properties?.sessionID;
      const errorMsg = error || properties?.error;
      
      if (!sessionId || !errorMsg) return;

      const subagentInfo = subagentSessions.get(sessionId);
      if (config.trackSubagentsOnly && !subagentInfo) return;

      const snapshot = await captureSessionSnapshot(client, sessionId);

      const errorRecord: SubagentError = {
        sessionId,
        parentSessionId: subagentInfo?.parentSessionId || "unknown",
        launchedBy: subagentInfo?.launchedBy || "unknown",
        taskId: subagentInfo?.taskId || "unknown",
        taskDescription: subagentInfo?.taskDescription || "unknown",
        error: typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg),
        errorType: "session.error",
        timestamp: new Date().toISOString(),
        sessionSnapshot: snapshot,
      };

      await appendErrorLog(errorRecord);
      console.error("[error-capture] SUBAGENT FAILED", { sessionId, error: errorRecord.error });

      await notifyParentAgent(client, errorRecord);
      if (subagentInfo?.parentSessionId) {
        await injectIntoParentSession(client, errorRecord);
      }
    },

    "tool.execute.after": async (input) => {
      const result = input as unknown as {
        sessionID?: string;
        tool: string;
        args: Record<string, unknown>;
        result?: unknown;
        error?: string;
        durationMs?: number;
      };

      if (!result.error) return;

      const sessionId = result.sessionID;
      if (!sessionId) return;

      const subagentInfo = subagentSessions.get(sessionId);
      if (config.trackSubagentsOnly && !subagentInfo) return;

      const snapshot = await captureSessionSnapshot(client, sessionId);

      const errorRecord: SubagentError = {
        sessionId,
        parentSessionId: subagentInfo?.parentSessionId || "unknown",
        launchedBy: subagentInfo?.launchedBy || "unknown",
        taskId: subagentInfo?.taskId || "unknown",
        taskDescription: subagentInfo?.taskDescription || "unknown",
        error: `Tool ${result.tool} failed: ${result.error}`,
        errorType: "tool.error",
        timestamp: new Date().toISOString(),
        sessionSnapshot: snapshot,
      };

      await appendErrorLog(errorRecord);
      console.error("[error-capture] SUBAGENT TOOL FAILED", { sessionId, tool: result.tool, error: result.error });

      await notifyParentAgent(client, errorRecord);
      if (subagentInfo?.parentSessionId) {
        await injectIntoParentSession(client, errorRecord);
      }
    },

    "session.deleted": async ({ sessionID }) => {
      subagentSessions.delete(sessionID);
    },
  };
};

export default ErrorCapturePlugin;