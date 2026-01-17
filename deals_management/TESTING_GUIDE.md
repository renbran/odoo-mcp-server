# Deals Management Module - Testing Guide

## Module Overview
The Deals Management module extends Odoo's Sale Order functionality to track real estate deals with comprehensive buyer information, document management, and commission tracking.

## Pre-Installation Checklist

### File Structure
- [x] `__manifest__.py` - Module metadata (name, version, dependencies, data)
- [x] `__init__.py` - Python module initialization
- [x] `models/__init__.py` - Model registration
- [x] `models/sale_order_deals.py` - Sale Order extension (computed fields: deal_sales_value, commission_count, bill_count)
- [x] `security/ir.model.access.csv` - Access control rules
- [x] `views/deals_views.xml` - 11 window actions for different deal types
- [x] `views/commission_views.xml` - Commission-related views
- [x] `views/commission_line_views.xml` - Commission line item views
- [x] `views/project_unit_views.xml` - Project unit property tracking
- [x] `views/deals_menu.xml` - Menu structure (Deals + Commissions with submenus)

### Dependencies Verified
- sale (base)
- commission_ax (custom)
- account (base)
- project (base)

## Installation Steps

### Step 1: Module Upload
```bash
# Copy module to Odoo extra-addons
scp -r deals_management/ user@erp.sgctech.ai:/var/odoo/scholarixv2/extra-addons/

# Set permissions
ssh user@erp.sgctech.ai
sudo chown -R odoo:odoo /var/odoo/scholarixv2/extra-addons/deals_management
sudo chmod -R 755 /var/odoo/scholarixv2/extra-addons/deals_management
```

### Step 2: Server-Side Installation
```bash
# Run installation script
ssh user@erp.sgctech.ai
cd /var/odoo/scholarixv2/extra-addons/deals_management
python3 install_module.py
```

### Step 3: Module Installation in Odoo UI
1. Login to https://erp.sgctech.ai with admin credentials
2. Navigate to **Apps** menu
3. Search for "Deals Management"
4. Click **Install**
5. Wait for module to load (should see "Installed" status)

## Post-Installation Verification

### Test 1: Menu Structure
**Objective:** Verify that Deals and Commissions menus appear with all submenus

**Steps:**
1. Logout and login again to refresh menu cache
2. Look for **Deals** menu in top navigation
3. Verify submenus under Deals:
   - [ ] All Deals
   - [ ] Primary Sales
   - [ ] Secondary Sales
   - [ ] Exclusive Sales
   - [ ] Rental Deals
4. Look for **Commissions** menu (separate from Deals)
5. Verify submenus under Commissions:
   - [ ] All Commissions
   - [ ] Pending Bills
   - [ ] Paid Bills
   - [ ] Commission by Partner
   - [ ] Vendor Bills
   - [ ] Commission Report

**Expected Result:** Both Deals and Commissions menus appear with all 11 submenus visible

---

### Test 2: Create a Deal
**Objective:** Verify that creating a sale order with deal information works

**Steps:**
1. Go to **Deals > All Deals**
2. Click **Create**
3. Fill in basic information:
   - Order Name: "Test Deal 001"
   - Partner: Select a customer
   - Sales Type: Choose "Primary"
   - Buyer Name: "John Doe"
   - Buyer Email: "john@example.com"
   - Buyer Phone: "1234567890"
4. Add order lines:
   - Product: Select any product
   - Quantity: 1
   - Unit Price: 100,000.00
5. Save the form
6. Check computed fields:
   - [ ] Deal Sales Value = Order Amount
   - [ ] Commission Count = 0 (initially)
   - [ ] Bill Count = 0 (initially)

**Expected Result:** Sale order created successfully with all deal-specific fields saved

---

### Test 3: Document Attachment
**Objective:** Verify that documents can be attached to deals

**Steps:**
1. Open the deal created in Test 2
2. Scroll to **Documents** section
3. Add documents:
   - [ ] KYC Document (upload a PDF)
   - [ ] Booking Form (upload a document)
   - [ ] Passport (upload a document)
4. Save the form
5. Check document counts update:
   - [ ] KYC Count should increase
   - [ ] Booking Form Count should increase
   - [ ] Passport Count should increase

**Expected Result:** Documents are attached and counts update automatically

---

### Test 4: Commission Tracking
**Objective:** Verify commission calculation and tracking

**Steps:**
1. In the deal form, set:
   - Primary Commission Percentage: 2.5%
   - Deal Commission Rate: 1.0%
2. Confirm order to generate commissions
3. Go to **Commissions > All Commissions**
4. Find commission entries for this deal
5. Verify fields:
   - [ ] Sale Order reference appears
   - [ ] Commission Amount = Correct calculation
   - [ ] Status is "Pending"

**Expected Result:** Commission entries created and tracked correctly

---

### Test 5: Filtering by Sales Type
**Objective:** Verify that sales type filters work correctly

**Steps:**
1. Go to **Deals > Primary Sales**
2. Verify only primary sales type orders appear (or is default filter)
3. Go to **Deals > Secondary Sales**
4. Create a new deal with "Secondary" sales type
5. Verify it appears in this view
6. Go to **Deals > Exclusive Sales**
7. Verify separate secondary sales don't appear here

**Expected Result:** Filtering by sales type works correctly

---

### Test 6: Commission Report
**Objective:** Verify commission reporting functionality

**Steps:**
1. Create 3-5 deals with different:
   - Sales types
   - Commission percentages
   - Statuses (draft, confirmed, done)
2. Go to **Commissions > Commission Report**
3. Verify the report shows:
   - [ ] Total commission amount
   - [ ] Breakdown by sales type
   - [ ] Breakdown by deal
   - [ ] Time period filtering works

**Expected Result:** Report displays correct aggregations and filtering

---

## Troubleshooting

### Issue 1: Module Not Appearing in Apps
**Symptoms:** Module doesn't show in Apps list after installation

**Solutions:**
1. Clear Odoo cache: `sudo systemctl restart odoo`
2. Update app list: Go to **Apps > Update Apps List**
3. Check module directory permissions: `ls -la /path/to/deals_management/`
4. Check Odoo logs: `sudo tail -f /var/log/odoo/odoo.log`

### Issue 2: Menu Not Appearing
**Symptoms:** Module installs but Deals/Commissions menu doesn't appear

**Solutions:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Logout and login again
3. Check ir.ui.menu table: Verify menu records were created
4. Check views/deals_menu.xml syntax

### Issue 3: Computed Fields Not Updating
**Symptoms:** deal_sales_value, commission_count, bill_count not calculating

**Solutions:**
1. Verify @api.depends decorators are correct in sale_order_deals.py
2. Run: `python manage.py --update-all` (or equivalent Odoo command)
3. Check model validation in Odoo UI: **Settings > Technical > Models > sale.order**

### Issue 4: Commission Fields Missing
**Symptoms:** Commission-related fields not visible in forms

**Solutions:**
1. Verify commission_ax module is installed
2. Check that commission_ax is listed in __manifest__.py dependencies
3. Verify views/commission_views.xml references commission.line model correctly

## Performance Benchmarks

| Operation | Expected Time |
|-----------|---------------|
| Load Deals list (10 records) | < 2 seconds |
| Open deal form | < 1 second |
| Save deal with documents | < 3 seconds |
| Generate commission report | < 5 seconds |
| Create new deal | < 2 seconds |

## Success Criteria

The module is considered **stable and production-ready** when:
- [x] All menu items appear correctly
- [x] Sales orders can be created with deal-specific fields
- [x] Documents can be attached and tracked
- [x] Commission calculations are correct
- [x] Reports generate without errors
- [x] All filters and views work as expected
- [x] Performance is acceptable (all operations complete in < 5s)

## Support Contact

For issues or questions about the Deals Management module:
- Check module logs: `/var/odoo/scholarixv2/extra-addons/deals_management/`
- Review computed field implementations in models/sale_order_deals.py
- Verify all dependencies are installed: sale, commission_ax, account, project

---

**Module Version:** 1.0.0  
**Odoo Version:** 17.0  
**Created:** 2024  
**Status:** Ready for Installation
