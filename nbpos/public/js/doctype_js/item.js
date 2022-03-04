frappe.ui.form.on('Item', {
    refresh: frm => {
        if (!frm.doc.__islocal) {
            show_include_multigroup(frm)
        }
        else {
            frm.set_df_property('incldues_item_group', 'hidden', 1)
        }
    },
    item_group: frm => {
        show_include_multigroup(frm)
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