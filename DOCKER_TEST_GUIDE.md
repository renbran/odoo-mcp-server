# Odoo 17 Docker Testing Environment - Quick Start

## 🎯 Purpose
Clean, fresh Odoo 17 Docker environment for testing rental management modules without any pre-installed customizations.

---

## 📋 Prerequisites

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version` and `docker-compose --version`

2. **Modules Ready**
   - ✅ rental_management
   - ✅ rental_website
   - ✅ rental_portal_syndication
   - ✅ rental_account_fields

---

## 🚀 Quick Start (5 Steps)

### Step 1: Start Fresh Docker Environment

```powershell
# Navigate to project directory
cd D:\01_WORK_PROJECTS\odoo-mcp-server

# Start Odoo 17 + PostgreSQL (fresh containers)
docker-compose up -d
```

**What happens:**
- Downloads official Odoo 17.0 image (~1GB, first time only)
- Creates PostgreSQL 15 database container
- Mounts rental modules to `/mnt/extra-addons/`
- Starts on http://localhost:8069

### Step 2: Wait for Startup (30-60 seconds)

```powershell
# Check logs to confirm Odoo is ready
docker-compose logs -f odoo
```

**Look for:** `odoo odoo: HTTP service (werkzeug) running on...`

Press `Ctrl+C` to exit logs.

### Step 3: Access Odoo

Open browser: **http://localhost:8069**

**Initial Setup:**
1. Master Password: `admin`
2. Database Name: `odoo17_test`
3. Email: `admin@example.com`
4. Password: `admin`
5. Language: English
6. Country: United Arab Emirates
7. Load Demo Data: **No** (uncheck)

Click **Create Database**

### Step 4: Install Rental Modules

After database creation:

1. Go to **Apps** menu
2. Click **Update Apps List**
3. Remove "Apps" filter
4. Search: `rental`

**Install in this order:**
1. ✅ **rental_account_fields** (install first - dependency)
2. ✅ **rental_management** (main module)
3. ✅ **rental_website** (optional - website features)
4. ✅ **rental_portal_syndication** (optional - portal integration)

### Step 5: Test Modules

**Basic Tests:**

1. **Property Management**
   - Go to **Rental Management → Properties → Properties**
   - Click **Create**
   - Fill property details (name, type, price)
   - Save and verify

2. **Rental Contract**
   - Go to **Rental Management → Contracts → Rental Contracts**
   - Click **Create**
   - Select property, tenant, dates
   - Generate invoice
   - Verify invoice created

3. **Dashboard**
   - Go to **Rental Management → Dashboard**
   - Verify charts and statistics load

4. **Reports**
   - Select a property
   - Click **Print → Property Brochure**
   - Verify PDF generation

---

## 🛠️ Docker Commands Reference

### Container Management

```powershell
# Start containers (fresh each time)
docker-compose up -d

# Stop containers (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove EVERYTHING (fresh start)
docker-compose down -v
docker system prune -a --volumes

# View logs
docker-compose logs -f odoo          # Odoo logs
docker-compose logs -f db            # Database logs

# Restart Odoo only
docker-compose restart odoo

# Execute commands in Odoo container
docker exec -it odoo17_test bash

# Check running containers
docker-compose ps
```

### Database Management

```powershell
# Access PostgreSQL directly
docker exec -it odoo17_postgres psql -U odoo -d odoo17_test

# Backup database
docker exec odoo17_postgres pg_dump -U odoo odoo17_test > backup.sql

# Restore database
cat backup.sql | docker exec -i odoo17_postgres psql -U odoo -d odoo17_test

# List databases
docker exec odoo17_postgres psql -U odoo -c "\l"
```

---

## 🧪 Testing Scenarios

### Test 1: Fresh Installation
```powershell
# Clean start
docker-compose down -v
docker-compose up -d

# Follow Step 3-5 above
```

### Test 2: Module Update
```powershell
# After making code changes to modules
docker-compose restart odoo

# In Odoo UI:
# Apps → rental_management → Upgrade
```

### Test 3: Performance Testing
```powershell
# Enable multi-worker mode (edit docker-compose.yml)
# Change: workers = 0  →  workers = 2

docker-compose restart odoo
```

### Test 4: Migration Testing
```powershell
# Test migrations from rental_management/migrations/
# Simulate upgrade from v17.0.2.4.0 to v17.0.2.5.0

# 1. Install old version
# 2. Create test data
# 3. Upgrade module
# 4. Verify data integrity
```

---

## 📊 Module Test Checklist

### rental_management

- [ ] **Property CRUD**
  - [ ] Create residential property
  - [ ] Create commercial property
  - [ ] Upload images
  - [ ] Add amenities
  - [ ] Add specifications
  - [ ] Publish to website

- [ ] **Rental Contract**
  - [ ] Create contract
  - [ ] Generate payment schedule
  - [ ] Create invoices automatically
  - [ ] Extend contract
  - [ ] Terminate contract

- [ ] **Sales Contract**
  - [ ] Create sale offer
  - [ ] Payment plan (installments)
  - [ ] Generate invoices per schedule
  - [ ] Commission calculation

- [ ] **Maintenance**
  - [ ] Create maintenance request
  - [ ] Assign vendor
  - [ ] Track costs
  - [ ] Close request

- [ ] **Dashboard**
  - [ ] Property statistics
  - [ ] Revenue charts
  - [ ] Contract status
  - [ ] Maintenance overview

- [ ] **Reports**
  - [ ] Property brochure
  - [ ] Sales agreement
  - [ ] Tenancy agreement
  - [ ] Invoice reports

### rental_website

- [ ] **Public Listing**
  - [ ] View published properties
  - [ ] Filter by type/location
  - [ ] Search functionality
  - [ ] Property details page

- [ ] **Booking**
  - [ ] Inquiry form
  - [ ] Lead creation
  - [ ] Email notifications

### rental_portal_syndication

- [ ] **Portal Config**
  - [ ] Configure portal credentials
  - [ ] Enable XML feed
  - [ ] Test webhook

- [ ] **Property Sync**
  - [ ] Publish to portal
  - [ ] Sync status
  - [ ] View sync logs

---

## 🐛 Troubleshooting

### Issue: Containers won't start

```powershell
# Check Docker is running
docker info

# Check port conflicts (8069, 5432)
netstat -ano | findstr :8069
netstat -ano | findstr :5432

# View detailed logs
docker-compose logs --tail=100 odoo
```

### Issue: Can't access http://localhost:8069

```powershell
# Verify Odoo is running
docker-compose ps

# Check Odoo logs for errors
docker-compose logs odoo | Select-String -Pattern "ERROR|CRITICAL"

# Restart containers
docker-compose restart
```

### Issue: Modules not visible

```powershell
# Verify modules mounted correctly
docker exec odoo17_test ls -la /mnt/extra-addons/

# Should show: rental_management, rental_website, etc.

# Update apps list in Odoo
# Apps → Update Apps List
```

### Issue: Permission errors

```powershell
# Fix Windows file permissions
icacls rental_management /grant Everyone:F /T
icacls rental_website /grant Everyone:F /T
icacls rental_portal_syndication /grant Everyone:F /T
icacls rental_account_fields /grant Everyone:F /T
```

### Issue: Database initialization failed

```powershell
# Remove all volumes and restart fresh
docker-compose down -v
docker volume prune -f
docker-compose up -d
```

---

## 📁 File Structure

```
odoo-mcp-server/
├── docker-compose.yml          ← Docker services definition
├── config/
│   └── odoo.conf              ← Odoo configuration
├── logs/                      ← Odoo log files
├── rental_management/         ← Module (auto-mounted)
├── rental_website/            ← Module (auto-mounted)
├── rental_portal_syndication/ ← Module (auto-mounted)
├── rental_account_fields/     ← Module (auto-mounted)
└── DOCKER_TEST_GUIDE.md       ← This file
```

---

## 🔒 Security Notes

**⚠️ FOR TESTING ONLY - NOT FOR PRODUCTION**

- Default passwords are intentionally simple
- Database is accessible on localhost:5432
- No SSL/HTTPS configured
- Master password is `admin`
- All ports exposed to localhost

**For Production:** Use proper secrets, SSL certificates, and security hardening.

---

## 🎓 Learning Resources

- **Odoo Documentation:** https://www.odoo.com/documentation/17.0/
- **Docker Compose:** https://docs.docker.com/compose/
- **Module Development:** https://www.odoo.com/documentation/17.0/developer/

---

## 📝 Next Steps After Testing

1. **Document Issues:** Note any bugs or errors found
2. **Performance Metrics:** Record load times, response times
3. **Data Validation:** Verify all fields save correctly
4. **Integration Tests:** Test with other Odoo modules (sale, account, crm)
5. **Browser Testing:** Test on Chrome, Firefox, Edge
6. **Mobile Testing:** Test responsive design on mobile devices

---

## 🔄 Clean Slate Reset

To start completely fresh:

```powershell
# Stop and remove everything
docker-compose down -v

# Remove Docker images (optional - will re-download)
docker rmi odoo:17.0
docker rmi postgres:15

# Clean all Docker data
docker system prune -a --volumes

# Start fresh
docker-compose up -d
```

---

**Created:** 2026-01-21  
**Odoo Version:** 17.0 (Official Docker Image)  
**Database:** PostgreSQL 15  
**Status:** ✅ Ready for Testing

