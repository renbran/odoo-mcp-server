# Deal Report Module - Architecture & Visual Diagrams

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         SCHOLARIXV2 ODOO 17                    │
└─────────────────────────────────────────────────────────────────┘
                                ↓
        ┌───────────────────────┴───────────────────────┐
        ↓                                               ↓
    ┌─────────────────┐                    ┌──────────────────────┐
    │   SALES MODULE  │                    │   ACCOUNTING MODULE  │
    └─────────────────┘                    └──────────────────────┘
        ↓                                               ↓
┌─────────────────────┐                    ┌──────────────────────────┐
│   sale.order        │                    │   account.move           │
│ (Model)             │                    │ (Model)                  │
├─────────────────────┤                    ├──────────────────────────┤
│ Standard Fields:    │                    │ Standard Fields:         │
│ - name              │                    │ - name                   │
│ - partner_id        │                    │ - partner_id             │
│ - amount_total      │ ────────────────→ │ - invoice_date           │
│ - date_order        │  (Create Invoice) │ - amount_total           │
│                     │                    │                          │
│ DEAL FIELDS [NEW]:  │                    │ DEAL FIELDS [NEW]:       │
│ ✓ buyer_name        │ ─────────────────→ │ ✓ buyer_name             │
│ ✓ project_name      │  (Auto-populate)   │ ✓ project_name           │
│ ✓ unit_sale_value   │                    │ ✓ unit_sale_value        │
│ ✓ commission_%      │                    │ ✓ commission_%           │
│ ✓ deal_reference    │                    │ ✓ deal_reference         │
│                     │                    │ ✓ sale_order_id (FK)     │
│                     │                    │ ✓ deal_summary (HTML)    │
└─────────────────────┘                    └──────────────────────────┘
        ↓                                               ↓
  [SaleOrder                                   [AccountMove
   Enhancements]                                Enhancements]
                                                      ↓
                                        ┌──────────────────────────┐
                                        │  REPORT MODULE           │
                                        ├──────────────────────────┤
                                        │ report_invoice_with_deals│
                                        │ (Qweb-PDF)               │
                                        │                          │
                                        │ Displays:                │
                                        │ ✓ Invoice Header         │
                                        │ ✓ Deal Info Panel        │
                                        │ ✓ Party Information      │
                                        │ ✓ Line Items             │
                                        │ ✓ Totals & Taxes         │
                                        │ ✓ Notes & Footer         │
                                        └──────────────────────────┘
                                                      ↓
                                        ┌──────────────────────────┐
                                        │    PDF OUTPUT            │
                                        │ (A4, Professional Format)│
                                        └──────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     SALES WORKFLOW                              │
└─────────────────────────────────────────────────────────────────┘

1. CREATE SALE ORDER
   ┌──────────────────────┐
   │ sale.order.create()  │
   ├──────────────────────┤
   │ User fills fields:   │
   │ - name               │
   │ - partner_id         │
   │ - line_ids           │
   │ + DEAL FIELDS:       │
   │ - buyer_name         │
   │ - project_name       │
   │ - unit_sale_value    │
   │ - commission_%       │
   │ - deal_reference     │
   └──────────────────────┘
            ↓
2. CONFIRM SALE ORDER
   ┌──────────────────────┐
   │ action_confirm()     │
   └──────────────────────┘
            ↓
3. CREATE INVOICE
   ┌────────────────────────────────────┐
   │ _prepare_invoice_values() override  │ [CUSTOM CODE]
   ├────────────────────────────────────┤
   │ Copies deal fields from SO:         │
   │ invoice_vals.update({               │
   │   'buyer_name':                     │
   │     sale_order.buyer_name,          │
   │   'project_name':                   │
   │     sale_order.project_name,        │
   │   'unit_sale_value':                │
   │     sale_order.unit_sale_value,     │
   │   'commission_%':                   │
   │     sale_order.commission_%,        │
   │   'sale_order_id':                  │
   │     sale_order.id,                  │
   │   ...                               │
   │ })                                  │
   └────────────────────────────────────┘
            ↓
4. INVOICE CREATED WITH DEAL DATA
   ┌──────────────────────┐
   │ account.move.create()│
   ├──────────────────────┤
   │ Fields populated:    │
   │ ✓ buyer_name        │
   │ ✓ project_name      │
   │ ✓ unit_sale_value   │
   │ ✓ commission_%      │
   │ ✓ sale_order_id     │
   └──────────────────────┘
            ↓
5. COMPUTE DEAL SUMMARY
   ┌─────────────────────────────────────┐
   │ _compute_deal_information_summary()  │ [CUSTOM CODE]
   ├─────────────────────────────────────┤
   │ Generates HTML formatted summary:    │
   │                                      │
   │ <div style="...">                   │
   │   <h6>DEAL INFORMATION</h6>         │
   │   <table>                           │
   │     <tr>                            │
   │       <td>Buyer:</td>               │
   │       <td>[buyer_name]</td>         │
   │     </tr>                           │
   │     ...                             │
   │   </table>                          │
   │ </div>                              │
   │                                      │
   │ Result stored in:                   │
   │ invoice.deal_information_summary    │
   └─────────────────────────────────────┘
            ↓
6. GENERATE REPORT
   ┌──────────────────────────────────┐
   │ account_report_invoice_with_deals │
   ├──────────────────────────────────┤
   │ Template loads:                   │
   │ report_invoice_with_deals.xml     │
   │                                   │
   │ Renders:                          │
   │ ✓ doc.name (Invoice #)            │
   │ ✓ doc.partner_id (Bill To)        │
   │ ✓ doc.invoice_date                │
   │ ✓ doc.invoice_line_ids (Items)    │
   │ ✓ doc.deal_information_summary    │ [HTML RENDERED]
   │ ✓ doc.amount_total (Total)        │
   │ ✓ doc.narration (Notes)           │
   └──────────────────────────────────┘
            ↓
7. GENERATE PDF
   ┌──────────────────────┐
   │ Qweb Engine          │
   │ (wkhtmltopdf)        │
   └──────────────────────┘
            ↓
8. PDF OUTPUT
   ┌──────────────────────────────┐
   │ Invoice_Number.pdf           │
   │ (A4, Professional Format)    │
   │                              │
   │ Contains:                    │
   │ ✓ All invoice details        │
   │ ✓ Deal information panel     │
   │ ✓ Professional styling       │
   │ ✓ Ready for printing         │
   └──────────────────────────────┘
```

## Field Synchronization Diagram

```
┌──────────────────────────────────────────────────────────────┐
│              FIELD SYNCHRONIZATION FLOW                      │
└──────────────────────────────────────────────────────────────┘

SCENARIO 1: CREATE INVOICE FROM SALE ORDER
──────────────────────────────────────────

Sale Order Fields          Invoice Fields         Report Display
──────────────────────────────────────────────────────────────
buyer_name (SO)     ───→  buyer_name (INV)  ──→  [PDF: Buyer Name]
project_name (SO)   ───→  project_name (INV) ──→ [PDF: Project]
unit_sale_value (SO) ──→  unit_sale_value (INV) → [PDF: Unit Value]
commission_% (SO)   ───→  commission_% (INV) ──→ [PDF: Commission]
id (SO)             ───→  sale_order_id (INV) ──→ [PDF: Reference]


SCENARIO 2: SET SALE_ORDER_ID ON EXISTING INVOICE
──────────────────────────────────────────────────

invoice.write({'sale_order_id': SO_ID})
         ↓
    write() method called (OVERRIDE)
         ↓
    Fetches linked SO
         ↓
    Populates deal fields if empty
         ↓
    deal_information_summary recomputes
         ↓
    Report reflects updated data


SCENARIO 3: MANUAL ENTRY (NO SALE ORDER)
──────────────────────────────────────────

User fills fields manually:
┌──────────────────────────┐
│ buyer_name = "John Doe"  │
│ project_name = "Project" │
│ unit_sale_value = 100000 │
│ commission_% = 5         │
└──────────────────────────┘
         ↓
    _compute_deal_information_summary()
         ↓
    HTML summary generates
         ↓
    Report displays summary
         ↓
    PDF shows all information
```

## Class Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    ODOO MODEL HIERARCHY                         │
└────────────────────────────────────────────────────────────────┘

                    account.move (Base)
                           ↑
                           │ inherits
                           │
                    ┌──────┴──────┐
                    │             │
                    │  Standard   │
                    │  Fields &   │
                    │  Methods    │
                    │             │
                    └──────┬──────┘
                           ↑
                           │ extends with @api decorators
                           │
                    ┌──────────────────────────────┐
                    │ AccountMoveWithDeals         │ [NEW]
                    ├──────────────────────────────┤
                    │ NEW FIELDS:                  │
                    │ ─────────────────────────    │
                    │ • buyer_name (Char)         │
                    │ • project_name (Char)       │
                    │ • unit_sale_value (Money)   │
                    │ • commission_% (Float)      │
                    │ • sale_order_ref (Char)     │
                    │ • sale_order_id (M2O)       │
                    │ • deal_summary (Html)       │
                    │                              │
                    │ NEW METHODS:                 │
                    │ ─────────────────────────    │
                    │ • create()                   │
                    │ • write()                    │
                    │ • _compute_deal_summary()    │
                    │ • generate_pdf()             │
                    └──────────────────────────────┘
                             ↓
                             │ uses in reports
                             ↓
                    ┌──────────────────────────────┐
                    │ Qweb Report Template         │
                    ├──────────────────────────────┤
                    │ report_invoice_with_deals    │
                    │ (account_report_inv_deals)   │
                    │                              │
                    │ Renders:                     │
                    │ - Invoice header             │
                    │ - Deal info panel            │
                    │ - Party info                 │
                    │ - Line items                 │
                    │ - Totals                     │
                    │ - Footer                     │
                    │                              │
                    │ Output: PDF (A4)             │
                    └──────────────────────────────┘


                    sale.order (Base)
                           ↑
                           │ inherits
                           │
                    ┌──────────────────────────────┐
                    │ SaleOrderDealIntegration     │ [NEW]
                    ├──────────────────────────────┤
                    │ NEW FIELDS:                  │
                    │ ─────────────────────────    │
                    │ • buyer_name (Char)         │
                    │ • project_name (Char)       │
                    │ • unit_sale_value (Money)   │
                    │ • commission_% (Float)      │
                    │ • sale_order_ref (Char)     │
                    │                              │
                    │ OVERRIDDEN METHODS:          │
                    │ ─────────────────────────    │
                    │ • _prepare_invoice_values()  │
                    │                              │
                    │ PURPOSE:                     │
                    │ Data source for invoice      │
                    │ field population             │
                    └──────────────────────────────┘
                             ↓
                             │ creates
                             ↓
                    AccountMoveWithDeals instance
                    (with deal fields populated)
```

## Module File Structure

```
recruitment_implementation/
│
├── 📄 __init__.py
│   └─ Imports: models, wizards
│
├── 📄 __manifest__.py
│   └─ Module metadata
│   └─ Dependencies: recruitment, mail, hr, base
│   └─ Data files: views/*, report/*
│
├── 📁 models/
│   ├── 📄 __init__.py
│   │   └─ from . import models_candidate_enhancement
│   │   └─ from . import models_followup
│   │   └─ from . import models_retention
│   │   └─ from . import models_invoice_deals [NEW]
│   │
│   ├── 📄 models_candidate_enhancement.py
│   │   └─ RecruitmentCandidate enhancements
│   │
│   ├── 📄 models_followup.py
│   │   └─ FollowUp model
│   │
│   ├── 📄 models_retention.py
│   │   └─ Retention tracking
│   │
│   └── 📄 models_invoice_deals.py [NEW]
│       ├─ AccountMoveWithDeals class
│       │  ├─ buyer_name field
│       │  ├─ project_name field
│       │  ├─ unit_sale_value field
│       │  ├─ commission_percentage field
│       │  ├─ sale_order_deal_reference field
│       │  ├─ sale_order_id field
│       │  ├─ deal_information_summary (computed)
│       │  ├─ create() override
│       │  ├─ write() override
│       │  ├─ _compute_deal_information_summary()
│       │  └─ generate_invoice_with_deals_pdf()
│       │
│       └─ SaleOrderDealIntegration class
│          ├─ buyer_name field
│          ├─ project_name field
│          ├─ unit_sale_value field
│          ├─ commission_percentage field
│          ├─ sale_order_deal_reference field
│          └─ _prepare_invoice_values() override
│
├── 📁 report/ [NEW]
│   ├── 📄 __init__.py
│   │   └─ (empty or comment only)
│   │
│   └── 📄 report_invoice_with_deals.xml [NEW]
│       ├─ <report> element (Qweb-PDF)
│       │  └─ report_name: scholarix_recruitment.report_invoice_with_deals
│       │  └─ model: account.move
│       │  └─ report_type: qweb-pdf
│       │
│       └─ <template> element
│          ├─ Header section
│          ├─ Deal info panel [CONDITIONAL]
│          ├─ Party information
│          ├─ Invoice details
│          ├─ Line items table
│          ├─ Totals section
│          ├─ Notes section [CONDITIONAL]
│          └─ Footer
│
├── 📁 views/
│   └── 📄 views_retention_followup.xml
│
├── 📁 wizards/
│   └── 📄 wizard_forfeit.py
│
└── 📚 Documentation/
    ├── 📄 DEAL_REPORT_DOCUMENTATION.md [NEW]
    │   └─ Complete technical guide (3500+ words)
    │
    ├── 📄 DEAL_REPORT_QUICKSTART.md [NEW]
    │   └─ Deployment & usage guide (2000+ words)
    │
    ├── 📄 DEAL_REPORT_IMPLEMENTATION_COMPLETE.md [NEW]
    │   └─ Project summary (2000+ words)
    │
    └── 📄 README_DEAL_REPORT.md [NEW]
        └─ Quick reference & summary
```

## Report Template Structure

```
┌───────────────────────────────────────────────────────────────┐
│          REPORT TEMPLATE: report_invoice_with_deals           │
└───────────────────────────────────────────────────────────────┘

┌─ <t t-call="web.html_container">
│  ├─ <t t-foreach="docs" t-as="doc">
│  │  └─ <t t-call="web.external_layout">
│  │     └─ <div class="page">
│  │        │
│  │        ├─ SECTION 1: Header
│  │        │  ├─ Invoice Type (INVOICE, CREDIT NOTE, BILL, etc)
│  │        │  └─ Invoice Number & Date
│  │        │
│  │        ├─ SECTION 2: Deal Information Panel [CONDITIONAL]
│  │        │  (Only for out_invoice, out_refund)
│  │        │  ├─ Styled box (border-left: #8b1538)
│  │        │  ├─ Title: ORIGINAL DEAL INFORMATION
│  │        │  ├─ Buyer: [buyer_name or partner_id.name]
│  │        │  ├─ Project: [project_name or "—"]
│  │        │  ├─ Unit Sale Value: [formatted monetary]
│  │        │  ├─ Commission %: [formatted percentage]
│  │        │  └─ Sales Order: [order reference - total]
│  │        │
│  │        ├─ SECTION 3: Party Information
│  │        │  ├─ Bill To
│  │        │  │  └─ Partner info (address, phone)
│  │        │  └─ Bill From
│  │        │     └─ Company info (address, phone)
│  │        │
│  │        ├─ SECTION 4: Invoice Details
│  │        │  ├─ Invoice Date
│  │        │  ├─ Due Date
│  │        │  ├─ Order Reference
│  │        │  ├─ Your Reference
│  │        │  ├─ Sales Person
│  │        │  └─ Sales Team
│  │        │
│  │        ├─ SECTION 5: Line Items Table
│  │        │  ├─ Header row (gray background)
│  │        │  │  ├─ Description (50%)
│  │        │  │  ├─ Quantity (10%)
│  │        │  │  ├─ Unit Price (15%)
│  │        │  │  └─ Amount (25%)
│  │        │  │
│  │        │  └─ Data rows (one per line)
│  │        │     ├─ Product name
│  │        │     ├─ Qty + UOM
│  │        │     ├─ Unit price (formatted)
│  │        │     └─ Line total (formatted)
│  │        │
│  │        ├─ SECTION 6: Totals
│  │        │  ├─ Subtotal
│  │        │  ├─ Tax lines (per tax group)
│  │        │  └─ TOTAL (large, bold, colored)
│  │        │
│  │        ├─ SECTION 7: Notes [CONDITIONAL]
│  │        │  (Only if narration exists)
│  │        │  └─ Terms & conditions from narration
│  │        │
│  │        └─ SECTION 8: Footer
│  │           ├─ Phone number
│  │           └─ Email address
│  │
│  └─ </div>
│
└─ </t>
```

## Styling & Colors

```
BRAND COLOR PALETTE
═══════════════════

Primary Color:
┌──────────────┐
│  #8b1538     │  (Dark Maroon)
│ (Used for:   │
│  - Borders   │
│  - Headers   │
│  - Emphasis) │
└──────────────┘

Secondary Colors:
┌──────────────┐
│  #f8f9fa     │  (Light Gray)
│ (Used for:   │
│  - Backgrounds)
└──────────────┘

┌──────────────┐
│  #333333     │  (Dark Gray)
│ (Used for:   │
│  - Text)     │
└──────────────┘

Text Colors:
- Headers: #8b1538
- Body text: #333
- Accent: #8b1538

Background Colors:
- Panel: #f8f9fa
- Table header: #f8f9fa
- Page: white
```

## System Integration Map

```
                    ┌─────────────────────┐
                    │   SCHOLARIXV2 DB    │
                    └─────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
      ┌─────▼────┐     ┌─────▼─────┐   ┌────▼─────┐
      │   SALES  │     │ ACCOUNTING │   │   HR     │
      │  MODULE  │     │   MODULE   │   │ MODULE   │
      └─────┬────┘     └─────┬──────┘   └──────────┘
            │                │
        sale.order      account.move
            │                │
       [Deal Fields]    [Deal Fields]
            │                │
            └────┬───────────┘
                 │
        [SYNC via overrides]
                 │
              ┌──▼────────────────────┐
              │  Report Generation    │
              │ (Qweb Template)       │
              └──┬───────────────────┘
                 │
           ┌─────▼──────┐
           │  PDF Output│
           │  (A4 Size) │
           └────────────┘
```

---

## Legend

```
[NEW]      = Files/Classes created for this module
[OVERRIDE] = Methods that extend base Odoo functionality
[AUTO]     = Automatic processing/computation
[FK]       = Foreign Key relationship
M2O        = Many2One relationship
HTML       = HTML formatted output
```

---

**Architecture Diagrams Created**: January 19, 2026  
**Module Version**: 1.0.0  
**Odoo Version**: 17.0  
**Status**: ✅ Complete
