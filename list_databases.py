#!/usr/bin/env python3
"""
List all available databases on local Odoo instance
"""

import xmlrpc.client
import psycopg2

def list_via_xmlrpc(url):
    """Try to list databases via XML-RPC (may be disabled)"""
    print(f"Attempting XML-RPC database list from {url}...")
    try:
        db = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/db")
        databases = db.list()
        return True, databases
    except Exception as e:
        return False, str(e)

def list_via_postgres():
    """List databases directly from PostgreSQL"""
    print("\nAttempting direct PostgreSQL connection...")
    
    # Common PostgreSQL connection attempts
    configs = [
        {'host': 'localhost', 'port': 5432, 'user': 'odoo', 'password': 'odoo'},
        {'host': 'localhost', 'port': 5432, 'user': 'postgres', 'password': 'postgres'},
        {'host': '127.0.0.1', 'port': 5432, 'user': 'odoo', 'password': 'odoo'},
        {'host': 'db', 'port': 5432, 'user': 'odoo', 'password': 'odoo'},  # Docker
    ]
    
    for config in configs:
        try:
            print(f"  Trying {config['user']}@{config['host']}:{config['port']}...")
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database='postgres'  # Connect to default postgres DB
            )
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT datname 
                FROM pg_database 
                WHERE datistemplate = false 
                AND datname NOT IN ('postgres')
                ORDER BY datname;
            """)
            
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return True, databases, config
            
        except Exception as e:
            continue
    
    return False, "Could not connect to PostgreSQL", None

def main():
    print("=" * 80)
    print("DATABASE DISCOVERY - LOCAL ODOO INSTANCE")
    print("=" * 80)
    print()
    
    # Test both local URLs
    urls = [
        'http://localhost:8069',
        'http://127.0.0.1:8069',
        'https://scholarixglobal.com',
        'http://scholarixglobal.com'
    ]
    
    xmlrpc_found = False
    databases_xmlrpc = []
    
    for url in urls:
        success, result = list_via_xmlrpc(url)
        if success:
            print(f"  ✓ Success from {url}")
            print(f"  Databases: {result}")
            databases_xmlrpc = result
            xmlrpc_found = True
            break
        else:
            print(f"  ✗ Failed from {url}: {result[:100]}...")
    
    # Try PostgreSQL directly
    print("\n" + "=" * 80)
    success, result, config = list_via_postgres()
    
    if success:
        print(f"  ✓ Connected to PostgreSQL!")
        print(f"  Connection: {config['user']}@{config['host']}:{config['port']}")
        print(f"\n  Found {len(result)} database(s):")
        print("  " + "-" * 76)
        
        for i, db in enumerate(result, 1):
            print(f"  {i}. {db}")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATION")
        print("=" * 80)
        
        if result:
            if 'SGCTECHAI' in result:
                print(f"\n✓ Database 'SGCTECHAI' EXISTS!")
            else:
                print(f"\n⚠ Database 'SGCTECHAI' NOT FOUND!")
                print(f"\nAvailable databases:")
                for db in result:
                    print(f"  - {db}")
                
                # Suggest closest match
                sgc_like = [db for db in result if 'sgc' in db.lower() or 'tech' in db.lower()]
                if sgc_like:
                    print(f"\n💡 Possible matches:")
                    for db in sgc_like:
                        print(f"  → {db}")
                    
                    print(f"\n📝 Update your claude_desktop_config.json:")
                    print(f"""
"sgctechai": {{
    "url": "http://localhost:8069",
    "db": "{sgc_like[0]}",  ← Use this database name
    "username": "admin",
    "password": "admin",
    "version": "v17",
    "environment": "On-Premise",
    "location": "LOCAL"
}}
                    """)
                else:
                    print(f"\n💡 To create 'SGCTECHAI' database:")
                    print(f"  1. Go to http://localhost:8069/web/database/manager")
                    print(f"  2. Click 'Create Database'")
                    print(f"  3. Name: SGCTECHAI")
                    print(f"  4. Admin password: admin")
        
    else:
        print(f"  ✗ Could not connect to PostgreSQL: {result}")
        print(f"\n  Try manually:")
        print(f"  psql -U odoo -h localhost -p 5432 -l")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
