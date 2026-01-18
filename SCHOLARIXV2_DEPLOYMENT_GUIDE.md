# Deployment Guide for deals_management Module to scholarixv2

**Server:** erp.sgctech.ai  
**Database:** scholarixv2  
**Module:** deals_management v17.0.1.0.0  
**Date:** January 17, 2026

---

## ✅ What Was Fixed

The module had missing namespace prefixes in action references within `deals_menu.xml`. This has been fixed in commit `f43ec28`.

### Changes Applied:
- Added `deals_management.` prefix to all 11 action references in menu items
- Created validation script (`validate_module.py`) for pre-deployment checks
- All validation checks pass ✅

---

## 📋 Pre-Deployment Checklist

Before deploying to scholarixv2, ensure:

- [ ] You have SSH access to erp.sgctech.ai
- [ ] You have sudo privileges or access to the odoo user
- [ ] commission_ax module is already installed on scholarixv2
- [ ] You have a backup of the current system (if module was previously installed)

---

## 🚀 Deployment Steps

### Option A: Deploy via Git Pull (Recommended)

If the server has Git access to this repository:

```bash
# 1. SSH into the server
ssh odoo@erp.sgctech.ai

# 2. Navigate to the addons directory
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc

# 3. Pull the latest changes
git fetch origin
git checkout copilot/fix-deal-management-module
git pull origin copilot/fix-deal-management-module

# 4. Verify the fix was applied
python3 deals_management/validate_module.py deals_management/

# 5. Restart Odoo service
sudo systemctl restart odoo

# 6. Exit SSH
exit
```

### Option B: Manual File Upload

If Git access is not available:

```bash
# 1. From your local machine, create a deployment package
cd /home/runner/work/odoo-mcp-server/odoo-mcp-server
tar -czf deals_management_fixed.tar.gz deals_management/

# 2. Upload to server
scp deals_management_fixed.tar.gz odoo@erp.sgctech.ai:/tmp/

# 3. SSH into server
ssh odoo@erp.sgctech.ai

# 4. Backup existing module (if installed)
sudo tar -czf /var/odoo/backups/deals_management_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management 2>/dev/null || true

# 5. Remove old module
sudo rm -rf /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management

# 6. Extract new module
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
sudo tar -xzf /tmp/deals_management_fixed.tar.gz

# 7. Set proper permissions
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management

# 8. Validate the module
python3 deals_management/validate_module.py deals_management/

# 9. Restart Odoo
sudo systemctl restart odoo
sudo systemctl status odoo

# 10. Exit SSH
exit
```

---

## 🔧 Module Installation in Odoo UI

After deploying the files:

### If Module is NOT Installed Yet:

1. Login to https://erp.sgctech.ai
2. Navigate to **Apps** menu
3. Click **Update Apps List** button
4. Search for "Deals Management"
5. Click **Install**
6. Wait for installation to complete (~30-60 seconds)
7. Refresh browser (F5)
8. Verify menus appear:
   - "Deals" menu in top navigation
   - "Commissions" menu in top navigation

### If Module is Already Installed:

1. Login to https://erp.sgctech.ai
2. Navigate to **Apps** menu
3. Remove all filters (click X on search filters)
4. Search for "Deals Management"
5. Click **Upgrade** button
6. Wait for upgrade to complete
7. Refresh browser (F5)

---

## ✅ Post-Deployment Verification

After installation/upgrade, verify:

### 1. Menu Structure
- [ ] "Deals" menu appears in top navigation
- [ ] "Commissions" menu appears in top navigation
- [ ] Click "Deals" → Should show 5 submenus:
  - All Deals
  - Primary Sales
  - Secondary Sales
  - Exclusive Sales
  - Rental Deals
- [ ] Click "Commissions" → Should show 6 submenus:
  - All Commissions
  - Pending Bills
  - Paid Bills
  - Commission by Partner
  - Vendor Bills
  - Commission Report

### 2. Test Creating a Deal
- [ ] Go to Deals → All Deals
- [ ] Click "Create" button
- [ ] Fill in required fields:
  - Customer
  - Sales Type (Primary/Secondary/Exclusive/Rental)
  - Booking Date
  - Unit Reference
- [ ] Click "Save"
- [ ] Verify deal is created successfully

### 3. Check for Errors
- [ ] Open browser console (F12)
- [ ] Check for JavaScript errors (Console tab)
- [ ] Check Odoo server logs:
  ```bash
  ssh odoo@erp.sgctech.ai
  sudo tail -f /var/log/odoo/odoo.log
  ```
- [ ] Verify no Python exceptions appear

### 4. Test Smart Buttons
- [ ] Open any deal
- [ ] Verify smart buttons appear:
  - Invoices
  - Commissions
  - Bills
  - KYC Documents
  - Booking Forms
  - Passports
- [ ] Click each button to ensure they work

---

## 🆘 Troubleshooting

### Issue: Module not showing in Apps list

**Solution:**
```bash
ssh odoo@erp.sgctech.ai
sudo systemctl restart odoo
# Then in Odoo UI: Apps → Update Apps List
```

### Issue: "External ID not found" error during installation

**Solution:** This should be fixed now, but if it still occurs:
1. Verify the fix was applied: `grep "deals_management\." deals_management/views/deals_menu.xml`
2. Should show all action references with module namespace
3. If not, re-deploy following Option B above

### Issue: Permission denied errors

**Solution:**
```bash
ssh odoo@erp.sgctech.ai
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management
sudo systemctl restart odoo
```

### Issue: Menus not appearing after installation

**Solution:**
1. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. Clear browser cache
3. Try in incognito/private browsing mode
4. Check if user has proper access rights

### Issue: commission_ax dependency not found

**Solution:**
```bash
# Install commission_ax module first
# In Odoo UI: Apps → Search "Commission AX" → Install
```

---

## 📊 Module Dependencies

The deals_management module requires:

1. **sale** (Odoo core module) - ✅ Always available
2. **commission_ax** (Custom module) - ⚠️ Must be installed first
3. **account** (Odoo core module) - ✅ Always available
4. **project** (Odoo core module) - ✅ Usually available

If any dependency is missing, install it first before installing deals_management.

---

## 🔄 Rollback Procedure

If you need to rollback to the previous version:

```bash
ssh odoo@erp.sgctech.ai

# Find the backup
ls -lt /var/odoo/backups/deals_management_backup_*.tar.gz | head -1

# Restore from backup
sudo rm -rf /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
sudo tar -xzf /var/odoo/backups/deals_management_backup_YYYYMMDD_HHMMSS.tar.gz --strip-components=7

# Restart Odoo
sudo systemctl restart odoo
```

---

## 📝 Important Notes

1. **Database Backup**: It's recommended to backup the scholarixv2 database before major module upgrades
   ```bash
   sudo -u postgres pg_dump scholarixv2 > scholarixv2_backup_$(date +%Y%m%d).sql
   ```

2. **Maintenance Mode**: For production systems, consider enabling maintenance mode during deployment

3. **Testing**: If possible, test the module on a staging environment first

4. **User Training**: After deployment, inform users about new features and any UI changes

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ Module installs/upgrades without errors
- ✅ All 11 menu items are visible and functional
- ✅ Can create and save deals
- ✅ Smart buttons work correctly
- ✅ No errors in browser console or server logs
- ✅ Commission integration works (if commission_ax is installed)

---

## 📞 Support

If you encounter issues not covered in this guide:

1. Run the validation script:
   ```bash
   python3 deals_management/validate_module.py deals_management/
   ```

2. Check Odoo logs:
   ```bash
   sudo tail -f /var/log/odoo/odoo.log
   ```

3. Review the module documentation:
   - README.md
   - TESTING_GUIDE.md
   - DEVELOPER_GUIDE.md

---

**Deployment Guide Version:** 1.0  
**Last Updated:** January 17, 2026  
**Prepared for:** scholarixv2 deployment
