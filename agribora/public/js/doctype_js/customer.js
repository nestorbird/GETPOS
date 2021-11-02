frappe.ui.form.on("Customer", {
ward: function(frm){
  		frappe.call({
				method: 'agribora.agribora.doctype.hub_manager.hub_manager.get_hub_manager',
				args: {
					"ward": frm.doc.ward
				},
				callback: function(r) {
				    console.log(r)
					frm.set_value("hub_manager", r.message);
				}
			});
}

});