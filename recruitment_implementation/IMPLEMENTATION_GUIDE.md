# Recruitment UAE - Retention & Follow-Up Implementation Guide

**Date:** January 13, 2026  
**Module:** recruitment_uae v18.0.2.0.0  
**Scope:** Retention management and post-placement follow-up system

---

## 📋 Implementation Summary

This implementation adds **critical retention and follow-up management features** to the recruitment_uae module:

### New Models
1. **recruitment.retention** - Manages placement retention periods and payments
2. **recruitment.followup** - Tracks post-placement follow-ups and candidate stability
3. **Enhanced recruitment.candidate** - Adds placement readiness and visa tracking

### Key Features
- ✅ Placement fee split (upfront + retention)
- ✅ Automatic retention release on schedule
- ✅ Retention forfeiture with reason tracking
- ✅ Post-placement follow-up scheduling
- ✅ Risk assessment and alerting
- ✅ NOC tracking and visa status management
- ✅ Placement readiness verification

---

## 🗂️ File Structure

```
recruitment_implementation/
├── __init__.py                          # Package initialization
├── models_retention.py                  # Main retention model
├── models_candidate_enhancement.py      # Enhanced candidate fields
├── models_followup.py                   # Follow-up tracking model
├── wizard_forfeit.py                    # Forfeit retention wizard
├── views_retention_followup.xml         # All views, actions, menus
└── IMPLEMENTATION_GUIDE.md              # This file
```

---

## 🚀 Installation Steps

### Step 1: Copy Files to Module
```bash
# On eigermarvel server, copy to recruitment_uae module:
scp -i ~/.ssh/id_rsa models_retention.py root@65.20.72.53:/var/odoo/eigermarvel/extra-addons/cybroaddons.git-XXXX/recruitment_uae/models/
scp -i ~/.ssh/id_rsa models_candidate_enhancement.py root@65.20.72.53:/var/odoo/eigermarvel/extra-addons/cybroaddons.git-XXXX/recruitment_uae/models/
scp -i ~/.ssh/id_rsa models_followup.py root@65.20.72.53:/var/odoo/eigermarvel/extra-addons/cybroaddons.git-XXXX/recruitment_uae/models/
scp -i ~/.ssh/id_rsa wizard_forfeit.py root@65.20.72.53:/var/odoo/eigermarvel/extra-addons/cybroaddons.git-XXXX/recruitment_uae/wizards/
scp -i ~/.ssh/id_rsa views_retention_followup.xml root@65.20.72.53:/var/odoo/eigermarvel/extra-addons/cybroaddons.git-XXXX/recruitment_uae/views/
```

### Step 2: Update __init__.py Files

**models/__init__.py** - Add:
```python
from . import retention
from . import followup
from . import candidate  # If enhancing existing
```

**wizards/__init__.py** - Add (create if not exists):
```python
from . import retention_forfeit
```

### Step 3: Update Module Manifest
Edit `recruitment_uae/__manifest__.py`:
```python
{
    'name': 'Recruitment UAE',
    'version': '18.0.2.0.0',
    'author': 'Your Company',
    'category': 'Human Resources',
    'depends': [
        'recruitment',
        'mail',
        'account',
    ],
    'data': [
        # ... existing data files ...
        'views/retention_views.xml',
        'views/followup_views.xml',
        'data/sequences.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
```

### Step 4: Create Security Rules
File: `security/ir.model.access.csv`
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_recruitment_retention_manager,Retention - Manager,model_recruitment_retention,base.group_user,1,1,1,1
access_recruitment_retention_read,Retention - Read,model_recruitment_retention,base.group_user,1,0,0,0
access_recruitment_followup_manager,Follow-up - Manager,model_recruitment_followup,base.group_user,1,1,1,0
access_retention_forfeit_wizard,Forfeit Wizard,model_retention_forfeit_wizard,base.group_user,1,1,1,1
```

### Step 5: Create Cron Jobs
File: `data/cron_jobs.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Daily: Release due retentions -->
    <record id="cron_release_due_retentions" model="ir.cron">
        <field name="name">Release Due Retentions</field>
        <field name="model_name">recruitment.retention</field>
        <field name="state">code</field>
        <field name="code">model.cron_release_due_retentions()</field>
        <field name="user_id" ref="base.user_admin"/>
        <field name="active" eval="True"/>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="nextcall">2026-01-14 00:00:00</field>
    </record>

    <!-- Daily: Schedule automatic follow-ups -->
    <record id="cron_schedule_followups" model="ir.cron">
        <field name="name">Schedule Follow-Ups</field>
        <field name="model_name">recruitment.followup</field>
        <field name="state">code</field>
        <field name="code">model.cron_schedule_automatic_followups()</field>
        <field name="user_id" ref="base.user_admin"/>
        <field name="active" eval="True"/>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="nextcall">2026-01-14 06:00:00</field>
    </record>

    <!-- Daily: Mark overdue follow-ups -->
    <record id="cron_mark_overdue" model="ir.cron">
        <field name="name">Mark Overdue Follow-Ups</field>
        <field name="model_name">recruitment.followup</field>
        <field name="state">code</field>
        <field name="code">model.cron_mark_overdue_followups()</field>
        <field name="user_id" ref="base.user_admin"/>
        <field name="active" eval="True"/>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="nextcall">2026-01-14 08:00:00</field>
    </record>
</odoo>
```

### Step 6: Update Module in Odoo
```bash
# SSH to eigermarvel
ssh -i ~/.ssh/id_rsa root@65.20.72.53

# Navigate and update module
cd /var/odoo/eigermarvel
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf \
    --no-http --stop-after-init --update=recruitment_uae
```

---

## 📊 Model Architecture

### recruitment.retention
**Purpose:** Track placement retention payment terms and collection

**Key Fields:**
- `deployment_id` - Links to deployment
- `total_placement_fee` - Total fee charged
- `upfront_percentage` - % due immediately
- `retention_percentage` - % held back
- `retention_period_days` - How long to hold
- `retention_release_date` - When payment due
- `candidate_status` - Working/Absconded/Resigned/etc
- `risk_level` - Low/Medium/High/Critical
- `state` - draft → active → released → completed/forfeited

**Key Actions:**
- `action_activate()` - Start retention tracking
- `action_mark_upfront_paid()` - Record upfront payment
- `action_release_retention()` - Release on schedule
- `action_mark_retention_paid()` - Record full payment
- `action_forfeit_retention()` - Open forfeit wizard

**Cron Jobs:**
- `cron_release_due_retentions()` - Auto-release on due date
- Sends activity reminders before release date

### recruitment.followup
**Purpose:** Track post-placement candidate stability

**Key Fields:**
- `deployment_id` - Links to deployment
- `followup_type` - week_1, week_2, day_30, day_60, day_90, etc
- `scheduled_date` - When to follow-up
- `candidate_working` - Yes/No
- `issue_reported` - Yes/No
- `issue_severity` - None/Minor/Moderate/Severe/Critical
- `candidate_status` - Working/Missing/Absconded/Resigned/etc
- `retention_at_risk` - Computed field shows if retention endangered
- `state` - scheduled → in_progress → completed

**Key Actions:**
- `action_start()` - Begin follow-up
- `action_complete()` - Mark done with notes
- `action_escalate_to_management()` - Alert manager
- `action_schedule_next_followup()` - Create next in series
- `action_propose_replacement()` - If candidate left

**Cron Jobs:**
- `cron_schedule_automatic_followups()` - Create on days 7,14,30,60,90
- `cron_mark_overdue_followups()` - Create alerts for missed follow-ups

### recruitment.candidate (Enhanced)
**New Fields for Placement Readiness:**
- `placement_ready` - Computed: can candidate be placed?
- `placement_blockers` - Text: what's preventing placement

**Visa Status Tracking:**
- `visa_status` - No visa/Visit/Employment Active/Cancelled/Free Zone
- `visa_sponsor` - Current employer/sponsor
- `visa_expiry` - When visa expires
- `visa_validity_days` - Days until expiry
- `visa_valid_for_placement` - Has 6+ months validity?

**NOC (No Objection Certificate):**
- `noc_required` - Computed: true if employment visa
- `noc_status` - Not Required/Pending/Obtained/Refused
- `noc_received_date` - When NOC arrived
- `noc_expiry_date` - When NOC expires
- `noc_document` - PDF upload

**Document Verification:**
- `passport_verified` - Boolean
- `passport_expiry_valid` - Has 6+ months?
- `certificates_verified` - Qualifications checked?
- `police_clearance_verified` - Clearance obtained?
- `medical_fitness_certificate` - Medical OK?

**Availability:**
- `availability_status` - Available/In Interview/Selected/Deployed/Unavailable
- `earliest_available_date` - When can start
- `notice_period_days` - Notice if employed elsewhere

---

## 🔄 Workflow Scenarios

### Scenario 1: Standard Placement with 90-Day Retention
```
Day 0:
  ├─ Create Deployment
  ├─ Create Retention (70% upfront, 30% held)
  ├─ Invoice client (100%)
  └─ Create Week 1 Follow-up

Day 7:
  ├─ Week 1 Follow-up (candidate settling in?)
  └─ Auto-create Week 2 follow-up if not exists

Day 14:
  ├─ Week 2 Follow-up (still working?)
  └─ Auto-create Day 30 follow-up

Day 30:
  ├─ Day 30 Follow-up (one month check)
  └─ Auto-create Day 60 follow-up

Day 60:
  ├─ Day 60 Follow-up (stability assessment)
  └─ Auto-create Day 90 follow-up

Day 90:
  ├─ Cron releases retention automatically
  ├─ Activity created to follow-up on payment
  ├─ Client should receive payment request
  └─ System shows retention as "released"

Day 90-120:
  ├─ Monitor for payment
  ├─ Send reminders
  └─ Mark as paid when received
```

### Scenario 2: Candidate Absconds (Day 45)
```
Day 45 (Follow-up):
  ├─ Follow-up shows "candidate_working = False"
  ├─ Mark as "absconded"
  └─ System auto-marks retention_at_risk

Manager View:
  ├─ High-risk alert on Retention
  ├─ Manager escalates to forfeit
  ├─ Opens Forfeit Wizard
  └─ Documents reason "Absconded"

Forfeiture:
  ├─ Retention state = "forfeited"
  ├─ Retention amount = lost revenue
  ├─ If guarantee: Search replacement candidate
  └─ Candidate marked "unavailable"
```

### Scenario 3: Client Terminates Early (Day 60)
```
Day 60 (Follow-up):
  ├─ Contact client for status
  ├─ Client reports: "Terminated for performance"
  ├─ Mark issue_severity = "critical"
  └─ Candidate resigned/terminated

Assessment:
  ├─ If within guarantee period:
  │  ├─ Must provide replacement
  │  ├─ Increment replacement_count
  │  └─ No additional revenue
  │
  ├─ If outside guarantee:
  │  ├─ Forfeit remaining retention
  │  └─ Record loss
```

---

## 🔐 Security Model

### User Roles
- **HR Manager** - Full access to retention & follow-ups
- **Finance** - Can view, mark payments, but not forfeit
- **Admin** - Can do everything

### Access Control
Default in `security/ir.model.access.csv`:
- Base.group_user can read/write retention and follow-ups
- Customize by adding group_id filters

### Sensitive Operations
- `action_forfeit_retention()` - Should require manager approval
- `action_mark_retention_paid()` - Should integrate with payment confirmation

---

## 📈 Dashboard & Reporting

### Key Metrics to Track
```
Retention Collection Rate = (Retention Paid / Total Retention Due) × 100
Target: 90%+

Follow-Up Compliance = (Completed / Scheduled) × 100
Target: 100%

Placement Stability Rate = (Candidates Staying 90 Days / Total Placed) × 100
Target: 95%+

Average Retention Days to Collection = Days from release to payment
Target: <30 days

Retention Lost (AED) = Total forfeited amounts
Track by month
```

### Recommended Reports
1. **Retention Aging** - How old are pending/released retentions?
2. **At-Risk Placements** - Which candidates showing issues?
3. **Collection Forecast** - When are retentions due?
4. **Follow-Up Compliance** - Completed vs overdue?
5. **Stability Report** - % completing retention period successfully?

---

## 🧪 Testing Checklist

### Unit Tests (Manual)
- [ ] Create retention, verify amounts calculated correctly
- [ ] Test placement_ready computation with various field combinations
- [ ] Test visa validity (expiry + 180 days logic)
- [ ] Test NOC requirement (only for employment visas)
- [ ] Test retention release date calculation

### Integration Tests
- [ ] Create deployment → auto-create retention
- [ ] Deployment date + 90 days = retention release date
- [ ] Mark upfront paid, verify state changes
- [ ] Mark retention paid, verify state = completed
- [ ] Forfeit retention, verify amount lost

### Workflow Tests
- [ ] Create follow-up, complete with issues
- [ ] Check retention_at_risk flag updates
- [ ] Escalate to management, verify activity created
- [ ] Week 1→90 follow-up sequence
- [ ] Overdue follow-up creates activity

### UI Tests
- [ ] Retention form loads with all fields
- [ ] Risk level changes colors (green/yellow/red)
- [ ] Buttons appear/disappear based on state
- [ ] Follow-up calendar shows schedule
- [ ] Kanban by risk level groups correctly

---

## 🐛 Troubleshooting

### Issue: Retention not releasing on due date
**Cause:** Cron job not running
**Fix:** 
```bash
# Check cron status
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf \
    --no-http --stop-after-init --update=recruitment_uae
# Check ir.cron records in DB
```

### Issue: Follow-ups not auto-creating
**Cause:** Cron not scheduled or deployment_date missing
**Fix:** 
- Ensure deployment.deployment_date is set
- Check cron_schedule_automatic_followups runs daily
- Verify is_deployment=deployed

### Issue: Placement blockers not showing
**Cause:** Compute methods not triggered
**Fix:**
- Update candidate record to trigger compute
- Check field dependencies in code

---

## 📝 Next Steps

### Phase 2: Enhanced Features
1. Email templates for payment reminders
2. SMS notifications for follow-up
3. Retention aging report
4. Dashboard with KPIs
5. Integration with payment module
6. Replacement guarantee automation

### Phase 3: Advanced Analytics
1. Predictive retention loss (which placements likely to fail?)
2. Candidate scoring (success likelihood)
3. Client segmentation (by retention collection rate)
4. Seasonality analysis (when do placements fail?)

---

## 📞 Support

For issues or questions:
1. Check logs: `/var/odoo/eigermarvel/logs/`
2. Use Odoo shell to debug:
   ```bash
   cd /var/odoo/eigermarvel && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf
   ```
3. Check database: `SELECT * FROM recruitment_retention;`
