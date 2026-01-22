# OSUSPROPERTIES ODOO FIX - COMPREHENSIVE GUIDE
## Critical Database Issues Resolution

**Date:** January 21, 2026
**Instance:** osusproperties (Odoo 17)  
**Server:** 104.207.139.132:8070  
**Status:** CRITICAL - Database cannot initialize

---

## 🚨 CRITICAL ISSUES IDENTIFIED

### 1. **User Type Validation Error** (BLOCKING)
```
odoo.exceptions.ValidationError: The user cannot have more than one user types.
File: /var/odoo/osusproperties/src/addons/purchase/security/purchase_security.xml:10
```

**Root Cause:** One or more users have multiple user type groups assigned (e.g., both Internal User and Portal)

### 2. **Database Concurrency Issues**
- SerializationFailure: concurrent update conflicts
- DeadlockDetected: Multiple processes competing for locks

### 3. **Translation File Syntax Error**
```
OSError: Syntax error in po file (line 92): unescaped double quote found
Language: ar_001
```

### 4. **View Definition Warnings**
- `'group'` attribute should be `'groups'` (5 files)
- Missing `alt` attribute on `<img>` tags

---

## ✅ SOLUTION - STEP BY STEP

### PHASE 1: Stop All Odoo Processes

```bash
# SSH to server
ssh odoo@104.207.139.132

# Stop the service
sudo systemctl stop odoo-osusproperties

# Kill any remaining processes
ps aux | grep odoo | grep osusproperties
# If any processes are running, kill them:
# sudo kill -9 <PID>

# Verify nothing is running
ps aux | grep odoo | grep osusproperties
```

### PHASE 2: Fix User Type Conflicts (CRITICAL)

#### Option A: Using PostgreSQL directly (FASTEST)

```bash
# Connect to PostgreSQL
sudo -u postgres psql osusproperties

# 1. Find the user type category ID
SELECT id, name FROM ir_module_category WHERE name = 'User types';
-- Note the ID (usually 14 or similar)

# 2. Find all user type group IDs  
SELECT g.id, g.name 
FROM res_groups g
WHERE g.category_id = 14;  -- Use actual category ID from step 1

-- Typical results:
-- ID | Name
-- ---+----------------
-- 10 | Internal User
-- 13 | Portal
-- 15 | Public

# 3. Find users with multiple user types
SELECT u.id, u.login, COUNT(DISTINCT r.group_id) as group_count,
       STRING_AGG(g.name, ', ') as groups
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.user_id
JOIN res_groups g ON r.group_id = g.id
WHERE g.category_id = 14
GROUP BY u.id, u.login
HAVING COUNT(DISTINCT r.group_id) > 1;

# 4. Fix each conflicted user (example for user ID 2)
-- Keep Internal User (10), remove Portal (13)
DELETE FROM res_groups_users_rel 
WHERE user_id = 2 AND group_id = 13;

-- Repeat for each conflicted user

# 5. Verify no conflicts remain
SELECT u.id, u.login, COUNT(DISTINCT r.group_id) as group_count
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.user_id
JOIN res_groups g ON r.group_id = g.id
WHERE g.category_id = 14
GROUP BY u.id, u.login
HAVING COUNT(DISTINCT r.group_id) > 1;

-- Should return 0 rows

# Exit PostgreSQL
\q
```

#### Option B: Using Odoo Shell (if database allows)

```bash
sudo -u odoo /var/odoo/osusproperties/venv/bin/python \
  /var/odoo/osusproperties/src/odoo-bin shell \
  -d osusproperties \
  --no-http

# In the Odoo shell:
env.cr.execute("""
    SELECT g.id, g.name 
    FROM res_groups g
    JOIN ir_module_category c ON g.category_id = c.id
    WHERE c.name = 'User types'
""")
user_type_groups = {r[0]: r[1] for r in env.cr.fetchall()}
print("User type groups:", user_type_groups)

# Find conflicted users
env.cr.execute("""
    SELECT u.id, u.login, array_agg(r.group_id) as groups
    FROM res_users u
    JOIN res_groups_users_rel r ON u.id = r.user_id
    WHERE r.group_id IN %s
    GROUP BY u.id, u.login
    HAVING COUNT(DISTINCT r.group_id) > 1
""", (tuple(user_type_groups.keys()),))

conflicted = env.cr.fetchall()
print(f"Found {len(conflicted)} conflicted users")

# Get specific group IDs
internal_group = env.ref('base.group_user').id
portal_group = env.ref('base.group_portal').id
public_group = env.ref('base.group_public').id

print(f"Internal: {internal_group}, Portal: {portal_group}, Public: {public_group}")

# Fix each user
for user_id, login, groups in conflicted:
    print(f"\nFixing: {login} (ID: {user_id})")
    
    # If user has internal, remove portal/public
    if internal_group in groups:
        to_remove = [g for g in groups if g in [portal_group, public_group]]
        if to_remove:
            env.cr.execute(
                "DELETE FROM res_groups_users_rel WHERE user_id = %s AND group_id = ANY(%s)",
                (user_id, to_remove)
            )
            print(f"  Removed: {[user_type_groups.get(g, g) for g in to_remove]}")
    # If user has portal, remove public/internal
    elif portal_group in groups:
        to_remove = [g for g in groups if g in [public_group, internal_group]]
        if to_remove:
            env.cr.execute(
                "DELETE FROM res_groups_users_rel WHERE user_id = %s AND group_id = ANY(%s)",
                (user_id, to_remove)
            )
            print(f"  Removed: {[user_type_groups.get(g, g) for g in to_remove]}")

env.cr.commit()
print("\n✓ All conflicts resolved!")

# Exit shell
exit()
```

### PHASE 3: Fix Translation File

```bash
# Find and disable problematic ar_001 translation files
find /var/odoo/osusproperties -name "*.po" -path "*ar_001*" 2>/dev/null

# Rename each problematic file
for file in $(find /var/odoo/osusproperties -name "ar_001.po" 2>/dev/null); do
    echo "Disabling: $file"
    mv "$file" "$file.bak"
done

# Or find files with ar_001 in path
find /var/odoo/osusproperties -type f -name "*.po" | xargs grep -l "ar_001" | while read file; do
    echo "Backing up: $file"
    cp "$file" "$file.bak"
done
```

### PHASE 4: Fix View Warnings

```bash
# Fix 'group' vs 'groups' attribute
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/account_line_view/views

# Create backup
tar -czf account_line_view_backup_$(date +%Y%m%d).tar.gz *.xml

# Fix all files
for file in invoice_line_view.xml bill_line_view.xml credit_note_line_view.xml refund_line_view.xml account_move_line_view.xml; do
    echo "Fixing: $file"
    sed -i 's/group="/groups="/g' "$file"
done

# Fix missing alt in budget views
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/base_account_budget/views

sed -i 's/<img /<img alt="Budget" /g' account_budget_views.xml
```

### PHASE 5: Reset Module State & Restart

```bash
# Option A: Update all modules (if safe)
sudo -u odoo /var/odoo/osusproperties/venv/bin/python \
  /var/odoo/osusproperties/src/odoo-bin \
  -d osusproperties \
  -u all \
  --stop-after-init \
  --log-level=info

# Option B: Update specific problematic modules
sudo -u odoo /var/odoo/osusproperties/venv/bin/python \
  /var/odoo/osusproperties/src/odoo-bin \
  -d osusproperties \
  -u purchase,stock,account_line_view,base_account_budget \
  --stop-after-init \
  --log-level=info

# Start the service
sudo systemctl start odoo-osusproperties

# Monitor logs
sudo tail -f /var/odoo/osusproperties/logs/odoo-server.log
```

---

## 🔍 VERIFICATION STEPS

### 1. Check Service Status
```bash
sudo systemctl status odoo-osusproperties --no-pager
```

Expected: **active (running)**

### 2. Check Logs for Errors
```bash
# Check for critical errors
sudo tail -n 100 /var/odoo/osusproperties/logs/odoo-server.log | grep -i "CRITICAL"

# Check for user type errors
sudo tail -n 100 /var/odoo/osusproperties/logs/odoo-server.log | grep -i "user type"

# Check for translation errors
sudo tail -n 100 /var/odoo/osusproperties/logs/odoo-server.log | grep -i "ar_001"

# Check for view warnings
sudo tail -n 100 /var/odoo/osusproperties/logs/odoo-server.log | grep -i "group.*is not valid"
```

Expected: **No output** or significantly reduced warnings

### 3. Test Web Access
```bash
curl -I http://localhost:8070
```

Expected: **HTTP/1.1 200 OK** or **303 See Other**

### 4. Verify Database Registry
```bash
sudo -u odoo /var/odoo/osusproperties/venv/bin/python \
  /var/odoo/osusproperties/src/odoo-bin \
  -d osusproperties \
  --test-enable \
  --stop-after-init \
  --log-level=warn 2>&1 | grep -i "registry.*loaded"
```

Expected: Registry loads successfully without errors

---

## 📊 TROUBLESHOOTING

### If user type errors persist:
1. Check that all multi-type users were fixed:
   ```sql
   SELECT u.login, array_agg(g.name)
   FROM res_users u
   JOIN res_groups_users_rel r ON u.id = r.user_id
   JOIN res_groups g ON r.group_id = g.id
   JOIN ir_module_category c ON g.category_id = c.id
   WHERE c.name = 'User types'
   GROUP BY u.id, u.login
   HAVING COUNT(*) > 1;
   ```

2. Check for orphaned group assignments:
   ```sql
   SELECT * FROM res_groups_users_rel r
   WHERE NOT EXISTS (
       SELECT 1 FROM res_users u WHERE u.id = r.user_id
   ) OR NOT EXISTS (
       SELECT 1 FROM res_groups g WHERE g.id = r.group_id
   );
   ```

### If deadlocks occur:
1. Ensure only one Odoo process is running
2. Check for long-running transactions:
   ```sql
   SELECT pid, state, query_start, query
   FROM pg_stat_activity
   WHERE datname = 'osusproperties'
   ORDER BY query_start;
   ```

3. Terminate stuck sessions:
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = 'osusproperties'
   AND pid <> pg_backend_pid()
   AND state = 'idle in transaction'
   AND query_start < now() - interval '5 minutes';
   ```

### If registry still fails to load:
1. Reset all module states:
   ```sql
   UPDATE ir_module_module SET state = 'installed'
   WHERE state = 'to upgrade';
   
   UPDATE ir_module_module SET state = 'uninstalled'
   WHERE state = 'to install';
   
   UPDATE ir_module_module SET state = 'installed'
   WHERE state = 'to remove';
   ```

2. Clear cache:
   ```bash
   rm -rf /var/odoo/.local/share/Odoo/sessions/*
   rm -rf /var/odoo/osusproperties/src/odoo/addons/*/static/src/**.pyc
   ```

---

## 📝 QUICK REFERENCE SQL

```sql
-- Get user type category ID
SELECT id FROM ir_module_category WHERE name = 'User types';

-- Get all user type groups
SELECT id, name FROM res_groups WHERE category_id = 14;

-- Find conflicted users
SELECT u.login, array_agg(g.name)
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.user_id
JOIN res_groups g ON r.group_id = g.id
WHERE g.category_id = 14
GROUP BY u.id, u.login
HAVING COUNT(*) > 1;

-- Remove portal from user ID 2
DELETE FROM res_groups_users_rel 
WHERE user_id = 2 AND group_id = 13;

-- Verify fix
SELECT COUNT(*) FROM (
    SELECT user_id
    FROM res_groups_users_rel r
    JOIN res_groups g ON r.group_id = g.id
    WHERE g.category_id = 14
    GROUP BY user_id
    HAVING COUNT(*) > 1
) conflicts;
-- Should return 0
```

---

## ✅ SUCCESS CRITERIA

- [ ] Service starts without errors
- [ ] No "user cannot have more than one user types" errors in logs
- [ ] No translation file syntax errors
- [ ] View warnings reduced or eliminated
- [ ] Web interface accessible at http://104.207.139.132:8070
- [ ] Database registry loads successfully
- [ ] No deadlocks or serialization failures
- [ ] All users have exactly one user type group

---

## 🔐 CREDENTIALS

**Database:** osusproperties  
**Web Admin:** salescompliance@osusproperties.com / 8586583  
**PostgreSQL:** postgres user (local only)  
**Odoo System User:** odoo  

---

## 📞 NEXT STEPS AFTER FIX

1. **Backup the database:**
   ```bash
   pg_dump -U postgres osusproperties | gzip > osusproperties_fixed_$(date +%Y%m%d).sql.gz
   ```

2. **Monitor for 24 hours** to ensure stability

3. **Update documentation** with any custom group assignments

4. **Review and clean up** disabled translation files

5. **Consider** implementing database maintenance tasks to prevent future issues

---

**Created by:** AI Assistant  
**Last Updated:** 2026-01-21  
**Status:** Ready for implementation
