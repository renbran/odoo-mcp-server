# 🚨 DEALS MANAGEMENT - INSTALLATION FIX GUIDE

**Status:** Module installation failed due to action reference error  
**Issue:** The server code is outdated (missing namespace fix)  
**Commit with fix:** `4041254` - add module namespace to action references  
**Generated:** January 17, 2026

---

## 🎯 Problem Summary

When attempting to install **deals_management** on scholarixv2, the following error occurred:

```
ValueError: External ID not found in the system: 
deals_management.action_deals_all_commissions
```

**Root Cause:** The module code on the server (`/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/`) is missing the action reference namespace fix.

**Location of error:** File `deals_management/views/deals_menu.xml` line 61

**Problem code:**
```xml
<menuitem id="menu_deals_all_commissions" name="All Commissions" 
          parent="menu_commissions_root" 
          action="action_deals_all_commissions" 
          sequence="1"/>
```

**Issue:** This references `action_deals_all_commissions` without the module namespace. Odoo requires the full reference: `deals_management.action_deals_all_commissions`.

---

## ✅ The Fix (Already Committed)

The fix has been **committed to the Git repository** at commit `4041254`:

**File:** `deals_management/views/deals_menu.xml`  
**Lines:** 35-55

**Changed from:**
```xml
action="action_deals_all_commissions"
```

**Changed to:**
```xml
action="deals_management.action_deals_all_commissions"
```

Applied to all 6 commission menu items.

---

## 🔧 How to Complete the Fix

You have **2 options**:

### OPTION A: Update Code via Git (Recommended)

**Requirements:** SSH access to server + Git access

**Steps:**

1. SSH into the server:
```bash
ssh odoo@erp.sgctech.ai
```

2. Navigate to the module directory:
```bash
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
```

3. Pull the latest code:
```bash
git pull origin mcp2odoo
```

4. Verify the fix was applied:
```bash
git log --oneline -3
# Should show commit 4041254 at the top
```

5. Check the file was updated:
```bash
grep -n "deals_management.action" deals_management/views/deals_menu.xml
# Should show the namespace prefix in action attributes
```

6. Verify no syntax errors:
```bash
grep "action=" deals_management/views/deals_menu.xml | head -10
```

7. Exit SSH:
```bash
exit
```

**Then proceed to step "Reinstall Module in Odoo" below.**

---

### OPTION B: Manual File Edit (If Git unavailable)

**Requirements:** File editing access to server

**Steps:**

1. Open the file:
```
/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/views/deals_menu.xml
```

2. Find these lines (~line 35-55):

```xml
<!-- ===== COMMISSIONS SUBMENUS ===== -->

<!-- All Commissions -->
<menuitem id="menu_deals_all_commissions" name="All Commissions" 
          parent="menu_commissions_root" 
          action="action_deals_all_commissions"    <!-- ❌ NEEDS FIX -->
          sequence="1"/>

<!-- Pending Bills (No Bill Created) -->
<menuitem id="menu_deals_pending_bills" name="Pending Bills" 
          parent="menu_commissions_root" 
          action="action_deals_pending_bills"      <!-- ❌ NEEDS FIX -->
          sequence="2"/>

<!-- ... etc for remaining 4 items ... -->
```

3. Replace each instance:

| Find | Replace |
|------|---------|
| `action="action_deals_all_commissions"` | `action="deals_management.action_deals_all_commissions"` |
| `action="action_deals_pending_bills"` | `action="deals_management.action_deals_pending_bills"` |
| `action="action_deals_paid_bills"` | `action="deals_management.action_deals_paid_bills"` |
| `action="action_deals_commission_by_partner"` | `action="deals_management.action_deals_commission_by_partner"` |
| `action="action_deals_vendor_bills"` | `action="deals_management.action_deals_vendor_bills"` |
| `action="action_deals_commission_report"` | `action="deals_management.action_deals_commission_report"` |

4. Save the file.

**Then proceed to step "Reinstall Module in Odoo" below.**

---

## 🔄 Reinstall Module in Odoo

Once the code is fixed (via Git or manual edit), complete the installation:

**Steps:**

1. Open browser and go to: **https://erp.sgctech.ai/web**

2. Log in as **Administrator**
   - Username: `info@scholarixglobal.com`
   - Password: `123456`

3. Go to **Apps** menu (top navigation)

4. Remove any search filters to see all apps

5. Search for **"Deals Management"**

6. When the module appears:
   - **If UNINSTALLED:** Click the **Install** button
   - **If INSTALLED (with errors):** Click the dropdown menu (⋮) → **Uninstall** → Wait → Then click **Install**

7. Monitor the installation:
   - A progress bar will appear
   - Installation typically takes 30-60 seconds
   - Do NOT refresh or navigate away

8. Wait for completion message:
   - ✅ Success: "Module installed successfully"
   - ❌ Error: Check the error message (should not occur if fix is applied)

9. **Refresh the browser** (F5)

10. Look for these menus in the navigation bar:
    - ✅ **Deals** menu should appear (top navigation)
    - ✅ **Commissions** menu should appear (top navigation)

---

## ✅ Verification Checklist

After installation, verify everything works:

### Check 1: Menus Visible
- [ ] "Deals" menu appears in main navigation
- [ ] "Commissions" menu appears in main navigation

### Check 2: Deals Menu Submenus
- [ ] Deals > All Deals (clickable, no errors)
- [ ] Deals > Primary Sales (clickable, no errors)
- [ ] Deals > Secondary Sales (clickable, no errors)
- [ ] Deals > Exclusive Sales (clickable, no errors)
- [ ] Deals > Rental Deals (clickable, no errors)

### Check 3: Commissions Menu Submenus
- [ ] Commissions > All Commissions (clickable, no errors)
- [ ] Commissions > Pending Bills (clickable, no errors)
- [ ] Commissions > Paid Bills (clickable, no errors)
- [ ] Commissions > Commission by Partner (clickable, no errors)
- [ ] Commissions > Vendor Bills (clickable, no errors)
- [ ] Commissions > Commission Report (clickable, no errors)

### Check 4: Browser Console
- [ ] Open Developer Tools (F12)
- [ ] Go to Console tab
- [ ] No red errors related to "action" or "deals_management"
- [ ] No references to missing external IDs

### Check 5: Create Test Deal
- [ ] Go to Sales > Orders > Create
- [ ] Verify "Sales Type" field exists (new field from module)
- [ ] Verify "Buyer Name" field exists
- [ ] Verify "Project" field exists
- [ ] Fill a few fields and save
- [ ] No errors

### Check 6: Module Status
- [ ] Go to Apps > Deals Management
- [ ] Status shows "Installed"
- [ ] No error messages displayed

---

## 🚨 Troubleshooting

### Issue: Still getting "External ID not found" error

**Cause:** The code fix wasn't applied or wasn't reloaded.

**Solutions:**
1. Verify the file was actually edited (Option A or B above)
2. If using Git, run `git pull origin mcp2odoo` again
3. Try uninstalling then reinstalling the module
4. Check file modification time (should be recent)

### Issue: Module appears as "Uninstalled" even after attempting install

**Cause:** Installation failed silently. Check server logs.

**Solutions:**
1. Go to `/var/odoo/scholarixv2/odoo.log`
2. Look for errors mentioning "deals_management" or "action"
3. If you see action reference errors, the XML fix wasn't applied
4. Apply the fix (Option A or B) and retry

### Issue: Menus don't appear after installation

**Cause:** Module installed but menus not loading. Could be permissions or caching.

**Solutions:**
1. Refresh browser with hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Log out and log back in
4. Try a different browser
5. Check browser console for JavaScript errors

### Issue: Can click menu but get "Action not found" error

**Cause:** Action definition is still broken or missing from views.

**Solutions:**
1. Verify the action definition in `deals_management/views/deals_views.xml` (lines 226-281)
2. Ensure all actions are defined (11 total)
3. Check that action IDs match the menu references
4. Restart Odoo service if available: `sudo systemctl restart odoo-scholarixv2`

---

## 📊 What the Fix Includes

After applying the fix and reinstalling, the module provides:

✅ **18 new fields** on sale.order:
- Sales type (selection)
- Buyer information (name, email, phone, address)
- Co-buyer details
- Reference person
- Property unit reference
- Booking and invoice dates
- Financial tracking (commission rate, VAT, totals)
- Document counters

✅ **11 new menu items:**
- 5 under "Deals" (All, Primary, Secondary, Exclusive, Rental)
- 6 under "Commissions" (All, Pending, Paid, by Partner, Vendor Bills, Reports)

✅ **8+ new views:**
- Deal list/form/search views
- Commission tracking views
- Report views (graph, pivot)

✅ **Full integration** with:
- Sale orders
- Commission tracking (commission_ax module)
- Project management
- Accounting

---

## 📞 Support

If you still encounter issues:

1. **Check the logs:** `/var/odoo/scholarixv2/odoo.log`
2. **Verify the code:** Run `git log --oneline -1` to confirm commit 4041254 is applied
3. **Re-run the script:**
   ```bash
   python /path/to/diagnose_action_issue.py
   ```

---

## ✨ Summary

| Step | Status | Notes |
|------|--------|-------|
| Fix committed | ✅ Done | Commit 4041254 has the namespace fix |
| Local code updated | ✅ Done | All action references now have `deals_management.` prefix |
| Server code needs update | ⏳ Pending | Need to git pull or manually edit on server |
| Module needs reinstall | ⏳ Pending | After code update, install/upgrade in Odoo UI |
| Verification | ⏳ Pending | Check menus appear and no errors |

**Next action:** Follow Option A or B above to update the server code, then reinstall the module.

---

**Issues?** Check the [DEALS_PRODUCTION_READINESS.md](DEALS_PRODUCTION_READINESS.md) for comprehensive documentation.
