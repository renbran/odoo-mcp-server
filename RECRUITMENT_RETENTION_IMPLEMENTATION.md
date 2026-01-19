# Recruitment UAE - Retention & Placement Implementation Plan

**Date:** 2025-01-13  
**Focus:** Placement Agency Workflow with Retention Management  
**Business Model:** Recruitment placement (NOT visa processing)

---

## Business Model Clarification

### What You DO:
✅ Source and screen candidates  
✅ Submit qualified candidates to clients  
✅ Coordinate interviews (client conducts)  
✅ Place candidates once client processes visa/offer  
✅ Invoice clients with retention terms  
✅ Follow-up to ensure candidate stability  
✅ Collect retention payment after guarantee period  

### What You DON'T DO:
❌ Process visas (client's responsibility)  
❌ Medical tests (client arranges)  
❌ Emirates ID processing (client handles)  
❌ PRO services (client manages)  

---

## Retention Management - How It Works

### Standard Retention Terms:
```
Example Invoice: AED 10,000 placement fee

Option 1 (70/30 Split):
- Upfront Payment: AED 7,000 (70%) - due on placement
- Retention: AED 3,000 (30%) - due after 90 days if candidate stable

Option 2 (60/40 Split):
- Upfront Payment: AED 6,000 (60%) - due on placement
- Retention: AED 4,000 (40%) - due after 120 days

Option 3 (80/20 Split):
- Upfront Payment: AED 8,000 (80%) - due on placement
- Retention: AED 2,000 (20%) - due after 60 days
```

### Retention Period Scenarios:

**Scenario 1: Successful Placement**
- Day 0: Candidate placed, invoice raised (70% + 30% retention)
- Day 1-90: Follow-up checks, ensure candidate working
- Day 90: Retention period ends, release 30% payment
- Result: ✅ Full payment received

**Scenario 2: Candidate Absconds (Day 45)**
- Day 0-45: Candidate working normally
- Day 45: Candidate absconds/leaves job
- Day 46: Within retention period → Lose 30% retention amount
- Day 47: Find replacement candidate (if guarantee offered)
- Result: ❌ Lost 30% revenue OR ❌ Cost of replacement

**Scenario 3: Replacement Guarantee**
- Day 0: Placement with 90-day guarantee
- Day 60: Candidate terminated by client
- Within guarantee → Must provide free replacement
- Find new candidate, place, start new 90-day cycle
- Result: ❌ No additional revenue, 2x work

---

## REVISED Phase 1: Critical Placement Features

### Feature 1: Placement Readiness Tracking

**Purpose:** Ensure candidate is legally placeable before submission

**Fields to Add:**

```python
# recruitment.candidate - Placement Eligibility

# Visa Status (Simplified for Placement Agency)
visa_status = fields.Selection([
    ('none', 'No UAE Visa'),
    ('visit_tourist', 'Visit/Tourist Visa'),
    ('employment_active', 'Valid Employment Visa'),
    ('employment_cancelled', 'Cancelled Employment Visa'),
    ('freezone', 'Free Zone Visa'),
], string='Current Visa Status', tracking=True)

visa_sponsor = fields.Char(string='Current Sponsor/Employer')
visa_expiry = fields.Date(string='Visa Expiry Date')

# NOC Requirement
noc_required = fields.Boolean(string='NOC Required', 
                                compute='_compute_noc_required', store=True)
noc_status = fields.Selection([
    ('not_required', 'Not Required'),
    ('pending', 'Pending'),
    ('obtained', 'NOC Obtained'),
    ('refused', 'NOC Refused'),
], string='NOC Status', default='not_required', tracking=True)
noc_received_date = fields.Date(string='NOC Received Date')
noc_document = fields.Binary(string='NOC Document', attachment=True)

# Document Verification (Basic)
passport_verified = fields.Boolean(string='Passport Verified')
passport_expiry_valid = fields.Boolean(string='Passport Valid (6+ Months)',
                                        compute='_compute_passport_validity')
certificates_verified = fields.Boolean(string='Certificates Verified')
police_clearance = fields.Boolean(string='Police Clearance Verified')

# Placement Eligibility
placement_ready = fields.Boolean(string='Ready for Placement',
                                   compute='_compute_placement_ready', store=True)
placement_blockers = fields.Text(string='Placement Blockers',
                                   compute='_compute_placement_ready')

@api.depends('visa_status', 'noc_status', 'passport_verified', 'passport_expiry_valid')
def _compute_placement_ready(self):
    for rec in self:
        blockers = []
        ready = True
        
        # Check visa eligibility
        if rec.visa_status == 'employment_active' and rec.noc_status != 'obtained':
            blockers.append('NOC required but not obtained')
            ready = False
        
        # Check passport
        if not rec.passport_verified:
            blockers.append('Passport not verified')
            ready = False
        
        if not rec.passport_expiry_valid:
            blockers.append('Passport expiring in <6 months')
            ready = False
        
        rec.placement_ready = ready
        rec.placement_blockers = '\n'.join(blockers) if blockers else False
```

---

### Feature 2: Retention Management System

**New Model: recruitment.retention**

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class RecruitmentRetention(models.Model):
    _name = 'recruitment.retention'
    _description = 'Placement Retention Management'
    _order = 'retention_release_date asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Retention Reference', required=True, 
                        default=lambda self: _('New'), copy=False)
    
    # Links
    deployment_id = fields.Many2one('recruitment.deployment', 
                                     string='Deployment', 
                                     required=True, ondelete='cascade', tracking=True)
    candidate_id = fields.Many2one('recruitment.candidate',
                                     related='deployment_id.candidate_id',
                                     string='Candidate', store=True)
    partner_id = fields.Many2one('res.partner',
                                   related='deployment_id.partner_id',
                                   string='Client', store=True)
    invoice_id = fields.Many2one('account.move',
                                   related='deployment_id.invoice_id',
                                   string='Invoice', store=True)
    
    # Retention Terms
    total_placement_fee = fields.Monetary(string='Total Placement Fee',
                                           required=True,
                                           currency_field='currency_id',
                                           tracking=True)
    
    upfront_percentage = fields.Float(string='Upfront %', 
                                        required=True, 
                                        default=70.0,
                                        tracking=True)
    retention_percentage = fields.Float(string='Retention %',
                                          compute='_compute_retention_percentage',
                                          store=True)
    
    upfront_amount = fields.Monetary(string='Upfront Payment',
                                       compute='_compute_amounts',
                                       store=True,
                                       currency_field='currency_id')
    retention_amount = fields.Monetary(string='Retention Amount',
                                         compute='_compute_amounts',
                                         store=True,
                                         currency_field='currency_id',
                                         tracking=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency',
                                    default=lambda self: self.env.company.currency_id)
    
    # Retention Period
    placement_date = fields.Date(string='Placement Date',
                                   related='deployment_id.deployment_date',
                                   store=True)
    retention_period_days = fields.Integer(string='Retention Period (Days)',
                                             required=True,
                                             default=90,
                                             tracking=True)
    retention_release_date = fields.Date(string='Retention Release Date',
                                           compute='_compute_release_date',
                                           store=True,
                                           tracking=True)
    
    # Payment Tracking
    upfront_paid = fields.Boolean(string='Upfront Paid', tracking=True)
    upfront_payment_date = fields.Date(string='Upfront Paid On')
    
    retention_status = fields.Selection([
        ('pending', 'Pending Release'),
        ('released', 'Released for Payment'),
        ('paid', 'Paid'),
        ('forfeited', 'Forfeited'),
    ], string='Retention Status', default='pending', tracking=True)
    
    retention_paid = fields.Boolean(string='Retention Paid')
    retention_payment_date = fields.Date(string='Retention Paid On')
    
    # Candidate Stability Tracking
    candidate_status = fields.Selection([
        ('working', 'Working Normally'),
        ('issue_minor', 'Minor Issues'),
        ('issue_major', 'Major Issues'),
        ('absconded', 'Absconded'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
    ], string='Candidate Status', default='working', tracking=True)
    
    candidate_working_days = fields.Integer(string='Working Days',
                                              compute='_compute_working_days')
    days_until_release = fields.Integer(string='Days Until Release',
                                          compute='_compute_days_until_release')
    
    # Risk Assessment
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ], string='Risk Level', compute='_compute_risk_level', store=True)
    
    risk_notes = fields.Text(string='Risk Notes')
    
    # Forfeiture
    forfeiture_reason = fields.Selection([
        ('absconded', 'Candidate Absconded'),
        ('early_resignation', 'Resigned Before Retention Period'),
        ('performance', 'Poor Performance - Client Terminated'),
        ('misconduct', 'Misconduct'),
        ('other', 'Other'),
    ], string='Forfeiture Reason')
    forfeiture_date = fields.Date(string='Forfeiture Date')
    forfeiture_notes = fields.Text(string='Forfeiture Notes')
    
    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active - Monitoring'),
        ('completed', 'Completed - Retention Collected'),
        ('forfeited', 'Forfeited - Retention Lost'),
    ], string='Status', default='draft', tracking=True)
    
    company_id = fields.Many2one('res.company', string='Company',
                                   default=lambda self: self.env.company)
    
    @api.depends('upfront_percentage')
    def _compute_retention_percentage(self):
        for rec in self:
            rec.retention_percentage = 100 - rec.upfront_percentage
    
    @api.depends('total_placement_fee', 'upfront_percentage')
    def _compute_amounts(self):
        for rec in self:
            rec.upfront_amount = rec.total_placement_fee * (rec.upfront_percentage / 100)
            rec.retention_amount = rec.total_placement_fee - rec.upfront_amount
    
    @api.depends('placement_date', 'retention_period_days')
    def _compute_release_date(self):
        for rec in self:
            if rec.placement_date and rec.retention_period_days:
                rec.retention_release_date = rec.placement_date + timedelta(days=rec.retention_period_days)
            else:
                rec.retention_release_date = False
    
    @api.depends('placement_date')
    def _compute_working_days(self):
        today = fields.Date.today()
        for rec in self:
            if rec.placement_date:
                rec.candidate_working_days = (today - rec.placement_date).days
            else:
                rec.candidate_working_days = 0
    
    @api.depends('retention_release_date')
    def _compute_days_until_release(self):
        today = fields.Date.today()
        for rec in self:
            if rec.retention_release_date:
                rec.days_until_release = (rec.retention_release_date - today).days
            else:
                rec.days_until_release = 0
    
    @api.depends('candidate_status', 'days_until_release', 'state')
    def _compute_risk_level(self):
        for rec in self:
            if rec.state in ['completed', 'forfeited']:
                rec.risk_level = 'low'
            elif rec.candidate_status in ['absconded', 'resigned', 'terminated']:
                rec.risk_level = 'critical'
            elif rec.candidate_status == 'issue_major':
                rec.risk_level = 'high'
            elif rec.candidate_status == 'issue_minor':
                rec.risk_level = 'medium'
            elif rec.days_until_release <= 7:
                rec.risk_level = 'low'  # Almost completed
            else:
                rec.risk_level = 'low'
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.retention') or _('New')
        return super(RecruitmentRetention, self).create(vals)
    
    def action_activate(self):
        """Activate retention monitoring"""
        self.write({'state': 'active'})
    
    def action_release_retention(self):
        """Release retention for payment (after successful period)"""
        for rec in self:
            if rec.candidate_status in ['absconded', 'resigned', 'terminated']:
                raise UserError(_('Cannot release retention - candidate is no longer working'))
            
            rec.write({
                'retention_status': 'released',
                'state': 'active',
            })
            
            # Create activity for accounts team
            rec.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.env.ref('base.user_admin').id,
                summary=_('Collect Retention Payment: %s') % rec.name,
                note=_('Retention period completed. Collect AED %s from %s') % (
                    rec.retention_amount, rec.partner_id.name
                )
            )
    
    def action_mark_paid(self):
        """Mark retention as paid"""
        self.write({
            'retention_paid': True,
            'retention_payment_date': fields.Date.today(),
            'retention_status': 'paid',
            'state': 'completed',
        })
    
    def action_forfeit(self):
        """Forfeit retention (candidate left/absconded)"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Forfeit Retention'),
            'res_model': 'recruitment.retention.forfeit.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_retention_id': self.id},
        }
    
    @api.model
    def cron_check_retention_releases(self):
        """Daily cron to auto-release completed retentions"""
        today = fields.Date.today()
        ready_for_release = self.search([
            ('state', '=', 'active'),
            ('retention_status', '=', 'pending'),
            ('retention_release_date', '<=', today),
            ('candidate_status', '=', 'working'),
        ])
        
        for retention in ready_for_release:
            retention.action_release_retention()
    
    @api.model
    def cron_send_retention_reminders(self):
        """Send reminders 7 days before retention release"""
        reminder_date = fields.Date.today() + timedelta(days=7)
        upcoming = self.search([
            ('state', '=', 'active'),
            ('retention_status', '=', 'pending'),
            ('retention_release_date', '=', reminder_date),
        ])
        
        # Send email reminders to follow up with candidate
        for retention in upcoming:
            # TODO: Send email to sales person
            retention.message_post(
                body=_('Retention release in 7 days. Please verify candidate is still working.'),
                subject=_('Retention Release Reminder'),
            )
```

---

### Feature 3: Enhanced Deployment Model

**Add to recruitment.deployment:**

```python
# Placement & Invoicing
placement_ready = fields.Boolean(string='Ready for Placement',
                                   related='candidate_id.placement_ready',
                                   store=True)
placement_blockers = fields.Text(string='Placement Blockers',
                                   related='candidate_id.placement_blockers')

# Visa/Offer Status (Tracking Only - Not Processing)
client_visa_status = fields.Selection([
    ('pending', 'Client Processing Visa'),
    ('approved', 'Visa Approved by Client'),
    ('ready', 'Visa Ready for Stamping'),
    ('completed', 'Visa Completed'),
    ('offer_only', 'Offer Letter Only (No Visa)'),
], string='Client Visa Status', tracking=True)

offer_letter_received = fields.Boolean(string='Offer Letter Received', tracking=True)
offer_letter_date = fields.Date(string='Offer Letter Date')
offer_letter_file = fields.Binary(string='Offer Letter', attachment=True)

# Placement Fee & Retention
placement_fee = fields.Monetary(string='Placement Fee',
                                  required=True,
                                  currency_field='currency_id',
                                  tracking=True)

# Retention Terms
retention_applicable = fields.Boolean(string='Retention Applicable', default=True)
retention_id = fields.Many2one('recruitment.retention', 
                                string='Retention Agreement',
                                copy=False)
retention_percentage = fields.Float(string='Retention %', default=30.0)
retention_period_days = fields.Integer(string='Retention Period (Days)', default=90)

# Invoice with Retention
invoice_total = fields.Monetary(string='Invoice Total',
                                  compute='_compute_invoice_amounts',
                                  store=True,
                                  currency_field='currency_id')
invoice_upfront = fields.Monetary(string='Upfront Amount',
                                    compute='_compute_invoice_amounts',
                                    store=True,
                                    currency_field='currency_id')
invoice_retention = fields.Monetary(string='Retention Amount',
                                      compute='_compute_invoice_amounts',
                                      store=True,
                                      currency_field='currency_id')

@api.depends('placement_fee', 'retention_percentage')
def _compute_invoice_amounts(self):
    for rec in self:
        rec.invoice_total = rec.placement_fee
        if rec.retention_applicable:
            rec.invoice_retention = rec.placement_fee * (rec.retention_percentage / 100)
            rec.invoice_upfront = rec.placement_fee - rec.invoice_retention
        else:
            rec.invoice_upfront = rec.placement_fee
            rec.invoice_retention = 0

def action_create_invoice_with_retention(self):
    """Create invoice with retention terms"""
    self.ensure_one()
    
    if not self.placement_ready:
        raise UserError(_('Candidate not ready for placement. Blockers: %s') % 
                         self.placement_blockers)
    
    # Create invoice (existing logic)
    invoice = self._create_placement_invoice()
    
    # Create retention record if applicable
    if self.retention_applicable:
        retention = self.env['recruitment.retention'].create({
            'deployment_id': self.id,
            'total_placement_fee': self.placement_fee,
            'upfront_percentage': 100 - self.retention_percentage,
            'retention_period_days': self.retention_period_days,
            'state': 'active',
        })
        self.retention_id = retention.id
    
    return {
        'type': 'ir.actions.act_window',
        'name': _('Placement Invoice'),
        'res_model': 'account.move',
        'res_id': invoice.id,
        'view_mode': 'form',
        'target': 'current',
    }
```

---

### Feature 4: Follow-Up with Retention Focus

**New Model: recruitment.followup (Simplified)**

```python
class RecruitmentFollowUp(models.Model):
    _name = 'recruitment.followup'
    _description = 'Candidate Stability Follow-Up'
    _order = 'followup_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Follow-Up Reference', required=True,
                        default=lambda self: _('New'))
    
    deployment_id = fields.Many2one('recruitment.deployment', 
                                     string='Deployment', required=True)
    retention_id = fields.Many2one('recruitment.retention',
                                     related='deployment_id.retention_id',
                                     string='Retention', store=True)
    candidate_id = fields.Many2one('recruitment.candidate',
                                     related='deployment_id.candidate_id',
                                     string='Candidate', store=True)
    partner_id = fields.Many2one('res.partner',
                                   related='deployment_id.partner_id',
                                   string='Client', store=True)
    
    # Follow-Up Details
    followup_date = fields.Date(string='Follow-Up Date', 
                                  default=fields.Date.today, required=True)
    followup_type = fields.Selection([
        ('week_1', 'Week 1 Check'),
        ('week_2', 'Week 2 Check'),
        ('day_30', '30-Day Check'),
        ('day_60', '60-Day Check'),
        ('day_90', '90-Day Check'),
        ('ad_hoc', 'Ad-Hoc Check'),
    ], string='Follow-Up Type', required=True)
    
    conducted_by = fields.Many2one('res.users', string='Conducted By',
                                     default=lambda self: self.env.user)
    
    # Candidate Status
    candidate_working = fields.Boolean(string='Candidate Still Working', default=True)
    candidate_satisfied = fields.Selection([
        ('very_satisfied', 'Very Satisfied'),
        ('satisfied', 'Satisfied'),
        ('neutral', 'Neutral'),
        ('dissatisfied', 'Dissatisfied'),
        ('very_dissatisfied', 'Very Dissatisfied'),
    ], string='Candidate Satisfaction')
    
    # Issues
    issues_identified = fields.Boolean(string='Issues Identified')
    issue_type = fields.Selection([
        ('salary_delay', 'Salary Delay'),
        ('accommodation', 'Accommodation Issues'),
        ('working_conditions', 'Working Conditions'),
        ('manager_conflict', 'Manager Conflict'),
        ('wants_to_leave', 'Wants to Leave'),
        ('other', 'Other'),
    ], string='Issue Type')
    issue_severity = fields.Selection([
        ('minor', 'Minor - Can be resolved'),
        ('moderate', 'Moderate - Needs attention'),
        ('severe', 'Severe - Risk of leaving'),
        ('critical', 'Critical - Will leave'),
    ], string='Issue Severity')
    
    issue_details = fields.Text(string='Issue Details')
    action_taken = fields.Text(string='Action Taken')
    
    # Retention Impact
    retention_at_risk = fields.Boolean(string='Retention at Risk',
                                         compute='_compute_retention_risk')
    
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('issue_found', 'Issue Found - Follow-Up Required'),
        ('escalated', 'Escalated'),
    ], string='Status', default='scheduled', tracking=True)
    
    @api.depends('issues_identified', 'issue_severity', 'candidate_working')
    def _compute_retention_risk(self):
        for rec in self:
            rec.retention_at_risk = (
                not rec.candidate_working or
                rec.issue_severity in ['severe', 'critical']
            )
            
            # Update retention record risk
            if rec.retention_id and rec.retention_at_risk:
                if not rec.candidate_working:
                    rec.retention_id.candidate_status = 'absconded'
                elif rec.issue_severity == 'critical':
                    rec.retention_id.candidate_status = 'issue_major'
                elif rec.issue_severity == 'severe':
                    rec.retention_id.candidate_status = 'issue_major'
                else:
                    rec.retention_id.candidate_status = 'issue_minor'
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.followup') or _('New')
        return super(RecruitmentFollowUp, self).create(vals)
    
    @api.model
    def cron_schedule_followups(self):
        """Auto-schedule follow-ups for active retentions"""
        active_retentions = self.env['recruitment.retention'].search([
            ('state', '=', 'active'),
        ])
        
        today = fields.Date.today()
        
        for retention in active_retentions:
            deployment = retention.deployment_id
            days_since_placement = retention.candidate_working_days
            
            # Schedule based on days since placement
            if days_since_placement == 7:
                self._create_scheduled_followup(deployment, 'week_1')
            elif days_since_placement == 14:
                self._create_scheduled_followup(deployment, 'week_2')
            elif days_since_placement == 30:
                self._create_scheduled_followup(deployment, 'day_30')
            elif days_since_placement == 60:
                self._create_scheduled_followup(deployment, 'day_60')
            elif days_since_placement == 90:
                self._create_scheduled_followup(deployment, 'day_90')
    
    def _create_scheduled_followup(self, deployment, followup_type):
        """Create scheduled follow-up if not exists"""
        existing = self.search([
            ('deployment_id', '=', deployment.id),
            ('followup_type', '=', followup_type),
        ], limit=1)
        
        if not existing:
            self.create({
                'deployment_id': deployment.id,
                'followup_type': followup_type,
                'state': 'scheduled',
            })
```

---

## Implementation Sequence

### Step 1: Model Files (Week 1)
1. Create `models/retention.py` - Retention management
2. Enhance `models/candidate.py` - Add placement readiness fields
3. Enhance `models/deployment.py` - Add retention & invoicing fields
4. Create `models/followup.py` - Follow-up tracking
5. Update `models/__init__.py` - Import new models

### Step 2: Views & Security (Week 1)
1. Create `views/retention_views.xml` - Retention form/tree/kanban
2. Enhance `views/candidate_views.xml` - Add placement status
3. Enhance `views/deployment_views.xml` - Add retention section
4. Create `views/followup_views.xml` - Follow-up calendar/list
5. Update `security/ir.model.access.csv` - Add access rules
6. Create `data/sequences.xml` - Add retention/followup sequences

### Step 3: Wizards (Week 2)
1. `wizard/retention_forfeit_wizard.py` - Forfeit retention with reason
2. `wizard/schedule_followup_wizard.py` - Bulk schedule follow-ups
3. Enhance invoice wizard - Include retention terms

### Step 4: Automation (Week 2)
1. Scheduled action: Daily retention release check
2. Scheduled action: Auto-schedule follow-ups
3. Scheduled action: Send retention reminders (7 days before)
4. Email templates: Retention release notification, follow-up reminder

### Step 5: Reports (Week 2)
1. Retention aging report (pending retentions by client)
2. At-risk placements report (candidates with issues during retention)
3. Follow-up compliance report (completed vs scheduled)
4. Retention collection forecast (expected retention releases)

---

## Key Success Metrics

### Operational Metrics:
- **Retention Collection Rate:** Target 90%+ (collect 90% of all retention amounts)
- **Follow-Up Compliance:** Target 100% (all scheduled follow-ups completed on time)
- **Early Issue Detection:** Target <7 days (identify issues within 1 week)
- **Placement Stability:** Target 95%+ (95% of candidates stay through retention period)

### Financial Metrics:
- **Average Retention Amount:** Track average held per placement
- **Retention Lost:** Track total AED lost to abscondments/failures
- **Collection Time:** Track days from release to payment received
- **Retention Revenue:** Track total retention collected per month/quarter

---

## Dashboard Widgets (Priority)

1. **Retention Releases This Week** - List of retentions becoming due
2. **At-Risk Placements** - Candidates with issues during retention period
3. **Overdue Follow-Ups** - Scheduled follow-ups not completed
4. **Retention Collection Forecast** - Expected retention releases next 30/60/90 days
5. **Retention Lost (YTD)** - Total retention forfeited this year
6. **Placement Success Rate** - % of placements completing retention successfully

---

**Ready to implement?** Should I start creating the model files?
