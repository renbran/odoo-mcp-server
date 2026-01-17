# Quick Inline Fix - Copy & Paste These Commands into SSH

## Issue
The module directory extraction isn't fully replacing the old file. Line 67 still has the bad menu reference.

## Solution: Use sed to delete the bad line

```bash
# SSH into your server, then run:

MODULE_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management"
MENU_FILE="$MODULE_PATH/views/deals_menu.xml"

# Check current state - what's on line 67?
echo "=== Current line 67 ==="
sed -n '67p' "$MENU_FILE"
echo ""

# Check total lines
echo "=== Line count ==="
wc -l "$MENU_FILE"
echo ""

# OPTION A: If line 67 shows the BAD menu (menu_deals_projects), delete it
if grep -q "menu_deals_projects" "$MENU_FILE"; then
    echo "Found bad reference! Deleting..."
    sudo sed -i '/menu_deals_projects/d' "$MENU_FILE"
    echo "✓ Bad line deleted"
    echo ""
    echo "=== New line count ==="
    wc -l "$MENU_FILE"
    echo ""
    echo "=== New line 67 ==="
    sed -n '67p' "$MENU_FILE"
fi

# Verify no bad references
echo ""
echo "=== Checking for remaining bad references ==="
if grep "menu_deals_projects\|action_deals_projects" "$MENU_FILE"; then
    echo "ERROR: Bad references still present!"
else
    echo "✓ CLEAN - No bad references"
fi
```

## If Above Doesn't Work - Nuclear Option

Run this to completely delete and rebuild:

```bash
# Complete cleanup and rebuild
sudo rm -rf /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management

cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/

sudo unzip -o /tmp/deals_management.zip -d deals_management

sudo chown -R odoo:odoo deals_management

sudo chmod -R 755 deals_management

# Verify
wc -l deals_management/views/deals_menu.xml

grep "menu_deals_projects" deals_management/views/deals_menu.xml || echo "✓ CLEAN"

# Clean database
sudo -u postgres psql scholarixv2 -c "DELETE FROM ir_model_data WHERE module = 'deals_management';"

# Restart
sudo systemctl restart odoo
```

---

## Debug: What's the actual problem?

The extraction command `unzip -o` should overwrite, but it's not. Try this to understand why:

```bash
# Check what's IN the ZIP file
unzip -l /tmp/deals_management.zip | grep deals_menu.xml

# Check what's on the server
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/views/deals_menu.xml

# Check file modification time
stat /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/views/deals_menu.xml
```

**If the server file timestamp is NOT recent, the extraction didn't work.**
