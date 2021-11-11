// Copyright (c) 2021, www.nestorbird.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ward', {
	ward: function(frm){
		if(frm.doc.ward && frm.doc.__islocal){
			frappe.call({
				method: "agribora.agribora.api.get_abbr",
				args:{
					string: frm.doc.ward
				},
				callback: (r)=> {
					frm.set_value("abbr",r.message)
				}
			});
		}
	}
});
