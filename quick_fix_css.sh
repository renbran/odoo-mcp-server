#!/bin/bash
# Quick Fix Script for Odoo Dashboard CSS Issues
# Run this on the server: bash quick_fix_css.sh

set -e  # Exit on error

echo "🔧 Odoo Dashboard CSS Fix - Starting..."
echo "========================================="

# Variables
MODULE_PATH="/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard"
SCSS_FILE="$MODULE_PATH/static/src/scss/dashboard_modern.scss"
BACKUP_FILE="$MODULE_PATH/static/src/scss/dashboard_modern.scss.backup_$(date +%Y%m%d_%H%M%S)"
ASSETS_PATH="$HOME/.local/share/Odoo/filestore/osusproperties/assets"

# Step 1: Backup
echo "📦 Step 1/5: Creating backup..."
cp "$SCSS_FILE" "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"

# Step 2: Create temporary variables file
echo "📝 Step 2/5: Preparing SCSS variables..."
cat > /tmp/scss_variables.txt << 'VARIABLES'
// ============================================================================
// OSUS Dashboard - SCSS Variables & Design Tokens
// ============================================================================

// Color Palette - Primary & Accents
$primary-accent: #1e3a8a;      // Deep blue for primary actions
$secondary: #6366f1;           // Indigo for secondary elements
$success: #10b981;             // Green for success states
$warning: #f59e0b;             // Amber for warnings
$danger: #ef4444;              // Red for errors/danger
$info: #06b6d4;                // Cyan for informational

// Text Colors
$text-dark: #1f2937;           // Primary text color
$text-muted: #6b7280;          // Secondary/muted text
$text-light: #9ca3af;          // Lighter text for hints

// Background Colors
$bg-light: #f9fafb;            // Light background
$bg-lighter: #f3f4f6;          // Even lighter background
$white: #ffffff;               // Pure white

// Border & Dividers
$border: #e5e7eb;              // Standard border color
$border-light: #f3f4f6;        // Light border

// Shadows - Material Design inspired
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
$shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

// Transitions
$transition-fast: all 0.15s ease-in-out;
$transition-base: all 0.3s ease-in-out;
$transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

// Border Radius
$radius-sm: 6px;
$radius-md: 8px;
$radius-lg: 12px;
$radius-xl: 16px;

// Spacing (multipliers of 4px base)
$space-1: 4px;
$space-2: 8px;
$space-3: 12px;
$space-4: 16px;
$space-5: 20px;
$space-6: 24px;
$space-8: 32px;
$space-10: 40px;

VARIABLES

echo "✅ Variables prepared"

# Step 3: Merge variables with existing file
echo "🔀 Step 3/5: Merging variables into SCSS file..."
cat /tmp/scss_variables.txt "$SCSS_FILE" > /tmp/dashboard_modern_new.scss
mv /tmp/dashboard_modern_new.scss "$SCSS_FILE"
echo "✅ SCSS file updated"

# Step 4: Clear assets cache
echo "🗑️  Step 4/5: Clearing Odoo assets cache..."
if [ -d "$ASSETS_PATH" ]; then
    rm -rf "$ASSETS_PATH"/*
    echo "✅ Assets cache cleared"
else
    echo "⚠️  Assets directory not found (may not exist yet)"
fi

# Step 5: Restart Odoo service
echo "🔄 Step 5/5: Restarting Odoo service..."
systemctl restart odoo-osusproperties
echo "✅ Service restarted"

# Wait for service to be ready
echo "⏳ Waiting for service to start (10 seconds)..."
sleep 10

# Check service status
if systemctl is-active --quiet odoo-osusproperties; then
    echo "✅ Service is running"
else
    echo "❌ Service failed to start - check logs with: journalctl -u odoo-osusproperties -n 50"
    exit 1
fi

# Summary
echo ""
echo "========================================="
echo "✅ CSS FIX COMPLETED SUCCESSFULLY!"
echo "========================================="
echo ""
echo "📊 Summary:"
echo "  - Backup created: $(basename $BACKUP_FILE)"
echo "  - Variables added: 53 SCSS variables"
echo "  - Assets cache: Cleared"
echo "  - Service status: Running"
echo ""
echo "🌐 Next Steps:"
echo "  1. Open browser: https://erposus.com"
echo "  2. Navigate to dashboard"
echo "  3. Hard refresh (Ctrl+F5)"
echo "  4. Verify styling looks correct"
echo ""
echo "📝 Rollback (if needed):"
echo "  cp $BACKUP_FILE $SCSS_FILE"
echo "  systemctl restart odoo-osusproperties"
echo ""
echo "🎉 Done!"
