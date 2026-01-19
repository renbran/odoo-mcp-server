# Odoo Configuration - Interactive Verbose Mode Setup

## Overview

Your Odoo instance has been configured with **two configuration modes**:

### 📋 Normal Mode (Production)
- Current configuration: `odoo.conf`
- Log level: DEBUG (for monitoring)
- Module updates: Run normally without verbose output
- Use for: Daily operations, events, production

### 🔧 Verbose Mode (Interactive Updates)
- Configuration file: `odoo-verbose.conf`
- Log handlers: DEBUG for modules, loading, and addons
- Module updates: Show every line of processing
- Use for: Development, troubleshooting, detailed monitoring

---

## Quick Start - Enable Verbose Mode

### Option 1: Interactive Menu (Recommended)

```bash
ssh root@139.84.163.11
cd /var/odoo/osusproperties
bash manage-odoo-config.sh
```

Then select option `1` to enable verbose mode.

### Option 2: Manual Commands

```bash
# Backup current config
cp /var/odoo/osusproperties/odoo.conf /var/odoo/osusproperties/odoo.conf.backup

# Switch to verbose config
cp /var/odoo/osusproperties/odoo-verbose.conf /var/odoo/osusproperties/odoo.conf

# Restart Odoo
systemctl restart odoo-osusproperties
```

---

## Using Verbose Mode - Line-by-Line Module Updates

### Setup (3 Steps)

#### Step 1: Enable Verbose Mode
```bash
ssh root@139.84.163.11
cd /var/odoo/osusproperties
bash manage-odoo-config.sh  # Choose option 1
```

#### Step 2: Watch Live Logs (Open NEW terminal)
```bash
ssh root@139.84.163.11
journalctl -u odoo-osusproperties -f
```

Keep this running - you'll see real-time output here.

#### Step 3: Trigger Module Update (In ORIGINAL terminal)

**Option A: From CLI (Recommended for testing)**
```bash
cd /var/odoo/osusproperties
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

**Option B: From Web Interface**
1. Open https://erposus.com/web/login
2. Go to Apps (top menu)
3. Search for "osus_sales_invoicing_dashboard"
4. Click "Upgrade" button

---

## What You'll See in Verbose Mode

Watch the journal terminal for output like:

```
2026-01-19 22:25:00,123 DEBUG odoo.modules.loading: Loading module osus_sales_invoicing_dashboard
2026-01-19 22:25:00,124 DEBUG odoo.modules: Initializing osus_sales_invoicing_dashboard
2026-01-19 22:25:00,125 DEBUG odoo.addons: Resolving dependencies
2026-01-19 22:25:00,200 INFO odoo.modules.loading: Modules to install ['osus_sales_invoicing_dashboard']
2026-01-19 22:25:00,300 DEBUG odoo.addons.base.ir_model: Computing fields for osus.sales.invoicing.dashboard
2026-01-19 22:25:00,400 DEBUG odoo.tools.xml: Loading XML file dashboard_views.xml
2026-01-19 22:25:00,500 DEBUG odoo.tools.xml: Processing record sales_invoicing_dashboard_view_form
2026-01-19 22:25:00,600 DEBUG odoo.tools.convert: Updating ir.ui.view with 1 changes
2026-01-19 22:25:00,700 DEBUG odoo.addons.ir_model: Applying field updates
2026-01-19 22:25:00,800 DEBUG odoo.addons.ir_rule: Creating security rules
2026-01-19 22:25:00,900 DEBUG odoo.addons.web: Compiling assets
2026-01-19 22:25:01,000 DEBUG odoo.addons.web: CSS files compiled: dashboard_modern.scss → dashboard_modern.css
2026-01-19 22:25:01,100 DEBUG odoo.addons.web: JavaScript bundles compiled
2026-01-19 22:25:01,200 INFO odoo.modules.loading: Module loaded successfully!
```

**This shows:**
- ✅ Each Python file being compiled
- ✅ Each XML file being loaded
- ✅ Database schema changes
- ✅ Security rules being applied
- ✅ Asset compilation (SCSS → CSS, JS bundling)
- ✅ Progress of each operation
- ✅ Any errors with full traceback

---

## Return to Normal Mode

```bash
ssh root@139.84.163.11
cd /var/odoo/osusproperties
bash manage-odoo-config.sh
```

Select option `2` to return to normal mode.

**Or manually:**
```bash
cp /var/odoo/osusproperties/odoo.conf.original /var/odoo/osusproperties/odoo.conf
systemctl restart odoo-osusproperties
```

---

## Configuration Files

### Location
```
/var/odoo/osusproperties/
├── odoo.conf              # Currently active config
├── odoo.conf.original     # Backup of original
├── odoo.conf.backup_*     # Timestamped backups
├── odoo-verbose.conf      # Verbose mode config
└── manage-odoo-config.sh  # Config manager script
```

### Key Differences

**Normal Mode (`odoo.conf.original`):**
```ini
log_level = debug
# (no log_handler specified - default behavior)
```

**Verbose Mode (`odoo-verbose.conf`):**
```ini
log_level = debug
log_handler = odoo.modules:DEBUG
log_handler = odoo.modules.loading:DEBUG
log_handler = odoo.addons:DEBUG
```

---

## Advanced Options

### Enable Even More Verbose Output

Edit `/var/odoo/osusproperties/odoo.conf` and uncomment:

```ini
# Optional: Uncomment for even more detailed output
log_handler = odoo.sql_db:DEBUG       # Shows SQL queries
log_handler = odoo.models:DEBUG       # Shows model operations
log_handler = odoo.tools:DEBUG        # Shows tool operations
```

Then restart:
```bash
systemctl restart odoo-osusproperties
```

### Log to File Instead

Add to `odoo.conf`:
```ini
logfile = /var/odoo/osusproperties/logs/module-update.log
```

Then view with:
```bash
tail -f /var/odoo/osusproperties/logs/module-update.log
```

---

## Troubleshooting

### Service Won't Start After Config Change

**Problem:** `systemctl status` shows "failed"

**Solution:**
```bash
# Check the error
tail -50 /var/odoo/osusproperties/logs/odoo-server.log

# Restore original config
cp /var/odoo/osusproperties/odoo.conf.original /var/odoo/osusproperties/odoo.conf

# Restart
systemctl restart odoo-osusproperties
```

### Not Seeing Verbose Output

**Problem:** No DEBUG lines in journal

**Solution:**
1. Confirm you're in verbose mode: `grep "log_handler" /var/odoo/osusproperties/odoo.conf`
2. Confirm service restarted: `systemctl status odoo-osusproperties | grep Active`
3. Check journal for errors: `journalctl -u odoo-osusproperties -n 50`

### Service Restart Takes Too Long

**Expected:** 30-60 seconds to start, depending on database size

**If longer:** Press Ctrl+C after 60 seconds and check logs

---

## Common Use Cases

### 1. Monitor CSS/SCSS Compilation

```bash
# Enable verbose mode
bash manage-odoo-config.sh  # Option 1

# Watch logs
journalctl -u odoo-osusproperties -f | grep -i "scss\|css\|asset"

# Trigger module update
cd /var/odoo/osusproperties
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

You'll see:
```
DEBUG odoo.addons.web: Compiling assets
DEBUG odoo.addons.web: Processing SCSS files
DEBUG odoo.addons.web: Bundling JavaScript
DEBUG odoo.addons.web: Asset compilation complete
```

### 2. Debug Database Schema Changes

```bash
# Enable verbose mode
bash manage-odoo-config.sh  # Option 1

# Watch for database changes
journalctl -u odoo-osusproperties -f | grep -i "field\|column\|constraint"

# Trigger update
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

### 3. Check Security Rule Application

```bash
# Watch for security rules
journalctl -u odoo-osusproperties -f | grep -i "rule\|security"

# Trigger update
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

---

## Summary

| Task | Command |
|------|---------|
| Enable verbose mode | `bash manage-odoo-config.sh` → Select 1 |
| View current config | `bash manage-odoo-config.sh` → Select 3 |
| Return to normal | `bash manage-odoo-config.sh` → Select 2 |
| Watch live logs | `journalctl -u odoo-osusproperties -f` |
| Update module (CLI) | `./venv/bin/python3 src/odoo-bin -u MODULE -d DB -c odoo.conf` |
| Update module (Web) | Go to Apps → Search → Upgrade |
| Check logs | `tail -100 /var/odoo/osusproperties/logs/odoo-server.log` |
| Emergency restore | `cp odoo.conf.original odoo.conf && systemctl restart odoo-osusproperties` |

---

## Files Provided

1. **odoo-verbose.conf** - Verbose configuration file
2. **manage-odoo-config.sh** - Interactive config manager
3. **This guide** - Complete documentation

All files are located in `/var/odoo/osusproperties/`

---

## Next Steps

1. **Test verbose mode:** `bash manage-odoo-config.sh` → Option 1
2. **Monitor logs:** Open new terminal and run `journalctl -u odoo-osusproperties -f`
3. **Update module:** Run the CLI command or use web interface
4. **Return to normal:** `bash manage-odoo-config.sh` → Option 2

Enjoy detailed line-by-line visibility into your module updates! 🎉
