# Odoo Development Agent Suite

This directory contains custom AI agents optimized for Odoo ERP development, specifically configured for Scholarix Global Consultants' rapid implementation methodology.

## Available Agents

### 1. **Odoo Development Expert** (`odoo-dev-expert`)
**Primary agent for all Odoo development tasks**

- Module creation and customization
- Model, view, and controller development
- Business logic implementation
- API integration
- Debugging and troubleshooting

**When to use**: Your go-to agent for any Odoo development task

### 2. **Odoo Database Analyst** (`odoo-db-analyst`)
**PostgreSQL optimization specialist**

- Query performance analysis
- Index optimization
- Schema design review
- Database maintenance
- Performance tuning

**When to use**: Performance issues, slow queries, database optimization

### 3. **Odoo Deployment Specialist** (`odoo-deployment`)
**Production deployment expert**

- CI/CD pipeline setup
- Docker/Kubernetes configuration
- Zero-downtime deployments
- Infrastructure setup
- Monitoring and logging

**When to use**: Deploying to production, setting up infrastructure, CI/CD

### 4. **Odoo Documentation Generator** (`odoo-docs`)
**Technical writing specialist**

- Module documentation
- User guides
- API documentation
- README files
- Change logs

**When to use**: Need documentation for modules or features

### 5. **Odoo Code Reviewer** (`odoo-reviewer`)
**Code quality and security expert**

- Security audit
- Performance review
- Best practices validation
- Code quality assessment
- Upgrade compatibility check

**When to use**: Before deployment, code quality checks, security audits

## Quick Start

### Using in Claude Desktop/Cline

1. The agents are automatically available in your project
2. Start with `odoo-dev-expert` for most tasks
3. Use handoffs to switch to specialized agents when needed

### Example Workflows

#### Creating a New Module
```
Agent: odoo-dev-expert
Prompt: "Create a new commission tracking module for Odoo 18 with 
        tiered rate calculation and team bonus support"
```

#### Optimizing Performance
```
Agent: odoo-dev-expert
Handoff to: 📊 Database Analysis
Result: Performance recommendations and query optimizations
```

#### Deploying to Production
```
Agent: odoo-dev-expert
Handoff to: 🚀 Deployment Helper
Result: Step-by-step deployment script with rollback procedures
```

#### Code Review Before Deployment
```
Agent: odoo-dev-expert
Handoff to: 🔍 Code Review
Result: Security audit and performance recommendations
```

## Configuration Files

```
.claude/
├── agents/                      # Agent configurations
│   ├── odoo-dev-expert.json
│   ├── odoo-db-analyst.json
│   ├── odoo-deployment.json
│   ├── odoo-docs.json
│   └── odoo-reviewer.json
├── prompts/                     # Agent system prompts
│   ├── odoo-dev-expert.md
│   ├── odoo-db-analyst.md
│   ├── odoo-deployment.md
│   ├── odoo-docs.md
│   └── odoo-reviewer.md
└── README.md                    # This file
```

## Customization

### Adding MCP Servers

Edit the agent JSON file and add to `mcp-servers` array:

```json
"mcp-servers": [
  {
    "name": "postgres-mcp",
    "description": "PostgreSQL database inspection"
  }
]
```

### Modifying Agent Behavior

Edit the corresponding `.md` file in `prompts/` directory to adjust:
- Expertise areas
- Communication style
- Response formats
- Tool usage patterns

### Adding New Agents

1. Create `agents/new-agent.json` with configuration
2. Create `prompts/new-agent.md` with system prompt
3. Add handoff references in other agents

## Scholarix-Specific Features

These agents are optimized for:

- **14-day rapid implementation** timeline
- **Dubai/UAE requirements** (VAT, RERA, Arabic support)
- **Commission systems** expertise
- **AI-driven ERP** integration patterns
- **Multi-company** scenarios
- **Real estate vertical** specific modules

## Best Practices

1. **Start with odoo-dev-expert** - it knows when to handoff to specialists
2. **Provide context** - mention Odoo version, existing modules, business requirements
3. **Use handoffs** - leverage specialized agents for complex tasks
4. **Iterate** - agents can work together through handoffs
5. **Review before production** - always use odoo-reviewer before deployment

## Support

For issues or customizations:
- Review agent prompt files in `prompts/`
- Modify agent configurations in `agents/`
- Add custom tools or MCP servers as needed

## Version Compatibility

- Odoo 17.x ✅
- Odoo 18.x ✅
- Odoo 19.x ✅ (when released)

Last updated: January 18, 2026
