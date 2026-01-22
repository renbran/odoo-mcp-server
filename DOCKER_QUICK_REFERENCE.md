# Quick Reference - Odoo 17 Docker Testing

## 🚀 Start/Stop Commands

```powershell
# Start environment (fresh)
docker-compose down -v && docker-compose up -d

# Stop (keeps data)
docker-compose stop

# Restart
docker-compose restart

# View logs
docker-compose logs -f odoo
```

## 🌐 Access Points

- **Odoo UI:** http://localhost:8069
- **Database:** localhost:5432
- **Master Password:** admin
- **Default Login:** admin / admin

## 📦 Module Installation Order

1. rental_account_fields ← Install FIRST
2. rental_management ← Main module
3. rental_website ← Optional
4. rental_portal_syndication ← Optional

## ✅ Verification Checklist

```powershell
# Run automated check
.\verify-docker-setup.ps1

# Manual checks
docker-compose ps                                    # Should show 2 running
docker exec odoo17_test ls /mnt/extra-addons/       # Should show 4 modules
curl http://localhost:8069                           # Should return HTML
```

## 🧪 Quick Tests

### Test 1: Property Creation
1. Go to: Rental Management → Properties
2. Create → Fill details → Save
3. ✅ Verify: Property saved successfully

### Test 2: Contract & Invoice
1. Go to: Rental Management → Contracts
2. Create contract → Select property
3. Click "Generate Invoice"
4. ✅ Verify: Invoice created in Accounting

### Test 3: Dashboard
1. Go to: Rental Management → Dashboard
2. ✅ Verify: Charts load, statistics show

### Test 4: PDF Report
1. Select any property
2. Print → Property Brochure
3. ✅ Verify: PDF downloads

## 🔄 Reset to Clean State

```powershell
# Nuclear option - complete fresh start
docker-compose down -v
docker system prune -f
docker-compose up -d

# Wait 30 seconds, then create new database
```

## 📊 Module Test Status

| Module | Status | Notes |
|--------|--------|-------|
| rental_account_fields | ⏳ Pending | Install first |
| rental_management | ⏳ Pending | Main module |
| rental_website | ⏳ Pending | Website features |
| rental_portal_syndication | ⏳ Pending | Portal sync |

**Update after testing!**

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| Port 8069 in use | `netstat -ano \| findstr :8069` then kill process |
| Modules not visible | Go to Apps → Update Apps List |
| Can't access localhost:8069 | Wait 30s, check `docker logs odoo17_test` |
| Permission denied | Run PowerShell as Administrator |

## 📝 Test Results Log

```
Date: _____________
Tester: _____________

[ ] Environment starts successfully
[ ] All 4 modules visible in Apps
[ ] rental_account_fields installs
[ ] rental_management installs
[ ] rental_website installs
[ ] rental_portal_syndication installs
[ ] Property CRUD works
[ ] Contract creation works
[ ] Invoice generation works
[ ] Dashboard loads
[ ] Reports generate
[ ] Website listing works

Issues Found:
_________________________________
_________________________________
_________________________________
```

---

**Quick Start:** `docker-compose up -d` → http://localhost:8069 → Create DB → Install Modules → Test!
