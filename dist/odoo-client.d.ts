/**
 * Odoo MCP Server - Odoo XML-RPC Client
 * Production-grade client with retry logic, error handling, and connection pooling
 */
import type { OdooConfig, OdooConnection, OdooResponse, SearchParams, CreateParams, UpdateParams, DeleteParams, ReadParams, ExecuteParams, ReportParams, ModelMetadata } from './types';
export declare class OdooClient {
    private config;
    private connection;
    private commonClient;
    private objectClient;
    private reportClient;
    constructor(config: OdooConfig);
    /**
     * Authenticate and establish connection to Odoo
     */
    authenticate(): Promise<OdooResponse<OdooConnection>>;
    /**
     * Search records with domain filters
     */
    search(params: SearchParams): Promise<OdooResponse<number[]>>;
    /**
     * Search and read records in one call
     */
    searchRead(params: SearchParams): Promise<OdooResponse<any[]>>;
    /**
     * Read records by IDs
     */
    read(params: ReadParams): Promise<OdooResponse<any[]>>;
    /**
     * Create new record
     */
    create(params: CreateParams): Promise<OdooResponse<number>>;
    /**
     * Update existing records
     */
    update(params: UpdateParams): Promise<OdooResponse<boolean>>;
    /**
     * Delete records
     */
    delete(params: DeleteParams): Promise<OdooResponse<boolean>>;
    /**
     * Execute arbitrary method on model
     */
    executeKw(params: ExecuteParams): Promise<OdooResponse<any>>;
    /**
     * Get model metadata (fields definition)
     */
    getModelMetadata(model: string): Promise<OdooResponse<ModelMetadata>>;
    /**
     * Get count of records matching domain
     */
    count(params: Omit<SearchParams, 'fields' | 'limit' | 'offset' | 'order'>): Promise<OdooResponse<number>>;
    /**
     * Execute button/action on records
     */
    executeAction(params: {
        model: string;
        ids: number[];
        action: string;
        context?: Record<string, any>;
    }): Promise<OdooResponse<any>>;
    /**
     * Generate report
     */
    generateReport(params: ReportParams): Promise<OdooResponse<string>>;
    /**
     * Execute XML-RPC call with retry logic
     */
    private executeXmlRpc;
    /**
     * Execute method on Odoo object
     */
    private execute;
    /**
     * Ensure authenticated before executing operations
     */
    private ensureAuthenticated;
    /**
     * Normalize domain format
     */
    private normalizeDomain;
    /**
     * Handle and format errors
     */
    private handleError;
    /**
     * Sleep utility for retry logic
     */
    private sleep;
    /**
     * Get connection status
     */
    isConnected(): boolean;
    /**
     * Get server info
     */
    getServerInfo(): OdooConnection | null;
}
//# sourceMappingURL=odoo-client.d.ts.map