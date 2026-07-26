// 🔱 Omega Engine — Soul Distillation Plugin (C-0.5)
// AP: AP-C05-SOUL-DISTILLER-PLUGIN-v1.0.0
//
// Listens for session.compacted and session.idle events and runs the
// soul distillation pipeline + Codex refresh via the Python hook script.
//
// Architecture: OpenCode Plugin API (NOT opencode.json hooks key)
// Reference: https://opencode.ai/docs/plugins/
//
// This replaces the broken .opencode/hooks/session_end.py + hooks config approach.
// The hooks key was never valid in OpenCode's schema (additionalProperties: false).

export const SoulDistillerPlugin = async ({ project, client, $, directory, worktree }) => {
  const PROJECT_ROOT = directory || process.cwd();
  const HOOK_SCRIPT = `${PROJECT_ROOT}/.opencode/hooks/session_end.py`;
  const PYTHON = `${PROJECT_ROOT}/.venv/bin/python`;

  return {
    event: async ({ event }) => {
      // Trigger ONLY on session.compacted — context is being lost, distill before it's gone.
      // session.idle fires every turn (too frequent). session.compacted is the right hook.
      if (event.type !== "session.compacted") {
        return;
      }

      try {
        await $`${PYTHON} ${HOOK_SCRIPT}`;
        if (client?.app?.log) {
          await client.app.log({
            body: {
              service: "soul-distiller",
              level: "info",
              message: "Soul distillation completed after compaction",
            },
          });
        }
      } catch (err) {
        // Best-effort — never crash OpenCode on distillation failure
        if (client?.app?.log) {
          await client.app.log({
            body: {
              service: "soul-distiller",
              level: "warn",
              message: `Soul distillation failed: ${err.message}`,
            },
          });
        }
      }
    },
  };
};
