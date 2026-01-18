#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Instance Discovery & Connection Test Tool
Helps identify available Odoo instances for testing
"""

import os
import sys
import json
from pathlib import Path
from urllib.parse import urlparse
import socket
import subprocess

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}{Colors.END}\n")


def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {text}{Colors.END}\n")


def print_ok(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_fail(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")


def check_env_variables():
    """Check environment variables for Odoo config"""
    print_section("Checking Environment Variables")
    
    env_vars = {
        'ODOO_URL': os.getenv('ODOO_URL'),
        'ODOO_DB': os.getenv('ODOO_DB'),
        'ODOO_USERNAME': os.getenv('ODOO_USERNAME'),
        'ODOO_INSTANCES': os.getenv('ODOO_INSTANCES'),
    }
    
    for var, value in env_vars.items():
        if value:
            if len(value) > 50:
                print_ok(f"{var}: {value[:50]}...")
            else:
                print_ok(f"{var}: {value}")
        else:
            print_info(f"{var}: not set")
    
    return env_vars


def check_port(host, port, timeout=2):
    """Check if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def test_odoo_connection(url, db, username, password):
    """Test Odoo connection"""
    print_section(f"Testing Connection: {url}")
    
    try:
        import xmlrpc.client
        
        # Parse URL
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        print(f"Host: {host}:{port}")
        
        # Check port
        if not check_port(host, port):
            print_fail(f"Port {port} is not open/reachable")
            return False
        
        print_ok(f"Port {port} is reachable")
        
        # Try authentication
        try:
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})
            
            if uid:
                print_ok(f"Successfully authenticated as user {uid}")
                print_ok(f"Database: {db}")
                return True
            else:
                print_fail("Authentication failed (invalid credentials?)")
                return False
        
        except Exception as e:
            print_fail(f"Connection error: {e}")
            return False
    
    except Exception as e:
        print_fail(f"Error: {e}")
        return False


def check_local_instances():
    """Check for local Odoo instances"""
    print_section("Checking Local Instances")
    
    common_ports = [8069, 8070, 8071, 8080, 8000]
    common_hosts = ['localhost', '127.0.0.1', 'odoo', '0.0.0.0']
    
    print("Scanning common ports...")
    
    found = False
    for port in common_ports:
        if check_port('localhost', port, timeout=1):
            print_ok(f"Port {port} is open")
            found = True
    
    if not found:
        print_info("No open ports found on localhost")
    
    return found


def check_config_files():
    """Check for Odoo config files"""
    print_section("Checking Configuration Files")
    
    config_paths = [
        Path('.') / 'odoo.conf',
        Path('~/.odoorc').expanduser(),
        Path('/etc/odoo/odoo.conf'),
        Path('/etc/odoo-server.conf'),
    ]
    
    for path in config_paths:
        if path.exists():
            print_ok(f"Found: {path}")
            
            # Try to read database name
            try:
                with open(path) as f:
                    for line in f:
                        if 'database' in line or 'db_name' in line:
                            print(f"  └─ {line.strip()}")
                        if 'db_host' in line:
                            print(f"  └─ {line.strip()}")
                        if 'db_port' in line:
                            print(f"  └─ {line.strip()}")
            except:
                pass
        else:
            print_info(f"Not found: {path}")


def check_docker():
    """Check for Docker Odoo containers"""
    print_section("Checking Docker Containers")
    
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'label=odoo', '--format', '{{.Names}}\t{{.Ports}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            print_ok("Docker Odoo containers found:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"  • {line}")
            return True
        else:
            print_info("No Docker Odoo containers found")
            return False
    
    except FileNotFoundError:
        print_info("Docker not installed or not in PATH")
        return False
    except Exception as e:
        print_fail(f"Error checking Docker: {e}")
        return False


def display_instructions():
    """Display testing instructions"""
    print_header("SETUP INSTRUCTIONS")
    
    print("""
Based on the diagnostic results above, here's what you need to do:

1. IDENTIFY YOUR ODOO INSTANCE
   
   Option A: Remote Instance
   • If testing against erp.sgctech.ai (from .env):
     python run_odoo_tests.py --url https://erp.sgctech.ai \\
                              --db scholarixv2 \\
                              --email your-email \\
                              --password your-password
   
   Option B: Local Instance
   • Make sure Odoo is running on localhost:8069
   • Check with: curl http://localhost:8069
   • If not running: python odoo-bin or docker-compose up
   
   Option C: Docker Instance
   • Start Docker container: docker-compose up -d
   • Wait 30 seconds for startup
   • Then run tests

2. VERIFY MODULE IS INSTALLED
   
   • In Odoo web UI: Go to Apps
   • Search for "deal_report"
   • Should see "Deal Report & Commission Management"
   • If not found, click Install

3. RUN TESTS
   
   Interactive mode:
   $ python test_runner_interactive.py
   
   Command line mode:
   $ python run_odoo_tests.py --url <your-url> --db <dbname> \\
                              --email <user> --password <pass>
   
   With default credentials from .env:
   $ python run_odoo_tests.py

4. MANUAL TESTING
   
   If automated tests don't work:
   • Open Odoo in browser
   • Navigate to Sales > Deal Report
   • Create a test deal
   • Verify fields and calculations
   • Test state transitions
   • Click smart buttons

NEXT STEP:
""")


def suggest_action():
    """Suggest next action"""
    print()
    url = os.getenv('ODOO_URL')
    db = os.getenv('ODOO_DB')
    username = os.getenv('ODOO_USERNAME')
    password = os.getenv('ODOO_PASSWORD')
    
    if url and db and username and password:
        print_ok(f"Found configuration in .env:")
        print(f"  URL: {url}")
        print(f"  DB: {db}")
        print(f"  User: {username}")
        print()
        print("To test this configuration, run:")
        print(f"  python run_odoo_tests.py --url {url} --db {db} \\\\")
        print(f"                          --email {username} --password {password}")
    else:
        print_info("No complete Odoo configuration found in .env")
        print()
        print("Please provide your Odoo instance details:")
        print("  python run_odoo_tests.py --url <url> --db <db> \\\\")
        print("                          --email <user> --password <pass>")


def main():
    print_header("ODOO INSTANCE DISCOVERY & CONNECTION TEST")
    
    # Run diagnostics
    check_env_variables()
    check_config_files()
    check_local_instances()
    check_docker()
    
    display_instructions()
    suggest_action()
    
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostics cancelled.")
        sys.exit(0)
