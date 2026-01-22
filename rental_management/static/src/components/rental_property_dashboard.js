/** @odoo-module **/

import { session } from '@web/session';
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class RentalPropertyDashboard extends Component {
    setup() {
        this.action = useService('action');
        this.rpc = useService('rpc')
        this.state = useState({
            'property_data': {}
        })
        onMounted(async ()=>{
            try {
                const data = await this.rpc('/get/property/data')
                this.state.property_data = data
            } catch (error) {
                console.error('[rental_management] Error fetching property data:', error);
                this.state.property_data = {
                    available_prop_count: 0,
                    on_lease_prop_count: 0,
                    sale_prop_count: 0,
                    booked_prop_count: 0,
                    sold_prop_count: 0,
                    draft_prop_count: 0,
                    total_prop_count: 0,
                }
            }
        })
    }
    viewAllProperties(status){
        let domain, context;
        if (status === 'all') {
           domain = [['stage', '!=', 'draft']]
        } else {
            domain = [['stage', '=', status]]
        }
        context = { 'create': true }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Properties',
            res_model: 'property.details',
            view_mode: 'list',
            views: [[false, 'list'], [false, 'kanban'], [false, 'form']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }
    viewProperties(status, type){
        let domain, context;
        if (status === 'all') {
           domain = [['stage', '!=', 'draft'],['type','=',type]]
        } else {
            domain = [['stage', '=', status],['type','=', type]]
        }
        context = { 'create': true }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Properties',
            res_model: 'property.details',
            view_mode: 'list',
            views: [[false, 'list'], [false, 'kanban'], [false, 'form']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }
}

RentalPropertyDashboard.template = 'rental_management.RentalPropertyDashboard';

// Register the action immediately when module loads
try {
    registry.category("actions").add("property_dashboard", RentalPropertyDashboard);
    console.log('[rental_management] property_dashboard registered successfully');
} catch (error) {
    console.error('[rental_management] Failed to register property_dashboard:', error);
}
