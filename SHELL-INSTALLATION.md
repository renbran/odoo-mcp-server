# SHELL-BASED INSTALLATION - STEP BY STEP
## Real-time Monitoring & Interactive Verification

---

## QUICK START

### Option 1: Fully Automated (Recommended)
Run the interactive installation script that handles everything:

```bash
# SSH to server
ssh root@139.84.163.11

# Download and run interactive installer
bash /tmp/deploy-interactive.sh
```

This will:
- ✅ Create backups automatically
- ✅ Deploy all 4 code files
- ✅ Update configuration files
- ✅ Restart Odoo service
- ✅ Monitor startup logs
- ✅ Verify deployment

**Time: ~15 minutes**

### Option 2: Manual Step-by-Step (With Monitoring)
Follow the steps below for complete control

**Time: ~30 minutes**

---

## MANUAL INSTALLATION - STEP BY STEP

### STEP 1: Connect to Server

```bash
ssh root@139.84.163.11
cd /var/odoo/scholarixv2
```

**Verify connection:**
```bash
pwd
# Should show: /var/odoo/scholarixv2

ls -la extra-addons/odooapps.git-68ee71eda34bc/commission_ax/
# Should list module files
```

---

### STEP 2: Create Backups

```bash
# Create backup directory
mkdir -p backups

# Backup database
echo "Backing up database..."
pg_dump commission_ax > backups/commission_ax_$(date +%Y%m%d_%H%M%S).sql
echo "✓ Database backup created"
ls -lh backups/commission_ax_*.sql | tail -1

# Backup module files
BACKUP_NAME="commission_ax_$(date +%Y%m%d_%H%M%S)"
mkdir -p backups/$BACKUP_NAME
cp -r extra-addons/odooapps.git-68ee71eda34bc/commission_ax/* backups/$BACKUP_NAME/
echo "✓ Module backup created"
du -sh backups/$BACKUP_NAME
```

**Monitor:**
```bash
# Verify backups
ls -lh backups/ | tail -5
```

---

### STEP 3: Stop Odoo Service

```bash
# Stop service
systemctl stop odoo
echo "Waiting for shutdown..."
sleep 5

# Verify stopped
systemctl status odoo
# Should show: inactive (dead)

echo "✓ Odoo service stopped"
```

---

### STEP 4: Deploy Python Files

```bash
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax
```

**Create sale_order_deal_tracking_ext.py:**

```bash
cat > models/sale_order_deal_tracking_ext.py << 'EOF'
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
EOF

echo "✓ sale_order_deal_tracking_ext.py created"
wc -l models/sale_order_deal_tracking_ext.py
```

**Verify Python syntax:**
```bash
python3 -m py_compile models/sale_order_deal_tracking_ext.py && echo "✓ Syntax OK" || echo "✗ Syntax error"
```

**Create account_move_deal_tracking_ext.py:**

```bash
cat > models/account_move_deal_tracking_ext.py << 'EOF'
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
EOF

echo "✓ account_move_deal_tracking_ext.py created"
wc -l models/account_move_deal_tracking_ext.py
```

**Verify Python syntax:**
```bash
python3 -m py_compile models/account_move_deal_tracking_ext.py && echo "✓ Syntax OK" || echo "✗ Syntax error"
```

---

### STEP 5: Deploy XML Files

**Create sale_order_deal_tracking_views.xml:**

```bash
cat > views/sale_order_deal_tracking_views.xml << 'EOF'
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
EOF

echo "✓ sale_order_deal_tracking_views.xml created"
wc -l views/sale_order_deal_tracking_views.xml
```

**Verify XML syntax:**
```bash
xmllint views/sale_order_deal_tracking_views.xml > /dev/null 2>&1 && echo "✓ XML syntax OK" || echo "✗ XML error"
```

**Create account_move_deal_tracking_views.xml:**

```bash
cat > views/account_move_deal_tracking_views.xml << 'EOF'
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
EOF

echo "✓ account_move_deal_tracking_views.xml created"
wc -l views/account_move_deal_tracking_views.xml
```

**Verify XML syntax:**
```bash
xmllint views/account_move_deal_tracking_views.xml > /dev/null 2>&1 && echo "✓ XML syntax OK" || echo "✗ XML error"
```

---

### STEP 6: Verify All Files Deployed

```bash
echo "Checking deployed files..."
ls -lh models/sale_order_deal_tracking_ext.py
ls -lh models/account_move_deal_tracking_ext.py
ls -lh views/sale_order_deal_tracking_views.xml
ls -lh views/account_move_deal_tracking_views.xml
echo "✓ All 4 files deployed"
```

---

### STEP 7: Update Configuration

**Update __manifest__.py:**

```bash
echo ""
echo "Updating __manifest__.py..."

# Check if already added
if ! grep -q "sale_order_deal_tracking_views.xml" __manifest__.py; then
    # Add views to data section
    sed -i "/^    'data': \[/a\        'views/sale_order_deal_tracking_views.xml',\n        'views/account_move_deal_tracking_views.xml'," __manifest__.py
    echo "✓ __manifest__.py updated"
else
    echo "! Views already in manifest"
fi

# Verify
echo "Verifying manifest..."
grep -n "deal_tracking" __manifest__.py | head -2
```

**Update models/__init__.py:**

```bash
echo ""
echo "Updating models/__init__.py..."

# Check if already added
if ! grep -q "sale_order_deal_tracking_ext" models/__init__.py; then
    echo "from . import sale_order_deal_tracking_ext" >> models/__init__.py
    echo "from . import account_move_deal_tracking_ext" >> models/__init__.py
    echo "✓ models/__init__.py updated"
else
    echo "! Modules already imported"
fi

# Verify
echo "Verifying imports..."
tail -3 models/__init__.py
```

---

### STEP 8: Start Odoo Service

```bash
echo ""
echo "Starting Odoo service..."
systemctl start odoo

echo "Waiting for startup (10 seconds)..."
sleep 10

echo "Checking service status..."
systemctl status odoo | head -5

if systemctl is-active --quiet odoo; then
    echo "✓ Odoo service started successfully"
else
    echo "✗ Odoo service failed to start"
    echo "Checking logs..."
    tail -20 /var/log/odoo/odoo-server.log
fi
```

---

### STEP 9: Monitor Logs

**Terminal 1 - Monitor logs in real-time:**

```bash
tail -f /var/log/odoo/odoo-server.log
```

**Terminal 2 - Check for errors (while monitoring):**

```bash
# Check for errors
tail -100 /var/log/odoo/odoo-server.log | grep -i "error"

# Check for commission_ax mention
tail -100 /var/log/odoo/odoo-server.log | grep "commission_ax"

# Overall status
echo "Service running:"
systemctl is-active odoo

echo "Database OK:"
psql -l | grep commission_ax
```

---

### STEP 10: Upgrade Module in Odoo UI

1. **Open browser:** http://139.84.163.11:8069
2. **Login** with admin credentials
3. **Go to:** Settings → Apps
4. **Search:** commission_ax
5. **Click** on module
6. **Click** "Upgrade" button
7. **Wait** 2-5 minutes for upgrade
8. **Check** for success message

---

### STEP 11: Verify Deal Fields in Odoo

1. **Go to:** Sales → Quotations
2. **Open** any sale order
3. **Look for:** "BROKERAGE DEAL INFORMATION" section
4. **Verify** fields visible:
   - buyer_name
   - project_name
   - unit_sale_value
   - primary_commission_percentage
   - deal_summary_html (colored box)

---

## TROUBLESHOOTING

### If Odoo Won't Start

```bash
# Check syntax
python3 -m py_compile models/sale_order_deal_tracking_ext.py
python3 -m py_compile models/account_move_deal_tracking_ext.py

# Check logs for specific error
tail -100 /var/log/odoo/odoo-server.log | grep -i "error"

# Restore from backup if needed
systemctl stop odoo
cp -r backups/commission_ax_YYYYMMDD_HHMMSS/* \
      extra-addons/odooapps.git-68ee71eda34bc/commission_ax/
systemctl start odoo
```

### If Fields Not Showing

```bash
# Verify manifest updated
grep "deal_tracking" __manifest__.py

# Verify imports
grep "deal_tracking" models/__init__.py

# Restart Odoo
systemctl restart odoo

# Upgrade module manually via CLI
cd /var/odoo/scholarixv2
python3 -m odoo -c ./odoo.conf -d commission_ax -u commission_ax --stop-after-init
```

---

## MONITORING DURING INSTALLATION

Use this in a separate terminal while installation is running:

```bash
# Watch the log file for progress
watch -n 5 'tail -20 /var/log/odoo/odoo-server.log'

# Or use the monitoring dashboard
bash /path/to/monitor-deployment.sh
```

---

## FINAL VERIFICATION

Run these checks after everything is installed:

```bash
# 1. Service running
systemctl status odoo | grep Active

# 2. All files present
ls models/sale_order_deal_tracking_ext.py models/account_move_deal_tracking_ext.py
ls views/sale_order_deal_tracking_views.xml views/account_move_deal_tracking_views.xml

# 3. Configuration updated
grep -c "deal_tracking" __manifest__.py
grep -c "deal_tracking" models/__init__.py

# 4. No errors in logs
tail -50 /var/log/odoo/odoo-server.log | grep -i error | wc -l
# Should be 0 or just expected messages

# 5. Database accessible
psql -c "SELECT COUNT(*) FROM pg_tables WHERE table_name LIKE '%deal%';" commission_ax

echo "✓ Installation verification complete"
```

---

**Installation via shell is now complete!**

**Next: Follow TESTING-GUIDE.md to run comprehensive tests**

