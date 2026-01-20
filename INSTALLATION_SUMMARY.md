# Invoice Status Tags Module - Installation Guide

## Quick Summary

**Module Created:** ✅ invoice_status_tags  
**ZIP File:** ✅ invoice_status_tags.zip (7.04 KB)  
**Status:** Ready for installation

---

## Installation Methods

### Method 1: Odoo Apps Upload (EASIEST) ⭐

1. **Login to Odoo**
   - URL: https://erposus.com
   - User: salescompliance@osusproperties.com

2. **Enable Developer Mode**
   - Click username (top right) → Settings
   - Activate developer mode
   - Or add to URL: https://erposus.com/web?debug=1

3. **Upload Module**
   - Go to **Apps** menu
   - Remove search filters (click X)
   - Click **Upload** button (top right)
   - Select: `invoice_status_tags.zip`
   - Click Upload

4. **Install Module**
   - Search: "Invoice Status Tags"
   - Click **Install**
   - Wait for completion

5. **Update Records**
   - Run: `python update_all_records_after_install.py`

---

### Method 2: CloudPepper File Manager

1. Login to CloudPepper control panel
2. Navigate to: `/opt/odoo/custom/addons/`
3. Create folder: `invoice_status_tags`
4. Upload all module files (maintain folder structure)
5. Set permissions: Folders=755, Files=644
6. Restart Odoo server
7. In Odoo: Apps → Update Apps List
8. Search and install "Invoice Status Tags"
9. Run: `python update_all_records_after_install.py`

---

### Method 3: Contact CloudPepper Support

Email them with:
- **Subject:** Install Custom Module - invoice_status_tags
- **Attachment:** invoice_status_tags.zip
- **Request:** Extract to custom addons, update apps list, install module

---

## What You'll Get

### Visual Indicators
- 🔴 Red ribbon: "DRAFT INVOICE WARNING"
- 🟡 Yellow ribbon: "NEEDS ATTENTION"
- 🔵 Blue ribbon: "UPSELL"

### New Fields
- **Invoice Type Badge** (color-coded status)
- **Invoicing Progress** (progress bar %)
- **Invoice Breakdown** (X Posted | Y Draft | Z Cancelled)
- **Total Invoiced** (posted invoices only)
- **Remaining to Invoice**
- **Upsell Amount** (if applicable)

### New Filters
- Needs Attention
- Has Draft Invoices
- **Partial Invoicing** ⭐
- Upsell Orders
- Draft Only

### New Menus
- Sales → Orders → **Needs Attention**
- Sales → Orders → **Partial Invoicing**

---

## Files Created

```
D:/odoo17_backup/odoo-mcp-server/
├── invoice_status_tags/              # Module folder
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── README.md
│   ├── models/
│   │   ├── __init__.py
│   │   └── sale_order.py
│   └── views/
│       └── sale_order_views.xml
├── invoice_status_tags.zip            # Ready to upload
└── update_all_records_after_install.py  # Run after install
```

---

## Next Steps

1. ✅ Module files created
2. ⏳ Upload to Odoo (choose method above)
3. ⏳ Install module
4. ⏳ Run update script: `python update_all_records_after_install.py`
5. ✅ Enjoy better invoice visibility!

---

## Support

**Module Location:** `D:/odoo17_backup/odoo-mcp-server/invoice_status_tags/`  
**ZIP File:** `D:/odoo17_backup/odoo-mcp-server/invoice_status_tags.zip`  
**Documentation:** `invoice_status_tags/README.md`

---

**Created:** 2026-01-19  
**Author:** SGC TECH AI  
**License:** LGPL-3
