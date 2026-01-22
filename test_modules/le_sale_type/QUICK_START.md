# Quick Start Guide - Sale Order Type Invoice Integration

## 5-Minute Quick Start

### If Module is Already Installed (Upgrading from v1.0)

```bash
# 1. Backup database (CRITICAL!)
pg_dump -U odoo -d your_database > backup_$(date +%Y%m%d).sql

# 2. Restart Odoo
sudo systemctl restart odoo17

# 3. Log into Odoo as Administrator
```

Then in Odoo UI:
1. Settings → Apps
2. Remove "Apps" filter
3. Search: "Sale Order Type"
4. Click: **Upgrade**
5. Wait for completion
6. Test: Create invoice from sale order → Verify Sale Type auto-fills

**Done!** Module is upgraded to v1.1.0.

---

### If Fresh Installation (Module Not Installed)

```bash
# 1. Verify module is in addons directory
ls "D:\RUNNING APPS\odoo17\osuspropertiesv1\le_sale_type"

# 2. Restart Odoo
sudo systemctl restart odoo17

# 3. Log into Odoo as Administrator
```

Then in Odoo UI:
1. Settings → Apps
2. Update Apps List (three dots menu)
3. Search: "Sale Order Type"
4. Click: **Install**
5. Configure sale types: Sales → Configuration → Sale Order Types
6. Create test sale order with type
7. Create invoice → Verify Sale Type auto-fills

**Done!** Module is installed.

---

## What You Get

After installation/upgrade:

### On Invoices
- **Sale Type** field in form view (auto-filled from sale orders)
- **Sale Type** column in list view
- Filter/search by sale type
- Group by sale type
- Pivot/graph analytics

### On Credit Notes
- Sale Type automatically copied from original invoice

### Smart Features
- Auto-fetch from sale order (no manual input)
- Works with multiple invoice lines
- Editable if manual adjustment needed
- Only shows on customer invoices (not supplier bills)

---

## Quick Test (2 Minutes)

1. **Create Sale Order**:
   - Sales → Quotations → Create
   - Customer: Any customer
   - Sale Type: Select any type
   - Add product line
   - Click Confirm

2. **Create Invoice**:
   - Click "Create Invoice"
   - Select "Regular Invoice"
   - Click "Create and View Invoice"
   - **Check**: Sale Type field is filled automatically ✓

3. **Verify List View**:
   - Invoicing → Invoices
   - **Check**: Sale Type column visible ✓
   - **Check**: Can filter by Sale Type ✓

**Test Passed!** Integration working correctly.

---

## Troubleshooting

### Problem: Sale Type field not showing on invoice

**Solution**:
```bash
# Clear cache and restart
sudo systemctl restart odoo17
# Then refresh browser (Ctrl+F5)
```

### Problem: Module won't upgrade

**Solution**:
1. Enable Developer Mode (Settings → Activate Developer Mode)
2. Apps → Remove "Apps" filter
3. Try upgrade again

### Problem: Field shows but doesn't auto-fill

**Check**:
- Sale order has Sale Type set?
- Invoice created FROM sale order (not manually)?
- Invoice is customer invoice (not supplier bill)?

---

## Next Steps

1. **Read Full Docs**: See `README.md` for complete guide
2. **Run Full Tests**: See `TESTING_GUIDE.md` for all test cases
3. **Production Deploy**: See `DEPLOYMENT_GUIDE.md` for checklist

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation |
| `TESTING_GUIDE.md` | 20 test cases |
| `DEPLOYMENT_GUIDE.md` | Production deployment |
| `INTEGRATION_SUMMARY.md` | Technical details |
| `QUICK_START.md` | This file |

---

## Support

**Issues?** Check:
1. TESTING_GUIDE.md → Troubleshooting section
2. DEPLOYMENT_GUIDE.md → Troubleshooting section
3. Odoo logs: `/var/log/odoo/odoo-server.log`

**Still stuck?** Contact: support@lunerpsolution.com

---

**Version**: 1.1.0 | **Ready for Production** ✓
