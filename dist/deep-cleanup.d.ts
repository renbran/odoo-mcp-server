/**
 * ScholarixV2 Deep Cleanup - Remove All Non-Essential Data
 * Retains only default setup and essential configuration
 * Removes all demo data, test records, and user-created data
 */
import type { OdooClient } from './odoo-client';
export interface DeepCleanupOptions {
    instance: string;
    dryRun?: boolean;
    keepCompanyDefaults?: boolean;
    keepUserAccounts?: boolean;
    keepMenus?: boolean;
    keepGroups?: boolean;
}
export interface DeepCleanupReport {
    success: boolean;
    timestamp: string;
    summary: {
        partnersRemoved: number;
        salesOrdersRemoved: number;
        invoicesRemoved: number;
        purchaseOrdersRemoved: number;
        stockMovesRemoved: number;
        documentsRemoved: number;
        contactsRemoved: number;
        leadsRemoved: number;
        opportunitiesRemoved: number;
        projectsRemoved: number;
        tasksRemoved: number;
        attendeesRemoved: number;
        eventsRemoved: number;
        journalsRemoved: number;
        accountsRemoved: number;
        productsRemoved: number;
        stockLocationsRemoved: number;
        warehousesRemoved: number;
        employeesRemoved: number;
        departmentsRemoved: number;
        logsAndAttachments: number;
        totalRecordsRemoved: number;
    };
    details: DeepCleanupDetail[];
    warnings: string[];
    errors: string[];
    dryRun: boolean;
    defaultDataRetained: string[];
}
export interface DeepCleanupDetail {
    model: string;
    recordsRemoved: number;
    details: string;
    status: 'success' | 'warning' | 'error';
}
export declare class DeepDatabaseCleanup {
    private getClient;
    constructor(getClient: (instance: string) => Promise<OdooClient>);
    /**
     * Execute complete database reset - remove all non-essential data
     */
    executeDeepCleanup(options: DeepCleanupOptions): Promise<DeepCleanupReport>;
    /**
     * Remove all partners except defaults
     */
    private removePartners;
    /**
     * Remove all sales orders and quotes
     */
    private removeSalesDocuments;
    /**
     * Remove all invoices and accounting entries
     */
    private removeInvoicesAndAccounting;
    /**
     * Remove all purchase orders
     */
    private removePurchaseOrders;
    /**
     * Remove inventory and stock data
     */
    private removeStockData;
    /**
     * Remove CRM data
     */
    private removeCRMData;
    /**
     * Remove project and task data
     */
    private removeProjectData;
    /**
     * Remove calendar events and attendees
     */
    private removeCalendarData;
    /**
     * Remove HR data
     */
    private removeHRData;
    /**
     * Remove logs and attachments
     */
    private removeLogsAndAttachments;
    /**
     * Identify default data that was retained
     */
    private identifyDefaultData;
}
//# sourceMappingURL=deep-cleanup.d.ts.map