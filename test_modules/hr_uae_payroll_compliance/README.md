# HR UAE Payroll Compliance Module

## Overview
Complete UAE Labor Law compliant payroll system with WPS (Wages Protection System) integration for Odoo 17.

**Module Version:** 17.0.1.0.0  
**Category:** Human Resources  
**Author:** SGC TECH AI  
**License:** LGPL-3

## Features

### ✅ Phase 1: Employee Master Data & UAE Compliance (COMPLETE)

#### Employee Extensions (hr.employee)
- **WPS Compliance Fields**
  - MOHRE Person ID (14 digits, validated)
  - Bank Routing Code (9 digits)
  - WPS Agent ID
  - Payment Method (Bank/Exchange)
  - IBAN Number (UAE format: AE + 21 digits)
  - WPS Ready status (computed)

- **Emirates ID Tracking**
  - Emirates ID (15 digits, starts with 784)
  - Expiry date tracking
  - Auto-status: Valid/Expiring/Expired
  - Days to expiry counter
  - Expiry warnings

- **Visa & Immigration**
  - Visa number and expiry
  - Passport expiry tracking
  - Labor card number and expiry
  - Status indicators for all documents

- **GPSSA (UAE Nationals)**
  - UAE National flag
  - GPSSA registration status
  - GPSSA number
  - Auto-validation for nationals

- **Compliance Scoring**
  - Automated compliance score (0-100%)
  - Tracks completion of required fields
  - Visual compliance indicators
  - Real-time status updates

#### Contract Extensions (hr.contract)
- **UAE Salary Structure**
  - Basic Salary (validated ≥ 50% of total)
  - Housing Allowance
  - Transport Allowance
  - Other Allowances
  - Total Salary (computed)
  - Basic Salary % (computed)

- **WPS Validation**
  - Enforces 50% basic salary requirement
  - Real-time compliance checking
  - Warning messages on violations
  - Visual compliance badges

- **UAE Contract Types**
  - Unlimited Contract (standard)
  - Limited Contract (max 3 years)
  - End date validation for limited contracts
  - Duration compliance checks

- **Working Hours**
  - Daily hours (max 8)
  - Weekly hours (max 48)
  - UAE Labor Law validation

- **Gratuity Calculations**
  - Gratuity base = Basic Salary only
  - Daily wage calculation
  - Formula: (Basic / 30) × Service Days
  - Automatic computation

- **GPSSA Contributions (UAE Nationals)**
  - Pensionable salary = Basic + Housing + Transport
  - Employee contribution: 5%
  - Employer contribution: 12.5%
  - Auto-calculated based on registration

- **Overtime Rates**
  - Hourly rate: Basic / 240
  - Regular OT: 125% of hourly
  - Premium OT: 150% of hourly
  - Helper methods for calculations

## Installation

### Prerequisites
- Odoo 17.0
- Modules: `hr`, `hr_contract`, `hr_uae`

### Method 1: Docker Installation (Recommended for Testing)

```bash
# 1. Copy module to Docker container
docker cp test_modules/hr_uae_payroll_compliance odoo17:/mnt/extra-addons/

# 2. Restart Odoo container
docker restart odoo17

# 3. Update Apps List (via UI or API)
# 4. Install "HR UAE Payroll Compliance" module
```

### Method 2: Manual Installation

```bash
# 1. Copy module to addons directory
cp -r hr_uae_payroll_compliance /path/to/odoo/addons/

# 2. Update module list
./odoo-bin -c odoo.conf -u all --stop-after-init

# 3. Restart Odoo
./odoo-bin -c odoo.conf

# 4. Install via Apps menu
```

### Method 3: Python Script Installation

```python
import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo17_test'
username = 'admin'
password = 'admin'

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

# Install module
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [[module_id]])
```

## Usage Guide

### Employee Setup

1. **Navigate to**: HR → Employees → [Select Employee]
2. **Go to tab**: "UAE Compliance"
3. **Fill WPS Section**:
   - MOHRE Person ID (14 digits)
   - Payment Method (Bank Transfer recommended)
   - IBAN Number (if bank transfer)
   - Bank Routing Code
   - WPS Agent ID

4. **Fill Emirates ID**:
   - Emirates ID (15 digits, starts 784)
   - Expiry Date
   - System auto-validates and tracks expiry

5. **Fill Visa & Immigration**:
   - Visa number and expiry
   - Passport expiry
   - Labor card details

6. **UAE Nationals Only**:
   - Check "Is UAE National"
   - Check "GPSSA Registered"
   - Enter GPSSA Number

7. **Monitor Compliance**:
   - Check compliance score (target: ≥ 80%)
   - View "WPS Ready" badge in header
   - Use filters to track expiring documents

### Contract Setup

1. **Navigate to**: HR → Contracts → [Select Contract]
2. **Fill UAE Salary Structure**:
   - Basic Salary: Enter amount
   - Housing Allowance: Typically 25-50% of basic
   - Transport Allowance: Typically 10-20% of basic
   - Other Allowances: Food, phone, etc.

3. **System Auto-Validates**:
   - ✓ Basic salary ≥ 50% of total (WPS requirement)
   - ✓ All amounts positive
   - ✓ Total salary computed automatically
   - ✓ WPS compliant badge shown

4. **Set Contract Type**:
   - Unlimited (standard, most common)
   - Limited (requires end date, max 3 years)

5. **Set Working Hours**:
   - Daily: 8 hours (UAE standard)
   - Weekly: 48 hours (UAE standard)

6. **Go to tab**: "UAE Contract Details"
   - View gratuity calculations
   - View GPSSA contributions (if applicable)
   - View overtime rates
   - Check compliance status

## Validation Rules

### Employee Validations
- ✓ MOHRE Person ID: Exactly 14 digits
- ✓ Emirates ID: Exactly 15 digits, starts with "784"
- ✓ IBAN: Format "AE" + 21 digits
- ✓ Bank Routing Code: Exactly 9 digits
- ✓ GPSSA Number: Required if registered and UAE national

### Contract Validations
- ✓ Basic Salary: Must be > 0
- ✓ Basic Salary %: Must be ≥ 50% of total (WPS)
- ✓ All allowances: Cannot be negative
- ✓ Limited contracts: Must have end date, max 3 years
- ✓ Working hours: ≤ 8 hours/day, ≤ 48 hours/week

## Compliance Monitoring

### Employee Filters
- WPS Ready / Incomplete
- Emirates ID: Expiring / Expired
- Visa: Expiring / Expired
- Labor Card: Expiring / Expired
- Compliance Score: Low (<50%) / Medium (50-80%) / High (≥80%)
- UAE Nationals
- GPSSA Registered

### Contract Filters
- WPS Compliant / Non-Compliant
- Unlimited / Limited Contracts
- Fully Compliant / Requires Attention

### Group By Options
- WPS Status
- Emirates ID Status
- Visa Status
- Contract Type

## Computed Fields Reference

### Employee
| Field | Computation | Purpose |
|-------|------------|---------|
| `x_wps_ready` | Checks all WPS fields complete | WPS file generation readiness |
| `x_compliance_score` | % of required fields filled | Overall compliance tracking |
| `x_emirates_id_status` | Days to expiry | Document expiry management |
| `x_visa_status` | Days to expiry | Immigration tracking |
| `x_labor_card_status` | Days to expiry | Work permit tracking |
| `x_days_to_*_expiry` | Date difference | Renewal planning |

### Contract
| Field | Computation | Purpose |
|-------|------------|---------|
| `x_total_salary` | Sum of all components | Total wage calculation |
| `x_basic_salary_percentage` | Basic / Total × 100 | WPS compliance check |
| `x_wps_compliant` | Basic % ≥ 50 | WPS validation |
| `x_contract_compliant` | All checks pass | Overall compliance |
| `x_gratuity_base_salary` | = Basic Salary | EOSB calculation |
| `x_gpssa_base_salary` | Basic + Housing + Transport | Pension calculation |
| `x_gpssa_employee_contribution` | GPSSA Base × 5% | Employee deduction |
| `x_gpssa_employer_contribution` | GPSSA Base × 12.5% | Employer cost |

## UAE Labor Law Compliance

### Salary Structure (WPS)
✅ **Article 51**: Wage breakdown required  
✅ **WPS Specification**: Basic ≥ 50% of total  
✅ **Payment Method**: Bank transfer or approved exchange  
✅ **MOHRE Registration**: Person ID mandatory  

### Contract Types
✅ **Article 56**: Unlimited vs Limited contracts  
✅ **Article 57**: Limited contracts max 3 years  
✅ **Article 58**: Renewal by mutual agreement  

### Working Hours
✅ **Article 65**: 8 hours/day, 48 hours/week  
✅ **Article 66**: Ramadan: 6 hours/day (handled separately)  
✅ **Article 68**: Overtime at 125% (day) or 150% (night/weekend)  

### End-of-Service Gratuity
✅ **Article 132**: Calculation based on basic salary  
✅ **Article 133**: 21 days for years 1-5, 30 days for 5+  
✅ **Formula**: (Basic Salary / 30) × Service Days  

### GPSSA (UAE Nationals)
✅ **Federal Law 7/1999**: Social Insurance  
✅ **Employee**: 5% of pensionable salary  
✅ **Employer**: 12.5% of pensionable salary  
✅ **Pensionable**: Basic + Housing + Transport  

## Data Structure

### Employee Fields (x_*)
```python
x_mohre_person_id = Char(14)          # WPS required
x_bank_routing_code = Char(9)         # Bank identifier
x_wps_agent_id = Char()               # WPS agent
x_payment_method = Selection()        # bank/exchange
x_iban_number = Char(AE+21)           # IBAN format
x_emirates_id = Char(15)              # 784XXXXXXXXXX
x_emirates_id_expiry = Date()         # Renewal tracking
x_visa_number = Char()                # Visa details
x_visa_expiry = Date()                # Visa renewal
x_passport_expiry = Date()            # Passport validity
x_labor_card_number = Char()          # Work permit
x_labor_card_expiry = Date()          # Renewal date
x_is_uae_national = Boolean()         # Nationality flag
x_gpssa_registered = Boolean()        # GPSSA enrollment
x_gpssa_number = Char()               # GPSSA ID
```

### Contract Fields (x_*)
```python
x_basic_salary = Monetary()           # Core wage component
x_housing_allowance = Monetary()      # Housing benefit
x_transport_allowance = Monetary()    # Transport benefit
x_other_allowances = Monetary()       # Other benefits
x_contract_type_uae = Selection()     # unlimited/limited
x_weekly_working_hours = Float()      # Hours/week
x_daily_working_hours = Float()       # Hours/day
```

## API / Helper Methods

### Contract Methods
```python
contract.calculate_daily_wage()       # Total Salary / 30
contract.calculate_hourly_rate()      # Basic / 240
contract.get_overtime_rate('regular') # Hourly × 1.25
contract.get_overtime_rate('premium') # Hourly × 1.50
```

## Troubleshooting

### WPS Non-Compliant Error
**Problem**: "Basic salary must be at least 50% of total salary"  
**Solution**: Increase basic salary OR reduce allowances to meet 50% threshold

### Emirates ID Validation Failed
**Problem**: "Emirates ID must be 15 digits starting with 784"  
**Solution**: Check format: 784-YYYY-NNNNNNN-N (remove dashes, enter digits only)

### Limited Contract Date Error
**Problem**: "Limited contracts must have an end date"  
**Solution**: Set end date in contract form (max 3 years from start)

### GPSSA Number Required
**Problem**: "GPSSA number is required for registered UAE nationals"  
**Solution**: Enter GPSSA number or uncheck "GPSSA Registered"

## Roadmap

### Phase 2: Salary Calculation Engine (Next)
- [ ] Salary rules for UAE components
- [ ] Overtime calculation automation
- [ ] Leave deduction formulas
- [ ] Absence impact calculations
- [ ] Payslip integration

### Phase 3: WPS Integration
- [ ] WPS SIF file generation
- [ ] MOHRE integration
- [ ] Bank file export
- [ ] Payment reconciliation
- [ ] Status tracking

### Phase 4: Employee Self-Service
- [ ] Document upload portal
- [ ] Payslip access
- [ ] Leave requests
- [ ] Document expiry notifications
- [ ] Personal info updates

### Phase 5: Compliance Monitoring
- [ ] Dashboard with KPIs
- [ ] Expiry alerts (30/60/90 days)
- [ ] Compliance reports
- [ ] Audit trail
- [ ] Automated reminders

### Phase 6: Testing & Deployment
- [ ] Unit tests
- [ ] Integration tests
- [ ] User acceptance testing
- [ ] Production deployment
- [ ] Training materials

## Support

For issues or questions:
- Check validation error messages (they include fix instructions)
- Review UAE Labor Law requirements
- Consult MOHRE WPS specifications
- Contact: SGC TECH AI

## License

LGPL-3 - See LICENSE file

## Credits

**Developer**: SGC TECH AI  
**Based on**: Odoo Community HR modules  
**Compliance**: UAE Ministry of Human Resources and Emiratisation (MOHRE)  
**References**:
- UAE Federal Law No. 8 of 1980 (Labor Law)
- UAE Cabinet Resolution No. 52 of 2020 (Implementing Regulations)
- UAE Central Bank WPS Specification
- GPSSA Federal Law No. 7 of 1999

---

**Version**: 1.0.0 (Phase 1 Complete)  
**Release Date**: January 2025  
**Odoo Version**: 17.0+
