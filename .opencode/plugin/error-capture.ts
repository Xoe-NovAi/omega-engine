import type { Plugin } from "@opencode-ai/plugin";

interface SubagentSession {
  sessionId: string;
  parentSessionId: string;
  launchedBy: string;        // launching agent entity (e.g., "kali")
  taskId: string;            // from task_registry
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

interface ErrorCaptureConfig {
  logDir: string;
  retentionDays: number;
  enableHivemindNotify: boolean;
  trackSubagentsOnly: boolean;
  captureSnapshots: boolean;
}

const DEFAULT_CONFIG: ErrorCaptureConfig = {
  logDir: "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/errors",
  retentionDays: 30,
  enableHivemindNotify: true,
  trackSubagentsOnly: true,
  captureSnapshots: true,
};

const subagentSessions = new Map<string, SubagentSession>();
const config: ErrorCaptureConfig = { ...DEFAULT_CONFIG };

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

    // Get recent messages for context
    const messages = session.messages || [];
    const recentMessages = messages.slice(-10);
    
    let lastThinking = "";
    let lastToolCall = "";
    let errorContext = "";
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

    // Build error context from recent messages
    errorContext = recentMessages
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

async function notifyHivemind(client: any, error: SubagentError) {
  if (!config.enableHivemindNotify) return;

  try {
    await client.hivemind?.post_context?.({
      channel: "opencode",
      entity: error.launchedBy,
      model: "opencode/nemotron-3-ultra-free",
      task_current: `Subagent error: ${error.taskDescription}`,
      focus_chain: [error.taskId],
      decisions: [
        `Subagent session ${error.sessionId} (child of ${error.parentSessionId}) encountered error`,
        `Error type: ${error.errorType}`,
        `Error: ${error.error}`,
      ],
      continuation: `AWAITING DECISION: Resume with custom prompt? Query subagent? Abandon and spawn new? Subagent is PAUSED - full context preserved.`,
      intent: "subagent_error",
    });
  } catch (e) {
    console.error("[error-capture] Hivemind notify failed:", e);
  }
}

async function loadTaskRegistry(taskId: string) {
  try {
    const task = await import("omega-hub_task_registry_get").then(m => m.omega-hub_task_registry_get({ task_id: taskId }));
    return task;
  } catch {
    return null;
  }
}

export const ErrorCapturePlugin: Plugin = async ({ client, $, directory }) => {
  console.log("[error-capture] Plugin initialized", { directory });

  return {
    // Track subagent session creation
    "session.created": async ({ sessionID, parentID, agent, model }) => {
      if (!parentID) return; // Main session, not a subagent

      // Try to get task info from Hivemind task registry
      let taskId = "unknown";
      let taskDescription = "unknown";
      let launchedBy = "unknown";

      try {
        // Check if there's a recent task registry entry for this parent session
        const tasks = await import("omega-hub_task_registry_query").then(m => 
          m.omega-hub_task_registry_query({ 
            channel: "opencode", 
            status: "active",
            limit: 10 
          })
        );
        
        // Find task that matches this parent session
        for (const task of tasks.tasks || []) {
          if (task.session_id === parentID || task.context?.includes(parentID)) {
            taskId = task.task_id;
            taskDescription = task.description;
            launchedBy = task.entity || task.launched_by || "unknown";
            break;
          }
        }
      } catch {}

      const subagentInfo: SubagentSession = {
        sessionId: sessionID,
        parentSessionId: parentID,
        launchedBy,
        taskId,
        taskDescription,
        createdAt: Date.now(),
      };

      subagentSessions.set(sessionID, subagentInfo);
      console.log("[error-capture] Tracked subagent session", subagentInfo);
    },

    // Capture session-level errors (streaming failures, etc.)
    "session.error": async ({ sessionID, error, providerID, modelID, properties }) => {
      const sessionId = sessionID || properties?.sessionID;
      const providerId = providerID || properties?.providerID;
      const errorMsg = error || properties?.error;
      
      if (!sessionId || !errorMsg) return;

      const subagentInfo = subagentSessions.get(sessionId);
      if (config.trackSubagentsOnly && !subagentInfo) return; // Only track subagents

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
      console.error("[error-capture] Subagent session error", { sessionId, error: errorRecord.error });

      // Notify launching agent + user via Hivemind
      await notifyHivemind(client, errorRecord);
    },

    // Capture tool execution errors
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
      console.error("[error-capture] Subagent tool error", { sessionId, tool: result.tool, error: result.error });

      await notifyHivemind(client, errorRecord);
    },

    // Cleanup on session end
    "session.deleted": async ({ sessionID }) => {
      subagentSessions.delete(sessionID);
    },
  };
};

export default ErrorCapturePlugin;