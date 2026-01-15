/**
 * Odoo MCP Server - MCP Tools Implementation
 * Context-aware tools for comprehensive Odoo operations
 */
import { z } from 'zod';
import type { OdooClient } from './odoo-client';
/**
 * MCP Tools for Odoo operations
 */
export declare const tools: ({
    name: string;
    description: string;
    inputSchema: z.ZodObject<{
        instance: z.ZodString;
        reportName: z.ZodString;
        ids: z.ZodArray<z.ZodNumber, "many">;
        data: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    }, "strip", z.ZodTypeAny, {
        instance: string;
        ids: number[];
        reportName: string;
        data?: Record<string, any> | undefined;
    }, {
        instance: string;
        ids: number[];
        reportName: string;
        data?: Record<string, any> | undefined;
    }>;
} | {
    name: string;
    description: string;
    inputSchema: z.ZodObject<{
        instance: z.ZodString;
        model: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        model: string;
        instance: string;
    }, {
        model: string;
        instance: string;
    }>;
})[];
/**
 * Tool execution handlers
 */
export declare class OdooTools {
    private getClient;
    constructor(getClient: (instance: string) => Promise<OdooClient>);
    executeTool(name: string, args: any): Promise<any>;
    private handleSearch;
    private handleSearchRead;
    private handleRead;
    private handleCreate;
    private handleUpdate;
    private handleDelete;
    private handleExecute;
    private handleCount;
    private handleWorkflowAction;
    private handleGenerateReport;
    private handleGetModelMetadata;
}
/**
 * Context-aware helper prompts for AI
 */
export declare const contextPrompts: {
    name: string;
    description: string;
    content: string;
}[];
//# sourceMappingURL=tools.d.ts.map