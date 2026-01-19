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
} | {
    name: string;
    description: string;
    inputSchema: z.ZodObject<{
        instance: z.ZodString;
        removeTestData: z.ZodOptional<z.ZodBoolean>;
        removeInactivRecords: z.ZodOptional<z.ZodBoolean>;
        cleanupDrafts: z.ZodOptional<z.ZodBoolean>;
        archiveOldRecords: z.ZodOptional<z.ZodBoolean>;
        optimizeDatabase: z.ZodOptional<z.ZodBoolean>;
        daysThreshold: z.ZodOptional<z.ZodNumber>;
        dryRun: z.ZodOptional<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        instance: string;
        removeTestData?: boolean | undefined;
        removeInactivRecords?: boolean | undefined;
        cleanupDrafts?: boolean | undefined;
        archiveOldRecords?: boolean | undefined;
        optimizeDatabase?: boolean | undefined;
        daysThreshold?: number | undefined;
        dryRun?: boolean | undefined;
    }, {
        instance: string;
        removeTestData?: boolean | undefined;
        removeInactivRecords?: boolean | undefined;
        cleanupDrafts?: boolean | undefined;
        archiveOldRecords?: boolean | undefined;
        optimizeDatabase?: boolean | undefined;
        daysThreshold?: number | undefined;
        dryRun?: boolean | undefined;
    }>;
} | {
    name: string;
    description: string;
    inputSchema: z.ZodObject<{
        instance: z.ZodString;
        dryRun: z.ZodOptional<z.ZodBoolean>;
        keepCompanyDefaults: z.ZodOptional<z.ZodBoolean>;
        keepUserAccounts: z.ZodOptional<z.ZodBoolean>;
        keepMenus: z.ZodOptional<z.ZodBoolean>;
        keepGroups: z.ZodOptional<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        instance: string;
        dryRun?: boolean | undefined;
        keepCompanyDefaults?: boolean | undefined;
        keepUserAccounts?: boolean | undefined;
        keepMenus?: boolean | undefined;
        keepGroups?: boolean | undefined;
    }, {
        instance: string;
        dryRun?: boolean | undefined;
        keepCompanyDefaults?: boolean | undefined;
        keepUserAccounts?: boolean | undefined;
        keepMenus?: boolean | undefined;
        keepGroups?: boolean | undefined;
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
    private handleDatabaseCleanup;
    private handleDeepCleanup;
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