# OSUS Properties - Monthly Duplicate Check Setup Guide

## 📅 Automated Monthly Duplicate Detection

This guide sets up automated contact duplicate checking that runs on the 1st of every month.

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Copy Scripts to Server

```bash
# SSH into server
ssh root@139.84.163.11

# Create directories
mkdir -p /opt/odoo/scripts
mkdir -p /opt/odoo/reports/duplicates
mkdir -p /var/log/odoo-maintenance

# Copy scripts (run from local machine)
scp -i C:/Users/branm/.ssh/id_ed25519_osusproperties \
    check_contact_duplicates.py \
    monthly_duplicate_check.sh \
    root@139.84.163.11:/opt/odoo/scripts/

# Set permissions
ssh root@139.84.163.11 "chmod +x /opt/odoo/scripts/monthly_duplicate_check.sh"
```

### Step 2: Setup Cron Job

```bash
# SSH into server
ssh root@139.84.163.11

# Edit crontab
crontab -e

# Add this line (runs 1st of every month at 2:00 AM):
0 2 1 * * /opt/odoo/scripts/monthly_duplicate_check.sh

# Save and exit (Ctrl+O, Enter, Ctrl+X for nano)

# Verify cron job
crontab -l
```

### Step 3: Test the Setup

```bash
# Manual test run
/opt/odoo/scripts/monthly_duplicate_check.sh

# Check log
tail -50 /var/log/odoo-maintenance/duplicate_check_*.log

# Check report
ls -lh /opt/odoo/reports/duplicates/
```

---

## 📋 Cron Schedule Options

```bash
# Every 1st of month at 2:00 AM (recommended)
0 2 1 * * /opt/odoo/scripts/monthly_duplicate_check.sh

# Every Sunday at 3:00 AM (weekly check)
0 3 * * 0 /opt/odoo/scripts/monthly_duplicate_check.sh

# 1st and 15th of every month at 2:00 AM (bi-monthly)
0 2 1,15 * * /opt/odoo/scripts/monthly_duplicate_check.sh

# Last day of every month at 2:00 AM
0 2 28-31 * * [ $(date -d tomorrow +\%d) -eq 1 ] && /opt/odoo/scripts/monthly_duplicate_check.sh
```

---

## 📊 What Gets Checked

The automated script checks for:
- ✅ Duplicate emails
- ✅ Duplicate phone numbers
- ✅ Duplicate mobile numbers
- ✅ Duplicate names (3+ occurrences)

**Output:**
- Detailed console report
- JSON report saved to `/opt/odoo/reports/duplicates/`
- Log file saved to `/var/log/odoo-maintenance/`

---

## 📧 Email Notifications (Optional)

To receive email alerts when duplicates are found:

### Setup 1: Install mail utility
```bash
apt-get update
apt-get install mailutils
```

### Setup 2: Configure email
Edit `/opt/odoo/scripts/monthly_duplicate_check.sh` and uncomment line 37:
```bash
mail -s "OSUS Properties: Duplicates Found" your-email@osusproperties.com < "$LOG_FILE"
```

### Setup 3: Test email
```bash
echo "Test email from OSUS Properties server" | mail -s "Test" your-email@osusproperties.com
```

---

## 📂 File Locations

```
Scripts:     /opt/odoo/scripts/
  - check_contact_duplicates.py
  - monthly_duplicate_check.sh
  - cleanup_contact_duplicates.py (optional)

Reports:     /opt/odoo/reports/duplicates/
  - contact_duplicates_report_YYYYMMDD_HHMMSS.json

Logs:        /var/log/odoo-maintenance/
  - duplicate_check_YYYYMMDD_HHMMSS.log

Retention:   180 days (6 months)
```

---

## 🔧 Maintenance Commands

```bash
# View latest log
tail -100 /var/log/odoo-maintenance/duplicate_check_*.log | less

# View latest report
cat /opt/odoo/reports/duplicates/contact_duplicates_report_*.json | jq

# Count total reports
ls -1 /opt/odoo/reports/duplicates/ | wc -l

# Check cron status
systemctl status cron
journalctl -u cron | grep duplicate

# Manual run
/opt/odoo/scripts/monthly_duplicate_check.sh

# View all scheduled jobs
crontab -l
```

---

## 📈 Monitoring Dashboard (Optional)

Create a simple monitoring script:

```bash
#!/bin/bash
# /opt/odoo/scripts/duplicate_stats.sh

echo "OSUS Properties - Duplicate Check Statistics"
echo "============================================="
echo ""
echo "Last 6 Checks:"
for log in $(ls -t /var/log/odoo-maintenance/duplicate_check_*.log | head -6); do
    DATE=$(basename "$log" | cut -d'_' -f3-4 | cut -d'.' -f1)
    DUPLICATES=$(grep "Duplicate Emails:" "$log" | awk '{print $3}')
    echo "  $DATE: $DUPLICATES email duplicates"
done
echo ""
echo "Total Reports Generated: $(ls -1 /opt/odoo/reports/duplicates/ | wc -l)"
echo "Disk Usage: $(du -sh /opt/odoo/reports/duplicates/)"
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Scripts copied to `/opt/odoo/scripts/`
- [ ] Scripts are executable (`chmod +x`)
- [ ] Cron job added (`crontab -l` shows entry)
- [ ] Directories created (scripts, reports, logs)
- [ ] Manual test run successful
- [ ] Log file created in `/var/log/odoo-maintenance/`
- [ ] Report JSON created in `/opt/odoo/reports/duplicates/`
- [ ] Email notifications configured (optional)

---

## 🚨 Troubleshooting

### Cron job not running?
```bash
# Check cron service
systemctl status cron

# Check cron logs
journalctl -u cron | tail -50

# Test script manually
/opt/odoo/scripts/monthly_duplicate_check.sh
```

### Python script errors?
```bash
# Check Python version
python3 --version

# Test connection
python3 /opt/odoo/scripts/check_contact_duplicates.py
```

### Email not working?
```bash
# Test mail utility
echo "Test" | mail -s "Test" your-email@example.com

# Check mail logs
tail -50 /var/log/mail.log
```

---

## 📊 Sample Output

```
================================================================================
OSUS PROPERTIES - CONTACT DUPLICATE CHECKER
================================================================================

✓ Connected to osusproperties (UID: 2)

📥 Fetching all contacts...
✓ Found 1557 total contacts

📊 CONTACT SUMMARY
   Total Contacts:       1557
   Active:               1557
   Inactive/Archived:    0

🔍 DUPLICATE ANALYSIS
   Duplicate Emails:     3 (6 contacts)
   Duplicate Phones:     0 (0 contacts)
   Duplicate Mobiles:    3 (6 contacts)

📄 Report saved: contact_duplicates_report_20260123_020000.json
```

---

## 🔄 Update Scripts

To update the duplicate check logic:

```bash
# Local machine - edit script
nano check_contact_duplicates.py

# Copy to server
scp -i ~/.ssh/id_ed25519_osusproperties \
    check_contact_duplicates.py \
    root@139.84.163.11:/opt/odoo/scripts/

# Test updated script
ssh root@139.84.163.11 "/opt/odoo/scripts/monthly_duplicate_check.sh"
```

---

**Setup Time:** 5 minutes  
**Maintenance:** None (fully automated)  
**Storage:** ~1MB per year (minimal)  
**Next Check:** 1st of next month at 2:00 AM

---

**Documentation Updated:** January 23, 2026  
**Contact:** SGC TECH AI - Database Management
