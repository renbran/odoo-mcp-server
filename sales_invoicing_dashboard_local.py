# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import ormcache
from datetime import date


class SalesInvoicingDashboard(models.Model):
    _name = 'osus.sales.invoicing.dashboard'
    _rec_name = 'name'
    _description = 'Sales & Invoicing Dashboard'

    # Simple label so the record always has a display name in forms/kanban
    name = fields.Char(default='Sales & Invoicing Dashboard', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    # Filters
    sales_order_type_ids = fields.Many2many(
        'sale.order.type', string='Sales Order Types',
        help='Filter by one or more order types - leave empty to include all'
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
        string='Posted Invoices', compute='_compute_metrics', store=False, compute_sudo=True
    )
    pending_to_invoice_order_count = fields.Integer(
        string='Orders To Invoice', compute='_compute_metrics', store=False, compute_sudo=True
    )
    unpaid_invoice_count = fields.Integer(
        string='Unpaid Invoices', compute='_compute_metrics', store=False, compute_sudo=True
    )
    total_invoiced_amount = fields.Monetary(
        string='Total Invoiced Amount', compute='_compute_metrics', store=False, compute_sudo=True,
        currency_field='company_currency_id'
    )
    total_pending_amount = fields.Monetary(
        string='Total Pending to Invoice', compute='_compute_metrics', store=False, compute_sudo=True,
        currency_field='company_currency_id'
    )
    # Extended KPIs
    total_booked_sales = fields.Monetary(
        string='Total Sales Value', compute='_compute_metrics', store=False, compute_sudo=True,
        currency_field='company_currency_id'
    )
    amount_to_collect = fields.Monetary(
        string='Amount to Collect', compute='_compute_metrics', store=False, compute_sudo=True,
        currency_field='company_currency_id'
    )
    amount_collected = fields.Monetary(
        string='Amount Collected', compute='_compute_metrics', store=False, compute_sudo=True,
        currency_field='company_currency_id'
    )
    commission_due = fields.Monetary(
        string='Commission Due', compute='_compute_metrics', store=False, compute_sudo=True,
        currency_field='company_currency_id'
    )
    company_currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )

    _sql_constraints = [
        ('unique_name_singleton', 'unique(name)', 'Only one dashboard record is allowed!')
    ]

    chart_sales_by_type = fields.Json(
        string='Chart Sales by Type', compute='_compute_chart_sales_by_type', store=True, compute_sudo=True,
        default=lambda self: {'labels': [], 'datasets': []}
    )
    chart_booking_trend = fields.Json(
        string='Chart Booking Trend', compute='_compute_chart_booking_trend', store=True, compute_sudo=True,
        default=lambda self: {'labels': [], 'datasets': []}
    )
    chart_payment_state = fields.Json(
        string='Chart Payment State', compute='_compute_chart_payment_state', store=True, compute_sudo=True,
        default=lambda self: {'labels': [], 'datasets': []}
    )
    chart_sales_funnel = fields.Json(
        string='Sales Funnel', compute='_compute_chart_sales_funnel', store=True, compute_sudo=True,
        default=lambda self: {'labels': [], 'datasets': []}
    )
    chart_top_customers = fields.Json(
        string='Top Customers Outstanding', compute='_compute_chart_top_customers', store=True, compute_sudo=True,
        default=lambda self: {'labels': [], 'datasets': []}
    )
    chart_agent_performance = fields.Json(
        string='Agent Performance', compute='_compute_chart_agent_performance', store=True, compute_sudo=True,
        default=lambda self: {'labels': [], 'datasets': []}
    )

    # Tabular data (HTML renders)
    table_order_type_html = fields.Html(string='Order Type Analysis', compute='_compute_table_order_type_html', sanitize=False, compute_sudo=True)
    table_agent_commission_html = fields.Html(string='Agent Commission Breakdown', compute='_compute_table_agent_commission_html', sanitize=False, compute_sudo=True)
    table_detailed_orders_html = fields.Html(string='Detailed Orders', compute='_compute_table_detailed_orders_html', sanitize=False, compute_sudo=True)
    table_invoice_aging_html = fields.Html(string='Invoice Aging', compute='_compute_table_invoice_aging_html', sanitize=False, compute_sudo=True)

    # Field to track deals without booking date (for fallback/future-proofing)
    include_unbooked_deals = fields.Boolean(
        string='Include Deals Without Booking Date',
        default=False,
        help='Include orders/deals that have no booking_date set yet'
    )
    unbooked_deals_count = fields.Integer(
        string='Unbooked Deals Count',
        compute='_compute_unbooked_deals_count',
        store=False,
        compute_sudo=True,
        help='Count of orders without a booking_date'
    )

    def _get_order_domain(self):
        # Include all confirmed deals: draft, sale, and done states
        # Exclude only cancelled orders
        domain = [('state', 'in', ['draft', 'sale', 'done'])]
        # Multi-select takes precedence if set
        # Important: Check .ids directly - empty recordset is still truthy!
        if self.sales_order_type_ids.ids:  # Check ids list, not recordset
            domain.append(('sale_order_type_id', 'in', self.sales_order_type_ids.ids))
        if self.invoice_status_filter and self.invoice_status_filter != 'all':
            domain.append(('invoice_status', '=', self.invoice_status_filter))
        # Use booking_date for date filtering instead of date_order (creation date)
        # This filters by when the deal was actually booked, not when the order was created
        if self.booking_date_from:
            if self.include_unbooked_deals:
                # Include orders with booking_date >= from_date OR no booking_date at all
                domain.append(('|', ('booking_date', '>=', self.booking_date_from), ('booking_date', '=', False)))
            else:
                # Only orders with booking_date >= from_date
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
            # Only filter invoices by orders if we have order-specific filters
            # Otherwise, include all invoices (respecting date ranges via invoice_date if applicable)
            has_order_filters = any([
                self.sales_order_type_ids.ids,
                self.invoice_status_filter and self.invoice_status_filter != 'all',
                self.agent_partner_id,
                self.partner_id,
            ])
            
            if has_order_filters:
                orders = self.env['sale.order'].search(order_domain)
                order_ids = orders.ids
                if order_ids:
                    # Link invoices to these specific orders
                    domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
                else:
                    # No orders match filters, so no invoices should match either
                    domain.append(('id', '=', False))  # Force empty result
            else:
                # No order-specific filters, apply date filter to invoices directly
                if self.booking_date_from:
                    domain.append(('invoice_date', '>=', self.booking_date_from))
                if self.booking_date_to:
                    domain.append(('invoice_date', '<=', self.booking_date_to))
                
        if unpaid_only:
            domain.append(('payment_state', 'in', ['not_paid', 'partial', 'in_payment']))
        if include_payment_filter and self.payment_status_filter and self.payment_status_filter != 'all':
            domain.append(('payment_state', '=', self.payment_status_filter))
        return domain

    @api.model
    def create(self, vals):
        # Enforce singleton: reuse existing record if any
        existing = self.search([], limit=1)
        if existing:
            return existing
        # Set defaults only on creation if not already set
        # Use 12-month lookback so charts have data to display
        today = date.today()
        twelve_months_ago = today.replace(year=today.year - 1)
        if 'booking_date_from' not in vals:
            vals['booking_date_from'] = twelve_months_ago
        if 'booking_date_to' not in vals:
            vals['booking_date_to'] = today
        if 'invoice_status_filter' not in vals:
            vals['invoice_status_filter'] = 'all'
        if 'payment_status_filter' not in vals:
            vals['payment_status_filter'] = 'all'
        return super(SalesInvoicingDashboard, self).create(vals)

    def write(self, vals):
        """
        Override write to ensure computed fields are refreshed when filters change.
        This handles cases where filters are updated programmatically or through
        the UI in ways that might not trigger @api.onchange.

        Note: Odoo's @api.depends automatically invalidates computed field caches
        when their dependencies change. Manual cache invalidation is not needed
        and was causing filter field rollback issues.
        """
        result = super(SalesInvoicingDashboard, self).write(vals)

        # Check if any filter field was updated
        filter_fields = {
     'sales_order_type_ids',
            'booking_date_from', 'booking_date_to',
            'invoice_status_filter', 'payment_status_filter',
            'agent_partner_id', 'partner_id',
        }

        # Note: Cache invalidation removed - @api.depends handles this automatically
        # Manual clear_cache() was causing AttributeError and is not needed

        return result

    @api.depends('sales_order_type_ids')
    def _compute_unbooked_deals_count(self):
        """Count orders/deals without a booking_date."""
        for dashboard in self:
            order_domain = dashboard._get_order_domain()
            # Add condition to find orders without booking_date
            order_domain_unbooked = order_domain + [('booking_date', '=', False)]
            unbooked_count = self.env['sale.order'].search_count(order_domain_unbooked)
            dashboard.unbooked_deals_count = unbooked_count

    @api.model
    def get_dashboard_singleton(self):
        """Return the singleton dashboard record, creating one if absent."""
        rec = self.search([], limit=1)
        if not rec:
            rec = self.create({})
        return rec

    def action_refresh_dashboard(self):
        """
        Manual refresh action for the dashboard.
        This can be called from a button to force complete refresh of all data.
        Returns an action to reload the current form view.
        """
        self.ensure_one()

        # Note: Cache clearing removed - @api.depends handles invalidation automatically
        # Accessing computed fields below triggers recomputation

        # Explicitly trigger recalculation of all computed fields
        # Note: Accessing computed fields triggers recomputation automatically
        self._refresh_all_computed_fields()

        # Return action to reload the form view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @ormcache('self.id', 'date_from', 'date_to')
    def _get_cached_order_stats(self, date_from, date_to):
        """Cached aggregation for orders between dates, to speed up charts.
        Returns dict with totals: amount_total, count.
        """
        domain = [('state', 'in', ['sale', 'done'])]
        if date_from:
            domain.append(('date_order', '>=', date_from))
        if date_to:
            domain.append(('date_order', '<=', date_to))
        groups = self.env['sale.order'].read_group(domain, ['amount_total', 'id:count'], [])
        total = sum(g.get('amount_total', 0.0) or 0.0 for g in groups)
        count = sum(int(g.get('id_count', 0) or g.get('__count', 0) or 0) for g in groups)
        return {'amount_total': total, 'count': count}

    def _refresh_all_computed_fields(self):
        """
        Helper method to force refresh all computed fields.
        This explicitly accesses all computed fields to trigger their recalculation.

        Note: Manual cache invalidation is not needed - Odoo's @api.depends
        handles this automatically when dependencies change.
        """
        # Access metrics (KPIs) to trigger computation
        _ = self.posted_invoice_count
        _ = self.pending_to_invoice_order_count
        _ = self.unpaid_invoice_count
        _ = self.total_booked_sales
        _ = self.total_invoiced_amount
        _ = self.total_pending_amount
        _ = self.amount_to_collect
        _ = self.amount_collected
        _ = self.commission_due

        # Access chart fields to trigger computation
        _ = self.chart_sales_by_type
        _ = self.chart_booking_trend
        _ = self.chart_payment_state
        _ = self.chart_sales_funnel
        _ = self.chart_top_customers
        _ = self.chart_agent_performance

        # Access table HTML fields to trigger computation
        _ = self.table_order_type_html
        _ = self.table_agent_commission_html
        _ = self.table_detailed_orders_html
        _ = self.table_invoice_aging_html

    @api.onchange(
        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _onchange_filters(self):
        """
        Trigger recomputation of all computed fields when filters change.

        In Odoo's form framework:
        1. @api.onchange is triggered when filter field changes
        2. Method runs in memory on the form (not saved to DB yet)
        3. Accessing computed fields triggers their @api.depends
        4. Form framework reads modified field values and updates UI

        The key is that by accessing computed fields here, we trigger
        their recalculation with the new filter values, and the form
        automatically detects and displays the updated values.

        IMPORTANT: This method is called every time a filter changes,
        including when filters are reset to default values.
        """
        # Use the helper method to refresh all computed fields
        self._refresh_all_computed_fields()

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_metrics(self):
        # Note: Odoo's @api.depends automatically handles cache invalidation
        # Manual invalidate_all() was causing filter field rollback issues
        for rec in self:
            order_domain = rec._get_order_domain()

            # Total Sales Value: SUM of price_unit from order lines in confirmed orders
            # This is the actual sales value from order line items (unit prices)
            # Excludes only cancelled orders as requested
            matching_orders = self.env['sale.order'].search(order_domain)
            order_ids = matching_orders.ids
            
            # Use read_group to efficiently sum price_unit from order lines
            if order_ids:
                line_groups = self.env['sale.order.line'].read_group(
                    [('order_id', 'in', order_ids)],
                    ['price_unit:sum'],
                    []
                )
                rec.total_booked_sales = sum(
                    float(g.get('price_unit', 0.0) or 0.0) for g in line_groups
                )
            else:
                rec.total_booked_sales = 0.0

            # Posted invoices count and total amount (respects all order filters)
            # If user filtered by order type/agent, only count invoices from those orders
            posted_invoice_domain = [
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ]
            
            # Apply date filters to invoices
            if rec.booking_date_from:
                posted_invoice_domain.append(('invoice_date', '>=', rec.booking_date_from))
            if rec.booking_date_to:
                posted_invoice_domain.append(('invoice_date', '<=', rec.booking_date_to))
            
            # If order filters are set, only include invoices from filtered orders
            has_order_filters = any([
                rec.sales_order_type_ids.ids,
                rec.agent_partner_id,
                rec.partner_id,
                rec.invoice_status_filter and rec.invoice_status_filter != 'all',
            ])
            
            if has_order_filters and order_ids:
                # Link invoices to filtered orders
                posted_invoice_domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
            elif has_order_filters and not order_ids:
                # No orders match filters, so no invoices should match either
                posted_invoice_domain.append(('id', '=', False))
            
            posted_invoices = self.env['account.move'].search(posted_invoice_domain)
            rec.posted_invoice_count = len(posted_invoices)
            rec.total_invoiced_amount = sum(posted_invoices.mapped('amount_total'))

            # Orders to invoice: orders with invoice_status = 'to invoice'
            pending_domain = [
                ('state', 'in', ['sale', 'done']),
                ('invoice_status', '=', 'to invoice'),
            ]
            # Apply same filters as order_domain but force invoice_status = 'to invoice'
            if rec.sales_order_type_ids.ids:
                pending_domain.append(('sale_order_type_id', 'in', rec.sales_order_type_ids.ids))
            if rec.booking_date_from:
                pending_domain.append(('booking_date', '>=', rec.booking_date_from))
            if rec.booking_date_to:
                pending_domain.append(('booking_date', '<=', rec.booking_date_to))
            if rec.agent_partner_id:
                pending_domain.append(('agent1_partner_id', '=', rec.agent_partner_id.id))
            if rec.partner_id:
                pending_domain.append(('partner_id', '=', rec.partner_id.id))
            
            pending_orders = self.env['sale.order'].search(pending_domain)
            rec.pending_to_invoice_order_count = len(pending_orders)
            rec.total_pending_amount = sum(pending_orders.mapped('amount_to_invoice'))

            # Unpaid invoices: respects all order filters (only unpaid from filtered orders)
            unpaid_domain = [
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('payment_state', 'in', ['not_paid', 'partial', 'in_payment']),
            ]
            
            # Apply date filtering
            if rec.booking_date_from:
                unpaid_domain.append(('invoice_date', '>=', rec.booking_date_from))
            if rec.booking_date_to:
                unpaid_domain.append(('invoice_date', '<=', rec.booking_date_to))
            
            # If order filters are set, only include unpaid invoices from filtered orders
            if has_order_filters and order_ids:
                unpaid_domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
            elif has_order_filters and not order_ids:
                unpaid_domain.append(('id', '=', False))
            
            unpaid_invoices = self.env['account.move'].search(unpaid_domain)
            rec.unpaid_invoice_count = len(unpaid_invoices)

            # Amount to collect / collected (from unpaid invoices respecting filters)
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

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_chart_sales_by_type(self):
        palette = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
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
            # Use pie chart type for distribution visualization
            rec.chart_sales_by_type = {
                'type': 'pie',
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Sales Distribution by Type',
                        'data': data,
                        'backgroundColor': colors,
                        'borderColor': '#fff',
                        'borderWidth': 2,
                    }
                ],
            }

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_chart_booking_trend(self):
        for rec in self:
            labels = []
            data = []
            try:
                domain = rec._get_order_domain()
                groups = self.env['sale.order'].read_group(
                    domain,
                    ['amount_total'],
                    ['date_order:month'],
                    orderby='date_order:month',
                    lazy=False
                )
                for group in groups:
                    # Safe dict access - don't trigger field machinery
                    month_label = str(group.get('date_order:month') or 'Unspecified')
                    labels.append(month_label)
                    data.append(float(group.get('amount_total', 0) or 0))
            except Exception:
                # If any error occurs, show empty chart
                labels = ['No data available']
                data = [0]

            # Use line chart with gradient for trend visualization
            rec.chart_booking_trend = {
                'type': 'line',
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Monthly Booking Trend',
                        'data': data,
                        'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                        'borderColor': '#3498db',
                        'pointBackgroundColor': '#3498db',
                        'pointBorderColor': '#fff',
                        'pointBorderWidth': 2,
                        'pointRadius': 5,
                        'fill': True,
                        'tension': 0.4,
                        'borderWidth': 3,
                    }
                ],
            }

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_chart_payment_state(self):
        palette = ['#d9534f', '#f39c12', '#3498db', '#27ae60']  # Not Paid, Partial, In Payment, Paid
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
            # Use doughnut chart for payment state distribution
            rec.chart_payment_state = {
                'type': 'doughnut',
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Invoice Amount by Payment State',
                        'data': data,
                        'backgroundColor': colors,
                        'borderColor': '#fff',
                        'borderWidth': 2,
                    }
                ],
            }

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
        'total_booked_sales',  # Depend on other computed fields
        'total_invoiced_amount',
        'amount_collected',
    )
    def _compute_chart_sales_funnel(self):
        for rec in self:
            data = [
                float(rec.total_booked_sales or 0.0),
                float(rec.total_invoiced_amount or 0.0),
                float(rec.amount_collected or 0.0),
            ]
            # Use horizontal bar chart to show sales funnel (conversion flow)
            rec.chart_sales_funnel = {
                'type': 'bar',
                'indexAxis': 'y',
                'labels': ['Booked Sales', 'Invoiced', 'Collected'],
                'datasets': [{
                    'label': 'Amount (AED)',
                    'data': data,
                    'backgroundColor': ['#3498db', '#f39c12', '#27ae60'],
                    'borderColor': ['#2980b9', '#e67e22', '#229954'],
                    'borderWidth': 2,
                    'borderRadius': 5,
                }],
            }

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_chart_top_customers(self):
        for rec in self:
            domain = rec._get_invoice_domain(include_payment_filter=False, unpaid_only=True)
            groups = self.env['account.move'].read_group(
                domain, ['amount_residual', 'partner_id'], ['partner_id']
            )
            # Sort and take top 10
            groups = sorted(groups, key=lambda g: g.get('amount_residual', 0.0), reverse=True)[:10]
            labels = [((g.get('partner_id') or ['', ''])[1] or '') for g in groups]
            data = [g.get('amount_residual', 0.0) for g in groups]
            # Use horizontal bar chart for top customers
            rec.chart_top_customers = {
                'type': 'bar',
                'indexAxis': 'y',
                'labels': labels,
                'datasets': [{
                    'label': 'Outstanding Amount (AED)',
                    'data': data,
                    'backgroundColor': '#e74c3c',
                    'borderColor': '#c0392b',
                    'borderWidth': 2,
                    'borderRadius': 4,
                }],
            }

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_chart_agent_performance(self):
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
            # Use grouped bar chart for agent commission breakdown
            rec.chart_agent_performance = {
                'type': 'bar',
                'labels': labels,
                'datasets': [
                    {'label': 'Total Commission', 'data': total_vals, 'backgroundColor': '#3498db', 'borderColor': '#2980b9', 'borderWidth': 1},
                    {'label': 'Paid', 'data': paid_vals, 'backgroundColor': '#27ae60', 'borderColor': '#229954', 'borderWidth': 1},
                    {'label': 'Outstanding', 'data': out_vals, 'backgroundColor': '#e74c3c', 'borderColor': '#c0392b', 'borderWidth': 1},
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
            # Use order line subtotal (price_unit * qty minus discount) as sales value
            order_lines = orders.mapped('order_line')
            total_sales = sum(order_lines.mapped('price_subtotal'))
            to_invoice = sum(
                orders.filtered(lambda o: o.invoice_status == 'to invoice')
                .mapped('order_line')
                .mapped('price_subtotal')
            )
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

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_table_order_type_html(self):
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

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_table_agent_commission_html(self):
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

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_table_detailed_orders_html(self):
        today = fields.Date.context_today(self)
        for rec in self:
            orders = self.env['sale.order'].search(rec._get_order_domain(), order='date_order desc, id desc', limit=50)
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
                # Convert datetime to date for proper comparison
                booking_date = o.booking_date.date() if hasattr(o.booking_date, 'date') else o.booking_date
                days_since = (today - (booking_date or today)).days if o.booking_date else 0
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

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_table_invoice_aging_html(self):
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

    def action_open_posted_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = [
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        order_domain = [('state', 'in', ['sale', 'done'])]
        if self.sales_order_type_ids.ids:
            order_domain.append(('sale_order_type_id', 'in', self.sales_order_type_ids.ids))
        if self.invoice_status_filter and self.invoice_status_filter != 'all':
            order_domain.append(('invoice_status', '=', self.invoice_status_filter))
        if self.booking_date_from:
            order_domain.append(('date_order', '>=', self.booking_date_from))
        if self.booking_date_to:
            order_domain.append(('date_order', '<=', self.booking_date_to))
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
        if self.sales_order_type_ids.ids:
            domain.append(('sale_order_type_id', 'in', self.sales_order_type_ids.ids))
        if self.booking_date_from:
            domain.append(('date_order', '>=', self.booking_date_from))
        if self.booking_date_to:
            domain.append(('date_order', '<=', self.booking_date_to))
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
            'graph_groupby': 'date_order:month',
        }
        return action

    def action_open_booked_sales(self):
        """Open detailed list of all booked sales (confirmed orders)."""
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        action['domain'] = domain
        action['view_mode'] = 'tree,form,graph,pivot'
        action['context'] = {
            'search_default_sale': 1,
            'search_default_done': 1,
        }
        action['name'] = 'Booked Sales Orders'
        return action

    def action_open_collected_invoices(self):
        """Open detailed list of fully paid/collected invoices."""
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = self._get_invoice_domain(include_payment_filter=False, unpaid_only=False)
        # Add filter for paid invoices only
        domain.append(('payment_state', '=', 'paid'))
        action['domain'] = domain
        action['view_mode'] = 'tree,form,graph,pivot'
        action['context'] = {'search_default_posted': 1}
        action['name'] = 'Collected Invoices (Paid)'
        return action

    def action_open_pending_to_invoice(self):
        """Open detailed list of orders pending to invoice."""
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        # Force invoice status to 'to invoice'
        domain = [d for d in domain if not (isinstance(d, tuple) and len(d) >= 1 and d[0] == 'invoice_status')]
        domain.append(('invoice_status', '=', 'to invoice'))
        action['domain'] = domain
        action['view_mode'] = 'tree,form,graph,pivot'
        action['context'] = {'search_default_to_invoice': 1}
        action['name'] = 'Orders Pending to Invoice'
        return action

    def action_open_commission_lines(self):
        """Open detailed list of commission lines due (pending/partial payment)."""
        self.ensure_one()
        order_ids = self.env['sale.order'].search(self._get_order_domain()).ids
        if not order_ids:
            # Return empty action if no orders match filters
            return {'type': 'ir.actions.act_window_close'}
        
        action = {
            'name': 'Commission Lines Due',
            'type': 'ir.actions.act_window',
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': [
                ('sale_order_id', 'in', order_ids),
                ('state', 'in', ['confirmed', 'processed']),
                ('payment_status', 'in', ['pending', 'partial']),
            ],
            'context': {'search_default_group_by_partner': 1},
        }
        return action

    def action_open_order_type_details(self):
        """Open pivot view for order type analysis."""
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        action['domain'] = domain
        action['view_mode'] = 'pivot,graph,tree,form'
        action['context'] = {
            'pivot_measures': ['amount_total'],
            'pivot_row_groupby': ['sale_order_type_id'],
        }
        action['name'] = 'Sales by Order Type'
        return action

    def action_open_agent_sales(self):
        """Open detailed sales orders grouped by agent/salesperson."""
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        action['domain'] = domain
        action['view_mode'] = 'tree,form,pivot,graph'
        action['context'] = {
            'search_default_agent1_partner_id': 1,
            'group_by': 'agent1_partner_id',
        }
        action['name'] = 'Sales by Agent/Salesperson'
        return action

    def action_open_customer_outstanding(self):
        """Open list of customers with outstanding invoices."""
        self.ensure_one()
        domain = self._get_invoice_domain(include_payment_filter=False, unpaid_only=True)
        invoice_ids = self.env['account.move'].search(domain).ids
        
        if not invoice_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        # Get unique partner IDs from unpaid invoices
        self.env.cr.execute("""
            SELECT DISTINCT partner_id 
            FROM account_move 
            WHERE id IN %s AND partner_id IS NOT NULL
        """, (tuple(invoice_ids),))
        partner_ids = [row[0] for row in self.env.cr.fetchall()]
        
        action = {
            'name': 'Customers with Outstanding Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', partner_ids)],
            'context': {'search_default_customer': 1},
        }
        return action

    @api.model
    def update_filters_and_refresh(self, filters_data):
        """
        API endpoint for frontend to update filters and get refreshed data.
        This ensures filters are properly saved and all computed fields are updated.

        Args:
            filters_data: dict with filter field names and values
                {
                    'booking_date_from': '2025-01-01',
                    'booking_date_to': '2025-12-31',
                    'sales_order_type_ids': [1, 2, 3],
                    'invoice_status_filter': 'to invoice',
                    ...
                }

        Returns:
            dict with updated field values for the dashboard
        """
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info(f'[OSUS Dashboard] update_filters_and_refresh called with filters: {filters_data}')
        rec = self.get_dashboard_singleton()

        # Prepare write values, handling different field types properly
        write_vals = {}
        for field_name, field_value in filters_data.items():
            if field_name not in rec._fields:
                continue

            field = rec._fields[field_name]

            # Handle many2many fields with proper Odoo command syntax
            if field.type == 'many2many':
                if isinstance(field_value, list):
                    write_vals[field_name] = [(6, 0, field_value)]  # Replace all
                else:
                    write_vals[field_name] = [(6, 0, [])]  # Clear if not a list
            # Handle many2one fields
            elif field.type == 'many2one':
                write_vals[field_name] = field_value if field_value else False
            # Handle other field types (dates, selection, etc.)
            else:
                write_vals[field_name] = field_value

        # Save the record - this persists the filter values
        if write_vals:
            rec.write(write_vals)
            # Commit to ensure values are persisted
            self.env.cr.commit()

        # Note: Cache clearing removed - @api.depends handles invalidation automatically
        # Accessing computed fields below triggers recomputation

        # Explicitly access computed fields to trigger their computation
        computed_data = {
            'posted_invoice_count': rec.posted_invoice_count,
            'pending_to_invoice_order_count': rec.pending_to_invoice_order_count,
            'unpaid_invoice_count': rec.unpaid_invoice_count,
            'total_booked_sales': rec.total_booked_sales,
            'total_invoiced_amount': rec.total_invoiced_amount,
            'total_pending_amount': rec.total_pending_amount,
            'amount_to_collect': rec.amount_to_collect,
            'amount_collected': rec.amount_collected,
            'commission_due': rec.commission_due,
            'chart_sales_by_type': rec.chart_sales_by_type,
            'chart_booking_trend': rec.chart_booking_trend,
            'chart_payment_state': rec.chart_payment_state,
            'chart_sales_funnel': rec.chart_sales_funnel,
            'chart_top_customers': rec.chart_top_customers,
            'chart_agent_performance': rec.chart_agent_performance,
            'table_order_type_html': rec.table_order_type_html,
            'table_agent_commission_html': rec.table_agent_commission_html,
            'table_detailed_orders_html': rec.table_detailed_orders_html,
            'table_invoice_aging_html': rec.table_invoice_aging_html,
        }

        _logger.info(f'[OSUS Dashboard] Returning computed data - chart_sales_funnel: {computed_data.get("chart_sales_funnel")}')
        _logger.info(f'[OSUS Dashboard] chart_sales_by_type: {computed_data.get("chart_sales_by_type")}')
        return computed_data

    def read(self, fields=None, load='_classic_read'):
        """Override read to ensure chart fields always return valid structures"""
        import logging
        _logger = logging.getLogger(__name__)
        result = super(SalesInvoicingDashboard, self).read(fields, load)
        
        # Ensure all chart fields have valid default structures (never None/False)
        chart_fields = [
            'chart_sales_by_type', 'chart_booking_trend', 'chart_payment_state',
            'chart_sales_funnel', 'chart_top_customers', 'chart_agent_performance'
        ]
        
        for record in result:
            for field_name in chart_fields:
                if field_name in record:
                    value = record[field_name]
                    # If the value is None, False, or an invalid structure, set empty chart
                    if not value or not isinstance(value, dict) or 'labels' not in value:
                        _logger.warning(f'[OSUS Dashboard] Field {field_name} had invalid value: {value}, setting empty chart')
                        record[field_name] = {'labels': [], 'datasets': []}
        
        _logger.info(f'[OSUS Dashboard] read() called with fields: {fields}, returning {len(result)} records')
        if result and 'chart_sales_by_type' in (fields or []):
            _logger.info(f'[OSUS Dashboard] Sample chart_sales_by_type from read(): {result[0].get("chart_sales_by_type")}')
        
        return result

    # Agent Ranking Tables
    table_agent_top_sales_value_html = fields.Html(
        string='Top 5 Agents by Sales Value',
        compute='_compute_table_agent_top_sales_value_html',
        sanitize=False,
        compute_sudo=True
    )
    table_agent_top_order_count_html = fields.Html(
        string='Top 5 Agents by Order Count',
        compute='_compute_table_agent_top_order_count_html',
        sanitize=False,
        compute_sudo=True
    )
    table_agent_top_revenue_html = fields.Html(
        string='Top 5 Agents by Revenue',
        compute='_compute_table_agent_top_revenue_html',
        sanitize=False,
        compute_sudo=True
    )

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_table_agent_top_sales_value_html(self):
        """Top 5 agents by total sales value (booked sales)."""
        for rec in self:
            domain = rec._get_order_domain()
            orders = self.env['sale.order'].search(domain)
            order_ids = orders.ids
            if not order_ids:
                rec.table_agent_top_sales_value_html = '<p>No data available</p>'
                continue

            # Sum line price_unit totals per order to avoid property-field groupby issues
            line_groups = self.env['sale.order.line'].read_group(
                [('order_id', 'in', order_ids)],
                ['price_unit:sum', 'order_id'],
                ['order_id']
            )
            subtotal_by_order = {
                g['order_id'][0]: float(g.get('price_unit') or 0.0)
                for g in line_groups if g.get('order_id')
            }

            # Aggregate per agent
            agent_totals = {}
            for order in orders:
                agent = order.agent1_partner_id
                subtotal = subtotal_by_order.get(order.id, 0.0)
                if agent not in agent_totals:
                    agent_totals[agent] = {'orders': 0, 'amount': 0.0}
                agent_totals[agent]['orders'] += 1
                agent_totals[agent]['amount'] += subtotal

            # Sort top 5 by amount
            top_agents = sorted(agent_totals.items(), key=lambda kv: kv[1]['amount'], reverse=True)[:5]
            html = [
                '<table class="table table-sm table-striped table-hover">',
                '<thead><tr>',
                '<th>Agent (Salesperson)</th><th>Orders</th><th>Total Sales Value</th>',
                '</tr></thead><tbody>'
            ]
            total_count = 0
            total_amount = 0.0
            for idx, (agent, data) in enumerate(top_agents, 1):
                agent_name = agent.display_name if agent else 'Unassigned'
                count = data['orders']
                amount = data['amount']
                html.append('<tr>')
                html.append(f'<td>{idx}. {agent_name}</td>')
                html.append(f'<td>{count}</td>')
                html.append(f'<td>{rec._fmt_money(amount)}</td>')
                html.append('</tr>')
                total_count += count
                total_amount += amount
            html.append('</tbody></table>')
            if top_agents:
                footer = [
                    '<tfoot><tr>',
                    '<th>Total</th>',
                    f'<th>{total_count}</th>',
                    f'<th>{rec._fmt_money(total_amount)}</th>',
                    '</tr></tfoot>'
                ]
                html.insert(2, ''.join(footer))
            rec.table_agent_top_sales_value_html = ''.join(html)

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_table_agent_top_order_count_html(self):
        """Top 5 agents by order count."""
        for rec in self:
            domain = rec._get_order_domain()
            orders = self.env['sale.order'].search(domain)
            order_ids = orders.ids
            if not order_ids:
                rec.table_agent_top_order_count_html = '<p>No data available</p>'
                continue

            # Sum line price_unit totals per order to avoid property-field groupby issues
            line_groups = self.env['sale.order.line'].read_group(
                [('order_id', 'in', order_ids)],
                ['price_unit:sum', 'order_id'],
                ['order_id']
            )
            subtotal_by_order = {
                g['order_id'][0]: float(g.get('price_unit') or 0.0)
                for g in line_groups if g.get('order_id')
            }

            agent_totals = {}
            for order in orders:
                agent = order.agent1_partner_id
                subtotal = subtotal_by_order.get(order.id, 0.0)
                if agent not in agent_totals:
                    agent_totals[agent] = {'orders': 0, 'amount': 0.0}
                agent_totals[agent]['orders'] += 1
                agent_totals[agent]['amount'] += subtotal

            top_agents = sorted(agent_totals.items(), key=lambda kv: kv[1]['orders'], reverse=True)[:5]
            html = [
                '<table class="table table-sm table-striped table-hover">',
                '<thead><tr>',
                '<th>Agent (Salesperson)</th><th>Order Count</th><th>Total Value</th>',
                '</tr></thead><tbody>'
            ]
            total_count = 0
            total_amount = 0.0
            for idx, (agent, data) in enumerate(top_agents, 1):
                agent_name = agent.display_name if agent else 'Unassigned'
                count = data['orders']
                amount = data['amount']
                html.append('<tr>')
                html.append(f'<td>{idx}. {agent_name}</td>')
                html.append(f'<td>{count}</td>')
                html.append(f'<td>{rec._fmt_money(amount)}</td>')
                html.append('</tr>')
                total_count += count
                total_amount += amount
            html.append('</tbody></table>')
            if top_agents:
                footer = [
                    '<tfoot><tr>',
                    '<th>Total</th>',
                    f'<th>{total_count}</th>',
                    f'<th>{rec._fmt_money(total_amount)}</th>',
                    '</tr></tfoot>'
                ]
                html.insert(2, ''.join(footer))
            rec.table_agent_top_order_count_html = ''.join(html)

    @api.depends(

        'sales_order_type_ids',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
        'agent_partner_id',
        'partner_id',
    )
    def _compute_table_agent_top_revenue_html(self):
        """Top 5 agents by collected revenue (invoiced & paid)."""
        for rec in self:
            domain = rec._get_order_domain()
            order_ids = self.env['sale.order'].search(domain).ids
            
            if not order_ids:
                rec.table_agent_top_revenue_html = '<p>No data available</p>'
                return

            # Get agents with their collected amounts
            sql = """
                SELECT 
                    partner.id,
                    partner.name,
                    COUNT(DISTINCT so.id) as order_count,
                    SUM(CASE WHEN am.state = 'posted' THEN (am.amount_total - am.amount_residual) ELSE 0 END) as collected_amount
                FROM res_partner partner
                LEFT JOIN sale_order so ON partner.id = so.agent1_partner_id
                LEFT JOIN account_move am ON am.id IN (
                    SELECT id FROM account_move 
                    WHERE state = 'posted' 
                    AND move_type IN ('out_invoice', 'out_refund')
                    GROUP BY id
                    LIMIT 1
                )
                WHERE so.id IN %s
                GROUP BY partner.id, partner.name
                ORDER BY collected_amount DESC NULLS LAST
                LIMIT 5
            """
            
            # Fallback: use commission lines for revenue calculation
            groups = self.env['commission.line'].read_group(
                [('sale_order_id', 'in', order_ids), ('commission_category', '=', 'internal'), ('paid_amount', '>', 0)],
                ['paid_amount', 'id:count', 'commission_amount'],
                ['partner_id'],
                limit=5,
                orderby='paid_amount DESC'
            )
            
            html = [
                '<table class="table table-sm table-striped table-hover">',
                '<thead><tr>',
                '<th>Agent (Salesperson)</th><th>Commissions Paid</th><th>Total Commission</th>',
                '</tr></thead><tbody>'
            ]
            total_paid = 0.0
            total_commission = 0.0
            for idx, g in enumerate(groups, 1):
                agent_name = (g.get('partner_id') or ['', ''])[1] or 'Unassigned'
                paid = float(g.get('paid_amount', 0.0) or 0.0)
                commission = float(g.get('commission_amount', 0.0) or 0.0)
                html.append('<tr>')
                html.append(f'<td>{idx}. {agent_name}</td>')
                html.append(f'<td>{rec._fmt_money(paid)}</td>')
                html.append(f'<td>{rec._fmt_money(commission)}</td>')
                html.append('</tr>')
                total_paid += paid
                total_commission += commission
            html.append('</tbody></table>')
            if groups:
                footer = [
                    '<tfoot><tr>',
                    '<th>Total</th>',
                    f'<th>{rec._fmt_money(total_paid)}</th>',
                    f'<th>{rec._fmt_money(total_commission)}</th>',
                    '</tr></tfoot>'
                ]
                html.insert(2, ''.join(footer))
            rec.table_agent_top_revenue_html = ''.join(html)
