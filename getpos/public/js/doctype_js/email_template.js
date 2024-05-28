frappe.ui.form.on("Email Template", {
	refresh: function () {
        frm.refresh("custom_default_coupon_code_notification  ")
    },

	validate: function(frm){
        if (frm.doc.custom_default_coupon_code_notification == true ) {
		frappe.call({
			method: "getpos.getpos.hooks.pricing_rule.default_coupon_code_email_template",
			args: {
				doc: cur_frm.doc.name,
			},
				callback: function(r) {
					if(r) {
            	        location.reload(true);
					}
				}
			})
    	}
	},

});