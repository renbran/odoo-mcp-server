-- Check module states
SELECT name, state FROM ir_module_module 
WHERE state IN ('to install', 'to upgrade', 'to remove')
ORDER BY name;

-- Check for any group assignment issues during the purchase module load
SELECT g.id, g.name->>'en_US' as group_name, g.category_id
FROM res_groups g
WHERE g.id IN (
    SELECT DISTINCT gid FROM res_groups_users_rel
    WHERE gid IN (1, 10, 11)  -- Internal, Portal, Public
)
ORDER BY g.id;

-- Check which users have Internal User group
SELECT u.id, u.login 
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
WHERE r.gid = 1
ORDER BY u.id
LIMIT 20;

-- Check which users have Portal group
SELECT u.id, u.login 
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
WHERE r.gid = 10
ORDER BY u.id
LIMIT 20;
