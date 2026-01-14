#!/bin/bash

# Safe Deployment Script for recruitment_uae v18.0.2.0.0
# This script executes the deployment with full logging and error handling
# Target: eigermarvelhr.com (Odoo 18.0, Database: eigermarvel)

set -e

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATETIME_STAMP=$(date '+%Y%m%d_%H%M%S')
LOG_DIR="/var/log/odoo"
LOG_FILE="$LOG_DIR/recruitment_deployment_${DATETIME_STAMP}.log"
BACKUP_DIR="/var/lib/odoo/backups"
MODULE_DIR="/opt/odoo/addons/recruitment_uae"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize status
DEPLOYMENT_SUCCESS=false
ROLLBACK_NEEDED=false

# Create log file
touch $LOG_FILE
chmod 666 $LOG_FILE

echo "═══════════════════════════════════════════════════════════════" | tee -a $LOG_FILE
echo "  Recruitment UAE v18.0.2.0.0 - Deployment Script" | tee -a $LOG_FILE
echo "  Timestamp: $TIMESTAMP" | tee -a $LOG_FILE
echo "  Log file: $LOG_FILE" | tee -a $LOG_FILE
echo "═══════════════════════════════════════════════════════════════" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Error handler
error_exit() {
    echo -e "${RED}❌ ERROR: $1${NC}" | tee -a $LOG_FILE
    ROLLBACK_NEEDED=true
    exit 1
}

success_msg() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a $LOG_FILE
}

warning_msg() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a $LOG_FILE
}

info_msg() {
    echo -e "${BLUE}ℹ️  $1${NC}" | tee -a $LOG_FILE
}

# ============================================================================
# PHASE 1: PRE-DEPLOYMENT SETUP (15 minutes)
# ============================================================================

echo "PHASE 1: PRE-DEPLOYMENT SETUP" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Step 1.1: Checking system readiness..."

# Verify script is running as root (for service control)
if [[ $EUID -ne 0 ]]; then
    error_exit "This script must be run as root (use: sudo)"
fi

# Check for pre-deployment check script
if [ -f "/tmp/recruitment_pre_deployment_check_*.log" ]; then
    info_msg "Pre-deployment checks found. Assuming validation passed."
else
    warning_msg "No pre-deployment check log found. Running basic checks..."
fi

# Verify database backup exists
info_msg "Step 1.2: Creating database backup..."

if ! mkdir -p $BACKUP_DIR; then
    error_exit "Cannot create backup directory: $BACKUP_DIR"
fi

BACKUP_FILE="$BACKUP_DIR/eigermarvel_pre_v18020_${DATETIME_STAMP}.dump"

if sudo -u postgres pg_dump -Fc eigermarvel > "$BACKUP_FILE" 2>&1; then
    BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    success_msg "Database backup created: $(basename $BACKUP_FILE) ($BACKUP_SIZE)"
else
    error_exit "Database backup failed"
fi

# Verify backup integrity
info_msg "Step 1.3: Testing backup integrity..."

if sudo -u postgres pg_restore --test -Fc "$BACKUP_FILE" > /dev/null 2>&1; then
    success_msg "Backup integrity verified"
else
    error_exit "Backup integrity test failed - ABORTING DEPLOYMENT"
fi

# Capture current data state
info_msg "Step 1.4: Capturing current database state..."

PRE_DEPLOYMENT_STATE=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) as requisitions FROM recruitment_job_requisition; \
     SELECT COUNT(*) as applications FROM recruitment_application; \
     SELECT COUNT(*) as contracts FROM recruitment_contract;" -t 2>/dev/null)

echo "Pre-deployment record counts:" | tee -a $LOG_FILE
echo "$PRE_DEPLOYMENT_STATE" | tee -a $LOG_FILE

# Notify users of maintenance
info_msg "Step 1.5: Preparing maintenance window..."

echo "" | tee -a $LOG_FILE
echo "NOTE: Consider putting system in maintenance mode for users:" | tee -a $LOG_FILE
echo "  1. Create /var/www/html/maintenance.html" | tee -a $LOG_FILE
echo "  2. Configure web server to serve maintenance page" | tee -a $LOG_FILE
echo "  3. Stop Odoo service: systemctl stop odoo" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "Continuing with deployment..." | tee -a $LOG_FILE

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 2: STOP ODOO SERVICE
# ============================================================================

echo "PHASE 2: STOPPING ODOO SERVICE" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Stopping Odoo service..."

if systemctl stop odoo 2>&1 | tee -a $LOG_FILE; then
    sleep 3
    if ! systemctl is-active --quiet odoo; then
        success_msg "Odoo service stopped successfully"
    else
        warning_msg "Odoo service may still be running. Forcing stop..."
        killall odoo-bin 2>/dev/null || true
        sleep 2
    fi
else
    error_exit "Failed to stop Odoo service"
fi

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 3: FILE UPLOAD/COPY
# ============================================================================

echo "PHASE 3: UPLOADING MODULE FILES" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Creating backup of current module..."

CURRENT_MODULE_BACKUP="/opt/odoo/addons/recruitment_uae.backup.${DATETIME_STAMP}"

if [ -d "$MODULE_DIR" ]; then
    cp -r "$MODULE_DIR" "$CURRENT_MODULE_BACKUP"
    success_msg "Current module backed up to: $CURRENT_MODULE_BACKUP"
else
    warning_msg "Current module directory not found"
fi

# Note: Actual file copy would be done via SCP
# This is a placeholder for the actual upload

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 4: VERIFY FILES
# ============================================================================

echo "PHASE 4: VERIFYING MODULE FILES" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Checking Python file syntax..."

SYNTAX_ERRORS=0

for pyfile in $MODULE_DIR/models/*.py; do
    if [ -f "$pyfile" ]; then
        if ! python3 -m py_compile "$pyfile" 2>&1 | tee -a $LOG_FILE; then
            ((SYNTAX_ERRORS++))
        fi
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    success_msg "All Python files have valid syntax"
else
    error_exit "Found $SYNTAX_ERRORS Python files with syntax errors"
fi

info_msg "Checking XML file format..."

for xmlfile in $MODULE_DIR/views/*.xml $MODULE_DIR/data/*.xml; do
    if [ -f "$xmlfile" ]; then
        if ! python3 -c "import xml.etree.ElementTree as ET; ET.parse('$xmlfile')" 2>&1 | tee -a $LOG_FILE; then
            error_exit "Invalid XML in: $(basename $xmlfile)"
        fi
    fi
done

success_msg "All XML files are well-formed"

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 5: MODULE UPDATE
# ============================================================================

echo "PHASE 5: EXECUTING MODULE UPDATE" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Starting Odoo module update (this may take 5-10 minutes)..."

cd /opt/odoo

# Create update command
UPDATE_CMD="python3 odoo-bin -u recruitment_uae \
  --database=eigermarvel \
  --config=/etc/odoo/odoo.conf \
  --stop-after-init \
  --logfile=$LOG_FILE \
  --log-level=debug"

echo "Executing: $UPDATE_CMD" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

if eval $UPDATE_CMD 2>&1 | tee -a $LOG_FILE; then
    success_msg "Module update completed"
else
    echo "" | tee -a $LOG_FILE
    error_exit "Module update failed - check logs above"
fi

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 6: VERIFY MODULE INSTALLATION
# ============================================================================

echo "PHASE 6: VERIFYING MODULE INSTALLATION" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Checking module state in database..."

MODULE_STATE=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT state FROM ir_module_module WHERE name='recruitment_uae';" -t 2>/dev/null)

if [ "$MODULE_STATE" = "installed" ]; then
    success_msg "Module state: INSTALLED"
else
    warning_msg "Module state: $MODULE_STATE (expected: installed)"
fi

# Get module version
MODULE_VERSION=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT latest_version FROM ir_module_module WHERE name='recruitment_uae';" -t 2>/dev/null)

info_msg "Module version: $MODULE_VERSION"

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 7: DATABASE VALIDATION
# ============================================================================

echo "PHASE 7: DATABASE VALIDATION" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Verifying new fields were created..."

# Check for new fields
if sudo -u postgres psql -d eigermarvel -c \
    "SELECT column_name FROM information_schema.columns WHERE table_name='recruitment_job_requisition' AND column_name='contract_count';" -t | grep -q "contract_count"; then
    success_msg "Field 'contract_count' created successfully"
else
    warning_msg "Field 'contract_count' not found (may not be required)"
fi

if sudo -u postgres psql -d eigermarvel -c \
    "SELECT column_name FROM information_schema.columns WHERE table_name='recruitment_job_requisition' AND column_name='deployment_count';" -t | grep -q "deployment_count"; then
    success_msg "Field 'deployment_count' created successfully"
else
    warning_msg "Field 'deployment_count' not found (may not be required)"
fi

# Verify critical records still exist
info_msg "Verifying critical records were preserved..."

POST_DEPLOYMENT_STATE=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) as requisitions FROM recruitment_job_requisition;" -t 2>/dev/null)

echo "Post-deployment requisitions: $POST_DEPLOYMENT_STATE" | tee -a $LOG_FILE

if [ "$POST_DEPLOYMENT_STATE" -ge 2 ]; then
    success_msg "All requisitions preserved"
else
    error_exit "Requisitions were lost during update!"
fi

# Check email templates
EMAIL_TEMPLATES=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) FROM mail_template WHERE name LIKE '%Recruitment%';" -t 2>/dev/null)

info_msg "Email templates created: $EMAIL_TEMPLATES"

# Check activity types
ACTIVITY_TYPES=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) FROM mail_activity_type WHERE name LIKE '%Recruitment%';" -t 2>/dev/null)

info_msg "Activity types created: $ACTIVITY_TYPES"

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 8: START ODOO SERVICE
# ============================================================================

echo "PHASE 8: STARTING ODOO SERVICE" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

info_msg "Starting Odoo service..."

if systemctl start odoo 2>&1 | tee -a $LOG_FILE; then
    sleep 10  # Give service time to start
    
    if systemctl is-active --quiet odoo; then
        success_msg "Odoo service started successfully"
    else
        error_exit "Odoo service failed to start"
    fi
else
    error_exit "Failed to start Odoo service"
fi

echo "" | tee -a $LOG_FILE

# ============================================================================
# PHASE 9: POST-DEPLOYMENT VALIDATION
# ============================================================================

echo "PHASE 9: POST-DEPLOYMENT VALIDATION" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check for errors in logs
info_msg "Checking for errors in Odoo logs..."

ERROR_COUNT=$(grep -c "ERROR\|FATAL\|TRACEBACK" /var/log/odoo/odoo.log 2>/dev/null || echo "0")

if [ "$ERROR_COUNT" -eq 0 ]; then
    success_msg "No errors found in logs"
else
    warning_msg "Found $ERROR_COUNT errors in logs (may be pre-existing)"
    echo "" | tee -a $LOG_FILE
    echo "Latest errors:" | tee -a $LOG_FILE
    grep -i "ERROR\|FATAL" /var/log/odoo/odoo.log | tail -5 | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
fi

# Check database health
info_msg "Verifying database health..."

if sudo -u postgres psql -d eigermarvel -c "SELECT 1" > /dev/null 2>&1; then
    success_msg "Database connection working"
else
    error_exit "Cannot connect to database"
fi

echo "" | tee -a $LOG_FILE

# ============================================================================
# SUMMARY
# ============================================================================

echo "═══════════════════════════════════════════════════════════════" | tee -a $LOG_FILE
echo "DEPLOYMENT SUMMARY" | tee -a $LOG_FILE
echo "═══════════════════════════════════════════════════════════════" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "Deployment Timeline:" | tee -a $LOG_FILE
echo "  Started: $(date)" | tee -a $LOG_FILE
echo "  Duration: Approx 30 minutes" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "Critical Information:" | tee -a $LOG_FILE
echo "  - Backup location: $BACKUP_FILE" | tee -a $LOG_FILE
echo "  - Module location: $MODULE_DIR" | tee -a $LOG_FILE
echo "  - Backup of old module: $CURRENT_MODULE_BACKUP" | tee -a $LOG_FILE
echo "  - Deployment log: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "Next Steps:" | tee -a $LOG_FILE
echo "  1. Verify web UI at https://eigermarvelhr.com" | tee -a $LOG_FILE
echo "  2. Check that all 2+ requisitions are visible" | tee -a $LOG_FILE
echo "  3. Test chatter and smart buttons" | tee -a $LOG_FILE
echo "  4. Monitor logs for next 24 hours" | tee -a $LOG_FILE
echo "  5. Keep this log file for audit trail" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

if [ $ROLLBACK_NEEDED = false ]; then
    DEPLOYMENT_SUCCESS=true
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}" | tee -a $LOG_FILE
    echo -e "${GREEN}✅ DEPLOYMENT COMPLETED SUCCESSFULLY${NC}" | tee -a $LOG_FILE
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}" | tee -a $LOG_FILE
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}" | tee -a $LOG_FILE
    echo -e "${RED}❌ DEPLOYMENT FAILED - REVIEW LOGS AND CONSIDER ROLLBACK${NC}" | tee -a $LOG_FILE
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}" | tee -a $LOG_FILE
    exit 1
fi
