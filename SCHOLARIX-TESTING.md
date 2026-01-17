# 🚀 Scholarix v2 Odoo Module - Testing Guide

## Connected MCP Server: `odoo-scholarix`

Your Odoo MCP Server is now connected to Claude Desktop and linked to **Scholarix Global's Odoo instance** (scholarixv2 database).

---

## 📋 Test Scenarios

### 1️⃣ **Verify Connection & Available Tools**

**In Claude, ask:**

```
What Odoo tools do you have available? List them all.
```

**Expected Response:** Should list 11 tools:
- odoo_search
- odoo_search_read
- odoo_read
- odoo_create
- odoo_update
- odoo_delete
- odoo_execute
- odoo_count
- odoo_workflow_action
- odoo_generate_report
- odoo_get_model_metadata

---

### 2️⃣ **Explore Scholarix Database Structure**

**Ask Claude:**

```
What models are available in the Scholarix v2 Odoo instance?
Show me the schema/structure of the database.
```

**Then ask about specific modules:**

```
What fields are available in the res.partner model?
```

---

### 3️⃣ **Search & List Records**

**Search for partners:**

```
Search for all partners (customers) in the Scholarix database.
How many partners are there?
```

**Search for students (if custom module exists):**

```
Search for all students in the database. What information is available?
```

**Count records:**

```
How many sale orders are in the database?
Count the total number of invoice records.
```

---

### 4️⃣ **Get Model Information**

**Explore model fields:**

```
Show me all available fields on the sale.order model in Scholarix.
```

```
What fields are available on the account.move (invoice) model?
```

```
List all fields in the res.partner model.
```

---

### 5️⃣ **Read Specific Records**

**After finding some records:**

```
Get the details of the first 5 partners in the database.
```

```
Show me the full details of invoice ID 1 from the Scholarix database.
```

---

### 6️⃣ **Create Test Data** (Optional)

```
Create a new test partner named "Test Scholar Company" with email "test@scholarix.ai"
```

```
Create a test customer contact with:
- Name: Test Student
- Email: student@test.com
- Phone: 1234567890
```

---

### 7️⃣ **Update Records**

```
Update the partner "Test Scholar Company" to add phone number "555-1234"
```

---

### 8️⃣ **Module-Specific Queries** (if applicable)

```
Search for all scholarship records in the scholarixv2 module.
```

```
What custom fields does the student module have?
```

```
Show me all enrollment records.
```

---

## 🎯 Common Scholarix Models to Explore

Based on a typical Scholarix implementation, these models might exist:

| Model | Description |
| --- | --- |
| `res.partner` | Contacts/Organizations |
| `student.profile` | Student records (if custom) |
| `scholarship.application` | Scholarship applications |
| `enrollment.record` | Student enrollments |
| `academic.program` | Programs/Courses |
| `student.payment` | Payment records |
| `student.documents` | Document submissions |
| `res.users` | Users/Staff |

**Try searching these:**

```
Search for all student.profile records.
Count scholarship.application records.
```

---

## 🔧 Power User Commands

### Create a complete student record:

```
Create a new student with:
- Student Name: John Scholar
- Email: john@scholarix.ai
- Phone: +1-555-0123
- Enrollment Status: Active
- Program: Computer Science
```

### Search with filters:

```
Search for all students with status "Active" in the Scholarix database.
```

```
Find all scholarship applications that are "Pending".
```

### Generate reports:

```
Generate a PDF report of all current enrollments.
```

---

## 📊 Example Domain Filters

**To understand filtering, these are the patterns:**

```
# Find students named "Ahmed"
[["name", "=", "Ahmed"]]

# Find active students
[["status", "=", "active"]]

# Find students with pending documents
[["status", "!=", "completed"]]

# Find students from specific program
[["program_id", "=", "Computer Science"]]

# Complex: Active students in CS program
["&", ["status", "=", "active"], ["program_id", "=", "Computer Science"]]
```

---

## ✅ Checklist

- [ ] Claude Desktop is open
- [ ] 🔌 Shows "odoo-scholarix" server connected (check the icon)
- [ ] Asked Claude "What tools do you have?" (should list 11)
- [ ] Successfully searched for records
- [ ] Retrieved model information
- [ ] Explored Scholarix database structure

---

## 🚨 If Something Doesn't Work

### Claude doesn't show the server:

1. Fully close Claude Desktop (right-click taskbar → Quit)
2. Wait 3 seconds
3. Reopen Claude Desktop
4. Check the 🔌 icon for "odoo-scholarix" connection

### "Unknown instance" error:

- Make sure you're using "odoo-scholarix" as the instance name
- Or ask: "Search for records in the odoo-scholarix instance"

### Connection timeout:

- Check if Odoo server is reachable: `https://erp.sgctech.ai`
- Verify credentials are correct in `.env` file

### Authentication failed:

- Double-check credentials:
  - URL: `https://erp.sgctech.ai`
  - DB: `scholarixv2`
  - Username: `info@scholarixglobal.com`
  - Password: Verify it's correct

---

## 💡 Pro Tips

### Ask Claude to be specific:

```
In the Scholarix v2 database (instance: odoo-scholarix), 
search for all students where enrollment status equals "active".
```

### Ask for structured data:

```
Give me a summary of:
- Total number of students
- Total number of active enrollments
- Average applications per program
```

### Combine operations:

```
Find all students, then for each student, show me:
- Their enrollment status
- Current program
- Outstanding payments
```

---

## 🎓 Next Steps

Once you verify the connection works:

1. **Explore the Scholarix database structure** - Understand what models exist
2. **Create a data analysis prompt** - "Give me a dashboard of key metrics"
3. **Build automation** - Ask Claude to help with bulk operations
4. **Generate reports** - Export data to PDFs or summaries

---

**Ready? Open Claude and ask:**

```
What Odoo tools do you have available?
```

**If you see them listed - you're connected! 🎉**

Let me know what models you find in the Scholarix database!
