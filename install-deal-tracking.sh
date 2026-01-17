#!/bin/bash

# Brokerage Deal Tracking Enhancement - Installation & Testing Script
# This script will systematically deploy and test the enhancement

set -e  # Exit on any error

# Configuration
COMMISSION_AX_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax"
SOURCE_PATH="/tmp/deal_tracking_files"
BACKUP_PATH="/var/odoo/scholarixv2/backups/commission_ax_$(date +%Y%m%d_%H%M%S)"
ODOO_SERVICE="odoo"
LOG_FILE="/var/log/odoo/deal_tracking_install.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

# Initialize log
mkdir -p "$(dirname "$LOG_FILE")"
echo "Installation started at $(date)" > "$LOG_FILE"

# ===== PHASE 1: PRE-INSTALLATION CHECKS =====

log "PHASE 1: Pre-installation Checks"

if [ ! -d "$COMMISSION_AX_PATH" ]; then
    error "Commission AX module not found at $COMMISSION_AX_PATH"
    exit 1
fi
success "Commission AX module found"

if ! command -v systemctl &> /dev/null; then
    error "systemctl not found. Cannot manage Odoo service."
    exit 1
fi
success "systemctl available"

if [ ! -f "$COMMISSION_AX_PATH/__manifest__.py" ]; then
    error "Module manifest not found"
    exit 1
fi
success "Module manifest found"

# Check if Odoo is running
if systemctl is-active --quiet $ODOO_SERVICE; then
    success "Odoo service is running"
else
    warning "Odoo service is not running. Will start it during installation."
fi

# ===== PHASE 2: BACKUP EXISTING MODULE =====

log "PHASE 2: Backup Existing Module"

mkdir -p "$BACKUP_PATH"
cp -r "$COMMISSION_AX_PATH"/* "$BACKUP_PATH/" || true
success "Backup created at $BACKUP_PATH"

# ===== PHASE 3: DEPLOY CODE FILES =====

log "PHASE 3: Deploy Code Files"

# Create models directory if needed
mkdir -p "$COMMISSION_AX_PATH/models"
mkdir -p "$COMMISSION_AX_PATH/views"

# Deploy Python files
echo "Deploying Python model extensions..."

cat > "$COMMISSION_AX_PATH/models/sale_order_deal_tracking_ext.py" << 'EOF'
# -*- coding: utf-8 -*-
"""
Sale Order Extension - Brokerage Deal Tracking
"""
from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrderDealTracking(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order with Deal Tracking'

    # Deal tracking fields
    buyer_name = fields.Char(
        string="Buyer Name",
        compute="_compute_buyer_name",
        store=True,
        help="Buyer/Customer name for deal tracking"
    )

    project_name = fields.Char(
        string="Project Name",
        compute="_compute_project_name",
        store=True,
        help="Project name if deal is project-related"
    )

    unit_sale_value = fields.Monetary(
        string="Unit Sale Value",
        compute="_compute_unit_sale_value",
        store=True,
        currency_field='currency_id',
        help="Price per unit for deal tracking"
    )

    primary_commission_percentage = fields.Float(
        string="Primary Commission %",
        compute="_compute_primary_commission_percentage",
        store=True,
        help="Highest commission % among all partners"
    )

    deal_summary_html = fields.Html(
        string="Deal Summary",
        compute="_compute_deal_summary_html",
        help="HTML summary of deal information for reporting"
    )

    @api.depends('partner_id', 'partner_id.name')
    def _compute_buyer_name(self):
        """Compute buyer name from customer"""
        for record in self:
            record.buyer_name = record.partner_id.name if record.partner_id else ''

    @api.depends('project_id', 'project_id.name')
    def _compute_project_name(self):
        """Compute project name from project field"""
        for record in self:
            record.project_name = record.project_id.name if record.project_id else ''

    @api.depends('order_line', 'order_line.price_unit')
    def _compute_unit_sale_value(self):
        """Compute unit sale value from first order line"""
        for record in self:
            if record.order_line:
                line = record.order_line[0]
                record.unit_sale_value = line.price_unit
            else:
                record.unit_sale_value = 0.0

    @api.depends(
        'broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate',
        'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate'
    )
    def _compute_primary_commission_percentage(self):
        """Compute highest commission percentage"""
        for record in self:
            rates = [
                record.broker_rate or 0, record.referrer_rate or 0,
                record.cashback_rate or 0, record.other_external_rate or 0,
                record.agent1_rate or 0, record.agent2_rate or 0,
                record.manager_rate or 0, record.director_rate or 0,
            ]
            record.primary_commission_percentage = max(rates) if rates else 0.0

    @api.depends(
        'buyer_name', 'project_name', 'unit_sale_value',
        'primary_commission_percentage', 'currency_id'
    )
    def _compute_deal_summary_html(self):
        """Compute HTML summary for display"""
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = (
                f"{record.currency_id.symbol} {record.unit_sale_value:,.2f}"
                if record.unit_sale_value else '—'
            )
            commission = (
                f"{record.primary_commission_percentage:.2f}%"
                if record.primary_commission_percentage else '—'
            )
            
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
        """Override to pass deal tracking info to invoice"""
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'buyer_name': self.buyer_name,
            'project_name': self.project_name,
            'unit_sale_value': self.unit_sale_value,
            'commission_percentage': self.primary_commission_percentage,
            'sale_order_deal_reference': self.name,
        })
        return invoice_vals
EOF

success "Deployed sale_order_deal_tracking_ext.py"

cat > "$COMMISSION_AX_PATH/models/account_move_deal_tracking_ext.py" << 'EOF'
# -*- coding: utf-8 -*-
"""
Account Move Extension - Brokerage Deal Reference
"""
from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountMoveWithDealTracking(models.Model):
    _inherit = 'account.move'
    _description = 'Invoice with Brokerage Deal Information'

    buyer_name = fields.Char(string="Buyer Name", help="Original buyer from sale order")
    project_name = fields.Char(string="Project Name", help="Original project from sale order")
    unit_sale_value = fields.Monetary(
        string="Unit Sale Value", currency_field='currency_id',
        help="Original unit sale value from order"
    )
    commission_percentage = fields.Float(
        string="Commission %", help="Primary commission percentage from order"
    )
    sale_order_deal_reference = fields.Char(
        string="Sale Order Reference", help="Link to originating sale order"
    )
    sale_order_id = fields.Many2one(
        'sale.order', string="Source Sale Order",
        help="Sale order that generated this invoice"
    )

    deal_information_summary = fields.Html(
        string="Deal Information Summary",
        compute="_compute_deal_information_summary",
        help="Summary of deal details for accounting review"
    )

    @api.depends(
        'buyer_name', 'project_name', 'unit_sale_value',
        'commission_percentage', 'currency_id'
    )
    def _compute_deal_information_summary(self):
        """Compute HTML summary of deal information"""
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = (
                f"{record.currency_id.symbol} {record.unit_sale_value:,.2f}"
                if record.unit_sale_value else '—'
            )
            commission = (
                f"{record.commission_percentage:.2f}%"
                if record.commission_percentage else '—'
            )
            
            record.deal_information_summary = f"""
            <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 4px solid #8b1538; margin: 10px 0;">
                <h6 style="color: #8b1538; font-weight: bold; margin: 0 0 8px 0;">ORIGINAL DEAL INFORMATION</h6>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <tr><td style="padding: 4px; font-weight: bold; width: 40%;">Buyer:</td>
                        <td style="padding: 4px; color: #8b1538;">{buyer}</td></tr>
                    <tr style="background: #ffffff;"><td style="padding: 4px; font-weight: bold;">Project:</td>
                        <td style="padding: 4px; color: #333;">{project}</td></tr>
                    <tr><td style="padding: 4px; font-weight: bold;">Unit Sale Value:</td>
                        <td style="padding: 4px; color: #333; text-align: right;">{unit_val}</td></tr>
                    <tr style="background: #ffe6e6;"><td style="padding: 4px; font-weight: bold;">Commission %:</td>
                        <td style="padding: 4px; color: #8b1538; text-align: right; font-weight: bold;">{commission}</td></tr>
                </table>
            </div>
            """

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-populate from sale order if needed"""
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

    def action_view_sale_order_deal(self):
        """Action to view the related sale order"""
        self.ensure_one()
        if self.sale_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': self.sale_order_id.id,
                'view_mode': 'form',
            }
        return True
EOF

success "Deployed account_move_deal_tracking_ext.py"

# Deploy XML view files
echo "Deploying XML views..."

cat > "$COMMISSION_AX_PATH/views/sale_order_deal_tracking_views.xml" << 'EOF'
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
                        <div class="col-md-12"><h5 style="color: #8b1538; font-weight: bold; margin-bottom: 10px;">BROKERAGE DEAL INFORMATION</h5></div>
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
                    <field name="buyer_name" string="Buyer" width="15%"/>
                    <field name="project_name" string="Project" width="15%"/>
                    <field name="unit_sale_value" string="Unit Price" width="12%"/>
                    <field name="primary_commission_percentage" string="Commission %" width="10%"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
EOF

success "Deployed sale_order_deal_tracking_views.xml"

cat > "$COMMISSION_AX_PATH/views/account_move_deal_tracking_views.xml" << 'EOF'
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
                    <field name="buyer_name" string="Buyer" width="15%"/>
                    <field name="project_name" string="Project" width="12%"/>
                    <field name="unit_sale_value" string="Unit Price" width="10%"/>
                    <field name="commission_percentage" string="Commission %" width="10%"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
EOF

success "Deployed account_move_deal_tracking_views.xml"

# ===== PHASE 4: UPDATE MODULE CONFIGURATION =====

log "PHASE 4: Update Module Configuration"

# Update __manifest__.py
python3 << 'PYTHONEOF'
import os
import sys

manifest_path = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py"

with open(manifest_path, 'r') as f:
    content = f.read()

# Check if views already added
if "sale_order_deal_tracking_views.xml" in content:
    print("Views already in manifest, skipping update")
    sys.exit(0)

# Find 'data' section and add views
lines = content.split('\n')
new_lines = []
in_data_section = False
data_closed = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    if "'data':" in line:
        in_data_section = True
    
    if in_data_section and not data_closed:
        if line.strip().endswith('],'):
            # Add before closing bracket
            new_lines.insert(-1, "        'views/sale_order_deal_tracking_views.xml',")
            new_lines.insert(-1, "        'views/account_move_deal_tracking_views.xml',")
            in_data_section = False
            data_closed = True

new_content = '\n'.join(new_lines)

with open(manifest_path, 'w') as f:
    f.write(new_content)

print("✓ Updated __manifest__.py with view registrations")
PYTHONEOF

success "Updated __manifest__.py"

# Update models/__init__.py
python3 << 'PYTHONEOF'
import sys

init_path = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/__init__.py"

with open(init_path, 'r') as f:
    content = f.read()

# Check if already imported
if "sale_order_deal_tracking_ext" in content:
    print("Modules already imported, skipping")
    sys.exit(0)

# Add imports before or after other model imports
if "from . import" in content:
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if "from . import sale_order" in line and "deal_tracking" not in line:
            new_lines.append("from . import sale_order_deal_tracking_ext")
            new_lines.append("from . import account_move_deal_tracking_ext")
            break
    
    if len(new_lines) == len(lines):
        # Not found after sale_order, add at end
        new_lines.append("from . import sale_order_deal_tracking_ext")
        new_lines.append("from . import account_move_deal_tracking_ext")
    
    new_content = '\n'.join(new_lines)
else:
    new_content = content + "\nfrom . import sale_order_deal_tracking_ext\nfrom . import account_move_deal_tracking_ext\n"

with open(init_path, 'w') as f:
    f.write(new_content)

print("✓ Updated models/__init__.py with imports")
PYTHONEOF

success "Updated models/__init__.py"

# ===== PHASE 5: RESTART ODOO =====

log "PHASE 5: Restart Odoo Service"

systemctl stop $ODOO_SERVICE || true
sleep 3

if systemctl start $ODOO_SERVICE; then
    sleep 5
    success "Odoo service restarted successfully"
else
    error "Failed to start Odoo service"
    exit 1
fi

# ===== PHASE 6: VERIFY DEPLOYMENT =====

log "PHASE 6: Verify Deployment"

# Check if Odoo is running
if systemctl is-active --quiet $ODOO_SERVICE; then
    success "Odoo service is running"
else
    error "Odoo service failed to start"
    exit 1
fi

# Check if files were deployed
files_to_check=(
    "$COMMISSION_AX_PATH/models/sale_order_deal_tracking_ext.py"
    "$COMMISSION_AX_PATH/models/account_move_deal_tracking_ext.py"
    "$COMMISSION_AX_PATH/views/sale_order_deal_tracking_views.xml"
    "$COMMISSION_AX_PATH/views/account_move_deal_tracking_views.xml"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        success "File deployed: $(basename $file)"
    else
        error "File NOT found: $file"
        exit 1
    fi
done

log "INSTALLATION COMPLETE!"
echo ""
success "All files deployed successfully"
success "Odoo service is running"
success "Ready for testing"

echo ""
log "Next steps:"
echo "  1. Test sale order deal fields"
echo "  2. Test invoice deal information"
echo "  3. Test UI navigation and views"
echo "  4. Check logs: tail -f /var/log/odoo/odoo-server.log"
echo ""

exit 0
