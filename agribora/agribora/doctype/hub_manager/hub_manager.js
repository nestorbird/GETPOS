// Copyright (c) 2021, www.nestorbird.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hub Manager', {
	refresh: function(frm){
		frappe.call({
			method: "agribora.agribora.doctype.ward.ward.get_unassigned_ward",
			callback: (r)=> {
				console.log(r.message);
				frm.set_query('wards', () => {
					return {
						filters: {
							ward: ['not in', r.message]
						}
					}
				});
			}
		});
	}
});
