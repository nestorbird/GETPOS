frappe.ui.form.on('Account', {
refresh: function(frm) {

  	frm.fields_dict['hub_manager'].get_query = function(doc) {
			return {
				filters: {
					"account": "",
				}
			}
		}

}
});