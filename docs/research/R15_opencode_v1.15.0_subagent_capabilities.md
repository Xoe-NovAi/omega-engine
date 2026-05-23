# 🔱 Omega Engine — R-15 OpenCode v1.15.0 Subagent Capabilities Analysis
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R15

**AP Token**: `AP-RESEARCH-R15-v1.0.0`
**Author**: Gemma 4-31B (Sovereign Gnosis Analyst)
**Date**: 2026-05-15
**Status**: READY

---

## 📋 Executive Summary

This research analyzes the subagent capabilities introduced in OpenCode v1.15.0, with particular focus on the experimental background subagents feature released in v1.14.51. The analysis covers new features, architectural changes, permission systems, MCP integration, and performance implications.

**Key Findings**:
- v1.14.51 introduced **experimental background subagents** enabling parallel task execution
- New **TaskTool** mechanism allows primary agents to spawn subagents programmatically
- Enhanced **mode system** with `primary`/`subagent`/`all` modes for fine-grained control
- Improved **recursion guards** and permission systems for secure subagent operations
- Seamless **MCP integration** allows subagents to leverage external tools and services
- Performance optimizations enable efficient multi-agent workflows

---

## 🔢 Version Analysis

### Release Timeline
- **v1.14.51** (May 15, 2026): Introduced experimental background subagents
- **v1.15.0** (May 15, 2026): Added Effect-based core event system

### Critical Subagent Features

#### 1. Background Subagents (v1.14.51)
```
Added experimental background subagents so tasks can keep running while you continue working.
```

**Impact**: This is the most significant subagent capability, enabling:
- Parallel execution of multiple tasks
- Continuous background processing
- Non-blocking workflow management

#### 2. Session Management Improvements
- Child sessions can now be created and managed independently
- Enhanced session navigation between parent and child sessions
- Better session lifecycle management

---

## 🏗️ Subagent Architecture

### Primary vs Subagent Modes

#### Primary Agents (`mode: "primary"`)
- Main interface agents (Build, Plan, etc.)
- Handle high-level strategic planning
- Can spawn subagents via TaskTool
- Have full or restricted tool access based on permissions

#### Subagents (`mode: "subagent"`)
- Specialized assistants for specific tasks
- Can be invoked manually (@mention) or automatically
- Operate independently from primary session
- Return focused results to parent agent

#### Mode System Updates

**New `mode` field options**:
- `primary`: Main interface agent
- `subagent`: Specialized assistant
- `all`: Universal access (deprecated in favor of explicit modes)

**Mode Precedence**:
1. Primary agents handle main conversation
2. Subagents can be invoked for specialized tasks
3. System agents run automatically (Compaction, Title, Summary)

### TaskTool Mechanism

The TaskTool enables primary agents to spawn subagents programmatically:

**Key Features**:
- Programmatic subagent creation and management
- Configurable task permissions
- Recursive subagent invocation with guards
- Background execution support

**Example Configuration**:
```json
{
  "agent": {
    "orchestrator": {
      "mode": "primary",
      "permission": {
        "task": {
          "*": "deny",
          "orchestrator-*": "allow",
          "code-reviewer": "ask"
        }
      }
    }
  }
}
```

---

## 🔐 Permissions and Security

### Enhanced Permission System

**New permission keys for subagent control**:
- `task`: Control which subagents can be invoked
- `todowrite`: Manage todo list access for subagents
- `external_directory`: Control file system access patterns

**Fine-Grained Control with Glob Patterns**:
```json
{
  "permission": {
    "task": {
      "*": "deny",
      "orchestrator-*": "allow",
      "code-reviewer": "ask"
    }
  }
}
```

### Recursion Guards

**New safety mechanisms**:
- Depth limiting for subagent chains
- Permission validation before invocation
- Resource guarding to prevent overload

**Implementation**:
```typescript
// Recursion guard checks
omega-core_observability_check_recursion(entity_name, current_depth)
```

---

## 🔌 MCP Integration

### Subagent Access to MCP Tools

**MCP servers are automatically available** to subagents alongside built-in tools:

**Configuration Example**:
```json
{
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "oauth": {}
    }
  }
}
```

**Usage in Prompts**:
```
use the sentry tool to analyze error patterns
```

### Agent-Specific MCP Access

**Per-agent MCP configuration**:
```json
{
  "tools": {
    "my-mcp*": false
  },
  "agent": {
    "my-agent": {
      "tools": {
        "my-mcp*": true
      }
    }
  }
}
```

### OAuth Integration

**Automatic OAuth handling** for remote MCP servers:
- Dynamic Client Registration (RFC 7591)
- Token storage and refresh
- Manual auth flow via `opencode mcp auth`

---

## ⚡ Performance Optimizations

### Background Execution

**Key improvements**:
- Non-blocking subagent execution
- Parallel task processing
- Resource isolation between sessions

### Session Management

**Enhanced session handling**:
- Efficient child session creation
- Optimized context switching
- Reduced memory footprint for parallel sessions

### Event System

**Effect-based event system** (v1.15.0):
- Complete event delivery across sessions
- Better integration with external systems
- Improved observability

---

## 🎯 Best Practices

### Subagent Design Patterns

#### 1. Hub-and-Spoke Model
```json
{
  "agent": {
    "orchestrator": {
      "mode": "primary",
      "permission": {
        "task": {
          "code-reviewer": "allow",
          "security-auditor": "allow"
        }
      }
    },
    "code-reviewer": {
      "mode": "subagent",
      "permission": {
        "edit": "deny"
      }
    }
  }
}
```

#### 2. Permission Granularity
```json
{
  "agent": {
    "build": {
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "mymcp_search": "allow"
      }
    }
  }
}
```

#### 3. Recursive Invocation Guards
```json
{
  "agent": {
    "deep-analyzer": {
      "steps": 3,
      "permission": {
        "task": {
          "*": "deny",
          "shallow-analyzer": "allow"
        }
      }
    }
  }
}
```

### MCP Integration Patterns

#### 1. Per-Agent MCP Access
```json
{
  "tools": {
    "sensitive_mcp*": false
  },
  "agent": {
    "security-auditor": {
      "tools": {
        "sensitive_mcp*": true
      }
    }
  }
}
```

#### 2. Global MCP Management
```json
{
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "enabled": true
    }
  }
}
```

---

## 📋 Implementation Checklist

### For Builders and Implementers

#### 1. Agent Configuration
- [ ] Define clear primary vs subagent roles
- [ ] Configure appropriate permissions
- [ ] Set up task invocation guards
- [ ] Test recursion limits

#### 2. MCP Integration
- [ ] Configure required MCP servers
- [ ] Set up OAuth authentication
- [ ] Test tool availability
- [ ] Implement error handling

#### 3. Performance Testing
- [ ] Test parallel subagent execution
- [ ] Monitor resource usage
- [ ] Optimize context switching
- [ ] Validate background processing

---

## 🚨 Common Issues and Solutions

### Issue 1: Subagent Permission Denied
**Symptom**: Subagent cannot invoke tools or other subagents

**Solution**: Check task permission configuration:
```json
{
  "agent": {
    "primary": {
      "permission": {
        "task": {
          "subagent-name": "allow"
        }
      }
    }
  }
}
```

### Issue 2: Recursion Depth Exceeded
**Symptom**: Session fails with recursion error

**Solution**: Implement depth limiting:
```json
{
  "agent": {
    "recursive-agent": {
      "steps": 3
    }
  }
}
```

### Issue 3: MCP Tool Not Available
**Symptom**: MCP tools don't appear in agent's available tools

**Solution**: Verify MCP configuration and permissions:
```json
{
  "mcp": {
    "server-name": {
      "enabled": true
    }
  },
  "permission": {
    "server_name_*": "allow"
  }
}
```

---

## 📚 References and Resources

### Official Documentation
- [Agents Documentation](https://opencode.ai/docs/agents)
- [Permissions Documentation](https://opencode.ai/docs/permissions)
- [MCP Servers Documentation](https://opencode.ai/docs/mcp-servers)
- [SDK Documentation](https://opencode.ai/docs/sdk)

### Changelog References
- [v1.14.51 Changelog](https://opencode.ai/changelog#v1.14.51)
- [v1.15.0 Changelog](https://opencode.ai/changelog#v1.15.0)

### Configuration References
- [Config Schema](https://opencode.ai/config.json)
- [Agents Schema](https://opencode.ai/agents.json)

---

## 📈 Impact Assessment

### For Omega Engine Implementation

**Subagent capabilities enable**:
1. **Parallel Task Processing**: Multiple agents working simultaneously
2. **Specialized Expertise**: Domain-specific agents for focused tasks
3. **Background Processing**: Non-blocking workflow execution
4. **Modular Architecture**: Easy extension with new agent types
5. **Enhanced Productivity**: Automated task delegation and management

### Recommended Next Steps

1. **Pilot Implementation**: Create test agents with background subagent capabilities
2. **Performance Testing**: Validate parallel execution and resource usage
3. **Security Review**: Test permission systems and recursion guards
4. **MCP Integration**: Connect external services through MCP servers
5. **Documentation**: Create agent-specific guidelines and best practices

---

## 🔮 Future Outlook

Based on the v1.15.0 release pattern, expected future developments:

1. **Enhanced Task Management**: More sophisticated task orchestration
2. **Improved Recursion Control**: Better depth and resource management
3. **Advanced MCP Features**: Deeper integration with external services
4. **Performance Optimizations**: Further improvements to parallel execution
5. **Monitoring Tools**: Better observability for multi-agent systems

---

## 📝 Research Notes

- **Data Source**: OpenCode official documentation and changelog
- **Verification**: Cross-referenced multiple sources for consistency
- **Limitations**: Analysis based on public documentation; some implementation details may be subject to change
- **Next Steps**: Practical implementation and testing recommended

---

*End of Document*