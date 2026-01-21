# Fix Odoo CSS Compilation Issues

## The session error you're seeing is not related to this MCP server project.

This error occurs on your Odoo instance at `/var/odoo/osusproperties/`

## To Fix CSS Compilation on Your Odoo Server:

### Option 1: Regenerate Assets via CLI
```bash
# SSH into your Odoo server
cd /var/odoo/osusproperties

# Regenerate all assets
./odoo-bin -c odoo.conf -d YOUR_DATABASE_NAME --stop-after-init --update=all

# Or regenerate web assets only
./odoo-bin -c odoo.conf -d YOUR_DATABASE_NAME --stop-after-init -u web
```

### Option 2: Via Odoo UI (Debug Mode)
1. Enable Developer Mode: Settings → Activate Developer Mode
2. Go to: Settings → Technical → User Interface → Views
3. Search for and delete all `ir.ui.view` records with "assets" in the name
4. Restart Odoo server
5. Clear browser cache

### Option 3: Clear Assets Directory
```bash
# SSH into your Odoo server
cd /var/odoo/osusproperties

# Remove compiled assets
rm -rf ~/.local/share/Odoo/filestore/YOUR_DATABASE_NAME/assets/*

# Restart Odoo
sudo systemctl restart odoo
# or
supervisorctl restart odoo
```

### Option 4: Fix Session Storage (if needed)
```bash
# Create missing session directories
mkdir -p /var/odoo/.local/share/Odoo/sessions/da

# Set proper permissions
chown -R odoo:odoo /var/odoo/.local/share/Odoo/
chmod -R 755 /var/odoo/.local/share/Odoo/
```

## Quick Fix Command:
```bash
# Run this on your Odoo server
cd /var/odoo/osusproperties && \
./odoo-bin -c odoo.conf -d YOUR_DATABASE_NAME --stop-after-init -u web && \
sudo systemctl restart odoo
```

## Note:
This MCP server project is a **client** that connects to Odoo via XML-RPC. It doesn't handle CSS compilation or sessions - those are managed by your Odoo server instance.
