-- Find user type category (searching in JSONB)
SELECT id, name FROM ir_module_category 
WHERE name->>'en_US' LIKE '%User%type%' 
   OR name->>'en_US' LIKE '%type%'
ORDER BY id;

-- Find all groups with their categories
SELECT g.id, g.name->>'en_US' as group_name, g.category_id, c.name->>'en_US' as category_name
FROM res_groups g
LEFT JOIN ir_module_category c ON g.category_id = c.id
WHERE g.name->>'en_US' LIKE '%User%' 
   OR g.name->>'en_US' LIKE '%Portal%' 
   OR g.name->>'en_US' LIKE '%Public%'
ORDER BY g.id;

-- Find users with multiple user type groups
-- First, let's identify the user type groups manually
-- Typical IDs: Internal User, Portal, Public

SELECT u.id, u.login, array_agg(g.name->>'en_US' ORDER BY g.name->>'en_US') as groups, array_agg(r.gid) as group_ids
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON r.gid = g.id
WHERE r.gid IN (
    SELECT g2.id FROM res_groups g2
    JOIN ir_module_category c ON g2.category_id = c.id
    WHERE c.name->>'en_US' = 'User types'
)
GROUP BY u.id, u.login
HAVING COUNT(DISTINCT r.gid) > 1;
