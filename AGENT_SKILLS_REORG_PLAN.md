# Legion Agent & Skills Reorganization Plan

## Current Issues
1. **Structure inconsistency**: `core/` should be at root level, not `legion/core/`
2. **Duplicate agent files**: Multiple `echo.py` and `therapist.py` files
3. **Skills underutilization**: Only ResearcherAgent uses skills properly
4. **Mixed responsibilities**: Infrastructure code mixed with actual skills

## Proposed Structure

### Core Utilities (Move to Root Level)
```
core/
├── utils/
│   ├── network.py          # HTTP clients, retries
│   ├── indexing.py         # Vector operations, embeddings  
│   ├── chroma_client.py    # Database client
│   └── logging.py          # Logging utilities
├── db/
│   ├── schema.sql          # Database schema
│   └── migrations/         # Migration scripts
└── web_api.js              # Web API utilities
```

### Skills Organization (Domain-Based)
```
skills/
├── research/
│   ├── search.py           # Web & vector search
│   ├── summarize.py        # Text summarization
│   └── fact_check.py       # Fact verification
├── communication/
│   ├── discord_utils.py    # Discord helpers
│   ├── message_format.py   # Message formatting
│   └── notification.py     # Alert management
├── analysis/
│   ├── metrics.py          # System metrics
│   ├── health_check.py     # Health monitoring
│   └── performance.py      # Performance analysis
├── development/
│   ├── code_review.py      # Code analysis
│   ├── architecture.py     # Architecture checks
│   └── testing.py          # Test utilities
└── __init__.py
```

### Agent Layer (Clean Separation)
```
legion/agents/
├── base.py                 # BaseAgent class
├── contracts.py            # Agent interfaces
├── python/
│   ├── specialist/         # Domain-specific agents
│   │   ├── researcher.py   # Research & information
│   │   ├── architect.py    # Code architecture
│   │   ├── doctor.py       # System diagnosis
│   │   ├── therapist.py    # Agent wellbeing
│   │   └── ux_designer.py  # UI/UX design
│   ├── operational/        # System operation agents
│   │   ├── metrics.py      # System monitoring
│   │   ├── healthcheck.py  # Health monitoring
│   │   ├── ping.py         # Connectivity tests
│   │   └── echo.py         # Message mirroring
│   └── __init__.py
├── go/
│   ├── developer.go        # Development tasks
│   └── __init__.py
└── __init__.py
```

### Infrastructure Separation
```
legion/infrastructure/
├── mcp/
│   ├── server.py           # MCP server (moved from skills/)
│   ├── client.py           # MCP client
│   └── config.yaml         # MCP configuration
├── llm/
│   ├── client.py           # LLM client (moved from skills/)
│   └── providers.py        # Provider abstractions
└── __init__.py
```

## Migration Steps

### Phase 1: Structure Compliance
1. **Move `legion/core/` → `core/`** to match required structure
2. **Remove duplicate files** (`legion/agents/echo.py`, `legion/agents/therapist.py`)
3. **Update all imports** to use new paths

### Phase 2: Skills Enhancement
1. **Categorize skills by domain** (research, communication, analysis, development)
2. **Create skill interfaces** for consistent agent integration
3. **Move infrastructure code** (MCP, LLM client) out of skills/

### Phase 3: Agent Optimization
1. **Subcategorize agents** (specialist vs operational)
2. **Implement skill usage** across all relevant agents
3. **Create agent factories** for easier instantiation

## Benefits

### **Better Separation of Concerns**
- Skills focus on domain capabilities
- Agents focus on personality and workflow
- Infrastructure handles connectivity and protocols

### **Improved Reusability**
- Skills can be mixed and matched across agents
- Core utilities available to all components
- Clear interfaces for extension

### **Enhanced Maintainability**
- Domain-based organization makes finding code easier
- Reduced duplication across agents
- Clear dependency hierarchy

### **Scalability**
- Easy to add new skills in appropriate domains
- Agent specialization vs operational roles clarified
- Infrastructure changes isolated from business logic

## Implementation Priority

1. **High**: Fix structure compliance (Phase 1)
2. **Medium**: Reorganize skills by domain (Phase 2)
3. **Low**: Agent subcategorization (Phase 3)

This reorganization aligns with the Legion structure rules while creating a more scalable and maintainable codebase. 