#!/bin/bash

echo "======================================"
echo "SYNCONICS BI DASHBOARD - DOCKER TEST"
echo "======================================"
echo ""

# Check if module is copied
echo "[1/5] Checking module in Docker..."
docker exec odoo17_test bash -c "ls -la /mnt/extra-addons/synconics_bi_dashboard/ | head -10" || exit 1
echo "✓ Module found in Docker"
echo ""

# Get database info
echo "[2/5] Checking database..."
docker exec odoo17_postgres psql -U odoo postgres -c "\l" 2>/dev/null | grep test_db
echo ""

# Check module manifest
echo "[3/5] Examining module manifest..."
docker exec odoo17_test bash -c "head -50 /mnt/extra-addons/synconics_bi_dashboard/__manifest__.py" | grep -E "(version|depends|assets)" | head -5
echo ""

# Check Docker logs for errors
echo "[4/5] Recent Docker errors (last 20 lines with 'error')..."
docker logs odoo17_test --tail 500 2>&1 | grep -i error | tail -20 || echo "No errors found"
echo ""

# Check module state
echo "[5/5] Module state in database..."
echo "Attempting to query module state..."
docker exec odoo17_postgres psql -U odoo -d postgres -c "SELECT datname FROM pg_database WHERE datname='test_db';" 2>&1 | head -5

echo ""
echo "======================================"
echo "TEST SUMMARY"
echo "======================================"
echo ""
echo "Module Location: ✓ /mnt/extra-addons/synconics_bi_dashboard"
echo "Module Size: $(docker exec odoo17_test bash -c 'du -sh /mnt/extra-addons/synconics_bi_dashboard' 2>/dev/null || echo 'Unknown')"
echo "Docker Container: odoo17_test (Odoo 17.0)"
echo ""
echo "Next Steps:"
echo "1. Manually install via Odoo UI at http://localhost:8069"
echo "2. Monitor Docker logs: docker logs -f odoo17_test"
echo "3. Check browser console for JavaScript errors"
echo "4. Expected error: TypeError in asset bundle compilation"
echo ""

