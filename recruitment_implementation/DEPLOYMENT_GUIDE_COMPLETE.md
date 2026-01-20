# 🚀 RECRUITMENT_UAE MODULE - DEPLOYMENT GUIDE

**Module:** recruitment_uae (Retention & Follow-up Management)  
**Version:** 1.0.0  
**Odoo Compatibility:** 17, 18, 19+  
**Status:** ✅ Ready for Production Deployment

---

## 📋 PRE-DEPLOYMENT CHECKLIST

- [ ] Backup Odoo database
- [ ] Backup Odoo addons folder
- [ ] Test deployment in staging environment first
- [ ] Verify all users understand new features
- [ ] Schedule deployment during low-traffic window
- [ ] Have rollback plan ready
- [ ] Document any customizations before upgrade

---

## 🔧 DEPLOYMENT STEPS

### Step 1: Backup Database & Addons

#### On Odoo Server:

```bash
# Backup PostgreSQL database
sudo -u postgres pg_dump -d your_database_name > ~/odoo_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup addons folder
cp -r /opt/odoo/addons ~/odoo_addons_backup_$(date +%Y%m%d_%H%M%S)

# Store backups securely
sudo mkdir -p /backups/odoo
sudo cp ~/odoo_backup_*.sql /backups/odoo/
```

---

### Step 2: Copy Module Files

#### Option A: Copy to Central Addons Directory

```bash
# Navigate to addons directory
cd /opt/odoo/addons

# Copy recruitment_uae module
sudo cp -r ~/recruitment_implementation ./recruitment_uae

# Set proper permissions
sudo chown -R odoo:odoo recruitment_uae
sudo chmod -R 755 recruitment_uae
```

#### Option B: Copy to Custom Addons Directory

```bash
# Navigate to custom addons directory
cd /home/odoo/custom-addons

# Copy recruitment_uae module
sudo cp -r ~/recruitment_implementation ./recruitment_uae

# Set proper permissions
sudo chown -R odoo:odoo recruitment_uae
sudo chmod -R 755 recruitment_uae
```

#### Option C: For Cloudpaper/Hosting Providers

1. Login to hosting control panel
2. Navigate to: Files → Addons folder
3. Create new folder: `recruitment_uae`
4. Upload all files from `recruitment_implementation` folder
5. Set permissions to 755 (read/write/execute for owner)

---

### Step 3: Stop Odoo Service

```bash
# For systemd
sudo systemctl stop odoo

# For supervisor
sudo supervisorctl stop odoo

# For standalone
# Kill the process manually if needed
sudo pkill -f odoo
```

**Wait 10-15 seconds for graceful shutdown**

---

### Step 4: Update Odoo Addons Path (if needed)

Edit `/etc/odoo/odoo.conf` or your Odoo configuration file:

```ini
[options]
# Add this path if not already present
addons_path = /opt/odoo/addons,/home/odoo/custom-addons
```

---

### Step 5: Restart Odoo Service

```bash
# For systemd
sudo systemctl start odoo

# For supervisor
sudo supervisorctl start odoo

# Check if it's running
sudo systemctl status odoo
ps aux | grep odoo
```

**Wait 30-60 seconds for Odoo to fully start**

---

### Step 6: Activate Module in Odoo

#### Via Web Interface:

1. Login to Odoo with Administrator account
2. Go to: **Apps** (search bar in top left)
3. Click **Clear** filters (remove any filters)
4. Search for: **recruitment_uae**
5. Click the module name
6. Click **Install** button
7. Wait for installation to complete (usually 1-2 minutes)

#### Expected Output:

```
Module installation completed successfully
Installed modules: recruitment_uae (1.0.0)
```

#### Via Command Line (Advanced):

```bash
# Stop Odoo
sudo systemctl stop odoo

# Initialize module with -i flag
odoo -c /etc/odoo/odoo.conf -d your_database -i recruitment_uae --without-demo

# Restart Odoo
sudo systemctl start odoo
```

---

### Step 7: Verify Installation

#### Check Module Installed:

1. Go to: **Apps** → Search "recruitment_uae"
2. Should show as **Installed** with green checkmark
3. Click to view:
   - Version: 1.0.0
   - Category: Human Resources/Recruitment
   - Dependencies: recruitment, mail, hr, base

#### Check Menus Created:

In Odoo menu, you should see new sections:

```
Human Resources (or HR)
├── Recruitment
│   ├── Candidates
│   ├── Jobs
│   └── Applications
├── Retention Management (NEW!)
│   ├── Placements Retention
│   ├── Active Retentions
│   └── At-Risk Retentions
└── Follow-Up Management (NEW!)
    ├── All Follow-Ups
    ├── Scheduled Follow-Ups
    └── Overdue Follow-Ups
```

#### Check Database Tables Created:

```bash
# Login to PostgreSQL
sudo -u postgres psql -d your_database

# List tables containing 'retention' or 'followup'
\dt *retention*
\dt *followup*

# Should show:
# public | recruitment_retention
# public | recruitment_followup
# public | retention_forfeit_wizard
```

---

### Step 8: Create Test Records

#### Test Retention Record:

1. Go to: **HR → Retention Management → Placements Retention**
2. Click **Create**
3. Fill required fields:
   - Deployment: Select existing deployment
   - Total Placement Fee: 1,000 AED
   - Retention Period: 90 days
4. Click **Save**
5. Verify:
   - Sequence generated (RET/00001, RET/00002, etc.)
   - Computed fields populated (upfront/retention amounts)
   - No errors in logs

#### Test Follow-Up Record:

1. Go to: **HR → Follow-Up Management → All Follow-Ups**
2. Click **Create**
3. Fill required fields:
   - Deployment: Select existing deployment
   - Follow-Up Type: Week 1 - Initial Check
   - Scheduled Date: Today
4. Click **Save**
5. Verify:
   - Sequence generated (FUP/00001, FUP/00002, etc.)
   - No errors in logs

---

## ✅ POST-DEPLOYMENT VERIFICATION

### Checklist Items

- [ ] Module shows as "Installed" in Apps
- [ ] New menus visible in HR section
- [ ] Can create retention records without errors
- [ ] Can create follow-up records without errors
- [ ] Sequences generate properly (RET/00001, FUP/00001)
- [ ] Computed fields populate (amounts, dates, days)
- [ ] Form fields responsive on all zoom levels
- [ ] Alerts display correctly when applicable
- [ ] Status bars and buttons functional
- [ ] Chatter section working (messages, activities)
- [ ] No error messages in Odoo logs
- [ ] Database tables created correctly

### Check Odoo Logs

```bash
# Watch Odoo logs for errors
tail -f /var/log/odoo/odoo.log

# Search for module initialization
grep -i "recruitment_uae" /var/log/odoo/odoo.log

# Should see:
# [INFO] recruitment_uae: Module loaded successfully
```

### Test in Browser

```
Test URL: https://your-odoo-instance.com/web/

Steps:
1. Login with test user account
2. Go to: Apps → Search "recruitment_uae"
3. Verify module is installed
4. Navigate to: HR → Retention Management
5. Create new retention record
6. Test all buttons and fields
7. Test responsive design (zoom 75%, 100%, 125%)
```

---

## 🔄 POST-DEPLOYMENT SETUP

### Create User Roles/Permissions

```
If you want to restrict access to retention management:

1. Go to: Settings → Users & Companies → Users
2. Select user to configure
3. Go to: Human Resources (tab)
4. Check permissions needed:
   - [ ] HR Officer
   - [ ] HR Manager
   - [ ] Recruitment Officer
```

### Configure Cron Jobs

The module includes automatic background tasks. Verify they're enabled:

1. Go to: **Settings → Technical → Automation → Scheduled Actions**
2. Should see:
   - `recruitment.retention.cron_release_due_retentions`
   - `recruitment.followup.cron_schedule_automatic_followups`
   - `recruitment.followup.cron_mark_overdue_followups`
3. All should be **Active** (checked)
4. Cron frequency:
   - Release retentions: Daily at midnight
   - Schedule follow-ups: Daily at 1 AM
   - Mark overdue: Daily at 2 AM

---

## 🔧 TROUBLESHOOTING

### Issue: Module Not Appearing in Apps

**Possible Causes:**
1. Module files not copied correctly
2. Permissions incorrect
3. Odoo not restarted
4. Addons path not configured

**Solution:**
```bash
# 1. Verify files exist
ls -la /opt/odoo/addons/recruitment_uae/

# 2. Check permissions
sudo chown -R odoo:odoo /opt/odoo/addons/recruitment_uae
sudo chmod -R 755 /opt/odoo/addons/recruitment_uae

# 3. Check addons path in config
grep addons_path /etc/odoo/odoo.conf

# 4. Restart Odoo
sudo systemctl restart odoo

# 5. Update module list
# In Odoo: Apps → Hamburger menu (≡) → Update Apps List
```

---

### Issue: "RecordNotFound: Model recruitment.retention does not exist"

**Possible Causes:**
1. Module not fully installed
2. Database not updated
3. Models not loaded

**Solution:**
```bash
# 1. Check if installed
# In Odoo: Apps → Search "recruitment_uae" → should show Installed

# 2. Reinstall module
# In Odoo: Apps → recruitment_uae → Uninstall → Install

# 3. Check logs
tail -50 /var/log/odoo/odoo.log | grep -i "recruitment"

# 4. Restart Odoo
sudo systemctl restart odoo
```

---

### Issue: "ModuleNotFoundError: No module named 'recruitment'"

**Possible Causes:**
1. Base recruitment module not installed
2. Dependencies not installed

**Solution:**
```bash
# 1. Install recruitment module first
# In Odoo: Apps → Search "recruitment" → Install

# 2. Verify dependencies
# recruitment_uae depends on:
# - recruitment
# - mail
# - hr
# - base

# 3. Install all dependencies
# In Odoo: Apps → Install each one

# 4. Then install recruitment_uae
```

---

### Issue: Views Not Showing/XML Error

**Possible Causes:**
1. XML syntax error
2. Reference field doesn't exist
3. Model reference incorrect

**Solution:**
```bash
# 1. Check Odoo logs for XML errors
grep -i "xml" /var/log/odoo/odoo.log | tail -20

# 2. Validate XML syntax
python -m xml.dom.minidom /opt/odoo/addons/recruitment_uae/views/views_retention_followup.xml

# 3. Reinstall module
# In Odoo: Apps → recruitment_uae → Uninstall → Install

# 4. Clear browser cache
# Ctrl+Shift+Delete (Chrome) or Cmd+Shift+Delete (Mac)
```

---

### Issue: Computed Fields Not Calculating

**Possible Causes:**
1. Dependencies syntax error
2. Database transaction issue
3. Field not properly triggered

**Solution:**
```python
# In Odoo Console or via database:
# Force recalculate computed fields

# Method 1: In Odoo UI
# 1. Edit record
# 2. Click "Save"
# 3. Fields should recalculate

# Method 2: Via Python console
from odoo import api, SUPERUSER_ID
env = api.Environment(cr, SUPERUSER_ID, {})
retention = env['recruitment.retention'].search([], limit=1)
retention._compute_amounts()  # Force recalculate
```

---

### Issue: Cron Jobs Not Running

**Possible Causes:**
1. Cron service not enabled
2. Scheduled actions disabled
3. Database not configured

**Solution:**
```bash
# 1. Check if Odoo cron is enabled
grep "cron" /etc/odoo/odoo.conf

# Ensure this line exists and is enabled:
# max_cron_threads = 2

# 2. Restart Odoo
sudo systemctl restart odoo

# 3. Verify cron in Odoo:
# Settings → Technical → Automation → Scheduled Actions
# All should show "Cron Interval" = "Days" with "Interval" = 1

# 4. Check logs for cron execution
grep "cron" /var/log/odoo/odoo.log
```

---

## 📊 PERFORMANCE OPTIMIZATION

### Database Indexes

For high-volume instances, consider adding indexes:

```sql
-- Connect to database
sudo -u postgres psql -d your_database

-- Add indexes for common queries
CREATE INDEX idx_retention_state ON recruitment_retention(state);
CREATE INDEX idx_retention_release_date ON recruitment_retention(retention_release_date);
CREATE INDEX idx_followup_scheduled_date ON recruitment_followup(scheduled_date);
CREATE INDEX idx_followup_state ON recruitment_followup(state);
CREATE INDEX idx_followup_candidate ON recruitment_followup(candidate_id);
```

### Cache Warming

After installation, warm up caches:

```bash
# 1. Clear Python cache
find /opt/odoo -name "*.pyc" -delete
find /opt/odoo -name "__pycache__" -type d -exec rm -rf {} +

# 2. Restart Odoo
sudo systemctl restart odoo

# 3. Access main pages to warm cache
# Visit: /web → HR → Retention Management
# Visit: /web → HR → Follow-Up Management
```

---

## 🔐 SECURITY CONSIDERATIONS

### User Access Control

```
By default, users need:
- Access to HR module
- Permission to view recruitment records

To restrict access:

1. Create security groups
2. Set record rules (ir.rule)
3. Assign to specific users

Example:
- Group: "Recruitment Officer" - Can view/edit own retention records
- Group: "HR Manager" - Can view/edit all records
- Group: "Finance" - Can only view payment fields
```

### Data Privacy

```
Ensure compliance:
- GDPR: Personal data fields (name, email, phone)
- UAE Labor Laws: Visa and employment terms
- Company Policies: Salary and payment data

Recommendation:
- Restrict access to finance fields
- Archive old records after compliance period
- Set data retention policies
```

---

## 🎓 USER TRAINING

### For HR Officers/Recruiters

**Module: Retention Management**
- Creating retention records for new placements
- Tracking upfront and retention payments
- Monitoring candidate stability
- Understanding risk assessment

**Module: Follow-Up Management**
- Creating scheduled follow-ups
- Completing follow-up activities
- Recording issues and concerns
- Escalating to management when needed

### Training Resources

1. **Quick Start Guide** (2 pages)
   - How to create retention record
   - How to create follow-up record

2. **Video Tutorials** (suggested)
   - 5-minute: Creating retention records
   - 5-minute: Managing follow-ups
   - 5-minute: Viewing at-risk retentions

3. **User Handbook** (5-10 pages)
   - Complete feature documentation
   - Step-by-step procedures
   - Troubleshooting guide

---

## 📞 SUPPORT & MAINTENANCE

### Regular Maintenance Tasks

**Weekly:**
- [ ] Review at-risk retentions
- [ ] Check overdue follow-ups
- [ ] Monitor cron job logs

**Monthly:**
- [ ] Verify data integrity
- [ ] Check for orphaned records
- [ ] Review payment tracking

**Quarterly:**
- [ ] Database optimization
- [ ] Performance review
- [ ] Security audit

### Contact Information

For technical support:
- Email: support@sgtechai.com
- Documentation: [Module Documentation]
- Issue Tracker: [GitHub Issues]

---

## 🔄 ROLLBACK PROCEDURE

If you need to revert the deployment:

```bash
# 1. Stop Odoo
sudo systemctl stop odoo

# 2. Restore database backup
sudo -u postgres psql -d your_database < ~/odoo_backup_YYYYMMDD_HHMMSS.sql

# 3. Remove module directory
sudo rm -rf /opt/odoo/addons/recruitment_uae

# 4. Restore addons backup if needed
# sudo cp -r ~/odoo_addons_backup_YYYYMMDD_HHMMSS/* /opt/odoo/addons/

# 5. Restart Odoo
sudo systemctl start odoo

# 6. Verify system
# Test normal operations in Odoo
```

---

## ✅ FINAL CHECKLIST

- [ ] Database backed up
- [ ] Addons backed up
- [ ] Module files copied
- [ ] Permissions set correctly
- [ ] Odoo restarted successfully
- [ ] Module installed in Odoo
- [ ] Menus visible
- [ ] Test retention created successfully
- [ ] Test follow-up created successfully
- [ ] No errors in logs
- [ ] Responsive design verified
- [ ] Cron jobs enabled
- [ ] Users trained on new features
- [ ] Support procedures documented
- [ ] Rollback plan ready

---

**Deployment Status:** ✅ **READY FOR PRODUCTION**

**Support:** For any issues or questions, refer to the troubleshooting section or contact support.

---

*Last Updated: January 13, 2026*  
*Version: 1.0.0*  
*Module: recruitment_uae*
