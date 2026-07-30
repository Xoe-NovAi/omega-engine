import type { Plugin } from "@opencode-ai/plugin";

interface ToolErrorLog {
  timestamp: string;
  sessionId: string;
  tool: string;
  error: string;
  input: Record<string, unknown>;
  durationMs: number;
}

interface SessionErrorLog {
  timestamp: string;
  sessionId: string;
  error: string;
  providerId?: string;
  modelId?: string;
}

interface RetryState {
  lastError: string;
  lastErrorTime: number;
  retryCount: number;
  originalSessionId: string;
}

const ERROR_LOG_DIR = "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/errors";
const RETRY_STATE_FILE = `${ERROR_LOG_DIR}/retry-state.json`;

async function ensureErrorLogDir() {
  const { $ } = await import("bun");
  await $`mkdir -p ${ERROR_LOG_DIR}`.quiet();
}

async function appendToolError(log: ToolErrorLog) {
  await ensureErrorLogDir();
  const date = new Date().toISOString().split("T")[0];
  const filePath = `${ERROR_LOG_DIR}/tool-errors-${date}.jsonl`;
  const line = JSON.stringify(log) + "\n";
  await Bun.write(filePath, line, { append: true });
}

async function appendSessionError(log: SessionErrorLog) {
  await ensureErrorLogDir();
  const date = new Date().toISOString().split("T")[0];
  const filePath = `${ERROR_LOG_DIR}/session-errors-${date}.jsonl`;
  const line = JSON.stringify(log) + "\n";
  await Bun.write(filePath, line, { append: true });
}

async function logToConsole(level: "info" | "warn" | "error", message: string, extra?: Record<string, unknown>) {
  const timestamp = new Date().toISOString();
  const prefix = level.toUpperCase().padEnd(5);
  console.log(`${timestamp} ${prefix} [error-capture] ${message}`, extra ? JSON.stringify(extra) : "");
}

async function loadRetryState(): Promise<RetryState | null> {
  try {
    const file = Bun.file(RETRY_STATE_FILE);
    if (await file.exists()) {
      return await file.json();
    }
  } catch {}
  return null;
}

async function saveRetryState(state: RetryState | null) {
  await ensureErrorLogDir();
  if (state) {
    await Bun.write(RETRY_STATE_FILE, JSON.stringify(state, null, 2));
  } else {
    try { await Bun.$`rm -f ${RETRY_STATE_FILE}`.quiet(); } catch {}
  }
}

async function checkAndInjectRetryContext(client: any, sessionId: string) {
  const state = await loadRetryState();
  if (!state) return;

  const timeSinceError = Date.now() - state.lastErrorTime;
  // If error was recent (< 5 min) and we haven't retried too many times
  if (timeSinceError < 300000 && state.retryCount < 5) {
    // Inject context about the retry
    await client.session.prompt({
      path: { id: sessionId },
      body: {
        noReply: true,
        parts: [{
          type: "text",
          text: `<retry-context>
This session is a RETRY (attempt ${state.retryCount + 1}) after a previous failure.
Previous session: ${state.originalSessionId}
Previous error: ${state.lastError}
Time since error: ${Math.round(timeSinceError / 1000)}s
The retry plugin automatically restarted the stream. Continue your task normally.
</retry-context>`
        }]
      }
    }).catch(() => {}); // Ignore errors

    // Update retry state
    state.retryCount++;
    await saveRetryState(state);
    await logToConsole("info", `Injected retry context`, { sessionId, retryCount: state.retryCount });
  } else if (timeSinceError >= 300000) {
    // Error is stale, clear state
    await saveRetryState(null);
  }
}

export const ErrorCapturePlugin: Plugin = async ({ client, $, directory }) => {
  await logToConsole("info", "ErrorCapturePlugin initialized", { directory });

  return {
    "tool.execute.after": async (input) => {
      const sessionId = input.sessionID || "unknown";
      const result = input as unknown as {
        tool: string;
        args: Record<string, unknown>;
        result?: unknown;
        error?: string;
        durationMs?: number;
      };

      if (result.error) {
        const errorLog: ToolErrorLog = {
          timestamp: new Date().toISOString(),
          sessionId,
          tool: result.tool,
          error: result.error,
          input: result.args,
          durationMs: result.durationMs || 0,
        };

        await appendToolError(errorLog);
        await logToConsole("error", `TOOL ERROR: ${result.tool}`, {
          sessionId,
          error: result.error,
          input: result.args,
        });
      }
    },

    event: async ({ event }) => {
      const sessionId = (event as any).sessionID || (event as any).session_id || (event as any).properties?.sessionID;

      if (event.type === "session.error") {
        const sessionError = event as unknown as {
          type: "session.error";
          sessionID?: string;
          error?: string;
          providerID?: string;
          modelID?: string;
          properties?: {
            error?: string;
            providerID?: string;
            modelID?: string;
          };
        };

        const errorMessage = sessionError.error || sessionError.properties?.error || "Unknown session error";
        const providerId = sessionError.providerID || sessionError.properties?.providerID;
        const modelId = sessionError.modelID || sessionError.properties?.modelID;

        const errorLog: SessionErrorLog = {
          timestamp: new Date().toISOString(),
          sessionId: sessionId || "unknown",
          error: errorMessage,
          providerId,
          modelId,
        };

        await appendSessionError(errorLog);
        await logToConsole("error", `SESSION ERROR: ${errorMessage}`, {
          sessionId,
          providerId,
          modelId,
        });

        // Save retry state for next session
        const retryState: RetryState = {
          lastError: errorMessage,
          lastErrorTime: Date.now(),
          retryCount: 0,
          originalSessionId: sessionId || "unknown",
        };
        await saveRetryState(retryState);
      }

      if (event.type === "session.created") {
        await logToConsole("info", "Session created", { sessionId });
        // Check if this is a retry and inject context
        await checkAndInjectRetryContext(client, sessionId || "");
      }
    },
  };
};