-- Check table structures
\d res_groups_users_rel

-- List all categories
SELECT id, name FROM ir_module_category ORDER BY id LIMIT 30;

-- Check for user-related groups
SELECT id, name, category_id FROM res_groups WHERE name LIKE '%User%' OR name LIKE '%Portal%' OR name LIKE '%Public%';
