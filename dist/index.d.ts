/**
 * Odoo MCP Server - Main Entry Point
 * Production-grade MCP server for Odoo 17-19
 * Supports multiple instances, comprehensive operations, and Cloudflare Workers deployment
 */
/**
 * Environment configuration interface
 */
interface Env {
    ODOO_INSTANCES?: string;
    ODOO_URL?: string;
    ODOO_DB?: string;
    ODOO_USERNAME?: string;
    ODOO_PASSWORD?: string;
    ODOO_API_KEY?: string;
    ODOO_CACHE?: any;
}
/**
 * Main server class
 */
declare class OdooMCPServer {
    private server;
    private instances;
    private clients;
    private tools;
    constructor(env: Env);
    /**
     * Get or create Odoo client for instance
     */
    private getClient;
    /**
     * Setup MCP request handlers
     */
    private setupHandlers;
    /**
     * Start the server with stdio transport
     */
    start(): Promise<void>;
}
/**
 * Entry point
 */
declare function main(): Promise<void>;
export { OdooMCPServer, main };
declare const _default: {
    fetch: (_request: Request) => Promise<import("undici-types").Response>;
};
export default _default;
//# sourceMappingURL=index.d.ts.map