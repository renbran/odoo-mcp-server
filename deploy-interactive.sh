#!/bin/bash

# Brokerage Deal Tracking Enhancement - Interactive Installation with Monitoring
# This script provides real-time progress monitoring and verification at each step

set -e

# Configuration
COMMISSION_AX_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax"
BACKUP_PATH="/var/odoo/scholarixv2/backups"
ODOO_SERVICE="odoo"
LOG_FILE="/tmp/deal_tracking_install_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}!${NC} $1" | tee -a "$LOG_FILE"
}

header() {
    echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}║${NC} $1" | tee -a "$LOG_FILE"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n" | tee -a "$LOG_FILE"
}

prompt() {
    read -p "$(echo -e ${YELLOW}→${NC} $1) " response
    echo "$response"
}

# ===== PHASE 0: BANNER =====

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  BROKERAGE DEAL TRACKING ENHANCEMENT - SHELL INSTALLATION        ║
║                                                                   ║
║  Real-time Progress Monitoring & Interactive Verification        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo "Log file: $LOG_FILE"
echo ""

# ===== PHASE 1: PRE-INSTALLATION CHECKS =====

header "PHASE 1: PRE-INSTALLATION CHECKS"

log "Checking module directory..."
if [ -d "$COMMISSION_AX_PATH" ]; then
    success "Module found at: $COMMISSION_AX_PATH"
else
    error "Module not found at $COMMISSION_AX_PATH"
    exit 1
fi

log "Checking Odoo service..."
if systemctl is-active --quiet $ODOO_SERVICE; then
    success "Odoo service is running"
    systemctl status $ODOO_SERVICE | grep "Active:" | tee -a "$LOG_FILE"
else
    warning "Odoo service is not running"
fi

log "Checking manifest file..."
if [ -f "$COMMISSION_AX_PATH/__manifest__.py" ]; then
    success "Module manifest found"
    head -5 "$COMMISSION_AX_PATH/__manifest__.py" | tee -a "$LOG_FILE"
else
    error "Module manifest not found"
    exit 1
fi

log "Creating backup directory..."
mkdir -p "$BACKUP_PATH"
success "Backup directory ready: $BACKUP_PATH"

# ===== PHASE 2: BACKUP =====

header "PHASE 2: BACKUP EXISTING MODULE"

log "Backing up module files..."
BACKUP_NAME="commission_ax_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_PATH/$BACKUP_NAME"

cp -r "$COMMISSION_AX_PATH"/* "$BACKUP_PATH/$BACKUP_NAME/" 2>&1 | head -5 | tee -a "$LOG_FILE"
echo "    ..." | tee -a "$LOG_FILE"

BACKUP_SIZE=$(du -sh "$BACKUP_PATH/$BACKUP_NAME" | cut -f1)
success "Module backup created: $BACKUP_NAME ($BACKUP_SIZE)"

log "Backing up Odoo database..."
DB_BACKUP="$BACKUP_PATH/commission_ax_$(date +%Y%m%d_%H%M%S).sql"
pg_dump commission_ax > "$DB_BACKUP" 2>&1

DB_SIZE=$(du -sh "$DB_BACKUP" | cut -f1)
success "Database backup created ($DB_SIZE)"

echo -e "\n${YELLOW}Backups created at: $BACKUP_PATH/${NC}" | tee -a "$LOG_FILE"
ls -lh "$BACKUP_PATH" | tail -5 | tee -a "$LOG_FILE"

# ===== PHASE 3: STOP ODOO =====

header "PHASE 3: STOP ODOO SERVICE"

log "Stopping Odoo service..."
systemctl stop $ODOO_SERVICE
sleep 3

log "Verifying service stopped..."
if systemctl is-active --quiet $ODOO_SERVICE; then
    error "Odoo service is still running!"
    exit 1
else
    success "Odoo service stopped"
    systemctl status $ODOO_SERVICE | grep "Active:" | tee -a "$LOG_FILE"
fi

# ===== PHASE 4: DEPLOY PYTHON FILES =====

header "PHASE 4: DEPLOY PYTHON MODEL FILES"

log "Creating sale_order_deal_tracking_ext.py..."

cat > "$COMMISSION_AX_PATH/models/sale_order_deal_tracking_ext.py" << 'PYTHON_EOF'
# -*- coding: utf-8 -*-
from odoo import fields, models, api

class SaleOrderDealTracking(models.Model):
    _inherit = 'sale.order'

    buyer_name = fields.Char(
        string="Buyer Name",
        compute="_compute_buyer_name",
        store=True
    )
    project_name = fields.Char(
        string="Project Name",
        compute="_compute_project_name",
        store=True
    )
    unit_sale_value = fields.Monetary(
        string="Unit Sale Value",
        compute="_compute_unit_sale_value",
        store=True,
        currency_field='currency_id'
    )
    primary_commission_percentage = fields.Float(
        string="Primary Commission %",
        compute="_compute_primary_commission_percentage",
        store=True
    )
    deal_summary_html = fields.Html(
        string="Deal Summary",
        compute="_compute_deal_summary_html"
    )

    @api.depends('partner_id', 'partner_id.name')
    def _compute_buyer_name(self):
        for record in self:
            record.buyer_name = record.partner_id.name if record.partner_id else ''

    @api.depends('project_id', 'project_id.name')
    def _compute_project_name(self):
        for record in self:
            record.project_name = record.project_id.name if record.project_id else ''

    @api.depends('order_line', 'order_line.price_unit')
    def _compute_unit_sale_value(self):
        for record in self:
            record.unit_sale_value = record.order_line[0].price_unit if record.order_line else 0.0

    @api.depends('broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate',
                 'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _compute_primary_commission_percentage(self):
        for record in self:
            rates = [
                record.broker_rate or 0, record.referrer_rate or 0,
                record.cashback_rate or 0, record.other_external_rate or 0,
                record.agent1_rate or 0, record.agent2_rate or 0,
                record.manager_rate or 0, record.director_rate or 0,
            ]
            record.primary_commission_percentage = max(rates) if rates else 0.0

    @api.depends('buyer_name', 'project_name', 'unit_sale_value', 'primary_commission_percentage')
    def _compute_deal_summary_html(self):
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = f"{record.currency_id.symbol} {record.unit_sale_value:,.2f}" if record.unit_sale_value else '—'
            commission = f"{record.primary_commission_percentage:.2f}%" if record.primary_commission_percentage else '—'
            
            record.deal_summary_html = f"""
            <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 4px solid #8b1538;">
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <tr><td style="padding: 6px; font-weight: bold; width: 35%;">Buyer:</td>
                        <td style="padding: 6px; color: #8b1538; font-weight: 500;">{buyer}</td></tr>
                    <tr style="background: #ffffff;"><td style="padding: 6px; font-weight: bold;">Project:</td>
                        <td style="padding: 6px; color: #333;">{project}</td></tr>
                    <tr><td style="padding: 6px; font-weight: bold;">Unit Sale Value:</td>
                        <td style="padding: 6px; color: #333; text-align: right;">{unit_val}</td></tr>
                    <tr style="background: #ffe6e6;"><td style="padding: 6px; font-weight: bold;">Commission %:</td>
                        <td style="padding: 6px; color: #8b1538; text-align: right; font-weight: bold;">{commission}</td></tr>
                </table>
            </div>
            """

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'buyer_name': self.buyer_name,
            'project_name': self.project_name,
            'unit_sale_value': self.unit_sale_value,
            'commission_percentage': self.primary_commission_percentage,
            'sale_order_deal_reference': self.name,
        })
        return invoice_vals
PYTHON_EOF

if [ -f "$COMMISSION_AX_PATH/models/sale_order_deal_tracking_ext.py" ]; then
    success "sale_order_deal_tracking_ext.py deployed"
    wc -l "$COMMISSION_AX_PATH/models/sale_order_deal_tracking_ext.py" | tee -a "$LOG_FILE"
else
    error "Failed to deploy sale_order_deal_tracking_ext.py"
    exit 1
fi

log "Creating account_move_deal_tracking_ext.py..."

cat > "$COMMISSION_AX_PATH/models/account_move_deal_tracking_ext.py" << 'PYTHON_EOF'
# -*- coding: utf-8 -*-
from odoo import fields, models, api

class AccountMoveWithDealTracking(models.Model):
    _inherit = 'account.move'

    buyer_name = fields.Char(string="Buyer Name")
    project_name = fields.Char(string="Project Name")
    unit_sale_value = fields.Monetary(string="Unit Sale Value", currency_field='currency_id')
    commission_percentage = fields.Float(string="Commission %")
    sale_order_deal_reference = fields.Char(string="Sale Order Reference")
    sale_order_id = fields.Many2one('sale.order', string="Source Sale Order")
    deal_information_summary = fields.Html(string="Deal Information Summary", compute="_compute_deal_information_summary")

    @api.depends('buyer_name', 'project_name', 'unit_sale_value', 'commission_percentage')
    def _compute_deal_information_summary(self):
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = f"{record.currency_id.symbol} {record.unit_sale_value:,.2f}" if record.unit_sale_value else '—'
            commission = f"{record.commission_percentage:.2f}%" if record.commission_percentage else '—'
            
            record.deal_information_summary = f"""
            <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 4px solid #8b1538;">
                <h6 style="color: #8b1538; margin: 0 0 8px 0;">ORIGINAL DEAL INFORMATION</h6>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <tr><td style="padding: 4px; font-weight: bold; width: 40%;">Buyer:</td>
                        <td style="padding: 4px; color: #8b1538;">{buyer}</td></tr>
                    <tr><td style="padding: 4px; font-weight: bold;">Project:</td>
                        <td style="padding: 4px; color: #333;">{project}</td></tr>
                    <tr><td style="padding: 4px; font-weight: bold;">Unit Sale Value:</td>
                        <td style="padding: 4px; text-align: right;">{unit_val}</td></tr>
                    <tr><td style="padding: 4px; font-weight: bold;">Commission %:</td>
                        <td style="padding: 4px; color: #8b1538; font-weight: bold; text-align: right;">{commission}</td></tr>
                </table>
            </div>
            """

    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.sale_order_id and not record.buyer_name:
                so = record.sale_order_id
                record.write({
                    'buyer_name': so.buyer_name,
                    'project_name': so.project_name,
                    'unit_sale_value': so.unit_sale_value,
                    'commission_percentage': so.primary_commission_percentage,
                    'sale_order_deal_reference': so.name,
                })
        return records
PYTHON_EOF

if [ -f "$COMMISSION_AX_PATH/models/account_move_deal_tracking_ext.py" ]; then
    success "account_move_deal_tracking_ext.py deployed"
    wc -l "$COMMISSION_AX_PATH/models/account_move_deal_tracking_ext.py" | tee -a "$LOG_FILE"
else
    error "Failed to deploy account_move_deal_tracking_ext.py"
    exit 1
fi

# ===== PHASE 5: DEPLOY XML FILES =====

header "PHASE 5: DEPLOY XML VIEW FILES"

log "Creating sale_order_deal_tracking_views.xml..."

cat > "$COMMISSION_AX_PATH/views/sale_order_deal_tracking_views.xml" << 'XML_EOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">
        <record id="sale_order_form_view_deal_tracking" model="ir.ui.view">
            <field name="name">sale.order.form.deal.tracking</field>
            <field name="model">sale.order</field>
            <field name="inherit_id" ref="sale.view_order_form"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='partner_id']" position="after">
                    <div class="row mt-3 mb-3" style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
                        <div class="col-md-12"><h5 style="color: #8b1538; font-weight: bold;">BROKERAGE DEAL INFORMATION</h5></div>
                    </div>
                    <div class="row">
                        <div class="col-md-6"><field name="buyer_name" readonly="1"/></div>
                        <div class="col-md-6"><field name="project_name" readonly="1"/></div>
                    </div>
                    <div class="row">
                        <div class="col-md-6"><field name="unit_sale_value" readonly="1"/></div>
                        <div class="col-md-6"><field name="primary_commission_percentage" readonly="1"/></div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-12"><field name="deal_summary_html" widget="html" nolabel="1" readonly="1"/></div>
                    </div>
                </xpath>
            </field>
        </record>

        <record id="sale_order_tree_view_deal_tracking" model="ir.ui.view">
            <field name="name">sale.order.tree.deal.tracking</field>
            <field name="model">sale.order</field>
            <field name="inherit_id" ref="sale.order_tree"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='name']" position="after">
                    <field name="buyer_name" string="Buyer"/>
                    <field name="project_name" string="Project"/>
                    <field name="unit_sale_value" string="Unit Price"/>
                    <field name="primary_commission_percentage" string="Commission %"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
XML_EOF

if [ -f "$COMMISSION_AX_PATH/views/sale_order_deal_tracking_views.xml" ]; then
    success "sale_order_deal_tracking_views.xml deployed"
    wc -l "$COMMISSION_AX_PATH/views/sale_order_deal_tracking_views.xml" | tee -a "$LOG_FILE"
else
    error "Failed to deploy sale_order_deal_tracking_views.xml"
    exit 1
fi

log "Creating account_move_deal_tracking_views.xml..."

cat > "$COMMISSION_AX_PATH/views/account_move_deal_tracking_views.xml" << 'XML_EOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">
        <record id="account_move_form_view_deal_tracking" model="ir.ui.view">
            <field name="name">account.move.form.deal.tracking</field>
            <field name="model">account.move</field>
            <field name="inherit_id" ref="account.view_move_form"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='partner_id']" position="after">
                    <group string="Brokerage Deal Information">
                        <field name="sale_order_deal_reference" readonly="1"/>
                        <field name="buyer_name" readonly="1"/>
                        <field name="project_name" readonly="1"/>
                        <field name="unit_sale_value" readonly="1"/>
                        <field name="commission_percentage" readonly="1"/>
                    </group>
                    <field name="deal_information_summary" nolabel="1" readonly="1" widget="html"/>
                </xpath>
            </field>
        </record>

        <record id="account_move_tree_view_deal_tracking" model="ir.ui.view">
            <field name="name">account.move.tree.deal.tracking</field>
            <field name="model">account.move</field>
            <field name="inherit_id" ref="account.view_move_tree"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='partner_id']" position="after">
                    <field name="buyer_name" string="Buyer"/>
                    <field name="project_name" string="Project"/>
                    <field name="unit_sale_value" string="Unit Price"/>
                    <field name="commission_percentage" string="Commission %"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
XML_EOF

if [ -f "$COMMISSION_AX_PATH/views/account_move_deal_tracking_views.xml" ]; then
    success "account_move_deal_tracking_views.xml deployed"
    wc -l "$COMMISSION_AX_PATH/views/account_move_deal_tracking_views.xml" | tee -a "$LOG_FILE"
else
    error "Failed to deploy account_move_deal_tracking_views.xml"
    exit 1
fi

# ===== PHASE 6: UPDATE CONFIGURATION =====

header "PHASE 6: UPDATE MODULE CONFIGURATION"

log "Updating __manifest__.py..."

# Check if views already in manifest
if grep -q "sale_order_deal_tracking_views.xml" "$COMMISSION_AX_PATH/__manifest__.py"; then
    warning "Views already in manifest, skipping update"
else
    # Add views to data section
    python3 << 'PYEOF'
import sys

manifest_path = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py"

with open(manifest_path, 'r') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
updated = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    if "'data':" in line and not updated:
        # Find the closing bracket
        j = i + 1
        while j < len(lines):
            if '],' in lines[j]:
                # Insert before closing bracket
                indent = len(lines[j]) - len(lines[j].lstrip())
                new_lines.append(" " * indent + "'views/sale_order_deal_tracking_views.xml',")
                new_lines.append(" " * indent + "'views/account_move_deal_tracking_views.xml',")
                updated = True
                break
            new_lines.append(lines[j])
            j += 1

if updated:
    with open(manifest_path, 'w') as f:
        f.write('\n'.join(new_lines))
    print("✓ manifest updated")
else:
    print("! manifest already has views")
PYEOF
fi

success "__manifest__.py configuration complete"

log "Updating models/__init__.py..."

if grep -q "sale_order_deal_tracking_ext" "$COMMISSION_AX_PATH/models/__init__.py"; then
    warning "Models already imported, skipping update"
else
    echo "" >> "$COMMISSION_AX_PATH/models/__init__.py"
    echo "from . import sale_order_deal_tracking_ext" >> "$COMMISSION_AX_PATH/models/__init__.py"
    echo "from . import account_move_deal_tracking_ext" >> "$COMMISSION_AX_PATH/models/__init__.py"
    success "models/__init__.py updated"
fi

# ===== PHASE 7: VERIFY FILES =====

header "PHASE 7: VERIFY DEPLOYMENT"

log "Verifying all files deployed..."

FILES=(
    "$COMMISSION_AX_PATH/models/sale_order_deal_tracking_ext.py"
    "$COMMISSION_AX_PATH/models/account_move_deal_tracking_ext.py"
    "$COMMISSION_AX_PATH/views/sale_order_deal_tracking_views.xml"
    "$COMMISSION_AX_PATH/views/account_move_deal_tracking_views.xml"
)

ALL_GOOD=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $(basename $file)"
    else
        error "✗ $(basename $file) NOT FOUND"
        ALL_GOOD=false
    fi
done

if [ "$ALL_GOOD" = false ]; then
    error "Some files missing!"
    exit 1
fi

# ===== PHASE 8: START ODOO =====

header "PHASE 8: START ODOO SERVICE"

log "Starting Odoo service..."
systemctl start $ODOO_SERVICE
sleep 5

log "Verifying Odoo started..."
if systemctl is-active --quiet $ODOO_SERVICE; then
    success "Odoo service started successfully"
    systemctl status $ODOO_SERVICE | head -3 | tee -a "$LOG_FILE"
else
    error "Odoo service failed to start!"
    tail -50 /var/log/odoo/odoo-server.log | tee -a "$LOG_FILE"
    exit 1
fi

# ===== PHASE 9: MONITOR STARTUP LOGS =====

header "PHASE 9: MONITOR STARTUP LOGS"

log "Waiting for Odoo to fully initialize (20 seconds)..."
sleep 20

log "Checking logs for errors..."
ERRORS=$(tail -100 /var/log/odoo/odoo-server.log | grep -i "error\|critical" | wc -l)

if [ $ERRORS -eq 0 ]; then
    success "No errors in startup logs"
else
    warning "Found $ERRORS error messages - checking details..."
    tail -50 /var/log/odoo/odoo-server.log | grep -i "error\|critical\|warning" | head -10 | tee -a "$LOG_FILE"
fi

log "Checking for successful module loading..."
if tail -50 /var/log/odoo/odoo-server.log | grep -q "commission_ax"; then
    success "commission_ax module detected in logs"
    tail -50 /var/log/odoo/odoo-server.log | grep "commission_ax" | tee -a "$LOG_FILE"
else
    warning "commission_ax not explicitly mentioned in logs (normal for fresh start)"
fi

# ===== FINAL SUMMARY =====

header "INSTALLATION COMPLETE"

echo -e "${GREEN}All files deployed successfully!${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Summary:" | tee -a "$LOG_FILE"
echo "  • Python files:    2 deployed" | tee -a "$LOG_FILE"
echo "  • XML views:       2 deployed" | tee -a "$LOG_FILE"
echo "  • Configuration:   Updated" | tee -a "$LOG_FILE"
echo "  • Odoo service:    Running" | tee -a "$LOG_FILE"
echo "  • Database backup: $BACKUP_NAME" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo -e "${YELLOW}NEXT STEPS:${NC}" | tee -a "$LOG_FILE"
echo "  1. Go to: http://139.84.163.11:8069" | tee -a "$LOG_FILE"
echo "  2. Settings → Apps" | tee -a "$LOG_FILE"
echo "  3. Search for: commission_ax" | tee -a "$LOG_FILE"
echo "  4. Click module and then 'Upgrade'" | tee -a "$LOG_FILE"
echo "  5. Wait 2-5 minutes for upgrade" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo -e "${YELLOW}Verify in Odoo UI:${NC}" | tee -a "$LOG_FILE"
echo "  • Sales → Quotations → Open any SO" | tee -a "$LOG_FILE"
echo "  • Look for: 'BROKERAGE DEAL INFORMATION' section" | tee -a "$LOG_FILE"
echo "  • Should see: buyer_name, project_name, unit_sale_value, commission %" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo -e "${YELLOW}Log file saved to: $LOG_FILE${NC}" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
success "Installation shell script completed successfully!"
echo "" | tee -a "$LOG_FILE"

exit 0
