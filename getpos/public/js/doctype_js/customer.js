frappe.ui.form.on("Customer", {
	ward: function(frm){
		if(frm.doc.ward){
			frappe.call({
				method: 'getpos.getpos.doctype.hub_manager.hub_manager.get_hub_manager',
				args: {
					"ward": frm.doc.ward
				},
				callback: function(r) {
					frm.set_value("hub_manager", r.message);
				}
			});
		}
	}
});