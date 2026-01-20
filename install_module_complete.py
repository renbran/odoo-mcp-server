#!/usr/bin/env python3
"""
Complete Module Installation via SSH with Progress Monitoring
Uses correct Odoo 17 installation commands and monitors logs
"""

import subprocess
import os
import time
from pathlib import Path

SSH_KEY_PATH = Path(os.path.expanduser("~/.ssh/id_rsa"))
CLOUDPEPPER_HOST = "139.84.163.11"
CLOUDPEPPER_USER = "root"
CLOUDPEPPER_PORT = "22"

# Server configuration
ODOO_HOME = "/var/odoo/osusproperties"
ODOO_BIN = f"{ODOO_HOME}/src/odoo-bin"
CONFIG = f"{ODOO_HOME}/odoo.conf"
PYTHON = f"{ODOO_HOME}/venv/bin/python3"
DB = "osusproperties"
MODULE = "invoice_status_tags"
LOG_FILE = f"{ODOO_HOME}/logs/odoo.log"

def ssh_command(cmd, show_output=True):
    """Execute SSH command and return result"""
    ssh_cmd = f'ssh -i "{SSH_KEY_PATH}" -p {CLOUDPEPPER_PORT} {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST} "{cmd}"'
    
    if show_output:
        print(f"\n>>> {cmd}\n")
        result = subprocess.run(ssh_cmd, shell=True)
        return result.returncode == 0
    else:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr

def log_step(step_num, title):
    """Print formatted step header"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*80}")

def monitor_logs(duration=20):
    """Monitor Odoo logs during installation"""
    print(f"\nMonitoring logs for {duration} seconds...")
    print("(Waiting for installation to complete)\n")
    
    # Get current log size
    cmd = f"wc -l {LOG_FILE} 2>/dev/null || echo 0"
    _, start_lines, _ = ssh_command(cmd, show_output=False)
    
    try:
        start_count = int(start_lines.split()[0])
    except:
        start_count = 0
    
    elapsed = 0
    while elapsed < duration:
        time.sleep(2)
        elapsed += 2
        
        # Check if Odoo is responsive
        check_cmd = f"systemctl is-active odoo 2>/dev/null || echo 'unknown'"
        _, status, _ = ssh_command(check_cmd, show_output=False)
        status = status.strip()
        
        # Show progress
        remaining = duration - elapsed
        bar_length = 40
        filled = int(bar_length * (elapsed / duration))
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\r[{bar}] {elapsed}s/{duration}s | Odoo: {status:10s}", end="", flush=True)
    
    print("\n\nInstallation monitoring complete!")
    
    # Show last few log lines
    print("\nRecent log entries:")
    print("─" * 80)
    cmd = f"tail -20 {LOG_FILE}"
    ssh_command(cmd, show_output=True)

def main():
    print("\n" + "="*80)
    print("ODOO MODULE INSTALLATION - COMPLETE SETUP")
    print("Invoice Status Tags - invoice_status_tags")
    print("="*80)
    
    print(f"\nConfiguration:")
    print(f"  Server: {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST}")
    print(f"  Odoo Home: {ODOO_HOME}")
    print(f"  Database: {DB}")
    print(f"  Module: {MODULE}")
    print(f"  SSH Key: {SSH_KEY_PATH}")
    
    # Step 1: Pre-installation checks
    log_step(1, "PRE-INSTALLATION CHECKS")
    
    print("\nVerifying module folder exists...")
    cmd = f"ls -la {ODOO_HOME}/extra-addons/odoo17_final.git-6880b7fcd4844/invoice_status_tags/__manifest__.py"
    if not ssh_command(cmd, show_output=True):
        print("\n[FATAL] Module folder not found!")
        return False
    
    # Step 2: Stop Odoo
    log_step(2, "STOPPING ODOO SERVICE")
    
    print("\nStopping Odoo service...")
    cmd = "sudo systemctl stop odoo"
    ssh_command(cmd, show_output=True)
    
    print("\nWaiting 5 seconds for clean shutdown...")
    time.sleep(5)
    
    # Step 3: Clear Odoo session cache
    log_step(3, "CLEARING SESSION CACHE")
    
    print("\nRemoving session cache...")
    cmd = f"sudo -u odoo rm -rf {ODOO_HOME}/sessions/* 2>/dev/null || true"
    ssh_command(cmd, show_output=True)
    
    # Step 4: Start Odoo with fresh module list
    log_step(4, "STARTING ODOO WITH FRESH MODULE DETECTION")
    
    print("\nStarting Odoo service...")
    cmd = "sudo systemctl start odoo"
    ssh_command(cmd, show_output=True)
    
    print("\nWaiting 10 seconds for Odoo to initialize...")
    time.sleep(10)
    
    # Step 5: Install module via Odoo CLI
    log_step(5, "INSTALLING MODULE VIA ODOO CLI")
    
    print(f"\nExecuting installation command...")
    print(f"Command: {PYTHON} {ODOO_BIN} -c {CONFIG} -i {MODULE} -d {DB} --no-http --stop-after-init")
    
    # Execute installation command
    cmd = f"cd {ODOO_HOME} && sudo -u odoo {PYTHON} {ODOO_BIN} -c {CONFIG} -i {MODULE} -d {DB} --no-http --stop-after-init"
    ssh_command(cmd, show_output=True)
    
    # Step 6: Restart Odoo
    log_step(6, "RESTARTING ODOO SERVICE")
    
    print("\nRestarting Odoo service...")
    cmd = "sudo systemctl restart odoo"
    ssh_command(cmd, show_output=True)
    
    print("\nWaiting 5 seconds after restart...")
    time.sleep(5)
    
    # Step 7: Monitor installation
    log_step(7, "MONITORING INSTALLATION PROGRESS")
    monitor_logs(duration=30)
    
    # Step 8: Verify installation
    log_step(8, "VERIFYING MODULE INSTALLATION")
    
    print("\nChecking if module is installed...")
    cmd = f"grep -i 'invoice_status_tags' {LOG_FILE} | tail -5"
    ssh_command(cmd, show_output=True)
    
    # Step 9: Check service status
    log_step(9, "CHECKING ODOO SERVICE STATUS")
    
    cmd = "sudo systemctl status odoo --no-pager | head -20"
    ssh_command(cmd, show_output=True)
    
    # Final summary
    print("\n" + "="*80)
    print("INSTALLATION COMPLETE")
    print("="*80)
    
    print("\nNext steps:")
    print("  1. Access Odoo: https://erposus.com")
    print("  2. Login with your credentials")
    print("  3. Go to Settings > Apps > Apps")
    print("  4. Search for 'Invoice Status Tags'")
    print("  5. Verify the module shows as 'Installed'")
    print("  6. Go to Sales > Orders to see new features")
    
    print("\nModule features now available:")
    print("  - Invoice Type Tag badges")
    print("  - Invoicing percentage progress")
    print("  - Draft invoice warnings")
    print("  - Smart filters for invoice status")
    print("  - Visual indicators (ribbons, progress bars)")
    
    print("\nIf there are issues:")
    print("  - Check logs: tail -100 /var/odoo/osusproperties/logs/odoo.log")
    print("  - Restart Odoo: sudo systemctl restart odoo")
    print("  - Force reinstall: python3 odoo-bin -i invoice_status_tags --new")
    
    print("\n" + "="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
