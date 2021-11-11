// Copyright (c) 2021, www.nestorbird.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hub Manager', {
	refresh: function(frm){
		set_ward_filter(frm);
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
