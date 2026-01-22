-- Step 1: Find user type category
SELECT id, name FROM ir_module_category WHERE name = 'User types';

-- Step 2: Find user type groups (assuming category_id = 14)
SELECT g.id, g.name 
FROM res_groups g
JOIN ir_module_category c ON g.category_id = c.id
WHERE c.name = 'User types';

-- Step 3: Find conflicted users
SELECT u.id, u.login, array_agg(g.name ORDER BY g.name) as groups
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.user_id
JOIN res_groups g ON r.group_id = g.id
JOIN ir_module_category c ON g.category_id = c.id
WHERE c.name = 'User types'
GROUP BY u.id, u.login
HAVING COUNT(DISTINCT r.group_id) > 1;
