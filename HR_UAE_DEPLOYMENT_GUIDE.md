# HR UAE Payroll Compliance - Deployment Guide

## 🚀 Quick Deploy to Docker (5 Minutes)

### Prerequisites
- Odoo 17 Docker container running
- Database: `odoo17_test`
- Admin access to Odoo

---

## Method 1: Docker Copy (Recommended)

### Step 1: Copy Module to Docker Container
```bash
# From project root directory
docker cp test_modules/hr_uae_payroll_compliance odoo17:/mnt/extra-addons/

# Verify copy
docker exec odoo17 ls -la /mnt/extra-addons/hr_uae_payroll_compliance
```

**Expected output:**
```
total XX
drwxr-xr-x 5 odoo odoo 4096 Jan 23 10:00 .
drwxr-xr-x 8 odoo odoo 4096 Jan 23 10:00 ..
-rw-r--r-- 1 odoo odoo XXXX Jan 23 10:00 __init__.py
-rw-r--r-- 1 odoo odoo XXXX Jan 23 10:00 __manifest__.py
drwxr-xr-x 2 odoo odoo 4096 Jan 23 10:00 models
drwxr-xr-x 2 odoo odoo 4096 Jan 23 10:00 views
drwxr-xr-x 2 odoo odoo 4096 Jan 23 10:00 security
```

### Step 2: Restart Odoo Container
```bash
docker restart odoo17

# Check container is running
docker ps | grep odoo17
```

### Step 3: Install Module via Python Script
```bash
# Run installation script
python install_hr_uae_compliance.py
```

**Expected output:**
```
======================================================================
HR UAE PAYROLL COMPLIANCE - INSTALLATION
======================================================================

🔐 Authenticating...
✅ Authenticated as user ID: 2

📋 Updating module list...
✅ Module list updated

🔍 Searching for module 'hr_uae_payroll_compliance'...
✅ Module found (ID: XX)

📦 Module: HR UAE Payroll Compliance
📊 Current state: uninstalled

⚙️  Installing module...
   (This may take a minute...)

✅ Module installed successfully!

🔍 Verifying installation...
✅ Installation verified!

======================================================================
🎉 SUCCESS - HR UAE PAYROLL COMPLIANCE INSTALLED
======================================================================
```

---

## Method 2: Manual Installation (Alternative)

### Step 1: Copy Module
Same as Method 1, Step 1

### Step 2: Restart Odoo
Same as Method 1, Step 2

### Step 3: Install via Odoo Web Interface
1. Login to Odoo: http://localhost:8069
2. Go to: **Apps** menu
3. Click: **Update Apps List** (⚙️ icon → Update Apps List)
4. Confirm update
5. Search for: "HR UAE Payroll Compliance"
6. Click: **Install** button
7. Wait for installation to complete

---

## Method 3: Command Line (Advanced)

```bash
# Enter Docker container
docker exec -it odoo17 bash

# Inside container
cd /mnt/extra-addons/

# Install module via odoo-bin
/usr/bin/odoo -c /etc/odoo/odoo.conf -d odoo17_test -i hr_uae_payroll_compliance --stop-after-init

# Exit container
exit

# Restart container
docker restart odoo17
```

---

## Verification Steps

### 1. Check Module Installation
```bash
python check_hr_modules.py
```

Look for:
```
hr_uae_payroll_compliance | installed | v17.0.1.0.0 | HR UAE Payroll Compliance
```

### 2. Test Employee Compliance Tab
1. Navigate to: **HR → Employees**
2. Open any employee record
3. Look for new tab: **"UAE Compliance"**
4. Verify sections visible:
   - ✅ WPS (Wages Protection System)
   - ✅ Emirates ID
   - ✅ Visa & Immigration
   - ✅ Labor Card
   - ✅ GPSSA (if UAE national)
   - ✅ Compliance Summary

### 3. Test Contract Salary Structure
1. Navigate to: **HR → Contracts**
2. Open any contract or create new one
3. Look for: **"UAE Salary Structure (WPS Compliant)"** section
4. Enter test data:
   - Basic Salary: 5000 AED
   - Housing Allowance: 2000 AED
   - Transport Allowance: 1000 AED
5. Verify:
   - ✅ Total Salary computed: 8000 AED
   - ✅ Basic Salary %: 62.5%
   - ✅ WPS Compliant: True (green badge)

### 4. Test Validation (Should Fail)
1. In same contract, change:
   - Basic Salary: 3000 AED
   - Housing Allowance: 5000 AED
2. Try to save
3. Should see error:
   ```
   WPS Compliance Error: Basic salary must be at least 50% of total salary.
   
   Employee: [Name]
   Basic Salary: 3000.00 AED
   Total Salary: 8000.00 AED
   Current Percentage: 37.50%
   Required: ≥ 50.00%
   ```
4. This confirms validation is working! ✅

---

## Troubleshooting

### ❌ Module Not Found After Copy
**Problem:** Module doesn't appear in update list

**Solutions:**
1. Verify module location:
   ```bash
   docker exec odoo17 ls -la /mnt/extra-addons/hr_uae_payroll_compliance/__manifest__.py
   ```
2. Check file permissions:
   ```bash
   docker exec odoo17 chmod -R 755 /mnt/extra-addons/hr_uae_payroll_compliance
   ```
3. Restart container:
   ```bash
   docker restart odoo17
   ```
4. Check Odoo logs:
   ```bash
   docker logs odoo17 --tail 100
   ```

### ❌ Authentication Failed
**Problem:** install_hr_uae_compliance.py fails to authenticate

**Solutions:**
1. Verify database name:
   ```python
   # In script, check DB_NAME = 'odoo17_test'
   ```
2. Test connection manually:
   ```bash
   python test_sgctechai_connection.py
   ```
3. Check admin password (default: 'admin')

### ❌ Dependency Error on Install
**Problem:** "Module 'hr_uae' not found"

**Solutions:**
1. Install hr_uae module first:
   ```bash
   # Via Odoo UI: Apps → Search "HR UAE" → Install
   ```
2. Or modify __manifest__.py to remove 'hr_uae' from depends (temporary)

### ❌ Views Not Showing
**Problem:** UAE Compliance tab doesn't appear

**Solutions:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Reload page with hard refresh (Ctrl+F5)
3. Update module:
   ```bash
   python install_hr_uae_compliance.py
   # Choose "y" when asked to upgrade
   ```
4. Check for errors in Odoo logs:
   ```bash
   docker logs odoo17 --tail 200 | grep -i error
   ```

### ❌ XML View Errors
**Problem:** "Invalid XML" or view errors

**Solutions:**
1. Check XML syntax in views files:
   ```bash
   xmllint --noout test_modules/hr_uae_payroll_compliance/views/*.xml
   ```
2. Review Odoo error message carefully (it shows line number)
3. Common issues:
   - Missing closing tags
   - Incorrect xpath expressions
   - Invalid field references

---

## Post-Installation Tasks

### 1. Configure Existing Employees
For each employee:
- [ ] Add MOHRE Person ID (14 digits)
- [ ] Add Emirates ID (15 digits)
- [ ] Set Emirates ID expiry date
- [ ] Add visa details (if expat)
- [ ] Set payment method (bank/exchange)
- [ ] Add IBAN (if bank transfer)
- [ ] Check WPS Ready status

### 2. Update Existing Contracts
For each contract:
- [ ] Break down salary into components:
  - Basic Salary (minimum 50%)
  - Housing Allowance
  - Transport Allowance
  - Other Allowances
- [ ] Set UAE contract type (unlimited/limited)
- [ ] Verify WPS compliance (green badge)
- [ ] Set working hours (8/day, 48/week)

### 3. Test Compliance Filters
- [ ] HR → Employees → Filters → "WPS Incomplete"
- [ ] HR → Employees → Filters → "Emirates ID Expiring"
- [ ] HR → Contracts → Filters → "WPS Non-Compliant"
- [ ] Test Group By: WPS Status, Emirates ID Status

### 4. Train Users
Share this guide with:
- HR Managers
- Payroll Administrators
- Department Managers

Key points to cover:
- How to fill UAE Compliance tab
- WPS 50% requirement
- Document expiry tracking
- Compliance score meaning

---

## Sample Data (For Testing)

### Test Employee 1: Complete Compliance
```
Name: Ahmed Al Mansoori
MOHRE Person ID: 12345678901234
Emirates ID: 784199012345678
Emirates ID Expiry: 2025-12-31
Payment Method: Bank Transfer
IBAN: AE070331234567890123456
Bank Routing Code: 033123456
Is UAE National: Yes
GPSSA Registered: Yes
GPSSA Number: 1234567890
```

**Expected Results:**
- WPS Ready: ✅ True
- Compliance Score: 100%
- Status: All Green

### Test Contract 1: WPS Compliant
```
Basic Salary: 10,000 AED
Housing Allowance: 5,000 AED
Transport Allowance: 2,000 AED
Other Allowances: 1,000 AED
Total: 18,000 AED
Basic %: 55.56%
Contract Type: Unlimited
Working Hours: 8/day, 48/week
```

**Expected Results:**
- WPS Compliant: ✅ True
- Contract Compliant: ✅ True
- GPSSA Employee (5%): 850 AED
- GPSSA Employer (12.5%): 2,125 AED
- Gratuity Base: 10,000 AED

### Test Contract 2: WPS Non-Compliant (Should Fail)
```
Basic Salary: 4,000 AED
Housing Allowance: 5,000 AED
Transport Allowance: 3,000 AED
Total: 12,000 AED
Basic %: 33.33%
```

**Expected Results:**
- ❌ Validation Error: "Basic salary must be at least 50% of total"
- Cannot save contract
- Warning shown in form

---

## Support & Documentation

📖 **Full Documentation:**
- Module README: `test_modules/hr_uae_payroll_compliance/README.md`
- Odoo 17 HR Docs: https://www.odoo.com/documentation/17.0/applications/hr.html

🔧 **Source Files:**
- Models: `test_modules/hr_uae_payroll_compliance/models/`
- Views: `test_modules/hr_uae_payroll_compliance/views/`
- Security: `test_modules/hr_uae_payroll_compliance/security/`

📋 **Legal References:**
- UAE Labor Law: Federal Law No. 8 of 1980
- WPS Specifications: UAE Central Bank
- GPSSA: Federal Law No. 7 of 1999

---

## Success Checklist

Installation Complete When:
- ✅ Module shows "Installed" status
- ✅ "UAE Compliance" tab visible in employee form
- ✅ "UAE Salary Structure" section visible in contract form
- ✅ WPS validation working (50% rule enforced)
- ✅ Compliance score calculating correctly
- ✅ Document expiry tracking active
- ✅ Filters and search working
- ✅ Sample data tested successfully

---

**Installation Status:** ⏳ Pending  
**Last Updated:** January 2025  
**Version:** 1.0.0  
**Support:** SGC TECH AI
