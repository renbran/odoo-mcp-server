#!/bin/bash
# Server Diagnostic Script
# Purpose: Check what's actually deployed on the server and identify issues

echo "========================================================================"
echo "RECRUITMENT UAE - SERVER DIAGNOSTIC"
echo "========================================================================"
echo "Time: $(date)"
echo ""

# Variables
ODOO_PATH="/var/odoo/eigermarvel/extra-addons"
MODULE_PATTERNS=("recruitment_uae" "recruitment-uae" "*recruitment*")
TARGET_FILE="views/application_views.xml"

echo "========================================================================"
echo "1. SEARCHING FOR RECRUITMENT MODULE ON SERVER"
echo "========================================================================"

# Find all potential recruitment modules
echo "Searching for recruitment modules in: $ODOO_PATH"
echo ""

for module_pattern in "${MODULE_PATTERNS[@]}"; do
    echo "Looking for: $module_pattern"
    find "$ODOO_PATH" -maxdepth 2 -type d -name "*${module_pattern}*" 2>/dev/null | while read module_dir; do
        echo "  ✓ Found: $module_dir"
        
        # Check if this is a valid module
        if [ -f "$module_dir/__init__.py" ] || [ -f "$module_dir/__manifest__.py" ]; then
            echo "    → Valid module (has __init__.py or __manifest__.py)"
            
            # Check for application_views.xml
            if [ -f "$module_dir/$TARGET_FILE" ]; then
                echo "    → File exists: $TARGET_FILE"
                echo ""
                echo "    First 30 lines of $TARGET_FILE:"
                echo "    ─────────────────────────────────────"
                head -30 "$module_dir/$TARGET_FILE" | sed 's/^/    /'
                echo ""
                echo "    Line 25 specifically:"
                sed -n '25p' "$module_dir/$TARGET_FILE" | sed 's/^/    /'
                echo ""
                
                # Check file encoding
                echo "    File encoding: $(file -b "$module_dir/$TARGET_FILE")"
                echo ""
                
                # Check for XML validity on server
                echo "    Testing XML validity..."
                python3 << 'PYEOF'
import sys
import xml.etree.ElementTree as ET

try:
    ET.parse('$module_dir/$TARGET_FILE')
    print("    ✓ XML is valid (Python ElementTree)")
except ET.ParseError as e:
    print(f"    ✗ XML Parse Error: {e}")
    print(f"      Line {e.position[0]}, Column {e.position[1]}")
PYEOF
                echo ""
            else
                echo "    ⚠ File NOT FOUND: $TARGET_FILE"
            fi
        fi
    done
    echo ""
done

echo "========================================================================"
echo "2. CHECKING FOR CONFLICTING MODULES"
echo "========================================================================"

find "$ODOO_PATH" -maxdepth 2 -type d -name "*recruitment*" 2>/dev/null | nl

echo ""
echo "========================================================================"
echo "3. CHECKING ODOO MODULE REGISTRY"
echo "========================================================================"

# Try to check manifest files
find "$ODOO_PATH" -maxdepth 2 -name "__manifest__.py" | xargs grep -l "recruitment_uae\|recruitment" 2>/dev/null | head -10

echo ""
echo "========================================================================"
echo "4. CHECKING FOR DUPLICATE/CONFLICTING FILES"
echo "========================================================================"

find "$ODOO_PATH" -name "application_views.xml" 2>/dev/null | nl

echo ""
echo "========================================================================"
echo "5. ODOO LOG ANALYSIS"
echo "========================================================================"

echo "Recent XML/Parse errors in Odoo logs (last 50 lines):"
tail -50 /var/log/odoo/odoo.log 2>/dev/null | grep -i "xml\|parse\|recruitment" || echo "No errors found or logs not accessible"

echo ""
echo "========================================================================"
echo "END OF DIAGNOSTIC"
echo "========================================================================"
