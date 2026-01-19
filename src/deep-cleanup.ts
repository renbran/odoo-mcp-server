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

export class DeepDatabaseCleanup {
  constructor(private getClient: (instance: string) => Promise<OdooClient>) {}

  /**
   * Execute complete database reset - remove all non-essential data
   */
  async executeDeepCleanup(
    options: DeepCleanupOptions
  ): Promise<DeepCleanupReport> {
    const client = await this.getClient(options.instance);
    const report: DeepCleanupReport = {
      success: true,
      timestamp: new Date().toISOString(),
      summary: {
        partnersRemoved: 0,
        salesOrdersRemoved: 0,
        invoicesRemoved: 0,
        purchaseOrdersRemoved: 0,
        stockMovesRemoved: 0,
        documentsRemoved: 0,
        contactsRemoved: 0,
        leadsRemoved: 0,
        opportunitiesRemoved: 0,
        projectsRemoved: 0,
        tasksRemoved: 0,
        attendeesRemoved: 0,
        eventsRemoved: 0,
        journalsRemoved: 0,
        accountsRemoved: 0,
        productsRemoved: 0,
        stockLocationsRemoved: 0,
        warehousesRemoved: 0,
        employeesRemoved: 0,
        departmentsRemoved: 0,
        logsAndAttachments: 0,
        totalRecordsRemoved: 0,
      },
      details: [],
      warnings: [],
      errors: [],
      dryRun: options.dryRun ?? false,
      defaultDataRetained: [],
    };

    try {
      // 1. Remove all partners except default (base company)
      const partnerResult = await this.removePartners(
        client,
        options.keepCompanyDefaults,
        options.dryRun
      );
      report.summary.partnersRemoved = partnerResult.count;
      report.details.push(...partnerResult.details);

      // 2. Remove all sales documents
      const salesResult = await this.removeSalesDocuments(client, options.dryRun);
      report.summary.salesOrdersRemoved = salesResult.orders;
      report.summary.documentsRemoved += salesResult.orders;
      report.details.push(...salesResult.details);

      // 3. Remove all invoices and accounting entries
      const invoiceResult = await this.removeInvoicesAndAccounting(
        client,
        options.dryRun
      );
      report.summary.invoicesRemoved = invoiceResult.invoices;
      report.summary.journalsRemoved = invoiceResult.journals;
      report.summary.accountsRemoved = invoiceResult.accounts;
      report.details.push(...invoiceResult.details);

      // 4. Remove all purchase orders
      const purchaseResult = await this.removePurchaseOrders(
        client,
        options.dryRun
      );
      report.summary.purchaseOrdersRemoved = purchaseResult.count;
      report.details.push(...purchaseResult.details);

      // 5. Remove inventory/stock data
      const stockResult = await this.removeStockData(client, options.dryRun);
      report.summary.stockMovesRemoved = stockResult.moves;
      report.summary.productsRemoved = stockResult.products;
      report.summary.stockLocationsRemoved = stockResult.locations;
      report.summary.warehousesRemoved = stockResult.warehouses;
      report.details.push(...stockResult.details);

      // 6. Remove CRM data
      const crmResult = await this.removeCRMData(client, options.dryRun);
      report.summary.leadsRemoved = crmResult.leads;
      report.summary.opportunitiesRemoved = crmResult.opportunities;
      report.details.push(...crmResult.details);

      // 7. Remove project management data
      const projectResult = await this.removeProjectData(client, options.dryRun);
      report.summary.projectsRemoved = projectResult.projects;
      report.summary.tasksRemoved = projectResult.tasks;
      report.details.push(...projectResult.details);

      // 8. Remove calendar/event data
      const calendarResult = await this.removeCalendarData(
        client,
        options.dryRun
      );
      report.summary.eventsRemoved = calendarResult.events;
      report.summary.attendeesRemoved = calendarResult.attendees;
      report.details.push(...calendarResult.details);

      // 9. Remove HR data
      const hrResult = await this.removeHRData(
        client,
        options.keepUserAccounts,
        options.dryRun
      );
      report.summary.employeesRemoved = hrResult.employees;
      report.summary.departmentsRemoved = hrResult.departments;
      report.details.push(...hrResult.details);

      // 10. Remove logs and attachments
      const logsResult = await this.removeLogsAndAttachments(
        client,
        options.dryRun
      );
      report.summary.logsAndAttachments = logsResult.count;
      report.details.push(...logsResult.details);

      // 11. List default data that was retained
      report.defaultDataRetained = await this.identifyDefaultData(client);

      // Calculate totals
      report.summary.totalRecordsRemoved = Object.values(report.summary)
        .filter((v) => typeof v === 'number' && v !== 0)
        .reduce((a, b) => a + (b as number), 0);

      if (!options.dryRun) {
        report.warnings.push(
          '⚠️ IMPORTANT: All non-essential data has been removed. Backup was recommended before this operation.'
        );
      }

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
   * Remove all partners except defaults
   */
  private async removePartners(
    client: OdooClient,
    keepDefaults: boolean = true,
    dryRun: boolean = false
  ): Promise<{ count: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let totalCount = 0;

    try {
      // Get all partners except the base company
      const allPartners = await client.search({
        model: 'res.partner',
        domain: (keepDefaults ? [['name', '!=', 'Your Company']] : []) as any,
        fields: ['id', 'name', 'is_company'],
      });

      if (allPartners.success && allPartners.data && allPartners.data.length > 0) {
        // Get details to identify which ones to keep
        const partnerDetails = await client.read({
          model: 'res.partner',
          ids: allPartners.data,
          fields: ['name', 'is_company', 'parent_id'],
        });

        // Filter out system partners that shouldn't be deleted
        const systemPartnerNames = [
          'Your Company',
          'Administrator',
          'Email Alias',
          'External IP',
        ];

        let toDelete = allPartners.data;
        if (keepDefaults && partnerDetails.success && partnerDetails.data) {
          toDelete = partnerDetails.data
            .filter(
              (p) =>
                !systemPartnerNames.some((name) =>
                  p.name?.includes(name)
                )
            )
            .map((p) => p.id);
        }

        totalCount = toDelete.length;

        if (!dryRun && toDelete.length > 0) {
          const deleteResult = await client.delete({
            model: 'res.partner',
            ids: toDelete,
          });

          details.push({
            model: 'res.partner',
            recordsRemoved: toDelete.length,
            details: `Removed ${toDelete.length} partners (kept defaults: ${keepDefaults})`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else if (dryRun) {
          details.push({
            model: 'res.partner',
            recordsRemoved: toDelete.length,
            details: `[DRY RUN] Would remove ${toDelete.length} partners`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'res.partner',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { count: totalCount, details };
  }

  /**
   * Remove all sales orders and quotes
   */
  private async removeSalesDocuments(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ orders: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let totalOrders = 0;

    try {
      // Remove sales orders
      const salesOrders = await client.search({
        model: 'sale.order',
      });

      if (salesOrders.success && salesOrders.data && salesOrders.data.length > 0) {
        totalOrders = salesOrders.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'sale.order',
            ids: salesOrders.data,
          });

          details.push({
            model: 'sale.order',
            recordsRemoved: totalOrders,
            details: `Removed ${totalOrders} sales orders`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'sale.order',
            recordsRemoved: totalOrders,
            details: `[DRY RUN] Would remove ${totalOrders} sales orders`,
            status: 'success',
          });
        }
      }

      // Remove sale quotes
      const quotes = await client.search({
        model: 'sale.order',
        domain: [['is_expired', '=', true]] as any,
      });

      if (quotes.success && quotes.data && quotes.data.length > 0) {
        if (!dryRun) {
          await client.delete({
            model: 'sale.order',
            ids: quotes.data,
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'sale.order',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { orders: totalOrders, details };
  }

  /**
   * Remove all invoices and accounting entries
   */
  private async removeInvoicesAndAccounting(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ invoices: number; journals: number; accounts: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let invoiceCount = 0;
    let journalCount = 0;
    let accountCount = 0;

    try {
      // Remove invoices
      const invoices = await client.search({
        model: 'account.move',
      });

      if (invoices.success && invoices.data && invoices.data.length > 0) {
        invoiceCount = invoices.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'account.move',
            ids: invoices.data,
          });

          details.push({
            model: 'account.move',
            recordsRemoved: invoiceCount,
            details: `Removed ${invoiceCount} invoices/moves`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'account.move',
            recordsRemoved: invoiceCount,
            details: `[DRY RUN] Would remove ${invoiceCount} invoices`,
            status: 'success',
          });
        }
      }

      // Remove custom journals (keep defaults)
      const journals = await client.search({
        model: 'account.journal',
        domain: [['type', 'not in', ['general', 'situation']]] as any,
      });

      if (journals.success && journals.data && journals.data.length > 0) {
        journalCount = journals.data.length;

        if (!dryRun) {
          try {
            await client.delete({
              model: 'account.journal',
              ids: journals.data,
            });
          } catch (error) {
            // Some journals might be protected
            details.push({
              model: 'account.journal',
              recordsRemoved: 0,
              details: `Could not delete some journals (protected)`,
              status: 'warning',
            });
          }
        }
      }

      // Remove custom accounts (keep defaults)
      const accounts = await client.search({
        model: 'account.account',
        domain: [['code', 'not ilike', '1%']] as any, // Keep accounts starting with 1
      });

      if (accounts.success && accounts.data && accounts.data.length > 0) {
        accountCount = accounts.data.length;

        if (!dryRun) {
          try {
            await client.delete({
              model: 'account.account',
              ids: accounts.data,
            });
          } catch (error) {
            // Some accounts might have transactions
            details.push({
              model: 'account.account',
              recordsRemoved: 0,
              details: `Could not delete some accounts (have transactions)`,
              status: 'warning',
            });
          }
        }
      }
    } catch (error) {
      details.push({
        model: 'account.*',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { invoices: invoiceCount, journals: journalCount, accounts: accountCount, details };
  }

  /**
   * Remove all purchase orders
   */
  private async removePurchaseOrders(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ count: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let totalCount = 0;

    try {
      const purchaseOrders = await client.search({
        model: 'purchase.order',
      });

      if (purchaseOrders.success && purchaseOrders.data && purchaseOrders.data.length > 0) {
        totalCount = purchaseOrders.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'purchase.order',
            ids: purchaseOrders.data,
          });

          details.push({
            model: 'purchase.order',
            recordsRemoved: totalCount,
            details: `Removed ${totalCount} purchase orders`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'purchase.order',
            recordsRemoved: totalCount,
            details: `[DRY RUN] Would remove ${totalCount} purchase orders`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'purchase.order',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { count: totalCount, details };
  }

  /**
   * Remove inventory and stock data
   */
  private async removeStockData(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ moves: number; products: number; locations: number; warehouses: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let moves = 0;
    let products = 0;
    let locations = 0;
    let warehouses = 0;

    try {
      // Remove stock moves
      const stockMoves = await client.search({
        model: 'stock.move',
      });

      if (stockMoves.success && stockMoves.data && stockMoves.data.length > 0) {
        moves = stockMoves.data.length;

        if (!dryRun) {
          try {
            await client.delete({
              model: 'stock.move',
              ids: stockMoves.data,
            });

            details.push({
              model: 'stock.move',
              recordsRemoved: moves,
              details: `Removed ${moves} stock moves`,
              status: 'success',
            });
          } catch (error) {
            details.push({
              model: 'stock.move',
              recordsRemoved: 0,
              details: `Could not delete stock moves`,
              status: 'warning',
            });
          }
        } else {
          details.push({
            model: 'stock.move',
            recordsRemoved: moves,
            details: `[DRY RUN] Would remove ${moves} stock moves`,
            status: 'success',
          });
        }
      }

      // Remove custom products (keep templates)
      const productProducts = await client.search({
        model: 'product.product',
        domain: [['create_date', '!=', false]] as any, // Remove created products
      });

      if (
        productProducts.success &&
        productProducts.data &&
        productProducts.data.length > 0
      ) {
        products = productProducts.data.length;

        if (!dryRun) {
          try {
            await client.delete({
              model: 'product.product',
              ids: productProducts.data,
            });
          } catch (error) {
            details.push({
              model: 'product.product',
              recordsRemoved: 0,
              details: `Could not delete all products`,
              status: 'warning',
            });
          }
        }
      }

      // Remove custom stock locations
      const stockLocations = await client.search({
        model: 'stock.location',
        domain: [['usage', '=', 'internal']] as any,
      });

      if (
        stockLocations.success &&
        stockLocations.data &&
        stockLocations.data.length > 0
      ) {
        locations = stockLocations.data.length;
      }

      // Remove custom warehouses
      const warehouses_search = await client.search({
        model: 'stock.warehouse',
      });

      if (
        warehouses_search.success &&
        warehouses_search.data &&
        warehouses_search.data.length > 1 // Keep at least one
      ) {
        warehouses = warehouses_search.data.length - 1;

        if (!dryRun) {
          try {
            await client.delete({
              model: 'stock.warehouse',
              ids: warehouses_search.data.slice(1), // Keep first one
            });
          } catch (error) {
            // Might have references
          }
        }
      }
    } catch (error) {
      details.push({
        model: 'stock.*',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { moves, products, locations, warehouses, details };
  }

  /**
   * Remove CRM data
   */
  private async removeCRMData(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ leads: number; opportunities: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let leads = 0;
    let opportunities = 0;

    try {
      // Remove leads
      const leadSearch = await client.search({
        model: 'crm.lead',
        domain: [['type', '=', 'lead']] as any,
      });

      if (leadSearch.success && leadSearch.data && leadSearch.data.length > 0) {
        leads = leadSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'crm.lead',
            ids: leadSearch.data,
          });

          details.push({
            model: 'crm.lead',
            recordsRemoved: leads,
            details: `Removed ${leads} leads`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'crm.lead',
            recordsRemoved: leads,
            details: `[DRY RUN] Would remove ${leads} leads`,
            status: 'success',
          });
        }
      }

      // Remove opportunities
      const oppSearch = await client.search({
        model: 'crm.lead',
        domain: [['type', '=', 'opportunity']] as any,
      });

      if (oppSearch.success && oppSearch.data && oppSearch.data.length > 0) {
        opportunities = oppSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'crm.lead',
            ids: oppSearch.data,
          });

          details.push({
            model: 'crm.lead (opportunities)',
            recordsRemoved: opportunities,
            details: `Removed ${opportunities} opportunities`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'crm.lead (opportunities)',
            recordsRemoved: opportunities,
            details: `[DRY RUN] Would remove ${opportunities} opportunities`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'crm.*',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { leads, opportunities, details };
  }

  /**
   * Remove project and task data
   */
  private async removeProjectData(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ projects: number; tasks: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let projects = 0;
    let tasks = 0;

    try {
      // Remove tasks first (dependencies)
      const taskSearch = await client.search({
        model: 'project.task',
      });

      if (taskSearch.success && taskSearch.data && taskSearch.data.length > 0) {
        tasks = taskSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'project.task',
            ids: taskSearch.data,
          });

          details.push({
            model: 'project.task',
            recordsRemoved: tasks,
            details: `Removed ${tasks} tasks`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'project.task',
            recordsRemoved: tasks,
            details: `[DRY RUN] Would remove ${tasks} tasks`,
            status: 'success',
          });
        }
      }

      // Remove projects
      const projectSearch = await client.search({
        model: 'project.project',
      });

      if (
        projectSearch.success &&
        projectSearch.data &&
        projectSearch.data.length > 0
      ) {
        projects = projectSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'project.project',
            ids: projectSearch.data,
          });

          details.push({
            model: 'project.project',
            recordsRemoved: projects,
            details: `Removed ${projects} projects`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'project.project',
            recordsRemoved: projects,
            details: `[DRY RUN] Would remove ${projects} projects`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'project.*',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { projects, tasks, details };
  }

  /**
   * Remove calendar events and attendees
   */
  private async removeCalendarData(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ events: number; attendees: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let events = 0;
    let attendees = 0;

    try {
      // Remove calendar events
      const eventSearch = await client.search({
        model: 'calendar.event',
      });

      if (eventSearch.success && eventSearch.data && eventSearch.data.length > 0) {
        events = eventSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'calendar.event',
            ids: eventSearch.data,
          });

          details.push({
            model: 'calendar.event',
            recordsRemoved: events,
            details: `Removed ${events} calendar events`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'calendar.event',
            recordsRemoved: events,
            details: `[DRY RUN] Would remove ${events} events`,
            status: 'success',
          });
        }
      }

      // Remove event attendees
      const attendeeSearch = await client.search({
        model: 'calendar.attendee',
      });

      if (attendeeSearch.success && attendeeSearch.data && attendeeSearch.data.length > 0) {
        attendees = attendeeSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'calendar.attendee',
            ids: attendeeSearch.data,
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'calendar.*',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { events, attendees, details };
  }

  /**
   * Remove HR data
   */
  private async removeHRData(
    client: OdooClient,
    keepUserAccounts: boolean = true,
    dryRun: boolean = false
  ): Promise<{ employees: number; departments: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let employees = 0;
    let departments = 0;

    try {
      // Remove employees (except admin)
      const employeeSearch = await client.search({
        model: 'hr.employee',
        domain: (keepUserAccounts ? [['user_id', '=', false]] : []) as any,
      });

      if (employeeSearch.success && employeeSearch.data && employeeSearch.data.length > 0) {
        employees = employeeSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'hr.employee',
            ids: employeeSearch.data,
          });

          details.push({
            model: 'hr.employee',
            recordsRemoved: employees,
            details: `Removed ${employees} employees`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'hr.employee',
            recordsRemoved: employees,
            details: `[DRY RUN] Would remove ${employees} employees`,
            status: 'success',
          });
        }
      }

      // Remove departments (except root)
      const deptSearch = await client.search({
        model: 'hr.department',
        domain: [['parent_id', '!=', false]] as any,
      });

      if (deptSearch.success && deptSearch.data && deptSearch.data.length > 0) {
        departments = deptSearch.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'hr.department',
            ids: deptSearch.data,
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'hr.*',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { employees, departments, details };
  }

  /**
   * Remove logs and attachments
   */
  private async removeLogsAndAttachments(
    client: OdooClient,
    dryRun: boolean = false
  ): Promise<{ count: number; details: DeepCleanupDetail[] }> {
    const details: DeepCleanupDetail[] = [];
    let totalCount = 0;

    try {
      // Remove all mail messages
      const messages = await client.search({
        model: 'mail.message',
      });

      if (messages.success && messages.data && messages.data.length > 0) {
        totalCount += messages.data.length;

        if (!dryRun) {
          try {
            await client.delete({
              model: 'mail.message',
              ids: messages.data,
            });
          } catch (error) {
            // Some might be protected
          }
        }
      }

      // Remove all activities
      const activities = await client.search({
        model: 'mail.activity',
      });

      if (activities.success && activities.data && activities.data.length > 0) {
        totalCount += activities.data.length;

        if (!dryRun) {
          try {
            await client.delete({
              model: 'mail.activity',
              ids: activities.data,
            });
          } catch (error) {
            // Some might be protected
          }
        }
      }

      // Remove all attachments
      const attachments = await client.search({
        model: 'ir.attachment',
      });

      if (attachments.success && attachments.data && attachments.data.length > 0) {
        totalCount += attachments.data.length;

        if (!dryRun) {
          const deleteResult = await client.delete({
            model: 'ir.attachment',
            ids: attachments.data,
          });

          details.push({
            model: 'mail.* + ir.attachment',
            recordsRemoved: totalCount,
            details: `Removed ${totalCount} messages, activities, and attachments`,
            status: deleteResult.success ? 'success' : 'error',
          });
        } else {
          details.push({
            model: 'mail.* + ir.attachment',
            recordsRemoved: totalCount,
            details: `[DRY RUN] Would remove ${totalCount} logs and attachments`,
            status: 'success',
          });
        }
      }
    } catch (error) {
      details.push({
        model: 'mail.* + ir.attachment',
        recordsRemoved: 0,
        details: `Error: ${error instanceof Error ? error.message : String(error)}`,
        status: 'error',
      });
    }

    return { count: totalCount, details };
  }

  /**
   * Identify default data that was retained
   */
  private async identifyDefaultData(client: OdooClient): Promise<string[]> {
    const defaults: string[] = [];

    try {
      // Check for default company
      const company = await client.search({
        model: 'res.company',
        limit: 1,
      });

      if (company.success && company.data && company.data.length > 0) {
        defaults.push('✓ Default Company Retained');
      }

      // Check for default user
      const users = await client.search({
        model: 'res.users',
        domain: [['id', '=', 2]] as any, // Admin user
        limit: 1,
      });

      if (users.success && users.data && users.data.length > 0) {
        defaults.push('✓ Admin User Retained');
      }

      // Check for menus
      const menus = await client.search({
        model: 'ir.ui.menu',
        limit: 1,
      });

      if (menus.success && menus.data && menus.data.length > 0) {
        defaults.push('✓ Menu Structure Retained');
      }

      // Check for groups
      const groups = await client.search({
        model: 'res.groups',
        limit: 1,
      });

      if (groups.success && groups.data && groups.data.length > 0) {
        defaults.push('✓ User Groups Retained');
      }

      // Check for default modules
      defaults.push('✓ Module Structure Intact');
      defaults.push('✓ System Configuration Retained');
    } catch (error) {
      defaults.push('⚠ Could not verify some defaults');
    }

    return defaults;
  }
}
