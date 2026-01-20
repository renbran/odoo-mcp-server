# 🎯 Quick Start: Deal Information Search & Filters

## Access the New Filters

### Location in Odoo
```
Accounting → Invoices  (for customer invoices/refunds)
Accounting → Bills     (for vendor bills/refunds)
```

## 📋 Available Filters

### Approval Status Section
| Filter | Use Case |
|--------|----------|
| **Draft** | Find invoices/bills that haven't been submitted yet |
| **Under Review** | Find documents waiting for approval |
| **Approved** | Find documents that have been approved |

### Sales Type Section
| Filter | Document Type | Use Case |
|--------|--------------|----------|
| **Vendor Bills** | Incoming invoices | Monitor bills from suppliers |
| **Customer Invoices** | Outgoing invoices | Track invoices to customers |
| **Vendor Refunds** | Incoming credit notes | Track credits from suppliers |
| **Customer Refunds** | Outgoing credit notes | Track credits to customers |

### Group By Section
| Option | Organize By | Use Case |
|--------|-------------|----------|
| **Partner** | Customer/Vendor | See all deals with each partner |
| **Approval State** | Workflow status | Analyze approval bottlenecks |
| **Sales Type** | Document type | Separate invoices from refunds |
| **Booking Date** | Invoice date | View deals by date |

## 🔍 Searchable Fields

In the search box, you can now search for:
- **Booking Date** - Search by invoice_date (YYYY-MM-DD)
- **Sales Type** - Search by move type (in_invoice, out_invoice, etc.)
- **Approval State** - Search by approval status (draft, under_review, approved)

## 💡 Example Workflows

### Workflow 1: Review Pending Approvals
1. Click **"Under Review"** filter in Approval Status section
2. Click **"Group By: Approval State"** to organize
3. Review documents waiting for approval

### Workflow 2: Monitor Vendor Activity
1. Click **"Vendor Bills"** filter in Sales Type section
2. Click **"Group By: Partner"** to see bills by vendor
3. Analyze spending by supplier

### Workflow 3: Track Monthly Revenue
1. Click **"Group By: Booking Date"** to organize invoices
2. Search by specific dates using the search box
3. Generate revenue reports by period

### Workflow 4: Find Customer Refunds
1. Click **"Customer Refunds"** filter in Sales Type section
2. Click **"Group By: Partner"** to organize by customer
3. Review refund patterns

## 📊 Form View Updates

When editing an invoice/bill:
- **Approval State** field is now visible with color-coded status
- In **Draft** state: Field is **editable** - you can change the status manually
- In other states: Field is **read-only** - displays current status

## 🎨 Visual Status Indicators

In the list view, documents now show color-coded status:
- 🔵 **Blue** = Draft (not submitted)
- 🟡 **Yellow** = Under Review (waiting for approval)
- 🟢 **Green** = Approved or Posted

## ⚡ Pro Tips

1. **Combine Filters:** Click multiple filters together
   - Example: "Vendor Bills" + "Approved" = Show all approved supplier bills

2. **Save Filter Views:** Use Group By to save useful combinations
   - Example: "Group By Partner" + "Vendor Bills" = Supplier analysis

3. **Search Operators:** Use standard Odoo search syntax
   - Exact: Search "exact value"
   - Like: Search partial text
   - Date ranges: Use calendar picker for date fields

4. **Bulk Operations:** After filtering, select multiple documents for:
   - Batch approval changes
   - Bulk export
   - Mass updates

## 🔄 Field Details

### approval_state
- Values: draft, under_review, for_approval, approved, posted
- Editable: Only in draft state
- Used for: Workflow tracking and filtering

### invoice_date (Booking Date)
- Format: YYYY-MM-DD
- Searchable: Yes
- Used for: Date-based filtering and grouping

### move_type (Sales Type)
- Values:
  - `out_invoice` = Customer Invoice
  - `in_invoice` = Vendor Bill
  - `out_refund` = Customer Refund
  - `in_refund` = Vendor Refund
- Searchable: Yes
- Used for: Document type filtering and grouping

## ✅ Verification Checklist

When using the new filters, verify:
- [ ] Filters appear in the search bar
- [ ] Clicking filters updates the document list
- [ ] Group By options reorganize results
- [ ] Color-coded status shows in list view
- [ ] Approval state is editable in draft forms
- [ ] Booking date and sales type are searchable

## 📞 Support

If filters don't appear:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Refresh the page (Ctrl+F5)
3. Log out and back in
4. Check that module "payment_account_enhanced" is installed

The filters are ready to use! Navigate to Accounting → Bills or Invoices to start filtering your deal information.
