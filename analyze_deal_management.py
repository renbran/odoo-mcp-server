#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze deal_management module from remote Odoo instance.
This tool fetches module details, models, and views to identify
what best practices from deal_report should be applied.
"""

import xmlrpc.client
import json
import sys
import base64
from datetime import datetime
from pathlib import Path


class DealManagementAnalyzer:
    """Analyzes deal_management module structure and best practices."""

    def __init__(self, url, db, username, password):
        """Initialize connection to Odoo."""
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.common = None
        self.object = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Odoo server."""
        try:
            self.common = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/common"
            )
            self.object = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/object"
            )

            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
            if self.uid:
                print(f"✅ Authenticated as UID {self.uid}\n")
            else:
                raise Exception("Authentication failed")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            sys.exit(1)

    def check_module_installed(self):
        """Check if deal_management is installed."""
        try:
            domains = [
                ["name", "=", "deal_management"],
                ["state", "=", "installed"],
            ]
            modules = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.module.module",
                "search_read",
                [domains],
                {"fields": ["name", "state", "version"]},
            )
            if modules:
                print("✅ deal_management Module Status:")
                for mod in modules:
                    print(f"   Name: {mod['name']}")
                    print(f"   State: {mod['state']}")
                    print(f"   Version: {mod['version']}")
                return True
            else:
                print("❌ deal_management module not installed")
                return False
        except Exception as e:
            print(f"⚠️ Error checking module: {e}")
            return False

    def get_models(self):
        """Get all models defined by deal_management."""
        try:
            print("\n📊 Models in deal_management:")
            domains = [["module", "=", "deal_management"]]
            models = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.model",
                "search_read",
                [domains],
                {"fields": ["model", "name", "trans_name"]},
            )
            if models:
                for model in models:
                    print(f"   - {model['model']}: {model['name']}")
                return models
            else:
                print("   ℹ️  No models found")
                return []
        except Exception as e:
            print(f"⚠️ Error getting models: {e}")
            return []

    def analyze_model_structure(self, model_name):
        """Analyze fields in a model."""
        try:
            fields = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                model_name,
                "fields_get",
                [],
                {"attributes": ["string", "type", "required", "readonly"]},
            )
            return fields
        except Exception as e:
            print(f"⚠️ Error analyzing {model_name}: {e}")
            return {}

    def get_views(self):
        """Get all views for deal_management models."""
        try:
            print("\n🎨 Views in deal_management:")
            domains = [["model", "like", "deal"]]
            views = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.ui.view",
                "search_read",
                [domains],
                {"fields": ["name", "model", "type", "priority"]},
            )
            if views:
                for view in views:
                    print(
                        f"   - {view['name']} ({view['type']}) "
                        f"for {view['model']}"
                    )
                return views
            else:
                print("   ℹ️  No views found")
                return []
        except Exception as e:
            print(f"⚠️ Error getting views: {e}")
            return []

    def get_security_groups(self):
        """Get security groups for deal_management."""
        try:
            print("\n🔐 Security Groups:")
            domains = [["name", "ilike", "deal"]]
            groups = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                "res.groups",
                "search_read",
                [domains],
                {"fields": ["name", "category_id"]},
            )
            if groups:
                for group in groups:
                    print(f"   - {group['name']}")
                return groups
            else:
                print("   ℹ️  No deal-related groups found")
                return []
        except Exception as e:
            print(f"⚠️ Error getting security groups: {e}")
            return []

    def get_access_rules(self):
        """Get record rules for deal_management models."""
        try:
            print("\n📋 Access Rules (Record Rules):")
            domains = [["model_id.model", "like", "deal"]]
            rules = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.rule",
                "search_read",
                [domains],
                {"fields": ["name", "model_id", "domain_force", "groups"]},
            )
            if rules:
                for rule in rules:
                    print(
                        f"   - {rule['name']}: "
                        f"{rule['model_id'][1]} "
                        f"({len(rule['groups'])} groups)"
                    )
                return rules
            else:
                print("   ℹ️  No access rules found")
                return []
        except Exception as e:
            print(f"⚠️ Error getting access rules: {e}")
            return []

    def analyze_dependencies(self):
        """Check module dependencies."""
        try:
            print("\n📦 Dependencies:")
            domains = [["name", "=", "deal_management"]]
            modules = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.module.module",
                "search_read",
                [domains],
                {"fields": ["depends_id"]},
            )
            if modules and modules[0].get("depends_id"):
                deps = modules[0]["depends_id"]
                for dep in deps:
                    print(f"   - {dep[1]}")
                return deps
            else:
                print("   ℹ️  No dependencies found or module not installed")
                return []
        except Exception as e:
            print(f"⚠️ Error getting dependencies: {e}")
            return []

    def get_workflows(self):
        """Get state machine workflows if defined."""
        try:
            print("\n⚙️ Workflows/States:")
            # Check for workflow in deal_management models
            domains = [["module", "=", "deal_management"]]
            models = self.object.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.model",
                "search_read",
                [domains],
                {"fields": ["model"]},
            )

            for model in models:
                model_name = model["model"]
                try:
                    fields = self.object.execute_kw(
                        self.db,
                        self.uid,
                        self.password,
                        model_name,
                        "fields_get",
                        [],
                        {"attributes": ["type"]},
                    )
                    # Look for state field
                    if "state" in fields and fields["state"]["type"] == "selection":
                        print(f"   - {model_name} has 'state' field (workflow)")
                except:
                    pass
        except Exception as e:
            print(f"⚠️ Error getting workflows: {e}")

    def generate_report(self):
        """Generate comprehensive analysis report."""
        print("=" * 70)
        print("DEAL_MANAGEMENT MODULE ANALYSIS".center(70))
        print("=" * 70)
        print(f"\nTarget: {self.url}")
        print(f"Database: {self.db}\n")

        # Run analyses
        self.check_module_installed()
        self.analyze_dependencies()
        models = self.get_models()
        self.get_views()
        self.get_security_groups()
        self.get_access_rules()
        self.get_workflows()

        # Detailed model analysis
        if models:
            print("\n" + "=" * 70)
            print("DETAILED MODEL STRUCTURE".center(70))
            print("=" * 70)
            for model in models:
                model_name = model["model"]
                print(f"\n📌 {model_name}")
                print("-" * 70)
                fields = self.analyze_model_structure(model_name)
                if fields:
                    print(f"   Fields ({len(fields)}):")
                    for field_name, field_info in sorted(fields.items())[:15]:
                        field_type = field_info.get("type", "?")
                        required = (
                            "⚠️  REQUIRED"
                            if field_info.get("required")
                            else ""
                        )
                        print(f"      - {field_name}: {field_type} {required}")
                    if len(fields) > 15:
                        print(f"      ... and {len(fields) - 15} more fields")

        self._save_report(models)

    def _save_report(self, models):
        """Save analysis report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = (
            f"deal_management_analysis_{timestamp}.json"
        )

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "url": self.url,
            "database": self.db,
            "models_count": len(models),
            "models": [
                {
                    "name": m["model"],
                    "description": m.get("name", ""),
                }
                for m in models
            ],
        }

        try:
            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"\n✅ Report saved to {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze deal_management module from Odoo instance"
    )
    parser.add_argument(
        "--url",
        default="https://erp.sgctech.ai",
        help="Odoo instance URL",
    )
    parser.add_argument(
        "--db", default="scholarixv2", help="Database name"
    )
    parser.add_argument(
        "--email",
        default="info@scholarixglobal.com",
        help="Login email",
    )
    parser.add_argument(
        "--password", default="123456", help="Login password"
    )

    args = parser.parse_args()

    analyzer = DealManagementAnalyzer(
        args.url, args.db, args.email, args.password
    )
    analyzer.generate_report()

    # Print recommendations
    print("\n" + "=" * 70)
    print("BEST PRACTICES FROM DEAL_REPORT".center(70))
    print("=" * 70)
    print("""
✅ RECOMMENDED ENHANCEMENTS FROM deal_report:

1. 📋 MANIFEST STRUCTURE
   - Add proper description, category, and icon
   - Include all data files in correct order
   - Define SCSS assets for UI styling
   - Set 'application': True for main module

2. 🗂️  MODULE ORGANIZATION
   - Separate models into individual files
   - Create dedicated views/security/data folders
   - Use consistent naming: <model>_views.xml, <model>_security.xml
   - Add tests/ folder with test cases

3. 🔒 SECURITY IMPLEMENTATION
   - Define res.groups with proper categories
   - Create ir.rule for record-level access control
   - Set field-level access via ir.model.access.csv
   - Implement domain-based filtering

4. 📊 MODEL DESIGN PATTERNS
   - Inherit mail.thread for change tracking
   - Use _order for default sorting
   - Implement _sql_constraints for data integrity
   - Add tracking=True on important fields
   - Use _compute and store for calculated fields

5. 👁️ VIEW BEST PRACTICES
   - Create form, tree, search, and pivot views
   - Use proper view types (form, tree, kanban, pivot)
   - Implement statusbar for state visualization
   - Add search filters and grouped views
   - Set view priority correctly (lower = higher priority)

6. 📱 USER INTERFACE
   - Add smart buttons for related records
   - Implement color coding for states
   - Create dashboards with KPIs
   - Use mail.activity.mixin for task management

7. 🔄 WORKFLOW & AUTOMATION
   - Define clear state transitions
   - Implement button actions for state changes
   - Add server actions for automated workflows
   - Use @api.depends for field computations

8. 📝 DATA MANAGEMENT
   - Create demo data XML files
   - Define sequences for reference numbers
   - Add default values with functions
   - Implement copy=False on critical fields

9. 🧪 TESTING & VALIDATION
   - Create comprehensive test suites
   - Add unit tests for computations
   - Implement integration tests
   - Test security rules thoroughly

10. 📖 DOCUMENTATION
    - Add README.md with features list
    - Document workflows and processes
    - Create installation guides
    - Add field descriptions with help text
    """)


if __name__ == "__main__":
    main()
