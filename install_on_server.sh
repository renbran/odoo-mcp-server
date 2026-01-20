#!/bin/bash
# Automated Installation Script for invoice_status_tags
# Generated: 2026-01-19 18:18:37

set -e  # Exit on error

echo "=================================="
echo "Invoice Status Tags Installation"
echo "=================================="

# Variables
MODULE_NAME="invoice_status_tags"
TARGET_PATH="/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/$MODULE_NAME"
PYTHON="/var/odoo/osusproperties/venv/bin/python3"
ODOO_BIN="/var/odoo/osusproperties/src/odoo-bin"
CONFIG="/var/odoo/osusproperties/odoo.conf"
DB="osusproperties"

echo ""
echo "Step 1: Setting permissions..."
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/
sudo chown -R odoo:odoo $MODULE_NAME
sudo chmod -R 755 $MODULE_NAME
sudo find $MODULE_NAME -type f -exec chmod 644 {} \;
echo "Permissions set"

echo ""
echo "Step 2: Updating module list..."
cd /var/odoo/osusproperties
sudo -u odoo $PYTHON $ODOO_BIN \
    -c $CONFIG \
    --no-http \
    --stop-after-init \
    --update-list
echo "Module list updated"

echo ""
echo "Step 3: Installing module..."
sudo -u odoo $PYTHON $ODOO_BIN \
    -c $CONFIG \
    --no-http \
    --stop-after-init \
    -i $MODULE_NAME \
    -d $DB
echo "Module installed"

echo ""
echo "Step 4: Restarting Odoo service..."
sudo systemctl restart odoo
echo "Odoo restarted"

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next: Run Python script to update all records"
echo "  python update_all_records_after_install.py"
