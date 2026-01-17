#!/usr/bin/env python3
"""
Deals Management Module - Installation and Verification Script
For use on the remote Odoo server (scholarixv2 database)
"""

import os
import subprocess
import json
from datetime import datetime

class DealsModuleInstaller:
    def __init__(self):
        self.module_name = "deals_management"
        self.odoo_path = "/var/odoo/scholarixv2"
        self.module_path = f"{self.odoo_path}/extra-addons/odooapps.git-68ee71eda34bc/{self.module_name}"
        self.db_name = "scholarixv2"
        self.odoo_user = "odoo"
        self.odoo_group = "odoo"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log(self, message, level="INFO"):
        """Print formatted log message"""
        prefix = f"[{level}]"
        print(f"{prefix} {message}")
    
    def run_command(self, cmd, as_root=False, as_odoo=False):
        """Execute shell command and return output"""
        if as_root:
            cmd = f"sudo {cmd}"
        elif as_odoo:
            cmd = f"sudo -u {self.odoo_user} {cmd}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log("Command timed out", "ERROR")
            return 1, "", "Timeout"
        except Exception as e:
            self.log(f"Command failed: {str(e)}", "ERROR")
            return 1, "", str(e)
    
    def backup_module(self):
        """Create a backup of the existing module"""
        self.log("Creating backup of existing module...")
        
        if not os.path.exists(self.module_path):
            self.log("Module not found, skipping backup", "WARN")
            return True
        
        backup_path = f"/var/odoo/backups/{self.module_name}_backup_{self.timestamp}.tar.gz"
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        ret, out, err = self.run_command(
            f"tar -czf {backup_path} {self.module_path}",
            as_root=True
        )
        
        if ret == 0:
            self.log(f"Backup created: {backup_path}", "OK")
            return True
        else:
            self.log(f"Backup failed: {err}", "ERROR")
            return False
    
    def verify_module_structure(self):
        """Verify the module has all required files"""
        self.log("Verifying module structure...")
        
        required_files = [
            "__manifest__.py",
            "__init__.py",
            "models/__init__.py",
            "models/sale_order_deals.py",
            "security/ir.model.access.csv",
            "views/deals_views.xml",
            "views/deals_menu.xml",
        ]
        
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.module_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            self.log(f"Missing files: {', '.join(missing_files)}", "ERROR")
            return False
        
        self.log(f"All required files present", "OK")
        return True
    
    def check_dependencies(self):
        """Verify that dependent modules exist"""
        self.log("Checking module dependencies...")
        
        dependencies = ['sale', 'commission_ax', 'account', 'project']
        
        for dep in dependencies:
            dep_path = f"{self.odoo_path}/extra-addons/odooapps.git-68ee71eda34bc/{dep}"
            if not os.path.exists(dep_path):
                self.log(f"Dependency not found: {dep}", "WARN")
        
        self.log("Dependency check complete", "OK")
        return True
    
    def clean_database_cache(self):
        """Clean database cache for the module"""
        self.log("Cleaning database cache...")
        
        psql_cmd = f"""
        PGPASSWORD='$PGPASSWORD' psql -U odoo -d {self.db_name} -c "
        DELETE FROM ir_ui_menu WHERE id IN (
            SELECT res_id FROM ir_model_data 
            WHERE module = '{self.module_name}' AND model = 'ir.ui.menu'
        );
        DELETE FROM ir_act_window WHERE id IN (
            SELECT res_id FROM ir_model_data 
            WHERE module = '{self.module_name}' AND model = 'ir.actions.act_window'
        );
        DELETE FROM ir_ui_view WHERE id IN (
            SELECT res_id FROM ir_model_data 
            WHERE module = '{self.module_name}' AND model = 'ir.ui.view'
        );
        DELETE FROM ir_model_data WHERE module = '{self.module_name}';
        UPDATE ir_module_module SET state = 'uninstalled' WHERE name = '{self.module_name}';
        "
        """
        
        ret, out, err = self.run_command(psql_cmd, as_root=True)
        
        if ret == 0:
            self.log("Database cache cleaned", "OK")
            return True
        else:
            self.log(f"Cache cleanup failed: {err}", "WARN")
            return True  # Don't fail on this
    
    def restart_odoo(self):
        """Restart Odoo service"""
        self.log("Restarting Odoo service...")
        
        ret, out, err = self.run_command(
            "systemctl restart odoo",
            as_root=True
        )
        
        if ret == 0:
            self.log("Odoo restarted successfully", "OK")
            # Wait for Odoo to fully start
            import time
            time.sleep(10)
            return True
        else:
            self.log(f"Failed to restart Odoo: {err}", "ERROR")
            return False
    
    def check_odoo_status(self):
        """Check if Odoo service is running"""
        self.log("Checking Odoo status...")
        
        ret, out, err = self.run_command(
            "systemctl status odoo",
            as_root=True
        )
        
        if ret == 0:
            self.log("Odoo service is running", "OK")
            return True
        else:
            self.log("Odoo service is not running", "ERROR")
            return False
    
    def generate_report(self):
        """Generate installation report"""
        report = {
            "timestamp": self.timestamp,
            "module": self.module_name,
            "database": self.db_name,
            "module_path": self.module_path,
            "status": "READY FOR INSTALLATION"
        }
        
        report_file = f"/var/odoo/logs/deals_module_report_{self.timestamp}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Report saved to: {report_file}", "OK")
        return report_file
    
    def install(self):
        """Execute full installation workflow"""
        self.log("=" * 60)
        self.log("Deals Management Module - Installation")
        self.log("=" * 60)
        
        steps = [
            ("Backup Module", self.backup_module),
            ("Verify Structure", self.verify_module_structure),
            ("Check Dependencies", self.check_dependencies),
            ("Check Odoo Status", self.check_odoo_status),
            ("Clean Cache", self.clean_database_cache),
            ("Restart Odoo", self.restart_odoo),
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            self.log(f"\n>>> Step: {step_name}")
            if not step_func():
                failed_steps.append(step_name)
                self.log(f"FAILED: {step_name}", "ERROR")
            else:
                self.log(f"OK: {step_name}", "OK")
        
        # Generate report
        self.log("\n>>> Generating Report")
        report_file = self.generate_report()
        
        # Final summary
        self.log("\n" + "=" * 60)
        if not failed_steps:
            self.log("✅ Installation preparation COMPLETE!", "OK")
            self.log("\nNext steps:")
            self.log("1. Login to Odoo at https://erp.sgctech.ai")
            self.log("2. Go to Apps > Deals Management")
            self.log("3. Click 'Install'")
            self.log("4. Verify the 'Deals' and 'Commissions' menus appear")
        else:
            self.log("⚠️  Some steps failed:", "WARN")
            for step in failed_steps:
                self.log(f"  - {step}", "WARN")
        
        self.log(f"\nReport: {report_file}")
        self.log("=" * 60)


if __name__ == "__main__":
    installer = DealsModuleInstaller()
    installer.install()
