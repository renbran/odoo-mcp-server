{
    'name': 'Recruitment UAE - Retention & Follow-up Management',
    'version': '1.0.0',
    'category': 'Human Resources/Recruitment',
    'sequence': 25,
    
    'author': 'SGC Tech AI',
    'website': 'https://www.sgtechai.com',
    'license': 'LGPL-3',
    
    'summary': 'Complete placement retention and post-placement follow-up management system for recruitment UAE module',
    
    'description': '''
        Recruitment UAE - Retention & Follow-up Management
        ==================================================
        
        This module extends the standard Odoo recruitment module with comprehensive
        retention and follow-up management features for the UAE recruitment industry.
        
        Key Features:
        - Placement Retention Tracking
          * Automatic retention period calculation
          * Upfront and retention payment tracking
          * Candidate stability monitoring
          * Risk assessment system
          * Forfeiture management
        
        - Post-Placement Follow-ups
          * Scheduled follow-up tracking
          * Automatic follow-up scheduling (1w, 2w, 4w, 30d, 60d, 90d)
          * Candidate location and working status
          * Issue and concern tracking
          * Next action recommendations
          * Retention risk flagging
        
        - Candidate Enhancement
          * Visa status tracking (6 types)
          * NOC (No Objection Certificate) management
          * Document verification
          * Placement readiness assessment
          * Placement history tracking
        
        - Professional UI
          * Fully responsive design (mobile, tablet, desktop)
          * Risk-based Kanban views
          * Calendar scheduling
          * Color-coded alerts and status indicators
          * Chatter integration for notes and activities
        
        - Automation
          * Automatic retention release when due
          * Scheduled follow-up creation
          * Overdue follow-up alerts
          * Activity-based reminders
        
        - Reports & Analytics
          * Risk assessment reports
          * Payment tracking
          * Follow-up completion rates
          * Candidate stability metrics
    ''',
    
    'depends': [
        'recruitment',      # Base recruitment module
        'mail',              # Chatter and messaging
        'hr',                # HR functionality
        'base',              # Basic Odoo features
    ],
    
    'data': [
        # Views and UI
        'views/views_retention_followup.xml',
        # Reports
        'report/report_invoice_with_deals.xml',
    ],
    
    'demo': [
        # Demo data can be added here
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    
    # Technical metadata
    'images': [],
    'post_init_hook': None,
    'pre_init_hook': None,
    'post_load': None,
    
    # Version compatibility
    'support': 'support@sgtechai.com',
}
