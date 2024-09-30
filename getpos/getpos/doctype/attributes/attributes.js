// Copyright (c) 2024, Nestorbird and contributors
// For license information, please see license.txt


frappe.ui.form.on('Attributes', {
		refresh(frm) {
			frm.set_query('parent_item', function(doc, cdt, cdn) {
				return {
					"filters": {
						"custom_item": "Standard Item"
					}
				};
			});

				frm.set_query('item', 'attribute_items', function(doc, cdt, cdn) {
					var d = locals[cdt][cdn];
					return {
						"filters": {
							"custom_item": "Attribute/Modifier"
						}
					};
				});
			}
		})
		


frappe.ui.form.on('Attribute Items', {
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
						frappe.model.set_value(cdt, cdn, 'price', r.message.price_list_rate);
					} else {
						frappe.model.set_value(cdt, cdn, 'price', 0);
					}
				}
			});
		}
	}
});
