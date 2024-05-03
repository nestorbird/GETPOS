// Copyright (c) 2023, swapnil and contributors
// For license information, please see license.txt

frappe.ui.form.on('Theme Settings', {
	refresh: function(frm) {
		frm.set_value({
			dine_in: 'dinein@yopmail.com',
			take_away: 'takeaway@yopmail.com'
		})

	}
});
