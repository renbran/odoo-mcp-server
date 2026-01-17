# Brokerage Deal Tracking Enhancement - Testing Plan
## Systematic Testing Guide

## INSTALLATION VERIFICATION

### Step 1: Verify Files Are Deployed
```bash
# SSH to server
ssh root@139.84.163.11

# Check files
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/sale_order_deal_tracking_views.xml
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/account_move_deal_tracking_views.xml

# Check Odoo is running
systemctl status odoo
```

### Step 2: Verify Module Upgrade
```bash
# Check Odoo logs for module upgrade
tail -f /var/log/odoo/odoo-server.log | grep -i "commission_ax"

# You should see: "commission_ax ... installed/upgraded successfully"
```

---

## TESTING PHASE 1: SALE ORDER DEAL FIELDS

### Test 1.1: Create Test Sale Order
**Steps:**
1. Login to Odoo as administrator
2. Go to Sales → Quotations → Create New
3. Fill in:
   - Customer: Create/Select any customer (e.g., "Brokerage Test Customer")
   - Project: Select a project (e.g., "Project A")
   - Add product line with price 100,000 (or any value)
   - Set commission rate: Manager Rate = 5%, Agent 1 = 3%, Broker = 2%

**Expected Results:**
- [ ] `buyer_name` field shows customer name
- [ ] `project_name` field shows selected project name
- [ ] `unit_sale_value` shows 100,000 (or whatever price_unit is)
- [ ] `primary_commission_percentage` shows 5 (highest among all rates)
- [ ] `deal_summary_html` displays formatted HTML with all deal info
- [ ] Colors are correct: borders/text are #8b1538 (burgundy)

**Test ID:** SO-001  
**Expected Status:** ✓ PASS

---

### Test 1.2: Test Computed Fields Without Optional Fields
**Steps:**
1. Create another sale order BUT don't select a project
2. Add order lines with price 50,000
3. Set only one commission rate (e.g., Broker = 4%)

**Expected Results:**
- [ ] `buyer_name` still shows correctly
- [ ] `project_name` shows empty/dash (—) in summary
- [ ] `unit_sale_value` shows 50,000
- [ ] `primary_commission_percentage` shows 4
- [ ] No errors in logs
- [ ] HTML summary handles missing project gracefully

**Test ID:** SO-002  
**Expected Status:** ✓ PASS

---

### Test 1.3: Test Multiple Order Lines (First Line Value)
**Steps:**
1. Create sale order with multiple order lines:
   - Line 1: Price 75,000
   - Line 2: Price 50,000
   - Line 3: Price 25,000
2. Set commission rates

**Expected Results:**
- [ ] `unit_sale_value` shows 75,000 (FIRST line price)
- [ ] Calculation doesn't use total, only first line
- [ ] HTML summary shows 75,000

**Test ID:** SO-003  
**Expected Status:** ✓ PASS

---

### Test 1.4: Test Commission Rate Hierarchy
**Steps:**
1. Create sale order with different rates:
   - Manager Rate: 2.5%
   - Agent 1: 3.75%
   - Agent 2: 2%
   - Broker: 4.1%
   - Referrer: 3%
   - Cashback: 1.5%
   - Director: 4%
   - Other External: 2.5%
2. Check primary commission percentage

**Expected Results:**
- [ ] `primary_commission_percentage` shows 4.1 (highest value)
- [ ] Calculation correctly identifies max()
- [ ] Summary shows 4.1%

**Test ID:** SO-004  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 2: SALE ORDER VIEWS

### Test 2.1: Form View Display
**Steps:**
1. Open any sale order created in Phase 1
2. Look for "BROKERAGE DEAL INFORMATION" section

**Expected Results:**
- [ ] Section appears after Partner field
- [ ] Has burgundy background (#f8f9fa with #8b1538 border)
- [ ] Shows 2x2 grid layout:
  - Top-left: Buyer Name
  - Top-right: Project Name
  - Bottom-left: Unit Sale Value
  - Bottom-right: Commission %
- [ ] Fields are read-only
- [ ] Deal summary HTML displays below grid
- [ ] No layout breaks or overlaps

**Test ID:** SO-VIEW-001  
**Expected Status:** ✓ PASS

---

### Test 2.2: Tree View Columns
**Steps:**
1. Go to Sales → Quotations (list view)
2. Check for new columns

**Expected Results:**
- [ ] Column "Buyer" shows customer names
- [ ] Column "Project" shows project names
- [ ] Column "Unit Price" shows prices
- [ ] Column "Commission %" shows percentages
- [ ] Columns are sortable
- [ ] Columns are searchable/filterable
- [ ] No overlapping with existing columns

**Test ID:** SO-VIEW-002  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 3: INVOICE DEAL FIELDS & TRANSFER

### Test 3.1: Invoice Creation from Sale Order
**Steps:**
1. Open sale order from Test SO-001
2. Click "Create Invoice" button
3. Confirm invoice creation

**Expected Results:**
- [ ] Invoice created successfully
- [ ] No errors in console/logs
- [ ] Invoice has all deal fields populated:
  - `buyer_name` = sale order buyer_name
  - `project_name` = sale order project_name
  - `unit_sale_value` = sale order unit_sale_value
  - `commission_percentage` = sale order primary_commission_percentage
  - `sale_order_deal_reference` = sale order name
- [ ] All fields have correct values

**Test ID:** INV-001  
**Expected Status:** ✓ PASS

---

### Test 3.2: Invoice Form Display
**Steps:**
1. Open invoice created in Test INV-001
2. Look for deal information section

**Expected Results:**
- [ ] "Brokerage Deal Information" group displays
- [ ] Shows all deal fields and their values
- [ ] `deal_information_summary` HTML shows
- [ ] HTML has burgundy styling consistent with SO
- [ ] Fields are read-only
- [ ] "ORIGINAL DEAL INFORMATION" header present

**Test ID:** INV-VIEW-001  
**Expected Status:** ✓ PASS

---

### Test 3.3: Invoice Tree View
**Steps:**
1. Go to Accounting → Invoices (list view)
2. Check for deal tracking columns

**Expected Results:**
- [ ] Columns for Buyer, Project, Unit Price, Commission % present
- [ ] Values match sale order values
- [ ] Columns are visible and properly aligned
- [ ] No layout issues

**Test ID:** INV-VIEW-002  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 4: DATA INTEGRITY

### Test 4.1: Field Persistence
**Steps:**
1. Create sale order with all deal info filled
2. Save and close
3. Open sale order again in new session

**Expected Results:**
- [ ] All deal fields still populated
- [ ] Values haven't changed
- [ ] HTML summary still renders correctly
- [ ] No database corruption

**Test ID:** DATA-001  
**Expected Status:** ✓ PASS

---

### Test 4.2: Invoice Field Persistence
**Steps:**
1. Create invoice from SO
2. Save and close
3. Open invoice again

**Expected Results:**
- [ ] All deal fields persist
- [ ] Summary HTML renders correctly
- [ ] Values match original SO

**Test ID:** DATA-002  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 5: PERFORMANCE

### Test 5.1: Large Dataset Query
**Steps:**
1. Run Odoo with 100+ sale orders
2. Load quotations list view
3. Time how long it takes to load

**Expected Results:**
- [ ] Loads in < 5 seconds
- [ ] No timeout errors
- [ ] Sorting by deal columns works
- [ ] No memory issues

**Test ID:** PERF-001  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 6: ERROR HANDLING

### Test 6.1: Missing Customer
**Steps:**
1. Try to create SO without selecting customer
2. Save SO
3. Check deal fields

**Expected Results:**
- [ ] System allows SO without customer
- [ ] `buyer_name` is empty string
- [ ] HTML summary shows "—" for buyer
- [ ] No errors in logs

**Test ID:** ERR-001  
**Expected Status:** ✓ PASS

---

### Test 6.2: Null Commission Rates
**Steps:**
1. Create SO with NO commission rates set
2. Check primary_commission_percentage

**Expected Results:**
- [ ] `primary_commission_percentage` = 0.0 (not NULL)
- [ ] HTML summary shows "—"
- [ ] No JavaScript/HTML errors

**Test ID:** ERR-002  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 7: INTEGRATION TESTS

### Test 7.1: Full Workflow
**Steps:**
1. Create sale order with all info (customer, project, lines, commissions)
2. Confirm it gets all deal fields
3. Create quotation → SO
4. Create invoice from SO
5. Verify all fields transferred
6. Verify all views display correctly

**Expected Results:**
- [ ] Complete workflow succeeds
- [ ] All data transfers correctly
- [ ] All views display properly
- [ ] HTML summaries render with correct styling

**Test ID:** INT-FULL-001  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 8: BROWSER COMPATIBILITY

### Test 8.1: HTML Rendering in Different Browsers
**Steps:**
1. Open SO/Invoice in Chrome
2. Open same in Firefox
3. Check HTML summary styling

**Expected Results:**
- [ ] HTML displays identically in Chrome
- [ ] HTML displays identically in Firefox
- [ ] No styling glitches
- [ ] Colors (burgundy #8b1538) match expectations

**Test ID:** BROWSER-001  
**Expected Status:** ✓ PASS

---

## TESTING PHASE 9: ODOO LOGS VALIDATION

### Test 9.1: No Errors in Server Logs
**Steps:**
1. During all tests above, monitor:
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

**Expected Results:**
- [ ] No ERROR level messages
- [ ] No CRITICAL level messages
- [ ] No AttributeError for deal fields
- [ ] No database errors
- [ ] Warning messages only for expected deprecations

**Test ID:** LOGS-001  
**Expected Status:** ✓ PASS

---

## SUMMARY TABLE

| Test ID | Phase | Description | Status | Notes |
|---------|-------|-------------|--------|-------|
| SO-001 | 1 | Create basic SO with deal info | ✓ | |
| SO-002 | 1 | SO without optional fields | ✓ | |
| SO-003 | 1 | Multiple order lines | ✓ | |
| SO-004 | 1 | Commission rate hierarchy | ✓ | |
| SO-VIEW-001 | 2 | Form view display | ✓ | |
| SO-VIEW-002 | 2 | Tree view columns | ✓ | |
| INV-001 | 3 | Invoice field transfer | ✓ | |
| INV-VIEW-001 | 3 | Invoice form display | ✓ | |
| INV-VIEW-002 | 3 | Invoice tree view | ✓ | |
| DATA-001 | 4 | SO field persistence | ✓ | |
| DATA-002 | 4 | Invoice field persistence | ✓ | |
| PERF-001 | 5 | Large dataset performance | ✓ | |
| ERR-001 | 6 | Missing customer handling | ✓ | |
| ERR-002 | 6 | Null rates handling | ✓ | |
| INT-FULL-001 | 7 | Complete workflow | ✓ | |
| BROWSER-001 | 8 | Browser compatibility | ✓ | |
| LOGS-001 | 9 | Server logs clean | ✓ | |

---

## SIGN-OFF

**Installation Date:** _______________  
**Tested By:** _______________  
**Result:** [ ] ALL PASS  [ ] SOME FAILED  [ ] CRITICAL ISSUES  
**Notes:** _________________________________________________________________

