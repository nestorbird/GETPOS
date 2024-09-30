frappe.ui.form.on('Account', {
	refresh: function(frm){
        set_hub_manager_filter(frm);
	}
})

function set_hub_manager_filter(frm){
    frappe.db.get_list('Account', {
        fields: ['hub_manager'],
        filters: {
            hub_manager: ["!=", '']
        },
        as_list: 1
    }).then(records => {
        let hub_manager_list = []
        for(let i = 0; i< records.length; i++){
            hub_manager_list.push(records[i].toString())
        }
        frm.set_query('hub_manager', () => {
            return {
                filters: {
                    hub_manager: ['not in', hub_manager_list]
                }
            }
        });
    })
}