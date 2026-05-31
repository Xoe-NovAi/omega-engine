/**
 * Jem 2.0 — OpenCode Plugin
 * 
 * Transforms OpenCode into Jem's research persona.
 * Model-agnostic: uses whatever model is currently selected in OpenCode.
 */

import type { PluginInput, Hooks } from 'opencode';

export async function OmegaJemPlugin(input: PluginInput): Promise<Hooks> {
  return {
    'experimental.chat.system.transform': {
      handler: async (context: any) => {
        // Inject Jem's research system prompt from spec
        const jemPrompt = `You are **Jem**, the Lead Research Persona. Your mission is to produce rigorously sourced, citation‑rich answers. Verify facts across at least two independent sources, use the MCP search tools, and respect the compaction policy. When you need external data, call one of the approved research MCPs. Always cite the source in markdown format.`;
        return {
          system: jemPrompt,
        };
      },
    },

    'chat.params': {
      handler: async (context: any) => {
        // Set research-appropriate parameters per spec (T=0.7)
        return {
          temperature: 0.7,
          max_tokens: 4096,
        };
      },
    },

    'tool.execute.before': {
      handler: async (context: any) => {
        // Whitelist research-focused MCP tools (Removed Brave, added SearXNG)
        const allowedTools = [
          'exa_web_search_exa',
          'tavily_tavily_search',
          'tavily_tavily_extract',
          'firecrawl_mcp',
          'mcp-jina',
          'searxng_search',
          'filesystem',
        ];
        
        const toolName = context.tool?.name || '';
        if (!allowedTools.some(t => toolName.includes(t))) {
          return {
            skip: true,
            message: `Tool '${toolName}' is not in the research whitelist. Use approved MCPs: Exa, Tavily, Firecrawl, Jina, SearXNG.`,
          };
        }
        
        return {};
      },
    },

    'tool.execute.after': {
      handler: async (context: any) => {
        // Wrap results with citation format as per spec
        const result = context.result;
        const citation = `\n\n---\n**Source**: ${context.tool?.name || 'unknown'}\n**Timestamp**: ${new Date().toISOString()}`;

        if (typeof result === 'string') {
          return result + citation;
        }
        
        if (result && typeof result === 'object' && result.content) {
          result.content += citation;
        }
        
        return result;
      },
    },

    'command.intercept': {
      handler: async (context: any) => {
        const command = context.command?.toLowerCase() || '';
        
        if (command === '/mode jem' || command === '/jem') {
          return {
            activate: true,
            response: '🔬 Jem 2.0 activated. Research mode engaged. Use Exa, Tavily, SearXNG, or other research MCPs for deep-dive queries.',
          };
        }
        
        return {};
      },
    },
  };
}

export default OmegaJemPlugin;
