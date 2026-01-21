# ✅ Odoo Configuration - Setup Complete

## 🎯 What Was Done

Your Odoo instance (`osusproperties`) has been configured with **interactive verbose mode** for line-by-line module update monitoring.

### Files Created on Remote Server

```
/var/odoo/osusproperties/
├── manage-odoo-config.sh      ← Interactive config manager (7.1 KB)
├── odoo-verbose.conf          ← Verbose configuration (5.8 KB)
├── odoo.conf                  ← Current active config (3.0 KB)
├── odoo.conf.backup           ← Original backup (3.0 KB)
└── odoo.conf.original         ← Created by manager script
```

### Files on Your Local Desktop

```
d:\01_WORK_PROJECTS\odoo-mcp-server\
├── manage-odoo-config.sh           ← Interactive menu tool
├── odoo-verbose.conf               ← Verbose config template
├── ODOO_VERBOSE_MODE_GUIDE.md      ← Complete documentation
└── (this summary file)
```

---

## 🚀 Quick Start (30 seconds)

### Enable Verbose Mode

```bash
ssh root@139.84.163.11
cd /var/odoo/osusproperties
bash manage-odoo-config.sh
# Press 1, then Enter
```

### Watch Live Logs

Open a **NEW terminal window** and run:

```bash
ssh root@139.84.163.11
journalctl -u odoo-osusproperties -f
```

### Trigger Module Update

In your original terminal:

```bash
cd /var/odoo/osusproperties
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

**Or** from web: https://erposus.com → Apps → Search "osus_sales_invoicing_dashboard" → Upgrade

---

## 📊 What You'll See

Real-time output showing each step:

```
DEBUG odoo.modules.loading: Loading module osus_sales_invoicing_dashboard
DEBUG odoo.modules: Initializing osus_sales_invoicing_dashboard
DEBUG odoo.addons: Resolving dependencies
DEBUG odoo.tools.xml: Loading XML file dashboard_views.xml
DEBUG odoo.addons.web: Compiling assets
DEBUG odoo.addons.web: CSS files compiled: dashboard_modern.scss
DEBUG odoo.addons.web: JavaScript bundles compiled
INFO odoo.modules.loading: Module loaded successfully!
```

**Visible for:**
- ✅ Each file being processed
- ✅ Database schema changes
- ✅ Security rules being applied
- ✅ Asset compilation (SCSS, CSS, JS)
- ✅ Any errors with full traceback

---

## 🎛️ Management Commands

### Interactive Menu
```bash
bash manage-odoo-config.sh
```

**Options:**
1. Enable VERBOSE mode (for module updates)
2. Enable NORMAL mode (production)
3. View current configuration
4. View verbose log example
5. Show how to monitor updates
6. Exit

### Quick Manual Commands

**Enable verbose:**
```bash
cp /var/odoo/osusproperties/odoo-verbose.conf /var/odoo/osusproperties/odoo.conf
systemctl restart odoo-osusproperties
```

**Return to normal:**
```bash
cp /var/odoo/osusproperties/odoo.conf.backup /var/odoo/osusproperties/odoo.conf
systemctl restart odoo-osusproperties
```

**Check current mode:**
```bash
grep "log_handler" /var/odoo/osusproperties/odoo.conf | head -3
```

**View logs in real-time:**
```bash
journalctl -u odoo-osusproperties -f
```

---

## 📚 Two Configuration Modes

### Normal Mode (Default)
- **Use for:** Daily operations, events, production
- **File:** `odoo.conf.original` or `odoo.conf.backup`
- **Output:** Standard logging only
- **Performance:** Normal

### Verbose Mode
- **Use for:** Development, troubleshooting, module updates
- **File:** `odoo-verbose.conf`
- **Output:** Shows every DEBUG step from module system
- **Performance:** Slightly more logging overhead

---

## 🔧 Configuration Settings

### What Makes It Verbose

In `odoo-verbose.conf`:

```ini
log_level = debug

log_handler = odoo.modules:DEBUG
log_handler = odoo.modules.loading:DEBUG
log_handler = odoo.addons:DEBUG
```

These log handlers tell Odoo to show DEBUG messages from:
- `odoo.modules` - Module loading system
- `odoo.modules.loading` - Detailed module loading steps
- `odoo.addons` - Addon management

### Optional Advanced Settings

Uncomment in `odoo-verbose.conf` for even more detail:

```ini
log_handler = odoo.sql_db:DEBUG       # SQL queries
log_handler = odoo.models:DEBUG       # Model operations
log_handler = odoo.tools:DEBUG        # Tool operations
```

---

## 📝 Current Status

### Service Status
```
✅ Odoo Service: ACTIVE (running)
✅ Configuration: odoo.conf (NORMAL mode)
✅ Verbose Files: Ready (odoo-verbose.conf)
✅ Manager Script: Ready (manage-odoo-config.sh)
```

### Available Configurations
```
- odoo.conf.original (original backup)
- odoo.conf.backup (additional backup)
- odoo-verbose.conf (verbose template)
- odoo.conf (currently active - NORMAL mode)
```

### How to Verify
```bash
ssh root@139.84.163.11
ls -lah /var/odoo/osusproperties/odoo*.conf
grep "log_level" /var/odoo/osusproperties/odoo.conf
systemctl status odoo-osusproperties | grep Active
```

---

## 💡 Common Use Cases

### Monitor CSS/SCSS Compilation During Module Update
```bash
# Terminal 1: Watch for SCSS/CSS messages
journalctl -u odoo-osusproperties -f | grep -i "scss\|css"

# Terminal 2: Trigger update
cd /var/odoo/osusproperties
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

### Debug Database Schema Changes
```bash
# Terminal 1: Watch for field/column changes
journalctl -u odoo-osusproperties -f | grep -i "field\|column"

# Terminal 2: Trigger update
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

### Track Security Rule Updates
```bash
# Terminal 1: Watch for security rules
journalctl -u odoo-osusproperties -f | grep -i "rule\|security"

# Terminal 2: Trigger update
./venv/bin/python3 src/odoo-bin -u osus_sales_invoicing_dashboard -d osusproperties -c odoo.conf
```

---

## 🚨 Emergency Recovery

If something goes wrong:

```bash
# Restore original config
cp /var/odoo/osusproperties/odoo.conf.backup /var/odoo/osusproperties/odoo.conf

# Restart service
systemctl restart odoo-osusproperties

# Verify it's running
systemctl is-active odoo-osusproperties
```

---

## 📞 Next Steps

1. **Test the system:**
   ```bash
   bash manage-odoo-config.sh  # Try the interactive menu
   ```

2. **Read the full guide:**
   - Local: `d:\01_WORK_PROJECTS\odoo-mcp-server\ODOO_VERBOSE_MODE_GUIDE.md`
   - Or read it online after cloning

3. **Use for next module update:**
   - Enable verbose mode
   - Open new terminal with `journalctl -f`
   - Trigger module update
   - Watch line-by-line progress

4. **Return to normal mode:**
   ```bash
   bash manage-odoo-config.sh  # Choose option 2
   ```

---

## 📋 Files Reference

### Remote Server Files
```
Location: /var/odoo/osusproperties/

manage-odoo-config.sh (7.1 KB)
  ├─ Interactive menu for switching modes
  ├─ Color-coded output
  └─ Safe backup/restore

odoo-verbose.conf (5.8 KB)
  ├─ Verbose logging configuration
  ├─ DEBUG handlers for modules
  └─ Full documentation in comments

odoo.conf (currently active)
  ├─ Currently active configuration
  └─ Can be switched by manage-odoo-config.sh

odoo.conf.backup & odoo.conf.original
  └─ Backups for recovery
```

### Local Desktop Files
```
Location: d:\01_WORK_PROJECTS\odoo-mcp-server\

manage-odoo-config.sh
  └─ Upload to server if needed

odoo-verbose.conf
  └─ Reference/backup copy

ODOO_VERBOSE_MODE_GUIDE.md
  └─ Complete documentation

CSS_FIX_GUIDE.md
  └─ SCSS variable fix documentation
```

---

## ✨ Summary

Your Odoo instance is now set up for **interactive verbose module updates** with:

- ✅ Two-mode configuration (normal/verbose)
- ✅ One-command switching (`bash manage-odoo-config.sh`)
- ✅ Real-time log monitoring (`journalctl -f`)
- ✅ Line-by-line operation visibility
- ✅ Easy backup/restore
- ✅ Safe emergency recovery

**Ready to use immediately!** 🎉

---

**Version:** 1.0  
**Date:** January 20, 2026  
**Server:** 139.84.163.11  
**Database:** osusproperties  
**Module:** osus_sales_invoicing_dashboard
