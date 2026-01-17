#!/bin/bash

# Real-time Monitoring Dashboard for Odoo Deployment
# Shows live progress of installation and system metrics

COMMISSION_AX_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax"
LOG_FILE="/tmp/deal_tracking_install_*.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

while true; do
    clear
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  REAL-TIME DEPLOYMENT MONITORING DASHBOARD${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # System Status
    echo -e "${BLUE}SYSTEM STATUS:${NC}"
    echo -n "  Odoo Service: "
    if systemctl is-active --quiet odoo; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Stopped${NC}"
    fi
    
    echo -n "  PostgreSQL:   "
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Stopped${NC}"
    fi
    
    echo ""
    
    # Files Status
    echo -e "${BLUE}DEPLOYED FILES:${NC}"
    
    FILES=(
        "models/sale_order_deal_tracking_ext.py"
        "models/account_move_deal_tracking_ext.py"
        "views/sale_order_deal_tracking_views.xml"
        "views/account_move_deal_tracking_views.xml"
    )
    
    for file in "${FILES[@]}"; do
        echo -n "  $file: "
        if [ -f "$COMMISSION_AX_PATH/$file" ]; then
            SIZE=$(du -h "$COMMISSION_AX_PATH/$file" | cut -f1)
            echo -e "${GREEN}✓${NC} ($SIZE)"
        else
            echo -e "${RED}✗${NC}"
        fi
    done
    
    echo ""
    
    # Configuration Status
    echo -e "${BLUE}CONFIGURATION:${NC}"
    
    echo -n "  __manifest__.py updated: "
    if grep -q "sale_order_deal_tracking_views.xml" "$COMMISSION_AX_PATH/__manifest__.py" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}?${NC}"
    fi
    
    echo -n "  models/__init__.py updated: "
    if grep -q "sale_order_deal_tracking_ext" "$COMMISSION_AX_PATH/models/__init__.py" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}?${NC}"
    fi
    
    echo ""
    
    # Log Analysis
    echo -e "${BLUE}RECENT LOG ACTIVITY:${NC}"
    
    LATEST_LOG=$(ls -t /tmp/deal_tracking_install_*.log 2>/dev/null | head -1)
    
    if [ -n "$LATEST_LOG" ]; then
        echo "  Latest log: $(basename $LATEST_LOG)"
        echo "  Recent entries:"
        tail -5 "$LATEST_LOG" | sed 's/^/    /' | tee -a /dev/stderr
    else
        echo "  No log file found"
    fi
    
    echo ""
    
    # Odoo Startup Status
    echo -e "${BLUE}ODOO STARTUP CHECK:${NC}"
    
    ODOO_LOG="/var/log/odoo/odoo-server.log"
    
    if [ -f "$ODOO_LOG" ]; then
        LINES=$(wc -l < "$ODOO_LOG")
        echo "  Log size: $LINES lines"
        
        ERRORS=$(tail -100 "$ODOO_LOG" 2>/dev/null | grep -i "error" | wc -l)
        WARNINGS=$(tail -100 "$ODOO_LOG" 2>/dev/null | grep -i "warning" | wc -l)
        
        echo "  Errors (last 100 lines):   $ERRORS"
        echo "  Warnings (last 100 lines): $WARNINGS"
        
        if grep -q "commission_ax" "$ODOO_LOG" 2>/dev/null; then
            echo -e "  Commission_ax status: ${GREEN}✓ Detected${NC}"
        fi
    else
        echo "  Odoo log not accessible"
    fi
    
    echo ""
    
    # Database Status
    echo -e "${BLUE}DATABASE STATUS:${NC}"
    
    if psql -l 2>/dev/null | grep -q commission_ax; then
        echo -e "  commission_ax database: ${GREEN}✓ Present${NC}"
        
        TABLES=$(psql -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" commission_ax 2>/dev/null)
        echo "  Tables: $TABLES"
    else
        echo "  commission_ax database: Not found"
    fi
    
    echo ""
    
    # Last Deployment Event
    echo -e "${BLUE}TIMELINE:${NC}"
    
    if [ -n "$LATEST_LOG" ]; then
        START_TIME=$(head -1 "$LATEST_LOG" | grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' 2>/dev/null || echo "N/A")
        LAST_TIME=$(tail -1 "$LATEST_LOG" | grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' 2>/dev/null || echo "N/A")
        
        echo "  Deployment started: $START_TIME"
        echo "  Last activity:      $LAST_TIME"
    fi
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo "  Press Ctrl+C to exit | Refreshing in 10 seconds..."
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    
    sleep 10
done
