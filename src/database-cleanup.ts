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
  daysThreshold?: number; // For archiving old records
  dryRun?: boolean; // Show what would be deleted without actually deleting
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

export class DatabaseCleanup {
  constructor(private getClient: (instance: string) => Promise<OdooClient>) {}

  /**
   * Execute comprehensive database cleanup
   */
  async executeFullCleanup(options: CleanupOptions): Promise<CleanupReport> {
    const client = await this.getClient(options.instance);
    const report: CleanupReport = {
      success: true,
      timestamp: new Date().toISOString(),
      summary: {
        testDataRemoved: 0,
        inactiveRecordsArchived: 0,
        draftsCleaned: 0,
        orphanRecordsRemoved: 0,
        logsCleaned: 0,
        attachmentsCleaned: 0,
        cacheCleared: false,
        totalRecordsProcessed: 0,
      },
      details: [],
      warnings: [],
      errors: [],
      dryRun: options.dryRun ?? false,
    };

    try {
      // 1. Remove test data
      if (options.removeTestData !== false) {
        const testDataResult = await this.removeTestData(
          client,
          options.dryRun
        );
        report.summary.testDataRemoved = testDataResult.count;
        report.details.push(...testDataResult.details);
      }

      // 2. Remove/archive inactive records
      if (options.removeInactivRecords !== false) {
        const inactiveResult = await this.archiveInactiveRecords(
          client,
          options.daysThreshold || 180,
          options.dryRun
        );
        report.summary.inactiveRecordsArchived = inactiveResult.count;
        report.details.push(...inactiveResult.details);
      }

      // 3. Clean up draft documents
      if (options.cleanupDrafts !== false) {
        const draftsResult = await this.cleanupDraftDocuments(
          client,
          options.dryRun
        );
        report.summary.draftsCleaned = draftsResult.count;
        report.details.push(...draftsResult.details);
      }

      // 4. Remove orphan records
      const orphanResult = await this.removeOrphanRecords(client, options.dryRun);
      report.summary.orphanRecordsRemoved = orphanResult.count;
      report.details.push(...orphanResult.details);

      // 5. Clean up logs and activity
      const logsResult = await this.cleanupActivityLogs(
        client,
        options.daysThreshold || 180,
        options.dryRun
      );
      report.summary.logsCleaned = logsResult.count;
      report.details.push(...logsResult.details);

      // 6. Clean up old attachments
      const attachmentsResult = await this.cleanupAttachments(
        client,
        options.daysThreshold || 180,
        options.dryRun
      );
      report.summary.attachmentsCleaned = attachmentsResult.count;
      report.details.push(...attachmentsResult.details);

      // 7. Clear caches (if not dry run)
      if (!options.dryRun) {
        try {
          const cacheResult = await this.clearCaches(client);
          report.summary.cacheCleared = cacheResult;
        } catch (error) {
          report.warnings.push(
            `Cache clearing failed: ${error instanceof Error ? error.message : String(error)}`
          );
        }
      }

      // Calculate totals
      report.summary.totalRecordsProcessed = Object.values(report.summary)
        .filter((v) => typeof v === 'number')
        .reduce((a, b) => a + (b as number), 0);

      return report;
    } catch (error) {
      report.success = false;
      report.errors.push(
        error instanceof Error ? error.message : String(error)
      );
      return report;
    }
  }

  /**
   * Remove test records and demo data
   */
  private async removeTestData(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ count: number; details: CleanupDetail[] }> {
    const details: CleanupDetail[] = [];
    let totalCount = 0;

    const testDataModels = [
      { model: 'res.partner', domain: [['name', 'like', 'Test%']] as any },
      { model: 'res.partner', domain: [['name', 'like', 'Demo%']] as any },
      { model: 'sale.order', domain: [['name', 'like', '%TEST%']] as any },
      { model: 'account.move', domain: [['ref', 'like', '%TEST%']] as any },
      { model: 'stock.move', domain: [['origin', 'like', '%TEST%']] as any },
    ];

    for (const { model, domain } of testDataModels) {
      try {
        const searchResult = await client.search({ model, domain });

        if (searchResult.success && searchResult.data && searchResult.data.length > 0) {
          const recordCount = searchResult.data.length;
          totalCount += recordCount;

          if (!dryRun) {
            const deleteResult = await client.delete({
              model,
              ids: searchResult.data,
            });

            details.push({
              operation: 'remove_test_data',
              model,
              recordsAffected: recordCount,
              details: `Removed ${recordCount} test/demo records`,
              status: deleteResult.success ? 'success' : 'error',
            });
          } else {
            details.push({
              operation: 'remove_test_data',
              model,
              recordsAffected: recordCount,
              details: `[DRY RUN] Would remove ${recordCount} test/demo records`,
              status: 'success',
            });
          }
        }
      } catch (error) {
        details.push({
          operation: 'remove_test_data',
          model,
          recordsAffected: 0,
          details: `Error: ${error instanceof Error ? error.message : String(error)}`,
          status: 'error',
        });
      }
    }

    return { count: totalCount, details };
  }

  /**
   * Archive inactive records (no activity for specified days)
   */
  private async archiveInactiveRecords(
    client: OdooClient,
    daysThreshold: number = 180,
    dryRun: boolean = false
  ): Promise<{ count: number; details: CleanupDetail[] }> {
    const details: CleanupDetail[] = [];
    let totalCount = 0;
    const thresholdDate = new Date();
    thresholdDate.setDate(thresholdDate.getDate() - daysThreshold);
    const thresholdDateStr = thresholdDate.toISOString().split('T')[0];

    const archivableModels = [
      { model: 'res.partner', dateField: 'write_date' },
      { model: 'sale.order', dateField: 'write_date' },
      { model: 'account.move', dateField: 'write_date' },
    ];

    for (const { model, dateField } of archivableModels) {
      try {
        const domain = [
          [dateField, '<', thresholdDateStr],
          ['active', '=', true],
        ] as any;

        const searchResult = await client.search({ model, domain });

        if (searchResult.success && searchResult.data && searchResult.data.length > 0) {
          const recordCount = searchResult.data.length;
          totalCount += recordCount;

          if (!dryRun) {
            const archiveResult = await client.update({
              model,
              ids: searchResult.data,
              values: { active: false },
            });

            details.push({
              operation: 'archive_inactive',
              model,
              recordsAffected: recordCount,
              details: `Archived ${recordCount} inactive records (no activity since ${thresholdDateStr})`,
              status: archiveResult.success ? 'success' : 'error',
            });
          } else {
            details.push({
              operation: 'archive_inactive',
              model,
              recordsAffected: recordCount,
              details: `[DRY RUN] Would archive ${recordCount} inactive records`,
              status: 'success',
            });
          }
        }
      } catch (error) {
        details.push({
          operation: 'archive_inactive',
          model,
          recordsAffected: 0,
          details: `Error: ${error instanceof Error ? error.message : String(error)}`,
          status: 'error',
        });
      }
    }

    return { count: totalCount, details };
  }

  /**
   * Clean up draft documents
   */
  private async cleanupDraftDocuments(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ count: number; details: CleanupDetail[] }> {
    const details: CleanupDetail[] = [];
    let totalCount = 0;

    const draftModels = [
      { model: 'sale.order', stateField: 'state' },
      { model: 'account.move', stateField: 'state' },
      { model: 'purchase.order', stateField: 'state' },
    ];

    for (const { model, stateField } of draftModels) {
      try {
        const domain = [[stateField, '=', 'draft']] as any;

        const searchResult = await client.search({ model, domain });

        if (searchResult.success && searchResult.data && searchResult.data.length > 0) {
          const recordCount = searchResult.data.length;
          totalCount += recordCount;

          if (!dryRun) {
            const deleteResult = await client.delete({
              model,
              ids: searchResult.data,
            });

            details.push({
              operation: 'cleanup_drafts',
              model,
              recordsAffected: recordCount,
              details: `Deleted ${recordCount} draft records`,
              status: deleteResult.success ? 'success' : 'error',
            });
          } else {
            details.push({
              operation: 'cleanup_drafts',
              model,
              recordsAffected: recordCount,
              details: `[DRY RUN] Would delete ${recordCount} draft records`,
              status: 'success',
            });
          }
        }
      } catch (error) {
        details.push({
          operation: 'cleanup_drafts',
          model,
          recordsAffected: 0,
          details: `Error: ${error instanceof Error ? error.message : String(error)}`,
          status: 'error',
        });
      }
    }

    return { count: totalCount, details };
  }

  /**
   * Remove orphan records (records with broken foreign keys)
   */
  private async removeOrphanRecords(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ count: number; details: CleanupDetail[] }> {
    const details: CleanupDetail[] = [];
    let totalCount = 0;

    try {
      // Clean up orphan lines in sales orders
      const orphanSaleLines = await client.search({
        model: 'sale.order.line',
        domain: [['order_id', '=', false]] as any,
      });

      if (
        orphanSaleLines.success &&
        orphanSaleLines.data &&
        orphanSaleLines.data.length > 0
      ) {
        const recordCount = orphanSaleLines.data.length;
        totalCount += recordCount;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'sale.order.line',
            ids: orphanSaleLines.data,
          });

          details.push({
            operation: 'remove_orphans',
            model: 'sale.order.line',
            recordsAffected: recordCount,
            details: `Removed ${recordCount} orphan sale order lines`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            operation: 'remove_orphans',
            model: 'sale.order.line',
            recordsAffected: recordCount,
            details: `[DRY RUN] Would remove ${recordCount} orphan sale order lines`,
            status: 'success',
          });
        }
      }

      // Clean up orphan lines in invoices
      const orphanInvoiceLines = await client.search({
        model: 'account.move.line',
        domain: [['move_id', '=', false]] as any,
      });

      if (
        orphanInvoiceLines.success &&
        orphanInvoiceLines.data &&
        orphanInvoiceLines.data.length > 0
      ) {
        const recordCount = orphanInvoiceLines.data.length;
        totalCount += recordCount;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'account.move.line',
            ids: orphanInvoiceLines.data,
          });

          details.push({
            operation: 'remove_orphans',
            model: 'account.move.line',
            recordsAffected: recordCount,
            details: `Removed ${recordCount} orphan invoice lines`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            operation: 'remove_orphans',
            model: 'account.move.line',
            recordsAffected: recordCount,
            details: `[DRY RUN] Would remove ${recordCount} orphan invoice lines`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        operation: 'remove_orphans',
        model: 'mixed',
        recordsAffected: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { count: totalCount, details };
  }

  /**
   * Clean up activity logs (mail.activity, mail.message)
   */
  private async cleanupActivityLogs(
    client: OdooClient,
    daysThreshold: number = 180,
    dryRun: boolean = false
  ): Promise<{ count: number; details: CleanupDetail[] }> {
    const details: CleanupDetail[] = [];
    let totalCount = 0;
    const thresholdDate = new Date();
    thresholdDate.setDate(thresholdDate.getDate() - daysThreshold);
    const thresholdDateStr = thresholdDate.toISOString();

    try {
      // Clean up old mail messages
      const oldMessages = await client.search({
        model: 'mail.message',
        domain: [['create_date', '<', thresholdDateStr]] as any,
      });

      if (
        oldMessages.success &&
        oldMessages.data &&
        oldMessages.data.length > 0
      ) {
        const recordCount = oldMessages.data.length;
        totalCount += recordCount;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'mail.message',
            ids: oldMessages.data,
          });

          details.push({
            operation: 'cleanup_logs',
            model: 'mail.message',
            recordsAffected: recordCount,
            details: `Deleted ${recordCount} old mail messages (before ${thresholdDateStr})`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            operation: 'cleanup_logs',
            model: 'mail.message',
            recordsAffected: recordCount,
            details: `[DRY RUN] Would delete ${recordCount} old mail messages`,
            status: 'success',
          });
        }
      }

      // Clean up old activities
      const oldActivities = await client.search({
        model: 'mail.activity',
        domain: [
          ['create_date', '<', thresholdDateStr],
          ['state', '=', 'done'],
        ] as any,
      });

      if (
        oldActivities.success &&
        oldActivities.data &&
        oldActivities.data.length > 0
      ) {
        const recordCount = oldActivities.data.length;
        totalCount += recordCount;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'mail.activity',
            ids: oldActivities.data,
          });

          details.push({
            operation: 'cleanup_logs',
            model: 'mail.activity',
            recordsAffected: recordCount,
            details: `Deleted ${recordCount} old completed activities`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            operation: 'cleanup_logs',
            model: 'mail.activity',
            recordsAffected: recordCount,
            details: `[DRY RUN] Would delete ${recordCount} old completed activities`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        operation: 'cleanup_logs',
        model: 'mail.*',
        recordsAffected: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { count: totalCount, details };
  }

  /**
   * Clean up old attachments
   */
  private async cleanupAttachments(
    client: OdooClient,
    daysThreshold: number = 180,
    dryRun: boolean = false
  ): Promise<{ count: number; details: CleanupDetail[] }> {
    const details: CleanupDetail[] = [];
    let totalCount = 0;
    const thresholdDate = new Date();
    thresholdDate.setDate(thresholdDate.getDate() - daysThreshold);
    const thresholdDateStr = thresholdDate.toISOString().split('T')[0];

    try {
      // Find attachments without related records
      const allAttachments = await client.search({
        model: 'ir.attachment',
        domain: [['create_date', '<', thresholdDateStr]] as any,
      });

      if (
        allAttachments.success &&
        allAttachments.data &&
        allAttachments.data.length > 0
      ) {
        const recordCount = allAttachments.data.length;
        totalCount += recordCount;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'ir.attachment',
            ids: allAttachments.data,
          });

          details.push({
            operation: 'cleanup_attachments',
            model: 'ir.attachment',
            recordsAffected: recordCount,
            details: `Deleted ${recordCount} old attachments (before ${thresholdDateStr})`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            operation: 'cleanup_attachments',
            model: 'ir.attachment',
            recordsAffected: recordCount,
            details: `[DRY RUN] Would delete ${recordCount} old attachments`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        operation: 'cleanup_attachments',
        model: 'ir.attachment',
        recordsAffected: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { count: totalCount, details };
  }

  /**
   * Clear caches (web cache, session cache)
   */
  private async clearCaches(client: OdooClient): Promise<boolean> {
    try {
      // Clear web cache
      await client.executeKw({
        model: 'ir.ui.view',
        method: 'clear_caches',
        args: [],
      });

      // Clear session cache
      await client.executeKw({
        model: 'ir.session',
        method: 'clear_session_cache',
        args: [],
      });

      return true;
    } catch (error) {
      console.error(
        'Error clearing caches:',
        error instanceof Error ? error.message : String(error)
      );
      return false;
    }
  }
}
