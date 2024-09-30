// Copyright (c) 2023, swapnil and contributors
// For license information, please see license.txt

frappe.ui.form.on('Theme Settings', {
	refresh: function(frm) {
		frappe.db.get_value("Customer", {"customer_name": "Dine In"}, "name")
			.then(doc => {
				frm.set_value({dine_in: doc.message['name']})
			})
		frappe.db.get_value("Customer", {"customer_name": "Take Away"}, "name")
			.then(doc => {
				frm.set_value({take_away: doc.message['name']})
			})
		frappe.db.get_value("Customer", {"customer_name": "Guest Customer"}, "name")
			.then(doc => {
				frm.set_value({guest_customer: doc.message['name']})
			})
		

	}
});
