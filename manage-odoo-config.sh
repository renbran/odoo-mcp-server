#!/bin/bash
# ==============================================================================
# Odoo Configuration Manager - Switch between normal and verbose modes
# ==============================================================================

set -e

CONFIG_PATH="/var/odoo/osusproperties"
NORMAL_CONFIG="odoo.conf"
VERBOSE_CONFIG="odoo-verbose.conf"
BACKUP_SUFFIX=".backup_$(date +%Y%m%d_%H%M%S)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root"
    exit 1
fi

# Main menu
show_menu() {
    print_header "Odoo Configuration Manager"
    echo ""
    echo "1) Enable VERBOSE mode (for module updates)"
    echo "2) Enable NORMAL mode (production)"
    echo "3) View current configuration"
    echo "4) View verbose log example"
    echo "5) Show how to monitor updates"
    echo "6) Exit"
    echo ""
    read -p "Select option (1-6): " choice
}

enable_verbose() {
    print_header "Enabling VERBOSE Mode"
    
    # Backup current config
    if [ ! -f "$CONFIG_PATH/$NORMAL_CONFIG.original" ]; then
        cp "$CONFIG_PATH/$NORMAL_CONFIG" "$CONFIG_PATH/$NORMAL_CONFIG.original"
        print_success "Created original backup"
    fi
    
    # Copy verbose config
    cp "$CONFIG_PATH/$VERBOSE_CONFIG" "$CONFIG_PATH/$NORMAL_CONFIG"
    print_success "Switched to verbose configuration"
    
    # Restart service
    print_info "Restarting Odoo service..."
    systemctl restart odoo-osusproperties
    sleep 5
    
    if systemctl is-active --quiet odoo-osusproperties; then
        print_success "Service restarted successfully"
        echo ""
        echo "📝 Next step: Open another terminal and run:"
        echo "   journalctl -u odoo-osusproperties -f"
        echo ""
        echo "💡 Then trigger module update from web interface or:"
        echo "   cd $CONFIG_PATH"
        echo "   ./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf"
    else
        print_error "Service failed to start"
        restore_normal
        exit 1
    fi
}

enable_normal() {
    print_header "Enabling NORMAL Mode"
    
    if [ ! -f "$CONFIG_PATH/$NORMAL_CONFIG.original" ]; then
        print_error "Original config backup not found"
        exit 1
    fi
    
    cp "$CONFIG_PATH/$NORMAL_CONFIG.original" "$CONFIG_PATH/$NORMAL_CONFIG"
    print_success "Switched back to normal configuration"
    
    print_info "Restarting Odoo service..."
    systemctl restart odoo-osusproperties
    sleep 5
    
    if systemctl is-active --quiet odoo-osusproperties; then
        print_success "Service restarted successfully"
    else
        print_error "Service failed to start"
        exit 1
    fi
}

view_config() {
    print_header "Current Configuration"
    echo ""
    echo "🔍 Active config file:"
    ls -lah $CONFIG_PATH/$NORMAL_CONFIG
    echo ""
    echo "📝 Current log level:"
    grep -E "^log_level" $CONFIG_PATH/$NORMAL_CONFIG || echo "Not set"
    echo ""
    echo "📝 Current log handlers:"
    grep -E "^log_handler" $CONFIG_PATH/$NORMAL_CONFIG || echo "None configured"
    echo ""
    echo "📁 Available configs:"
    ls -lah $CONFIG_PATH/$NORMAL_CONFIG* | grep -E "(normal|verbose|conf)" || echo "Not found"
}

show_verbose_example() {
    print_header "Example Verbose Output"
    echo ""
    echo "When running with verbose mode, you'll see output like:"
    echo ""
    cat << 'EXAMPLE'
2026-01-19 22:25:00,123 1234567 DEBUG odoo.modules.loading: Loading module osus_sales_invoicing_dashboard
2026-01-19 22:25:00,124 1234567 DEBUG odoo.modules: Initializing osus_sales_invoicing_dashboard
2026-01-19 22:25:00,125 1234567 DEBUG odoo.addons: Resolving dependencies
2026-01-19 22:25:00,200 1234567 INFO odoo.modules.loading: Modules to install ['osus_sales_invoicing_dashboard']
2026-01-19 22:25:00,300 1234567 DEBUG odoo.addons.base.ir_model: Computing fields for osus.sales.invoicing.dashboard
2026-01-19 22:25:00,400 1234567 DEBUG odoo.tools.xml: Loading XML file dashboard_views.xml
2026-01-19 22:25:00,500 1234567 DEBUG odoo.tools.xml: Processing record sales_invoicing_dashboard_view_form
2026-01-19 22:25:00,600 1234567 DEBUG odoo.tools.convert: Updating ir.ui.view with 1 changes
2026-01-19 22:25:00,700 1234567 DEBUG odoo.addons.ir_model: Applying field updates
2026-01-19 22:25:00,800 1234567 DEBUG odoo.addons.ir_rule: Creating security rules
2026-01-19 22:25:00,900 1234567 DEBUG odoo.addons.web: Compiling assets
2026-01-19 22:25:01,000 1234567 DEBUG odoo.addons.web: CSS files compiled: dashboard_modern.scss → dashboard_modern.css
2026-01-19 22:25:01,100 1234567 DEBUG odoo.addons.web: JavaScript bundles compiled
2026-01-19 22:25:01,200 1234567 INFO odoo.modules.loading: Module loaded successfully!
EXAMPLE
    echo ""
    print_info "This shows every step being executed"
}

show_monitoring() {
    print_header "How to Monitor Module Updates"
    echo ""
    echo "📺 TERMINAL 1 - Watch the logs in real-time:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$ ssh root@139.84.163.11"
    echo "$ journalctl -u odoo-osusproperties -f"
    echo ""
    echo "📺 TERMINAL 2 - Trigger the module update:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$ ssh root@139.84.163.11"
    echo "$ cd /var/odoo/osusproperties"
    echo "$ ./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf"
    echo ""
    echo "OR use web interface:"
    echo "1. Go to https://erposus.com/web/login"
    echo "2. Navigate to: Settings → Apps → Search 'osus_sales_invoicing_dashboard'"
    echo "3. Click 'Upgrade'"
    echo "4. Watch Terminal 1 for detailed output"
    echo ""
    echo "✨ You'll see each step being executed line-by-line!"
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1) enable_verbose ;;
        2) enable_normal ;;
        3) view_config ;;
        4) show_verbose_example ;;
        5) show_monitoring ;;
        6) 
            print_success "Exiting"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
done
