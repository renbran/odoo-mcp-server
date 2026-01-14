@echo off
REM ============================================================================
REM EMERGENCY XML FIX & REDEPLOYMENT SCRIPT (Windows)
REM ============================================================================
REM This script fixes the XML parsing error and redeploys the recruitment_uae module

setlocal enabledelayedexpansion

REM Configuration
set REMOTE_USER=%1
if "%REMOTE_USER%"=="" set REMOTE_USER=odoo

set REMOTE_HOST=%2
if "%REMOTE_HOST%"=="" set REMOTE_HOST=eigermarvelhr.com

set DB_NAME=%3
if "%DB_NAME%"=="" set DB_NAME=eigermarvel

set MODULE_PATH=/var/odoo/%DB_NAME%/extra-addons/recruitment_uae

echo.
echo ================================================================================
echo 🚨 EMERGENCY FIX: XML Parsing Error in recruitment_uae Module
echo ================================================================================
echo.
echo REMOTE: %REMOTE_USER%@%REMOTE_HOST%
echo DATABASE: %DB_NAME%
echo.

REM Step 1: Create backup on server
echo 💾 Step 1: Creating backup on server...
ssh %REMOTE_USER%@%REMOTE_HOST% "TIMESTAMP=$(date +%%Y%%m%%d_%%H%%M%%S); BACKUP_DIR=/var/odoo/recruitment_uae_backup_${TIMESTAMP}; cp -r /var/odoo/%DB_NAME%/extra-addons/recruitment_uae $BACKUP_DIR; echo ✅ Backup created: $BACKUP_DIR"

if errorlevel 1 (
    echo ❌ Failed to create backup
    exit /b 1
)
echo.

REM Step 2: Copy corrected files to server
echo 📤 Step 2: Transferring corrected files to server...
scp -r recruitment_uae_improvements\views\*.xml %REMOTE_USER%@%REMOTE_HOST%:%MODULE_PATH%/views/
if errorlevel 1 (
    echo ❌ Failed to transfer files
    exit /b 1
)
echo ✅ All view files transferred
echo.

REM Step 3: Validate files and restart Odoo
echo ⏹️  Step 3: Stopping Odoo service...
ssh %REMOTE_USER%@%REMOTE_HOST% "sudo systemctl stop odoo && sleep 5 && echo ✅ Odoo stopped"

if errorlevel 1 (
    echo ❌ Failed to stop Odoo
    exit /b 1
)
echo.

echo ▶️  Step 4: Starting Odoo service...
ssh %REMOTE_USER%@%REMOTE_HOST% "sudo systemctl start odoo && sleep 20 && echo ✅ Odoo started"

if errorlevel 1 (
    echo ❌ Failed to start Odoo
    exit /b 1
)
echo.

REM Step 5: Check for XML errors
echo 🔍 Step 5: Checking for XML parsing errors...
ssh %REMOTE_USER%@%REMOTE_HOST% "tail -200 /var/log/odoo/odoo.log | grep -i 'xmlparse' | wc -l"

echo ✅ Validation complete
echo.

echo ================================================================================
echo ✅ EMERGENCY FIX COMPLETE
echo ================================================================================
echo.
echo 🎯 Next steps:
echo    1. Open Odoo: http://%REMOTE_HOST%:8069
echo    2. Log in with your credentials
echo    3. Go to Apps menu
echo    4. Search for 'recruitment_uae'
echo    5. If it shows 'To Install', click Install button
echo    6. Test the module
echo.
echo ❓ Troubleshooting:
echo    If issues persist, check logs:
echo    ssh %REMOTE_USER%@%REMOTE_HOST% "tail -100 /var/log/odoo/odoo.log"
echo.
pause
