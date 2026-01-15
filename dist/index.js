/**
 * Odoo MCP Server - Main Entry Point
 * Production-grade MCP server for Odoo 17-19
 * Supports multiple instances, comprehensive operations, and Cloudflare Workers deployment
 */
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema, ListPromptsRequestSchema, GetPromptRequestSchema, } from '@modelcontextprotocol/sdk/types.js';
import { OdooClient } from './odoo-client.js';
import { OdooTools, tools, contextPrompts } from './tools.js';
/**
 * Parse Odoo instance configurations from environment
 */
function parseOdooInstances(env) {
    const instances = new Map();
    // Try parsing ODOO_INSTANCES JSON first
    if (env.ODOO_INSTANCES) {
        try {
            const parsed = JSON.parse(env.ODOO_INSTANCES);
            Object.entries(parsed).forEach(([name, config]) => {
                instances.set(name, config);
            });
            return instances;
        }
        catch (error) {
            console.error('Failed to parse ODOO_INSTANCES:', error);
        }
    }
    // Fall back to individual environment variables
    if (env.ODOO_URL && env.ODOO_DB && env.ODOO_USERNAME && env.ODOO_PASSWORD) {
        instances.set('default', {
            url: env.ODOO_URL,
            db: env.ODOO_DB,
            username: env.ODOO_USERNAME,
            password: env.ODOO_PASSWORD,
            apiKey: env.ODOO_API_KEY,
        });
    }
    if (instances.size === 0) {
        throw new Error('No Odoo instances configured. Set ODOO_INSTANCES or individual ODOO_* variables.');
    }
    return instances;
}
/**
 * Main server class
 */
class OdooMCPServer {
    server;
    instances;
    clients = new Map();
    tools;
    constructor(env) {
        this.instances = parseOdooInstances(env);
        this.server = new Server({
            name: 'odoo-mcp-server',
            version: '1.0.0',
        }, {
            capabilities: {
                tools: {},
                prompts: {},
            },
        });
        this.tools = new OdooTools(this.getClient.bind(this));
        this.setupHandlers();
    }
    /**
     * Get or create Odoo client for instance
     */
    async getClient(instance) {
        // Check if client already exists and is connected
        if (this.clients.has(instance)) {
            const client = this.clients.get(instance);
            if (client.isConnected()) {
                return client;
            }
        }
        // Get instance config
        const config = this.instances.get(instance);
        if (!config) {
            const availableInstances = Array.from(this.instances.keys()).join(', ');
            throw new Error(`Unknown Odoo instance: ${instance}. Available instances: ${availableInstances}`);
        }
        // Create and authenticate new client
        const client = new OdooClient(config);
        const result = await client.authenticate();
        if (!result.success) {
            throw new Error(`Failed to authenticate with ${instance}: ${result.error?.message}`);
        }
        console.error(`✓ Connected to Odoo ${instance} (${result.data?.serverVersion})`);
        this.clients.set(instance, client);
        return client;
    }
    /**
     * Setup MCP request handlers
     */
    setupHandlers() {
        // List available tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: tools.map(tool => ({
                name: tool.name,
                description: tool.description,
                inputSchema: {
                    type: 'object',
                    properties: tool.inputSchema.shape,
                    required: Object.keys(tool.inputSchema.shape).filter((key) => !tool.inputSchema.shape[key].isOptional()),
                },
            })),
        }));
        // Execute tool
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            try {
                console.error(`Executing tool: ${name}`);
                const result = await this.tools.executeTool(name, args);
                return result;
            }
            catch (error) {
                console.error(`Tool execution error (${name}):`, error);
                return {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify({
                                error: error instanceof Error ? error.message : 'Unknown error',
                                tool: name,
                                arguments: args,
                            }, null, 2),
                        },
                    ],
                    isError: true,
                };
            }
        });
        // List available prompts
        this.server.setRequestHandler(ListPromptsRequestSchema, async () => ({
            prompts: contextPrompts.map(prompt => ({
                name: prompt.name,
                description: prompt.description,
            })),
        }));
        // Get prompt content
        this.server.setRequestHandler(GetPromptRequestSchema, async (request) => {
            const prompt = contextPrompts.find(p => p.name === request.params.name);
            if (!prompt) {
                throw new Error(`Unknown prompt: ${request.params.name}`);
            }
            return {
                description: prompt.description,
                messages: [
                    {
                        role: 'user',
                        content: {
                            type: 'text',
                            text: prompt.content,
                        },
                    },
                ],
            };
        });
        // Error handler
        this.server.onerror = (error) => {
            console.error('[MCP Error]', error);
        };
        // Log when server is closed
        process.on('SIGINT', async () => {
            console.error('\nShutting down Odoo MCP Server...');
            await this.server.close();
            process.exit(0);
        });
    }
    /**
     * Start the server with stdio transport
     */
    async start() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        const instanceNames = Array.from(this.instances.keys()).join(', ');
        console.error('Odoo MCP Server running');
        console.error(`Configured instances: ${instanceNames}`);
        console.error(`Available tools: ${tools.length}`);
    }
}
/**
 * Entry point
 */
async function main() {
    try {
        // Get environment variables (works in Node.js and Cloudflare Workers)
        const env = {
            ODOO_INSTANCES: process.env.ODOO_INSTANCES,
            ODOO_URL: process.env.ODOO_URL,
            ODOO_DB: process.env.ODOO_DB,
            ODOO_USERNAME: process.env.ODOO_USERNAME,
            ODOO_PASSWORD: process.env.ODOO_PASSWORD,
            ODOO_API_KEY: process.env.ODOO_API_KEY,
        };
        const server = new OdooMCPServer(env);
        await server.start();
    }
    catch (error) {
        console.error('Failed to start Odoo MCP Server:', error);
        process.exit(1);
    }
}
// Auto-start if running directly in Node.js
try {
    if (typeof process !== 'undefined' && process.argv && import.meta.url === `file://${process.argv[1]}`) {
        main();
    }
}
catch (e) {
    // Running in Cloudflare Workers or browser, skip auto-start
}
export { OdooMCPServer, main };
// Default export for Cloudflare Workers
export default {
    fetch: async (_request) => {
        return new Response('Odoo MCP Server is running', { status: 200 });
    },
};
//# sourceMappingURL=index.js.map