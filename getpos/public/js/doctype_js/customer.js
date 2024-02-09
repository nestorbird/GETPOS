frappe.ui.form.on("Customer", {
	ward: function(frm){
		if(frm.doc.ward){
			frappe.call({
				method: 'nbpos.nbpos.doctype.hub_manager.hub_manager.get_hub_manager',
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