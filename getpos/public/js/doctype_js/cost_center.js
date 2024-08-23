frappe.ui.form.on("Cost Center", {
	after_save: function(frm){
			frappe.call({
				method: 'getpos.getpos.hooks.cost_center.create_warehouse',
				args: {
					"self": frm.doc
				},
				callback: function(r) {
					frm.refresh();
				}
			});
	}
});