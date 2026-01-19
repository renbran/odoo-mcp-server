# Odoo MCP Server - One-Page Quick Reference

## 🎯 Setup (2 Minutes)

**Step 1:** Copy this file:
```
d:\odoo17_backup\odoo-mcp-server\claude_desktop_config.json
```

**Step 2:** Paste to:
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Step 3:** Restart Claude Desktop → Look for ✓ in bottom-left corner

---

## 📋 Your 6 Odoo Instances

| Instance | URL | Version |
| -------- | --- | ------- |
| scholarixv2 | https://erp.sgctech.ai | v17 |
| osusproperties | https://erposus.com | v17 |
| eigermarvelhr | https://eigermarvelhr.com | v18 |
| scholarix-restaurant | https://scholarix.cloudpepper.site | v18 |
| testserver-hospital | https://testserver.cloudpepper.site | v18 |
| sgctechai | https://scholarixglobal.com | v19 |

---

## 🛠️ 11 Available Tools

| Tool | What It Does | Example |
| ---- | ------------ | ------- |
| **odoo_search** | Find records with filters | Search for customers in scholarixv2 |
| **odoo_search_read** | Search + read combined | Get top 10 orders by amount |
| **odoo_read** | Get record details by ID | Show customer details for ID 5 |
| **odoo_create** | Create new records | Create a new customer |
| **odoo_update** | Modify existing records | Update order status |
| **odoo_delete** | Remove records | Delete old test data |
| **odoo_execute** | Run model methods | Execute action_confirm |
| **odoo_count** | Count matching records | How many active customers? |
| **odoo_workflow_action** | Click workflow buttons | Post invoice #100 |
| **odoo_generate_report** | Create PDF reports | Generate invoice PDF |
| **odoo_get_model_metadata** | See field definitions | Show all fields on sale.order |

---

## 💡 Quick Ask Examples

```
"Find all customers in scholarixv2"
→ Returns: List of customers

"How many orders in eigermarvelhr?"
→ Returns: Order count

"Create a new customer 'Tech Corp' in osusproperties"
→ Returns: New record ID

"Update order SO001 status to shipped"
→ Returns: Confirmation

"Generate invoice PDF for order #100"
→ Returns: PDF file

"Show me fields on res.partner"
→ Returns: All available fields
```

---

## 🔍 Domain Filter Syntax

```python
# Basic
[['name', '=', 'John']]                    # Exact match
[['amount', '>', 1000]]                    # Greater than
[['email', 'like', '@company.com']]        # Contains

# Logical
['&', ['state', '=', 'sale'], ['amount', '>', 5000]]  # AND
['|', ['name', '=', 'John'], ['name', '=', 'Jane']]   # OR
['!', ['state', '=', 'cancel']]                        # NOT

# Related fields
[['partner_id.country_id.code', '=', 'US']]           # Nested fields
```

---

## 📊 Common Models

**Sales:** sale.order, sale.order.line, crm.lead
**Accounting:** account.move, account.payment
**Inventory:** stock.picking, product.product
**Contacts:** res.partner, res.company, res.users
**HR:** hr.employee, hr.department
**Projects:** project.project, project.task
**Purchase:** purchase.order

---

## ⚡ Quick Verification

Ask Claude these questions:

1. **"What instances are available?"**
   - Should list all 6 instances

2. **"Search for customers in scholarixv2"**
   - Should return customer records

3. **"How many sale orders in eigermarvelhr?"**
   - Should return a number

4. **"Show me fields on res.partner in osusproperties"**
   - Should list all customer fields

---

## 🐛 Troubleshooting

| Issue | Solution |
| ----- | --------- |
| Claude doesn't see instances | Restart Claude Desktop |
| "Authentication failed" | Check username/password in .env |
| "Model not found" | Use exact Odoo model name (e.g., res.partner) |
| "Instance not found" | Check exact name: scholarixv2 (not scholarix-v2) |
| Instance offline | Verify URL reachable: ping erp.sgctech.ai |
| No results | Check domain filter syntax or increase limit |

---

## 📚 Documentation Files

- **QUICK-START.md** - 2-minute setup (this page)
- **USAGE-GUIDE.md** - 30-minute comprehensive guide (3,500+ words)
- **SETUP-CHECKLIST.md** - 6-phase verification
- **IMPLEMENTATION-SUMMARY.md** - What was built
- **DOCUMENTATION-INDEX.md** - Full index with learning path

---

## 🚀 Next Steps

### Today
- [ ] Copy config to Claude
- [ ] Restart Claude Desktop
- [ ] Ask: "What instances are available?"

### This Week
- [ ] Read USAGE-GUIDE.md
- [ ] Test each of 11 tools
- [ ] Create dedicated API users

### This Month
- [ ] Set up backups
- [ ] Deploy to production (optional)
- [ ] Optimize queries

---

## 🔐 Security Checklist

- [ ] .env file never shared
- [ ] Use dedicated API users (not admin)
- [ ] Strong passwords (16+ characters)
- [ ] Regular credential rotation
- [ ] Automated backups enabled
- [ ] Audit logging configured
- [ ] Network firewall rules set

---

## 📞 Help

- **Setup issues?** → See SETUP-CHECKLIST.md
- **Need examples?** → See USAGE-GUIDE.md (Section 7)
- **Domain filters?** → See USAGE-GUIDE.md (Section 10)
- **Troubleshooting?** → See SETUP-CHECKLIST.md or USAGE-GUIDE.md

---

## ✅ Success Criteria

You're good to go when:
- ✅ Claude shows green checkmark
- ✅ Can ask Claude questions
- ✅ Get answers about your Odoo data
- ✅ All 6 instances are responsive
- ✅ No authentication errors

---

**Print this page. Keep it handy. You're ready! 🎉**

---

**Created:** January 13, 2026  
**Status:** Production-Ready  
**Setup Time:** 2 minutes  
**Learn Time:** 30 minutes  
**Full Documentation:** See DOCUMENTATION-INDEX.md
