#!/usr/bin/env python3
"""
OSUS Properties - Contact Duplicate Checker
Identifies duplicate contacts by email, phone, mobile, and name
"""

import xmlrpc.client
import json
from datetime import datetime
from collections import defaultdict

# Server configuration
PROD_URL = "http://localhost:8070"  # Use localhost when running on server
PROD_DB = "osusproperties"
PROD_USER = "salescompliance@osusproperties.com"
PROD_PASS = "8586583"

def normalize_phone(phone):
    """Remove common phone number formatting"""
    if not phone:
        return None
    # Remove spaces, dashes, parentheses, plus signs
    return ''.join(c for c in str(phone) if c.isdigit())

def normalize_email(email):
    """Normalize email for comparison"""
    if not email:
        return None
    return str(email).lower().strip()

def normalize_name(name):
    """Normalize name for fuzzy matching"""
    if not name:
        return None
    return ' '.join(str(name).lower().split())

def check_duplicates():
    """Check for duplicate contacts in the database"""
    print("=" * 80)
    print("OSUS PROPERTIES - CONTACT DUPLICATE CHECKER")
    print("=" * 80)
    print()
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f"{PROD_URL}/xmlrpc/2/common")
    uid = common.authenticate(PROD_DB, PROD_USER, PROD_PASS, {})
    
    if not uid:
        print("❌ Authentication failed!")
        return
    
    print(f"✓ Connected to {PROD_DB} (UID: {uid})")
    print()
    
    models = xmlrpc.client.ServerProxy(f"{PROD_URL}/xmlrpc/2/object")
    
    # Get all contacts
    print("📥 Fetching all contacts...")
    partner_ids = models.execute_kw(
        PROD_DB, uid, PROD_PASS,
        'res.partner', 'search',
        [[]]
    )
    
    partners = models.execute_kw(
        PROD_DB, uid, PROD_PASS,
        'res.partner', 'read',
        [partner_ids, ['name', 'email', 'phone', 'mobile', 'is_company', 
                       'customer_rank', 'supplier_rank', 'active', 'create_date']]
    )
    
    print(f"✓ Found {len(partners)} total contacts")
    print()
    
    # Group by different criteria
    email_groups = defaultdict(list)
    phone_groups = defaultdict(list)
    mobile_groups = defaultdict(list)
    name_groups = defaultdict(list)
    
    # Categorize partners
    active_partners = []
    inactive_partners = []
    companies = []
    individuals = []
    
    for partner in partners:
        if partner.get('active'):
            active_partners.append(partner)
        else:
            inactive_partners.append(partner)
        
        if partner.get('is_company'):
            companies.append(partner)
        else:
            individuals.append(partner)
        
        # Group by email
        email = normalize_email(partner.get('email'))
        if email:
            email_groups[email].append(partner)
        
        # Group by phone
        phone = normalize_phone(partner.get('phone'))
        if phone and len(phone) >= 7:  # Only consider valid phone numbers
            phone_groups[phone].append(partner)
        
        # Group by mobile
        mobile = normalize_phone(partner.get('mobile'))
        if mobile and len(mobile) >= 7:
            mobile_groups[mobile].append(partner)
        
        # Group by name
        name = normalize_name(partner.get('name'))
        if name:
            name_groups[name].append(partner)
    
    # Find duplicates
    email_duplicates = {k: v for k, v in email_groups.items() if len(v) > 1}
    phone_duplicates = {k: v for k, v in phone_groups.items() if len(v) > 1}
    mobile_duplicates = {k: v for k, v in mobile_groups.items() if len(v) > 1}
    name_duplicates = {k: v for k, v in name_groups.items() if len(v) > 1}
    
    # Print summary
    print("📊 CONTACT SUMMARY")
    print(f"   Total Contacts:       {len(partners)}")
    print(f"   Active:               {len(active_partners)}")
    print(f"   Inactive/Archived:    {len(inactive_partners)}")
    print(f"   Companies:            {len(companies)}")
    print(f"   Individuals:          {len(individuals)}")
    print()
    
    print("🔍 DUPLICATE ANALYSIS")
    print(f"   Duplicate Emails:     {len(email_duplicates)} ({sum(len(v) for v in email_duplicates.values())} contacts)")
    print(f"   Duplicate Phones:     {len(phone_duplicates)} ({sum(len(v) for v in phone_duplicates.values())} contacts)")
    print(f"   Duplicate Mobiles:    {len(mobile_duplicates)} ({sum(len(v) for v in mobile_duplicates.values())} contacts)")
    print(f"   Duplicate Names:      {len(name_duplicates)} ({sum(len(v) for v in name_duplicates.values())} contacts)")
    print()
    
    # Detailed duplicate reports
    duplicates_report = {
        'timestamp': datetime.now().isoformat(),
        'total_contacts': len(partners),
        'active_contacts': len(active_partners),
        'inactive_contacts': len(inactive_partners),
        'duplicate_summary': {
            'by_email': len(email_duplicates),
            'by_phone': len(phone_duplicates),
            'by_mobile': len(mobile_duplicates),
            'by_name': len(name_duplicates)
        },
        'duplicates': {
            'email': [],
            'phone': [],
            'mobile': [],
            'name': []
        }
    }
    
    # Email duplicates
    if email_duplicates:
        print("=" * 80)
        print("📧 DUPLICATE EMAILS")
        print("=" * 80)
        print()
        
        for email, partners_list in sorted(email_duplicates.items(), 
                                          key=lambda x: len(x[1]), 
                                          reverse=True)[:20]:  # Top 20
            print(f"Email: {email} ({len(partners_list)} contacts)")
            dup_entry = {'email': email, 'count': len(partners_list), 'contacts': []}
            
            for p in partners_list:
                status = "✓ Active" if p.get('active') else "✗ Inactive"
                type_str = "Company" if p.get('is_company') else "Individual"
                customer = "Customer" if p.get('customer_rank', 0) > 0 else ""
                supplier = "Supplier" if p.get('supplier_rank', 0) > 0 else ""
                roles = f"{customer} {supplier}".strip() or "No role"
                
                print(f"  • ID {p['id']}: {p.get('name', 'N/A')} | {type_str} | {roles} | {status}")
                
                dup_entry['contacts'].append({
                    'id': p['id'],
                    'name': p.get('name'),
                    'active': p.get('active'),
                    'is_company': p.get('is_company'),
                    'customer_rank': p.get('customer_rank'),
                    'supplier_rank': p.get('supplier_rank'),
                    'create_date': p.get('create_date')
                })
            
            print()
            duplicates_report['duplicates']['email'].append(dup_entry)
    
    # Phone duplicates
    if phone_duplicates:
        print("=" * 80)
        print("📞 DUPLICATE PHONE NUMBERS")
        print("=" * 80)
        print()
        
        for phone, partners_list in sorted(phone_duplicates.items(), 
                                          key=lambda x: len(x[1]), 
                                          reverse=True)[:15]:  # Top 15
            print(f"Phone: {phone} ({len(partners_list)} contacts)")
            dup_entry = {'phone': phone, 'count': len(partners_list), 'contacts': []}
            
            for p in partners_list:
                status = "✓" if p.get('active') else "✗"
                print(f"  • [{status}] ID {p['id']}: {p.get('name', 'N/A')} | Email: {p.get('email', 'N/A')}")
                
                dup_entry['contacts'].append({
                    'id': p['id'],
                    'name': p.get('name'),
                    'email': p.get('email'),
                    'active': p.get('active')
                })
            
            print()
            duplicates_report['duplicates']['phone'].append(dup_entry)
    
    # Mobile duplicates
    if mobile_duplicates:
        print("=" * 80)
        print("📱 DUPLICATE MOBILE NUMBERS")
        print("=" * 80)
        print()
        
        for mobile, partners_list in sorted(mobile_duplicates.items(), 
                                           key=lambda x: len(x[1]), 
                                           reverse=True)[:15]:  # Top 15
            print(f"Mobile: {mobile} ({len(partners_list)} contacts)")
            dup_entry = {'mobile': mobile, 'count': len(partners_list), 'contacts': []}
            
            for p in partners_list:
                status = "✓" if p.get('active') else "✗"
                print(f"  • [{status}] ID {p['id']}: {p.get('name', 'N/A')} | Email: {p.get('email', 'N/A')}")
                
                dup_entry['contacts'].append({
                    'id': p['id'],
                    'name': p.get('name'),
                    'email': p.get('email'),
                    'active': p.get('active')
                })
            
            print()
            duplicates_report['duplicates']['mobile'].append(dup_entry)
    
    # Name duplicates (only show top ones with high counts)
    significant_name_duplicates = {k: v for k, v in name_duplicates.items() if len(v) >= 3}
    
    if significant_name_duplicates:
        print("=" * 80)
        print("👤 DUPLICATE NAMES (3+ occurrences)")
        print("=" * 80)
        print()
        
        for name, partners_list in sorted(significant_name_duplicates.items(), 
                                         key=lambda x: len(x[1]), 
                                         reverse=True)[:10]:  # Top 10
            print(f"Name: {name} ({len(partners_list)} contacts)")
            dup_entry = {'name': name, 'count': len(partners_list), 'contacts': []}
            
            for p in partners_list:
                status = "✓" if p.get('active') else "✗"
                email = p.get('email', 'No email')
                phone = p.get('phone') or p.get('mobile', 'No phone')
                print(f"  • [{status}] ID {p['id']}: {email} | {phone}")
                
                dup_entry['contacts'].append({
                    'id': p['id'],
                    'email': p.get('email'),
                    'phone': p.get('phone'),
                    'mobile': p.get('mobile'),
                    'active': p.get('active')
                })
            
            print()
            duplicates_report['duplicates']['name'].append(dup_entry)
    
    # Save report
    report_file = f"contact_duplicates_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(duplicates_report, f, indent=2)
    
    print("=" * 80)
    print("✅ DUPLICATE CHECK COMPLETE")
    print("=" * 80)
    print(f"📄 Report saved: {report_file}")
    print()
    
    # Recommendations
    if email_duplicates or phone_duplicates or mobile_duplicates:
        print("💡 RECOMMENDATIONS")
        print()
        print("   To merge duplicates via Odoo UI:")
        print("   1. Go to: Contacts → Select duplicates")
        print("   2. Action → Merge → Choose which record to keep")
        print("   3. Confirm merge")
        print()
        print("   To archive inactive duplicates:")
        print("   1. Review inactive contacts with duplicates")
        print("   2. Archive or delete obsolete records")
        print("   3. Keep the most recent/complete record")
        print()
    else:
        print("✅ No significant duplicates found!")
        print()
    
    return duplicates_report

if __name__ == "__main__":
    check_duplicates()
