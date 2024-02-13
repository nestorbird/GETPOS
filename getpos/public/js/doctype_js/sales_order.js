frappe.ui.form.on('Sales Order', {
     hub_manager: function(frm){
         if(frm.doc.hub_manager){
            frappe.call({
                method: "getpos.getpos.doctype.ward.ward.get_ward_by_hub_manager",
                args:{
                    hub_manager: frm.doc.hub_manager
                },
                callback: (r)=> {
                    frm.set_query('ward', () => {
                        return {
                            filters: {
                                name: ['in', r.message]
                            }
                        }
                    });
                }
            });
         }  
     },
     ward: function(frm){
         if(frm.doc.ward){
            frappe.call({
                method: "getpos.getpos.hooks.customer.get_customer_by_ward",
                args:{
                    ward: frm.doc.ward
                },
                callback: (r)=> {
                    frm.set_query('customer', () => {
                        return {
                            filters: {
                                name: ['in', r.message]
                            }
                        }
                    });
                }
            });
         }
     }
});