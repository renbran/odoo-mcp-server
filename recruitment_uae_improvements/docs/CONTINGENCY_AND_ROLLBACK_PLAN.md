# Recruitment UAE Module v18.0.2.0.0 - Contingency & Rollback Plan

**Created:** 2024
**Target System:** eigermarvelhr.com (Odoo 18.0, Database: eigermarvel)
**Critical Data Protected:** 2 Job Requisitions, 1 Application, All Chatter Messages
**Module Version:** recruitment_uae v18.0.2.0.0

---

## 📋 Table of Contents

1. [Risk Assessment](#risk-assessment)
2. [Pre-Deployment Verification](#pre-deployment-verification)
3. [Deployment Strategy](#deployment-strategy)
4. [Rollback Procedures](#rollback-procedures)
5. [Data Recovery Procedures](#data-recovery-procedures)
6. [Monitoring & Validation](#monitoring--validation)
7. [Emergency Contacts](#emergency-contacts)

---

## 🎯 Risk Assessment

### Critical Dependencies
- **Module:** recruitment_uae (v18.0.1.1.0 → v18.0.2.0.0)
- **Database:** eigermarvel (PostgreSQL)
- **Active Records:** 2 requisitions, 1 application
- **Chatter Status:** Messages on application (YES), contract (YES), deployment (NO), requisition (NO)
- **Custom Fields:** application_count on requisition (EXISTS), contract_count (NEW), deployment_count (NEW)

### Identified Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| View inheritance ID mismatch | HIGH | Verify external IDs before deployment |
| Email template name conflicts | MEDIUM | Renamed with "_enhanced" suffix |
| Duplicate mail.thread inheritance | HIGH | ✅ FIXED - Removed from models |
| Missing computed fields | MEDIUM | Added contract_count, deployment_count |
| Smart button conflicts | MEDIUM | Used unique field names, checked existing structure |
| Chatter widget placement | LOW | Views designed for form replacement not inheritance |
| Database connection loss during update | CRITICAL | Full backup taken before deployment |

### Conflict Resolution Status

| Conflict | Status | Solution |
|----------|--------|----------|
| Duplicate mail.thread in models | ✅ FIXED | Removed from all 4 models - using simple string inheritance |
| View external ID references | ✅ VERIFIED | Updated to use "_inherit" variants |
| Email template name conflicts | ✅ FIXED | Added "(Enhanced)" suffix to all 5 new templates |
| Automated action template references | ✅ FIXED | Updated to reference new template names |
| Computed fields for counts | ✅ ADDED | Added contract_count, deployment_count to requisition |
| Activity types configuration | ✅ READY | 12 new types with unique codes ready to install |
| Automated actions setup | ✅ READY | 8 automated actions configured and ready |

---

## ✅ Pre-Deployment Verification

### 1. Backup Verification (MANDATORY)

**Execute on remote server (eigermarvelhr.com):**

```bash
# SSH to server
ssh odoo@eigermarvelhr.com

# Navigate to backup directory
cd /var/lib/odoo/backups

# Create dated backup of current database
sudo -u postgres pg_dump -Fc eigermarvel > eigermarvel_pre_v18020_$(date +%Y%m%d_%H%M%S).dump

# Verify backup was created
ls -lh eigermarvel_pre_v18020_*.dump

# Test backup integrity (CRITICAL)
sudo -u postgres pg_restore --test -Fc eigermarvel_pre_v18020_*.dump

# Output should show "** Restore started" with no ERRORS
```

### 2. Current State Snapshot

**Execute on remote server:**

```bash
# Save current module metadata
cd /opt/odoo/addons/recruitment_uae
cp __manifest__.py __manifest__.py.backup
git status > /tmp/module_status_before.txt
git log --oneline -5 > /tmp/module_git_before.txt

# Capture current data state
cd ~
cat > /tmp/capture_state.py << 'EOF'
import json
import subprocess
from datetime import datetime

# Get current requisitions count
result = subprocess.run([
    'odoo-bin', 'shell', '--database=eigermarvel', 
    '-c', '/etc/odoo/odoo.conf',
    '--no-http'
], input='''
import json
requisitions = env['recruitment.job.requisition'].search([])
applications = env['recruitment.application'].search([])
contracts = env['recruitment.contract'].search([])
print(f"Requisitions: {len(requisitions)}")
print(f"Applications: {len(applications)}")
print(f"Contracts: {len(contracts)}")
''', capture_output=True, text=True)

with open('/tmp/pre_deployment_state.txt', 'w') as f:
    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    f.write(result.stdout)
EOF

python /tmp/capture_state.py
```

### 3. Module Dependencies Check

**Execute on remote server:**

```bash
# Check for conflicting modules
cd /opt/odoo/addons
ls -d recruitment* | grep -v recruitment_uae

# Check mail module dependencies
grep -r "mail.thread\|mail.activity.mixin" recruitment_uae/models/ | grep -v "def \|#"

# Verify no duplicate definitions
grep -c "class.*mail.thread" recruitment_uae/models/recruitment_*.py
# Expected: 0 (all should be removed)
```

### 4. Database Health Check

**Execute on remote server:**

```bash
# Connect to PostgreSQL
sudo -u postgres psql eigermarvel

-- Check for orphaned records
SELECT COUNT(*) FROM recruitment_job_requisition WHERE name IS NULL;
SELECT COUNT(*) FROM recruitment_application WHERE name IS NULL;
SELECT COUNT(*) FROM recruitment_contract WHERE name IS NULL;

-- Verify message_ids integrity
SELECT COUNT(*) FROM recruitment_application WHERE message_ids IS NOT NULL;
SELECT COUNT(*) FROM recruitment_contract WHERE message_ids IS NOT NULL;

-- Check for missing application_count field
SELECT column_name FROM information_schema.columns 
WHERE table_name='recruitment_job_requisition' AND column_name='application_count';

-- Exit psql
\q
```

---

## 🚀 Deployment Strategy

### Phase 1: Pre-Deployment (15 minutes)

1. **Notify Users**
   ```bash
   # Create maintenance message
   systemctl stop odoo
   # Or create banner
   echo "Maintenance in progress. Recruitment module updating. ETA: 20 minutes" > /var/www/html/maintenance.html
   ```

2. **Verify No Active Users**
   ```bash
   # Check active sessions
   sudo -u postgres psql eigermarvel -c "SELECT pid, usename, state FROM pg_stat_activity WHERE datname='eigermarvel';"
   ```

3. **Create Pre-Deployment Snapshot**
   ```bash
   # Backup database
   sudo -u postgres pg_dump -Fc eigermarvel > /var/lib/odoo/backups/eigermarvel_pre_v18020_$(date +%s).dump
   
   # Verify backup
   sudo -u postgres pg_restore --test -Fc /var/lib/odoo/backups/eigermarvel_pre_v18020_*.dump
   ```

### Phase 2: File Upload (5 minutes)

1. **Upload Module Files**
   ```bash
   # Copy to temporary location
   scp -r recruitment_uae_improvements/* odoo@eigermarvelhr.com:/tmp/recruitment_uae_v18020/
   
   # On server
   cd /tmp/recruitment_uae_v18020
   ls -la
   ```

2. **Verify File Integrity**
   ```bash
   # Check no corrupted files
   find . -type f -name "*.py" -exec python -m py_compile {} \;
   find . -type f -name "*.xml" -exec python -m xml.etree.ElementTree {} \;
   ```

### Phase 3: Module Update (10 minutes)

1. **Execute Update with Logging**
   ```bash
   cd /opt/odoo
   
   # Create detailed log file
   touch /var/log/odoo/recruitment_update_$(date +%Y%m%d_%H%M%S).log
   
   # Run module update
   python odoo-bin -u recruitment_uae \
     --database=eigermarvel \
     -c /etc/odoo/odoo.conf \
     --stop-after-init \
     --log-level=debug \
     2>&1 | tee /var/log/odoo/recruitment_update.log
   
   # Monitor for errors
   grep -i "error\|traceback\|exception" /var/log/odoo/recruitment_update.log
   ```

2. **Verify Module Installation**
   ```bash
   # Check module state
   sudo -u postgres psql eigermarvel -c \
     "SELECT name, state, latest_version FROM ir_module_module WHERE name='recruitment_uae';"
   
   # Expected: recruitment_uae | installed | 18.0.2.0.0
   ```

### Phase 4: Validation (10 minutes)

1. **Database Integrity Check**
   ```bash
   sudo -u postgres psql eigermarvel << 'EOF'
   -- Check new fields exist
   SELECT column_name FROM information_schema.columns 
   WHERE table_name IN ('recruitment_job_requisition', 'recruitment_application', 'recruitment_contract', 'recruitment_deployment')
   ORDER BY table_name, ordinal_position;
   
   -- Verify record counts unchanged
   SELECT COUNT(*) as requisitions FROM recruitment_job_requisition;
   SELECT COUNT(*) as applications FROM recruitment_application;
   SELECT COUNT(*) as contracts FROM recruitment_contract;
   
   -- Check mail activity integration
   SELECT COUNT(*) FROM mail_activity WHERE res_model='recruitment.job.requisition';
   SELECT COUNT(*) FROM mail_activity WHERE res_model='recruitment.application';
   EOF
   ```

2. **Start Odoo Service**
   ```bash
   systemctl start odoo
   
   # Wait for service to fully start
   sleep 10
   
   # Check service status
   systemctl status odoo
   
   # Monitor logs
   tail -f /var/log/odoo/odoo.log | grep -i "recruitment\|error"
   ```

3. **Web UI Verification**
   ```
   # Open browser to https://eigermarvelhr.com
   # Login with admin user
   # Navigate to Recruitment > Job Requisitions
   # Verify:
   # ✅ All 2 existing requisitions visible
   # ✅ Smart buttons working (applications, contracts, deployments)
   # ✅ Chatter sidebar visible
   # ✅ Activity tracking working
   # ✅ No error messages in console
   ```

---

## 🔄 Rollback Procedures

### Scenario 1: Module Update Failed (Error During Installation)

**Immediate Action (< 5 minutes):**

```bash
# Stop Odoo service
systemctl stop odoo

# Remove newly updated module files
rm -rf /opt/odoo/addons/recruitment_uae/models/recruitment_contract.py
rm -rf /opt/odoo/addons/recruitment_uae/models/recruitment_deployment.py
rm -rf /opt/odoo/addons/recruitment_uae/__manifest__.py
# ... restore from backup

# Restore from git if available
cd /opt/odoo/addons/recruitment_uae
git checkout HEAD -- .

# Start Odoo
systemctl start odoo
```

**Detailed Rollback (< 15 minutes):**

1. **Stop Application & Database**
   ```bash
   systemctl stop odoo
   sleep 5
   ```

2. **Drop Corrupted Database**
   ```bash
   sudo -u postgres dropdb --if-exists eigermarvel
   ```

3. **Restore from Backup**
   ```bash
   # List available backups
   ls -lh /var/lib/odoo/backups/eigermarvel_pre_v18020_*.dump
   
   # Restore latest backup
   sudo -u postgres pg_restore \
     --create \
     --verbose \
     /var/lib/odoo/backups/eigermarvel_pre_v18020_*.dump
   
   # Verify restoration (wait for completion - may take 5-10 minutes)
   sudo -u postgres psql eigermarvel -c "SELECT COUNT(*) FROM recruitment_job_requisition;"
   ```

4. **Restore Module Code**
   ```bash
   cd /opt/odoo/addons
   
   # Either restore from git
   cd recruitment_uae
   git checkout HEAD~1 -- .
   
   # Or restore from backup
   rm -rf recruitment_uae
   cp -r /var/backups/recruitment_uae.backup ./recruitment_uae
   ```

5. **Restart Odoo**
   ```bash
   systemctl start odoo
   sleep 10
   systemctl status odoo
   tail -100 /var/log/odoo/odoo.log
   ```

### Scenario 2: Data Corruption Detected (After Successful Update)

**If you notice data issues like missing requisitions or application records:**

```bash
# Stop Odoo
systemctl stop odoo

# Prepare rollback script
cat > /tmp/rollback.sql << 'EOF'
-- Drop new tables if they caused issues
DROP TABLE IF EXISTS recruitment_deployment CASCADE;

-- Reset auto-increment sequences if needed
SELECT setval('recruitment_job_requisition_id_seq', 
  (SELECT MAX(id) FROM recruitment_job_requisition) + 1);

-- Verify critical records still exist
SELECT COUNT(*) FROM recruitment_job_requisition;
SELECT COUNT(*) FROM recruitment_application;
EOF

# Execute rollback
sudo -u postgres psql eigermarvel < /tmp/rollback.sql

# Restore from backup if needed (see Scenario 1, Step 3)
```

### Scenario 3: View/UI Broken After Update

**If forms/views don't display correctly:**

```bash
# Check for view errors
sudo -u postgres psql eigermarvel -c \
  "SELECT * FROM ir_ui_view WHERE name LIKE '%recruitment%' AND arch_db IS NULL LIMIT 10;"

# Clear view cache
cat > /tmp/clear_views.py << 'EOF'
env['ir.ui.view'].clear_caches()
env['ir.model.data'].flush()
EOF

# Execute via odoo shell
python odoo-bin shell --database=eigermarvel -c /etc/odoo/odoo.conf < /tmp/clear_views.py

# Restart Odoo
systemctl restart odoo
```

### Scenario 4: Email Template Conflicts

**If duplicate email templates appear:**

```bash
# Check for duplicates
sudo -u postgres psql eigermarvel -c \
  "SELECT name, COUNT(*) FROM mail_template WHERE name LIKE '%Requisition%' GROUP BY name HAVING COUNT(*) > 1;"

# Delete duplicates (keep oldest)
cat > /tmp/fix_templates.sql << 'EOF'
DELETE FROM mail_template 
WHERE id NOT IN (
  SELECT MIN(id) FROM mail_template 
  GROUP BY name
) AND name LIKE '%Recruitment%';
EOF

sudo -u postgres psql eigermarvel < /tmp/fix_templates.sql
```

---

## 📊 Data Recovery Procedures

### Full Database Restore from Backup

**Use when all else fails (Complete data recovery):**

```bash
#!/bin/bash
# Full Recovery Script

set -e  # Exit on error

BACKUP_FILE="/var/lib/odoo/backups/eigermarvel_pre_v18020_*.dump"
BACKUP_LATEST=$(ls -t $BACKUP_FILE | head -1)

echo "Starting recovery from: $BACKUP_LATEST"

# 1. Stop application
echo "Stopping Odoo..."
systemctl stop odoo
sleep 5

# 2. Kill existing connections
echo "Terminating database connections..."
sudo -u postgres psql -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='eigermarvel';"
sleep 2

# 3. Drop corrupted database
echo "Dropping corrupted database..."
sudo -u postgres dropdb --if-exists eigermarvel

# 4. Restore from backup
echo "Restoring from backup... (this may take 5-10 minutes)"
sudo -u postgres pg_restore \
  --create \
  --no-owner \
  --verbose \
  "$BACKUP_LATEST" 2>&1 | tail -20

# 5. Verify restore
echo "Verifying restoration..."
RECORD_COUNT=$(sudo -u postgres psql eigermarvel -c "SELECT COUNT(*) FROM recruitment_job_requisition;" -t)
echo "Requisitions in restored database: $RECORD_COUNT"

# 6. Restart Odoo
echo "Starting Odoo..."
systemctl start odoo
sleep 10

# 7. Verify service
if systemctl is-active --quiet odoo; then
    echo "✅ Recovery completed successfully"
else
    echo "❌ Odoo failed to start"
    systemctl status odoo
fi
```

### Partial Recovery (Specific Records)

**If you need to recover specific records (e.g., one application):**

```bash
# 1. Export record from backup database
sudo -u postgres pg_dump \
  --data-only \
  --table=recruitment_application \
  -Fc \
  /var/lib/odoo/backups/eigermarvel_pre_v18020_*.dump | \
  sudo -u postgres pg_restore --data-only -d eigermarvel

# 2. Or execute recovery script
cat > /tmp/recover_record.sql << 'EOF'
-- Insert missing application from backup (replace values)
INSERT INTO recruitment_application (id, name, partner_id, job_id, state, create_date, create_uid)
VALUES (
  1, 
  'John Doe - Senior Developer', 
  2, 
  1, 
  'received',
  NOW(),
  2
);

-- Re-subscribe to messages
INSERT INTO mail_followers (res_model, res_id, partner_id, subtype_ids)
VALUES ('recruitment.application', 1, 2, '{}');
EOF

sudo -u postgres psql eigermarvel < /tmp/recover_record.sql
```

---

## 👁️ Monitoring & Validation

### Post-Deployment Monitoring (24 hours)

**Create monitoring script:**

```bash
#!/bin/bash
# Monitoring script - run for 24 hours after deployment

LOG_FILE="/var/log/odoo/recruitment_monitor_$(date +%Y%m%d).log"

while true; do
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  
  echo "[$TIMESTAMP] Monitoring checkpoint" >> $LOG_FILE
  
  # Check Odoo service
  if ! systemctl is-active --quiet odoo; then
    echo "[$TIMESTAMP] ❌ CRITICAL: Odoo service is DOWN" >> $LOG_FILE
    systemctl status odoo >> $LOG_FILE
    break
  fi
  
  # Check database connection
  CONN_CHECK=$(sudo -u postgres psql -d eigermarvel -c "SELECT 1" 2>&1)
  if [ $? -ne 0 ]; then
    echo "[$TIMESTAMP] ❌ CRITICAL: Database connection failed" >> $LOG_FILE
    break
  fi
  
  # Check recruitment module
  MODULE_STATE=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT state FROM ir_module_module WHERE name='recruitment_uae';" -t)
  if [ "$MODULE_STATE" != "installed" ]; then
    echo "[$TIMESTAMP] ❌ WARNING: Module state is $MODULE_STATE" >> $LOG_FILE
  fi
  
  # Check for errors in logs
  ERRORS=$(grep -c "ERROR\|FATAL\|TRACEBACK" /var/log/odoo/odoo.log || true)
  if [ $ERRORS -gt 0 ]; then
    echo "[$TIMESTAMP] ⚠️ WARNING: $ERRORS errors found in logs" >> $LOG_FILE
  fi
  
  # Check record counts
  REQ_COUNT=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) FROM recruitment_job_requisition;" -t)
  APP_COUNT=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) FROM recruitment_application;" -t)
  
  echo "[$TIMESTAMP] Records - Requisitions: $REQ_COUNT, Applications: $APP_COUNT" >> $LOG_FILE
  
  # Wait 1 hour before next check
  sleep 3600
done

echo "Monitoring ended at $(date)" >> $LOG_FILE
```

**Run monitoring:**
```bash
chmod +x /tmp/monitor_recruitment.sh
nohup /tmp/monitor_recruitment.sh > /dev/null 2>&1 &
```

### Validation Checklist

**After deployment, verify each item:**

- [ ] Odoo service is running (`systemctl status odoo`)
- [ ] Database connection working (`psql -d eigermarvel`)
- [ ] Module state is "installed" (check ir_module_module)
- [ ] All 2 job requisitions visible in UI
- [ ] All 1 application visible in UI
- [ ] Chatter sidebar visible on requisition form
- [ ] Chatter sidebar visible on application form
- [ ] Chatter sidebar visible on contract form
- [ ] Smart button "Deployments" visible on requisition
- [ ] Smart button "Contracts" visible on application
- [ ] Activity tracking working (create new activity type)
- [ ] Email templates created (5 new templates visible)
- [ ] No JavaScript errors in browser console
- [ ] No Python errors in Odoo logs
- [ ] Database backup exists and is restorable
- [ ] All new fields exist (contract_count, deployment_count)

---

## 🆘 Emergency Contacts & Escalation

### If Deployment Fails

**Step 1: Immediate Assessment**
```bash
# Check service status
systemctl status odoo

# Check logs for errors
tail -50 /var/log/odoo/odoo.log | grep -i error

# Check database
sudo -u postgres psql eigermarvel -c "SELECT 1;"
```

**Step 2: Attempt Quick Fix**
- Verify backup was created ✅
- Check file permissions: `ls -la /opt/odoo/addons/recruitment_uae/`
- Try restart: `systemctl restart odoo`

**Step 3: Rollback Decision**
- If any data loss suspected → Execute Scenario 1 (Rollback)
- If views broken → Execute Scenario 3 (View Cache Clear)
- If email conflicts → Execute Scenario 4 (Template Fix)
- If all else fails → Execute Full Database Restore

### Backup Location & Access

- **Backups Directory:** `/var/lib/odoo/backups/`
- **Latest Backup:** `eigermarvel_pre_v18020_*.dump`
- **Backup Size:** ~500MB-2GB (depending on data)
- **Restore Time:** 5-10 minutes
- **Test Before Prod:** Always test restore in staging first

### Critical Records to Verify

**Must check after deployment:**

```sql
-- These 2 requisitions must exist and have unchanged data
SELECT id, name, state, partner_id FROM recruitment_job_requisition ORDER BY id;

-- This 1 application must exist with messages intact
SELECT id, name, job_id, state, message_ids FROM recruitment_application;

-- Message counts should match (verify chatter worked)
SELECT res_model, COUNT(*) FROM mail_message GROUP BY res_model;
```

### Success Criteria

✅ **Deployment is SUCCESSFUL when:**
- All 2 requisitions visible in UI
- All 1 application visible in UI  
- Chatter showing on all forms
- Smart buttons displaying correct counts
- No JavaScript errors in browser
- No Python errors in server logs
- Database backup verified and restorable
- Module version shows 18.0.2.0.0

❌ **Rollback IMMEDIATELY if:**
- Any requisition missing from database
- Any application missing from database
- Any chatter messages lost
- Service fails to restart
- Web UI shows blank/error pages
- Database cannot be accessed

---

## 📝 Deployment Checklist

**Before Deployment:**
- [ ] All backups verified and tested
- [ ] File integrity checked
- [ ] Module dependencies verified
- [ ] Database health checked
- [ ] Users notified of maintenance window
- [ ] Rollback procedures documented and ready
- [ ] Monitoring script prepared

**During Deployment:**
- [ ] Odoo stopped cleanly
- [ ] Database backup created
- [ ] Files uploaded without errors
- [ ] Module update command executed
- [ ] No errors in installation logs
- [ ] Database integrity verified

**After Deployment:**
- [ ] Odoo service started successfully
- [ ] All 2 requisitions visible
- [ ] All 1 application visible
- [ ] Chatter working on all forms
- [ ] Smart buttons counting correctly
- [ ] No errors in browser or server logs
- [ ] Monitoring script running

---

## 🔐 Security Considerations

- **Database Access:** Only odoo user touches production database
- **File Ownership:** All files owned by odoo:odoo (verified with chown)
- **Backup Encryption:** Consider encrypting backups with GPG
- **Access Logs:** Check `pg_log/` for any unauthorized access attempts
- **Audit Trail:** All changes logged in `/var/log/odoo/recruitment_update.log`

---

**Document Version:** 1.0
**Last Updated:** 2024
**Valid Until:** v18.0.2.0.0 deployment complete + 7 days monitoring

For additional assistance, refer to:
- SAFE_DEPLOYMENT_PLAN.md (deployment strategy)
- IMPLEMENTATION_SUMMARY.md (technical details)
- README.md (feature overview)
