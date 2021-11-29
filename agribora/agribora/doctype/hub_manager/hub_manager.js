// Copyright (c) 2021, www.nestorbird.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hub Manager', {
	refresh: function(frm){
		set_ward_filter(frm);
		get_hub_manager_list(frm);
		frm.get_field("wards").grid.df.cannot_delete_rows = true;
	}
});

function set_ward_filter(frm){
	frappe.call({
		method: "agribora.agribora.doctype.ward.ward.get_assigned_ward",
		callback: (r)=> {
			frm.set_query('wards', () => {
				return {
					filters: {
						name: ['not in', r.message]
					}
				}
			});
		}
	});
}
function get_hub_manager_list(frm){
	frappe.call({
		method: "agribora.agribora.doctype.hub_manager.hub_manager.get_hub_manager_list",
		callback: (r)=> {
			frm.set_query('hub_manager', () => {
				return {
					filters: {
						name: ['not in', r.message]
					}
				}
			});
		}
	});
}
