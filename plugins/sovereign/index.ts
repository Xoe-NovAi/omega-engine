/**
 * 🔱 Omega Sovereign Plugin
 * 
 * This plugin integrates the OpenCode runtime with the Omega Engine's sovereign brain (omega-hub).
 * It enforces identity injection, boundary guarding, and gnosis filtering.
 */

import { PluginInput } from '@opencode/types'; // Assumption based on arch map

const OMEGA_HUB_URL = 'http://127.0.0.1:8016';

export async function OmegaSovereignPlugin(input: PluginInput) {
  console.log('[OmegaSovereign] Initializing Sovereign Interface...');

  return {
    /**
     * 1. Identity Injection
     * Injects the active Omega Entity's identity and soul-print into the system prompt.
     */
    'experimental.chat.system.transform': async ({ sessionID, model }, { system }) => {
      try {
        const response = await fetch(`${OMEGA_HUB_URL}/entity/current`);
        const entity = await response.json();
        
        if (entity && entity.personality) {
          const sovereignPrompt = `\n\n[SOVEREIGN IDENTITY]\nEntity: ${entity.name}\nArchetype: ${entity.archetype}\nPersonality: ${entity.personality}\nSoul-Print: ${entity.soul_print || 'Active'}\n`;
          system.push(sovereignPrompt);
        }
      } catch (e) {
        console.error('[OmegaSovereign] Failed to fetch identity from omega-hub:', e);
      }
      return { system };
    },

    /**
     * 2. Boundary Guard
     * Prevents tool execution that violates the current session's sovereign boundaries.
     */
    'tool.execute.before': async ({ tool, sessionID, callID }, { args }) => {
      try {
        const response = await fetch(`${OMEGA_HUB_URL}/soul/check-boundary`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tool, sessionID, args })
        });
        const result = await response.json();

        if (result.action === 'BLOCK') {
          throw new Error(`Sovereign Boundary Violation: ${result.reason || 'This action is forbidden by the current entity lens.'}`);
        }
      } catch (e) {
        if (e.message.includes('Sovereign Boundary Violation')) throw e;
        console.error('[OmegaSovereign] Boundary check failed, defaulting to ALLOW:', e);
      }
      return { args };
    },

    /**
     * 3. Gnosis Filter
     * Redacts or transforms tool output to align with the entity's perspective.
     */
    'tool.execute.after': async ({ tool, sessionID, callID, args }, output) => {
      try {
        const response = await fetch(`${OMEGA_HUB_URL}/soul/filter-output`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tool, sessionID, output })
        });
        const result = await response.json();

        if (result.filtered_output) {
          return result.filtered_output;
        }
      } catch (e) {
        console.error('[OmegaSovereign] Gnosis filter failed, returning raw output:', e);
      }
      return output;
    },
  };
}
