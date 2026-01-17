# Odoo 17 Docker Testing Environment

Quick setup guide for testing the Deal Report module in a containerized Odoo 17 environment.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v2.0+
- Ports 8069 and 5432 available

## Quick Start

### 1. Start Odoo Environment

```powershell
# Start all services (Odoo + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f odoo
```

### 2. Access Odoo

- **URL**: http://localhost:8069
- **Master Password**: admin
- **Database Name**: odoo17_test (create on first access)

### 3. Create Database

1. Navigate to http://localhost:8069
2. Click "Create Database"
3. Fill in:
   - **Database Name**: `odoo17_test`
   - **Email**: `admin@example.com`
   - **Password**: `admin`
   - **Language**: English
   - **Country**: Your country
   - **Load demonstration data**: ✓ (recommended for testing)
4. Click "Create Database"

### 4. Install Modules

After database creation:

1. Go to Apps menu (activate Developer Mode if needed)
2. Click "Update Apps List"
3. Search for "Deal Report"
4. Click "Install"

This will automatically install dependencies:
- Sale Management
- Invoicing/Accounting
- Mail (Chatter)

### 5. Test the Module

#### A. Create a Deal Report

1. Navigate to: **Sales → Deals → Deal Reports**
2. Click "Create"
3. Select a Sale Order
4. Click "Save"
5. Test workflow:
   - Click "Confirm"
   - Click "Generate Commissions"
   - Click "Process Bills"
   - Use smart button to view invoices

#### B. View Dashboard

1. Navigate to: **Sales → Deals → Deal Dashboard**
2. Select a period (This Month, Last Month, etc.)
3. Click "Refresh"
4. Click "Open Analytics"

#### C. Explore Analytics

1. Navigate to: **Sales → Deals → Analytics**
2. Switch between:
   - **Overview**: Bar charts, pivot, kanban
   - **Trends**: Line chart
   - **Distribution**: Pie chart
3. Apply filters (Period, Amount, Commission, etc.)
4. Use Group By options

## Management Commands

### Stop Environment

```powershell
# Stop services (data persists)
docker-compose stop

# Stop and remove containers (data persists in volumes)
docker-compose down
```

### Restart Environment

```powershell
# Restart all services
docker-compose restart

# Restart only Odoo
docker-compose restart odoo
```

### Clean Restart

```powershell
# Remove everything including data
docker-compose down -v

# Start fresh
docker-compose up -d
```

### View Logs

```powershell
# All services
docker-compose logs -f

# Only Odoo
docker-compose logs -f odoo

# Only PostgreSQL
docker-compose logs -f db
```

### Access Container Shell

```powershell
# Odoo container
docker exec -it odoo17_app bash

# PostgreSQL container
docker exec -it odoo17_postgres bash

# Connect to database
docker exec -it odoo17_postgres psql -U odoo -d odoo17_test
```

## Module Development Workflow

### 1. Update Module Code

Make changes to files in `deal_report/` folder.

### 2. Update Module in Odoo

Option A - UI (recommended for testing):
1. Go to Apps
2. Search "Deal Report"
3. Click "Upgrade"

Option B - Command line:
```powershell
docker exec -it odoo17_app odoo -d odoo17_test -u deal_report --stop-after-init
docker-compose restart odoo
```

### 3. Debug Mode

Enable Developer Mode:
1. Settings → Activate Developer Mode
2. Or add `?debug=1` to URL

## Configuration Details

### Database Connection

- **Host**: localhost
- **Port**: 5432
- **Database**: odoo17_test
- **User**: odoo
- **Password**: odoo

### Odoo Connection

- **URL**: http://localhost:8069
- **XML-RPC**: http://localhost:8069/xmlrpc/2
- **JSON-RPC**: http://localhost:8069/web/database/selector

### For MCP Server Integration

Update your `.env` file:

```env
ODOO_URL=http://localhost:8069
ODOO_DB=odoo17_test
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=admin
```

Test MCP connection:
```powershell
npm run dev
```

## Troubleshooting

### Port Already in Use

```powershell
# Check what's using port 8069
netstat -ano | findstr :8069

# Kill process (replace PID)
taskkill /PID <process_id> /F

# Or change port in docker-compose.yml
ports:
  - "8070:8069"
```

### Database Connection Issues

```powershell
# Check if PostgreSQL is running
docker ps | findstr postgres

# Restart database
docker-compose restart db

# View database logs
docker-compose logs db
```

### Module Not Showing Up

```powershell
# Restart Odoo with update
docker-compose restart odoo

# Force module list update
docker exec -it odoo17_app odoo -d odoo17_test --update=all --stop-after-init
docker-compose restart odoo
```

### Performance Issues

Increase Docker resources:
1. Docker Desktop → Settings → Resources
2. Set:
   - CPUs: 4+
   - Memory: 4GB+
3. Apply & Restart

## Data Persistence

Data is stored in Docker volumes:
- `odoo-db-data`: PostgreSQL database
- `odoo-web-data`: Odoo filestore (attachments, etc.)

To completely reset:
```powershell
docker-compose down -v
docker volume prune
docker-compose up -d
```

## Testing Checklist

- [ ] Database created successfully
- [ ] Deal Report module installed
- [ ] Can create Deal Report from Sale Order
- [ ] Workflow buttons work (Confirm, Generate Commissions, Process Bills)
- [ ] Dashboard shows KPIs correctly
- [ ] All chart types display (bar, line, pie, kanban, pivot)
- [ ] Filters work (period, amount, commission, status)
- [ ] Auto-post invoice toggle works
- [ ] Chatter tracking visible
- [ ] PDF report generates correctly
- [ ] Search and Group By functions work

## Next Steps

Once testing is complete:
1. Export your configuration/customizations
2. Deploy to production environment
3. Set up regular backups
4. Configure SSL/HTTPS
5. Set proper security settings

## Support

- Odoo Documentation: https://www.odoo.com/documentation/17.0/
- Docker Documentation: https://docs.docker.com/
- Module Issues: Check module logs in Odoo
