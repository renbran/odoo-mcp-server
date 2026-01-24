# -*- coding: utf-8 -*-
{
    'name': 'UAE HR Payroll Compliance',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'UAE Labor Law Compliance, WPS Integration & Employee Self-Service',
    'description': """
UAE HR Payroll Compliance System
=================================

Complete UAE Labor Law compliance solution with:

**Phase 1: Employee Master Data & Compliance Fields**
* MOHRE Person ID and WPS integration fields
* Emirates ID tracking with expiry alerts
* Visa and labor card management
* GPSSA registration for UAE nationals
* Banking details with IBAN validation
* Contract compliance (Basic salary ≥ 50% requirement)

**Key Features:**
* Automated document expiry alerts (60-day advance warning)
* WPS-ready employee data structure
* UAE Labor Law compliant salary structure
* Complete audit trail for compliance
* Real-time validation and error prevention

**Compliance Standards:**
* UAE Labor Law (Federal Law No. 8 of 1980)
* MOHRE regulations
* WPS (Wage Protection System) requirements
* Central Bank of UAE specifications
* GPSSA guidelines for UAE nationals

**Technical Features:**
* Production-ready code with error handling
* Comprehensive field validation
* Automated calculations and onchange methods
* Mobile-responsive compliance tabs
* Integration-ready for WPS file generation

    """,
    'author': 'SGC TECH AI',
    'website': 'https://www.sgctech.ai',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_contract',
        'hr_uae',  # Build on existing UAE HR module
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
