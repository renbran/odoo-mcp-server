#!/usr/bin/env python3
"""
Quick deployment status and checklist
"""

import json
from datetime import datetime

DEPLOYMENT_CHECKLIST = {
    "deployment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "target": {
        "url": "https://erp.sgctech.ai",
        "database": "scholarixv2",
        "user": "info@scholarixglobal.com"
    },
    "module": {
        "name": "deal_report",
        "version": "17.0.1.0.0",
        "status": "NOT INSTALLED ON SERVER",
        "local_path": "d:\\01_WORK_PROJECTS\\odoo-mcp-server\\deal_report"
    },
    "test_results": {
        "total": 17,
        "passed": 4,
        "failed": 13,
        "success_rate": "23.5%",
        "tests_passed": [
            "Connection Authentication",
            "Partner Creation (ID: 1808)",
            "Project Creation (ID: 36)",
            "Product Creation (ID: 374)"
        ],
        "tests_failed": [
            "Module Installation Check",
            "Model: deal.report",
            "Model: deal.commission.line",
            "Model: deal.bill.line",
            "View: deal_report_form_view",
            "View: deal_report_tree_view",
            "View: deal_report_search_view",
            "View: deal_commission_line_form_view",
            "View: deal_bill_line_form_view",
            "Security Group: group_deal_manager",
            "Security Group: group_deal_salesperson",
            "Deal Creation",
            "Access Control"
        ]
    },
    "root_cause": "Module not deployed to server's Odoo addons path",
    "deployment_checklist": {
        "step_1_connect_to_server": {
            "task": "SSH into server",
            "command": "ssh user@erp.sgctech.ai",
            "status": "❌ PENDING"
        },
        "step_2_find_addons_path": {
            "task": "Locate Odoo addons directory",
            "command": "grep -i 'addons_path' /etc/odoo/odoo.conf",
            "expected": "/var/lib/odoo/addons or similar",
            "status": "❌ PENDING"
        },
        "step_3_copy_module": {
            "task": "Copy deal_report module to server",
            "command": "scp -r deal_report/ user@erp.sgctech.ai:/var/lib/odoo/addons/",
            "status": "❌ PENDING",
            "notes": "Use the addons path from step 2"
        },
        "step_4_restart_odoo": {
            "task": "Restart Odoo service",
            "command": "systemctl restart odoo",
            "or_docker": "docker restart <container_id>",
            "status": "❌ PENDING"
        },
        "step_5_verify_installation": {
            "task": "Check module installation",
            "command": "python deploy_deal_report_module.py --action status",
            "expected_output": "Module state: installed",
            "status": "❌ PENDING"
        },
        "step_6_run_tests": {
            "task": "Run comprehensive test suite",
            "command": "python run_odoo_tests.py",
            "expected_result": "17/17 tests passing",
            "status": "❌ PENDING"
        },
        "step_7_verify_ui": {
            "task": "Verify in Odoo UI",
            "steps": [
                "Navigate to Apps",
                "Search for 'deal_report'",
                "Confirm module is installed",
                "Check menu for Deal Report entry"
            ],
            "status": "❌ PENDING"
        }
    },
    "files_created": {
        "deploy_deal_report_module.py": "RPC-based module deployment tool",
        "run_odoo_tests.py": "Comprehensive test suite (10 tests)",
        "test_runner_interactive.py": "Interactive testing menu",
        "diagnose_odoo_connection.py": "Connection diagnostics",
        "DEPLOYMENT_INSTRUCTIONS.md": "Detailed deployment guide",
        "TEST_REPORT_FINAL.md": "This test report",
        "DEPLOYMENT_CHECKLIST.py": "This checklist"
    },
    "quick_start": {
        "option_1_ssh": {
            "description": "Manual deployment via SSH (Recommended)",
            "steps": [
                "ssh user@erp.sgctech.ai",
                "cat /etc/odoo/odoo.conf | grep addons_path",
                "Exit and copy module: scp -r deal_report/ user@erp.sgctech.ai:/path/to/addons/",
                "SSH back and restart: systemctl restart odoo",
                "Run tests: python run_odoo_tests.py"
            ]
        },
        "option_2_docker": {
            "description": "Deployment in Docker container",
            "steps": [
                "docker ps | grep odoo  # Find container ID",
                "docker cp deal_report/ <container_id>:/var/lib/odoo/addons/",
                "docker exec <container_id> systemctl restart odoo",
                "Run tests: python run_odoo_tests.py"
            ]
        },
        "option_3_rpc": {
            "description": "Via Python RPC (after module in addons path)",
            "steps": [
                "Ensure module is in server's addons path",
                "Run: python deploy_deal_report_module.py --action install",
                "Verify: python run_odoo_tests.py"
            ]
        }
    },
    "troubleshooting": {
        "module_not_found": {
            "error": "Module deal_report not found in repository",
            "cause": "Module directory not in Odoo's addons path",
            "solution": "Copy deal_report/ to the correct addons directory on server"
        },
        "models_dont_exist": {
            "error": "Object deal.report doesn't exist",
            "cause": "Module not installed on server",
            "solution": "Deploy module and restart Odoo"
        },
        "views_not_loading": {
            "error": "View records return errors or not found",
            "cause": "Module not installed",
            "solution": "Deploy module and clear browser cache"
        },
        "indexerror_expression_parser": {
            "error": "IndexError in Odoo's expression.py",
            "cause": "Possible Odoo bug or system issue",
            "solution": "Verify Odoo logs: tail -f /var/log/odoo/odoo.log"
        }
    },
    "success_criteria": {
        "after_deployment": [
            "Module appears in Odoo Apps list",
            "Module status shows 'Installed'",
            "No errors in Odoo logs",
            "All 17 tests pass",
            "Menu entry visible in UI",
            "Models accessible via API"
        ]
    },
    "contact_info": {
        "remote_server": "erp.sgctech.ai",
        "database": "scholarixv2",
        "admin_user": "info@scholarixglobal.com",
        "log_location": "/var/log/odoo/odoo.log (typical)",
        "config_file": "/etc/odoo/odoo.conf (typical)"
    }
}

def print_checklist():
    """Print formatted checklist"""
    print("\n" + "="*80)
    print("  DEAL REPORT MODULE - DEPLOYMENT CHECKLIST")
    print("="*80)
    print(f"\nDate: {DEPLOYMENT_CHECKLIST['deployment_date']}")
    print(f"Target: {DEPLOYMENT_CHECKLIST['target']['url']}/{DEPLOYMENT_CHECKLIST['target']['database']}")
    print(f"Module: {DEPLOYMENT_CHECKLIST['module']['name']} v{DEPLOYMENT_CHECKLIST['module']['version']}")
    
    print(f"\n📊 TEST RESULTS")
    print(f"   Passed: {DEPLOYMENT_CHECKLIST['test_results']['passed']}/17 ✅")
    print(f"   Failed: {DEPLOYMENT_CHECKLIST['test_results']['failed']}/17 ❌")
    print(f"   Success Rate: {DEPLOYMENT_CHECKLIST['test_results']['success_rate']}")
    
    print(f"\n⚠️  ROOT CAUSE")
    print(f"   {DEPLOYMENT_CHECKLIST['root_cause']}")
    
    print(f"\n📋 DEPLOYMENT STEPS")
    steps = DEPLOYMENT_CHECKLIST['deployment_checklist']
    for i, (key, step) in enumerate(steps.items(), 1):
        print(f"\n   Step {i}: {step['task']}")
        if 'command' in step:
            print(f"   Command: {step['command']}")
        if 'status' in step:
            print(f"   Status: {step['status']}")
    
    print(f"\n🚀 QUICK START OPTIONS")
    for option, details in DEPLOYMENT_CHECKLIST['quick_start'].items():
        print(f"\n   {details['description']}")
        for j, step in enumerate(details['steps'], 1):
            print(f"   {j}. {step}")
    
    print(f"\n✅ SUCCESS CRITERIA")
    for criterion in DEPLOYMENT_CHECKLIST['success_criteria']['after_deployment']:
        print(f"   ☐ {criterion}")
    
    print(f"\n📁 FILES PROVIDED")
    for filename, purpose in DEPLOYMENT_CHECKLIST['files_created'].items():
        print(f"   • {filename}")
        print(f"     └─ {purpose}")
    
    print("\n" + "="*80)
    print("NEXT ACTION: Deploy module to server using one of the options above")
    print("="*80 + "\n")

def save_json():
    """Save checklist as JSON"""
    with open('DEPLOYMENT_CHECKLIST.json', 'w') as f:
        json.dump(DEPLOYMENT_CHECKLIST, f, indent=2)
    print("✅ Checklist saved to DEPLOYMENT_CHECKLIST.json")

if __name__ == '__main__':
    print_checklist()
    save_json()
