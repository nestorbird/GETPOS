frappe.ui.form.on('Sales Order', {
     hub_manager: function(frm){
             frappe.call({
                 method: "agribora.agribora.doctype.ward.ward.get_ward_by_hub_manager",
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
});