# 📋 DEPLOYMENT EXECUTION CHECKLIST

**Project:** recruitment_uae v18.0.2.0.0 → eigermarvelhr.com
**Date:** _______________ | **Time Started:** _______________ | **Time Ended:** _______________
**Deployed By:** _______________ | **Reviewed By:** _______________

---

## PRE-DEPLOYMENT PHASE (Duration: ~15 minutes)

### Preparation & Notification

- [ ] Read 00_START_HERE.md
- [ ] Read DEPLOYMENT_READY_STATUS.md
- [ ] Review SAFE_DEPLOYMENT_PLAN.md sections 1-2
- [ ] Have CONTINGENCY_AND_ROLLBACK_PLAN.md open in browser
- [ ] Set maintenance window: From _______ to _______
- [ ] Notify users of temporary system unavailability
- [ ] Confirmed SSH access to eigermarvelhr.com
- [ ] Backup directory exists: `/var/lib/odoo/backups/` ✓

### System Verification

- [ ] Odoo service running: `systemctl status odoo` ✓
- [ ] Database responding: `psql -d eigermarvel -c "SELECT 1"` ✓
- [ ] Required 2+ requisitions present: `SELECT COUNT(*) FROM recruitment_job_requisition;` ✓
  - Count: ________
- [ ] Required 1+ applications present: `SELECT COUNT(*) FROM recruitment_application;` ✓
  - Count: ________
- [ ] Backup directory accessible and writable ✓
- [ ] Disk space adequate: `df /opt/odoo` ✓
- [ ] No active users in system (recommend off-hours) ✓

### Pre-Deployment Check Script

```bash
# SSH to server
ssh odoo@eigermarvelhr.com

# Run pre-deployment check as root
sudo bash /path/to/scripts/pre_deployment_check.sh
```

- [ ] Script execution started: ______ (time)
- [ ] Script completed without errors
- [ ] Output: "✅ SYSTEM IS READY FOR DEPLOYMENT"
- [ ] Checks Passed: _______ (should be 30+)
- [ ] Warnings: _______ (if any, document below)
- [ ] Checks Failed: _______ (should be 0)

**Warnings encountered (if any):**
_____________________________________________________________________________
_____________________________________________________________________________

**Decision:** Proceed with deployment? [ ] YES [ ] NO

If NO, address issues and re-run pre_deployment_check.sh

---

## FILE UPLOAD PHASE (Duration: ~5 minutes)

### Upload Module Files

- [ ] Copy all files to server:
  ```bash
  scp -r recruitment_uae_improvements/* odoo@eigermarvelhr.com:/tmp/recruitment_v18020/
  ```
- [ ] Verify files uploaded:
  ```bash
  ssh odoo@eigermarvelhr.com "ls -la /tmp/recruitment_v18020/"
  ```
- [ ] File count verified (should be 25+ files)
- [ ] Python files present (4 models)
- [ ] View files present (4 XML view files)
- [ ] Data files present (mail activity, templates, actions)
- [ ] Script files present (pre_deployment_check.sh, deploy.sh)

**Upload completion time:** ________

---

## DEPLOYMENT EXECUTION PHASE (Duration: ~30 minutes)

### Execute Deployment Script

```bash
# SSH to server
ssh odoo@eigermarvelhr.com

# Run deployment as root
sudo bash /tmp/recruitment_v18020/scripts/deploy.sh
```

- [ ] Deployment script started: _______ (time)
- [ ] Deployment log file created: _________________________ (note full path)
- [ ] Database backup completed ✓
- [ ] Backup file: _________________________ (note filename)
- [ ] Backup integrity test passed ✓
- [ ] Odoo service stopped ✓
- [ ] Module files verified ✓
- [ ] Module update command executed ✓
- [ ] Module update completed successfully ✓
- [ ] No syntax errors in deployment log
- [ ] No database errors in deployment log
- [ ] Odoo service started ✓
- [ ] Post-deployment validation passed ✓

**Deployment completion time:** ________

### Monitor Deployment Progress

- [ ] Watched for ERROR or TRACEBACK messages
- [ ] Noted any warnings (document below)
- [ ] Confirmed "DEPLOYMENT COMPLETED SUCCESSFULLY" message at end
- [ ] Deployment log accessible: `tail -100 /var/log/odoo/recruitment_deployment_*.log`

**Warnings encountered (if any):**
_____________________________________________________________________________
_____________________________________________________________________________

**Expected final message:**
```
✅ DEPLOYMENT COMPLETED SUCCESSFULLY
```

---

## IMMEDIATE VALIDATION PHASE (Duration: ~10 minutes)

### Server-Side Verification

```bash
# Verify module installed
sudo -u postgres psql -d eigermarvel -c \
  "SELECT name, state, latest_version FROM ir_module_module WHERE name='recruitment_uae';"
```

- [ ] Module name: recruitment_uae ✓
- [ ] Module state: installed ✓
- [ ] Module version: 18.0.2.0.0 ✓

```bash
# Check for errors in Odoo logs
grep ERROR /var/log/odoo/odoo.log | wc -l
```

- [ ] Error count: _________ (should be 0 or pre-existing)

```bash
# Verify requisitions preserved
sudo -u postgres psql -d eigermarvel -c \
  "SELECT COUNT(*) FROM recruitment_job_requisition;"
```

- [ ] Pre-deployment count: _________ (from earlier)
- [ ] Post-deployment count: _________ (should match or be greater)
- [ ] Data preserved: [ ] YES [ ] NO ⚠️ (If NO, ROLLBACK immediately)

```bash
# Verify applications preserved
sudo -u postgres psql -d eigermarvel -c \
  "SELECT COUNT(*) FROM recruitment_application;"
```

- [ ] Pre-deployment count: _________ (from earlier)
- [ ] Post-deployment count: _________ (should match)
- [ ] Data preserved: [ ] YES [ ] NO ⚠️ (If NO, ROLLBACK immediately)

### Web UI Verification

**Open https://eigermarvelhr.com and login as admin**

1. **Navigation Check**
   - [ ] Login successful
   - [ ] Home page loads
   - [ ] No error messages visible
   - [ ] Recruitment menu accessible

2. **Job Requisitions View**
   - [ ] Navigate to Recruitment > Job Requisitions
   - [ ] All 2+ requisitions visible in list
   - [ ] Requisition count matches database count
   - [ ] No 404 errors in console (F12 developer tools)

3. **Open First Requisition**
   - [ ] Form loads without errors
   - [ ] All fields visible
   - [ ] Chatter sidebar visible on right
   - [ ] Smart button "Applications" shows correct count
   - [ ] Smart button "Contracts" shows correct count
   - [ ] Smart button "Deployments" visible and shows count
   - [ ] No JavaScript errors in console

4. **Chatter Functionality**
   - [ ] Chatter shows existing messages (if any)
   - [ ] Can type new message in chatter
   - [ ] Activity section visible
   - [ ] No chatter-related errors

5. **Applications View**
   - [ ] Navigate to Recruitment > Applications
   - [ ] All 1+ applications visible
   - [ ] Application form opens without errors
   - [ ] Chatter visible
   - [ ] No errors in console

6. **Final UI Check**
   - [ ] No JavaScript console errors (F12 developer tools)
   - [ ] No red error banners on screen
   - [ ] All forms load quickly (< 3 seconds)
   - [ ] Responsive design working on mobile (if testing)

---

## EXTENDED VALIDATION PHASE (Duration: ~20 minutes)

### Functional Testing

- [ ] Create new activity type on requisition
  - [ ] Activity selected from list
  - [ ] Activity created successfully
  - [ ] Activity visible in timeline

- [ ] Test email template system
  - [ ] Email templates list accessible
  - [ ] New templates visible (count: __________)
  - [ ] Template names contain "(Enhanced)" suffix
  - [ ] No naming conflicts with existing templates

- [ ] Test chatter functionality
  - [ ] Post message to chatter
  - [ ] Message saved and visible
  - [ ] Thread preserved on refresh

### Database Verification

```bash
# Verify new templates created
sudo -u postgres psql -d eigermarvel -c \
  "SELECT COUNT(*) FROM mail_template WHERE name LIKE '%Recruitment%';"
```
- [ ] Template count: __________ (should be 5+)

```bash
# Verify new activity types created
sudo -u postgres psql -d eigermarvel -c \
  "SELECT COUNT(*) FROM mail_activity_type WHERE name LIKE '%Recruitment%';"
```
- [ ] Activity type count: __________ (should be 12)

```bash
# Verify new automated actions created
sudo -u postgres psql -d eigermarvel -c \
  "SELECT COUNT(*) FROM base_automation WHERE name LIKE '%Recruitment%';"
```
- [ ] Automated action count: __________ (should be 8)

### Performance Check

- [ ] Odoo service CPU usage: __________ % (normal: < 80%)
- [ ] Odoo service memory usage: __________ MB (normal: < 2000)
- [ ] Database response time: < 1 second
- [ ] Page load time: < 3 seconds

---

## MONITORING PHASE (Duration: Ongoing - 24 hours)

### Initial Monitoring (First Hour)

**Time:** __________ to __________

- [ ] Check Odoo service every 5 minutes (first 30 min)
  ```bash
  systemctl is-active odoo
  ```

- [ ] Monitor error logs (every 10 minutes)
  ```bash
  tail -20 /var/log/odoo/odoo.log
  ```

- [ ] Check database connectivity (every 30 minutes)
  ```bash
  sudo -u postgres psql -d eigermarvel -c "SELECT 1;"
  ```

**Issues encountered (if any):**
_____________________________________________________________________________
_____________________________________________________________________________

### Extended Monitoring (Next 24 hours)

- [ ] Set reminder to check logs at: __________ (next day)
- [ ] Set reminder to verify backup at: __________ (next day)
- [ ] Plan post-deployment review meeting: __________

**Monitoring Schedule:**
- [ ] Check logs: Every 2 hours for first 8 hours
- [ ] Check logs: Every 4 hours for next 16 hours
- [ ] Keep deployment log: /var/log/odoo/recruitment_deployment_*.log
- [ ] Keep monitoring log: /var/log/odoo/recruitment_monitor_*.log

---

## COMPLETION & SIGN-OFF

### Final Validation

- [ ] All 25 files deployed successfully
- [ ] Module version 18.0.2.0.0 confirmed
- [ ] All 2+ requisitions visible and intact
- [ ] All 1+ applications visible and intact
- [ ] Chatter working on at least one form
- [ ] Smart buttons displaying correct counts
- [ ] No unresolved errors in logs
- [ ] Backup file created and verified: ________________
- [ ] Monitoring plan established
- [ ] Team notified of completion

### Sign-Off

**Deployment Status:** [ ] SUCCESS ✅ [ ] PARTIAL ⚠️ [ ] FAILED ❌

**Issues Encountered:**
- [ ] None - deployment successful
- [ ] Minor warnings (non-blocking)
- [ ] Critical issues (see below)

**Critical Issues (if any):**
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

**Action Taken:**
_____________________________________________________________________________
_____________________________________________________________________________

**Final Notes:**
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

---

### Sign-Off Signatures

| Role | Name | Signature | Time |
|------|------|-----------|------|
| **Deployed By** | __________________ | __________________ | ______ |
| **Reviewed By** | __________________ | __________________ | ______ |
| **Approved By** | __________________ | __________________ | ______ |

---

## ROLLBACK DECISION MATRIX

**If ANY of the following occur, EXECUTE EMERGENCY ROLLBACK:**

- [ ] ❌ Data loss detected (requisitions missing)
- [ ] ❌ Application cannot start (service won't start)
- [ ] ❌ Database connection lost
- [ ] ❌ Critical errors in logs (more than 5 ERROR messages)
- [ ] ❌ Form rendering completely broken
- [ ] ❌ Multiple JavaScript console errors

**Emergency Rollback Instructions:**
See [CONTINGENCY_AND_ROLLBACK_PLAN.md](docs/CONTINGENCY_AND_ROLLBACK_PLAN.md) - Scenario 1

**Quick Rollback (< 15 minutes):**
```bash
# 1. Stop Odoo
systemctl stop odoo

# 2. Restore backup
sudo -u postgres dropdb eigermarvel
sudo -u postgres pg_restore --create \
  /var/lib/odoo/backups/eigermarvel_pre_v18020_*.dump

# 3. Restart Odoo
systemctl start odoo
```

---

## CRITICAL FILE LOCATIONS

**Deployment Log:** 
`/var/log/odoo/recruitment_deployment_YYYYMMDD_HHMMSS.log`

**Database Backup:** 
`/var/lib/odoo/backups/eigermarvel_pre_v18020_YYYYMMDD_HHMMSS.dump`

**Module Location:** 
`/opt/odoo/addons/recruitment_uae`

**Module Backup:** 
`/opt/odoo/addons/recruitment_uae.backup.YYYYMMDD_HHMMSS`

**Odoo Service Logs:** 
`/var/log/odoo/odoo.log`

---

## REFERENCE DOCUMENTS

- **Quick Start:** 00_START_HERE.md
- **Status Checklist:** DEPLOYMENT_READY_STATUS.md
- **Deployment Guide:** COMPLETE_PACKAGE_GUIDE.md
- **Detailed Procedure:** SAFE_DEPLOYMENT_PLAN.md
- **Emergency Procedures:** CONTINGENCY_AND_ROLLBACK_PLAN.md
- **Technical Details:** IMPLEMENTATION_SUMMARY.md

---

## COMPLETION TIME SUMMARY

| Phase | Start Time | End Time | Duration | Status |
|-------|-----------|----------|----------|--------|
| Pre-Deployment | __________ | __________ | ~15 min | ✅/⚠️/❌ |
| File Upload | __________ | __________ | ~5 min | ✅/⚠️/❌ |
| Deployment Execution | __________ | __________ | ~30 min | ✅/⚠️/❌ |
| Immediate Validation | __________ | __________ | ~10 min | ✅/⚠️/❌ |
| Extended Validation | __________ | __________ | ~20 min | ✅/⚠️/❌ |
| **TOTAL** | __________ | __________ | **~80 min** | **✅/⚠️/❌** |

---

**Checklist Completed:** ✅

**Date:** _______________ | **Time:** _______________

**Prepared By:** _______________ | **Signature:** _______________

---

**DEPLOYMENT COMPLETE - PROCEED TO POST-DEPLOYMENT MONITORING**

*Keep this checklist for audit trail and future reference.*

