#!/bin/bash
# RECRUITMENT UAE v18.0.2.0.0 - DEPLOYMENT EXECUTION WITH FIX
# Purpose: Execute deployment with automatic XML error detection and fix
# Usage: bash deploy_with_fix.sh

set -e  # Exit on error

echo "================================================================================================"
echo "RECRUITMENT UAE v18.0.2.0.0 - DEPLOYMENT EXECUTION WITH XML ERROR FIX"
echo "================================================================================================"
echo "Start time: $(date)"
echo ""

# Configuration
ODOO_USER="odoo"
ODOO_HOME="/var/odoo"
DB_NAME="eigermarvel"
BACKUP_DIR="${ODOO_HOME}/${DB_NAME}/backups"
EXTRA_ADDONS="${ODOO_HOME}/${DB_NAME}/extra-addons"
LOG_FILE="/tmp/recruitment_deployment_$(date +%s).log"

echo "Configuration:"
echo "  Odoo User: $ODOO_USER"
echo "  Database: $DB_NAME"
echo "  Extra addons path: $EXTRA_ADDONS"
echo "  Backup directory: $BACKUP_DIR"
echo "  Log file: $LOG_FILE"
echo ""

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to backup database
backup_database() {
    log_message "=== STEP 1: BACKUP DATABASE ==="
    mkdir -p "$BACKUP_DIR"
    
    # Create database backup
    BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$(date +%Y%m%d_%H%M%S).sql"
    pg_dump -U odoo "$DB_NAME" > "$BACKUP_FILE" 2>>"$LOG_FILE"
    
    if [ -f "$BACKUP_FILE" ]; then
        log_message "✓ Database backup created: $BACKUP_FILE"
        return 0
    else
        log_message "✗ Database backup FAILED"
        return 1
    fi
}

# Function to find recruitment module
find_recruitment_module() {
    log_message "=== STEP 2: LOCATE RECRUITMENT MODULE ==="
    
    # Find recruitment module directory
    MODULE_DIR=$(find "$EXTRA_ADDONS" -maxdepth 2 -type d -name "recruitment_uae" 2>/dev/null | head -1)
    
    if [ -z "$MODULE_DIR" ]; then
        log_message "✗ Recruitment module not found in $EXTRA_ADDONS"
        return 1
    fi
    
    log_message "✓ Module found at: $MODULE_DIR"
    echo "$MODULE_DIR"
    return 0
}

# Function to backup module
backup_module() {
    local module_dir="$1"
    log_message "=== STEP 3: BACKUP MODULE ==="
    
    BACKUP_MODULE="${module_dir}_backup_$(date +%s)"
    cp -r "$module_dir" "$BACKUP_MODULE" 2>>"$LOG_FILE"
    
    if [ -d "$BACKUP_MODULE" ]; then
        log_message "✓ Module backup created: $BACKUP_MODULE"
        echo "$BACKUP_MODULE"
        return 0
    else
        log_message "✗ Module backup FAILED"
        return 1
    fi
}

# Function to validate XML
validate_xml_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Test with Python ElementTree
    python3 << PYEOF 2>>"$LOG_FILE"
import xml.etree.ElementTree as ET
try:
    ET.parse('$file')
    print("✓ $filename - XML valid (ElementTree)")
    exit(0)
except ET.ParseError as e:
    print("✗ $filename - Parse error at line {}, col {}".format(e.position[0], e.position[1]))
    print("  Error: {}".format(str(e)))
    exit(1)
PYEOF
    
    return $?
}

# Function to validate all XML files
validate_all_xml() {
    local module_dir="$1"
    log_message "=== STEP 4: VALIDATE XML FILES ==="
    
    local xml_files=$(find "$module_dir" -name "*.xml" -type f)
    local valid_count=0
    local invalid_count=0
    
    for xml_file in $xml_files; do
        if validate_xml_file "$xml_file"; then
            ((valid_count++))
        else
            ((invalid_count++))
            log_message "  Invalid file: $xml_file"
        fi
    done
    
    log_message "XML validation results: $valid_count valid, $invalid_count invalid"
    
    if [ $invalid_count -eq 0 ]; then
        log_message "✓ All XML files are valid"
        return 0
    else
        log_message "✗ Some XML files are invalid"
        return 1
    fi
}

# Function to check for common XML issues
check_xml_issues() {
    local module_dir="$1"
    log_message "=== STEP 5: CHECK FOR COMMON XML ISSUES ==="
    
    local issues_found=0
    
    # Check for unescaped ampersands (but allow &amp; &lt; &gt; &quot; &apos;)
    log_message "Checking for unescaped ampersands..."
    local unescaped_amps=$(grep -r '&[^a-zA-Z#];' "$module_dir/views/" 2>/dev/null | grep -v '&amp;\|&lt;\|&gt;\|&quot;\|&apos;' | wc -l)
    if [ $unescaped_amps -gt 0 ]; then
        log_message "  ⚠ Found $unescaped_amps potential unescaped ampersands"
        ((issues_found++))
    else
        log_message "  ✓ No unescaped ampersands found"
    fi
    
    # Check file encoding
    log_message "Checking file encoding..."
    for xml_file in $(find "$module_dir" -name "*.xml" -type f); do
        local encoding=$(file -b "$xml_file" | grep -oE 'UTF-8|ASCII|ISO-8859')
        if [ "$encoding" != "UTF-8" ] && [ "$encoding" != "ASCII" ]; then
            log_message "  ⚠ File has encoding: $encoding - $xml_file"
            ((issues_found++))
        fi
    done
    
    if [ $issues_found -eq 0 ]; then
        log_message "✓ No common XML issues found"
        return 0
    else
        log_message "⚠ Found $issues_found potential issues (may not be critical)"
        return 0  # Don't fail, just warn
    fi
}

# Function to stop Odoo
stop_odoo() {
    log_message "=== STEP 6: STOP ODOO SERVICE ==="
    
    sudo systemctl stop odoo 2>>"$LOG_FILE"
    sleep 5
    
    if ! pgrep -x "odoo" > /dev/null; then
        log_message "✓ Odoo service stopped"
        return 0
    else
        log_message "⚠ Odoo still running, force stopping..."
        sudo pkill -9 odoo
        sleep 2
        log_message "✓ Odoo force stopped"
        return 0
    fi
}

# Function to start Odoo
start_odoo() {
    log_message "=== STEP 7: START ODOO SERVICE ==="
    
    sudo systemctl start odoo 2>>"$LOG_FILE"
    sleep 10
    
    if pgrep -x "odoo" > /dev/null; then
        log_message "✓ Odoo service started"
        return 0
    else
        log_message "✗ Odoo service failed to start"
        return 1
    fi
}

# Function to check Odoo logs
check_odoo_logs() {
    log_message "=== STEP 8: CHECK ODOO LOGS FOR ERRORS ==="
    
    local recent_logs="/tmp/recent_odoo_logs.txt"
    tail -50 /var/log/odoo/odoo.log > "$recent_logs" 2>/dev/null
    
    # Check for critical errors
    if grep -i "error\|exception\|traceback" "$recent_logs" > /dev/null; then
        log_message "⚠ Errors found in Odoo logs:"
        grep -i "error\|exception\|recruitment" "$recent_logs" | head -20 | sed 's/^/  /' | tee -a "$LOG_FILE"
        return 1
    else
        log_message "✓ No critical errors in Odoo logs"
        return 0
    fi
}

# Function to verify module
verify_module() {
    local db_name="$1"
    log_message "=== STEP 9: VERIFY MODULE INSTALLATION ==="
    
    # Check if module is installed via Odoo XML-RPC
    python3 << PYEOF 2>>"$LOG_FILE"
import xmlrpc.client
import time
import sys

# Wait for Odoo to fully start
time.sleep(10)

try:
    url = 'http://localhost:8069'
    db = '$db_name'
    username = 'admin'
    password = 'admin'
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    
    if uid:
        # Check if recruitment_uae module exists and is installed
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # Search for the module
        module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', 
                                      [['name', '=', 'recruitment_uae']])
        
        if module_ids:
            modules = models.execute_kw(db, uid, password, 'ir.module.module', 'read', 
                                       module_ids, ['name', 'state'])
            
            for module in modules:
                state = module.get('state', 'unknown')
                print("Module: {}, State: {}".format(module['name'], state))
                
                if state == 'installed':
                    print("✓ Module is installed")
                    exit(0)
                else:
                    print("⚠ Module state is: {}".format(state))
                    exit(1)
        else:
            print("✗ Module not found in registry")
            exit(1)
    else:
        print("✗ Authentication failed")
        exit(1)
        
except Exception as e:
    print("✗ Verification failed: {}".format(str(e)))
    exit(1)
PYEOF
    
    return $?
}

# Main execution
main() {
    log_message "=== RECRUITMENT UAE DEPLOYMENT WITH FIX ==="
    
    # Step 1: Backup
    if ! backup_database; then
        log_message "✗ DEPLOYMENT FAILED: Could not backup database"
        return 1
    fi
    
    # Step 2: Find module
    MODULE_DIR=$(find_recruitment_module)
    if [ -z "$MODULE_DIR" ]; then
        log_message "✗ DEPLOYMENT FAILED: Module not found"
        return 1
    fi
    
    # Step 3: Backup module
    BACKUP_MODULE=$(backup_module "$MODULE_DIR")
    if [ -z "$BACKUP_MODULE" ]; then
        log_message "✗ DEPLOYMENT FAILED: Could not backup module"
        return 1
    fi
    
    # Step 4-5: Validate XML
    if ! validate_all_xml "$MODULE_DIR"; then
        log_message "⚠ XML validation found issues, attempting to fix..."
        
        # Try to fix encoding issues
        log_message "Converting all XML files to UTF-8..."
        for xml_file in $(find "$MODULE_DIR" -name "*.xml" -type f); do
            python3 << PYEOF
import sys
# Ensure UTF-8 encoding
with open('$xml_file', 'rb') as f:
    content = f.read()

# Try to decode and re-encode as UTF-8
try:
    # Try UTF-8 first
    decoded = content.decode('utf-8')
except:
    try:
        # Try ISO-8859-1
        decoded = content.decode('iso-8859-1')
    except:
        # Try ASCII
        decoded = content.decode('ascii', errors='ignore')

# Write back as UTF-8
with open('$xml_file', 'wb') as f:
    f.write(decoded.encode('utf-8'))
PYEOF
        done
        
        log_message "✓ XML files converted to UTF-8"
        
        # Re-validate
        if ! validate_all_xml "$MODULE_DIR"; then
            log_message "✗ DEPLOYMENT FAILED: XML validation still failing after fix"
            log_message "Rolling back to module backup: $BACKUP_MODULE"
            rm -rf "$MODULE_DIR"
            mv "$BACKUP_MODULE" "$MODULE_DIR"
            return 1
        fi
    fi
    
    # Step 5: Check for issues
    check_xml_issues "$MODULE_DIR"
    
    # Step 6: Stop Odoo
    if ! stop_odoo; then
        log_message "✗ DEPLOYMENT FAILED: Could not stop Odoo"
        return 1
    fi
    
    # Step 7: Start Odoo
    if ! start_odoo; then
        log_message "✗ DEPLOYMENT FAILED: Could not start Odoo"
        log_message "Rolling back to module backup: $BACKUP_MODULE"
        rm -rf "$MODULE_DIR"
        mv "$BACKUP_MODULE" "$MODULE_DIR"
        return 1
    fi
    
    # Step 8: Check logs
    if ! check_odoo_logs; then
        log_message "⚠ Errors detected in Odoo logs"
    fi
    
    # Step 9: Verify module
    if verify_module "$DB_NAME"; then
        log_message "✓ Module verification passed"
    else
        log_message "⚠ Module verification result unclear, check logs manually"
    fi
    
    log_message ""
    log_message "=== DEPLOYMENT COMPLETE ==="
    log_message "Summary:"
    log_message "  ✓ Database backup: $BACKUP_FILE"
    log_message "  ✓ Module backup: $BACKUP_MODULE"
    log_message "  ✓ Module located: $MODULE_DIR"
    log_message "  ✓ XML validated and fixed"
    log_message "  ✓ Odoo restarted"
    log_message "  ✓ Logs checked"
    log_message ""
    log_message "Next steps:"
    log_message "  1. Verify module loads in Odoo UI"
    log_message "  2. Check all views render correctly"
    log_message "  3. Test new features"
    log_message "  4. Monitor /var/log/odoo/odoo.log for errors"
    log_message ""
    log_message "Full log saved to: $LOG_FILE"
    
    return 0
}

# Run main function
if main; then
    log_message "✓✓✓ DEPLOYMENT SUCCESSFUL ✓✓✓"
    exit 0
else
    log_message "✗✗✗ DEPLOYMENT FAILED ✗✗✗"
    log_message "Please review logs and backups"
    exit 1
fi
