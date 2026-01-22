#!/bin/bash
echo "================================================================================"
echo "OSUSPROPERTIES SERVICE VERIFICATION REPORT"
echo "================================================================================"
echo ""

echo "Service Status:"
systemctl is-active odoo-osusproperties
echo ""

echo "Service Running Time:"
systemctl show odoo-osusproperties --property=ActiveEnterTimestamp --no-pager
echo ""

echo "Recent Errors (last 200 lines):"
tail -200 /var/odoo/osusproperties/logs/odoo-server.log | grep -c ERROR
echo ""

echo "Recent Critical Errors (last 200 lines):"
tail -200 /var/odoo/osusproperties/logs/odoo-server.log | grep -c CRITICAL
echo ""

echo "User Type Errors (last 200 lines):"
tail -200 /var/odoo/osusproperties/logs/odoo-server.log | grep -ic "user type"
echo ""

echo "Translation Errors (last 200 lines):"
tail -200 /var/odoo/osusproperties/logs/odoo-server.log | grep -ic "ar_001"
echo ""

echo "Registry Status:"
tail -50 /var/odoo/osusproperties/logs/odoo-server.log | grep -i "registry"
echo ""

echo "Port 8070 Status:"
netstat -tlnp 2>/dev/null | grep 8070 || ss -tlnp 2>/dev/null | grep 8070
echo ""

echo "HTTP Response:"
curl -I -s http://localhost:8070 | head -3
echo ""

echo "================================================================================"
echo "VERIFICATION COMPLETE"
echo "================================================================================"
