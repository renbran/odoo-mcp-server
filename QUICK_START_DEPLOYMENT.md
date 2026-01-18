# Quick Start Guide - Deploy Fixed Module to scholarixv2

**Status:** ✅ Module Fixed and Ready  
**Target:** scholarixv2 @ erp.sgctech.ai  
**Branch:** copilot/fix-deal-management-module

---

## 🎯 What Was Fixed

**Issue:** Menu actions missing namespace → installation errors  
**Fix:** Added `deals_management.` prefix to all action references  
**Validation:** ✅ 44/44 checks passed

---

## 🚀 Deploy in 3 Steps

### Option 1: Automated (Easiest)

```bash
# From repository root
./deploy_to_scholarixv2.sh
```

That's it! The script will:
- Validate the module
- Create deployment package
- Upload to server
- Deploy with backup
- Restart Odoo

---

### Option 2: Git Pull (If server has Git access)

```bash
# SSH into server
ssh odoo@erp.sgctech.ai

# Navigate to addons
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc

# Pull the fix
git pull origin copilot/fix-deal-management-module

# Validate
python3 deals_management/validate_module.py deals_management/

# Restart Odoo
sudo systemctl restart odoo
```

---

### Option 3: Manual Upload

See detailed steps in: `SCHOLARIXV2_DEPLOYMENT_GUIDE.md`

---

## ✅ After Deployment

1. Login to https://erp.sgctech.ai
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Search "Deals Management"
5. Click **Install** (or **Upgrade**)
6. Wait ~30 seconds
7. Refresh browser (F5)

### Verify Success

- ✅ "Deals" menu appears (5 submenus)
- ✅ "Commissions" menu appears (6 submenus)
- ✅ Can create new deal
- ✅ No errors in console

---

## 📚 Documentation

- **Quick Start:** This file (you are here)
- **Deployment Guide:** SCHOLARIXV2_DEPLOYMENT_GUIDE.md
- **Complete Summary:** FIX_COMPLETE_SUMMARY.md
- **Validation Script:** deals_management/validate_module.py
- **Deploy Script:** deploy_to_scholarixv2.sh

---

## 🆘 Need Help?

### Module not showing in Apps?
```bash
sudo systemctl restart odoo
# Then: Apps → Update Apps List
```

### Permission errors?
```bash
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management
sudo systemctl restart odoo
```

### Still having issues?
Check the full troubleshooting guide in `SCHOLARIXV2_DEPLOYMENT_GUIDE.md`

---

## 🎯 Summary

**What:** Fixed deal_management module for scholarixv2  
**Where:** Branch copilot/fix-deal-management-module  
**How:** Use automated script or manual deployment  
**Status:** ✅ READY TO DEPLOY

**Next:** Choose deployment option above and proceed!

---

**Last Updated:** January 17, 2026  
**Commits:** 5 (all pushed)  
**Validation:** ✅ All checks pass
