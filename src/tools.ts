/**
 * Odoo MCP Server - MCP Tools Implementation
 * Context-aware tools for comprehensive Odoo operations
 */

import { z } from 'zod';
import type { OdooClient } from './odoo-client';

// Zod schemas for tool validation
const SearchSchema = z.object({
  instance: z.string().describe('Odoo instance identifier (e.g., "production", "staging", "local")'),
  model: z.string().describe('Odoo model name (e.g., "res.partner", "sale.order", "account.move")'),
  domain: z.array(z.any()).optional().describe('Search domain filters (e.g., [[\'name\', \'like\', \'John\']])'),
  fields: z.array(z.string()).optional().describe('Fields to return'),
  limit: z.number().optional().describe('Maximum number of records'),
  offset: z.number().optional().describe('Number of records to skip'),
  order: z.string().optional().describe('Sort order (e.g., "name ASC, id DESC")'),
});

const CreateSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  values: z.record(z.any()).describe('Field values for the new record'),
  context: z.record(z.any()).optional().describe('Additional context'),
});

const UpdateSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  ids: z.array(z.number()).describe('Record IDs to update'),
  values: z.record(z.any()).describe('Field values to update'),
  context: z.record(z.any()).optional().describe('Additional context'),
});

const DeleteSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  ids: z.array(z.number()).describe('Record IDs to delete'),
});

const ReadSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  ids: z.array(z.number()).describe('Record IDs to read'),
  fields: z.array(z.string()).optional().describe('Fields to return'),
});

const ExecuteSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  method: z.string().describe('Method name to execute'),
  args: z.array(z.any()).optional().describe('Positional arguments'),
  kwargs: z.record(z.any()).optional().describe('Keyword arguments'),
  context: z.record(z.any()).optional().describe('Additional context'),
});

const ReportSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  reportName: z.string().describe('Report technical name (e.g., "account.report_invoice")'),
  ids: z.array(z.number()).describe('Record IDs for the report'),
  data: z.record(z.any()).optional().describe('Additional report data'),
});

const WorkflowSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  ids: z.array(z.number()).describe('Record IDs'),
  action: z.string().describe('Action/button method name (e.g., "action_confirm", "action_post")'),
  context: z.record(z.any()).optional().describe('Additional context'),
});

const ModelMetadataSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
});

const CountSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  domain: z.array(z.any()).optional().describe('Search domain filters'),
});

/**
 * MCP Tools for Odoo operations
 */
export const tools = [
  {
    name: 'odoo_search',
    description: 'Search for Odoo records with domain filters. Returns record IDs matching the criteria.',
    inputSchema: SearchSchema,
  },
  {
    name: 'odoo_search_read',
    description: 'Search and read Odoo records in one operation. Returns full record data.',
    inputSchema: SearchSchema,
  },
  {
    name: 'odoo_read',
    description: 'Read specific Odoo records by IDs. Returns detailed field values.',
    inputSchema: ReadSchema,
  },
  {
    name: 'odoo_create',
    description: 'Create a new Odoo record. Returns the ID of the created record.',
    inputSchema: CreateSchema,
  },
  {
    name: 'odoo_update',
    description: 'Update existing Odoo records. Returns true on success.',
    inputSchema: UpdateSchema,
  },
  {
    name: 'odoo_delete',
    description: 'Delete Odoo records. Returns true on success. Use with caution!',
    inputSchema: DeleteSchema,
  },
  {
    name: 'odoo_execute',
    description: 'Execute arbitrary method on Odoo model. For advanced operations and custom methods.',
    inputSchema: ExecuteSchema,
  },
  {
    name: 'odoo_count',
    description: 'Count records matching domain filters. Returns the total count.',
    inputSchema: CountSchema,
  },
  {
    name: 'odoo_workflow_action',
    description: 'Execute workflow action/button on records (e.g., confirm sale order, post invoice).',
    inputSchema: WorkflowSchema,
  },
  {
    name: 'odoo_generate_report',
    description: 'Generate PDF report for records. Returns base64-encoded PDF.',
    inputSchema: ReportSchema,
  },
  {
    name: 'odoo_get_model_metadata',
    description: 'Get model metadata including field definitions, types, and relationships.',
    inputSchema: ModelMetadataSchema,
  },
];

/**
 * Tool execution handlers
 */
export class OdooTools {
  constructor(private getClient: (instance: string) => Promise<OdooClient>) {}

  async executeTool(name: string, args: any): Promise<any> {
    const client = await this.getClient(args.instance);

    switch (name) {
      case 'odoo_search':
        return this.handleSearch(client, args);

      case 'odoo_search_read':
        return this.handleSearchRead(client, args);

      case 'odoo_read':
        return this.handleRead(client, args);

      case 'odoo_create':
        return this.handleCreate(client, args);

      case 'odoo_update':
        return this.handleUpdate(client, args);

      case 'odoo_delete':
        return this.handleDelete(client, args);

      case 'odoo_execute':
        return this.handleExecute(client, args);

      case 'odoo_count':
        return this.handleCount(client, args);

      case 'odoo_workflow_action':
        return this.handleWorkflowAction(client, args);

      case 'odoo_generate_report':
        return this.handleGenerateReport(client, args);

      case 'odoo_get_model_metadata':
        return this.handleGetModelMetadata(client, args);

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  }

  private async handleSearch(client: OdooClient, args: any) {
    const result = await client.search({
      model: args.model,
      domain: args.domain,
      fields: args.fields,
      limit: args.limit,
      offset: args.offset,
      order: args.order,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Search failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            ids: result.data,
            count: result.data?.length || 0,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleSearchRead(client: OdooClient, args: any) {
    const result = await client.searchRead({
      model: args.model,
      domain: args.domain,
      fields: args.fields,
      limit: args.limit,
      offset: args.offset,
      order: args.order,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Search read failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            records: result.data,
            count: result.data?.length || 0,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleRead(client: OdooClient, args: any) {
    const result = await client.read({
      model: args.model,
      ids: args.ids,
      fields: args.fields,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Read failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            records: result.data,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleCreate(client: OdooClient, args: any) {
    const result = await client.create({
      model: args.model,
      values: args.values,
      context: args.context,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Create failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            id: result.data,
            success: true,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleUpdate(client: OdooClient, args: any) {
    const result = await client.update({
      model: args.model,
      ids: args.ids,
      values: args.values,
      context: args.context,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Update failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: result.data,
            updated_count: args.ids.length,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleDelete(client: OdooClient, args: any) {
    const result = await client.delete({
      model: args.model,
      ids: args.ids,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Delete failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: result.data,
            deleted_count: args.ids.length,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleExecute(client: OdooClient, args: any) {
    const result = await client.executeKw({
      model: args.model,
      method: args.method,
      args: args.args,
      kwargs: args.kwargs,
      context: args.context,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Execute failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            result: result.data,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleCount(client: OdooClient, args: any) {
    const result = await client.count({
      model: args.model,
      domain: args.domain,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Count failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            count: result.data,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleWorkflowAction(client: OdooClient, args: any) {
    const result = await client.executeAction({
      model: args.model,
      ids: args.ids,
      action: args.action,
      context: args.context,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Workflow action failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            result: result.data,
            executed_on: args.ids,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleGenerateReport(client: OdooClient, args: any) {
    const result = await client.generateReport({
      reportName: args.reportName,
      ids: args.ids,
      data: args.data,
    });

    if (!result.success) {
      throw new Error(result.error?.message || 'Report generation failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            pdf_base64: result.data,
            report_name: args.reportName,
            record_ids: args.ids,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }

  private async handleGetModelMetadata(client: OdooClient, args: any) {
    const result = await client.getModelMetadata(args.model);

    if (!result.success) {
      throw new Error(result.error?.message || 'Get metadata failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            model: result.data,
            metadata: result.metadata,
          }, null, 2),
        },
      ],
    };
  }
}

/**
 * Context-aware helper prompts for AI
 */
export const contextPrompts = [
  {
    name: 'odoo_common_models',
    description: 'List of commonly used Odoo models',
    content: `
# Common Odoo Models (v17-19)

## Sales & CRM
- sale.order - Sales Orders
- sale.order.line - Sales Order Lines
- crm.lead - CRM Leads/Opportunities
- crm.team - Sales Teams

## Accounting & Invoicing
- account.move - Invoices & Bills
- account.move.line - Invoice/Bill Lines
- account.payment - Payments
- account.journal - Journals
- account.account - Chart of Accounts

## Inventory & Manufacturing
- stock.picking - Transfers
- stock.move - Stock Moves
- stock.warehouse - Warehouses
- stock.location - Locations
- product.product - Products (variants)
- product.template - Product Templates

## Partners & Contacts
- res.partner - Contacts/Customers/Vendors
- res.company - Companies
- res.users - Users

## HR & Employees
- hr.employee - Employees
- hr.department - Departments
- hr.leave - Time Off

## Projects & Tasks
- project.project - Projects
- project.task - Tasks

## Purchase
- purchase.order - Purchase Orders
- purchase.order.line - Purchase Order Lines
    `,
  },
  {
    name: 'odoo_domain_filters',
    description: 'Guide for Odoo domain filter syntax',
    content: `
# Odoo Domain Filter Examples

## Basic Operators
- ['name', '=', 'John'] - Exact match
- ['name', '!=', 'John'] - Not equal
- ['age', '>', 18] - Greater than
- ['age', '>=', 18] - Greater than or equal
- ['age', '<', 65] - Less than
- ['age', '<=', 65] - Less than or equal

## String Operators
- ['name', 'like', 'John'] - Contains (case-sensitive)
- ['name', 'ilike', 'john'] - Contains (case-insensitive)
- ['email', '=like', '%@example.com'] - Pattern match
- ['name', '=ilike', 'john%'] - Pattern match (case-insensitive)

## List Operators
- ['state', 'in', ['draft', 'posted']] - In list
- ['state', 'not in', ['cancel', 'draft']] - Not in list

## Logical Operators
- ['&', ['name', '=', 'John'], ['age', '>', 18]] - AND
- ['|', ['name', '=', 'John'], ['name', '=', 'Jane']] - OR
- ['!', ['state', '=', 'cancel']] - NOT

## Complex Example
[
  '&',
  ['state', '=', 'sale'],
  '|',
  ['amount_total', '>', 1000],
  ['partner_id.country_id.code', '=', 'US']
]
    `,
  },
];
