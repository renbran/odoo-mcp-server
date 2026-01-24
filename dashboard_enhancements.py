# -*- coding: utf-8 -*-
"""
Enhanced Dashboard Compute Methods
To be added to sales_invoicing_dashboard.py

This file contains all new compute methods for the enhanced dashboard.
Insert these methods before the action_export methods in the model.
"""

# NEW COMPUTE METHODS TO ADD:

def _compute_enhanced_metrics(self):
    """Compute additional KPI metrics for enhanced dashboard"""
    self.env.invalidate_all()
    for rec in self:
        order_domain = rec._get_order_domain()
        matching_orders = self.env['sale.order'].search(order_domain)
        order_count = len(matching_orders)
        
        # Average Deal Size
        rec.avg_deal_size = (rec.total_booked_sales / order_count) if order_count > 0 else 0.0
        
        # Conversion Rate (invoiced orders / total orders)
        invoiced_orders = matching_orders.filtered(lambda o: o.invoice_status in ['invoiced', 'to invoice'])
        rec.conversion_rate = (len(invoiced_orders) / order_count * 100.0) if order_count > 0 else 0.0
        
        # Collection Rate
        rec.collection_rate = (rec.amount_collected / rec.total_invoiced_amount * 100.0) if rec.total_invoiced_amount > 0 else 0.0
        
        # Outstanding Ratio
        rec.outstanding_ratio = (rec.amount_to_collect / rec.total_invoiced_amount * 100.0) if rec.total_invoiced_amount > 0 else 0.0
        
        # Commission Rate
        rec.commission_rate = (rec.commission_due / rec.total_booked_sales * 100.0) if rec.total_booked_sales > 0 else 0.0
        
        # Active Customers Count
        rec.active_customers_count = len(matching_orders.mapped('partner_id'))
        
        # Average Days to Invoice
        total_days_to_invoice = 0
        invoice_count = 0
        for order in matching_orders:
            if order.invoice_ids:
                first_invoice = min(order.invoice_ids.filtered(lambda inv: inv.invoice_date), 
                                    key=lambda inv: inv.invoice_date, default=None)
                if first_invoice and first_invoice.invoice_date and order.booking_date:
                    days = (first_invoice.invoice_date - order.booking_date).days
                    total_days_to_invoice += days
                    invoice_count += 1
        rec.avg_days_to_invoice = (total_days_to_invoice / invoice_count) if invoice_count > 0 else 0.0
        
        # Average Days to Payment (simplified estimate)
        invoice_domain = rec._get_invoice_domain(include_payment_filter=False, unpaid_only=False)
        paid_invoices = self.env['account.move'].search(invoice_domain).filtered(
            lambda inv: inv.payment_state == 'paid'
        )
        total_days_to_payment = 0
        payment_count = len(paid_invoices)
        for invoice in paid_invoices:
            if invoice.invoice_date and invoice.invoice_date_due:
                # Use due date as proxy
                total_days_to_payment += (invoice.invoice_date_due - invoice.invoice_date).days
        rec.avg_days_to_payment = (total_days_to_payment / payment_count) if payment_count > 0 else 0.0


# Add decorator before each method when integrating:
# @api.depends('sales_order_type_id', 'sales_order_type_ids', 'booking_date_from', 'booking_date_to', 'invoice_status_filter', 'payment_status_filter', 'agent_partner_id', 'partner_id', 'total_booked_sales', 'total_invoiced_amount', 'amount_to_collect', 'amount_collected', 'commission_due')

def _compute_chart_sales_pipeline(self):
    """Compute sales pipeline chart showing stages"""
    self.env.invalidate_all()
    for rec in self:
        order_domain = rec._get_order_domain()
        all_orders = self.env['sale.order'].search(order_domain)
        
        # Pipeline stages
        confirmed_orders = all_orders.filtered(lambda o: o.state in ['sale', 'done'])
        invoiced_orders = confirmed_orders.filtered(lambda o: o.invoice_status == 'invoiced')
        paid_orders = confirmed_orders.filtered(lambda o: all(
            inv.payment_state == 'paid' for inv in o.invoice_ids.filtered(lambda i: i.state == 'posted')
        ) if o.invoice_ids else False)
        
        data = [
            sum(confirmed_orders.mapped('amount_total')),
            sum(invoiced_orders.mapped('amount_total')),
            sum(paid_orders.mapped('amount_total')),
        ]
        
        rec.chart_sales_pipeline = {
            'labels': ['Confirmed', 'Invoiced', 'Paid'],
            'datasets': [{
                'label': 'Flow',
                'data': data,
                'backgroundColor': ['#3498db', '#f39c12', '#27ae60'],
                'borderColor': ['#3498db', '#f39c12', '#27ae60'],
                'borderWidth': 1,
            }],
        }


def _compute_chart_weekly_trend(self):
    """Compute weekly booking trend chart"""
    self.env.invalidate_all()
    for rec in self:
        order_domain = rec._get_order_domain()
        try:
            groups = self.env['sale.order'].read_group(
                order_domain,
                ['amount_total'],
                ['booking_date:week'],
                orderby='booking_date:week',
                lazy=False
            )
            labels = [str(g.get('booking_date:week') or 'N/A') for g in groups]
            data = [float(g.get('amount_total', 0) or 0) for g in groups]
        except:
            labels = ['No data']
            data = [0]
        
        rec.chart_weekly_trend = {
            'labels': labels,
            'datasets': [{
                'label': 'Weekly Bookings',
                'data': data,
                'backgroundColor': '#3498db',
                'borderColor': '#3498db',
                'fill': False,
                'tension': 0.4,
                'borderWidth': 2,
            }],
        }


def _compute_chart_salesperson_performance(self):
    """Compute salesperson performance chart"""
    self.env.invalidate_all()
    for rec in self:
        order_domain = rec._get_order_domain()
        # Group by agent1_partner_id if available
        if 'agent1_partner_id' in self.env['sale.order']._fields:
            groups = self.env['sale.order'].read_group(
                order_domain,
                ['amount_total'],
                ['agent1_partner_id'],
                orderby='amount_total DESC',
                limit=10
            )
            labels = [(g.get('agent1_partner_id') or ['', 'Unassigned'])[1] for g in groups]
            data = [g.get('amount_total', 0.0) for g in groups]
        else:
            labels = ['No Agent Data']
            data = [0]
        
        rec.chart_salesperson_performance = {
            'labels': labels,
            'datasets': [{
                'label': 'Total Sales',
                'data': data,
                'backgroundColor': '#9b59b6',
                'borderColor': '#9b59b6',
                'borderWidth': 1,
            }],
        }


def _compute_chart_payment_distribution(self):
    """Compute payment distribution pie chart"""
    self.env.invalidate_all()
    for rec in self:
        domain = rec._get_invoice_domain(include_payment_filter=False, unpaid_only=False)
        groups = self.env['account.move'].read_group(
            domain,
            ['amount_total'],
            ['payment_state']
        )
        state_names = {
            'not_paid': 'Not Paid',
            'partial': 'Partially Paid',
            'in_payment': 'In Payment',
            'paid': 'Paid',
        }
        labels = [state_names.get(g.get('payment_state', ''), 'Unknown') for g in groups]
        data = [g.get('amount_total', 0.0) for g in groups]
        colors = ['#e74c3c', '#f39c12', '#3498db', '#27ae60'][:len(data)]
        
        rec.chart_payment_distribution = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors,
                'borderColor': '#fff',
                'borderWidth': 2,
            }],
        }


def _compute_chart_order_type_pie(self):
    """Compute order type distribution pie chart"""
    self.env.invalidate_all()
    palette = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6', '#1abc9c']
    for rec in self:
        order_domain = rec._get_order_domain()
        groups = self.env['sale.order'].read_group(
            order_domain,
            ['amount_total'],
            ['sale_order_type_id']
        )
        labels = [(g.get('sale_order_type_id') or ['', 'Unspecified'])[1] for g in groups]
        data = [g.get('amount_total', 0.0) for g in groups]
        colors = [palette[i % len(palette)] for i in range(len(data))]
        
        rec.chart_order_type_pie = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors,
                'borderColor': '#fff',
                'borderWidth': 2,
            }],
        }

