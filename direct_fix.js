/**
 * Direct fix for osusproperties user type conflicts
 * Uses the Odoo MCP client directly
 */

import { OdooClient } from './dist/odoo-client.js';

const config = {
    url: 'https://erposus.com',
    db: 'osusproperties',
    username: 'salescompliance@osusproperties.com',
    password: '8586583'
};

async function main() {
    console.log('='.repeat(80));
    console.log('OSUSPROPERTIES USER TYPE FIX');
    console.log('='.repeat(80));
    
    const client = new OdooClient(config);
    
    // Step 1: Authenticate
    console.log('\n[1/6] Authenticating...');
    const authResult = await client.authenticate();
    
    if (!authResult.success) {
        console.error('✗ Authentication failed:', authResult.error?.message);
        process.exit(1);
    }
    
    console.log(`✓ Authenticated (Server: ${authResult.data?.serverVersion})`);
    
    // Step 2: Get user type category
    console.log('\n[2/6] Finding user type category...');
    let categoryResult = await client.searchRead({
        model: 'ir.module.category',
        domain: [['name', '=', 'User types']],
        fields: ['id', 'name']
    });
    
    // Try alternative search if first attempt fails
    if (!categoryResult.success || !categoryResult.data || categoryResult.data.length === 0) {
        console.log('  Trying alternative category search...');
        categoryResult = await client.searchRead({
            model: 'ir.module.category',
            domain: [['name', 'ilike', 'user']],
            fields: ['id', 'name']
        });
    }
    
    if (!categoryResult.success || !categoryResult.data || categoryResult.data.length === 0) {
        console.log('✗ User type category not found, using direct group approach instead');
        
        // Skip category and get groups directly by XML ID
        const directApproach = true;
        var categoryId = null;
    } else {
        const categoryId = categoryResult.data[0].id;
        console.log(`✓ Found category (ID: ${categoryId}): ${categoryResult.data[0].name}`);
        var directApproach = false;
    }
    
    // Step 3: Get all user type groups
    console.log('\n[3/6] Getting user type groups...');
    
    let userTypeGroups;
    let userTypeGroupIds;
    
    if (directApproach) {
        // Get groups directly by XML ID
        console.log('  Using direct XML ID approach...');
        const groupXmlIds = ['base.group_user', 'base.group_portal', 'base.group_public'];
        userTypeGroups = [];
        
        for (const xmlId of groupXmlIds) {
            const parts = xmlId.split('.');
            const xmlIdResult = await client.searchRead({
                model: 'ir.model.data',
                domain: [['&'], ['module', '=', parts[0]], ['name', '=', parts[1]]],
                fields: ['res_id', 'model']
            });
            
            if (xmlIdResult.success && xmlIdResult.data && xmlIdResult.data.length > 0) {
                const record = xmlIdResult.data.find(r => r.model === 'res.groups');
                if (record) {
                    const groupId = record.res_id;
                    const groupResult = await client.read({
                        model: 'res.groups',
                        ids: [groupId],
                        fields: ['id', 'name']
                    });
                    
                    if (groupResult.success && groupResult.data && groupResult.data.length > 0) {
                        userTypeGroups.push(groupResult.data[0]);
                    }
                }
            }
        }
    } else {
        const groupsResult = await client.searchRead({
            model: 'res.groups',
            domain: [['category_id', '=', categoryId]],
            fields: ['id', 'name']
        });
        
        if (!groupsResult.success) {
            console.error('✗ Failed to get groups:', groupsResult.error?.message);
            process.exit(1);
        }
        
        userTypeGroups = groupsResult.data;
    }
    
    console.log(`✓ Found ${userTypeGroups.length} user type groups:`);
    userTypeGroups.forEach(g => console.log(`  - ${g.name} (ID: ${g.id})`));
    
    userTypeGroupIds = userTypeGroups.map(g => g.id);
    
    // Step 4: Get XML ID mappings for specific groups
    console.log('\n[4/6] Getting group XML ID mappings...');
    
    const xmlIdMappings = {};
    const groupNames = ['group_user', 'group_portal', 'group_public'];
    
    for (const groupName of groupNames) {
        const xmlIdResult = await client.searchRead({
            model: 'ir.model.data',
            domain: [['module', '=', 'base'], ['name', '=', groupName], ['model', '=', 'res.groups']],
            fields: ['res_id', 'name']
        });
        
        if (xmlIdResult.success && xmlIdResult.data && xmlIdResult.data.length > 0) {
            xmlIdMappings[groupName] = xmlIdResult.data[0].res_id;
            console.log(`  ✓ ${groupName}: ${xmlIdResult.data[0].res_id}`);
        }
    }
    
    const internalGroupId = xmlIdMappings['group_user'];
    const portalGroupId = xmlIdMappings['group_portal'];
    const publicGroupId = xmlIdMappings['group_public'];
    
    // Step 5: Find users with multiple user type groups
    console.log('\n[5/6] Finding users with multiple user types...');
    
    const usersResult = await client.searchRead({
        model: 'res.users',
        domain: [],
        fields: ['id', 'login', 'name', 'groups_id'],
        limit: 1000
    });
    
    if (!usersResult.success) {
        console.error('✗ Failed to get users:', usersResult.error?.message);
        process.exit(1);
    }
    
    const allUsers = usersResult.data;
    console.log(`✓ Checking ${allUsers.length} users...`);
    
    const conflictedUsers = [];
    
    for (const user of allUsers) {
        const userTypeGroupCount = user.groups_id.filter(gid => userTypeGroupIds.includes(gid)).length;
        
        if (userTypeGroupCount > 1) {
            const userGroups = userTypeGroups.filter(g => user.groups_id.includes(g.id));
            conflictedUsers.push({
                id: user.id,
                login: user.login,
                name: user.name,
                groups: userGroups,
                groups_id: user.groups_id
            });
        }
    }
    
    if (conflictedUsers.length === 0) {
        console.log('\n✓ No users with conflicting user types found!');
        return;
    }
    
    console.log(`\n⚠ Found ${conflictedUsers.length} users with conflicts:`);
    conflictedUsers.forEach(user => {
        console.log(`  - ${user.login} (ID: ${user.id}): ${user.groups.map(g => g.name).join(', ')}`);
    });
    
    // Step 6: Fix conflicted users
    console.log('\n[6/6] Fixing conflicted users...');
    
    let fixedCount = 0;
    
    for (const user of conflictedUsers) {
        const userGroupIds = user.groups.map(g => g.id);
        const groupsToRemove = [];
        let keepType = '';
        
        // If user has internal group, remove portal and public
        if (internalGroupId && userGroupIds.includes(internalGroupId)) {
            if (portalGroupId && userGroupIds.includes(portalGroupId)) {
                groupsToRemove.push(portalGroupId);
            }
            if (publicGroupId && userGroupIds.includes(publicGroupId)) {
                groupsToRemove.push(publicGroupId);
            }
            keepType = 'Internal User';
        }
        // If user has portal, remove public and internal
        else if (portalGroupId && userGroupIds.includes(portalGroupId)) {
            if (publicGroupId && userGroupIds.includes(publicGroupId)) {
                groupsToRemove.push(publicGroupId);
            }
            if (internalGroupId && userGroupIds.includes(internalGroupId)) {
                groupsToRemove.push(internalGroupId);
            }
            keepType = 'Portal';
        }
        
        if (groupsToRemove.length > 0) {
            console.log(`\n  Fixing: ${user.login}`);
            console.log(`    Keep: ${keepType}`);
            console.log(`    Remove: ${groupsToRemove.map(id => {
                const g = userTypeGroups.find(ug => ug.id === id);
                return g ? g.name : id;
            }).join(', ')}`);
            
            // Build the update command
            const updateValues = {
                groups_id: groupsToRemove.map(gid => [3, gid])  // 3 = unlink
            };
            
            const updateResult = await client.update({
                model: 'res.users',
                ids: [user.id],
                values: updateValues
            });
            
            if (updateResult.success) {
                console.log(`    ✓ Fixed`);
                fixedCount++;
            } else {
                console.log(`    ✗ Failed: ${updateResult.error?.message}`);
            }
        }
    }
    
    console.log(`\n✓ Fixed ${fixedCount}/${conflictedUsers.length} users`);
    
    console.log('\n' + '='.repeat(80));
    console.log('FIX COMPLETED!');
    console.log('='.repeat(80));
    console.log('\nNext steps:');
    console.log('1. Restart Odoo service: sudo systemctl restart odoo-osusproperties');
    console.log('2. Monitor logs: sudo tail -f /var/odoo/osusproperties/logs/odoo-server.log');
    console.log('3. Verify registry loads without "user type" errors');
}

main().catch(error => {
    console.error('\n✗ Unexpected error:', error);
    process.exit(1);
});
