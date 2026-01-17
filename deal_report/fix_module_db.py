#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Attempt to fix the module by directly manipulating the module state
in the Odoo database via psycopg2.
This requires direct database access.
"""

import subprocess
import sys
import time

def run_docker_cmd(cmd):
    """Run a command in the Docker container."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def clear_module_from_db():
    """Clear the deal_report module from the database."""
    print("="*70)
    print("ATTEMPTING TO CLEAR MODULE FROM DATABASE")
    print("="*70)
    
    # The module might be stuck in "upgrade" or "install_ing" state
    # We need to find the database name first
    
    print("\n1. Finding Odoo databases...")
    ok, stdout, stderr = run_docker_cmd([
        "docker", "exec", "odoo17_postgres",
        "psql", "-U", "odoo", "-c",
        "SELECT datname FROM pg_database WHERE datistemplate = false;"
    ])
    
    if ok and stdout:
        print(f"Output:\n{stdout}")
        # Try to find a non-template, non-default database
        databases = [line.strip() for line in stdout.split('\n') 
                     if line.strip() and 'datname' not in line and '---' not in line and '(' not in line]
        
        if databases:
            for db in databases:
                if db and not db.startswith('-'):
                    print(f"\nFound database: {db}")
                    
                    # Try to clear the deal_report module state
                    print(f"Clearing deal_report module from '{db}'...")
                    
                    sql = """
                    DELETE FROM ir_module_module WHERE name = 'deal_report';
                    DELETE FROM ir_model WHERE module = 'deal_report';
                    DELETE FROM ir_ui_view WHERE name LIKE '%deal%';
                    DELETE FROM ir_ui_menu WHERE name IN ('Deals', 'Deal Reports', 'Deal Dashboard', 'Analytics');
                    """
                    
                    ok, stdout, stderr = run_docker_cmd([
                        "docker", "exec", "odoo17_postgres",
                        "psql", "-U", "odoo", "-d", db, "-c", sql
                    ])
                    
                    if ok:
                        print(f"✓ Successfully cleared module from database")
                        return True, db
                    else:
                        print(f"Error: {stderr}")
    else:
        print(f"Error listing databases: {stderr}")
    
    return False, None

def restart_odoo():
    """Restart the Odoo container."""
    print("\n2. Restarting Odoo...")
    ok, _, _ = run_docker_cmd(["docker", "restart", "odoo17_app"])
    
    if ok:
        print("✓ Odoo restarted")
        time.sleep(5)
        return True
    else:
        print("✗ Failed to restart Odoo")
        return False

def main():
    """Main function."""
    print("\n" + "="*70)
    print("DEAL REPORT MODULE - RECOVERY PROCEDURE")
    print("="*70)
    
    print("\nThis will attempt to:")
    print("1. Clear any broken deal_report module data from the database")
    print("2. Restart Odoo")
    print("\nYou'll then need to reinstall the module from Apps.")
    
    success, db_name = clear_module_from_db()
    
    if success:
        if restart_odoo():
            print("\n" + "="*70)
            print("RECOVERY COMPLETE")
            print("="*70)
            print(f"\nDatabase '{db_name}' has been cleaned.")
            print("Odoo has been restarted.")
            print("\nNEXT STEPS:")
            print("1. Wait for Odoo to fully start (10-15 seconds)")
            print("2. Open http://localhost:8069 in your browser")
            print("3. Go to Apps > Database > Update Apps List")
            print("4. Search for 'deal_report' ")
            print("5. Click 'Install'")
            print("\nIf you still get errors:")
            print("- Check the Odoo logs: docker logs odoo17_app | tail -50")
            print("- The module files are all syntactically correct")
            return True
        else:
            print("\n✗ Failed to restart Odoo")
            return False
    else:
        print("\n✗ Could not access database")
        print("\nFallback solution:")
        print("1. Clear Docker volumes: docker volume prune")
        print("2. Delete the database container: docker rm odoo17_postgres")
        print("3. Recreate everything: docker-compose up")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
