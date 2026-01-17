# Odoo 17 Deal Report Module - Testing Guide

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "ODOO 17 DEAL REPORT MODULE TEST GUIDE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✓ Containers Status:" -ForegroundColor Green
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
docker ps --filter "name=odoo17" --format "table {{.Names}}\t{{.Status}}"

Write-Host ""
Write-Host "Step 1: Access Odoo" -ForegroundColor Yellow
Write-Host "  URL: http://localhost:8069" -ForegroundColor White
Write-Host "  Open this URL in your browser now" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 2: Create Database" -ForegroundColor Yellow
Write-Host "  When you see the database selector, click 'Create Database'" -ForegroundColor White
Write-Host "  Fill in:" -ForegroundColor Gray
Write-Host "    Database Name: odoo17_test" -ForegroundColor Gray
Write-Host "    Email: admin@example.com" -ForegroundColor Gray
Write-Host "    Password: admin" -ForegroundColor Gray
Write-Host "    Language: English" -ForegroundColor Gray
Write-Host "    Load demo data: ✓ (checked)" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 3: Install Deal Report Module" -ForegroundColor Yellow
Write-Host "  1. After login, open Apps menu" -ForegroundColor White
Write-Host "  2. Click 'Update Apps List' (or search icon)" -ForegroundColor White
Write-Host "  3. Search: 'deal report'" -ForegroundColor White
Write-Host "  4. Click on 'Deal Report & Commissions'" -ForegroundColor White
Write-Host "  5. Click 'Install'" -ForegroundColor White
Write-Host ""
Write-Host "  The module will also install dependencies:" -ForegroundColor Gray
Write-Host "    - Sale Management" -ForegroundColor Gray
Write-Host "    - Invoicing/Accounting" -ForegroundColor Gray
Write-Host "    - Mail (Chatter)" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 4: Test Module Features" -ForegroundColor Yellow
Write-Host ""
Write-Host "  A. Create a Deal Report:" -ForegroundColor White
Write-Host "     1. Sales → Deals → Deal Reports" -ForegroundColor Gray
Write-Host "     2. Create button" -ForegroundColor Gray
Write-Host "     3. Select a Sale Order" -ForegroundColor Gray
Write-Host "     4. Save" -ForegroundColor Gray
Write-Host ""

Write-Host "  B. Test Workflow:" -ForegroundColor White
Write-Host "     1. Click 'Confirm' button" -ForegroundColor Gray
Write-Host "     2. Click 'Generate Commissions'" -ForegroundColor Gray
Write-Host "     3. Toggle 'Auto Post Invoice' in Billing section" -ForegroundColor Gray
Write-Host "     4. Click 'Process Bills'" -ForegroundColor Gray
Write-Host "     5. Click 'Invoices' smart button to view generated invoice" -ForegroundColor Gray
Write-Host ""

Write-Host "  C. Test Dashboard:" -ForegroundColor White
Write-Host "     1. Sales → Deals → Deal Dashboard" -ForegroundColor White
Write-Host "     2. Select period (This Month, Last Month, etc.)" -ForegroundColor Gray
Write-Host "     3. Click 'Refresh'" -ForegroundColor Gray
Write-Host "     4. Verify KPI score cards display" -ForegroundColor Gray
Write-Host "     5. Click 'Open Analytics'" -ForegroundColor Gray
Write-Host ""

Write-Host "  D. Test Analytics Views:" -ForegroundColor White
Write-Host "     1. Sales → Deals → Analytics → Overview" -ForegroundColor Gray
Write-Host "        - See bar chart of monthly totals" -ForegroundColor Gray
Write-Host "        - See pivot table breakdown by customer/state" -ForegroundColor Gray
Write-Host "        - See kanban cards with status badges" -ForegroundColor Gray
Write-Host ""
Write-Host "     2. Sales → Deals → Analytics → Trends" -ForegroundColor Gray
Write-Host "        - See line chart showing commission trends" -ForegroundColor Gray
Write-Host ""
Write-Host "     3. Sales → Deals → Analytics → Distribution" -ForegroundColor Gray
Write-Host "        - See pie chart of deal distribution by state" -ForegroundColor Gray
Write-Host ""

Write-Host "  E. Test Filters:" -ForegroundColor White
Write-Host "     1. Go to any Deal Reports list view" -ForegroundColor Gray
Write-Host "     2. Use search bar to apply filters:" -ForegroundColor Gray
Write-Host "        - Status: Draft, Confirmed, Commissioned, Billed" -ForegroundColor Gray
Write-Host "        - Period: This Month, Last Month, Last 90 Days" -ForegroundColor Gray
Write-Host "        - Amount: High Value (>100k), Medium, Low" -ForegroundColor Gray
Write-Host "        - Commission: High (>5%), Standard (3-5%), Low (<3%)" -ForegroundColor Gray
Write-Host "        - Billing: Has Invoices, No Invoices" -ForegroundColor Gray
Write-Host "     3. Use Group By for: State, Customer, Month, Year, Salesperson" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 5: Verify All Features Work" -ForegroundColor Yellow
Write-Host "  ✓ Create deal report" -ForegroundColor Gray
Write-Host "  ✓ Workflow buttons work" -ForegroundColor Gray
Write-Host "  ✓ Commission lines generate" -ForegroundColor Gray
Write-Host "  ✓ Invoices create and auto-post" -ForegroundColor Gray
Write-Host "  ✓ Dashboard KPIs calculate" -ForegroundColor Gray
Write-Host "  ✓ Charts render (bar, line, pie)" -ForegroundColor Gray
Write-Host "  ✓ Filters work correctly" -ForegroundColor Gray
Write-Host "  ✓ Search and Group By function" -ForegroundColor Gray
Write-Host "  ✓ Kanban status badges display" -ForegroundColor Gray
Write-Host "  ✓ Chatter tracks changes" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 6: Common Issues & Solutions" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Issue: Can't create database" -ForegroundColor Red
Write-Host "  Solution: Check PostgreSQL is running:" -ForegroundColor Gray
Write-Host "    docker ps | findstr postgres" -ForegroundColor Gray
Write-Host ""

Write-Host "  Issue: Module not appearing in Apps" -ForegroundColor Red
Write-Host "  Solution: Restart Odoo:" -ForegroundColor Gray
Write-Host "    docker restart odoo17_app" -ForegroundColor Gray
Write-Host "    Wait 30 seconds, refresh browser" -ForegroundColor Gray
Write-Host ""

Write-Host "  Issue: Charts not rendering" -ForegroundColor Red
Write-Host "  Solution: Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor Gray
Write-Host "    Then refresh page (F5)" -ForegroundColor Gray
Write-Host ""

Write-Host "  Issue: Buttons not working" -ForegroundColor Red
Write-Host "  Solution: Check browser console (F12)" -ForegroundColor Gray
Write-Host "    Look for error messages" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 7: Useful Docker Commands" -ForegroundColor Yellow
Write-Host ""
Write-Host "  View Odoo logs:" -ForegroundColor Gray
Write-Host "    docker logs odoo17_app -f" -ForegroundColor Gray
Write-Host ""
Write-Host "  Stop environment:" -ForegroundColor Gray
Write-Host "    docker compose stop" -ForegroundColor Gray
Write-Host ""
Write-Host "  Restart after code changes:" -ForegroundColor Gray
Write-Host "    docker compose restart odoo" -ForegroundColor Gray
Write-Host ""
Write-Host "  Access database directly:" -ForegroundColor Gray
Write-Host "    docker exec -it odoo17_postgres psql -U odoo -d odoo17_test" -ForegroundColor Gray
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Ready to test! Visit http://localhost:8069" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
