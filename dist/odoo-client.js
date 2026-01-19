/**
 * Odoo MCP Server - Odoo XML-RPC Client
 * Production-grade client with retry logic, error handling, and connection pooling
 */
import xmlrpc from 'xmlrpc';
export class OdooClient {
    config;
    connection = null;
    commonClient;
    objectClient;
    reportClient;
    constructor(config) {
        this.config = {
            ...config,
            timeout: config.timeout ?? 30000,
            maxRetries: config.maxRetries ?? 3,
        };
        const url = new URL(this.config.url);
        const clientOptions = {
            host: url.hostname,
            port: parseInt(url.port) || (url.protocol === 'https:' ? 443 : 8069),
            path: '/xmlrpc/2/common',
        };
        this.commonClient = xmlrpc.createSecureClient(clientOptions);
        this.objectClient = xmlrpc.createSecureClient({
            ...clientOptions,
            path: '/xmlrpc/2/object',
        });
        this.reportClient = xmlrpc.createSecureClient({
            ...clientOptions,
            path: '/xmlrpc/2/report',
        });
    }
    /**
     * Authenticate and establish connection to Odoo
     */
    async authenticate() {
        const startTime = Date.now();
        try {
            const uid = await this.executeXmlRpc(this.commonClient, 'authenticate', [this.config.db, this.config.username, this.config.password, {}]);
            if (!uid) {
                return {
                    success: false,
                    error: {
                        code: 'AUTH_FAILED',
                        message: 'Authentication failed. Check credentials.',
                    },
                };
            }
            // Get server version
            const serverVersion = await this.executeXmlRpc(this.commonClient, 'version', []);
            this.connection = {
                uid,
                serverVersion: serverVersion?.server_version || 'unknown',
            };
            return {
                success: true,
                data: this.connection,
                metadata: {
                    executionTime: Date.now() - startTime,
                    serverVersion: this.connection.serverVersion,
                },
            };
        }
        catch (error) {
            return {
                success: false,
                error: {
                    code: 'AUTH_ERROR',
                    message: error instanceof Error ? error.message : 'Unknown authentication error',
                    data: error,
                },
            };
        }
    }
    /**
     * Search records with domain filters
     */
    async search(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const domain = this.normalizeDomain(params.domain || []);
            const options = {};
            if (params.limit)
                options.limit = params.limit;
            if (params.offset)
                options.offset = params.offset;
            if (params.order)
                options.order = params.order;
            const ids = await this.execute('search', params.model, [domain, options], params.context);
            return {
                success: true,
                data: ids,
                metadata: {
                    executionTime: Date.now() - startTime,
                    recordCount: ids.length,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('SEARCH_ERROR', error);
        }
    }
    /**
     * Search and read records in one call
     */
    async searchRead(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const domain = this.normalizeDomain(params.domain || []);
            const options = {};
            if (params.fields)
                options.fields = params.fields;
            if (params.limit)
                options.limit = params.limit;
            if (params.offset)
                options.offset = params.offset;
            if (params.order)
                options.order = params.order;
            const records = await this.execute('search_read', params.model, [domain, options], params.context);
            return {
                success: true,
                data: records,
                metadata: {
                    executionTime: Date.now() - startTime,
                    recordCount: records.length,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('SEARCH_READ_ERROR', error);
        }
    }
    /**
     * Read records by IDs
     */
    async read(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const records = await this.execute('read', params.model, [params.ids, params.fields || []], params.context);
            return {
                success: true,
                data: records,
                metadata: {
                    executionTime: Date.now() - startTime,
                    recordCount: records.length,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('READ_ERROR', error);
        }
    }
    /**
     * Create new record
     */
    async create(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const id = await this.execute('create', params.model, [params.values], params.context);
            return {
                success: true,
                data: id,
                metadata: {
                    executionTime: Date.now() - startTime,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('CREATE_ERROR', error);
        }
    }
    /**
     * Update existing records
     */
    async update(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const result = await this.execute('write', params.model, [params.ids, params.values], params.context);
            return {
                success: true,
                data: result,
                metadata: {
                    executionTime: Date.now() - startTime,
                    recordCount: params.ids.length,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('UPDATE_ERROR', error);
        }
    }
    /**
     * Delete records
     */
    async delete(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const result = await this.execute('unlink', params.model, [params.ids], params.context);
            return {
                success: true,
                data: result,
                metadata: {
                    executionTime: Date.now() - startTime,
                    recordCount: params.ids.length,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('DELETE_ERROR', error);
        }
    }
    /**
     * Execute arbitrary method on model
     */
    async executeKw(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const result = await this.execute(params.method, params.model, params.args || [], params.context, params.kwargs);
            return {
                success: true,
                data: result,
                metadata: {
                    executionTime: Date.now() - startTime,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('EXECUTE_ERROR', error);
        }
    }
    /**
     * Get model metadata (fields definition)
     */
    async getModelMetadata(model) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const fieldsInfo = await this.execute('fields_get', model, [[]], {});
            const modelInfo = await this.execute('name_get', 'ir.model', [[]], {});
            return {
                success: true,
                data: {
                    name: model,
                    description: modelInfo[0]?.[1] || model,
                    fields: fieldsInfo,
                },
                metadata: {
                    executionTime: Date.now() - startTime,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('METADATA_ERROR', error);
        }
    }
    /**
     * Get count of records matching domain
     */
    async count(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const domain = this.normalizeDomain(params.domain || []);
            const count = await this.execute('search_count', params.model, [domain], params.context);
            return {
                success: true,
                data: count,
                metadata: {
                    executionTime: Date.now() - startTime,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('COUNT_ERROR', error);
        }
    }
    /**
     * Execute button/action on records
     */
    async executeAction(params) {
        return this.executeKw({
            model: params.model,
            method: params.action,
            args: [params.ids],
            context: params.context,
        });
    }
    /**
     * Generate report
     */
    async generateReport(params) {
        await this.ensureAuthenticated();
        const startTime = Date.now();
        try {
            const result = await this.executeXmlRpc(this.reportClient, 'render_report', [
                this.config.db,
                this.connection.uid,
                this.config.password,
                params.reportName,
                params.ids,
                params.data || {},
                params.context || {},
            ]);
            return {
                success: true,
                data: result.toString('base64'),
                metadata: {
                    executionTime: Date.now() - startTime,
                    serverVersion: this.connection?.serverVersion,
                },
            };
        }
        catch (error) {
            return this.handleError('REPORT_ERROR', error);
        }
    }
    /**
     * Execute XML-RPC call with retry logic
     */
    async executeXmlRpc(client, method, params) {
        let lastError = null;
        for (let attempt = 0; attempt < this.config.maxRetries; attempt++) {
            try {
                return await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => {
                        reject(new Error('Request timeout'));
                    }, this.config.timeout);
                    client.methodCall(method, params, (error, value) => {
                        clearTimeout(timeout);
                        if (error)
                            reject(error);
                        else
                            resolve(value);
                    });
                });
            }
            catch (error) {
                lastError = error;
                // Don't retry authentication errors
                if (method === 'authenticate') {
                    throw error;
                }
                // Exponential backoff
                if (attempt < this.config.maxRetries - 1) {
                    await this.sleep(Math.pow(2, attempt) * 1000);
                }
            }
        }
        throw lastError || new Error('Unknown XML-RPC error');
    }
    /**
     * Execute method on Odoo object
     */
    async execute(method, model, args, context, kwargs) {
        // Build standard execute_kw parameters: [db, uid, password, model, method, args, kwargs]
        const params = [
            this.config.db,
            this.connection.uid,
            this.config.password,
            model,
            method,
            Array.isArray(args) ? args : [],
        ];
        if (context || kwargs) {
            const options = {};
            if (context)
                options.context = context;
            if (kwargs)
                Object.assign(options, kwargs);
            params.push(options);
        }
        return this.executeXmlRpc(this.objectClient, 'execute_kw', params);
    }
    /**
     * Ensure authenticated before executing operations
     */
    async ensureAuthenticated() {
        if (!this.connection) {
            const result = await this.authenticate();
            if (!result.success) {
                throw new Error(result.error?.message || 'Authentication failed');
            }
        }
    }
    /**
     * Normalize domain format
     */
    normalizeDomain(domain) {
        if (domain.length === 0)
            return [];
        return domain.map(item => {
            if (typeof item === 'object' && 'field' in item) {
                return [item.field, item.operator, item.value];
            }
            return item;
        });
    }
    /**
     * Handle and format errors
     */
    handleError(code, error) {
        return {
            success: false,
            error: {
                code,
                message: error instanceof Error ? error.message : 'Unknown error',
                data: error,
            },
        };
    }
    /**
     * Sleep utility for retry logic
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    /**
     * Get connection status
     */
    isConnected() {
        return this.connection !== null;
    }
    /**
     * Get server info
     */
    getServerInfo() {
        return this.connection;
    }
}
//# sourceMappingURL=odoo-client.js.map