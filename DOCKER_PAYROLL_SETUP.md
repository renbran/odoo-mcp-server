# 🐳 Local Docker Payroll Module Setup Guide

**Date:** January 23, 2026  
**Target:** odoo17_test (Local Docker Instance)  
**Objective:** Install payroll modules for UAE compliance testing

---

## 📋 **Quick Setup Steps**

### Step 1: Download Payroll Modules

**Option A - Automated Download (Recommended)**
```bash
python download_payroll_modules.py
```

This will:
- Clone from GitHub repositories
- Extract hr_payroll_community and hr_payroll_account_community
- Place them in `test_modules/` directory

**Option B - Manual Download**
1. Go to https://apps.odoo.com/
2. Search "Odoo 17 HR Payroll Community Edition"
3. Download ZIP files
4. Extract to `test_modules/hr_payroll_community/`
5. Extract to `test_modules/hr_payroll_account_community/`

**Option C - Copy from OSUSPROPERTIES**
```bash
python export_payroll_modules.py
# Then get SSH access and download actual files
```

---

### Step 2: Copy Modules to Docker Container

**Find your Docker container:**
```bash
docker ps
# Look for odoo container
```

**Copy modules to container:**
```bash
# Copy hr_payroll_community
docker cp test_modules/hr_payroll_community <container_name>:/mnt/extra-addons/

# Copy hr_payroll_account_community
docker cp test_modules/hr_payroll_account_community <container_name>:/mnt/extra-addons/
```

**Alternative: If using volume mount**
```bash
# If test_modules is mounted, just copy there
cp -r test_modules/hr_payroll_community /path/to/mounted/addons/
cp -r test_modules/hr_payroll_account_community /path/to/mounted/addons/
```

---

### Step 3: Restart Odoo Container

```bash
docker restart <container_name>

# Or if using docker-compose
docker-compose restart odoo
```

**Wait for container to be ready (~30 seconds)**

---

### Step 4: Install Modules via Script

```bash
python install_payroll_local.py
```

This will:
- Connect to local Odoo instance
- Update module list
- Install hr_payroll_community
- Install hr_payroll_account_community
- Verify installation

**OR Install Manually:**
1. Go to http://localhost:8069
2. Login (admin/admin)
3. Apps → Update Apps List
4. Search "hr_payroll_community" → Install
5. Search "hr_payroll_account_community" → Install

---

### Step 5: Verify Installation

```bash
python check_hr_modules.py
```

**Expected Output:**
```
LOCAL (odoo17_test):
  ✓ commission_ax (17.0.3.2.2)
  ✓ hr_uae (17.0.1.0)
  ✓ hr_payroll_community (17.0.1.0.0)        ← NEW
  ✓ hr_payroll_account_community (17.0.1.0.0) ← NEW
```

---

## 🐳 **Docker Container Information**

### Find Container Details

```bash
# List running containers
docker ps

# Check Odoo logs
docker logs <container_name>

# Access container shell
docker exec -it <container_name> bash

# Check addons path inside container
ls /mnt/extra-addons/
```

### Common Docker Locations

**Addons Path:**
- `/mnt/extra-addons/` (common)
- `/opt/odoo/addons/`
- `/var/lib/odoo/addons/`

**Configuration:**
- `/etc/odoo/odoo.conf`

**Logs:**
- `docker logs <container_name>`
- `/var/log/odoo/odoo.log` (inside container)

---

## 🔧 **Troubleshooting**

### Module Not Found After Copy

**Check addons path in odoo.conf:**
```bash
docker exec <container_name> cat /etc/odoo/odoo.conf | grep addons_path
```

**Verify files are accessible:**
```bash
docker exec <container_name> ls /mnt/extra-addons/hr_payroll_community/
```

### Installation Fails

**Check dependencies:**
```bash
# Required modules (should already be installed):
- hr
- hr_contract
- hr_holidays (or hr_leave)
- account
```

**Check logs:**
```bash
docker logs <container_name> --tail 100
```

### Database Connection Issues

**Verify database exists:**
```bash
docker exec <postgres_container> psql -U odoo -l | grep odoo17_test
```

**Test connection:**
```bash
python test_sgctechai_connection.py
```

---

## 📊 **Current Module Status**

| Module | Status | Version | Location |
|--------|--------|---------|----------|
| hr_uae | ✅ Installed | 17.0.1.0 | test_modules/ |
| commission_ax | ✅ Installed | 17.0.3.2.2 | test_modules/ |
| hr_payroll_community | ⏳ To Install | 17.0.1.0.0 | Need to download |
| hr_payroll_account_community | ⏳ To Install | 17.0.1.0.0 | Need to download |

---

## 🎯 **Next Steps After Installation**

Once payroll modules are installed:

1. **Verify Installation:**
   - Run `python check_hr_modules.py`
   - Check via web interface: Apps → Installed

2. **Ready for Phase 1:**
   - Begin UAE Payroll Compliance implementation
   - Employee Master Data enhancement
   - Compliance fields addition

3. **Testing Environment:**
   - All testing in Docker container
   - Safe to experiment
   - Easy to reset if needed

---

## 📝 **Available Scripts**

| Script | Purpose |
|--------|---------|
| `download_payroll_modules.py` | Download modules from GitHub |
| `install_payroll_local.py` | Automated installation |
| `check_hr_modules.py` | Verify installation status |
| `export_payroll_modules.py` | Export from OSUSPROPERTIES |
| `list_databases.py` | List available databases |

---

## 🔒 **Docker Backup Before Changes**

**Backup database before major changes:**
```bash
# Backup database
docker exec <postgres_container> pg_dump -U odoo odoo17_test > backup_$(date +%Y%m%d).sql

# Or using docker-compose
docker-compose exec db pg_dump -U odoo odoo17_test > backup_$(date +%Y%m%d).sql
```

**Restore if needed:**
```bash
docker exec -i <postgres_container> psql -U odoo odoo17_test < backup_20260123.sql
```

---

## ✅ **Installation Checklist**

- [ ] Docker container running
- [ ] Payroll modules downloaded
- [ ] Modules copied to container addons path
- [ ] Container restarted
- [ ] Module list updated
- [ ] hr_payroll_community installed
- [ ] hr_payroll_account_community installed
- [ ] Installation verified
- [ ] Ready for Phase 1 development

---

**Status:** Ready to begin installation  
**Estimated Time:** 15-30 minutes  
**Next:** Run `python download_payroll_modules.py`
