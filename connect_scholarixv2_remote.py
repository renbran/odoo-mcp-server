#!/usr/bin/env python3
"""
Connect local scholarixv2 Odoo instance to remote server
Syncs modules, configurations, and credentials
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ScholarixV2RemoteConnector:
    def __init__(self):
        # Local scholarixv2 config
        self.local_path = "/var/odoo/scholarixv2"
        self.local_db = "scholarixv2"
        self.local_conf = "/var/odoo/scholarixv2/odoo.conf"
        
        # Remote server config
        self.remote_url = os.getenv("ODOO_URL", "https://erp.sgctech.ai")
        self.remote_db = os.getenv("ODOO_DB", "commission_ax")
        self.username = os.getenv("ODOO_USERNAME", "info@scholarixglobal.com")
        self.password = os.getenv("ODOO_PASSWORD", "123456")
        
        # Session for remote API calls
        self.session = requests.Session()
        self.auth_uid = None
        self.auth_session_id = None
        
    def authenticate_remote(self):
        """Authenticate with remote Odoo server"""
        print(f"🔐 Authenticating with remote server: {self.remote_url}")
        
        try:
            # Authenticate and get session
            auth_url = f"{self.remote_url}/web/session/authenticate"
            auth_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "login": self.username,
                    "password": self.password,
                    "db": self.remote_db
                },
                "id": 1
            }
            
            response = self.session.post(
                auth_url,
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    print("   ✅ Authentication successful")
                    return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Connection error: {str(e)}")
            return False
    
    def get_remote_modules(self):
        """Fetch installed modules from remote server"""
        print(f"\n📦 Fetching modules from {self.remote_url}...")
        
        try:
            modules_url = f"{self.remote_url}/api/modules/installed"
            response = self.session.get(modules_url)
            
            if response.status_code == 200:
                modules = response.json()
                print(f"   ✅ Found {len(modules)} installed modules")
                return modules
            else:
                print(f"   ⚠️  Could not fetch modules: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error fetching modules: {str(e)}")
            return []
    
    def sync_commission_ax_module(self):
        """Ensure commission_ax module is synced"""
        print("\n🔄 Syncing commission_ax module...")
        
        try:
            sync_url = f"{self.remote_url}/api/modules/sync"
            sync_data = {
                "module": "commission_ax",
                "target_db": self.remote_db
            }
            
            response = self.session.post(
                sync_url,
                json=sync_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("   ✅ Module sync successful")
                return True
            else:
                print(f"   ⚠️  Sync status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Sync error: {str(e)}")
            return False
    
    def test_connection(self):
        """Test connection to remote server"""
        print(f"\n🧪 Testing connection to {self.remote_url}...")
        
        try:
            response = self.session.get(f"{self.remote_url}/web/health", timeout=5)
            
            if response.status_code == 200:
                print("   ✅ Connection successful")
                return True
            else:
                print(f"   ⚠️  Server responded with {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Cannot reach server: {self.remote_url}")
            return False
        except Exception as e:
            print(f"   ❌ Connection error: {str(e)}")
            return False
    
    def generate_connection_config(self):
        """Generate configuration for scholarixv2 to connect to remote"""
        config = {
            "local_instance": {
                "path": self.local_path,
                "database": self.local_db,
                "config_file": self.local_conf
            },
            "remote_server": {
                "url": self.remote_url,
                "database": self.remote_db,
                "username": self.username,
                "authenticated": bool(self.auth_uid)
            },
            "modules": {
                "required": ["commission_ax", "deal_tracking"],
                "status": "syncing"
            }
        }
        
        config_file = "scholarixv2_remote_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuration saved to {config_file}")
        return config_file
    
    def connect(self):
        """Execute full connection workflow"""
        print("=" * 60)
        print("🚀 ScholarixV2 Remote Server Connection")
        print("=" * 60)
        
        # Step 1: Test connection
        if not self.test_connection():
            print("\n❌ Cannot reach remote server. Check ODOO_URL in .env")
            return False
        
        # Step 2: Authenticate
        if not self.authenticate_remote():
            print("\n❌ Authentication failed. Check credentials in .env")
            return False
        
        # Step 3: Fetch modules
        modules = self.get_remote_modules()
        
        # Step 4: Sync modules
        if "commission_ax" in [m.get("name") for m in modules]:
            self.sync_commission_ax_module()
        
        # Step 5: Generate config
        config_file = self.generate_connection_config()
        
        print("\n" + "=" * 60)
        print("✅ Connection Setup Complete!")
        print("=" * 60)
        print(f"\nRemote Server: {self.remote_url}")
        print(f"Database: {self.remote_db}")
        print(f"Config File: {config_file}")
        print("\nNext steps:")
        print("1. Review generated config file")
        print("2. Deploy commission_ax module if needed")
        print("3. Sync database changes")
        
        return True


if __name__ == "__main__":
    connector = ScholarixV2RemoteConnector()
    success = connector.connect()
    sys.exit(0 if success else 1)
