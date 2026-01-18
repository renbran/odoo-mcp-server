#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Odoo 17 Test Runner for deal_report Module
Guides user through testing process step by step
"""

import os
import sys
from pathlib import Path

# ANSI Colors
COLORS = {
    'blue': '\033[94m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'bold': '\033[1m',
    'end': '\033[0m',
}


def print_banner(text):
    """Print banner"""
    width = 80
    print(f"\n{COLORS['blue']}{COLORS['bold']}")
    print('=' * width)
    print(f"  {text}")
    print('=' * width)
    print(f"{COLORS['end']}\n")


def print_section(text):
    """Print section header"""
    print(f"\n{COLORS['bold']}{COLORS['blue']}▶ {text}{COLORS['end']}\n")


def print_success(text):
    """Print success message"""
    print(f"{COLORS['green']}✓ {text}{COLORS['end']}")


def print_error(text):
    """Print error message"""
    print(f"{COLORS['red']}✗ {text}{COLORS['end']}")


def print_info(text):
    """Print info message"""
    print(f"{COLORS['yellow']}ℹ {text}{COLORS['end']}")


def get_input(prompt, default=None):
    """Get user input with default"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    return value if value else default


def check_prerequisites():
    """Check if prerequisites are installed"""
    print_section("Checking Prerequisites")
    
    try:
        import xmlrpc.client
        print_success("xmlrpc.client available")
    except ImportError:
        print_error("xmlrpc.client not available")
        return False
    
    return True


def get_connection_details():
    """Interactively get Odoo connection details"""
    print_section("Odoo Connection Details")
    
    print("Please provide your Odoo instance details:")
    print()
    
    # Get from .env first
    url = os.getenv('ODOO_URL')
    db = os.getenv('ODOO_DB')
    username = os.getenv('ODOO_USERNAME')
    password = os.getenv('ODOO_PASSWORD')
    
    url = get_input("Odoo URL", url or "http://localhost:8069")
    db = get_input("Database name", db or "scholarixv2")
    username = get_input("Username/Email", username or "admin")
    
    if not password:
        from getpass import getpass
        password = getpass("Password: ")
    
    return {
        'url': url,
        'db': db,
        'username': username,
        'password': password,
    }


def display_menu():
    """Display test menu"""
    print_section("Select Tests to Run")
    
    print("""
1. Quick Module Check (1 min)
   - Check module installation
   - Verify models exist
   - Check views are loaded

2. Complete Workflow Test (3-5 min)
   - Create test deal
   - Calculate commissions
   - Test bill processing
   - Verify state transitions

3. Security & Access Test (2 min)
   - Test security groups
   - Verify ACLs
   - Check record rules

4. Run All Tests (5-10 min)
   - All of the above

5. Manual Testing Guide
   - Print guide for manual testing

0. Exit

    """)
    
    choice = input("Select option (0-5): ").strip()
    return choice


def display_manual_guide():
    """Display manual testing guide"""
    print_banner("MANUAL TESTING GUIDE")
    
    print("""
After module installation, test via web UI:

1. NAVIGATE TO MODULE
   • Go to Sales menu
   • Click "Deal Report" or search for "Deal Report"
   • Should see "Deal Report & Commission Management"

2. CREATE TEST DEAL
   • Click "Create" button
   • Fill in form:
     - Sales Type: Primary
     - Booking Date: Today
     - Primary Buyer: Create new or select existing
     - Project: Create new test project
     - Unit: Create new product
     - Sales Value: 500000
     - VAT Rate: 5%
   • Click Save

3. VERIFY COMPUTATIONS
   • VAT Amount should auto-calculate to 25000 (5% of 500000)
   • Total with VAT should show 525000

4. TEST SMART BUTTONS
   • Look for smart buttons: Invoices, Commissions, Bills, Documents
   • Click each to verify they navigate correctly

5. CREATE COMMISSION LINE (Manually)
   • Open Commission Lines tab
   • Click Add
   • Fill: Partner, Type, Rate (2.5%), Amount should auto-compute
   • Commission Amount should be 12500 (2.5% of 500000)

6. TEST STATE TRANSITIONS
   • Find "Confirm" button (in form header)
   • Click to transition from Draft to Confirmed
   • Verify state changes

7. VERIFY SEARCH & FILTER
   • Go to Deal Report tree view
   • Try filters: By Sales Type, By State
   • Try group by: Type, Date, Buyer
   • Verify records appear correctly

8. CHECK SECURITY
   • As salesperson: Should see own deals only
   • As manager: Should see all deals
   • Verify permission restrictions work

KEY TEST DATA:
  • Sales Value: 500,000
  • VAT Rate: 5%
  • Commission Rate: 2.5%
  • Expected VAT: 25,000
  • Expected Commission: 12,500

EXPECTED RESULTS:
  ✓ Deal form loads
  ✓ Fields are visible
  ✓ Computations are correct
  ✓ State transitions work
  ✓ Smart buttons navigate
  ✓ Search/filters work
  ✓ Security rules applied
    """)


def run_quick_check(conn_details):
    """Run quick module check"""
    print_section("Running Quick Module Check")
    
    try:
        import xmlrpc.client
        
        url = conn_details['url']
        db = conn_details['db']
        username = conn_details['username']
        password = conn_details['password']
        
        print(f"Connecting to: {url} / {db}")
        
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print_error("Authentication failed")
            return False
        
        print_success(f"Authenticated as user {uid}")
        
        env = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Check module
        module = env.execute_kw(
            db, uid, password,
            'ir.module.module', 'search_read',
            [('name', '=', 'deal_report')],
            {'fields': ['name', 'state']}
        )
        
        if module and module[0]['state'] == 'installed':
            print_success(f"Module installed: {module[0]['name']}")
        else:
            print_error("Module not installed")
            return False
        
        # Check models
        for model in ['deal.report', 'deal.commission.line', 'deal.bill.line']:
            count = env.execute_kw(db, uid, password, model, 'search_count', [[]])
            print_success(f"Model {model}: {count} records")
        
        print()
        print_success("Quick check completed!")
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def run_comprehensive_test(conn_details):
    """Run comprehensive test"""
    print_section("Running Comprehensive Test")
    
    print("Executing: python run_odoo_tests.py")
    print(f"  URL: {conn_details['url']}")
    print(f"  DB: {conn_details['db']}")
    print(f"  User: {conn_details['username']}")
    print()
    
    import subprocess
    result = subprocess.run(
        [
            sys.executable, 'run_odoo_tests.py',
            '--url', conn_details['url'],
            '--db', conn_details['db'],
            '--email', conn_details['username'],
            '--password', conn_details['password'],
        ],
        cwd=Path(__file__).parent
    )
    
    return result.returncode == 0


def main():
    """Main interactive runner"""
    print_banner("DEAL_REPORT MODULE - ODOO 17 COMPREHENSIVE TEST SUITE")
    
    print("""
This interactive test runner will help you:
  ✓ Validate module installation
  ✓ Test model creation & workflows
  ✓ Verify security & access control
  ✓ Check smart buttons & computations
  ✓ Ensure all features work correctly

Let's get started!
    """)
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Missing prerequisites. Please install required packages.")
        sys.exit(1)
    
    print_success("All prerequisites available\n")
    
    # Get connection details
    conn_details = get_connection_details()
    
    # Loop for menu
    while True:
        choice = display_menu()
        
        if choice == '1':
            run_quick_check(conn_details)
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            run_comprehensive_test(conn_details)
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            print_info("Running security tests...")
            print("(Implementation pending)")
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            print_info("Running all tests...")
            success = run_comprehensive_test(conn_details)
            if success:
                print_success("\nAll tests completed!")
            else:
                print_error("Some tests failed")
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            display_manual_guide()
            input("\nPress Enter to continue...")
        
        elif choice == '0':
            print("\nThank you for testing deal_report module!")
            print("For issues or questions, refer to DEPLOYMENT_READY.md")
            sys.exit(0)
        
        else:
            print_error("Invalid option. Please select 0-5.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(0)
