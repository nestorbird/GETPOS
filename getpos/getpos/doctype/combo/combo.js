// Copyright (c) 2024, Nestorbird and contributors
// For license information, please see license.txt

frappe.ui.form.on('Combo', {
	refresh(frm) {
		frm.set_query('parent_combo_item', function(doc, cdt, cdn) {
			return {
				"filters": {
					"custom_item": "Combo Item"
				}
			};
		});

			frm.set_query('item', 'combo_item', function(doc, cdt, cdn) {
				var d = locals[cdt][cdn];
				return {
					"filters": {
						"custom_item": "Standard Item"
					}
				};
			});
		}
	})


frappe.ui.form.on('Combo Item', {
	item: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.item) {
			frappe.call({
				method: 'getpos.getpos.hooks.item_price.get_item_price',
				args: {
					item_code: child.item
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'item_price', r.message.price_list_rate);
					} else {
						frappe.model.set_value(cdt, cdn, 'item_price', 0);
					}
				}
			});
		}
	}
});
