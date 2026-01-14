# QUICK FIX REFERENCE CARD

## Status: 🔴 CRITICAL - Odoo Down, XML Parsing Error

---

## ⚡ INSTANT FIX (Pick One)

### Linux/Mac
```bash
bash recruitment_uae_improvements/scripts/emergency_fix_complete.sh
```

### Windows
```batch
recruitment_uae_improvements\scripts\emergency_fix_complete.bat
```

### With Server Details
```bash
bash recruitment_uae_improvements/scripts/emergency_fix_complete.sh odoo eigermarvelhr.com eigermarvel
```

---

## 🔍 What the Script Does (Automatically)

1. ✅ Validates all local XML files are correct
2. ✅ Creates backup on server (auto-restore point)
3. ✅ Copies clean files to server
4. ✅ Validates files on server
5. ✅ Stops Odoo
6. ✅ Starts Odoo
7. ✅ Verifies no errors in logs
8. ✅ Confirms module loaded

**Time: 2-3 minutes**

---

## ❌ If Script Fails

### Check status first:
```bash
bash recruitment_uae_improvements/scripts/diagnose.sh
```

### Manual quick steps:
```bash
# 1. Backup
ssh odoo@eigermarvelhr.com
cp -r /var/odoo/eigermarvel/extra-addons/recruitment_uae \
      /var/odoo/recruitment_uae_backup_$(date +%s)
exit

# 2. Copy files
scp -r recruitment_uae_improvements/views/*.xml \
    odoo@eigermarvelhr.com:/var/odoo/eigermarvel/extra-addons/recruitment_uae/views/

# 3. Restart
ssh odoo@eigermarvelhr.com
sudo systemctl stop odoo && sleep 5 && sudo systemctl start odoo
sleep 20
pgrep odoo && echo "OK" || echo "FAILED"
exit

# 4. Check
ssh odoo@eigermarvelhr.com
tail -50 /var/log/odoo/odoo.log | grep -i error
exit
```

---

## ✅ Verification

After fix, verify:
1. Open: `http://eigermarvelhr.com:8069`
2. Go to Apps
3. Search: `recruitment_uae`
4. Should show: **Installed** ✅
5. No errors in view load

---

## 🔄 Rollback (If Needed)

```bash
ssh odoo@eigermarvelhr.com
sudo systemctl stop odoo
rm -rf /var/odoo/eigermarvel/extra-addons/recruitment_uae
# Use your backup TIMESTAMP:
mv /var/odoo/recruitment_uae_backup_1234567890 \
   /var/odoo/eigermarvel/extra-addons/recruitment_uae
sudo systemctl start odoo
exit
```

---

## 📞 Troubleshooting

| Issue | Command | Expected |
|-------|---------|----------|
| Odoo not running | `ssh odoo@host "pgrep odoo"` | Should return PID |
| XML errors | `tail -50 /var/log/odoo/odoo.log \| grep xml` | No output = OK |
| Module state | `psql -U odoo eigermarvel -c "SELECT state FROM ir_module_module WHERE name='recruitment_uae';"` | installed |

---

## 💡 Key Points

- ✅ All local files are CLEAN
- ✅ Server has bad files (will be replaced)
- ✅ Backup exists (can rollback instantly)
- ✅ Fix takes 2-3 minutes
- ✅ No data loss risk
- ✅ Simple script handles everything

---

## NOW: Run the fix! 🚀

```bash
bash recruitment_uae_improvements/scripts/emergency_fix_complete.sh
```

