#!/bin/bash
# CloudPepper Module Installation Commands
# Run on server after uploading module files


# Connect to CloudPepper server via SSH
ssh user@your-server

# Set proper ownership and permissions
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/
sudo chown -R odoo:odoo invoice_status_tags
sudo chmod -R 755 invoice_status_tags
sudo find invoice_status_tags -type f -exec chmod 644 {} \;

# Update module list
cd /var/odoo/osusproperties
sudo -u odoo /var/odoo/osusproperties/venv/bin/python3 /var/odoo/osusproperties/src/odoo-bin \
    -c /var/odoo/osusproperties/odoo.conf \
    --no-http \
    --stop-after-init \
    --update-list

# Install the module
sudo -u odoo /var/odoo/osusproperties/venv/bin/python3 /var/odoo/osusproperties/src/odoo-bin \
    -c /var/odoo/osusproperties/odoo.conf \
    --no-http \
    --stop-after-init \
    -i invoice_status_tags \
    -d osusproperties

# Restart Odoo service
sudo systemctl restart odoo
    