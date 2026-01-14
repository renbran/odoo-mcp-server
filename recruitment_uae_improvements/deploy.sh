#!/bin/bash

# Recruitment UAE Module - Deployment Script
# Server: eigermarvelhr.com
# Database: eigermarvel
# Odoo: 18.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REMOTE_USER="admin"
REMOTE_HOST="eigermarvelhr.com"
REMOTE_ODOO_PATH="/var/odoo/eigermarvel/src/recruitment_uae"
BACKUP_DIR="/var/odoo/backups"
DATABASE="eigermarvel"
LOCAL_PATH="d:/01_WORK_PROJECTS/odoo-mcp-server/recruitment_uae_improvements"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Recruitment UAE Module - Deployment Script${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Step 1: Verify local files exist
echo -e "${YELLOW}[1/7] Verifying local files...${NC}"
if [ ! -d "$LOCAL_PATH/models" ]; then
    echo -e "${RED}ERROR: models/ directory not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Local files verified${NC}"
echo ""

# Step 2: Create backup directory on server
echo -e "${YELLOW}[2/7] Creating backup directory on server...${NC}"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/recruitment_uae_upgrade_${BACKUP_DATE}"

ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${BACKUP_PATH}"
echo -e "${GREEN}✓ Backup directory created: ${BACKUP_PATH}${NC}"
echo ""

# Step 3: Backup database
echo -e "${YELLOW}[3/7] Backing up database (this may take a while)...${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "pg_dump ${DATABASE} > ${BACKUP_PATH}/${DATABASE}_backup.sql"
echo -e "${GREEN}✓ Database backed up${NC}"
echo ""

# Step 4: Backup existing module files
echo -e "${YELLOW}[4/7] Backing up existing module files...${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "cp -r ${REMOTE_ODOO_PATH} ${BACKUP_PATH}/recruitment_uae_original"
echo -e "${GREEN}✓ Module files backed up${NC}"
echo ""

# Step 5: Transfer new files
echo -e "${YELLOW}[5/7] Transferring new files to server...${NC}"

# Convert Windows path to Unix-style for WSL/Git Bash
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows Git Bash
    LOCAL_PATH_CONVERTED=$(echo "$LOCAL_PATH" | sed 's|d:|/d|' | sed 's|\\|/|g')
else
    LOCAL_PATH_CONVERTED="$LOCAL_PATH"
fi

# Transfer models
echo "  - Transferring models..."
scp -r "${LOCAL_PATH_CONVERTED}/models/"* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_ODOO_PATH}/models/

# Transfer views
echo "  - Transferring views..."
scp -r "${LOCAL_PATH_CONVERTED}/views/"* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_ODOO_PATH}/views/

# Transfer data
echo "  - Transferring data..."
scp -r "${LOCAL_PATH_CONVERTED}/data/"* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_ODOO_PATH}/data/

# Transfer security
echo "  - Transferring security..."
scp -r "${LOCAL_PATH_CONVERTED}/security/"* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_ODOO_PATH}/security/

echo -e "${GREEN}✓ Files transferred successfully${NC}"
echo ""

# Step 6: Update module
echo -e "${YELLOW}[6/7] Updating module (this may take a while)...${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    # Stop Odoo
    echo "  - Stopping Odoo service..."
    sudo systemctl stop odoo18
    
    # Update module
    echo "  - Running module update..."
    /var/odoo/venv/bin/python3 /var/odoo/odoo18/odoo-bin \
        -c /etc/odoo18.conf \
        -d eigermarvel \
        -u recruitment_uae \
        --stop-after-init
    
    # Start Odoo
    echo "  - Starting Odoo service..."
    sudo systemctl start odoo18
    
    # Wait for service to start
    sleep 5
    
    # Check status
    sudo systemctl status odoo18 --no-pager | head -n 10
EOF
echo -e "${GREEN}✓ Module updated${NC}"
echo ""

# Step 7: Verify deployment
echo -e "${YELLOW}[7/7] Verifying deployment...${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    # Check if service is running
    if systemctl is-active --quiet odoo18; then
        echo "  ✓ Odoo service is running"
    else
        echo "  ✗ ERROR: Odoo service not running!"
        exit 1
    fi
    
    # Check recent logs for errors
    echo "  - Checking logs for errors..."
    if tail -n 50 /var/log/odoo/odoo18.log | grep -i "error" | grep -i "recruitment"; then
        echo "  ⚠ Warning: Found errors in logs - please review"
    else
        echo "  ✓ No recruitment-related errors in recent logs"
    fi
EOF
echo -e "${GREEN}✓ Verification complete${NC}"
echo ""

# Summary
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Backup location: ${BACKUP_PATH}"
echo ""
echo -e "Next steps:"
echo -e "  1. Login to https://eigermarvelhr.com"
echo -e "  2. Navigate to Recruitment menu"
echo -e "  3. Verify smart buttons are visible"
echo -e "  4. Test chatter functionality"
echo -e "  5. Check automated emails in Settings > Technical > Email"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC} Monitor logs for the next 24-48 hours:"
echo -e "  ssh ${REMOTE_USER}@${REMOTE_HOST}"
echo -e "  tail -f /var/log/odoo/odoo18.log"
echo ""
echo -e "${YELLOW}If issues occur, rollback with:${NC}"
echo -e "  ssh ${REMOTE_USER}@${REMOTE_HOST}"
echo -e "  sudo systemctl stop odoo18"
echo -e "  sudo -u postgres psql ${DATABASE} < ${BACKUP_PATH}/${DATABASE}_backup.sql"
echo -e "  rm -rf ${REMOTE_ODOO_PATH}"
echo -e "  cp -r ${BACKUP_PATH}/recruitment_uae_original ${REMOTE_ODOO_PATH}"
echo -e "  sudo systemctl start odoo18"
echo ""
echo -e "${GREEN}Deployment script finished!${NC}"
