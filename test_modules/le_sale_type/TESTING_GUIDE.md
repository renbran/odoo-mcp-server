# Sale Order Type - Invoice Integration Testing Guide

## Pre-Upgrade Checklist

Before upgrading the module to version 1.1.0, ensure:

- [ ] Odoo server is accessible
- [ ] You have administrator access
- [ ] 'sale' and 'account' modules are installed
- [ ] Backup of database is created
- [ ] No active users are working with sales/invoices

## Module Upgrade Steps

### Step 1: Update Module Files

1. Ensure all new files are in place:
   ```bash
   cd "D:\RUNNING APPS\odoo17\osuspropertiesv1\le_sale_type"

   # Verify new files exist:
   # - models/account_move.py
   # - views/account_move_views.xml
   # - README.md
   # - TESTING_GUIDE.md
   ```

2. Verify __manifest__.py shows version 1.1.0

3. Verify models/__init__.py imports account_move

### Step 2: Restart Odoo Server

```bash
# Restart your Odoo service
# Example for systemd:
sudo systemctl restart odoo17

# Or if running manually:
# Stop the server (Ctrl+C) and restart with:
python odoo-bin -c /path/to/odoo.conf
```

### Step 3: Upgrade Module

1. Log in to Odoo as Administrator
2. Go to **Settings → Apps**
3. Remove the "Apps" filter (click the X on the filter)
4. Search for "Sale Order Type"
5. Click the **Upgrade** button
6. Wait for upgrade to complete

### Step 4: Verify Installation

Check that no errors occurred:
- Review Odoo server logs
- Verify the module shows version 1.1.0

## Functional Testing

### Test 1: Sale Type Field on Invoices (Form View)

**Objective**: Verify sale_order_type_id field appears on invoice form

**Steps**:
1. Navigate to **Invoicing → Customers → Invoices**
2. Open any existing customer invoice OR create a new one
3. Look for **Sale Type** field in the form header area

**Expected Result**:
- [ ] Sale Type field is visible on customer invoices
- [ ] Field shows placeholder "Auto-filled from Sale Order"
- [ ] Field is NOT visible on supplier bills

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 2: Sale Type Field on Invoice List View

**Objective**: Verify sale type column in invoice tree view

**Steps**:
1. Navigate to **Invoicing → Customers → Invoices**
2. Ensure you're in list/tree view
3. Look for **Sale Type** column

**Expected Result**:
- [ ] Sale Type column is visible (or can be shown via column options)
- [ ] Column shows sale type names for invoices created from sale orders
- [ ] Column is empty for manually created invoices

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 3: Auto-Fetch from Sale Order (Primary Feature)

**Objective**: Verify automatic population of sale type when creating invoice from sale order

**Test Data Setup**:
1. Create/identify a Sale Order Type:
   - Go to **Sales → Configuration → Sale Order Types**
   - Ensure at least one type exists (e.g., "Retail")

2. Create a new Sale Order:
   - Go to **Sales → Orders → Quotations**
   - Click **Create**
   - Customer: Select any customer
   - **Sale Type**: Select "Retail" (or your test type)
   - Add at least one order line
   - Click **Confirm**

**Test Steps**:
1. On the confirmed sale order, click **Create Invoice**
2. Select "Regular Invoice"
3. Click **Create and View Invoice**
4. Check the **Sale Type** field on the invoice

**Expected Result**:
- [ ] Invoice Sale Type field is automatically filled
- [ ] Sale Type matches the sale order's type ("Retail")
- [ ] No manual intervention was needed

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 4: Invoice Search by Sale Type

**Objective**: Verify filtering and searching by sale type

**Steps**:
1. Navigate to **Invoicing → Customers → Invoices**
2. Click the **Search** icon (magnifying glass)
3. In the search dropdown, click **Sale Type**
4. Select a sale type from the dropdown

**Expected Result**:
- [ ] Sale Type appears in filter options
- [ ] Invoices are filtered by selected sale type
- [ ] Count shows correct number of invoices

**Alternative Search**:
1. In the search box, type a sale type name
2. Press Enter

**Expected Result**:
- [ ] Search finds invoices with matching sale type
- [ ] Results are accurate

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 5: Group By Sale Type

**Objective**: Verify grouping functionality in list view

**Steps**:
1. Navigate to **Invoicing → Customers → Invoices**
2. Click **Filters** dropdown
3. Under "Group By" section, select **Sale Type**

**Expected Result**:
- [ ] "Sale Type" option appears in Group By section
- [ ] Invoices are grouped by their sale types
- [ ] Groups show invoice counts
- [ ] Expandable groups show individual invoices

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 6: Credit Note Sale Type Propagation

**Objective**: Verify sale type is copied to credit notes

**Test Steps**:
1. Open an invoice that has a Sale Type set
2. Note the Sale Type value (e.g., "Wholesale")
3. Click **Add Credit Note** button
4. Select "Partial Refund" and create credit note
5. View the created credit note
6. Check the **Sale Type** field

**Expected Result**:
- [ ] Credit note has Sale Type field populated
- [ ] Sale Type matches the original invoice
- [ ] Field was automatically filled

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 7: Pivot View Analysis

**Objective**: Verify sale type integration in pivot view

**Steps**:
1. Navigate to **Invoicing → Customers → Invoices**
2. Switch to **Pivot** view (icon next to list view)
3. Click on column headers to add **Sale Type** as a dimension
4. Try adding Sale Type to rows, then to columns

**Expected Result**:
- [ ] Sale Type appears as available dimension
- [ ] Pivot table displays data grouped by sale type
- [ ] Amounts are correctly aggregated
- [ ] Can cross-analyze with other dimensions (customer, date, etc.)

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 8: Graph View Analysis

**Objective**: Verify sale type in graph/chart view

**Steps**:
1. Navigate to **Invoicing → Customers → Invoices**
2. Switch to **Graph** view
3. Click **Measures** and select a measure (e.g., Amount Total)
4. Click **Group By** and select **Sale Type**

**Expected Result**:
- [ ] Graph displays data grouped by sale type
- [ ] Different sale types shown in different colors/segments
- [ ] Chart is readable and accurate
- [ ] Can switch between bar, line, and pie charts

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 9: Manual Invoice (No Sale Order)

**Objective**: Verify behavior when creating invoice without sale order

**Steps**:
1. Go to **Invoicing → Customers → Invoices**
2. Click **Create**
3. Select a customer
4. Add invoice lines manually (without sale order)
5. Check **Sale Type** field

**Expected Result**:
- [ ] Sale Type field is visible but empty
- [ ] Can manually set sale type if desired
- [ ] No errors occur
- [ ] Invoice can be saved with or without sale type

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 10: Multiple Sale Orders (Edge Case)

**Objective**: Verify behavior when invoice has lines from multiple sale orders

**Test Setup**:
1. Create two sale orders with DIFFERENT sale types:
   - Sale Order 1: Type = "Retail"
   - Sale Order 2: Type = "Wholesale"
2. Confirm both orders

**Test Steps**:
1. Create a new invoice manually
2. Add invoice lines:
   - Line 1: Link to Sale Order 1 (Retail)
   - Line 2: Link to Sale Order 2 (Wholesale)
3. Save the invoice
4. Check **Sale Type** field
5. Check Odoo server logs

**Expected Result**:
- [ ] Invoice Sale Type is set (uses first order's type)
- [ ] Warning message logged in server logs about mixed types
- [ ] No error prevents invoice creation
- [ ] Invoice functions normally

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 11: Supplier Bills (Negative Test)

**Objective**: Verify sale type field does NOT appear on supplier bills

**Steps**:
1. Navigate to **Invoicing → Vendors → Bills**
2. Create or open a vendor bill
3. Look for Sale Type field

**Expected Result**:
- [ ] Sale Type field is NOT visible on vendor bills
- [ ] Field is hidden/invisible (not applicable to purchases)
- [ ] No errors or layout issues

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 12: Field Editability

**Objective**: Verify sale type can be manually edited if needed

**Steps**:
1. Open any invoice with auto-filled Sale Type
2. Click on the Sale Type field
3. Change to a different sale type
4. Save the invoice

**Expected Result**:
- [ ] Field is editable (not readonly)
- [ ] Can select different sale type from dropdown
- [ ] Change is saved successfully
- [ ] Change is tracked in chatter (if tracking enabled)

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 13: Invoice Duplication

**Objective**: Verify sale type is copied when duplicating invoice

**Steps**:
1. Open an invoice with Sale Type set (e.g., "Retail")
2. Click Action → Duplicate
3. Check Sale Type on duplicated invoice

**Expected Result**:
- [ ] Duplicated invoice has same Sale Type
- [ ] Field was automatically copied
- [ ] Can be edited if needed

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 14: Performance Test

**Objective**: Verify no performance degradation

**Steps**:
1. Navigate to invoice list with many records (100+)
2. Apply Sale Type filter
3. Group by Sale Type
4. Switch between views (list, pivot, graph)

**Expected Result**:
- [ ] List loads in reasonable time (< 3 seconds)
- [ ] Filtering is fast
- [ ] Grouping works smoothly
- [ ] No timeouts or errors

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

## Integration Testing

### Test 15: Dashboard Integration (If Applicable)

If you have the osus_sales_invoicing_dashboard module:

**Steps**:
1. Navigate to the sales/invoicing dashboard
2. Check if Sale Type appears in filters
3. Test filtering dashboard data by sale type

**Expected Result**:
- [ ] Dashboard recognizes sale_order_type_id field
- [ ] Can filter dashboard by sale type
- [ ] Data updates correctly

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 16: Report Generation

**Objective**: Verify sale type appears in printed reports

**Steps**:
1. Open an invoice with Sale Type set
2. Click **Print** → **Invoice**
3. Review the PDF/printed output

**Expected Result**:
- [ ] PDF generates without errors
- [ ] Sale Type may appear on report (depends on template)
- [ ] No layout issues

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

## Data Validation Testing

### Test 17: Existing Data

**Objective**: Verify existing invoices are not affected negatively

**Steps**:
1. Open several existing invoices (created before upgrade)
2. Check Sale Type field
3. Verify invoice still functions normally

**Expected Result**:
- [ ] Existing invoices open without errors
- [ ] Sale Type field is empty (unless they were from sale orders)
- [ ] All other invoice functions work normally
- [ ] Can edit and post existing invoices

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

### Test 18: Database Consistency

**Objective**: Verify database integrity

**Steps**:
Run these SQL queries via psql or pgAdmin:

```sql
-- Check if column was added
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'account_move'
  AND column_name = 'sale_order_type_id';

-- Check for any invalid references
SELECT COUNT(*)
FROM account_move
WHERE sale_order_type_id IS NOT NULL
  AND sale_order_type_id NOT IN (SELECT id FROM sale_order_type);

-- Check index was created
SELECT indexname
FROM pg_indexes
WHERE tablename = 'account_move'
  AND indexdef LIKE '%sale_order_type_id%';
```

**Expected Result**:
- [ ] Column exists with type integer
- [ ] No invalid foreign key references (count = 0)
- [ ] Index exists for performance

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

## Security Testing

### Test 19: Access Rights

**Objective**: Verify users can access sale type field appropriately

**Steps**:
1. Log in as a user with Sales User role (not manager)
2. Navigate to invoices
3. Try to view and edit Sale Type field

**Expected Result**:
- [ ] Sales users can view Sale Type
- [ ] Sales users can edit Sale Type (unless restricted)
- [ ] No permission errors

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

## Error Handling Testing

### Test 20: Deleted Sale Type

**Objective**: Verify behavior if a sale type is deleted/archived

**Steps**:
1. Create a sale order with Sale Type "Test Type"
2. Create invoice from that sale order
3. Archive or deactivate the "Test Type"
4. Open the invoice again

**Expected Result**:
- [ ] Invoice still displays the sale type name (even if archived)
- [ ] No errors when opening invoice
- [ ] Field shows inactive type with indication

**Status**: ⬜ Pass ⬜ Fail

**Notes**: _________________________________

---

## Test Summary

**Total Tests**: 20
**Passed**: ____
**Failed**: ____
**Skipped**: ____

**Critical Issues**: ____________________________________________

**Minor Issues**: ____________________________________________

**Recommendations**: ____________________________________________

---

## Post-Testing Actions

### If All Tests Pass:
- [ ] Document any observations
- [ ] Train end users on new features
- [ ] Update internal documentation
- [ ] Monitor production usage for first week

### If Tests Fail:
- [ ] Document exact failure scenarios
- [ ] Capture error logs
- [ ] Create bug reports
- [ ] Roll back if critical
- [ ] Contact module support

---

## Rollback Procedure (If Needed)

### Emergency Rollback:

1. **Restore Database Backup**:
   ```bash
   # Stop Odoo
   sudo systemctl stop odoo17

   # Restore backup
   psql -U odoo -d your_database < backup_before_upgrade.sql

   # Restart Odoo
   sudo systemctl start odoo17
   ```

2. **Revert Module Files**:
   ```bash
   cd "D:\RUNNING APPS\odoo17\osuspropertiesv1\le_sale_type"

   # Restore from git if tracked
   git checkout HEAD -- .

   # Or restore from backup copy
   ```

3. **Alternative: Keep Data, Remove Views**:
   - If only views have issues, you can keep the data
   - Temporarily remove account_move_views.xml from __manifest__.py
   - Upgrade module again

---

## Sign-off

**Tester Name**: _____________________
**Date**: _____________________
**Environment**: Production / Staging / Development
**Odoo Version**: _____________________
**Module Version**: _____________________

**Approval for Production**: ⬜ Yes ⬜ No

**Approved By**: _____________________
**Date**: _____________________

---

## Notes and Observations

_Use this space for additional notes, observations, or recommendations:_

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

