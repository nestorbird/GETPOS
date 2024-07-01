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
		
