#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate module status report."""
import os
import json

# Create a comprehensive status report
report = {
    "module_name": "deal_report",
    "module_version": None,
    "files": {},
    "issues": []
}

# Check manifest
try:
    with open('__manifest__.py', 'r') as f:
        import re
        content = f.read()
        match = re.search(r"'version':\s*'([^']+)'", content)
        if match:
            report["module_version"] = match.group(1)
except:
    report["issues"].append("Could not read manifest")

# List all relevant files
for root, dirs, files in os.walk('.'):
    # Skip __pycache__ and other dirs
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    
    for f in sorted(files):
        if f.startswith('.'):
            continue
        
        filepath = os.path.join(root, f).lstrip('./')
        
        # Check file sizes
        size = os.path.getsize(os.path.join(root, f))
        
        if f.endswith(('.py', '.xml', '.csv')):
            report["files"][filepath] = {
                "size": size,
                "type": f.split('.')[-1]
            }

# Generate report
print(json.dumps(report, indent=2))
