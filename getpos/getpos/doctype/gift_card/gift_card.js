// Copyright (c) 2024, Nestorbird and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Gift Card", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Gift Card", {
    gift_card_name: function (frm) {
		if (frm.doc.__islocal === 1) {
			frm.trigger("make_code");
		}
	},
	make_code: function (frm) {
		frm.doc.code = Math.random().toString(12).substring(2, 12).toUpperCase();
		frm.refresh_field("code");
	}
 });
