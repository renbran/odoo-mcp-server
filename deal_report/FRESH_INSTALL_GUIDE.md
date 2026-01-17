# Fresh Installation Guide - After Database Reset

## What Happened
The Odoo database became corrupted during the module installation attempt. The database has been reset and Odoo has been restarted with a fresh database.

## Current Status
✓ Odoo server is running at http://localhost:8069
✓ Fresh database has been initialized  
✓ Module files are all syntactically correct and ready

## Installation Steps

### Step 1: Create Initial Database
1. Open http://localhost:8069 in your browser
2. You should see the Odoo Database Manager/Setup screen
3. Create a new database:
   - **Database Name**: `odoo` (or any name you prefer)
   - **Email**: `admin@example.com`
   - **Password**: `admin`
   - **Phone**: `+1234567890` (optional)
   - **Language**: English
   - **Country**: Your country
   - **Demo Data**: Leave unchecked for faster setup
4. Click "Create Database"
5. Wait for the database to be created (2-5 minutes)

### Step 2: Install Sale Module
1. Once logged in, you should be on the main dashboard
2. Go to **Apps** (top left menu or search)
3. Search for "Sale" or "Sales"
4. Click on "Sales" module
5. Click **Install**
6. Wait for installation to complete

### Step 3: Install Deal Report Module
1. Go to **Apps** > **Database** > **Update Apps List** (if needed)
2. Search for "deal_report" or "Deal Report"
3. Find **"Deal Report & Commissions"** module
4. Click **Install**
5. Wait for installation to complete

### Step 4: Verify Installation
1. Go to **Sales** menu in the left sidebar
2. You should see a new **"Deals"** submenu with:
   - **Deal Reports** (main list view)
   - **Deal Dashboard** (KPI dashboard)
   - **Analytics** (submenu with Overview, Trends, Distribution)

### Step 5: Create Your First Deal
1. Click **Sales** > **Deals** > **Deal Reports**
2. Click **Create** button
3. Fill in the required fields:
   - **Deal Reference**: Will auto-generate
   - **Deal Date**: Select a date
   - **Sale Order**: Select or create a sale order
   - (Other fields will auto-populate)
4. Click **Save**

## Troubleshooting

### Odoo won't load
- Check if container is running: `docker ps`
- Check logs: `docker logs odoo17_app | tail -50`
- Try restarting: `docker restart odoo17_app`

### Module installation fails
- **Check dependencies**: Ensure Sale and Account modules are installed first
- **Check logs** for specific error message
- **Try updating module list**: Go to Apps > Database > Update Apps List

### Menu doesn't appear after install
- Clear browser cache (Ctrl+Shift+Delete) and refresh (Ctrl+F5)
- Log out and log back in
- Go to Apps > deal_report and verify status is "Installed"

### "Internal Server Error"
- This usually means database tables haven't been created yet
- Wait a few more seconds and refresh
- Check logs: `docker logs odoo17_app | tail -100`

## Module Components

The **Deal Report & Commissions** module includes:

### Models (Database Tables)
- `deal.report` - Main deal record with workflow
- `deal.commission.line` - Commission tracking
- `deal.bill.line` - Billing integration
- `deal.dashboard` - KPI dashboard (transient)

### Views
- **Tree View**: List all deals
- **Form View**: Detail view of a deal with tabs
- **Search View**: Advanced filtering
- **Dashboard**: KPI metrics and status overview
- **Graphs**: Bar, Line, Pie charts
- **Pivot**: Data analysis pivot table
- **Kanban**: Card-based view grouped by status

### Reports
- **Deal Report (PDF)**: Printable deal details with commission breakdown

### Workflow States
- Draft → Confirmed → Commissioned → Billed → Cancel

## Next Steps

After successful installation:

1. **Create Sale Orders** in the Sale module
2. **Create Deal Reports** linked to sale orders
3. **Generate Commissions** when deals are confirmed
4. **Create Invoices** for commission amounts
5. **View Analytics** in the Deal Dashboard
6. **Monitor KPIs** in the dashboard

## Support

All module files have been verified as syntactically correct:
- ✓ 4 Python models with proper definitions
- ✓ 9 XML view files with proper structure
- ✓ 1 CSV security file with correct access rules
- ✓ 1 PDF report template
- ✓ Data files (sequences, products)

If you continue to experience issues:
1. Provide the exact error message
2. Check `/var/log/odoo/odoo-server.log` in the container
3. Ensure all dependencies (sale, account, mail) are installed
4. Verify browser is not caching old pages (Ctrl+F5)
