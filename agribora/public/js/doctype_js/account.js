frappe.ui.form.on('Account', {
refresh: function(frm){
		set_hub_manager_filter(frm);
	}
});
function set_hub_manager_filter(frm){
frappe.call({
		method: "agribora.agribora.doctype.hub_manager.hub_manager.get_assigned_hub_manager",
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