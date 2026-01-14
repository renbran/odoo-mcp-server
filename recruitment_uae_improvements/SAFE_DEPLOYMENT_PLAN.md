# SAFE DEPLOYMENT PLAN - Based on Current Database Analysis

## 📊 Current Database State (eigermarvelhr.com)

### Module Information
- **Module:** recruitment_uae v18.0.1.1.0 (installed)
- **Database:** eigermarvel
- **Odoo Version:** 18.0

### Existing Infrastructure
✅ **Chatter Already Configured:**
- recruitment.application (has chatter)
- recruitment.contract (has chatter)
- Both already have message_ids and activity_ids fields

✅ **Smart Buttons Partially Exist:**
- recruitment.job.requisition (has smart buttons)
- recruitment.application (has smart buttons)
- recruitment.contract (has smart buttons)

✅ **Existing Data:**
- 2 job requisitions
- 1 application
- 0 contracts
- 0 deployments
- 0 retentions

✅ **Existing Email Templates:** 10 templates
- Application Rejection
- Application Submitted
- Application Withdrawn
- Candidate Selected
- Candidate Shortlisted
- Interview Scheduled
- Job Requisition Cancelled
- Job Requisition Completed
- Job Requisition Confirmed
- Recruitment Started

❌ **Missing:**
- No activity types configured
- No automated actions for recruitment
- Missing computed fields (contract_count, deployment_count)
- deployment.form view has no chatter
- job.requisition.form has no chatter

### Existing Fields (Job Requisition)
- activity_ids, message_ids ✅
- application_ids, application_count ✅
- deployment_ids (but no count field)
- No contract-related fields

---

## 🎯 Deployment Strategy

### Phase 1: Prepare Adjusted Implementation Files

**CRITICAL ADJUSTMENTS NEEDED:**

1. **Remove Redundant Chatter Inheritance**
   - Application and Contract already have chatter
   - Only add tracking=True to fields
   - Do NOT re-inherit mail.thread/mail.activity.mixin

2. **Add Missing Computed Fields Only**
   - Job Requisition: contract_count (NEW)
   - Application: Already has candidate fields
   - Contract: deployment_count (NEW)
   - Deployment: retention_count (NEW)

3. **Fix View Inheritance**
   - Use proper `inherit_id` references
   - Don't duplicate existing smart buttons
   - Add chatter only where missing (deployment, job requisition)

4. **Careful with Automated Actions**
   - Don't conflict with existing 10 email templates
   - Use different names for new templates

---

## 📝 Step-by-Step Deployment Plan

### ✅ STEP 1: Create Backup (CRITICAL)

```bash
# SSH to server
ssh admin@eigermarvelhr.com

# Create backup directory
BACKUP_DIR="/var/odoo/backups/recruitment_uae_upgrade_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump eigermarvel > $BACKUP_DIR/eigermarvel_backup.sql

# Backup module files
cp -r /var/odoo/eigermarvel/src/recruitment_uae $BACKUP_DIR/recruitment_uae_original

# Verify backup
ls -lh $BACKUP_DIR/
echo "Backup location: $BACKUP_DIR"
```

### ✅ STEP 2: Adjust Implementation Files Locally

**Files to Modify Before Upload:**

1. **models/recruitment_job_requisition.py**
   - ❌ Remove: `_inherit = ['recruitment.job.requisition', 'mail.thread', 'mail.activity.mixin']`
   - ✅ Keep: `_inherit = 'recruitment.job.requisition'`
   - ✅ Add: Contract count field and method

2. **models/recruitment_application.py**
   - ❌ Remove: `_inherit = ['recruitment.application', 'mail.thread', 'mail.activity.mixin']`
   - ✅ Keep: `_inherit = 'recruitment.application'`
   - Already has chatter, just add tracking

3. **models/recruitment_contract.py**
   - ❌ Remove: `_inherit = ['recruitment.contract', 'mail.thread', 'mail.activity.mixin']`
   - ✅ Keep: `_inherit = 'recruitment.contract'`
   - Already has chatter, just add tracking

4. **models/recruitment_deployment.py**
   - ✅ Check if already has chatter
   - If not, add mail.thread inheritance
   - Add tracking and new fields

5. **views/*.xml**
   - Fix inherit_id to use correct external IDs
   - Don't add chatter where it already exists
   - Add smart buttons carefully (check for duplicates)

6. **data/email_template_data.xml**
   - Rename templates to avoid conflicts with existing 10
   - Use prefix like "Recruitment Enhanced:"

### ✅ STEP 3: Test Files Locally (Optional but Recommended)

If you have local Odoo 18:
```bash
# Install module locally
odoo-bin -c odoo.conf -d test_db -u recruitment_uae
```

### ✅ STEP 4: Upload Adjusted Files to Server

```bash
# From Windows, use WinSCP or scp:
scp models/* admin@eigermarvelhr.com:/tmp/recruitment_improvements/models/
scp views/* admin@eigermarvelhr.com:/tmp/recruitment_improvements/views/
scp data/* admin@eigermarvelhr.com:/tmp/recruitment_improvements/data/
scp security/* admin@eigermarvelhr.com:/tmp/recruitment_improvements/security/
```

### ✅ STEP 5: Apply Files on Server

```bash
# SSH to server
ssh admin@eigermarvelhr.com

# Copy files to module directory
cp /tmp/recruitment_improvements/models/* /var/odoo/eigermarvel/src/recruitment_uae/models/
cp /tmp/recruitment_improvements/views/* /var/odoo/eigermarvel/src/recruitment_uae/views/
cp /tmp/recruitment_improvements/data/* /var/odoo/eigermarvel/src/recruitment_uae/data/
cp /tmp/recruitment_improvements/security/* /var/odoo/eigermarvel/src/recruitment_uae/security/

# Set proper ownership
chown -R odoo:odoo /var/odoo/eigermarvel/src/recruitment_uae/
```

### ✅ STEP 6: Update __manifest__.py

```bash
# Edit manifest
nano /var/odoo/eigermarvel/src/recruitment_uae/__manifest__.py

# Update version
'version': '18.0.2.0.0',

# Add new data files
'data': [
    # ... existing files ...
    'data/mail_activity_data.xml',
    'data/email_template_data.xml',
    'data/automated_action_data.xml',
    'views/recruitment_job_requisition_views.xml',
    'views/recruitment_application_views.xml',
    'views/recruitment_contract_views.xml',
    'views/recruitment_deployment_views.xml',
],
```

### ✅ STEP 7: Update Module (DRY RUN FIRST)

```bash
# Stop Odoo
sudo systemctl stop odoo18

# Dry run with --test-enable (doesn't commit)
/var/odoo/venv/bin/python3 /var/odoo/odoo18/odoo-bin \
  -c /etc/odoo18.conf \
  -d eigermarvel \
  -u recruitment_uae \
  --test-enable \
  --stop-after-init \
  --log-level=debug

# Check logs for errors
tail -n 100 /var/log/odoo/odoo18.log

# If OK, run actual update (commits changes)
/var/odoo/venv/bin/python3 /var/odoo/odoo18/odoo-bin \
  -c /etc/odoo18.conf \
  -d eigermarvel \
  -u recruitment_uae \
  --stop-after-init

# Start Odoo
sudo systemctl start odoo18
sudo systemctl status odoo18
```

### ✅ STEP 8: Verification Tests

**Login to https://eigermarvelhr.com**

1. **Test Job Requisition:**
   - Open one of the 2 existing requisitions
   - Check: Smart buttons visible (Applications, Contracts, Deployments)
   - Check: Chatter at bottom
   - Check: Activities panel
   - Create test: Add comment in chatter
   - Create test: Schedule activity

2. **Test Application:**
   - Open the 1 existing application
   - Check: Contract smart button
   - Check: Chatter working
   - Test: Try "Create Contract" button

3. **Test Activity Types:**
   - Settings > Technical > Automation > Activity Types
   - Search for "recruitment"
   - Should see 12 new activity types

4. **Test Email Templates:**
   - Settings > Technical > Email > Email Templates
   - Search for "recruitment"
   - Should see original 10 + new 5 = 15 templates

5. **Test Automated Actions:**
   - Settings > Technical > Automation > Automated Actions
   - Search for "recruitment"
   - Should see 8 new actions

### ✅ STEP 9: Test Workflows

1. **Create New Job Requisition:**
   - Recruitment > Job Requisitions > Create
   - Fill form
   - Submit
   - Approve
   - Check if activity scheduled
   - Check if email sent (if configured)

2. **Test Auto-Create Application:**
   - On approved requisition
   - Click "Create Applications" button
   - Verify applications created

3. **Test Application → Contract:**
   - Open application
   - Change state to "Accepted"
   - Check if contract auto-created
   - Verify chatter notification

4. **Test Contract → Deployment:**
   - Create/edit contract
   - Change state to "Signed"
   - Check if deployment auto-created

### ✅ STEP 10: Monitor for 24 Hours

```bash
# Watch logs in real-time
tail -f /var/log/odoo/odoo18.log | grep -i recruitment

# Check for errors
grep -i error /var/log/odoo/odoo18.log | grep -i recruitment

# Monitor database queries
psql eigermarvel -c "SELECT * FROM pg_stat_activity WHERE query LIKE '%recruitment%';"
```

---

## 🚨 Rollback Procedure (If Problems Occur)

```bash
# Stop Odoo
sudo systemctl stop odoo18

# Restore database
sudo -u postgres psql eigermarvel < $BACKUP_DIR/eigermarvel_backup.sql

# Restore module files
rm -rf /var/odoo/eigermarvel/src/recruitment_uae
cp -r $BACKUP_DIR/recruitment_uae_original /var/odoo/eigermarvel/src/recruitment_uae

# Start Odoo
sudo systemctl start odoo18
```

---

## 📋 Pre-Deployment Checklist

- [ ] Database backup created
- [ ] Module files backed up
- [ ] Filestore backed up (if needed)
- [ ] Files adjusted for existing infrastructure
- [ ] __manifest__.py updated
- [ ] Dry run completed successfully
- [ ] Team notified
- [ ] Maintenance window scheduled
- [ ] Rollback procedure tested

---

## ⚠️ Critical Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Duplicate chatter | Medium | High | Check existing views, use proper inheritance |
| Field conflicts | Low | High | Use computed fields, don't override existing |
| Data loss | Very Low | Critical | Complete backup before any change |
| View inheritance errors | Medium | Medium | Use correct external IDs |
| Email template conflicts | Medium | Low | Rename new templates with prefix |
| Performance degradation | Low | Medium | Test with existing 2 requisitions first |

---

## 📊 Success Criteria

- ✅ All 2 existing requisitions still accessible
- ✅ All 1 existing application still works
- ✅ New smart buttons visible
- ✅ Chatter working on all models
- ✅ 12 activity types installed
- ✅ 5 new email templates (15 total)
- ✅ 8 automated actions active
- ✅ No errors in logs
- ✅ Workflows function correctly
- ✅ Existing data unchanged

---

##Next Steps

Would you like me to:
1. **Adjust the implementation files now** based on this analysis?
2. **Proceed with SSH deployment** to the server?
3. **Create test scripts** for verification?

The current implementation files need adjustments to avoid conflicts with the existing infrastructure!
