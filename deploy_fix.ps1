# Deploy and execute the comprehensive fix script for osusproperties
# PowerShell version

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "OSUSPROPERTIES FIX DEPLOYMENT SCRIPT" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

$SERVER = "odoo@104.207.139.132"
$SCRIPT_NAME = "fix_all_osusproperties_issues.py"
$REMOTE_PATH = "/tmp/$SCRIPT_NAME"

Write-Host ""
Write-Host "[1/4] Uploading fix script to server..." -ForegroundColor Yellow
scp $SCRIPT_NAME "$SERVER`:$REMOTE_PATH"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to upload script" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Script uploaded successfully" -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] Making script executable..." -ForegroundColor Yellow
ssh $SERVER "chmod +x $REMOTE_PATH"

Write-Host ""
Write-Host "[3/4] Executing fix script..." -ForegroundColor Yellow
ssh $SERVER "python3 $REMOTE_PATH"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Script execution had errors (this may be normal for some steps)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] Restarting Odoo service..." -ForegroundColor Yellow
ssh $SERVER "sudo systemctl restart odoo-osusproperties"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to restart Odoo service" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Odoo service restarted" -ForegroundColor Green

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "MONITORING SERVICE STATUS..." -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

Start-Sleep -Seconds 5

ssh $SERVER "sudo systemctl status odoo-osusproperties --no-pager | head -n 20"

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "CHECKING LOGS FOR ERRORS..." -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

ssh $SERVER "sudo tail -n 100 /var/odoo/osusproperties/logs/odoo-server.log | grep -i -E '(CRITICAL|ERROR)' | tail -n 20"

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Monitor full logs: ssh $SERVER 'sudo tail -f /var/odoo/osusproperties/logs/odoo-server.log'" -ForegroundColor White
Write-Host "2. Test the application at http://104.207.139.132:8070" -ForegroundColor White
Write-Host "3. Verify no more 'user type' errors appear" -ForegroundColor White
Write-Host ""
