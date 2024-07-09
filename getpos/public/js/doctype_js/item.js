frappe.ui.form.on('Item', {

    refresh: frm => {
        if (!frm.doc.__islocal) {

            if (frm.doc.custom_item == "Standard Item") {
                frm.add_custom_button(__("Create Attribute"), function() {
                    frappe.new_doc("Attributes",{
                        "parent_item":frm.doc.name
    
                    })
                }).css({"color":"white", "background-color": "#2490EF", "font-weight": "800"});
            }
    
            if (frm.doc.custom_item == "Combo Item") {
                frm.add_custom_button(__("Create Combo"), function() {
                    frappe.new_doc("Combo",{
                        "parent_item":frm.doc.name
    
                    })
                }).css({"color":"white", "background-color": "#2490EF", "font-weight": "800"});
            }

        }
       
        // if (!frm.doc.__islocal) {
        //     show_include_multigroup(frm)
        // }
        // else {
        //     frm.set_df_property('incldues_item_group', 'hidden', 1)
        // }

    },
    item_group: frm => {
        show_include_multigroup(frm)
    },
    

    custom_fetch_cost_center: function(frm) {
        frappe.call({
            method: "getpos.getpos.hooks.cost_center.fetch_all_cost_centers",
            callback: function(r) {
                if (r.message) {
                    frm.clear_table("custom_cost_center_details");
                    $.each(r.message, function(_i, d) {
                        let row = frm.add_child("custom_cost_center_details");
                        row.cost_center = d.name;
                    });
                    frm.refresh_field("custom_cost_center_details");
                    frappe.msgprint(__("Cost Centers fetched successfully"));
                }
            }
        });
    }

})

let show_include_multigroup = (frm) => {
    if (frm.doc.item_group) {
        frappe.db.get_doc('Item Group', frm.doc.item_group)
            .then(doc => {
                if (doc.parent_item_group === 'Extra') {
                    console.log(doc.parent_item_group)
                    frm.set_df_property('incldues_item_group', 'hidden', 0)
                }
                else {
                    frm.doc.incldues_item_group =[]
                    refresh_field('incldues_item_group')
                    frm.set_df_property('incldues_item_group', 'hidden', 1)
                }
            })
    }

}

frappe.ui.form.on('Related Item', {
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
                        frappe.msgprint(__('No price found for item {0}', [child.item]));
                    }
                }
            });
        }
    }
});
