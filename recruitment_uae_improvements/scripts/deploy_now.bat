@echo off
REM RECRUITMENT UAE - AUTOMATED DEPLOYMENT FROM WINDOWS
REM Purpose: Deploy files to server with single command
REM Usage: deploy_now.bat <remote_host> [remote_user] [db_name]

setlocal enabledelayedexpansion

REM Configuration
set REMOTE_HOST=%1
set REMOTE_USER=%2
set DB_NAME=%3

REM Set defaults
if "%REMOTE_HOST%"=="" set REMOTE_HOST=eigermarvelhr.com
if "%REMOTE_USER%"=="" set REMOTE_USER=odoo
if "%DB_NAME%"=="" set DB_NAME=eigermarvel

set EXTRA_ADDONS=/var/odoo/%DB_NAME%/extra-addons

echo ================================================================================
echo.
echo  ^!^! RECRUITMENT UAE MODULE - AUTOMATED DEPLOYMENT
echo.
echo ================================================================================
echo Remote Host:   %REMOTE_HOST%
echo Remote User:   %REMOTE_USER%
echo Database:      %DB_NAME%
echo Extra Addons:  %EXTRA_ADDONS%
echo.
echo ================================================================================

REM Check if SSH is available
where ssh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: SSH client not found in PATH
    echo Please install OpenSSH (comes with Windows 10+) or Git Bash
    pause
    exit /b 1
)

REM Test connection
echo Testing SSH connection...
ssh -q -o ConnectTimeout=5 %REMOTE_USER%@%REMOTE_HOST% "exit" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cannot connect to %REMOTE_HOST%
    echo Please check:
    echo   - SSH is working: ssh %REMOTE_USER%@%REMOTE_HOST%
    echo   - User/host are correct
    echo   - You have SSH key/password configured
    pause
    exit /b 1
)
echo ^[OK^] SSH connection successful
echo.

REM STEP 1: Create backup
echo ================================================================================
echo STEP 1: CREATE BACKUP
echo ================================================================================
ssh %REMOTE_USER%@%REMOTE_HOST% << 'BACKUP_SCRIPT'
MODULE_DIR=$(find /var/odoo/eigermarvel/extra-addons -maxdepth 2 -type d -name "recruitment_uae" 2>/dev/null | head -1)
if [ -z "$MODULE_DIR" ]; then
    echo "ERROR: Module not found!"
    exit 1
fi
echo "Found module at: $MODULE_DIR"
BACKUP_DIR="${MODULE_DIR}_backup_$(date +%%s)"
cp -r "$MODULE_DIR" "$BACKUP_DIR"
echo "^[OK^] Backup created: $BACKUP_DIR"
BACKUP_SCRIPT
echo.

REM STEP 2: Transfer files
echo ================================================================================
echo STEP 2: TRANSFER FILES
echo ================================================================================

echo Transferring models...
scp -q -r models\ %REMOTE_USER%@%REMOTE_HOST%:%EXTRA_ADDONS%/recruitment_uae/models/ 2>nul && echo ^[OK^] models transferred || echo ERROR transferring models

echo Transferring views...
scp -q -r views\ %REMOTE_USER%@%REMOTE_HOST%:%EXTRA_ADDONS%/recruitment_uae/views/ 2>nul && echo ^[OK^] views transferred || echo ERROR transferring views

echo Transferring data...
scp -q -r data\ %REMOTE_USER%@%REMOTE_HOST%:%EXTRA_ADDONS%/recruitment_uae/data/ 2>nul && echo ^[OK^] data transferred || echo ERROR transferring data

echo Transferring security...
scp -q -r security\ %REMOTE_USER%@%REMOTE_HOST%:%EXTRA_ADDONS%/recruitment_uae/security/ 2>nul && echo ^[OK^] security transferred || echo ERROR transferring security

echo Transferring manifest...
scp -q __manifest__.py %REMOTE_USER%@%REMOTE_HOST%:%EXTRA_ADDONS%/recruitment_uae/ 2>nul && echo ^[OK^] __manifest__.py transferred || echo ERROR transferring manifest

echo Transferring init...
scp -q __init__.py %REMOTE_USER%@%REMOTE_HOST%:%EXTRA_ADDONS%/recruitment_uae/ 2>nul && echo ^[OK^] __init__.py transferred || echo ERROR transferring init

echo.

REM STEP 3: Validate files
echo ================================================================================
echo STEP 3: VALIDATE FILES ON SERVER
echo ================================================================================

ssh %REMOTE_USER%@%REMOTE_HOST% << 'VALIDATE_SCRIPT'
cd /var/odoo/eigermarvel/extra-addons/recruitment_uae

python3 << 'PYEOF'
import xml.etree.ElementTree as ET
import os

xml_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith('.xml'):
            xml_files.append(os.path.join(root, file))

print("Validating XML files...")
valid_count = 0
invalid_count = 0

for xml_file in sorted(xml_files):
    try:
        ET.parse(xml_file)
        print(f"  [OK] {xml_file}")
        valid_count += 1
    except ET.ParseError as e:
        print(f"  ERROR {xml_file}: {e}")
        invalid_count += 1

print("")
print(f"Results: {valid_count} valid, {invalid_count} invalid")

if invalid_count == 0:
    print("[OK] ALL FILES ARE VALID")
    exit(0)
else:
    print("ERROR: SOME FILES HAVE ERRORS")
    exit(1)
PYEOF
VALIDATE_SCRIPT

echo.

REM STEP 4: Restart Odoo
echo ================================================================================
echo STEP 4: RESTART ODOO SERVICE
echo ================================================================================

ssh %REMOTE_USER%@%REMOTE_HOST% << 'RESTART_SCRIPT'
echo "Stopping Odoo..."
sudo systemctl stop odoo
sleep 3
sleep 7

if pgrep -x "odoo" > /dev/null; then
    echo "WARNING: Odoo still running, forcing..."
    sudo pkill -9 odoo
    sleep 2
fi

echo "[OK] Odoo stopped"
echo ""
echo "Starting Odoo..."
sudo systemctl start odoo
echo "Waiting for startup (30 seconds)..."
sleep 30

if pgrep -x "odoo" > /dev/null; then
    echo "[OK] Odoo started"
else
    echo "ERROR: Odoo failed to start!"
    exit 1
fi
RESTART_SCRIPT

echo.

REM STEP 5: Check logs
echo ================================================================================
echo STEP 5: CHECK LOGS
echo ================================================================================

ssh %REMOTE_USER%@%REMOTE_HOST% << 'LOGS_SCRIPT'
echo "Checking for errors..."
ERRORS=$(tail -100 /var/log/odoo/odoo.log 2>/dev/null | grep -i "error\|exception\|xmlparse" | wc -l)

if [ $ERRORS -gt 0 ]; then
    echo "WARNING: Found $ERRORS potential issues in logs"
    tail -100 /var/log/odoo/odoo.log 2>/dev/null | grep -i "error\|exception\|xmlparse" | head -10
else
    echo "[OK] No critical errors in logs"
fi
LOGS_SCRIPT

echo.

REM SUMMARY
echo ================================================================================
echo.
echo  ✓ DEPLOYMENT COMPLETE
echo.
echo ================================================================================
echo.
echo Next steps:
echo   1. Open Odoo: http://%REMOTE_HOST%:8069
echo   2. Login as admin
echo   3. Go to Apps menu
echo   4. Search for "recruitment_uae"
echo   5. Check if module is installed
echo   6. Test views and features
echo.
echo ================================================================================
echo.

pause
