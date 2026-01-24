#!/usr/bin/env python3
"""
Test SGCTECHAI connection and troubleshoot authentication issues
"""

import xmlrpc.client
import sys

# SGCTECHAI configurations to test
CONFIGS = [
    {
        'name': 'HTTPS with SGCTECHAI (Current Config)',
        'url': 'https://scholarixglobal.com',
        'db': 'SGCTECHAI',
        'username': 'admin',
        'password': 'admin'
    },
    {
        'name': 'HTTP with SGCTECHAI',
        'url': 'http://scholarixglobal.com',
        'db': 'SGCTECHAI',
        'username': 'admin',
        'password': 'admin'
    },
    {
        'name': 'Localhost HTTPS',
        'url': 'https://localhost:8069',
        'db': 'SGCTECHAI',
        'username': 'admin',
        'password': 'admin'
    },
    {
        'name': 'Localhost HTTP',
        'url': 'http://localhost:8069',
        'db': 'SGCTECHAI',
        'username': 'admin',
        'password': 'admin'
    },
    {
        'name': '127.0.0.1 HTTP',
        'url': 'http://127.0.0.1:8069',
        'db': 'SGCTECHAI',
        'username': 'admin',
        'password': 'admin'
    }
]

def test_server_reachable(url):
    """Test if server is reachable"""
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        version = common.version()
        return True, version
    except Exception as e:
        return False, str(e)

def test_authentication(config):
    """Test authentication with given config"""
    try:
        common = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/common")
        uid = common.authenticate(
            config['db'],
            config['username'],
            config['password'],
            {}
        )
        if uid:
            return True, uid
        else:
            return False, "Authentication returned UID 0 (invalid credentials)"
    except Exception as e:
        return False, str(e)

def test_list_databases(url):
    """Try to list available databases"""
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        db_list = common.list()
        return True, db_list
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 80)
    print("SGCTECHAI CONNECTION TEST")
    print("=" * 80)
    print()
    
    successful_configs = []
    
    for config in CONFIGS:
        print(f"\nTesting: {config['name']}")
        print("-" * 80)
        print(f"URL: {config['url']}")
        print(f"Database: {config['db']}")
        print(f"Username: {config['username']}")
        print()
        
        # Test 1: Server reachability
        print("1. Testing server reachability...")
        reachable, result = test_server_reachable(config['url'])
        if reachable:
            print(f"   ✓ Server is reachable")
            print(f"   Server info: {result}")
        else:
            print(f"   ✗ Cannot reach server: {result}")
            continue
        
        # Test 2: List databases
        print("\n2. Listing available databases...")
        success, databases = test_list_databases(config['url'])
        if success:
            print(f"   ✓ Available databases: {', '.join(databases)}")
            if config['db'] in databases:
                print(f"   ✓ Database '{config['db']}' found!")
            else:
                print(f"   ⚠ Database '{config['db']}' NOT in list")
                print(f"   Available: {databases}")
        else:
            print(f"   ⚠ Could not list databases: {databases}")
        
        # Test 3: Authentication
        print("\n3. Testing authentication...")
        auth_success, uid = test_authentication(config)
        if auth_success:
            print(f"   ✓ AUTHENTICATION SUCCESSFUL!")
            print(f"   UID: {uid}")
            successful_configs.append(config)
        else:
            print(f"   ✗ Authentication failed: {uid}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if successful_configs:
        print(f"\n✓ Found {len(successful_configs)} working configuration(s):\n")
        for config in successful_configs:
            print(f"  ✓ {config['name']}")
            print(f"    URL: {config['url']}")
            print(f"    Database: {config['db']}")
            print()
        
        print("RECOMMENDED: Update claude_desktop_config.json with:")
        best_config = successful_configs[0]
        print(f"""
"sgctechai": {{
    "url": "{best_config['url']}",
    "db": "{best_config['db']}",
    "username": "{best_config['username']}",
    "password": "{best_config['password']}",
    "version": "v19",
    "environment": "On-Premise",
    "location": "LOCAL"
}}
        """)
    else:
        print("\n✗ No working configurations found!")
        print("\nPossible issues:")
        print("  1. Odoo server is not running")
        print("  2. Database 'SGCTECHAI' does not exist")
        print("  3. Wrong admin password")
        print("  4. Firewall blocking connections")
        print("  5. SSL/TLS certificate issues")
        print("\nTroubleshooting steps:")
        print("  1. Check if Odoo is running: ps aux | grep odoo")
        print("  2. Check Odoo logs: tail -f /var/log/odoo/odoo.log")
        print("  3. Verify database: psql -l | grep SGCTECHAI")
        print("  4. Reset admin password: odoo-bin -d SGCTECHAI --save --stop-after-init")
        print("  5. Check Odoo config: cat /etc/odoo/odoo.conf")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
