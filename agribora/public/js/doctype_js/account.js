frappe.ui.form.on('Account', {
<<<<<<< HEAD
refresh: function(frm){
		set_hub_manager_filter(frm);
	}
});
function set_hub_manager_filter(frm){
  frappe.db.get_list('Account', {
=======
	refresh: function(frm){
        set_hub_manager_filter(frm);
	}
})

function set_hub_manager_filter(frm){
    frappe.db.get_list('Account', {
>>>>>>> a429c1f7e4b44c1a9d3225c51ed6b36e6db91e6c
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