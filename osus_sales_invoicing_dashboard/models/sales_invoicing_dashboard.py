# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date


class SalesInvoicingDashboard(models.Model):
    _name = 'osus.sales.invoicing.dashboard'
    _rec_name = 'name'
    _description = 'Sales & Invoicing Dashboard'

    # Simple label so the record always has a display name in forms/kanban
    name = fields.Char(default='Sales & Invoicing Dashboard', readonly=True)

    # Multi-company
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )
    company_currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string='Company Currency', readonly=True
    )

    # Filters
    sales_order_type_id = fields.Many2one(
        'sale.order.type', string='Sales Order Type'
    )
    sales_order_type_ids = fields.Many2many(
        'sale.order.type', string='Sales Order Types',
        help='Filter by one or more order types'
    )
    booking_date_from = fields.Date(string='Booking Date From')
    booking_date_to = fields.Date(string='Booking Date To')
    invoice_status_filter = fields.Selection(
        [
            ('all', 'All'),
            ('no', 'Not Invoiced'),
            ('to invoice', 'Pending to Invoice'),
            ('invoiced', 'Fully Invoiced'),
        ],
        string='Invoice Status'
    )
    payment_status_filter = fields.Selection(
        [
            ('all', 'All'),
            ('not_paid', 'Not Paid'),
            ('partial', 'Partially Paid'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
        ],
        string='Payment Status'
    )

    # Additional recommended filters
    agent_partner_id = fields.Many2one('res.partner', string='Salesperson (Agent1)')
    partner_id = fields.Many2one('res.partner', string='Customer')

    # Computed metrics using field relationships
    posted_invoice_count = fields.Integer(
        string='Posted Invoices', compute='_compute_metrics', store=False
    )
    pending_to_invoice_order_count = fields.Integer(
        string='Orders To Invoice', compute='_compute_metrics', store=False
    )
    unpaid_invoice_count = fields.Integer(
        string='Unpaid Invoices', compute='_compute_metrics', store=False
    )
    total_invoiced_amount = fields.Monetary(
        string='Total Invoiced Amount', compute='_compute_metrics', store=False,
        currency_field='company_currency_id'
    )
    total_pending_amount = fields.Monetary(
        string='Total Pending to Invoice', compute='_compute_metrics', store=False,
        currency_field='company_currency_id'
    )
    # Extended KPIs
    total_booked_sales = fields.Monetary(
        string='Total Booked Sales', compute='_compute_metrics', store=False,
        currency_field='company_currency_id'
    )
    amount_to_collect = fields.Monetary(
        string='Amount to Collect', compute='_compute_metrics', store=False,
        currency_field='company_currency_id'
    )
    amount_collected = fields.Monetary(
        string='Amount Collected', compute='_compute_metrics', store=False,
        currency_field='company_currency_id'
    )
    commission_due = fields.Monetary(
        string='Commission Due', compute='_compute_metrics', store=False,
        currency_field='company_currency_id'
    )
    company_currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    average_order_value = fields.Monetary(
        string='Average Order Value',
        compute='_compute_performance_metrics',
        currency_field='company_currency_id',
        help='Average value per sales order'
    )
    
    conversion_rate = fields.Float(
        string='Conversion Rate (%)',
        compute='_compute_performance_metrics',
        help='Percentage of quotes converted to sales orders'
    )
    
    total_orders_count = fields.Integer(
        string='Total Orders',
        compute='_compute_performance_metrics',
        help='Total number of sales orders'
    )
    
    total_invoices_count = fields.Integer(
        string='Total Invoices',
        compute='_compute_performance_metrics',
        help='Total number of invoices'
    )
    
    pending_orders_count = fields.Integer(
        string='Pending Orders',
        compute='_compute_performance_metrics',
        help='Orders awaiting invoice'
    )
    
    collection_efficiency = fields.Float(
        string='Collection Efficiency (%)',
        compute='_compute_performance_metrics',
        help='Percentage of invoiced amount collected'
    )
    
    outstanding_amount = fields.Monetary(
        string='Outstanding Amount',
        compute='_compute_performance_metrics',
        currency_field='company_currency_id',
        help='Amount to collect - Amount collected'
    )
    
    daily_sales_average = fields.Monetary(
        string='Daily Sales Average',
        compute='_compute_performance_metrics',
        currency_field='company_currency_id',
        help='Average sales per day in selected period'
    )


    # Additional KPI Metrics (Enhanced Dashboard)
    avg_deal_size = fields.Monetary(
        string='Average Deal Size', compute='_compute_enhanced_metrics', store=False,
        currency_field='company_currency_id'
    )
    conversion_rate = fields.Float(
        string='Conversion Rate %', compute='_compute_enhanced_metrics', store=False
    )
    collection_rate = fields.Float(
        string='Collection Rate %', compute='_compute_enhanced_metrics', store=False
    )
    outstanding_ratio = fields.Float(
        string='Outstanding Ratio %', compute='_compute_enhanced_metrics', store=False
    )
    commission_rate = fields.Float(
        string='Commission Rate %', compute='_compute_enhanced_metrics', store=False
    )
    active_customers_count = fields.Integer(
        string='Active Customers', compute='_compute_enhanced_metrics', store=False
    )
    avg_days_to_invoice = fields.Float(
        string='Avg Days to Invoice', compute='_compute_enhanced_metrics', store=False
    )
    avg_days_to_payment = fields.Float(
        string='Avg Days to Payment', compute='_compute_enhanced_metrics', store=False
    )

    chart_sales_by_type = fields.Json(
        string='Chart Sales by Type', compute='_compute_chart_sales_by_type'
    )
    chart_booking_trend = fields.Json(
        string='Chart Booking Trend', compute='_compute_chart_booking_trend'
    )
    chart_payment_state = fields.Json(
        string='Chart Payment State', compute='_compute_chart_payment_state'
    )
    chart_sales_funnel = fields.Json(
        string='Sales Funnel', compute='_compute_chart_sales_funnel'
    )
    chart_top_customers = fields.Json(
        string='Top Customers Outstanding', compute='_compute_chart_top_customers'
    )
    chart_agent_performance = fields.Json(
        string='Agent Performance', compute='_compute_chart_agent_performance'
    )

    # Tabular data (HTML renders)
    table_order_type_html = fields.Html(string='Order Type Analysis', compute='_compute_table_order_type_html', sanitize=False)
    table_agent_commission_html = fields.Html(string='Agent Commission Breakdown', compute='_compute_table_agent_commission_html', sanitize=False)
    table_detailed_orders_html = fields.Html(string='Detailed Orders', compute='_compute_table_detailed_orders_html', sanitize=False)
    table_invoice_aging_html = fields.Html(string='Invoice Aging', compute='_compute_table_invoice_aging_html', sanitize=False)
    table_product_analysis_html = fields.Html(
        string='Product Analysis Table',
        compute='_compute_table_product_analysis_html',
        sanitize=False
    )
    table_daily_sales_html = fields.Html(
        string='Daily Sales Table',
        compute='_compute_table_daily_sales_html',
        sanitize=False
    )
    table_customer_activity_html = fields.Html(
        string='Customer Activity Table',
        compute='_compute_table_customer_activity_html',
        sanitize=False
    )

    def _get_order_domain(self):
        domain = [('state', 'in', ['sale', 'done'])]
        # Multi-select takes precedence if set
        if self.sales_order_type_ids:
            domain.append(('sale_order_type_id', 'in', self.sales_order_type_ids.ids))
        elif self.sales_order_type_id:
            domain.append(('sale_order_type_id', '=', self.sales_order_type_id.id))
        if self.invoice_status_filter and self.invoice_status_filter != 'all':
            domain.append(('invoice_status', '=', self.invoice_status_filter))
        if self.booking_date_from:
            domain.append(('booking_date', '>=', self.booking_date_from))
        if self.booking_date_to:
            domain.append(('booking_date', '<=', self.booking_date_to))
        # Salesperson in this environment maps to internal agent1 partner
        if self.agent_partner_id:
            domain.append(('agent1_partner_id', '=', self.agent_partner_id.id))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        return domain

    def _get_invoice_domain(self, include_payment_filter=True, unpaid_only=False):
        domain = [
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        order_ids = []
        order_domain = self._get_order_domain()
        if order_domain:
            orders = self.env['sale.order'].search(order_domain)
            order_ids = orders.ids
            if order_ids:
                domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
        if unpaid_only:
            domain.append(('payment_state', 'in', ['not_paid', 'partial', 'in_payment']))
        if include_payment_filter and self.payment_status_filter and self.payment_status_filter != 'all':
            domain.append(('payment_state', '=', self.payment_status_filter))
        return domain

    @api.model
    def create(self, vals):
        # Set defaults only on creation if not already set
        if 'booking_date_from' not in vals:
            vals['booking_date_from'] = date.today().replace(day=1)
        if 'booking_date_to' not in vals:
            vals['booking_date_to'] = date.today()
        if 'invoice_status_filter' not in vals:
            vals['invoice_status_filter'] = 'all'
        if 'payment_status_filter' not in vals:
            vals['payment_status_filter'] = 'all'
        return super(SalesInvoicingDashboard, self).create(vals)

    @api.onchange(
        'sales_order_type_id',
        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _onchange_filters(self):
        # Trigger recomputation when any filter changes
        pass

    @api.depends(
        'sales_order_type_id',
        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_metrics(self):
        # Invalidate cache to ensure fresh data from DB on every computation
        self.env.invalidate_all()
        for rec in self:
            order_domain = rec._get_order_domain()

            matching_orders = self.env['sale.order'].search(order_domain)
            order_ids = matching_orders.ids

            # Total booked sales (confirmed orders in range)
            rec.total_booked_sales = sum(matching_orders.mapped('amount_total'))

            # Posted invoices count and total amount (filtered by selected orders and payment status if provided)
            posted_domain = [
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ]
            if order_ids:
                posted_domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
            if rec.payment_status_filter and rec.payment_status_filter != 'all':
                posted_domain.append(('payment_state', '=', rec.payment_status_filter))
            
            posted_invoices = self.env['account.move'].search(posted_domain)
            rec.posted_invoice_count = len(posted_invoices)
            rec.total_invoiced_amount = sum(posted_invoices.mapped('amount_total'))

            # Orders to invoice count and total pending amount (respecting filters, but always focusing 'to invoice')
            pending_domain = list(order_domain)
            # If invoice_status_filter is 'all', focus on 'to invoice'
            if rec.invoice_status_filter == 'all':
                # Replace any existing invoice_status in order_domain
                pending_domain = [d for d in pending_domain if not (isinstance(d, tuple) and d[0] == 'invoice_status')]
                pending_domain.append(('invoice_status', '=', 'to invoice'))
            
            pending_orders = self.env['sale.order'].search(pending_domain)
            rec.pending_to_invoice_order_count = len(pending_orders)
            rec.total_pending_amount = sum(pending_orders.mapped('amount_to_invoice'))

            # Unpaid invoices count (filtered by orders and payment status)
            unpaid_domain = [
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('payment_state', 'in', ['not_paid', 'partial', 'in_payment']),
            ]
            if order_ids:
                unpaid_domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
            if rec.payment_status_filter and rec.payment_status_filter != 'all':
                # Override the payment_state list with the selected filter
                unpaid_domain = [d for d in unpaid_domain if not (isinstance(d, tuple) and d[0] == 'payment_state')]
                unpaid_domain.append(('payment_state', '=', rec.payment_status_filter))
            unpaid_invoices = self.env['account.move'].search(unpaid_domain)
            rec.unpaid_invoice_count = len(unpaid_invoices)

            # Amount to collect / collected
            rec.amount_to_collect = sum(unpaid_invoices.mapped('amount_residual'))
            rec.amount_collected = rec.total_invoiced_amount - rec.amount_to_collect

            # Commission due (commission_ax): pending/partial on confirmed/processed
            commission_due_total = 0.0
            if order_ids:
                cl_domain = [
                    ('sale_order_id', 'in', order_ids),
                    ('state', 'in', ['confirmed', 'processed']),
                    ('payment_status', 'in', ['pending', 'partial']),
                ]
                CommissionLine = self.env['commission.line']
                lines = CommissionLine.search(cl_domain)
                company = self.env.company
                for line in lines:
                    # Convert outstanding_amount to company currency
                    line_currency = line.currency_id or company.currency_id
                    amount = line.outstanding_amount
                    commission_due_total += line_currency._convert(
                        amount, company.currency_id, company, rec.booking_date_to or fields.Date.context_today(self)
                    )
            rec.commission_due = commission_due_total

    @api.depends(
        'sales_order_type_id',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
    )
    def _compute_chart_sales_by_type(self):
        self.env.invalidate_all()
        palette = ['#0060df', '#00a651', '#f0ad4e', '#d9534f', '#5bc0de', '#7b7b7b']
        for rec in self:
            domain = rec._get_order_domain()
            groups = self.env['sale.order'].read_group(
                domain, ['amount_total'], ['sale_order_type_id'], orderby='amount_total DESC'
            )
            labels = []
            data = []
            for idx, group in enumerate(groups):
                label = group['sale_order_type_id'][1] if group.get('sale_order_type_id') else 'Unspecified'
                labels.append(label)
                data.append(group.get('amount_total', 0.0))
            colors = [palette[i % len(palette)] for i in range(len(data))]
            rec.chart_sales_by_type = {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Sales Amount',
                        'data': data,
                        'backgroundColor': colors,
                        'borderColor': colors,
                        'borderWidth': 1,
                    }
                ],
            }

    @api.depends(
        'sales_order_type_id',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
    )
    def _compute_chart_booking_trend(self):
        self.env.invalidate_all()
        palette = ['#0060df']
        for rec in self:
            labels = []
            data = []
            try:
                domain = rec._get_order_domain()
                groups = self.env['sale.order'].read_group(
                    domain,
                    ['amount_total'],
                    ['booking_date:month'],
                    orderby='booking_date:month',
                    lazy=False
                )
                for group in groups:
                    # Safe dict access - don't trigger field machinery
                    month_label = str(group.get('booking_date:month') or 'Unspecified')
                    labels.append(month_label)
                    data.append(float(group.get('amount_total', 0) or 0))
            except Exception:
                # If any error occurs, show empty chart
                labels = ['No data available']
                data = [0]

            rec.chart_booking_trend = {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Booking Amount',
                        'data': data,
                        'backgroundColor': palette[0],
                        'borderColor': palette[0],
                        'fill': False,
                        'tension': 0.3,
                        'borderWidth': 2,
                    }
                ],
            }

    @api.depends(
        'sales_order_type_id',
        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_chart_payment_state(self):
        self.env.invalidate_all()
        palette = ['#5bc0de', '#f0ad4e', '#d9534f', '#00a651']
        for rec in self:
            domain = rec._get_invoice_domain(include_payment_filter=False, unpaid_only=False)
            groups = self.env['account.move'].read_group(
                domain,
                ['amount_total', 'payment_state'],
                ['payment_state'],
            )
            labels = []
            data = []
            # Friendly names for payment states
            state_names = {
                'not_paid': 'Not Paid',
                'partial': 'Partially Paid',
                'in_payment': 'In Payment',
                'paid': 'Paid',
            }
            for group in groups:
                payment_state = group.get('payment_state') or 'unknown'
                label = state_names.get(payment_state, str(payment_state))
                labels.append(label)
                data.append(group.get('amount_total', 0.0))
            colors = [palette[i % len(palette)] for i in range(len(data))]
            rec.chart_payment_state = {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Invoice Amount by Payment State',
                        'data': data,
                        'backgroundColor': colors,
                        'borderColor': colors,
                        'borderWidth': 1,
                    }
                ],
            }

    def _compute_chart_sales_funnel(self):
        self.env.invalidate_all()
        for rec in self:
            data = [
                float(rec.total_booked_sales or 0.0),
                float(rec.total_invoiced_amount or 0.0),
                float(rec.amount_collected or 0.0),
            ]
            rec.chart_sales_funnel = {
                'labels': ['Booked Sales', 'Invoiced', 'Collected'],
                'datasets': [{
                    'label': 'Flow',
                    'data': data,
                    'backgroundColor': ['#3498db', '#f39c12', '#27ae60'],
                    'borderColor': ['#3498db', '#f39c12', '#27ae60'],
                    'borderWidth': 1,
                }],
            }

    def _compute_chart_top_customers(self):
        self.env.invalidate_all()
        for rec in self:
            domain = rec._get_invoice_domain(include_payment_filter=False, unpaid_only=True)
            groups = self.env['account.move'].read_group(
                domain, ['amount_residual', 'partner_id'], ['partner_id']
            )
            # Sort and take top 10
            groups = sorted(groups, key=lambda g: g.get('amount_residual', 0.0), reverse=True)[:10]
            labels = [((g.get('partner_id') or ['', ''])[1] or '') for g in groups]
            data = [g.get('amount_residual', 0.0) for g in groups]
            rec.chart_top_customers = {
                'labels': labels,
                'datasets': [{
                    'label': 'Outstanding',
                    'data': data,
                    'backgroundColor': '#d9534f',
                    'borderColor': '#d9534f',
                    'borderWidth': 1,
                }],
            }

    def _compute_chart_agent_performance(self):
        self.env.invalidate_all()
        for rec in self:
            order_ids = self.env['sale.order'].search(rec._get_order_domain()).ids
            labels, total_vals, paid_vals, out_vals = [], [], [], []
            if order_ids:
                # Only internal commissions (staff/agents)
                cl_domain = [('sale_order_id', 'in', order_ids), ('commission_category', '=', 'internal')]
                groups = self.env['commission.line'].read_group(
                    cl_domain,
                    ['commission_amount', 'paid_amount', 'partner_id', 'currency_id'],
                    ['partner_id']
                )
                company = self.env.company
                for g in groups:
                    partner = (g.get('partner_id') or ['', ''])
                    name = partner[1] or 'Agent'
                    labels.append(name)
                    # Convert sums to company currency (approx: use first line currency if mixed)
                    amt = float(g.get('commission_amount', 0.0) or 0.0)
                    paid = float(g.get('paid_amount', 0.0) or 0.0)
                    # No currency aggregation in read_group; fallback assumes company currency
                    total_vals.append(amt)
                    paid_vals.append(paid)
                    out_vals.append(max(amt - paid, 0.0))
            rec.chart_agent_performance = {
                'labels': labels,
                'datasets': [
                    {'label': 'Total', 'data': total_vals, 'backgroundColor': '#0060df'},
                    {'label': 'Collected', 'data': paid_vals, 'backgroundColor': '#27ae60'},
                    {'label': 'Outstanding', 'data': out_vals, 'backgroundColor': '#d9534f'},
                ],
            }

    # --------------------
    # Helper dataset builders
    # --------------------
    def _get_order_type_rows(self):
        domain = self._get_order_domain()
        groups = self.env['sale.order'].read_group(
            domain, ['amount_total', 'id:count'], ['sale_order_type_id']
        )
        rows = []
        for g in groups:
            type_name = (g.get('sale_order_type_id') or ['', ''])[1] or 'Unspecified'
            type_domain = list(domain)
            if g.get('sale_order_type_id'):
                type_domain.append(('sale_order_type_id', '=', g['sale_order_type_id'][0]))
            else:
                type_domain.append(('sale_order_type_id', '=', False))
            orders = self.env['sale.order'].search(type_domain)
            total_sales = sum(orders.mapped('amount_total'))
            to_invoice = sum(orders.filtered(lambda o: o.invoice_status == 'to invoice').mapped('amount_total'))
            invoices = orders.mapped('invoice_ids').filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
            invoiced = sum(invoices.mapped('amount_total'))
            outstanding = sum(invoices.mapped('amount_residual'))
            collected = max(invoiced - outstanding, 0.0)
            rate = (collected / invoiced * 100.0) if invoiced else 0.0
            status = 'Good' if rate >= 90 else ('Attention' if rate >= 70 else 'Critical')
            color = 'success' if rate >= 90 else ('warning' if rate >= 70 else 'danger')
            rows.append({
                'name': type_name,
                'count': len(orders),
                'total_sales': total_sales,
                'to_invoice': to_invoice,
                'invoiced': invoiced,
                'outstanding': outstanding,
                'collected': collected,
                'rate': rate,
                'status': status,
                'status_color': color,
            })
        return rows

    def _fmt_money(self, amount):
        curr = self.env.company.currency_id
        return f"{curr.symbol or ''}{amount:,.2f}"

    def _compute_table_order_type_html(self):
        self.env.invalidate_all()
        for rec in self:
            rows = rec._get_order_type_rows()
            html = [
                '<table class="table table-sm table-striped table-hover">',
                '<thead><tr>',
                '<th>Order Type</th><th>Order Count</th><th>Total Sales</th>'
                '<th>To Invoice</th><th>Invoiced</th><th>Outstanding</th>'
                '<th>Collected</th><th>Collection %</th><th>Status</th>',
                '</tr></thead><tbody>'
            ]
            # accumulate totals
            tot_count = 0
            tot_sales = 0.0
            tot_to_inv = 0.0
            tot_inv = 0.0
            tot_out = 0.0
            tot_coll = 0.0
            for r in rows:
                html.append('<tr>')
                html.append(f'<td>{r["name"]}</td>')
                html.append(f'<td>{r["count"]}</td>')
                html.append(f'<td>{rec._fmt_money(r["total_sales"])}</td>')
                html.append(f'<td>{rec._fmt_money(r["to_invoice"])}</td>')
                html.append(f'<td>{rec._fmt_money(r["invoiced"])}</td>')
                html.append(f'<td>{rec._fmt_money(r["outstanding"])}</td>')
                html.append(f'<td>{rec._fmt_money(r["collected"])}</td>')
                html.append(f'<td>{r["rate"]:.1f}%</td>')
                html.append(f'<td><span class="badge badge-{r["status_color"]}">{r["status"]}</span></td>')
                html.append('</tr>')
                tot_count += int(r['count'] or 0)
                tot_sales += float(r['total_sales'] or 0.0)
                tot_to_inv += float(r['to_invoice'] or 0.0)
                tot_inv += float(r['invoiced'] or 0.0)
                tot_out += float(r['outstanding'] or 0.0)
                tot_coll += float(r['collected'] or 0.0)
            html.append('</tbody></table>')
            # add totals footer
            total_rate = (tot_coll / tot_inv * 100.0) if tot_inv else 0.0
            footer = [
                '<tfoot><tr>',
                '<th>Total</th>',
                f'<th>{tot_count}</th>',
                f'<th>{rec._fmt_money(tot_sales)}</th>',
                f'<th>{rec._fmt_money(tot_to_inv)}</th>',
                f'<th>{rec._fmt_money(tot_inv)}</th>',
                f'<th>{rec._fmt_money(tot_out)}</th>',
                f'<th>{rec._fmt_money(tot_coll)}</th>',
                f'<th>{total_rate:.1f}%</th>',
                '<th>-</th>',
                '</tr></tfoot>'
            ]
            html.insert(2, ''.join(footer))  # insert footer after thead for visibility
            rec.table_order_type_html = ''.join(html)

    def _compute_table_agent_commission_html(self):
        self.env.invalidate_all()
        for rec in self:
            order_ids = self.env['sale.order'].search(rec._get_order_domain()).ids
            html = [
                '<table class="table table-sm table-striped table-hover">',
                '<thead><tr>',
                '<th>Agent</th><th>Lines</th><th>Total</th><th>Paid</th><th>Outstanding</th><th>Status</th>',
                '</tr></thead><tbody>'
            ]
            total_lines = 0
            total_amount = 0.0
            total_paid = 0.0
            total_outstanding = 0.0
            if order_ids:
                groups = self.env['commission.line'].read_group(
                    [('sale_order_id', 'in', order_ids), ('commission_category', '=', 'internal')],
                    ['commission_amount', 'paid_amount', 'id:count', 'partner_id'],
                    ['partner_id']
                )
                for g in groups:
                    name = (g.get('partner_id') or ['', ''])[1] or 'Agent'
                    total = float(g.get('commission_amount', 0.0) or 0.0)
                    paid = float(g.get('paid_amount', 0.0) or 0.0)
                    out = max(total - paid, 0.0)
                    status = 'Paid' if out == 0 else ('Partial' if paid > 0 else 'Pending')
                    color = 'success' if out == 0 else ('warning' if paid > 0 else 'danger')
                    count = int(g.get('id_count', 0) or g.get('__count', 0) or 0)
                    html.append('<tr>')
                    html.append(f'<td>{name}</td>')
                    html.append(f'<td>{count}</td>')
                    html.append(f'<td>{rec._fmt_money(total)}</td>')
                    html.append(f'<td>{rec._fmt_money(paid)}</td>')
                    html.append(f'<td>{rec._fmt_money(out)}</td>')
                    html.append(f'<td><span class="badge badge-{color}">{status}</span></td>')
                    html.append('</tr>')
                    total_lines += count
                    total_amount += total
                    total_paid += paid
                    total_outstanding += out
            html.append('</tbody></table>')
            footer = [
                '<tfoot><tr>',
                '<th>Total</th>',
                f'<th>{total_lines}</th>',
                f'<th>{rec._fmt_money(total_amount)}</th>',
                f'<th>{rec._fmt_money(total_paid)}</th>',
                f'<th>{rec._fmt_money(total_outstanding)}</th>',
                '<th>-</th>',
                '</tr></tfoot>'
            ]
            html.insert(2, ''.join(footer))
            rec.table_agent_commission_html = ''.join(html)

    def _compute_table_detailed_orders_html(self):
        self.env.invalidate_all()
        today = fields.Date.context_today(self)
        for rec in self:
            orders = self.env['sale.order'].search(rec._get_order_domain(), order='booking_date desc, id desc', limit=50)
            html = [
                '<table class="table table-sm table-striped table-hover">',
                '<thead><tr>',
                '<th>Order</th><th>Booking Date</th><th>Type</th><th>Customer</th><th>Salesperson</th>'
                '<th>Status</th><th>Amount</th><th>Invoiced</th><th>Outstanding</th>'
                '<th>Invoice Status</th><th>Payment Status</th><th>Days Since</th><th>Action Required</th>',
                '</tr></thead><tbody>'
            ]
            tot_orders = 0
            tot_amount = 0.0
            tot_invoiced = 0.0
            tot_outstanding = 0.0
            for o in orders:
                invs = o.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
                invoiced = sum(invs.mapped('amount_total'))
                outstanding = sum(invs.mapped('amount_residual'))
                # payment status heuristic
                if invoiced and outstanding == 0:
                    pay_status = 'Paid'
                elif invoiced and outstanding > 0:
                    # overdue check
                    overdue = any([inv.invoice_date_due and inv.invoice_date_due < today and (inv.amount_residual or 0) > 0 for inv in invs])
                    pay_status = 'Overdue' if overdue else 'Pending'
                else:
                    pay_status = '-'
                days_since = (today - (o.booking_date or today)).days if o.booking_date else 0
                if o.invoice_status == 'to invoice':
                    action = 'Invoice Pending'
                elif invoiced and outstanding > 0:
                    action = 'Payment Overdue' if 'Overdue' in pay_status else 'Payment Pending'
                else:
                    action = '-'
                html.append('<tr>')
                html.append(f'<td>{o.name}</td>')
                html.append(f'<td>{o.booking_date or ""}</td>')
                html.append(f'<td>{o.sale_order_type_id.name or ""}</td>')
                html.append(f'<td>{o.partner_id.name or ""}</td>')
                html.append(f'<td>{getattr(o, "agent1_partner_id").name if hasattr(o, "agent1_partner_id") and o.agent1_partner_id else ""}</td>')
                html.append(f'<td>{o.state}</td>')
                html.append(f'<td>{rec._fmt_money(o.amount_total)}</td>')
                html.append(f'<td>{rec._fmt_money(invoiced)}</td>')
                html.append(f'<td>{rec._fmt_money(outstanding)}</td>')
                html.append(f'<td>{o.invoice_status}</td>')
                html.append(f'<td>{pay_status}</td>')
                html.append(f'<td>{days_since}</td>')
                html.append(f'<td>{action}</td>')
                html.append('</tr>')
                tot_orders += 1
                tot_amount += float(o.amount_total or 0.0)
                tot_invoiced += float(invoiced or 0.0)
                tot_outstanding += float(outstanding or 0.0)
            html.append('</tbody></table>')
            footer = [
                '<tfoot><tr>',
                '<th>Total</th>',
                f'<th>{tot_orders}</th>',
                '<th></th><th></th><th></th>',
                '<th></th>',
                f'<th>{rec._fmt_money(tot_amount)}</th>',
                f'<th>{rec._fmt_money(tot_invoiced)}</th>',
                f'<th>{rec._fmt_money(tot_outstanding)}</th>',
                '<th></th><th></th><th></th><th></th>',
                '</tr></tfoot>'
            ]
            html.insert(2, ''.join(footer))
            rec.table_detailed_orders_html = ''.join(html)

    def _compute_table_invoice_aging_html(self):
        self.env.invalidate_all()
        today = fields.Date.context_today(self)
        for rec in self:
            domain = rec._get_invoice_domain(include_payment_filter=False, unpaid_only=True)
            invs = self.env['account.move'].search(domain)
            buckets = {
                'current': {'label': 'Current (Not Due)', 'count': 0, 'amount': 0.0},
                '1_30': {'label': '1-30 Days', 'count': 0, 'amount': 0.0},
                '31_60': {'label': '31-60 Days', 'count': 0, 'amount': 0.0},
                '61_90': {'label': '61-90 Days', 'count': 0, 'amount': 0.0},
                '90_plus': {'label': '90+ Days Overdue', 'count': 0, 'amount': 0.0},
            }
            total_amt = 0.0
            total_count = 0
            for inv in invs:
                amt = inv.amount_residual or 0.0
                total_amt += amt
                due = inv.invoice_date_due
                if not due or due >= today:
                    key = 'current'
                else:
                    delta = (today - due).days
                    if delta <= 30:
                        key = '1_30'
                    elif delta <= 60:
                        key = '31_60'
                    elif delta <= 90:
                        key = '61_90'
                    else:
                        key = '90_plus'
                buckets[key]['count'] += 1
                buckets[key]['amount'] += amt
                total_count += 1

            html = [
                '<table class="table table-sm table-striped table-hover">',
                '<thead><tr><th>Aging Bucket</th><th>Count</th><th>Amount</th><th>% of Total</th></tr></thead><tbody>'
            ]
            for key in ['current','1_30','31_60','61_90','90_plus']:
                b = buckets[key]
                pct = (b['amount'] / total_amt * 100.0) if total_amt else 0.0
                html.append('<tr>')
                html.append(f'<td>{b["label"]}</td>')
                html.append(f'<td>{b["count"]}</td>')
                html.append(f'<td>{rec._fmt_money(b["amount"])}</td>')
                html.append(f'<td>{pct:.1f}%</td>')
                html.append('</tr>')
            html.append('</tbody></table>')
            footer = [
                '<tfoot><tr>',
                '<th>Total</th>',
                f'<th>{total_count}</th>',
                f'<th>{rec._fmt_money(total_amt)}</th>',
                '<th>100.0%</th>',
                '</tr></tfoot>'
            ]
            html.insert(2, ''.join(footer))
            rec.table_invoice_aging_html = ''.join(html)

    # --------------------
    # Export helpers (act_url)
    # --------------------
    @api.depends('booking_date_from', 'booking_date_to', 'sales_order_type_ids', 'agent_partner_id', 'partner_id')
    def _compute_performance_metrics(self):
        """Compute additional performance metrics"""
        for record in self:
            domain = record._get_order_domain()
            
            # Get all sales orders
            orders = self.env['sale.order'].search(domain)
            orders_count = len(orders)
            
            # Average Order Value
            if orders_count > 0:
                record.average_order_value = sum(orders.mapped('amount_total')) / orders_count
            else:
                record.average_order_value = 0.0
            
            # Conversion Rate (confirmed orders / total orders including quotes)
            all_orders_domain = domain.copy()
            if ('state', '=', 'sale') in domain:
                domain_without_state = [d for d in all_orders_domain if d != ('state', '=', 'sale')]
                all_orders = self.env['sale.order'].search(domain_without_state)
                total_count = len(all_orders)
                if total_count > 0:
                    record.conversion_rate = (orders_count / total_count) * 100
                else:
                    record.conversion_rate = 0.0
            else:
                record.conversion_rate = 0.0
            
            # Orders and Invoices Count
            record.total_orders_count = orders_count
            
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', record.booking_date_from),
                ('invoice_date', '<=', record.booking_date_to),
                ('state', '=', 'posted')
            ])
            record.total_invoices_count = len(invoices)
            
            # Pending orders (booked but not fully invoiced)
            pending = orders.filtered(lambda o: o.invoice_status in ['to invoice', 'invoiced'])
            record.pending_orders_count = len(pending)
            
            # Collection Efficiency
            if record.total_invoiced_amount > 0:
                record.collection_efficiency = (record.amount_collected / record.total_invoiced_amount) * 100
            else:
                record.collection_efficiency = 0.0
            
            # Outstanding Amount
            record.outstanding_amount = record.amount_to_collect - record.amount_collected
            
            # Daily Sales Average
            if record.booking_date_from and record.booking_date_to:
                days = (record.booking_date_to - record.booking_date_from).days + 1
                if days > 0:
                    record.daily_sales_average = record.total_booked_sales / days
                else:
                    record.daily_sales_average = 0.0
            else:
                record.daily_sales_average = 0.0


    def _export_url(self, endpoint):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f"/osus_dashboard/export/{endpoint}?rec_id={self.id}",
            'target': 'self',
        }

    def action_export_order_types_csv(self):
        return self._export_url('order_types')

    def action_export_agent_commissions_csv(self):
        return self._export_url('agent_commissions')

    def action_export_detailed_orders_csv(self):
        return self._export_url('detailed_orders')

    def action_export_invoice_aging_csv(self):
        return self._export_url('invoice_aging')

    @api.depends('booking_date_from', 'booking_date_to', 'sales_order_type_ids')
    def _compute_table_product_analysis_html(self):
        """Generate product/service analysis table"""
        for rec in self:
            domain = rec._get_order_domain()
            orders = self.env['sale.order'].search(domain)
            
            # Group by product
            product_data = {}
            for order in orders:
                for line in order.order_line:
                    if not line.product_id:
                        continue
                    product_name = line.product_id.name
                    if product_name not in product_data:
                        product_data[product_name] = {
                            'qty': 0,
                            'amount': 0,
                            'orders': set()
                        }
                    product_data[product_name]['qty'] += line.product_uom_qty
                    product_data[product_name]['amount'] += line.price_subtotal
                    product_data[product_name]['orders'].add(order.id)
            
            # Convert to list and sort by amount
            products = [
                {
                    'name': name,
                    'qty': data['qty'],
                    'amount': data['amount'],
                    'orders': len(data['orders'])
                }
                for name, data in product_data.items()
            ]
            products.sort(key=lambda x: x['amount'], reverse=True)
            
            # Generate HTML table
            html = ['<table class="table table-sm table-hover">']
            html.append('<thead class="table-light">')
            html.append('<tr><th>Product/Service</th><th>Qty</th><th>Orders</th><th>Amount</th></tr>')
            html.append('</thead><tbody>')
            
            for p in products[:20]:  # Top 20
                html.append('<tr>')
                html.append(f'<td>{p["name"]}</td>')
                html.append(f'<td>{p["qty"]:.0f}</td>')
                html.append(f'<td>{p["orders"]}</td>')
                html.append(f'<td>{rec._fmt_money(p["amount"])}</td>')
                html.append('</tr>')
            
            html.append('</tbody></table>')
            rec.table_product_analysis_html = ''.join(html) if products else '<p>No data</p>'

    @api.depends('booking_date_from', 'booking_date_to', 'sales_order_type_ids')
    def _compute_table_daily_sales_html(self):
        """Generate daily sales breakdown table"""
        for rec in self:
            if not rec.booking_date_from or not rec.booking_date_to:
                rec.table_daily_sales_html = '<p>Please select a date range</p>'
                continue
                
            domain = rec._get_order_domain()
            orders = self.env['sale.order'].search(domain)
            
            # Group by date
            daily_data = {}
            for order in orders:
                if order.booking_date:
                    date_str = order.booking_date.strftime('%Y-%m-%d')
                    if date_str not in daily_data:
                        daily_data[date_str] = {
                            'count': 0,
                            'amount': 0
                        }
                    daily_data[date_str]['count'] += 1
                    daily_data[date_str]['amount'] += order.amount_total
            
            # Sort by date descending
            daily_list = [
                {'date': date, 'count': data['count'], 'amount': data['amount']}
                for date, data in daily_data.items()
            ]
            daily_list.sort(key=lambda x: x['date'], reverse=True)
            
            # Generate HTML
            html = ['<table class="table table-sm table-striped">']
            html.append('<thead class="table-dark">')
            html.append('<tr><th>Date</th><th>Orders</th><th>Amount</th><th>Avg/Order</th></tr>')
            html.append('</thead><tbody>')
            
            for day in daily_list:
                avg = day['amount'] / day['count'] if day['count'] > 0 else 0
                html.append('<tr>')
                html.append(f'<td>{day["date"]}</td>')
                html.append(f'<td>{day["count"]}</td>')
                html.append(f'<td>{rec._fmt_money(day["amount"])}</td>')
                html.append(f'<td>{rec._fmt_money(avg)}</td>')
                html.append('</tr>')
            
            html.append('</tbody></table>')
            rec.table_daily_sales_html = ''.join(html) if daily_list else '<p>No data</p>'

    @api.depends('booking_date_from', 'booking_date_to', 'sales_order_type_ids', 'partner_id')
    def _compute_table_customer_activity_html(self):
        """Generate customer activity summary table"""
        for rec in self:
            domain = rec._get_order_domain()
            orders = self.env['sale.order'].search(domain)
            
            # Group by customer
            customer_data = {}
            for order in orders:
                customer = order.partner_id
                if not customer:
                    continue
                    
                cust_id = customer.id
                if cust_id not in customer_data:
                    customer_data[cust_id] = {
                        'name': customer.name,
                        'orders': 0,
                        'amount': 0,
                        'invoiced': 0,
                        'paid': 0
                    }
                
                customer_data[cust_id]['orders'] += 1
                customer_data[cust_id]['amount'] += order.amount_total
                
                # Get invoices for this order
                for invoice in order.invoice_ids.filtered(lambda i: i.state == 'posted'):
                    customer_data[cust_id]['invoiced'] += invoice.amount_total
                    if invoice.payment_state == 'paid':
                        customer_data[cust_id]['paid'] += invoice.amount_total
            
            # Convert to list and sort by amount
            customers = [
                {
                    'name': data['name'],
                    'orders': data['orders'],
                    'amount': data['amount'],
                    'invoiced': data['invoiced'],
                    'paid': data['paid'],
                    'outstanding': data['invoiced'] - data['paid']
                }
                for cust_id, data in customer_data.items()
            ]
            customers.sort(key=lambda x: x['amount'], reverse=True)
            
            # Generate HTML
            html = ['<table class="table table-sm table-bordered">']
            html.append('<thead class="table-primary">')
            html.append('<tr><th>Customer</th><th>Orders</th><th>Booked</th><th>Invoiced</th><th>Paid</th><th>Outstanding</th></tr>')
            html.append('</thead><tbody>')
            
            for c in customers[:25]:  # Top 25
                html.append('<tr>')
                html.append(f'<td>{c["name"]}</td>')
                html.append(f'<td>{c["orders"]}</td>')
                html.append(f'<td>{rec._fmt_money(c["amount"])}</td>')
                html.append(f'<td>{rec._fmt_money(c["invoiced"])}</td>')
                html.append(f'<td>{rec._fmt_money(c["paid"])}</td>')
                html.append(f'<td class="{"text-danger" if c["outstanding"] > 0 else ""}">{rec._fmt_money(c["outstanding"])}</td>')
                html.append('</tr>')
            
            html.append('</tbody></table>')
            rec.table_customer_activity_html = ''.join(html) if customers else '<p>No data</p>'

    def action_open_posted_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = [
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        order_domain = [('state', 'in', ['sale', 'done'])]
        if self.sales_order_type_id:
            order_domain.append(('sale_order_type_id', '=', self.sales_order_type_id.id))
        if self.invoice_status_filter and self.invoice_status_filter != 'all':
            order_domain.append(('invoice_status', '=', self.invoice_status_filter))
        if self.booking_date_from:
            order_domain.append(('booking_date', '>=', self.booking_date_from))
        if self.booking_date_to:
            order_domain.append(('booking_date', '<=', self.booking_date_to))
        orders = self.env['sale.order'].search(order_domain)
        if orders:
            domain.append(('line_ids.sale_line_ids.order_id', 'in', orders.ids))
        if self.payment_status_filter and self.payment_status_filter != 'all':
            domain.append(('payment_state', '=', self.payment_status_filter))
        action['domain'] = domain
        action['context'] = {'search_default_posted': 1}
        return action

    def action_open_pending_orders(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = [('state', 'in', ['sale', 'done'])]
        if self.invoice_status_filter == 'all':
            domain.append(('invoice_status', '=', 'to invoice'))
        else:
            domain.append(('invoice_status', '=', self.invoice_status_filter))
        if self.sales_order_type_id:
            domain.append(('sale_order_type_id', '=', self.sales_order_type_id.id))
        if self.booking_date_from:
            domain.append(('booking_date', '>=', self.booking_date_from))
        if self.booking_date_to:
            domain.append(('booking_date', '<=', self.booking_date_to))
        action['domain'] = domain
        action['context'] = {
            'search_default_sale': 1,
            'search_default_done': 1,
        }
        return action

    def action_open_unpaid_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = self._get_invoice_domain(include_payment_filter=True, unpaid_only=True)
        action['domain'] = domain
        action['context'] = {'search_default_unpaid': 1}
        return action

    def action_open_sales_graph(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        action['domain'] = domain
        action['view_mode'] = 'graph,tree,pivot,form'
        action['context'] = {
            'search_default_sale': 1,
            'search_default_done': 1,
            'graph_measure': 'amount_total',
            'graph_groupby': 'sale_order_type_id',
        }
        return action

    def action_open_invoice_payment_graph(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = self._get_invoice_domain(include_payment_filter=True)
        action['domain'] = domain
        action['view_mode'] = 'graph,tree,pivot'
        action['context'] = {
            'search_default_posted': 1,
            'graph_measure': 'amount_total',
            'graph_groupby': 'payment_state',
        }
        return action

    def action_open_booking_trend_graph(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        action['domain'] = domain
        action['view_mode'] = 'graph,tree,pivot,form'
        action['context'] = {
            'search_default_sale': 1,
            'search_default_done': 1,
            'graph_measure': 'amount_total',
            'graph_groupby': 'booking_date:month',
        }
        return action
