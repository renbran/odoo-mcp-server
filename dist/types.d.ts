/**
 * Odoo MCP Server - Type Definitions
 * Production-grade types for Odoo 17-19 compatibility
 */
export interface OdooConfig {
    url: string;
    db: string;
    username: string;
    password: string;
    apiKey?: string;
    timeout?: number;
    maxRetries?: number;
}
export interface OdooConfigInternal extends Omit<OdooConfig, 'timeout' | 'maxRetries'> {
    timeout: number;
    maxRetries: number;
}
export interface OdooConnection {
    uid: number;
    sessionId?: string;
    serverVersion?: string;
}
export interface OdooDomain {
    field: string;
    operator: '=' | '!=' | '>' | '<' | '>=' | '<=' | 'like' | 'ilike' | 'in' | 'not in' | '=like' | '=ilike';
    value: any;
}
export interface SearchParams {
    model: string;
    domain?: Array<string | OdooDomain>;
    fields?: string[];
    limit?: number;
    offset?: number;
    order?: string;
    context?: Record<string, any>;
}
export interface CreateParams {
    model: string;
    values: Record<string, any>;
    context?: Record<string, any>;
}
export interface UpdateParams {
    model: string;
    ids: number[];
    values: Record<string, any>;
    context?: Record<string, any>;
}
export interface DeleteParams {
    model: string;
    ids: number[];
    context?: Record<string, any>;
}
export interface ReadParams {
    model: string;
    ids: number[];
    fields?: string[];
    context?: Record<string, any>;
}
export interface ExecuteParams {
    model: string;
    method: string;
    args?: any[];
    kwargs?: Record<string, any>;
    context?: Record<string, any>;
}
export interface ReportParams {
    reportName: string;
    ids: number[];
    data?: Record<string, any>;
    context?: Record<string, any>;
}
export interface WorkflowParams {
    model: string;
    ids: number[];
    action: string;
    context?: Record<string, any>;
}
export interface OdooError {
    code: string;
    message: string;
    data?: any;
}
export interface OdooResponse<T = any> {
    success: boolean;
    data?: T;
    error?: OdooError;
    metadata?: {
        executionTime: number;
        recordCount?: number;
        serverVersion?: string;
    };
}
export interface FieldMetadata {
    name: string;
    type: string;
    string: string;
    required: boolean;
    readonly: boolean;
    help?: string;
    relation?: string;
    selectionOptions?: Array<[string, string]>;
}
export interface ModelMetadata {
    name: string;
    description: string;
    fields: Record<string, FieldMetadata>;
    access_rights?: {
        create: boolean;
        read: boolean;
        write: boolean;
        unlink: boolean;
    };
}
//# sourceMappingURL=types.d.ts.map