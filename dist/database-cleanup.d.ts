/**
 * Odoo Database Cleanup Module
 * Performs comprehensive database cleanup for production readiness
 * Targets: ScholarixV2 and similar Odoo 17-19 instances
 */
import type { OdooClient } from './odoo-client';
export interface CleanupOptions {
    instance: string;
    removeTestData?: boolean;
    removeInactivRecords?: boolean;
    cleanupDrafts?: boolean;
    archiveOldRecords?: boolean;
    optimizeDatabase?: boolean;
    daysThreshold?: number;
    dryRun?: boolean;
}
export interface CleanupReport {
    success: boolean;
    timestamp: string;
    summary: {
        testDataRemoved: number;
        inactiveRecordsArchived: number;
        draftsCleaned: number;
        orphanRecordsRemoved: number;
        logsCleaned: number;
        attachmentsCleaned: number;
        cacheCleared: boolean;
        totalRecordsProcessed: number;
    };
    details: CleanupDetail[];
    warnings: string[];
    errors: string[];
    dryRun: boolean;
}
export interface CleanupDetail {
    operation: string;
    model: string;
    recordsAffected: number;
    details: string;
    status: 'success' | 'warning' | 'error';
}
export declare class DatabaseCleanup {
    private getClient;
    constructor(getClient: (instance: string) => Promise<OdooClient>);
    /**
     * Execute comprehensive database cleanup
     */
    executeFullCleanup(options: CleanupOptions): Promise<CleanupReport>;
    /**
     * Remove test records and demo data
     */
    private removeTestData;
    /**
     * Archive inactive records (no activity for specified days)
     */
    private archiveInactiveRecords;
    /**
     * Clean up draft documents
     */
    private cleanupDraftDocuments;
    /**
     * Remove orphan records (records with broken foreign keys)
     */
    private removeOrphanRecords;
    /**
     * Clean up activity logs (mail.activity, mail.message)
     */
    private cleanupActivityLogs;
    /**
     * Clean up old attachments
     */
    private cleanupAttachments;
    /**
     * Clear caches (web cache, session cache)
     */
    private clearCaches;
}
//# sourceMappingURL=database-cleanup.d.ts.map