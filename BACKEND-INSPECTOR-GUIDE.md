# Backend Module Inspector Guide

## Quick Start

You now have direct backend access to the Odoo instance running at `/var/odoo/scholarixv2`.

### Python Inspector Tool

Located at: `d:\01_WORK_PROJECTS\odoo-mcp-server\inspect-backend.py`

This tool connects directly to the Odoo commission_ax database for module inspection and installation.

## Commands

### List all modules
```bash
python3 inspect-backend.py list
```

### List modules by state
```bash
python3 inspect-backend.py list installed      # Only installed modules
python3 inspect-backend.py list uninstalled    # Only uninstalled modules
```

### Get module information
```bash
python3 inspect-backend.py info account
python3 inspect-backend.py info sale
```

### Install a module
```bash
python3 inspect-backend.py install account_reports
python3 inspect-backend.py install sale_management
```

## Server Paths

- **Source Code**: `/var/odoo/scholarixv2/src`
- **Log Files**: `/var/odoo/scholarixv2/logs`
- **Config File**: `/var/odoo/scholarixv2/odoo.conf`
- **Python Interpreter**: `/var/odoo/scholarixv2/venv/bin/python3`
- **Odoo Binary**: `/var/odoo/scholarixv2/src/odoo-bin`

## Direct Odoo Shell Access

You can also access the Odoo shell directly:

```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d commission_ax --no-http
```

## Update All Modules

To update all installed modules:

```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d commission_ax --no-http --stop-after-init --update all
```

## Use Cases

1. **Discover Available Modules**
   ```bash
   python3 inspect-backend.py list uninstalled
   ```

2. **Check Module Dependencies**
   ```bash
   python3 inspect-backend.py info sale_commission
   ```

3. **Safe Installation Workflow**
   - First, list uninstalled modules
   - Check each module's info to understand dependencies
   - Install in dependency order
   - Verify installation with logs

4. **Troubleshoot Issues**
   - Check logs: `/var/odoo/scholarixv2/logs`
   - Use the inspector to verify module states
   - Check dependencies for conflicts

## Safety Notes

- The Python inspector uses Odoo's built-in methods for module installation
- All operations run as the `odoo` user (proper permissions)
- The commission_ax database is the default database
- Always check module dependencies before installation
- Keep backups of important data
