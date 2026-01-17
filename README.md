# Odoo MCP Server - Property Deal Management

Production-grade Model Context Protocol (MCP) server for Odoo 17-19 with comprehensive property deal management capabilities.

## 🎯 Project Overview

This project provides:
- **MCP Server**: Enables AI assistants to interact with Odoo instances via Model Context Protocol
- **Odoo Client**: Production-grade XML-RPC client with retry logic and error handling
- **Property Deals Module**: Comprehensive real estate deal tracking and management
- **Multi-Instance Support**: Manage multiple Odoo instances from a single MCP server

## 📋 Features

### MCP Server Features
✅ Multi-instance Odoo support  
✅ Context-aware prompts and operations  
✅ Comprehensive error handling and logging  
✅ Automatic retry logic (configurable)  
✅ Support for all Odoo models and operations  
✅ Type-safe TypeScript implementation  

### Property Deal Management Features
✅ Deal lifecycle tracking (Primary, Secondary, Exclusive, Rental)  
✅ Multi-buyer support (Primary & Secondary buyers)  
✅ Financial tracking (VAT, commissions, totals)  
✅ Document repository (KYC, contracts, passports)  
✅ Commission integration  
✅ Booking date management  
✅ Automated bill generation (bypass POs)  
✅ Advanced filtering and reporting  

## 🚀 Getting Started

### Prerequisites
- Node.js >= 18.0.0
- npm or yarn
- Odoo 17 or later (local or cloud instance)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd odoo-mcp-server
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your Odoo credentials
# For local development: http://localhost:8069
# For Odoo.com: https://yourcompany.odoo.com
```

4. **Build the project**
```bash
npm run build
```

## 📖 Development Guide

### Available npm Scripts

```bash
# Development
npm run dev              # Start MCP server with hot reload
npm run dev:watch       # Watch TypeScript files and rebuild
npm run build           # Build TypeScript to JavaScript

# Running
npm start               # Run the built MCP server

# Testing
npm test                # Run all tests
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Generate coverage report

# Code Quality
npm run lint            # Check code style
npm run lint:fix        # Fix code style issues
npm run type-check      # Check TypeScript types
npm run type-check:watch # Watch and check types

# Maintenance
npm run clean           # Remove build artifacts
```

## 🔧 Project Structure

```
odoo-mcp-server/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── odoo-client.ts        # Odoo XML-RPC client
│   ├── tools.ts              # MCP tools implementation
│   └── types.ts              # TypeScript type definitions
├── deals_management/         # Odoo 17 property deals module
│   ├── models/
│   │   ├── __init__.py
│   │   └── sale_order_deals.py
│   ├── views/
│   │   ├── deals_views.xml
│   │   ├── commission_line_views.xml
│   │   └── deals_menu.xml
│   ├── security/
│   │   └── ir.model.access.csv
│   ├── __init__.py
│   └── __manifest__.py
├── package.json              # Node.js dependencies
├── tsconfig.json            # TypeScript configuration
├── jest.config.js           # Testing configuration
├── .eslintrc.json           # Linting configuration
├── .env.example             # Environment template
└── README.md               # This file
```

## 🔌 Using the MCP Server

### Environment Configuration

#### Single Instance (Development)
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_dev
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

#### Multiple Instances (Production)
```bash
ODOO_INSTANCES={
  "production": {
    "url": "https://odoo.yourcompany.com",
    "db": "odoo_production",
    "username": "admin",
    "password": "secure_password"
  },
  "staging": {
    "url": "https://staging.odoo.com",
    "db": "odoo_staging",
    "username": "admin",
    "password": "secure_password"
  }
}
```

### Available MCP Tools

#### Search & Read Operations
- `odoo_search` - Find records matching criteria
- `odoo_search_read` - Search and read in one operation
- `odoo_read` - Read specific records by ID
- `odoo_count` - Count records matching domain

#### Create, Update, Delete
- `odoo_create` - Create new records
- `odoo_update` - Update existing records
- `odoo_delete` - Delete records

#### Advanced Operations
- `odoo_execute` - Call model methods
- `odoo_workflow` - Trigger state transitions
- `odoo_model_info` - Get field and model metadata
- `odoo_report` - Generate/fetch reports

### Example: Search for Property Deals

```typescript
{
  "tool": "odoo_search_read",
  "params": {
    "instance": "production",
    "model": "sale.order",
    "domain": [
      ["sales_type", "=", "primary"],
      ["state", "!=", "cancel"]
    ],
    "fields": [
      "name",
      "primary_buyer_id",
      "deal_sales_value",
      "booking_date"
    ],
    "limit": 10,
    "order": "booking_date DESC"
  }
}
```

### Example: Create a Deal

```typescript
{
  "tool": "odoo_create",
  "params": {
    "instance": "production",
    "model": "sale.order",
    "values": {
      "partner_id": 1,
      "primary_buyer_id": 123,
      "secondary_buyer_id": 124,
      "sales_type": "primary",
      "booking_date": "2026-01-17",
      "unit_reference": "A-101",
      "deal_sales_value": 250000.00
    }
  }
}
```

## 📦 Property Deals Module Development

### Module Structure

The `deals_management` module extends `sale.order` with property-specific functionality:

#### Key Fields
- `sales_type` - Deal type (Primary, Secondary, Exclusive, Rental)
- `primary_buyer_id` - Main buyer
- `secondary_buyer_id` - Co-buyer
- `booking_date` - Deal booking date
- `deal_sales_value` - Transaction amount
- `deal_commission_rate` - Commission percentage
- `vat_amount` - VAT calculation
- `total_with_vat` - Final total

#### Related Models
- `sale.order` - Base model (inherited)
- `res.partner` - Buyers and companies
- `account.move` - Invoicing
- `commission.ax` - Commission tracking

### Extending the Module

To add new features to the deals module:

1. **Create Models** (`deals_management/models/`)
2. **Update Manifest** (`__manifest__.py`)
3. **Create Views** (XML in `views/`)
4. **Update Access Control** (`security/ir.model.access.csv`)

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- odoo-client.test.ts

# Watch mode for development
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## 🔍 Code Quality

### ESLint

```bash
# Check code style
npm run lint

# Fix code style issues
npm run lint:fix
```

### TypeScript Type Checking

```bash
# One-time check
npm run type-check

# Watch mode
npm run type-check:watch
```

## 📚 API Documentation

All types are defined in `src/types.ts` with comprehensive interfaces for:
- OdooConfig - Connection configuration
- SearchParams - Search operations
- CreateParams - Record creation
- UpdateParams - Record updates
- ExecuteParams - Method execution
- ReportParams - Report generation

## 🐛 Troubleshooting

### Connection refused
- Verify ODOO_URL is correct
- Ensure Odoo server is running

### Authentication failed
- Verify ODOO_USERNAME and ODOO_PASSWORD
- Check database name in ODOO_DB

### Module not installed
- Install deals_management module in Odoo first
- Run: `npm run build` after adding module files

## 📚 Additional Resources

- [Odoo Documentation](https://www.odoo.com/documentation)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Odoo XML-RPC API](https://www.odoo.com/documentation/17.0/developer/reference/external_api/index.html)

## 📄 License

LGPL-3 License

## 👨‍💻 Author

**renbran** - Initial development

---

**Status**: Production Ready ✅  
**Last Updated**: January 17, 2026  
**Version**: 1.0.0
