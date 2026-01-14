# Recruitment UAE Module - Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the improved recruitment_uae module to your Odoo 18 production server (eigermarvelhr.com).

---

## 📋 Pre-Deployment Checklist

### 1. Backup Requirements
- [ ] Full database backup
- [ ] Filestore backup
- [ ] Module files backup
- [ ] Configuration backup

### 2. Environment Check
- [ ] Odoo version: 18.0
- [ ] Python version: 3.10+
- [ ] Database: PostgreSQL 14+
- [ ] Disk space: >2GB free
- [ ] User permissions: admin access

### 3. Dependencies Verification
- [ ] `mail` module installed
- [ ] `hr` module installed
- [ ] `base_automation` module installed
- [ ] `recruitment_uae` module installed (v18.0.1.1.0)

---

## 🚀 Deployment Steps

### Phase 1: Backup (CRITICAL)

```bash
# Connect to server
ssh admin@eigermarvelhr.com

# Navigate to Odoo directory
cd /var/odoo

# Create backup directory
mkdir -p backups/recruitment_uae_upgrade_$(date +%Y%m%d)

# Backup database
pg_dump eigermarvel > backups/recruitment_uae_upgrade_$(date +%Y%m%d)/eigermarvel_backup.sql

# Backup current module files
cp -r eigermarvel/src/recruitment_uae backups/recruitment_uae_upgrade_$(date +%Y%m%d)/recruitment_uae_original

# Backup filestore
tar -czf backups/recruitment_uae_upgrade_$(date +%Y%m%d)/filestore_backup.tar.gz eigermarvel/data/filestore
```

### Phase 2: File Transfer

```bash
# From your local machine (Windows)
# Option 1: Using SCP
scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\recruitment_uae_improvements\models\* admin@eigermarvelhr.com:/var/odoo/eigermarvel/src/recruitment_uae/models/

scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\recruitment_uae_improvements\views\* admin@eigermarvelhr.com:/var/odoo/eigermarvel/src/recruitment_uae/views/

scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\recruitment_uae_improvements\data\* admin@eigermarvelhr.com:/var/odoo/eigermarvel/src/recruitment_uae/data/

scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\recruitment_uae_improvements\security\* admin@eigermarvelhr.com:/var/odoo/eigermarvel/src/recruitment_uae/security/

# Option 2: Using WinSCP (GUI method)
# 1. Open WinSCP
# 2. Connect to eigermarvelhr.com
# 3. Navigate to /var/odoo/eigermarvel/src/recruitment_uae/
# 4. Upload files from local directory
```

### Phase 3: Update __manifest__.py

```bash
# On the server, edit the manifest file
nano /var/odoo/eigermarvel/src/recruitment_uae/__manifest__.py

# Add the new data files to the 'data' section:
'data': [
    # ... existing files ...
    
    # New improvement files
    'data/mail_activity_data.xml',
    'data/email_template_data.xml',
    'data/automated_action_data.xml',
    'views/recruitment_job_requisition_views.xml',
    'views/recruitment_application_views.xml',
    'views/recruitment_contract_views.xml',
    'views/recruitment_deployment_views.xml',
],

# Update version from 18.0.1.1.0 to 18.0.2.0.0
'version': '18.0.2.0.0',
```

### Phase 4: Update Module

```bash
# Stop Odoo service
sudo systemctl stop odoo18

# Update module with Odoo shell
/var/odoo/venv/bin/python3 /var/odoo/odoo18/odoo-bin \
  -c /etc/odoo18.conf \
  -d eigermarvel \
  -u recruitment_uae \
  --stop-after-init

# Check for errors in log
tail -n 100 /var/log/odoo/odoo18.log

# Start Odoo service
sudo systemctl start odoo18

# Verify service is running
sudo systemctl status odoo18
```

### Phase 5: Verification & Testing

#### 5.1 Database Verification
```bash
# Connect to PostgreSQL
sudo -u postgres psql eigermarvel

# Check if new fields exist
\d recruitment_job_requisition
\d recruitment_application
\d recruitment_contract
\d recruitment_deployment

# Check activity types
SELECT name, res_model FROM mail_activity_type WHERE res_model LIKE 'recruitment%';

# Check email templates
SELECT name, model FROM mail_template WHERE model LIKE 'recruitment%';

# Exit PostgreSQL
\q
```

#### 5.2 UI Verification
1. **Login to Odoo:**
   - URL: https://eigermarvelhr.com
   - User: admin
   - Password: 8586583

2. **Check Job Requisition:**
   - Navigate to Recruitment > Job Requisitions
   - Open any requisition
   - Verify smart buttons appear (Applications, Contracts, Deployments)
   - Check chatter is at the bottom
   - Verify activities panel exists
   - Test "Create Applications" button (if approved)

3. **Check Application:**
   - Navigate to Recruitment > Applications
   - Open any application
   - Verify Contract smart button
   - Check chatter integration
   - Test "Create Contract" button (if accepted)

4. **Check Contract:**
   - Navigate to Recruitment > Contracts
   - Open any contract
   - Verify Deployment smart button
   - Check chatter and activities
   - Test "Create Deployment" button (if signed)

5. **Check Deployment:**
   - Navigate to Recruitment > Deployments
   - Open any deployment
   - Verify Retentions smart button
   - Check chatter
   - Test "Confirm Arrival" button

#### 5.3 Automation Testing
```bash
# Test automated emails via Odoo shell
/var/odoo/venv/bin/python3 /var/odoo/odoo18/odoo-bin shell \
  -c /etc/odoo18.conf \
  -d eigermarvel

# In the Odoo shell:
>>> requisition = env['recruitment.job.requisition'].browse(1)
>>> requisition.action_approve()
>>> env.cr.commit()
>>> exit()

# Check mail queue
sudo -u postgres psql eigermarvel -c "SELECT * FROM mail_mail WHERE state = 'outgoing' LIMIT 5;"
```

---

## 🔧 Troubleshooting

### Issue 1: Module Update Fails
**Symptoms:** Error during module update

**Solution:**
```bash
# Check logs
tail -f /var/log/odoo/odoo18.log

# Common errors:
# - Syntax error: Check Python file syntax
# - XML parsing error: Validate XML files
# - Missing dependency: Install required module

# Rollback if needed (see Rollback section)
```

### Issue 2: Smart Buttons Not Appearing
**Symptoms:** No smart buttons visible on forms

**Solution:**
```bash
# Clear browser cache
# Refresh page with Ctrl+F5

# Check if views are properly inherited
# Navigate to Settings > Technical > User Interface > Views
# Search for "recruitment" and verify new views exist
```

### Issue 3: Chatter Not Working
**Symptoms:** Chatter section missing or not functional

**Solution:**
```bash
# Verify models inherit mail.thread
# Check if message_ids field exists:
sudo -u postgres psql eigermarvel -c "SELECT column_name FROM information_schema.columns WHERE table_name='recruitment_job_requisition' AND column_name='message_ids';"

# Update module again if missing
```

### Issue 4: Activities Not Creating
**Symptoms:** No activities scheduled automatically

**Solution:**
```bash
# Verify activity types exist
sudo -u postgres psql eigermarvel -c "SELECT name FROM mail_activity_type WHERE res_model='recruitment.job.requisition';"

# Re-import data files if missing
/var/odoo/venv/bin/python3 /var/odoo/odoo18/odoo-bin \
  -c /etc/odoo18.conf \
  -d eigermarvel \
  -i recruitment_uae \
  --stop-after-init
```

---

## ⏮️ Rollback Procedure

If deployment fails or causes issues:

```bash
# Stop Odoo
sudo systemctl stop odoo18

# Restore database
sudo -u postgres psql eigermarvel < backups/recruitment_uae_upgrade_YYYYMMDD/eigermarvel_backup.sql

# Restore module files
rm -rf /var/odoo/eigermarvel/src/recruitment_uae
cp -r backups/recruitment_uae_upgrade_YYYYMMDD/recruitment_uae_original /var/odoo/eigermarvel/src/recruitment_uae

# Restore filestore
cd /var/odoo/eigermarvel/data
rm -rf filestore
tar -xzf ~/backups/recruitment_uae_upgrade_YYYYMMDD/filestore_backup.tar.gz

# Start Odoo
sudo systemctl start odoo18

# Verify rollback
sudo systemctl status odoo18
```

---

## 📊 Post-Deployment Monitoring

### Week 1: Monitor Usage
- [ ] Check error logs daily: `tail -f /var/log/odoo/odoo18.log`
- [ ] Monitor database performance: `SELECT * FROM pg_stat_activity;`
- [ ] Verify email queue: Check Settings > Technical > Email > Emails
- [ ] User feedback collection

### Week 2-4: Optimize
- [ ] Review activity completion rates
- [ ] Check automated action performance
- [ ] Monitor chatter usage
- [ ] Gather user feedback

### Month 1+: Analyze
- [ ] Generate workflow efficiency reports
- [ ] Measure time savings from automation
- [ ] Identify areas for further improvement
- [ ] Plan next enhancements

---

## 📞 Support & Contact

**For Technical Issues:**
- Developer: Eiger Marvel HR Development Team
- Email: it@eigermarvelhr.com
- Server: eigermarvelhr.com

**For Module Questions:**
- Refer to: RECRUITMENT_UAE_IMPROVEMENTS.md
- Check logs: /var/log/odoo/odoo18.log
- Odoo Documentation: https://www.odoo.com/documentation/18.0/

---

## ✅ Deployment Checklist Summary

- [ ] Pre-deployment backup completed
- [ ] Files transferred to server
- [ ] __manifest__.py updated
- [ ] Module updated successfully
- [ ] Database verification passed
- [ ] UI verification passed
- [ ] Automation testing passed
- [ ] No errors in logs
- [ ] User acceptance testing completed
- [ ] Documentation updated
- [ ] Team notified of changes

---

## 📝 Deployment Record

**Deployment Date:** _________________

**Deployed By:** _________________

**Odoo Version:** 18.0

**Module Version:** 18.0.2.0.0

**Database:** eigermarvel

**Backup Location:** /var/odoo/backups/recruitment_uae_upgrade_YYYYMMDD/

**Status:** ☐ Success ☐ Partial ☐ Rollback Required

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________

---

**END OF DEPLOYMENT GUIDE**
