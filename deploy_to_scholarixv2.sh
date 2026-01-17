#!/bin/bash
# Quick deployment script for deals_management module to scholarixv2
# Run this from the project root directory

set -e  # Exit on error

echo "========================================"
echo "Deals Management - scholarixv2 Deploy"
echo "========================================"
echo ""

# Configuration
REMOTE_HOST="erp.sgctech.ai"
REMOTE_USER="odoo"
REMOTE_ADDONS_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
MODULE_NAME="deals_management"
BACKUP_DIR="/var/odoo/backups"

# Step 1: Validate module locally
echo "📋 Step 1: Validating module structure..."
if [ -f "$MODULE_NAME/validate_module.py" ]; then
    python3 "$MODULE_NAME/validate_module.py" "$MODULE_NAME/"
    if [ $? -ne 0 ]; then
        echo "❌ Module validation failed. Fix errors before deploying."
        exit 1
    fi
else
    echo "⚠️  Warning: validate_module.py not found. Skipping validation."
fi

echo ""
echo "✅ Validation passed!"
echo ""

# Step 2: Create deployment package
echo "📦 Step 2: Creating deployment package..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="deals_management_${TIMESTAMP}.tar.gz"

tar -czf "$PACKAGE_NAME" "$MODULE_NAME/"
echo "✅ Package created: $PACKAGE_NAME"
echo ""

# Step 3: Upload to server
echo "📤 Step 3: Uploading to server..."
scp "$PACKAGE_NAME" "${REMOTE_USER}@${REMOTE_HOST}:/tmp/"
if [ $? -eq 0 ]; then
    echo "✅ Upload successful"
else
    echo "❌ Upload failed"
    exit 1
fi
echo ""

# Step 4: Deploy on remote server
echo "🚀 Step 4: Deploying on remote server..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
set -e

echo "Creating backup of existing module..."
sudo tar -czf ${BACKUP_DIR}/deals_management_backup_${TIMESTAMP}.tar.gz \
    ${REMOTE_ADDONS_PATH}/${MODULE_NAME} 2>/dev/null || echo "No existing module to backup"

echo "Removing old module..."
sudo rm -rf ${REMOTE_ADDONS_PATH}/${MODULE_NAME}

echo "Extracting new module..."
cd ${REMOTE_ADDONS_PATH}
sudo tar -xzf /tmp/${PACKAGE_NAME}

echo "Setting permissions..."
sudo chown -R odoo:odoo ${MODULE_NAME}
sudo chmod -R 755 ${MODULE_NAME}

echo "Validating deployed module..."
python3 ${MODULE_NAME}/validate_module.py ${MODULE_NAME}/

echo "Restarting Odoo..."
sudo systemctl restart odoo

echo "Checking Odoo status..."
sleep 3
sudo systemctl status odoo --no-pager -l

echo "Cleaning up..."
rm /tmp/${PACKAGE_NAME}

echo ""
echo "✅ Deployment complete!"
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Remote deployment successful!"
else
    echo ""
    echo "❌ Remote deployment failed"
    exit 1
fi

# Step 5: Cleanup local package
echo ""
echo "🧹 Step 5: Cleaning up local files..."
rm "$PACKAGE_NAME"
echo "✅ Cleanup complete"

# Final instructions
echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Login to https://${REMOTE_HOST}"
echo "2. Navigate to Apps menu"
echo "3. Click 'Update Apps List'"
echo "4. Search for 'Deals Management'"
echo "5. Click 'Install' (or 'Upgrade' if already installed)"
echo "6. Verify menus appear after installation"
echo ""
echo "For detailed verification steps, see SCHOLARIXV2_DEPLOYMENT_GUIDE.md"
echo ""
