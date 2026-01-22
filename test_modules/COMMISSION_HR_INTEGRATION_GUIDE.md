# Commission AX ↔ HR UAE Integration Guide

## ✅ Integration Complete!

### What Was Done

I've successfully integrated the **commission_ax** module with **hr_uae** module to enable **automatic commission rate population** based on HR employee profiles and lead types.

---

## 🔄 How It Works

### The Integration Flow

```
1. User selects an Agent/Employee in Sales Order
   ↓
2. System checks if partner is linked to HR Employee
   ↓
3. System checks the Lead Source (source_id field)
   ↓
4. System determines: Personal Lead or Business Lead
   ↓
5. System looks up employee's commission rate from HR
   ↓
6. System auto-fills the commission rate field
   ↓
7. System auto-calculates commission amount
```

---

## 📊 Lead Type Detection

### How System Determines Personal vs Business

The system checks the **source_id** field (Marketing Source/UTM Source) on the Sales Order:

**Personal Lead:**
- Source name contains "**personal**"
- Source name contains "**referral**"
- Origin contains "**personal**" or "**referral**"

**Business Lead:**
- Everything else (default)

**Example:**
```python
Source: "Personal Referral" → Personal Lead → Agent gets 60%
Source: "Google Ads"        → Business Lead → Agent gets 40%
Source: "Walk-in"           → Business Lead → Agent gets 40%
```

---

## 💰 Commission Rate Auto-Population

### Agent 1 (agent1_partner_id)

When you select an employee as Agent 1, the system:

1. **Finds the HR employee** linked to the partner
2. **Checks their agent_type** (Primary, Secondary, Exclusive RM, Exclusive SM)
3. **Checks the lead source** (Personal or Business)
4. **Auto-fills commission rate:**

| Agent Type | Personal Lead | Business Lead |
|------------|---------------|---------------|
| **Primary Agent** | 60% (from `primary_agent_personal_commission`) | 40% (from `primary_agent_business_commission`) |
| **Secondary Agent** | 60% (from `secondary_agent_personal_commission`) | 40% (from `secondary_agent_business_commission`) |
| **Exclusive RM** | 5% (from `exclusive_rm_commission`) | 5% (same) |
| **Exclusive SM** | 2% (from `exclusive_sm_commission`) | 2% (same) |

### Agent 2 (agent2_partner_id)

Same logic as Agent 1. Typically used for secondary agents.

### Manager (manager_partner_id)

When you select a manager:
- Uses **Exclusive RM** commission rate (5% default)
- Or **Exclusive SM** rate if employee is type SM
- Doesn't vary by lead type (managers get flat rate)

### Director (director_partner_id)

When you select a director:
- Uses **Exclusive SM** commission rate (2% default)
- Or **Exclusive RM** rate if employee is type RM
- Doesn't vary by lead type (directors get flat rate)

---

## 🎯 Real-World Examples

### Example 1: Personal Referral Deal

**Scenario:**
- Customer came through agent's personal referral
- Source: "Personal Referral"
- Deal Amount: $100,000

**Sales Order Setup:**
- Agent 1: John Doe (Primary Agent in HR)
- Agent 2: Jane Smith (Secondary Agent in HR)
- Manager: Mike Manager (Exclusive RM in HR)

**Auto-Populated Rates:**
```
Agent 1 (John):   60% → $60,000 commission
Agent 2 (Jane):   60% → $60,000 commission
Manager (Mike):    5% → $5,000 commission
Total: 125% commission pool
```

### Example 2: Business Lead (Google Ads)

**Scenario:**
- Customer came through Google Ads
- Source: "Google Ads Campaign"
- Deal Amount: $100,000

**Sales Order Setup:**
- Agent 1: John Doe (Primary Agent in HR)
- Agent 2: Jane Smith (Secondary Agent in HR)
- Manager: Mike Manager (Exclusive RM in HR)

**Auto-Populated Rates:**
```
Agent 1 (John):   40% → $40,000 commission
Agent 2 (Jane):   40% → $40,000 commission
Manager (Mike):    5% → $5,000 commission
Total: 85% commission pool
```

---

## 🔧 Technical Implementation

### Files Modified

**commission_ax/models/sale_order.py:**
- Added `_onchange_agent1_partner()` method
- Added `_onchange_agent2_partner()` method
- Added `_onchange_manager_partner()` method
- Added `_onchange_director_partner()` method
- Enhanced existing `_onchange_*_commission()` methods to re-trigger when source changes

### Key Code Changes

```python
@api.onchange('agent1_partner_id')
def _onchange_agent1_partner(self):
    """Auto-populate agent1 commission rate from HR employee profile"""
    if self.agent1_partner_id:
        # Find linked employee
        employee = self.env['hr.employee'].search([
            ('user_id.partner_id', '=', self.agent1_partner_id.id)
        ], limit=1)
        
        if employee and employee.is_agent:
            # Determine lead type
            is_personal_lead = False
            if self.source_id:
                source_name = self.source_id.name.lower()
                is_personal_lead = 'personal' in source_name or 'referral' in source_name
            
            # Set rate based on agent type and lead type
            if employee.agent_type == 'primary':
                if is_personal_lead:
                    self.agent1_rate = employee.primary_agent_personal_commission
                else:
                    self.agent1_rate = employee.primary_agent_business_commission
```

---

## 🔗 Integration Dependencies

### HR Module (hr_uae) Provides:

**Employee Fields:**
- `is_agent` - Boolean flag
- `agent_type` - Selection (primary, secondary, exclusive_rm, exclusive_sm)
- `primary_agent_personal_commission` - Float (default 60%)
- `primary_agent_business_commission` - Float (default 40%)
- `secondary_agent_personal_commission` - Float (default 60%)
- `secondary_agent_business_commission` - Float (default 40%)
- `exclusive_rm_commission` - Float (default 5%)
- `exclusive_sm_commission` - Float (default 2%)

### Commission Module (commission_ax) Uses:

**Sales Order Fields:**
- `source_id` - Marketing source (utm.source model)
- `agent1_partner_id` - Agent 1 partner
- `agent1_rate` - Agent 1 commission %
- `agent2_partner_id` - Agent 2 partner
- `agent2_rate` - Agent 2 commission %
- `manager_partner_id` - Manager partner
- `manager_rate` - Manager commission %
- `director_partner_id` - Director partner
- `director_rate` - Director commission %

---

## 📝 User Workflow

### Step-by-Step: Creating a Sales Order with Auto-Commission

1. **Create New Sales Order**
   - Go to Sales → Orders → Create

2. **Select Customer & Products**
   - Add customer
   - Add order lines

3. **Set Marketing Source** (Important!)
   - Go to "Other Info" tab
   - Set "Source" field (e.g., "Personal Referral" or "Google Ads")
   - This determines Personal vs Business lead

4. **Add Commission Tab**
   - Go to "Commission Management" tab

5. **Select Agent 1**
   - Choose employee from dropdown
   - **Rate auto-fills based on HR profile + lead type** ✅
   - Amount auto-calculates ✅

6. **Select Agent 2** (if applicable)
   - Choose employee
   - **Rate auto-fills** ✅
   - Amount auto-calculates ✅

7. **Select Manager** (if applicable)
   - Choose manager
   - **Rate auto-fills (5% default for RM)** ✅
   - Amount auto-calculates ✅

8. **Select Director** (if applicable)
   - Choose director
   - **Rate auto-fills (2% default for SM)** ✅
   - Amount auto-calculates ✅

9. **Confirm Order**
   - All commissions already calculated!

---

## 🎨 Smart Features

### Dynamic Rate Updates

If you **change the source** after selecting agents, the rates **automatically recalculate**!

**Example:**
```
1. Select Agent 1: John Doe
2. Source is blank → Defaults to Business (40%)
3. Change Source to "Personal Referral"
4. Rate automatically updates to 60% ✅
```

### Fallback Logic

If employee is not found or not flagged as agent:
- System doesn't auto-fill rate
- You can still manually enter commission rate
- Backward compatible with non-HR agents

### Employee-Partner Linking

System checks TWO ways to link partners to employees:
1. **User Partner:** `employee.user_id.partner_id`
2. **Home Address:** `employee.address_home_id`

This ensures maximum compatibility.

---

## 🧪 Testing Checklist

### Test Case 1: Primary Agent Personal Lead
- [ ] Create employee: is_agent=True, agent_type='primary'
- [ ] Set personal commission to 60%
- [ ] Create sales order with source="Personal Referral"
- [ ] Select employee as Agent 1
- [ ] **Verify:** agent1_rate = 60%

### Test Case 2: Primary Agent Business Lead
- [ ] Same employee from Test 1
- [ ] Create sales order with source="Google Ads"
- [ ] Select employee as Agent 1
- [ ] **Verify:** agent1_rate = 40%

### Test Case 3: Secondary Agent
- [ ] Create employee: agent_type='secondary'
- [ ] Set personal=60%, business=40%
- [ ] Test with both lead types
- [ ] **Verify:** Rates match HR settings

### Test Case 4: Manager (Exclusive RM)
- [ ] Create employee: agent_type='exclusive_rm', commission=5%
- [ ] Select as Manager
- [ ] **Verify:** manager_rate = 5% (regardless of lead type)

### Test Case 5: Source Change
- [ ] Create order with business lead, select agent
- [ ] **Verify:** 40% rate
- [ ] Change source to "Personal Referral"
- [ ] **Verify:** Rate auto-updates to 60%

### Test Case 6: Non-Agent Partner
- [ ] Select regular partner (not employee or is_agent=False)
- [ ] **Verify:** Rate field stays empty, manual entry works

---

## 🚀 Benefits

### Before Integration ❌
- Manual rate entry for every deal
- Inconsistent commission rates
- Errors and disputes
- No differentiation between lead types
- Rates not tied to employee records

### After Integration ✅
- **Automatic rate population**
- **Consistent with HR policy**
- **Lead-type aware** (Personal 60%, Business 40%)
- **Real-time updates** when source changes
- **Audit trail** through HR records
- **Reduced errors**
- **Faster order processing**

---

## 📋 Configuration Requirements

### HR Module Setup (hr_uae)

For each agent employee, configure:

1. **Go to:** HR → Employees → [Employee]

2. **Agent Settings Tab:**
   - ✅ Check "Is Agent"
   - Select "Agent Type" (Primary/Secondary/Exclusive RM/SM)

3. **Commission Rates:**
   ```
   Primary Agent Commission: 55%
   Primary Agent Business Commission: 40%
   Primary Agent Personal Commission: 60%
   
   Secondary Agent Commission: 45%
   Secondary Agent Business Commission: 40%
   Secondary Agent Personal Commission: 60%
   
   Exclusive RM Commission: 5%
   Exclusive SM Commission: 2%
   ```

4. **Save**

### Sales Module Setup (commission_ax)

1. **Ensure source_id field exists:**
   - Usually from website/utm module
   - Field: `utm_source_id` → related to `source_id`

2. **Configure UTM Sources:**
   - Go to: Website → Configuration → UTM Sources
   - Add sources with clear names:
     - "Personal Referral"
     - "Personal Network"
     - "Google Ads"
     - "Website"
     - "Walk-in"

---

## 🐛 Troubleshooting

### Rate Not Auto-Populating

**Check:**
1. Is partner linked to employee? (Check user_id or address_home_id)
2. Is employee flagged as agent? (is_agent = True)
3. Are commission fields filled in HR? (Not 0.0)
4. Is source_id set on sales order?

**Debug SQL:**
```sql
-- Check partner → employee link
SELECT e.name, e.is_agent, e.agent_type, p.name as partner_name
FROM hr_employee e
LEFT JOIN res_users u ON e.user_id = u.id
LEFT JOIN res_partner p ON u.partner_id = p.id
WHERE e.is_agent = true;
```

### Rate Updates But Amount Doesn't Calculate

**Check:**
1. Commission type = "Percentage"
2. Calculation base is set
3. Order amount > 0
4. Commission amount field is not manually filled (should auto-calculate)

### Wrong Rate Being Applied

**Check:**
1. Employee agent_type matches expected (Primary vs Secondary)
2. Lead source is correctly identified
3. Check source_id.name for keywords "personal" or "referral"
4. HR commission fields have correct values

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Commission approval workflow
- [ ] Historical rate tracking
- [ ] Commission payment integration
- [ ] Multi-tier commission structures
- [ ] Commission clawback on cancellation
- [ ] Commission vs actual payment reconciliation
- [ ] Agent performance dashboard
- [ ] Commission budget tracking

---

## 📞 Support

If you encounter issues:
1. Check this guide
2. Verify HR employee configuration
3. Check source_id field on sales orders
4. Review employee → partner linking

---

**Integration Status:** ✅ **COMPLETE & READY FOR TESTING**  
**Modules:** commission_ax v17.0.3.2.2 + hr_uae v1.0  
**Last Updated:** January 22, 2026
