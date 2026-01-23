#!/bin/bash
# OSUS Properties - Monthly Contact Duplicate Check
# This script runs automated duplicate detection and sends report via email

SCRIPT_DIR="/opt/odoo/scripts"
LOG_DIR="/var/log/odoo-maintenance"
REPORT_DIR="/opt/odoo/reports/duplicates"

# Create directories if they don't exist
mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"

# Timestamp for files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/duplicate_check_$TIMESTAMP.log"

echo "================================================================================" | tee -a "$LOG_FILE"
echo "OSUS Properties - Monthly Contact Duplicate Check" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run duplicate check
cd "$SCRIPT_DIR"
python3 check_contact_duplicates.py 2>&1 | tee -a "$LOG_FILE"

# Move generated report to reports directory
if [ -f /tmp/contact_duplicates_report_*.json ]; then
    mv /tmp/contact_duplicates_report_*.json "$REPORT_DIR/"
    echo "Report moved to: $REPORT_DIR" | tee -a "$LOG_FILE"
fi

# Check if duplicates were found
DUPLICATE_COUNT=$(grep "Duplicate Emails:" "$LOG_FILE" | awk '{print $3}')

echo "" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"
echo "Check completed: $(date)" | tee -a "$LOG_FILE"

if [ -n "$DUPLICATE_COUNT" ] && [ "$DUPLICATE_COUNT" -gt 0 ]; then
    echo "Status: ⚠️  DUPLICATES FOUND" | tee -a "$LOG_FILE"
    echo "Action: Manual review required" | tee -a "$LOG_FILE"
    
    # Send email notification (configure email settings)
    # mail -s "OSUS Properties: Duplicates Found in Monthly Check" admin@osusproperties.com < "$LOG_FILE"
else
    echo "Status: ✅ DATABASE CLEAN" | tee -a "$LOG_FILE"
fi

echo "================================================================================" | tee -a "$LOG_FILE"

# Clean up old logs (keep last 6 months)
find "$LOG_DIR" -name "duplicate_check_*.log" -mtime +180 -delete
find "$REPORT_DIR" -name "contact_duplicates_report_*.json" -mtime +180 -delete

exit 0
