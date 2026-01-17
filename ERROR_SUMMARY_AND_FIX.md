# 🔴 INSTALLATION ERROR - WHAT HAPPENED & HOW TO FIX

**Date:** January 17, 2026  
**Module:** deals_management v17.0.1.0.0  
**Server:** scholarixv2 (erp.sgctech.ai)  
**Error Code:** `ValueError: External ID not found in the system`

---

## What Happened

You tried to **install the deals_management module** on the scholarixv2 server. The installation **failed** with this error:

```
ValueError: External ID not found in the system: 
deals_management.action_deals_all_commissions
```

### Root Cause

The **server version of the module code is OUTDATED**. It's missing a critical fix that we applied locally.

**Problem Location:** `deals_management/views/deals_menu.xml` line 61

The file on the server has:
```xml
action="action_deals_all_commissions"
```

But it should have:
```xml
action="deals_management.action_deals_all_commissions"
```

### Why This Matters

When Odoo loads the module, it tries to find an action called `action_deals_all_commissions`. But since the module hasn't been loaded yet at that point in the data loading sequence, Odoo automatically prepends the module name, looking for `deals_management.action_deals_all_commissions`.

However, the menu XML file is referencing it without the namespace, so Odoo can't find it during the loading process.

---

## The Fix

We **already fixed this locally** in commit `4041254`:

✅ Updated `deals_management/views/deals_menu.xml` (lines 35-55)  
✅ Added module namespace to all 6 commission action references  
✅ Committed to Git repository (branch: mcp2odoo)

**But the fix isn't on the server yet.**

---

## How to Complete the Fix

### Step 1: Update Server Code

**Option A - Via Git (Recommended):**

```bash
ssh odoo@erp.sgctech.ai
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
git pull origin mcp2odoo
```

**Option B - Manual Edit (If no SSH):**

Edit `/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/views/deals_menu.xml`

Change these 6 lines (around line 35-55):

```diff
- action="action_deals_all_commissions"
+ action="deals_management.action_deals_all_commissions"

- action="action_deals_pending_bills"
+ action="deals_management.action_deals_pending_bills"

- action="action_deals_paid_bills"
+ action="deals_management.action_deals_paid_bills"

- action="action_deals_commission_by_partner"
+ action="deals_management.action_deals_commission_by_partner"

- action="action_deals_vendor_bills"
+ action="deals_management.action_deals_vendor_bills"

- action="action_deals_commission_report"
+ action="deals_management.action_deals_commission_report"
```

### Step 2: Reinstall Module in Odoo UI

1. Go to https://erp.sgctech.ai/web
2. Login as administrator
3. **Apps** menu
4. Search **"Deals Management"**
5. Click **Install** (or **Upgrade** if already installed)
6. Wait for completion (~30 seconds)
7. **Refresh browser** (F5)

### Step 3: Verify

After installation, you should see:
- ✅ "Deals" menu in top navigation
- ✅ "Commissions" menu in top navigation
- ✅ All submenus accessible
- ✅ No JavaScript errors in browser (F12 > Console)

---

## Why Was There a Delay?

We fixed the code **locally** but the server had an **outdated copy** of the module. The fix is in the Git repository, but the server needs to pull it.

Timeline:
1. ✅ Code fixed locally (commit 4041254)
2. ✅ Pushed to Git repository
3. ❌ Server still has old version
4. ❌ Installation failed
5. ⏳ Need to pull latest code to server
6. ⏳ Then reinstall module

---

## Complete Fix Timeline

| Step | Status | When |
|------|--------|------|
| 1. Fix identified | ✅ Done | During development |
| 2. Fix committed | ✅ Done | Commit 4041254 |
| 3. Deploy to server | ⏳ **NOW** | Git pull or manual edit |
| 4. Reinstall module | ⏳ **AFTER DEPLOY** | Odoo UI install/upgrade |
| 5. Verify | ⏳ **FINAL** | Check menus appear |

---

## Next Action

👉 **Run this command on the server:**

```bash
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc && \
git pull origin mcp2odoo && \
git log --oneline -1
```

Expected output should show commit `4041254` or newer.

**Then:** Go to Odoo UI and install/upgrade the module.

---

## Questions?

Refer to the detailed guide: [INSTALLATION_FIX_GUIDE.md](INSTALLATION_FIX_GUIDE.md)

For complete module documentation: [DEALS_PRODUCTION_READINESS.md](DEALS_PRODUCTION_READINESS.md)
