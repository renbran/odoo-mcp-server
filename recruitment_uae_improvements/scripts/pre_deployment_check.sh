#!/bin/bash

# Pre-Deployment Verification Script for recruitment_uae v18.0.2.0.0
# This script verifies the system is ready for safe deployment
# Target: eigermarvelhr.com (Odoo 18.0, Database: eigermarvel)

set -e

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/tmp/recruitment_pre_deployment_check_$(date +%Y%m%d_%H%M%S).log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════════════════════════════"
echo "  Recruitment UAE Module v18.0.2.0.0 - Pre-Deployment Check"
echo "  Timestamp: $TIMESTAMP"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Initialize counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Helper functions
log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a $LOG_FILE
}

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1" | tee -a $LOG_FILE
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1" | tee -a $LOG_FILE
    ((CHECKS_FAILED++))
}

check_warning() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1" | tee -a $LOG_FILE
    ((CHECKS_WARNING++))
}

# ============================================================================
# 1. SYSTEM & SERVICE CHECKS
# ============================================================================

echo "1️⃣  SYSTEM & SERVICE CHECKS" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check Odoo service
if systemctl is-active --quiet odoo; then
    check_pass "Odoo service is running"
else
    check_fail "Odoo service is NOT running"
fi

# Check PostgreSQL service
if systemctl is-active --quiet postgresql; then
    check_pass "PostgreSQL service is running"
else
    check_fail "PostgreSQL service is NOT running"
fi

# Check disk space
DISK_USAGE=$(df /opt/odoo | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_pass "Disk usage is healthy ($DISK_USAGE%)"
else
    check_fail "Disk usage is critical ($DISK_USAGE%)"
fi

echo ""

# ============================================================================
# 2. DATABASE CHECKS
# ============================================================================

echo "2️⃣  DATABASE CHECKS" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Test database connection
if sudo -u postgres psql -d eigermarvel -c "SELECT 1" > /dev/null 2>&1; then
    check_pass "Database 'eigermarvel' is accessible"
else
    check_fail "Cannot connect to database 'eigermarvel'"
    exit 1
fi

# Check recruitment module is installed
CURRENT_MODULE=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT state FROM ir_module_module WHERE name='recruitment_uae';" -t 2>/dev/null)

if [ "$CURRENT_MODULE" = "installed" ]; then
    check_pass "recruitment_uae module is currently installed"
else
    check_fail "recruitment_uae module is not installed (state: $CURRENT_MODULE)"
fi

# Check current requisitions count
REQ_COUNT=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) FROM recruitment_job_requisition;" -t)
log "Current requisitions: $REQ_COUNT"

if [ "$REQ_COUNT" -ge 2 ]; then
    check_pass "Found $REQ_COUNT requisitions (expected ≥ 2)"
else
    check_warning "Only found $REQ_COUNT requisitions (expected ≥ 2)"
fi

# Check current applications count
APP_COUNT=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) FROM recruitment_application;" -t)
log "Current applications: $APP_COUNT"

if [ "$APP_COUNT" -ge 1 ]; then
    check_pass "Found $APP_COUNT applications (expected ≥ 1)"
else
    check_warning "Only found $APP_COUNT applications (expected ≥ 1)"
fi

# Check chatter configuration
CHATTER_CHECK=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT COUNT(*) FROM mail_message WHERE model='recruitment.application';" -t)
log "Messages on recruitment.application: $CHATTER_CHECK"

if [ "$CHATTER_CHECK" -gt 0 ]; then
    check_pass "Chatter already configured on recruitment.application"
else
    check_warning "No messages found on recruitment.application (may be new module)"
fi

# Check for mail.thread inheritance conflicts
CONFLICTING_INHERIT=$(grep -r "mail.thread.*mail.activity.mixin" /opt/odoo/addons/recruitment_uae/models/ 2>/dev/null | wc -l)
if [ "$CONFLICTING_INHERIT" -eq 0 ]; then
    check_pass "No duplicate mail.thread inheritance detected"
else
    check_fail "Found $CONFLICTING_INHERIT files with conflicting inheritance"
fi

echo ""

# ============================================================================
# 3. MODULE FILES CHECK
# ============================================================================

echo "3️⃣  MODULE FILES CHECK" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check module directory exists
if [ -d "/opt/odoo/addons/recruitment_uae" ]; then
    check_pass "Module directory exists (/opt/odoo/addons/recruitment_uae)"
else
    check_fail "Module directory not found (/opt/odoo/addons/recruitment_uae)"
    exit 1
fi

# Check critical Python files
CRITICAL_FILES=("__manifest__.py" "__init__.py" "models/__init__.py")

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "/opt/odoo/addons/recruitment_uae/$file" ]; then
        check_pass "Found: $file"
    else
        check_fail "Missing: $file"
    fi
done

# Check model files syntax
for model_file in /opt/odoo/addons/recruitment_uae/models/recruitment_*.py; do
    if python -m py_compile "$model_file" 2>/dev/null; then
        check_pass "Model file syntax OK: $(basename $model_file)"
    else
        check_fail "Syntax error in: $(basename $model_file)"
    fi
done

# Check XML files are well-formed
for xml_file in /opt/odoo/addons/recruitment_uae/views/*.xml /opt/odoo/addons/recruitment_uae/data/*.xml 2>/dev/null; do
    if [ -f "$xml_file" ] && python -c "import xml.etree.ElementTree as ET; ET.parse('$xml_file')" 2>/dev/null; then
        check_pass "XML valid: $(basename $xml_file)"
    else
        check_warning "Could not validate: $(basename $xml_file)"
    fi
done

echo ""

# ============================================================================
# 4. BACKUP VERIFICATION
# ============================================================================

echo "4️⃣  BACKUP VERIFICATION" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check backup directory
if [ -d "/var/lib/odoo/backups" ]; then
    check_pass "Backup directory exists (/var/lib/odoo/backups)"
else
    check_fail "Backup directory not found (/var/lib/odoo/backups)"
fi

# Check for recent backups
BACKUP_COUNT=$(ls -1 /var/lib/odoo/backups/eigermarvel*.dump 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 0 ]; then
    check_pass "Found $BACKUP_COUNT backup file(s)"
    
    # List latest backup
    LATEST_BACKUP=$(ls -1t /var/lib/odoo/backups/eigermarvel*.dump 2>/dev/null | head -1)
    BACKUP_SIZE=$(ls -lh "$LATEST_BACKUP" | awk '{print $5}')
    log "Latest backup: $(basename $LATEST_BACKUP) ($BACKUP_SIZE)"
else
    check_fail "No backup files found in /var/lib/odoo/backups"
fi

# Test backup integrity (optional - takes time)
if [ "$BACKUP_COUNT" -gt 0 ]; then
    log "Testing backup integrity... (this may take a moment)"
    if sudo -u postgres pg_restore --test -Fc "$LATEST_BACKUP" > /dev/null 2>&1; then
        check_pass "Latest backup integrity verified"
    else
        check_fail "Latest backup failed integrity test"
    fi
fi

echo ""

# ============================================================================
# 5. FILE PERMISSIONS CHECK
# ============================================================================

echo "5️⃣  FILE PERMISSIONS CHECK" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check module directory ownership
OWNER=$(stat -c "%U:%G" /opt/odoo/addons/recruitment_uae 2>/dev/null)
if [ "$OWNER" = "odoo:odoo" ]; then
    check_pass "Module directory owned by odoo:odoo"
else
    check_warning "Module directory owned by $OWNER (expected odoo:odoo)"
fi

# Check odoo user exists
if id "odoo" &>/dev/null; then
    check_pass "Odoo system user exists"
else
    check_fail "Odoo system user not found"
fi

# Check odoo can write to var/log
if touch /var/log/odoo/test_write.log 2>/dev/null; then
    rm /var/log/odoo/test_write.log
    check_pass "Odoo can write to /var/log/odoo"
else
    check_fail "Odoo cannot write to /var/log/odoo"
fi

echo ""

# ============================================================================
# 6. DEPENDENCIES CHECK
# ============================================================================

echo "6️⃣  DEPENDENCIES CHECK" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check if mail module is installed
MAIL_MODULE=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT state FROM ir_module_module WHERE name='mail';" -t 2>/dev/null)

if [ "$MAIL_MODULE" = "installed" ]; then
    check_pass "Mail module is installed (required for chatter)"
else
    check_fail "Mail module is not installed (required for chatter)"
fi

# Check for conflicting module versions
EXISTING_VERSION=$(sudo -u postgres psql -d eigermarvel -c \
    "SELECT latest_version FROM ir_module_module WHERE name='recruitment_uae';" -t 2>/dev/null)

log "Current recruitment_uae version: $EXISTING_VERSION"

if [ "$EXISTING_VERSION" = "18.0.1.1.0" ]; then
    check_pass "Current version is 18.0.1.1.0 (eligible for upgrade to 18.0.2.0.0)"
else
    check_warning "Current version is $EXISTING_VERSION (update may skip some steps)"
fi

echo ""

# ============================================================================
# 7. APPLICATION-SPECIFIC CHECKS
# ============================================================================

echo "7️⃣  APPLICATION-SPECIFIC CHECKS" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check application_count field exists on requisition
if sudo -u postgres psql -d eigermarvel -c \
    "SELECT column_name FROM information_schema.columns WHERE table_name='recruitment_job_requisition' AND column_name='application_count';" -t | grep -q "application_count"; then
    check_pass "application_count field exists on recruitment_job_requisition"
else
    check_warning "application_count field not found on recruitment_job_requisition (may be added during update)"
fi

# Check contract_count field (should not exist yet)
if sudo -u postgres psql -d eigermarvel -c \
    "SELECT column_name FROM information_schema.columns WHERE table_name='recruitment_job_requisition' AND column_name='contract_count';" -t | grep -q "contract_count"; then
    check_warning "contract_count field already exists (duplicate update?)"
else
    check_pass "contract_count field not found (will be added during update)"
fi

# Check deployment_count field (should not exist yet)
if sudo -u postgres psql -d eigermarvel -c \
    "SELECT column_name FROM information_schema.columns WHERE table_name='recruitment_job_requisition' AND column_name='deployment_count';" -t | grep -q "deployment_count"; then
    check_warning "deployment_count field already exists (duplicate update?)"
else
    check_pass "deployment_count field not found (will be added during update)"
fi

echo ""

# ============================================================================
# 8. ODOO CONFIGURATION CHECK
# ============================================================================

echo "8️⃣  ODOO CONFIGURATION CHECK" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check odoo.conf exists and is readable
if [ -f "/etc/odoo/odoo.conf" ]; then
    check_pass "Odoo configuration file exists (/etc/odoo/odoo.conf)"
else
    check_fail "Odoo configuration file not found"
fi

# Check database config in odoo.conf
if grep -q "^db_name = eigermarvel" /etc/odoo/odoo.conf 2>/dev/null; then
    check_pass "Database 'eigermarvel' is configured in odoo.conf"
else
    check_warning "Database 'eigermarvel' not found in odoo.conf configuration"
fi

echo ""

# ============================================================================
# 9. SYSTEM RESOURCE CHECK
# ============================================================================

echo "9️⃣  SYSTEM RESOURCE CHECK" | tee -a $LOG_FILE
echo "─────────────────────────────────────────────────────────────" | tee -a $LOG_FILE

# Check CPU load
CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')
CPU_CORES=$(nproc)
log "CPU Load Average: $CPU_LOAD (cores: $CPU_CORES)"

if (( $(echo "$CPU_LOAD < $CPU_CORES" | bc -l) )); then
    check_pass "CPU load is reasonable ($CPU_LOAD)"
else
    check_warning "CPU load is high ($CPU_LOAD) - deployment may be slower"
fi

# Check memory usage
FREE_MEM=$(free -h | grep "^Mem" | awk '{print $7}')
log "Free memory: $FREE_MEM"

check_pass "Memory check completed (Free: $FREE_MEM)"

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "═══════════════════════════════════════════════════════════════"
echo "  SUMMARY" | tee -a $LOG_FILE
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo -e "${GREEN}Checks Passed:${NC} $CHECKS_PASSED" | tee -a $LOG_FILE
echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARNING" | tee -a $LOG_FILE
echo -e "${RED}Checks Failed:${NC} $CHECKS_FAILED" | tee -a $LOG_FILE
echo ""

TOTAL_CHECKS=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))
echo "Total Checks: $TOTAL_CHECKS" | tee -a $LOG_FILE

echo ""
echo "Log file saved to: $LOG_FILE"
echo ""

# Final recommendation
if [ $CHECKS_FAILED -eq 0 ]; then
    if [ $CHECKS_WARNING -eq 0 ]; then
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}🚀 SYSTEM IS READY FOR DEPLOYMENT${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
        exit 0
    else
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}⚠️  SYSTEM READY FOR DEPLOYMENT (WITH WARNINGS)${NC}"
        echo -e "${YELLOW}Review warnings above before proceeding${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        exit 0
    fi
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ DEPLOYMENT NOT RECOMMENDED${NC}"
    echo -e "${RED}Fix the $CHECKS_FAILED critical issue(s) before proceeding${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
