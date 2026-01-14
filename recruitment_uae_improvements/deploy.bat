@echo off
REM Recruitment UAE Module - Windows Deployment Helper
REM This script helps transfer files to the server
REM For full automated deployment, use deploy.sh in Git Bash or WSL

echo ============================================
echo Recruitment UAE Module - Deployment Helper
echo ============================================
echo.

REM Configuration
set REMOTE_USER=admin
set REMOTE_HOST=eigermarvelhr.com
set REMOTE_PATH=/var/odoo/eigermarvel/src/recruitment_uae
set LOCAL_PATH=d:\01_WORK_PROJECTS\odoo-mcp-server\recruitment_uae_improvements

echo [INFO] This script will help you deploy the improvements.
echo.
echo Prerequisites:
echo   1. WinSCP or scp command available
echo   2. SSH access to %REMOTE_HOST%
echo   3. Admin password ready
echo.
echo Deployment Steps:
echo   1. Backup database and files on server
echo   2. Transfer files using WinSCP or scp
echo   3. Update module on server
echo   4. Verify deployment
echo.
pause

echo.
echo ============================================
echo Step 1: Backup Instructions
echo ============================================
echo.
echo Connect to server and run:
echo   ssh %REMOTE_USER%@%REMOTE_HOST%
echo   cd /var/odoo
echo   mkdir -p backups/recruitment_uae_upgrade_$(date +%%Y%%m%%d)
echo   pg_dump eigermarvel ^> backups/recruitment_uae_upgrade_$(date +%%Y%%m%%d)/backup.sql
echo   cp -r eigermarvel/src/recruitment_uae backups/recruitment_uae_upgrade_$(date +%%Y%%m%%d)/original
echo.
pause

echo.
echo ============================================
echo Step 2: File Transfer Options
echo ============================================
echo.
echo Option 1: Using WinSCP (Recommended for Windows)
echo   1. Open WinSCP
echo   2. Connect to %REMOTE_HOST% as %REMOTE_USER%
echo   3. Navigate to %REMOTE_PATH%
echo   4. Upload files from %LOCAL_PATH%
echo      - models/* to models/
echo      - views/* to views/
echo      - data/* to data/
echo      - security/* to security/
echo.
echo Option 2: Using scp command (if available)
echo   Run these commands in PowerShell or Git Bash:
echo.
echo   scp -r "%LOCAL_PATH%\models\*" %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_PATH%/models/
echo   scp -r "%LOCAL_PATH%\views\*" %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_PATH%/views/
echo   scp -r "%LOCAL_PATH%\data\*" %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_PATH%/data/
echo   scp -r "%LOCAL_PATH%\security\*" %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_PATH%/security/
echo.
pause

echo.
echo ============================================
echo Step 3: Update Module on Server
echo ============================================
echo.
echo Connect to server and run:
echo   ssh %REMOTE_USER%@%REMOTE_HOST%
echo   sudo systemctl stop odoo18
echo   /var/odoo/venv/bin/python3 /var/odoo/odoo18/odoo-bin -c /etc/odoo18.conf -d eigermarvel -u recruitment_uae --stop-after-init
echo   sudo systemctl start odoo18
echo   sudo systemctl status odoo18
echo.
pause

echo.
echo ============================================
echo Step 4: Verification
echo ============================================
echo.
echo 1. Login to https://eigermarvelhr.com
echo 2. Navigate to Recruitment menu
echo 3. Open a Job Requisition
echo 4. Verify:
echo    - Smart buttons at top (Applications, Contracts, Deployments)
echo    - Chatter at bottom with activities
echo    - Statusbar shows correct states
echo.
echo 5. Check logs on server:
echo    ssh %REMOTE_USER%@%REMOTE_HOST%
echo    tail -f /var/log/odoo/odoo18.log
echo.
pause

echo.
echo ============================================
echo Deployment Helper Complete
echo ============================================
echo.
echo For automated deployment, use deploy.sh in Git Bash or WSL
echo.
echo Documentation:
echo   - README.md
echo   - DEPLOYMENT_GUIDE.md
echo   - IMPLEMENTATION_SUMMARY.md
echo.
echo If you encounter issues:
echo   - Check DEPLOYMENT_GUIDE.md for troubleshooting
echo   - Review server logs: /var/log/odoo/odoo18.log
echo   - Use rollback procedure in DEPLOYMENT_GUIDE.md
echo.
pause
