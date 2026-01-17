#!/bin/bash

# ============================================
# INLINE DEPLOYMENT SCRIPT
# ============================================
# This script creates and executes the installation
# directly on the target server without external files

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   ODOO DEAL TRACKING DEPLOYMENT - DIRECT INLINE EXECUTION     ║"
echo "║                   Starting Installation                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================
# CHECK ENVIRONMENT
# ============================================

echo "[STEP] Verifying deployment environment..."
cd /var/odoo/scholarixv2 || exit 1
echo "  ✓ Working directory: $(pwd)"

if systemctl is-active --quiet odoo; then
    echo "  ✓ Odoo service is running"
else
    echo "  ✗ Odoo service not running - starting..."
    systemctl start odoo
    sleep 3
fi

# ============================================
# CREATE PYTHON FILES INLINE
# ============================================

echo ""
echo "[STEP] Creating Python extension files..."

# File 1: sale_order_deal_tracking_ext.py
cat > extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py << 'PYTHON_SALE_EOF'
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
            
            record.deal_summary_html = f"""<div style="background: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 4px solid #8b1538;"><table style="width: 100%; border-collapse: collapse; font-size: 12px;"><tr><td style="padding: 6px; font-weight: bold;">Buyer:</td><td style="padding: 6px; color: #8b1538;">{buyer}</td></tr><tr><td style="padding: 6px; font-weight: bold;">Project:</td><td style="padding: 6px;">{project}</td></tr><tr><td style="padding: 6px; font-weight: bold;">Unit Sale Value:</td><td style="padding: 6px; text-align: right;">{unit_val}</td></tr><tr><td style="padding: 6px; font-weight: bold;">Commission %:</td><td style="padding: 6px; color: #8b1538; text-align: right;">{commission}</td></tr></table></div>"""

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
PYTHON_SALE_EOF

echo "  ✓ Created: sale_order_deal_tracking_ext.py ($(wc -l < extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py) lines)"

# File 2: account_move_deal_tracking_ext.py
cat > extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py << 'PYTHON_ACCOUNT_EOF'
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
            
            record.deal_information_summary = f"""<div style="background: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 4px solid #8b1538;"><h6 style="color: #8b1538; margin: 0 0 8px 0;">ORIGINAL DEAL INFORMATION</h6><table style="width: 100%; border-collapse: collapse; font-size: 11px;"><tr><td style="padding: 4px; font-weight: bold;">Buyer:</td><td style="padding: 4px; color: #8b1538;">{buyer}</td></tr><tr><td style="padding: 4px; font-weight: bold;">Project:</td><td style="padding: 4px;">{project}</td></tr><tr><td style="padding: 4px; font-weight: bold;">Unit Sale Value:</td><td style="padding: 4px; text-align: right;">{unit_val}</td></tr><tr><td style="padding: 4px; font-weight: bold;">Commission %:</td><td style="padding: 4px; color: #8b1538; text-align: right;">{commission}</td></tr></table></div>"""

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
PYTHON_ACCOUNT_EOF

echo "  ✓ Created: account_move_deal_tracking_ext.py ($(wc -l < extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py) lines)"

# ============================================
# CREATE XML FILES INLINE
# ============================================

echo ""
echo "[STEP] Creating XML view files..."

# File 3: sale_order_deal_tracking_views.xml
cat > extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/sale_order_deal_tracking_views.xml << 'XML_SALE_EOF'
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
XML_SALE_EOF

echo "  ✓ Created: sale_order_deal_tracking_views.xml ($(wc -l < extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/sale_order_deal_tracking_views.xml) lines)"

# File 4: account_move_deal_tracking_views.xml
cat > extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/account_move_deal_tracking_views.xml << 'XML_ACCOUNT_EOF'
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
XML_ACCOUNT_EOF

echo "  ✓ Created: account_move_deal_tracking_views.xml ($(wc -l < extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/account_move_deal_tracking_views.xml) lines)"

# ============================================
# VERIFY FILES
# ============================================

echo ""
echo "[STEP] Verifying deployed files..."
ls -lh extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py
ls -lh extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py
ls -lh extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/sale_order_deal_tracking_views.xml
ls -lh extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/account_move_deal_tracking_views.xml
echo "  ✓ All 4 files verified"

# ============================================
# UPDATE CONFIGURATION
# ============================================

echo ""
echo "[STEP] Updating configuration..."

# Update __manifest__.py
if ! grep -q "sale_order_deal_tracking_views.xml" extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py; then
    sed -i "/^    'data': \[/a\        'views/sale_order_deal_tracking_views.xml',\n        'views/account_move_deal_tracking_views.xml'," extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py
    echo "  ✓ Updated __manifest__.py"
fi

# Update models/__init__.py
if ! grep -q "sale_order_deal_tracking_ext" extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/__init__.py; then
    echo "from . import sale_order_deal_tracking_ext" >> extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/__init__.py
    echo "from . import account_move_deal_tracking_ext" >> extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/__init__.py
    echo "  ✓ Updated models/__init__.py"
fi

# ============================================
# RESTART ODOO SERVICE
# ============================================

echo ""
echo "[STEP] Restarting Odoo service..."
systemctl stop odoo
sleep 3
systemctl start odoo
sleep 5

if systemctl is-active --quiet odoo; then
    echo "  ✓ Odoo service restarted successfully"
else
    echo "  ✗ Failed to restart Odoo"
    exit 1
fi

# ============================================
# FINAL VERIFICATION
# ============================================

echo ""
echo "[STEP] Final verification..."
systemctl status odoo | head -3
echo "  ✓ Service running"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✓ DEPLOYMENT SUCCESSFUL!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Deployed Files:"
echo "  ✓ sale_order_deal_tracking_ext.py"
echo "  ✓ account_move_deal_tracking_ext.py"
echo "  ✓ sale_order_deal_tracking_views.xml"
echo "  ✓ account_move_deal_tracking_views.xml"
echo ""
echo "Configuration:"
echo "  ✓ __manifest__.py updated"
echo "  ✓ models/__init__.py updated"
echo ""
echo "Service:"
echo "  ✓ Odoo restarted"
echo ""
echo "NEXT STEPS:"
echo "1. Open: http://139.84.163.11:8069"
echo "2. Go to: Settings → Apps"
echo "3. Search: commission_ax"
echo "4. Click: UPGRADE"
echo "5. Wait 2-5 minutes"
echo "6. Verify deal fields appear in sale orders"
echo ""
