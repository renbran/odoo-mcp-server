#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to simulate Odoo module loading.
This tries to parse all data files as if Odoo is loading them.
"""
import os
import sys
from xml.etree import ElementTree as ET

def test_module_loading():
    """Test if module can be loaded by Odoo."""
    
    # Change to module directory
    os.chdir(os.path.dirname(__file__))
    
    # Read manifest
    with open('__manifest__.py', 'r') as f:
        content = f.read()
    
    # Parse manifest to get data files
    import re
    data_match = re.search(r"'data':\s*\[(.*?)\]", content, re.DOTALL)
    
    if not data_match:
        print("ERROR: Could not find 'data' list in manifest")
        return False
    
    data_files = re.findall(r"'([^']+)'", data_match.group(1))
    print(f"Found {len(data_files)} data files")
    
    # Try to parse each XML file
    print("\n=== XML FILE VALIDATION ===\n")
    xml_files = [f for f in data_files if f.endswith('.xml')]
    
    all_valid = True
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            if root.tag != 'odoo':
                print(f"ERROR: {xml_file} - Root tag is '{root.tag}', expected 'odoo'")
                all_valid = False
                continue
            
            # Check for multiple data elements
            data_elements = root.findall('data')
            if len(data_elements) != 1:
                print(f"ERROR: {xml_file} - Found {len(data_elements)} <data> elements, expected 1")
                all_valid = False
                continue
            
            # Check for content between data and odoo closing tags
            for i, child in enumerate(root):
                if child.tag != 'data':
                    print(f"ERROR: {xml_file} - Found unexpected element '{child.tag}' as child of <odoo> at position {i}")
                    all_valid = False
            
            print(f"OK: {xml_file}")
        
        except ET.ParseError as e:
            print(f"ERROR: {xml_file} - XML Parse Error: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"ERROR: {xml_file} - File not found")
            all_valid = False
        except Exception as e:
            print(f"ERROR: {xml_file} - Unexpected error: {e}")
            all_valid = False
    
    # Check CSV files  
    print("\n=== CSV FILE VALIDATION ===\n")
    csv_files = [f for f in data_files if f.endswith('.csv')]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            with open(csv_file, 'r') as f:
                lines = f.readlines()
            print(f"OK: {csv_file} ({len(lines)-1} records)")
        else:
            print(f"ERROR: {csv_file} - File not found")
            all_valid = False
    
    print("\n" + "="*50)
    if all_valid:
        print("SUCCESS: All module data files are valid!")
        return True
    else:
        print("FAILURE: Some files have errors")
        return False

if __name__ == '__main__':
    success = test_module_loading()
    sys.exit(0 if success else 1)
