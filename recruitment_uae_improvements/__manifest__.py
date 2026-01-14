{
    "name": "Recruitment UAE Improvements",
    "version": "18.0.2.0.0",
    "category": "Human Resources",
    "summary": "Enhanced recruitment module with automated workflows and modern chatter",
    "description": """
Recruitment UAE Module Improvements
====================================

This module extends the recruitment_uae module with:

**Modernized Chatter Integration:**
- Field tracking on all key fields
- Activity-based workflow management
- Automated email notifications
- Follower auto-subscription

**Automated Stage Transitions:**
- Auto-create applications from approved requisitions
- Auto-create contracts from accepted applications
- Auto-create deployments from signed contracts
- Smart activity scheduling

**Smart Buttons:**
- Application count on requisitions
- Contract tracking on applications
- Deployment tracking on contracts
- Retention tracking on deployments

**Enhanced Views:**
- Modern chatter placement
- Kanban boards with color coding
- Statusbar widgets
- Improved tree views with decorations

**Activity Types:**
- Requisition review activities
- Application processing activities
- Contract review activities
- Deployment preparation activities
- Retention follow-up activities (30/60/90 days)

**Email Templates:**
- Requisition approval notifications
- Application acceptance emails
- Contract sent notifications
- Visa approval notifications
- Deployment confirmation emails

**Data Validation:**
- Enhanced field constraints
- Onchange methods for auto-population
- Date validation
- Salary validation

**Dashboard & Reporting:**
- Real-time statistics
- Activity tracking
- Stage progression analytics

Installation
------------
1. Backup your database
2. Copy improved files to recruitment_uae module
3. Restart Odoo server
4. Update module from Apps menu
5. Verify data integrity

Authors
-------
- Eiger Marvel HR Development Team
    """,
    "author": "Eiger Marvel HR",
    "website": "https://eigermarvelhr.com",
    "license": "LGPL-3",
    "depends": [
        "recruitment_uae",
        "mail",
        "hr",
        "base_automation",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/security_rules.xml",
        
        # Data
        "data/mail_activity_data.xml",
        "data/email_template_data.xml",
        "data/automated_action_data.xml",
        
        # Views
        "views/recruitment_job_requisition_views.xml",
        "views/recruitment_application_views.xml",
        "views/recruitment_contract_views.xml",
        "views/recruitment_deployment_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
