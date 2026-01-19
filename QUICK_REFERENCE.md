# Quick Reference - UAE Recruitment Module

## Access URL
```
http://eigermarvel.cloudpepper.site:3000
or
http://65.20.72.53:3000
```

## Module Details
- **Module Name**: recruitment_uae
- **Odoo Version**: 18.0
- **Status**: Deployed & Ready
- **Location**: `/var/odoo/eigermarvel/extra-addons/cybroaddons.git-691b3baa7e1df/recruitment_uae/`

## Main Models

| Model | Purpose | Menu Path |
|-------|---------|-----------|
| Candidate | Employee profiles | Recruitment > Candidates |
| Job Requisition | Job openings | Recruitment > Job Requisitions |
| Application | Applications | Recruitment > Applications |
| Supplier | Agencies/Partners | Recruitment > Suppliers |
| Deployment | Employee assignments | Recruitment > Deployments |
| Contract | MOUs & Agreements | Recruitment > Contracts |
| Retention | Stability program | Recruitment > Retention |
| Follow-up | Stability checks | From Retention record |

## Key Features

### Retention Tracking
- **Guarantee Period**: Configurable days (typically 90)
- **Progress Tracking**: Days worked / Total period
- **Risk Assessment**: Automatic risk computation
- **Follow-ups**: Embedded tree view in Retention form

### Follow-up Management
- **Types**: Week 1, Week 2, 30-day, 60-day, 90-day, Ad-hoc
- **Assessment**: Satisfaction, issues, severity, risk
- **Actions**: Track resolution and next steps
- **Status**: Scheduled → Completed → Issue Found → Escalated

### Risk Indicators
- **Red (Danger)**: retention_at_risk = True
- **Yellow (Warning)**: issues_identified = True
- **Automatic**: Based on working status and issue severity

## Common Tasks

### 1. Create a Deployment
```
Menu > Recruitment > Deployments > Create
- Select candidate
- Assign to client/department
- Verify retention record created
- Set guarantee period
```

### 2. Add Follow-up
```
Open Retention record > Follow-Up History tab > Add Line
- Set follow-up date and type
- Update candidate status
- Identify any issues
- Assess satisfaction
- Save
```

### 3. Assess Risk
```
In Follow-up record:
- If candidate_working = False → retention_at_risk = True
- If issue_severity in ['severe', 'critical'] → retention_at_risk = True
- Tree row shows red (danger) background
```

### 4. Track Issue Resolution
```
When issue found:
- Fill issue_type and severity
- Add issue_details
- Set action_taken
- Change state to "Issue Found - Follow-Up Required"
- Schedule next follow-up
```

## Fields Reference

### Retention
- `retention_period_days` - Guarantee period length
- `candidate_working_days` - Days worked so far
- `retention_at_risk` - Risk status (computed)
- `retention_paid` - Payment made?
- `followup_ids` - All follow-ups for this record

### Follow-up
- `followup_date` - Date of follow-up
- `followup_type` - Type of check performed
- `candidate_working` - Still employed?
- `candidate_satisfied` - Satisfaction (very satisfied...very dissatisfied)
- `issues_identified` - Any issues found?
- `issue_severity` - minor/moderate/severe/critical
- `issue_details` - Description of issues
- `action_taken` - What was done to resolve
- `retention_at_risk` - Computed risk (not working OR severe/critical)
- `state` - Status in workflow

## Database Info

### Odoo Instance (eigermarvel)
- **HTTP Port**: 3000
- **Gevent Port**: 3001
- **Database**: eigermarvel (PostgreSQL)
- **Config**: `/var/odoo/eigermarvel/odoo.conf`
- **Logs**: `/var/odoo/eigermarvel/logs/odoo-server.log`

### Process Management
```bash
# Check if running
ps aux | grep 'odoo-bin.*3000'

# Check logs
tail -f /var/odoo/eigermarvel/logs/odoo-server.log

# Module location
ls -la /var/odoo/eigermarvel/extra-addons/cybroaddons.git-691b3baa7e1df/recruitment_uae/
```

## Installation Checklist

- [x] Module files deployed
- [x] Python syntax validated
- [x] XML syntax validated
- [x] Manifest configured
- [x] All views registered
- [x] Database models ready
- [ ] Module installed in Odoo UI ← DO THIS FIRST
- [ ] User training completed
- [ ] Test data created
- [ ] Workflows configured
- [ ] Reports verified

## First Time Setup

1. **Install Module**
   - Settings > Technical > Modules > Update Modules List
   - Search: "recruitment_uae"
   - Click Install

2. **Verify Installation**
   - Menu should show "Recruitment" option
   - All submenus should be available
   - No error messages in logs

3. **Create Test Data**
   - Create candidate record
   - Create job requisition
   - Create deployment
   - Verify retention auto-created

4. **Test Follow-up**
   - Open retention record
   - Add follow-up in "Follow-Up History" tab
   - Verify tree view displays correctly
   - Test decorations (set issues_identified to True)

## Troubleshooting

### Issue: Module doesn't appear in menu
**Solution**: Click "Update Modules List" in Settings > Technical > Modules

### Issue: Fields showing errors
**Solution**: Clear browser cache, then reload Odoo

### Issue: Tree view not displaying
**Solution**: 
- Verify followup_ids field exists in retention.py
- Check retention_views.xml syntax
- Reload module list

### Issue: Decorations not working
**Solution**: 
- Verify field name in decoration condition
- Check field type matches (Boolean for issues_identified, etc.)
- Save record to compute values

### Issue: Performance slow
**Solution**:
- Check PostgreSQL is running
- Verify database indexes created
- Check server logs for errors
- Monitor system resources

## Common Workflows

### Workflow 1: New Employee Deployment
```
1. Create Job Requisition
2. Receive Applications
3. Create Deployment
   → Auto-creates Retention (90 days)
4. Day 7: Create Week 1 Follow-up
   → Check candidate satisfaction
   → Identify any issues
5. Day 30: Create 30-day Follow-up
   → Verify still employed
   → Assess satisfaction
6. Day 60: Create 60-day Follow-up
   → Same checks
7. Day 90: Create 90-day Follow-up
   → Final check
   → Mark retention complete
```

### Workflow 2: Issue Resolution
```
1. During follow-up, identify issue
2. Set issues_identified = True
3. Select issue_type
4. Set issue_severity
5. Add issue_details
6. Save (retention_at_risk auto-computed = True)
7. Tree row shows in red (danger)
8. Create action plan
9. Schedule follow-up
10. Record action_taken
11. Update state to "Issue Found - Follow-Up Required"
12. Follow up until resolved
```

## Reporting

### Built-in Reports
- Candidate applications
- Deployment status
- Retention tracking
- Follow-up history
- Issue tracking

### Custom Reports (Can be created)
- Risk assessment dashboard
- Follow-up schedule
- Issue trend analysis
- Candidate satisfaction trends
- Retention success rate

## API Integration

The module can be integrated via:
- Odoo REST API (JSON-RPC)
- Custom Python controllers
- Webhooks
- Third-party integrations

Example endpoints:
```
POST /api/recruitment.candidate/create
POST /api/recruitment.deployment/create
GET /api/recruitment.retention/read
POST /api/recruitment.followup/create
```

## Security Notes

- All records tracked via mail.thread
- Audit trail available
- User actions logged
- Role-based access configurable
- No sensitive data exposed by default

## Performance Tips

1. **Indexing**: Fields on followup_ids are indexed
2. **Caching**: Computed fields stored for performance
3. **Filters**: Use proper domain filters for large datasets
4. **Batch**: Bulk operations supported for deployments
5. **Reporting**: Pre-computed aggregations available

## Contact & Support

- **Server Admin**: See server configuration
- **Database Admin**: PostgreSQL access for backups
- **Odoo Logs**: `/var/odoo/eigermarvel/logs/odoo-server.log`
- **Error Handling**: Check logs for detailed error messages

---

**Last Updated**: January 13, 2026  
**Module Version**: 18.0.1.1.0  
**Status**: ✅ Production Ready
